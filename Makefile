ifeq ($(OS),Windows_NT)
	SLEEP := timeout /t 10 /nobreak

else
	SLEEP := sleep 4
endif

COMPOSE := docker compose -f docker-compose.yaml

merge:
	git checkout main
	git pull
	git merge dev
	git push
	git checkout dev

# dev

start:
	$(COMPOSE) up --build -d  backend db
	$(SLEEP)
# 	$(COMPOSE) exec backend python -m alembic upgrade head

rebuild:
	$(COMPOSE) down -v
	$(COMPOSE) up --build -d  backend db
	$(SLEEP)
# 	$(COMPOSE) exec backend python -m alembic upgrade head

down:
	$(COMPOSE) down

update-api:
	$(COMPOSE) exec backend rm -r src
	$(COMPOSE) cp ./src backend:core

update-db:
	$(COMPOSE) exec backend python -m alembic upgrade head

new-migr:
	$(COMPOSE) cp app/src/models app:/src
	$(COMPOSE) exec app python -m alembic revision --autogenerate -m "$(name)"
	$(COMPOSE) cp app:app/migrations/versions app/migrations

see-db:
	$(COMPOSE) exec db psql -U postgres

see-api:
	$(COMPOSE) logs -f backend --since $(time)

dump:
	$(COMPOSE) exec db sh -c 'pg_dump -h 127.0.0.1 --username=postgress -d database > /dumps/$$(date +'\''%Y-%m-%d_%H-%M-%S'\'').sql'