import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.preprocessing import StandardScaler


# Load dataset
data = pd.read_csv("dataset.csv")

X = data[["temperature", "voltage", "rpm"]].values

# Recreate the scaler used during training
scaler = StandardScaler()
scaler.fit(X)


# Load trained model
model = tf.keras.models.load_model("aegis_fault_model.keras")


# Class names
classes = {
    0: "NORMAL",
    1: "OVERHEAT",
    2: "LOW_VOLTAGE",
    3: "HIGH_RPM"
}


# Test sensor conditions
test_samples = np.array([
    [25.0, 3.30, 1500],   # Normal
    [95.0, 3.30, 1500],   # Overheat
    [25.0, 2.20, 1500],   # Low voltage
    [25.0, 3.30, 4000],   # High RPM
])


# Normalize
test_scaled = scaler.transform(test_samples)


# Predict
predictions = model.predict(test_scaled, verbose=0)


for sample, prediction in zip(test_samples, predictions):

    predicted_class = np.argmax(prediction)
    confidence = prediction[predicted_class] * 100

    print(
        f"TEMP={sample[0]:.1f} C | "
        f"VOLT={sample[1]:.2f} V | "
        f"RPM={sample[2]:.0f} | "
        f"PREDICTION={classes[predicted_class]} | "
        f"CONFIDENCE={confidence:.2f}%"
    )
