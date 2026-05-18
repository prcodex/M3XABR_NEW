"""Actor 3 — Agent Hub.

Fires data agents in parallel to gather labeled context blocks for the
synthesizer. The Brazil subset doesn't fire macro-only agents (Iran,
Hormuz, Trump approval, etc.).

For m3xabr-core v0, the markets agent is implemented against yfinance
(free, no API key). polymarket/calendar/boost are stubbed as plug
points — implement your own by subclassing the AgentHub or by
extending its `agents` registry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from m3xabr_core.schemas import AgentBlock, AgentContext, ClassifierOutput


class DataAgent(Protocol):
    """A data agent that produces a labeled context block."""

    name: str

    def fire(self, classifier_output: ClassifierOutput) -> AgentBlock | None:
        """Run the agent. Return None if no relevant data."""
        ...


class MarketsAgent:
    """Live market snapshot via yfinance.

    Pulls Ibovespa, USDBRL, S&P, DXY, oil, gold. Free, no API key, fine
    for v0 demos. Production-grade would use a real-time market data
    feed.
    """

    name = "MARKET SNAPSHOT"

    DEFAULT_TICKERS = {
        "Ibovespa": "^BVSP",
        "USD/BRL": "USDBRL=X",
        "S&P 500": "^GSPC",
        "DXY": "DX-Y.NYB",
        "Oil (WTI)": "CL=F",
        "Gold": "GC=F",
    }

    def __init__(self, tickers: dict[str, str] | None = None) -> None:
        self._tickers = tickers or self.DEFAULT_TICKERS

    def fire(self, classifier_output: ClassifierOutput) -> AgentBlock | None:
        """Always fires for Brazil queries — markets are background context."""
        try:
            import yfinance as yf
        except ImportError:
            # Markets agent disabled — return None and let synthesizer
            # work without market context
            return None

        lines = ["Ticker      Price       Change%"]
        for label, ticker in self._tickers.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="2d")
                if len(hist) < 1:
                    continue
                price = hist["Close"].iloc[-1]
                if len(hist) >= 2:
                    prev = hist["Close"].iloc[-2]
                    change_pct = (price - prev) / prev * 100
                else:
                    change_pct = 0.0
                lines.append(f"{label:<10}  {price:>10.2f}  {change_pct:>+6.2f}%")
            except Exception:
                # Skip failed tickers silently — markets agent should
                # be resilient
                continue

        if len(lines) == 1:  # only header, no data
            return None

        return AgentBlock(
            name=self.name,
            content="\n".join(lines),
            timestamp=datetime.now(timezone.utc),
        )


class PolymarketAgent:
    """Stub. Implement your Polymarket integration here.

    The production implementation would query Polymarket's Gamma API for
    markets relevant to Brazilian politics (2026 election, etc.) when
    the classifier indicates electoral topics.
    """

    name = "POLYMARKET"

    def fire(self, classifier_output: ClassifierOutput) -> AgentBlock | None:
        # Only fire for electoral topics
        if "election_polls" not in classifier_output.topics:
            return None
        # Stub — return None so synthesizer doesn't see fake data
        return None


class CalendarAgent:
    """Stub. Implement your economic-calendar integration here.

    Production would query an econ-calendar source (econoday, investing.com
    API, or a curated YAML) for upcoming Brazilian releases.
    """

    name = "CALENDAR"

    def fire(self, classifier_output: ClassifierOutput) -> AgentBlock | None:
        return None


class BoostAgent:
    """Stub. Implement your boost agent here.

    Production would query the entity registry for sources matching
    the entities mentioned in the query, and surface their most recent
    relevant content.
    """

    name = "BOOST"

    def fire(self, classifier_output: ClassifierOutput) -> AgentBlock | None:
        return None


class AgentHub:
    """Actor 3 — orchestrates data agents."""

    def __init__(self, agents: list[DataAgent] | None = None) -> None:
        if agents is None:
            agents = [
                MarketsAgent(),
                PolymarketAgent(),
                CalendarAgent(),
                BoostAgent(),
            ]
        self._agents = agents

    def gather(self, classifier_output: ClassifierOutput) -> AgentContext:
        """Run all applicable agents and collect their blocks."""
        blocks: list[AgentBlock] = []
        for agent in self._agents:
            try:
                block = agent.fire(classifier_output)
                if block is not None:
                    blocks.append(block)
            except Exception:
                # Agent failures should never break the pipeline
                continue
        return AgentContext(blocks=blocks)

    def register(self, agent: DataAgent) -> None:
        """Add a custom agent. Useful for extending in your fork."""
        self._agents.append(agent)
