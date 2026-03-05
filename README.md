# Pipet Physical AI

Indy7 로봇팔과 Mand.ro Mark7 로봇손을 이용해 파이펫(pipette)을 조작하는 Physical AI 프로젝트.

## 시스템 구성

- **로봇팔**: Neuromeka Indy7
- **로봇손**: Mand.ro Mark7
- **카메라**: Intel RealSense D435
- **OS / ROS**: Ubuntu 22.04 / ROS2 Humble

## 아키텍처

계층형 구조:
- **모듈 레이어**: Indy7, Mark7, RealSense — 각 장치를 토픽/서비스로 노출
- **오케스트레이터 레이어**: 데이터 수집, 텔레오프, 추론 — 모듈 인터페이스를 조합하여 동작

## 문서

| 문서 | 설명 |
|------|------|
| `docs/architecture.md` | 전체 시스템 설계 |
| `docs/interface_spec.md` | ROS2 노드 인터페이스 명세 |
| `docs/mark7/architecture.md` | Mark7 모듈 상세 설계 |

## 디렉터리 구조

```
ros2_ws/          # ROS2 워크스페이스
  src/
    mark7/        # Mark7 관련 패키지
    indy7_ros2/   # Indy7 드라이버
    pipet_*/      # 오케스트레이터 패키지
ai/               # AI 학습 코드
docs/             # 설계 문서
```
