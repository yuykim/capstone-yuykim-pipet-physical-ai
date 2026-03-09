# Task ID: 24

**Title:** 추론 노드 구현

**Status:** pending

**Dependencies:** 23, 17

**Priority:** high

**Description:** 학습된 모델을 로드하고 센서 데이터를 입력받아 실시간으로 로봇 액션을 추론하는 노드를 구현한다.

**Details:**

pipet_inference/inference_node.py에서 ~15Hz 추론 루프 구현. RGB 이미지, Depth 이미지, Indy7 관절 상태를 입력으로 받아 모델 추론 수행. 연속 관절 제어는 FollowJointTrajectory 액션으로 Indy7에 전달, 이산 그리퍼 액션은 /gripper/* 서비스 호출. pipet_inference/model_backends/lerobot_backend.py에서 LeRobot 모델 로딩 및 추론 구현.

**Test Strategy:**

mock 모드에서 더미 모델로 추론 루프 15Hz 동작 확인. 실제 모델 로드 후 추론 결과가 유효한 관절 각도 범위 내에 있는지 검증.
