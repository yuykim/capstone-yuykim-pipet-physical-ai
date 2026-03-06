# Task ID: 6

**Title:** Mark7 시리얼 통신 프로토콜 구현

**Status:** pending

**Dependencies:** 1 ✓

**Priority:** high

**Description:** PC와 Mark7 동글 간 15바이트 Tx / 19바이트 Rx 직렬 통신 프로토콜을 C++로 구현한다.

**Details:**

include/pipet_hand_mark7_driver/mark7_protocol.hpp에서 TxPacket, RxPacket 구조체 정의. 헤더 0xAA 0x55, XOR 체크섬 검증 로직 구현. Position=0은 '변경 없음' 처리. src/mark7_protocol.cpp에서 encodeTxPacket(), decodeRxPacket() 함수 구현. src/mark7_serial.cpp에서 시리얼 포트 열기/닫기, 송수신 함수 구현.

**Test Strategy:**

단위 테스트로 패킷 인코딩/디코딩 검증. 알려진 입력값에 대해 기대되는 15바이트 출력 확인. 체크섬 불일치 패킷에 대한 에러 처리 검증.
