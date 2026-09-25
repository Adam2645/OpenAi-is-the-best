from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Settings

AUDIO_TOKENS_PER_S = 25.0


# cennik w dolarach za milion tokenów jest konfigurowalny, bo ceny się zmieniają i są tylko szacunkiem
@dataclass(frozen=True)
class PriceTable:
    text_in: float
    audio_in: float
    image_in: float
    text_out: float
    audio_out: float

    # domyślne stawki pochodzą z cennika gemini-3.8-live z dnia przygotowania projektu
    @classmethod
    def from_settings(cls, s: Settings) -> "PriceTable":
        return cls(s.price_text_in_usd, s.price_audio_in_usd, s.price_image_in_usd, s.price_text_out_usd, s.price_audio_out_usd)


# migawka budżetu trafia do stanu robota i do wskaźnika zużycia w interfejsie
@dataclass(frozen=True)
class BudgetSnapshot:
    session_pln: float
    total_pln: float
    session_limit_pln: float
    total_limit_pln: float
    warning: bool
    blocked: bool
    reason: str
    server_usd: float
    estimate_usd: float


# rejestr zapisuje łączne wydatki między uruchomieniami, żeby limit całkowity obejmował wszystkie sesje
class UsageLedger:
    # brak pliku oznacza zerowe wydatki, a uszkodzony plik jest traktowany ostrożnie jako błąd
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.data = {"total_usd": 0.0, "sessions": []}
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    # suma z poprzednich sesji jest bazą dla limitu całkowitego
    @property
    def total_usd(self) -> float:
        return float(self.data.get("total_usd", 0.0))

    # zapis atomowy chroni rejestr przed uszkodzeniem przy nagłym zamknięciu programu
    def add(self, delta_usd: float, meta: dict) -> None:
        if delta_usd <= 0:
            return
        with self._lock:
            self.data["total_usd"] = self.total_usd + delta_usd
            self.data.setdefault("sessions", []).append({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "usd": round(delta_usd, 6), **meta})
            self.data["sessions"] = self.data["sessions"][-500:]
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=1, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.path)


# licznik kosztów bierze większą z dwóch wartości: z metadanych serwera i z ostrożnego lokalnego szacunku
class CostMeter:
    # model kosztu uwzględnia ponowne naliczanie kontekstu w każdej turze oraz kompresję okna
    def __init__(
        self,
        prices: PriceTable,
        usd_to_pln: float,
        session_limit_pln: float,
        total_limit_pln: float,
        ledger: UsageLedger,
        warn_fraction: float = 0.8,
        safety_factor: float = 1.25,
        image_tokens: int = 258,
        context_trigger: int = 12000,
        context_target: int = 4000,
        bill_listening_time: bool = True,
    ) -> None:
        self.prices = prices
        self.usd_to_pln = usd_to_pln
        self.session_limit_pln = session_limit_pln
        self.total_limit_pln = total_limit_pln
        self.ledger = ledger
        self.warn_fraction = warn_fraction
        self.safety_factor = safety_factor
        self.image_tokens = image_tokens
        self.context_trigger = context_trigger
        self.context_target = context_target
        self.bill_listening_time = bill_listening_time
        self._lock = threading.Lock()
        self.server_usd = 0.0
        self.sent_audio_s = 0.0
        self.listen_s = 0.0
        self.recv_audio_s = 0.0
        self.images = 0
        self.text_in_tokens = 0.0
        self.text_out_tokens = 0.0
        self.rebilled_tokens = 0.0
        self._context = 0.0
        self._turn_tokens = 0.0
        self._flushed_usd = 0.0
        self.usage_messages = 0

    # budowa z ustawień łączy cennik, limity i rejestr w jednym miejscu
    @classmethod
    def from_settings(cls, s: Settings) -> "CostMeter":
        return cls(
            PriceTable.from_settings(s), s.usd_to_pln, s.budget_session_pln, s.budget_total_pln,
            UsageLedger(s.resolve_path(s.ledger_path)), s.budget_warn_fraction, s.cost_safety_factor,
            s.image_tokens_per_frame, s.context_trigger_tokens, s.context_target_tokens, s.bill_listening_time,
        )

    # metadane zużycia z serwera są przeliczane według modalności na stawki cennika
    def record_server_usage(self, usage) -> None:
        rates_in = {"AUDIO": self.prices.audio_in, "TEXT": self.prices.text_in, "IMAGE": self.prices.image_in, "VIDEO": self.prices.image_in}
        rates_out = {"AUDIO": self.prices.audio_out, "TEXT": self.prices.text_out}
        cost = 0.0
        prompt_details = getattr(usage, "prompt_tokens_details", None) or []
        if prompt_details:
            for d in prompt_details:
                modality = str(getattr(d.modality, "value", d.modality) or "AUDIO").upper()
                cost += (d.token_count or 0) * rates_in.get(modality, self.prices.audio_in)
        else:
            cost += (getattr(usage, "prompt_token_count", 0) or 0) * self.prices.audio_in
        response_details = getattr(usage, "response_tokens_details", None) or []
        if response_details:
            for d in response_details:
                modality = str(getattr(d.modality, "value", d.modality) or "AUDIO").upper()
                cost += (d.token_count or 0) * rates_out.get(modality, self.prices.audio_out)
        else:
            cost += (getattr(usage, "response_token_count", 0) or 0) * self.prices.audio_out
        cost += (getattr(usage, "thoughts_token_count", 0) or 0) * self.prices.text_out
        with self._lock:
            self.server_usd += cost / 1e6
            self.usage_messages += 1

    # wysłany dźwięk mikrofonu to 25 tokenów na sekundę według dokumentacji live api
    def add_audio_in(self, seconds: float) -> None:
        with self._lock:
            self.sent_audio_s += seconds
            self._turn_tokens += seconds * AUDIO_TOKENS_PER_S

    # przy stale włączonym proactive audio w 3.8 live liczymy ostrożnie cały czas nasłuchu
    def add_listening_time(self, seconds: float) -> None:
        with self._lock:
            self.listen_s += seconds

    # dźwięk odpowiedzi robota jest najdroższą składową rozmowy
    def add_audio_out(self, seconds: float) -> None:
        with self._lock:
            self.recv_audio_s += seconds
            self._turn_tokens += seconds * AUDIO_TOKENS_PER_S

    # każda rzadka klatka obrazu dokłada tokeny wejścia i kontekstu
    def add_image(self) -> None:
        with self._lock:
            self.images += 1
            self._turn_tokens += self.image_tokens

    # tekst kontekstu z czujników jest tani, ale też trafia do okna sesji
    def add_text_in(self, chars: int) -> None:
        with self._lock:
            self.text_in_tokens += chars / 4.0
            self._turn_tokens += chars / 4.0

    # transkrypcje są naliczane według stawki tekstu wyjściowego jako dopłata
    def add_text_out(self, chars: int) -> None:
        with self._lock:
            self.text_out_tokens += chars / 4.0

    # na koniec tury serwer ponownie przetwarza zgromadzony kontekst aż do progu kompresji
    def on_turn_complete(self) -> None:
        with self._lock:
            self.rebilled_tokens += min(self._context, float(self.context_trigger))
            self._context += self._turn_tokens
            self._turn_tokens = 0.0
            if self._context > self.context_trigger:
                self._context = float(self.context_target)

    # lokalny szacunek zawyża raczej niż zaniża, bo służy do bezpiecznego wyłączenia api
    def estimate_usd(self) -> float:
        with self._lock:
            audio_in_s = max(self.sent_audio_s, self.listen_s if self.bill_listening_time else 0.0)
            p = self.prices
            usd = (
                audio_in_s * AUDIO_TOKENS_PER_S * p.audio_in
                + self.recv_audio_s * AUDIO_TOKENS_PER_S * p.audio_out
                + self.images * self.image_tokens * p.image_in
                + self.text_in_tokens * p.text_in
                + self.text_out_tokens * p.text_out
                + self.rebilled_tokens * p.audio_in
            )
            return usd / 1e6

    # koszt sesji to większy z dwóch pomiarów pomnożony przez współczynnik bezpieczeństwa
    def session_usd(self) -> float:
        return max(self.server_usd, self.estimate_usd()) * self.safety_factor

    # migawka porównuje wydatki z limitem sesji i limitem całkowitym z rejestru
    def snapshot(self) -> BudgetSnapshot:
        session_usd = self.session_usd()
        session_pln = session_usd * self.usd_to_pln
        unflushed = max(0.0, session_usd - self._flushed_usd)
        total_pln = (self.ledger.total_usd + unflushed) * self.usd_to_pln
        blocked, reason = False, ""
        if self.session_limit_pln > 0 and session_pln >= self.session_limit_pln:
            blocked, reason = True, f"limit sesji {self.session_limit_pln:.2f} zł"
        elif self.total_limit_pln > 0 and total_pln >= self.total_limit_pln:
            blocked, reason = True, f"limit całkowity {self.total_limit_pln:.2f} zł"
        warning = (
            (self.session_limit_pln > 0 and session_pln >= self.warn_fraction * self.session_limit_pln)
            or (self.total_limit_pln > 0 and total_pln >= self.warn_fraction * self.total_limit_pln)
        )
        return BudgetSnapshot(
            session_pln, total_pln, self.session_limit_pln, self.total_limit_pln, warning, blocked, reason,
            self.server_usd, self.estimate_usd(),
        )

    # zgoda na dalsze wywołania api jest sprawdzana przed każdym wysłaniem danych
    def allow(self) -> bool:
        return not self.snapshot().blocked

    # przyrost wydatków jest dopisywany do rejestru okresowo i przy zamknięciu, więc limit przetrwa restart
    def flush(self) -> None:
        session_usd = self.session_usd()
        delta = session_usd - self._flushed_usd
        if delta > 0:
            self.ledger.add(delta, {"server_usd": round(self.server_usd, 6), "estimate_usd": round(self.estimate_usd(), 6)})
            self._flushed_usd = session_usd
