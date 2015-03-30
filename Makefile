all: install test

.PHONY: install test

install-python:
	./scripts/install-python.sh

install-test:
	pip install -q -r requirements/test.txt

install: install-python install-test

test: install-test
	./scripts/test.sh

workbench: install-python
	./scripts/workbench.sh
