import numpy as np
import pandas as pd
import tensorflow as tf

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

data = pd.read_csv("dataset.csv")

X_raw = data[
    ["temperature", "voltage", "rpm"]
].values.astype(np.float32)

y = data["label"].values.astype(np.int32)


# --------------------------------------------------
# Feature scaling
# --------------------------------------------------
# Convert raw sensor values into approximately 0–1
# ranges before feeding them to the neural network.

FEATURE_SCALE = np.array(
    [100.0, 4.0, 5000.0],
    dtype=np.float32
)

X = X_raw / FEATURE_SCALE


print("Feature scale:", FEATURE_SCALE)


# --------------------------------------------------
# Train / validation split
# --------------------------------------------------

indices = np.arange(len(X))

np.random.seed(42)
np.random.shuffle(indices)

split = int(0.8 * len(X))

train_idx = indices[:split]
test_idx = indices[split:]

X_train = X[train_idx]
X_test = X[test_idx]

y_train = y[train_idx]
y_test = y[test_idx]


# --------------------------------------------------
# Build TinyML model
# --------------------------------------------------

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(3,)),

    tf.keras.layers.Dense(
        16,
        activation="relu"
    ),

    tf.keras.layers.Dense(
        8,
        activation="relu"
    ),

    tf.keras.layers.Dense(
        4,
        activation="softmax"
    )
])


# --------------------------------------------------
# Compile
# --------------------------------------------------

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# --------------------------------------------------
# Train
# --------------------------------------------------

model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=30,
    batch_size=40,
    verbose=1
)


# --------------------------------------------------
# Evaluate
# --------------------------------------------------

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print()
print("====================================")
print(f"Test accuracy: {accuracy * 100:.2f}%")
print("====================================")


# --------------------------------------------------
# Save model
# --------------------------------------------------

model.save("aegis_fault_model.keras")

print("Model saved as aegis_fault_model.keras")
