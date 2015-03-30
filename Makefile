all: install test

.PHONY: install test

install-python:
	pip install -r requirements/base.txt

install-test:
	pip install -q -r requirements/test.txt

install: install-python install-test

test:
	./scripts/test.sh

workbench:
	./scripts/workbench.sh
