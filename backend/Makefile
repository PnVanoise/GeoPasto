VENV=venv
PY=python3
PIP=pip

.PHONY: init install migrate runserver test shell clean secret-key \
        collectstatic import-groups crontab-add createsuperuser

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

collectstatic:
	. $(VENV)/bin/activate && $(PY) manage.py collectstatic --noinput

import-groups:
	. $(VENV)/bin/activate && $(PY) manage.py import_groups groups_export.json

crontab-add:
	. $(VENV)/bin/activate && $(PY) manage.py crontab add

createsuperuser:
	. $(VENV)/bin/activate && $(PY) manage.py createsuperuser

clean:
	rm -rf $(VENV)

secret-key:
	@. $(VENV)/bin/activate && $(PY) -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
