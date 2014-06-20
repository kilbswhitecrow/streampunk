# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012-2014 Stephen Kilbane
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

from datetime import datetime, date

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.views.generic import DeleteView, DetailView, UpdateView, CreateView, ListView
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Count, Sum

from django.shortcuts import render
from django_tables2 import RequestConfig

from .tables import ItemTable, PersonTable, RoomTable, ItemKindTable, RoomCapacityTable
from .tables import TagTable, KitThingTable, GridTable, GenderTable
from .tables import KitRequestTable, SlotTable, ConInfoTable
from .tables import KitRoomAssignmentTable
from .tables import KitItemAssignmentTable
from .tables import ItemPersonTable, KitBundleTable

from .models import Item, Person, Room, Tag, ItemPerson, Grid, Slot, ConDay, ConInfoString, Check
from .models import KitThing, KitBundle, KitItemAssignment, KitRoomAssignment, KitRequest, PersonList
from .models import UserProfile, ItemKind, RoomCapacity, Gender, ConInfoBool, ConInfoInt, KitSatisfaction
from .forms import KitThingForm, KitBundleForm, KitRequestForm
from .forms import ItemPersonForm, ItemTagForm, PersonTagForm, ItemForm, PersonForm
from .forms import TagForm, RoomForm, CheckModelFormSet
from .forms import AddMultipleTagsForm, FillSlotUnschedForm, FillSlotSchedForm
from .forms import AddBundleToRoomForm, AddBundleToItemForm
from .forms import AddThingToRoomForm, AddThingToItemForm
from .forms import EmailForm, PersonListForm, UserProfileForm, UserProfileFullForm
from .auth import add_con_groups
from .tabler import Rower, Tabler, make_tabler

# Some diagnostic code for debugging.
# def show_request(request):
#   if request.method == 'GET':
#     d = request.GET.copy()
#   else:
#     d = request.POST.copy()
#   for t in d.lists():
#     k, l = t
#     for v in l:
#       print u"Got '%s' = '%s'\n" % (k, v)
#   return render_to_response('streampunk/show_request.html',
#                             locals(),
#                             context_instance=RequestContext(request))

def get_initial_data_from_request(request, models):
  """
  models is a dictionary. We expect the URL to possibly contain a ?foo=N parameter.
  The dictionary should contain  key foo, with the corresponding value being the model class.
  We fetch object N of that model, and return it as the value of a new dictionary, using the
  same key. This becomes the initial data for the form.
  """
  data = { }
  for k in request.GET:
    if k in models:
      id = int(request.GET[k])
      m = models[k]
      data = { k: m.objects.get(id = id) }
  return data

class NewView(CreateView):
  template_name = 'streampunk/editform.html'

  def get_context_data(self, **kwargs):
    context = super(CreateView, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context

  def get_initial(self):
    models = { 'item': Item, 'person': Person }
    initial = super(NewView, self).get_initial()
    for k in self.request.GET:
      if k in models:
        id = int(self.request.GET[k])
        m = models[k]
        initial[k] = m.objects.get(id = id)
    return initial

  def get_success_url(self):
    df = super(NewView, self).get_success_url()
    subs = [ ('submit0', 'after0'), ('submit1', 'after1') ]
    for (s, a) in subs:
      if self.request.POST.has_key(s) and self.request.POST.has_key(a):
        attr = self.request.POST.get(a, 'self')
        return getattr(self.object, attr).get_absolute_url()
    return df

class EditView(UpdateView):
  template_name = 'streampunk/editform.html'

  def get_context_data(self, **kwargs):
    context = super(EditView, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context



class AllView(ListView):
  template_name = 'streampunk/object_list.html'

  def get_context_data(self, **kwargs):
    context = super(AllView, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['verbose_name'] = self.model._meta.verbose_name
    context['verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['new_url'] = reverse('new_%s' % ( self.model.__name__.lower() ))
    return context

class VisibleView(AllView):
  def get_queryset(self):
    if self.request.user.has_perm('streampunk.read_private'):
      return self.model.objects.all()
    else:
      return self.model.objects.filter(visible = True)

class AfterDeleteView(DeleteView):
  def get_context_data(self, **kwargs):
    context = super(AfterDeleteView, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context

  def get_success_url(self):
    if self.request.POST.has_key('after'):
      return self.request.POST.get('after')
    else:
      return '/streampunk/main/'

def static_page(request, template):
  return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def edit_user_profile(request):
  userprofile = request.user.userprofile
  if request.method == 'POST':
    if request.user.has_perm('streampunk.read_private'):
      form = UserProfileFullForm(request.POST, instance=userprofile)
    else:
      form = UserProfileForm(request.POST, instance=userprofile)
    if form.is_valid():
      userprofile.save()
      return HttpResponseRedirect(reverse('userprofile'))
  else:
    initial_data = { 'show_shortname': userprofile.show_shortname,
                     'show_tags': userprofile.show_tags,
                     'show_people': userprofile.show_people,
                     'name_order': userprofile.name_order }
    if request.user.has_perm('streampunk.read_private'):
      initial_data['person'] = userprofile.person
      form = UserProfileFullForm(instance=userprofile, initial=initial_data)
    else:
      form = UserProfileForm(instance=userprofile, initial=initial_data)
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))


@login_required
def show_profile_detail(request):
  userprofile = request.user.userprofile
  return render_to_response('streampunk/show_userprofile.html',
                            locals(),
                            context_instance=RequestContext(request))




def main_page(request):
  num_people = Person.objects.count()
  num_items = Item.scheduled.count()
  if num_items > 0:
    # e.g. {'num_people__sum': 5, 'budget__sum': 0}
    totals = Item.scheduled.annotate(num_people=Count('people')).aggregate(Sum('num_people'), Sum('budget'))
    # {'length__length__sum': 870}
    mins_scheduled = Item.scheduled.aggregate(Sum('length__length'))
    # [ { 'kind__name': 'Panel', 'kind__count': N }, { 'kind__name': 'Talk', 'kind__count': Y } ]
    num_panellists = totals['num_people__sum']
    budget = totals['budget__sum']
    hours_scheduled = mins_scheduled['length__length__sum'] / 60
  else:
    num_panellists = 0
    budget = 0
    hours_scheduled = 0

  item_kinds = Item.objects.values('kind__name').annotate(Count('kind')).order_by()
  kind_table = make_tabler(ItemKind, ItemKindTable, request=request, qs=item_kinds, prefix='ikc-', empty='No items yet')

  genders = ItemPerson.objects.values('person__gender__name').annotate(Count('person__gender')).order_by()
  gender_table = make_tabler(Gender, GenderTable, request=request, qs=genders, prefix='gc-', empty='Nobody on items yet')

  con_name = ConInfoString.objects.con_name()

  con_info = ConInfoTable(list(ConInfoBool.objects.all()) +
                          list(ConInfoInt.objects.all()) +
                          list(ConInfoString.objects.all()), prefix='ci-')
  return render_to_response('streampunk/main_page.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_grids(request):
  gtable = make_tabler(Grid, GridTable, request=request,
                       qs=Grid.objects.all(), prefix='g-', empty='No grids')
  return render_to_response('streampunk/list_grids.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_room_detail(DetailView):
  context_object_name='room'
  model = Room
  template_name = 'streampunk/show_room.html'

  def get_context_data(self, **kwargs):
    context = super(show_room_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['room_items'] = self.object.item_set.all()
    context['ritable'] = make_tabler(Item, ItemTable, request=self.request,
                                     qs=context['room_items'], prefix='ri-', empty='No items in this room',
                                     extra_exclude=['room', 'edit', 'remove'])
    context['avail'] = self.object.availability.all()
    context['atable'] = make_tabler(Slot, SlotTable, request=self.request,
                                      qs=context['avail'], prefix='a-', empty='No availability defined')
    context['always_available'] = self.object.always_available()
    context['never_available'] = self.object.never_available()
    context['kitrooms'] = KitRoomAssignment.objects.filter(room=self.object)
    context['kratable'] = make_tabler(KitRoomAssignment, KitRoomAssignmentTable, request=self.request,
                                      qs=context['kitrooms'], prefix='kra-', empty='No kit assigned',
                                      extra_exclude=['item', 'day', 'time'])
    context['rctable'] = make_tabler(RoomCapacity, RoomCapacityTable, request=self.request,
                                     qs=context['room'].capacities.all(), prefix='rc-', empty='No capacities defined')
    return context

def show_grid(request, gr):
  gid = int(gr)
  grid = Grid.objects.get(id = gid)
  slots = grid.slots.all()
  if request.user.has_perm('streampunk.read_private'):
    rooms = Room.objects.all();
  else:
    rooms = Room.objects.filter(visible=True);
      
  return render_to_response('streampunk/show_grid.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_slot_detail(DetailView):
  context_object_name = 'slot'
  model = Slot
  template_name = 'streampunk/show_slot.html'

  def get_context_data(self, **kwargs):
    context = super(show_slot_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['items'] = self.object.items()
    context['itable'] = make_tabler(Item, ItemTable, request=self.request,
                                     qs=context['items'], prefix='it-', empty='No items',
                                     extra_exclude=['edit', 'remove', 'start'])
    context['items_starting'] = self.object.items_starting()
    context['itable_starting'] = make_tabler(Item, ItemTable, request=self.request,
                                     qs=context['items_starting'], prefix='its-', empty='No items',
                                     extra_exclude=['edit', 'remove', 'start'])
    return context

class show_item_detail(DetailView):
  context_object_name = 'item'
  model = Item
  template_name = 'streampunk/show_item.html'

  def get_context_data(self, **kwargs):
    empty= 'Nobody on this item yet'
    context = super(show_item_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    if self.request.user.has_perm('streampunk.read_private'):
      qs = ItemPerson.objects.filter(item=self.object)
      context['item_people'] = qs
      tagqs = self.object.tags.all()
      ip_exclude = ['item']
    else:
      qs = ItemPerson.objects.filter(item=self.object, visible=True)
      context['item_people'] = qs
      tagqs = self.object.tags.filter(visible=True)
      ip_exclude = ['item', 'person']
    if self.request.user.has_perm('streampunk.edit_programme'):
      krexclude = []
    else:
      krexclude = ['edit', 'remove']
    context['item_people_table'] = make_tabler(ItemPerson, ItemPersonTable, request=self.request, qs=qs,
                                               prefix='ipt-', empty=empty, extra_exclude=ip_exclude)
    context['tagtable'] = make_tabler(Tag, TagTable, request=self.request, qs=tagqs, prefix='tag-', empty='No tags',
                                      extra_exclude=['description', 'visible', 'edit', 'remove'])
    context['kitrequests'] = self.object.kitRequests.all()
    context['krtable'] = make_tabler(KitRequest, KitRequestTable, request=self.request, qs=context['kitrequests'],
                                     prefix='kr-', empty='No kit requests yet',
                                     extra_exclude=['item', 'room', 'day', 'start', 'status', 'notes', 'setup'] + krexclude)
    context['kititems'] = KitItemAssignment.objects.filter(item=self.object)
    context['kiatable'] = make_tabler(KitItemAssignment, KitItemAssignmentTable, request=self.request,
                                      qs=context['kititems'], prefix='kia-', empty='No kit assigned',
                                      extra_exclude=['item', 'room', 'day', 'time'])
    context['missing_things'] = KitSatisfaction(self.object).missing_things()
    return context

class show_person_detail(DetailView):
  context_object_name = 'person'
  model = Person
  template_name = 'streampunk/show_person.html'

  def get_context_data(self, **kwargs):
    empty= 'Not on any items yet'
    context = super(show_person_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    if self.request.user.has_perm('streampunk.read_private'):
      context['person_name'] = "%s" % self.object
      tagqs = self.object.tags.all()
      qs = ItemPerson.objects.filter(person=self.object)
      context['person_items'] = qs
    else:
      context['person_name'] = "%s" % self.object.as_badge()
      tagqs = self.object.tags.filter(visible=True)
      qs = ItemPerson.objects.filter(person=self.object, visible=True)
      context['person_items'] = qs
    context['person_items_table'] = make_tabler(ItemPerson, ItemPersonTable, request=self.request, qs=qs,
                                                prefix='pit-', empty=empty, extra_exclude=['person', 'select'])
    context['tagtable'] = make_tabler(Tag, TagTable, request=self.request, qs=tagqs, prefix='tag-', empty='No tags',
                                      extra_exclude=['description', 'visible', 'edit', 'remove'])
    context['avail'] = self.object.availability.all()
    context['atable'] = make_tabler(Slot, SlotTable, request=self.request,
                                      qs=context['avail'], prefix='a-', empty='No availability defined')
    context['always_available'] = self.object.always_available()
    context['never_available'] = self.object.never_available()
    return context

class show_tag_detail(DetailView):
  context_object_name = 'tag'
  model = Tag
  template_name = 'streampunk/show_tag.html'

  def get_context_data(self, **kwargs):
    context = super(show_tag_detail, self).get_context_data(**kwargs)
    # These tables' edit/remove links apply to the person/item, not to
    # the association with the tag, so never show them in this view -
    # otherwise, users will delete people/items thinking they're just
    # removing a tag.
    extra_exclude = [ 'edit', 'remove' ]
    context['request'] = self.request
    context['ittable'] = make_tabler(Item, ItemTable, request=self.request,
                                     qs=self.object.item_set.all(), prefix='it-', empty='No items',
                                     extra_exclude=extra_exclude)
    context['pttable'] = make_tabler(Person, PersonTable, request=self.request,
                                     qs=self.object.person_set.all(), prefix='pt-', empty='No people',
                                     extra_exclude=extra_exclude)
    return context


class show_kitthing_detail(DetailView):
  context_object_name = 'kitthing'
  model = KitThing
  template_name = 'streampunk/show_kitthing.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitthing_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['kitbundles'] = self.object.kitbundle_set.all()
    context['kbtable'] = make_tabler(KitBundle, KitBundleTable, request=self.request,
                                     qs=context['kitbundles'], prefix='kb-', empty='Not part of any bundle')
    context['kititems'] = KitItemAssignment.objects.filter(thing = self.object)
    context['kiatable'] = make_tabler(KitItemAssignment, KitItemAssignmentTable, request=self.request,
                                      qs=context['kititems'], prefix='kia-', empty='Not assigned to items',
                                      extra_exclude=['thing'])
    context['kitrooms'] = KitRoomAssignment.objects.filter(thing = self.object)
    context['kratable'] = make_tabler(KitRoomAssignment, KitRoomAssignmentTable, request=self.request,
                                      qs=context['kitrooms'], prefix='kra-', empty='Not assigned to rooms',
                                      extra_exclude=['thing'])
    context['avail'] = self.object.availability.all()
    context['atable'] = make_tabler(Slot, SlotTable, request=self.request,
                                      qs=context['avail'], prefix='a-', empty='No availability defined')
    context['always_available'] = self.object.always_available()
    context['never_available'] = self.object.never_available()
    return context


class show_kitbundle_detail(DetailView):
  context_object_name = 'kitbundle'
  model = KitBundle
  template_name = 'streampunk/show_kitbundle.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitbundle_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['kitthings'] = self.object.things.all()
    context['kttable'] = make_tabler(KitThing, KitThingTable, request=self.request,
                                     qs=context['kitthings'], prefix='kt-', empty='No kit things')
    context['kititems'] = KitItemAssignment.objects.filter(bundle = self.object)
    context['kiatable'] = make_tabler(KitItemAssignment, KitItemAssignmentTable, request=self.request,
                                      qs=context['kititems'], prefix='kia-', empty='Not assigned to items',
                                      extra_exclude=['bundle'])
    context['kitrooms'] = KitRoomAssignment.objects.filter(bundle = self.object)
    context['kratable'] = make_tabler(KitRoomAssignment, KitRoomAssignmentTable, request=self.request,
                                      qs=context['kitrooms'], prefix='kra-', empty='Not assigned to rooms',
                                      extra_exclude=['thing', 'bundle'])
    return context

class show_kitrequest_detail(DetailView):
  context_object_name = 'kitrequest'
  model = KitRequest
  template_name = 'streampunk/show_kitrequest.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitrequest_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['krtable'] = make_tabler(KitRequest, KitRequestTable, request=self.request,
                                     qs=[ context['kitrequest'] ], prefix='kr-', empty='No kit requests',
                                     extra_exclude=['item', 'room', 'day', 'start', 'sat'])
    context['itable'] = make_tabler(KitRequest, KitRequestTable, request=self.request,
                                    qs=[ context['kitrequest'] ], prefix='ki-', empty='No kit requests',
                                    extra_exclude=['name', 'kind', 'count', 'status', 'setup', 'notes'])
    return context

class show_kitroomassignment_detail(DetailView):
  context_object_name = 'kitroomassignment'
  model = KitRoomAssignment
  template_name = 'streampunk/show_kitroomassignment.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitroomassignment_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context

class show_kititemassignment_detail(DetailView):
  context_object_name = 'kititemassignment'
  model = KitItemAssignment
  template_name = 'streampunk/show_kititemassignment.html'

  def get_context_data(self, **kwargs):
    context = super(show_kititemassignment_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context


class show_itemperson_detail(DetailView):
  context_object_name = 'itemperson'
  model = ItemPerson
  template_name = 'streampunk/show_itemperson.html'

  def get_context_data(self, **kwargs):
    context = super(show_itemperson_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context


class show_personlist_detail(DetailView):
  context_object_name = 'personlist'
  model = PersonList
  template_name = 'streampunk/show_personlist.html'

  def get_context_data(self, **kwargs):
    context = super(show_personlist_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    return context



def is_from_item(request):
  referer = request.META['HTTP_REFERER']
  return referer.find('/item/') >= 0

def is_from_person(request):
  referer = request.META['HTTP_REFERER']
  return referer.find('/person/') >= 0

def add_person_to_item(request, p=None, i=None):
  if request.method == 'POST':
    form = ItemPersonForm(request.POST)
    if form.is_valid():
      # Do stuff here
      item = form.cleaned_data['item']
      person = form.cleaned_data['person']
      role = form.cleaned_data['role']
      status = form.cleaned_data['status']
      vis = form.cleaned_data['visible']
      distEmail = form.cleaned_data['distEmail']
      itemPerson = ItemPerson(item=item, person=person, role=role, status=status, visible=vis, distEmail=distEmail)
      itemPerson.save()
      if form.cleaned_data['fromPerson']:
        return HttpResponseRedirect(reverse('show_person_detail', args=(int(person.id),)))
      else:
        return HttpResponseRedirect(reverse('show_item_detail', args=(int(item.id),)))
  else:
    form = ItemPersonForm( initial = { 'item' : i, 'person' : p, 'fromPerson' : is_from_person(request) })
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def mkemail(request, dirvars, subject, person):
  context = RequestContext(request)
  txt = render_to_string('streampunk/email.txt', dirvars, context_instance=context)
  msg = EmailMultiAlternatives(subject, txt, request.user.email, [ person.email ] )
  html = render_to_string('streampunk/email.html', dirvars, context_instance=context)
  msg.attach_alternative(html, "text/html")
  return msg

@permission_required('streampunk.send_direct_email')
def email_person(request, pk):
  if request.method == 'POST':
    form = EmailForm(request.POST)
    if form.is_valid():
      pid = int(pk)
      person = Person.objects.get(id = pid)
      if person.email:
        con_name = ConInfoString.objects.con_name()
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        incItems = form.cleaned_data['includeItems']
        incContact = form.cleaned_data['includeContact']
        incAvail = form.cleaned_data['includeAvail']
        if incItems:
          itemspeople = ItemPerson.objects.filter(person = person)
        if incAvail:
          avail = person.availability.all()
          noAvailMsg = u"We have no information about your availablity over the convention."
        msg = mkemail(request, locals(), subject, person)
        msg.send()
      return HttpResponseRedirect(reverse('emailed_person', args=(int(person.id),)))
  else:
    form = EmailForm()
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('streampunk.send_direct_email')
def emailed_person(request, pk):
  pid = int(pk)
  person = Person.objects.get(id = pid)
  return render_to_response('streampunk/emailed.html',
                            locals(),
                            context_instance=RequestContext(request))


def send_mail_to_personlist(request, personlist, subject=None, success_url=None, cancel_url=None, edittemplate='streampunk/mail_personlist.html'):
  people = personlist.people.exclude(email='')
  nomail = personlist.people.filter(email='')

  if not subject:
    subject = personlist.name
  if not cancel_url:
    cancel_url = reverse('main_page')
  if not success_url:
    success_url = reverse('main_page')
  if request.method == 'POST':
    if request.POST.has_key('cancel'):
      if personlist.auto == True:
        # discard this personlist
        personlist.delete()
      return HttpResponseRedirect(cancel_url)
    form = EmailForm(request.POST)
    if form.is_valid():
      if people:
        con_name = ConInfoString.objects.con_name()
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        incItems = form.cleaned_data['includeItems']
        incContact = form.cleaned_data['includeContact']
        incAvail = form.cleaned_data['includeAvail']
        for person in people:
          if incItems:
            itemspeople = ItemPerson.objects.filter(person = person)
          if incAvail:
            avail = person.availability.all()
            noAvailMsg = u"We have no information about your availablity over the convention."
          msg = mkemail(request, locals(), subject, person)
          msg.send()
      if personlist.auto == True:
        personlist.delete()
      return HttpResponseRedirect(success_url)
  else:
    form = EmailForm(initial = { 'subject' : subject })
  return render_to_response(edittemplate,
                            locals(),
                            context_instance=RequestContext(request))


@permission_required('streampunk.send_item_email')
def email_personlist(request, pk):
  personlist = PersonList.objects.get(id = int(pk))
  if personlist.auto:
    success_url = reverse('main_page')
    cancel_url = success_url
  else:
    success_url = personlist.get_absolute_url()
    cancel_url = success_url
  return send_mail_to_personlist(request, personlist,
                                 subject=personlist.name,
                                 success_url=success_url,
                                 cancel_url=cancel_url)

@permission_required('streampunk.send_item_email')
def email_item_with_personlist(request, ipk, plpk):
  item = Item.objects.get(id = int(ipk))
  subject = item.title
  cancel_url = item.get_absolute_url()
  success_url = reverse('emailed_item', args=(int(item.id),))
  personlist = PersonList.objects.get(id = int(plpk))
  return send_mail_to_personlist(request, personlist,
                                 subject=item.title,
                                 success_url=success_url,
                                 cancel_url=cancel_url)

@permission_required('streampunk.send_item_email')
def emailed_item(request, pk):
  iid = int(pk)
  item = Item.objects.get(id = iid)
  people = item.people.exclude(email='')
  return render_to_response('streampunk/emailed.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('streampunk.edit_tags')
def edit_tags_for_item(request, i):
  iid = int(i)
  item = Item.objects.get(id = iid)
  if request.method == 'POST':
    form = ItemTagForm(request.POST, instance=item)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('show_item_detail', kwargs={ 'pk': int(i) }))
  else:
    form = ItemTagForm(instance = item, initial = { 'fromTag' : False  })
  form_title = u'Edit tags for item'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('streampunk.edit_tags')
def edit_tags_for_person(request, p):
  pid = int(p)
  person = Person.objects.get(id = pid)
  if request.method == 'POST':
    form = PersonTagForm(request.POST, instance=person)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('show_person_detail', kwargs={ 'pk' : int(p) }))
  else:
    form = PersonTagForm(instance = person, initial = { 'fromTag' : False  })
  form_title = u'Edit tags for person'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_tags(request):
  if request.method == 'POST':
    form = AddMultipleTagsForm(request.POST)
    if form.is_valid():
      items = form.cleaned_data['items']
      tags = form.cleaned_data['tags']
      people = form.cleaned_data['people']
      for tag in tags:
        for person in people:
          person.tags.add(tag)
        for item in items:
          item.tags.add(tag)
      return render_to_response('streampunk/added_tags.html',
                                locals(),
                                context_instance=RequestContext(request))
  else:
    form = AddMultipleTagsForm()
  form_intro = u'Select the tags to be added, and the items and/or people to which to add them.'
  form_title = u'Add Multiple Tags'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_kitbundle_to_room(request):
  if request.method == 'POST':
    form = AddBundleToRoomForm(request.POST)
    if form.is_valid():
      bundle = form.cleaned_data['bundle']
      room = form.cleaned_data['room']
      fromSlot = form.cleaned_data['fromSlot']
      toSlot = form.cleaned_data['toSlot']
      toLength = form.cleaned_data['toLength']
      things = bundle.things.all()
      for thing in things:
        kras = KitRoomAssignment(thing=thing, bundle=bundle, room=room,
                                 fromSlot=fromSlot, toSlot=toSlot, toLength=toLength)
        kras.save()
      return HttpResponseRedirect(reverse('show_room_detail', args=(int(room.id),)))
  else:
    data = get_initial_data_from_request(request, { 'room': Room, 'bundle': KitBundle })
    form = AddBundleToRoomForm(initial = data)
  form_title = u'Add Kit Bundle to Room'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def delete_kitbundle_from_room(request, kb, room):
  kbid = int(kb)
  rid = int(room)
  kitb = KitBundle.objects.get(id = kbid)
  rm = Room.objects.get(id = rid)
  KitRoomAssignment.objects.filter(bundle=kitb, room=rm).delete()
  return HttpResponseRedirect(reverse('show_room_detail', args=(rid,)))

def add_kitbundle_to_item(request):
  if request.method == 'POST':
    form = AddBundleToItemForm(request.POST)
    if form.is_valid():
      bundle = form.cleaned_data['bundle']
      item = form.cleaned_data['item']
      things = bundle.things.all()
      for thing in things:
        kras = KitItemAssignment(thing=thing, bundle=bundle, item=item)
        kras.save()
      return HttpResponseRedirect(reverse('show_item_detail', args=(int(item.id),)))
  else:
    data = get_initial_data_from_request(request, { 'item': Item, 'bundle': KitBundle })
    form = AddBundleToItemForm(initial = data)
  form_title = u'Add Kit Bundle to Item'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def delete_kitbundle_from_item(request, kb, item):
  kbid = int(kb)
  iid = int(item)
  kitb = KitBundle.objects.get(id = kbid)
  i = Item.objects.get(id = iid)
  KitItemAssignment.objects.filter(bundle=kitb, item=i).delete()
  return HttpResponseRedirect(reverse('show_item_detail', args=(iid,)))

def add_kitthing_to_room(request):
  if request.method == 'POST':
    form = AddThingToRoomForm(request.POST)
    if form.is_valid():
      thing = form.cleaned_data['thing']
      room = form.cleaned_data['room']
      fromSlot = form.cleaned_data['fromSlot']
      toSlot = form.cleaned_data['toSlot']
      toLength = form.cleaned_data['toLength']
      kras = KitRoomAssignment(thing=thing, room=room, fromSlot=fromSlot, toSlot=toSlot, toLength=toLength)
      kras.save()
      return HttpResponseRedirect(reverse('show_room_detail', args=(int(room.id),)))
  else:
    data = get_initial_data_from_request(request, { 'room': Room, 'thing': KitThing })
    form = AddThingToRoomForm(initial = data)
  form_title = u'Add Kit Thing to Room'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_kitthing_to_item(request):
  if request.method == 'POST':
    form = AddThingToItemForm(request.POST)
    if form.is_valid():
      thing = form.cleaned_data['thing']
      item = form.cleaned_data['item']
      kras = KitItemAssignment(thing=thing, item=item)
      kras.save()
      return HttpResponseRedirect(reverse('show_item_detail', args=(int(item.id),)))
  else:
    data = get_initial_data_from_request(request, { 'item': Item, 'thing': KitThing })
    form = AddThingToItemForm(initial = data)
  form_title = u'Add Kit Thing to Item'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_kitrequest_to_item(request, pk):
  if request.method == 'POST':
    form = KitRequestForm(request.POST)
    if form.is_valid():
      item = Item.objects.get(id=int(pk))
      kind = form.cleaned_data['kind']
      count = form.cleaned_data['count']
      setupAssistance = form.cleaned_data['setupAssistance']
      notes = form.cleaned_data['notes']
      status = form.cleaned_data['status']
      req = KitRequest(kind=kind, count=count, setupAssistance=setupAssistance, notes=notes, status=status)
      req.save()
      item.kitRequests.add(req)
      item.save()
      return HttpResponseRedirect(reverse('show_item_detail', args=(int(item.id),)))
  else:
    form = KitRequestForm()
  form_title = u'Add a new Kit Request to Item'
  return render_to_response('streampunk/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def fill_slot_gen(request, r, s, cls, suf):
  rid = int(r)
  sid = int(s)
  room = Room.objects.get(id = rid)
  slot = Slot.objects.get(id = sid)
  grid = slot.grid_set.all()[0]
  if request.method == 'POST':
    form = cls(request.POST)
    if form.is_valid():
      item = form.cleaned_data['item']
      item.room = room
      item.start = slot
      item.save()
      return HttpResponseRedirect(reverse('show_grid', args=(grid.id,)))
  else:
    form = cls()
  return render_to_response('streampunk/fill_slot.html',
                            locals(),
                            context_instance=RequestContext(request))

def fill_slot_sched(request, r, s):
  return fill_slot_gen(request, r, s, FillSlotSchedForm, 's')

def fill_slot_unsched(request, r, s):
  return fill_slot_gen(request, r, s, FillSlotUnschedForm, 'u')

def list_checks(request):
  CheckFormSet = modelformset_factory(Check, extra=0, formset=CheckModelFormSet, fields=())
  if request.method == 'POST':
    formset = CheckFormSet(request.POST)
    if formset.is_valid():
      checkOutputs = []
      for form in formset:
        if form.cleaned_data['enable']:
          check = form.instance
          module = check.module
          importcmd = "import streampunk.checks.%s" % (module,)
          runcmd = "checkOutput = streampunk.checks.%s.run_check(check)" % (module,)
          exec(importcmd)
          exec(runcmd)
          checkOutputs.append(checkOutput)
      return render_to_response('streampunk/checkresults.html',
                                locals(),
                                context_instance=RequestContext(request))

  else:
    # We want to order the checks so that they're predictable for testing.
    formset = CheckFormSet(queryset=Check.objects.order_by('name'))
  return render_to_response('streampunk/checks.html',
                            locals(),
                            context_instance=RequestContext(request))

def make_personlist(request):
  if request.method == 'POST':
    if request.POST.has_key('email_all') or request.POST.has_key('save_all'):
      peeps = request.POST.getlist('allpeople')
    elif request.POST.has_key('email_some') or request.POST.has_key('save_some'):
      peeps = request.POST.getlist('somepeople')
    elif request.POST.has_key('email_select') or request.POST.has_key('save_select'):
      # We have the "select" combo for the tables2 variant with which I'm experimenting.
      peeps = request.POST.getlist('select')
    else:
      # huh? what happened?
      return HttpResponseRedirect(reverse('new_personlist'))
    pids = [ int(p) for p in peeps ]
    people = Person.objects.filter(id__in=pids)
    name = request.POST.get('listname', '')
    if request.POST.has_key('email_all') or request.POST.has_key('email_some') or request.POST.has_key('email_select'):
      # we're going to use this personlist to mail people immediately, so save
      # the list, and head over to creating the mail message.
      personlist = PersonList(name = name, auto = True)
      personlist.save()
      for p in people:
        personlist.people.add(p)
      iid = request.POST.get('itemid', None)
      if iid == None:
        return HttpResponseRedirect(reverse('email_personlist', kwargs={'pk': personlist.id}))
      else:
        return HttpResponseRedirect(reverse('mail_item_with_personlist', kwargs={'ipk': iid, 'plpk': personlist.id}))
    else:
      # we're creating the list for later use, so let's populate a form that'll
      # allow correction and renaming, before saving.
      form = PersonListForm(initial = { 'name' : name, 'people' : people, 'auto' : False })
      return render_to_response('streampunk/edit_personlist.html',
                                locals(),
                                context_instance=RequestContext(request))
  else:
    return HttpResponseRedirect(reverse('new_personlist'))
  
def make_con_groups(request):
  if request.user.is_superuser:
    added_perms = add_con_groups()
    status_msg = u"Added permissions"
  else:
    status_msg = u"Permission denied!"
  return render_to_response('streampunk/make_con_groups.html',
                            locals(),
                            context_instance=RequestContext(request))

def kit_usage(request):
  kratable = make_tabler(KitRoomAssignment, KitRoomAssignmentTable, request=request,
                      qs=KitRoomAssignment.objects.all(), prefix='kra-', empty='No kit room assignments')
  kiatable = make_tabler(KitItemAssignment, KitItemAssignmentTable, request=request,
                      qs=KitItemAssignment.objects.all(), prefix='kia-', empty='No kit item assignments')
  krtable = make_tabler(KitRequest, KitRequestTable, request=request,
                     qs=KitRequest.objects.all(), prefix='kr-', empty='No kit requests',
                     extra_exclude=['setup', 'notes', 'status'])
  return render_to_response('streampunk/kit_usage.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_people(request):
  extra_exclude = [] if request.user.has_perm('streampunk.edit_programme') else [ 'edit', 'remove' ]
  table = make_tabler(Person, PersonTable, request=request, qs=Person.objects.all(), prefix='p-',
                      empty='No people', extra_exclude=extra_exclude)
  return render(request, "streampunk/list_people.html", { "ptable": table,
                                                          "verbose_name": 'person' })


def list_items_filtered(request, extra_exclude):
  if request.user.has_perm('streampunk.read_private'):
    qs = Item.objects.all()
  else:
    qs = Item.objects.filter(visible = True)
  table = make_tabler(Item, ItemTable, request=request, qs=qs, prefix='i-', empty='No items', extra_exclude=extra_exclude)
  return render(request, "streampunk/list_items.html", { "itable": table,
                                                         "verbose_name": 'item' })

def list_items(request):
  return list_items_filtered(request, [ 'projNeeded', 'satisfies_kit_requests' ])

def list_items_tech(request):
  return list_items_filtered(request, [ ])

def list_kitthings(request):
  extra_exclude = [ ] if request.user.has_perm('streampunk.edit_kit') else [ 'edit', 'remove' ]
  table = make_tabler(KitThing, KitThingTable, request=request, qs=KitThing.objects.all(), prefix='kt-',
                      empty='No kit things', extra_exclude=extra_exclude)
  return render(request, "streampunk/kitthing_list.html", { "kttable": table,
                                                            "verbose_name": 'kit thing' })

def list_kitrequests(request):
  table = make_tabler(KitRequest, KitRequestTable, request=request, qs=KitRequest.objects.all(), prefix='kr-', empty='No kit requests',
                      extra_exclude=['setup', 'notes'])
  return render(request, "streampunk/kitrequest_list.html", { "krtable": table,
                                                            "verbose_name": 'kit thing' })


def list_tags(request):
  if request.user.has_perm('streampunk.read_private'):
    qs = Tag.objects.all()
  else:
    qs = Tag.objects.filter(visible = True)
  table = make_tabler(Tag, TagTable, request=request, qs=qs, prefix='t-', empty='No tags')
  return render(request, "streampunk/list_tags.html", { "ttable": table,
                                                        "verbose_name": 'tag' })

def list_kitbundles(request):
  extra_exclude = [ ] if request.user.has_perm('streampunk.edit_kit') else [ 'edit', 'remove' ]
  table = make_tabler(KitBundle, KitBundleTable, request=request,
                      qs=KitBundle.objects.all(), prefix='kb-', empty='No kit bundles', extra_exclude=extra_exclude)
  return render(request, "streampunk/kitbundle_list.html", { "kbtable": table,
                                                             "verbose_name": 'kit bundle' })

def list_rooms_filtered(request, extra_exclude):
  if request.user.has_perm('streampunk.read_private'):
    qs = Room.objects.all()
  else:
    qs = Room.objects.filter(visible = True)
  table = make_tabler(Room, RoomTable, request=request,
                      qs=qs, prefix='r-', empty='No rooms', extra_exclude=extra_exclude)
  return render(request, "streampunk/list_rooms.html", { "rtable": table,
                                                             "verbose_name": 'room' })

def list_rooms(request):
  return list_rooms_filtered(request, [ 'canClash', 'needsSound', 'naturalLight', 'securable',
                                        'controlLightsInRoom', 'controlAirConInRoom',
                                        'accessibleOnFlat', 'hasCableRuns', 'openableWindows',
                                        'closableCurtains', 'inRadioRange', 'hasWifi', 'techNotes', 'privNotes' ])

def list_rooms_prog(request):
  return list_rooms_filtered(request, [ 'isDefault', 'isUndefined', 'canClash',
                                        'needsSound', 'naturalLight', 'securable',
                                        'controlLightsInRoom', 'controlAirConInRoom',
                                        'accessibleOnFlat', 'hasCableRuns', 'openableWindows',
                                        'closableCurtains', 'inRadioRange' ])

def list_rooms_tech(request):
  return list_rooms_filtered(request, [ 'gridOrder', 'visible', 'isDefault', 'isUndefined', 'canClash', 'parent'])

def xml_dump(request):
  con_name = ConInfoString.objects.con_name()
  if request.user.has_perm('streampunk.read_private'):
    rooms = Room.objects.all()
    allitems = Item.scheduled.all()
    template = 'xml/streampunk.xml'
  else:
    rooms = Room.objects.filter(visible = True)
    allitems = Item.scheduled.filter(visible = True, room__visible = True)
    template = 'xml/streampunk_public.xml'
  people = Person.objects.all()

  return render_to_response(template,
                            { "rooms": rooms, "people": people, "items": allitems, "con_name": con_name },
                            context_instance=RequestContext(request),
                            content_type='application/xml')

def xsl_stylesheet(request, template):
  return render_to_response(template, locals(), context_instance=RequestContext(request), content_type='text/xsl')

