import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from django.test import SimpleTestCase

from app.management.commands.history import (
    Command,
    get_existing_basho,
    get_existing_keys,
    get_existing_rank,
    get_rikishis,
    pick_measurements,
    pick_shikona,
)
from app.models.basho import Basho
from app.models.rank import Rank
from app.models.rikishi import Rikishi
from libs.sumoapi import SumoApiError

CMD_PREFIX = "app.management.commands.history"


class HistoryCommandTests(SimpleTestCase):
    """Tests for the ``history`` management command helpers."""

    def run_async(self, coro):
        """Synchronously run an async coroutine for convenience."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_helper_functions(self):
        """Utility getters should return data in expected formats."""
        with (
            patch(f"{CMD_PREFIX}.Rikishi.objects") as ro,
            patch(f"{CMD_PREFIX}.Basho.objects") as bo,
            patch(f"{CMD_PREFIX}.Rank.objects") as rao,
            patch(f"{CMD_PREFIX}.BashoHistory.objects") as ho,
        ):
            ro.only.return_value = [1]
            bo.all.return_value = [SimpleNamespace(slug="x")]
            rao.all.return_value = [SimpleNamespace(slug="y")]
            ho.values_list.return_value = [(1, "x")]

            self.assertEqual(self.run_async(get_rikishis()), [1])  # Queryset
            self.assertEqual(
                self.run_async(get_existing_basho()),
                {"x": bo.all.return_value[0]},
            )
            self.assertEqual(
                self.run_async(get_existing_rank()),
                {"y": rao.all.return_value[0]},
            )
            self.assertEqual(self.run_async(get_existing_keys()), {(1, "x")})

    def test_pick_shikona(self):
        """Select the nearest available shikona data."""
        data = {
            "202401": {"shikonaEn": "Old", "shikonaJp": "旧"},
            "202403": {"shikonaEn": "New", "shikonaJp": "新"},
        }
        self.assertEqual(pick_shikona(data, "202402")["shikonaEn"], "Old")
        self.assertEqual(pick_shikona(data, "202404")["shikonaJp"], "新")
        self.assertEqual(pick_shikona(data, "202312"), {})

    def test_pick_measurements(self):
        """Select the nearest measurement data."""
        data = {
            "202401": {"height": 180, "weight": 100},
            "202403": {"height": 181, "weight": 101},
        }
        self.assertEqual(pick_measurements(data, "202402")["height"], 180)
        self.assertEqual(pick_measurements(data, "202404")["weight"], 101)
        self.assertEqual(pick_measurements(data, "202312"), {})

    def test_shikona_fields_populated(self):
        """Command should populate shikona fields when available."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=1)
        basho.slug = "202501"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202501", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = [
                {
                    "bashoId": "202501",
                    "shikonaEn": "Test",
                    "shikonaJp": "テスト",
                }
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.shikona_en, "Test")  # Stored English
            self.assertEqual(created.shikona_jp, "テスト")  # Stored Japanese

    def test_shikona_fallback_previous(self):
        """When missing, use shikona from prior basho."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=4)
        basho.slug = "202504"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202504", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = [
                {"bashoId": "202503", "shikonaEn": "Later", "shikonaJp": "後"}
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.shikona_en, "Later")
            self.assertEqual(created.shikona_jp, "後")

    def test_no_future_shikona_used(self):
        """The command should not use future shikona entries."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=1)
        basho.slug = "202501"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202501", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = [
                {"bashoId": "202503", "shikonaEn": "Future", "shikonaJp": "未"}
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.shikona_en, "")
            self.assertEqual(created.shikona_jp, "")

    def test_measurement_fields_populated(self):
        """Command should populate measurement fields when available."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=1)
        basho.slug = "202501"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202501", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = []
            mock_api.get_measurements.return_value = [
                {"bashoId": "202501", "height": 180, "weight": 150}
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.height, 180)
            self.assertEqual(created.weight, 150)

    def test_measurement_fallback_previous(self):
        """Missing measurements should use prior values."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=2)
        basho.slug = "202502"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202502", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = []
            mock_api.get_measurements.return_value = [
                {"bashoId": "202501", "height": 180, "weight": 150}
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.height, 180)
            self.assertEqual(created.weight, 150)

    def test_no_future_measurement_used(self):
        """Measurements from future basho should be ignored."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=1)
        basho.slug = "202501"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.history.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_api
            mock_client_cls.return_value.__aexit__.return_value = None
            mock_api.get_ranking_history.return_value = {
                1: [{"bashoId": "202501", "rank": "Y1E"}]
            }
            mock_api.get_shikonas.return_value = []
            mock_api.get_measurements.return_value = [
                {"bashoId": "202503", "height": 181, "weight": 151}
            ]
            mock_api.get_basho_by_id.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd.run())

            created = mock_bulk.call_args[0][0][0]
            self.assertIsNone(created.height)
            self.assertIsNone(created.weight)

    def test_log_and_handle(self):
        """Ensure synchronous wrapper and logger behave."""
        cmd = Command()
        output = []
        cmd.stdout = SimpleNamespace(write=lambda msg: output.append(msg))
        cmd.style = SimpleNamespace(NOTICE=lambda m: m)
        with (
            patch("app.management.commands.base.asyncio.run") as run_mock,
            patch.object(
                Command,
                "run",
                new=MagicMock(return_value=None),
            ) as a_mock,
        ):
            cmd.handle()
            self.assertTrue(run_mock.called)
            self.assertTrue(a_mock.called)
        cmd.log("hello")
        self.assertEqual(output[-1], "hello")  # Message printed

    def test_handle_api_error(self):
        """Handle should report API failures."""
        cmd = Command()
        output = []
        cmd.stderr = SimpleNamespace(write=lambda m: output.append(m))
        cmd.style = SimpleNamespace(ERROR=lambda m: m)

        def runner(c):
            return asyncio.get_event_loop().run_until_complete(c)

        with (
            patch(
                "app.management.commands.base.asyncio.run",
                side_effect=runner,
            ) as run_mock,
            patch.object(
                Command,
                "run",
                new=AsyncMock(side_effect=SumoApiError("oops")),
            ),
        ):
            cmd.handle()
        self.assertTrue(run_mock.called)
        self.assertIn("oops", output[-1])

    def test_get_or_create_rank_variations(self):
        """Rank caching should prevent duplicate queries."""
        cmd = Command()
        cache = {}
        rank_obj = SimpleNamespace()
        with patch(
            "app.management.commands.history.Rank.objects.aget_or_create",
            new=AsyncMock(return_value=(rank_obj, True)),
        ) as create_mock:
            self.run_async(cmd.get_or_create_rank("Yokozuna 1 East", cache))
            self.run_async(cmd.get_or_create_rank("Yokozuna 1 East", cache))
            self.run_async(cmd.get_or_create_rank("Sekiwake 1", cache))
            self.run_async(cmd.get_or_create_rank("Jonokuchi", cache))
        self.assertEqual(create_mock.call_count, 3)

    def test_create_basho_from_api(self):
        """Creating a ``Basho`` from API data should hit the ORM once."""
        cmd = Command()
        basho_data = {
            "date": "202501",
            "startDate": "2025-01-10T00:00:00Z",
            "endDate": "2025-01-24T00:00:00Z",
        }
        with patch(
            "app.management.commands.history.Basho.objects.acreate",
            new=AsyncMock(),
        ) as create_mock:
            self.run_async(cmd.create_basho_from_api(basho_data))
        create_mock.assert_awaited_once()

    def test_handle_skip_old_and_new_basho_paths(self):
        """Command should fetch missing basho and bulk save history."""
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        existing = Basho(year=2025, month=4)
        existing.slug = "202504"
        async_mock = AsyncMock
        entries = (
            [{"bashoId": "202503", "rank": "Y1E"}]
            + [{"bashoId": "195702", "rank": "Y1E"}]
            + [{"bashoId": "202502", "rank": "Y1E"}]
            + [{"bashoId": "202505", "rank": "Y1E"}]
            + [{"bashoId": "202504", "rank": "Y1E"}] * 1001
        )
        with (
            patch(
                "app.management.commands.history.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.history.get_existing_basho",
                new=async_mock(return_value={"202504": existing}),
            ),
            patch(
                "app.management.commands.history.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.history.get_existing_keys",
                new=async_mock(return_value={(1, "202503")}),
            ),
            patch(
                "app.management.commands.history.SumoApiClient"
            ) as client_cls,
            patch(
                "app.management.commands.history.BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as bulk_mock,
            patch(
                "app.management.commands.history.Rank.objects.aget_or_create",
                new=async_mock(return_value=(Rank(title="Y"), True)),
            ),
        ):
            api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = api
            client_cls.return_value.__aexit__.return_value = None
            api.get_ranking_history.return_value = {1: entries}
            api.get_shikonas.return_value = []
            api.get_basho_by_id.side_effect = [
                {
                    "date": "202502",
                    "startDate": "2025-02-01T00:00:00Z",
                    "endDate": "2025-02-15T00:00:00Z",
                },
                None,
            ]
            cmd = Command()
            cmd.log = lambda *a, **k: None
            cmd.create_basho_from_api = AsyncMock(
                return_value=Basho(year=2025, month=2)
            )
            cmd.bulk_save = AsyncMock(wraps=cmd.bulk_save)
            self.run_async(cmd.run())
            cmd.create_basho_from_api.assert_awaited()
            self.assertTrue(bulk_mock.await_count)
            cmd.bulk_save.assert_awaited()
