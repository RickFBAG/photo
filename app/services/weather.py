from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import requests


@dataclass
class WeatherNow:
    temperature_c: float
    wind_kph: float
    condition: str
    icon: str
    high_c: Optional[float] = None
    low_c: Optional[float] = None
    hourly: List[Tuple[str, float]] | None = None


class WeatherService:
    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon

    def fetch(self) -> Optional[WeatherNow]:
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&current=temperature_2m,wind_speed_10m,weather_code&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
                % (self.lat, self.lon)
            )
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            j = r.json()
            cur = j.get("current", {})
            daily = j.get("daily", {})
            hourly = j.get("hourly", {})
            wcode = int(cur.get("weather_code", 0))
            icon, cond = self._icon_for_code(wcode)
            hourly_list: List[Tuple[str, float]] = []
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            for t, temp in list(zip(times, temps))[:6]:
                label = t[-5:]
                hourly_list.append((label, float(temp)))
            return WeatherNow(
                temperature_c=float(cur.get("temperature_2m", 0)),
                wind_kph=float(cur.get("wind_speed_10m", 0)),
                condition=cond,
                icon=icon,
                high_c=float((daily.get("temperature_2m_max") or [None])[0] or 0),
                low_c=float((daily.get("temperature_2m_min") or [None])[0] or 0),
                hourly=hourly_list,
            )
        except Exception:
            return None

    def _icon_for_code(self, code: int) -> tuple[str, str]:
        mapping = {
            0: ("☀", "Clear"),
            1: ("🌤", "Mainly clear"),
            2: ("⛅", "Partly cloudy"),
            3: ("☁", "Cloudy"),
            45: ("🌫", "Fog"),
            48: ("🌫", "Depositing rime fog"),
            51: ("🌦", "Light drizzle"),
            61: ("🌧", "Rain"),
            71: ("🌨", "Snow"),
            80: ("🌦", "Showers"),
            95: ("⛈", "Thunderstorm"),
        }
        return mapping.get(code, ("☁", "Clouds"))


