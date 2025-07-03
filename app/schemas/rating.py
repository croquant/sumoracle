from ninja import Schema


class BashoRatingSchema(Schema):
    """Serialized representation of ``BashoRating``."""

    basho: str
    previous_rating: float
    previous_rd: float
    previous_vol: float
    rating: float
    rd: float
    vol: float
