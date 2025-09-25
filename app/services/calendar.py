from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

import requests
from icalendar import Calendar
from dateutil import tz


@dataclass
class CalendarEvent:
    start: datetime
    end: datetime
    title: str
    location: str | None = None


class CalendarService:
    def __init__(self, ics_url: str | None, lookahead_days: int = 3, timezone_name: str | None = None) -> None:
        self.ics_url = ics_url
        self.lookahead_days = lookahead_days
        self.tzinfo = tz.gettz(timezone_name) if timezone_name else tz.tzlocal()

    def fetch_events(self) -> List[CalendarEvent]:
        if not self.ics_url:
            return []
        try:
            resp = requests.get(self.ics_url, timeout=10)
            resp.raise_for_status()
            cal = Calendar.from_ical(resp.text)
        except Exception:
            return []

        now = datetime.now(timezone.utc).astimezone(self.tzinfo)
        end_window = now + timedelta(days=self.lookahead_days)
        results: List[CalendarEvent] = []
        for component in cal.walk():
            if component.name != "VEVENT":
                continue
            dtstart = component.get("dtstart")
            dtend = component.get("dtend")
            if not dtstart:
                continue
            start = self._to_dt(dtstart.dt)
            end = self._to_dt(dtend.dt) if dtend else (start + timedelta(hours=1))
            if start > end_window or end < now:
                continue
            title = str(component.get("summary", ""))
            location = str(component.get("location", "")) or None
            results.append(CalendarEvent(start=start, end=end, title=title, location=location))

        results.sort(key=lambda e: e.start)
        return results

    def _to_dt(self, value) -> datetime:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=self.tzinfo)
            return value.astimezone(self.tzinfo)
        # Date-only all-day event; assume local midnight
        return datetime(value.year, value.month, value.day, tzinfo=self.tzinfo)


