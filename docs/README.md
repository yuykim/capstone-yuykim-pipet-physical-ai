# Docs Index

이 디렉터리는 시스템 설계, 데이터 수집, 학습, 하드웨어 설정, Mark7 핸드 문서를 모아둔 곳이다.
처음 보는 사람은 아래 순서로 읽으면 된다.

## 먼저 볼 문서

| 파일 | 내용 |
|------|------|
| [architecture.md](architecture.md) | 전체 시스템 설계. Indy7, Mark7, RealSense, 데이터 수집/학습 흐름을 큰 그림으로 설명한다. |
| [interface_spec.md](interface_spec.md) | ROS2 토픽, 서비스, 메시지, NPZ 저장 형식 등 모듈 간 인터페이스 명세. |
| [data_collection_decisions.md](data_collection_decisions.md) | 현재 데이터 수집 스키마와 학습에 쓸 데이터/보류한 데이터에 대한 결정 로그. |
| [history.md](history.md) | 로봇 연결, 환경 설정, 문제 해결 이력. 이미 겪은 시행착오를 확인할 때 본다. |

## 데이터 / AI / 학습

| 파일 | 내용 |
|------|------|
| [ai/ai_architecture.md](ai/ai_architecture.md) | 데이터 수집 및 학습 전략. observation/action 구성과 학습 데이터 구조를 설명한다. |
| [ai/lerobot_architecture.md](ai/lerobot_architecture.md) | NPZ 데이터를 LeRobotDataset 형식으로 변환하고 학습에 연결하는 구조 설명. |
| [ai/lerobot_setup.md](ai/lerobot_setup.md) | LeRobot 환경 설정 및 실행 절차. |
| [data_collection_decisions.md](data_collection_decisions.md) | 실제 수집할 NPZ 키, `ee_pose` 중심 action, `gripper_actions` mode 결정, 제외/보류 후보 정리. |

## Indy7 / Neuromeka

| 파일 | 내용 |
|------|------|
| [neuromeka_indydcp3_summary.md](neuromeka_indydcp3_summary.md) | Neuromeka IndyDCP3 Python API 요약. 관절값 읽기, motion command, teleop, 상태 조회 등. |
| [history.md](history.md) | Indy7 네트워크 연결, DCP/gRPC 문제 해결 이력 포함. |

## Mark7 Hand

| 파일 | 내용 |
|------|------|
| [mark7/architecture.md](mark7/architecture.md) | Mark7 ROS2 드라이버와 teleop/프리셋 서비스 설계. |
| [mark7/PRD.md](mark7/PRD.md) | Mark7 모듈 요구사항과 제품/기능 정의. |
| [mark7/status.md](mark7/status.md) | Mark7 구현 현황과 남은 작업. |
| [mark7/improvements.md](mark7/improvements.md) | Mark7 개선 아이디어와 후속 작업 후보. |
| [mark7/prev_architecture.md](mark7/prev_architecture.md) | 이전 Mark7 설계 기록. 현재 설계와 비교할 때 참고. |
| [mark7/Interface_with_Mark7 Hand_Simpler Protocol_20260305.pdf](<mark7/Interface_with_Mark7 Hand_Simpler Protocol_20260305.pdf>) | Mand.ro Mark7 통신 프로토콜 PDF 원문. |

## 개발 환경 / 노트북 설정

| 파일 | 내용 |
|------|------|
| [SirLab_publicLaptop/SirLab_PublicLaptop_dev_environment.md](SirLab_publicLaptop/SirLab_PublicLaptop_dev_environment.md) | SirLab 공용 노트북 개발 환경, Python/conda/ROS 관련 상태 정리. |
| [SirLab_publicLaptop/setup_progress.md](SirLab_publicLaptop/setup_progress.md) | 공용 노트북 설정 진행 상황과 체크리스트. |

## 읽는 순서 추천

1. 전체 구조를 보려면 [architecture.md](architecture.md)
2. 실제 ROS 토픽/서비스/NPZ 키를 확인하려면 [interface_spec.md](interface_spec.md)
3. 데이터 수집 판단 근거를 보려면 [data_collection_decisions.md](data_collection_decisions.md)
4. 학습 변환 구조를 보려면 [ai/lerobot_architecture.md](ai/lerobot_architecture.md)
5. Mark7 쪽 작업은 [mark7/architecture.md](mark7/architecture.md)
6. 설치/연결 문제가 생기면 [history.md](history.md)와 [SirLab_publicLaptop/SirLab_PublicLaptop_dev_environment.md](SirLab_publicLaptop/SirLab_PublicLaptop_dev_environment.md)
