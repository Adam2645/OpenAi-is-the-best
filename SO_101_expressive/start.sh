#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  if command -v uv >/dev/null 2>&1; then
    echo "Tworzę środowisko .venv (uv, Python 3.12)..."
    uv venv -q .venv --python 3.12
  else
    PY="${PYTHON:-python3}"
    if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      echo "Potrzebny jest Python 3.10+ albo uv. Zainstaluj: brew install uv  (lub: brew install python@3.12)" >&2
      exit 1
    fi
    echo "Tworzę środowisko .venv ($("$PY" --version))..."
    "$PY" -m venv .venv
  fi
fi

if [ ! -f .venv/.deps-ok ] || [ pyproject.toml -nt .venv/.deps-ok ]; then
  echo "Instaluję zależności..."
  if command -v uv >/dev/null 2>&1; then
    VIRTUAL_ENV="$PWD/.venv" uv pip install -q -e ".[dev]"
  else
    .venv/bin/python -m pip install -q --upgrade pip
    .venv/bin/python -m pip install -q -e ".[dev]"
  fi
  touch .venv/.deps-ok
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Utworzono .env z .env.example - wpisz GEMINI_API_KEY, aby włączyć rozmowę z Gemini (bez klucza działa tryb lokalny)."
fi

exec .venv/bin/python -m so101_expressive "$@"
