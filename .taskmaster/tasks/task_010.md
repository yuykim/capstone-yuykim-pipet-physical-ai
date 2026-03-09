# Task ID: 10

**Title:** Mark7 드라이버 통합 런치 파일 작성

**Status:** pending

**Dependencies:** 7, 8, 9

**Priority:** high

**Description:** Mark7 드라이버의 모든 구성 요소를 통합하여 실행하는 런치 파일을 작성한다.

**Details:**

launch/mark7.launch.py에서 use_mock_hardware 파라미터 지원. robot_state_publisher, controller_manager, grip_preset_node, safety_monitor_node를 순차 실행. config/mark7_controllers.yaml에서 joint_state_broadcaster와 forward_position_controller 설정.

**Test Strategy:**

ros2 launch pipet_hand_mark7_driver mark7.launch.py use_mock_hardware:=true와 use_mock_hardware:=false 모두 실행하여 필요한 모든 토픽/서비스 존재 확인
