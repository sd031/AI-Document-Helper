.PHONY: help setup start stop restart logs test clean build train

help:
	@echo "AI Document Helper - Available Commands"
	@echo "========================================"
	@echo "make setup      - Initial setup and start services"
	@echo "make start      - Start all services"
	@echo "make stop       - Stop all services"
	@echo "make restart    - Restart all services"
	@echo "make logs       - View logs from all services"
	@echo "make test       - Run all tests"
	@echo "make train      - Run MLOps training pipeline"
	@echo "make build      - Rebuild Docker images"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make shell-backend  - Access backend container shell"
	@echo "make shell-frontend - Access frontend container shell"

setup:
	@echo "Running initial setup..."
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

start:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

stop:
	@echo "Stopping services..."
	@docker-compose down

restart:
	@echo "Restarting services..."
	@docker-compose restart

logs:
	@docker-compose logs -f

test:
	@echo "Running tests..."
	@chmod +x scripts/run_tests.sh
	@./scripts/run_tests.sh

train:
	@echo "Running training pipeline..."
	@docker-compose --profile training up mlops

build:
	@echo "Building Docker images..."
	@docker-compose build

clean:
	@echo "Cleaning up..."
	@docker-compose down -v
	@echo "Cleanup complete!"

shell-backend:
	@docker-compose exec backend bash

shell-frontend:
	@docker-compose exec frontend sh

pull-model:
	@echo "Pulling Ollama model..."
	@docker exec ollama ollama pull llama3.2

status:
	@docker-compose ps

stats:
	@curl -s http://localhost:8000/stats | python3 -m json.tool
