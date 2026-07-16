import json
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,
    "page": 1,
    "sparkline": "false",
}

LANDING_ZONE_DIR = Path.home() / "Desktop" / "landing_zone"

def fetch_data():
    try:
        response = requests.get(API_URL, params=API_PARAMS, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        print(f"API request failed: {exc}")
        return None

def write_to_landing_zone(payload):
    LANDING_ZONE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    final_path = LANDING_ZONE_DIR / f"market_data_{timestamp}.json"
    tmp_path = final_path.with_suffix(".tmp")

    record = {
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "coingecko_markets_api",
        "record_count": len(payload),
        "data": payload,
    }

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
    tmp_path.rename(final_path)
    return final_path

def main():
    print(f"Landing zone: {LANDING_ZONE_DIR}")
    for i in range(5):  # هيسحب 5 مرات بس للتجربة
        payload = fetch_data()
        if payload:
            out_file = write_to_landing_zone(payload)
            print(f"[{i+1}/5] Wrote {len(payload)} records -> {out_file.name}")
        else:
            print(f"[{i+1}/5] Skipped: no data received.")
        time.sleep(10)

if __name__ == "__main__":
    main()
