# Aegis Edge — Verified Project Metrics & Results

## Purpose

This document records the measured and verified results obtained during development and validation of the Aegis Edge project. It is intended as a reference when preparing the future README, project report, presentation, resume entry, or technical documentation.

Only values that have been explicitly measured or observed during validation are included. Metrics that have not yet been measured are marked as pending.

---

# 1. Project Overview

Aegis Edge is an embedded AI fault-detection system combining:

- Zephyr RTOS firmware
- TensorFlow Lite Micro (TFLM) inference
- A deterministic rule-based fault detector
- Renode-based fault injection and firmware validation
- UART/CSV telemetry
- Python telemetry bridge
- FastAPI backend
- WebSocket communication
- React live monitoring dashboard

The system currently detects four states:

1. NORMAL
2. OVERHEAT
3. LOW_VOLTAGE
4. HIGH_RPM

The ML prediction and deterministic rule prediction are both exposed through the telemetry pipeline and displayed in the dashboard.

---

# 2. ML Dataset

## Dataset

File:

`ml/dataset.csv`

Total samples:

**8,000**

Class distribution:

| Label | Class       | Samples |
| ----: | ----------- | ------: |
|     0 | NORMAL      |   2,000 |
|     1 | OVERHEAT    |   2,000 |
|     2 | LOW_VOLTAGE |   2,000 |
|     3 | HIGH_RPM    |   2,000 |

The dataset is therefore balanced across all four classes.

## Input Features

The model uses three input features:

- Temperature
- Voltage
- RPM

Feature scaling used by the evaluation pipeline:

| Feature     |  Scale |
| ----------- | -----: |
| Temperature |  100.0 |
| Voltage     |    4.0 |
| RPM         | 5000.0 |

---

# 3. ML Model

Primary Keras model:

`ml/aegis_fault_model.keras`

Primary deployed INT8 TFLite model:

`ml/aegis_fault_model_int8.tflite`

Measured INT8 TFLite model file size:

**3.5 KB**

Exact file size reported by `ls -lh`:

**3.5K**

The deployed embedded model is used by TensorFlow Lite Micro inside the Zephyr firmware.

---

# 4. ML Evaluation Methodology

The existing evaluation script is:

`ml/evaluate_model.py`

The evaluation procedure:

- Loads `ml/dataset.csv`
- Uses temperature, voltage, and RPM as inputs
- Applies the same feature scaling used by the model
- Creates an 80/20 train/test-style split
- Uses `np.random.seed(42)`
- Evaluates the held-out 20% test set
- Loads `aegis_fault_model.keras`
- Generates predictions using the Keras model
- Calculates overall accuracy
- Calculates a 4×4 confusion matrix
- Calculates per-class precision and recall

Total test samples:

**1,600**

---

# 5. Overall ML Performance

## Test Accuracy

**98.75%**

This result was obtained on the held-out 1,600-sample test set.

Because the original dataset contains 8,000 balanced samples, the evaluation set contains approximately 20% of the complete dataset.

---

# 6. Test Set Distribution

The actual test split contained:

| Class       | Test Samples |
| ----------- | -----------: |
| NORMAL      |          373 |
| OVERHEAT    |          414 |
| LOW_VOLTAGE |          422 |
| HIGH_RPM    |          391 |
| **Total**   |    **1,600** |

---

# 7. Confusion Matrix

The measured confusion matrix was:

| Actual \ Predicted | NORMAL | OVERHEAT | LOW_VOLTAGE | HIGH_RPM |
| ------------------ | -----: | -------: | ----------: | -------: |
| NORMAL             |    353 |        0 |          20 |        0 |
| OVERHEAT           |      0 |      414 |           0 |        0 |
| LOW_VOLTAGE        |      0 |        0 |         422 |        0 |
| HIGH_RPM           |      0 |        0 |           0 |      391 |

## Interpretation

The model correctly classified:

- 353/373 NORMAL samples
- 414/414 OVERHEAT samples
- 422/422 LOW_VOLTAGE samples
- 391/391 HIGH_RPM samples

The only observed test-set errors were:

**20 NORMAL samples incorrectly classified as LOW_VOLTAGE.**

There were no observed OVERHEAT or HIGH_RPM misclassifications in this test split.

---

# 8. Per-Class ML Performance

| Class       | Precision |  Recall |
| ----------- | --------: | ------: |
| NORMAL      |   100.00% |  94.64% |
| OVERHEAT    |   100.00% | 100.00% |
| LOW_VOLTAGE |    95.48% | 100.00% |
| HIGH_RPM    |   100.00% | 100.00% |

Important observation:

- NORMAL recall is 94.64% because 20 NORMAL samples were classified as LOW_VOLTAGE.
- LOW_VOLTAGE precision is 95.48% because those 20 false positives were assigned to the LOW_VOLTAGE class.
- All three fault classes achieved 100% recall on this test split.

---

# 9. Embedded Firmware Build Metrics

Build target:

`stm32f4_disco`

Build directory:

`firmware/app/build-tflm`

Zephyr version observed during the build:

`4.4.99`

Measured firmware memory usage:

| Memory Region |     Used |  Total |  Usage |
| ------------- | -------: | -----: | -----: |
| FLASH         | 59,852 B |   1 MB |  5.71% |
| RAM           | 25,792 B | 128 KB | 19.68% |

These values are from the successful Zephyr firmware build.

---

# 10. Embedded Fault Detection Validation

The firmware performs both:

- ML prediction using TFLM
- Rule-based prediction using the deterministic fault detector

The observed fault injection scenarios are:

| Scenario    | Sensor Condition           | ML Prediction | Rule Prediction | Result |
| ----------- | -------------------------- | ------------- | --------------- | ------ |
| Normal      | ~25–27°C, 3.30 V, 1500 RPM | NORMAL        | NONE            | PASS   |
| Overheat    | 95.0°C, 3.30 V, 1500 RPM   | OVERHEAT      | OVERHEAT        | PASS   |
| Recovery    | ~25°C+, 3.30 V, 1500 RPM   | NORMAL        | NONE            | PASS   |
| Low Voltage | ~25–26°C, 2.20 V, 1500 RPM | LOW_VOLTAGE   | LOW_VOLTAGE     | PASS   |
| Recovery    | ~26°C+, 3.30 V, 1500 RPM   | NORMAL        | NONE            | PASS   |
| High RPM    | ~26–27°C, 3.30 V, 4500 RPM | HIGH_RPM      | HIGH_RPM        | PASS   |
| Recovery    | ~27°C+, 3.30 V, 1500 RPM   | NORMAL        | NONE            | PASS   |

The Renode test repeatedly demonstrated correct transitions into the injected fault states and back to NORMAL after recovery.

---

# 11. Example Renode Fault Injection Values

## Overheat

Injected:

- Temperature: **95.0°C**
- Voltage: **3.30 V**
- RPM: **1500**

Observed:

- ML: **OVERHEAT**
- Rule: **OVERHEAT**
- Final fault: **OVERHEAT**

## Low Voltage

Injected:

- Temperature: approximately **25.8–26.2°C**
- Voltage: **2.20 V**
- RPM: **1500**

Observed:

- ML: **LOW_VOLTAGE**
- Rule: **LOW_VOLTAGE**
- Final fault: **LOW_VOLTAGE**

## High RPM

Injected:

- Temperature: approximately **26.8–27.2°C**
- Voltage: **3.30 V**
- RPM: **4500**

Observed:

- ML: **HIGH_RPM**
- Rule: **HIGH_RPM**
- Final fault: **HIGH_RPM**

---

# 12. TFLM Inference Latency

The TFLM inference latency was measured inside the Zephyr firmware running in the Renode environment.

| Metric  |    Result |
| ------- | --------: |
| Minimum | **40 µs** |
| Mean    | **48 µs** |
| Maximum | **51 µs** |
| Samples |   **100** |

The measurement was performed inside the embedded Zephyr/TFLM execution path rather than using Python/Keras inference timing.

**Environment:** Zephyr RTOS running in Renode.

This result represents the Renode/Zephyr embedded execution environment and should not be interpreted as a physical STM32 board latency measurement.

---

# 12. Telemetry Pipeline

The validated telemetry pipeline is:

```text
Renode
   ↓
Zephyr firmware
   ↓
Sensor simulation
   ↓
TFLM ML inference
   +
Rule-based fault detector
   ↓
UART / CSV telemetry
   ↓
/tmp/aegis_uart.log
   ↓
telemetry_bridge.py
   ↓
FastAPI backend
   ↓
WebSocket
   ↓
React dashboard
```

The machine-readable CSV telemetry format was extended to include:

```text
timestamp_ms,
temperature_c,
voltage_v,
rpm,
fault,
ml_prediction,
rule_prediction
```

Example:

```text
CSV,48005,26.8,3.30,4500,HIGH_RPM,HIGH_RPM,HIGH_RPM
```

---

# 14. Backend / WebSocket Validation

FastAPI backend:

`tools/backend.py`

Validated endpoints:

- `/`
- `/health`
- `/ws`

The `/health` endpoint was observed returning:

```json
{
  "status": "ok",
  "clients": 0
}
```

The WebSocket endpoint:

```text
/ws
```

was successfully tested using:

`tools/test_websocket.py`

Example telemetry received through WebSocket:

```json
{
  "timestamp": 48005,
  "temperature": 26.8,
  "voltage": 3.3,
  "rpm": 4500,
  "fault": "HIGH_RPM"
}
```

The telemetry bridge was also successfully observed sending live Renode telemetry to the backend.

---

# 15. Frontend Dashboard Validation

The React dashboard is located in:

`frontend/`

Validated dashboard functionality includes:

- Live WebSocket connection status
- Temperature display
- Voltage display
- RPM display
- Timestamp display
- ML prediction display
- Rule prediction display
- Detection agreement indicator
- Live temperature chart
- Live voltage chart
- Live RPM chart
- Fault event history
- Live telemetry table

The dashboard was successfully observed receiving real telemetry from the Renode → Zephyr → backend pipeline.

The dashboard is therefore not based solely on mock data; it has been integrated with the live telemetry pipeline.

The backend was also updated to retain telemetry history for the current run. After a browser refresh, the dashboard successfully reconnects to the WebSocket, restores the stored telemetry history, and continues receiving live telemetry.

---

# 16. Current Verified Metrics Summary

| Category         | Metric                 |                         Verified Value |
| ---------------- | ---------------------- | -------------------------------------: |
| Dataset          | Total samples          |                              **8,000** |
| Dataset          | Samples/class          |                              **2,000** |
| ML evaluation    | Test samples           |                              **1,600** |
| ML evaluation    | Accuracy               |                             **98.75%** |
| ML               | NORMAL precision       |                            **100.00%** |
| ML               | NORMAL recall          |                             **94.64%** |
| ML               | OVERHEAT precision     |                            **100.00%** |
| ML               | OVERHEAT recall        |                            **100.00%** |
| ML               | LOW_VOLTAGE precision  |                             **95.48%** |
| ML               | LOW_VOLTAGE recall     |                            **100.00%** |
| ML               | HIGH_RPM precision     |                            **100.00%** |
| ML               | HIGH_RPM recall        |                            **100.00%** |
| Model            | INT8 TFLite file size  |                             **3.5 KB** |
| ML               | TFLM inference latency | **48 µs mean (40–51 µs, 100 samples)** |
| Firmware         | Flash usage            |                   **59,852 B (5.71%)** |
| Firmware         | RAM usage              |                  **25,792 B (19.68%)** |
| Fault validation | Fault classes tested   |                                  **3** |
| Fault validation | Recovery behavior      |                           **Verified** |
| Integration      | WebSocket telemetry    |                           **Verified** |
| Integration      | Live React dashboard   |                           **Verified** |

---

# 17. Metrics Still Pending

The following metrics have **not yet been measured** and should not be claimed in the README/resume until validated:

- End-to-end telemetry latency
- TFLM arena/runtime memory usage
- Exact deployed model memory footprint inside firmware
- Quantitative fault-detection latency
- Long-duration stability test results
- Large-scale Renode fault-injection statistics
- Hardware-board inference measurements, if later tested on physical hardware

These should be added after the corresponding experiments are performed.

---

# 18. Safe Resume/README Claims Based on Current Results

The following claims are currently supported by the measured results:

### ML performance

> Achieved **98.75% test accuracy** across four embedded fault classes using an 8,000-sample balanced dataset and a held-out 1,600-sample test set.

### TinyML model

> Deployed a **3.5 KB INT8 TensorFlow Lite Micro model** for on-device fault classification.

### TFLM inference latency

> Measured **48 µs mean TFLM inference latency** (40–51 µs over 100 samples) in the Zephyr/Renode embedded execution environment.

### Embedded resource usage

> Firmware build uses **5.71% of available Flash** and **19.68% of available RAM** on the STM32F4 Discovery target.

### Fault detection

> Validated detection of **overheat, low-voltage, and high-RPM faults** using both TFLM inference and deterministic rule-based detection, including recovery to NORMAL state.

### Full-stack embedded telemetry

> Integrated Zephyr/TFLM telemetry with a FastAPI/WebSocket backend and React real-time monitoring dashboard.

---

# 19. Important Documentation Rule

When creating the final README, distinguish between:

**Measured results**

and

**Future/pending metrics.**

For example, it is valid to write:

> 98.75% test accuracy

because this was actually evaluated.

It is not valid to claim an inference latency value without a supporting measurement and a specified execution environment.

The current measured result may be reported as:

> 48 µs mean TFLM inference latency (40–51 µs over 100 samples) in the Zephyr/Renode environment.

Do not present this as physical STM32 hardware latency unless it is measured on the physical board.

Similarly, avoid claiming a specific RAM footprint for the TFLM model unless it is separately measured.

---

# 20. Final Renode Fault-Injection Validation

A clean Renode validation run was performed after the telemetry, backend, WebSocket, dashboard, and one-command launcher integration was completed.

| Scenario          | Injected condition         | ML prediction | Rule prediction | Recovery |
| ----------------- | -------------------------- | ------------- | --------------- | -------- |
| Normal            | ~25–27°C, 3.30 V, 1500 RPM | NORMAL        | NONE            | —        |
| Overheat          | 95.0°C, 3.30 V, 1500 RPM   | OVERHEAT      | OVERHEAT        | **PASS** |
| Low voltage       | ~26°C, 2.20 V, 1500 RPM    | LOW_VOLTAGE   | LOW_VOLTAGE     | **PASS** |
| High RPM          | ~27°C, 3.30 V, 4500 RPM    | HIGH_RPM      | HIGH_RPM        | **PASS** |
| Repeated overheat | 95.0°C, 3.30 V, 1500 RPM   | OVERHEAT      | OVERHEAT        | **PASS** |

For every completed fault cycle, the ML and deterministic rule predictions agreed, the corresponding fault was reported, and the system subsequently returned to `ML PREDICTION: NORMAL`, `RULE PREDICTION: NONE`, and `FAULT=NONE`.

The validation run produced **50 CSV telemetry records** before the log was captured. A subsequent scripted low-voltage cycle had begun when the run was stopped, so that incomplete cycle is not counted as a completed recovery result.

Representative latency checkpoints during the same run were:

```text
samples=10  min=45 us  avg=48 us  max=50 us
samples=20  min=45 us  avg=49 us  max=51 us
samples=30  min=40 us  avg=48 us  max=51 us
samples=40  min=40 us  avg=48 us  max=51 us
```

The dedicated 100-sample benchmark remains the official latency measurement documented below.

---

# 21. One-Command Runtime Validation

The complete Aegis Edge runtime was successfully launched using:

```bash
./run_aegis.sh
```

The launcher successfully started the FastAPI backend, telemetry bridge, Renode, and React/Vite frontend. The dashboard received live telemetry correctly, and the backend retained current-run telemetry history so the dashboard could restore its state after a browser refresh.

The standalone `tools/test_websocket.py` remains an optional diagnostic tool and is not required for normal runtime operation.

---

# 22. Completed Latency Measurement

The embedded inference latency experiment has been completed.

The intended measurement path was:

```text
sensor input
    ↓
ml_predict()
    ↓
TFLM inference
    ↓
ML prediction
```

Measured in the Zephyr firmware under Renode:

```text
TFLM inference latency
Minimum: 40 µs
Mean:    48 µs
Maximum: 51 µs
Samples: 100
```

The next quantitative measurements can focus on end-to-end telemetry latency, TFLM arena/runtime memory usage, long-duration stability, and larger-scale Renode fault-injection statistics.

---

## Current Status

**Aegis Edge is currently an end-to-end functional prototype with verified ML, embedded firmware, TFLM inference latency, telemetry, backend, WebSocket, dashboard, fault injection/recovery, and one-command runtime integration.**

Additional quantitative benchmarking such as end-to-end telemetry latency, TFLM arena/runtime memory usage, long-duration stability, and larger-scale fault-injection statistics remains optional future validation rather than required functionality.
