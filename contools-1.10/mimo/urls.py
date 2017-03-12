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
  url(r'^plan/add/$', views.add_techitem, name='plan_add'),
  url(r'^plan/(?P<pk>[0-9]+)/$', views.PlanDetailView.as_view(), name='plan_detail'),
  url(r'^plan/(?P<pk>[0-9]+)/edit/$', views.edit_techitem, name='plan_edit'),
  url(r'^plan/(?P<pk>[0-9]+)/delete/$', views.TechItemDeleteView.as_view(), name='techitem_delete'),
  url(r'^plan/(?P<pk>[0-9]+)/dup/$', views.dup_techitem, name='techitem_dup'),
  url(r'^mi/$', views.mi_index, name='mi_index'),
  url(r'^mi/setup/$', views.setup_movein, name='mi_setup'),
  url(r'^mi/(?P<pk>[0-9]+)/$', views.MoveInDetailView.as_view(), name='mi_detail'),
  url(r'^mi/(?P<pk>[0-9]+)/received/$', views.mark_received_movein, name='mi_received'),
  url(r'^mi/(?P<pk>[0-9]+)/notreceived/$', views.mark_not_received_movein, name='mi_not_received'),
  url(r'^mi/(?P<pk>[0-9]+)/reset/$', views.mark_reset_movein, name='mi_reset'),
  url(r'^mi/(?P<pk>[0-9]+)/replace/$', views.rep_movein, name='mi_replace'),
  url(r'^live/$', views.LiveIndexView.as_view(), name='live_index'),
  url(r'^live/(?P<pk>[0-9]+)/$', views.LiveDetailView.as_view(), name='live_detail'),
  url(r'^mo/$', views.MoveOutIndexView.as_view(), name='mo_index'),
  url(r'^mo/(?P<pk>[0-9]+)/$', views.MoveOutDetailView.as_view(), name='mo_detail'),
]
