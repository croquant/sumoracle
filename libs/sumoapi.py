import asyncio

import httpx

BASE_URL = "https://sumo-api.com/api"


class SumoApiClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)

    async def get_all_rikishi(self):
        all_rikishi = []
        skip = 0
        while True:
            endpoint = f"/rikishis?intai=true&limit=1000&skip={skip * 1000}"
            response = await self.client.get(endpoint)
            data = response.json()
            records = data.get("records", [])
            if not records:
                break
            all_rikishi.extend(records)
            skip += 1
        return all_rikishi

    async def get_ranking_history(self, rikishi_ids):
        tasks = []
        for rikishi_id in rikishi_ids:
            tasks.append(self.client.get(f"/ranks?rikishiId={rikishi_id}"))
        responses = await asyncio.gather(*tasks)
        return {
            rikishi_ids[i]: responses[i].json()
            for i in range(len(rikishi_ids))
            if responses[i].status_code == 200
        }

    async def get_measurements_history(self, rikishi_ids):
        tasks = []
        for rikishi_id in rikishi_ids:
            tasks.append(self.client.get(f"/measurements?rikishiId={rikishi_id}"))
        responses = await asyncio.gather(*tasks)
        return {
            rikishi_ids[i]: responses[i].json()
            for i in range(len(rikishi_ids))
            if responses[i].status_code == 200
        }

    async def get_basho_by_id(self, basho_id):
        response = await self.client.get(f"/basho/{basho_id}")
        data = response.json()
        if "date" in data and data["date"]:
            return data
        return None

    async def aclose(self):
        await self.client.aclose()
