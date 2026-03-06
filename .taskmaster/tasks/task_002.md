# Task ID: 2

**Title:** pipet_hand_mark7_description URDF 모델 작성

**Status:** done

**Dependencies:** None

**Priority:** high

**Description:** Mark7 로봇손의 URDF 모델, 메시 파일, RViz 설정을 포함한 description 패키지를 작성한다.

**Details:**

urdf/mark7.urdf.xacro 파일에서 6개 손가락(Thumb Flex, Index, Middle, Ring, Little, Thumb Ab) 관절을 revolute joint로 정의. 각 관절의 limit, dynamics 파라미터 설정. meshes/ 디렉터리에 STL/DAE 파일 배치. rviz/mark7.rviz 설정 파일 작성. launch/display.launch.py에서 robot_state_publisher와 joint_state_publisher_gui 실행.

**Test Strategy:**

ros2 launch pipet_hand_mark7_description display.launch.py 실행 후 RViz에서 6개 관절이 정상 표시되는지 확인, joint_state_publisher_gui로 관절 조작 가능 여부 검증
