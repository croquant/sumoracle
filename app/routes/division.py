from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from app.models import Division
from app.schemas import DivisionSchema
from libs.api_utils import division_to_schema

router = Router()


@router.get("", response=List[DivisionSchema])
def division_list(request):
    """Return a list of all divisions."""

    queryset = Division.objects.all()
    return [division_to_schema(d) for d in queryset]


@router.get("{slug}/", response=DivisionSchema)
def division_detail(request, slug: str):
    """Return details for a single division."""

    division = get_object_or_404(Division, name__iexact=slug)
    return division_to_schema(division)
