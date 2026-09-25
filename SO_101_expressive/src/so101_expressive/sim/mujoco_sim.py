from __future__ import annotations

import threading
from pathlib import Path

import mujoco
import numpy as np

from ..motion.limits import GRIPPER, JOINT_NAMES
from ..state import GripEvidence, PersonStatus

CUBE_HALF = 0.015
DEFAULT_CUBE_POS = (0.20, 0.10, CUBE_HALF)
DEFAULT_PLACE_POS = (0.20, -0.10, CUBE_HALF)
MARKER_RGBA = {
    PersonStatus.TRACKED: (0.20, 0.85, 0.35, 0.30),
    PersonStatus.ACQUIRING: (0.95, 0.85, 0.20, 0.25),
    PersonStatus.UNCERTAIN: (0.95, 0.55, 0.10, 0.25),
    PersonStatus.ABSENT: (0.50, 0.50, 0.50, 0.0),
}


# scenę doklejamy programowo, więc działa z dowolnym plikiem mjcf so-101 bez zmieniania oryginału
def build_scene_spec(mjcf_path: Path, cube_pos=DEFAULT_CUBE_POS, place_pos=DEFAULT_PLACE_POS) -> mujoco.MjSpec:
    spec = mujoco.MjSpec.from_file(str(mjcf_path))
    spec.add_texture(
        name="scene_grid",
        type=mujoco.mjtTexture.mjTEXTURE_2D,
        builtin=mujoco.mjtBuiltin.mjBUILTIN_CHECKER,
        rgb1=[0.22, 0.30, 0.38],
        rgb2=[0.14, 0.20, 0.27],
        width=300,
        height=300,
        mark=mujoco.mjtMark.mjMARK_EDGE,
        markrgb=[0.7, 0.7, 0.7],
    )
    spec.add_texture(
        name="scene_sky",
        type=mujoco.mjtTexture.mjTEXTURE_SKYBOX,
        builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT,
        rgb1=[0.35, 0.50, 0.65],
        rgb2=[0.05, 0.05, 0.08],
        width=512,
        height=3072,
    )
    grid = spec.add_material(name="scene_grid", texrepeat=[8, 8], texuniform=True, reflectance=0.15)
    textures = list(grid.textures)
    textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "scene_grid"
    grid.textures = textures
    world = spec.worldbody
    world.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[0, 0, 0.05], material="scene_grid")
    world.add_light(pos=[0.3, -0.4, 1.6], dir=[-0.2, 0.3, -1.0], type=mujoco.mjtLightType.mjLIGHT_DIRECTIONAL)
    world.add_light(pos=[0.8, 0.6, 1.2], dir=[-0.5, -0.4, -1.0], type=mujoco.mjtLightType.mjLIGHT_SPOT, castshadow=False)
    cube = world.add_body(name="cube", pos=list(cube_pos))
    cube.add_freejoint(name="cube_free")
    cube.add_geom(
        name="cube_geom",
        type=mujoco.mjtGeom.mjGEOM_BOX,
        size=[CUBE_HALF] * 3,
        mass=0.03,
        rgba=[0.92, 0.35, 0.12, 1.0],
        friction=[1.0, 0.02, 0.002],
        condim=4,
        solref=[0.01, 1.0],
    )
    place = world.add_body(name="place_target", pos=[place_pos[0], place_pos[1], 0.0005])
    place.add_geom(
        type=mujoco.mjtGeom.mjGEOM_CYLINDER,
        size=[0.028, 0.0005, 0],
        rgba=[0.2, 0.6, 1.0, 0.5],
        contype=0,
        conaffinity=0,
    )
    marker = world.add_body(name="person_marker", pos=[0.75, 0.0, 0.35], mocap=True)
    marker.add_geom(
        name="person_marker_geom",
        type=mujoco.mjtGeom.mjGEOM_ELLIPSOID,
        size=[0.07, 0.07, 0.09],
        rgba=list(MARKER_RGBA[PersonStatus.ABSENT]),
        contype=0,
        conaffinity=0,
    )
    world.add_camera(name="overview", pos=[0.95, 0.75, 0.55], xyaxes=[-0.62, 0.78, 0, -0.30, -0.24, 0.92])
    return spec


# adapter izoluje resztę programu od api mujoco, żeby później podmienić go na sterownik prawdziwych serw
class MujocoSim:
    # identyfikatory ciał i przegubów ustalamy po nazwach raz przy starcie, by kroki symulacji były tanie
    def __init__(
        self,
        mjcf_path: Path,
        cube_pos=DEFAULT_CUBE_POS,
        place_pos=DEFAULT_PLACE_POS,
    ) -> None:
        spec = build_scene_spec(Path(mjcf_path), cube_pos, place_pos)
        self.model = spec.compile()
        self.data = mujoco.MjData(self.model)
        self.lock = threading.RLock()
        self.qadr = np.array([self.model.joint(n).qposadr[0] for n in JOINT_NAMES])
        self.dofadr = np.array([self.model.joint(n).dofadr[0] for n in JOINT_NAMES])
        self.act = np.array([self.model.actuator(n).id for n in JOINT_NAMES])
        self.site_id = self.model.site("gripperframe").id
        self.cube_body = self.model.body("cube").id
        self.cube_qadr = self.model.joint("cube_free").qposadr[0]
        self.cube_dofadr = self.model.joint("cube_free").dofadr[0]
        self.floor_geom = self.model.geom("floor").id
        self.moving_jaw_body = int(self.model.jnt_bodyid[self.model.joint("gripper").id])
        self.fixed_jaw_body = int(self.model.body_parentid[self.moving_jaw_body])
        self.marker_mocap = int(self.model.body("person_marker").mocapid[0])
        self.marker_geom = self.model.geom("person_marker_geom").id
        self.initial_cube_pos = np.array(cube_pos, dtype=float)
        self.place_pos = np.array(place_pos, dtype=float)
        self._force = np.zeros(6)

    # reset ustawia ramię i kostkę w znanej pozycji, co jest potrzebne w testach i po awarii fizyki
    def reset(self, q6: np.ndarray) -> None:
        with self.lock:
            mujoco.mj_resetData(self.model, self.data)
            self.data.qpos[self.qadr] = q6
            self.data.ctrl[self.act] = q6
            self._place_cube(self.initial_cube_pos)
            mujoco.mj_forward(self.model, self.data)

    # kostka wraca na start bez resetu ramienia, aby można było powtarzać chwyt w demie
    def reset_cube(self, pos: np.ndarray | None = None) -> None:
        with self.lock:
            self._place_cube(self.initial_cube_pos if pos is None else np.asarray(pos, dtype=float))
            mujoco.mj_forward(self.model, self.data)

    # wspólne ustawienie pozy kostki wraz z wyzerowaniem prędkości zapobiega jej wyrzuceniu
    def _place_cube(self, pos: np.ndarray) -> None:
        self.data.qpos[self.cube_qadr : self.cube_qadr + 3] = pos
        self.data.qpos[self.cube_qadr + 3 : self.cube_qadr + 7] = [1.0, 0.0, 0.0, 0.0]
        self.data.qvel[self.cube_dofadr : self.cube_dofadr + 6] = 0.0

    # polecenia trafiają do aktuatorów pozycyjnych jak w serwach sts3215 prawdziwego ramienia
    def apply(self, q_cmd: np.ndarray) -> None:
        with self.lock:
            self.data.ctrl[self.act] = q_cmd

    # fizyka kroczy krótszymi podkrokami niż pętla sterowania, aby kontakt chwytu był stabilny
    def step(self, duration: float) -> None:
        n = max(1, int(round(duration / self.model.opt.timestep)))
        with self.lock:
            for _ in range(n):
                mujoco.mj_step(self.model, self.data)
            if not np.all(np.isfinite(self.data.qpos)):
                raise FloatingPointError("symulacja stała się niestabilna")

    # zmierzone pozycje przegubów zamykają pętlę dla sterownika i dla weryfikacji dojazdu
    def joint_q(self) -> np.ndarray:
        with self.lock:
            return self.data.qpos[self.qadr].copy()

    # położenie punktu chwytaka służy do sprawdzenia, czy obiekt faktycznie jedzie razem z nim
    def tcp_position(self) -> np.ndarray:
        with self.lock:
            return self.data.site_xpos[self.site_id].copy()

    # położenie kostki z symulacji zastępuje percepcję obiektu, której na tym etapie nie budujemy
    def cube_position(self) -> np.ndarray:
        with self.lock:
            return self.data.xpos[self.cube_body].copy()

    # dowód chwytu wynika z sił kontaktu obu szczęk, blokady chwytaka i uniesienia kostki
    def grasp_evidence(self, gripper_cmd: float) -> GripEvidence:
        with self.lock:
            fixed = moving = floor = 0.0
            for i in range(self.data.ncon):
                con = self.data.contact[i]
                b1 = int(self.model.geom_bodyid[con.geom1])
                b2 = int(self.model.geom_bodyid[con.geom2])
                if self.cube_body not in (b1, b2):
                    continue
                other_body = b2 if b1 == self.cube_body else b1
                other_geom = con.geom2 if b1 == self.cube_body else con.geom1
                mujoco.mj_contactForce(self.model, self.data, i, self._force)
                normal = abs(float(self._force[0]))
                if other_body == self.fixed_jaw_body:
                    fixed += normal
                elif other_body == self.moving_jaw_body:
                    moving += normal
                elif other_geom == self.floor_geom:
                    floor += normal
            q_grip = float(self.data.qpos[self.qadr[GRIPPER]])
            cube = self.data.xpos[self.cube_body]
            tcp = self.data.site_xpos[self.site_id]
            blocked = (q_grip - gripper_cmd) > 0.08
            lifted = floor < 1e-6 and cube[2] > CUBE_HALF + 0.01
            attached = float(np.linalg.norm(cube - tcp)) < 0.035
        both = fixed > 0.5 and moving > 0.5
        confidence = 0.0
        if both and blocked:
            confidence = 0.6
            if lifted and attached:
                confidence = 0.97
        return GripEvidence("physics", fixed, moving, blocked, lifted, attached, confidence)

    # znacznik rozmówcy w scenie pokazuje, gdzie robot sądzi, że jest osoba i jak pewna jest detekcja
    def set_person_marker(self, pos: tuple[float, float, float] | None, status: PersonStatus) -> None:
        with self.lock:
            if pos is not None:
                self.data.mocap_pos[self.marker_mocap] = pos
            rgba = MARKER_RGBA[status] if pos is not None else MARKER_RGBA[PersonStatus.ABSENT]
            self.model.geom_rgba[self.marker_geom] = rgba
