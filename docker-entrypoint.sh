#!/bin/sh

flask db upgrade
echo "test"

exec gunicorn --bind 0.0.0.0:80 "app:create_app()"