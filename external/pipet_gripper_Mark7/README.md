# pipet_ws

Pipet Hand Mark7 로봇 핸드를 위한 ROS2 Humble 워크스페이스입니다.

## 패키지

| 패키지 | 설명 |
|--------|------|
| [pipet_hand_mark7_description](src/pipet_hand_mark7_description/) | 로봇 핸드 URDF description |

## 빌드

```bash
cd ~/pipet_ws
colcon build
source install/setup.bash
```

## 빠른 시작

### RViz에서 로봇 모델 시각화
```bash
ros2 launch pipet_hand_mark7_description display.launch.py
```
