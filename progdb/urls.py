from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from progdb.progdb2.views import main_page, list_grids, list_items, list_people, list_rooms, list_tags, show_room, show_tag
from progdb.progdb2.views import show_person, show_item, show_grid, show_slot, add_person_to_item, remove_person_from_item, show_referer
from progdb.progdb2.views import edit_tags_for_item, edit_tags_for_person, edit_item, edit_person, edit_room, edit_tag
from progdb.progdb2.views import add_tags, fill_slot_unsched, fill_slot_sched

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'progdb.views.home', name='home'),
    # url(r'^progdb/', include('progdb.foo.urls')),
    url(r'^progdb/show_referer/$', show_referer),
    url(r'^progdb/main/$', main_page),
    url(r'^progdb/login/$', login, { 'template_name': 'progdb2/login.html' }),
    url(r'^progdb/logout/$', logout),
    url(r'^progdb/list_grids/$', list_grids),
    url(r'^progdb/list_items/$', list_items),
    url(r'^progdb/list_people/$', list_people),
    url(r'^progdb/list_rooms/$', list_rooms),
    url(r'^progdb/list_tags/$', list_tags),
    url(r'^progdb/conday/(\d+)/grid/(\d+)/$', show_grid),
    url(r'^progdb/slot/(\d+)/$', show_slot),
    url(r'^progdb/room/(\d+)/$', show_room),
    url(r'^progdb/item/(\d+)/$', show_item),
    url(r'^progdb/person/(\d+)/$', show_person),
    url(r'^progdb/tag/(\d+)/$', show_tag),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/u/$', fill_slot_unsched),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/s/$', fill_slot_sched),

    url(r'^progdb/add_person_to_item/$', add_person_to_item),
    url(r'^progdb/add_person/(?P<p>\d+)/to_item/$', add_person_to_item),
    url(r'^progdb/add_person/(?P<p>\d+)/to_item/(?P<i>\d+)/$', add_person_to_item),
    url(r'^progdb/add_person_to_item/(?P<i>\d+)/$', add_person_to_item),

    url(r'^progdb/remove_person/(?P<p>\d+)/from_item/(?P<i>\d+)/$', remove_person_from_item),

    url(r'^progdb/edit_item/(\d+)/$', edit_item),
    url(r'^progdb/edit_person/(\d+)/$', edit_person),
    url(r'^progdb/edit_tag/(\d+)/$', edit_tag),
    url(r'^progdb/edit_room/(\d+)/$', edit_room),
    url(r'^progdb/edit_tags_for_item/(\d+)/$', edit_tags_for_item),
    url(r'^progdb/edit_tags_for_person/(\d+)/$', edit_tags_for_person),

    url(r'^progdb/add_tags/$', add_tags),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
