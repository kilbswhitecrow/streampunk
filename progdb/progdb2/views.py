# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.generic import DeleteView, DetailView, UpdateView, CreateView, ListView
from django.forms.models import modelformset_factory

from progdb2.models import Item, Person, Room, Tag, ItemPerson, Grid, Slot, ConDay, Check
from progdb2.models import KitThing, KitBundle, KitItemAssignment, KitRoomAssignment, KitRequest
from progdb2.forms import KitThingForm, KitBundleForm
from progdb2.forms import ItemPersonForm, ItemTagForm, PersonTagForm, ItemForm, PersonForm
from progdb2.forms import TagForm, RoomForm, CheckModelFormSet
from progdb2.forms import AddMultipleTagsForm, FillSlotUnschedForm, FillSlotSchedForm
from progdb2.forms import AddBundleToRoomForm, AddBundleToItemForm
from progdb2.forms import AddThingToRoomForm, AddThingToItemForm

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
    context['verbose_name'] = self.model._meta.verbose_name
    context['verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['new_url'] = r'/progdb/new_%s/' % ( self.model.__name__.lower() )
    return context

class AfterDeleteView(DeleteView):
  def get_success_url(self):
    if self.request.POST.has_key('after'):
      return self.request.POST.get('after')
    else:
      return '/progdb/main/'

def main_page(request):
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
  rooms = Room.objects.all();
  # Following is buggy: it won't include any items that start
  # earlier, but run into this grid.
  items = Item.objects.filter(day = day, start__in = slots)
  people = ItemPerson.objects.filter(item__in=items)
      
  return render_to_response('progdb2/show_grid.html',
                            locals(),
                            context_instance=RequestContext(request))

def show_slot(request, sl):
  sid = int(sl)
  slot = Grid.objects.get(id = sid)
  return render_to_response('progdb2/show_slot.html',
                            locals(),
                            context_instance=RequestContext(request))

class show_item_detail(DetailView):
  context_object_name = 'item'
  model = Item
  template_name = 'progdb2/show_item.html'

  def get_context_data(self, **kwargs):
    context = super(show_item_detail, self).get_context_data(**kwargs)
    context['item_people'] = ItemPerson.objects.filter(item=self.object)
    context['item_tags'] = self.object.tags.all()
    context['kitrequests'] = self.object.kitRequests.all()
    context['kitthings'] = KitItemAssignment.objects.filter(item=self.object)
    return context


class show_person_detail(DetailView):
  context_object_name = 'person'
  model = Person
  template_name = 'progdb2/show_person.html'

  def get_context_data(self, **kwargs):
    context = super(show_person_detail, self).get_context_data(**kwargs)
    context['person_name'] = "%s" % self.object
    context['person_tags'] = self.object.tags.all()
    context['person_items'] = ItemPerson.objects.filter(person=self.object)
    context['avail'] = self.object.availability.all()
    return context

class show_tag_detail(DetailView):
  context_object_name = 'tag'
  model = Tag
  template_name = 'progdb2/show_tag.html'

  def get_context_data(self, **kwargs):
    context = super(show_tag_detail, self).get_context_data(**kwargs)
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
        return HttpResponseRedirect(reverse('progdb.progdb2.views.show_person', args=(int(person.id),)))
      else:
        return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(int(item.id),)))
  else:
    form = ItemPersonForm( initial = { 'item' : i, 'person' : p, 'fromPerson' : is_from_person(request) })
  return render_to_response('progdb2/editform.html',
                            locals(),
                            context_instance=RequestContext(request))

def show_referer(request):
  if request.method == 'POST':
    blurb = 'Post method'
  else:
    blurb = 'Get method'
  referer = request.META['HTTP_REFERER']
  if is_from_person(request):
    result = 'from person'
  else:
    result = 'not from person'
  return render_to_response('progdb2/show_referer.html',
                            locals(),
                            context_instance=RequestContext(request))

def edit_tags_for_item(request, i):
  iid = int(i)
  item = Item.objects.get(id = iid)
  if request.method == 'POST':
    form = ItemTagForm(request.POST, instance=item)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(int(i),)))
  else:
    form = ItemTagForm(instance = item, initial = { 'fromTag' : False  })
  return render_to_response('progdb2/edit_tags_for_item.html',
                            locals(),
                            context_instance=RequestContext(request))

def edit_tags_for_person(request, p):
  pid = int(p)
  person = Person.objects.get(id = pid)
  if request.method == 'POST':
    form = PersonTagForm(request.POST, instance=person)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_person', args=(int(p),)))
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
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_room', args=(int(room.id),)))
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
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(int(item.id),)))
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
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_room', args=(int(room.id),)))
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
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(int(item.id),)))
  else:
    form = AddThingToItemForm()
  form_title = u'Add Kit Thing to Item'
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
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_grid', args=(did, gid,)))
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
