#!/usr/bin/env python3
import argparse
from pathlib import Path

import matplotlib
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def overlapping_allan(rate, dt, m_values):
    theta = np.concatenate(([0.0], np.cumsum(rate) * dt))
    out = []
    for m in m_values:
        n = len(theta) - 2 * m
        if n < 10:
            continue
        diffs = theta[2 * m:2 * m + n] - 2 * theta[m:m + n] + theta[0:n]
        avar = np.sum(diffs**2) / (2.0 * (m * dt) ** 2 * n)
        out.append((m * dt, np.sqrt(avar)))
    return np.array(out)

def write_yaml(results):
    yaml_path = Path(__file__).parent / "outputs" / "imu_noise.yaml"

    clean_results = {
        signal: {key: float(value) for key, value in metric.items()}
        for signal, metric in results.items()
    }

    with open(yaml_path, 'w') as file:
        yaml.dump(clean_results, file)

    print(f"\nResults saved at {yaml_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Compute per-axis Allan deviation curves for gyro/accel from an IMU bag "
        "cache produced by extract_imu_bag.py, and derive white-noise and bias-instability "
        "coefficients usable as Gazebo IMU sensor noise parameters."
    )
    parser.add_argument("--dt", type=float, default=0.01, help="Nominal sample period in seconds (default: 0.01 = 100 Hz)")
    args = parser.parse_args()

    cache_path = Path(__file__).parent / "outputs" / "imu_bag_cache.npz"
    data = np.load(cache_path)
    acc, gyro = data["acc"], data["gyro"]
    n_samples = len(gyro)

    m_values = np.unique(np.logspace(0, np.log10(n_samples // 3), 150).astype(int))
    labels = ["x", "y", "z"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))

    results = {}
    for col, axis in enumerate(labels):
        for row, (name, arr) in enumerate([("gyro", gyro), ("acc", acc)]):
            curve = overlapping_allan(arr[:, col], args.dt, m_values)
            tau, adev = curve[:, 0], curve[:, 1]
            white_noise_coeff = np.mean(adev[:8] * np.sqrt(tau[:8]))
            idx_min = np.argmin(adev)
            bias_instability = adev[idx_min] * 0.664
            results[f"{name}_{axis}"] = dict(N=white_noise_coeff, B=bias_instability, tau_min=tau[idx_min])

            ax = axes[row, col]
            ax.loglog(tau, adev)
            ax.axvline(tau[idx_min], color="r", linestyle="--", alpha=0.5)
            ax.set_title(f"{name} {axis}")
            ax.set_xlabel("tau (s)")
            ax.set_ylabel("Allan deviation")
            ax.grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plot_path = Path(__file__).parent / "outputs" / "allan_deviation.png"
    plt.savefig(plot_path, dpi=120)
    print(f"saved plot to {plot_path}")

    print(f"\n{'signal':10s} {'N (white noise, /sqrt(Hz))':28s} {'B (bias instability)':24s} {'tau_min (s)':12s}")
    for k, v in results.items():
        print(f"{k:10s} {v['N']:.6e}                {v['B']:.6e}              {v['tau_min']:.2f}")

    write_yaml(results)


if __name__ == "__main__":
    main()
