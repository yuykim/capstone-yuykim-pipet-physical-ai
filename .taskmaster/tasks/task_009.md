# Task ID: 9

**Title:** Mark7 Safety Monitor Node 구현

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** 손가락 온도와 전류를 모니터링하여 이상 상황 시 경고 및 긴급 정지 기능을 제공하는 노드를 구현한다.

**Details:**

src/safety_monitor_node.cpp에서 /gripper/status 토픽 구독. 각 손가락의 temperature > 60°C 또는 current > 1100mA 감지 시 /gripper/safety_warning 토픽에 경고 메시지 발행. 지속적 임계값 초과 시 /forward_position_controller/commands에 현재 위치 유지 명령 발행.

**Test Strategy:**

mock 모드에서 GripperStatus 메시지에 임계값 초과 값 주입 후 /gripper/safety_warning 토픽 발행 확인. 긴급 정지 명령 발행 검증.
