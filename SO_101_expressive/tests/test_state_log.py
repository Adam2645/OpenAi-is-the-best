from __future__ import annotations

import json

from so101_expressive.app import StateLogWriter
from so101_expressive.state import RobotState, StateJournal


# przełącza jedno pole stanu, tworząc dokładnie jedną zmianę w dzienniku
def toggle(journal: StateJournal, state: RobotState, t: float) -> None:
    state.t = t
    state.music = not state.music
    journal.observe(state)


# odczyt wierszy pliku dziennika jako słowników ułatwia asercje na jego treści
def rows(writer: StateLogWriter) -> list[dict]:
    return [json.loads(line) for line in writer.path.read_text(encoding="utf-8").splitlines()]


# zapis trwa po zapełnieniu ograniczonego dziennika, bo postęp liczy licznik zmian, a nie długość listy
def test_log_keeps_writing_after_journal_is_full(tmp_path):
    journal = StateJournal(maxlen=10)
    writer = StateLogWriter(tmp_path)
    state = RobotState()
    journal.observe(state)
    for i in range(25):
        toggle(journal, state, i * 0.1)
        writer.write(journal)
    written = rows(writer)
    assert len(written) == 25
    assert written[-1]["pole"] == "music" and written[-1]["t"] == round(24 * 0.1, 3)


# gdy zapis nie nadąża za dziennikiem, plik dostaje jawny wpis o liczbie utraconych zmian zamiast cichej luki
def test_log_marks_lost_entries_when_writer_falls_behind(tmp_path):
    journal = StateJournal(maxlen=10)
    writer = StateLogWriter(tmp_path)
    state = RobotState()
    journal.observe(state)
    for i in range(30):
        toggle(journal, state, i * 0.1)
    writer.write(journal)
    written = rows(writer)
    assert written[0]["pole"] == "pominięte wpisy" and written[0]["na"] == "20"
    assert len(written) == 11
    writer.write(journal)
    assert len(rows(writer)) == 11
