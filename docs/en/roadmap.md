# Project roadmap

| Milestone | Development | Expected result |
|---|---|---|
| Phase 1 | Simulation, synthetic MLP, UI, baseline safety | Demonstrable software pipeline |
| Phase 1.1 | Bench Test 1 with one motor | Short spin validated with start and stop ramps |
| Phase 1.2 | Bench Test 2 with gradient | `10% -> 60% -> 25%` profile validated with logs |
| Phase 1.3 | Bench application | Button-based operation, serial-port selection, logs, and visible stop |
| Phase 2 | Anemometer, optional LiDAR, real dataset | Calibrated model |
| Phase 3 | Feed-forward plus feedback control and watchdog | Closed-loop prototype |
| Phase 4 | Duct, flow straightener, instrumentation | More uniform spatial profile |
| Phase 5 | Multiple motors and multivariable control | Programmable wind field |
| Phase 6 | Kaimal spectra, coupled scenarios, LSTM/TCN research | Richer offshore scenarios |
| Phase 7 | Digital twin, uncertainty, anomaly detection | Auditable operation |
| Phase 8 | Standards-based testing and independent review | Path toward industrial use |

The priority order is deliberate: independent safety, data quality, a transparent baseline,
efficient inference, and full experiment traceability come before model complexity.
