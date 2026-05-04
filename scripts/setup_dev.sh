#!/usr/bin/env bash
# 저장소 클론 후 다른 PC에서 개발 환경을 맞추는 스크립트 (macOS / Linux).
# 사용: 저장소 루트에서 ./scripts/setup_dev.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Repo root: $ROOT"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: '$1' 명령이 없습니다. 설치 후 다시 실행하세요." >&2
    exit 1
  }
}

need_cmd python3
PYTHON="$(command -v python3)"

echo "==> Backend: venv + pip"
cd "$ROOT/backend"
if [[ ! -d .venv ]]; then
  "$PYTHON" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

ENV_FILE="$ROOT/backend/.env"
EXAMPLE="$ROOT/backend/.env.example"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> backend/.env 생성 (예시 복사)"
  cp "$EXAMPLE" "$ENV_FILE"
fi

# PROJECT_ROOT를 현재 저장소 루트로 맞춤 (경로에 '|' 금지)
if grep -q '^PROJECT_ROOT=' "$ENV_FILE"; then
  tmp="$(mktemp)"
  sed "s|^PROJECT_ROOT=.*|PROJECT_ROOT=$ROOT|" "$ENV_FILE" >"$tmp"
  mv "$tmp" "$ENV_FILE"
else
  echo "PROJECT_ROOT=$ROOT" >>"$ENV_FILE"
fi

echo "==> Frontend: npm install (npm 있으면)"
cd "$ROOT/frontend"
if command -v npm >/dev/null 2>&1; then
  npm install
else
  echo "SKIP: npm 없음 — docs/setup-protocol.md 의「도구 설치」참고 후 npm install 실행"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "자동 설정 완료. 다음은 반드시 수동:"
echo ""
echo "  1) backend/.env 에 DATABASE_URL 설정 (Neon 또는 로컬 Postgres)"
echo "  2) 마이그레이션:"
echo "       cd backend && source .venv/bin/activate && alembic upgrade head"
echo "  3) (선택) 샘플 데이터:"
echo "       python scripts/seed_sample.py"
echo "  4) 백엔드 실행:"
echo "       uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  5) 프런트 실행 (다른 터미널):"
echo "       cd frontend && npm run dev"
echo ""
echo "문서: docs/setup-protocol.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
