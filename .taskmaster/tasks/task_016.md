# Task ID: 16

**Title:** 통합 키보드 텔레오프 노드 구현

**Status:** pending

**Dependencies:** 3 ✓, 10, 15

**Priority:** high

**Description:** 하나의 키보드에서 Indy7 직접 교시, Mark7 그리퍼, 데이터 수집을 통합 제어하는 노드를 구현한다.

**Details:**

pipet_system_teleop/system_teleop_node.py에서 키보드 입력 처리. SPACE=녹화 토글, H=홈, D=DT ON, d=DT OFF, G=잡기, O=펴기, P=누르기, Q=종료 키 매핑. indy_srv 서비스와 /gripper/* 서비스, /data_collector/* 서비스 호출. 현재 녹화 상태를 터미널에 실시간 표시.

**Test Strategy:**

mock 모드에서 각 키 입력 후 해당 서비스 호출 로그 확인. 녹화 상태 토글 동작 검증.
