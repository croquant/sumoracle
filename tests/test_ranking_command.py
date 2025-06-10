import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from app.management.commands.ranking import (
    Command,
    get_existing_basho,
    get_existing_keys,
    get_existing_rank,
    get_rikishis,
)
from app.models.basho import Basho
from app.models.rank import Rank
from app.models.rikishi import Rikishi


class RankingCommandTests(SimpleTestCase):
    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_helper_functions(self):
        with (
            patch("app.management.commands.ranking.Rikishi.objects") as ro,
            patch("app.management.commands.ranking.Basho.objects") as bo,
            patch("app.management.commands.ranking.Rank.objects") as rao,
            patch("app.management.commands.ranking.BashoHistory.objects") as ho,
        ):
            ro.only.return_value = [1]
            bo.all.return_value = [SimpleNamespace(slug="x")]
            rao.all.return_value = [SimpleNamespace(slug="y")]
            ho.values_list.return_value = [(1, "x")]

            self.assertEqual(self.run_async(get_rikishis()), [1])
            self.assertEqual(
                self.run_async(get_existing_basho()),
                {"x": bo.all.return_value[0]},
            )
            self.assertEqual(
                self.run_async(get_existing_rank()),
                {"y": rao.all.return_value[0]},
            )
            self.assertEqual(self.run_async(get_existing_keys()), {(1, "x")})

    def test_shikona_fields_populated(self):
        rikishi = Rikishi(id=1, name="R", name_jp="R")
        basho = Basho(year=2025, month=1)
        basho.slug = "202501"
        rank = Rank(title="Y", level=1)

        async_mock = AsyncMock
        with (
            patch(
                "app.management.commands.ranking.get_rikishis",
                new=async_mock(return_value=[rikishi]),
            ),
            patch(
                "app.management.commands.ranking.get_existing_basho",
                new=async_mock(return_value={basho.slug: basho}),
            ),
            patch(
                "app.management.commands.ranking.get_existing_rank",
                new=async_mock(return_value={}),
            ),
            patch(
                "app.management.commands.ranking.get_existing_keys",
                new=async_mock(return_value=set()),
            ),
            patch(
                "app.management.commands.ranking.Rank.objects.aget_or_create",
                new=async_mock(return_value=(rank, True)),
            ),
            patch(
                "app.management.commands.ranking."
                "BashoHistory.objects.abulk_create",
                new=async_mock(),
            ) as mock_bulk,
            patch(
                "app.management.commands.ranking.SumoApiClient",
            ) as mock_client_cls,
        ):
            mock_api = AsyncMock()
            mock_client_cls.return_value = mock_api
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
            mock_api.aclose.return_value = None

            cmd = Command()
            cmd.log = lambda *a, **k: None
            self.run_async(cmd._handle_async())

            created = mock_bulk.call_args[0][0][0]
            self.assertEqual(created.shikona_en, "Test")
            self.assertEqual(created.shikona_jp, "テスト")
