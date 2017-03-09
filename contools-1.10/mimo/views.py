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

from django.shortcuts import render
from django.http import HttpResponse

from .models import Settings
from .models import TechItem, PlanItem, MoveInItem, LiveItem, MoveOutItem

# Create your views here.

def index(request):
  settings = Settings.objects.settings()
  context = { 'settings': settings, }
  return render(request, 'mimo/index.html', context)

def plan_index(request):
  return HttpResponse("Mimo plan_Index view needs writing.")

def mi_index(request):
  return HttpResponse("Mimo mi_Index view needs writing.")

def live_index(request):
  return HttpResponse("Mimo live_Index view needs writing.")

def mo_index(request):
  return HttpResponse("Mimo mo_Index view needs writing.")
