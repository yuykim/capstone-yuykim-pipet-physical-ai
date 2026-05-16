#!/usr/bin/env python3
"""Read current Indy7 joint values through Neuromeka IndyDCP3."""

import argparse
import json
import math
import time
from datetime import datetime


DEFAULT_ROBOT_IP = "192.168.1.10"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read Indy7 joint values from get_control_state()."
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
        "--watch",
        action="store_true",
        help="Keep reading until Ctrl+C.",
    )
    parser.add_argument(
        "--hz",
        type=float,
        default=2.0,
        help="Read rate in watch mode. Default: 2.0",
    )
    parser.add_argument(
        "--rad",
        action="store_true",
        help="Also print joint positions converted to radians.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print one JSON object per sample.",
    )
    return parser.parse_args()


def format_sample(control_state, include_rad=False):
    q_deg = [float(v) for v in control_state["q"]]
    tpos = [float(v) for v in control_state["p"]]
    sample = {
        "time": datetime.now().isoformat(timespec="milliseconds"),
        "q_deg": q_deg,
        "tcp_pose": tpos,
    }
    if include_rad:
        sample["q_rad"] = [math.radians(v) for v in q_deg]
    return sample


def print_sample(sample, as_json=False):
    if as_json:
        print(json.dumps(sample, ensure_ascii=False))
        return

    print(f"[{sample['time']}]")
    print("q_deg   :", " ".join(f"{v:9.3f}" for v in sample["q_deg"]))
    if "q_rad" in sample:
        print("q_rad   :", " ".join(f"{v:9.5f}" for v in sample["q_rad"]))
    print("tcp_pose:", " ".join(f"{v:9.3f}" for v in sample["tcp_pose"]))


def main():
    args = parse_args()
    if args.hz <= 0:
        raise ValueError("--hz must be greater than 0")

    try:
        from neuromeka import IndyDCP3
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "neuromeka Python package is not installed in this environment.\n"
            "Install it with: pip3 install neuromeka"
        ) from exc

    indy = IndyDCP3(robot_ip=args.ip, index=args.index)
    interval = 1.0 / args.hz

    try:
        while True:
            control_state = indy.get_control_state()
            sample = format_sample(control_state, include_rad=args.rad)
            print_sample(sample, as_json=args.json)

            if not args.watch:
                break

            if not args.json:
                print()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
