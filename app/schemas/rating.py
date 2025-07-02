from ninja import Schema


class BashoRatingSchema(Schema):
    """Serialized representation of ``BashoRating``."""

    basho: str
    rating: float
    rd: float
    vol: float
