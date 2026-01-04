build:
	docker compose build
full-build:
	docker compose build --no-cache
up:
	docker compose up -d --remove-orphans
down:
	docker compose down
ruff-format:
	docker exec -it sevengram_bot /bin/bash -c 'uv run ruff check --fix && uv run ruff format'
sync:
	docker exec -it sevengram_bot /bin/bash -c 'uv sync'
