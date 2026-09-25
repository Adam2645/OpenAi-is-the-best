from __future__ import annotations

from types import SimpleNamespace

from so101_expressive.budget import CostMeter, PriceTable, UsageLedger

PRICES = PriceTable(text_in=0.75, audio_in=3.0, image_in=1.0, text_out=4.5, audio_out=12.0)


# licznik testowy z jawnie podanymi limitami i rejestrem w katalogu tymczasowym
def meter(tmp_path, session=5.0, total=130.0, safety=1.0):
    return CostMeter(PRICES, 4.0, session, total, UsageLedger(tmp_path / "l.json"), safety_factor=safety,
                     context_trigger=12000, context_target=4000)


# minuta audio odpowiada stawkom z cennika: około 0.0045 usd wejścia i 0.018 usd wyjścia
def test_audio_minute_matches_published_rates(tmp_path):
    m = meter(tmp_path)
    m.add_audio_in(60.0)
    assert abs(m.estimate_usd() - 0.0045) < 1e-9
    m.add_audio_out(60.0)
    assert abs(m.estimate_usd() - (0.0045 + 0.018)) < 1e-9


# ponowne naliczanie kontekstu rośnie z liczbą tur, ale kompresja ogranicza koszt pojedynczej tury
def test_context_rebilling_is_capped_by_compression(tmp_path):
    m = meter(tmp_path)
    per_turn = []
    for _ in range(40):
        before = m.rebilled_tokens
        m.add_audio_in(5.0)
        m.add_audio_out(5.0)
        m.on_turn_complete()
        per_turn.append(m.rebilled_tokens - before)
    assert per_turn[5] > per_turn[1]
    assert max(per_turn) <= 12000


# czas nasłuchu liczy się jak wejście audio, gdy proactive audio nalicza cały strumień
def test_listening_time_counts_when_enabled(tmp_path):
    m = meter(tmp_path)
    m.add_listening_time(600.0)
    m.add_audio_in(30.0)
    assert abs(m.estimate_usd() - 600 * 25 * 3.0 / 1e6) < 1e-9


# metadane serwera są przeliczane według modalności na właściwe stawki
def test_server_usage_by_modality(tmp_path):
    m = meter(tmp_path)
    usage = SimpleNamespace(
        prompt_tokens_details=[SimpleNamespace(modality="AUDIO", token_count=1000), SimpleNamespace(modality="TEXT", token_count=1000)],
        response_tokens_details=[SimpleNamespace(modality="AUDIO", token_count=500)],
        thoughts_token_count=0,
    )
    m.record_server_usage(usage)
    assert abs(m.server_usd - (1000 * 3.0 + 1000 * 0.75 + 500 * 12.0) / 1e6) < 1e-12


# limit sesji blokuje api, a rejestr przenosi wydatki do kolejnego uruchomienia i limitu całkowitego
def test_limits_and_persistent_ledger(tmp_path):
    m = meter(tmp_path, session=0.5, total=1.0)
    m.add_audio_out(60.0 * 7)
    snap = m.snapshot()
    assert snap.blocked and "sesji" in snap.reason
    m.flush()
    again = meter(tmp_path, session=10.0, total=1.0)
    again.add_audio_out(60.0 * 7)
    snap2 = again.snapshot()
    assert snap2.blocked and "całkowity" in snap2.reason
    assert UsageLedger(tmp_path / "l.json").total_usd > 0.1
