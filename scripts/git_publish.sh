#!/usr/bin/env bash
# GitHub 등 origin 으로 main(또는 현재 브랜치) 푸시 — 원격만 있으면 한 번에 실행.
# 사용: 저장소 루트에서 ./scripts/git_publish.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [[ -z "${BRANCH}" ]]; then
  echo "ERROR: 브랜치를 확인할 수 없습니다." >&2
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  cat >&2 <<'EOF'
ERROR: git remote origin 이 설정되어 있지 않습니다.

[한 번만] GitHub에서 빈 저장소를 만든 뒤(README 추가 안 함):

  git remote add origin https://github.com/<계정>/<저장소>.git

또는 SSH:

  git remote add origin git@github.com:<계정>/<저장소>.git

그 다음 다시:

  ./scripts/git_publish.sh
EOF
  exit 1
fi

echo "==> git push origin ${BRANCH}"
git push -u origin "${BRANCH}"
echo "==> 완료: 원격과 동기화됨 (${BRANCH})"
