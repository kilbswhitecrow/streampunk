# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2017 Stephen Kilbane
# 
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

from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^plan/$', views.plan_index, name='plan_index'),
  url(r'^plan/(?P<pk>[0-9]+)/$', views.plan_detail, name='plan_detail'),
  url(r'^mi/$', views.mi_index, name='mi_index'),
  url(r'^mi/(?P<pk>[0-9]+)/$', views.mi_detail, name='mi_detail'),
  url(r'^live/$', views.live_index, name='live_index'),
  url(r'^live/(?P<pk>[0-9]+)/$', views.live_detail, name='live_detail'),
  url(r'^mo/$', views.mo_index, name='mo_index'),
  url(r'^mo/(?P<pk>[0-9]+)/$', views.mo_detail, name='mo_detail'),
]
