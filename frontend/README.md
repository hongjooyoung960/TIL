# 프런트엔드 — Daily Productivity Planner

React + Vite + TypeScript + Recharts.

## 실행 (개발)

백엔드(FastAPI)가 `http://127.0.0.1:8000` 에서 실행 중이어야 합니다.

```bash
cd frontend
npm install
npm run dev
```

브라우저: http://localhost:5173

`VITE_API_URL` 을 두지 않은 경우 요청 경로는 **상대 경로**(예: `/daily/...`)이며, `vite.config.ts` 가 `/daily`, `/activities`, `/weekly`, `/goals`, `/git`, `/reports`, `/health` 를 백엔드로 프록시합니다.

## 프로덕션 빌드

API가 다른 호스트일 때 빌드 **전에**:

```bash
export VITE_API_URL=https://api.example.com    # 브라우저가 접속할 API 베이스 URL, 끝 슬래시 없이
npm run build
```

`VITE_API_URL` 이 비어 있으면 여전히 상대 URL만 사용합니다(Nginx 같은 리버스 프록시 한 도메인 뒤에 붙일 때 활용 가능).

Docker 이미지로 빌드할 때는 `docker build --build-arg VITE_API_URL=https://... -t planner-web frontend/` 형태로 같은 값을 넘깁니다(루트 `docker-compose.yml` 참고).

## Docker (nginx 정적 제공)

프로덕션용 Dockerfile은 빌드 스테이지 후 **nginx**로 `dist/` 만 서빙합니다(API는 **`VITE_API_URL`** 로 분리 호스트에 두는 방식을 권장합니다).
