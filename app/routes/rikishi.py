from typing import Optional

from django.db.models import Q
from ninja import Router

from app.models import Rikishi
from app.schemas import Paginated, RikishiSchema
from libs.api_utils import rikishi_to_schema
from libs.pagination import LimitOffsetPaginator

router = Router()


@router.get("", response=Paginated[RikishiSchema])
def rikishi_list(
    request,
    include_retired: Optional[bool] = None,
    q: Optional[str] = None,
    division: Optional[str] = None,
    heya: Optional[str] = None,
    international: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
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

    paginator = LimitOffsetPaginator()
    data = paginator.paginate(queryset, limit, offset)
    data["items"] = [rikishi_to_schema(r) for r in data["items"]]
    return data


@router.get("{rikishi_id}/", response=RikishiSchema)
def rikishi_detail(request, rikishi_id: int):
    """Return details for a single rikishi."""

    rikishi = Rikishi.objects.get(pk=rikishi_id)
    return rikishi_to_schema(rikishi)
