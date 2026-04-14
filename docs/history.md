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