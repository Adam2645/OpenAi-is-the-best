from __future__ import annotations

import mujoco
import numpy as np

from .mujoco_sim import MujocoSim


# renderer poza ekranem pozwala złożyć podgląd symulacji z kamerą w jednym oknie opencv na macos
class SimRenderer:
    # kontekst gl powstaje w wątku interfejsu, bo tam też będzie używany
    def __init__(self, sim: MujocoSim, width: int = 640, height: int = 480) -> None:
        self.sim = sim
        self.renderer = mujoco.Renderer(sim.model, height, width)
        self.cam = mujoco.MjvCamera()
        self.reset_view()

    # domyślny widok obejmuje ramię, kostkę i znacznik rozmówcy
    def reset_view(self) -> None:
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.cam.lookat[:] = [0.42, 0.0, 0.22]
        self.cam.distance = 1.35
        self.cam.azimuth = 115.0
        self.cam.elevation = -16.0

    # obrót kamery myszą lub klawiszami zastępuje interaktywny viewer, który na macos wymaga mjpython
    def orbit(self, d_azimuth: float, d_elevation: float) -> None:
        self.cam.azimuth = (self.cam.azimuth + d_azimuth) % 360.0
        self.cam.elevation = float(np.clip(self.cam.elevation + d_elevation, -85.0, 5.0))

    # przybliżanie pozwala obejrzeć chwyt kostki z bliska
    def zoom(self, factor: float) -> None:
        self.cam.distance = float(np.clip(self.cam.distance * factor, 0.35, 3.0))

    # render czyta dane symulacji pod blokadą, żeby nie trafić w połowę kroku fizyki
    def render(self) -> np.ndarray:
        with self.sim.lock:
            self.renderer.update_scene(self.sim.data, camera=self.cam)
        return self.renderer.render()

    # zamknięcie zwalnia kontekst gl przed zakończeniem programu
    def close(self) -> None:
        self.renderer.close()
