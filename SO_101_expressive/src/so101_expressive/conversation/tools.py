from __future__ import annotations

from ..behavior.expressive import GESTURES

GESTURE_NAMES = sorted(GESTURES)

TOOL_SPECS: dict[str, dict] = {
    "perform_gesture": {
        "description": (
            "Perform one short expressive arm gesture that fits what you are saying. "
            "Use at most one gesture per utterance. The safety system may refuse it."
        ),
        "params": {
            "gesture": GESTURE_NAMES,
            "intensity": ["subtle", "normal", "strong"],
        },
        "required": ["gesture"],
        "blocking": False,
    },
    "dance": {
        "description": "Do a gentle, safe dance with the arm, e.g. when music is playing and the user wants it.",
        "params": {"duration": ["short", "medium", "long"]},
        "required": [],
        "blocking": False,
    },
    "set_attention": {
        "description": "Look at the person (default) or rest your gaze for a while.",
        "params": {"target": ["person", "rest"]},
        "required": ["target"],
        "blocking": False,
    },
    "manipulate": {
        "description": (
            "Pick up the small orange cube in front of you or place it on the blue spot. "
            "Report the outcome only after the tool response arrives."
        ),
        "params": {"action": ["pick_cube", "place_cube"]},
        "required": ["action"],
        "blocking": False,
    },
    "stop_motion": {
        "description": "Stop gestures and tracking when the user asks you to stop moving.",
        "params": {},
        "required": [],
        "blocking": False,
    },
    "get_robot_state": {
        "description": "Get your true current body state before answering questions about what you are doing or holding.",
        "params": {},
        "required": [],
        "blocking": True,
    },
    "look_at_scene": {
        "description": "Take a fresh look through the laptop camera when the user asks what you see.",
        "params": {},
        "required": [],
        "blocking": True,
    },
}


# deklaracje funkcji dla live api zawierają wyłącznie wyliczenia, więc model nie może podać kątów ani prędkości
def function_declarations() -> list[dict]:
    out = []
    for name, spec in TOOL_SPECS.items():
        decl: dict = {"name": name, "description": spec["description"]}
        if spec["params"]:
            decl["parameters"] = {
                "type": "OBJECT",
                "properties": {k: {"type": "STRING", "enum": list(v)} for k, v in spec["params"].items()},
                "required": list(spec["required"]),
            }
        decl["behavior"] = "BLOCKING" if spec["blocking"] else "NON_BLOCKING"
        out.append(decl)
    return out


# walidacja odrzuca nieznane funkcje, nadmiarowe pola i wartości spoza wyliczeń zanim prośba dotrze do planisty
def validate_call(name: str, args: dict | None) -> tuple[bool, dict | str]:
    spec = TOOL_SPECS.get(name)
    if spec is None:
        return False, f"nieznana funkcja: {name}"
    args = dict(args or {})
    extra = set(args) - set(spec["params"])
    if extra:
        return False, f"niedozwolone argumenty: {sorted(extra)}"
    for key in spec["required"]:
        if key not in args:
            return False, f"brak wymaganego argumentu: {key}"
    clean: dict = {}
    for key, value in args.items():
        if not isinstance(value, str) or value not in spec["params"][key]:
            return False, f"niedozwolona wartość {key}={value!r}"
        clean[key] = value
    return True, clean


# sposób ogłoszenia wyniku przez model zależy od tego, czy czynność się udała i czy użytkownik czeka na raport
def response_scheduling(name: str, accepted: bool) -> str:
    if name in ("perform_gesture", "set_attention", "dance", "stop_motion") and accepted:
        return "SILENT"
    return "WHEN_IDLE"
