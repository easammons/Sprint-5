import io
import requests
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

ISD_HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"

# name, rating, year, start_lat, start_lon
TORNADOES = [
    ("Cleburne County AL",     2023, 33.73, -85.47),
    ("Winterset IA",           2022, 41.28, -94.05),
    ("Naplate IL",             2017, 41.25, -88.77),
    ("Orange County FL",       2024, 28.59, -81.47),
    ("Rochelle-Fairdale IL",   2015, 41.84, -89.24),
    ("Newnan GA",              2021, 33.34, -84.88),
    ("Rolling Fork MS",        2023, 32.86, -90.97),
    ("Mayfield KY",            2021, 36.52, -89.19),
    ("Greensburg KS",          2007, 37.55, -99.42),
    ("Joplin MO",              2011, 37.06, -94.57),
    ("Moore OK",               2013, 35.29, -97.60),
    ("Enderlin ND",            2025, 46.62, -97.60),
]


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def find_nearest(df, lat, lon, year, n=3):
    d = df.copy()
    d["BEGIN"] = pd.to_numeric(d["BEGIN"], errors="coerce")
    d["END"] = pd.to_numeric(d["END"], errors="coerce")
    d = d[(d["BEGIN"] <= int(f"{year}1231")) & (d["END"] >= int(f"{year}0101"))]
    d = d[d["ICAO"].notna()]  # skip stations with no ICAO code (usually unreliable)

    d["distance_km"] = d.apply(
        lambda row: haversine_km(lat, lon, row["LAT"], row["LON"]), axis=1
    )
    return d.sort_values("distance_km").head(n)


def main():
    print("Downloading NOAA station list (once)...")
    resp = requests.get(ISD_HISTORY_URL)
    df = pd.read_csv(io.StringIO(resp.text))
    df = df.dropna(subset=["LAT", "LON"])
    df = df[(df["LAT"] != 0) | (df["LON"] != 0)]

    for name, year, lat, lon in TORNADOES:
        print(f"\n=== {name} ({year}) — start ({lat}, {lon}) ===")
        nearest = find_nearest(df, lat, lon, year)
        stations = {}
        for _, row in nearest.iterrows():
            icao = row["ICAO"]
            usaf = str(row["USAF"]).zfill(6)
            wban = str(row["WBAN"]).zfill(5)
            station_id = f"{usaf}{wban}"
            stations[icao] = station_id
            print(f"  {row['STATION NAME']:<35} ICAO={icao:<6} id={station_id:<12} dist={row['distance_km']:.1f} km")
        print(f"  JSON: {stations}")


if __name__ == "__main__":
    main()