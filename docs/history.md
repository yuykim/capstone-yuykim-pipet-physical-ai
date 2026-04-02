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