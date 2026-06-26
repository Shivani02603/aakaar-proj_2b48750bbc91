install:
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	./scripts/dev.sh

build:
	docker-compose build

test:
	pytest
	cd frontend && npm test

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ frontend/node_modules .pytest_cache