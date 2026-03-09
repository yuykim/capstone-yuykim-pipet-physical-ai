# Task ID: 7

**Title:** Mark7 ros2_control Hardware Interface 구현

**Status:** pending

**Dependencies:** 1 ✓, 2 ✓, 6

**Priority:** high

**Description:** Mark7 하드웨어를 ros2_control SystemInterface로 구현하여 표준 ROS2 제어 프레임워크에 통합한다.

**Details:**

include/pipet_hand_mark7_driver/mark7_hardware_interface.hpp에서 hardware_interface::SystemInterface 상속 클래스 정의. on_configure(), on_activate(), read(), write() 메서드 구현. URDF에서 use_mock_hardware 파라미터 읽기. mock 모드에서는 command를 state로 복사, real 모드에서는 시리얼 통신 사용. /joint_states와 /gripper/status 토픽을 20Hz로 발행.

**Test Strategy:**

mock 모드에서 /forward_position_controller/commands 토픽 발행 후 /joint_states에서 동일한 값 수신 확인. ros2 topic hz로 20Hz 발행 주기 검증.
