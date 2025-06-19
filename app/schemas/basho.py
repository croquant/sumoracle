from datetime import date
from typing import Optional

from ninja import Schema


class BashoSchema(Schema):
    """Serialized representation of a ``Basho``."""

    slug: str
    year: int
    month: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
