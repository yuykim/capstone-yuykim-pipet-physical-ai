from pathlib import Path
import numpy as np

folder = Path("ai/indy7_lerobot/raw_data")

for path in sorted(folder.glob("*.npz")):
    print("=" * 60)
    print("file:", path.name)

    data = np.load(path, allow_pickle=True)
    for key in data.files:
        arr = data[key]
        print(f"{key:20s} shape={arr.shape}, dtype={arr.dtype}")
    print()

# timestamps: (N,)
# joint_positions: (N, 6)
# joint_velocities: (N, 6)
# joint_efforts: (N, 6)
# wrist_rgb_images: (N, 480, 640, 3)
# overhead_rgb_images: (N, 480, 640, 3)
# gripper_actions: (N,)
# success: () 스칼라 bool