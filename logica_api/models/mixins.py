from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr

from pytz import timezone


class TimeMixin:
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            default=lambda: datetime.now(timezone("UTC"))
            .astimezone(timezone("America/Bogota"))
            .replace(tzinfo=None),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=lambda: datetime.now(timezone("UTC"))
            .astimezone(timezone("America/Bogota"))
            .replace(tzinfo=None),
            onupdate=lambda: datetime.now(timezone("UTC"))
            .astimezone(timezone("America/Bogota"))
            .replace(tzinfo=None),
            nullable=False,
        )
