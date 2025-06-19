from datetime import date
from typing import List, Optional

from django.db.models import Q
from ninja import NinjaAPI, Schema

from .models import Rikishi


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


api = NinjaAPI()


@api.get("")
def root(request):
    """Return a simple confirmation message."""
    return {"status": "ok"}


def _rikishi_to_schema(rikishi: Rikishi) -> RikishiSchema:
    """Convert a :class:`Rikishi` instance to :class:`RikishiSchema`."""

    return RikishiSchema(
        id=rikishi.id,
        name=rikishi.name,
        name_jp=rikishi.name_jp,
        heya=rikishi.heya.name if rikishi.heya else None,
        shusshin=rikishi.shusshin.name if rikishi.shusshin else None,
        rank=rikishi.rank.title if rikishi.rank else None,
        division=rikishi.rank.division.name if rikishi.rank else None,
        international=(
            rikishi.shusshin.international if rikishi.shusshin else False
        ),
        intai=rikishi.intai,
    )


@api.get("/rikishi/", response=List[RikishiSchema])
def rikishi_list(
    request,
    include_retired: Optional[bool] = None,
    q: Optional[str] = None,
    division: Optional[str] = None,
    heya: Optional[str] = None,
    international: Optional[bool] = None,
):
    """Return a filtered list of rikishi."""

    queryset = Rikishi.objects.all()
    if include_retired is None:
        queryset = queryset.filter(intai__isnull=True)
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(name_jp__icontains=q)
        )
    if heya:
        queryset = queryset.filter(heya__slug=heya)
    if division:
        queryset = queryset.filter(rank__division__name=division)
    if international is not None:
        queryset = queryset.filter(shusshin__international=True)

    return [_rikishi_to_schema(r) for r in queryset]


@api.get("/rikishi/{rikishi_id}/", response=RikishiSchema)
def rikishi_detail(request, rikishi_id: int):
    """Return details for a single rikishi."""

    rikishi = Rikishi.objects.get(pk=rikishi_id)
    return _rikishi_to_schema(rikishi)
