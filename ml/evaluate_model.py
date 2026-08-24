import numpy as np
import pandas as pd
import tensorflow as tf

MODEL_FILE = "aegis_fault_model.keras"
DATASET_FILE = "dataset.csv"

classes = {
    0: "NORMAL",
    1: "OVERHEAT",
    2: "LOW_VOLTAGE",
    3: "HIGH_RPM"
}


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

data = pd.read_csv(DATASET_FILE)

X_raw = data[
    ["temperature", "voltage", "rpm"]
].values.astype(np.float32)

y = data["label"].values.astype(np.int32)


# --------------------------------------------------
# Feature scaling
# --------------------------------------------------

FEATURE_SCALE = np.array(
    [100.0, 4.0, 5000.0],
    dtype=np.float32
)

X = X_raw / FEATURE_SCALE


# --------------------------------------------------
# Reproduce the same train/test split
# --------------------------------------------------

indices = np.arange(len(X))

np.random.seed(42)
np.random.shuffle(indices)

split = int(0.8 * len(X))

test_idx = indices[split:]

X_test = X[test_idx]
y_test = y[test_idx]


# --------------------------------------------------
# Load model
# --------------------------------------------------

model = tf.keras.models.load_model(MODEL_FILE)


# --------------------------------------------------
# Predictions
# --------------------------------------------------

probabilities = model.predict(
    X_test,
    verbose=0
)

predictions = np.argmax(
    probabilities,
    axis=1
)


# --------------------------------------------------
# Overall accuracy
# --------------------------------------------------

accuracy = np.mean(
    predictions == y_test
)

print()
print("=" * 70)
print("OVERALL TEST PERFORMANCE")
print("=" * 70)

print(f"Test samples : {len(y_test)}")
print(f"Accuracy     : {accuracy * 100:.2f}%")


# --------------------------------------------------
# Confusion matrix
# --------------------------------------------------

confusion = np.zeros(
    (4, 4),
    dtype=int
)

for actual, predicted in zip(
    y_test,
    predictions
):
    confusion[actual][predicted] += 1


print()
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(
    "              "
    + "".join(
        f"{classes[i]:>14}"
        for i in range(4)
    )
)

for i in range(4):

    print(
        f"{classes[i]:<14}"
        + "".join(
            f"{confusion[i][j]:>14}"
            for j in range(4)
        )
    )


# --------------------------------------------------
# Per-class metrics
# --------------------------------------------------

print()
print("=" * 70)
print("PER-CLASS PERFORMANCE")
print("=" * 70)

for i in range(4):

    true_positive = confusion[i][i]

    actual_count = np.sum(
        confusion[i]
    )

    predicted_count = np.sum(
        confusion[:, i]
    )

    recall = (
        true_positive / actual_count
        if actual_count > 0
        else 0
    )

    precision = (
        true_positive / predicted_count
        if predicted_count > 0
        else 0
    )

    print(
        f"{classes[i]:<14}"
        f"Precision={precision * 100:6.2f}%  "
        f"Recall={recall * 100:6.2f}%"
    )
