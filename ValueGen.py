import requests
import time
import json
import random
from datetime import datetime, timedelta

# ---- CONFIG ----
BASE_URL = "https://beeguard-6b72f-default-rtdb.firebaseio.com"

MAX_ENTRIES = 15  # aantal punten op grafiek

LIVE_UPDATE_INTERVAL_MIN = 0.1  # Live data /min
GRAPH_UPDATE_INTERVAL_HOURS = 0  # Graph data /uur
GRAPH_UPDATE_INTERVAL_MIN = 0.2  # ...plus X /min


# ---- Simulated Sensor Values ----
def read_sensors():
    return {
        "tempext": round(random.uniform(20, 30), 1),
        "tempint": round(random.uniform(18, 25), 1),
        "luchtvochtigheidext": random.randint(50, 80),
        "luchtvochtigheidint": random.randint(45, 70),
        "luchtdruk": round(random.uniform(1000, 1030), 2),
        "gewicht": round(random.uniform(30, 45), 1),
        "batterij": random.randint(75, 100),
    }


# ---- Upload Live Data ----
def update_live_data(sensor_data):
    try:
        response = requests.put(
            f"{BASE_URL}/liveData.json", data=json.dumps(sensor_data)
        )
        print("✅ Live data updated.")
    except Exception as e:
        print("❌ Failed to update liveData:", e)


# ---- Upload Graph Data ----
def update_graph_data(sensor_data):
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:00")
    for key, value in sensor_data.items():
        path = f"{BASE_URL}/graphData/{key}Data.json"
        try:
            response = requests.get(path)
            data = response.json() if response.text != "null" else {}
            data[timestamp] = value

            sorted_keys = sorted(data.keys())
            if len(sorted_keys) > MAX_ENTRIES:
                for old_key in sorted_keys[:-MAX_ENTRIES]:
                    del data[old_key]

            requests.put(path, data=json.dumps(data))
        except Exception as e:
            print(f"❌ Failed to update graphData for {key}:", e)
    print("✅ Graph data updated.")


# ---- Main Loop ----
def main():
    next_live_update = datetime.now()
    next_graph_update = datetime.now()

    while True:
        now = datetime.now()

        if now >= next_live_update:
            print("📡 Live update...")
            sensor_data = read_sensors()
            update_live_data(sensor_data)
            next_live_update = now + timedelta(minutes=LIVE_UPDATE_INTERVAL_MIN)

        if now >= next_graph_update:
            print("📊 Graph update...")
            if "sensor_data" not in locals():  # Read if not already fetched
                sensor_data = read_sensors()
            update_graph_data(sensor_data)
            next_graph_update = now + timedelta(
                hours=GRAPH_UPDATE_INTERVAL_HOURS, minutes=GRAPH_UPDATE_INTERVAL_MIN
            )

        # Sleep briefly to avoid busy loop
        time.sleep(1)


if __name__ == "__main__":
    main()
