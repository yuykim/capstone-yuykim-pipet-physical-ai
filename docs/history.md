# 26.04.02 작성자: 김유영

## 로봇 연결 문제 및 대응

### 1) 초기 증상: `ping 192.168.1.10` 실패
- Indy7(로봇 컨트롤러)의 IP 주소는 `192.168.1.10`(고정)로 가정하고 연결을 시도했음.
- PC에서 `ping 192.168.1.10` 수행 시 패킷이 수신되지 않음(100% packet loss).
- 또한 gRPC 포트 확인을 위한 `nc -zv 192.168.1.10 20001`도 타임아웃.

### 2) 원인 추정
- 해당 로봇 연결용 이더넷 인터페이스는 `enx00e04c360046`였으나,
  - 초기 상태에서 이 인터페이스에 IPv4 주소가 잡히지 않았고,
  - IPv6 link-local만 존재함.
- 즉, NetworkManager 관점에서 “고정 IP가 실제로 적용되지 않은 상태”로 판단됨.

### 3) 해결: `nmcli con mod` 대신 `nmcli con add`로 connection 생성
- 처음에는 아래처럼 `nmcli con mod enx00e04c360046 ...` 형태로 고정 IP를 바꾸려 했으나,
  - `Error: unknown connection 'enx00e04c360046'.`
- `nmcli con mod`의 첫 인자는 “네트워크 인터페이스 이름(ifname)”이 아니라 “NetworkManager connection 이름”이어야 함.
- 현재 시스템에서는 `enx00e04c360046`가 기존 connection 이름으로 등록되어 있지 않았기 때문에 수정이 실패한 것으로 이해됨.

#### 적용한 절차(최종 성공)
```bash
# (1) 해당 인터페이스를 대상으로 새 connection 생성 및 고정 IP 할당
sudo nmcli con add type ethernet ifname enx00e04c360046 con-name indy7-static \
  ipv4.addresses 192.168.1.100/24 ipv4.method manual \
  ipv6.method ignore autoconnect yes

# (2) connection 활성화
sudo nmcli con up indy7-static

# (3) IPv4 할당 확인
ip addr show enx00e04c360046 | grep inet
# -> inet 192.168.1.100/24 가 보여야 함

# (4) 로봇 연결 테스트
ping -c 2 192.168.1.10
```
- 위 절차 이후 `ping 192.168.1.10`가 성공(패킷 수신 2/2)하여 로봇 연결 네트워크 설정 문제가 해결됨.

### 4) 재발(26.04.10): 허브 교체 -> `ping 192.168.1.10` 실패 — USB 동글 교체·인터페이스 이름 변경

**증상:** 이전에 성공했던 `indy7-static` 설정이 있는데도 `ping 192.168.1.10`이 100% loss.

**원인(해당 PC 기준으로 확인):**
- USB 이더넷 동글의 **udev 인터페이스 이름**은 MAC 주소 기반이라, **동글을 바꾸면 `enx...` 이름이 바뀜** (예: 예전 문서의 `enx00e04c360046` → 현재 `enx00e04cae0a69`).
- `nmcli con show indy7-static`에 `connection.interface-name: enx00e04c360046`로 남아 있으면, **실제로는 존재하지 않는 인터페이스**에만 연결을 올리려 해서 **고정 IP(192.168.1.100/24)가 새 동글에 안 붙음**.
- 동일 이름 `indy7-static` 프로필이 **UUID가 다른 복수 개** 남아 있으면 정리가 필요할 수 있음.

**진단:**
```bash
ip -br link | grep enx
ip addr show enxXXXXXXXXXXXX   # 위에서 확인한 실제 이름으로
nmcli -t -f NAME,UUID,DEVICE con show | grep indy7
nmcli con show indy7-static | grep connection.interface-name
ping -c 2 -W 2 192.168.1.10
```

**해결(관리자 권한):** 실제 USB 이더넷 이름을 `<INDY_IF>`로 바꿔 실행.

```bash
# (선택) 중복 indy7-static 중 오래된 것 삭제 — UUID는 nmcli 출력으로 확인
# sudo nmcli con delete <불필요한_UUID>

# 기존 indy7-static이 있으면 인터페이스만 현재 동글로 교체
sudo nmcli con mod indy7-static connection.interface-name <INDY_IF>
sudo nmcli con up indy7-static

# 또는 새로 만들기(이름 충돌 시 기존 indy7-static 이름 변경/삭제 후)
# sudo nmcli con add type ethernet ifname <INDY_IF> con-name indy7-static \
#   ipv4.addresses 192.168.1.100/24 ipv4.method manual ipv6.method ignore autoconnect yes
# sudo nmcli con up indy7-static

ip addr show <INDY_IF> | grep inet   # -> 192.168.1.100/24
ping -c 2 192.168.1.10
```

**참고:** `CLAUDE.md` 등 문서에 적힌 `enx00e04c360046`는 **당시 동글 MAC 기준 이름**이므로, 장비가 바뀌면 **`ip -br link`로 매번 확인**하는 것이 안전함.

---

## 빌드 과정 중 문제와 해결 방법(colcon build)

ROS2 Humble 워크스페이스(`ros2_ws`)를 빌드하는 과정에서 여러 파이썬 의존성 문제로 `colcon build`가 연속 실패했다.
실패 로그를 기반으로 필요한 패키지를 설치/버전 조정을 반복하여 최종적으로 빌드 성공까지 도달했다.

### 1) 실패: `ModuleNotFoundError: No module named 'catkin_pkg'`
- 증상:
  - `pipet_hand_mark7_description` 빌드 단계에서 `package_xml_2_cmake.py` 실행 중 `catkin_pkg` 모듈이 없다고 실패.
- 원인:
  - 빌드에 사용되는 시스템 파이썬(python3) 또는 해당 환경에 `catkin_pkg`가 설치되어 있지 않았음.
- 해결:
  - sudo 없이 사용자 패키지로 설치하여 해결:
```bash
python3 -m pip install --user catkin_pkg
```

### 2) 실패: `ModuleNotFoundError: No module named 'em'` (rosidl_adapter 단계)
- 증상:
  - `pipet_hand_mark7_msgs` 빌드에서 `rosidl_adapter`가 실행되며 `import em` 실패.
- 해결:
  - `empy`를 사용자 설치로 먼저 도입:
```bash
python3 -m pip install --user empy
```

### 3) 실패: empy 버전 불일치 (`em.BUFFERED_OPT` 누락)
- 증상:
  - `AttributeError processing template 'msg.idl.em'`
  - `AttributeError: module 'em' has no attribute 'BUFFERED_OPT'`
- 원인 추정:
  - ROS2 Humble이 기대하는 `empy` 인터페이스(속성/상수)와 현재 설치된 `empy` 버전(4.2.1)이 호환되지 않음.
- 해결:
  - ROS2 Humble 호환 버전으로 다운그레이드:
```bash
python3 -m pip install --user 'empy==3.3.4'
```

### 4) 실패: `ModuleNotFoundError: No module named 'numpy'`
- 증상:
  - `rosidl_generator_py` 단계에서 numpy include 경로를 얻으려다 실패.
- 원인:
  - 빌드 과정에서 `/home/.../miniconda3/bin/python3`(conda python)가 호출되고 있었는데, 해당 파이썬에 `numpy`가 설치되어 있지 않았음.
- 해결:
  - conda python에 numpy 설치:
```bash
/home/sirlab-pwd-0000/miniconda3/bin/python3 -m pip install --user numpy
```

### 5) 실패: `ModuleNotFoundError: No module named 'lark'`
- 증상:
  - rosidl_parser에서 `from lark import Lark` 실행 중 실패.
- 원인:
  - 마찬가지로 `/home/.../miniconda3/bin/python3`에서 실행되고 있었고,
  - 그 conda 파이썬 환경에는 `lark`(정확히 `lark-parser`)가 없었음.
- 해결:
```bash
/home/sirlab-pwd-0000/miniconda3/bin/python3 -m pip install lark-parser
```

### 6) 결과: `colcon build` 최종 성공
- 위 의존성/버전 문제들을 순차적으로 해결한 뒤,
  - `pipet_hand_mark7_msgs`, `pipet_bringup` 등 패키지들이 정상 빌드되어 워크스페이스가 설치까지 완료됨.

---

## 다음에 참고할 포인트
- ROS2 Humble의 `rosidl_*` 계열 빌드는 “CMake가 호출하는 파이썬”이 실제로 어떤 경로인지가 중요하다.
- 같은 `python3`라도 시스템 파이썬(`/usr/bin/python3.10` 등)과 conda 파이썬(`/home/.../miniconda3/bin/python3`)이 섞여 사용될 수 있다.
- 따라서 실패 로그에 찍히는 파이썬 경로(`/miniconda3/bin/python3`, `/usr/bin/python3`)를 보고,
  그 경로의 파이썬에 맞춰 패키지를 설치하는 방식으로 접근하면 수렴이 빠르다.

---

## 로봇 데이터 수집 중단 문제 (Mark7 동글 /dev/ttyACM0 권한)

### 1) 초기 증상: `data_collection.launch.py`가 실행 직후 중단
- `ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10` 실행 중,
  `Mark7SystemHardware` 단계에서 활성화가 실패하며 프로세스가 abort됨.

### 2) 핵심 에러 로그
- `Mark7SystemHardware`: 시리얼 포트 열기 실패: `/dev/ttyACM0`

### 3) 원인
- `/dev/ttyACM0`는 소유자 `root`, 그룹 `dialout` 권한(`crw-rw----`) 형태로 존재했음.
- 당시 현재 세션의 사용자 그룹에 `dialout`이 포함되어 있지 않아,
  사용자 계정으로 `/dev/ttyACM0`를 열 수 없었음.
- 실제로 확인: 사용자로 `os.open('/dev/ttyACM0', ...)` 수행 시 `PermissionError: [Errno 13] Permission denied`가 발생.

### 4) 해결 과정
#### (1) dialout 그룹 권한 추가
```bash
sudo usermod -aG dialout $USER
newgrp dialout
```

#### (2) 세션 그룹 갱신 문제 확인 및 즉시 우회
- `newgrp dialout` 이후에도 현재 세션의 `groups` 출력에는 `dialout`이 반영되지 않은 상태로 보였고,
  `/dev/ttyACM0` 오픈이 계속 실패함.
- `sg dialout`로 해당 명령을 dialout 그룹 권한으로 실행했을 때는,
  `/dev/ttyACM0` 오픈이 성공(`open ok`)했음.

예시:
```bash
sg dialout -c "python3 - <<'PY'\nimport os\nfd=os.open('/dev/ttyACM0', os.O_RDWR|os.O_NOCTTY)\nprint('open ok')\nos.close(fd)\nPY"
```

### 5) 이후 조치
- 권한 반영이 확실해진 상태에서 `data_collection.launch.py`(터미널 1)와 `system_teleop_node`(터미널 2)를 다시 실행하여,
  `data_collector_node`가 정상적으로 살아있는지(카메라 토픽 포함) 확인하는 것으로 마무리.

---

## Direct teaching(교시/핸드가이드) 미동작 문제 및 해결 (옵션 A: `colcon_ws` 유지)

### 1) 초기 증상
- 녹화(SPACE)는 성공적으로 시작/중지되고 저장도 되지만,
  텔레옵에서 `D`(Direct teaching ON)를 눌러도 로봇이 “직접 교시/핸드가이드” 모드로 전환되지 않는다고 판단됨.

### 2) 원인 분석(코드 매핑 불일치)
- `pipet_system_teleop/system_teleop_node.py`에서 `D`를 누르면 `indy_srv`에 `IndyService.Request().data = 9`를 호출하도록 구현되어 있음.
- 그런데 실제 Indy7 드라이버( `indy_driver` )의 `indy_srv_callback()`은 `request.data`에 대해 `1~8`(Recover/Home/Teleop start/stop 등)만 처리 로직이 있었고,
  `9/10`에 대한 직접 teaching 로직이 없었음.
- 결과적으로 서비스 호출은 `success=True`로 반환될 수 있으나, 로봇 컨트롤러 입장에서는 teaching 모드가 켜지지 않는 상태가 발생.

### 3) 해결(Indy driver에 9/10 핸들러 추가)
- 우리 리포지토리(`pipet-physical-ai/ros2_ws`)가 아닌,
  Indy 드라이버 소스가 있는 외부 작업공간인 `colcon_ws`에 패치를 적용하고 재빌드함.

적용한 변경:
- `colcon_ws/src/indy-ros2/indy_driver/indy_driver/indy_define.py`
  - `MSG_DIRECT_TEACHING_ON  = 9`
  - `MSG_DIRECT_TEACHING_OFF = 10`
- `colcon_ws/src/indy-ros2/indy_driver/indy_driver/indy_driver/indy_driver.py`
  - `request.data == 9`일 때 `IndyDCP3.set_direct_teaching(enable=True)` 호출
  - `request.data == 10`일 때 `IndyDCP3.set_direct_teaching(enable=False)` 호출

### 4) 반영 방법
- 위 패치 후 `colcon_ws`에서 `indy_driver`를 다시 빌드한 다음,
  실제 로봇을 띄우는 `data_collection.launch.py`를 다시 실행해서 변경이 로드되도록 함.

### 5) 현재 상태(옵션 A 유지)
- Indy 관련 패치는 `colcon_ws`에 유지(옵션 A)하고,
  `pipet-physical-ai` 리포지토리 코드 수정은 최소화하는 방향으로 진행 중.

---

## 로봇 데이터 수집 최종 성공 확인(현재 상태)

### 1) ttyACM0 권한 이슈 해결(Mark7 동글)
- 초기에는 `ros2_control_node`/`Mark7SystemHardware`에서 `/dev/ttyACM0` 시리얼 포트 열기 실패로 백엔드가 죽었음.
- 현재는 `dialout` 권한이 정상 반영된 상태에서(필요 시 `sg dialout`로 백엔드를 실행) `Mark7` 구동이 안정적으로 동작함.

### 2) Direct teaching + 데이터 수집 동시 정상 동작
- `colcon_ws`의 Indy 드라이버에 직접 teaching(enable/disable: data=9/10) 처리를 추가한 뒤,
  `data_collection.launch.py`를 재실행하고 텔레옵에서 `D`(Direct teaching ON) 및 `SPACE`(녹화 시작/중지) 절차를 수행함.
- 그 결과 데이터 수집이 정상 진행되었고, `data_collector_node`가 `Recording started` 로그 이후 저장까지 완료되는 것을 확인함.

### 3) 사용 절차(운영 관점 요약)
- 백엔드(터미널 1): `ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10` 실행(필요 시 `sg dialout`로 감싸서)
- 텔레옵(터미널 2): `ros2 run pipet_system_teleop system_teleop_node` 실행
- 텔레옵 키:
  - `D` : Direct teaching ON
  - `SPACE` : 녹화 시작/중지
  - 중지 후 `Y/N` : 성공/실패 라벨링

---

# 26.04.06 작성자: 김유영

## 추론(LeRobot ACT) 배포: 그리퍼는 동작·Indy7 팔은 거의 안 움직임 (26.04.07 정리)

### 1) 초기 증상
- `inference.launch.py` + ZMQ 사이드카(`zmq_act_server`)로 학습된 ACT 체크포인트를 올려 자율 추론 시,
  **Mark7 그리퍼(프리셋 서비스)는 반응**하는데 **Indy7 팔은 눈에 띄게 움직이지 않는다**고 판단됨.
- 로그상 `delta_norm`이 매우 작게 찍히는 경우가 있었음.

### 2) ROS 그래프 점검: 궤적 토픽은 연결됨
- `ros2 topic list`에 `/joint_trajectory_controller/joint_trajectory`가 보인다고 해서 **구독자가 있다고 단정할 수는 없음**
  (`inference_node`가 퍼블리셔만 있어도 토픽 이름은 목록에 뜰 수 있음).

- 실제 확인 명령:
```bash
ros2 topic info /joint_trajectory_controller/joint_trajectory -v
```
- 결과(해당 PC 기준):
  - **Publisher**: `inference_node` (1)
  - **Subscription**: `indy_driver` (1)
- 결론: **“토픽이 안 닿아서”가 아님** — 메시지는 드라이버까지 도달하는 연결 구조가 맞음.

### 3) 팔이 여전히 안 움직일 때 추가로 볼 것 (환경/모드)
- **직접 교시(D) ON** 상태에서는 궤적 명령이 기대와 다르게 동작하거나 무시되는 경우가 있을 수 있음 → 자율 전 **교시 OFF** 권장.
- `/joint_states`와 궤적의 **`joint_names` 순서·이름**이 Indy 6축과 일치하는지 `ros2 topic echo`로 교차 확인.
- 정책과 무관하게 드라이버만 검증하려면, `JointTrajectory`를 수동 `ros2 topic pub` 등으로 소량 발행해 반응 여부를 분리 진단 가능.

### 4) 학습 데이터 통계(`ai/datasets/<dataset>/meta/stats.json`)와 액션 정의
- NPZ→LeRobot 변환(`ai/data_conversion/npz_to_lerobot/convert.py`)에서 액션은
  **`action = [delta_q (6), gripper_action]`**, `delta_q[t] = joint_positions[t+1] - joint_positions[t]` (20Hz 인접 프레임 차이).
- 동일 루트의 `stats.json`에서 `action`의 `delta_q` 차원은 **스텝당 변화가 대부분 매우 작은 분포**로 나타남(평균·분위수 기준).
- 해석: **“모델이 팔을 학습 못했다”기보다**, 학습 타깃 자체가 **프레임 간 델타가 작은 샘플이 많은 분포**이면 ACT가 **작은 델타를 예측**하는 것이 손실 관점에서 자연스러움.

### 5) 원시 NPZ로 검증 (에피소드 `episode_20260402_180823_success.npz` 예시)
- 스크립트 경로 주의: **`/~/path`는 잘못된 경로**(틸드는 `/` 뒤에서 확장되지 않음). 아래처럼 `pathlib.Path.expanduser()` 사용 권장.

```python
import numpy as np
from pathlib import Path
p = Path("~/2026capstone2_ws/pipet-physical-ai/ros2_ws/episodes/success/episode_20260402_180823_success.npz").expanduser()
d = np.load(p)
q = d["joint_positions"]
dq = np.diff(q, axis=0)
print("per-step |dq| mean:", np.abs(dq).mean(axis=0))
print("per-step |dq| max :", np.abs(dq).max(axis=0))
print("fraction all joints |dq|<1e-4:", (np.abs(dq) < 1e-4).all(axis=1).mean())
```

- 해당 파일에서 관측된 요약(참고):
  - 프레임 수 약 1213, 스텝 1212.
  - 관절 0~4: 스텝당 `|dq|` **평균**은 대략 **1e-4 ~ 1e-3 rad** 수준, **최대**는 일부 축에서 **~1e-2 ~ 3e-2 rad**까지 존재(순간 움직임은 기록됨).
  - **6축 모두 `|dq|<1e-4`인 스텝 비율 ≈ 0.52** → 절반 가까운 스텝은 “거의 정지”에 가까움.
  - **6번째 축(인덱스 5)** 은 이 에피소드에서 **거의 변하지 않음**(max가 ~1e-5 rad 수준) → 학습/추론에서 해당 축이 0에 가깝게 나오는 것이 데이터와 일치.

### 6) “자주 움직여야 하는 축도 추론에서 잘 안 움직인다”에 대한 요약 설명
- 정책은 “이 축은 과제상 중요” 같은 **라벨 없이**, **스텝마다 전 관절 델타의 통계**를 맞추는 회귀에 가깝게 학습됨.
- 사람이 느끼는 “몇 초 동안 계속 움직였다”와 **20Hz 스텝 단위 델타**는 다름: 정지·미세 조정이 섞이면 **평균 스텝 델타는 작게** 나오기 쉬움.
- **드문 큰 델타(분포의 꼬리)** 는 빈도가 낮아 출력이 **평균 쪽으로 눌리는(평활)** 경향이 있음.
- 액션 **mean/std 정규화**는 작은 분산을 가진 축에서 “출력이 작게 나오기”를 더 강화할 수 있음.

### 7) 학습 프로토콜 개선 아이디어 (기록 전용 — **아직 코드/운영에 적용하지 않음**)

아래는 Indy7 팔 델타가 데이터·학습 분포상 작게 잡히는 문제를 완화하기 위한 **검토용 아이디어**만 정리한 것이다. 당시 리포지토리에는 반영하지 않았다.

#### 7-1) 수집 프로토콜 (효과 대비 비용이 상대적으로 낮음)
- **정지 구간 줄이기**: 녹화 중 자세만 잡고 멈춰 있는 시간이 길수록 “스텝당 델타 ≈ 0” 샘플 비율이 늘어난다.
- **스텝당 델타를 키우는 움직임**: 천천히라도 **한 번에 충분한 각도**를 움직이면 20Hz에서도 `delta_q`가 커진다. 미세 조정만 길게 이어지면 통계는 다시 작아진다.
- **과제에 필요한 축**: 실제로 거의 안 쓰는 축은 그대로 두되, **반드시 써야 하는 축**은 데모마다 의도적으로 범위를 쓰도록 반복한다.
- **다양성**: 같은 성공이라도 시작 자세·속도·경로가 다른 데모를 여러 개 둔다.

#### 7-2) 데이터셋 구성·변환 (필터/가중)
- **고변화 프레임 oversample**: `||delta_q||`가 큰 프레임을 변환 단계나 별도 스크립트에서 복제해 비율을 올린다. (분포를 바꾸므로 과하면 부작용 가능 — 점진 적용.)
- **저모션 프레임 downsample**: 정지에 가까운 스텝 비율을 줄인다.
- **에피소드 설계**: 짧고 “움직임 위주”인 클립을 늘려 전체에서 정지 비율을 낮춘다.

#### 7-3) 액션 표현·제어 주기 (구조 변경 — 공수·효과 모두 큼)
- **제어 Hz 정렬**: 학습만 낮은 Hz로 리샘플하거나 `q[t+k]-q[t]`처럼 스텝당 델타를 키운 뒤, ROS 추론 주기·궤적 시간과 맞춘다.
- **절대 관절 목표 등**: 프레임 간 델타 대신 절대각을 액션으로 쓰면 잘게 쪼개진 델타 분포에 덜 민감할 수 있으나, `convert.py`·정책·`inference_node` 등 **파이프라인 전반** 수정이 필요하다.

#### 7-4) 학습 쪽 튜닝 (보조)
- **관절별 손실 가중**: 움직여야 하는 축에 더 큰 weight (LeRobot/ACT에서 지원 여부 확인 필요).
- **정규화**: `std`가 지나치게 작은 축에 **최소 std floor** 등 — 이론상 가능하나 프레임워크 기본만으로는 까다로울 수 있어 우선순위는 낮게 둘 수 있음.

#### 7-5) 검증 프로토콜
- 새 데이터 도입 전·후에 동일 스크립트로 `per-step |dq|` 평균·분위수·“전 축 저모션 스텝 비율” 등을 찍어 **수치 목표**를 정한다 (예: 저모션 비율을 절반대에서 더 낮추기).

#### 7-6) 권장 순서(검토용)
1. 수집 습관·클립 설계 정비  
2. `meta/stats.json` / NPZ 스크립트로 지표 목표 설정  
3. 필요 시 oversample/downsample  
4. 여전히 부족하면 액션 표현·제어 Hz 검토  

#### 7-7) 추론 시 정규화 관련 (오해 방지)
- LeRobot `predict_action`은 **관측 preprocessor → 정책 → action postprocessor(비정규화)** 순으로 동작하며, 체크포인트의 `policy_postprocessor`로 액션을 물리 단위로 되돌린다. “학습할 때만 정규화하고 추론에서 역변환을 안 한다”는 구조가 아니다. 작은 출력은 **데이터 분포·모델 예측** 쪽 원인과 함께 본다 (`lerobot.utils.control_utils.predict_action`, `pipet_inference/lerobot_act_backend.py` 참고).

### 8) 관련 코드/문서 위치
- 추론 노드: `ros2_ws/src/pipet_inference/pipet_inference/inference_node.py` (`JointTrajectory` 발행, 그리퍼 `Trigger` 호출).
- 추론 런치: `ros2_ws/src/pipet_bringup/launch/inference.launch.py`.
- NPZ 수집: `ros2_ws/src/pipet_data_collector/pipet_data_collector/data_collector_node.py` (`/joint_states`의 `position` 앞 6개를 저장).
- 인터페이스 명세: `docs/interface_spec.md` (궤적 토픽·`indy_srv` 코드 등).

---

## 26.04.07 학습 설정 변경 반영 (ACT)

`ai/lerobot/run_lerobot_train.py` 기준으로, 다음 학습 설정을 기본 실행값으로 반영했다.

- `policy.use_vae`: `false`
- `policy.chunk_size`: `40` (기존 100)
- `policy.n_action_steps`: `40` (기존 100)
- `policy.use_amp`: `true`
- `batch_size`: `8` 유지
- `dataset.use_imagenet_stats`: `true` 유지

또한 이미지 해상도는 한 단계 축소하기 위해 변환 래퍼 기본값을 아래처럼 변경했다.

- `--image_resize_to` 기본값: `360x480` (기존 빈 값/원본 해상도 유지)

주의:
- 위 값은 `python ai/lerobot/run_lerobot_train.py ...` 래퍼 경로에서 자동 적용된다.
- 체크포인트 구조(`chunk_size` 등)가 바뀌므로 기존 100-step 설정 모델과는 호환되지 않을 수 있어, 새 설정으로는 재학습을 전제로 한다.

---

## 26.04.07 데이터 변환·학습 파이프라인 트러블슈팅 (26.04.11 정리)

`ros2_ws/episodes/success/26.04.07` NPZ → `ai/data_conversion/npz_to_lerobot/convert.py` → `ai/datasets/26.04.07`(LeRobot v3), 학습은 `ai/lerobot/train_26_04_07.sh` → `ai/models/26.04.07`(10만 스텝, 1만 스텝마다 저장)까지 진행하면서 겪은 이슈와 대응을 정리한다.

### 1) 변환·실행 환경

- **conda `lerobot` 환경**에서 실행하고, `PYTHONPATH`에 `ai/lerobot_source/lerobot/src`를 넣어야 `lerobot`·`lerobot-train`이 프로젝트 벤더 소스와 맞는다.
- 변환 시 `meta/info.json`의 `repo_id`는 `--output_repo_id`(예: `pipet_26_04_07`)와 맞춘다. 학습 시 `--dataset.repo_id`도 동일해야 한다.
- `LeRobotDataset.create()`는 출력 루트 디렉터리가 **이미 존재하면** 실패할 수 있으므로, 재변환 시 해당 폴더를 비우거나 다른 경로를 쓴다.

### 2) 학습 출력 디렉터리: `FileExistsError`

**증상:** `Output directory ... already exists and resume is False`.

**원인:** LeRobot은 `resume=False`일 때 기존 `output_dir`가 디렉터리로 있으면 덮어쓰기를 막는다. 스크립트에서 `mkdir -p`로 빈 폴더만 만들어도 동일하게 막힌다.

**해결:** 출력 폴더는 학습 프로세스가 만든다. 스크립트에서 사전 `mkdir` 제거. 처음부터 다시 돌릴 때는 `rm -rf ai/models/26.04.07` 후 재실행.

### 3) 디스크 부족: `OSError: [Errno 28] No space left on device`

**증상:** 비스트리밍으로 데이터셋 로드 시 `datasets`가 parquet를 캐시에 풀다가 실패.

**원인:** 루트 파티션(예: 96GB 중 사용률 98%, 여유 ~2GB)에 `~/.cache/huggingface` 등이 쌓이며, **데이터셋 크기 + HF 캐시**가 동시에 들어가기 어렵다.

**해결:**
- **용량 확보:** 목표로 **여유 15GB 이상**(가능하면 30GB+) 권장. `conda clean`, 저널 vacuum, `~/.cache/huggingface` 정리, 워크스페이스 내 불필요 빌드·중복 데이터 등.
- **캐시 위치:** `HF_HOME` / `HF_DATASETS_CACHE`를 `ai/.cache/huggingface` 등 **여유 있는 경로**로 지정(`train_26_04_07.sh`에 반영). `.gitignore`에 `ai/.cache/` 추가.

### 4) 스트리밍 학습: OOM·빈 배치

디스크가 빡빡할 때 `--dataset.streaming true`로 우회를 시도했으나 다음이 발생했다.

| 증상 | 원인·대응 |
|------|-----------|
| `DataLoader worker ... Killed` | 스트리밍+고해상도 듀얼 카메라에서 `num_workers`가 크면 RAM 폭증 → OOM. `num_workers=0` 등으로 완화 시도. |
| `ValueError: Batch does not contain any data (None)` | **Accelerate + IterableDataset(스트리밍)** 조합에서 첫 배치가 비는 케이스. 로컬 학습은 **비스트리밍(`LeRobotDataset`)** 이 더 안정적. |
| (패치) 스트리밍 `_get_delta_frames` | parquet 행의 `episode_index`가 텐서일 때 `if past_item["episode_index"] == current_episode_idx`가 **0차원 bool 텐서**를 만들어 `RuntimeError` → 상위 `except RuntimeError`에 잡혀 샤드만 삭제되고 이터레이터가 비는 문제가 있어, `ai/lerobot_source/.../streaming_dataset.py`에 스칼라 비교 헬퍼(`_episode_index_eq`) 등을 추가해 두었음. **그래도 스트리밍 경로는 우선 비추천.** |

**실제 채택한 해결:** 디스크 여유 확보 후 **`--dataset.streaming` 끄고** `num_workers=2`로 비스트리밍 학습. 로그에 `streaming: False`이고 스텝이 증가하면 정상.

### 5) 콘솔에서 loss·lr 보기

- LeRobot은 `log_freq` 스텝마다 `train_tracker`(loss, grad_norm, lr 등)를 `logging.info`로 찍는다. 기본 200이면 한동안 조용할 수 있다.
- **`ai/lerobot/run_lerobot_train.py`**에 `--log_freq`를 추가(기본 50), **`train_26_04_07.sh`**에서 `--log_freq 50` 전달.
- **이미 실행 중인 프로세스**에는 `log_freq`를 런타임에 바꿀 수 없다. 더 촘촘히 보려면 중단 후 스크립트로 재시작하거나, 터미널에서 `tee`로 로그 파일을 남긴다.

### 6) 관련 파일 변경 요약

- `ai/lerobot/train_26_04_07.sh`: 출력·캐시·비스트리밍·`log_freq`·`num_workers` 등.
- `ai/lerobot/run_lerobot_train.py`: `--dataset_streaming`, `--num_workers`, `--log_freq`, `--save_freq` 등 `lerobot-train` 전달.
- `ai/lerobot_source/lerobot/src/lerobot/datasets/streaming_dataset.py`: 스트리밍 시 에피소드 인덱스 비교·`task_index` 정수화(로컬 이미지 parquet 호환).
- `.gitignore`: `ai/.cache/`.

---

## 26.04.10 추론(Indy7+Mark7+RealSense) 트러블슈팅 및 운영 정리

### 1) `autonomy_enabled:=true`인데 Indy7 팔이 전혀 움직이지 않음

**증상:** `inference_node` 로그에 `delta_norm`, `grip_cmd`는 찍히는데 로봇 팔은 반응 없음. Mark7·카메라는 정상인 것처럼 보임.

**원인:** Neuromeka `indy_driver`의 `joint_trajectory_callback`은 내부 상태가 **`MSG_TELE_JOINT_ABS`(관절 절대 텔레옵)** 일 때만 `movetelej_abs`로 궤적을 반영한다. 데이터 수집 후 **직접 교시(다른 `indy_srv` 모드)** 가 켜진 채로 두면 `/joint_trajectory_controller/joint_trajectory`를 발행해도 **드라이버가 무시**한다.

**해결(코드 반영):** `pipet_inference`의 `inference_node`가 자율 모드에서 추론 전에 `indy_srv`로 `data=6`(기본, `indy_define.MSG_TELE_JOINT_ABS`)를 한 번 호출하도록 했다. 런치 인자 `indy_prep_joint_teleop`(기본 true), `indy_prep_joint_teleop_code`(포크마다 다를 수 있음)로 조절.

**확인 로그:** `Indy 관절 텔레옵 준비 완료 (indy_srv data=6).` 이후 팔 명령이 나가야 한다.

### 2) 팔은 움직이는데 너무 느리거나 `delta_norm`이 ~0.001 수준

**원인 후보:**
- 학습 데이터·전처리와 불일치: 예) `act_360_idle`은 **360×480** 이미지인데 추론은 RealSense **640×480**을 그대로 넣으면 정책 출력이 작게 나올 수 있음.
- idle 위주 데이터면 스텝당 `delta_q` 분포 자체가 작음.

**해결(코드 반영):** `inference_node`에 **`action_delta_scale`**(모델 6D 델타에 곱한 뒤 `max_delta_rad`로 클립), **`image_target_height` / `image_target_width`**(0이면 미리사이즈 없음) 추가. 런치에서 예: `action_delta_scale:=8.0`, `image_target_height:=360`, `image_target_width:=480`.

### 3) ZMQ 사이드카·실행 순서

- ROS Humble(Python 3.10)과 LeRobot(Python 3.12+) 분리를 위해 **터미널 A:** `python -m pipet_inference.zmq_act_server --model-path .../checkpoints/...`  
- **터미널 B:** `ros2 launch pipet_bringup inference.launch.py ...`  
- `model_path`는 A의 `--model-path`와 **동일**해야 한다. `checkpoints/last` 대신 **`020000` 등 특정 스텝 폴더**를 쓰려면 양쪽 모두 그 경로로 통일.

### 4) NetworkManager: 문서의 `<INDY_IF>`는 치환 표기

- 셸에서 `sudo nmcli con mod indy7-static connection.interface-name <enx...>`처럼 **꺾쇠를 그대로 입력하면** 리다이렉션으로 `syntax error`가 난다. **꺾쇠 없이** 실제 인터페이스 이름만 넣는다 (예: `enx00e04cae0a69`).

### 5) `ai/` 디렉터리 정리 (26.04.10)

**목적:** 학습용 LeRobot 데이터셋, 학습 산출물(체크포인트), 학습 로그를 역할별로 분리.

| 경로 | 내용 |
|------|------|
| `ai/datasets/` | 변환된 LeRobotDataset (`training_data`, `training_data_360_idle_v3` 등) |
| `ai/models/` | 학습 런별 체크포인트 (예: `act/`, `act_360_idle/` — 기존 `pipet_train_outputs` 대체) |
| `ai/logs/` | `trainlog.md` 등 (기존 `ai/log/` 이동) |

- 기존 체크포인트 내 `train_config.json` 등의 **절대 경로**는 `models/`, `datasets/`에 맞게 일괄 갱신해 두었음(추론 시 `dataset.root` 자동 로드 유지).
- `.gitignore`: `ai/models/`, `ai/datasets/` 무시. 루트 `logs` 패턴이 `ai/logs`까지 막지 않도록 **`/logs/`** 로 한정.
- `inference.launch.py` 기본 `model_path`: `.../ai/models/act/checkpoints/last`.
- `run_lerobot_train.py`: `--output_dir` 생략 시 **`ai/models/<job_name>`**; `--steps` 기본 `20000`; `--save_freq` 있으면 `lerobot-train`에 전달.

### 6) Ctrl+C 시 `grip_preset_node` exit -2 / Traceback

- **SIGINT**로 스핀 중인 노드가 종료될 때 흔히 나오는 현상. `launch`에서 exit code -2를 비정상으로 찍을 수 있으나, **의도적 중단**이면 무시해도 됨.

### 7) 26.04.07 `050000` 체크포인트 추론 점검 (26.04.11)

#### 7-1) `ModuleNotFoundError: lerobot.configs.policies`

**증상:** `python -m pipet_inference.zmq_act_server --model-path .../checkpoints/050000` 실행 시 `No module named 'lerobot.configs.policies'`.

**원인:** conda `lerobot` editable 경로가 `ai/lerobot_source/lerobot`가 아니라 **불완전 복사본** `ai/huggingFace/lerobot/src`를 가리켰다.

**확인 포인트:**
- `lerobot.configs`는 잡히는데 `lerobot.configs.policies`는 없음
- `site-packages/__editable__.lerobot-0.5.1.pth`가 `ai/huggingFace/lerobot/src`를 가리킴

**해결:** 아래처럼 재설치해 editable path를 `ai/lerobot_source/lerobot`로 교정.

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lerobot
pip uninstall -y lerobot
pip install -e /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot
```

#### 7-2) 추론은 동작하지만 그리퍼가 `open ↔ grasp` 반복(플리킹)

**증상 로그:** `grip_preset_node`에서 `open`/`grasp`가 약 1초 간격으로 계속 교차. `inference_node`는 `delta_norm=0.0048`, `grip_cmd=1` 주기 로그.

**해석:**
- ZMQ 사이드카, 추론 루프, Mark7 서비스 호출 경로 자체는 정상 동작.
- 다만 그리퍼 분류 출력이 경계에서 흔들려 실제 서비스 호출은 `open`과 `grasp`를 왕복.
- 팔 델타는 작아(`delta_norm~0.0048`) 체감 움직임이 약할 수 있음.

**운영 대응:**
- 런치 인자로 `action_delta_scale:=8.0`(또는 10.0 근처) 상향
- 학습 해상도가 360x480이면 `image_target_height:=360 image_target_width:=480` 적용
- 근본적으로는 `inference_node` 그리퍼 명령에 히스테리시스/쿨다운(짧은 시간 재전환 금지) 추가 권장

#### 7-3) `ai/huggingFace` 폴더 정리(삭제)

**왜 생겼는가:**
- 과거에 LeRobot 코드를 로컬에서 별도 복사/실험하면서 `ai/huggingFace/lerobot` 트리가 생성된 것으로 확인.
- conda editable 설치가 이 경로를 참조(`.../__editable__.lerobot-0.5.1.pth`)하면서, 프로젝트의 기준 트리 `ai/lerobot_source/lerobot` 대신 이 복사본이 import됨.

**왜 문제가 되었는가:**
- `ai/huggingFace/lerobot`는 **불완전 트리**여서(예: `pyproject.toml`, `src/lerobot/configs/policies.py` 부재), 추론 시작 시 `ModuleNotFoundError: lerobot.configs.policies`를 유발.
- 동일 저장소에 LeRobot 소스가 `ai/lerobot_source/lerobot`로 이미 존재하므로, 중복/혼선만 키움.

**조치:**
- editable 설치 경로를 `ai/lerobot_source/lerobot`로 교정 후, `ai/huggingFace` 폴더를 삭제.
- 운영 기준 LeRobot 소스는 `ai/lerobot_source/lerobot` 단일 경로로 통일.

---

## 현재까지 요약 (26.04.11 기준)

- **네트워크:** Indy용 USB 이더넷은 동글·MAC에 따라 `enx...` 이름이 바뀌므로 `indy7-static`의 `connection.interface-name`을 실제 인터페이스에 맞출 것.
- **추론:** ZMQ 서버 선기동 → `inference.launch.py`; 팔 명령은 **`indy_srv`로 관절 절대 텔레옵(기본 code 6)** 준비 후 궤적 토픽이 먹힘.
- **체감 속도/델타:** `action_delta_scale`·360×480 리사이즈 옵션으로 튜닝; 안전 거리·E-stop 유지.
- **데이터/모델 경로:** `ai/datasets/`, `ai/models/`, `ai/logs/` 구조로 통일; 문서·런치·래퍼 기본값 반영됨.
- **26.04.07 학습:** 루트 디스크 여유·`HF_HOME`/`HF_DATASETS_CACHE`·비스트리밍·`log_freq` 등은 위 **「26.04.07 데이터 변환·학습 파이프라인 트러블슈팅」** 절 참고.

---

## 26.04.26 yuykim/dogyung 반영, 텔레옵, 실행 문서 정리

### 1) `dogyung` 브랜치 기능 확인 및 `yuykim` 반영

- GitHub의 `dogyung` 브랜치를 가져와 `yuykim`과 비교했다.
- `dogyung`에 있던 데이터 수집 discard 기능만 `yuykim`으로 가져왔다.
- 반영 커밋: `b9a27ef Add discard option (X) to skip saving episode on recording stop`
**변경 내용**

- `pipet_data_collector/data_collector_node.py`: `/data_collector/discard` 서비스 추가
- `pipet_system_teleop/system_teleop_node.py`: 녹화 종료 시 `[Y] Success / [N] Fail / [X] Discard` 선택지 추가
- `X` 선택 시 현재 녹화 버퍼를 저장하지 않고 폐기하도록 정리했다.

### 2) `AGENTS.md` 추가 및 MuJoCo 상태 명시

- 레포 루트에 `AGENTS.md`를 추가해 협업/운영 기준을 정리했다.
- `mujoco_env`는 현재 실험적 상태로 기록했다.
- 현재 `mujoco_env`는 Indy7 URDF/mesh 기반 viewer와 간단한 NPZ 수집은 가능하지만, Mark7 그리퍼와의 실제 접촉/상호작용 시뮬레이션은 완성되지 않았다.
- `mujoco_env`는 `ros2_ws/src/indy7_ros2`를 런타임에 직접 읽는 구조가 아니라, `mujoco_env/indy7_urdf`, `assets`, `generated`에 복사/가공된 모델 파일을 사용한다.
- 따라서 `indy_driver`, `indy_moveit`은 MuJoCo 실행 경로가 아니라 실제 ROS2 로봇 제어 경로에 속한다.

### 3) Indy7 Cartesian X/Y/Z 텔레옵 추가

- 기존 텔레옵은 각 관절 중심 조작/직접교시 중심이었고, Neuromeka 제공 코드에는 Cartesian jog가 구현되어 있었다.
- Neuromeka `servo_keyboard_input.py` 방식을 참고해 `system_teleop_node.py`에 MoveIt Servo 기반 Cartesian jog를 추가했다.
- `/servo_node/start_servo` 서비스를 호출해 Servo를 시작하고, `/servo_node/delta_twist_cmds`로 `geometry_msgs/TwistStamped`를 publish한다.
- 실제 로봇 teleop 모드 진입을 위해 `indy_srv`에 `MSG_TELE_JOINT_ABS = 6`을 호출한다.
- Cartesian 조작 중 다른 모드로 전환하거나 종료할 때 `MSG_TELE_STOP = 8`을 호출하고 zero twist를 publish하도록 했다.
**추가 키 매핑**

- 방향키: X/Y 이동
- `;` / `.`: Z up/down
- `B` / `T`: base frame(`link0`) / TCP frame(`tcp`) 전환
- `9` / `0`: Cartesian 속도 down/up
- 기존 `R`은 Mark7 release, `E`는 error recovery로 유지해 기존 통합 텔레옵 동작과 충돌하지 않게 했다.

### 4) MoveIt Servo launch 옵션 추가

- `pipet_bringup/launch/indy7_only.launch.py`에 `enable_cartesian_servo` 인자를 추가했다.
- `pipet_bringup/launch/data_collection.launch.py`에도 동일 인자를 추가했다.
- 기본값은 `false`로 두어 기존 데이터 수집 launch 동작은 유지한다.
- X/Y/Z Cartesian 조작이 필요할 때만 아래처럼 켠다.

```bash
ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10 enable_cartesian_servo:=true
ros2 run pipet_system_teleop system_teleop_node
```

### 5) README 빠른 실행 코드 정리

- 루트 `README.md` 상단에 `빠른 실행 코드` 섹션을 추가했다.
**포함 항목**

- 학습 실행 코드
- 데이터 수집 실행 코드
- 그리퍼 조작 테스트 코드
- Indy7 조작 코드
- 카메라 2개 화면 확인 코드
- 그리퍼 테스트 명령은 실제 `setup.py` entry point 기준으로 `teleop_keyboard`, `grip_preset_node`를 사용하도록 적었다.

### 6) 검증 및 남은 주의사항

- Python AST 문법 체크 통과:

```bash
python -c "import ast, pathlib; files=[...]; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8'), filename=f) for f in files]"
```

- `git diff --check` 통과.
- 하드웨어 smoke test는 아직 수행하지 않았다.
- `ros2_ws/src/indy7_ros2`는 submodule이며, 확인 과정에서 로컬 checkout 상태가 dirty가 되었다.
- 부모 레포는 `indy7_ros2`를 `b4df14ba...`에 고정하고 있으나 해당 커밋을 remote에서 받지 못했고, 로컬 submodule HEAD는 `3f326e1...`로 확인됐다.
- 이 submodule dirty 상태는 `3d1e4f0 feat: add Cartesian teleop and run docs` 커밋에 포함하지 않았다.
- `indy7_ros2`를 최신 브랜치로 새로 pull해 submodule pointer를 올리는 작업은 나중에 별도 커밋으로 진행한다.
- 이유: `indy_driver`, `indy_description`, `indy_moveit` 변경은 `/joint_states`, `indy_srv`, controller topic, MoveIt Servo 설정에 영향을 줄 수 있어 데이터 수집 smoke test와 함께 검증해야 한다.

---

## 26.04.20 half data 변환·학습·추론 점검 (26.04.25)

### 1) 데이터 검증 및 변환

- 입력 폴더: `ros2_ws/episodes/success/26.04.20 half data`
- 총 `10`개 NPZ(약 `2.7GB`)를 전수 검증:
  - 필수 키 존재, 배열 길이 일치, `success=True`, 압축 손상 없음
  - 에피소드 길이 약 `15.8~20.6s`, 수집률 약 `17.6~20Hz`
- LeRobot v3 변환 완료:
  - 출력: `ai/datasets/26.04.20_half_data`
  - `repo_id`: `pipet_26_04_20_half_data`
  - 로드 스모크 테스트: `episodes=10`, `frames=3448`, `fps=20`

### 2) 학습 실행/결과

- 학습 스크립트 추가: `ai/lerobot/train_26_04_20_half_data.sh`
  - `steps=100000`, `save_freq=10000`
  - `PYTHONUNBUFFERED=1` 및 `tee`로 `ai/logs`에 로그 저장
- 학습 완료:
  - 체크포인트 `010000`~`100000`, `last -> 100000`
  - 출력 경로: `ai/models/26.04.20_half_data/checkpoints/`
- 요약 문서 저장: `ai/logs/train_26_04_20_half_data_summary.md`

### 3) 추론 전 하드웨어 점검

- Indy7:
  - `ping 192.168.1.10` 정상
  - `nc -zv 192.168.1.10 20001` 정상
- Mark7:
  - 초기에 `/dev/ttyACM0` 기준으로 실행 시 포트 열기 실패
  - 실제 포트가 `/dev/ttyACM1`로 변경된 것을 확인 후 `mark7_port:=/dev/ttyACM1`로 해결
- RealSense 2대:
  - 일시적 USB 재열거/`VIDIOC_QBUF` 오류 및 `No such device` 발생
  - 재기동 후 `Publisher count=1`(wrist/overhead), 약 `29~30Hz` 스트림 확인

### 4) 현재 운영 메모

- 추론 기본 실행 시 Mark7 포트 인자는 반드시 실제 장치 노드로 지정:
  - 예) `mark7_port:=/dev/ttyACM1`
- `Ctrl+C` 후 Indy 직접교시 모드가 남을 수 있음:
  - OFF: `ros2 service call /indy_srv indy_interfaces/srv/IndyService "{data: 10}"`
  - 관절 텔레옵 복귀(추론용): `ros2 service call /indy_srv indy_interfaces/srv/IndyService "{data: 6}"`
- 카메라가 토픽명만 있고 `Publisher count: 0`이면 스트림 실패 상태이므로 재기동 후 재확인 필요.

### 5) 파이펫 위치 인식 실패 이슈 및 보완 아이디어(초안)

#### 배경

- 현재 추론에서 "파이펫 위치를 안정적으로 못 잡는" 구간이 반복적으로 관찰됨.
- 데이터 추가 수집은 계속 진행하되, 데이터 양만으로 해결되지 않을 가능성(구도/조명/가림/단계 판단)이 있어 보조 전략을 병행 검토.

#### 보완 방향

1) **고수준 인식/초기화 보조 (LLM/VLM/API)**
- 목적: 저수준 제어를 대체하지 않고, 저속 주기(예: 0.5~1Hz)로 장면 이해를 제공
- 출력 예시:
  - `pipette_direction`: left/right/up/down/center/not_visible
  - `stage`: search/approach/align/grasp/press/release/done
  - `confidence`: 0.0~1.0
- 적용 원칙: 출력은 직접 모터 명령이 아니라 "모드 전환 신호"로만 사용

2) **재시도/리커버리 트리거**
- 조건 예시: 파이펫 미가시 상태 지속, 그리퍼 플리킹, 장시간 stage 정체
- 액션 예시: 재탐색(search), 후진 후 재접근(backoff+re-approach), 안전 정지

3) **데이터 품질 향상 자동화**
- 수집 영상/에피소드 자동 태깅:
  - 파이펫 가시성, 가림 정도, 난이도, 조명 품질
- 활용: 저품질 샘플 제외, hard 샘플 선별, 재수집 우선순위 지정

#### 운영 관점 결론(현시점)

- 메인 제어 루프(20Hz)는 로컬 ACT를 유지하고,
- LLM/VLM/API는 "고수준 판단 보조"로 결합하는 하이브리드 전략이 유력.
- 즉시 할 일:
  - 데이터 추가 수집(다양한 파이펫 위치/조명/배경),
  - 보조 판단 스키마(JSON) 정의,
  - 오프라인 태깅 파이프라인(에피소드 난이도/가시성 점수화)부터 적용.

---

## 26.04.27 MuJoCo Indy7 + Mark7 통합/텔레옵 정리

### 1) MuJoCo 텔레옵 스크립트 추가

- `mujoco_env/scripts/keyboard_cartesian_teleop.py`를 추가해 Indy7 Cartesian 키보드 조작을 구현.
- 키 매핑:
  - 이동: `W/S`(+/-X), `A/D`(+/-Y), `Q/E`(+/-Z)
  - 프레임/속도: `B/T`(world/tool), `[`/`]`(속도), `-`/`=`(qvel gain)
  - 자세: `H`(controller home), `Shift+H`(teleop start)
- 기본 제어는 kinematic 적분(정지 시 처짐 방지), 필요 시 `--dynamic`으로 동역학 스텝 사용.

### 2) Mark7 실제 xacro 기반 결합

- `mujoco_env/scripts/prepare_models.py`를 확장:
  - Indy7 URDF + Mark7 xacro를 결합해 `generated/indy7_mujoco.urdf` 생성
  - `meshdir`를 `../assets`로 통일하고 `indy7/`, `mark7/` 하위 mesh를 사용
  - Mark7 링크/조인트 이름에 `mark7_` prefix를 부여해 이름 충돌 회피
  - `link6`에 `mark7_mount_joint`(fixed)로 결합
- Mark7 소스 경로는 자동 탐색:
  - 우선 `ros2_ws/src/mark7/pipet_hand_mark7_description`
  - 대안 `external/pipet_gripper_Mark7/src/pipet_hand_mark7_description`

### 3) Mark7 프리셋 조작 반영 및 mimic 보정

- 실제 프리셋(`grip_presets.yaml`)을 기준으로 `G/O/P/R` 동작을 반영:
  - `grasp/open/press/release` 순서와 step 값을 그대로 사용
  - step -> rad 변환을 적용해 MuJoCo 관절 목표값으로 매핑
- MuJoCo에서 `mimic`이 자동 적용되지 않는 경우를 보완하기 위해,
  - index/middle/ringer/pinky/thumb 상부 관절을 하부 관절 값에 수동 동기화.

### 4) 결과

- MuJoCo 장면에서 Indy7과 Mark7이 함께 로드되고,
- 키보드로 Indy7 Cartesian 이동 + Mark7 프리셋 조작이 가능해짐.
- 장착 자세(`mark7_mount_joint`의 `xyz/rpy`)는 작업 포즈 기준 미세 튜닝 가능 상태.

---

## 26.05.07 학습 입력 확장(extended state + ee_pose FK + gripper_action) + 100ep 데이터 학습 시도

### 1) 배경: 기존 extended 26D의 빈 슬롯 문제

- `--state_profile extended`는 형식상 `q+dq+τ(18) + ee_pose(7) + gripper_state(1) = 26D` 구조였지만,
  - 수집기(`pipet_data_collector`)가 NPZ에 `ee_pose`/`gripper_state`를 저장하지 않음(`gripper_actions`만 저장).
  - 변환기는 두 키가 없으면 해당 7+1칸을 **0으로 패딩**해 왔음.
  - 결과: 26D 중 뒤 8칸이 사실상 가짜 입력 → 모델이 "관절 + 이미지(+depth)" 위주로 학습.

### 2) 변환 단계 보강: 그리퍼 모드 + Pinocchio TCP FK

- `ai/data_conversion/npz_to_lerobot/convert.py` 수정:
  - `gripper_state` 미존재 시 **`gripper_actions[t]` 이산값(0~4)** 을 그 자리에 채움(피드백 부재 대체).
  - `ee_pose` 미존재 시 **`--fk_urdf` URDF + Pinocchio**로 매 프레임 TCP FK 계산
    → `(x, y, z, qx, qy, qz, qw)` 7D를 `observation.state[18:25]`에 채움.
  - 새 인자: `--fk_urdf`, `--fk_tcp_frame`(기본 `tcp`), `--fk_joint_names`(기본 `joint0,...,joint5`).
- 신규 모듈: `ai/data_conversion/npz_to_lerobot/indy7_tcp_fk.py` (Pinocchio 래퍼).
  - URDF에 동일 이름의 FRAME/BODY가 같이 있는 경우(예: `tcp` 프레임 + body)에 대비해 **`pin.BODY` 우선** 조회 후 fallback.

### 3) 추론 단계 보강: TF + FK fallback로 동일 정의 맞춤

- `ros2_ws/src/pipet_inference/pipet_inference/inference_node.py`:
  - `state_target_dim >= 26`이면 `observation.state[18:25]`를 **TF lookup(`world` ← `tcp`)** 결과로 채우고, 실패 시 **같은 URDF의 Pinocchio FK**로 fallback.
  - `observation.state[25]`는 마지막 그리퍼 명령(`_last_grip_cmd`, 0~4)을 그대로 기록 → 학습 분포와 일치.
- `inference.launch.py` 신규 인자: `use_tf_ee_pose`, `ee_tf_parent_frame`, `ee_tf_child_frame`, `fk_urdf_path`, `fk_tcp_frame`, `fk_joint_names`.
- `package.xml`에 `tf2_ros` depend 추가, ZMQ 사이드카(`zmq_act_server.py`/`sidecar_zmq_client.py`)는 이전에 이미 6-frame 멀티파트로 depth까지 전달.
- 결론: **변환과 추론이 같은 URDF·같은 TCP 정의**를 쓰면, 학습/추론 입력 분포가 일치하도록 설계.

### 4) 실행 스크립트 정비

- `run_scripts/20_train_lerobot.sh`: 6번째 인자부터 `run_lerobot_train.py`에 그대로 패스(`--state_profile extended --fk_urdf ... --include_depth`).
- `run_scripts/40_inference_ros.sh`: `[fk_urdf_path]`, `[state_target_dim]` 추가 인자.
- `run_scripts/README.md` 업데이트.

### 5) 신규 데이터셋: `26.05.03_half_data_100` (검증 결과)

- 경로: `ros2_ws/episodes/success/26.05.03_half_data_100/`
- 수집 기간: 2026-05-03 14:34 ~ 19:53.
- 총 100/100 NPZ, 28GB, 총 35,422 프레임(min/median/max = 237/338/607).
- 필수 키 누락·손상·`success=False` 0건. 변환·학습 직행 가능.

### 6) 변환·학습 실행 결과

#### 6-1) Pinocchio 환경 설정

- `lerobot` conda env에 Pinocchio 미설치 → `pip install pin`(numpy 2.x 경고 있으나 import 정상).
- Indy7 URDF는 `mujoco_env/generated/indy7_mujoco.urdf` 사용(서브모듈 미빌드 시 임시 활용).
  - **주의:** 이 URDF는 MuJoCo용 합성본이라 Mark7까지 포함되어 있어 추후 실기 추론에는 Neuromeka `indy_description` 정식 URDF로 교체 권장.

#### 6-2) 변환 완료(2026-05-07 18:12)

- 입력: `26.05.03_half_data_100` 100ep
- 출력: `ai/datasets/pipet_extended_depth_100`
  - `repo_id = pipet_extended_depth_100`
  - 100 parquet 청크 / **15GB**
  - `meta/info.json`: total_episodes=100, total_frames=35,322, fps=20
  - features: `front`, `front_depth`, `overhead`, `overhead_depth`, `state(26D)`, `action(7D)`
- 변환 옵션: `--state_profile extended --include_depth --fk_urdf ...indy7_mujoco.urdf --image_resize_to 360x480`

#### 6-3) 첫 학습 시도 → CUDA OOM

- `batch_size=16` + 8GB GPU(7.66 GiB)에서 첫 backward에 OOM 발생:
  - `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB. GPU 0 has a total capacity of 7.66 GiB of which 5.88 MiB is free.`
- 원인: ACT 입력이 RGB×2 + depth×2 + state 26D + chunk 40이라 8GB급 GPU에선 batch 16이 무리.

#### 6-4) 재실행 명령(채택안: batch=8, steps=100k)

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs

python ai/lerobot/run_lerobot_train.py \
  --skip_convert \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100" \
  --dataset_output_dir "${PWD}/ai/datasets/pipet_extended_depth_100" \
  --dataset_repo_id pipet_extended_depth_100 \
  --job_name act_pipet_extended_depth_100 \
  --steps 100000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 2 \
  --device cuda \
2>&1 | tee "ai/logs/train_act_pipet_extended_depth_100_$(date +%Y%m%d_%H%M%S).log"
```

### 9) 2026-05-09 실기 추론 결과 및 grasp gate 보정

#### 9-1) 실기 관찰

- 100k 학습 모델은 파이펫의 대략적인 위치/방향은 찾지만, 실행마다 최종 접근 위치가 흔들리고 완전한 grasp가 안정적으로 되지 않음.
- 증상은 단순한 "파이펫 미검출"보다는:
  - 마지막 2~5cm 정밀 접근이 불안정함.
  - grasp 명령이 너무 빨리 나오거나, 팔이 아직 움직이는 중에 손이 닫힘.
  - 같은 모델/같은 태스크에서도 초기 조건과 카메라 입력 변화에 민감함.
- 판단:
  - 코드 보정만으로 일부 개선은 가능하지만, 근본적으로는 데이터 수집/라벨/마지막 접근 제어 문제가 큼.
  - 특히 `gripper_action`은 `action[6]` 회귀값으로 학습되어 "정확한 이벤트 타이밍"보다 "현재 그리퍼 모드"처럼 동작하기 쉬움.

#### 9-2) 추론 노드 grasp gate 보강

- `ros2_ws/src/pipet_inference/pipet_inference/inference_node.py`에 grasp 실행 조건을 추가:
  - `grasp_delay_steps`: 첫 grasp 예측 후 일정 tick 동안 바로 닫지 않음.
  - `pre_grasp_delta_scale`: delay/gate 중에만 팔 `delta_q`에 추가 배율을 적용.
  - `grasp_confirm_steps`: grasp가 연속으로 일정 횟수 이상 예측되어야 함.
  - `grasp_max_delta_norm`: 팔 이동량(`delta_q` norm)이 충분히 작아졌을 때만 grasp 허용.
- 그리퍼 서비스 호출 보정:
  - 기존에는 서비스가 준비되지 않은 순간에도 `_last_grip_cmd`가 먼저 바뀔 수 있어, 실제 grasp 실패 후 재시도하지 않을 위험이 있었음.
  - 이제 서비스가 준비되어 호출을 보낸 뒤에만 `_last_grip_cmd`를 갱신하고, 서비스 결과 실패/예외를 로그로 남김.
- `inference.launch.py`와 `run_scripts/40_inference_ros.sh`에 위 파라미터를 노출.
- 추천 시작값:

```bash
grasp_delay_steps:=8
pre_grasp_delta_scale:=1.15
grasp_confirm_steps:=8
grasp_max_delta_norm:=0.008
max_joint_speed_rad_s:=0.25
```

- 튜닝 방향:
  - 너무 빨리 잡으면 `grasp_delay_steps`를 늘리거나 `grasp_max_delta_norm`을 낮춤.
  - 아예 안 잡으면 `grasp_confirm_steps`를 줄이거나 `grasp_max_delta_norm`을 높임.
  - 더 깊게 들어가야 하면 `pre_grasp_delta_scale`을 조금 높임.

#### 9-3) 검증

- Python AST parse:
  - `inference_node.py`
  - `inference.launch.py`
- Shell syntax:
  - `run_scripts/40_inference_ros.sh`
- ROS build:
  - `colcon build --symlink-install --packages-select pipet_inference pipet_bringup`

#### 9-4) 다음 실험 방향: Gemini-ER 검증기

- 현재 ACT만으로 위치/타이밍이 흔들리므로, 새 브랜치에서 Gemini Robotics-ER를 "파이펫 위치/잡기 타이밍 검증기"로 붙이는 실험을 진행하기로 함.
- 목표는 Gemini-ER가 직접 로봇을 제어하는 것이 아니라:
  - wrist/overhead 이미지에서 파이펫 point/bbox를 찾고,
  - gripper 중심 근처에 파이펫이 충분히 들어왔는지 판단하고,
  - 조건이 맞을 때만 ACT의 grasp를 허용하는 보조 판단기로 쓰는 것.
- 공식 Gemini Robotics-ER 1.6 문서 기준:
  - 모델명: `gemini-robotics-er-1.6-preview`
  - 이미지 입력 + 자연어 prompt로 2D point/bbox/trajectory 같은 JSON 구조화 출력을 받을 수 있음.
  - 출력 좌표는 `[y, x]`, 0~1000 정규화 형식 예시가 문서에 제시되어 있음.

- 데이터셋이 이미 변환돼 있어 `--skip_convert`. 디스크/시간 절약.
- `PYTORCH_ALLOC_CONF=expandable_segments:True`: 메모리 단편화 완화.
- 8GB GPU에서 batch=8이 안전선. 8에서도 OOM이면 `--batch_size 4`로 한 단계 더 낮춤.
- batch가 줄었으니 동일 데이터 노출량을 맞추기 위해 `steps=100000`으로 상향(이전 v2는 80k).

### 7) 다음 점검 항목

- 첫 100~500step 안에 `Training: ... step` 진행바 + loss 하강 확인.
- 10k step 체크포인트(`checkpoints/010000/`) 저장 직후, 추론에서 `state_target_dim:=26`, `fk_urdf_path:=…/indy7_mujoco.urdf`로 분포 일치 검증.
- 실기 운영 전 단계로 Neuromeka `indy_description` 정식 URDF로 변환·추론 모두 재정렬할 것(현재는 임시 MuJoCo 합성본).

### 8) 2026-05-07 CUDA OOM 대응 및 학습 래퍼 보강

#### 8-1) OOM 재현/원인 정리

- `pipet_extended_depth_100` 데이터셋은 360x480 이미지 입력 4개(`front`, `overhead`, `front_depth`, `overhead_depth`)를 사용한다.
- RTX 3080 Laptop 8GB급 GPU에서 ACT 기본 구조(`dim_model=512`, `dim_feedforward=3200`, `chunk_size=40`)와 `batch_size=16` 조합은 첫 backward에서 반복적으로 OOM 발생.
- `PYTORCH_ALLOC_CONF=expandable_segments:True`만으로는 `batch_size=16`을 살릴 수 없었음.
  - allocator 단편화 문제가 아니라, 실제 활성화 메모리 자체가 8GB 한계를 넘는 상황으로 판단.

#### 8-2) `run_lerobot_train.py` 보강

- `ai/lerobot/run_lerobot_train.py`에 ACT 메모리 조절 인자를 추가:
  - `--chunk_size`
  - `--n_action_steps`
  - `--use_amp`
  - `--policy_dim_model`
  - `--policy_dim_feedforward`
  - `--policy_n_heads`
  - `--policy_n_encoder_layers`
  - `--torch_alloc_conf`
- 기존에는 wrapper 내부에서 `policy.chunk_size=40`, `policy.n_action_steps=40`, `policy.use_amp=true`가 하드코딩되어 있었지만, 이제 실행 명령에서 명시적으로 조절 가능.
- 학습 subprocess 실행 시 `--torch_alloc_conf` 기본값(`expandable_segments:True`)을 사용해 아래 환경변수를 자동 주입:
  - `PYTORCH_ALLOC_CONF=expandable_segments:True`
  - `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
- `--n_action_steps > --chunk_size`인 경우 즉시 에러 처리.
- `--policy_n_heads`가 `dim_model`을 나누지 못하는 경우 즉시 에러 처리.

#### 8-3) 검증 결과

- AST parse 통과:
  - `python -c "import ast,pathlib; ast.parse(...run_lerobot_train.py...)"`
- CUDA 1-step smoke test:
  - `batch_size=4`, `chunk_size=20`, `num_workers=0`: 성공
  - `batch_size=4`, `chunk_size=40`, `num_workers=0`: 성공
  - `batch_size=8`, `chunk_size=40`, `num_workers=0`: 성공
  - `batch_size=8`, `chunk_size=40`, `num_workers=4`: 성공
  - `batch_size=16`, `chunk_size=40`, `num_workers=4`: 실패(OOM)
- 결론:
  - 현재 데이터셋/모델/GPU 조합의 안전선은 `batch_size=8`.
  - 데이터 로딩 병목(`data_s`)이 크면 `num_workers=4`가 유리.
  - 그래도 OOM이 나면 `batch_size=4`로 낮추는 것이 다음 대응.

#### 8-4) 최신 재학습 실행안

- 실패한 첫 실행으로 모델 출력 폴더가 일부 생성되었을 수 있으므로, 재학습 전 `ai/models/act_pipet_extended_depth_100`만 삭제한다.
- 변환된 데이터셋(`ai/datasets/pipet_extended_depth_100`)은 삭제하지 않는다.
- 사용자와 최종 합의한 재실행 설정:
  - `steps=80000`
  - `batch_size=8`
  - `chunk_size=40`
  - `n_action_steps=40`
  - `num_workers=4`

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

set -o pipefail

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True

mkdir -p "${HF_DATASETS_CACHE}" ai/logs

OUT_DIR="${PWD}/ai/models/act_pipet_extended_depth_100"

rm -rf "${OUT_DIR}"

python ai/lerobot/run_lerobot_train.py \
  --skip_convert \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100" \
  --dataset_output_dir "${PWD}/ai/datasets/pipet_extended_depth_100" \
  --dataset_repo_id pipet_extended_depth_100 \
  --output_dir "${OUT_DIR}" \
  --job_name act_pipet_extended_depth_100 \
  --steps 80000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 4 \
  --device cuda \
  2>&1 | tee "ai/logs/train_act_pipet_extended_depth_100_$(date +%Y%m%d_%H%M%S).log"
```

## 26.05.09 Gemini-ER 검증기 실험 결과와 grasp-focus 추가 데이터 생성

### 1) 실기 문제 재정의

- 100k step 학습 모델은 파이펫을 완전히 엉뚱한 곳에서 찾는 것은 아니었음.
- 실제 실패는 대부분 마지막 접근 구간에서 발생:
  - 파이펫까지 대략 접근은 하지만 마지막 1~2cm 정밀 위치가 흔들림.
  - grasp가 너무 빠르게 나오거나, 손가락 사이에 파이펫이 충분히 들어가기 전에 닫힘.
  - 실행마다 최종 위치가 조금씩 달라져 성공률이 안정적이지 않음.
- 결론:
  - 단순히 `grasp_delay_steps`, `grasp_confirm_steps`, `pre_grasp_delta_scale` 같은 추론 보정만으로는 한계가 있음.
  - 모델이 "마지막 2cm 접근 + 손가락 사이에 파이펫이 들어간 상태 + 그 직후 grasp" 구간을 더 많이 학습해야 할 가능성이 큼.

### 2) Gemini Robotics-ER 검증기 실험

- 별도 브랜치 `feature/gemini-er-verifier`에서 Gemini Robotics-ER를 grasp 허용 검증기로 붙이는 실험을 진행.
- 목표:
  - Gemini가 로봇을 직접 제어하는 것이 아니라,
  - wrist/overhead 이미지를 보고 파이펫이 손가락 사이에 충분히 들어왔는지 판단하고,
  - 조건이 맞을 때만 ACT의 grasp를 통과시키는 보조 gate로 사용.
- API 확인:
  - `GEMINI_API_KEY` 설정 후 Gemini API 호출 성공.
  - `models/gemini-robotics-er-1.5-preview`, `models/gemini-robotics-er-1.6-preview` 접근 가능 확인.
- 실기 결과:
  - 낮은 빈도(`gemini_er_hz:=0.5`, `0.1`)와 긴 timeout을 적용해도 HTTP 429 quota/rate-limit에 자주 걸림.
  - quota 오류가 발생하면 verifier가 최신 판단을 주지 못하고, grasp gate가 보수적으로 막히는 상황이 생김.
- 결론:
  - Gemini-ER는 디버깅/오프라인 검증 또는 낮은 빈도의 보조 판단기로는 의미가 있음.
  - 현재 API quota 상태에서는 실시간 grasp gate로 쓰기 어렵고, 당장 성공률 개선의 1순위는 데이터 보강으로 판단.

### 3) idle frame 삭제 영향 재검토

- 처음에는 convert 단계에서 정지 프레임을 삭제해서 grasp 직전/직후의 중요한 장면이 빠졌을 가능성을 의심.
- 하지만 기존 `pipet_extended_depth_100` 데이터셋은 raw 100개 episode의 transition 수와 변환 후 frame 수가 거의 일치:
  - raw 기준 transition: 약 35,322
  - 기존 LeRobot dataset `total_frames`: 35,322
- 결론:
  - 이번 실패의 주원인은 "idle frame 삭제"보다는 grasp 근처 장면의 상대적 비중 부족, 마지막 접근 분포 부족, grasp 타이밍 라벨의 애매함에 더 가까움.

### 4) grasp-focus NPZ 추가 데이터 생성

- 기존 100개 성공 episode는 그대로 유지.
- 각 episode에서 첫 `grasp` 시점 주변만 잘라낸 짧은 focus episode를 추가 생성.
- 목적:
  - 전체 approach 데이터는 유지하면서,
  - 마지막 2cm 접근과 grasp 직전/직후 장면의 학습 비중을 높임.

추가한 스크립트:

```text
ai/data_conversion/make_grasp_focus_episodes.py
```

생성 방식:

- 입력: `ros2_ws/episodes/success/26.05.03_half_data_100`
- 출력: `ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus`
- 각 원본 episode를 `_orig_...npz`로 복사.
- 각 episode의 첫 grasp 주변을 잘라 `_grasp_focus_...npz`로 저장.
- 기본 crop 범위:
  - grasp 이전 4.0초
  - grasp 이후 2.0초
  - 20Hz 기준 crop episode당 약 120 frame
- 생성 결과:
  - 원본 100개 + grasp-focus 100개 = 총 200 NPZ
  - NPZ 폴더 용량: 약 37GB

실행 명령:

```bash
python ai/data_conversion/make_grasp_focus_episodes.py \
  --input_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100" \
  --output_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --pre_grasp_sec 4.0 \
  --post_grasp_sec 2.0 \
  --fps 20 \
  2>&1 | tee "ai/logs/make_grasp_focus_episodes_$(date +%Y%m%d_%H%M%S).log"
```

### 5) 새 LeRobot dataset 변환 완료

- 새 NPZ 폴더를 LeRobotDataset 형식으로 변환.
- 출력:

```text
ai/datasets/pipet_extended_depth_100_grasp_focus
```

변환 결과:

- `total_episodes`: 200
- `total_frames`: 47,222
- `fps`: 20
- 데이터셋 용량: 약 20GB
- features:
  - `observation.images.front`
  - `observation.images.front_depth`
  - `observation.images.overhead`
  - `observation.images.overhead_depth`
  - `observation.state`
  - `action`

변환 명령:

```bash
python ai/data_conversion/npz_to_lerobot/convert.py \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --output_dir "${PWD}/ai/datasets/pipet_extended_depth_100_grasp_focus" \
  --output_repo_id pipet_extended_depth_100_grasp_focus \
  --fps 20 \
  --task "Pick up the pipette" \
  --image_resize_to 360x480 \
  --state_profile extended \
  --include_depth \
  --fk_urdf "${PWD}/mujoco_env/generated/indy7_mujoco.urdf" \
  --fk_tcp_frame tcp \
  --log_every_frames 1000 \
  2>&1 | tee "ai/logs/convert_pipet_extended_depth_100_grasp_focus_$(date +%Y%m%d_%H%M%S).log"
```

### 6) 관련 코드 변경

- `ai/data_conversion/make_grasp_focus_episodes.py`
  - grasp 주변 crop episode 생성 스크립트 추가.
- `ai/data_conversion/npz_to_lerobot/convert.py`
  - `--idle_keep_action_window_sec` 인자 추가.
  - `--drop_idle_sec`를 사용할 때 non-hold action 주변 frame을 보호할 수 있도록 보강.
  - 이번 grasp-focus dataset 변환은 idle drop 없이 진행했으므로, 이 옵션은 다음 실험용 안전장치에 가까움.
- `ai/lerobot/run_lerobot_train.py`
  - convert wrapper 경로에도 `--idle_keep_action_window_sec` 전달 가능하게 보강.

검증:

```bash
python -m py_compile \
  ai/data_conversion/make_grasp_focus_episodes.py \
  ai/data_conversion/npz_to_lerobot/convert.py \
  ai/lerobot/run_lerobot_train.py
```

- 위 문법 체크 통과.
- `meta/info.json` 확인 결과 새 dataset의 episode/frame/features 정상.

### 7) 다음 학습안: 60k 먼저 비교

- 기존 100k 모델은 과대적합 또는 최종 접근 위치 외움 가능성이 있음.
- 새 grasp-focus 데이터셋은 grasp 주변 분포를 강화했으므로, 우선 60k step으로 학습해 기존 100k 모델과 비교.
- 성능이 좋아지면 80k도 추가 비교.

추천 실행 명령:

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai

source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs

python ai/lerobot/run_lerobot_train.py \
  --skip_convert \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --dataset_output_dir "${PWD}/ai/datasets/pipet_extended_depth_100_grasp_focus" \
  --dataset_repo_id pipet_extended_depth_100_grasp_focus \
  --job_name act_pipet_extended_depth_100_grasp_focus \
  --steps 60000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 2 \
  --device cuda \
  2>&1 | tee "ai/logs/train_act_pipet_extended_depth_100_grasp_focus_$(date +%Y%m%d_%H%M%S).log"
```

### 8) 참고: 사용하지 않는 중간 산출물

- 이전 실험 중 생성되다 중단된 dataset:

```text
ai/datasets/pipet_extended_depth_100_keep_grasp_idle
```

- 현재 학습에는 사용하지 않음.
- 용량은 약 14GB이며, 디스크 정리가 필요하면 별도로 삭제 가능.

### 9) 2026-05-10 grasp-focus 학습 resume 및 dataloader 병목 대응

#### 9-1) 초기 학습 상태

- 새 dataset `pipet_extended_depth_100_grasp_focus`로 100k 학습을 시작.
- 최초 실행은 `--num_workers 2`로 진행됨.
- 20k 이후 로그에서 관찰:
  - `updt_s`: 약 0.24초
  - `data_s`: 약 2.4~2.6초
- 해석:
  - GPU 계산보다 dataloader/video decoding 쪽이 훨씬 느린 상태.
  - 학습 품질 문제는 아니지만 전체 학습 시간이 길어질 가능성이 큼.
- 기존 원본 100ep 학습은 `--num_workers 4`로 안정적으로 돌았으므로, grasp-focus 학습도 4 worker로 이어가기로 결정.

#### 9-2) checkpoint 확인

- 현재 checkpoint:

```text
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/010000
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/020000
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last -> 020000
```

- 따라서 처음부터 재학습하지 않고 `020000`에서 resume하는 것이 맞음.

#### 9-3) `run_lerobot_train.py` resume 지원 추가

- 기존 wrapper는 `--resume` 인자를 받지 않아 아래 에러 발생:

```text
run_lerobot_train.py: error: unrecognized arguments: --resume
```

- `ai/lerobot/run_lerobot_train.py`에 추가:
  - `--resume`
  - `--resume_config_path`
- 기본 resume config 경로:

```text
<output_dir>/checkpoints/last/pretrained_model/train_config.json
```

- LeRobot 내부 parser는 `--config_path 경로` 형태를 인식하지 못하고,
  `--config_path=경로` 형태만 `parse_arg("config_path")`에서 읽는다.
- 그래서 wrapper는 resume 시 아래처럼 넘기도록 수정:

```text
--resume=true
--config_path=/.../checkpoints/last/pretrained_model/train_config.json
```

#### 9-4) resume 실행 명령

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai

source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs

python ai/lerobot/run_lerobot_train.py \
  --skip_convert \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --dataset_output_dir "${PWD}/ai/datasets/pipet_extended_depth_100_grasp_focus" \
  --dataset_repo_id pipet_extended_depth_100_grasp_focus \
  --output_dir "${PWD}/ai/models/act_pipet_extended_depth_100_grasp_focus" \
  --job_name act_pipet_extended_depth_100_grasp_focus \
  --resume \
  --resume_config_path "${PWD}/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last/pretrained_model/train_config.json" \
  --steps 100000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 4 \
  --device cuda \
  2>&1 | tee "ai/logs/train_act_pipet_extended_depth_100_grasp_focus_resume_workers4_$(date +%Y%m%d_%H%M%S).log"
```

#### 9-5) 확인 포인트

- 시작 로그에서 아래를 확인:
  - `resume=True`
  - `checkpoint_path`가 `.../checkpoints/last` 또는 `020000` 계열을 가리킴
  - `num_workers=4`
- resume은 checkpoint의 기존 train config를 기반으로 하므로, CLI override가 실제 반영되는지 로그 확인이 중요.
- step이 20k 근처에서 이어지면 정상.

---

## 26.05.12 grasp-focus 080000 실기 결과 및 early-grasp 방지 패치

### 1) 080000 모델 실기 결과 요약

실행 모델:

```text
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/080000
```

관찰 결과:

- 10회 시도 중 3회 성공, 7회 실패.
- 성공한 경우도 일부는 너무 빨리 잡거나 헐겁게 잡은 느낌이 있어 완전히 안정적인 성공으로 보기는 어려움.
- 파이펫이 로봇에 가까운 위치일 때 성공 가능성이 높았음.
- 파이펫을 조금 옮기거나 좌우 방향으로 옮기면 실패율이 높아짐.
- 앞뒤 방향 이동은 어느 정도 따라가지만, 좌우 위치 변화와 먼 위치 배치에 약함.
- 70k 모델 대비 grasp-focus 데이터 효과는 분명히 있음. 적어도 파이펫 방향으로 접근하고 일부 조건에서는 실제로 잡음.
- 하지만 핵심 실패는 여전히 "더 깊게 들어간 뒤 잡기"가 아니라 "너무 빨리 잡기"임.

### 2) 갑작스러운 grasp 로그 해석

실기 로그에서 아래 흐름이 확인됨.

```text
grasp delay 시작
grasp gate 통과: confirm=8/8, delta_norm=0.0006
grip_preset_node: grasp: [0.0, 0.0, 350.0, 350.0, 350.0, 0.0]
Mark7SystemHardware: Tx: [0,0,350,350,350,0]
```

해석:

- Mark7이 혼자 닫힌 것이 아니라, ACT 모델 출력이 `grasp`로 해석됨.
- `inference_node`가 delay/confirm/delta gate를 통과시킨 뒤 `/gripper/grasp` 서비스를 호출함.
- 즉 현재 문제는 하드웨어/시리얼 오동작보다는, 모델이 아직 잘못된 위치에서도 `grasp`를 내는 문제에 가까움.

중요:

- `use_zmq_sidecar:=true`일 때 실제로 사용되는 모델은 ROS launch의 `model_path`가 아니라, 별도 터미널에서 켠 `zmq_act_server --model-path ...` 쪽이다.
- 따라서 ZMQ 서버 시작 로그에서 `...grasp_focus/checkpoints/080000` 또는 `pretrained_model` 경로를 실제로 물고 있는지 확인해야 한다.

### 3) Early-grasp 방지 코드 추가

기존 gate:

```text
grasp_delay_steps
pre_grasp_delta_scale
grasp_confirm_steps
grasp_max_delta_norm
```

여기에 아래 파라미터를 추가했다.

```text
grasp_min_elapsed_steps
grasp_min_motion_rad
enable_gripper
```

의도:

- `grasp_min_elapsed_steps`: 추론 시작 후 일정 tick 전에는 모델이 `grasp`를 내도 무조건 보류.
- `grasp_min_motion_rad`: 시작 자세에서 관절 기준으로 일정량 이상 움직이기 전에는 grasp 보류.
- `enable_gripper`: 디버깅용. `false`면 팔만 움직이고 Mark7 서비스 호출은 차단.

수정 파일:

- `ros2_ws/src/pipet_inference/pipet_inference/inference_node.py`
  - 새 파라미터 선언
  - `_gate_gripper_cmd()`에 최소 elapsed/motion 조건 추가
  - `_maybe_gripper_service()`에 `enable_gripper=false` 차단 로직 추가
- `ros2_ws/src/pipet_bringup/launch/inference.launch.py`
  - 새 launch argument 노출

### 4) 다음 실행 명령 변경

기존 실행 명령에서 early-grasp 방지를 위해 아래 값을 추가/강화한다.

```text
grasp_min_elapsed_steps:=50
grasp_min_motion_rad:=0.015
grasp_delay_steps:=12
grasp_confirm_steps:=12
grasp_max_delta_norm:=0.006
```

20Hz 기준 `grasp_min_elapsed_steps:=50`은 약 2.5초이며, 시작하자마자 닫는 현상을 막기 위한 값이다.

실행 명령:

```bash
./run_scripts/40_inference_ros.sh \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/080000 \
  192.168.1.10 \
  /dev/ttyACM0 \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/mujoco_env/generated/indy7_mujoco.urdf \
  26 \
  autonomy_enabled:=true \
  use_zmq_sidecar:=true \
  zmq_endpoint:=tcp://127.0.0.1:5560 \
  image_target_height:=360 \
  image_target_width:=480 \
  grasp_min_elapsed_steps:=50 \
  grasp_min_motion_rad:=0.015 \
  grasp_delay_steps:=12 \
  pre_grasp_delta_scale:=1.15 \
  grasp_confirm_steps:=12 \
  grasp_max_delta_norm:=0.006 \
  max_joint_speed_rad_s:=0.25
```

팔 접근 경로만 확인할 때는 아래를 추가한다.

```text
enable_gripper:=false
```

튜닝 기준:

- 너무 늦게 잡으면 `grasp_min_elapsed_steps`를 40으로 낮춤.
- 아직 너무 빨리 잡으면 `grasp_min_elapsed_steps`를 60으로 올림.
- grasp가 아예 안 나오면 `grasp_confirm_steps`를 줄이거나 `grasp_max_delta_norm`을 0.008 쪽으로 완화.

---

# 26.05.17 작성자: Codex

## Xbox 패드 기반 Indy7 + Mark7 데이터 수집 텔레옵 추가

### 1) 목표
- 기존 키보드 기반 데이터 수집 흐름은 유지한다.
- 추가로 Xbox 컨트롤러로도 Indy7 팔, Mark7 그리퍼, 데이터 수집 시작/종료/라벨링을 수행할 수 있게 한다.
- 데이터 수집 서비스 계약(`/data_collector/start`, `stop`, `mark_success`, `mark_fail`, `discard`)과 그리퍼 action logging 서비스(`/data_collector/log_*`)는 기존 키보드 노드와 동일하게 사용한다.

### 2) 추가된 코드
- 새 노드:
  - `ros2_ws/src/pipet_system_teleop/pipet_system_teleop/xbox_servo_node.py`
- 실행 엔트리 추가:
  - `ros2_ws/src/pipet_system_teleop/setup.py`
  - `xbox_servo_node = pipet_system_teleop.xbox_servo_node:main`

### 3) 실행 방법
먼저 데이터 수집 백엔드/Indy driver/Mark7/카메라를 띄운다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
```

다른 터미널에서 Xbox 텔레옵 노드를 실행한다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run pipet_system_teleop xbox_servo_node
```

입력 값을 확인해야 할 때:

```bash
ros2 run pipet_system_teleop xbox_servo_node --ros-args -p debug_input:=true
```

### 4) 현재 Xbox 조작 매핑
- `D-pad 위/아래`: Indy7 task-space X축 `+/-`
- `D-pad 좌/우`: Indy7 task-space Y축 `+/-`
- `LT / RT`: Z축 `-/+`
- 오른쪽 스틱: Rx/Ry 회전
- `LB / RB`: Rz 회전
- `A`: Mark7 grasp
- `B`: Mark7 open
- `X`: Mark7 press
- `Y`: Mark7 release
- `START`: 녹화 시작. 녹화 중이면 종료/라벨 대기 상태로 전환
- 녹화 종료 라벨 대기 중:
  - `A`: success
  - `B`: fail
  - `X`: discard
- `BACK`: teleop stop 및 relative target reset
- `BACK + A`: Indy recover
- `BACK + B`: Indy zero
- `BACK + Y`: Indy home
- `BACK + LB`: 이동/회전 step 감소
- `BACK + RB`: 이동/회전 step 증가

기본 step:
- `linear_step_mm = 1.0`
- `angular_step_deg = 1.0`
- `BACK+LB/RB`로 `0.25` 단위 조절
- 최대 `5.0`, 최소 `0.1`

처음부터 step을 바꿔 실행할 수도 있다.

```bash
ros2 run pipet_system_teleop xbox_servo_node --ros-args \
  -p linear_step_mm:=2.0 \
  -p angular_step_deg:=2.0
```

### 5) 입력 backend 관련 트러블슈팅
처음에는 `pygame.joystick` 기반으로 구현했으나, 이 환경에서는 다음 현상이 있었다.

- `/usr/bin/python3` 기준 `pygame 2.1.2`, Python `3.10.12`는 정상.
- `pygame.joystick.get_count()`가 1을 반환하고, 컨트롤러 이름도 `Xbox Series X Controller`로 보였음.
- 하지만 `get_axis()`와 `get_button()` 값이 중립 상태에서 변하지 않는 현상이 발생.
- `/dev/input/js0` 직접 읽기(`linuxjs`)도 초기 상태 이벤트만 보이고 실제 조작 변화가 안 보이는 시점이 있었음.
- 컨트롤러를 뽑았다가 다시 꽂은 뒤에는 일시적으로 USB 장치 자체가 사라져 `lsusb`, `/dev/input/js0`, `/dev/input/by-id/*Microsoft*`에 보이지 않는 상태도 발생.
- 이후 재연결 후 컨트롤러 조작이 다시 정상 동작함.

결론:
- 키보드 pygame 입력은 정상이나, Xbox는 `pygame/SDL joystick` 경로가 이 머신에서 불안정했다.
- 현재 기본 입력 backend는 `linuxevdev`로 설정했다.
- 즉 `/dev/input/by-id/*event-joystick` 또는 `/dev/input/event*` 계열을 직접 읽어 ROS 텔레옵 로직에 연결한다.

사용 가능한 backend:

```bash
# 기본값: evdev 직접 읽기
ros2 run pipet_system_teleop xbox_servo_node --ros-args -p input_backend:=linuxevdev

# joystick 호환 장치 직접 읽기
ros2 run pipet_system_teleop xbox_servo_node --ros-args -p input_backend:=linuxjs -p joystick_device:=/dev/input/js0

# pygame joystick 강제 사용
ros2 run pipet_system_teleop xbox_servo_node --ros-args -p input_backend:=pygame
```

### 6) 컨트롤러 인식 확인 절차
USB 레벨 확인:

```bash
lsusb | grep -i -E 'microsoft|xbox|045e'
```

input 장치 확인:

```bash
ls /dev/input/js* /dev/input/by-id/*Microsoft* 2>/dev/null
cat /proc/bus/input/devices | grep -A8 -i 'xbox\|microsoft'
```

정상적으로 잡히면 보통 다음이 보여야 한다.

- `Microsoft Corp. Xbox Wireless Controller`
- `/dev/input/js0`
- `/dev/input/by-id/...event-joystick`
- kernel driver: `xpad`

현재 확인된 드라이버:

```bash
lsmod | grep -E 'xpad|joydev'
# xpad, joydev 로드 확인
```

### 7) 컨트롤러가 갑자기 안 잡힐 때
- USB 케이블이 충전 전용이면 인식되지 않음. 데이터 지원 케이블 필요.
- USB 허브 대신 노트북 본체 포트에 직접 연결해본다.
- Xbox 버튼을 길게 눌러 전원을 껐다가, 유선 연결 상태에서 다시 켠다.
- 배터리를 빼고 유선만으로 연결해본다.
- `lsusb`에 `Microsoft/Xbox/045e`가 없으면 ROS나 pygame 문제가 아니라 OS가 USB 장치 자체를 못 보는 상태다.

### 8) 검증 상태
- `pipet_system_teleop` 패키지 빌드 성공:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select pipet_system_teleop
```

- 빌드 중 기존 `ai/lerobot_source/lerobot`의 Python package identification 에러 로그가 출력되지만, 선택한 `pipet_system_teleop` 빌드는 완료됨.
- `xbox_servo_node`는 `indy_srv`가 없으면 대기한다. 따라서 `data_collection.launch.py` 또는 Indy driver가 먼저 떠 있어야 한다.

---

## Neuromeka IndyDCP3 Python API 정리 문서 추가

관련 문서:
- `docs/neuromeka_indydcp3_summary.md`

### 1) 문서 목적
- Neuromeka 공식 문서의 `Indy > Indy API > IndyDCP3 > Python` 내용을 프로젝트에서 자주 쓰는 관점으로 정리했다.
- Indy7을 Python/DCP3로 직접 제어하거나, ROS driver/service 동작을 이해할 때 참고하기 위한 문서다.

### 2) 핵심 내용
- `IndyDCP3(robot_ip, index)`로 로봇 컨트롤러에 연결한다.
- 주요 응답은 기본적으로 Python `dict` 형태로 반환된다.
- `get_control_state()`에서 관절 위치 `q`와 TCP pose `p`를 확인할 수 있다.
  - `q`: 관절 각도, 단위 `deg`
  - `p`: `[x, y, z, rx, ry, rz]`, 위치 `mm`, 자세 `deg`
- `get_motion_data()`의 `is_target_reached` 또는 `wait_for_motion_state("is_target_reached")`로 모션 완료를 확인한다.
- 상태 확인용 주요 API:
  - `get_robot_data()`
  - `get_control_state()`
  - `get_motion_data()`
  - `get_servo_data()`
  - `get_violation_data()`
  - `get_program_data()`

### 3) 모션/텔레옵 관련 정리
- 기본 모션:
  - `movej()`: 관절 공간 이동
  - `movel()`: 작업공간 선형 이동
  - `movec()`: 원호 이동
  - `stop_motion()`: 모션 정지
- 작업공간 이동의 pose는 `[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]` 형태다.
- 텔레오퍼레이션 API:
  - `start_teleop(method)`
  - `stop_teleop()`
  - `movetelej_rel()`
  - `movetelel_rel()`
- 프로젝트 텔레옵 노드(`keyboard_servo_node`, `xbox_servo_node`)는 이 개념과 맞춰 relative target을 계속 업데이트하는 방식으로 동작한다.

### 4) 실사용 안전 메모
- `movej`, `movel`, `movec`는 명령 전달 즉시 실제 로봇이 움직일 수 있으므로 저속/저가속으로 먼저 확인한다.
- 절대 좌표 이동 전에는 현재 `q`, `p`를 반드시 출력해 확인한다.
- 텔레옵은 `try/finally` 구조로 `stop_teleop()`이 항상 호출되게 하는 것이 안전하다.
- collision/violation 발생 시 `get_violation_data()`를 확인하고 `recover()` 또는 `move_recover_joint()` 흐름을 사용한다.
- direct teaching은 `set_direct_teaching(enable=True/False)` API와 연결된다. 이전 history에 정리한 Indy driver `data=9/10` 처리와 같은 맥락이다.

---

## 데이터 수집 스키마/학습 방향 결정 문서 추가

관련 문서:
- `docs/data_collection_decisions.md`

### 1) 최종 방향
- 데이터는 NPZ episode 파일로 저장한다.
- 라벨은 NPZ 내부 bool이 아니라 경로/파일명으로 관리한다.
- 학습 중심은 `ee_poses` 기반 Cartesian 제어로 둔다.
- `joint_positions`는 학습 중심은 아니지만 상태 확인, 안전 검증, replay/debug 용도로 계속 저장한다.
- 그리퍼 명령은 event가 아니라 mode로 저장한다.
- metadata는 유지보수용으로 저장하되, LeRobot 변환 시 학습 feature에는 넣지 않는다.

저장 경로 기준:

```text
episodes/success/episode_YYYYMMDD_HHMMSS_success.npz
episodes/fail/episode_YYYYMMDD_HHMMSS_fail.npz
episodes/unlabeled/episode_YYYYMMDD_HHMMSS_unlabeled.npz
```

### 2) 현재 NPZ 핵심 키
- `timestamps`: 녹화 시작 기준 상대 시간
- `joint_positions`: Indy7 6축 관절 위치, rad
- `joint_velocities`: 관절 속도
- `ee_poses`: TCP pose `[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]`
- `wrist_rgb_images`: 손목 카메라 RGB
- `overhead_rgb_images`: 오버헤드 카메라 RGB
- `gripper_actions`: 그리퍼 mode
- `home_joint_deg`, `camera_setup`, `joint_names`: metadata

`success` 내부 키는 저장하지 않는다. `fail`과 `unlabeled`가 bool 값에서 구분되지 않는 문제를 피하기 위해 경로/파일명으로 라벨을 판정한다.

### 3) 학습 feature/action 결정
- 필수 observation:
  - `wrist_rgb_images`
  - `overhead_rgb_images`
  - `ee_poses`
- 기본 action:

```text
action = [delta_ee_pose(6), gripper_action(1)]
delta_ee_pose = ee_poses[t+1] - ee_poses[t]
```

- `joint_positions`는 보조 상태로 쓸 수 있으나 중심 action은 `ee_pose` delta로 둔다.
- `gripper_actions`는 아래 mode 정의를 사용한다.

```text
0 = hold
1 = grasp
2 = open
3 = press
4 = release
```

event 방식은 대부분 `0`이 되어 class imbalance가 심해질 수 있으므로 제외했다. mode 방식은 같은 명령이 여러 frame에 유지되어 학습 label을 더 조밀하게 제공한다.

### 4) 저장하지만 학습 feature로 쓰지 않는 항목
- `timestamps`: FPS, drop/jitter, replay/후처리 확인용
- `joint_velocities`: trajectory 분석용
- `joint_names`: column 순서 무결성 확인
- `home_joint_deg`: home position 변경 시 유지보수용
- `camera_setup`: wrist/overhead 구성 변경 추적용

### 5) 저장하지 않기로 한 항목
- NPZ 내부 `success`
- `joint_efforts`: 현재 `/joint_states.effort`가 빈 배열(`[]`)로 publish되어 `(N, 0)` 저장물이 생기므로 제외
- `camera_info`
- depth 이미지
- camera extrinsics / TF
- `schema_version`
- `ee_twist` / TCP velocity
- `episode_phase`
- `robot_status`
- `raw_commanded_action`

현재 baseline은 RGB 두 대와 `ee_pose` 중심으로 먼저 성공 데모 품질을 확보하는 방향이다. depth, TF, camera extrinsics는 baseline 실패 원인이 명확해진 뒤 2차 실험으로 다시 고려한다.

### 6) 현재 추천 수집 전략
- RGB 두 대와 `ee_pose` 중심 스키마로 성공 데모를 먼저 충분히 모은다.
- 학습은 Cartesian action(`delta_ee_pose + gripper_action`)으로 시작한다.
- 실패/에러 episode는 저장하지 않거나 `fail`로 분리한다.
- 데이터 종류를 무리하게 늘리기보다 깨끗한 성공 demo를 우선한다.

### 26.05.17 - `joint_efforts` 수집 제외 결정

- 실제 `/joint_states` 확인 결과 `effort: []`로 publish되는 것을 확인했다.
- 기존 수집 결과에서 `joint_efforts`가 `(N, 0)`으로 저장되어, 의미 있는 6축 토크 데이터가 아니었다.
- 데이터 수집 노드는 `joint_efforts`를 NPZ에 저장하지 않도록 변경한다.
- LeRobot 변환도 `joint_efforts`를 feature로 사용하지 않고, 기본 state를 `[joint_positions, joint_velocities]`로 둔다.

### 26.05.17 - Xbox remove/insert 2단계 수집 흐름 추가

- Xbox 수집 노드에 기본 2단계 workflow를 추가했다.
- 기본 task는 `remove`이며, remove 성공 저장 후 UI에서 insert 수집 여부를 묻는다.
- `A`를 누르면 `insert` task가 armed 상태가 되고, 사용자가 Indy7을 원하는 시작 위치로 옮긴 뒤 `START`로 insert 녹화를 시작한다.
- 저장 경로는 `episodes/remove/<label>/...`, `episodes/insert/<label>/...`처럼 task별로 분리한다.
- NPZ에는 `task_name`, `final_gripper_action`, `quality_warnings` metadata를 추가한다.
- 저장 시 remove는 마지막 gripper action이 잡은 상태(`grasp`/`press`)인지, insert는 놓은 상태(`open`/`release`)인지 점검한다.

### 26.05.18 - Cartesian action 추론 모드 추가

- remove 60개 데이터로 학습한 ACT 모델은 `--action_space cartesian`으로 변환/학습했기 때문에 `action[:6]`이 관절 delta(rad)가 아니라 `delta_ee_pose`다.
- 기존 `inference_node`는 `action[:6]`을 관절 delta로 해석해 `JointTrajectory`를 발행했으므로, 해당 모델을 그대로 `autonomy_enabled:=true`로 실행하면 의미가 다른 명령이 로봇에 전달될 수 있었다.
- `inference_node`에 `control_mode`를 추가했다.
  - `control_mode:=joint`: 기존 방식 유지. `action[:6] -> delta_q(rad)`, `JointTrajectory` 발행, `indy_srv data=6`.
  - `control_mode:=cartesian`: `action[:6] -> delta_ee_pose [x_mm,y_mm,z_mm,rx_deg,ry_deg,rz_deg]`, `/indy/teleop_pose`에 누적 상대 task pose 발행, `indy_srv data=5`.
- Cartesian 모드에서 모델 출력은 매 tick delta로 보고, keyboard/xbox teleop과 동일하게 누적 `relative_pose`로 바꿔 publish한다.
- 안전 클립 파라미터를 분리했다: `max_delta_mm`, `max_delta_deg`, `max_cartesian_speed_mm_s`, `max_angular_speed_deg_s`.
- 현재 학습 모델을 쓸 때는 `control_mode:=cartesian`, `image_target_height:=360`, `image_target_width:=480`, `state_target_dim:=18`을 함께 지정해 학습 입력/출력 구조와 맞춘다.

### 26.05.18 - Indy7 홈 복귀 단독 스크립트 추가

- 추론/텔레옵 실행 후 빠르게 기준 자세로 돌아가기 위해 `control_indy7/indy7/move_home.py`를 추가했다.
- ROS 노드 없이 Neuromeka `IndyDCP3.movej()`를 직접 호출하며, 프로젝트 공통 home joint `[0, 25, -115, 90, 0, 0] deg`를 사용한다.
- `--stop-before`, `--recover`, `--servo-on` 옵션으로 추론/텔레옵 직후 또는 violation 상태에서 필요한 사전 동작을 명시적으로 선택할 수 있게 했다.

### 26.05.18 - Cartesian inference state 입력 정합 수정

- `convert.py`에서 `action_space=cartesian`으로 변환한 데이터셋은 baseline이라도 `observation.state`가 `[q(6), dq(6), ee_pose(6)] == 18D`다.
- 기존 `inference_node`는 `state_target_dim:=18`일 때 `[q, dq, tau]`를 넣고 있었고, 학습 때의 `ee_pose` 자리에 `/joint_states.effort` 기반 값이 들어갔다. 실제 `/joint_states.effort`는 빈 배열이라 0으로 패딩되어 모델 입력 분포가 어긋났다.
- `control_mode:=cartesian`에서는 `/indy/ee_pose`(`Float64MultiArray`, `[x_mm,y_mm,z_mm,rx_deg,ry_deg,rz_deg]`)를 구독해 state를 `[q,dq,ee_pose]`로 구성하도록 수정했다.
- `state_profile=extended` + `action_space=cartesian`으로 학습한 모델은 state가 `[q,dq,ee_pose,gripper_state] == 19D`이므로 추론 시 `state_target_dim:=19`를 사용한다.

### 26.05.18 - remove grasp-focus 증강 데이터 생성

- 현재 remove 모델은 파이펫 위치 접근은 잘하지만 마지막 그리퍼 정렬과 grasp pose 결정이 약했다.
- 접근 구간이 긴 full episode만 학습하면 실제로 중요한 grasp 직전/직후 구간의 비중이 작아질 수 있으므로, 기존 remove 성공 데이터 60개에서 첫 `gripper_actions == 1` 주변 window를 잘라 추가하기로 했다.
- `ai/data_conversion/make_grasp_focus_episodes.py`로 `episodes/remove/grasp_focus_3s2s/success`를 생성했다.
  - 원본 60개를 유지한다.
  - 각 원본에서 첫 grasp 기준 `3.0s` 전부터 `2.0s` 후까지 100 frame crop을 1개씩 추가한다.
  - 결과는 원본 60개 + crop 60개 = 총 120개 episode다.
- 검증 결과 crop 60개 모두 길이 100 frame이고, 첫 grasp는 crop index 60에 위치했다. 모든 crop의 마지막 `gripper_actions`는 `1=grasp`였다.
- 이 데이터는 실제 새 시연을 만든 것은 아니므로, 빠른 재학습 실험용이다. 마지막 정렬 문제가 계속 남으면 별도 `remove_align/success` 데이터를 수집하는 편이 더 강한 개선책이다.

### 26.05.19 - remove grasp-focus v2 학습 계획 (lr↑ + cosine + dropout↓ + drop_idle)

`act_remove_60_cartesian_360` 학습 로그(`ai/logs/train_act_remove_60_20260518_004452.log`)를 다시 보면 train loss가 1K=0.43 → 10K=0.30 → 30K=0.24 → 50K=0.23 → 70K=0.20 → 90K=0.20 으로 50K 이후 사실상 평탄이었다. 설정은 `optimizer_lr=1e-5, scheduler=None, dropout=0.1, use_vae=false, image_transforms.enable=false, batch=8, 60 ep / 25,840 frame`. 즉 추가 step만으로는 더 안 내려간다.

다음 학습은 같은 cartesian baseline 스키마(`state_profile=baseline`, `action_space=cartesian`, `image_resize_to=360x480`)로 grasp-focus 120 ep을 그대로 쓰되, 학습 쪽 손실 평탄을 깨는 데 집중한다.

변경 의도:

- 데이터: grasp-focus 3s2s 120 episode (원본 60 + crop 60) 그대로 사용.
- 변환: `--drop_idle_sec 1.0 --idle_keep_action_window_sec 2.0` 추가. 긴 정지 구간을 잘라 효과적인 gradient 비중을 올리고 0-액션 dominance를 줄인다. grasp 직전/직후는 보호된다.
- Optimizer: `adamw, lr=3e-5, weight_decay=1e-4, grad_clip_norm=10`. 기존 1e-5는 50K 이후 거의 미세조정 수준이라 평탄을 깨기 어렵다.
- Scheduler: `cosine_decay_with_warmup, num_warmup_steps=2000, num_decay_steps=80000, peak_lr=3e-5, decay_lr=3e-6`. 후반 lr을 자연 감쇠시켜 평탄 구간을 추가로 깎는다. `use_policy_training_preset=false`로 두어야 외부 scheduler가 사용된다 (ACT 프리셋은 scheduler=None이 기본).
- 정규화: `policy.dropout=0.05`. 0.1보다 약간 낮춰 train loss를 조금 더 내리고, 실기 일반화 손실은 최소화한다.
- 학습 길이: `steps=80000, eval_freq=10000, save_freq=10000, log_freq=50`. 60 ep 실험에서 80K 이후 사실상 평탄이었으므로 100K는 과학습 위험.
- 배치/워커: `batch_size=8, num_workers=4`. 8GB VRAM(RTX 3080 Laptop) 기준으로 검증된 값.
- ACT 구조는 유지: `chunk_size=40, n_action_steps=40, use_vae=false, use_amp=true, dataset.use_imagenet_stats=true`.
- 출력: `ai/datasets/remove_grasp_focus_3s2s_cartesian_360_v2`, `ai/models/act_remove_grasp_focus_3s2s_cartesian_360_v2`. 기존 `act_remove_60_cartesian_360`은 비교군으로 그대로 둔다.

기대치:

- 동일 ACT-L1 (MEAN_STD 정규화) 기준으로 0.12 ~ 0.15 구간을 목표로 한다. 0.01은 ACT-L1의 정의상 사실상 불가능.
- 실기 평가는 기존과 같이 `inference_node`를 `control_mode:=cartesian`, `state_target_dim:=18`, `image_target_height:=360`, `image_target_width:=480`로 실행한다.

실행 명령(요약):

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
conda activate lerobot

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs ai/datasets ai/models

DATASET_DIR="${PWD}/ai/datasets/remove_grasp_focus_3s2s_cartesian_360_v2"
MODEL_DIR="${PWD}/ai/models/act_remove_grasp_focus_3s2s_cartesian_360_v2"
rm -rf "${DATASET_DIR}" "${MODEL_DIR}"

python ai/data_conversion/npz_to_lerobot/convert.py \
  --episodes_dir "${PWD}/episodes/remove/grasp_focus_3s2s/success" \
  --output_dir "${DATASET_DIR}" \
  --output_repo_id pipet_remove_grasp_focus_3s2s_v2 \
  --fps 0 \
  --task "Remove the pipette from the holder" \
  --only_success \
  --image_resize_to 360x480 \
  --state_profile baseline \
  --action_space cartesian \
  --drop_idle_sec 1.0 \
  --idle_keep_action_window_sec 2.0 \
  --log_every_frames 500

lerobot-train \
  --dataset.repo_id pipet_remove_grasp_focus_3s2s_v2 \
  --dataset.root "${DATASET_DIR}" \
  --policy.type act \
  --policy.push_to_hub false \
  --policy.device cuda \
  --output_dir "${MODEL_DIR}" \
  --job_name act_remove_grasp_focus_3s2s_v2 \
  --batch_size 8 \
  --steps 80000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 50 \
  --num_workers 4 \
  --policy.chunk_size 40 \
  --policy.n_action_steps 40 \
  --policy.use_vae false \
  --policy.use_amp true \
  --policy.dropout 0.05 \
  --dataset.use_imagenet_stats true \
  --use_policy_training_preset false \
  --optimizer.type adamw \
  --optimizer.lr 3e-5 \
  --optimizer.weight_decay 1e-4 \
  --optimizer.grad_clip_norm 10 \
  --scheduler.type cosine_decay_with_warmup \
  --scheduler.num_warmup_steps 2000 \
  --scheduler.num_decay_steps 80000 \
  --scheduler.peak_lr 3e-5 \
  --scheduler.decay_lr 3e-6 \
  2>&1 | tee "ai/logs/train_act_remove_grasp_focus_3s2s_v2_$(date +%Y%m%d_%H%M%S).log"
```

리스크/조치:

- 초기 5K 안에 loss가 튄다 → `optimizer.lr 1.5e-5`, `scheduler.peak_lr 1.5e-5`로 절반.
- VRAM OOM → `batch_size 6`, 그래도 안 되면 `policy.dim_feedforward 2048` 까지 축소.
- `drop_idle_sec` 때문에 `total_frames`가 절반 이하로 줄면 → `drop_idle_sec 1.5`로 완화.

### 26.05.19 - DAgger correction 수집 파이프라인 추가

- grasp-focus v2 모델이 파이펫 위치는 찾지만 grasp 직전 미세 정렬을 실패하는 문제가 남아 있어, 모델 실패 상태에서 인간이 바로잡는 correction 데이터만 따로 수집하는 파이프라인을 추가했다.
- 기존 추론/텔레옵/수집 코드는 수정하지 않고 새 ROS2 패키지 `pipet_dagger_collection`을 추가했다.
- `dagger_collection.launch.py`는 기존 `pipet_bringup/inference.launch.py`를 포함하되, 모델의 cartesian 출력 토픽을 `/indy/teleop_pose`가 아니라 `/dagger/model_teleop_pose`로 돌린다.
- 새 `dagger_supervisor_node`가 평소에는 `/dagger/model_teleop_pose`를 `/indy/teleop_pose`로 forwarding한다.
- 사람이 `START`를 누르면 model forwarding을 중단하고 `/data_collector/start`를 호출해 그 순간부터만 `remove_dagger` correction episode를 녹화한다.
- takeover 중 Xbox 조작은 기존 cartesian teleop과 같은 방식으로 동작한다: D-pad x/y, LT/RT z, right stick rx/ry, LB/RB rz, A/B/X/Y gripper.
- 다시 `START`를 누르면 label 대기 상태가 되고, `A=success`, `B=fail`, `X=discard`로 저장/폐기한다.
- 모델의 잘못된 action 구간은 학습 데이터로 저장하지 않고, 인간이 개입한 정렬/grasp/pull 구간만 `episodes/remove_dagger/<label>` 아래에 저장하는 것이 목적이다.

### 26.05.19 - DAgger-style 수집 기본 속도 보수화

- 실제 DAgger-style rollout 중 로봇이 덜덜 떨리는 현상이 있어, 수집 launch 기본값을 안전한 쪽으로 낮췄다.
- 모델 rollout 기본 속도는 `max_cartesian_speed_mm_s=8.0`, `max_angular_speed_deg_s=8.0`에서 각각 `2.0`으로 낮췄다.
- 모델 tick당 delta clip은 `max_delta_mm=1.0`, `max_delta_deg=1.0`에서 각각 `0.5`로 낮췄다.
- 사람 TAKEOVER 기본 조작 step은 `linear_step_mm=1.0`, `angular_step_deg=1.0`에서 각각 `0.25`로 낮췄다.
- joystick deadzone은 `0.18`에서 `0.22`로 올려 스틱 미세 노이즈가 명령으로 들어가는 것을 줄였다.

### 26.05.19 - DAgger-style 연속 수집 UX 개선

- DAgger-style 수집을 매 episode마다 재실행하지 않고 계속 쓸 수 있도록, 저장/폐기 후 `HOMING` 상태로 전환해 Indy7 HOME 위치로 자동 복귀한 뒤 `AUTO` rollout을 재개하도록 수정했다.
- inference node의 cartesian output은 누적 relative pose이므로, HOME 복귀 후 첫 모델 출력을 새 offset으로 잡아 `/indy/teleop_pose`를 다시 0 기준에서 시작하게 했다. 이 offset reset이 없으면 이전 rollout의 누적 pose가 다음 rollout에 섞여 로봇이 튈 수 있다.
- Pygame UI에 `control:` 줄을 추가해 현재 컨트롤러 조작 가능 상태를 명시한다: `MODEL AUTO active`, `HUMAN TAKEOVER ACTIVE`, `LABEL ONLY`, `LOCKED`, `PAUSED`.
- TAKEOVER 중 속도 조절을 위해 왼쪽 스틱 클릭은 step 감소, 오른쪽 스틱 클릭은 step 증가로 추가했다. 기존 `BACK+LB/RB` 조합은 `BACK` emergency stop과 충돌하기 쉬워 주 조작법에서 제외했다.
- 안전상 `BACK`은 계속 emergency stop/discard로 유지하며, 자동 재개 대신 `PAUSED`에 머무르게 했다.

### 26.05.19 - DAgger-style AUTO forwarding 차단 수정

- `/dagger/model_teleop_pose`에는 모델 출력이 나오는데 `/indy/teleop_pose`가 publish되지 않는 현상이 있었다.
- 원인은 DAgger supervisor가 AUTO forwarding 전에 `indy_srv` task teleop 준비 확인을 동기 호출했고, 이 서비스 준비/응답 문제로 토픽 publish 자체가 막힐 수 있었기 때문이다.
- inference launch가 이미 cartesian teleop 준비를 수행하므로, AUTO에서는 모델 pose를 `/indy/teleop_pose`로 바로 forwarding하도록 수정했다.
- TAKEOVER 수동 조작은 기존처럼 실제 조작 직전에 task teleop 준비를 확인한다.
