from typing import List

from PIL import ImageDraw

from .base import Widget, Rect


class NewsWidget:
    def __init__(self, config) -> None:
        self.config = config

    def draw(self, draw: ImageDraw.ImageDraw, region: Rect) -> None:
        x0, y0, x1, y1 = region
        draw.rectangle(region, fill=self.config.get("theme.background"))
        fg = self.config.get("theme.primary")
        accent = self.config.get("theme.accent")
        draw.text((x0 + 16, y0 + 8), "Top News", fill=accent)

        # Temporary mocked headlines
        headlines: List[str] = [
            "Markets steady as inflation cools",
            "Tech unveils new AI chips",
            "Global travel demand surges",
            "Energy prices decline",
            "New health guidelines released",
        ]

        y = y0 + 40
        for title in headlines[:5]:
            draw.text((x0 + 16, y), f"• {title}", fill=fg)
            y += 24


