# Zasoby dołączone do projektu

| Zasób | Źródło | Licencja | Zmiany |
|---|---|---|---|
| `so101/so101.xml`, `so101/assets/*.stl` | [google-deepmind/mujoco_menagerie `robotstudio_so101`](https://github.com/google-deepmind/mujoco_menagerie/tree/main/robotstudio_so101), commit `c96a32d28fb5da84da38c1da4d749e7a13212855` (23.09.2026), pochodna oficjalnego `so101_new_calib.xml` z [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101) | Apache-2.0 (`so101/LICENSE`) | brak; scena (podłoga, kostka, znacznik rozmówcy, światła) jest doklejana w kodzie przez `MjSpec` |
| `models/face_detection_yunet_2026may.onnx` | [opencv/opencv_zoo `face_detection_yunet`](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) | MIT (`models/LICENSE_YuNet.txt`) | brak; wersja z dynamicznym rozmiarem wejścia, wymagana przez OpenCV 5.x |

Model Menagerie ma prymitywne geometrie kolizji chwytaka i parametry kontaktu dobrane do manipulacji,
dlatego chwyt kostki działa w fizyce. Oryginalny plik TheRobotStudio (np. z projektu `SO_101_arm`)
można wskazać zmienną `MJCF_PATH`, ale jego kolizje chwytaka są siatkami i chwyt może być mniej stabilny.
