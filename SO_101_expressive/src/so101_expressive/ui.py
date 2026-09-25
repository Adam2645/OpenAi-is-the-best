from __future__ import annotations

import unicodedata
from pathlib import Path

import numpy as np

from .sim.render import SimRenderer
from .sim.mujoco_sim import MujocoSim
from .state import Activity, ApiStatus, PersonStatus, RobotState

FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
KEY_HELP = (
    "SPACJA/E: stop   R: zwolnij   I: przerwij mowę   P: chwyć   O: odłóż   C: kostka na start   "
    "G: gest   T: taniec   M: milczenie przy trzymaniu   A/D/W/S/Z/X/V: widok   Q: wyjście"
)
STATUS_COLORS = {
    PersonStatus.TRACKED: (80, 200, 90),
    PersonStatus.ACQUIRING: (60, 200, 230),
    PersonStatus.UNCERTAIN: (40, 140, 240),
    PersonStatus.ABSENT: (140, 140, 140),
}
PANEL_H = 268


# polskie znaki są rysowane czcionką systemową, a bez niej tekst jest transliterowany do ascii
def _ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text.replace("ł", "l").replace("Ł", "L")).encode("ascii", "ignore").decode()


# poziom w decybelach jest czytelniejszy niż surowa wartość rms
def _db(level: float) -> str:
    return f"{20 * np.log10(max(level, 1e-6)):.0f} dBFS"


# panel składa podgląd kamery, symulację i stan robota w jednym oknie opencv, które działa na macos bez mjpython
class Dashboard:
    # okno jest opcjonalne, bo w trybie bez ekranu ten sam panel trafia tylko do nagrania wideo
    def __init__(self, sim: MujocoSim, width: int = 640, height: int = 480, window: bool = True, mode_label: str = "") -> None:
        import cv2

        self.cv2 = cv2
        self.w, self.h = width, height
        self.renderer = SimRenderer(sim, width, height)
        self.mode_label = mode_label
        self.window = "SO-101 - ekspresyjny robot rozmowny" if window else None
        self.font = self.font_small = None
        try:
            from PIL import ImageFont

            for path in FONT_CANDIDATES:
                if Path(path).exists():
                    self.font = ImageFont.truetype(path, 17)
                    self.font_small = ImageFont.truetype(path, 14)
                    break
        except Exception:
            self.font = None
        self._drag: tuple[int, int] | None = None
        if self.window:
            cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window, 2 * width, height + PANEL_H)
            cv2.setMouseCallback(self.window, self._mouse)

    # przeciąganie myszą po prawej połowie obraca kamerę symulacji, a kółko przybliża
    def _mouse(self, event, x, y, flags, param) -> None:
        cv2 = self.cv2
        if event == cv2.EVENT_LBUTTONDOWN and x >= self.w:
            self._drag = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self._drag is not None:
            dx, dy = x - self._drag[0], y - self._drag[1]
            self.renderer.orbit(-dx * 0.4, -dy * 0.3)
            self._drag = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self._drag = None
        elif event == cv2.EVENT_MOUSEWHEEL:
            self.renderer.zoom(0.9 if flags > 0 else 1.1)

    # tekst z polskimi znakami rysujemy przez pillow, bo czcionki opencv obsługują tylko ascii
    def _text(self, img: np.ndarray, lines: list[tuple[int, int, str, tuple[int, int, int], bool]]) -> np.ndarray:
        if self.font is None:
            for x, y, text, color, small in lines:
                self.cv2.putText(img, _ascii(text), (x, y + 14), self.cv2.FONT_HERSHEY_SIMPLEX, 0.42 if small else 0.5, color, 1, self.cv2.LINE_AA)
            return img
        from PIL import Image, ImageDraw

        pil = Image.fromarray(img[:, :, ::-1])
        draw = ImageDraw.Draw(pil)
        for x, y, text, color, small in lines:
            draw.text((x, y), text, font=self.font_small if small else self.font, fill=(color[2], color[1], color[0]))
        return np.asarray(pil)[:, :, ::-1].copy()

    # lewa połowa pokazuje kamerę z ramkami twarzy w kolorze statusu śledzenia
    def _camera_panel(self, frame: np.ndarray | None, faces, state: RobotState, mirror: bool) -> np.ndarray:
        cv2 = self.cv2
        if frame is None:
            panel = np.full((self.h, self.w, 3), 30, dtype=np.uint8)
            cv2.putText(panel, "brak obrazu z kamery", (20, self.h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2)
            return panel
        panel = cv2.resize(frame, (self.w, self.h))
        color = STATUS_COLORS[state.person]
        for f in faces or []:
            x0, y0 = int(f.x * self.w), int(f.y * self.h)
            cv2.rectangle(panel, (x0, y0), (int((f.x + f.w) * self.w), int((f.y + f.h) * self.h)), color, 2)
        if mirror:
            panel = cv2.flip(panel, 1)
        return panel

    # szerokość napisu mierzymy czcionką, żeby czipy i tekst wyrównany do prawej nie nachodziły na siebie
    def _width(self, text: str, small: bool = True) -> int:
        font = self.font_small if small else self.font
        if font is not None:
            return int(font.getlength(text))
        return int(len(text) * (7.5 if small else 9.0))

    # czip czynności jest podświetlony, gdy czynność trwa, dzięki czemu stan robota widać na pierwszy rzut oka
    def _chips(self, img: np.ndarray, state: RobotState, y: int) -> list:
        cv2 = self.cv2
        active = set(state.activities())
        labels = []
        x = 10
        for act in Activity:
            text = act.value.upper()
            if act is Activity.GESTURING and state.gesture:
                text = f"GEST: {state.gesture}"
            width = self._width(text) + 14
            on = act in active
            fill = (40, 90, 200) if act is Activity.STOPPED and on else ((60, 150, 60) if on else (55, 55, 55))
            cv2.rectangle(img, (x, y), (x + width, y + 22), fill, -1)
            labels.append((x + 7, y + 3, text, (255, 255, 255) if on else (150, 150, 150), True))
            x += width + 5
        return labels

    # dolny pasek zbiera stan rozmowy, budżet, percepcję, chwytak i decyzje arbitra
    def compose(self, frame: np.ndarray | None, faces, state: RobotState, extra: dict | None = None, mirror: bool = True) -> np.ndarray:
        cv2 = self.cv2
        extra = extra or {}
        cam = self._camera_panel(frame, faces, state, mirror)
        sim = self.renderer.render()[:, :, ::-1]
        top = np.hstack([cam, sim])
        info = np.full((PANEL_H, 2 * self.w, 3), 22, dtype=np.uint8)
        panel = self._chips(info, state, 32)
        budget_frac = 0.0 if state.budget_session_limit_pln <= 0 else min(1.0, state.budget_session_pln / state.budget_session_limit_pln)
        bar_color = (60, 60, 220) if state.budget_blocked else ((40, 190, 230) if state.budget_warning else (70, 180, 70))
        bar_x0, bar_x1 = 2 * self.w - 170, 2 * self.w - 12
        cv2.rectangle(info, (bar_x0, 10), (bar_x0 + int((bar_x1 - bar_x0) * budget_frac), 20), bar_color, -1)
        cv2.rectangle(info, (bar_x0, 10), (bar_x1, 20), (120, 120, 120), 1)
        budget_text = (f"Budżet: {state.budget_session_pln:.2f}/{state.budget_session_limit_pln:.2f} zł sesja, "
                       f"{state.budget_total_pln:.2f}/{state.budget_total_limit_pln:.0f} zł łącznie")
        ev = state.grip_evidence
        grip_src = "brak pomiaru" if ev is None else (
            "POZOROWANY STAN TESTOWY" if ev.source == "mock" else
            f"{ev.source}: szczęki {ev.fixed_jaw_force_n:.0f}/{ev.moving_jaw_force_n:.0f} N, "
            f"{'uniesiony' if ev.lifted else 'nieuniesiony'}, pewność {ev.confidence:.2f}"
        )
        api = state.api.value + (f" - {state.api_detail}" if state.api_detail else "")
        tempo = f", {state.music_bpm:.0f} BPM" if state.music and state.music_bpm else ""
        white, grey, warn = (235, 235, 235), (170, 170, 170), (60, 170, 250)
        panel += [
            (12, 6, f"SO-101 robot rozmowny  |  {self.mode_label}", white, False),
            (bar_x0 - 12 - self._width(budget_text), 7, budget_text, grey, True),
            (12, 62, f"Rozmowa: {state.conversation.value}   |   API: {api}   |   "
             f"Klatki kamery do chmury: {extra.get('frames_sent', 0)}", white, False),
            (12, 86, f"Osoba: {state.person.value} (pewność {state.person_confidence:.2f})   |   Muzyka: "
             f"{'tak' if state.music else 'nie'} (wynik {state.music_score:.2f}{tempo})   |   "
             f"Mikrofon: {_db(extra.get('mic_rms', 0.0))} {'[bramka otwarta]' if extra.get('gate_open', True) else '[bramka echa]'}"
             f"   |   Głośnik: {_db(state.audio_level)}{' WYCISZONY' if state.speech_muted else ''}", white, False),
            (12, 110, f"Chwytak: {state.grip.value} ({grip_src})   |   Manipulacja: {state.manipulation.value}", white, False),
            (12, 134, f"Ramię: {extra.get('arm_owner', '-')}   |   Chwytak steruje: {extra.get('gripper_owner', '-')}", grey, False),
            (12, 158, "Wstrzymane: " + ("; ".join(state.suppressed) or "nic"), warn if state.suppressed else grey, True),
            (12, 178, "Komunikat: " + (str(extra.get("message") or "-"))[:150], warn if extra.get("message") else grey, True),
            (12, 198, f"Ty: {state.last_user_text[-140:]}", grey, True),
            (12, 218, f"Robot: {state.last_robot_text[-140:]}", grey, True),
            (12, 244, KEY_HELP, (130, 130, 130), True),
        ]
        img = np.vstack([top, info])
        overlay = []
        if state.estop:
            cv2.rectangle(img, (self.w, 0), (2 * self.w, 44), (30, 30, 200), -1)
            overlay.append((self.w + 14, 10, f"AWARYJNY STOP ({state.estop_reason}) - R zwalnia", (255, 255, 255), False))
        if state.api is ApiStatus.BUDGET_EXCEEDED:
            cv2.rectangle(img, (0, 0), (self.w, 44), (30, 30, 170), -1)
            overlay.append((14, 10, "BUDŻET WYCZERPANY - wywołania API wyłączone", (255, 255, 255), False))
        shifted = [(x, y + self.h, t, c, s) for x, y, t, c, s in panel]
        return self._text(img, shifted + overlay)

    # wyświetlenie klatki zwraca kod klawisza albo minus jeden, gdy nic nie wciśnięto
    def show(self, img: np.ndarray) -> int:
        if not self.window:
            return -1
        self.cv2.imshow(self.window, img)
        return self.cv2.waitKey(1) & 0xFF

    # klawisze kamery symulacji są obsługiwane w panelu, a pozostałe zwracane do aplikacji
    def handle_view_key(self, key: int) -> bool:
        moves = {ord("a"): (-6, 0), ord("d"): (6, 0), ord("w"): (0, 4), ord("s"): (0, -4)}
        if key in moves:
            self.renderer.orbit(*moves[key])
            return True
        if key == ord("z"):
            self.renderer.zoom(0.9)
            return True
        if key == ord("x"):
            self.renderer.zoom(1.1)
            return True
        if key == ord("v"):
            self.renderer.reset_view()
            return True
        return False

    # zamknięcie niszczy okno i zwalnia kontekst gl renderera
    def close(self) -> None:
        if self.window:
            self.cv2.destroyWindow(self.window)
        self.renderer.close()
