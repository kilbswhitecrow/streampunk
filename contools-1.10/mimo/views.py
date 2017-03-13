# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2017 Stephen Kilbane
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

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import Settings
from .models import TechItem, PlanItem, MoveInItem, LiveItem, MoveOutItem
from .models import SettingsModeForm, SettingsContainerForm, SettingsRoomForm
from .models import SettingsKindForm, SettingsSubkindForm, SettingsGroupForm
from .models import SettingsSupplierForm, PlanItemForm, MoveInItemForm, LiveItemForm
from .models import SplitForm

# ----------- TOP LEVEL -------------

def index(request):
  settings = Settings.objects.settings()
  context = { 'settings': settings, }
  return render(request, 'mimo/index.html', context)

# ----------- PLANNING -------------

def plan_index(request):
  settings = Settings.objects.settings()
  items = PlanItem.objects.all()
  context = { 'settings': settings, 'items': items, }
  return render(request, 'mimo/plan_index.html', context)

class PlanIndexView(generic.ListView):
  template_name = 'mimo/plan_index.html'
  context_object_name = 'items'
  model = PlanItem

  def get_queryset(self):
    return PlanItem.objects.order_by('item__group', 'item__kind', 'item__subkind')

def plan_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(PlanItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/plan_detail.html', context)

class PlanDetailView(generic.DetailView):
  template_name = 'mimo/plan_detail.html'
  context_object_name = 'item'
  model = PlanItem

class TechItemDeleteView(generic.DeleteView):
  context_object_name = 'item'
  model = TechItem
  success_url = reverse_lazy('plan_index')

def add_techitem(request):
  if request.method == 'POST':
    form = PlanItemForm(request.POST)
    if form.is_valid():
      group = form.cleaned_data['group']
      supplier = form.cleaned_data['supplier']
      count = form.cleaned_data['count']
      code = form.cleaned_data['code']
      kind = form.cleaned_data['kind']
      subkind = form.cleaned_data['subkind']
      room = form.cleaned_data['room']
      container = form.cleaned_data['container']
      state = form.cleaned_data['state']
      item = TechItem(group=group, supplier=supplier, count=count, code=code, state=state,
                      kind=kind, subkind=subkind, room=room, container=container)
      item.save()
      planitem = PlanItem(item=item)
      planitem.save()
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = PlanItemForm(initial={
      'supplier': settings.supplier,
      'group': settings.group,
      'room': settings.room,
      'kind': settings.kind,
      'subkind': settings.subkind,
      'container': settings.container,
      'state': 'Planned',
    })
    return render(request, 'mimo/techitem_form.html', { 'form': form })

def dup_techitem(request, pk):
  if request.method == 'POST':
    item = get_object_or_404(TechItem, pk=pk)
    newitem = TechItem(supplier=item.supplier, group=item.group, code=item.code,
                       count=item.count, kind=item.kind, subkind=item.subkind,
                       room=item.room, container=item.container, state=item.state)
    newitem.save()
    planitem = PlanItem(item=newitem)
    planitem.save()
  return HttpResponseRedirect(reverse('plan_index'))

def edit_techitem(request, pk):
  item = get_object_or_404(TechItem, pk=pk)
  if request.method == 'POST':
    form = PlanItemForm(request.POST)
    if form.is_valid():
      item.group = form.cleaned_data['group']
      item.supplier = form.cleaned_data['supplier']
      item.count = form.cleaned_data['count']
      item.code = form.cleaned_data['code']
      item.kind = form.cleaned_data['kind']
      item.subkind = form.cleaned_data['subkind']
      item.room = form.cleaned_data['room']
      item.container = form.cleaned_data['container']
      item.state = form.cleaned_data['state']
      item.save()
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from the item
    form = PlanItemForm(initial={
      'supplier': item.supplier,
      'group': item.group,
      'room': item.room,
      'kind': item.kind,
      'subkind': item.subkind,
      'container': item.container,
      'count': item.count,
      'code': item.code,
      'state': item.state,
    })
    return render(request, 'mimo/techitem_form.html', { 'form': form })

# ----------- MOVE IN -------------

def mi_index(request):
  planitems = PlanItem.objects.order_by('item__group','item__kind','item__subkind')
  extraitems = MoveInItem.objects.filter(plan__isnull=True).order_by('item__container','item__kind','item__subkind')
  context = { 'planitems': planitems, 'extraitems': extraitems }
  return render(request, 'mimo/mi_index.html', context)

def mi_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(MoveInItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/mi_detail.html', context)

class MoveInDetailView(generic.DetailView):
  template_name = 'mimo/mi_detail.html'
  context_object_name = 'item'
  model = MoveInItem

def mark_movein(request, pk, state, room, container):
  # pk is the PlanItem pk.
  pl = get_object_or_404(PlanItem, pk=pk)
  if request.method == 'POST':
    newitem = TechItem(supplier=pl.item.supplier, group=pl.item.group, code=pl.item.code,
                       count=pl.item.count, kind=pl.item.kind, subkind=pl.item.subkind,
                       room=room, container=container, state=state)
    newitem.save()
    mi = MoveInItem(plan=pl, item=newitem)
    mi.save()
  return HttpResponseRedirect(reverse('mi_index'))

def faulty_movein(request, pk):
  settings = Settings.objects.settings()
  return mark_movein(request, pk, state='Faulty', room=settings.room, container=settings.container)

def received_movein(request, pk):
  settings = Settings.objects.settings()
  return mark_movein(request, pk, state='Received', room=settings.room, container=settings.container)

def missing_movein(request, pk):
  return mark_movein(request, pk, state='Not Received', room=None, container=None)

def not_received_movein(request, pk):
  # pk is the PlanItem pk.
  pl = get_object_or_404(PlanItem, pk=pk)
  if request.method == 'POST':
    MoveInItem.objects.filter(plan=pl).delete()
  return HttpResponseRedirect(reverse('mi_index'))

def zap_replacement(request, pk):
  if request.method == 'POST':
    mi = get_object_or_404(MoveInItem, pk=pk)
    mi.item.delete()
    mi.delete()
  return HttpResponseRedirect(reverse('mi_index'))

def rep_movein(request, pk):
  pl = get_object_or_404(PlanItem, pk=pk)
  settings = Settings.objects.settings()
  repitems = pl.moveinitem_set.all()
  if request.method == 'POST':
    form = MoveInItemForm(request.POST)
    if form.is_valid():
      count = form.cleaned_data['count']
      code = form.cleaned_data['code']
      kind = form.cleaned_data['kind']
      subkind = form.cleaned_data['subkind']
      room = form.cleaned_data['room']
      container = form.cleaned_data['container']
      group = pl.item.group       # Doesn't change
      supplier = pl.item.supplier # Doesn't change
      state = 'Replaced'
      newitem = TechItem(group=group, supplier=supplier, count=count, code=code,
                         kind=kind, subkind=subkind, room=room, container=container,
                         state='Replaced')
      newitem.save()
      newmi = MoveInItem(plan=pl, item=newitem)
      newmi.save()
    return HttpResponseRedirect(reverse('mi_replace', args=(pk,)))

  else:
    form = MoveInItemForm(initial={ 'state': 'Replaced',
                                    'group': pl.item.group,
                                    'supplier': settings.supplier,
                                    'container': settings.container,
                                    'room': settings.room,
                                    'kind': pl.item.kind,
                                    'subkind': pl.item.subkind,
                                    'code': pl.item.code,
                                    'count': pl.item.count,
                          })
    context = { 'planitem': pl, 'repitems': repitems, 'form': form }
    return render(request, 'mimo/mi_replacements.html', context)
  
def edit_movein(request, pk):
  mi = get_object_or_404(MoveInItem, pk=pk)
  item = mi.item
  if request.method == 'POST':
    form = MoveInItemForm(request.POST)
    if form.is_valid():
      item.count = form.cleaned_data['count']
      item.code = form.cleaned_data['code']
      item.kind = form.cleaned_data['kind']
      item.subkind = form.cleaned_data['subkind']
      item.room = form.cleaned_data['room']
      item.container = form.cleaned_data['container']
      # supplier is fixed
      # group is fixed
      # state will still be Replaced
      item.save()
      return HttpResponseRedirect(reverse('mi_index'))
  else:
    # Initialise the form from the item
    form = MoveInItemForm(initial={
      'supplier': item.supplier,
      'group': item.group,
      'room': item.room,
      'kind': item.kind,
      'subkind': item.subkind,
      'container': item.container,
      'count': item.count,
      'code': item.code,
      'state': item.state,
    })
    return render(request, 'mimo/techitem_form.html', { 'form': form })

def add_extra_movein(request):
  settings = Settings.objects.settings()
  if request.method == 'POST':
    form = MoveInItemForm(request.POST)
    if form.is_valid():
      newitem=TechItem(count=form.cleaned_data['count'],
                       code=form.cleaned_data['code'],
                       kind=form.cleaned_data['kind'],
                       subkind=form.cleaned_data['subkind'],
                       room=form.cleaned_data['room'],
                       container=form.cleaned_data['container'],
                       supplier=settings.supplier,
                       state='Extra')
      newitem.save()
      mi = MoveInItem(item=newitem)
      mi.save()
      return HttpResponseRedirect(reverse('mi_index'))
  else:
    # Initialise the form to defaults
    form = MoveInItemForm(initial={
      'supplier': settings.supplier,
      'group': settings.group,
      'room': settings.room,
      'kind': settings.kind,
      'subkind': settings.subkind,
      'container': settings.container,
      'count': 1,
      'state': 'Extra'
    })
    return render(request, 'mimo/techitem_form.html', { 'form': form })

# ----------- LIVE -------------

def live_setup(request):
  if request.method == 'POST':
    for mi in MoveInItem.objects.all():
      item = mi.item
      newitem = TechItem(code=item.code, kind=item.kind, subkind=item.subkind,
                         room=item.room, container=item.container,
                         supplier=item.supplier, group=item.group,
                         count=item.count, state='Spare')
      newitem.save()
      li = LiveItem(item=newitem, mi=mi)
      li.save()
  return HttpResponseRedirect(reverse('live_index'))

def live_index(request):
  settings = Settings.objects.settings()
  items = LiveItem.objects.all()
  context = { 'settings': settings, 'items': items, }
  return render(request, 'mimo/live_index.html', context)

class LiveIndexView(generic.ListView):
  template_name = 'mimo/live_index.html'
  context_object_name = 'items'
  model = LiveItem

def live_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(LiveItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/live_detail.html', context)

class LiveDetailView(generic.DetailView):
  template_name = 'mimo/live_detail.html'
  context_object_name = 'item'
  model = LiveItem

def live_edit(request, pk):
  li = get_object_or_404(LiveItem, pk=pk)
  if request.method == 'POST':
    form = LiveItemForm(request.POST)
    if form.is_valid():
      li.item.state = form.cleaned_data['state']
      li.item.container = form.cleaned_data['container']
      li.item.room = form.cleaned_data['room']
      li.item.save()
      return HttpResponseRedirect(reverse('live_index'))
  form = LiveItemForm(initial={
                        'state': li.item.state,
                        'room': li.item.room,
                        'container': li.item.container})
  context = { 'liveitem': li, 'form': form }
  return render(request, 'mimo/live_edit.html', context)

def live_split(request, pk):
  li = get_object_or_404(LiveItem, pk=pk)
  i = li.item
  if request.method == 'POST':
    form = SplitForm(request.POST)
    if form.is_valid():
      split_off = form.cleaned_data['count']
      if split_off > 0 and split_off < i.count:
        i.count = i.count - split_off
        i.save()
        newitem = TechItem(supplier=i.supplier, group=i.group, room=i.room,
                           kind=i.kind, subkind=i.subkind, state=i.state,
                           code=i.code,count=split_off)
        newitem.save()
        newli = LiveItem(item=newitem)
        newli.save()
      return HttpResponseRedirect(reverse('live_index'))
  form = SplitForm(initial={ 'count': 1 })
  context = { 'liveitem': li, 'form': form }
  return render(request, 'mimo/live_split.html', context)

# ----------- MOVE OUT -------------

def mo_index(request):
  settings = Settings.objects.settings()
  items = MoveOutItem.objects.all()
  context = { 'settings': settings, 'items': items, }
  return render(request, 'mimo/mo_index.html', context)

class MoveOutIndexView(generic.ListView):
  template_name = 'mimo/mo_index.html'
  context_object_name = 'items'
  model = MoveOutItem

def mo_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(MoveOutItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/mo_detail.html', context)

class MoveOutDetailView(generic.DetailView):
  template_name = 'mimo/mo_detail.html'
  context_object_name = 'item'
  model = MoveOutItem

# ----------- SETTINGS -------------

def set_mode(request):
  if request.method == 'POST':
    form = SettingsModeForm(request.POST)
    if form.is_valid():
      Settings.objects.SetMode(form.cleaned_data['mode'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsModeForm(initial={'mode': settings.mode})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_container(request):
  if request.method == 'POST':
    form = SettingsContainerForm(request.POST)
    if form.is_valid():
      Settings.objects.SetContainer(form.cleaned_data['container'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsContainerForm(initial={'container': settings.container})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_room(request):
  if request.method == 'POST':
    form = SettingsRoomForm(request.POST)
    if form.is_valid():
      Settings.objects.SetRoom(form.cleaned_data['room'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsRoomForm(initial={'room': settings.room})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_kind(request):
  if request.method == 'POST':
    form = SettingsKindForm(request.POST)
    if form.is_valid():
      Settings.objects.SetKind(form.cleaned_data['kind'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsKindForm(initial={'kind': settings.kind})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_subkind(request):
  if request.method == 'POST':
    form = SettingsSubkindForm(request.POST)
    if form.is_valid():
      Settings.objects.SetSubkind(form.cleaned_data['subkind'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsSubkindForm(initial={'subkind': settings.subkind})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_group(request):
  if request.method == 'POST':
    form = SettingsGroupForm(request.POST)
    if form.is_valid():
      Settings.objects.SetGroup(form.cleaned_data['group'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsGroupForm(initial={'group': settings.group})
    return render(request, 'mimo/settings_form.html', { 'form': form })


def set_supplier(request):
  if request.method == 'POST':
    form = SettingsSupplierForm(request.POST)
    if form.is_valid():
      Settings.objects.SetSupplier(form.cleaned_data['supplier'])
      return HttpResponseRedirect(reverse('plan_index'))
  else:
    # Initialise the form from Settings.object.settings()
    settings = Settings.objects.settings()
    form = SettingsSupplierForm(initial={'supplier': settings.supplier})
    return render(request, 'mimo/settings_form.html', { 'form': form })
