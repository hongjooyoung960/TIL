# Backend — Daily Productivity Planner

FastAPI + SQLAlchemy + Alembic + PostgreSQL.

데이터베이스는 **로컬 Postgres 대신 Neon(호스티드 PostgreSQL)** 사용을 권장합니다. 코드 수정 없이 `DATABASE_URL`만 Neon에서 발급받은 값으로 바꿉니다.

Neon CLI(MCP·스킬 설치 마법사)는 **저장소 루트**에서 `npm run neon:init` (`npx neonctl@latest init` 와 동일) — 대화형이므로 로컬 터미널에서 실행하세요.

## 준비

1. 가상환경 및 패키지:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. 환경 변수:

```bash
cp .env.example .env
```

- **`DATABASE_URL`**: Neon 대시보드의 연결 문자열(없으면 끝에 `?sslmode=require` 추가).  
- **`PROJECT_ROOT`**: 저장소 루트 디렉터리 절대 경로 (`daily/`, `reports/` 가 있는 폴더).

3. 마이그레이션:

```bash
alembic upgrade head
```

4. (선택) 샘플 데이터:

```bash
python scripts/seed_sample.py
```

## 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서: http://localhost:8000/docs

## Neon 참고

- 프로젝트: https://neon.tech  
- 마이그레이션 중 연결 문제가 있으면 Neon에서 제공하는 **Direct** 연결 URI로 `DATABASE_URL`을 바꿔 `alembic upgrade head`만 다시 실행해 보세요.
