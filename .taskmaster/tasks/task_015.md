# Task ID: 15

**Title:** 데이터 수집 제어 서비스 구현

**Status:** pending

**Dependencies:** 14

**Priority:** high

**Description:** 녹화 시작/중지를 서비스로 제어하고 현재 녹화 상태를 토픽으로 발행하는 기능을 구현한다.

**Details:**

/data_collector/start, /data_collector/stop 서비스 생성 (std_srvs/Trigger). 녹화 상태를 내부 플래그로 관리. /data_collector/is_recording 토픽에 std_msgs/Bool로 현재 상태 발행. 이미 녹화 중에 start 요청 시 success=false 반환, 녹화 중이 아닐 때 stop 요청 시 success=false 반환.

**Test Strategy:**

start → stop 순서로 서비스 호출하여 NPZ 파일 1개 생성 확인. 중복 start/stop 요청에 대한 에러 반환 검증.
