# Hardware integration and safety

## Recommended topology

- Raspberry Pi 2B: prompt handling, simulation, inference, logging, and supervision.
- SpeedyBee F405 V4: motor/ESC timing under a compatible Betaflight firmware.
- Stack ESC and brushless outrunner: power stage.
- Properly sized bench supply: current limiting and electrical protection.
- Anemometer: mandatory for physical calibration of the MLP.

Never power the motor from the Raspberry Pi. Review common ground, logic levels, wiring, power
distribution, and board documentation before connecting the systems. Remove the propeller during
communication tests.

## Why this version does not use MAVLink

The original PDF assumes Pixhawk/PyMAVLink. A SpeedyBee F405 V4 running Betaflight belongs to a
different ecosystem. The included backend emits an experimental MSP v1 motor command, but exact
permissions, modes, mapping, and behavior can vary by firmware version. Validate it with the
matching Betaflight documentation and configurator. If compatibility is uncertain, remain in mock
mode.

## Minimum commissioning sequence

1. Record motor KV, ESC rating, supply voltage, and current limits.
2. Confirm FC and ESC firmware and protocols.
3. Validate serial communication while ESC power is disconnected.
4. Verify an independent loss-of-communication shutdown.
5. Energize without a propeller at the lowest current and command limits.
6. Install shielding and the anemometer before low-energy airflow tests.

The environment variable `LABO_HARDWARE_ENABLE=EU_CONFIRMO_BANCADA_SEGURA` only unlocks the
software path. It does not certify the test bench or replace a physical emergency stop.

