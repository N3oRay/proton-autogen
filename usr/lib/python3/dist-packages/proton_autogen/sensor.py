#!/usr/bin/env python3
#sensor.py

from pathlib import Path
from typing import Iterator

HWMON_ROOT = Path("/sys/class/hwmon")


def read_text(path: Path) -> str | None:
    """Read a sysfs file and return its content, or None if unavailable."""
    try:
        return path.read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def get_hwmons(root: Path = HWMON_ROOT) -> Iterator[Path]:
    """Yield all hwmon devices."""
    yield from sorted(root.glob("hwmon*"))


def get_hwmon_name(hwmon: Path) -> str:
    """Return the hwmon device name."""
    return read_text(hwmon / "name") or "unknown"


def get_temperature_label(hwmon: Path, sensor: str) -> str:
    """Return the label associated with a temperature sensor."""
    label = read_text(hwmon / f"{sensor.replace('_input', '_label')}")
    return label or "(no label)"


def get_temperature_value(sensor_file: Path) -> float | None:
    """Return a temperature in °C."""
    value = read_text(sensor_file)
    if value is None:
        return None

    try:
        return int(value) / 1000.0
    except ValueError:
        return None


def iter_temperatures(hwmon: Path):
    """Yield (sensor, label, value) tuples."""
    for sensor_file in sorted(hwmon.glob("temp*_input")):
        sensor = sensor_file.name
        label = get_temperature_label(hwmon, sensor)
        value = get_temperature_value(sensor_file)

        if value is not None:
            yield sensor, label, value


def print_hwmon(hwmon: Path):
    """Pretty-print one hwmon device."""
    print(f"\n=== {get_hwmon_name(hwmon)} ({hwmon}) ===")

    for sensor, label, value in iter_temperatures(hwmon):
        print(f"{sensor:<12} {value:5.1f} °C   {label}")


def get_sensors():
    sensors = []

    for hw in sorted(HWMON_ROOT.glob("hwmon*")):
        try:
            name = (hw / "name").read_text().strip()
        except FileNotFoundError:
            continue

        device = {
            "name": name,
            "path": str(hw),
            "temps": [],
        }

        for temp in sorted(hw.glob("temp*_input")):
            sensor = temp.name

            label_file = hw / sensor.replace("_input", "_label")
            label = (
                label_file.read_text().strip()
                if label_file.exists()
                else None
            )

            value = int(temp.read_text().strip()) / 1000

            device["temps"].append({
                "sensor": sensor,
                "label": label,
                "value": value,
            })

        sensors.append(device)

    return sensors


def print_sensors_search(sensors):
    """Print all detected temperature sensors."""

    for device in sensors:
        print(device["name"])

        for temp in device["temps"]:
            label = temp["label"] or "no label"

            print(
                f"  {temp['sensor']}: "
                f"{temp['value']:.1f}°C "
                f"({label})"
            )


def get_sensors_text() -> str:
    """Return all sensors as formatted text."""

    lines = []

    for device in get_sensors():
        lines.append(f"=== {device['name']} ===")

        for temp in device["temps"]:
            label = temp["label"] or "no label"

            lines.append(
                f"  {temp['sensor']:<12} "
                f"{temp['value']:5.1f} °C   {label}"
            )

        lines.append("")

    return "\n".join(lines)

def print_sensors():
    print(get_sensors_text())


def get_mangohud_advice():
    from pathlib import Path

    hwmon_root = Path("/sys/class/hwmon")

    cpu_sensor = None
    cpu_input = None

    for hw in hwmon_root.glob("hwmon*"):
        name = (hw / "name").read_text().strip()

        if name in ("coretemp", "k10temp"):
            cpu_sensor = name

            core_temps = []

            for temp in hw.glob("temp*_input"):
                label_file = hw / temp.name.replace("_input", "_label")

                label = (
                    label_file.read_text().strip()
                    if label_file.exists()
                    else ""
                )

                if "Core" in label:
                    # extrait index du Core
                    try:
                        core_id = int(label.split()[-1])
                    except Exception:
                        core_id = 999

                    core_temps.append((core_id, temp.name))

            if core_temps:
                # 🎯 prend le Core 0 ou le plus petit index
                cpu_input = sorted(core_temps)[0][1]
            else:
                # fallback sécurisé
                cpu_input = next(hw.glob("temp*_input")).name

            break

    return (
        "📊 MangoHud recommended config:\n\n"
        "cpu_stats\n"
        "cpu_temp\n"
        f"cpu_custom_temp_sensor={cpu_sensor},{cpu_input}\n\n"
        "✔ Selected lowest-index Core sensor (stable choice)"
    )


def print_mangohud_advice():
    print(get_mangohud_advice())

"""
def main():
    for hwmon in get_hwmons():
        print_hwmon(hwmon)


if __name__ == "__main__":
    main()

"""
