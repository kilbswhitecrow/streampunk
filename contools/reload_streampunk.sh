#!/bin/sh

echo Enter MySQL root password...
mysql -u root -p < setup_streampunk.sql
python manage.py syncdb --noinput
python manage.py loaddata room person items tags avail kit
user=congod
echo Enter password for superuser $user - suggest 'xxx'
python manage.py createsuperuser --user $user --email steve@whitecrow.demon.co.uk


