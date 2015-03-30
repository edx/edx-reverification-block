#!/usr/bin/env bash

cd `dirname $BASH_SOURCE` && cd ..

export DJANGO_SETTINGS_MODULE="settings.dev"
python manage.py runserver

