#!/bin/sh

mysql -u root -p < progdb.sql
python manage.py syncdb
python manage.py loaddata room person items tags

