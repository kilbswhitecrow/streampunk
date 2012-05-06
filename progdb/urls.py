from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from django.views.generic import DetailView
from django.contrib.auth.decorators import permission_required

from progdb.progdb2.models import Person, Item, Room, Tag, KitBundle, KitThing, KitRequest, ItemPerson
from progdb.progdb2.models import Slot, PersonList

from progdb.progdb2.forms import ItemForm, PersonForm, TagForm, RoomForm, ItemPersonForm
from progdb.progdb2.forms import KitThingForm, KitBundleForm, KitRequestForm, PersonListForm
from progdb.progdb2.forms import DeleteItemPersonForm

from progdb.progdb2.views import main_page, list_grids, EditView, NewView, AllView, AfterDeleteView, VisibleView
from progdb.progdb2.views import show_grid, show_slot_detail, email_person, emailed_person, email_item, emailed_item, email_item_with_personlist
from progdb.progdb2.views import edit_tags_for_item, edit_tags_for_person
from progdb.progdb2.views import add_tags, fill_slot_unsched, fill_slot_sched, list_checks
from progdb.progdb2.views import show_kitthing, show_kitbundle
from progdb.progdb2.views import add_kitbundle_to_room, add_kitbundle_to_item
from progdb.progdb2.views import add_kitthing_to_room, add_kitthing_to_item
from progdb.progdb2.views import show_room_detail, show_item_detail, show_person_detail, show_tag_detail
from progdb.progdb2.views import show_kitrequest_detail, show_kitbundle_detail, show_kitthing_detail, show_itemperson_detail
from progdb.progdb2.views import show_personlist_detail, show_request, make_personlist, make_con_groups

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'progdb.views.home', name='home'),
    # url(r'^progdb/', include('progdb.foo.urls')),
    url(r'^progdb/show_request/$', show_request),
    url(r'^progdb/main/$', main_page),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout),

    url(r'^progdb/grids/$', list_grids),
    url(r'^progdb/people/$', AllView.as_view(model=Person,
                                             template_name='progdb2/list_people.html')),
    url(r'^progdb/items/$', VisibleView.as_view(model=Item)),
    url(r'^progdb/rooms/$', VisibleView.as_view(model=Room)),
    url(r'^progdb/tags/$', VisibleView.as_view(model=Tag)),
    url(r'^progdb/kitbundles/$', AllView.as_view(model=KitBundle)),
    url(r'^progdb/kitthings/$', AllView.as_view(model=KitThing)),
    url(r'^progdb/kitrequests/$', AllView.as_view(model=KitRequest)),
    url(r'^progdb/itemspeople/$', VisibleView.as_view(model=ItemPerson)),
    url(r'^progdb/peoplelists/$', VisibleView.as_view(model=PersonList)),
    url(r'^progdb/slots/$', VisibleView.as_view(model=Slot)),

    url(r'^progdb/room/(?P<pk>\d+)/$', show_room_detail.as_view()),
    url(r'^progdb/item/(?P<pk>\d+)/$', show_item_detail.as_view(), name='show_item_detail'),
    url(r'^progdb/person/(?P<pk>\d+)/$', show_person_detail.as_view(), name='show_person_detail'),
    url(r'^progdb/tag/(?P<pk>\d+)/$', show_tag_detail.as_view()),
    url(r'^progdb/kitbundle/(?P<pk>\d+)/$', show_kitbundle_detail.as_view()),
    url(r'^progdb/kitthing/(?P<pk>\d+)/$', show_kitthing_detail.as_view()),
    url(r'^progdb/kitrequest/(?P<pk>\d+)/$', show_kitrequest_detail.as_view()),
    url(r'^progdb/itemperson/(?P<pk>\d+)/$', show_itemperson_detail.as_view()),
    url(r'^progdb/personlist/(?P<pk>\d+)/$', show_personlist_detail.as_view()),

    url(r'^progdb/conday/(\d+)/grid/(\d+)/$', show_grid),
    url(r'^progdb/slot/(?P<pk>\d+)/$', show_slot_detail.as_view()),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/u/$', fill_slot_unsched),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/s/$', fill_slot_sched),

    url(r'^progdb/add_kitbundle_to_room/$', add_kitbundle_to_room),
    url(r'^progdb/add_kitbundle_to_item/$', add_kitbundle_to_item),
    url(r'^progdb/add_kitthing_to_room/$', add_kitthing_to_room),
    url(r'^progdb/add_kitthing_to_item/$', add_kitthing_to_item),

    url(r'^progdb/delete_itemperson/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(AfterDeleteView.as_view(
          model=ItemPerson))),

    url(r'^progdb/edit_item/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = Item,
          form_class=ItemForm))),
    url(r'^progdb/edit_person/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = Person,
          form_class=PersonForm))),
    url(r'^progdb/edit_tag/(?P<pk>\d+)/$', permission_required('progdb2.edit_tags')(EditView.as_view(
          model = Tag,
          form_class=TagForm))),
    url(r'^progdb/edit_room/(?P<pk>\d+)/$', permission_required('progdb2.edit_room')(EditView.as_view(
          model = Room,
          form_class=RoomForm))),
    url(r'^progdb/edit_kitthing/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitThing,
          form_class=KitThingForm))),
    url(r'^progdb/edit_kitbundle/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitBundle,
          form_class=KitBundleForm))),
    url(r'^progdb/edit_kitrequest/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitRequest,
          form_class=KitRequestForm))),
    url(r'^progdb/edit_itemperson/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = ItemPerson,
          form_class=ItemPersonForm))),
    url(r'^progdb/edit_personlist/(?P<pk>\d+)/$', permission_required('progdb2.send_item_email')(EditView.as_view(
          model = PersonList,
          form_class=PersonListForm))),

    url(r'^progdb/new_person/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          model = Person,
          form_class=PersonForm))),
    url(r'^progdb/new_item/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          model = Item,
          form_class=ItemForm))),
    url(r'^progdb/new_room/$', permission_required('progdb2.config_db')(NewView.as_view(
          model = Room,
          form_class=RoomForm))),
    url(r'^progdb/new_tag/$', permission_required('progdb2.edit_tags')(NewView.as_view(
          model = Tag,
          form_class=TagForm))),
    url(r'^progdb/new_kitthing/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitThing,
          form_class=KitThingForm))),
    url(r'^progdb/new_kitbundle/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitBundle,
          form_class=KitBundleForm))),
    url(r'^progdb/new_kitrequest/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitRequest,
          form_class=KitRequestForm))),
    url(r'^progdb/new_itemperson/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          template_name = 'progdb2/edit_itemperson.html',
          model = ItemPerson,
          form_class=ItemPersonForm))),
    url(r'^progdb/new_personlist/$', permission_required('progdb2.send_item_email')(NewView.as_view(
          template_name = 'progdb2/edit_personlist.html',
          model = PersonList,
          success_url = '/progdb/peoplelists/',
          form_class=PersonListForm)), name='add_personlist'),

    url(r'^progdb/mail_person/(?P<pk>\d+)/$', email_person),
    url(r'^progdb/mailed_person/(?P<pk>\d+)/$', emailed_person),
    url(r'^progdb/mail_item/(?P<pk>\d+)/$', email_item),
    url(r'^progdb/mail_item/(?P<ipk>\d+)/with_personlist/(?P<plpk>\d+)/$', email_item_with_personlist, name='mail_item_with_personlist'),
    url(r'^progdb/mailed_item/(?P<pk>\d+)/$', emailed_item),

    url(r'^progdb/edit_tags_for_item/(\d+)/$', edit_tags_for_item),
    url(r'^progdb/edit_tags_for_person/(\d+)/$', edit_tags_for_person),

    url(r'^progdb/make_personlist/$', make_personlist),

    url(r'^progdb/add_tags/$', add_tags),

    url(r'^progdb/checks/$', list_checks),
    url(r'^progdb/make_con_groups/$', make_con_groups),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
