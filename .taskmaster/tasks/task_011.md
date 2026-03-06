# Task ID: 11

**Title:** Mark7 키보드 텔레오프 노드 구현

**Status:** pending

**Dependencies:** 10

**Priority:** medium

**Description:** 터미널 키보드로 Mark7 손가락 6개를 개별 제어할 수 있는 단독 테스트 노드를 구현한다.

**Details:**

pipet_hand_mark7_teleop/keyboard_teleop_node.py에서 키보드 입력 처리. 각 손가락별 키 매핑 정의 (예: 1-6번 키로 각 손가락 제어). 키 1회 입력 시 step 파라미터만큼 position count 변화. Thumb Flex 방향 이슈 해결 포함. /forward_position_controller/commands 토픽 발행.

**Test Strategy:**

mock 모드에서 키 입력 후 /joint_states에서 해당 손가락 관절 값 변화 확인. 각 손가락별 정방향/역방향 동작 검증.
