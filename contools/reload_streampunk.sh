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


echo Enter MySQL root password...
mysql -u root -p < setup_streampunk.sql
python manage.py syncdb --noinput
python manage.py loaddata room person items tags avail kit
user=congod
echo Enter password for superuser $user - suggest 'xxx'
python manage.py createsuperuser --user $user --email steve@whitecrow.demon.co.uk


