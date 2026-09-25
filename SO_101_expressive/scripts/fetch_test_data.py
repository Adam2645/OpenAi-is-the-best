from __future__ import annotations

import argparse
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tests" / "data" / "downloaded"
USER_AGENT = "SO101-expressive-tests/0.1 (local test data download)"
PORTRAIT_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Neil_Armstrong_pose.jpg/960px-Neil_Armstrong_pose.jpg"
LIBROSA_BASE = "https://librosa.org/data/audio/"
LIBROSA_CLIPS = {
    "music": [
        "Kevin_MacLeod_-_Vibe_Ace", "admiralbob77_-_Choice_-_Drum-bass",
        "Kevin_MacLeod_-_P_I_Tchaikovsky_Dance_of_the_Sugar_Plum_Fairy",
        "Hungarian_Dance_number_5_-_Allegro_in_F_sharp_minor_(string_orchestra)",
        "Karissa_Hobbs_-_Let's_Go_Fishin'", "147793__setuniman__sweet-waltz-0i-22mi",
        "442789__lena-orsa__happy-music-pistachio-ice-cream-ragtime",
    ],
    "speech": ["5703-47212-0000", "3436-172162-0000", "198-209-0000"],
}


# pobranie z nagłówkiem user-agent, którego wymaga wikimedia, bez nadpisywania istniejących plików
def fetch(url: str, target: Path) -> None:
    if target.exists():
        print("jest:", target.name)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        target.write_bytes(response.read())
    print("pobrano:", target.name)


# portret z domeny publicznej i nagrania na licencjach cc służą tylko do lokalnych testów, nie są dołączane do projektu
def main() -> None:
    parser = argparse.ArgumentParser(description="Pobiera dane do testów detektora twarzy i muzyki")
    parser.add_argument("--audio", action="store_true", help="pobierz także przykładowe nagrania muzyki i mowy (librosa)")
    args = parser.parse_args()
    fetch(PORTRAIT_URL, ROOT / "portrait_public_domain.jpg")
    if args.audio:
        for label, names in LIBROSA_CLIPS.items():
            for name in names:
                safe = "".join(ch for ch in name if ch not in "'()")
                fetch(LIBROSA_BASE + urllib.parse.quote(name) + ".hq.ogg", ROOT / "audio" / f"{label}__{safe}.ogg")


if __name__ == "__main__":
    main()
