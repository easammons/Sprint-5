import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from django.conf import settings


def parse_temp(value):
    try:
        temp = int(str(value).split(",")[0])
        if temp in (9999, -9999):
            return None
        return temp / 10
    except:
        return None


def parse_pressure(value):
    try:
        pressure = int(str(value).split(",")[0])
        if pressure == 99999:
            return None
        return pressure / 10
    except:
        return None


def parse_wind(value):
    try:
        parts = str(value).split(",")
        speed = int(parts[3])
        if speed == 9999:
            return None
        return speed / 10
    except:
        return None


def generate_tornado_plot(name, stations, start_time, end_time,
                           tornado_start, tornado_end, output_filename, year):
    """
    stations: dict of {station_name: station_id}
    times: pandas Timestamps
    output_filename: e.g. "jarrell.png" -- saved under static/weather/tornadoes/
    """
    data = {}

    for station_name, station_id in stations.items():
        url = (
            f"https://www.ncei.noaa.gov/data/"
            f"global-hourly/access/{year}/"
            f"{station_id}.csv"
        )
        df = pd.read_csv(url, low_memory=False)
        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df[(df["DATE"] >= start_time) & (df["DATE"] <= end_time)].copy()

        df["Temperature_C"] = df["TMP"].apply(parse_temp)
        df["Dewpoint_C"] = df["DEW"].apply(parse_temp)
        if "SLP" in df.columns:
            df["Pressure_hPa"] = df["SLP"].apply(parse_pressure)
        df["WindSpeed_mps"] = df["WND"].apply(parse_wind)

        data[station_name] = df

    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

    variables = [
        ("Temperature_C", "Temperature (°C)"),
        ("Dewpoint_C", "Dew Point (°C)"),
        ("Pressure_hPa", "Pressure (hPa)"),
        ("WindSpeed_mps", "Wind Speed (m/s)")
    ]

    for ax, (column, label) in zip(axes, variables):
        for station_name, df in data.items():
            if column in df.columns:
                ax.plot(df["DATE"], df[column], marker="o", label=station_name)

        ax.axvline(tornado_start, color="red", linestyle="--")
        ax.axvline(tornado_end, color="orange", linestyle="--")
        ax.set_ylabel(label)
        ax.grid(True)

    axes[0].set_title(f"{name} Weather Analysis")
    axes[-1].legend()
    plt.tight_layout()

    output_dir = Path(settings.BASE_DIR) / "weather" / "static" / "weather" / "tornadoes"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return f"weather/tornadoes/{output_filename}"