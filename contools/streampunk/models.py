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

"""
Models for Streampunk
"""

from datetime import timedelta, datetime
from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from .tabler import Rower
from .exceptions import DeleteDefaultException, DeleteUndefException

YesNo = (
  ( 'TBA', 'TBA'),
  ( 'Yes', 'Yes' ), 
  ( 'No', 'No'),
)

class DefUndefManager(models.Manager):
  """
  A manager that has extra methods for finding the default/undefined
  values based on fields.
  """
  def find_default(self):
    return self.get(isDefault=True)
  def find_undefined(self):
    return self.get(isUndefined=True)

def avail_for_slots(avail, slots):
  """
  avail and slots are both querysets of slots. Return true if all of
  the slots listed in slots are also listed in avail, and false otherwise.
  """
  avail_set = set([ s.id for s in avail ])
  slots_set = set([ s.id for s in slots ])
  not_covered = slots_set - avail_set
  return len(not_covered) == 0

class ConInfoBoolManager(models.Manager):
  "A manager that knows how to look up certain flags within the database."
  def show_shortname(self):
    return self.get(var='show_shortname').val
  def rooms_across_top(self):
    return self.get(var='rooms_across_top').val
  def no_avail_means_always_avail(self):
    return self.get(var='no_avail_means_always_avail').val

class ConInfoBool(models.Model):
  """
  Boolean flags, for making con-wide preference selections. This is used to
  create var=True or var=False configuration choices.
  """
  name = models.CharField(max_length=64,
                          help_text='A descriptive name for this flag')
  var = models.SlugField(max_length=64,
                         help_text='The name used internally to access this flag: Alphanumerics only, no whitespace')
  val = models.BooleanField(default=False,help_text="The flag's value")
  objects = ConInfoBoolManager()
  def __unicode__(self):
    return self.name

class ConInfoIntManager(models.Manager):
  "A manager that knows how to look up integer variables in the database."
  def max_items_per_day(self):
    return self.get(var='max_items_per_day').val
  def max_items_whole_con(self):
    return self.get(var='max_items_whole_con').val
  def max_consecutive_items(self):
    return self.get(var='max_consecutive_items').val

class ConInfoInt(models.Model):
  """
  These objects are integer con-wide configuration values, such as how many
  items per day you can programme a person, before the corresponding check
  will consider it a problem. Objects should be var=N form.
  """
  name = models.CharField(max_length=64,
                          help_text="A descriptive name for this variable")
  var = models.SlugField(max_length=64,
                         help_text="The internal name of the variable. Alphanumerics only, no whitespace")
  val = models.IntegerField(help_text="The value for the variable.")
  objects = ConInfoIntManager()
  def __unicode__(self):
    return self.name

class ConInfoStringManager(models.Manager):
  "A manager that knows how to look up certain strings in the database."
  def con_name(self):
    return self.get(var='con_name').val
  def email_from(self):
    return self.get(var='email_from').val

class ConInfoString(models.Model):
  """
  These objects are string-typed con-wide configuration values. The most
  significant one is the name of the convention itself.
  """
  name = models.CharField(max_length=64,
                          help_text="A descriptive name for this variable")
  var = models.SlugField(max_length=64,
                         help_text="The internal name of the variable. Alphanumerics only, no whitespace")
  val = models.CharField(max_length=256,
                         help_text="The value for the variable.")
  objects = ConInfoStringManager()
  def __unicode__(self):
    return self.name


class ConDayManager(DefUndefManager):
  "A manager with some convenience methods."
  def earliest_day(self):
    return self.exclude(isUndefined=True).earliest()
  def earliest_public_day(self):
    return self.filter(visible=True, isUndefined=False).earliest()
  def latest_day(self):
    return self.exclude(isUndefined=True).latest()
  def latest_public_day(self):
    return self.filter(visible=True, isUndefined=False).latest()

class ConDay(models.Model):
  """
  A ConDay is how we map from a given date to
  a name, and whether it's a public date.
  """
  name = models.CharField(max_length=24,
                          help_text="The name of the day, e.g. Friday, or Bank Holiday Monday")
  date = models.DateField(help_text="The actual date of the day.")
  order = models.IntegerField(help_text="This could be used for determining the order in which days are listed. Currently ignored.")
  visible = models.BooleanField(default=False,help_text="Should this day be displayed in the official programme?")
  isDefault = models.BooleanField(default=False,help_text="True if this is the default day for items. Set this for <em>exactly one</em> day.")
  isUndefined = models.BooleanField(default=False,help_text="True if this day means 'to be decided'. Items on this day are considered unscheduled.")
  objects = ConDayManager()

  class Meta:
    # XXX - why are we not using order, here?
    ordering = [ 'order' ]
    get_latest_by = 'date'

  def __unicode__(self):
    return self.name

class SlotLength(models.Model):
  "A SlotLength is how long a given item may run."
  name = models.CharField(max_length=30,
                          help_text="The name of this slot, e.g. '1 hour'")
  length = models.IntegerField(default=60,
                               help_text="The duration of the slot, in minutes.")
  isDefault = models.BooleanField(default=False,help_text="True if this is the default choice for an item. <em>Set this on exactly one slot</em>.")
  isUndefined = models.BooleanField(default=False,help_text="True if this value means 'to be decided'. Set this on <em>exactly one</em> slot. Items with this length are considered problematic by checks.")
  objects = DefUndefManager()

  class Meta:
    ordering = [ 'isDefault', 'length' ]

  def __unicode__(self):
    return self.name

class Slot(models.Model):
  """
  a Slot is a potential position in the day at which
  an item may start.
  """
  start = models.IntegerField(help_text="When the slot will start, in minutes after midnight.")
  length = models.ForeignKey(SlotLength, default=SlotLength.objects.find_default,
                             help_text="How long the slot lasts, in the programme")
  day = models.ForeignKey(ConDay, default=ConDay.objects.find_default,
                             help_text="Which day this slot occurs on")
  startText = models.CharField(max_length=20,
                               help_text="A convenient label for the slot, e.g. 7pm")
  slotText = models.CharField(max_length=20,
                               help_text="A label for the duration of the slot, e.g. 7-8pm")
  visible = models.BooleanField(default=True,
                                help_text="True if the slot should be visible in the printed programme")
  isDefault = models.BooleanField(default=False,help_text="True if this should be the default slot for an item. Set this on <em>exactly one</em> slot")
  isUndefined = models.BooleanField(default=False,help_text="True if this value means 'to be decided.' Set this on <em>exactly one</em> slot. Items starting in this slot are considered unscheduled.")
  order = models.IntegerField(help_text="This is used for determining the order in which slots are listed.")
  objects = DefUndefManager()

  class Meta:
    ordering = [ 'order' ]

  def __unicode__(self):
    return "%s %s" % (self.day, self.startText)
    # return self.startText
  def get_absolute_url(self):
    return reverse('show_slot_detail', kwargs={"pk": self.id})

  def items(self, room=None):
    """
    Returns the list of items that are on (but may start earlier) during
    this slot.
    """
    all = Item.objects.filter(start__day=self.day, start__start__lte=self.start)
    if room:
      all = all.filter(room=room)
    overlaps = [ i for i in all if (self.start < (i.start.start + i.length.length)) ]
    return overlaps

  def items_public(self, room=None):
    """
    Returns the list of items that are on (but may start earlier) during
    this slot. Filters out things that are not visible.
    """
    return [ i for i in self.items(room) if i.visible ]

  def items_starting(self, room=None):
    """
    Returns the list of items that start in this slot.
    """
    if room:
      return Item.objects.filter(start=self, room=room)
    else:
      return Item.objects.filter(start=self)

  @classmethod
  def rower(cls, request):
    return Rower({  "pk":          "pk",
                    "slot":    "__unicode__" })
  @classmethod
  def tabler_exclude(cls, request):
    return None


class Grid(models.Model):
  """
  A Grid is a collection of slots that get displayed together.
  """
  name = models.CharField(max_length=40,
                          help_text="A label for the period covered by the slots, e.g. 'Midday-4pm'")
  slots = models.ManyToManyField(Slot,
                                 help_text="The slots within the period of the grid. The slots should be consecutive.")
  gridOrder = models.IntegerField(default=1,
                                  help_text="The grids will be displayed in ascending order of this field.")

  class Meta:
    ordering = ['gridOrder']

  def __unicode__(self):
    return self.name

  @classmethod
  def rower(cls, request):
    return Rower({  "pk":      "pk",
                    "name":    "name" })
  @classmethod
  def tabler_exclude(cls, request):
    return None

class Revision(models.Model):
  """
  A Revision tells us when an item was last modified. We create a new one
  when we think the programme's in a good state, then we mark each item
  with the current revision when we change the item.
  """
  baseline = models.DateTimeField(help_text="This is when the set of changes began.")
  colour = models.CharField(max_length=20, help_text="This should be the name of a CSS style, to control how items in this revision should be displayed.")
  description = models.TextField(help_text="A description of this baseline of the programme")

  class Meta:
    ordering = [ '-baseline' ]
    get_latest_by = 'baseline'

  def __unicode__(self):
    return self.description

class EnumManager(DefUndefManager):
  pass

class EnumTable(models.Model):
  "A generic class for named lists of choices."
  name = models.CharField(max_length=64, help_text="The name for this choice.")
  isDefault = models.BooleanField(default=False,help_text="True if objects for this class should default to this value. Set this for <em>exactly one</em> value.")
  isUndefined = models.BooleanField(default=False,help_text="True is this value means 'to be decided'. Set this for <em>exactly one</em> value.")
  gridOrder = models.IntegerField(default=1,
                                  help_text="The choices for this class are displayed in ascending order of this field")
  description = models.TextField(blank=True,
                                 help_text="An explanation of this value")

  objects = EnumManager()

  class Meta:
    ordering = [ 'gridOrder' ]
    abstract = True

  def __unicode__(self):
    return self.name

  def delete_replacement(self):
    "Returns what we should reassign to, when deleting this value."
    if self.isUndefined:
      raise DeleteUndefException
    if self.isDefault:
      raise DeleteDefaultException
    return self.__class__.objects.get(isUndefined=True)

class ItemKind(EnumTable):
  """
  An Item's ItemKind tells you what kind of activity
  the item is.
  """
  def delete(self):
    self.item_set.all().update(kind=self.delete_replacement())
    return super(ItemKind, self).delete()

  @classmethod
  def rower(cls, request):
    return Rower({ "kind": "kind__name", "count": "kind__count" })
  @classmethod
  def tabler_exclude(cls, request):
    return None

class SeatingKind(EnumTable):
  """
  An Item's SeatingKind tells you how the item's
  room should be laid out.
  """
  def delete(self):
    self.item_set.all().update(seating=self.delete_replacement())
    return super(SeatingKind, self).delete()


class FrontLayoutKind(EnumTable):
  """
  Used to describe how the front of the room - where panellist or a stage is - should be laid out.
  """
  def delete(self):
    self.item_set.all().update(frontLayout=self.delete_replacement())
    return super(FrontLayoutKind, self).delete()


class PersonRole(EnumTable):
  """
  A PersonRole defines the person's job, for
  a given Item
  """
  def delete(self):
    self.itemperson_set.all().update(role=self.delete_replacement())
    return super(PersonRole, self).delete()


class PersonStatus(EnumTable):
  """
  A PersonStatus indicates how confident you are
  that a person will turn up and carry out their role.
  """
  class Meta:
    verbose_name = 'Person Status'
    verbose_name_plural = 'Person Statuses'
  def delete(self):
    self.itemperson_set.all().update(status=self.delete_replacement())
    return super(PersonStatus, self).delete()


class Gender(EnumTable):
  """
  A Gender allows you to determine whether you have
  a suitable balance on your programme.
  """
  def delete(self):
    self.person_set.all().update(gender=self.delete_replacement())
    return super(Gender, self).delete()

  @classmethod
  def rower(cls, request):
    return Rower({ "gender": "person__gender__name", "count": "person__gender__count" })
  @classmethod
  def tabler_exclude(cls, request):
    return None


class Tag(models.Model):
  """
  A Tag is an arbitrary piece of information about Items,
  People, etc.
  """
  name = models.CharField(max_length=64,
                          help_text="The name for the tag")
  description = models.TextField(blank=True,
                                 help_text="An explanation of what this tag means")
  icon = models.URLField(blank=True,
                         help_text="You can make this the URL of an image, in which case the image can be displayed on the grids")
  visible = models.BooleanField(default=True,
                                help_text="Set this if the tag should be visible in the printed programme")

  class Meta:
    verbose_name = 'tag'
    verbose_name_plural = 'tags'
    ordering = [ 'name' ]

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_tag_detail', kwargs={"pk": self.id})

  def as_xml_public(self):
    return render_to_string('xml/tag_public.xml', { "t": self } )
  def as_xml(self):
    return render_to_string('xml/tag.xml', { "t": self } )

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":          "id",
                   "name":        "name",
                   "visible":     "visible",
                   "description": "description",
                   "edit":        "Edit",
                   "remove":      "Remove" })
  @classmethod
  def tabler_exclude(cls, request):
    if request.user.has_perm('progb2.read_private'):
      if request.user.has_perm('progb2.edit_programme'):
        return None
      else:
        return ['edit', 'remove']
    else:
        return ['edit', 'remove', 'visible']


# Kit is physical stuff. It can be technical equipment, like a DVD player, or
# something non-tech like a flip-chart or laminator. It's something that you
# want to keep track of, to make sure it's available in the right place at the
# right time.

class KitKind(EnumTable):
  "What kind of kit this is, e.g. DVD player, flip chart."
  def delete(self):
    rep=self.delete_replacement()
    self.kitthing_set.all().update(kind=rep)
    self.kitrequest_set.all().update(kind=rep)
    return super(KitKind, self).delete()


class KitRole(EnumTable):
  "The purpose for this bit of kit, in the item, e.g. stage mic vs audience mic."
  def delete(self):
    self.kitthing_set.all().update(role=self.delete_replacement())
    return super(KitRole, self).delete()


class KitDepartment(EnumTable):
  "Which con dept is responsible for managing this bit of kit."
  def delete(self):
    self.kitthing_set.all().update(department=self.delete_replacement())
    return super(KitDepartment, self).delete()


class KitSource(EnumTable):
  "Where you're getting this bit of kit from."
  def delete(self):
    self.kitthing_set.all().update(source=self.delete_replacement())
    return super(KitSource, self).delete()


class KitBasis(EnumTable):
  "On what basis are you obtaining this bit of kit. Borrow, hire, buy, etc."
  def delete(self):
    self.kitthing_set.all().update(basis=self.delete_replacement())
    return super(KitBasis, self).delete()


class MediaStatus(EnumTable):
  "If an item requires some media as well, what is the status of the provision of that media"
  def delete(self):
    self.item_set.all().update(mediaStatus=self.delete_replacement())
    return super(MediaStatus, self).delete()


class KitStatus(EnumTable):
  "What is the status of this bit of kit? Is it properly sorted?"
  def delete(self):
    rep=self.delete_replacement()
    self.kitthing_set.all().update(status=rep)
    self.kitrequest_set.all().update(status=rep)
    return super(KitStatus, self).delete()

class KitSatisfaction(object):
  """
  An indication of how well an item's requests are satisfied.
  Note: Not a model class.
  """

  def count_things(self, pairs):
    d = dict([ (k,0) for (k,v) in pairs])
    for (k,v) in pairs:
      d[k] += v
    return d

  def __init__(self, i):
   self.item = i

   # Each of the Map members is a dict, mapping KitKind id onto a count.
   # What the item wants
   self.requestMap = self.count_things([ (r.kind.id, r.count) for r in self.item.kitRequests.all() ])
   # What the item provides
   self.itemMap = self.count_things([ (kia.thing.kind.id, kia.thing.count) for kia in KitItemAssignment.objects.filter(item=self.item) ])
   # What the room provides
   self.roomMap = self.count_things([ (kra.thing.kind.id, kra.thing.count) for kra in KitRoomAssignment.objects.filter(room=self.item.room) if kra.covers(self.item) ])
   # Total of the two
   self.totalMap = self.count_things(self.itemMap.items() + self.roomMap.items())

   # Are there enough of each requested kind, in total?
   # Let's start off assuming there are.
   self.satisfied = True
   self.missingMap = dict()

   # Now let's take a look.
   for (thing, count) in self.requestMap.items():
     if thing in self.totalMap:
       if self.totalMap[thing] >= count:
         # We have enough. Yay.
         pass
       else:
         # We have some, but not enough. Boo.
         self.satisfied = False
         self.missingMap[thing] = count - self.totalMap[thing]
     else:
       # We don't have any. Uh-oh.
       self.satisfied = False
       self.missingMap[thing] = count

  def missing_things(self):
    "Return a list of (KitKind, count) pairs of things we still need for this item"
    return [ (kind, self.missingMap[kind.id]) for kind in KitKind.objects.filter(id__in=self.missingMap.keys()) ]

class KitRequest(models.Model):
  """
  Items can have kit requests. These are a record of what kind of kit the
  item requires. The request can be satisfied by kit assigned to the room
  that the item is in, or by directly assigning kit to the item.
  """
  kind = models.ForeignKey(KitKind, default=KitKind.objects.find_default,
                           help_text="What kind of kit does this item need?")
  count = models.SmallIntegerField(default=1,
                                   help_text="How many instances of that kit does the item require?")
  setupAssistance = models.BooleanField(default=False,help_text="Set this if the item's participants require Tech Crew to come in and help set up the kit")
  notes = models.TextField(blank=True,
                           help_text="Any additional information required.")
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default,
                             help_text="Has this request been sorted out?")

  class Meta:
    verbose_name = 'kitrequest'
    verbose_name_plural = 'kitrequests'

  def __unicode__(self):
    return u"%s: %d" % (self.kind, self.count)
  def get_absolute_url(self):
    return reverse('show_kitrequest_detail', kwargs={"pk": self.id})

  def as_xml_public(self):
    return render_to_string('xml/kitrequest_public.xml', { "kr": self } )
  def as_xml(self):
    return render_to_string('xml/kitrequest.xml', { "kr": self } )

  def okay_to_edit(self):
    "This should never return false, because the same Request shouldn't be used by multiple items."
    return self.item_set.count() < 2

  def okay_to_delete(self):
    "This should never return false, because the same Request shouldn't be used by multiple items."
    return self.item_set.count() < 2

  def requested_by_first(self):
    return self.item_set.all()[0]

  def requested_by_first_room(self):
    return self.requested_by_first().room

  def requested_by_first_start(self):
    return self.requested_by_first().start

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":     "id",
                  "name":   "__str__",
                  "kind":   "kind",
                  "count":  "count",
                  "status": "status",
                  "setup":  "setupAssistance",
                  "notes":  "notes",
                  "item":   "requested_by_first",
                  "room":   "requested_by_first_room",
                  "start":  "requested_by_first_start",
                  "edit":   "Edit",
                  "remove": "Remove" })

  @classmethod
  def tabler_exclude(cls, request):
    return None

class KitThing(models.Model):
  """
  A kit thing is an instance of the physical kit. Or, possible, several instances which
  you're moving around as an indivisible unit. Kit things can be assigned to rooms or
  to items, which you do to satisfy kit requests.
  """
  name = models.CharField(max_length=64,
                          help_text="The name of this bit of kit. Be descriptive so that you can distinguish similar things.")
  description = models.TextField(blank=True,
                                 help_text="Additional information, if necessary.")
  kind = models.ForeignKey(KitKind, default=KitKind.objects.find_default,
                           help_text="What kind of kit thing this is.")
  count = models.SmallIntegerField(default=1,
                                   help_text="How many instances are there in this thing? They must always be kept together.")
  role = models.ForeignKey(KitRole, default=KitRole.objects.find_default,
                           help_text="The purpose of this bit of kit, in the item")
  source = models.ForeignKey(KitSource, default=KitSource.objects.find_default,
                             help_text="Who's providing this bit of kit to the event")
  department = models.ForeignKey(KitDepartment, default=KitDepartment.objects.find_default,
                                 help_text="Which dept is responsible for managing this bit of kit")
  basis = models.ForeignKey(KitBasis, default=KitBasis.objects.find_default,
                            help_text="Are you borrowing this kit? Buying it?")
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default,
                             help_text="Is this bit of kit sorted?")
  cost = models.IntegerField(default=0,
                             help_text="How much is this going to hit the budget?")
  insurance = models.IntegerField(default=0,
                                  help_text="What is the value of the kit, for insurance purposes?")
  notes = models.TextField(blank=True,
                           help_text="Any additional notes required")
  coordinator = models.CharField(max_length=64,
                                 help_text="The name of the person responsible for sourcing this bit of kit")
  availability = models.ManyToManyField(Slot, null=True, blank=True,
                                        help_text="The slots during when the kit is available for allocation")

  class Meta:
    verbose_name = 'kitthing'
    verbose_name_plural = 'kitthings'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_kitthing_detail', kwargs={"pk": self.id})

  def as_xml_public(self):
    return render_to_string('xml/kitthing_public.xml', { "kt": self } )
  def as_xml(self):
    return render_to_string('xml/kitthing.xml', { "kt": self } )

  def always_available(self):
    """
    Return true if there are no slots where the thing is not available.
    If there are no slots listed, then it's a con preference whether that
    means "always available" or never available".
    """
    return self.availability.count() == 0 and ConInfoBool.objects.no_avail_means_always_avail()

  def never_available(self):
    """
    Return true if there are no slots listed, and that should be interpreted
    as 'never available'.
    """
    return self.availability.count() == 0 and not ConInfoBool.objects.no_avail_means_always_avail()

  def available_for(self, item):
    """
    Return true if the item falls entirely within one of the kit thing's periods of
    availability. If the thing has NO availability listed, that might be a problem,
    or it might mean it's always available - con preference.
    NOTE: "item" might actually be a Room, not an Item.
    """
    return self.always_available() or avail_for_slots(self.availability.all(), item.slots()) 

  def in_use(self):
    return self.kitbundle_set.exists() or self.kititemassignment_set.exists() or self.kitroomassignment_set.exists()
  def okay_to_edit(self):
    return (self.kitbundle_set.count() + self.kititemassignment_set.count() + self.kitroomassignment_set.count()) < 2
  def okay_to_delete(self):
    return not self.in_use()

  @classmethod
  def rower(cls, request=None):
    return Rower({ "pk":     "id",
                   "name":   "name",
                   "kind":   "kind",
                   "count":  "count",
                   "notes":  "notes",
                   "edit":   "Edit",
                   "remove": "Remove" })
  @classmethod
  def tabler_exclude(cls, request):
    return None if request.user.has_perm('progb2.edit_tech') else ['remove']

class KitBundle(models.Model):
  """
  A kit bundle is a collection of kit things that you can assign to a room or an
  item as one, although the kit things are managed separately as well.
  """
  name = models.CharField(max_length=64,
                          help_text="The name of the bundle. Make sure you can distinguish bundles by name")
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default,
                             help_text="Is this bundle sorted?")
  things = models.ManyToManyField(KitThing,
                                  help_text="The things that make up this bundle")

  class Meta:
    verbose_name = 'kitbundle'
    verbose_name_plural = 'kitbundles'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_kitbundle_detail', kwargs={"pk": self.id})

  def things_all(self):
     return self.things.all()
  def rooms_unique(self):
    "Provide a set of the rooms using this bundle (so each room appears once)"
    return set([ kra.room for kra in KitRoomAssignment.objects.order_by('room').filter(bundle=self) ])
  def items_unique(self):
    "Provide a set of the items using this bundle (so each items appears once)"
    return set([ kia.item for kia in KitItemAssignment.objects.order_by('item').filter(bundle=self) ])

  def room_count(self):
    return len(self.rooms_unique())
  def item_count(self):
    return len(self.items_unique())

  def in_use(self):
    if self.room_count() > 0:
      return True
    if self.item_count() > 0:
      return True
    return False

  def okay_to_edit(self):
    return (self.room_count() + self.item_count()) < 2
  def okay_to_delete(self):
    return not self.in_use()

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":       "pk",
                   "name":     "name",
                   "status":   "status",
                   "things":   "things_all",
                   "rooms":    "rooms_unique",
                   "used_by":  "items_unique",
                   "remove":   "Remove" })
  @classmethod
  def tabler_exclude(cls, request):
    return None if request.user.has_perm('progb2.edit_tech') else ['remove']

class KitRoomAssignment(models.Model):
  """
  You can assign kit to rooms, either thing-by-thing, or as part of a bundle.
  The assignment is for a period, so you might have a screen in one room for one day,
  and then in another room for the following day. Kit assigned to a room can satisfy
  kit requests for items that take place in that room.
  """
  room = models.ForeignKey('Room',
                           help_text="The room to which you're assigning the kit")
  thing = models.ForeignKey(KitThing,
                            help_text="If you're assigning a single kit thing, choose it here.")
  bundle = models.ForeignKey(KitBundle, null=True, blank=True,
                             help_text="the bundle which assigned this thing to the room, if part of a bundle assignment.")
  fromSlot = models.ForeignKey(Slot, related_name='kitroomfrom_set',
                               help_text="The slot at which the assignment starts. The kit thing can satisfy requests that need the kit in this slot")
  toSlot = models.ForeignKey(Slot, related_name='kitroomto_set',
                             help_text="The last slot for this assignment. The assignment can satisfy items that are in this slot.")
  toLength = models.ForeignKey(SlotLength,
                               help_text="The length of the final slot assignment. At the end of this length, the assignment ends.")

  def __unicode__(self):
    return u"%s in %s" % (self.thing, self.room)
  def get_absolute_url(self):
    return reverse('show_kitroomassignment_detail', kwargs={"pk": self.id})

  def starts_before_slot(self, slot, mins):
    """
    Return true if this assignment begins before (or at the same time as) this many minutes
    past the given slot.
    """
    return (   self.fromSlot.day.date < slot.day.date
            or (    self.fromSlot.day.date == slot.day.date 
                and self.fromSlot.start <= slot.start))

  def finishes_after_slot(self, slot, mins):
    """
    Returns true if the assignment lasts until at least the end of this day/slot.
    """
    return (   slot.day.date < self.toSlot.day.date
            or (    slot.day.date == self.toSlot.day.date
                and (slot.start + mins) <= (self.toSlot.start + self.toLength.length)))


  def starts_before(self, item):
    "True if the assignment starts before the item does."
    return self.starts_before_slot(item.start, 0)

  def finishes_after(self, item):
    "True if the assignment finishes after the item does"
    return self.finishes_after_slot(item.start, item.length.length)

  def covers(self, item):
    "True if the assignment entirely encompasses the period for the item."
    r = self.starts_before(item) and self.finishes_after(item)
    return r

  def overlaps(self, item):
    "True if any part of the assignment is concurrent with any part of the item."
    return (    self.starts_before_slot(item.start, item.length.length)
            and self.finishes_after_slot(item.start, item.length.length))

  def overlaps_room_assignment(self, other):
    "True if any part of the assignment is concurrent with the other assignment."
    return (    self.starts_before_slot(other.toSlot, 0)
            and self.finishes_after_slot(other.fromSlot, 0))

  def slots(self):
    "Return a queryset of the slots this assignment occupies"
    return Slot.objects.filter(day=self.fromSlot.day, start__gte=self.fromSlot.start, start__lt=self.toSlot.start+self.toLength.length)

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":       "id",
                   "thing":    "thing",
                   "bundle":   "bundle",
                   "room":     "room",
                   "fromSlot": "fromSlot",
                   "toSlot":   "toSlot",
                   "remove":   "Remove" })
  @classmethod
  def tabler_exclude(cls, request):
    return None if request.user.has_perm('progb2.edit_tech') else ['remove']

  
class KitItemAssignment(models.Model):
  """
  A kit item assignment assigns a kit thing directly to an item, either directly or as part
  of a bundle. The assignment can then satisfy kit requests of the item.
  """
  item = models.ForeignKey('Item',
                           help_text="The item we're assigning the thing to")
  thing = models.ForeignKey(KitThing,
                            help_text="The thing assigned to the item")
  bundle = models.ForeignKey(KitBundle, null=True, blank=True,
                             help_text="The bundle, if this assignment is part of a bundle.")

  def __unicode__(self):
    return u"%s to %s" % (self.thing, self.item)
  def get_absolute_url(self):
    return reverse('show_kititemassignment_detail', kwargs={"pk": self.id})

  def item_day(self):
    return self.item.start.day
  def item_start(self):
    return self.item.start.startText
  def item_room(self):
    return self.item.room

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":     "id",
                   "thing":  "thing",
                   "bundle": "bundle",
                   "item":   "item",
                   "room":   "item_room",
                   "day":    "item_day",
                   "time":   "item_start",
                   "remove": "Remove" })

  @classmethod
  def tabler_exclude(cls, request):
    return None if request.user.has_perm('progb2.edit_tech') else ['remove']

class RoomCapacity(models.Model):
  """
  Rooms can be laid out in different ways, and they can fit differing numbers of
  people into the room as a result. Each room can have multiple Room Capacities,
  saying how many people can fit in, with that layout. This can be used to check
  against the expected audience for an item.
  """
  layout = models.ForeignKey(SeatingKind, default=SeatingKind.objects.find_default,
                             help_text="How the room is laid out")
  count = models.IntegerField(help_text="How many people can fit into the room, in this layout")

  class Meta:
    verbose_name = 'room-capacity'
    verbose_name_plural = 'room-capacities'

  def __unicode__(self):
    return u"%s: %d" % (self.layout, self.count)

  def as_xml_public(self):
    return render_to_string('xml/capacity_public.xml', { "c": self } )
  def as_xml(self):
    return render_to_string('xml/capacity.xml', { "c": self } )

  @classmethod
  def rower(cls, request):
    return Rower({  "pk":        "pk",
                    "layout":    "layout",
                    "count":     "count" })
  @classmethod
  def tabler_exclude(cls, request):
    return None


class Room(models.Model):
  """
  A Room is where a programme item can take place.
  Every item is in some room somewhere, although we
  have a couple of special rooms for unassigned
  items (Nowhere) or items that don't get a specific
  room (Everywhere).
  """
  name = models.CharField(max_length=64,
                          help_text="The name of the room, as it'll appear in the programme")
  description = models.TextField(blank=True,
                                 help_text="What you'll use this room for")
  visible = models.BooleanField(default=True,
                                help_text="Should it appear on the printed programme?")
  isDefault = models.BooleanField(default=False,help_text="True if this is where items go by default. Set this on <em>exactly one</em> room.")
  isUndefined = models.BooleanField(default=False,help_text="True if this room means 'no room defined'. Items in this room will be considered unscheduled. Set this on <em>exactly one</em> room.")
  canClash = models.BooleanField(default=False,help_text="True if multiple concurrent items in this room should be considered a problem.")
  disabledAccess = models.BooleanField(default=True,
                                       help_text="True if the room is wheelchair-accessible")
  gridOrder = models.IntegerField(default=50,
                                  help_text="The rooms will be displayed in the grid in ascending order of this field")
  privNotes = models.TextField(blank=True,
                               help_text="Pivate notes about the room. <em>Don't</em> put tech-related info here.")
  techNotes = models.TextField(blank=True,
                               help_text="Any additional tech-related information")
  needsSound = models.BooleanField(default=False,help_text="True if items in this room will require amplification")
  naturalLight = models.BooleanField(default=False,help_text="True if the room has its own natural light")
  securable = models.BooleanField(default=False,help_text="True if the room can be securely locked, so that valuables can be left inside")
  controlLightsInRoom = models.BooleanField(default=False,help_text="True if you can control the room's lighting from inside the room")
  controlAirConInRoom = models.BooleanField(default=False,help_text="True if you can control the room's air conditioning from inside the room")
  accessibleOnFlat = models.BooleanField(default=False,help_text="True if you can get to the room without stairs (for trolleys, etc)")
  hasWifi = models.BooleanField(default=False,help_text="True if the room has a usable wifi signal")
  hasCableRuns = models.BooleanField(default=False,help_text="True if the room has usable cable runs")
  openableWindows = models.BooleanField(default=False,help_text="true if the room has windows which you can open")
  closableCurtains = models.BooleanField(default=False,help_text="True if the room has curtains you can close")
  inRadioRange = models.BooleanField(default=False,help_text="True if the radio net can reach people in the room")
  kit = models.ManyToManyField(KitThing, through='KitRoomAssignment', null=True, blank=True,
                               help_text="Kit assigned to the room for a duration. May satisfy items' kit requests.")
  parent = models.ForeignKey('self', null=True, blank=True,
                             help_text="If this room is really part of a larger, subdividable room, set this field to the parent room")
  capacities = models.ManyToManyField(RoomCapacity, null=True, blank=True,
                                      help_text="Use room capacities to indicate how many people can fit in the room in a given layout")
  availability = models.ManyToManyField(Slot, null=True, blank=True,
                                        help_text="Add availabilities to indicate which slots the room is available for.")
  objects = DefUndefManager()

  class Meta:
    ordering = [ 'isDefault', 'gridOrder' ]
    verbose_name = 'room'
    verbose_name_plural = 'rooms'

  def delete(self):
    if self.isUndefined:
      # Don't want to delete list room, as it'll cause us problems.
      raise DeleteUndefException()
    elif self.isDefault:
      # This will cause find_default() to fail
      raise DeleteDefaultException()
    else:
      # Move items to the "no room defined" room
      unsched = Room.objects.get(isUndefined=True)
      Item.objects.filter(room=self).update(room=unsched)
    return super(Room, self).delete()

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_room_detail', kwargs={ "pk": self.id })

  def as_xml_public(self):
   return render_to_string('xml/room_public.xml', { "r": self } )
  def as_xml(self):
   return render_to_string('xml/room.xml', { "r": self } )

  def always_available(self):
    """
    Return true if there are no slots where the room is not available.
    If there are no slots listed, then it's a con preference whether that
    means "always available" or never available".
    """
    return self.availability.count() == 0 and ConInfoBool.objects.no_avail_means_always_avail()

  def never_available(self):
    """
    Return true if there are no slots listed, and that should be interpreted
    as 'never available'.
    """
    return self.availability.count() == 0 and not ConInfoBool.objects.no_avail_means_always_avail()

  def available_for(self, item):
    """
    Return true if the item falls entirely within one of the room's periods of
    availability. If the room has NO availability listed, that might be a problem,
    or it might mean it's always available - con preference.
    """
    return self.always_available() or avail_for_slots(self.availability.all(), item.slots())

  def items(self, slot=None):
    """
    Returns the list of items that are scheduled in this room. If Slot is specified,
    the list is filtered to just those items that overlap with that slot.
    """
    return slot.items(self) if slot else Item.objects.filter(room=self)

  def items_public(self, slot=None):
    """
    Returns the list of items that are scheduled in this room, filtered to just the public
    items. If Slot is specified, the filter only includes the items in that slot.
    """
    return [ i for i in self.items(slot) if i.visible ]

  def kit_room_assignments(self):
    "Returns all the KitRoomAssignments assigned to this room"
    return KitRoomAssignment.objects.filter(room = self)

  @classmethod
  def rower(cls, request):
    return Rower({  "pk":                 "pk",
                    "name":               "name",
                    "gridOrder":          "gridOrder",
                    "visible":            "visible",
                    "isDefault":          "isDefault",
                    "isUndefined":        "isUndefined",
                    "canClash":           "canClash",
                    "description":        "description",
                    "parent":              "parent",
                    "privNotes":           "privNotes",
                    "needsSound":          "needsSound",
                    "naturalLight":        "naturalLight",
                    "securable":           "securable",
                    "controlLightsInRoom": "controlLightsInRoom",
                    "controlAirConInRoom": "controlAirConInRoom",
                    "accessibleOnFlat":    "accessibleOnFlat",
                    "hasWifi":             "hasWifi",
                    "hasCableRuns":        "hasCableRuns",
                    "openableWindows":     "openableWindows",
                    "closableCurtains":    "closableCurtains",
                    "inRadioRange":        "inRadioRange",
                    "techNotes":           "techNotes",
                    "edit":                "Edit",
                    "remove":              "Remove" })
  @classmethod
  def tabler_exclude(cls, request):
    if request.user.has_perm('progb2.read_private'):
      if request.user.has_perm('progb2.edit_room'):
        return None
      else:
        return ['edit', 'remove']
    else:
      return ['visible', 'isDefault', 'isUndefined', 'canClash', 'edit', 'remove']

class Person(models.Model):
  """
  A Person is someone who is a candidate for being scheduled on
  one or more Items. Different from Users, who are the people who
  have access to the database.
  """

  firstName = models.CharField(max_length=64,blank=True,
                               help_text="Someone's first name, e.g. Karen. People <em>can</em> be listed sorted by this field. Can be blank.")
  middleName = models.CharField(max_length=64,blank=True,
                                help_text="Someone's middle name, e.g. Clarence. Entirely optional.")
  lastName = models.CharField(max_length=64,blank=True,
                              help_text="Someone's surname, e.g. Nixon. People will most often be listed sorted by this field. If someone only has a single name, probably best to put it here.")
  badge = models.CharField(max_length=64,blank=True,
                           help_text="Optional.")
  badge_only = models.BooleanField(default=False,
                                   help_text="If you set this to true, only the badge name will be visible in the public versions of the programme.")
  email = models.EmailField(blank=True,
                            help_text="<em>Just</em> the email address")
  memnum = models.IntegerField(default=-1,
                               help_text="The person's membership number, or -1 if they haven't joined yet.")
  pubNotes = models.TextField(blank=True,
                              help_text="Public notes about the person. Can be biographic. These details will be visible to everyone.")
  privNotes = models.TextField(blank=True,
                               help_text="Private notes about the person, visible only to con staff.")
  contact = models.TextField(blank=True,
                             help_text="The person's contact details: address, phone number, etc.")
  gender = models.ForeignKey(Gender, default=Gender.objects.find_default,
                             help_text="Gender. You can use this to determine your balance on your programme.")
  complete = models.CharField(max_length=4, choices=YesNo, default='No',
                              help_text="Set this to Yes when you have gathered all the information you need about this person.")
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No',
                               help_text="True if the person has confirmed that it's okay to pass on their email address to other programme participants")
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No',
                                   help_text="True if the person has confirmed they're okay with being recorded (audio or video) on programme items")
  tags = models.ManyToManyField(Tag,null=True,blank=True,
                                help_text="Allocate whatever tags you think are appropriate to this person")
  availability = models.ManyToManyField(Slot, null=True, blank=True,
                                        help_text="Add availability entries to this person to indicate when they're available for scheduling")

  class Meta:
    verbose_name = 'person'
    verbose_name_plural = 'people'
    ordering = [ 'lastName', 'firstName', 'middleName' ]

  def combined_name(self):
    """
    We need at least one of the three name fields defined, but we don't really care which.
    Assemble whichever ones are defined into a single string, with a single space between them.
    """
    s = u''
    gap = u''
    for n in [ self.firstName, self.middleName, self.lastName ]:
      if n:
        s = s + gap + n
        gap = u' '
    return s

  def as_name(self):
    "returns the person's name"
    return self.combined_name()

  def as_name_then_badge(self):
    "Returns the person's name and badge as 'Name (Badge)', if they have a badge, or just the name if not."
    if self.badge:
      return u"%s (%s)" % ( self.as_name(), self.badge )
    else:
      return self.as_name()

  def as_badge(self):
    "Returns the person's badge, if badge_only is set, or their name if not."
    if self.badge_only and self.badge:
      return self.badge
    else:
      return self.combined_name()

  def __unicode__(self):
    """
    Any of the name fields can be blank; we need to find a
    way of expressing how at least one of the three must be
    filled in. Ideally, we also want to change how the names
    are viewed, based on permissions and on user choice.
    """
    return self.as_name_then_badge()
  def get_absolute_url(self):
    return reverse('show_person_detail', kwargs={ "pk": self.id })

  def as_xml_public(self):
    return render_to_string('xml/person_public.xml', { "p": self } )
  def as_xml(self):
    return render_to_string('xml/person.xml', { "p": self } )

  def clean_firstName(self):
    "Strip whitespace from the field"
    return self.cleaned_data['firstName'].strip()

  def clean_middleName(self):
    "Strip whitespace from the field"
    return self.cleaned_data['middleName'].strip()

  def clean_lastName(self):
    "Strip whitespace from the field"
    return self.cleaned_data['lastName'].strip()

  def clean_badge(self):
    "Strip whitespace from the field"
    return self.cleaned_data['badge'].strip()

  def clean(self):
    "Ensure that at least one of firstName, MiddleName and lastName is set."
    from django.core.exceptions import ValidationError
    if not (self.firstName + self.middleName + self.lastName):
      raise ValidationError('At least one of first/middle/last name must be set')
    if self.badge_only and not self.badge:
      raise ValidationError('Cannot set badge_only if badge is not set')

  def always_available(self):
    """
    Return true if there are no slots where the person is not available.
    If there are no slots listed, then it's a con preference whether that
    means "always available" or never available".
    """
    return self.availability.count() == 0 and ConInfoBool.objects.no_avail_means_always_avail()

  def never_available(self):
    """
    Return true if there are no slots listed, and that should be interpreted
    as 'never available'.
    """
    return self.availability.count() == 0 and not ConInfoBool.objects.no_avail_means_always_avail()

  def available_for(self, item):
    """
    Return true if the item falls entirely within one of the person's periods of
    availability. If the person has NO availability listed, that might be a problem,
    or it might mean it's always available - con preference.
    """
    return self.always_available() or avail_for_slots(self.availability.all(), item.slots())


  def scheduled_items(self):
    "Returns the list of items this person is on"
    return [ i for i in ItemPerson.objects.filter(person=self) ]

  def item_count(self):
    "Returns the number of items this person is on"
    return len(self.scheduled_items())

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":         "id",
                   "memnum":     "memnum",
                   "name":       "as_badge",
                   "firstName":  "firstName",
                   "middleName": "middleName",
                   "lastName":   "lastName",
                   "badge":      "badge",
                   "badge_only": "badge_only",
                   "email":      "email",
                   "item_count": "item_count",
                   "edit":       "Edit",
                   "remove":     "Remove" })

  @classmethod
  def tabler_exclude(cls, request):
    if request.user.has_perm('progb2.read_private'):
      if request.user.has_perm('progb2.edit_private'):
        return ['name']
      else:
        return ['edit', 'name']
    else:
      return ['edit', 'memnum', 'firstName', 'middleName', 'lastName', 'email', 'badge_only' ]
 

class ScheduledManager(models.Manager):
  "A manager for returning only items that have been scheduled. Useful for checking for problems."
  def get_query_set(self):
    undef_slot = Slot.objects.find_undefined()
    undef_len = SlotLength.objects.find_undefined()
    undef_room = Room.objects.find_undefined()
    return super(ScheduledManager, self).get_query_set().exclude(start=undef_slot).exclude(length=undef_len).exclude(room=undef_room)

class UnscheduledManager(models.Manager):
  "A manager that only returns unscheduled items. Useful for when filling slots in the grid."
  def get_query_set(self):
    undef_slot = Slot.objects.find_undefined()
    undef_len = SlotLength.objects.find_undefined()
    undef_room = Room.objects.find_undefined()
    return super(UnscheduledManager, self).get_query_set().filter(Q(start=undef_slot) | Q(length=undef_len) | Q(room=undef_room))

class Item(models.Model):
  "An Item is a single scheduled item in the programme."
  title = models.CharField(max_length=128, blank=True,
                            help_text="The full title of the item")
  shortname = models.CharField(max_length=32, blank=True,
                               help_text="Shorthand for the item. Handy for grids, back-of-badge labels, etc.") 
  blurb = models.TextField(blank=True,
                           help_text="A public description about the item, so people know what it's about")
  start = models.ForeignKey(Slot, null=True, default=Slot.objects.find_default,
                            help_text="The slot in which the item will begin")
  length = models.ForeignKey(SlotLength, default=SlotLength.objects.find_default,
                             help_text="The duration of the item")
  room = models.ForeignKey(Room, default=Room.objects.find_default,
                           help_text="The room in which the item takes place")
  kind = models.ForeignKey(ItemKind, default=ItemKind.objects.find_default,
                           help_text="What kind of item is this? Panel, talk, workshop, etc.")
  seating = models.ForeignKey(SeatingKind, default=SeatingKind.objects.find_default,
                              help_text="How should the main body of the room be laid out, for the audience?")
  frontLayout = models.ForeignKey(FrontLayoutKind, default=FrontLayoutKind.objects.find_default,
                                  help_text="How should the front of the room be laid out, for the item participants?")
  revision = models.ForeignKey(Revision, default=Revision.objects.latest,
                               help_text="Indicates which baseline of the programme this item was last modified in")
  visible = models.BooleanField(default=True,
                                help_text="Set to true if the item should appear on the printed programme")
  expAudience = models.IntegerField(default=30,
                                    help_text="estimate the size of the audience. Used to check whether the item's in a suitably-sized room")
  gophers = models.IntegerField(default=0,
                                help_text="Any gophers required by this item?")
  stewards = models.IntegerField(default=0,
                                 help_text="Any stewards required by this item?")
  budget = models.IntegerField(default=0,
                               help_text="How much budget has been allocated to this item?")
  projNeeded = models.CharField(max_length=4, choices=YesNo, default='TBA',
                                help_text="Does the item require a projector?")
  techNeeded = models.CharField(max_length=4, choices=YesNo, default='TBA',
                                help_text="Does the item require any other Tech, besides a projector?")
  complete = models.CharField(max_length=4, choices=YesNo, default='No',
                              help_text="Mark as Yes when you no longer expect any changes to happen to this item.")
  privNotes = models.TextField(blank=True,
                               help_text="Private notes, visible only to con staff. <em>Don't</em> put tech notes here.")
  techNotes = models.TextField(blank=True,
                               help_text="Any info about needed Tech should go here.")
  pubBring = models.TextField(blank=True,
                              help_text="Information about anything the audience should bring, for this item, e.g. loose clothing, kilts for a ceilidh. Useful for putting into Progress Reports.")
  tags = models.ManyToManyField(Tag,null=True,blank=True,
                                help_text="Assign any tags you think are relevant to this item.")
  people = models.ManyToManyField(Person, through='ItemPerson', null=True, blank=True,
                                  help_text="The people participating in this item")
  kitRequests = models.ManyToManyField(KitRequest, null=True, blank=True,
                                       help_text="Kit requested by this item. <em>Only Tech should fill this in.</em>")
  kit = models.ManyToManyField(KitThing, through='KitItemAssignment', null=True, blank=True,
                               help_text="Kit allocated to this item, to satisfy requests. <em>Only Tech should fill this in.</em>")
  audienceMics = models.BooleanField(default=False,
                                     help_text="True if the item probably needs roving microphones for questions from audience.")
  allTechCrew = models.BooleanField(default=False,
                                    help_text="True if this item will need the entire Tech Crew to work on it.")
  needsReset = models.BooleanField(default=False,
                                   help_text="True if the room will need to be reset <em>before</em> the item")
  needsCleanUp = models.BooleanField(default=False,
                                     help_text="True if the room will need to be cleaned up <em>after</em> the item")
  mediaStatus = models.ForeignKey(MediaStatus, default=MediaStatus.objects.find_default,
                                  help_text="Indicates whether Tech have suitably processed any media requirements for the item")
  follows = models.ForeignKey('self', null=True, blank=True,
                              help_text="If this item must always immediately follow another item in the same room (e.g. setup, item, tear down), select the preceding item here")
  objects = models.Manager()
  scheduled = ScheduledManager()
  unscheduled = UnscheduledManager()

  class Meta:
    ordering = [ 'title', 'shortname' ]
    verbose_name = 'item'
    verbose_name_plural = 'items'

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":                     "id",
                   "start":                  "start",
                   "room":                   "room",
                   "shortname":              "shortname",
                   "projNeeded":             "projNeeded",
                   "title":                  "title",
                   "satisfies_kit_requests": "satisfies_kit_requests",
                   "edit":                   "Edit",
                   "remove":                 "Remove" })
 
  @classmethod
  def tabler_exclude(cls, request):
    if request.user.has_perm('progb2.read_private'):
      if request.user.has_perm('progb2.edit_programme'):
        return None
      else:
        return ['edit', 'remove', 'satisfies_kit_requests']
    else:
      return ['edit', 'remove', 'shortname', 'satisfies_kit_requests' ]

  def __unicode__(self):
    if self.title:
      return self.title
    else:
      return self.shortname
  def get_absolute_url(self):
    return reverse('show_item_detail', kwargs={ "pk": self.id })

  def as_xml_public(self):
    return render_to_string('xml/item_public.xml', { "i": self } )
  def as_xml(self):
    return render_to_string('xml/item.xml', { "i": self } )

  def clean_title(self):
    "Strip whitespace from the field"
    return self.cleaned_data['title'].strip()

  def clean_shortname(self):
    "Strip whitespace from the field"
    return self.cleaned_data['shortname'].strip()

  def clean(self):
    "Ensure that at least one of shortname and title is set."
    from django.core.exceptions import ValidationError
    if not (self.shortname + self.title):
      raise ValidationError('At least one of title/shortname must be set')

  def slots(self):
    "Return a queryset of the slots this item occupies"
    return Slot.objects.filter(day=self.start.day, start__gte=self.start.start, start__lt=self.start.start+self.length.length)

  def overlaps(self, other):
    "Returns true if this item overlaps another item"
    if (self == other):
      return False
    return (    self.start.day == other.start.day
            and self.start.start < (other.start.start + other.length.length)
            and other.start.start < (self.start.start + self.length.length))

  def kit_item_assignments(self):
    "Return all the KitItemAssignments for this item"
    return KitItemAssignment.objects.filter(item = self)

  def kit_room_assignments(self):
    "Return all the KitRoomAssignments for this item's room"
    return self.room.kit_room_assignments()

  def satisfies_kit_requests(self):
    "Returns true if the kit assigned to this item satisfies all the item's requests"
    return KitSatisfaction(self).satisfied

  def satisfies_kit_requests_yesno(self):
    "Returns true if the kit assigned to this item satisfies all the item's requests"
    return "Yes" if KitSatisfaction(self).satisfied else "No"

  def has_unsatisfied_kit_requests(self):
    return not self.satisfies_kit_requests()

  def day(self):
    return self.start.day
  def startText(self):
    return self.start.startText

  def itempeople(self):
    "Give access to the ItemPerson objects, rather than the Person objects that people gives."
    return ItemPerson.objects.filter(item = self)

  def people_public(self):
    "Return all the people who are publicly visible on this item."
    return [ ip.person for ip in self.itempeople() if ip.visible ]

  def delete(self):
    "Don't leave KitRequests lying around if this item gets deleted."
    self.kitRequests.all().delete()
    return super(Item, self).delete()


class ItemPerson(models.Model):
  """
  An ItemPerson is the assignment of a Person to an Item.
  """
  item = models.ForeignKey(Item,
                           help_text="The item the person is participating in")
  person = models.ForeignKey(Person,
                             help_text="The person participating in the item")
  role = models.ForeignKey(PersonRole, default=PersonRole.objects.find_default,
                           help_text="What is the person's role, for this item?")
  status = models.ForeignKey(PersonStatus, default=PersonStatus.objects.find_default,
                             help_text="Has the person confirmed they can participate in this item?")
  visible = models.BooleanField(default=True,
                                help_text="True if the the person should be listed as participating, in the printed programme")
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No',
                               help_text="True if the person has confirmed it's okay to distribute their email address to the other people on the item")
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No',
                                   help_text="True if the person has confirmed they're okay with being recorded, for this item")

  class Meta:
    verbose_name = 'itemperson'
    verbose_name_plural = 'itemspeople'
    unique_together = (('item', 'person'),)

  def __unicode__(self):
    return u"%s: %s [%s]" % (self.item, self.person, self.role)
  def get_absolute_url(self):
    return reverse('show_itemperson_detail', kwargs={"pk": self.id})

  def as_xml_public(self):
    return render_to_string('xml/itemperson_public.xml', { "ip": self } )
  def as_xml(self):
    return render_to_string('xml/itemperson.xml', { "ip": self } )

  @classmethod
  def rower(cls, request):
    return Rower({ "pk":            "id",
                   "item":          "item",
                   "person":        "person",
                   "role":          "role",
                   "status":        "status",
                   "visible":       "visible",
                   "distEmail":     "distEmail",
                   "recordingOkay": "recordingOkay",
                   "edit":          "Edit",
                   "remove":        "Remove" })

  @classmethod
  def tabler_exclude(cls, request):
    no_perms = ['select', 'edit', 'remove', 'status', 'visible', 'distEmail', 'recordingOkay']
    if not request:
      return no_perms
    if request.user.has_perm('progb2.read_private'):
      if request.user.has_perm('progb2.edit_programme'):
        return []
      else:
        return ['select', 'edit', 'remove']
    else:
      return no_perms

class PersonList(models.Model):
  """
  A PersonList is a list of people that we're saving, for some purpose - usually in order to send
  some email to the people on the list. PersonLists can be created automatically, and then deleted
  again once used, or may be explicitly created and saved by a user.
  """
  name = models.CharField(max_length=120,
                          help_text="Pick a meaningful name, including why you've saved this list")
  auto = models.BooleanField(default=False,help_text="If true, this list will be deleted as soon as it's been used to send email")
  created = models.DateTimeField(auto_now_add=True,
                                 help_text="We note when a PersonList is created, so we can delete old ones.")
  people = models.ManyToManyField(Person, null=True, blank=True,
                                 help_text="The people in this list")

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_personlist_detail', kwargs={"pk": self.id})

class CheckResult(EnumTable):
  "Indicates what kind of result we get back from a particular check, so we know how to display it."
  def delete(self):
    self.check_set.all().update(result=self.delete_replacement())
    return super(CheckResult, self).delete()


class Check(models.Model):
  """
  A Check is one of the database's checks on the validity of the programme. These should only
  be created by developers, not by users.
  """
  name = models.CharField(max_length=120,
                          help_text="The name of the check.")
  description = models.TextField(max_length=256,
                                 help_text="Explanation of what the check verifies")
  module = models.SlugField(max_length=48,
                            help_text="Used to identify the code to load and run, and how to render the results")
  result = models.ForeignKey(CheckResult, default=CheckResult.objects.find_default,
                             help_text="The kind of result returned by the check")

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return reverse('show_check_detail', kwargs={"pk": self.id})


NameOrder = (
  ( 'Last', 'Last, First, Middle, Badge'),
  ( 'First', 'First, Middle, Last, Badge' ),
  ( 'Badge', 'Badge, First, Middle, Last' ),
)

class UserProfile(models.Model):
  """
  UserProfile stores additional information for each user, as directed by Django docs. Mostly what
  we store is user preferences, in case they differ from the overall con preferences that are
  stored in ConInfoBool.
  """
  # required field
  user = models.OneToOneField(User,
                              help_text="The User for which this profile applies")
  # personal preferences about grid rendering
  show_shortname = models.BooleanField(default=ConInfoBool.objects.show_shortname,
                                       help_text="True if shortnames should be displayed")
  show_tags = models.BooleanField(default=True,
                                  help_text="True if tags should be displayed on the grid")
  show_people = models.BooleanField(default=True,
                                    help_text="True if people should be displayed on the grid")
  show_kithings = models.BooleanField(default=False,
                                      help_text="True if kit things should be displayed on the grid")
  show_kitbundles = models.BooleanField(default=False,
                                        help_text="True if kit bundles should be displayed on the grid")
  show_kitrequests = models.BooleanField(default=False,
                                         help_text="True if kit requests should be displayed on the grid")
  rooms_across_top = models.BooleanField(default=ConInfoBool.objects.rooms_across_top,
                                         help_text="True if rooms should be listed across the top of the grid, False if they should be listed down the side.")
  name_order = models.CharField(max_length=4, choices=NameOrder, default='Last',
                                help_text="How should person-lists be sorted?")
  person = models.ForeignKey(Person, null=True, blank=True,
                             help_text="If this user is also a programme participant, select the person here.")

  class Meta:
    permissions = (
      ("edit_private",      "Can edit private data"),
      ("edit_public",       "Can edit public data"),
      ("read_public",       "Can read public data"),
      ("read_private",      "Can read private data"),
      ("config_db",         "Can configure the database"),
      ("edit_programme",    "Can edit programme data"),
      ("edit_kit",          "Can edit kit-related data"),
      ("send_direct_email", "Can send email to individuals"),
      ("send_item_email",   "Can send email to everyone on an item"),
      ("send_mass_email",   "Can send email to everyone"),
      ("import_data",       "Can import data"),
      ("export_data",       "Can export data"),
      ("edit_room",         "Can edit room info"),
      ("edit_tags",         "Can tag items/people and edit tags"),
    )

  def __unicode__(self):
    return u"profile:%s" % (self.user)

  def get_absolute_url(self):
    return reverse('userprofile')

def create_user_profile(sender, instance, created, **kwargs):
  "Associate a user profile with each user that is created, as directed by the Django docs."
  if created:
    UserProfile.objects.create(user=instance)

# Register the signal handler against the User object
post_save.connect(create_user_profile, sender=User, dispatch_uid="create_user_profile")


# Outstanding things that need thinking about:
# - Item Moves. Add when we need that.

# Things that need something better than the admin interface:
# The slot form: need to be able to enter a time, and have that converted to mins.


