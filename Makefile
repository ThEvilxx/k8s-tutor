PYTHON ?= python
IMAGE ?= k8s-tutor:v1

.PHONY: install migrate seed run check test static image
install:
	$(PYTHON) -m pip install -r requirements.txt
migrate:
	$(PYTHON) manage.py migrate
seed:
	$(PYTHON) manage.py seed_demo
run:
	$(PYTHON) manage.py runserver
check:
	$(PYTHON) manage.py check
	$(PYTHON) manage.py makemigrations --check --dry-run
test:
	$(PYTHON) manage.py test
static:
	$(PYTHON) manage.py collectstatic --noinput
image:
	docker build --platform linux/amd64 --provenance=false --sbom=false -t $(IMAGE) .
