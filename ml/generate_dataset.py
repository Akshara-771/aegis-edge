import csv
import random

OUTPUT_FILE = "dataset.csv"

SAMPLES_PER_CLASS = 2000

random.seed(42)


def add_noise(value, noise):
    return value + random.gauss(0, noise)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# --------------------------------------------------
# Boundary-aware value generation
# --------------------------------------------------

def near_boundary(boundary, distance):
    """
    Generate a value close to a safety boundary.
    """
    return boundary + random.uniform(-distance, distance)


# --------------------------------------------------
# NORMAL
# --------------------------------------------------

def generate_normal():
    """
    Normal operating region.

    Most samples are drawn broadly from the safe region,
    while some are deliberately concentrated near the
    safety boundaries.
    """

    region = random.randint(0, 2)

    if region == 0:
        # Typical normal operation
        temperature = random.uniform(24.0, 40.0)
        rpm = random.uniform(1400.0, 2000.0)

    elif region == 1:
        # Warm but still normal operation
        temperature = random.uniform(40.0, 65.0)
        rpm = random.uniform(1800.0, 2600.0)

    else:
        # Upper edge of normal operation
        temperature = random.uniform(60.0, 79.5)
        rpm = random.uniform(2400.0, 2999.0)

    voltage = random.uniform(3.001, 3.40)

    temperature = add_noise(temperature, 0.3)
    voltage = add_noise(voltage, 0.01)
    rpm = add_noise(rpm, 10.0)

    temperature = clamp(temperature, 23.0, 79.5)
    voltage = clamp(voltage, 3.001, 3.40)
    rpm = clamp(rpm, 1400.0, 2999.0)

    return temperature, voltage, rpm, 0

# --------------------------------------------------
# OVERHEAT
# --------------------------------------------------

def generate_overheat():
    """
    Overheat condition.

    Samples are concentrated near the 80°C boundary
    as well as deeper inside the fault region.
    """

    if random.random() < 0.40:
        temperature = random.uniform(80.0, 84.0)
    else:
        temperature = random.uniform(84.0, 100.0)

    voltage = random.uniform(3.20, 3.40)
    rpm = random.uniform(1400.0, 1600.0)

    temperature = clamp(
        add_noise(temperature, 0.3),
        80.01,
        100.0
    )

    voltage = add_noise(voltage, 0.01)
    rpm = add_noise(rpm, 15.0)

    return temperature, voltage, rpm, 1

# --------------------------------------------------
# LOW VOLTAGE
# --------------------------------------------------

def generate_low_voltage():
    """
    Low-voltage condition.

    Samples are concentrated near the 3.0V boundary.
    """

    if random.random() < 0.40:
        voltage = random.uniform(2.90, 3.00)
    else:
        voltage = random.uniform(2.20, 2.90)

    temperature = random.uniform(24.0, 32.0)
    rpm = random.uniform(1400.0, 1600.0)

    temperature = add_noise(temperature, 0.3)

    voltage = clamp(
        add_noise(voltage, 0.01),
        2.20,
        2.999
    )

    rpm = add_noise(rpm, 15.0)

    return temperature, voltage, rpm, 2

# --------------------------------------------------
# HIGH RPM
# --------------------------------------------------

def generate_high_rpm():
    """
    High-RPM condition.

    Samples are concentrated near the 3000 RPM boundary.
    """

    if random.random() < 0.40:
        rpm = random.uniform(3000.0, 3100.0)
    else:
        rpm = random.uniform(3100.0, 4500.0)

    temperature = random.uniform(24.0, 32.0)
    voltage = random.uniform(3.20, 3.40)

    temperature = add_noise(temperature, 0.3)
    voltage = add_noise(voltage, 0.01)

    rpm = clamp(
        add_noise(rpm, 15.0),
        3000.01,
        4500.0
    )

    return temperature, voltage, rpm, 3

generators = [
    generate_normal,
    generate_overheat,
    generate_low_voltage,
    generate_high_rpm,
]


# --------------------------------------------------
# Generate dataset
# --------------------------------------------------

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
