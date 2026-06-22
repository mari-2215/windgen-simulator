# Implementation plan

## Stage 1 - Logical core (delivered)

- prompt and unit parser;
- reproducible Weibull time series;
- lightweight MLP and synthetic integration dataset;
- CSV, chart, dashboard, CLI, and unit tests;
- actuator abstraction, mock backend, and safety locks.

## Stage 2 - Electronic commissioning

- inventory the motor, ESC, supply, and wiring;
- confirm the F405 firmware and protocol;
- implement heartbeat, watchdog, and independent shutdown;
- test without a propeller and record telemetry.

## Stage 3 - Physical calibration

- design a distance x throttle x wind experiment;
- collect repeated anemometer measurements;
- split training, validation, and testing by session;
- compare the MLP with a simple physical/statistical baseline.

## Stage 4 - Closed-loop control

- add measured wind feedback;
- use the MLP for feed-forward control and a supervisor for error correction;
- validate overshoot, settling time, steady-state error, and shutdown behavior.

## Stage 5 - Academic validation

- publish the experimental protocol, statistics, and traceability;
- run endurance, thermal, vibration, and fault tests;
- produce the final reproducible report and demonstration package.

