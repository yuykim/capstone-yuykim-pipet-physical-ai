# AI 폴더 안내

이 폴더는 데이터 변환, LeRobot 학습, 참고용 소스 코드를 관리한다.

## 디렉터리 역할

| 경로 | 용도 |
|------|------|
| `datasets/` | LeRobotDataset v3.0 변환 결과 (`meta/`, `data/` 등). NPZ → `convert.py` 출력을 여기 두는 것을 권장. |
| `models/` | `lerobot-train` 체크포인트(런별 하위 폴더, 예: `act/`, `act_360_idle/`). |
| `logs/` | 학습·실험 메모, 터미널 로그 붙여넣기 등(예: `trainlog.md`). |
| `data_conversion/` | NPZ → LeRobot 변환 스크립트 |
| `lerobot/` | `run_lerobot_train.py` 학습 래퍼 |
| `diagnostics/` | 전처리 정합/오프라인 오차 분리 진단 스크립트 |
| `lerobot_source/` | LeRobot 업스트림 소스(참고/벤더링) |

코드·런치 기본값은 위 구조를 가정한다(추론 `model_path` 기본: `ai/models/act/checkpoints/last`).

## 관련 문서
- [AI 아키텍처 문서](/docs/ai/ai_architecture.md)
- [Raw 데이터 정의 문서](/docs/ai/ai_architecture.md)
- [LeRobotDataset v3.0 문서](/docs/ai/lerobot_architecture.md)
- [파이펫 위치 인식 복구 가이드](/docs/ai/pipette_localization_recovery.md)

## 빠른 시작
1. ROS2로 `episodes/*.npz` 수집
2. `ai/data_conversion/npz_to_lerobot/convert.py`로 변환 → 출력을 `ai/datasets/<이름>/` 권장
3. `ai/lerobot/run_lerobot_train.py` 실행 (`--dataset_output_dir`에 위 경로, `--output_dir` 생략 시 `ai/models/<job_name>`)

## 참고/레거시 경로
```text
ai/indy7_lerobot/
└── scripts/
   - 초기 실험용/보조 스크립트
   - 현재 메인 학습 파이프라인의 필수 경로는 아님
```
