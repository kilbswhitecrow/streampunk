from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from django.views.generic import DetailView

from progdb.progdb2.models import Person, Item, Room, Tag, KitBundle, KitThing, KitRequest

from progdb.progdb2.forms import ItemForm, PersonForm, TagForm, RoomForm
from progdb.progdb2.forms import KitThingForm, KitBundleForm, KitRequestForm

from progdb.progdb2.views import main_page, list_grids, EditView, NewView, AllView
from progdb.progdb2.views import show_grid, show_slot, add_person_to_item, remove_person_from_item
from progdb.progdb2.views import edit_tags_for_item, edit_tags_for_person
from progdb.progdb2.views import add_tags, fill_slot_unsched, fill_slot_sched, list_checks
from progdb.progdb2.views import show_kitthing, show_kitbundle
from progdb.progdb2.views import add_kitbundle_to_room, add_kitbundle_to_item
from progdb.progdb2.views import add_kitthing_to_room, add_kitthing_to_item
from progdb.progdb2.views import show_room_detail, show_item_detail, show_person_detail, show_tag_detail
from progdb.progdb2.views import show_kitrequest_detail, show_kitbundle_detail, show_kitthing_detail

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'progdb.views.home', name='home'),
    # url(r'^progdb/', include('progdb.foo.urls')),
    url(r'^progdb/main/$', main_page),
    url(r'^progdb/login/$', login, { 'template_name': 'progdb2/login.html' }),
    url(r'^progdb/logout/$', logout),

    url(r'^progdb/grids/$', list_grids),
    url(r'^progdb/people/$', AllView.as_view(model=Person)),
    url(r'^progdb/items/$', AllView.as_view(model=Item)),
    url(r'^progdb/rooms/$', AllView.as_view(model=Room)),
    url(r'^progdb/tags/$', AllView.as_view(model=Tag)),
    url(r'^progdb/kitbundles/$', AllView.as_view(model=KitBundle)),
    url(r'^progdb/kitthings/$', AllView.as_view(model=KitThing)),
    url(r'^progdb/kitrequests/$', AllView.as_view(model=KitRequest)),

    url(r'^progdb/room/(?P<pk>\d+)/$', show_room_detail.as_view()),
    url(r'^progdb/item/(?P<pk>\d+)/$', show_item_detail.as_view()),
    url(r'^progdb/person/(?P<pk>\d+)/$', show_person_detail.as_view()),
    url(r'^progdb/tag/(?P<pk>\d+)/$', show_tag_detail.as_view()),
    url(r'^progdb/kitbundle/(?P<pk>\d+)/$', show_kitbundle_detail.as_view()),
    url(r'^progdb/kitthing/(?P<pk>\d+)/$', show_kitthing_detail.as_view()),
    url(r'^progdb/kitrequest/(?P<pk>\d+)/$', show_kitrequest_detail.as_view()),

    url(r'^progdb/conday/(\d+)/grid/(\d+)/$', show_grid),
    url(r'^progdb/slot/(\d+)/$', show_slot),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/u/$', fill_slot_unsched),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/s/$', fill_slot_sched),

    url(r'^progdb/add_person_to_item/$', add_person_to_item),
    url(r'^progdb/add_person/(?P<p>\d+)/to_item/$', add_person_to_item),
    url(r'^progdb/add_person/(?P<p>\d+)/to_item/(?P<i>\d+)/$', add_person_to_item),
    url(r'^progdb/add_person_to_item/(?P<i>\d+)/$', add_person_to_item),

    url(r'^progdb/add_kitbundle_to_room/$', add_kitbundle_to_room),
    url(r'^progdb/add_kitbundle_to_item/$', add_kitbundle_to_item),
    url(r'^progdb/add_kitthing_to_room/$', add_kitthing_to_room),
    url(r'^progdb/add_kitthing_to_item/$', add_kitthing_to_item),

    url(r'^progdb/remove_person/(?P<p>\d+)/from_item/(?P<i>\d+)/$', remove_person_from_item.as_view()),

    url(r'^progdb/edit_item/(?P<pk>\d+)/$', EditView.as_view(
          model = Item,
          form_class=ItemForm)),
    url(r'^progdb/edit_person/(?P<pk>\d+)/$', EditView.as_view(
          model = Person,
          form_class=PersonForm)),
    url(r'^progdb/edit_tag/(?P<pk>\d+)/$', EditView.as_view(
          model = Tag,
          form_class=TagForm)),
    url(r'^progdb/edit_room/(?P<pk>\d+)/$', EditView.as_view(
          model = Room,
          form_class=RoomForm)),
    url(r'^progdb/edit_kitthing/(?P<pk>\d+)/$', EditView.as_view(
          model = KitThing,
          form_class=KitThingForm)),
    url(r'^progdb/edit_kitbundle/(?P<pk>\d+)/$', EditView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)),
    url(r'^progdb/edit_kitrequest/(?P<pk>\d+)/$', EditView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)),

    url(r'^progdb/new_person/$', NewView.as_view(
          model = Person,
          form_class=PersonForm)),
    url(r'^progdb/new_item/$', NewView.as_view(
          model = Item,
          form_class=ItemForm)),
    url(r'^progdb/new_room/$', NewView.as_view(
          model = Room,
          form_class=RoomForm)),
    url(r'^progdb/new_tag/$', NewView.as_view(
          model = Tag,
          form_class=TagForm)),
    url(r'^progdb/new_kitthing/$', NewView.as_view(
          model = KitThing,
          form_class=KitThingForm)),
    url(r'^progdb/new_kitbundle/$', NewView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)),
    url(r'^progdb/new_kitrequest/$', NewView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)),

    url(r'^progdb/edit_tags_for_item/(\d+)/$', edit_tags_for_item),
    url(r'^progdb/edit_tags_for_person/(\d+)/$', edit_tags_for_person),

    url(r'^progdb/add_tags/$', add_tags),

    url(r'^progdb/checks/$', list_checks),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
