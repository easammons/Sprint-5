"""
Helper script (run manually, not part of the Django app) to find the
nearest NOAA ISD stations to a given location for a given year.

Usage:
    python find_stations.py 33.588 -85.858 2023   # lat, lon, year
"""
import sys
import io
import requests
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

ISD_HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def find_nearest_stations(lat, lon, year, n=5):
    print("Downloading NOAA station list...")
    resp = requests.get(ISD_HISTORY_URL)
    df = pd.read_csv(io.StringIO(resp.text))

    df = df.dropna(subset=["LAT", "LON"])
    df = df[(df["LAT"] != 0) | (df["LON"] != 0)]

    # Keep only stations with data covering the target year
    df["BEGIN"] = pd.to_numeric(df["BEGIN"], errors="coerce")
    df["END"] = pd.to_numeric(df["END"], errors="coerce")
    df = df[(df["BEGIN"] <= int(f"{year}1231")) & (df["END"] >= int(f"{year}0101"))]

    df["distance_km"] = df.apply(
        lambda row: haversine_km(lat, lon, row["LAT"], row["LON"]), axis=1
    )

    nearest = df.sort_values("distance_km").head(n)

    print(f"\nNearest stations to ({lat}, {lon}) active in {year}:\n")
    for _, row in nearest.iterrows():
        usaf = str(row["USAF"]).zfill(6)
        wban = str(row["WBAN"]).zfill(5)
        station_id = f"{usaf}{wban}"
        print(
            f"  {row['STATION NAME']:<35} "
            f"ICAO={row.get('ICAO', 'N/A'):<6} "
            f"station_id={station_id:<12} "
            f"dist={row['distance_km']:.1f} km"
        )


if __name__ == "__main__":
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    year = int(sys.argv[3])
    find_nearest_stations(lat, lon, year)