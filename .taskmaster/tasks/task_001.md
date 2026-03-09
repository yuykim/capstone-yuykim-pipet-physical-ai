# Task ID: 1

**Title:** pipet_hand_mark7_msgs 패키지 생성 및 메시지 타입 정의

**Status:** done

**Dependencies:** None

**Priority:** high

**Description:** Mark7 로봇손을 위한 커스텀 ROS2 메시지 타입 GripperStatus와 FingerState를 정의하는 패키지를 생성한다.

**Details:**

ROS2 패키지 구조로 pipet_hand_mark7_msgs 디렉터리 생성. msg/GripperStatus.msg와 msg/FingerState.msg 파일 작성. GripperStatus는 Header와 FingerState[6] fingers 필드 포함. FingerState는 float32 position, current, temperature 필드 포함. CMakeLists.txt에서 rosidl_generate_interfaces() 설정, package.xml에서 메시지 의존성 추가.

**Test Strategy:**

colcon build 성공 확인, ros2 interface show pipet_hand_mark7_msgs/msg/GripperStatus 명령으로 메시지 정의 출력 검증
