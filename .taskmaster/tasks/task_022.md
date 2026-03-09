# Task ID: 22

**Title:** NPZ to Unity Demo 변환 스크립트 작성

**Status:** pending

**Dependencies:** 19

**Priority:** medium

**Description:** NPZ 에피소드를 Unity ML-Agents GAIL 학습용 데모 포맷으로 변환하는 스크립트를 작성한다.

**Details:**

ai/data_conversion/npz_to_unity/convert.py에서 Unity ML-Agents demonstration recorder 출력 포맷과 호환되도록 변환. observation과 action을 Unity 환경에 맞는 형태로 재구성.

**Test Strategy:**

Unity ML-Agents 환경에서 변환된 demo 파일 로드 가능 여부 확인.
