from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

RATE = 16000


# nagranie jest przeliczane na mono 16 khz i normalizowane do typowego poziomu mikrofonu
def load(path: Path, max_s: float) -> np.ndarray:
    if path.suffix.lower() == ".wav":
        with wave.open(str(path)) as wf:
            sr = wf.getframerate()
            data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
            if wf.getnchannels() > 1:
                data = data.reshape(-1, wf.getnchannels()).mean(axis=1)
    else:
        import soundfile as sf

        data, sr = sf.read(str(path), dtype="float32")
        data = data.mean(axis=1) if data.ndim > 1 else data
    data = data[: int(max_s * sr)]
    y = np.interp(np.arange(int(data.size * RATE / sr)) * (sr / RATE), np.arange(data.size), data)
    return (y / (np.max(np.abs(y)) + 1e-9) * 0.3 * 32767).astype(np.int16)


# przebieg detektora zwraca odsetek ocen z muzyką i czas pierwszego wykrycia
def evaluate(samples: np.ndarray) -> tuple[float, float | None, float]:
    from so101_expressive.inputs.music import MusicDetector

    det = MusicDetector(RATE)
    states, first = [], None
    for i in range(0, samples.size - 512, 512):
        st = det.update(samples[i : i + 512], own_playback=False)
        if st.evaluated:
            states.append(st.music)
        if st.music and first is None:
            first = i / RATE
    return (float(np.mean(states)) if states else 0.0), first, det.bpm


# raport pozwala sprawdzić detektor na własnych nagraniach, np. z mikrofonu macbooka w pokoju
def main() -> None:
    parser = argparse.ArgumentParser(description="Ewaluacja detektora muzyki na plikach audio")
    parser.add_argument("--music", nargs="*", type=Path, default=[], help="pliki z muzyką")
    parser.add_argument("--other", nargs="*", type=Path, default=[], help="pliki bez muzyki: mowa, szum, cisza")
    parser.add_argument("--max-seconds", type=float, default=30.0)
    args = parser.parse_args()
    rows = [("muzyka", p) for p in args.music] + [("inne", p) for p in args.other]
    if not rows:
        parser.error("podaj pliki przez --music i/lub --other")
    hits = false_alarms = 0
    for label, path in rows:
        frac, first, bpm = evaluate(load(path, args.max_seconds))
        detected = frac > 0.3
        hits += int(detected and label == "muzyka")
        false_alarms += int(detected and label == "inne")
        first_s = f"{first:5.1f} s" if first is not None else "   -   "
        print(f"{label:7s} {path.name[:50]:50s} muzyka w {frac * 100:3.0f}% ocen, pierwsze wykrycie {first_s}, tempo {bpm:4.0f}")
    print(f"\nwykryta muzyka: {hits}/{len(args.music)}, fałszywe alarmy: {false_alarms}/{len(args.other)}")


if __name__ == "__main__":
    main()
