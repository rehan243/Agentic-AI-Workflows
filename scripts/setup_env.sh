#!/usr/bin/env bash
# bootstrap a machine for hacking on agent workflows without assuming docker
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
  echo "usage: $0 [--skip-models]"
  echo "  creates venv, installs python deps, optionally pulls small reference models"
}

SKIP_MODELS=0
for arg in "$@"; do
  case "$arg" in
    --skip-models) SKIP_MODELS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo -e "${RED}unknown arg:${NC} $arg"; usage; exit 1 ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}need python3 on PATH${NC}"; exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo -e "${YELLOW}creating venv${NC}"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo -e "${GREEN}upgrading pip${NC}"
python -m pip install -U pip wheel

echo -e "${GREEN}installing project deps${NC}"
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  pip install httpx pydantic python-dotenv openai langchain-core
fi

if [[ "$SKIP_MODELS" -eq 0 ]]; then
  echo -e "${YELLOW}downloading tiny reference weights (stub paths)${NC}"
  mkdir -p models/cache
  echo "put real wget/curl calls here for your org mirror"
fi

echo -e "${GREEN}done. activate with:${NC} source .venv/bin/activate"
