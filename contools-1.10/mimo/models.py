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

from __future__ import unicode_literals

from django.db import models

from streampunk.models import Room

class Supplier(models.Model):
  """
  Suppliers covers hire companies, the venue's own gear, and individual's loaners.
  """
  name = models.CharField(max_length=128)

  def __str__(self):
    return self.name

class ContainerType(models.Model):
  """
  We use ContainerType to provide an extensible list of the sort of things that
  gear can come in, but the most likely values are:
  - none
  - Flight Case - large rect
  - Flight Case - large square
  - Flight Case - small
  - Soft Cover
  - Small bag
  - Cardboard box
  """
  name = models.CharField(max_length=32)

  def __str__(self):
    return self.name

class Container(models.Model):
  """
  We use Container to identify:
  - what the item arrived in.
  - where the item is currently stored.
  - what we're returning the item in.
  """
  name = models.CharField(max_length=64)
  type = models.ForeignKey(ContainerType, on_delete=models.CASCADE)
  parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)

  def __str__(self):
    return self.name

SettingModes = (
  ('Plan', 'Planning'),
  ('MI',   'Move In'),
  ('Live', 'Live event'),
  ('MO',   'Move Out'),
)

class Settings(models.Model):
  """
  MIMO is a modal app; we want the user to be selecting
  defaults so that we can apply them when carrying out
  operations.
  """
  mode = models.CharField(max_length=16, choices=SettingModes, default='Plan')
  container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True)
  room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)

  def __str__(self):
    return 'Settings'

class TechKind(models.Model):
  """
  An extensible enumeration of the sort of thing that an item can be.
  E.g. cable, light, mic.
  """
  name = models.CharField(max_length=32)

  def __str__(self):
    return self.name

class TechSubkind(models.Model):
  """
  An extensible enumeration of the sort of thing that an item can be.
  E.g. DMX, Profile, handheld.
  """
  name = models.CharField(max_length=32)

  def __str__(self):
    return self.name

class TechGroup(models.Model):
  """
  We use TechGroup to provide a meaningful grouping of gear, e.g.
  staging, stage lighting, stage audio, disco lighting, and so on.
  """
  name = models.CharField(max_length=64)
  description = models.CharField(max_length=256, blank=True)

  def __str__(self):
    return self.name

MoveInStateValues = (
                                    # MOVE IN STATES
  ('Received',     'Received'),     # Turned up as expected.
  ('Not Received', 'Not Received'), # Asked for it, it didn't arrive.
  ('Extra',        'Extra'),        # Didn't ask for it, it arrived anyway.
  ('Replaced',     'Replaced'),     # Asked for it, got something else instead.
  ('Faulty',       'Faulty'),       # Received as requested, but not usable.
)

LiveStateValues = (
                                    # LIVE STATES
  ('Deployed',     'Deployed'),     # Now in use in the event.
  ('Spare',        'Spare'),        # Awaiting use.
)

MoveOutStateValues = (
                                    # MOVE OUT STATES
  ('Returned',     'Returned'),     # Packed away ready for return.
  ('Lost',         'Lost'),         # Vanished during the event.
  ('Broken',       'Broken'),       # Damaged during the event, repairable.
  ('Consumed',     'Consumed'),     # Consumable used up during the event.
  ('Destroyed',    'Destroyed'),    # Damaged beyond repair during the event.
)

class TechItem(models.Model):
  """
  A TechItem is either a single item, or a collection, according to count. So we
  could have a DMX 10m cable, or 20 DMX 10m cables. TechItems can be created with
  a count during Planning, for convenience, and then divided up into smaller
  groups during Move In.
  """
  group = models.ForeignKey(TechGroup, on_delete=models.SET_NULL, null=True)
  supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
  code = models.CharField(max_length=32, blank=True)
  kind = models.ForeignKey(TechKind, on_delete=models.CASCADE)
  subkind = models.ForeignKey(TechSubkind, on_delete=models.CASCADE)
  container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True)
  room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
  count = models.IntegerField(default=1)
  state = models.CharField(max_length=32, blank=True)

  def name(self):
    if self.count > 1:
      num = ' x %d' % (self.count)
    else:
      num = ''
    if self.subkind:
      desc = self.subkind
    elif self.kind:
      desc = self.kind
    elif self.code:
      desc = self.code
    else:
      desc = '(unknown)'
    return '%s%s' % (desc, num)

class PlanItem(models.Model):
  item = models.ForeignKey(TechItem, on_delete=models.CASCADE)
  def __str__(self):
    return 'Plan:%s' % (self.name())

class MoveInItem(models.Model):
  item = models.ForeignKey(TechItem, on_delete=models.CASCADE)
  plan = models.ForeignKey(PlanItem, on_delete=models.SET_NULL, null=True)
  def __str__(self):
    return 'Plan:%s' % (self.name())

class LiveItem(models.Model):
  item = models.ForeignKey(TechItem, on_delete=models.CASCADE)
  mi = models.ForeignKey(MoveInItem, on_delete=models.SET_NULL, null=True)
  def __str__(self):
    return 'Plan:%s' % (self.name())

class MoveOutItem(models.Model):
  item = models.ForeignKey(TechItem, on_delete=models.CASCADE)
  live = models.ForeignKey(LiveItem, on_delete=models.SET_NULL, null=True)
  def __str__(self):
    return 'Plan:%s' % (self.name())


