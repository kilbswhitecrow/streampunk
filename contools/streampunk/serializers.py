# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2014 Stephen Kilbane
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

"""
Serializers, to support a RESTful interface.
"""

from django.forms import widgets

from rest_framework import serializers

from .models import Item, Room, Person, Slot, SlotLength, Grid

class GridSlotSerializer(serializers.ModelSerializer):
  class Meta:
    model = Slot

class GridSlotLengthSerializer(serializers.ModelSerializer):
  class Meta:
    model = SlotLength

class GridRoomSerializer(serializers.ModelSerializer):
  class Meta:
    model = Room
    fields = ('id', 'name')

class GridPersonSerializer(serializers.ModelSerializer):
  name = serializers.CharField(source='as_badge')
  class Meta:
    model = Person
    fields = ('id', 'name' )

class GridItemSerializer(serializers.ModelSerializer):
  slots = GridSlotSerializer(many=True, source='slots', read_only=True, required=False)
  people = GridPersonSerializer(many=True, source='people', read_only=True, required=False)
  class Meta:
    model = Item
    fields = ('id', 'title', 'room', 'start', 'length', 'slots', 'people')
    # Only room and start can be written-to.
    read_only_fields = ('id', 'title', 'length')

class GridSerializer(serializers.ModelSerializer):
  slots = GridSlotSerializer(many=True, source='slots', read_only=True, required=False)
  items = GridItemSerializer(many=True, read_only=True, required=False)
  class Meta:
    model = Grid


