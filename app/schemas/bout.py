from ninja import Schema


class BoutSchema(Schema):
    """Serialized representation of a ``Bout``."""

    day: int
    match_no: int
    division: str
    east: str
    west: str
    kimarite: str
    winner: str
