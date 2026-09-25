from __future__ import annotations

import threading
from dataclasses import dataclass

import mujoco
import numpy as np

from .limits import ARM_JOINTS, ELBOW, JOINT_NAMES, LIFT, PAN, WRIST_FLEX

Z_MIN_BY_MODE = {"expressive": 0.07, "manipulation": 0.004}


# wynik ik zawiera błędy, aby planista mógł odrzucić nieosiągalny cel zamiast go wymuszać
@dataclass(frozen=True)
class IkResult:
    q_arm: np.ndarray
    pos_err: float
    ang_err_deg: float
    ok: bool


# kinematyka działa na osobnej kopii danych mujoco, żeby obliczenia nie zaburzały trwającej symulacji
class So101Kinematics:
    # wyszukujemy przeguby i punkty kontrolne po nazwach, więc działa też podmieniony plik mjcf so-101
    def __init__(self, model: mujoco.MjModel, site: str = "gripperframe") -> None:
        self.model = model
        self.data = mujoco.MjData(model)
        self._lock = threading.Lock()
        self.site_id = model.site(site).id
        self.qadr = np.array([model.joint(n).qposadr[0] for n in JOINT_NAMES])
        self.dofadr = np.array([model.joint(n).dofadr[0] for n in JOINT_NAMES])
        arm_ids = [model.joint(JOINT_NAMES[i]).id for i in ARM_JOINTS]
        self.arm_lo = model.jnt_range[arm_ids, 0].copy()
        self.arm_hi = model.jnt_range[arm_ids, 1].copy()
        self.shoulder_x = float(self._body_pos_at_zero("shoulder")[0])
        self.check_bodies = [
            model.body(n).id
            for n in ("lower_arm", "wrist", "gripper", "moving_jaw_so101_v1")
            if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, n) >= 0
        ]
        self.check_geoms = [
            model.geom(n).id
            for n in ("fixed_jaw_sph_tip1", "moving_jaw_sph_tip1")
            if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n) >= 0
        ]

    # położenie barku w pozycji zerowej daje oś obrotu podstawy dla obliczeń kierunku patrzenia
    def _body_pos_at_zero(self, name: str) -> np.ndarray:
        with self._lock:
            self.data.qpos[:] = self.model.qpos0
            mujoco.mj_kinematics(self.model, self.data)
            return self.data.xpos[self.model.body(name).id].copy()

    # wspólne ładowanie konfiguracji utrzymuje spójność fk, jakobianu i sprawdzania wysokości
    def _load(self, q6: np.ndarray) -> None:
        self.data.qpos[:] = self.model.qpos0
        self.data.qpos[self.qadr] = q6
        mujoco.mj_kinematics(self.model, self.data)
        mujoco.mj_comPos(self.model, self.data)

    # pozycja i orientacja punktu chwytaka są potrzebne do śledzenia, gestów i manipulacji
    def fk(self, q6: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        with self._lock:
            self._load(np.asarray(q6, dtype=float))
            return self.data.site_xpos[self.site_id].copy(), self.data.site_xmat[self.site_id].reshape(3, 3).copy()

    # najniższy punkt ramienia pozwala zablokować ruch, który wbiłby chwytak w blat
    def min_height(self, q6: np.ndarray) -> float:
        with self._lock:
            self._load(np.asarray(q6, dtype=float))
            zs = [self.data.site_xpos[self.site_id][2]]
            zs.extend(self.data.xpos[b][2] for b in self.check_bodies)
            zs.extend(self.data.geom_xpos[g][2] for g in self.check_geoms)
            return float(min(zs))

    # zapas wysokości nad blatem pozwala sterownikowi zatrzymać ruch w dół, ale nie blokuje wyjazdu w górę
    def clearance(self, q6: np.ndarray, mode: str = "expressive") -> float:
        return self.min_height(q6) - Z_MIN_BY_MODE.get(mode, Z_MIN_BY_MODE["expressive"])

    # prosta odpowiedź tak lub nie jest wygodna w testach i przy walidacji póz gestów
    def pose_is_safe(self, q6: np.ndarray, mode: str = "expressive") -> bool:
        return self.clearance(q6, mode) >= 0.0

    # ik z tłumieniem wybiera rozwiązanie najbliższe konfiguracji odniesienia, bo symetryczny chwytak ma dwie równoważne gałęzie obrotu
    def ik(
        self,
        target: np.ndarray,
        approach: np.ndarray | None = None,
        close_dirs: list[np.ndarray] | None = None,
        seeds: list[np.ndarray] | None = None,
        iters: int = 150,
        w_rot: float = 0.5,
        pos_tol: float = 0.004,
        ang_tol_deg: float = 8.0,
        prefer: np.ndarray | None = None,
        w_prefer: float = 0.02,
    ) -> IkResult:
        target = np.asarray(target, dtype=float)
        seeds = seeds or [np.zeros(5), np.array([0.0, 0.0, 0.5, 1.0, 0.0]), np.array([0.0, -0.5, 1.0, 1.0, 1.5])]
        if prefer is not None:
            seeds = [np.asarray(prefer, dtype=float)[:5]] + list(seeds)
        best: IkResult | None = None
        best_cost = float("inf")
        with self._lock:
            for seed in seeds:
                q = np.clip(np.asarray(seed, dtype=float).copy(), self.arm_lo, self.arm_hi)
                for _ in range(iters):
                    q6 = np.zeros(6)
                    q6[:5] = q
                    self._load(q6)
                    p = self.data.site_xpos[self.site_id]
                    rot = self.data.site_xmat[self.site_id].reshape(3, 3)
                    jp = np.zeros((3, self.model.nv))
                    jr = np.zeros((3, self.model.nv))
                    mujoco.mj_jacSite(self.model, self.data, jp, jr, self.site_id)
                    errs = [target - p]
                    jacs = [jp[:, self.dofadr[:5]]]
                    if approach is not None:
                        errs.append(w_rot * np.cross(rot[:, 0], approach))
                        jacs.append(w_rot * jr[:, self.dofadr[:5]])
                    if close_dirs:
                        z = rot[:, 2]
                        c = max(close_dirs, key=lambda v: abs(float(np.dot(v, z))))
                        c = c * np.sign(np.dot(c, z))
                        errs.append(w_rot * np.cross(z, c))
                        jacs.append(w_rot * jr[:, self.dofadr[:5]])
                    e = np.concatenate(errs)
                    jac = np.vstack(jacs)
                    lam = 1e-4 + 1e-2 * float(np.dot(e, e))
                    dq = jac.T @ np.linalg.solve(jac @ jac.T + lam * np.eye(len(e)), e)
                    q = np.clip(q + dq, self.arm_lo, self.arm_hi)
                q6 = np.zeros(6)
                q6[:5] = q
                self._load(q6)
                p = self.data.site_xpos[self.site_id]
                rot = self.data.site_xmat[self.site_id].reshape(3, 3)
                pos_err = float(np.linalg.norm(target - p))
                ang = 0.0
                if approach is not None:
                    ang = float(np.degrees(np.arccos(np.clip(np.dot(rot[:, 0], approach), -1.0, 1.0))))
                ok = pos_err <= pos_tol and ang <= ang_tol_deg
                cand = IkResult(q.copy(), pos_err, ang, ok)
                cost = pos_err + 0.001 * ang
                if prefer is not None:
                    cost += w_prefer * float(np.linalg.norm(q - np.asarray(prefer, dtype=float)[:5]))
                if best is None or (cand.ok and not best.ok) or (cand.ok == best.ok and cost < best_cost):
                    best = cand
                    best_cost = cost
        assert best is not None
        return best

    # śledzenie wzrokiem używa obrotu podstawy i pochylenia nadgarstka, bo so-101 nie ma osobnej głowy
    def gaze(self, target: np.ndarray, posture: np.ndarray) -> tuple[float, float]:
        target = np.asarray(target, dtype=float)
        pan = -float(np.arctan2(target[1], target[0] - self.shoulder_x))
        q6 = np.asarray(posture, dtype=float).copy()
        q6[PAN] = pan
        q6[WRIST_FLEX] = 0.0
        with self._lock:
            self._load(q6)
            wrist = self.data.xpos[self.model.body("wrist").id].copy()
        horiz = float(np.hypot(target[0] - wrist[0], target[1] - wrist[1]))
        elevation = float(np.arctan2(target[2] - wrist[2], max(horiz, 0.05)))
        wrist_flex = -elevation - (q6[LIFT] + q6[ELBOW])
        return pan, wrist_flex
