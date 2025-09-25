from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

import requests


@dataclass
class Quote:
    symbol: str
    price: float
    change_pct: float


class MarketService:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    def fetch_quote(self) -> Optional[Quote]:
        # Placeholder: return mock; can be replaced with a real provider
        return Quote(symbol=self.symbol, price=102.35, change_pct=0.42)

    def fetch_history(self, days: int = 30) -> List[Tuple[str, float]]:
        # Use Stooq free CSV endpoint for simple history if supported symbol.
        # Many ETFs like VWCE are not present; return mock normalized series for now.
        series = [100 + i * 0.2 + (i % 5 - 2) * 0.6 for i in range(days)]
        out: List[Tuple[str, float]] = [(str(i), v) for i, v in enumerate(series)]
        return out


