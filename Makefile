all: install test

.PHONY: install test

install-sass:
	npm install node-sass

install-python:
	./scripts/install-python.sh

install-test:
	pip install -q -r requirements/test.txt

install: install-sass install-python install-test

test: install-test compile-sass
	./scripts/test.sh

test-i18n: install-test
	python manage.py makemessages -l eo

i18n-push: install-python
	./scripts/i18n-push.sh

i18n-pull: install-python
	./scripts/i18n-pull.sh

compile-sass: install-sass
	./scripts/sass.sh

workbench: install-python compile-sass
	./scripts/workbench.sh
