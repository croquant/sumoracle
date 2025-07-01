from typing import List, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router

from app.models import Rikishi
from app.schemas import RikishiSchema
from libs.api_utils import rikishi_to_schema

router = Router()


@router.get("", response=List[RikishiSchema])
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

    return [rikishi_to_schema(r) for r in queryset]


@router.get("{rikishi_id}/", response=RikishiSchema)
def rikishi_detail(request, rikishi_id: int):
    """Return details for a single rikishi."""

    rikishi = get_object_or_404(Rikishi, pk=rikishi_id)
    return rikishi_to_schema(rikishi)
