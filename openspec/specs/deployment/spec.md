## Purpose

로컬 개발과 운영 배포 환경 분리, 그리고 Vercel + Neon을 통한 운영 배포를 담당한다.

## Requirements

### Requirement: 환경별 DB 전환
시스템은 `DATABASE_URL` 환경변수만으로 로컬 SQLite와 운영 Neon(PostgreSQL) 사이를 전환할 수 있어야 한다(SHALL). 코드 변경 없이 환경변수만으로 전환되어야 한다.

#### Scenario: 로컬 실행
- **WHEN** `DATABASE_URL`이 SQLite 파일 경로로 설정된 상태로 서버를 실행하면
- **THEN** 시스템은 로컬 SQLite 파일에 대해 4테이블(users, teams, tasks, messages)로 동작한다

#### Scenario: 운영 배포
- **WHEN** `DATABASE_URL`이 Neon Postgres 연결 문자열로 설정된 상태로 배포되면
- **THEN** 시스템은 동일한 스키마로 Neon Postgres에 대해 동작한다

### Requirement: Vercel 배포
시스템은 프론트엔드(정적 파일)와 백엔드(FastAPI)를 Vercel에 함께 배포할 수 있어야 한다(SHALL).

#### Scenario: main 브랜치 배포
- **WHEN** `main` 브랜치에 push가 발생하면
- **THEN** Vercel은 프론트엔드 정적 파일과 백엔드 Serverless Functions를 함께 자동 배포한다

### Requirement: 로컬 개발 서버
시스템은 로컬에서 단일 FastAPI 프로세스로 정적 파일과 API를 함께 서빙해야 한다(SHALL).

#### Scenario: 로컬 통합 실행
- **WHEN** 개발자가 `uvicorn main:app --reload`로 로컬 서버를 실행하면
- **THEN** 프론트엔드 정적 파일과 API가 동일 서버에서 응답한다
