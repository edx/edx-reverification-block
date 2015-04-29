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

compile-sass: install-sass
	./node_modules/node-sass/bin/node-sass ./edx_reverification_block/xblock/static/sass/main.scss ./edx_reverification_block/xblock/static/reverification.min.css --output-style compressed

workbench: install-python compile-sass
	./scripts/workbench.sh
