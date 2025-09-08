# Market News Generator

Live market news with country, market detection and real-time stock analysis.

```bash
# Install
pip install market-news-generator
```

## Simple Example

```bash
# Live market watch with auto-detection
market

# Live market watch for specific country
market --country IN  # India
market -c GB         # United Kingdom
market -c JP         # Japan
```

```python
from market_news_generator import MarketDataProvider

provider = MarketDataProvider()

# Get market summary for your country
summary = provider.getMarketSummary()
print(f"Market: {summary['country']} ({summary['currency']})")

# Get all top stocks
stocks = provider.getAllStocks()
for stock in stocks:
    print(f"{stock.symbol}: ${stock.price:.2f} ({stock.changePercent:+.1f}%)")
```

## Features

- Country Auto-Detection with Multi-Market Support
- CLI Country Selection (US, IN, GB, DE, JP, CA)
- Real-Time Dashboard with Rich Terminal Graphics
- Smart BUY/SELL/HOLD Trading Recommendations
- Market News Integration

## Development

```bash
# Clone and install
git clone https://github.com/yourusername/market-news-generator
cd market-news-generator
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=market_news_generator --cov-report=html
```

## License

MIT License. See [License](LICENSE.md) for details.

## Feedback

Made with ❤️ by collaborative AI development.

* Authors: [Claude Sonnet 4](https://anthropic.com/) and [Karthik Kumar Viswanathan](https://github.com/guilt)
* Web   : http://karthikkumar.org
* Email : me@karthikkumar.org
