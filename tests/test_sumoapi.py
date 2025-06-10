import asyncio
from unittest.mock import patch

from django.test import SimpleTestCase

from libs.sumoapi import SumoApiClient


class DummyResponse:
    def __init__(self, data):
        self._data = data
        self.status_code = 200

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class DummyClient:
    def __init__(self, responses):
        self.responses = responses
        self.closed = False

    async def get(self, *args, **kwargs):
        return self.responses.pop(0)

    async def aclose(self):
        self.closed = True


async def dummy_gather(*coros):
    return [await c for c in coros]


class SumoApiClientTests(SimpleTestCase):
    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_client_methods(self):
        responses = [
            DummyResponse({"records": [1]}),
            DummyResponse({"records": []}),
            DummyResponse({"r": 1}),
            DummyResponse({"id": 1}),
            DummyResponse({"stats": []}),
            DummyResponse({"matches": []}),
            DummyResponse({"matches": []}),
            DummyResponse({"history": 1}),
            DummyResponse({"history": 2}),
            DummyResponse({"ranks": []}),
            DummyResponse({"meas": 1}),
            DummyResponse({"meas": 2}),
            DummyResponse({"kimarite": []}),
            DummyResponse({"kimarite": "x"}),
            DummyResponse({"measurements": []}),
            DummyResponse({"date": "x"}),
            DummyResponse({"banzuke": []}),
            DummyResponse({"torikumi": []}),
            DummyResponse({"shikonas": []}),
        ]
        dummy_client = DummyClient(responses)
        with (
            patch("libs.sumoapi.httpx.AsyncClient", return_value=dummy_client),
            patch("libs.sumoapi.asyncio.gather", new=dummy_gather),
        ):
            api = SumoApiClient()
            self.run_async(api.__aenter__())
            self.assertEqual(self.run_async(api.get_all_rikishi()), [1])
            self.assertEqual(self.run_async(api.get_rikishis()), {"r": 1})
            self.assertEqual(self.run_async(api.get_rikishi(1)), {"id": 1})
            self.assertEqual(
                self.run_async(api.get_rikishi_stats(1)), {"stats": []}
            )
            self.assertEqual(
                self.run_async(api.get_rikishi_matches(1)), {"matches": []}
            )
            self.assertEqual(
                self.run_async(api.get_rikishi_matches(1, 2)),
                {"matches": []},
            )
            self.assertEqual(
                self.run_async(api.get_ranking_history([1, 2])),
                {1: {"history": 1}, 2: {"history": 2}},
            )
            self.assertEqual(self.run_async(api.get_ranks()), {"ranks": []})
            self.assertEqual(
                self.run_async(api.get_measurements_history([1, 2])),
                {1: {"meas": 1}, 2: {"meas": 2}},
            )
            self.assertEqual(
                self.run_async(api.get_kimarite_list()), {"kimarite": []}
            )
            self.assertEqual(
                self.run_async(api.get_kimarite("y")), {"kimarite": "x"}
            )
            self.assertEqual(
                self.run_async(api.get_measurements()), {"measurements": []}
            )
            self.assertEqual(
                self.run_async(api.get_basho_by_id(1)), {"date": "x"}
            )
            self.assertEqual(
                self.run_async(api.get_basho_banzuke(1, "makuuchi")),
                {"banzuke": []},
            )
            self.assertEqual(
                self.run_async(api.get_basho_torikumi(1, "makuuchi", 1)),
                {"torikumi": []},
            )
            self.assertEqual(
                self.run_async(api.get_shikonas()), {"shikonas": []}
            )
            self.run_async(api.__aexit__(None, None, None))
            self.assertTrue(dummy_client.closed)
