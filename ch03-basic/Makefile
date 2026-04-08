SOURCE = main.py

.PHONY: format lint run setup-db teardown-db

all: format lint

format:
	uv run ruff format $(SOURCE)
	uv run ruff check --fix $(SOURCE)

lint:
	uv run ruff check $(SOURCE)
	uv run ty check $(SOURCE)

run:
	uv run chainlit run --watch --host localhost --port 8000 main.py

create-secret:
	uv run chainlit create-secret

start-db:
	docker compose -f sandbox/postgres/docker-compose.yaml up -d

stop-db:
	docker compose -f sandbox/postgres/docker-compose.yaml stop
