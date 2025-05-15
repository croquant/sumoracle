import json

import requests

BASE_URL = "https://sumo-api.com/api"


class SumoApiClient:
    def get_all_rikishi(self):
        all_rikishi = []
        skip = 0
        records = []
        while records is not None:
            all_rikishi.extend(records)
            endpoint = f"/rikishis?intai=true&limit=1000&skip={skip * 1000}"
            response = requests.get(f"{BASE_URL}{endpoint}")
            records = json.loads(response.text)["records"]
            skip += 1
        return all_rikishi
