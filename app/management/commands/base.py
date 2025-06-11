import asyncio

from django.core.management.base import BaseCommand

from libs.sumoapi import SumoApiError


class AsyncBaseCommand(BaseCommand):
    """Base class for async management commands."""

    async def run(self, *args, **kwargs):
        """Override in subclasses with async logic."""
        raise NotImplementedError("Subclasses must implement run()")

    def handle(self, *args, **kwargs):
        try:
            asyncio.run(self.run(*args, **kwargs))
        except SumoApiError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
