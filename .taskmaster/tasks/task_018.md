# Task ID: 18

**Title:** Mark7 관절 각도 캘리브레이션

**Status:** pending

**Dependencies:** 17

**Priority:** high

**Description:** URDF 관절 각도(rad)와 Mark7 position count 간 매핑을 실측하여 정확한 프리셋 값을 설정한다.

**Details:**

각 손가락을 단계적으로 이동시켜 rad ↔ position count 선형 매핑 측정. 물리적 가동 범위 확인 후 grip_presets.yaml 파일 업데이트. grasp/open/press 프리셋이 실제 파이펫 잡기에 적합하도록 조정.

**Test Strategy:**

/gripper/grasp 서비스 호출 시 실제 Mark7가 파이펫 잡기 포즈로 이동하는지 육안 확인. 각 프리셋별 반복 테스트로 일관성 검증.
