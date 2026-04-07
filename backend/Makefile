VENV=venv
PY=python3
PIP=pip

.PHONY: init install migrate runserver test shell clean

init:
	$(PY) -m venv $(VENV)
	@echo "created venv at $(VENV)"

install: init
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r requirements-dev.txt

migrate:
	. $(VENV)/bin/activate && $(PY) manage.py migrate

runserver:
	. $(VENV)/bin/activate && $(PY) manage.py runserver

test:
	. $(VENV)/bin/activate && pytest -q

shell:
	. $(VENV)/bin/activate && $(PY) manage.py shell

clean:
	rm -rf $(VENV)
