# Backend — Daily Productivity Planner

FastAPI + SQLAlchemy + Alembic + PostgreSQL.

데이터베이스는 **로컬 Postgres 대신 Neon(호스티드 PostgreSQL)** 사용을 권장합니다. 코드 수정 없이 `DATABASE_URL`만 Neon에서 발급받은 값으로 바꿉니다.

## 준비

1. 가상환경 및 패키지:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

1. 환경 변수:

```bash
cp .env.example .env
```

- `**DATABASE_URL**`: Neon 대시보드의 연결 문자열(없으면 끝에 `?sslmode=require` 추가).  
- `**PROJECT_ROOT**`: 저장소 루트 디렉터리 절대 경로 (`daily/`, `reports/` 가 있는 폴더).

1. 마이그레이션:

```bash
alembic upgrade head
```

1. (선택) 샘플 데이터:

```bash
python scripts/seed_sample.py
```

## 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 이미지

저장소 `backend/Dockerfile` 로 빌드할 수 있습니다(`uvicorn` 은 `--host 0.0.0.0`). 런타임 변수는 `DATABASE_URL`, `PROJECT_ROOT`, `CORS_ORIGINS` 등 `.env.example` 과 동일합니다. SPA와 오리진이 다르면 `**CORS_ORIGINS**` 에 브라우저 접속 오리진을 쉼표로 명시합니다.

API 문서: [http://localhost:8000/docs](http://localhost:8000/docs)

## Neon 참고

- 프로젝트: [https://neon.tech](https://neon.tech)  
- 마이그레이션 중 연결 문제가 있으면 Neon에서 제공하는 **Direct** 연결 URI로 `DATABASE_URL`을 바꿔 `alembic upgrade head`만 다시 실행해 보세요.

