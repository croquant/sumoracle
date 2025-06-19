from ninja import Schema


class DivisionSchema(Schema):
    """Serialized representation of a ``Division``."""

    name: str
    name_short: str
    level: int
