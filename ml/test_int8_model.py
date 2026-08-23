import numpy as np
import tensorflow as tf

MODEL_FILE = "aegis_fault_model_int8.tflite"

classes = {
    0: "NORMAL",
    1: "OVERHEAT",
    2: "LOW_VOLTAGE",
    3: "HIGH_RPM"
}


# --------------------------------------------------
# Feature scaling
# Must exactly match training
# --------------------------------------------------

FEATURE_SCALE = np.array(
    [100.0, 4.0, 5000.0],
    dtype=np.float32
)


# --------------------------------------------------
# Load INT8 model
# --------------------------------------------------

interpreter = tf.lite.Interpreter(
    model_path=MODEL_FILE
)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Input:")
print(input_details)

print()
print("Output:")
print(output_details)


# --------------------------------------------------
# Test sensor samples
# --------------------------------------------------

samples = np.array([
    [25.0, 3.30, 1500],   # NORMAL
    [95.0, 3.30, 1500],   # OVERHEAT
    [25.0, 2.20, 1500],   # LOW VOLTAGE
    [25.0, 3.30, 4000]    # HIGH RPM
], dtype=np.float32)


# --------------------------------------------------
# Get quantization parameters
# --------------------------------------------------

input_scale, input_zero_point = (
    input_details[0]["quantization"]
)

print()
print("Input scale:", input_scale)
print(
    "Input zero point:",
    input_zero_point
)


# --------------------------------------------------
# Run inference
# --------------------------------------------------

for sample in samples:

    # ----------------------------------------------
    # Normalize raw sensor values
    # ----------------------------------------------

    normalized = sample / FEATURE_SCALE

    # ----------------------------------------------
    # Convert normalized values to INT8
    # ----------------------------------------------

    quantized_input = np.round(
        normalized / input_scale
        + input_zero_point
    ).astype(np.int8)

    quantized_input = np.expand_dims(
        quantized_input,
        axis=0
    )

    # ----------------------------------------------
    # Inference
    # ----------------------------------------------

    interpreter.set_tensor(
        input_details[0]["index"],
        quantized_input
    )

    interpreter.invoke()

    output = interpreter.get_tensor(
        output_details[0]["index"]
    )[0]

    predicted_class = int(
        np.argmax(output)
    )

    print(
        f"TEMP={sample[0]:.1f} C | "
        f"VOLT={sample[1]:.2f} V | "
        f"RPM={sample[2]:.0f} | "
        f"PREDICTION="
        f"{classes[predicted_class]}"
    )
