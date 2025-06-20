from typing import Generic, List, TypeVar

from ninja import Schema

T = TypeVar("T")


class Paginated(Schema, Generic[T]):
    """Generic pagination schema."""

    count: int
    limit: int
    offset: int
    items: List[T]
