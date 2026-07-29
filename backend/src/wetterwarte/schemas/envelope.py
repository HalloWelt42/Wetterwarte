"""Einheitlicher Antwort-Umschlag: { data, meta }."""

from typing import Generic, TypeVar

from pydantic import BaseModel

from ..config import settings

T = TypeVar("T")


class Meta(BaseModel):
    version: str = settings.version
    platzhalter: bool = False


class Envelope(BaseModel, Generic[T]):
    data: T
    meta: Meta = Meta()


def wrap(data: object, *, platzhalter: bool = False) -> dict:
    return {"data": data, "meta": {"version": settings.version, "platzhalter": platzhalter}}
