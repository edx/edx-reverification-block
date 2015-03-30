#!/usr/bin/env bash

cd `dirname $BASH_SOURCE` && cd ..

export DJANGO_SETTINGS_MODULE="settings.test"
python manage.py test $1
