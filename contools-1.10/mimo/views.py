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
from django.urls import reverse
from django.views import generic

from .models import Settings
from .models import TechItem, PlanItem, MoveInItem, LiveItem, MoveOutItem

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

def plan_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(PlanItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/plan_detail.html', context)

class PlanDetailView(generic.DetailView):
  template_name = 'mimo/plan_detail.html'
  context_object_name = 'item'
  model = PlanItem

# ----------- MOVE IN -------------

def mi_index(request):
  settings = Settings.objects.settings()
  items = MoveInItem.objects.all()
  context = { 'settings': settings, 'items': items, }
  return render(request, 'mimo/mi_index.html', context)

class MoveInIndexView(generic.ListView):
  template_name = 'mimo/mi_index.html'
  context_object_name = 'items'
  model = MoveInItem

def mi_detail(request, pk):
  settings = Settings.objects.settings()
  item = get_object_or_404(MoveInItem, pk=pk)
  context = { 'settings': settings, 'item': item, }
  return render(request, 'mimo/mi_detail.html', context)

class MoveInDetailView(generic.DetailView):
  template_name = 'mimo/mi_detail.html'
  context_object_name = 'item'
  model = MoveInItem

# ----------- LIVE -------------

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

