# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012 Stephen Kilbane
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

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.views.generic import DetailView
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings # for dajaxice

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

from streampunk.models import Person, Item, Room, Tag, KitBundle, KitThing, KitRequest, ItemPerson
from streampunk.models import Slot, PersonList, KitRoomAssignment, KitItemAssignment

from streampunk.forms import ItemForm, PersonForm, TagForm, RoomForm, ItemPersonForm
from streampunk.forms import KitThingForm, KitBundleForm, KitRequestForm, PersonListForm
from streampunk.forms import DeleteItemPersonForm, KitRoomAssignmentForm

from streampunk.views import main_page, static_page, list_grids, EditView, NewView, AllView, AfterDeleteView, VisibleView
from streampunk.views import show_grid, show_slot_detail, email_person, emailed_person, emailed_item, email_item_with_personlist, email_personlist
from streampunk.views import edit_tags_for_item, edit_tags_for_person
from streampunk.views import add_tags, fill_slot_unsched, fill_slot_sched, list_checks
from streampunk.views import show_kitthing, show_kitbundle
from streampunk.views import add_kitbundle_to_room, add_kitbundle_to_item
from streampunk.views import delete_kitbundle_from_room, delete_kitbundle_from_item
from streampunk.views import add_kitthing_to_room, add_kitthing_to_item, add_kitrequest_to_item, kit_usage
from streampunk.views import show_room_detail, show_item_detail, show_person_detail, show_tag_detail
from streampunk.views import show_kitrequest_detail, show_kitbundle_detail, show_kitthing_detail, show_itemperson_detail
from streampunk.views import show_kitroomassignment_detail
from streampunk.views import show_kititemassignment_detail
from streampunk.views import show_personlist_detail, show_request, make_personlist, make_con_groups
from streampunk.views import show_profile_detail, edit_user_profile

from streampunk.views import peepsandrooms

from streampunk.tables import OldItemTable, OldPersonTable
from django_tables2 import SingleTableView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'contools.views.home', name='home'),
    # url(r'^contools/', include('contools.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # The next line is for dajaxice
    url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),

    url(r'^streampunk/show_request/$', show_request),
    url(r'^streampunk/main/$', main_page, name='main_page'),
    url(r'^streampunk/about/$', static_page, { 'template': 'streampunk/about.html' }, name='about'),
    url(r'^streampunk/legal/$', static_page, { 'template': 'streampunk/legal.html' }, name='legal'),
    url(r'^streampunk/wibble/$', static_page, { 'template': 'streampunk/wibble.html' }, name='wibble'),
    url(r'^streampunk/peepsandrooms/$', peepsandrooms, name='peepsandrooms'),
    url(r'^streampunk/itemsintable/$', SingleTableView.as_view(model=Item,
                                                               table_class=OldItemTable,
                                                               template_name='streampunk/itemsintable.html') ),
    url(r'^streampunk/peopleintable/$', SingleTableView.as_view(model=Person,
                                                               table_class=OldPersonTable,
                                                               template_name='streampunk/peopleintable.html'), name='peopleintable' ),

    url(r'^help/$', static_page, { 'template': 'help/help.html' }, name='help_intro'),
    url(r'^help/basic_concepts/$', static_page,
        { 'template': 'help/basic_concepts.html' }, name='help_basic_concepts'),
    url(r'^help/main_page/$', static_page,
        { 'template': 'help/main_page.html' }, name='help_main_page'),
    url(r'^help/grids/$', static_page,
        { 'template': 'help/grids.html' }, name='help_grids'),
    url(r'^help/rooms/$', static_page,
        { 'template': 'help/rooms.html' }, name='help_rooms'),
    url(r'^help/people/$', static_page,
        { 'template': 'help/people.html' }, name='help_people'),
    url(r'^help/items/$', static_page,
        { 'template': 'help/items.html' }, name='help_items'),
    url(r'^help/kit/$', static_page,
        { 'template': 'help/kit.html' }, name='help_kit'),
    url(r'^help/tags/$', static_page,
        { 'template': 'help/tags.html' }, name='help_tags'),
    url(r'^help/checks/$', static_page,
        { 'template': 'help/checks.html' }, name='help_checks'),
    url(r'^help/admin/$', static_page,
        { 'template': 'help/admin.html' }, name='help_admin'),
    url(r'^help/users/$', static_page,
        { 'template': 'help/users.html' }, name='help_users'),

    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, kwargs={'next_page':'/streampunk/main/', 'redirect_field_name':'next'}, name='logout'),
    url(r'^accounts/logout_then_login/$', logout_then_login, name='logout_then_login'),
    url(r'^accounts/change_password/$', password_change, name='password_change'),
    url(r'^accounts/password_changed/$', password_change_done, name='password_change_done'),
    url(r'^accounts/password_reset/$', password_reset, name='password_reset'),
    url(r'^accounts/password_reset_done/$', password_reset_done, name='password_reset_done'),
    url(r'^accounts/password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^accounts/password_reset_complete/$', password_reset_complete, name='password_reset_complete'),

    url(r'^accounts/change_profile/$', edit_user_profile, name='editprofile'),
    url(r'^accounts/profile/$', show_profile_detail, name='userprofile'),

    url(r'^streampunk/grids/$', list_grids, name='list_grids'),
    url(r'^streampunk/people/$', AllView.as_view(model=Person,
                                             template_name='streampunk/list_people.html'), name='list_people'),
    url(r'^streampunk/items/$', VisibleView.as_view(model=Item,
                                             template_name='streampunk/list_items.html'), name='list_items'),
    url(r'^streampunk/rooms/$', VisibleView.as_view(model=Room,
                                             template_name='streampunk/list_rooms.html'), name='list_rooms'),
    url(r'^streampunk/tags/$', VisibleView.as_view(model=Tag,
                                             template_name='streampunk/list_tags.html'), name='list_tags'),
    url(r'^streampunk/kitbundles/$', AllView.as_view(model=KitBundle,
                                             template_name='streampunk/kitbundle_list.html',
                                             context_object_name='kitbundles'), name='list_kitbundles'),
    url(r'^streampunk/kitthings/$', AllView.as_view(model=KitThing,
                                             template_name='streampunk/kitthing_list.html',
                                             context_object_name='kitthings'), name='list_kitthings'),
    url(r'^streampunk/kitrequests/$', AllView.as_view(model=KitRequest,
                                             template_name='streampunk/kitrequest_list.html',
                                             context_object_name='kitrequests'), name='list_kitrequests'),
    url(r'^streampunk/itemspeople/$', VisibleView.as_view(model=ItemPerson), name='list_itemspeople'),
    url(r'^streampunk/peoplelists/$', VisibleView.as_view(model=PersonList), name='list_peoplelists'),
    url(r'^streampunk/slots/$', VisibleView.as_view(model=Slot), name='list_slots'),
    url(r'^streampunk/kit_usage/$', kit_usage, name='kit_usage'),

    url(r'^streampunk/room/(?P<pk>\d+)/$', show_room_detail.as_view(), name='show_room_detail'),
    url(r'^streampunk/item/(?P<pk>\d+)/$', show_item_detail.as_view(), name='show_item_detail'),
    url(r'^streampunk/person/(?P<pk>\d+)/$', show_person_detail.as_view(), name='show_person_detail'),
    url(r'^streampunk/tag/(?P<pk>\d+)/$', show_tag_detail.as_view(), name='show_tag_detail'),
    url(r'^streampunk/kitbundle/(?P<pk>\d+)/$', show_kitbundle_detail.as_view(), name='show_kitbundle_detail'),
    url(r'^streampunk/kitthing/(?P<pk>\d+)/$', show_kitthing_detail.as_view(), name='show_kitthing_detail'),
    url(r'^streampunk/kitrequest/(?P<pk>\d+)/$', show_kitrequest_detail.as_view(), name='show_kitrequest_detail'),
    url(r'^streampunk/kitroomassignment/(?P<pk>\d+)/$', show_kitroomassignment_detail.as_view(), name='show_kitroomassignment_detail'),
    url(r'^streampunk/kititemassignment/(?P<pk>\d+)/$', show_kititemassignment_detail.as_view(), name='show_kititemassignment_detail'),
    url(r'^streampunk/itemperson/(?P<pk>\d+)/$', show_itemperson_detail.as_view(), name='show_itemperson_detail'),
    url(r'^streampunk/personlist/(?P<pk>\d+)/$', show_personlist_detail.as_view(), name='show_personlist_detail'),

    url(r'^streampunk/conday/(\d+)/grid/(\d+)/$', show_grid, name='show_grid'),
    url(r'^streampunk/slot/(?P<pk>\d+)/$', show_slot_detail.as_view(), name='show_slot_detail'),
    url(r'^streampunk/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/u/$', fill_slot_unsched, name='fill_slot_unsched'),
    url(r'^streampunk/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/s/$', fill_slot_sched, name='fill_slot_sched'),

    url(r'^streampunk/add_kitbundle_to_room/$', add_kitbundle_to_room, name='add_kitbundle_to_room'),
    url(r'^streampunk/add_kitbundle_to_item/$', add_kitbundle_to_item, name='add_kitbundle_to_item'),
    url(r'^streampunk/add_kitthing_to_room/$', add_kitthing_to_room, name='add_kitthing_to_room'),
    url(r'^streampunk/add_kitthing_to_item/$', add_kitthing_to_item, name='add_kitthing_to_item'),
    url(r'^streampunk/add_kitrequest_to_item/(?P<pk>\d+)/$', add_kitrequest_to_item, name='add_kitrequest_to_item'),

    url(r'^streampunk/delete_kitbundle/(?P<kb>\d+)/from_room/(?P<room>\d+)/$', delete_kitbundle_from_room, name='delete_kitbundle_from_room'),
    url(r'^streampunk/delete_kitbundle/(?P<kb>\d+)/from_item/(?P<item>\d+)/$', delete_kitbundle_from_item, name='delete_kitbundle_from_item'),

    url(r'^streampunk/delete_itemperson/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=ItemPerson)), name='delete_itemperson'),
    url(r'^streampunk/delete_kitroomassignment/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=KitRoomAssignment)), name='delete_kitroomassignment'),
    url(r'^streampunk/delete_kititemassignment/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=KitItemAssignment)), name='delete_kititemassignment'),
    url(r'^streampunk/delete_kitrequest/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=KitRequest)), name='delete_kitrequest'),
    url(r'^streampunk/delete_kitbundle/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=KitBundle)), name='delete_kitbundle'),
    url(r'^streampunk/delete_kitthing/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(AfterDeleteView.as_view(
          model=KitThing)), name='delete_kitthing'),

    url(r'^streampunk/edit_item/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(EditView.as_view(
          model = Item,
          form_class=ItemForm)), name='edit_item'),
    url(r'^streampunk/edit_person/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(EditView.as_view(
          model = Person,
          form_class=PersonForm)), name='edit_person'),
    url(r'^streampunk/edit_tag/(?P<pk>\d+)/$', permission_required('streampunk.edit_tags')(EditView.as_view(
          model = Tag,
          form_class=TagForm)), name='edit_tag'),
    url(r'^streampunk/edit_room/(?P<pk>\d+)/$', permission_required('streampunk.edit_room')(EditView.as_view(
          model = Room,
          form_class=RoomForm)), name='edit_room'),
    url(r'^streampunk/edit_kitthing/(?P<pk>\d+)/$', permission_required('streampunk.edit_kit')(EditView.as_view(
          model = KitThing,
          form_class=KitThingForm)), name='edit_kitthing'),
    url(r'^streampunk/edit_kitbundle/(?P<pk>\d+)/$', permission_required('streampunk.edit_kit')(EditView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)), name='edit_kitbundle'),
    url(r'^streampunk/edit_kitrequest/(?P<pk>\d+)/$', permission_required('streampunk.edit_kit')(EditView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)), name='edit_kitrequest'),
    url(r'^streampunk/edit_kitroomassignment/(?P<pk>\d+)/$', permission_required('streampunk.edit_kit')(EditView.as_view(
          model = KitRoomAssignment,
          form_class=KitRoomAssignmentForm)), name='edit_kitroomassignment'),
    url(r'^streampunk/edit_itemperson/(?P<pk>\d+)/$', permission_required('streampunk.edit_programme')(EditView.as_view(
          model = ItemPerson,
          form_class=ItemPersonForm)), name='edit_itemperson'),
    url(r'^streampunk/edit_personlist/(?P<pk>\d+)/$', permission_required('streampunk.send_item_email')(EditView.as_view(
          model = PersonList,
          form_class=PersonListForm)), name='edit_personlist'),

    url(r'^streampunk/new_person/$', permission_required('streampunk.edit_programme')(NewView.as_view(
          model = Person,
          form_class=PersonForm)), name='new_person'),
    url(r'^streampunk/new_item/$', permission_required('streampunk.edit_programme')(NewView.as_view(
          model = Item,
          form_class=ItemForm)), name='new_item'),
    url(r'^streampunk/new_room/$', permission_required('streampunk.config_db')(NewView.as_view(
          model = Room,
          form_class=RoomForm)), name='new_room'),
    url(r'^streampunk/new_tag/$', permission_required('streampunk.edit_tags')(NewView.as_view(
          model = Tag,
          form_class=TagForm)), name='new_tag'),
    url(r'^streampunk/new_kitthing/$', permission_required('streampunk.edit_kit')(NewView.as_view(
          model = KitThing,
          form_class=KitThingForm)), name='new_kitthing'),
    url(r'^streampunk/new_kitbundle/$', permission_required('streampunk.edit_kit')(NewView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)), name='new_kitbundle'),
    url(r'^streampunk/new_kitrequest/$', permission_required('streampunk.edit_kit')(NewView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)), name='new_kitrequest'),
    url(r'^streampunk/new_itemperson/$', permission_required('streampunk.edit_programme')(NewView.as_view(
          template_name = 'streampunk/edit_itemperson.html',
          model = ItemPerson,
          form_class=ItemPersonForm)), name='new_itemperson'),
    url(r'^streampunk/new_personlist/$', permission_required('streampunk.send_item_email')(NewView.as_view(
          template_name = 'streampunk/edit_personlist.html',
          model = PersonList,
          success_url = '/streampunk/peoplelists/',
          form_class=PersonListForm)), name='new_personlist'),

    url(r'^streampunk/mail_person/(?P<pk>\d+)/$', email_person, name='email_person'),
    url(r'^streampunk/mailed_person/(?P<pk>\d+)/$', emailed_person, name='emailed_person'),
    url(r'^streampunk/mail_item/(?P<ipk>\d+)/with_personlist/(?P<plpk>\d+)/$', email_item_with_personlist, name='mail_item_with_personlist'),
    url(r'^streampunk/mailed_item/(?P<pk>\d+)/$', emailed_item, name='emailed_item'),
    url(r'^streampunk/mail_personlist/(?P<pk>\d+)/$', email_personlist, name='email_personlist'),

    url(r'^streampunk/edit_tags_for_item/(\d+)/$', edit_tags_for_item, name='edit_tags_for_item'),
    url(r'^streampunk/edit_tags_for_person/(\d+)/$', edit_tags_for_person, name='edit_tags_for_person'),

    url(r'^streampunk/make_personlist/$', make_personlist, name='make_personlist'),

    url(r'^streampunk/add_tags/$', add_tags, name='add_tags'),

    url(r'^streampunk/checks/$', list_checks, name='list_checks'),
    url(r'^streampunk/make_con_groups/$', make_con_groups, name='make_con_groups'),
)
