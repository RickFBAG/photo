from __future__ import annotations

from typing import Protocol, Tuple

from PIL import ImageDraw


Rect = Tuple[int, int, int, int]


class Widget(Protocol):
    def __init__(self, config) -> None: ...
    def draw(self, draw: ImageDraw.ImageDraw, region: Rect) -> None: ...


