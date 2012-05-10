"""
Experimental models for ProgDB 2.0.
"""

from datetime import timedelta, datetime
from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from django.contrib.auth.models import User
from django.db.models.signals import post_save

YesNo = (
  ( 'TBA', 'TBA'),
  ( 'Yes', 'Yes' ), 
  ( 'No', 'No'),
)

def mk_url(self, alt=None):
  text = alt
  if text == None:
    text = self.__class__.__name__.lower()
  return r'/progdb/%s/%d/' % (text, self.id)

class DefUndefManager(models.Manager):
  """
  A manager that has extra methods for finding the default/undefined
  values based on fields.
  """
  def find_default(self):
    return self.get(isDefault=True)
  def find_undefined(self):
    return self.get(isUndefined=True)


class Availability(models.Model):
  label = models.CharField(max_length=24, blank=True)
  fromWhen = models.DateTimeField()
  toWhen = models.DateTimeField()

  def __unicode__(self):
    if self.label:
      return u"%s: (%s - %s)" % (self.label, self.fromWhen, self.toWhen)
    else:
      return "%s - %s" % (self.fromWhen, self.toWhen)

  def covers(self, item):
    dt = item.day.date
    itemstart = datetime(year=dt.year, month=dt.month, day=dt.day) + timedelta(minutes=item.start.start)
    itemend = itemstart + timedelta(minutes=item.length.length)
    return self.fromWhen <= itemstart and itemend <= self.toWhen
    

class KitAvailability(Availability):
  pass

class RoomAvailability(Availability):
  pass

class PersonAvailability(Availability):
  pass

class ConInfoBoolManager(models.Manager):
  def show_shortname(self):
    return self.get(var='show_shortname').val
  def rooms_across_top(self):
    return self.get(var='rooms_across_top').val
  def no_avail_means_always_avail(self):
    return self.get(var='no_avail_means_always_avail').val

class ConInfoBool(models.Model):
  name = models.CharField(max_length=64)
  var = models.SlugField(max_length=64)
  val = models.BooleanField()
  objects = ConInfoBoolManager()
  def __unicode__(self):
    return self.name

class ConInfoIntManager(models.Manager):
  def max_items_per_day(self):
    return self.get(var='max_items_per_day').val
  def max_items_whole_con(self):
    return self.get(var='max_items_whole_con').val
  def max_consecutive_items(self):
    return self.get(var='max_consecutive_items').val

class ConInfoInt(models.Model):
  name = models.CharField(max_length=64)
  var = models.SlugField(max_length=64)
  val = models.IntegerField()
  objects = ConInfoIntManager()
  def __unicode__(self):
    return self.name

class ConInfoStringManager(models.Manager):
  def con_name(self):
    return self.get(var='con_name').val
  def email_from(self):
    return self.get(var='email_from').val

class ConInfoString(models.Model):
  name = models.CharField(max_length=64)
  var = models.SlugField(max_length=64)
  val = models.CharField(max_length=256)
  objects = ConInfoStringManager()
  def __unicode__(self):
    return self.name


class ConDayManager(DefUndefManager):
  def earliest_day(self):
    return (self).objects.all().order_by('date')[0]
  def earliest_public_day(self):
    return (self).objects.filter(visible=True).order_by('date')[0]
  def latest_day(self):
    return (self).objects.all().order_by('-date')[0]
  def latest_public_day(self):
    return (self).objects.filter(visible=True).order_by('-date')[0]

class ConDay(models.Model):
  """
  A ConDay is how we map from a given date to
  a name, and whether it's a public date.
  """
  name = models.CharField(max_length=24)
  date = models.DateField()
  order = models.IntegerField()
  visible = models.BooleanField()
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
  objects = DefUndefManager()

  class Meta:
    ordering = [ '-isDefault', 'date' ]

  def __unicode__(self):
    return self.name

class SlotLength(models.Model):
  "A SlotLength is how long a given item may run."
  name = models.CharField(max_length=30)
  length = models.IntegerField(default=60)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
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
  start = models.IntegerField()
  length = models.ForeignKey(SlotLength, default=SlotLength.objects.find_default)
  startText = models.CharField(max_length=20)
  slotText = models.CharField(max_length=20)
  visible = models.BooleanField(default=True)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
  objects = DefUndefManager()

  class Meta:
    ordering = [ 'isDefault', 'start' ]

  def __unicode__(self):
    return self.startText
  def get_absolute_url(self):
    return mk_url(self)

class Grid(models.Model):
  """
  A Grid is a collection of slots that get displayed together
  In ProgDB 1.0, we had a start, a length, and a slotlen,
  and we went looking for all the Slots that fitted.
  Here, we're explicitly going to assign the Slots to the
  Grid.
  """
  name = models.CharField(max_length=40)
  slots = models.ManyToManyField(Slot)
  gridOrder = models.IntegerField(default=1)

  class Meta:
    ordering = ['gridOrder']

  def __unicode__(self):
    return self.name

class Revision(models.Model):
  """
  A Revision tells us when an item was last modified.
  The colour is intended to be a CSS style, later on.
  """
  baseline = models.DateTimeField()
  colour = models.CharField(max_length=20)
  description = models.TextField()

  class Meta:
    ordering = [ '-baseline' ]
    get_latest_by = 'baseline'

  def __unicode__(self):
    return self.description

class EnumManager(DefUndefManager):
  pass

class EnumTable(models.Model):
  "Various name/value choices, with a default choice."
  name = models.CharField(max_length=64)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
  gridOrder = models.IntegerField(default=1)
  description = models.TextField(blank=True)

  objects = EnumManager()

  class Meta:
    ordering = [ 'gridOrder' ]
    abstract = True

  def __unicode__(self):
    return self.name

class ItemKind(EnumTable):
  """
  An Item's ItemKind tells you what kind of activity
  the item is.
  """
  pass

class SeatingKind(EnumTable):
  """
  An Item's SeatingKind tells you how the item's
  room should be laid out.
  """
  pass

class FrontLayoutKind(EnumTable):
  """
  Used to describe how the front of the room should be laid out.
  """

class PersonRole(EnumTable):
  """
  A PersonRole defines the person's job, for
  a given Item
  """
  pass

class PersonStatus(EnumTable):
  """
  A PersonStatus indicates how confident you are
  that a person will turn up and carry out their role.
  """
  pass
  class Meta:
    verbose_name = 'Person Statuses'

class Gender(EnumTable):
  """
  A Gender allows you to determine whether you have
  a suitable balance on your programme.
  """
  pass

class Tag(models.Model):
  """
  A Tag is an arbitrary piece of information about Items,
  People, etc.
  """
  name = models.CharField(max_length=64)
  description = models.TextField(blank=True)
  icon = models.URLField(verify_exists=False, blank=True)
  visible = models.BooleanField(default=True)

  class Meta:
    verbose_name = 'tag'
    verbose_name_plural = 'tags'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)

class KitKind(EnumTable):
  pass

class KitRole(EnumTable):
  pass

class KitDepartment(EnumTable):
  pass

class KitSource(EnumTable):
  pass

class KitBasis(EnumTable):
  pass

class MediaStatus(EnumTable):
  pass

class KitStatus(EnumTable):
  pass

class KitRequest(models.Model):
  kind = models.ForeignKey(KitKind, default=KitKind.objects.find_default)
  count = models.SmallIntegerField(default=1)
  setupAssistance = models.BooleanField()
  notes = models.TextField(blank=True)
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default)

  class Meta:
    verbose_name = 'kitrequest'
    verbose_name_plural = 'kitrequests'

  def __unicode__(self):
    return u"%s: %d" % (self.kind, self.count)
  def get_absolute_url(self):
    return mk_url(self)

class KitThing(models.Model):
  name = models.CharField(max_length=64)
  description = models.TextField(blank=True)
  kind = models.ForeignKey(KitKind, default=KitKind.objects.find_default)
  count = models.SmallIntegerField(default=1)
  role = models.ForeignKey(KitRole, default=KitRole.objects.find_default)
  source = models.ForeignKey(KitSource, default=KitSource.objects.find_default)
  department = models.ForeignKey(KitDepartment, default=KitDepartment.objects.find_default)
  basis = models.ForeignKey(KitBasis, default=KitBasis.objects.find_default)
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default)
  cost = models.IntegerField(default=0)
  insurance = models.IntegerField(default=0)
  notes = models.TextField(blank=True)
  coordinator = models.CharField(max_length=64)
  availability = models.ManyToManyField(KitAvailability, null=True, blank=True)

  class Meta:
    verbose_name = 'kitthing'
    verbose_name_plural = 'kitthings'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)

  def available_for(self, item):
    for av in self.availability.all():
      if av.covers(item):
        return True
    if len(self.availability.all()) == 0:
      return ConInfoBool.objects.no_avail_means_always_avail()
    return False

class KitBundle(models.Model):
  name = models.CharField(max_length=64)
  status = models.ForeignKey(KitStatus, default=KitStatus.objects.find_default)
  things = models.ManyToManyField(KitThing)

  class Meta:
    verbose_name = 'kitbundle'
    verbose_name_plural = 'kitbundles'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)

class KitRoomAssignment(models.Model):
  room = models.ForeignKey('Room')
  thing = models.ForeignKey(KitThing)
  bundle = models.ForeignKey(KitBundle, null=True, blank=True)
  fromDay = models.ForeignKey(ConDay, related_name='kitroomfrom_set')
  fromSlot = models.ForeignKey(Slot, related_name='kitroomfrom_set')
  toDay = models.ForeignKey(ConDay, related_name='kitroomto_set')
  toSlot = models.ForeignKey(Slot, related_name='kitroomto_set')
  toLength = models.ForeignKey(SlotLength)

  def __unicode__(self):
    return u"%s in %s" % (self.thing, self.room)
  def get_absolute_url(self):
    return mk_url(self)

  def starts_before_day_and_slot(self, day, slot, mins):
    return (   self.fromDay.date < day.date
            or (    self.fromDay.date == day.date 
                and self.fromSlot.start <= slot.start))

  def finishes_after_day_and_slot(self, day, slot, mins):
    # Bug: toSlot is inclusive, but what's the length of that slot?
    return (   day.date < self.toDay.date
            or (    day.date == self.toDay.date
                and (slot.start + mins) <= self.toSlot.start))


  def starts_before(self, item):
    return self.starts_before_day_and_slot(item.day, item.start, 0)

  def finishes_after(self, item):
    return finishes_after_day_and_slot(self, item.day, item.start, item.length.length)

  def covers(self, item):
    return self.starts_before(item) and self.finishes_after(item)

  def overlaps(self, item):
    return (    self.starts_before_day_and_slot(item.day, item.start, item.length.length)
            and self.finishes_after_day_and_slot(item.day, item.start, item.length.length))

  def overlaps_room_assignment(self, other):
    return (    self.starts_before_day_and_slot(other.toDay, other.toSlot, 0)
            and self.finishes_after_day_and_slot(other.fromDay, other.fromSlot, 0))

  def satisfies(self, req, item):
    "Return True if this assignment satisfies the request"
    r = self.thing.kind == req.kind and self.thing.count >= req.count and self.covers(item)
    return self.thing.kind == req.kind and self.thing.count >= req.count and self.covers(item)
  
class KitItemAssignment(models.Model):
  item = models.ForeignKey('Item')
  thing = models.ForeignKey(KitThing)
  bundle = models.ForeignKey(KitBundle, null=True, blank=True)

  def __unicode__(self):
    return u"%s to %s" % (self.thing, self.item)
  def get_absolute_url(self):
    return mk_url(self)

  def satisfies(self, req):
    "Return True if this assignment satisfies the request"
    r = self.thing.kind == req.kind and self.thing.count >= req.count
    return self.thing.kind == req.kind and self.thing.count >= req.count

class RoomCapacity(models.Model):
  layout = models.ForeignKey(SeatingKind, default=SeatingKind.objects.find_default)
  count = models.IntegerField()

  class Meta:
    verbose_name = 'room-capacity'
    verbose_name_plural = 'room-capacities'

  def __unicode__(self):
    return u"%s: %d" % (self.layout, self.count)

class Room(models.Model):
  """
  A Room is where a programme item can take place.
  Every item is in some room somewhere, although we
  have a couple of special rooms for unassigned
  items (Nowhere) or items that don't get a specific
  room (Everywhere).
  """
  name = models.CharField(max_length=64)
  description = models.TextField(blank=True)
  visible = models.BooleanField(default=True)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
  canClash = models.BooleanField()
  disabledAccess = models.BooleanField(default=True)
  gridOrder = models.IntegerField(default=50)
  privNotes = models.TextField(blank=True)
  techNotes = models.TextField(blank=True)
  needsSound = models.BooleanField()
  naturalLight = models.BooleanField()
  securable = models.BooleanField()
  controlLightsInRoom = models.BooleanField()
  controlAirConInRoom = models.BooleanField()
  accessibleOnFlat = models.BooleanField()
  hasWifi = models.BooleanField()
  hasCableRuns = models.BooleanField()
  openableWindows = models.BooleanField()
  closableCurtains = models.BooleanField()
  inRadioRange = models.BooleanField()
  kit = models.ManyToManyField(KitThing, through='KitRoomAssignment', null=True, blank=True)
  parent = models.ForeignKey('self', null=True, blank=True)
  capacities = models.ManyToManyField(RoomCapacity, null=True, blank=True)
  availability = models.ManyToManyField(RoomAvailability, null=True, blank=True)
  objects = DefUndefManager()

  class Meta:
    ordering = [ 'isDefault', 'gridOrder' ]
    verbose_name = 'room'
    verbose_name_plural = 'rooms'

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)

  def available_for(self, item):
    for av in self.availability.all():
      if av.covers(item):
        return True
    if len(self.availability.all()) == 0:
      return ConInfoBool.objects.no_avail_means_always_avail()
    return False

  def satisfies_kit_request(self, request, item):
    if self.isUndefined:
      return False
    if self.kit.count() == 0:
      return False
    # XXX should be a list comprehension
    for k in KitRoomAssignment.objects.filter(room=self):
      if k.satisfies(request, item):
        return True
    return False

  def satisfies_kit_requests(self, requests, item):
    if self.isUndefined:
      return False
    if self.kit.count() == 0:
      return False
    # XXX should be a list comprehension
    for req in requests:
      if not self.satisfies_kit_request(req, item):
        return False
    return True

class Person(models.Model):
  """
  A Person is someone who is a candidate for being scheduled on
  one or more Items.
  Again, we're moving to ManyToMany to handle the Tag relationship.
  """
  firstName = models.CharField(max_length=64,blank=True)
  middleName = models.CharField(max_length=64,blank=True)
  lastName = models.CharField(max_length=64,blank=True)
  badge = models.CharField(max_length=64,blank=True)
  email = models.EmailField(blank=True)
  memnum = models.IntegerField(default=-1)
  pubNotes = models.TextField(blank=True)
  privNotes = models.TextField(blank=True)
  contact = models.TextField(blank=True)
  gender = models.ForeignKey(Gender, default=Gender.objects.find_default)
  complete = models.CharField(max_length=4, choices=YesNo, default='No')
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No')
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No')
  tags = models.ManyToManyField(Tag,null=True,blank=True)
  availability = models.ManyToManyField(PersonAvailability, null=True, blank=True)

  class Meta:
    verbose_name = 'person'
    verbose_name_plural = 'people'
    ordering = [ 'lastName', 'firstName', 'middleName' ]

  def combined_name(self):
    """
    Append the defined names.
    """
    s = u''
    gap = u''
    for n in [ self.firstName, self.middleName, self.lastName ]:
      if n:
        s = s + gap + n
        gap = u' '
    return s

  def as_name(self):
    return self.combined_name()

  def as_name_then_badge(self):
    if self.badge:
      return u"%s (%s)" % ( self.as_name(), self.badge )
    else:
      return self.as_name()

  def as_badge(self):
    if self.badge:
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
    return mk_url(self)

  def clean_firstName(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['firstName'].strip()

  def clean_middleName(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['middleName'].strip()

  def clean_lastName(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['lastName'].strip()

  def clean_badge(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['badge'].strip()

  def clean(self):
    """
    Ensure that at least one of firstName, MiddleName and lastName is set.
    """
    from django.core.exceptions import ValidationError
    if not (self.firstName + self.middleName + self.lastName):
      raise ValidationError('At least one of first/middle/last name must be set')

  def available_for(self, item):
    for av in self.availability.all():
      if av.covers(item):
        return True
    if len(self.availability.all()) == 0:
      return ConInfoBool.objects.no_avail_means_always_avail()
    return False

class ScheduledManager(models.Manager):
  def get_query_set(self):
    undef_day = ConDay.objects.find_undefined()
    undef_slot = Slot.objects.find_undefined()
    undef_len = SlotLength.objects.find_undefined()
    undef_room = Room.objects.find_undefined()
    return super(ScheduledManager, self).get_query_set().exclude(day=undef_day).exclude(start=undef_slot).exclude(length=undef_len).exclude(room=undef_room)

class UnscheduledManager(models.Manager):
  def get_query_set(self):
    undef_day = ConDay.objects.find_undefined()
    undef_slot = Slot.objects.find_undefined()
    undef_len = SlotLength.objects.find_undefined()
    undef_room = Room.objects.find_undefined()
    return super(UnscheduledManager, self).get_query_set().filter(Q(day=undef_day) | Q(start=undef_slot) | Q(length=undef_len) | Q(room=undef_room))

class Item(models.Model):
  """
  An Item is a single scheduled item in the programme.
  In ProgDB 1.0, we allowed items to start at any DateTime.
  Toyed with keeping that flexibility, even when the times
  are indicated by day/offset-from-midnight. Now we're
  going to directly key to a Slot, so a slot will have to
  be created to allow a start to be allocated.
  We're also moving from having explicit tables for joins
  to Tags, to using ManyToMany.
  """
  title = models.CharField(max_length=128, blank=True)
  shortname = models.CharField(max_length=32, blank=True)
  blurb = models.TextField(blank=True)
  day = models.ForeignKey(ConDay, null=True, default=ConDay.objects.find_default)
  start = models.ForeignKey(Slot, null=True, default=Slot.objects.find_default)
  length = models.ForeignKey(SlotLength, default=SlotLength.objects.find_default)
  room = models.ForeignKey(Room, default=Room.objects.find_default)
  kind = models.ForeignKey(ItemKind, default=ItemKind.objects.find_default)
  seating = models.ForeignKey(SeatingKind, default=SeatingKind.objects.find_default)
  frontLayout = models.ForeignKey(FrontLayoutKind, default=FrontLayoutKind.objects.find_default)
  revision = models.ForeignKey(Revision, default=Revision.objects.latest)
  visible = models.BooleanField(default=True)
  expAudience = models.IntegerField(default=30)
  gophers = models.IntegerField(default=0)
  stewards = models.IntegerField(default=0)
  budget = models.IntegerField(default=0)
  techNeeded = models.CharField(max_length=4, choices=YesNo, default='TBA')
  complete = models.CharField(max_length=4, choices=YesNo, default='No')
  privNotes = models.TextField(blank=True)
  techNotes = models.TextField(blank=True)
  pubBring = models.TextField(blank=True)
  tags = models.ManyToManyField(Tag,null=True,blank=True)
  people = models.ManyToManyField(Person, through='ItemPerson', null=True, blank=True)
  kitRequests = models.ManyToManyField(KitRequest, null=True, blank=True)
  kit = models.ManyToManyField(KitThing, through='KitItemAssignment', null=True, blank=True)
  audienceMics = models.BooleanField(default=False)
  allTechCrew = models.BooleanField(default=False)
  needsReset = models.BooleanField(default=False)
  needsCleanUp = models.BooleanField(default=False)
  mediaStatus = models.ForeignKey(MediaStatus, default=MediaStatus.objects.find_default)
  follows = models.ForeignKey('self', null=True, blank=True)
  objects = models.Manager()
  scheduled = ScheduledManager()
  unscheduled = UnscheduledManager()

  class Meta:
    ordering = [ 'title', 'shortname' ]
    verbose_name = 'item'
    verbose_name_plural = 'items'

  def __unicode__(self):
    if self.title:
      return self.title
    else:
      return self.shortname
  def get_absolute_url(self):
    return mk_url(self)

  def clean_title(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['title'].strip()

  def clean_shortname(self):
    """
    Strip whitespace from the field
    """
    return self.cleaned_data['shortname'].strip()

  def clean(self):
    """
    Ensure that at least one of shortname and title is set.
    """
    from django.core.exceptions import ValidationError
    if not (self.shortname + self.title):
      raise ValidationError('At least one of title/shortname must be set')

  def overlaps(self, other):
    if (self == other):
      return False
    return (    self.day == other.day
            and self.start.start < (other.start.start + other.length.length)
            and other.start.start < (self.start.start + self.length.length))

  def satisfies_kit_request(self, req):
    for kas in self.kit.all():
      if kas.satisfies(req):
        return True
    return False

  def satisfies_kit_requests(self):
    for req in self.kitRequests.all():
      if not self.satisfies_kit_request(req):
        return False
    return True

  def room_satisfies_kit_requests(self):
    if self.room:
      return self.room.satisfies_kit_requests(self.kitRequests.all(), self)
    return False


class ItemPerson(models.Model):
  """
  An ItemPerson is the assignment of a Person to an Item.
  We should probably be implementing the Items -> People ManyToMany
  via a through field, rather than doing this.
  """
  item = models.ForeignKey(Item)
  person = models.ForeignKey(Person)
  role = models.ForeignKey(PersonRole, default=PersonRole.objects.find_default)
  status = models.ForeignKey(PersonStatus, default=PersonStatus.objects.find_default)
  visible = models.BooleanField(default=True)
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No')
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No')

  class Meta:
    verbose_name = 'itemperson'
    verbose_name_plural = 'itemspeople'

  def __unicode__(self):
    return u"%s: %s [%s]" % (self.item, self.person, self.role)
  def get_absolute_url(self):
    return mk_url(self)

class PersonList(models.Model):
  name = models.CharField(max_length=120)
  auto = models.BooleanField()
  created = models.DateTimeField(auto_now_add=True)
  people = models.ManyToManyField(Person, null=True, blank=True)

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)

class CheckResult(EnumTable):
  pass

class Check(models.Model):
  name = models.CharField(max_length=120)
  description = models.TextField(max_length=256)
  module = models.SlugField(max_length=48)
  result = models.ForeignKey(CheckResult, default=CheckResult.objects.find_default)

  def __unicode__(self):
    return self.name
  def get_absolute_url(self):
    return mk_url(self)


NameOrder = (
  ( 'Last', 'Last, First, Middle, Badge'),
  ( 'First', 'First, Middle, Last, Badge' ),
  ( 'Badge', 'Badge, First, Middle, Last' ),
)

class UserProfile(models.Model):
  # required field
  user = models.OneToOneField(User)
  # personal preferences about grid rendering
  show_shortname = models.BooleanField(default=ConInfoBool.objects.show_shortname)
  show_tags = models.BooleanField(default=True)
  show_people = models.BooleanField(default=True)
  show_kithings = models.BooleanField(default=False)
  show_kitbundles = models.BooleanField(default=False)
  show_kitrequests = models.BooleanField(default=False)
  rooms_across_top = models.BooleanField(default=ConInfoBool.objects.rooms_across_top)
  name_order = models.CharField(max_length=4, choices=NameOrder, default='Last')
  # If this user is actually a person in the programme too
  person = models.ForeignKey(Person, null=True, blank=True)

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
  if created:
    UserProfile.objects.create(user=instance)

# Register the signal handler against the User object
post_save.connect(create_user_profile, sender=User, dispatch_uid="create_user_profile")


# Outstanding things that need thinking about:
# - Item Moves. Add when we need that.

# Things that need something better than the admin interface:
# The slot form: need to be able to enter a time, and have that converted to mins.


