#!/usr/bin/env python3
"""
Live Market Watch - Uses country-aware market data with camelCase
"""

import signal
import sys
import time
from datetime import datetime
from typing import List

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .enhanced_market_data import EnhancedMarketDataProvider
from .market_data import NewsItem, StockData


class MarketWatch:
    def __init__(self, countryCode=None):
        self.console = Console()
        self.running = True
        self.provider = EnhancedMarketDataProvider(countryCode=countryCode)

        # Setup signal handler
        signal.signal(signal.SIGINT, self._signalHandler)

    def _signalHandler(self, signum, frame):
        self.running = False

    def _getTradingAdvice(
        self, stock: StockData, news: List[NewsItem]
    ) -> tuple[str, str]:
        """Get trading advice based on stock data and news"""
        changePct = abs(stock.changePercent)

        # Check news impact
        newsImpact = "neutral"
        for item in news:
            if stock.symbol in item.impact:
                newsImpact = (
                    "positive" if item.impact[stock.symbol] == "up" else "negative"
                )
                break

        if stock.changePercent < -2.0 and changePct > 2.0:
            if newsImpact == "positive":
                return "🟢 BUY ", "Bad news temporary, good company"
            else:
                return "🟢 BUY ", "Good discount price"
        elif stock.changePercent > 3.0:
            return "🔴 SELL", "Take profits while high"
        elif stock.changePercent > 1.5:
            if newsImpact == "positive":
                return "🟡 HOLD", "Riding positive news"
            else:
                return "🟡 HOLD", "Steady upward trend"
        elif changePct < 1.0:
            return "🔵 WAIT", "Normal trading range"
        else:
            return "🔵 WAIT", "Minor movement"

    def _createStocksTable(
        self, stocks: List[StockData], news: List[NewsItem]
    ) -> Table:
        """Create stocks table with alternating row colors"""
        marketSummary = self.provider.getMarketSummary()
        tableTitle = (
            f"📊 {marketSummary['country']} Top Stocks ({marketSummary['currency']})"
        )

        table = Table(show_header=True, header_style="bold blue", title=tableTitle)
        table.add_column("Stock", style="cyan", width=12)
        table.add_column("Price", justify="right", style="green", width=12)
        table.add_column("Change", justify="right", width=14)
        table.add_column("Action", justify="center", width=10)
        table.add_column("Why?", style="italic", width=40, no_wrap=True)

        for i, stock in enumerate(stocks):
            # Alternating row colors - subtle but visible in both light/dark modes
            rowStyle = "on grey15" if i % 2 == 0 else None

            # Format price with currency
            priceStr = f"{stock.price:.2f} {marketSummary['currency']}"

            # Format change
            changeStr = f"{stock.change:+.2f} ({stock.changePercent:+.1f}%)"
            changeStyle = (
                "green" if stock.change > 0 else "red" if stock.change < 0 else "white"
            )

            # Get advice
            action, advice = self._getTradingAdvice(stock, news)

            # Fixed width explanation - exactly 40 chars
            explanation = stock.explanation
            if len(explanation) > 40:
                explanation = explanation[:37] + "..."
            explanation = explanation.ljust(40)  # Always pad to 40 chars

            table.add_row(
                f"${stock.symbol}",
                priceStr,
                Text(changeStr, style=changeStyle),
                action,
                explanation,
                style=rowStyle,
            )

        return table

    def _createNewsPanel(self, news: List[NewsItem]) -> Panel:
        """Create news panel"""
        marketSummary = self.provider.getMarketSummary()

        if not news:
            content = Text("📰 Loading news...", style="dim")
        else:
            newsItems = []
            for item in news:
                # Show affected stocks
                affected = ", ".join(
                    [
                        f"${k}{'📈' if v == 'up' else '📉'}"
                        for k, v in item.impact.items()
                    ]
                )

                newsText = f"• {item.headline}\n"
                newsText += f"  💡 {item.explanation}\n"
                if affected:
                    newsText += f"  📊 Affects: {affected}\n"

                newsItems.append(newsText)

            content = Text("\n".join(newsItems))

        panelTitle = f"📰 {marketSummary['country']} Market News"
        return Panel(content, title=panelTitle, border_style="yellow")

    def _createDashboard(self, stocks: List[StockData], news: List[NewsItem]) -> Layout:
        """Create dashboard layout"""
        layout = Layout()

        # Header with market info
        marketSummary = self.provider.getMarketSummary()
        currentTime = datetime.now().strftime("%H:%M:%S")
        headerText = f"📈 {marketSummary['country']} MARKET WATCH 📉 • {currentTime}"
        indexesText = f"Indexes: {', '.join(marketSummary['indexes'])}"

        header = Panel(
            Align.center(Text(f"{headerText}\n{indexesText}", style="bold magenta")),
            style="blue",
        )

        # Main content
        stocksTable = self._createStocksTable(stocks, news)
        newsPanel = self._createNewsPanel(news)

        # Footer
        footer = Panel(
            Align.center(
                "Press Ctrl+C to quit • Auto-detected market • Updates every 3s"
            ),
            style="dim",
        )

        # Layout
        mainContent = Layout()
        mainContent.split_row(Layout(stocksTable, ratio=2), Layout(newsPanel, ratio=1))

        layout.split_column(Layout(header, size=4), mainContent, Layout(footer, size=3))

        return layout

    def run(self):
        """Main run loop with graceful fallback messaging"""
        marketSummary = self.provider.getMarketSummary()

        self.console.print(
            f"[bold green]🚀 Starting {marketSummary['country']} Market Watch...[/bold green]"
        )

        if marketSummary.get("fallback", False):
            self.console.print(
                f"[yellow]📍 {marketSummary.get('fallbackMessage', 'Using global market data')}[/yellow]"
            )
            self.console.print(
                f"[dim]Note: Local market data not yet available for {marketSummary['country']}[/dim]"
            )
        else:
            self.console.print(
                f"[dim]Auto-detected: {marketSummary['country']} ({marketSummary['currency']})[/dim]"
            )

        self.console.print(
            f"[dim]Tracking {marketSummary['stockCount']} top stocks[/dim]\n"
        )

        # Show data provider info
        providers = marketSummary.get("dataProviders", {})
        if providers.get("hasRealData", False):
            financialProviders = ", ".join(providers.get("financial", []))
            newsProviders = ", ".join(providers.get("news", []))

            if financialProviders:
                self.console.print(
                    f"[dim]📈 Financial data: {financialProviders}[/dim]"
                )
            if newsProviders:
                self.console.print(f"[dim]📰 News data: {newsProviders}[/dim]")
            self.console.print()  # Extra line break
        else:
            self.console.print("[dim]📊 Using simulated market data[/dim]\n")

        try:
            with Live(refresh_per_second=1, screen=True) as live:
                while self.running:
                    try:
                        # Get fresh data
                        stocks = self.provider.getAllStocks()
                        news = self.provider.getMarketNews()

                        # Update display
                        live.update(self._createDashboard(stocks, news))

                    except Exception as e:
                        # Show error but keep running
                        errorPanel = Panel(f"Error: {e}", style="red")
                        live.update(errorPanel)

                    time.sleep(3)

        except KeyboardInterrupt:
            pass
        finally:
            self.console.print(
                f"\n[bold red]📊 {marketSummary['country']} Market Watch stopped[/bold red]"
            )


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Market Watch")
    parser.add_argument("--country", "-c", help="Country code (e.g., US, IN, GB, DE, JP, CA)")
    args = parser.parse_args()
    
    try:
        watch = MarketWatch(countryCode=args.country)
        watch.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
