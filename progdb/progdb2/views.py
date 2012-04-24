# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.forms.models import modelformset_factory
from progdb2.models import Item, Person, Room, Tag, ItemPerson, Grid, Slot, ConDay, Check
from progdb2.models import KitThing, KitBundle, KitItemAssignment, KitRoomAssignment, KitRequest
from progdb2.forms import KitThingForm, KitBundleForm
from progdb2.forms import ItemPersonForm, ItemTagForm, PersonTagForm, ItemForm, PersonForm
from progdb2.forms import TagForm, RoomForm, CheckModelFormSet
from progdb2.forms import AddMultipleTagsForm, FillSlotUnschedForm, FillSlotSchedForm
from progdb2.forms import AddBundleToRoomForm, AddBundleToItemForm
from progdb2.forms import AddThingToRoomForm, AddThingToItemForm

def main_page(request):
  return render_to_response('progdb2/main_page.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_items(request):
  item_list = Item.objects.all()
  return render_to_response('progdb2/list_items.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_people(request):
  person_list = Person.objects.all()
  return render_to_response('progdb2/list_people.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_grids(request):
  grid_list = Grid.objects.all()
  day_list = ConDay.objects.all()
  return render_to_response('progdb2/list_grids.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_rooms(request):
  room_list = Room.objects.all()
  return render_to_response('progdb2/list_rooms.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_tags(request):
  tag_list = Tag.objects.all()
  return render_to_response('progdb2/list_tags.html',
                            locals(),
                            context_instance=RequestContext(request))

def list_kit(request):
  kitthings = KitThing.objects.all()
  kitbundles = KitBundle.objects.all()
  return render_to_response('progdb2/list_kit.html',
                            locals(),
                            context_instance=RequestContext(request))

def show_room(request, rm):
  rid = int(rm)
  room = Room.objects.get(id = rid)
  room_items = room.item_set.all()
  avail = room.availability.all()
  kitthings = KitRoomAssignment.objects.filter(room=room)
  return render_to_response('progdb2/show_room.html',
                            locals(),
                            context_instance=RequestContext(request))

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

def show_item(request, im):
  iid = int(im)
  item = Item.objects.get(id = iid)
  item_people = ItemPerson.objects.filter(item=item)
  item_tags = item.tags.all()
  kitrequests = item.kitRequests.all()
  kitthings = KitItemAssignment.objects.filter(item=item)
  return render_to_response('progdb2/show_item.html',
                            locals(),
                            context_instance=RequestContext(request))

def show_person(request, p):
  pid = int(p)
  person = Person.objects.get(id = pid)
  person_name = "%s" % person
  person_tags = person.tags.all()
  person_items = ItemPerson.objects.filter(person=person)
  avail = person.availability.all()
  return render_to_response('progdb2/show_person.html',
                            locals(),
                            context_instance=RequestContext(request))

def show_tag(request, t):
  tid = int(t)
  tag = Tag.objects.get(id = tid)
  tag_items = tag.item_set.all()
  tag_people = tag.person_set.all()
  return render_to_response('progdb2/show_tag.html',
                            locals(),
                            context_instance=RequestContext(request))

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

def show_kitbundle(request, kb):
  kbid = int(kb)
  kitbundle = KitBundle.objects.get(id = kbid)
  kitthings = kitbundle.things.all()
  kititems = KitItemAssignment.objects.filter(bundle = kitbundle)
  kitrooms = KitRoomAssignment.objects.filter(bundle = kitbundle)
  return render_to_response('progdb2/show_kitbundle.html',
                            locals(),
                            context_instance=RequestContext(request))

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
  return render_to_response('progdb2/add_person_to_item.html',
                            locals(),
                            context_instance=RequestContext(request))

def remove_person_from_item(request, p, i):
  # Really shouldn't do this kind of updating on a GET, but we're
  # being somewhat lazy here.
  pid = int(p)
  iid = int(i)
  item = Item.objects.get(id = iid)
  person = Person.objects.get(id = pid)
  ItemPerson.objects.filter(item = item, person = person).delete()
  if is_from_person(request):
    return HttpResponseRedirect(reverse('progdb.progdb2.views.show_person', args=(pid,)))
  else:
    return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(iid,)))

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

def edit_item(request, i):
  iid = int(i)
  item = Item.objects.get(id = iid)
  if request.method == 'POST':
    form = ItemForm(request.POST, instance=item)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_item', args=(int(i),)))
  else:
    form = ItemForm(instance = item)
  return render_to_response('progdb2/edit_item.html',
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
  return render_to_response('progdb2/edit_tags_for_person.html',
                            locals(),
                            context_instance=RequestContext(request))


def edit_person(request, p):
  pid = int(p)
  person = Person.objects.get(id = pid)
  if request.method == 'POST':
    form = PersonForm(request.POST, instance=person)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_person', args=(int(p),)))
  else:
    form = PersonForm(instance = person)
  return render_to_response('progdb2/edit_person.html',
                            locals(),
                            context_instance=RequestContext(request))


def edit_tag(request, p):
  pid = int(p)
  tag = Tag.objects.get(id = pid)
  if request.method == 'POST':
    form = TagForm(request.POST, instance=tag)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_tag', args=(int(p),)))
  else:
    form = TagForm(instance = tag)
  return render_to_response('progdb2/edit_tag.html',
                            locals(),
                            context_instance=RequestContext(request))


def edit_room(request, p):
  pid = int(p)
  room = Room.objects.get(id = pid)
  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_room', args=(int(p),)))
  else:
    form = RoomForm(instance = room)
  return render_to_response('progdb2/edit_room.html',
                            locals(),
                            context_instance=RequestContext(request))


def edit_kitthing(request, kt):
  ktid = int(kt)
  kitthing = KitThing.objects.get(id = ktid)
  if request.method == 'POST':
    form = KitThingForm(request.POST, instance=kitthing)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_kitthing', args=(int(kt),)))
  else:
    form = KitThingForm(instance = kitthing)
  return render_to_response('progdb2/edit_kitthing.html',
                            locals(),
                            context_instance=RequestContext(request))


def edit_kitbundle(request, kb):
  kbid = int(kb)
  kitbundle = KitBundle.objects.get(id = kbid)
  if request.method == 'POST':
    form = KitBundleForm(request.POST, instance=kitbundle)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('progdb.progdb2.views.show_kitbundle', args=(int(kb),)))
  else:
    form = KitBundleForm(instance = kitbundle)
  return render_to_response('progdb2/edit_kitbundle.html',
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
  return render_to_response('progdb2/add_tags.html',
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
  return render_to_response('progdb2/add_kitbundle_to_room.html',
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
  return render_to_response('progdb2/add_kitbundle_to_item.html',
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
  return render_to_response('progdb2/add_kitthing_to_room.html',
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
  return render_to_response('progdb2/add_kitthing_to_item.html',
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
