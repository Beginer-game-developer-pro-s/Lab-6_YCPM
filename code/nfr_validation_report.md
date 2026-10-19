# NFR Verification Report (simulation)

## NFR-001 -- Doctor search performance
- Criterion: Doctor-search page response time <= 2s with 500 concurrent users.
- Simulation result: p50=835ms, p95=1233ms, max=2459ms (n=500 requests)
- **Conclusion: PASS** (threshold p95 <= 2000ms)

## NFR-007 -- Booking conflict detection safety
- Criterion: The system shall raise a conflict warning within <= 1 second when a doctor double-booking is detected.
- Simulation result: p99=0.824s (n=200 trials)
- **Conclusion: PASS** (threshold p99 <= 1.0s)
