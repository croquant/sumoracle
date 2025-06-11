import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from app.management.commands.base import AsyncBaseCommand
from libs.sumoapi import SumoApiError


class DummyCommand(AsyncBaseCommand):
    async def run(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return "done"


class ErrorCommand(AsyncBaseCommand):
    async def run(self, *args, **kwargs):
        raise SumoApiError("bad")


class AsyncBaseCommandTests(SimpleTestCase):
    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_run_not_implemented(self):
        cmd = AsyncBaseCommand()
        with self.assertRaises(NotImplementedError):
            self.run_async(cmd.run())

    def test_handle_invokes_run(self):
        cmd = DummyCommand()

        def runner(coro):
            return asyncio.get_event_loop().run_until_complete(coro)

        patch_path = "app.management.commands.base.asyncio.run"
        with patch(patch_path, side_effect=runner) as run_mock:
            cmd.handle(1, foo="bar")
        self.assertTrue(run_mock.called)
        self.assertEqual(cmd.args, (1,))
        self.assertEqual(cmd.kwargs, {"foo": "bar"})

    def test_handle_reports_errors(self):
        cmd = ErrorCommand()
        output = []
        cmd.stderr = SimpleNamespace(write=lambda m: output.append(m))
        cmd.style = SimpleNamespace(ERROR=lambda m: m)

        def runner(coro):
            return asyncio.get_event_loop().run_until_complete(coro)

        patch_path = "app.management.commands.base.asyncio.run"
        with patch(patch_path, side_effect=runner) as run_mock:
            cmd.handle()
        self.assertTrue(run_mock.called)
        self.assertIn("bad", output[-1])
