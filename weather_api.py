"""Weather knowledge for the Autonomous Trailer (ICS 3202 Practical Exercise 4).

Source: Open-Meteo forecast API (https://open-meteo.com/). It is free and needs no API key.
We ask for the *current* weather at each town and turn Open-Meteo's WMO weather code
into one of five simple conditions that our knowledge base understands:
Clear, Cloudy, Fog, Rain, Storm.

If the internet is not available, fetch_weather() returns the stored fallback value
for each town, so the notebook still runs.
"""

import json
import urllib.request

# Approximate town-centre coordinates (latitude, longitude)
TOWN_COORDS = {
    "Nairobi":  (-1.286, 36.817),
    "Thika":    (-1.033, 37.069),
    "Nyeri":    (-0.420, 36.947),
    "Naivasha": (-0.717, 36.431),
    "Nakuru":   (-0.303, 36.080),
    "Kericho":  (-0.368, 35.286),
    "Eldoret":  ( 0.514, 35.270),
    "Kakamega": ( 0.282, 34.752),
    "Kisumu":   (-0.092, 34.768),
}

# Used when the API cannot be reached
FALLBACK_WEATHER = {town: "Clear" for town in TOWN_COORDS}


def wmo_to_condition(code):
    """Map a WMO weather code (what Open-Meteo returns) to our five conditions."""
    if code is None:
        return "Clear"
    if code in (0, 1):
        return "Clear"
    if code in (2, 3):
        return "Cloudy"
    if code in (45, 48):
        return "Fog"
    if code >= 95:
        return "Storm"
    if 51 <= code <= 86:
        return "Rain"   # drizzle, rain, showers (and the rare snow codes)
    return "Cloudy"


def fetch_weather(towns, timeout=8):
    """Return ({town: condition}, source) where source is 'Open-Meteo (live)' or 'fallback'."""
    towns = [t for t in towns if t in TOWN_COORDS]
    lats = ",".join(str(TOWN_COORDS[t][0]) for t in towns)
    lons = ",".join(str(TOWN_COORDS[t][1]) for t in towns)
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lats}&longitude={lons}&current=weather_code&timezone=Africa%2FNairobi")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if isinstance(data, dict):      # one town comes back as a dict, several as a list
            data = [data]
        result = {t: wmo_to_condition(d["current"]["weather_code"]) for t, d in zip(towns, data)}
        return result, "Open-Meteo (live)"
    except Exception as err:            # no internet, timeout, API change ...
        print(f"Weather API not reachable ({err.__class__.__name__}); using stored fallback values.")
        return {t: FALLBACK_WEATHER[t] for t in towns}, "fallback"


if __name__ == "__main__":
    weather, source = fetch_weather(list(TOWN_COORDS))
    print("Source:", source)
    for town, cond in weather.items():
        print(f"  {town:9s} {cond}")
