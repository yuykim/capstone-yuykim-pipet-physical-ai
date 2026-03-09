# Task ID: 20

**Title:** NPZ to LeRobot 데이터셋 변환 스크립트 작성

**Status:** pending

**Dependencies:** 19

**Priority:** high

**Description:** 수집된 NPZ 에피소드 파일들을 LeRobot 데이터셋 포맷으로 변환하는 스크립트를 작성한다.

**Details:**

ai/data_conversion/npz_to_lerobot/convert.py에서 episodes/*.npz 파일들을 일괄 처리. timestamps/joint_positions/rgb_images/gripper_actions를 LeRobot observation/action 스키마로 매핑. HuggingFace datasets 포맷으로 출력 디렉터리 생성.

**Test Strategy:**

변환된 데이터셋으로 LeRobot 데이터 로더 실행하여 에러 없이 로드되는지 확인. episode_index 연속성, 타임스탬프 단조 증가 검증.
