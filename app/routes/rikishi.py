from typing import List, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router

from app.models import BashoHistory, BashoRating, Rikishi
from app.schemas import BashoHistorySchema, BashoRatingSchema, RikishiSchema
from libs.api_utils import (
    history_to_schema,
    rating_to_schema,
    rikishi_to_schema,
)

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

    queryset = Rikishi.objects.select_related(
        "rank__division",
        "heya",
        "shusshin",
        "rank",
    )
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


@router.get("{rikishi_id}/history/", response=List[BashoHistorySchema])
def rikishi_history(request, rikishi_id: int):
    """Return basho history records for a rikishi."""

    records = (
        BashoHistory.objects.select_related("basho", "rank")
        .filter(rikishi_id=rikishi_id)
        .order_by("-basho__year", "-basho__month")
    )
    return [history_to_schema(r) for r in records]


@router.get("{rikishi_id}/ratings/", response=List[BashoRatingSchema])
def rikishi_ratings(request, rikishi_id: int):
    """Return rating history records for a rikishi."""

    ratings = (
        BashoRating.objects.select_related("basho")
        .filter(rikishi_id=rikishi_id)
        .order_by("-basho__year", "-basho__month")
    )
    return [rating_to_schema(r) for r in ratings]
