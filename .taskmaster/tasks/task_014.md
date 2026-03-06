# Task ID: 14

**Title:** 에피소드 NPZ 저장 기능 구현

**Status:** pending

**Dependencies:** 13

**Priority:** high

**Description:** 동기화된 데이터를 에피소드 단위로 NPZ 파일에 저장하는 기능을 구현한다.

**Details:**

동기화된 데이터 프레임을 메모리에 버퍼링. RGB/Depth 이미지를 224x224로 리사이즈. gripper_actions는 키 입력 이벤트를 0(유지)/1(잡기)/2(펴기)/3(누르기)로 매핑. 녹화 중지 시 episodes/episode_<YYYYMMDD_HHMMSS>.npz 파일로 저장. numpy 배열 형태로 timestamps, joint_positions, joint_velocities, joint_efforts, rgb_images, depth_images, gripper_actions 저장.

**Test Strategy:**

10초 녹화 후 생성된 NPZ 파일을 numpy.load로 로드하여 모든 키 존재 확인. rgb_images shape (N,224,224,3) uint8, gripper_actions 범위 0-3 검증.
