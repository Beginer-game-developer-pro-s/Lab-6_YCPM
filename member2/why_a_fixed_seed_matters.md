# Why a Fixed Seed Matters

**Lab 06 — Member 2: Simulation & Data Analyst**  
**Author:** Trần Doãn Việt Anh  
**Source under test:** `code/nfr_validator.py` (`random.seed(42)`)

Stochastic NFR simulations do not observe a live clinic; they draw latency and detection times from a pseudo-random generator. Python’s `random` module is a deterministic Mersenne Twister. Calling `random.seed(42)` writes a known internal state, so every later `random.random()` and `random.uniform()` call is a pure function of that state and of the algorithm. The doctor-search load test (NFR-001, *n* = 500) and the double-booking detection test (NFR-007, *n* = 200) therefore become repeatable experiments rather than one-off anecdotes.

**Reproducibility.** With seed 42, any machine that re-runs the validator obtains the same statistics: NFR-001 *p*50 = 835 ms, *p*95 = 1233 ms, max = 2459 ms, and NFR-007 *p*99 = 0.824 s. Both still meet their SMART thresholds (*p*95 ≤ 2000 ms; *p*99 ≤ 1.0 s) and are recorded as PASS. If the seed were omitted, a later execution could shift the tail percentiles even though the model never changed, making “PASS/FAIL” untrustworthy as scientific evidence.

**Peer review.** Instructors and testers can execute the same command and match the published figures sample-for-sample. A shared seed prevents cherry-picking a lucky draw and turns the report into an inspectable artefact: disagreement would indicate a code or environment difference, not chance.

**Baseline comparison.** Seed 42 freezes the control condition for future optimisation. Caching, indexing, or a faster conflict check can be judged only if the random stream is held constant; otherwise a drop in *p*95 might be luck. Independent multi-seed trials remain useful to show that PASS is not an artefact of 42 alone, but the official baseline stays locked so that before/after deltas are attributable to the system, not to the generator.

---

## Appendix — Independent multi-seed test of Member 1’s functions

Member 1’s `simulate_load_test` (NFR-001) and `simulate_conflict_detection` (NFR-007) were re-executed with seeds `{1, 7, 42, 100, 2026}`. Across these five streams, NFR-001 *p*95 stayed in **1231.5–1236.1 ms** (mean 1232.9 ms, population stdev 1.7 ms) and NFR-007 *p*99 stayed in **0.824–0.845 s** (mean 0.837 s, stdev 0.007 s). The pass rate was **100%** against *p*95 ≤ 2000 ms and *p*99 ≤ 1.0 s. The algorithm is therefore stable: a fixed seed is required for bit-level reproducibility, but the PASS verdict is not an artefact of seed 42.

Raw samples: `nfr001_measurements_seed42.csv`, `nfr007_measurements_seed42.csv`.  
Summaries: `nfr_baseline_summary_seed42.csv`, `nfr_stability_multi_seed.csv`.
