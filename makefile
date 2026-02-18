.PHONY: help install migrate test run docker-up docker-down

help:
	@echo "Renais Gin Commands"
	@echo "make install    - Install dependencies"
	@echo "make migrate    - Run migrations"
	@echo "make test       - Run tests"
	@echo "make run        - Run development server"
	@echo "make docker-up  - Start Docker containers"

install:
	pip install -r requirements.txt

migrate:
	cd renais_gin && python manage.py migrate

test:
	cd renais_gin && python manage.py test

run:
	cd renais_gin && python manage.py runserver

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down