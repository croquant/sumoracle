from .division import DivisionDetailView, DivisionListView  # noqa: F401
from .index import IndexView  # noqa: F401
from .rikishi import RikishiDetailView, RikishiListView  # noqa: F401

__all__ = [
    "IndexView",
    "DivisionListView",
    "DivisionDetailView",
    "RikishiListView",
    "RikishiDetailView",
]
