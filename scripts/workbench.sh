#!/usr/bin/env bash

cd `dirname $BASH_SOURCE` && cd ..

export DJANGO_SETTINGS_MODULE="settings.dev"

echo "Updating the database..."
python manage.py syncdb --migrate -v 0

echo "Starting server..."
python manage.py runserver

