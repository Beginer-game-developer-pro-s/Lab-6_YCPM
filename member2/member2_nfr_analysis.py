#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Member 2 — Simulation & Data Analyst
Trần Doãn Việt Anh

Collects baseline measurements (seed=42) for NFR-001 and NFR-007 using
Member 1's simulation functions, then re-runs those functions across
multiple seeds to assess algorithmic stability.
"""
from __future__ import annotations

import csv
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.normpath(os.path.join(HERE, "..", "code"))
sys.path.insert(0, CODE_DIR)

import nfr_validator as nv  # noqa: E402


SEEDS = (1, 7, 42, 100, 2026)


def percentile_sorted(sorted_values, p):
    """Match Member 1's index rule: values[int(p * n) - 1]."""
    n = len(sorted_values)
    return sorted_values[int(p * n) - 1]


def collect_raw_stream(seed=42):
    """Replay Member 1's RNG stream so raw samples match the report."""
    random.seed(seed)
    latencies = []
    slow_flags = []
    for _ in range(500):
        latency = 350 + random.random() * 900
        is_slow = random.random() < 0.03
        if is_slow:
            latency += random.uniform(800, 1500)
        latencies.append(latency)
        slow_flags.append(is_slow)

    detection_times = [random.uniform(0.02, 0.85) for _ in range(200)]
    return latencies, slow_flags, detection_times


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def baseline_seed42():
    latencies, slow_flags, detection_times = collect_raw_stream(42)
    sorted_lat = sorted(latencies)
    sorted_det = sorted(detection_times)

    nfr001 = {
        "nfr_id": "NFR-001",
        "metric": "doctor_search_latency",
        "seed": 42,
        "n": 500,
        "p50_ms": statistics.median(latencies),
        "p95_ms": percentile_sorted(sorted_lat, 0.95),
        "max_ms": max(latencies),
        "threshold": "p95 <= 2000 ms",
        "verdict": "PASS" if percentile_sorted(sorted_lat, 0.95) <= 2000 else "FAIL",
    }
    nfr007 = {
        "nfr_id": "NFR-007",
        "metric": "conflict_detection_time",
        "seed": 42,
        "n": 200,
        "p99_s": percentile_sorted(sorted_det, 0.99),
        "threshold": "p99 <= 1.0 s",
        "verdict": "PASS" if percentile_sorted(sorted_det, 0.99) <= 1.0 else "FAIL",
    }

    write_csv(
        os.path.join(HERE, "nfr001_measurements_seed42.csv"),
        ["request_id", "latency_ms", "abnormal_slow_tail"],
        [
            {
                "request_id": i + 1,
                "latency_ms": f"{lat:.6f}",
                "abnormal_slow_tail": int(flag),
            }
            for i, (lat, flag) in enumerate(zip(latencies, slow_flags))
        ],
    )
    write_csv(
        os.path.join(HERE, "nfr007_measurements_seed42.csv"),
        ["trial_id", "detection_time_s"],
        [
            {"trial_id": i + 1, "detection_time_s": f"{t:.6f}"}
            for i, t in enumerate(detection_times)
        ],
    )
    write_csv(
        os.path.join(HERE, "nfr_baseline_summary_seed42.csv"),
        [
            "nfr_id",
            "metric",
            "seed",
            "n",
            "p50_ms",
            "p95_ms",
            "max_ms",
            "p99_s",
            "threshold",
            "verdict",
        ],
        [
            {
                "nfr_id": nfr001["nfr_id"],
                "metric": nfr001["metric"],
                "seed": nfr001["seed"],
                "n": nfr001["n"],
                "p50_ms": f"{nfr001['p50_ms']:.0f}",
                "p95_ms": f"{nfr001['p95_ms']:.0f}",
                "max_ms": f"{nfr001['max_ms']:.0f}",
                "p99_s": "",
                "threshold": nfr001["threshold"],
                "verdict": nfr001["verdict"],
            },
            {
                "nfr_id": nfr007["nfr_id"],
                "metric": nfr007["metric"],
                "seed": nfr007["seed"],
                "n": nfr007["n"],
                "p50_ms": "",
                "p95_ms": "",
                "max_ms": "",
                "p99_s": f"{nfr007['p99_s']:.3f}",
                "threshold": nfr007["threshold"],
                "verdict": nfr007["verdict"],
            },
        ],
    )
    return nfr001, nfr007


def independent_multi_seed():
    """Call Member 1's simulation functions under several seeds."""
    rows = []
    for seed in SEEDS:
        random.seed(seed)
        perf = nv.simulate_load_test()
        safety = nv.simulate_conflict_detection()
        rows.append(
            {
                "seed": seed,
                "nfr001_n": perf["n"],
                "nfr001_p50_ms": f"{perf['p50_ms']:.3f}",
                "nfr001_p95_ms": f"{perf['p95_ms']:.3f}",
                "nfr001_max_ms": f"{perf['max_ms']:.3f}",
                "nfr001_verdict": "PASS" if perf["pass"] else "FAIL",
                "nfr007_n": safety["n"],
                "nfr007_p99_s": f"{safety['p99_s']:.6f}",
                "nfr007_verdict": "PASS" if safety["pass"] else "FAIL",
            }
        )

    write_csv(
        os.path.join(HERE, "nfr_stability_multi_seed.csv"),
        [
            "seed",
            "nfr001_n",
            "nfr001_p50_ms",
            "nfr001_p95_ms",
            "nfr001_max_ms",
            "nfr001_verdict",
            "nfr007_n",
            "nfr007_p99_s",
            "nfr007_verdict",
        ],
        rows,
    )

    p95_values = [float(r["nfr001_p95_ms"]) for r in rows]
    p99_values = [float(r["nfr007_p99_s"]) for r in rows]
    stats = {
        "nfr001_p95_mean": statistics.mean(p95_values),
        "nfr001_p95_stdev": statistics.pstdev(p95_values),
        "nfr001_p95_min": min(p95_values),
        "nfr001_p95_max": max(p95_values),
        "nfr007_p99_mean": statistics.mean(p99_values),
        "nfr007_p99_stdev": statistics.pstdev(p99_values),
        "nfr007_p99_min": min(p99_values),
        "nfr007_p99_max": max(p99_values),
        "nfr001_pass_rate": sum(r["nfr001_verdict"] == "PASS" for r in rows) / len(rows),
        "nfr007_pass_rate": sum(r["nfr007_verdict"] == "PASS" for r in rows) / len(rows),
    }
    return rows, stats


def main():
    nfr001, nfr007 = baseline_seed42()
    rows, stats = independent_multi_seed()

    print("=== Baseline seed=42 ===")
    print(
        f"NFR-001: p50={nfr001['p50_ms']:.0f}ms, p95={nfr001['p95_ms']:.0f}ms, "
        f"max={nfr001['max_ms']:.0f}ms (n={nfr001['n']}) -> {nfr001['verdict']}"
    )
    print(
        f"NFR-007: p99={nfr007['p99_s']:.3f}s (n={nfr007['n']}) -> {nfr007['verdict']}"
    )
    print("\n=== Multi-seed stability (Member 1 functions) ===")
    for r in rows:
        print(
            f"seed={r['seed']:>4}: NFR-001 p95={r['nfr001_p95_ms']}ms "
            f"[{r['nfr001_verdict']}] | NFR-007 p99={r['nfr007_p99_s']}s "
            f"[{r['nfr007_verdict']}]"
        )
    print(
        f"\nNFR-001 p95: mean={stats['nfr001_p95_mean']:.1f}ms, "
        f"stdev={stats['nfr001_p95_stdev']:.1f}ms, "
        f"range=[{stats['nfr001_p95_min']:.1f}, {stats['nfr001_p95_max']:.1f}] "
        f"pass_rate={stats['nfr001_pass_rate']:.0%}"
    )
    print(
        f"NFR-007 p99: mean={stats['nfr007_p99_mean']:.3f}s, "
        f"stdev={stats['nfr007_p99_stdev']:.4f}s, "
        f"range=[{stats['nfr007_p99_min']:.3f}, {stats['nfr007_p99_max']:.3f}] "
        f"pass_rate={stats['nfr007_pass_rate']:.0%}"
    )


if __name__ == "__main__":
    main()
