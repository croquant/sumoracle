from typing import List, Optional

from django.db.models import Q
from ninja import Router

from app.models import Basho, Bout
from app.schemas import BashoSchema, BoutSchema
from libs.api_utils import basho_to_schema, bout_to_schema

router = Router()


@router.get("", response=List[BashoSchema])
def basho_list(request):
    """Return a list of basho ordered by most recent."""

    queryset = Basho.objects.all().order_by("-year", "-month")
    return [basho_to_schema(b) for b in queryset]


@router.get("{slug}/", response=BashoSchema)
def basho_detail(request, slug: str):
    """Return details for a single basho."""

    basho = Basho.objects.get(slug=slug)
    return basho_to_schema(basho)


@router.get("{slug}/bouts/", response=List[BoutSchema])
def basho_bouts(
    request,
    slug: str,
    division: Optional[str] = None,
    day: Optional[int] = None,
    rikishi_id: Optional[int] = None,
):
    """Return bouts for a basho with optional filters."""

    queryset = Bout.objects.filter(basho__slug=slug)
    if division:
        queryset = queryset.filter(division__name=division)
    if day is not None:
        queryset = queryset.filter(day=day)
    if rikishi_id is not None:
        queryset = queryset.filter(
            Q(east__id=rikishi_id) | Q(west__id=rikishi_id)
        )
    return [bout_to_schema(b) for b in queryset]
