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