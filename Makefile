.PHONY: help format lint check test test-cov install-dev all

help: ## Print this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

format: ## Format code with black and isort
	black market_news_generator/ tests/
	isort market_news_generator/ tests/

lint: ## Lint code with flake8
	flake8 market_news_generator/ tests/

check: ## Check formatting without making changes
	black --check market_news_generator/ tests/
	isort --check-only market_news_generator/ tests/
	flake8 market_news_generator/ tests/

test: ## Run tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ --cov=market_news_generator --cov-report=html

all: format lint test ## Run all checks (format, lint, test)
	@echo "✅ All checks passed!"
