from ninja import Schema


class BashoHistorySchema(Schema):
    """Serialized representation of ``BashoHistory``."""

    basho: str
    rank: str
    height: float | None = None
    weight: float | None = None
    shikona_en: str | None = None
    shikona_jp: str | None = None
