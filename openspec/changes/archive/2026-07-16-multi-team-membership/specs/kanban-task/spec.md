## MODIFIED Requirements

### Requirement: 태스크 생성
시스템은 팀 멤버가 제목(1-100자)과 담당자(nullable)를 지정해 TODO 컬럼에 태스크를 생성할 수 있도록 해야 한다(SHALL). 과제가 비활성 상태이면 생성을 차단해야 한다.

#### Scenario: 비활성 과제에서 생성 시도
- **WHEN** 비활성화된 과제에 멤버가 `POST /teams/{id}/tasks`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환한다

#### Scenario: 태스크 생성
- **WHEN** 팀 멤버가 `POST /teams/{id}/tasks`에 제목과 선택적 `assignee_id`를 전달하면
- **THEN** 시스템은 201과 함께 생성된 태스크(`status: TODO`, `creator_id`=요청자)를 반환한다
