from typing import Iterable, Optional


class LimitOffsetPaginator:
    """Simple limit/offset pagination."""

    default_limit = 100
    max_limit = 1000

    def paginate(
        self,
        data: Iterable,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> dict:
        """Return paginated results as a dictionary."""

        if limit is None:
            limit = self.default_limit
        else:
            limit = min(int(limit), self.max_limit)
        offset = int(offset or 0)
        if hasattr(data, "count"):
            count = data.count()
        else:
            data = list(data)
            count = len(data)
        items = list(data[offset : offset + limit])
        return {
            "count": count,
            "limit": limit,
            "offset": offset,
            "items": items,
        }
