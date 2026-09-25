from __future__ import annotations

from pathlib import Path

import pytest

from so101_expressive.inputs.face import Face, FaceDetector, FaceTracker
from so101_expressive.state import PersonStatus

PORTRAIT = Path(__file__).parent / "data" / "downloaded" / "portrait_public_domain.jpg"


# pewna twarz w środku kadru
def face(x=0.45, score=0.95):
    return Face(x, 0.3, 0.12, 0.16, score)


# śledzenie rusza dopiero po kilku pewnych klatkach, a nie po pierwszej detekcji
def test_acquisition_needs_several_confident_frames():
    tr = FaceTracker(acquire_frames=3)
    statuses = [tr.update([face()], t * 0.066).status for t in range(4)]
    assert statuses[:2] == [PersonStatus.ACQUIRING, PersonStatus.ACQUIRING]
    assert statuses[2] is PersonStatus.TRACKED


# niepewne detekcje przechodzą w stan niepewny, a dłuższy brak w nieobecność
def test_low_confidence_becomes_uncertain_then_absent():
    tr = FaceTracker()
    t = 0.0
    for _ in range(4):
        tr.update([face()], t)
        t += 0.066
    seen = []
    for _ in range(30):
        seen.append(tr.update([face(score=0.3)], t).status)
        t += 0.066
    assert PersonStatus.UNCERTAIN in seen and seen[-1] is PersonStatus.ABSENT
    assert seen[0] is PersonStatus.TRACKED


# nagły skok twarzy przez pół kadru wymusza ponowne potwierdzenie zamiast gwałtownego obrotu
def test_large_jump_requires_reacquisition():
    tr = FaceTracker()
    t = 0.0
    for _ in range(4):
        tr.update([face(0.1)], t)
        t += 0.066
    assert tr.update([face(0.8)], t).status is PersonStatus.ACQUIRING


# detektor yunet na prawdziwym portrecie z domeny publicznej, pobieranym skryptem fetch_test_data
@pytest.mark.skipif(not PORTRAIT.exists(), reason="uruchom scripts/fetch_test_data.py, aby pobrać portret testowy")
def test_yunet_detects_real_face_and_ignores_blank(settings):
    import cv2
    import numpy as np

    det = FaceDetector(settings.resolve_path(settings.face_model_path))
    faces = det.detect(cv2.imread(str(PORTRAIT)))
    assert len(faces) == 1 and faces[0].score > 0.85
    assert det.detect(np.zeros((480, 640, 3), dtype=np.uint8)) == []
