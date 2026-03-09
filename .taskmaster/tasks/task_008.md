# Task ID: 8

**Title:** Mark7 Grip Preset Service Node 구현

**Status:** pending

**Dependencies:** 7

**Priority:** high

**Description:** grasp, open, press 프리셋을 std_srvs/Trigger 서비스로 제공하는 노드를 구현한다.

**Details:**

src/grip_preset_node.cpp에서 rclcpp::Node 상속 클래스 구현. /gripper/grasp, /gripper/open, /gripper/press 서비스 생성. config/grip_presets.yaml에서 각 프리셋의 6개 관절 각도(rad) 값 로드. 서비스 호출 시 /forward_position_controller/commands 토픽에 Float64MultiArray 발행.

**Test Strategy:**

mock 모드에서 각 서비스 호출 후 /joint_states에서 해당 프리셋 값으로 변경되는지 확인. 서비스 응답 success=true 반환 검증.
