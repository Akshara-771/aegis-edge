import numpy as np
import tensorflow as tf

MODEL_FILE = "aegis_fault_model_int8.tflite"

FEATURE_SCALE = np.array(
    [100.0, 4.0, 5000.0],
    dtype=np.float32
)

classes = {
    0: "NORMAL",
    1: "OVERHEAT",
    2: "LOW_VOLTAGE",
    3: "HIGH_RPM"
}


# --------------------------------------------------
# Load INT8 model
# --------------------------------------------------

interpreter = tf.lite.Interpreter(
    model_path=MODEL_FILE
)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_scale, input_zero_point = (
    input_details[0]["quantization"]
)


# --------------------------------------------------
# ML prediction helper
# --------------------------------------------------

def predict(sample):

    normalized = sample / FEATURE_SCALE

    quantized = np.round(
        normalized / input_scale
        + input_zero_point
    ).astype(np.int8)

    quantized = np.expand_dims(
        quantized,
        axis=0
    )

    interpreter.set_tensor(
        input_details[0]["index"],
        quantized
    )

    interpreter.invoke()

    output = interpreter.get_tensor(
        output_details[0]["index"]
    )[0]

    return int(np.argmax(output))


# --------------------------------------------------
# Rule detector
# --------------------------------------------------

def rule_predict(sample):

    temperature, voltage, rpm = sample

    if temperature > 80.0:
        return 1

    if voltage < 3.0:
        return 2

    if rpm > 3000:
        return 3

    return 0


# --------------------------------------------------
# Run boundary experiment
# --------------------------------------------------

def run_test(name, samples):

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    for sample in samples:

        ml_result = predict(sample)
        rule_result = rule_predict(sample)

        agreement = (
            "AGREE"
            if ml_result == rule_result
            else "DISAGREE"
        )

        print(
            f"TEMP={sample[0]:6.1f} C | "
            f"VOLT={sample[1]:.3f} V | "
            f"RPM={sample[2]:6.0f} | "
            f"ML={classes[ml_result]:12s} | "
            f"RULE={classes[rule_result]:12s} | "
            f"{agreement}"
        )


# --------------------------------------------------
# Temperature boundary
# --------------------------------------------------

temperature_samples = np.array([
    [30.0, 3.30, 1500],
    [32.0, 3.30, 1500],
    [33.0, 3.30, 1500],
    [40.0, 3.30, 1500],
    [50.0, 3.30, 1500],
    [60.0, 3.30, 1500],
    [70.0, 3.30, 1500],
    [75.0, 3.30, 1500],
    [80.0, 3.30, 1500],
    [81.0, 3.30, 1500],
    [82.0, 3.30, 1500],
    [83.0, 3.30, 1500],
    [90.0, 3.30, 1500],
], dtype=np.float32)


# --------------------------------------------------
# Voltage boundary
# --------------------------------------------------

voltage_samples = np.array([
    [25.0, 2.20, 1500],
    [25.0, 2.50, 1500],
    [25.0, 2.80, 1500],
    [25.0, 2.90, 1500],
    [25.0, 2.95, 1500],
    [25.0, 2.99, 1500],
    [25.0, 3.00, 1500],
    [25.0, 3.01, 1500],
    [25.0, 3.10, 1500],
    [25.0, 3.19, 1500],
    [25.0, 3.20, 1500],
    [25.0, 3.30, 1500],
    [25.0, 3.40, 1500],
], dtype=np.float32)


# --------------------------------------------------
# RPM boundary
# --------------------------------------------------

rpm_samples = np.array([
    [25.0, 3.30, 1500],
    [25.0, 3.30, 1600],
    [25.0, 3.30, 1700],
    [25.0, 3.30, 2000],
    [25.0, 3.30, 2500],
    [25.0, 3.30, 2800],
    [25.0, 3.30, 2900],
    [25.0, 3.30, 2999],
    [25.0, 3.30, 3000],
    [25.0, 3.30, 3001],
    [25.0, 3.30, 3100],
    [25.0, 3.30, 3500],
    [25.0, 3.30, 4000],
], dtype=np.float32)


# --------------------------------------------------
# Execute experiments
# --------------------------------------------------

run_test(
    "TEMPERATURE BOUNDARY",
    temperature_samples
)

run_test(
    "VOLTAGE BOUNDARY",
    voltage_samples
)

run_test(
    "RPM BOUNDARY",
    rpm_samples
)
