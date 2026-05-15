# Neuromeka IndyDCP3 Python API 정리

**정리 기준:** Neuromeka Docs 한국어 `Indy > Indy API > IndyDCP3 > Python` 문서  
**대상:** Indy7 등 Neuromeka Indy 계열 로봇을 Python에서 DCP3로 제어하는 코드 작성자

---

## 1. 핵심 개요

IndyDCP3는 Neuromeka 로봇 컨트롤러와 Python으로 통신하기 위한 클라이언트 API이다. 로봇 상태 조회, 디지털/아날로그 IO 제어, 모션 명령, 텔레오퍼레이션, 변수 공유, 프로그램 제어, 안전/유틸리티 설정 등을 제공한다.

모든 API 응답은 기본적으로 Python `dict` 타입으로 반환된다.

> 주의: `movej`, `movel`, `movec` 같은 모션 명령은 성공적으로 전달되면 로봇이 즉시 움직인다. 실제 로봇 사용 전 주변 충돌 가능 물체 제거, 저속 설정, 비상 정지 확인이 필요하다.

---

## 2. 설치 및 연결

### 설치 요구 사항

- Python 3.6 이상
- 문서 기준 Python 3.9 이상에서는 동작하지 않을 수 있음
- `pip` 또는 `pip3`

```bash
pip3 install neuromeka
pip3 install --upgrade neuromeka
pip3 show neuromeka
```

### 클라이언트 생성

```python
from neuromeka import IndyDCP3

indy = IndyDCP3(robot_ip="192.168.0.10", index=0)
```

- `robot_ip`: 로봇 컨트롤러 IP 주소
- `index`: 하나의 컨트롤러에 여러 로봇이 연결된 경우 로봇 인덱스

---

## 3. 상태 조회 API

로봇의 현재 운용 상태, 제어 상태, 모션 상태, 서보 상태, 에러 상태, 프로그램 상태를 조회할 수 있다.

| 함수 | 용도 |
| --- | --- |
| `get_robot_data()` | 로봇 운용 상태, 실행 시간, 시뮬레이션 모드, 기준/툴 프레임 |
| `get_control_state()` | 관절/작업공간 위치, 속도, 가속도, 목표값, 토크 |
| `get_motion_data()` | 모션 진행률, 목표 도달 여부, 모션 큐, 속도 비율 |
| `get_servo_data()` | 서보 상태 코드, 온도, 전압, 전류, 서보/브레이크 활성 상태 |
| `get_violation_data()` | 에러 코드, 발생 관절, 메시지 |
| `get_program_data()` | 현재 프로그램 이름, 실행 상태, 실행 시간, 알람/주석 |

### 자주 쓰는 예시

```python
robot_data = indy.get_robot_data()
control = indy.get_control_state()
motion = indy.get_motion_data()

current_jpos = control["q"]  # deg
current_tpos = control["p"]  # [mm, mm, mm, deg, deg, deg]
is_done = motion["is_target_reached"]
```

### 주요 상태 enum

```python
from neuromeka import OpState, TrajState, ProgramState

OpState.IDLE       # 5
OpState.MOVING     # 6
TrajState.CALC     # 2
ProgramState.IDLE  # 0
```

대표 `OpState`:

| 값 | 의미 |
| --- | --- |
| `SYSTEM_OFF(0)` | 시스템 꺼짐 |
| `SYSTEM_ON(1)` | 시스템 켜짐 |
| `VIOLATE(2)` | violation 상태 |
| `IDLE(5)` | 대기 |
| `MOVING(6)` | 모션 중 |
| `COLLISION(8)` | 충돌 |
| `TELE_OP(17)` | 텔레오퍼레이션 |

---

## 4. IO 제어

디지털/아날로그 IO와 엔드툴 IO를 조회하거나 설정할 수 있다.

| 함수 | 용도 |
| --- | --- |
| `get_di()` | 컨트롤박스 디지털 입력 |
| `get_do()`, `set_do()` | 컨트롤박스 디지털 출력 |
| `get_ai()` | 컨트롤박스 아날로그 입력 |
| `get_ao()`, `set_ao()` | 컨트롤박스 아날로그 출력 |
| `get_endtool_di()` | 엔드툴 디지털 입력 |
| `get_endtool_do()`, `set_endtool_do()` | 엔드툴 디지털 출력 |
| `get_endtool_ai()` | 엔드툴 아날로그 입력 |
| `get_endtool_ao()`, `set_endtool_ao()` | 엔드툴 아날로그 출력 |
| `get_io_data()` | 전체 IO 데이터 |

### 디지털 출력 예시

```python
from neuromeka import DigitalState

indy.set_do([
    {"address": 1, "state": DigitalState.ON},
    {"address": 5, "state": DigitalState.OFF},
])

do_state = indy.get_do()
```

`DigitalState`:

| 값 | 의미 |
| --- | --- |
| `OFF(0)` | 꺼짐 |
| `ON(1)` | 켜짐 |
| `UNUSED(2)` | 미사용 |

### 아날로그 출력 예시

```python
indy.set_ao([
    {"address": 0, "voltage": 7},
    {"address": 1, "voltage": 2},
])

ao_state = indy.get_ao()
```

### 엔드툴 출력 예시

```python
from neuromeka import EndtoolState

indy.set_endtool_do([
    {"port": "C", "states": [EndtoolState.HIGH_PNP]},
])

endtool_do = indy.get_endtool_do()
```

`EndtoolState` 주요 값:

| 값 | 의미 |
| --- | --- |
| `UNUSED(0)` | 미사용 |
| `HIGH_NPN(1)` | NPN High |
| `HIGH_PNP(2)` | PNP High |
| `LOW_NPN(-1)` | NPN Low |
| `LOW_PNP(-2)` | PNP Low |

---

## 5. 장치 및 툴 데이터

| 함수 | 용도 |
| --- | --- |
| `get_device_info()` | 로봇/컨트롤러 장치 정보 |
| `get_ft_sensor_data()` | 엔드툴 F/T 센서 원시 데이터 |
| `get_transformed_ft_sensor_data()` | 기준/툴 좌표계 변환 F/T 데이터 |
| `get_gripper_data()` | 그리퍼 상태 |
| `set_gripper_command()` | 그리퍼 명령 |
| `set_endtool_rs485_rx()` | 엔드툴 RS485 RX 버퍼 쓰기 |
| `get_endtool_rs485_rx()` | 엔드툴 RS485 RX 버퍼 읽기 |
| `get_endtool_rs485_tx()` | 엔드툴 RS485 TX 버퍼 읽기 |
| `set_sander_command()` | 샌더 설정/시작/정지 |
| `get_sander_command()` | 마지막 샌더 명령 상태 |

```python
ft = indy.get_ft_sensor_data()

indy.set_gripper_command(command=1, gripper_type=0, pvt_data=[50, 100, 1])
gripper = indy.get_gripper_data()
```

---

## 6. 기본 모션 명령

| 함수 | 용도 |
| --- | --- |
| `stop_motion(stop_category)` | 정지 카테고리에 따라 모션 정지 |
| `move_home()` | 설정된 홈 위치로 이동 |
| `movej()` | 관절 공간 이동 |
| `movej_time()` | 지정 시간 기반 관절 이동 |
| `movel()` | 작업공간 선형 이동 |
| `movel_time()` | 지정 시간 기반 선형 이동 |
| `movec()` | 원호 이동 |
| `movec_time()` | 지정 시간 기반 원호 이동 |
| `move_axis()` | 부가축 이동 |
| `move_gcode()` | G-code 경로 실행 |

### 정지

```python
from neuromeka import StopCategory

indy.stop_motion(StopCategory.CAT2)
```

| 값 | 의미 |
| --- | --- |
| `CAT0(0)` | 즉시 전원 차단 |
| `CAT1(1)` | 모션 정지 후 전원 차단 |
| `CAT2(2)` | 모션 정지 |

### 관절 이동

```python
target_jpos = [0, 0, -90, 0, -90, 0]
indy.movej(jtarget=target_jpos, vel_ratio=20, acc_ratio=100)
```

- `jtarget`: 관절 목표값, 단위 `deg`
- `vel_ratio`: 0~100, 최대 관절 속도 대비 비율
- `acc_ratio`: 0~900, 속도 비율 대비 가속도 배율

절대/상대 관절 이동:

```python
from neuromeka import JointBaseType

indy.movej(jtarget=[50, 0, -90, 0, -90, 0], base_type=JointBaseType.ABSOLUTE)
indy.movej(jtarget=[10, 0, 0, 0, 0, 0], base_type=JointBaseType.RELATIVE)
```

### 작업공간 선형 이동

```python
pos = indy.get_control_state()["p"]
pos[0] += 100  # x 방향 100 mm

indy.movel(ttarget=pos, vel_ratio=20, acc_ratio=100)
```

- `ttarget`: `[x, y, z, u, v, w]`
- 위치 단위: `mm`
- 자세 단위: `deg`

작업공간 기준:

```python
from neuromeka import TaskBaseType

indy.movel(ttarget=[100, 0, 0, 0, 0, 0], base_type=TaskBaseType.RELATIVE)
indy.movel(ttarget=[100, 0, 0, 0, 0, 0], base_type=TaskBaseType.TCP)
```

| 값 | 의미 |
| --- | --- |
| `ABSOLUTE(0)` | 절대 작업공간 위치 |
| `RELATIVE(1)` | 참조 좌표계 기준 상대 이동 |
| `TCP(2)` | 툴 좌표계 기준 상대 이동 |

### 원호 이동

```python
via_point = [241.66, -51.11, 644.20, 0.0, 180.0, 23.36]
end_point = [401.53, -47.74, 647.50, 0.0, 180.0, 23.37]

indy.movec(tpos0=via_point, tpos1=end_point, angle=360)
```

- `tpos0`: via point
- `tpos1`: end point
- `angle`: 원호 각도. 180은 반원, 360은 원, 720은 두 바퀴

---

## 7. Waypoint 및 비동기 모션

### Joint Waypoint

```python
indy.clear_joint_waypoint()

indy.add_joint_waypoint([0, 0, 0, 0, 0, 0])
indy.add_joint_waypoint([0, 0, -90, 0, -90, 0])

waypoints = indy.get_joint_waypoint()
indy.move_joint_waypoint(move_time=3)
```

### Task Waypoint

```python
indy.clear_task_waypoint()

indy.add_task_waypoint([400, -50, 650, 0, 180, 23])
indy.add_task_waypoint([300, -50, 650, 0, 180, 23])

waypoints = indy.get_task_waypoint()
indy.move_task_waypoint(move_time=1.5)
```

### 비동기 모션

```python
from neuromeka import BlendingType

indy.movel(target_pos1)
indy.movel(target_pos2, blending_type=BlendingType.DUPLICATE)
indy.movel(target_pos3)
```

| 값 | 의미 |
| --- | --- |
| `NONE(0)` | 동기 모션 |
| `OVERRIDE(1)` | 기존 모션을 다음 모션으로 갈아타기 |
| `DUPLICATE(2)` | 기존 모션과 중첩 |

---

## 8. Waiting 함수

모션 실행 중 특정 조건까지 대기할 수 있다.

| 함수 | 용도 |
| --- | --- |
| `wait_time()` | 첫 모션 명령 후 지정 시간 대기 |
| `wait_progress()` | 특정 진행률까지 대기 |
| `wait_radius()` | 지정 반경 조건까지 대기 |
| `wait_traj()` | 궤적 진행 상태까지 대기 |
| `wait_io()` | IO 조건 대기 |
| `wait_for_operation_state()` | 특정 운용 상태 대기 |
| `wait_for_motion_state()` | 특정 모션 상태 대기 |

```python
indy.movej(jtarget=[0, 0, 0, 0, 0, 0], blending_type=1)
indy.wait_progress(15)
indy.movej(jtarget=[0, 0, -90, 0, -90, 0], blending_type=1)
```

```python
indy.wait_for_operation_state(5)  # IDLE
indy.wait_for_motion_state("is_target_reached")
```

IO 대기:

```python
indy.wait_io(
    di_signal_list=[{"address": 1, "state": True}],
    do_signal_list=[],
    end_di_signal_list=[],
    end_do_signal_list=[],
    conjunction=0,
)
```

---

## 9. 텔레오퍼레이션

텔레오퍼레이션 모드는 목표 위치를 지속적으로 업데이트해 즉각적이고 부드러운 원격 제어를 수행하는 용도이다. 일반 `movej`, `movel`보다 실시간 반응에 적합하다.

| 함수 | 용도 |
| --- | --- |
| `start_teleop(method)` | 텔레오퍼레이션 시작 |
| `stop_teleop()` | 텔레오퍼레이션 종료 |
| `movetelej_abs()` | 관절 절대 목표 |
| `movetelej_rel()` | 관절 상대 목표 |
| `movetelel_abs()` | 작업공간 절대 목표 |
| `movetelel_rel()` | 작업공간 상대 목표 |
| `get_teleop_state()` | 텔레오퍼레이션 상태 |
| `get_teleop_device()` | 연결 장치 정보 |

### 관절 상대 텔레옵

```python
from neuromeka import JointTeleopType

indy.start_teleop(method=JointTeleopType.RELATIVE)
indy.movetelej_rel(jpos=[10, 0, 0, 0, 0, 0], vel_ratio=0.8, acc_ratio=7.0)
indy.stop_teleop()
```

### 작업공간 상대 텔레옵

```python
from neuromeka import TaskTeleopType

indy.start_teleop(method=TaskTeleopType.RELATIVE)
indy.movetelel_rel(tpos=[10, 0, 0, 0, 0, 0], vel_ratio=0.8, acc_ratio=7.0)
indy.stop_teleop()
```

텔레옵 `vel_ratio`는 0~1, `acc_ratio`는 0~10 범위로 사용한다.

---

## 10. Conty/API 공유 변수

Conty와 API가 함께 접근 가능한 변수 타입을 제공한다.

| 타입 | get 함수 | set 함수 |
| --- | --- | --- |
| Bool | `get_bool_variable()` | `set_bool_variable()` |
| Integer | `get_int_variable()` | `set_int_variable()` |
| Float | `get_float_variable()` | `set_float_variable()` |
| JPos | `get_jpos_variable()` | `set_jpos_variable()` |
| TPos | `get_tpos_variable()` | `set_tpos_variable()` |

```python
indy.set_bool_variable([{"addr": 100, "value": True}])
indy.set_int_variable([{"addr": 10, "value": 20}])
indy.set_float_variable([{"addr": 15, "value": 55.12}])

indy.set_jpos_variable([{"addr": 0, "jpos": [0, 0, 0, 0, 0, 0]}])
indy.set_tpos_variable([{"addr": 10, "tpos": [100, 100, 200, 0, 180, 0]}])
```

플러그인 변수:

```python
indy.set_plugin_bool_variable("bool_1", True)
indy.set_plugin_int_variable("int_1", 3)
indy.set_plugin_float_variable("float_1", 0.8)
indy.set_plugin_jpos_variable("ex_home_pose", [0, 0, -90, 0, -90, 0])
indy.set_plugin_tpos_variable("ex_t_pose", [100, 0, 300, 0, 90, 0])
```

---

## 11. 역기구학, 시뮬레이션, 복구

| 함수 | 용도 |
| --- | --- |
| `inverse_kin(tpos, init_jpos)` | 작업공간 목표에서 관절 해 계산 |
| `set_direct_teaching(enable)` | 직접교시 모드 활성/비활성 |
| `set_simulation_mode(enable)` | 시뮬레이션 모드 활성/비활성 |
| `recover()` | 에러/충돌 상태 복구 |
| `move_recover_joint()` | 충돌/violation 이후 복구용 MoveJ |

```python
tpos = indy.get_control_state()["p"]
init_jpos = indy.get_control_state()["q"]

ik = indy.inverse_kin(tpos=tpos, init_jpos=init_jpos)
```

```python
indy.set_simulation_mode(enable=True)
indy.set_direct_teaching(enable=True)

indy.recover()
```

---

## 12. 프로그램 제어

Conty에서 작성해 저장한 프로그램을 API로 재생/제어할 수 있다.

| 함수 | 용도 |
| --- | --- |
| `play_program(prog_name, prog_idx)` | 프로그램 실행 |
| `pause_program()` | 일시정지 |
| `resume_program()` | 재개 |
| `stop_program()` | 정지 |

```python
indy.play_program(prog_name="example_program.indy7v2.json")
indy.pause_program()
indy.resume_program()
indy.stop_program()
```

프로그램 파일 경로는 STEP 기준 `~/ProgramScripts`이다.

---

## 13. IndySDK 및 제어 게인

IndySDK 기능을 사용하면 사용자 정의 제어 모드와 제어 게인을 설정할 수 있다.

| 함수 | 용도 |
| --- | --- |
| `activate_sdk()` | SDK 라이선스 활성화 |
| `set_custom_control_mode()` | 사용자 컨트롤러 사용 여부 |
| `get_custom_control_mode()` | 사용자 컨트롤러 모드 확인 |
| `set_custom_control_gain()` | 사용자 컨트롤러 gain0~gain9 설정 |
| `get_custom_control_gain()` | 사용자 컨트롤러 게인 확인 |
| `set_joint_control_gain()` | 관절 제어 게인 |
| `set_task_control_gain()` | 작업공간 제어 게인 |
| `set_impedance_control_gain()` | 임피던스 제어 게인 |
| `set_force_control_gain()` | 힘 제어 게인 |

```python
indy.activate_sdk(
    license_key="...",
    expire_date="2025-02-01",
)
```

라이선스 응답 주요 상태:

| 코드 | 의미 |
| --- | --- |
| `0` | Activated |
| `1` | Invalid |
| `2` | No Internet Connection |
| `3` | Expired |
| `4` | HW_FAILURE |

---

## 14. 안전 및 유틸리티

### 로그

```python
indy.start_log()
# 로봇 동작 수행
indy.end_log()
```

RT 로그 경로:

```text
/home/user/release/IndyDeployments/RTlog/RTLog.csv
```

### 서보/브레이크

```python
indy.set_servo_all(enable=True)
indy.set_servo(index=3, enable=False)
indy.set_brakes([True, False, True, True, False, True])
```

### 마찰 보상 및 장착 자세

```python
indy.set_friction_comp_state(enable=True)
friction = indy.get_friction_comp_state()

indy.set_mount_pos(rot_y=5.0, rot_z=10.0)
mount = indy.get_mount_pos()
```

### 컴플라이언스/힘 제어

```python
indy.set_compliance_mode(enable=True, stiffness=[1000, 1000, 800, 50, 50, 50])
compliance = indy.get_compliance_mode()
```

### 충돌 민감도/정책

```python
level = indy.get_coll_sens_level()
indy.set_coll_sens_level(level=3)

policy = indy.get_coll_policy()
indy.set_coll_policy(policy=1, sleep_time=2.0, gravity_time=1.0)
```

### 프레임/툴/환경 설정

| 함수 | 용도 |
| --- | --- |
| `get_ref_frame()`, `set_ref_frame()` | 기준 좌표계 |
| `set_ref_frame_planar()` | 3점 기반 기준 좌표계 설정 |
| `save_reference_frame()`, `load_reference_frame()` | 기준 좌표계 저장/로드 |
| `get_tool_frame_list()`, `set_tool_frame_list()` | 툴 프레임 목록 |
| `get_tool_list()`, `set_tool_list()` | 툴 실행 목록 |
| `get_tool_property()`, `set_tool_property()` | 툴 질량/무게중심/관성 |
| `get_environment_list()`, `set_environment_list()` | 환경 모델 |
| `get_tool_shape_list()`, `set_tool_shape_list()` | 툴 형상 모델 |

### 안전 제한

```python
safety_limits = indy.get_safety_limits()

indy.set_safety_limits(
    power_limit=safety_limits["power_limit"],
    power_limit_ratio=safety_limits["power_limit_ratio"],
    tcp_force_limit=safety_limits["tcp_force_limit"],
    tcp_force_limit_ratio=safety_limits["tcp_force_limit_ratio"],
    tcp_speed_limit=safety_limits["tcp_speed_limit"],
    tcp_speed_limit_ratio=safety_limits["tcp_speed_limit_ratio"],
)
```

| 함수 | 용도 |
| --- | --- |
| `get_safety_limits()` | 파워, TCP 힘, TCP 속도, 관절 제한 조회 |
| `set_safety_limits()` | 안전 제한 설정 |
| `get_safety_stop_config()` | 안전 정지 설정 조회 |
| `set_safety_stop_config()` | 안전 정지 설정 |
| `set_reduced_speed()` | 감속 모드 속도 설정 |
| `get_reduced_speed()` | 감속 속도 조회 |
| `get_reduced_ratio()` | 감속 비율 조회 |
| `request_safety_function()` | 안전 기능 상태 전환 |
| `get_safety_function_state()` | 안전 기능 상태 조회 |
| `get_safety_control_data()` | 안전 제어 데이터 |
| `set_auto_mode()` | 자동 모드 설정 |
| `check_auto_mode()` | 자동 모드 확인 |
| `check_reduced_mode()` | 감속 모드 확인 |

---

## 15. 프로젝트에서 자주 쓸 패턴

### 1) 연결 확인

```python
from neuromeka import IndyDCP3

indy = IndyDCP3(robot_ip="192.168.0.10", index=0)

print(indy.get_robot_data())
print(indy.get_control_state()["q"])
print(indy.get_control_state()["p"])
```

### 2) 저속 상대 이동

```python
from neuromeka import TaskBaseType

indy.movel(
    ttarget=[10, 0, 0, 0, 0, 0],
    base_type=TaskBaseType.RELATIVE,
    vel_ratio=10,
    acc_ratio=50,
)

indy.wait_for_motion_state("is_target_reached")
```

### 3) 텔레옵 시작/종료 안전 구조

```python
from neuromeka import TaskTeleopType

try:
    indy.start_teleop(method=TaskTeleopType.RELATIVE)
    indy.movetelel_rel(tpos=[1, 0, 0, 0, 0, 0], vel_ratio=0.2, acc_ratio=2.0)
finally:
    indy.stop_teleop()
```

### 4) 에러 복구 흐름

```python
violation = indy.get_violation_data()
print(violation)

indy.recover()
indy.wait_for_operation_state(5)  # IDLE
```

---

## 16. 실사용 전 체크리스트

- 로봇 주변 작업 공간에 충돌 가능 물체가 없는지 확인한다.
- 비상 정지 버튼과 teach pendant/Conty 상태를 확인한다.
- 최초 테스트는 `set_simulation_mode(True)` 또는 낮은 `vel_ratio`, `acc_ratio`로 수행한다.
- 절대 좌표 이동 전 현재 `q`, `p` 값을 반드시 출력해 확인한다.
- 상대 이동은 좌표계 기준이 `RELATIVE`인지 `TCP`인지 명확히 구분한다.
- 텔레오퍼레이션은 `try/finally`로 `stop_teleop()`이 항상 호출되게 한다.
- 모션 후 `wait_for_motion_state("is_target_reached")` 또는 `get_motion_data()`로 완료 상태를 확인한다.
- violation/collision 발생 시 원인 로그를 확인하고 `recover()` 또는 `move_recover_joint()`를 사용한다.
