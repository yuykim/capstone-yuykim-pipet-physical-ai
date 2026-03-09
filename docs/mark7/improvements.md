# 개선 아이디어

> 구현 중 발견한 개선 가능 사항들. 당장 필요하지 않지만 나중에 고려할 것.

---

## [write] 동일 position 손가락 묶어서 전송

**파일**: `src/pipet_hand_mark7_driver/src/mark7_system_hardware.cpp` — `write()`

**현재 방식**: 손가락별 개별 패킷 전송 (6패킷 × 2회 = 12회 전송/cycle)

**개선 방향**:
- `hw_commands_` 값이 동일한 손가락끼리 하나의 패킷으로 묶어 전송
- Mark7 Tx 패킷의 finger 비트마스크(B2~B7)를 활용해 동시 제어 가능
- 전송 횟수 감소 → 통신 부하 감소

**예시**:
```
엄지(100), 검지(100), 중지(200) 명령 시
  → 패킷 1: fingers[0]=1, fingers[1]=1, position=100 (엄지+검지 묶음)
  → 패킷 2: fingers[2]=1,              position=200 (중지 단독)
```

---

## [write] 변경 없는 손가락 패킷 전송 스킵

**파일**: `src/pipet_hand_mark7_driver/src/mark7_system_hardware.cpp` — `write()`

**개선 방향**:
- `hw_commands_[i]`가 이전 제어 주기와 동일하면 해당 손가락 패킷 전송 스킵
- `hw_prev_commands_` 벡터를 멤버로 추가하여 이전 값 추적
- 변경된 손가락만 전송 → 통신량 대폭 감소

**구현 아이디어**:
```cpp
if (hw_commands_[i] != hw_prev_commands_[i]) {
    // 패킷 전송
    hw_prev_commands_[i] = hw_commands_[i];
}
```

---

**현재 방식이 충분한 이유**:
- 115200bps 기준 180바이트/cycle ≈ 1.5ms → 실시간 제어에 무리 없음
- 각 손가락이 독립적인 목표 위치를 갖는 일반적 ros2_control 사용 패턴에서는 묶음 효과 미미
