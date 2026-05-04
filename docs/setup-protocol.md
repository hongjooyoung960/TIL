# 다른 PC에서 이어하기 — 설정 프로토콜

이 문서는 **순서대로 실행**하면 어떤 PC에서도 동일한 로컬 개발 환경을 만들 수 있도록 작성했습니다.  
비밀값은 Git에 넣지 마세요. **`backend/.env`는 각 PC에서 다시 만듭니다.**

---

## Phase 0 — 옮길 것 / 옮기지 말 것

| 동기화 | 방법 |
|--------|------|
| 코드 | `git clone` 또는 `git pull` |
| DB 데이터 | Neon 등 **동일한 `DATABASE_URL`** 쓰면 공유됨 |
| `backend/.env` | **커밋 금지** — 새 PC에서 아래대로 재생성 |
| 로컬 생성물 `daily/*.json`, `reports/*.md` | 필요하면 Git에 포함하거나 무시 |

체크리스트:

- [ ] 이 저장소를 새 PC에 클론(또는 압축 복사)했다.
- [ ] Neon/Postgres 접속 정보를 안전한 곳에서 복사해 둘 수 있다.

---

## Phase 1 — 필수 도구 (한 번만)

### macOS (Homebrew 예시)

```bash
brew install python@3.12 node postgresql@16   # Postgres는 로컬 DB 쓸 때만
```

### Windows

- Python 3.12+: https://www.python.org/downloads/
- Node.js LTS: https://nodejs.org/
- Postgres 또는 Neon만 사용 (로컬 Postgres 생략 가능)

### 확인

```bash
python3 --version    # 3.11+ 권장
node -v && npm -v
```

체크리스트:

- [ ] `python3`, `npm` 명령이 동작한다.

---

## Phase 2 — 저장소 위치 고정

원하는 폴더로 이동한 뒤 clone 합니다.

```bash
git clone <저장소-URL> productivity-planner
cd productivity-planner
```

체크리스트:

- [ ] `backend/`, `frontend/`, `scripts/` 폴더가 보인다.

---

## Phase 3 — 자동 초기화 (권장)

저장소 **루트**에서:

```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

수행 내용:

- `backend/.venv` 생성 및 `pip install -r requirements.txt`
- `backend/.env` 없으면 `.env.example` 복사 후 **`PROJECT_ROOT`를 현재 저장소 절대 경로로 설정**
- `npm` 있으면 `frontend/npm install`

체크리스트:

- [ ] 스크립트가 에러 없이 끝났다.

수동으로 하려면 `README.md`의 백엔드/프런트 설치 절차를 따르되, **`PROJECT_ROOT`는 반드시 저장소 루트 절대 경로**로 맞춘다.

---

## Phase 4 — 데이터베이스 연결 (`DATABASE_URL`)

`backend/.env`를 연다.

### Neon 사용 시

1. [Neon 대시보드](https://console.neon.tech) → 프로젝트 → **Connection string** 복사  
2. 끝에 SSL 파라미터가 없으면 `?sslmode=require` 추가  
3. 한 줄로 설정:

```env
DATABASE_URL=postgresql://USER:PASSWORD@ep-xxxx.region.aws.neon.tech/neondb?sslmode=require
```

### 로컬 Postgres 사용 시

DB 생성 후 사용자에 맞게 URL 수정:

```sql
CREATE DATABASE productivity_planner;
```

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/productivity_planner
```

체크리스트:

- [ ] `DATABASE_URL` 저장했다.

---

## Phase 5 — 마이그레이션 및 (선택) 시드

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
alembic upgrade head
python scripts/seed_sample.py      # 선택
```

실패 시:

- DB가 뜨지 않았거나 URL이 틀린 경우가 많음 → Phase 4 재확인  
- Neon에서 **Direct** 연결 문자열로 마이그레이션만 다시 시도

체크리스트:

- [ ] `alembic upgrade head` 성공  
- [ ] (선택) 시드 실행함  

---

## Phase 6 — 개발 서버 실행

**터미널 A — API**

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 B — UI**

```bash
cd frontend
npm run dev
```

### 확인 URL

| 목적 | 주소 |
|------|------|
| Swagger | http://127.0.0.1:8000/docs |
| 완성 화면(SPA) | http://localhost:5173 |

체크리스트:

- [ ] `/docs` 가 열린다  
- [ ] `/` 플래너 화면이 열리고 API 호출이 된다 (브라우저 개발자 도구 Network 확인)

---

## Phase 7 — Docker로 통째로 (선택)

Docker Desktop 실행 후, 저장소 **루트**:

```bash
# backend/.env 에 DATABASE_URL 필수
docker compose build
docker compose run --rm api alembic upgrade head
docker compose up
```

| 서비스 | URL |
|--------|-----|
| UI | http://localhost:8080 |
| API | http://localhost:8000 |

`backend/.env`에 `CORS_ORIGINS=http://localhost:8080` 포함되어 있거나, `docker-compose.yml` 기본값을 사용한다.

체크리스트:

- [ ] `docker compose up` 후 8080·8000 응답 확인  

---

## Phase 8 — 배포(운영) 빌드 요약

프런트를 정적 호스팅할 때는 빌드 시 API 주소를 박아 넣는다:

```bash
cd frontend
VITE_API_URL=https://내-API-도메인 npm run build
```

자세한 내용은 루트 `README.md`의 배포 섹션을 따른다.

---

## 문제 발생 시 빠른 분류

| 증상 | 점검 |
|------|------|
| `npm: command not found` | Phase 1 Node 설치 |
| `cd backend` 실패 | Phase 2에서 저장소 루트인지 확인 (`ls backend`) |
| DB 연결 오류 | `DATABASE_URL`, DB 기동 여부, Neon 방화벽 |
| 브라우저만 안 됨 | Phase 6 URL, 방화벽/VPN |
| CORS 오류 | `CORS_ORIGINS`에 브라우저 오리진(ex: `http://localhost:5173`) 추가 |

---

## 한 줄 요약

```text
clone → ./scripts/setup_dev.sh → DATABASE_URL 작성 → alembic upgrade → uvicorn + npm run dev
```

이 순서를 다른 PC에서 그대로 반복하면 같은 개발 환경으로 이어갈 수 있습니다.
