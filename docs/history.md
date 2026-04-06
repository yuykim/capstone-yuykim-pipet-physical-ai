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

### 4) 학습 데이터 통계(`ai/training_data/meta/stats.json`)와 액션 정의
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