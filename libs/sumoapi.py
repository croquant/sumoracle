import asyncio

import httpx


class SumoApiError(Exception):
    """Raised when the Sumo API request fails."""

    pass


BASE_URL = "https://sumo-api.com/api"


class SumoApiClient:
    """Async client for the public Sumo API."""

    def __init__(self, **client_kwargs):
        """Create a new :class:`SumoApiClient`.

        Parameters
        ----------
        **client_kwargs : dict
            Optional arguments forwarded to ``httpx.AsyncClient``. ``base_url``
            and ``timeout`` are preconfigured but can be overridden.
        """

        default_kwargs = {"base_url": BASE_URL, "timeout": 30.0}
        default_kwargs.update(client_kwargs)
        self.client = httpx.AsyncClient(**default_kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def _get(self, endpoint, **kwargs):
        try:
            response = await self.client.get(endpoint, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            msg = f"HTTP error while requesting {endpoint}: {exc}"
            raise SumoApiError(msg) from exc

    async def _get_with_retries(self, endpoint, retries=3, **kwargs):
        for attempt in range(retries):
            try:
                return await self._get(endpoint, **kwargs)
            except SumoApiError:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

    async def get_all_rikishi(self):
        all_rikishi = []
        skip = 0
        while True:
            endpoint = f"/rikishis?intai=true&limit=1000&skip={skip * 1000}"
            response = await self._get_with_retries(endpoint)
            data = response.json()
            records = data.get("records", [])
            if not records:
                break
            all_rikishi.extend(records)
            skip += 1
        return all_rikishi

    async def get_rikishis(self, limit=100, skip=0, intai=True):
        """Fetch a single page of rikishi records."""
        params = {"limit": limit, "skip": skip, "intai": str(intai).lower()}
        response = await self._get("/rikishis", params=params)
        return response.json()

    async def get_rikishi(self, rikishi_id):
        """Get a single rikishi by id."""
        response = await self._get(f"/rikishi/{rikishi_id}")
        return response.json()

    async def get_rikishi_stats(self, rikishi_id):
        """Retrieve career statistics for a rikishi."""
        response = await self._get(f"/rikishi/{rikishi_id}/stats")
        return response.json()

    async def get_rikishi_matches(self, rikishi_id, **params):
        """Return a list of matches for a rikishi.

        Optional query parameters (e.g., ``bashoId``) are forwarded to the
        API.
        """

        endpoint = f"/rikishi/{rikishi_id}/matches"
        response = await self._get(endpoint, params=params)
        return response.json()

    async def get_ranking_history(self, rikishi_ids):
        tasks = []
        for rikishi_id in rikishi_ids:
            tasks.append(
                self._get_with_retries(f"/ranks?rikishiId={rikishi_id}")
            )
        responses = await asyncio.gather(*tasks)
        return {
            rikishi_ids[i]: responses[i].json()
            for i in range(len(rikishi_ids))
            if responses[i].status_code == 200
        }

    async def get_ranks(self, **params):
        """Fetch rank data with optional query parameters."""
        response = await self._get("/ranks", params=params)
        return response.json()

    async def get_measurements_history(self, rikishi_ids):
        tasks = []
        for rikishi_id in rikishi_ids:
            tasks.append(
                self._get_with_retries(f"/measurements?rikishiId={rikishi_id}")
            )
        responses = await asyncio.gather(*tasks)
        return {
            rikishi_ids[i]: responses[i].json()
            for i in range(len(rikishi_ids))
            if responses[i].status_code == 200
        }

    async def get_kimarite_list(self):
        """Return a list of all kimarite."""
        response = await self._get("/kimarite")
        return response.json()

    async def get_kimarite(self, kimarite_name):
        """Return details for a specific kimarite."""
        response = await self._get(f"/kimarite/{kimarite_name}")
        return response.json()

    async def get_measurements(self, **params):
        """Fetch measurements with optional query parameters."""
        response = await self._get("/measurements", params=params)
        return response.json()

    async def get_basho_by_id(self, basho_id):
        response = await self._get(f"/basho/{basho_id}")
        data = response.json()
        return data if data.get("date") else None

    async def get_basho_banzuke(self, basho_id, division):
        response = await self._get(f"/basho/{basho_id}/banzuke/{division}")
        return response.json()

    async def get_basho_torikumi(self, basho_id, division, day):
        endpoint = f"/basho/{basho_id}/torikumi/{division}/{day}"
        response = await self._get(endpoint)
        return response.json()

    async def get_shikonas(self, **params):
        """Fetch shikona records. Typically requires ``rikishiId``."""
        response = await self._get("/shikonas", params=params)
        return response.json()

    async def aclose(self):
        await self.client.aclose()
