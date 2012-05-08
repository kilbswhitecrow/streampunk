from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.views.generic import DetailView
from django.contrib.auth.decorators import permission_required, login_required

from progdb.progdb2.models import Person, Item, Room, Tag, KitBundle, KitThing, KitRequest, ItemPerson
from progdb.progdb2.models import Slot, PersonList

from progdb.progdb2.forms import ItemForm, PersonForm, TagForm, RoomForm, ItemPersonForm
from progdb.progdb2.forms import KitThingForm, KitBundleForm, KitRequestForm, PersonListForm
from progdb.progdb2.forms import DeleteItemPersonForm

from progdb.progdb2.views import main_page, list_grids, EditView, NewView, AllView, AfterDeleteView, VisibleView
from progdb.progdb2.views import show_grid, show_slot_detail, email_person, emailed_person, emailed_item, email_item_with_personlist, email_personlist
from progdb.progdb2.views import edit_tags_for_item, edit_tags_for_person
from progdb.progdb2.views import add_tags, fill_slot_unsched, fill_slot_sched, list_checks
from progdb.progdb2.views import show_kitthing, show_kitbundle
from progdb.progdb2.views import add_kitbundle_to_room, add_kitbundle_to_item
from progdb.progdb2.views import add_kitthing_to_room, add_kitthing_to_item, add_kitrequest_to_item
from progdb.progdb2.views import show_room_detail, show_item_detail, show_person_detail, show_tag_detail
from progdb.progdb2.views import show_kitrequest_detail, show_kitbundle_detail, show_kitthing_detail, show_itemperson_detail
from progdb.progdb2.views import show_personlist_detail, show_request, make_personlist, make_con_groups
from progdb.progdb2.views import show_profile_detail, edit_user_profile

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'progdb.views.home', name='home'),
    # url(r'^progdb/', include('progdb.foo.urls')),

    url(r'^progdb/show_request/$', show_request),
    url(r'^progdb/main/$', main_page, name='main_page'),

    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, kwargs={'next_page':'/progdb/main/', 'redirect_field_name':'next'}, name='logout'),
    url(r'^accounts/logout_then_login/$', logout_then_login, name='logout_then_login'),
    url(r'^accounts/change_password/$', password_change, name='password_change'),
    url(r'^accounts/password_changed/$', password_change_done, name='password_change_done'),
    url(r'^accounts/password_reset/$', password_reset, name='password_reset'),
    url(r'^accounts/password_reset_done/$', password_reset_done, name='password_reset_done'),
    url(r'^accounts/password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^accounts/password_reset_complete/$', password_reset_complete, name='password_reset_complete'),

    url(r'^accounts/change_profile/$', edit_user_profile, name='editprofile'),
    url(r'^accounts/profile/$', show_profile_detail, name='userprofile'),

    url(r'^progdb/grids/$', list_grids, name='list_grids'),
    url(r'^progdb/people/$', AllView.as_view(model=Person,
                                             template_name='progdb2/list_people.html'), name='list_people'),
    url(r'^progdb/items/$', VisibleView.as_view(model=Item), name='list_items'),
    url(r'^progdb/rooms/$', VisibleView.as_view(model=Room), name='list_rooms'),
    url(r'^progdb/tags/$', VisibleView.as_view(model=Tag), name='list_tags'),
    url(r'^progdb/kitbundles/$', AllView.as_view(model=KitBundle), name='list_kitbundles'),
    url(r'^progdb/kitthings/$', AllView.as_view(model=KitThing), name='list_kitthings'),
    url(r'^progdb/kitrequests/$', AllView.as_view(model=KitRequest), name='list_kitrequests'),
    url(r'^progdb/itemspeople/$', VisibleView.as_view(model=ItemPerson), name='list_itemspeople'),
    url(r'^progdb/peoplelists/$', VisibleView.as_view(model=PersonList), name='list_peoplelists'),
    url(r'^progdb/slots/$', VisibleView.as_view(model=Slot), name='list_slots'),

    url(r'^progdb/room/(?P<pk>\d+)/$', show_room_detail.as_view(), name='show_room_detail'),
    url(r'^progdb/item/(?P<pk>\d+)/$', show_item_detail.as_view(), name='show_item_detail'),
    url(r'^progdb/person/(?P<pk>\d+)/$', show_person_detail.as_view(), name='show_person_detail'),
    url(r'^progdb/tag/(?P<pk>\d+)/$', show_tag_detail.as_view(), name='show_tag_detail'),
    url(r'^progdb/kitbundle/(?P<pk>\d+)/$', show_kitbundle_detail.as_view(), name='show_kitbundle_detail'),
    url(r'^progdb/kitthing/(?P<pk>\d+)/$', show_kitthing_detail.as_view(), name='show_kitthing_detail'),
    url(r'^progdb/kitrequest/(?P<pk>\d+)/$', show_kitrequest_detail.as_view(), name='show_kitrequest_detail'),
    url(r'^progdb/itemperson/(?P<pk>\d+)/$', show_itemperson_detail.as_view(), name='show_itemperson_detail'),
    url(r'^progdb/personlist/(?P<pk>\d+)/$', show_personlist_detail.as_view(), name='show_personlist_detail'),

    url(r'^progdb/conday/(\d+)/grid/(\d+)/$', show_grid, name='show_grid'),
    url(r'^progdb/slot/(?P<pk>\d+)/$', show_slot_detail.as_view(), name='show_slot_detail'),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/u/$', fill_slot_unsched, name='fill_slot_unsched'),
    url(r'^progdb/fill/d/(?P<d>\d+)/g/(?P<g>\d+)/r/(?P<r>\d+)/s/(?P<s>\d+)/s/$', fill_slot_sched, name='fill_slot_sched'),

    url(r'^progdb/add_kitbundle_to_room/$', add_kitbundle_to_room, name='add_kitbundle_to_room'),
    url(r'^progdb/add_kitbundle_to_item/$', add_kitbundle_to_item, name='add_kitbundle_to_item'),
    url(r'^progdb/add_kitthing_to_room/$', add_kitthing_to_room, name='add_kitthing_to_room'),
    url(r'^progdb/add_kitthing_to_item/$', add_kitthing_to_item, name='add_kitthing_to_item'),
    url(r'^progdb/add_kitrequest_to_item/(?P<pk>\d+)/$', add_kitrequest_to_item, name='add_kitrequest_to_item'),

    url(r'^progdb/delete_itemperson/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(AfterDeleteView.as_view(
          model=ItemPerson)), name='delete_itemperson'),

    url(r'^progdb/edit_item/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = Item,
          form_class=ItemForm)), name='edit_item'),
    url(r'^progdb/edit_person/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = Person,
          form_class=PersonForm)), name='edit_person'),
    url(r'^progdb/edit_tag/(?P<pk>\d+)/$', permission_required('progdb2.edit_tags')(EditView.as_view(
          model = Tag,
          form_class=TagForm)), name='edit_tag'),
    url(r'^progdb/edit_room/(?P<pk>\d+)/$', permission_required('progdb2.edit_room')(EditView.as_view(
          model = Room,
          form_class=RoomForm)), name='edit_room'),
    url(r'^progdb/edit_kitthing/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitThing,
          form_class=KitThingForm)), name='edit_kitthing'),
    url(r'^progdb/edit_kitbundle/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)), name='edit_kitbundle'),
    url(r'^progdb/edit_kitrequest/(?P<pk>\d+)/$', permission_required('progdb2.edit_kit')(EditView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)), name='edit_kitrequest'),
    url(r'^progdb/edit_itemperson/(?P<pk>\d+)/$', permission_required('progdb2.edit_programme')(EditView.as_view(
          model = ItemPerson,
          form_class=ItemPersonForm)), name='edit_itemperson'),
    url(r'^progdb/edit_personlist/(?P<pk>\d+)/$', permission_required('progdb2.send_item_email')(EditView.as_view(
          model = PersonList,
          form_class=PersonListForm)), name='edit_personlist'),

    url(r'^progdb/new_person/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          model = Person,
          form_class=PersonForm)), name='new_person'),
    url(r'^progdb/new_item/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          model = Item,
          form_class=ItemForm)), name='new_item'),
    url(r'^progdb/new_room/$', permission_required('progdb2.config_db')(NewView.as_view(
          model = Room,
          form_class=RoomForm)), name='new_room'),
    url(r'^progdb/new_tag/$', permission_required('progdb2.edit_tags')(NewView.as_view(
          model = Tag,
          form_class=TagForm)), name='new_tag'),
    url(r'^progdb/new_kitthing/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitThing,
          form_class=KitThingForm)), name='new_kitthing'),
    url(r'^progdb/new_kitbundle/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitBundle,
          form_class=KitBundleForm)), name='new_kitbundle'),
    url(r'^progdb/new_kitrequest/$', permission_required('progdb2.edit_kit')(NewView.as_view(
          model = KitRequest,
          form_class=KitRequestForm)), name='new_kitrequest'),
    url(r'^progdb/new_itemperson/$', permission_required('progdb2.edit_programme')(NewView.as_view(
          template_name = 'progdb2/edit_itemperson.html',
          model = ItemPerson,
          form_class=ItemPersonForm)), name='new_itemperson'),
    url(r'^progdb/new_personlist/$', permission_required('progdb2.send_item_email')(NewView.as_view(
          template_name = 'progdb2/edit_personlist.html',
          model = PersonList,
          success_url = '/progdb/peoplelists/',
          form_class=PersonListForm)), name='new_personlist'),

    url(r'^progdb/mail_person/(?P<pk>\d+)/$', email_person, name='email_person'),
    url(r'^progdb/mailed_person/(?P<pk>\d+)/$', emailed_person, name='emailed_person'),
    url(r'^progdb/mail_item/(?P<ipk>\d+)/with_personlist/(?P<plpk>\d+)/$', email_item_with_personlist, name='mail_item_with_personlist'),
    url(r'^progdb/mailed_item/(?P<pk>\d+)/$', emailed_item, name='emailed_item'),
    url(r'^progdb/mail_personlist/(?P<pk>\d+)/$', email_personlist, name='email_personlist'),

    url(r'^progdb/edit_tags_for_item/(\d+)/$', edit_tags_for_item, name='edit_tags_for_item'),
    url(r'^progdb/edit_tags_for_person/(\d+)/$', edit_tags_for_person, name='edit_tags_for_person'),

    url(r'^progdb/make_personlist/$', make_personlist, name='make_personlist'),

    url(r'^progdb/add_tags/$', add_tags, name='add_tags'),

    url(r'^progdb/checks/$', list_checks, name='list_checks'),
    url(r'^progdb/make_con_groups/$', make_con_groups, name='make_con_groups'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name='admin'),
)
