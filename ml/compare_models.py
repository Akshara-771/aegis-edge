import numpy as np
import tensorflow as tf

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


MODELS = {
    "BASELINE": "aegis_fault_model_baseline_int8.tflite",
    "TRAJECTORY": "aegis_fault_model_trajectory_int8.tflite",
}


def load_model(filename):
    interpreter = tf.lite.Interpreter(
        model_path=filename
    )

    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    return interpreter, input_details, output_details


loaded_models = {}

for name, filename in MODELS.items():

    interpreter, input_details, output_details = load_model(
        filename
    )

    loaded_models[name] = (
        interpreter,
        input_details,
        output_details
    )


def predict(model_name, sample):

    interpreter, input_details, output_details = (
        loaded_models[model_name]
    )

    input_scale, input_zero_point = (
        input_details[0]["quantization"]
    )

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


def rule_predict(sample):

    temperature, voltage, rpm = sample

    if temperature > 80.0:
        return 1

    if voltage < 3.0:
        return 2

    if rpm > 3000:
        return 3

    return 0


def run_test(name, samples):

    print()
    print("=" * 100)
    print(name)
    print("=" * 100)

    print(
        f"{'TEMP':>7} {'VOLT':>7} {'RPM':>7} | "
        f"{'BASELINE':<14} "
        f"{'TRAJECTORY':<14} "
        f"{'RULE':<14} "
        f"RESULT"
    )

    disagreements = 0

    for sample in samples:

        baseline = predict(
            "BASELINE",
            sample
        )

        trajectory = predict(
            "TRAJECTORY",
            sample
        )

        rule = rule_predict(sample)

        if baseline != trajectory:
            result = "MODEL DIFFER"
            disagreements += 1

        elif baseline != rule:
            result = "ML/RULE DIFF"

        else:
            result = "AGREE"

        print(
            f"{sample[0]:7.1f} "
            f"{sample[1]:7.3f} "
            f"{sample[2]:7.0f} | "
            f"{classes[baseline]:<14} "
            f"{classes[trajectory]:<14} "
            f"{classes[rule]:<14} "
            f"{result}"
        )

    print()
    print(
        f"Model disagreements: "
        f"{disagreements}/{len(samples)}"
    )


# --------------------------------------------------
# Temperature boundary
# --------------------------------------------------

temperature_samples = np.array([
    [30.0, 3.30, 1500],
    [40.0, 3.30, 1500],
    [50.0, 3.30, 1500],
    [60.0, 3.30, 1500],
    [70.0, 3.30, 1500],
    [75.0, 3.30, 1500],
    [78.0, 3.30, 1500],
    [79.0, 3.30, 1500],
    [80.0, 3.30, 1500],
    [81.0, 3.30, 1500],
    [82.0, 3.30, 1500],
    [85.0, 3.30, 1500],
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
    [25.0, 3.20, 1500],
    [25.0, 3.30, 1500],
    [25.0, 3.40, 1500],
], dtype=np.float32)


# --------------------------------------------------
# RPM boundary
# --------------------------------------------------

rpm_samples = np.array([
    [25.0, 3.30, 1500],
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
# Run comparisons
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
