# 대화 진행 상황 요약

> 마지막 업데이트: 2026-02-24
> 목적: 다음 세션에서 맥락을 바로 이어가기 위한 기록

---

## 현재 단계

**구현 진행 중 — Task 1, 2, 5 완료 / 실제 하드웨어 Rx 디버깅 블로킹**

---

## 완료된 작업

### Task 1 — 프로토콜/Serial 레이어
- `mark7_tx_packet.hpp`: 15바이트 Tx 패킷 인코딩
- `mark7_rx_packet.hpp`: ASCII CSV Rx 파싱
- `serial_port.hpp/.cpp`: POSIX termios, 115200-8N1, `read_crlf_line()` (`\r\n` 기준)

### Task 2 — ros2_control Hardware Interface
- `mark7_system_hardware.hpp/.cpp`: on_init/activate/deactivate/read/write 구현
  - read(): `->` echo 필터링 포함
- `mark7_hardware_plugin.xml`: pluginlib 등록
- `pipet_hand_mark7.xacro`: `<ros2_control>` 블록, `use_mock_hardware`/`port` xacro 인자화

### Task 5 — 런치/컨트롤러 설정
- `config/mark7_controllers.yaml`: controller_manager(1Hz), joint_state_broadcaster, forward_position_controller
- `launch/mark7_hardware.launch.py`: `use_mock_hardware`, `port` 런치 인자
- Mock 모드 기동 확인 완료

---

## 현재 블로킹 이슈

### 실제 하드웨어 Rx 미동작
- **Tx는 정상**: 동글이 `-> SENT: [F ...] [S ...] [C ...] [P ...] [D ...]` echo 반환 확인
- **Rx 없음**: 메뉴얼의 CSV 형식 (`+0, 60, 28, ...`) 데이터가 수신되지 않음
- **원인 불명**: 동글 Arduino 코드 미확보 — 실제 Rx 형식/타이밍 불명
- **해결 방법**: 동글 Arduino 코드 입수 후 아래 사항 분석 필요
  - PC→동글 패킷을 RF로 어떻게 전송하는지
  - Mark7 손→동글 RF 수신 후 PC로 올려보내는 형식과 타이밍
  - `-> SENT:` echo 발생 조건

---

## 설계 결정 (변경/확인된 사항)

| 결정 사항 | 내용 |
|----------|------|
| 포트 | Tx/Rx 단일 포트 `/dev/ttyACM0` (메뉴얼과 다름, Tx/Rx 동글 하나) |
| Rx 형식 | ASCII CSV (메뉴얼의 19바이트 바이너리와 다름) |
| update_rate | 1Hz (디버깅 중, 추후 조정 필요) |
| 캘리브레이션 | 실측 필요 — 보류 중 |

---

## 다음 할 일

1. 동글 Arduino 코드 입수 및 분석
2. Rx 파싱 수정 (실제 형식 확인 후)
3. Task 3 — 캘리브레이션 (rad ↔ position count 매핑 YAML)
4. Task 4 — 안전 모니터링 (온도/전류 임계값)
