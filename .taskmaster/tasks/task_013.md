# Task ID: 13

**Title:** 멀티모달 데이터 시간 동기화 구현

**Status:** pending

**Dependencies:** 3 ✓, 4, 10

**Priority:** high

**Description:** Indy7 관절 상태, RGB 이미지, Depth 이미지, Mark7 그리퍼 상태를 ApproximateTimeSynchronizer로 동기화한다.

**Details:**

pipet_data_collector/data_collector_node.py에서 message_filters.ApproximateTimeSynchronizer 사용. /joint_states, /camera/camera/color/image_raw, /camera/camera/aligned_depth_to_color/image_raw, /gripper/status 토픽 구독. sync_slop=0.1초 설정으로 ~15Hz 동기화 달성.

**Test Strategy:**

4개 토픽이 모두 발행되는 상태에서 동기화된 콜백 함수 호출 빈도 측정. sync 드롭률 < 10% 확인.
