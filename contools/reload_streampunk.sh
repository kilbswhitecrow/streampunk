#!/bin/sh
# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012 Stephen Kilbane
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

dbtype=`python get_db_type.py`
case "$dbtype" in
  django.db.backends.mysql)
          echo Enter suitable MySQL password...
          mysql -u root -p < setup_streampunk.sql
          ;;
  django.db.backends.sqlite3) 
          dbname=`python get_db_name.py`
          if [ -f $dbname ]
          then rm $dbname
          fi
          ;;
  *)
          echo "I don't recognise this database type. Please reset manually."
          exit 1
          ;;
esac

python manage.py syncdb --noinput
python manage.py loaddata demo_data
user=congod
echo Enter password for superuser $user - suggest 'xxx'
python manage.py createsuperuser --user $user --email steve@whitecrow.demon.co.uk


