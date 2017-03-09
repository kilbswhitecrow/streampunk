# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2017 Stephen Kilbane
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
from django.contrib import admin

from .models import ContainerType, TechKind, TechSubkind, TechGroup, Supplier

admin.site.register(ContainerType)
admin.site.register(TechKind)
admin.site.register(TechSubkind)
admin.site.register(TechGroup)
admin.site.register(Supplier)
