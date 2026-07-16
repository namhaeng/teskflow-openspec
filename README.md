# TaskFlow MVP

소규모 팀(3-5인)이 칸반 보드와 팀 채팅으로 업무 진행 상황을 한 화면에서 추적하는 Day 2 MVP 프로젝트입니다.

## 기능

- **인증**: 회원가입, 로그인, JWT(24h) 발급/검증, bcrypt 비밀번호 해시
- **팀**: 팀 생성/초대코드 발급, 초대코드로 합류(미리보기 포함), 팀 나가기, 멤버 목록
- **칸반**: TODO/DOING/DONE 3컬럼, 태스크 생성/드래그로 상태 변경/수정/삭제, 담당자 배정 및 필터
- **채팅**: 팀 단위 메시지 송수신(1000자 제한), 5초 폴링, 본인 메시지 삭제
- **배포**: 로컬 SQLite / 운영 Vercel + Neon(PostgreSQL) 환경 분리

## 기술 스택

- Backend: FastAPI, SQLAlchemy, JWT, bcrypt
- Frontend: Vanilla JS + Tailwind CSS (CDN)
- DB: 로컬 SQLite / 운영 Neon(PostgreSQL)
- 배포: Vercel (프론트 정적 파일 + 백엔드 Serverless Functions)

## 로컬 실행

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # macOS/Linux

uvicorn main:app --reload --port 8000
```

`http://localhost:8000` 접속 후 회원가입부터 시작합니다. 환경변수는 `backend/.env.example` 참고.

## 프로젝트 구조

```
backend/          FastAPI 서버 (API 18개 + preview 엔드포인트)
  routers/        auth, teams, tasks, messages 라우터
frontend/         Vanilla JS + Tailwind 화면 (로그인/회원가입/팀선택/칸반/채팅/멤버)
  js/             api.js(fetch 래퍼), nav.js(공통 네비게이션)
docs/             프로그램 정의서, 스토리보드 원본 PDF
openspec/changes/taskflow-mvp/   OpenSpec 산출물 (proposal, design, specs, tasks)
vercel.json       Vercel 배포 설정
```

## 문서

이 프로젝트는 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 워크플로우로 스펙을 먼저 정의하고 구현했습니다. 전체 스펙과 결정 근거는 `openspec/changes/taskflow-mvp/`에서 확인할 수 있습니다.

## 범위 외 (Out of Scope)

알림, 파일 첨부, 전문 검색, 세분화된 권한, 다국어, WebSocket 실시간, 자동화 테스트는 이번 MVP 범위에 포함되지 않습니다.
