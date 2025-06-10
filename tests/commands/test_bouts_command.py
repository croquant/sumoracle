import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from app.management.commands.bouts import Command
from libs.sumoapi import SumoApiError


class BoutsCommandTests(SimpleTestCase):
    """Tests for the ``bouts`` management command."""

    def run_async(self, coro):
        """Synchronously run an async coroutine."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def get_record(self):
        return {
            "bashoId": "202501",
            "division": "Makuuchi",
            "day": 1,
            "matchNo": 1,
            "eastId": 10,
            "westId": 11,
            "eastShikona": "East",
            "westShikona": "West",
            "kimarite": "yorikiri",
            "winnerId": 10,
        }

    def setup_patches(self):
        east = SimpleNamespace(id=10)
        west = SimpleNamespace(id=11)
        winner = east
        patches = (
            patch("app.management.commands.bouts.SumoApiClient"),
            patch(
                "app.management.commands.bouts.Basho.objects.aget_or_create",
                new=AsyncMock(return_value=(SimpleNamespace(), True)),
            ),
            patch(
                "app.management.commands.bouts.Division.objects.aget",
                new=AsyncMock(return_value=SimpleNamespace()),
            ),
            patch(
                "app.management.commands.bouts.Rikishi.objects.aget",
                new=AsyncMock(side_effect=[east, west, winner]),
            ),
            patch(
                "app.management.commands.bouts.Bout.objects.aupdate_or_create",
                new=AsyncMock(),
            ),
        )
        return patches

    def test_parses_and_saves_bout(self):
        """A single API record should populate model fields."""
        record = self.get_record()
        patches = self.setup_patches()
        with (
            patches[0] as client_cls,
            patches[1],
            patches[2],
            patches[3],
            patches[4] as create_mock,
        ):
            api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = api
            client_cls.return_value.__aexit__.return_value = None
            api.get_rikishi_matches.return_value = {"records": [record]}
            cmd = Command()
            cmd.stdout = SimpleNamespace(write=lambda msg: None)
            cmd.style = SimpleNamespace(SUCCESS=lambda m: m)
            self.run_async(cmd._handle_async(1, None))
            create_mock.assert_awaited_once()
            kwargs = create_mock.call_args.kwargs
            self.assertEqual(kwargs["defaults"]["kimarite"], "yorikiri")
            self.assertEqual(kwargs["day"], 1)
            self.assertEqual(kwargs["match_no"], 1)

    def test_basho_option_passed_to_api(self):
        """Passing ``--basho`` should filter API requests."""
        record = self.get_record()
        patches = self.setup_patches()
        with (
            patches[0] as client_cls,
            patches[1],
            patches[2],
            patches[3],
            patches[4],
        ):
            api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = api
            client_cls.return_value.__aexit__.return_value = None
            api.get_rikishi_matches.return_value = {"records": [record]}
            cmd = Command()
            cmd.stdout = SimpleNamespace(write=lambda msg: None)
            cmd.style = SimpleNamespace(SUCCESS=lambda m: m)
            self.run_async(cmd._handle_async(1, "202501"))
            api.get_rikishi_matches.assert_awaited_with(1, bashoId="202501")

    def test_no_records_no_save(self):
        """No matches should produce no ORM writes."""
        patches = self.setup_patches()
        with (
            patches[0] as client_cls,
            patches[1],
            patches[2],
            patches[3],
            patches[4] as create_mock,
        ):
            api = AsyncMock()
            client_cls.return_value.__aenter__.return_value = api
            client_cls.return_value.__aexit__.return_value = None
            api.get_rikishi_matches.return_value = {"records": []}
            output = []
            cmd = Command()
            cmd.stdout = SimpleNamespace(write=lambda msg: output.append(msg))
            cmd.style = SimpleNamespace(SUCCESS=lambda m: m)
            self.run_async(cmd._handle_async(1, None))
            create_mock.assert_not_awaited()
            self.assertIn("Imported 0 bouts", output[-1])

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
                "app.management.commands.bouts.asyncio.run",
                side_effect=runner,
            ) as run_mock,
            patch.object(
                Command,
                "_handle_async",
                new=AsyncMock(side_effect=SumoApiError("fail")),
            ),
        ):
            cmd.handle()
        self.assertTrue(run_mock.called)
        self.assertIn("fail", output[-1])

    def test_parser_arguments(self):
        """Argument parser should accept rikishi and basho options."""
        cmd = Command()
        parser = cmd.create_parser("manage.py", "bouts")
        args = parser.parse_args(["10", "--basho", "202501"])
        self.assertEqual(args.rikishi_id, 10)
        self.assertEqual(args.basho_id, "202501")
