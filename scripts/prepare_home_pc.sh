#!/usr/bin/env bash
# 집 PC 등 새 환경에서: 저장소 받은 직후 한 번 실행 (setup_dev.sh 래퍼 + 안내).
# 사용: 저장소 루트에서 ./scripts/prepare_home_pc.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cat <<'EOF'

╔════════════════════════════════════════════════════════════╗
║  집 PC · 새 컴퓨터 준비 (자동 가능한 부분만 실행합니다)      ║
╚════════════════════════════════════════════════════════════╝

다음으로 진행합니다:
  • Python 가상환경 + 패키지 설치 (backend)
  • backend/.env 없으면 생성 + PROJECT_ROOT 자동 설정
  • npm 있으면 frontend 의존성 설치

그 다음은 반드시 직접:
  • backend/.env 에 DATABASE_URL (Neon 또는 로컬 Postgres)
  • alembic upgrade head → 서버 실행

자세한 순서: docs/setup-protocol.md

EOF

chmod +x "$ROOT/scripts/setup_dev.sh" "$ROOT/scripts/git_publish.sh" 2>/dev/null || true
exec "$ROOT/scripts/setup_dev.sh"
