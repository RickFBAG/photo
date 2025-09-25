import os
import threading
import time
from typing import List

from .config import ConfigManager
from .renderer import DisplayRenderer
from ..widgets.base import Widget
from ..widgets.agenda import AgendaWidget
from ..widgets.news import NewsWidget
from ..widgets.market import MarketWidget
from ..services.calendar import CalendarService
from ..services.news import NewsService
from ..services.market import MarketService
from ..services.weather import WeatherService


class SmartDisplayApp:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.renderer = DisplayRenderer(self.config)
        self.widgets: List[Widget] = []
        self._load_widgets()

    def _load_widgets(self) -> None:
        layout = self.config.get("layout.enabled_widgets", ["agenda", "news", "market"])
        widget_map = {
            "agenda": AgendaWidget,
            "news": NewsWidget,
            "market": MarketWidget,
        }
        self.widgets = [widget_map[name](self.config) for name in layout if name in widget_map]

    def render_once(self) -> None:
        mode = (self.config.get("display.mode", "html") or "html").lower()
        if mode == "html":
            context = self._build_context()
            image = self.renderer.render_html(context)
            self.renderer.show(image)
            return

        # Fallback to PIL widgets mode
        image = self.renderer.create_canvas()
        draw = self.renderer.get_draw(image)
        width, height = image.size
        num = max(1, len(self.widgets))
        slot_h = height // num
        y = 0
        for widget in self.widgets:
            region = (0, y, width, y + slot_h)
            widget.draw(draw, region)
            y += slot_h
        self.renderer.show(image)

    def _build_context(self) -> dict:
        from datetime import datetime

        now_str = datetime.now().strftime("%a %d %b • %H:%M")

        # Calendar
        ics_url = self.config.get("data.calendar.ics_url", "")
        look = int(self.config.get("data.calendar.lookahead_days", 3) or 3)
        tzname = self.config.get("data.calendar.timezone", None)
        cal = CalendarService(ics_url=ics_url, lookahead_days=look, timezone_name=tzname)
        events = cal.fetch_events()
        agenda = [{"time": e.start.strftime("%H:%M"), "title": e.title, "location": e.location or ""} for e in events][:6]

        # News
        rss_url = self.config.get("data.news.rss_url", "https://feeds.bbci.co.uk/news/rss.xml")
        news_limit = int(self.config.get("data.news.limit", 3) or 3)
        headlines = NewsService(rss_url=rss_url, limit=news_limit).fetch_headlines()

        # Market
        symbol = self.config.get("data.market.symbol", "VWCE")
        msvc = MarketService(symbol=symbol)
        q = msvc.fetch_quote()
        hist = msvc.fetch_history(30)
        market = {"symbol": symbol, "price": f"{q.price:.2f}" if q else "-", "change_pct": round(q.change_pct, 2) if q else 0.0, "history": hist}

        # Weather
        lat = float(self.config.get("data.weather.lat", 52.3676) or 52.3676)
        lon = float(self.config.get("data.weather.lon", 4.9041) or 4.9041)
        wsvc = WeatherService(lat=lat, lon=lon)
        w = wsvc.fetch()
        weather = {
            "temp": f"{w.temperature_c:.0f}°C" if w else "-",
            "cond": w.condition if w else "",
            "icon": w.icon if w else "☁",
            "hi": f"{w.high_c:.0f}°" if (w and w.high_c is not None) else "",
            "lo": f"{w.low_c:.0f}°" if (w and w.low_c is not None) else "",
            "hourly": w.hourly if w and w.hourly else [],
        }

        return {"now_str": now_str, "agenda": agenda, "headlines": headlines, "market": market, "weather": weather}

    def run(self) -> None:
        interval = int(self.config.get("refresh.interval_seconds", 300))
        while True:
            self._load_widgets()
            self.render_once()
            time.sleep(interval)


