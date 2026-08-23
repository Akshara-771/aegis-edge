import tensorflow as tf
import numpy as np
import pandas as pd

# --------------------------------------------------
# Load trained model
# --------------------------------------------------

model = tf.keras.models.load_model(
    "aegis_fault_model.keras"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

data = pd.read_csv("dataset.csv")

X_raw = data[
    ["temperature", "voltage", "rpm"]
].values.astype(np.float32)


# --------------------------------------------------
# Normalize exactly as done during training
# --------------------------------------------------

FEATURE_SCALE = np.array(
    [100.0, 4.0, 5000.0],
    dtype=np.float32
)

X = X_raw / FEATURE_SCALE


# --------------------------------------------------
# Representative dataset
# --------------------------------------------------

def representative_dataset():

    for sample in X[::10]:

        yield [
            np.expand_dims(
                sample,
                axis=0
            )
        ]


# --------------------------------------------------
# TFLite converter
# --------------------------------------------------

converter = tf.lite.TFLiteConverter.from_keras_model(
    model
)

converter.optimizations = [
    tf.lite.Optimize.DEFAULT
]

converter.representative_dataset = (
    representative_dataset
)

converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]

converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8


# --------------------------------------------------
# Convert
# --------------------------------------------------

tflite_model = converter.convert()


# --------------------------------------------------
# Save
# --------------------------------------------------

with open(
    "aegis_fault_model_int8.tflite",
    "wb"
) as file:

    file.write(tflite_model)


print("INT8 model created successfully.")
print(f"Model size: {len(tflite_model)} bytes")
