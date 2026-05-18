#!/usr/bin/env python3
"""Move Indy7 to the project home joint position with Neuromeka IndyDCP3."""

import argparse
import time


DEFAULT_ROBOT_IP = "192.168.1.10"
HOME_JOINT_DEG = [0.0, 25.0, -115.0, 90.0, 0.0, 0.0]
DEFAULT_VEL_RATIO = 10
DEFAULT_ACC_RATIO = 10


def parse_args():
    parser = argparse.ArgumentParser(
        description="Move Indy7 to HOME_JOINT_DEG using the Neuromeka Python API."
    )
    parser.add_argument(
        "--ip",
        default=DEFAULT_ROBOT_IP,
        help=f"Indy controller IP address. Default: {DEFAULT_ROBOT_IP}",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Robot index for multi-robot controllers. Default: 0",
    )
    parser.add_argument(
        "--vel-ratio",
        type=int,
        default=DEFAULT_VEL_RATIO,
        help=f"movej velocity ratio. Default: {DEFAULT_VEL_RATIO}",
    )
    parser.add_argument(
        "--acc-ratio",
        type=int,
        default=DEFAULT_ACC_RATIO,
        help=f"movej acceleration ratio. Default: {DEFAULT_ACC_RATIO}",
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Call recover() before moving. Use after a violation/error state.",
    )
    parser.add_argument(
        "--servo-on",
        action="store_true",
        help="Call set_servo_all(True) before moving.",
    )
    parser.add_argument(
        "--stop-before",
        action="store_true",
        help="Call stop_motion(2) before moving. Useful after teleop/inference.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait for is_target_reached after sending movej.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        from neuromeka import IndyDCP3
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "neuromeka Python package is not installed in this environment.\n"
            "Try: /usr/bin/python3 -m pip install neuromeka"
        ) from exc

    indy = IndyDCP3(robot_ip=args.ip, index=args.index)

    if args.stop_before:
        print("Stopping current motion...")
        indy.stop_motion(2)
        time.sleep(0.5)

    if args.recover:
        print("Recovering robot...")
        indy.recover()
        time.sleep(1.0)

    if args.servo_on:
        print("Turning all servos on...")
        indy.set_servo_all(True)
        time.sleep(1.0)

    print(f"Moving Indy7 HOME: {HOME_JOINT_DEG} deg")
    print(f"vel_ratio={args.vel_ratio}, acc_ratio={args.acc_ratio}")
    indy.movej(
        jtarget=HOME_JOINT_DEG,
        vel_ratio=args.vel_ratio,
        acc_ratio=args.acc_ratio,
    )

    if not args.no_wait:
        indy.wait_for_motion_state("is_target_reached")

    print("Indy7 HOME reached.")


if __name__ == "__main__":
    main()
