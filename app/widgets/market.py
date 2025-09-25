from typing import Tuple

from PIL import ImageDraw

from .base import Rect


class MarketWidget:
    def __init__(self, config) -> None:
        self.config = config

    def draw(self, draw: ImageDraw.ImageDraw, region: Rect) -> None:
        x0, y0, x1, y1 = region
        draw.rectangle(region, fill=self.config.get("theme.background"))
        fg = self.config.get("theme.primary")
        accent = self.config.get("theme.accent")
        draw.text((x0 + 16, y0 + 8), "Market", fill=accent)

        # Placeholder market info
        symbol = self.config.get("data.market.symbol", "VWCE.DE")
        price = "102.35"
        change = "+0.42%"
        draw.text((x0 + 16, y0 + 44), f"{symbol}  {price}  ({change})", fill=fg)


