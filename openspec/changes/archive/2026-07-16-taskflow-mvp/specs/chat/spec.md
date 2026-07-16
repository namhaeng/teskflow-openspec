## ADDED Requirements

### Requirement: 메시지 조회 (폴링)
시스템은 `since=` 파라미터를 지원하는 팀 단위 메시지 조회를 제공해야 한다(SHALL). 클라이언트는 5초 간격으로 폴링하며, 네트워크 재연결 시 `since=`로 누락 없이 재동기화해야 한다.

#### Scenario: 최초 조회
- **WHEN** 팀 멤버가 `since` 없이 `GET /teams/{id}/messages`를 호출하면
- **THEN** 시스템은 200과 함께 최근 메시지 목록을 반환한다

#### Scenario: 증분 폴링
- **WHEN** 클라이언트가 마지막 메시지 시각을 `since=`로 전달해 조회하면
- **THEN** 시스템은 해당 시각 이후 생성된 메시지만 반환한다

#### Scenario: 메시지 누락 없음 보장
- **WHEN** 네트워크가 일시적으로 끊겼다가 복구되어 `since=`로 재조회하면
- **THEN** POST가 성공(201)했던 모든 메시지가 빠짐없이 응답에 포함된다 (DELETE된 메시지는 누락으로 간주하지 않는다)

### Requirement: 메시지 전송
시스템은 1000자 이내의 메시지 전송을 허용해야 하며(SHALL), 클라이언트와 서버 양쪽에서 길이를 검증해야 한다.

#### Scenario: 정상 전송
- **WHEN** 팀 멤버가 1000자 이내 메시지로 `POST /teams/{id}/messages`를 호출하면
- **THEN** 시스템은 201과 함께 생성된 메시지(발신자, 시각 포함)를 반환한다

#### Scenario: 1000자 초과
- **WHEN** 1000자를 초과하는 메시지로 전송을 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'TOO_LONG', limit: 1000, actual: <length> } }`를 반환한다

### Requirement: 메시지 삭제 (본인만)
시스템은 메시지 작성자 본인만 자신의 메시지를 삭제할 수 있도록 해야 한다(SHALL). 팀 owner라도 타인의 메시지는 삭제할 수 없다.

#### Scenario: 본인 메시지 삭제
- **WHEN** 메시지 작성자가 `DELETE /messages/{id}`를 호출하면
- **THEN** 시스템은 200을 반환하고 해당 메시지를 삭제한다

#### Scenario: 타인 메시지 삭제 시도
- **WHEN** 작성자가 아닌 사용자(owner 포함)가 `DELETE /messages/{id}`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'NOT_OWNER' } }`를 반환한다
