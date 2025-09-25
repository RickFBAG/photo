from datetime import datetime, timedelta
from typing import List, Tuple

from PIL import ImageDraw

from .base import Widget, Rect


class AgendaWidget:
    def __init__(self, config) -> None:
        self.config = config

    def draw(self, draw: ImageDraw.ImageDraw, region: Rect) -> None:
        x0, y0, x1, y1 = region
        width = x1 - x0
        height = y1 - y0

        title_font = draw.font if hasattr(draw, "font") else None
        # Header
        draw.rectangle(region, fill=self.config.get("theme.background"))
        fg = self.config.get("theme.primary")
        accent = self.config.get("theme.accent")
        draw.text((x0 + 16, y0 + 8), "Agenda", fill=accent)

        # Mock data for now
        now = datetime.now()
        events = [
            (now.replace(hour=9, minute=0), "Standup", "Zoom"),
            (now.replace(hour=12, minute=30), "Lunch", "Kitchen"),
            (now.replace(hour=15, minute=0), "1:1", "Room 2"),
        ]

        y = y0 + 40
        for dt, title, loc in events:
            time_str = dt.strftime("%H:%M")
            draw.text((x0 + 16, y), f"{time_str}  {title} — {loc}", fill=fg)
            y += 28


