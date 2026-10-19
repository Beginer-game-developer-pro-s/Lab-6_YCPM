#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nfr_validator.py
Lab 6 - Non-functional Requirements
--------------------------------------
Simulates verification of two representative non-functional
requirements:
  - NFR-001 (Performance): doctor-search API response time under a
    load of 500 concurrent users must be <= 2 seconds (p95).
  - NFR-007 (Safety): appointment double-booking conflict must be
    detected within <= 1 second.

No real system is needed: a controlled random simulation (fixed seed)
is used so results are reproducible, illustrating the principle of
"SMART measurement" for NFRs.

Run: python3 nfr_validator.py
"""
import random
import statistics
import csv
import os

random.seed(42)

def _datasets_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "datasets"),
        os.path.join(here, "..", "..", "..", "datasets"),
        os.path.join(here, "..", "..", "Lab 4_YCPM", "datasets-for-LABs", "datasets"),
    ]
    for candidate in candidates:
        path = os.path.normpath(candidate)
        if os.path.isfile(os.path.join(path, "nonfunctional_requirements.csv")):
            return path
    return os.path.normpath(candidates[0])


BASE = _datasets_dir()
REPORT_PATH = os.path.join(os.path.dirname(__file__), "nfr_validation_report.md")


def load_nfrs():
    with open(os.path.join(BASE, "nonfunctional_requirements.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def simulate_load_test(n_requests=500, base_latency_ms=350, jitter_ms=900):
    """Simulate response latency of the doctor-search API under concurrent load."""
    latencies = []
    for _ in range(n_requests):
        latency = base_latency_ms + random.random() * jitter_ms
        # 3% of requests are abnormally slow (simulating GC pause / cold cache)
        if random.random() < 0.03:
            latency += random.uniform(800, 1500)
        latencies.append(latency)
    latencies.sort()
    p95 = latencies[int(0.95 * len(latencies)) - 1]
    p50 = statistics.median(latencies)
    return {"n": n_requests, "p50_ms": p50, "p95_ms": p95,
            "max_ms": max(latencies), "pass": p95 <= 2000}


def simulate_conflict_detection(n_trials=200):
    """Simulate the time to detect a double-booking conflict."""
    detection_times = []
    for _ in range(n_trials):
        # Time to check the unique(doctor, slot) database constraint
        t = random.uniform(0.02, 0.85)  # seconds
        detection_times.append(t)
    p99 = sorted(detection_times)[int(0.99 * n_trials) - 1]
    return {"n": n_trials, "p99_s": p99, "pass": p99 <= 1.0}


def main():
    nfrs = load_nfrs()
    nfr_map = {n["NFRID"]: n for n in nfrs}

    perf_result = simulate_load_test()
    safety_result = simulate_conflict_detection()

    report = ["# NFR Verification Report (simulation)\n"]

    report.append("## NFR-001 -- Doctor search performance")
    report.append(f"- Criterion: {nfr_map['NFR-001']['SMARTMeasurementCriterion']}")
    report.append(f"- Simulation result: p50={perf_result['p50_ms']:.0f}ms, "
                   f"p95={perf_result['p95_ms']:.0f}ms, max={perf_result['max_ms']:.0f}ms "
                   f"(n={perf_result['n']} requests)")
    report.append(f"- **Conclusion: {'PASS' if perf_result['pass'] else 'FAIL'}** "
                   f"(threshold p95 <= 2000ms)\n")

    report.append("## NFR-007 -- Booking conflict detection safety")
    report.append(f"- Criterion: {nfr_map['NFR-007']['SMARTMeasurementCriterion']}")
    report.append(f"- Simulation result: p99={safety_result['p99_s']:.3f}s "
                   f"(n={safety_result['n']} trials)")
    report.append(f"- **Conclusion: {'PASS' if safety_result['pass'] else 'FAIL'}** "
                   f"(threshold p99 <= 1.0s)\n")

    content = "\n".join(report)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(content)
    print(f"\n[OK] Report saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()
