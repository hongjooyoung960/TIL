# Daily Productivity Planner

일간·주간 계획, 목표 계층, 기상/취침 기록, 가중 성취율, 파일 리포트 생성, 로컬 Git 커밋·push까지 포함한 풀스택 MVP입니다.

> **경로 안내:** 요청하신 Windows 경로는 `C:\work\productivity-planner` 입니다. 이 작업은 macOS 에이전트 환경에서 동일 구조로 생성되었으며, 로컬 경로는 `/Users/skku_aws2_23/work/productivity-planner` 입니다. Windows에서는 해당 폴더를 만들고 이 저장소 내용을 그대로 두면 됩니다.

## 기능 개요

1. 일간 플래너 — 기상/취침, 메인 목표, 활동 CRUD, 가중 성취율 진행 바  
2. 주간 플래너 — 주차별 평균 성취율, 카테고리 분포, 집중·활동 시간, missed 카운트  
3. 목표 관리 — 장기/월간/주간/일간 및 부모–자식 관계  
4. 리포트 — `daily/*.json`, `reports/*-report.md` 목록 및 Git 커밋 로그 조회  
5. Git 자동화 — 저장 시 리포트 생성 후 API 또는 `scripts/git_auto_commit.py`로 add/commit/push (실패 시 DB 로그만 기록)

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프런트엔드 | React 18, Vite, TypeScript, Recharts |
| 백엔드 | FastAPI, SQLAlchemy 2, Alembic |
| DB | PostgreSQL (**권장: Neon** 호스티드 — 로컬 Postgres 설치 선택) |
| 설정 | `.env` / `backend/.env.example` |

## 폴더 구조

```
productivity-planner/
├── backend/           # FastAPI, Alembic, 서비스 레이어
├── frontend/          # React 앱
├── daily/             # 일별 JSON 산출물
├── weekly/            # 향후 확장용 (현재 .gitkeep)
├── reports/           # 일별 Markdown 리포트
├── docs/              # architecture.md, data_model.md
├── scripts/           # git_auto_commit.py
├── README.md
└── .gitignore
```

## 사전 준비 — 데이터베이스 (권장: Neon)

로컬에 PostgreSQL을 깔지 않아도 되도록 **[Neon](https://neon.tech)**(관리형 PostgreSQL, 무료 티어) 사용을 기준으로 안내합니다. 코드 변경 없이 `DATABASE_URL`만 바꿉니다.

### 1) Neon에서 프로젝트 만들기

1. Neon에 가입 후 **New Project**로 프로젝트를 만듭니다.  
2. 대시보드 **Connection details**에서 연결 문자열을 복사합니다.  
3. 문자열 끝에 SSL이 없다면 **`?sslmode=require`** 를 붙입니다.

예시 형태(값은 Neon에서 발급받은 그대로 사용):

```bash
DATABASE_URL=postgresql://USER:PASSWORD@ep-xxxx.region.aws.neon.tech/neondb?sslmode=require
```

### 2) 마이그레이션 시 연결 팁

- 대부분은 Neon이 제공하는 기본 URI로 `alembic upgrade head`가 동작합니다.  
- 연결 타임아웃이 나면 Neon 대시보드의 **직접 연결(Direct)** URI를 복사해 같은 형식으로 `DATABASE_URL`에 넣은 뒤 마이그레이션만 다시 실행해 보세요.

### 3) 로컬 PostgreSQL을 쓰는 경우 (선택)

로컬 서버를 이미 쓰신다면 DB만 만들고 사용자 권한을 맞춘 뒤, 동일하게 `DATABASE_URL`만 설정하면 됩니다.

```sql
CREATE DATABASE productivity_planner;
```

### 4) `PROJECT_ROOT`

리포트·Git 스크립트가 저장소 루트를 찾도록 **`PROJECT_ROOT`** 에 이 프로젝트 폴더의 **절대 경로**를 넣습니다. (`backend/.env.example` 참고)

## 백엔드 실행

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # 후 편집
alembic upgrade head
python scripts/seed_sample.py      # 선택 — 데모 데이터
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 프런트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 http://localhost:5173 — API는 Vite 프록시를 통해 http://127.0.0.1:8000 으로 전달됩니다.

## 주요 HTTP 엔드포인트

- `POST/GET/PUT/DELETE /daily[...]` — 일간 플랜  
- `POST/PUT/DELETE /activities[...]` — 활동  
- `GET /weekly/sleep-pattern/recent`, `GET /weekly/{year}/{week}` — 주간 통계 및 수면 패턴 시계열  
- `POST/GET/PUT/DELETE /goals[...]` — 목표  
- `POST /git/commit-daily/{date}`, `GET /git/logs` — Git 작업 및 로그  
- `GET /reports/list` — 생성된 리포트 목록  

(OpenAPI: http://localhost:8000/docs)

## 성취율 계산

- **기본 성취율:** 완료(`done`) 활동 수 ÷ 전체 활동 수 × 100 → `daily_plans.total_score`  
- **가중 성취율(주 지표):** 완료 활동의 `importance_score` 합 ÷ 전체 활동의 `importance_score` 합 × 100 → `daily_plans.achievement_rate`

## Git 자동 커밋 시 주의

- 원격 저장소와 자격 증명(`git credential`, SSH 등)이 미리 설정되어 있어야 `git push origin main`(또는 `GIT_BRANCH`) 이 성공합니다.  
- 푸시 실패는 애플리케이션을 중단하지 않으며 `git_commit_logs` 에 오류 문자열로 남습니다.  
- **GitHub 토큰은 저장소에 커밋하지 마세요.** 향후 GitHub API 연동 시 환경 변수로만 주입하세요.  
- 일별 파일만 스테이징합니다: `daily/YYYY-MM-DD.json`, `reports/YYYY-MM-DD-report.md`.

CLI 예시 (저장소 루트에서):

```bash
python scripts/git_auto_commit.py --date 2026-05-04
```

## 라이선스

포트폴리오용 샘플 프로젝트 — 필요에 맞게 수정해 사용하세요.
