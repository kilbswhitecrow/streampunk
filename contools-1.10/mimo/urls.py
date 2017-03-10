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
  url(r'^settings/mode/$', views.set_mode, name='settings_mode'),
  url(r'^settings/container/$', views.set_container, name='settings_container'),
  url(r'^settings/room/$', views.set_room, name='settings_room'),
  url(r'^settings/kind/$', views.set_kind, name='settings_kind'),
  url(r'^settings/subkind/$', views.set_subkind, name='settings_subkind'),
  url(r'^settings/group/$', views.set_group, name='settings_group'),
  url(r'^settings/supplier/$', views.set_supplier, name='settings_supplier'),
  url(r'^plan/$', views.PlanIndexView.as_view(), name='plan_index'),
  url(r'^plan/(?P<pk>[0-9]+)/$', views.PlanDetailView.as_view(), name='plan_detail'),
  url(r'^mi/$', views.MoveInIndexView.as_view(), name='mi_index'),
  url(r'^mi/(?P<pk>[0-9]+)/$', views.MoveInDetailView.as_view(), name='mi_detail'),
  url(r'^live/$', views.LiveIndexView.as_view(), name='live_index'),
  url(r'^live/(?P<pk>[0-9]+)/$', views.LiveDetailView.as_view(), name='live_detail'),
  url(r'^mo/$', views.MoveOutIndexView.as_view(), name='mo_index'),
  url(r'^mo/(?P<pk>[0-9]+)/$', views.MoveOutDetailView.as_view(), name='mo_detail'),
]
