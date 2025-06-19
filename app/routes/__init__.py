from .basho import router as basho_router  # noqa: F401
from .division import router as division_router  # noqa: F401
from .rikishi import router as rikishi_router  # noqa: F401
from .root import router as root_router  # noqa: F401

__all__ = [
    "root_router",
    "rikishi_router",
    "division_router",
    "basho_router",
]
