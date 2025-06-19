from django.test import TestCase
from django.urls import reverse

from app.models.division import Division
from app.models.rank import Rank
from app.models.rikishi import Rikishi
from libs.constants import Direction, RankName


class RikishiOrderingTests(TestCase):
    def setUp(self):
        division = Division.objects.get(name="Makuuchi")
        self.rank1 = Rank.objects.create(
            slug="y1e",
            division=division,
            title=RankName.YOKOZUNA,
            order=1,
            direction=Direction.EAST,
        )
        self.rank2 = Rank.objects.create(
            slug="y1w",
            division=division,
            title=RankName.YOKOZUNA,
            order=1,
            direction=Direction.WEST,
        )
        self.rank3 = Rank.objects.create(
            slug="o1e",
            division=division,
            title=RankName.OZEKI,
            order=1,
            direction=Direction.EAST,
        )
        Rikishi.objects.create(
            id=1,
            name="Hakuho",
            name_jp="白鵬",
            rank=self.rank1,
        )
        Rikishi.objects.create(
            id=2,
            name="Yokozuna West",
            name_jp="YW",
            rank=self.rank2,
        )
        Rikishi.objects.create(
            id=3,
            name="Ozeki East",
            name_jp="OE",
            rank=self.rank3,
        )
        Rikishi.objects.create(
            id=4,
            name="No Rank",
            name_jp="NR",
        )

    def test_default_model_order(self):
        ids = list(Rikishi.objects.values_list("id", flat=True))
        self.assertEqual(ids, [1, 2, 3, 4])

    def test_list_view_ordering(self):
        response = self.client.get(reverse("rikishi-list"))
        ids = [rikishi.id for rikishi in response.context["object_list"]]
        self.assertEqual(ids, [1, 2, 3, 4])
