# System architecture

```mermaid
flowchart LR
    A[Natural-language prompt] --> B[Parser and validation]
    B --> C[Weibull profile and gusts]
    C --> D[Target time series]
    D --> E[Inverse MLP]
    F[Target distance] --> E
    E --> G[Ramp and saturation limiter]
    G --> H{Actuator backend}
    H --> I[Mock - default]
    H --> J[Experimental Betaflight MSP]
    J --> K[SpeedyBee F405 V4]
    K --> L[ESC and motor]
    D --> M[CSV, chart, dashboard]
```

| Layer | Responsibility |
|---|---|
| Interface | Prompt, CLI, and Streamlit dashboard |
| Domain | Scenario validation and SI-unit conversion |
| Simulation | Weibull distribution, temporal correlation, gust limiting |
| AI | Two-input, one-output inverse MLP |
| Safety | Saturation, ramp limiting, hardware lock, emergency stop |
| Integration | Mock or experimental serial MSP backend |
| Data | CSV time series and NPZ model files |

Training is kept outside the control loop. In a future closed-loop version, an anemometer supplies
feedback while a supervisory controller corrects the MLP feed-forward command.

