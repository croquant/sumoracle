from typing import List, Optional

from django.db.models import Q
from ninja import NinjaAPI

from .models import Basho, Bout, Division, Rikishi
from .routes import root_router
from .schemas import BashoSchema, BoutSchema, DivisionSchema, RikishiSchema

api = NinjaAPI()
api.add_router("", root_router)


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


def _division_to_schema(division: Division) -> DivisionSchema:
    """Convert a :class:`Division` instance to :class:`DivisionSchema`."""

    return DivisionSchema(
        name=division.name,
        name_short=division.name_short,
        level=division.level,
    )


def _basho_to_schema(basho: Basho) -> BashoSchema:
    """Convert a :class:`Basho` instance to :class:`BashoSchema`."""

    return BashoSchema(
        slug=basho.slug,
        year=basho.year,
        month=basho.month,
        start_date=basho.start_date,
        end_date=basho.end_date,
    )


def _bout_to_schema(bout: Bout) -> BoutSchema:
    """Convert a :class:`Bout` instance to :class:`BoutSchema`."""

    return BoutSchema(
        day=bout.day,
        match_no=bout.match_no,
        division=bout.division.name,
        east=bout.east_shikona,
        west=bout.west_shikona,
        kimarite=bout.kimarite,
        winner=bout.winner.name,
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


@api.get("/division/", response=List[DivisionSchema])
def division_list(request):
    """Return a list of all divisions."""

    queryset = Division.objects.all()
    return [_division_to_schema(d) for d in queryset]


@api.get("/division/{slug}/", response=DivisionSchema)
def division_detail(request, slug: str):
    """Return details for a single division."""

    division = Division.objects.get(name__iexact=slug)
    return _division_to_schema(division)


@api.get("/basho/", response=List[BashoSchema])
def basho_list(request):
    """Return a list of basho ordered by most recent."""

    queryset = Basho.objects.all().order_by("-year", "-month")
    return [_basho_to_schema(b) for b in queryset]


@api.get("/basho/{slug}/", response=BashoSchema)
def basho_detail(request, slug: str):
    """Return details for a single basho."""

    basho = Basho.objects.get(slug=slug)
    return _basho_to_schema(basho)


@api.get("/basho/{slug}/bouts/", response=List[BoutSchema])
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
    return [_bout_to_schema(b) for b in queryset]
