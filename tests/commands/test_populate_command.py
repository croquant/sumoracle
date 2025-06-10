import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from app.models.rank import Rank
from app.models.rikishi import Heya, Shusshin


class PopulateCommandTests(SimpleTestCase):
    """End-to-end tests for the ``populate`` management command."""

    def test_run_manage_py_populate(self):
        """Running ``manage.py populate`` should process API data."""
        rikishi_data = [
            {
                "id": 1,
                "sumodbId": "1",
                "nskId": 1,
                "shikonaEn": "Test",
                "shikonaJp": "テスト",
                "currentRank": "Yokozuna 1 East",
                "heya": "TestBeya",
                "shusshin": "Tokyo",
                "height": 190,
                "weight": 120,
                "birthDate": "1990-01-01T00:00:00Z",
                "debut": "201001",
                "intai": None,
            }
        ]

        def passthrough(func):
            async def inner(*args, **kwargs):
                return func()

            return inner

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.populate.SumoApiClient"
            ) as client_cls,
            patch(
                "app.management.commands.populate.sync_to_async",
                side_effect=passthrough,
            ),
            patch(
                "app.management.commands.populate.Division.objects.aget_or_create",
                new=async_mock(),
            ),
            patch("app.management.commands.populate.Rikishi.objects") as ro,
            patch("app.management.commands.populate.Rank.objects") as rao,
            patch("app.management.commands.populate.Heya.objects") as ho,
            patch("app.management.commands.populate.Shusshin.objects") as so,
            patch(
                "app.management.commands.populate.pycountry.countries.search_fuzzy"
            ) as search_fuzzy,
        ):
            ro.all.return_value = []
            ro.abulk_create = async_mock()
            ro.abulk_update = async_mock()

            rao.all.return_value = []
            rao.aget_or_create = async_mock(
                return_value=(Rank(title="Yokozuna"), True)
            )

            ho.all.return_value = []
            ho.aget_or_create = async_mock(
                return_value=(Heya(name="TestBeya"), True)
            )

            so.all.return_value = []
            so.aget_or_create = async_mock(
                return_value=(Shusshin(name="Tokyo"), True)
            )

            search_fuzzy.return_value = [SimpleNamespace(name="Japan")]

            mock_client = AsyncMock()
            client_cls.return_value = mock_client
            mock_client.get_all_rikishi.return_value = rikishi_data
            mock_client.aclose.return_value = None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                call_command("populate")
            finally:
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop.close()

            mock_client.get_all_rikishi.assert_awaited_once()
            ro.abulk_create.assert_awaited_once()
            ro.abulk_update.assert_not_called()
