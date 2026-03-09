# Task ID: 23

**Title:** LeRobot 모델 훈련 설정 및 실행

**Status:** pending

**Dependencies:** 20

**Priority:** high

**Description:** LeRobot 프레임워크를 사용하여 ACT 또는 Diffusion Policy 모방학습 모델을 훈련한다.

**Details:**

ai/lerobot/config/pipet_act.yaml에서 ACT 하이퍼파라미터 설정. 입력 차원(관절 6개 + RGB 이미지), 출력 차원(관절 6개 + 그리퍼 액션) 설정. ai/lerobot/train.sh 스크립트로 LeRobot CLI 또는 Python API를 통한 훈련 실행. GPU 메모리에 맞는 배치 사이즈 조정.

**Test Strategy:**

훈련 loss 수렴 확인. LeRobot eval 스크립트로 시뮬레이션 평가 수행. 체크포인트 파일 저장 확인.
