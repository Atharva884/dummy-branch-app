ENV ?= dev
ENV_FILE = .env.$(ENV)

SERVICE_DB = db
SERVICE_API = api
SERVICE_NGINX = nginx
SERVICE_PROM = prometheus
SERVICE_GRAF = grafana

CONTAINER_API_NAME = branch-app-api
CONTAINER_DB_NAME  = branch-app-db

IMAGE = ghcr.io/atharva884/dummy-branch-app

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make up-all ENV=dev       - Start API + DB + Nginx (LOCAL build) + migrate + seed"
	@echo "  make up-img-all ENV=dev   - Start API + DB + Nginx (GHCR image) + migrate + seed"
	@echo "  make up ENV=dev           - Start API + DB + Nginx (LOCAL build)"
	@echo "  make up-img ENV=dev       - Start API + DB + Nginx (GHCR image)"
	@echo "  make pull                 - Pull latest GHCR image"
	@echo "  make pull-amd             - Pull GHCR amd64 image"
	@echo "  make monitor              - Start API + DB + Nginx + Prometheus + Grafana"
	@echo "  make migrate              - Run Alembic migrations"
	@echo "  make seed                 - Seed database"
	@echo "  make logs                 - View API logs"
	@echo "  make down                 - Stop all containers"
	@echo "  make clean                - Stop and remove volumes"
	@echo "  make nuke                 - Remove containers, volumes, images"
	@echo ""

up-all: up
	@sleep 5
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) alembic upgrade head
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) python -m scripts.seed

up-img-all: up-img
	@sleep 5
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) alembic upgrade head
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) python -m scripts.seed

up:
	docker compose --env-file $(ENV_FILE) up -d $(SERVICE_DB) $(SERVICE_API) $(SERVICE_NGINX)

up-img:
	docker compose --env-file $(ENV_FILE) up -d $(SERVICE_DB) $(SERVICE_API) $(SERVICE_NGINX)

pull:
	docker pull $(IMAGE):latest

pull-amd:
	docker pull --platform=linux/amd64 $(IMAGE):latest

monitor:
	docker compose --env-file $(ENV_FILE) up -d $(SERVICE_DB) $(SERVICE_API) $(SERVICE_NGINX) $(SERVICE_PROM) $(SERVICE_GRAF)
	@sleep 5
	@echo "Grafana: http://localhost:3000/dashboards | open http://localhost:3000/dashboards"
	open http://localhost:3000/dashboards || xdg-open http://localhost:3000/dashboards

down:
	docker compose --env-file $(ENV_FILE) down

clean:
	docker compose --env-file $(ENV_FILE) down -v

nuke:
	docker compose --env-file $(ENV_FILE) down -v --rmi all

migrate:
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) alembic upgrade head

seed:
	docker compose --env-file $(ENV_FILE) exec $(SERVICE_API) python -m scripts.seed

logs:
	docker logs -f $(CONTAINER_API_NAME)
