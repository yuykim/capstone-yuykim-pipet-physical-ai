# Task ID: 3

**Title:** indy7_ros2 서브모듈 통합 및 빌드 검증

**Status:** done

**Dependencies:** None

**Priority:** high

**Description:** neuromeka-robotics/indy-ros2 저장소를 서브모듈으로 추가하고 ROS2 Humble 환경에서 빌드 및 동작을 검증한다.

**Details:**

git submodule add https://github.com/neuromeka-robotics/indy-ros2.git ros2_ws/src/indy7_ros2 명령으로 서브모듈 추가. 특정 안정 커밋으로 고정. colcon build --packages-select indy7_ros2로 빌드 테스트. mock 모드에서 /joint_states 토픽 발행 확인.

**Test Strategy:**

colcon build 성공, ros2 launch indy7_ros2 indy7.launch.py use_mock_hardware:=true 실행 후 ros2 topic echo /joint_states로 20Hz 데이터 수신 확인
