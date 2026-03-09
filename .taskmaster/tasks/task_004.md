# Task ID: 4

**Title:** RealSense D435 패키지 설치 및 동작 검증

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** RealSense D435 카메라를 위한 공식 ROS2 패키지를 설치하고 RGB/Depth 이미지 스트림 동작을 검증한다.

**Details:**

sudo apt install ros-humble-realsense2-camera 명령으로 공식 패키지 설치. USB 3.0 연결 확인 및 권한 설정. ros2 launch realsense2_camera rs_launch.py로 카메라 노드 실행.

**Test Strategy:**

ros2 topic hz /camera/camera/color/image_raw와 /camera/camera/aligned_depth_to_color/image_raw 토픽이 각각 30Hz로 발행되는지 확인, RViz에서 이미지 품질 검증
