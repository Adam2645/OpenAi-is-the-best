from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ..motion.kinematics import So101Kinematics
from ..state import GripEvidence, GripPhase, ManipulationPhase
from .expressive import min_jerk

GRIPPER_OPEN = 0.9
GRIPPER_CLOSED = -0.14
DOWN = np.array([0.0, 0.0, -1.0])
FACE_DIRS = [np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])]
ACTIVE_PHASES = tuple(p for p in ManipulationPhase if p is not ManipulationPhase.IDLE)
MAX_DESCENT_JOINT_CHANGE = 0.8


# wynik kroku manipulacji mówi arbitrowi, czy zadanie przejmuje ramię i jak ostrożnie ma się ruszać
@dataclass(frozen=True)
class ManipulationOutput:
    targets: np.ndarray | None
    phase: ManipulationPhase
    grip: GripPhase
    speed_scale: float
    message: str = ""


# odcinek trajektorii w przestrzeni przegubów z profilem minimalnego szarpnięcia
class _Segment:
    # cel i czas trwania są stałe, dzięki czemu odcinek można wznowić po awaryjnym stopie
    def __init__(self, q_from: np.ndarray, q_to: np.ndarray, t0: float, duration: float) -> None:
        self.q_from = np.asarray(q_from, dtype=float).copy()
        self.q_to = np.asarray(q_to, dtype=float).copy()
        self.t0 = t0
        self.duration = max(duration, 1e-3)

    # pozycja zadana w chwili t leży na gładkiej krzywej między początkiem a celem
    def at(self, t: float) -> np.ndarray:
        s = min_jerk((t - self.t0) / self.duration)
        return self.q_from + (self.q_to - self.q_from) * s

    # koniec odcinka jest warunkiem koniecznym przejścia do następnej fazy
    def finished(self, t: float) -> bool:
        return t >= self.t0 + self.duration


# chwyt i odłożenie kostki są prawdziwą manipulacją w fizyce mujoco, a nie przełączeniem flagi
class PickPlaceSkill:
    # lokalizator obiektu z symulacji zastępuje percepcję, a punkt odłożenia jest stały w scenie
    def __init__(
        self,
        kin: So101Kinematics,
        locate_object: Callable[[], np.ndarray],
        place_position: np.ndarray,
        cube_half: float = 0.015,
        approach_height: float = 0.06,
        lift_height: float = 0.09,
        hold_point: tuple[float, float, float] = (0.24, 0.0, 0.17),
    ) -> None:
        self.kin = kin
        self.locate_object = locate_object
        self.place_position = np.asarray(place_position, dtype=float)
        self.cube_half = cube_half
        self.approach_height = approach_height
        self.lift_height = lift_height
        self.hold_point = np.asarray(hold_point, dtype=float)
        self.phase = ManipulationPhase.IDLE
        self.grip = GripPhase.OPEN
        self.message = ""
        self._seg: _Segment | None = None
        self._plan: dict[str, np.ndarray] = {}
        self._t_phase = 0.0
        self._since: float | None = None
        self._bad_since: float | None = None
        self._paused = False
        self._last: np.ndarray | None = None

    # aktywne zadanie przejmuje ramię i chwytak na wyłączność
    @property
    def active(self) -> bool:
        return self.phase in ACTIVE_PHASES

    # wartość zadana chwytaka w trakcie trzymania jest stała i nie zależy od mowy
    @property
    def hold_value(self) -> float:
        return GRIPPER_CLOSED

    # pełna poza z ramieniem i chwytakiem ułatwia składanie celów odcinków
    @staticmethod
    def _pose(q_arm: np.ndarray, gripper: float) -> np.ndarray:
        return np.r_[np.asarray(q_arm, dtype=float)[:5], gripper]

    # czas odcinka rośnie z dystansem, żeby prędkość dojazdu była umiarkowana
    @staticmethod
    def _duration(q_from: np.ndarray, q_to: np.ndarray, speed: float = 0.7, minimum: float = 0.8) -> float:
        return max(minimum, float(np.max(np.abs(q_to[:5] - q_from[:5]))) / speed)

    # zmiana fazy zeruje liczniki potwierdzeń, żeby dowód z poprzedniego etapu nie przechodził dalej
    def _enter(self, phase: ManipulationPhase, t: float, q_to: np.ndarray | None, duration: float | None = None) -> None:
        self.phase = phase
        self._t_phase = t
        self._since = None
        self._bad_since = None
        if q_to is not None:
            start = self._last if self._last is not None else q_to
            dur = duration if duration is not None else self._duration(start, q_to)
            self._seg = _Segment(start, q_to, t, dur)

    # prośba o chwyt planuje całą sekwencję z góry i odrzuca cele poza zasięgiem mechaniki
    def request_pick(self, t: float, q_now: np.ndarray) -> tuple[bool, str]:
        if self.phase not in (ManipulationPhase.IDLE, ManipulationPhase.FAILED):
            return False, "trwa inne zadanie manipulacji"
        if self.grip is not GripPhase.OPEN:
            return False, "chwytak nie jest wolny"
        cube = np.asarray(self.locate_object(), dtype=float)
        q_now = np.asarray(q_now, dtype=float)
        grasp = self.kin.ik(cube + [0.0, 0.0, 0.002], approach=DOWN, close_dirs=FACE_DIRS, prefer=q_now[:5])
        pre = self.kin.ik(
            cube + [0.0, 0.0, self.approach_height], approach=DOWN, close_dirs=FACE_DIRS,
            seeds=[np.zeros(5)], prefer=grasp.q_arm,
        )
        lift = self.kin.ik(cube + [0.0, 0.0, self.lift_height], seeds=[np.zeros(5)], prefer=grasp.q_arm)
        hold = self.kin.ik(self.hold_point, seeds=[np.zeros(5)], prefer=lift.q_arm)
        if not (grasp.ok and pre.ok):
            return False, f"obiekt poza zasięgiem (błąd ik {grasp.pos_err * 1000:.0f} mm)"
        if float(np.max(np.abs(pre.q_arm - grasp.q_arm))) > MAX_DESCENT_JOINT_CHANGE:
            return False, "niespójne rozwiązanie ik - opuszczanie wymagałoby obrotu nad obiektem"
        self._plan = {"pre": pre.q_arm, "grasp": grasp.q_arm, "lift": lift.q_arm, "hold": hold.q_arm}
        self._last = q_now.copy()
        self.message = "sięgam po kostkę"
        self._enter(ManipulationPhase.APPROACH, t, self._pose(pre.q_arm, GRIPPER_OPEN))
        return True, self.message

    # odłożenie jest dozwolone wyłącznie przy potwierdzonym trzymaniu obiektu
    def request_place(self, t: float, q_now: np.ndarray) -> tuple[bool, str]:
        if self.phase is not ManipulationPhase.HOLD or self.grip is not GripPhase.HOLDING:
            return False, "nie trzymam obiektu"
        target = self.place_position.copy()
        target[2] = self.cube_half + 0.004
        current = self._last[:5] if self._last is not None else np.asarray(q_now, dtype=float)[:5]
        down = self.kin.ik(target, approach=DOWN, close_dirs=FACE_DIRS, prefer=current)
        above = self.kin.ik(
            target + [0.0, 0.0, self.approach_height], approach=DOWN, close_dirs=FACE_DIRS,
            seeds=[np.zeros(5)], prefer=down.q_arm,
        )
        if not (down.ok and above.ok):
            return False, "miejsce odłożenia poza zasięgiem"
        if float(np.max(np.abs(above.q_arm - down.q_arm))) > MAX_DESCENT_JOINT_CHANGE:
            return False, "niespójne rozwiązanie ik przy odkładaniu"
        self._plan.update({"place_above": above.q_arm, "place_down": down.q_arm})
        self.message = "odkładam kostkę"
        self._enter(ManipulationPhase.PLACE_APPROACH, t, self._pose(above.q_arm, GRIPPER_CLOSED))
        return True, self.message

    # przerwanie nigdy nie upuszcza trzymanego obiektu, a przy pustym chwytaku wycofuje ramię
    def abort(self, t: float) -> tuple[bool, str]:
        if not self.active:
            return False, "brak zadania do przerwania"
        if self.grip in (GripPhase.CONTACT, GripPhase.HOLDING):
            self.message = "przerwano - trzymam obiekt dalej"
            self._enter(ManipulationPhase.HOLD, t, self._pose(self._plan.get("hold", self._last[:5]), GRIPPER_CLOSED))
            return True, self.message
        self._fail(t, "przerwano zadanie")
        return True, self.message

    # niepowodzenie otwiera chwytak i unosi ramię, aby nie zostawić go przy blacie
    def _fail(self, t: float, reason: str) -> None:
        self.message = reason
        if self.grip is not GripPhase.LOST:
            self.grip = GripPhase.OPEN
        retreat = self._plan.get("pre", self._last[:5] if self._last is not None else np.zeros(5))
        self._enter(ManipulationPhase.FAILED, t, self._pose(retreat, GRIPPER_OPEN), duration=1.2)

    # dojazd uznajemy po końcu odcinka i zbliżeniu zmierzonej pozycji albo po limicie czasu
    def _reached(self, t: float, q_meas: np.ndarray, tol: float = 0.04, timeout: float = 1.5) -> bool:
        if self._seg is None or not self._seg.finished(t):
            return False
        close = float(np.max(np.abs(q_meas[:5] - self._seg.q_to[:5]))) < tol
        return close or t > self._seg.t0 + self._seg.duration + timeout

    # warunek musi trwać przez zadany czas, by chwilowy kontakt nie potwierdził chwytu
    def _sustained(self, cond: bool, t: float, hold_s: float) -> bool:
        if not cond:
            self._since = None
            return False
        if self._since is None:
            self._since = t
        return t - self._since >= hold_s

    # utrata dowodu trzymania przez krótki czas oznacza wyślizgnięcie obiektu
    def _lost(self, bad: bool, t: float, hold_s: float) -> bool:
        if not bad:
            self._bad_since = None
            return False
        if self._bad_since is None:
            self._bad_since = t
        return t - self._bad_since >= hold_s

    # automat faz rozdziela komendę chwytu od potwierdzenia fizycznego i reaguje na utratę obiektu
    def update(self, t: float, q_meas: np.ndarray, evidence: GripEvidence, estop: bool) -> ManipulationOutput:
        if not self.active:
            return ManipulationOutput(None, self.phase, self.grip, 1.0, self.message)
        if estop:
            self._paused = True
            return ManipulationOutput(self._last.copy(), self.phase, self.grip, 0.5, self.message)
        if self._paused and self._seg is not None:
            remaining = max(0.6, self._seg.t0 + self._seg.duration - t)
            self._seg = _Segment(self._last, self._seg.q_to, t, remaining)
            self._paused = False
        phase = self.phase
        if phase is ManipulationPhase.APPROACH and self._reached(t, q_meas):
            self._enter(ManipulationPhase.DESCEND, t, self._pose(self._plan["grasp"], GRIPPER_OPEN), duration=1.0)
        elif phase is ManipulationPhase.DESCEND and self._reached(t, q_meas, tol=0.05):
            self.grip = GripPhase.CLOSING
            self.message = "zamykam chwytak - czekam na potwierdzenie"
            self._enter(ManipulationPhase.CLOSE, t, self._pose(self._plan["grasp"], GRIPPER_CLOSED), duration=0.6)
        elif phase is ManipulationPhase.CLOSE:
            if self._sustained(evidence.both_jaws and evidence.blocked, t, 0.25):
                self.grip = GripPhase.CONTACT
                self.message = "kontakt obu szczęk - podnoszę"
                self._enter(ManipulationPhase.LIFT, t, self._pose(self._plan["lift"], GRIPPER_CLOSED), duration=1.3)
            elif t - self._t_phase > 2.5:
                self._fail(t, "brak potwierdzenia chwytu")
        elif phase is ManipulationPhase.LIFT:
            if self._lost(evidence.released, t, 0.15):
                self.grip = GripPhase.LOST
                self._fail(t, "obiekt wyślizgnął się podczas podnoszenia")
            elif self._reached(t, q_meas, tol=0.06):
                if evidence.both_jaws and evidence.lifted and evidence.attached:
                    self.grip = GripPhase.HOLDING
                    self.message = "trzymam kostkę - potwierdzone fizycznie"
                    self._enter(ManipulationPhase.HOLD, t, self._pose(self._plan["hold"], GRIPPER_CLOSED), duration=1.3)
                elif t - self._seg.t0 - self._seg.duration > 1.0:
                    self.grip = GripPhase.LOST
                    self._fail(t, "obiekt nie uniósł się razem z chwytakiem")
        elif phase in (ManipulationPhase.HOLD, ManipulationPhase.PLACE_APPROACH, ManipulationPhase.PLACE_DESCEND):
            if self._lost(not (evidence.both_jaws and evidence.attached), t, 0.3):
                self.grip = GripPhase.LOST
                self._fail(t, "utracono trzymany obiekt")
            elif phase is ManipulationPhase.PLACE_APPROACH and self._reached(t, q_meas):
                self._enter(ManipulationPhase.PLACE_DESCEND, t, self._pose(self._plan["place_down"], GRIPPER_CLOSED), duration=1.0)
            elif phase is ManipulationPhase.PLACE_DESCEND and self._reached(t, q_meas, tol=0.05):
                self.grip = GripPhase.RELEASING
                self.message = "otwieram chwytak"
                self._enter(ManipulationPhase.RELEASE, t, self._pose(self._plan["place_down"], GRIPPER_OPEN), duration=0.6)
        elif phase is ManipulationPhase.RELEASE:
            if self._seg.finished(t) and self._sustained(evidence.released, t, 0.2):
                self.grip = GripPhase.OPEN
                self.message = "odłożone"
                self._enter(ManipulationPhase.RETREAT, t, self._pose(self._plan["place_above"], GRIPPER_OPEN), duration=0.9)
        elif phase is ManipulationPhase.RETREAT and self._reached(t, q_meas):
            self.phase = ManipulationPhase.IDLE
            self._seg = None
            return ManipulationOutput(None, self.phase, self.grip, 1.0, self.message)
        elif phase is ManipulationPhase.FAILED and self._seg is not None and self._seg.finished(t) and t - self._t_phase > 1.7:
            if self.grip is GripPhase.LOST and evidence.released:
                self.grip = GripPhase.OPEN
            self.phase = ManipulationPhase.IDLE
            self._seg = None
            return ManipulationOutput(None, self.phase, self.grip, 1.0, self.message)
        target = self._seg.at(t) if self._seg is not None else self._last
        self._last = target.copy()
        careful = self.grip in (GripPhase.CONTACT, GripPhase.HOLDING)
        speed = 0.5 if careful else (1.0 if self.phase is ManipulationPhase.CLOSE else 0.7)
        return ManipulationOutput(target.copy(), self.phase, self.grip, speed, self.message)
