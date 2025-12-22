build:
	docker compose build
full-build:
	docker compose build --no-cache
up:
	docker compose up -d --remove-orphans
down:
	docker compose down
