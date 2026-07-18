.PHONY: dev build test lint migrate seed docker-up docker-down clean

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build:
	docker compose build

test:
	cd backend && pytest tests/ -v --cov=app
	cd frontend && npm run test

lint:
	cd backend && flake8 . --max-line-length=120
	cd backend && black --check .
	cd backend && isort --check-only .
	cd frontend && npm run lint

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.seeds.run

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	docker compose down -v --remove-orphans
	docker system prune -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache

logs:
	docker compose logs -f

restart:
	docker compose restart

status:
	docker compose ps
