# Task ID: 19

**Title:** 에피소드 데이터 수집 (50개 이상)

**Status:** pending

**Dependencies:** 18

**Priority:** high

**Description:** 실제 하드웨어를 사용하여 파이펫 조작 시연 에피소드를 50개 이상 수집한다.

**Details:**

통합 텔레오프를 사용하여 홈 포지션 → 파이펫 잡기 시연을 반복 수행. 각 에피소드는 10-30초 길이로 녹화. 다양한 거치대 위치, 각도, 조명 조건에서 수집하여 데이터 다양성 확보. 시연 품질 검수 기준에 따라 불량 에피소드 제외.

**Test Strategy:**

50개 NPZ 파일 생성 확인. 각 에피소드별 gripper_actions 분포 확인 (0,1,2,3 모두 포함). rgb_images 품질 시각 검수.
