import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from app.management.commands.populate import Command
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

            mock_api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = mock_api
            client_cls.return_value.__aexit__.return_value = None
            mock_api.get_all_rikishi.return_value = rikishi_data

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                call_command("populate")
            finally:
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop.close()

            mock_api.get_all_rikishi.assert_awaited_once()
            ro.abulk_create.assert_awaited_once()
            ro.abulk_update.assert_not_called()

    def test_updates_existing_rikishi(self):
        """Existing entries should trigger bulk update."""
        rikishi_data = [
            {
                "id": 1,
                "sumodbId": "1",
                "nskId": 1,
                "shikonaEn": "Test",
                "currentRank": "Yokozuna",
            }
        ]

        def passthrough(func):
            async def inner(*args, **kwargs):
                return func()

            return inner

        existing = SimpleNamespace(id=1)
        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.populate.SumoApiClient",
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
        ):
            ro.all.return_value = [existing]
            ro.abulk_create = async_mock()
            ro.abulk_update = async_mock()

            rao.all.return_value = []
            rao.aget_or_create = async_mock(
                return_value=(Rank(title="Yokozuna"), True)
            )

            ho.all.return_value = []
            ho.aget_or_create = async_mock(return_value=(Heya(name="H"), True))

            so.all.return_value = []
            so.aget_or_create = async_mock(
                return_value=(Shusshin(name="S"), True)
            )

            mock_api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = mock_api
            client_cls.return_value.__aexit__.return_value = None
            mock_api.get_all_rikishi.return_value = rikishi_data

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                call_command("populate")
            finally:
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop.close()

            ro.abulk_create.assert_not_called()
            ro.abulk_update.assert_awaited_once()

    def test_skips_and_warns_unknown_country(self):
        """Command should warn on missing data and unknown countries."""
        rikishi_data = [
            {"shikonaEn": "NoID"},
            {
                "id": 2,
                "shikonaEn": "BadCountry",
                "shusshin": "Atlantis",
            },
            {
                "id": 3,
                "shikonaEn": "Intl",
                "shusshin": "Ulaanbaatar, Mongolia",
            },
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
            patch("app.management.commands.populate.Command.warn") as warn_mock,
        ):
            ro.all.return_value = []
            ro.abulk_create = async_mock()
            ro.abulk_update = async_mock()

            rao.all.return_value = []
            rao.aget_or_create = async_mock(
                return_value=(Rank(title="Y"), True)
            )

            ho.all.return_value = []
            ho.aget_or_create = async_mock(return_value=(Heya(name="H"), True))

            so.all.return_value = []
            so.aget_or_create = async_mock(
                return_value=(
                    Shusshin(name="Mongolia", international=True),
                    True,
                )
            )

            search_fuzzy.side_effect = [
                LookupError,
                [SimpleNamespace(name="Mongolia")],
            ]

            mock_api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = mock_api
            client_cls.return_value.__aexit__.return_value = None
            mock_api.get_all_rikishi.return_value = rikishi_data

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                call_command("populate")
            finally:
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop.close()

            # Should warn twice: once for skip and once for unknown country
            self.assertGreaterEqual(warn_mock.call_count, 2)
            so.aget_or_create.assert_awaited_with(
                name="Mongolia", international=True
            )

    def test_warn_helper(self):
        """The warn helper should format and write messages."""
        cmd = Command()
        output = []
        cmd.stdout = SimpleNamespace(write=lambda m: output.append(m))
        cmd.style = SimpleNamespace(WARNING=lambda m: m)
        cmd.warn("oops")
        self.assertIn("oops", output[-1])
