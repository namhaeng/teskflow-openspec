## ADDED Requirements

### Requirement: 태스크 조회 및 필터
시스템은 팀의 태스크를 TODO/DOING/DONE 상태별로 조회할 수 있어야 하며, 전체/내 태스크(`@me`)/미할당 필터를 지원해야 한다(SHALL). "내 태스크"는 `assignee_id = current_user_id` 기준이며 `creator_id`가 아니다.

#### Scenario: 전체 조회
- **WHEN** 팀 멤버가 `GET /teams/{id}/tasks`를 호출하면
- **THEN** 시스템은 200과 함께 해당 팀의 모든 태스크를 `created_at` 내림차순으로 반환한다

#### Scenario: 내 태스크 필터
- **WHEN** 사용자가 `@me` 필터로 태스크를 조회하면
- **THEN** 시스템은 `assignee_id = current_user_id`인 태스크만 반환한다

#### Scenario: 미할당 필터
- **WHEN** 사용자가 `미할당` 필터로 태스크를 조회하면
- **THEN** 시스템은 `assignee_id IS NULL`인 태스크만 반환한다

### Requirement: 태스크 생성
시스템은 팀 멤버가 제목(1-100자)과 담당자(nullable)를 지정해 TODO 컬럼에 태스크를 생성할 수 있도록 해야 한다(SHALL).

#### Scenario: 태스크 생성
- **WHEN** 팀 멤버가 `POST /teams/{id}/tasks`에 제목과 선택적 `assignee_id`를 전달하면
- **THEN** 시스템은 201과 함께 생성된 태스크(`status: TODO`, `creator_id`=요청자)를 반환한다

### Requirement: 태스크 상태 변경 (드래그)
시스템은 태스크 상태를 TODO/DOING/DONE 간에 변경할 수 있도록 별도 엔드포인트를 제공해야 한다(SHALL). 제목 수정과 상태 변경은 분리된 엔드포인트를 사용한다.

#### Scenario: 드래그로 상태 변경
- **WHEN** 팀 멤버가 카드를 다른 컬럼에 드롭하여 `PATCH /tasks/{id}/status`에 새 상태를 전달하면
- **THEN** 시스템은 200과 함께 갱신된 태스크를 반환한다

### Requirement: 태스크 제목/담당자 수정
시스템은 태스크의 제목 및 담당자를 수정할 수 있도록 해야 한다(SHALL).

#### Scenario: 제목 수정
- **WHEN** 팀 멤버가 `PUT /tasks/{id}`에 새 제목을 전달하면
- **THEN** 시스템은 200과 함께 갱신된 태스크를 반환한다

### Requirement: 태스크 삭제 권한
시스템은 태스크 생성자(creator) 또는 팀 owner만 태스크를 삭제할 수 있도록 해야 한다(SHALL). 그 외 사용자의 삭제 요청은 거부해야 한다.

#### Scenario: 생성자의 삭제
- **WHEN** 태스크 생성자가 `DELETE /tasks/{id}`를 호출하면
- **THEN** 시스템은 200을 반환하고 해당 태스크를 삭제한다

#### Scenario: owner의 타인 태스크 삭제
- **WHEN** 팀 owner가 자신이 생성하지 않은 태스크에 대해 `DELETE /tasks/{id}`를 호출하면
- **THEN** 시스템은 200을 반환하고 해당 태스크를 삭제한다

#### Scenario: 권한 없는 삭제 시도
- **WHEN** 생성자도 owner도 아닌 멤버가 `DELETE /tasks/{id}`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환한다

### Requirement: 태스크 상세 조회
시스템은 단일 태스크의 상세 정보(제목, 상태, 담당자, 생성자, 생성 시각)를 조회할 수 있도록 해야 한다(SHALL).

#### Scenario: 상세 조회
- **WHEN** 팀 멤버가 `GET /tasks/{id}`를 호출하면
- **THEN** 시스템은 200과 함께 태스크 상세 정보를 반환한다
