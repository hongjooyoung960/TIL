# Daily Productivity Planner

일간·주간 계획, 목표 계층, 기상/취침 기록, 가중 성취율, 파일 리포트 생성, 로컬 Git 커밋·push까지 포함한 풀스택 MVP입니다.

**다른 PC에서 동일 환경으로 이어하기:** 순서형 체크리스트는 **[docs/setup-protocol.md](docs/setup-protocol.md)** — 저장소 루트에서 `./scripts/setup_dev.sh` 로 자동화 가능한 부분을 한 번에 실행할 수 있습니다.

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
├── docker-compose.yml # 선택 — api + 정적 nginx (DB는 비포함)
├── package.json       # 루트 스크립트 (예: npm run neon:init)
├── backend/           # FastAPI, Alembic, Dockerfile
├── frontend/          # React 앱, Dockerfile
├── daily/             # 일별 JSON 산출물
├── weekly/            # 향후 확장용 (현재 .gitkeep)
├── reports/           # 일별 Markdown 리포트
├── docs/              # architecture.md, data_model.md, setup-protocol.md
├── scripts/           # git_auto_commit.py, setup_dev.sh
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

### 5) Neon CLI (`neonctl init`) — IDE·MCP 연동 (선택)

Neon 공식 마법사는 **프로젝트 루트**에서 아래와 같이 실행합니다 (`npx neonctl@latest init` 과 동일).

```bash
npm run neon:init
```

- Node.js/npm이 설치되어 있어야 합니다.
- **브라우저 OAuth·에디터 선택** 등 대화형 단계가 있어, 반드시 **본인 PC 터미널**에서 실행하세요.
- 생성되는 MCP 설정·에이전트 스킬 등은 [Neon CLI `init` 문서](https://neon.tech/docs/reference/cli-init)를 참고하세요.
- **`DATABASE_URL`** 은 Neon 콘솔의 연결 문자열을 복사해 `backend/.env`에 넣은 뒤 `alembic upgrade head` 로 스키마를 적용하면 됩니다.

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

브라우저에서 http://localhost:5173 로 접속합니다. 개발 시 API는 동일 출처처럼 **상대 경로**로 두고 `vite.config.ts` 프록시가 `http://127.0.0.1:8000` 으로 넘깁니다. 배포 빌드(`npm run build`)에서는 **`VITE_API_URL`** 에 백엔드 **절대 URL** 이 있으면 그 값이 API 요청 접두사로 들어갑니다(미설정이면 계속 상대 경로).

## 배포

### 필요한 환경 변수 요약

| 변수 | 어디서 | 설명 |
|------|--------|------|
| `DATABASE_URL` | 백엔드 | PostgreSQL 연결 문자열(Neon 등). Docker에서도 호스트 등 외부 DB를 가리키면 됩니다. |
| `PROJECT_ROOT` | 백엔드 | 저장소 루트(`daily/`, `reports/` 포함)의 절대 경로. 리포트·파일/Git 연동 시 필수입니다. **`docker-compose.yml` 예제는 레포 전체를 `/workspace` 에 마운트하고 `PROJECT_ROOT=/workspace` 로 맞춥니다.** 호스트에는 `.:/workspace` 볼륨이 필요합니다. |
| `CORS_ORIGINS` | 백엔드 | 쉼표로 구분한 **허용 Origin**(스키마+호스트+포트). 단일 도메인에 SPA만 올린 경우 해당 오리진 한 줄이면 충분합니다. 예: `https://플래너.example.com`. Docker Compose로 정적 파일을 `http://localhost:8080` 에 띄우면 `http://localhost:8080` 을 포함하세요(`http://localhost:5173` 만 있으면 CORS 차단됩니다). |
| `VITE_API_URL` | 프런트 **빌드 시점** | 운영에서 API 호스트와 포트까지 적은 절대 URL(끝 `/` 불필요). 예: `https://api.example.com`. 로컬 Compose 예시에서는 브라우저가 접근하는 값으로 **`http://localhost:8000`**. 빌드에 녹음되므로 API 주소가 바뀌면 프런트 이미지를 다시 빌드해야 합니다. |

### 브라우저에서 열 주소

- **로컬 개발**: `http://localhost:5173`(Vite) + 프록시.
- **`docker-compose` 로 `web` + `api`**: 정적 페이지 `http://localhost:8080`, API `http://localhost:8000`(프런트는 빌드 시 `VITE_API_URL` 로 이 주소를 사용).

### Docker Compose (선택)

저장소 루트에 `docker-compose.yml` 이 있습니다. DB는 포함하지 않고 **외부**(예: Neon)의 `DATABASE_URL` 을 `backend/.env` 에 두는 형태입니다.

```bash
# backend/.env 에 DATABASE_URL, CORS_ORIGINS=http://localhost:8080 등 설정 후
docker compose build
docker compose run --rm api alembic upgrade head   # 최초 1회(또는 마이그레이션 시)
docker compose up
```

컨테이너 안에서 **`PROJECT_ROOT`** 는 마운트된 호스트 레포(`/workspace`)를 가리킵니다. 리포트·Git 커밋은 그 경로 아래 파일을 수정합니다.

**컨테이너·PaaS에서 Git push**: 호스트처럼 `git` 자격증명·SSH가 없으면 실패만 로그로 남을 수 있습니다. 배포 서버에서는 push를 전제하지 않거나, 레포만 별도 마운트/볼륨으로 두고 운영하세요.

### Fly.io / Render 등 API만 호스팅할 때 체크리스트

1. **`DATABASE_URL`**: 해당 플랫폼 비밀/환경 변수로 주입(Neon 등).
2. **`PROJECT_ROOT`**: 레포 루트를 **영구 볼륨으로 마운트**한 디렉터리와 동일하게 맞추거나, 파일 리포트·Git 기능 없이만 쓰면 경로 불일치에 유의합니다.
3. **`CORS_ORIGINS`**: 정적 SPA가 올라간 **브라우저 Origin** 과 정확히 일치(HTTPS·포트 포함).
4. **`VITE_API_URL`**: 정적 SPA를 구축하는 CI/빌드 단계에서, 브라우저가 접속할 공개 API URL로 설정 후 `npm run build`.

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
