from django.test import TestCase
from django.urls import reverse

from app.models.basho import Basho
from app.models.division import Division
from app.models.history import BashoHistory
from app.models.rank import Rank
from app.models.rating import BashoRating
from app.models.rikishi import Heya, Rikishi, Shusshin
from libs.constants import Direction, RankName


class RikishiDetailViewTests(TestCase):
    """Verify behaviour of the rikishi detail view."""

    def setUp(self):
        division = Division.objects.get(name="Makuuchi")
        self.rank = Rank.objects.create(
            slug="y1e",
            division=division,
            title=RankName.YOKOZUNA,
            order=1,
            direction=Direction.EAST,
        )
        heya = Heya.objects.create(name="Miyagino")
        shusshin = Shusshin.objects.create(name="Hokkaido")
        self.rikishi = Rikishi.objects.create(
            id=1,
            name="Hakuho",
            name_jp="白鵬",
            rank=self.rank,
            heya=heya,
            shusshin=shusshin,
            height=192.0,
            weight=158.0,
        )
        basho = Basho.objects.create(year=2025, month=1)
        BashoHistory.objects.create(
            rikishi=self.rikishi,
            basho=basho,
            rank=self.rank,
            height=192.0,
            weight=158.0,
            shikona_en="Hakuho",
            shikona_jp="白鵬",
        )
        BashoRating.objects.create(
            rikishi=self.rikishi,
            basho=basho,
            rating=1500.0,
            rd=200.0,
            vol=0.06,
        )

    def test_view_status_code(self):
        """The detail view should return HTTP 200."""
        response = self.client.get(
            reverse("rikishi-detail", args=[self.rikishi.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_view_template_and_content(self):
        """Page should use template and display rikishi data."""
        response = self.client.get(
            reverse("rikishi-detail", args=[self.rikishi.id])
        )
        self.assertTemplateUsed(response, "rikishi_detail.html")
        self.assertContains(response, self.rikishi.name)
        self.assertContains(response, self.rank.long_name())
        self.assertContains(response, self.rikishi.heya.name)
        self.assertContains(response, self.rikishi.shusshin.name)
        self.assertContains(response, "192.0")
        self.assertContains(response, "158.0")
        records_url = reverse("rikishi-records", args=[self.rikishi.id])
        self.assertContains(response, f'hx-get="{records_url}"')

    def test_records_endpoint(self):
        """Records endpoint should render table with rank and rating."""

        url = reverse("rikishi-records", args=[self.rikishi.id])
        response = self.client.get(url)
        self.assertContains(response, "202501")
        self.assertContains(response, "1500")
