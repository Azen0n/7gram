MSG=$(error MSG required)

build:
	docker compose build
full-build:
	docker compose build --no-cache
up:
	docker compose up -d --remove-orphans
down:
	docker compose down
restart:
	docker restart sevengram_bot
logs:
	docker logs sevengram_bot
ruff-format:
	docker exec -it sevengram_bot /bin/bash -c 'uv run ruff check --fix && uv run ruff format'
sync:
	docker exec -it sevengram_bot /bin/bash -c 'uv sync'
alembic-upgrade:
	docker exec sevengram_bot alembic upgrade head
alembic-revision:
	docker exec sevengram_bot alembic revision --autogenerate -m "$(MSG)"
alembic-downgrade:
	docker exec sevengram_bot alembic downgrade -1
shell:
	docker exec -it sevengram_bot ipython
