# Create your views here.

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

from progdb2.models import Item, Person, Room, Tag, ItemPerson, Grid, Slot, ConDay, ConInfoString, Check
from progdb2.models import KitThing, KitBundle, KitItemAssignment, KitRoomAssignment, KitRequest, PersonList
from progdb2.models import UserProfile
from progdb2.forms import KitThingForm, KitBundleForm, KitRequestForm
from progdb2.forms import ItemPersonForm, ItemTagForm, PersonTagForm, ItemForm, PersonForm
from progdb2.forms import TagForm, RoomForm, CheckModelFormSet
from progdb2.forms import AddMultipleTagsForm, FillSlotUnschedForm, FillSlotSchedForm
from progdb2.forms import AddBundleToRoomForm, AddBundleToItemForm
from progdb2.forms import AddThingToRoomForm, AddThingToItemForm
from progdb2.forms import EmailForm, PersonListForm, UserProfileForm, UserProfileFullForm
from progdb2.auth import add_con_groups

def show_request(request):
  if request.method == 'GET':
    d = request.GET.copy()
  else:
    d = request.POST.copy()
  for t in d.lists():
    k, l = t
    for v in l:
      print u"Got '%s' = '%s'\n" % (k, v)
  return render_to_response('progdb2/show_request.html',
                            locals(),
                            context_instance=RequestContext(request))

class NewView(CreateView):
  template_name = 'progdb2/editform.html'

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
  template_name = 'progdb2/editform.html'

class AllView(ListView):
  template_name = 'progdb2/object_list.html'

  def get_context_data(self, **kwargs):
    context = super(AllView, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['verbose_name'] = self.model._meta.verbose_name
    context['verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['new_url'] = r'/progdb/new_%s/' % ( self.model.__name__.lower() )
    return context

class VisibleView(AllView):
  def get_queryset(self):
    if self.request.user.has_perm('progb2.read_private'):
      return self.model.objects.all()
    else:
      return self.model.objects.filter(visible = True)

class AfterDeleteView(DeleteView):
  def get_success_url(self):
    if self.request.POST.has_key('after'):
      return self.request.POST.get('after')
    else:
      return '/progdb/main/'

@login_required
def edit_user_profile(request):
  userprofile = request.user.get_profile()
  if request.method == 'POST':
    if request.user.has_perm('progdb2.read_private'):
      form = UserProfileFullForm(request.POST, instance=userprofile)
    else:
      form = UserProfileForm(request.POS, instance=userprofile)
    if form.is_valid():
      userprofile.save()
      return HttpResponseRedirect(reverse('userprofile'))
  else:
    initial_data = { 'show_shortname': userprofile.show_shortname,
                     'show_tags': userprofile.show_tags,
                     'show_people': userprofile.show_people,
                     'name_order': userprofile.name_order }
    if request.user.has_perm('progdb2.read_private'):
      initial_data['person'] = userprofile.person
      form = UserProfileFullForm(instance=userprofile, initial=initial_data)
    else:
      form = UserProfileForm(instance=userprofile, initial=initial_data)
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))


@login_required
def show_profile_detail(request):
  userprofile = request.user.get_profile()
  return render_to_response('progdb2/show_userprofile.html',
                            locals(),
                            context_instance=RequestContext(request))


def main_page(request):
  num_items = Item.scheduled.count()
  num_people = Person.objects.count()
  # e.g. {'num_people__sum': 5, 'budget__sum': 0}
  totals = Item.scheduled.annotate(num_people=Count('people')).aggregate(Sum('num_people'), Sum('budget'))
  # {'length__length__sum': 870}
  mins_scheduled = Item.scheduled.aggregate(Sum('length__length'))

  con_name = ConInfoString.objects.con_name()
  num_panellists = totals['num_people__sum']
  budget = totals['budget__sum']
  hours_scheduled = mins_scheduled['length__length__sum'] / 60
  return render_to_response('progdb2/main_page.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_grids(request):
  grid_list = Grid.objects.all()
  day_list = ConDay.objects.all()
  return render_to_response('progdb2/list_grids.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_room_detail(DetailView):
  context_object_name='room'
  model = Room
  template_name = 'progdb2/show_room.html'

  def get_context_data(self, **kwargs):
    context = super(show_room_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['room_items'] = self.object.item_set.all()
    context['avail'] = self.object.availability.all()
    context['kitthings'] = KitRoomAssignment.objects.filter(room=self.object)
    return context

def show_grid(request, dy, gr):
  did = int(dy)
  day = ConDay.objects.get(id = did)
  gid = int(gr)
  grid = Grid.objects.get(id = gid)
  slots = grid.slots.all()
  # Following is buggy: it won't include any items that start
  # earlier, but run into this grid.
  if request.user.has_perm('progb2.read_private'):
    items = Item.objects.filter(day = day, start__in = slots)
    people = ItemPerson.objects.filter(item__in=items)
    rooms = Room.objects.all();
  else:
    items = Item.objects.filter(day = day, start__in = slots, visible=True)
    people = ItemPerson.objects.filter(visible=True).filter(item__in=items)
    rooms = Room.objects.filter(visible=True);
      
  return render_to_response('progdb2/show_grid.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_slot_detail(DetailView):
  context_object_name = 'slot'
  model = Slot
  template_name = 'progdb2/show_slot.html'

  def get_context_data(self, **kwargs):
    context = super(show_slot_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['items'] = Item.objects.filter(start = self.object).order_by('day')
    return context

class show_item_detail(DetailView):
  context_object_name = 'item'
  model = Item
  template_name = 'progdb2/show_item.html'

  def get_context_data(self, **kwargs):
    context = super(show_item_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    if self.request.user.has_perm('progb2.read_private'):
      context['item_people'] = ItemPerson.objects.filter(item=self.object)
      context['item_tags'] = self.object.tags.all()
    else:
      context['item_people'] = ItemPerson.objects.filter(item=self.object, visible=True)
      context['item_tags'] = self.object.tags.filter(visible=True)
    context['kitrequests'] = self.object.kitRequests.all()
    context['kitthings'] = KitItemAssignment.objects.filter(item=self.object)
    return context


class show_person_detail(DetailView):
  context_object_name = 'person'
  model = Person
  template_name = 'progdb2/show_person.html'

  def get_context_data(self, **kwargs):
    context = super(show_person_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    if self.request.user.has_perm('progb2.read_private'):
      context['person_name'] = "%s" % self.object
      context['person_tags'] = self.object.tags.all()
      context['person_items'] = ItemPerson.objects.filter(person=self.object)
    else:
      context['person_name'] = "%s" % self.object.as_badge()
      context['person_tags'] = self.object.tags.filter(visible=True)
      context['person_items'] = ItemPerson.objects.filter(person=self.object, visible=True)
    context['avail'] = self.object.availability.all()
    return context

class show_tag_detail(DetailView):
  context_object_name = 'tag'
  model = Tag
  template_name = 'progdb2/show_tag.html'

  def get_context_data(self, **kwargs):
    context = super(show_tag_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['tag_items'] = self.object.item_set.all()
    context['tag_people'] = self.object.person_set.all()
    return context


def show_kitthing(request, kt):
  ktid = int(kt)
  kitthing = KitThing.objects.get(id = ktid)
  kitbundles = kitthing.kitbundle_set.all()
  kititems = KitItemAssignment.objects.filter(thing = kitthing)
  kitrooms = KitRoomAssignment.objects.filter(thing = kitthing)
  avail = kitthing.availability.all()
  return render_to_response('progdb2/show_kitthing.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_kitthing_detail(DetailView):
  context_object_name = 'kitthing'
  model = KitThing
  template_name = 'progdb2/show_kitthing.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitthing_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['kitbundles'] = self.object.kitbundle_set.all()
    context['kititems'] = KitItemAssignment.objects.filter(thing = self.object)
    context['kitrooms'] = KitRoomAssignment.objects.filter(thing = self.object)
    context['avail'] = self.object.availability.all()
    return context


def show_kitbundle(request, kb):
  kbid = int(kb)
  kitbundle = KitBundle.objects.get(id = kbid)
  kitthings = kitbundle.things.all()
  kititems = KitItemAssignment.objects.filter(bundle = kitbundle)
  kitrooms = KitRoomAssignment.objects.filter(bundle = kitbundle)
  return render_to_response('progdb2/show_kitbundle.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_kitbundle_detail(DetailView):
  context_object_name = 'kitbundle'
  model = KitBundle
  template_name = 'progdb2/show_kitbundle.html'

  def get_context_data(self, **kwargs):
    context = super(show_kitbundle_detail, self).get_context_data(**kwargs)
    context['request'] = self.request
    context['kitthings'] = self.object.things.all()
    context['kititems'] = KitItemAssignment.objects.filter(bundle = self.object)
    context['kitrooms'] = KitRoomAssignment.objects.filter(bundle = self.object)
    return context

class show_kitrequest_detail(DetailView):
  context_object_name = 'kitrequest'
  model = KitRequest
  template_name = 'progdb2/show_kitrequest.html'

class show_itemperson_detail(DetailView):
  context_object_name = 'itemperson'
  model = ItemPerson
  template_name = 'progdb2/show_itemperson.html'

class show_personlist_detail(DetailView):
  context_object_name = 'personlist'
  model = PersonList
  template_name = 'progdb2/show_personlist.html'


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
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def mkemail(request, dirvars, subject, person):
  context = RequestContext(request)
  txt = render_to_string('progdb2/email.txt', dirvars, context_instance=context)
  msg = EmailMultiAlternatives(subject, txt, request.user.email, [ person.email ] )
  html = render_to_string('progdb2/email.html', dirvars, context_instance=context)
  msg.attach_alternative(html, "text/html")
  return msg

@permission_required('progdb2.send_direct_email')
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
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('progdb2.send_direct_email')
def emailed_person(request, pk):
  pid = int(pk)
  person = Person.objects.get(id = pid)
  return render_to_response('progdb2/emailed.html',
                            locals(),
                            context_instance=RequestContext(request))


def send_mail_to_personlist(request, personlist, subject=None, success_url=None, cancel_url=None, edittemplate='progdb2/mail_personlist.html'):
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


@permission_required('progdb2.send_item_email')
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

@permission_required('progdb2.send_item_email')
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

@permission_required('progdb2.send_item_email')
def emailed_item(request, pk):
  iid = int(pk)
  item = Item.objects.get(id = iid)
  people = item.people.exclude(email='')
  return render_to_response('progdb2/emailed.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('progdb2.edit_tags')
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
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

@permission_required('progdb2.edit_tags')
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
  return render_to_response('progdb2/editform.html',
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
      return render_to_response('progdb2/added_tags.html',
                                locals(),
                                context_instance=RequestContext(request))
  else:
    form = AddMultipleTagsForm()
  form_intro = u'Select the tags to be added, and the items and/or people to which to add them.'
  form_title = u'Add Multiple Tags'
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_kitbundle_to_room(request):
  if request.method == 'POST':
    form = AddBundleToRoomForm(request.POST)
    if form.is_valid():
      bundle = form.cleaned_data['bundle']
      room = form.cleaned_data['room']
      fromDay = form.cleaned_data['fromDay']
      fromSlot = form.cleaned_data['fromSlot']
      toDay = form.cleaned_data['toDay']
      toSlot = form.cleaned_data['toSlot']
      things = bundle.things.all()
      for thing in things:
        kras = KitRoomAssignment(thing=thing, bundle=bundle, room=room, fromDay=fromDay, fromSlot=fromSlot, toDay=toDay, toSlot=toSlot)
        kras.save()
      return HttpResponseRedirect(reverse('show_room_detail', args=(int(room.id),)))
  else:
    form = AddBundleToRoomForm()
  form_title = u'Add Kit Bundle to Room'
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

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
    form = AddBundleToItemForm()
  form_title = u'Add Kit Bundle to Item'
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def add_kitthing_to_room(request):
  if request.method == 'POST':
    form = AddThingToRoomForm(request.POST)
    if form.is_valid():
      thing = form.cleaned_data['thing']
      room = form.cleaned_data['room']
      fromDay = form.cleaned_data['fromDay']
      fromSlot = form.cleaned_data['fromSlot']
      toDay = form.cleaned_data['toDay']
      toSlot = form.cleaned_data['toSlot']
      kras = KitRoomAssignment(thing=thing, room=room, fromDay=fromDay, fromSlot=fromSlot, toDay=toDay, toSlot=toSlot)
      kras.save()
      return HttpResponseRedirect(reverse('show_room_detail', args=(int(room.id),)))
  else:
    form = AddThingToRoomForm()
  form_title = u'Add Kit Thing to Room'
  return render_to_response('progdb2/editform.html',
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
    form = AddThingToItemForm()
  form_title = u'Add Kit Thing to Item'
  return render_to_response('progdb2/editform.html',
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
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def fill_slot_gen(request, d, g, r, s, cls, suf):
  did = int(d)
  gid = int(g)
  rid = int(r)
  sid = int(s)
  day = ConDay.objects.get(id = did)
  grid = Grid.objects.get(id = gid)
  room = Room.objects.get(id = rid)
  slot = Slot.objects.get(id = sid)
  if request.method == 'POST':
    form = cls(request.POST)
    if form.is_valid():
      item = form.cleaned_data['item']
      item.room = room
      item.start = slot
      item.day = day
      item.save()
      return HttpResponseRedirect(reverse('show_grid', args=(did, gid,)))
  else:
    form = cls()
  return render_to_response('progdb2/fill_slot.html',
                            locals(),
                            context_instance=RequestContext(request))

def fill_slot_sched(request, d, g, r, s):
  return fill_slot_gen(request, d, g, r, s, FillSlotSchedForm, 's')

def fill_slot_unsched(request, d, g, r, s):
  return fill_slot_gen(request, d, g, r, s, FillSlotUnschedForm, 'u')

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
          importcmd = "import progdb2.checks.%s" % (module,)
          runcmd = "checkOutput = progdb2.checks.%s.run_check(check)" % (module,)
          exec(importcmd)
          exec(runcmd)
          checkOutputs.append(checkOutput)
      return render_to_response('progdb2/checkresults.html',
                                locals(),
                                context_instance=RequestContext(request))

  else:
    formset = CheckFormSet()
  return render_to_response('progdb2/checks.html',
                            locals(),
                            context_instance=RequestContext(request))

def make_personlist(request):
  if request.method == 'POST':
    if request.POST.has_key('email_all') or request.POST.has_key('save_all'):
      peeps = request.POST.getlist('allpeople')
    elif request.POST.has_key('email_some') or request.POST.has_key('save_some'):
      peeps = request.POST.getlist('somepeople')
    else:
      # huh? what happened?
      return HttpResponseRedirect(reverse('new_personlist'))
    pids = [ int(p) for p in peeps ]
    people = Person.objects.filter(id__in=pids)
    name = request.POST.get('listname', '')
    if request.POST.has_key('email_all') or request.POST.has_key('email_some'):
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
      return render_to_response('progdb2/edit_personlist.html',
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
  return render_to_response('progdb2/make_con_groups.html',
                            locals(),
                            context_instance=RequestContext(request))

def kit_usage(request):
  kitrooms = KitRoomAssignment.objects.all()
  kititems = KitItemAssignment.objects.all()
  kitrequests = KitRequest.objects.all()
  return render_to_response('progdb2/kit_usage.html',
                            locals(),
                            context_instance=RequestContext(request))
