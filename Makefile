.PHONY: format lint check test install-dev

# Install development dependencies
install-dev:
	pip install -e ".[dev]"

# Format code with black and isort
format:
	black market_news_generator/ tests/
	isort market_news_generator/ tests/

# Lint code with flake8
lint:
	flake8 market_news_generator/ tests/

# Check formatting without making changes
check:
	black --check market_news_generator/ tests/
	isort --check-only market_news_generator/ tests/
	flake8 market_news_generator/ tests/

# Run tests
test:
	python -m unittest discover tests/ -v

# Run all checks (format, lint, test)
all: format lint test
	@echo "✅ All checks passed!"
