from datetime import date
from typing import Optional

from ninja import Schema


class RikishiSchema(Schema):
    """Serialized representation of a ``Rikishi``."""

    id: int
    name: str
    name_jp: str
    heya: Optional[str] = None
    shusshin: Optional[str] = None
    rank: Optional[str] = None
    division: Optional[str] = None
    international: bool = False
    intai: Optional[date] = None
