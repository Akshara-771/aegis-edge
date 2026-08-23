import csv
import random

OUTPUT_FILE = "dataset.csv"

SAMPLES_PER_CLASS = 2000

random.seed(42)


def generate_normal():
    temperature = random.uniform(24.0, 32.0)
    voltage = random.uniform(3.20, 3.40)
    rpm = random.uniform(1400, 1600)

    return temperature, voltage, rpm, 0


def generate_overheat():
    temperature = random.uniform(82.0, 100.0)
    voltage = random.uniform(3.20, 3.40)
    rpm = random.uniform(1400, 1600)

    return temperature, voltage, rpm, 1


def generate_low_voltage():
    temperature = random.uniform(24.0, 32.0)
    voltage = random.uniform(2.20, 2.95)
    rpm = random.uniform(1400, 1600)

    return temperature, voltage, rpm, 2


def generate_high_rpm():
    temperature = random.uniform(24.0, 32.0)
    voltage = random.uniform(3.20, 3.40)
    rpm = random.uniform(3001, 4500)

    return temperature, voltage, rpm, 3


generators = [
    generate_normal,
    generate_overheat,
    generate_low_voltage,
    generate_high_rpm,
]


with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "temperature",
        "voltage",
        "rpm",
        "label"
    ])

    for generator in generators:
        for _ in range(SAMPLES_PER_CLASS):
            writer.writerow(generator())


print(f"Dataset generated: {OUTPUT_FILE}")
print(f"Samples: {SAMPLES_PER_CLASS * len(generators)}")
