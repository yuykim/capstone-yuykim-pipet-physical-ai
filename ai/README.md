# AI 폴더 안내

이 폴더는 데이터 변환, LeRobot 학습, 참고용 소스 코드를 관리한다.

## 관련 문서
- [AI 아키텍처 문서](/docs/ai/ai_architecture.md)
- [Raw 데이터 정의 문서](/docs/ai/ai_architecture.md)
- [LeRobotDataset v3.0 문서](/docs/ai/lerobot_architecture.md)

## 현재 사용 중인 경로 (권장)
```text
ai/
├── data_conversion/
│   └── npz_to_lerobot/
│       └── convert.py
│          - episodes/*.npz -> LeRobotDataset v3.0 변환 스크립트
│
├── lerobot/
│   └── run_lerobot_train.py
│      - 변환 + lerobot-train 실행 래퍼
│
└── lerobot_source/
   └── lerobot/
      - LeRobot 소스 코드(벤더링/참고용)
```

## 참고/레거시 경로
```text
ai/indy7_lerobot/
└── scripts/
   - 초기 실험용/보조 스크립트
   - 현재 메인 학습 파이프라인의 필수 경로는 아님
```

## 빠른 시작
1. ROS2로 `episodes/*.npz` 수집
2. `ai/data_conversion/npz_to_lerobot/convert.py`로 LeRobotDataset 변환
3. `ai/lerobot/run_lerobot_train.py`로 학습 실행