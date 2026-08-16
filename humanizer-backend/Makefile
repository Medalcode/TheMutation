.PHONY: venv install run test docker-build

venv:
	python -m venv .venv

install: venv
	. .venv/bin/activate && pip install -e ".[dev]"

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	. .venv/bin/activate && pytest -q

docker-build:
	docker build -t humanizer-backend .
