#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
from rclpy.serialization import deserialize_message
from rosbag2_py import ConverterOptions, SequentialReader, StorageOptions


def main():
    parser = argparse.ArgumentParser(
        description="Extract acc/gyro samples from a controller_msgs/IMUData rosbag "
        "into a numpy cache for Allan deviation analysis. "
        "Run `source setup_env.sh` first so controller_msgs is importable."
    )
    parser.add_argument("bag_path", help="Path to the rosbag2 .db3 file")
    parser.add_argument("--topic", default="/ImuData")
    args = parser.parse_args()

    from controller_msgs.msg import IMUData

    reader = SequentialReader()
    reader.open(
        StorageOptions(uri=args.bag_path, storage_id="sqlite3"),
        ConverterOptions(input_serialization_format="cdr", output_serialization_format="cdr"),
    )

    stamps, acc, gyro = [], [], []
    while reader.has_next():
        topic, data, _ = reader.read_next()
        if topic != args.topic:
            continue
        msg = deserialize_message(data, IMUData)
        stamps.append(msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9)
        acc.append(msg.acc.copy())
        gyro.append(msg.gyro.copy())

    if len(stamps) < 2:
        raise SystemExit(f"No messages found on topic {args.topic}")

    stamps = np.array(stamps)
    acc = np.array(acc)
    gyro = np.array(gyro)

    rate = (len(stamps) - 1) / (stamps[-1] - stamps[0])
    print(f"{len(stamps)} samples, {stamps[-1] - stamps[0]:.1f} s, ~{rate:.2f} Hz")
    print(f"acc  mean (xyz): {acc.mean(axis=0)}  std: {acc.std(axis=0)}")
    print(f"gyro mean (xyz): {gyro.mean(axis=0)}  std: {gyro.std(axis=0)}")

    output = Path(__file__).parent / "outputs" / "imu_bag_cache.npz"
    np.savez(output, stamps=stamps, acc=acc, gyro=gyro)
    print(f"saved cache to {output}")


if __name__ == "__main__":
    main()
