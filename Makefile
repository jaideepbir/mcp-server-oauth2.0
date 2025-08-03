SHELL := /bin/bash

.PHONY: build up down logs ps

build:
	docker compose -f compose/docker-compose.yml build

up:
	docker compose -f compose/docker-compose.yml up -d

Down:
	docker compose -f compose/docker-compose.yml down

logs:
	docker compose -f compose/docker-compose.yml logs -f --tail=200

ps:
	docker compose -f compose/docker-compose.yml ps
