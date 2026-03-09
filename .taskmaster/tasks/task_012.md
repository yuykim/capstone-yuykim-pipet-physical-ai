# Task ID: 12

**Title:** 통합 시스템 URDF 작성

**Status:** pending

**Dependencies:** 2 ✓, 3 ✓

**Priority:** high

**Description:** Indy7, Mark7, RealSense D435를 하나의 URDF로 통합하여 전체 시스템의 TF 트리를 관리한다.

**Details:**

pipet_system_description/urdf/pipet_system.urdf.xacro에서 indy7.urdf.xacro와 mark7.urdf.xacro를 include. Mark7를 Indy7 엔드이펙터에 부착하는 fixed joint 정의. RealSense D435를 Mark7와 함께 마운트하는 joint 추가. launch/system.launch.py에서 robot_state_publisher 실행.

**Test Strategy:**

ros2 launch pipet_system_description system.launch.py 실행 후 RViz에서 Indy7+Mark7+RealSense 통합 모델 표시 확인. ros2 run tf2_tools view_frames로 TF 트리 구조 검증.
