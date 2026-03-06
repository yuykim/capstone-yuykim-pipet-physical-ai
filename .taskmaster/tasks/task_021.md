# Task ID: 21

**Title:** NPZ to HDF5 변환 스크립트 작성 (Robomimic용)

**Status:** pending

**Dependencies:** 19

**Priority:** medium

**Description:** NPZ 에피소드를 Robomimic/Isaac Lab용 HDF5 포맷으로 변환하는 스크립트를 작성한다.

**Details:**

ai/data_conversion/npz_to_hdf5/convert.py에서 Robomimic의 데모 그룹 구조 (obs/actions/dones) 준수. h5py를 사용하여 robomimic_dataset.hdf5 파일 생성. observation에는 joint_positions와 rgb_images, action에는 다음 스텝 joint_positions와 gripper_actions 저장.

**Test Strategy:**

생성된 HDF5 파일을 Robomimic 데이터 로더로 검증. 파일 구조와 데이터 타입 확인.
