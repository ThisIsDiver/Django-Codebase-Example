#!/bin/sh

export DJANGOSUPERUSER_USERNAME=admin
export DJANGOSUPERUSER_PASSWORD=securepassword123

python manage.py migrate

python manage.py createsuperuser --noinput || true

exec "$@"
