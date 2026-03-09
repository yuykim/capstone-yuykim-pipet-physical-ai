# Task ID: 17

**Title:** 실제 하드웨어 통합 테스트

**Status:** pending

**Dependencies:** 12, 16, 5

**Priority:** high

**Description:** Indy7, Mark7, RealSense D435 실제 하드웨어를 연결하여 전체 시스템 통합 동작을 테스트한다.

**Details:**

Indy7을 이더넷 192.168.1.100으로 연결, Mark7을 USB Serial /dev/ttyACM0으로 연결, RealSense D435를 USB 3.0으로 연결. 전체 시스템 런치 후 세 장치 동시 구동 확인. /joint_states, /gripper/status, /camera/... 토픽 모두 정상 발행 확인.

**Test Strategy:**

ros2 topic hz로 각 토픽 주기 실측. RViz에서 실시간 로봇 상태와 카메라 이미지 동시 시각화 확인.
