from app.models import Basho, BashoHistory, BashoRating, Bout, Division, Rikishi
from app.schemas import (
    BashoHistorySchema,
    BashoRatingSchema,
    BashoSchema,
    BoutSchema,
    DivisionSchema,
    RikishiSchema,
)


def rikishi_to_schema(rikishi: Rikishi) -> RikishiSchema:
    """Convert a ``Rikishi`` instance to ``RikishiSchema``."""

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


def division_to_schema(division: Division) -> DivisionSchema:
    """Convert a ``Division`` instance to ``DivisionSchema``."""

    return DivisionSchema(
        name=division.name,
        name_short=division.name_short,
        level=division.level,
    )


def basho_to_schema(basho: Basho) -> BashoSchema:
    """Convert a ``Basho`` instance to ``BashoSchema``."""

    return BashoSchema(
        slug=basho.slug,
        year=basho.year,
        month=basho.month,
        start_date=basho.start_date,
        end_date=basho.end_date,
    )


def bout_to_schema(bout: Bout) -> BoutSchema:
    """Convert a ``Bout`` instance to ``BoutSchema``."""

    return BoutSchema(
        day=bout.day,
        match_no=bout.match_no,
        division=bout.division.name,
        east=bout.east_shikona,
        west=bout.west_shikona,
        kimarite=bout.kimarite,
        winner=bout.winner.name,
    )


def history_to_schema(record: BashoHistory) -> BashoHistorySchema:
    """Convert a ``BashoHistory`` instance to ``BashoHistorySchema``."""

    return BashoHistorySchema(
        basho=record.basho.slug,
        rank=record.rank.title,
        height=record.height,
        weight=record.weight,
        shikona_en=record.shikona_en,
        shikona_jp=record.shikona_jp,
    )


def rating_to_schema(rating: BashoRating) -> BashoRatingSchema:
    """Convert a ``BashoRating`` instance to ``BashoRatingSchema``."""

    return BashoRatingSchema(
        basho=rating.basho.slug,
        previous_rating=rating.previous_rating,
        previous_rd=rating.previous_rd,
        previous_vol=rating.previous_vol,
        rating=rating.rating,
        rd=rating.rd,
        vol=rating.vol,
    )
