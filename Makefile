ifeq ($(OS),Windows_NT)
	SLEEP := timeout /t 10 /nobreak

else
	SLEEP := sleep 4
endif

COMPOSE := docker compose -f docker-compose.yaml
BACKEND := $(COMPOSE) exec -T backend

start:
	$(COMPOSE) up --build -d  backend db
	$(SLEEP)
	$(BACKEND) alembic upgrade head

rebuild:
	$(COMPOSE) down -v
	$(COMPOSE) up --build -d  backend db
	$(SLEEP)
	$(BACKEND) alembic upgrade head

down:
	$(COMPOSE) down

update-api:
	$(COMPOSE) restart backend

update-db:
	$(BACKEND) alembic upgrade head

new-migr:
	$(BACKEND) alembic revision --autogenerate -m "$(name)"

back-migr:
	$(BACKEND) alembic downgrade -1

see-migr:
	$(BACKEND) alembic current -v

see-db:
	$(COMPOSE) exec db psql -U postgres

see-api:
	$(COMPOSE) logs -f backend --since $(time)

dump:
	$(COMPOSE) exec db sh -c 'pg_dump -h 127.0.0.1 --username=postgress -d database > /dumps/$$(date +'\''%Y-%m-%d_%H-%M-%S'\'').sql'