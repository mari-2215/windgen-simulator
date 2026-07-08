# Technical documentation

## Weibull model

For shape `k` and scale `lambda`, the mean is `lambda * Gamma(1 + 1/k)`. The software receives a
target mean and derives the scale. Weibull samples are smoothed with an AR(1)-style recurrence and
renormalized to preserve the requested mean. This is suitable for software experiments, not a
certified turbulence spectrum.

## Neural network

The MLP has two inputs (`wind_mps`, `distance_m`), configurable hidden layers, and one sigmoid
output. The default configuration uses `32 -> 24 -> 12` hidden units, `tanh` activations,
input/output normalization, deterministic validation, and Adam optimization. The output is
normalized throttle from 0 to 1.

The synthetic dataset approximates a nonlinear wind/distance/throttle plant with noise. This
relationship is strictly didactic.
A physical model must be built using anemometer measurements with the columns
`wind_mps,distance_m,throttle`, separate training/validation/test sessions, and uncertainty data.

## Phase 1 acceptance criteria

- a valid prompt produces a time series, CSV, and chart without hardware;
- the series follows the requested mean and gust ceiling;
- the MLP reduces training error on the synthetic integration dataset;
- commands pass through ramp and saturation limits;
- the physical backend cannot open a serial port without explicit opt-in;
- all tests pass under Python 3.12.
