# ZenRows Scraping API - Simple Makefile
# ======================================

.PHONY: help up down test clean

# Default target
help: ## Show available commands
	@echo "Available commands:"
	@echo "  make up     - Start Docker services"
	@echo "  make down   - Stop Docker services"
	@echo "  make test   - Run all tests"
	@echo "  make clean  - Clean up containers and files"

# Core Commands
up: ## Start Docker services
	docker-compose up -d

down: ## Stop Docker services
	docker-compose down

test: ## Run all tests
	poetry run python -m pytest

clean: ## Clean up containers and files
	docker-compose down -v
	rm -f *.db
