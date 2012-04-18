"""
Experimental models for ProgDB 2.0.
"""

from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput

YesNo = (
  ( 'TBA', 'TBA'),
  ( 'Yes', 'Yes' ), 
  ( 'No', 'No'),
)

class Availability(models.Model):
  label = models.CharField(max_length=24, blank=True)
  fromWhen = models.DateTimeField()
  toWhen = models.DateTimeField()

class KitAvailability(Availability):
  pass

class RoomAvailability(Availability):
  pass

class PersonAvailability(Availability):
  pass

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

  class Meta:
    ordering = [ '-isDefault', 'date' ]

  def __unicode__(self):
    return self.name

  @classmethod
  def find_default(cls):
    return cls.objects.filter(isDefault=True)[0]

  def clean_isDefault(self):
    v = self.cleaned_data['isDefault']
    if v:
      numTrue = ConDay.objects.filter(isDefault=True).count()
      if numTrue > 0:
        from django.core.exceptions import ValidationError
        raise ValidationError('Only one ConDay can be the default')
    return v

class SlotLength(models.Model):
  "A SlotLength is how long a given item may run."
  name = models.CharField(max_length=30)
  length = models.IntegerField(default=60)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()

  class Meta:
    ordering = [ 'isDefault', 'length' ]

  def __unicode__(self):
    return self.name

  @classmethod
  def find_default(cls):
    return cls.objects.filter(isDefault=True)[0]

class Slot(models.Model):
  """
  a Slot is a potential position in the day at which
  an item may start.
  """
  start = models.IntegerField()
  length = models.ForeignKey(SlotLength, default=SlotLength.find_default)
  startText = models.CharField(max_length=20)
  slotText = models.CharField(max_length=20)
  visible = models.BooleanField(default=True)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()

  class Meta:
    ordering = [ 'isDefault', 'start' ]

  def __unicode__(self):
    return self.startText

  @classmethod
  def find_default(cls):
    return cls.objects.filter(isDefault=True)[0]

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

class EnumTable(models.Model):
  "Various name/value choices, with a default choice."
  name = models.CharField(max_length=64)
  isDefault = models.BooleanField()
  isUndefined = models.BooleanField()
  gridOrder = models.IntegerField(default=1)
  description = models.TextField(blank=True)

  class Meta:
    ordering = [ 'gridOrder' ]
    abstract = True

  @classmethod
  def find_default(cls):
    return cls.objects.filter(isDefault=True)[0]

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

  def __unicode__(self):
    return self.name

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
  kind = models.ForeignKey(KitKind, default=KitKind.find_default)
  count = models.SmallIntegerField(default=1)
  setupAssistance = models.BooleanField()
  notes = models.TextField(blank=True)
  status = models.ForeignKey(KitStatus, default=KitStatus.find_default)

class KitThing(models.Model):
  name = models.CharField(max_length=64)
  description = models.TextField(blank=True)
  kind = models.ForeignKey(KitKind, default=KitKind.find_default)
  count = models.SmallIntegerField(default=1)
  role = models.ForeignKey(KitRole, default=KitRole.find_default)
  source = models.ForeignKey(KitSource, default=KitSource.find_default)
  department = models.ForeignKey(KitDepartment, default=KitDepartment.find_default)
  basis = models.ForeignKey(KitBasis, default=KitBasis.find_default)
  status = models.ForeignKey(KitStatus, default=KitStatus.find_default)
  cost = models.IntegerField(default=0)
  insurance = models.IntegerField(default=0)
  nodes = models.TextField(blank=True)
  coordinator = models.CharField(max_length=64)
  availability = models.ManyToManyField(KitAvailability, null=True, blank=True)

class KitBundle(models.Model):
  name = models.CharField(max_length=64)
  status = models.ForeignKey(KitStatus, default=KitStatus.find_default)
  things = models.ManyToManyField(KitThing)

class KitRoomAssignment(models.Model):
  room = models.ForeignKey('Room')
  thing = models.ForeignKey(KitThing)
  bundle = models.ForeignKey(KitBundle, null=True, blank=True)
  fromDay = models.ForeignKey(ConDay, related_name='kitroomfrom_set')
  fromSlot = models.ForeignKey(Slot, related_name='kitroomfrom_set')
  toDay = models.ForeignKey(ConDay, related_name='kitroomto_set')
  toSlot = models.ForeignKey(Slot, related_name='kitroomto_set')
  
class KitItemAssignment(models.Model):
  item = models.ForeignKey('Item')
  thing = models.ForeignKey(KitThing)
  bundle = models.ForeignKey(KitBundle, null=True, blank=True)

class RoomCapacity(models.Model):
  layout = models.ForeignKey(SeatingKind, default=SeatingKind.find_default)
  count = models.IntegerField()

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
  CanClash = models.BooleanField()
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
  kit = models.ManyToManyField(KitThing, through='KitRoomAssignment')
  parent = models.ForeignKey('self', null=True, blank=True)
  capacities = models.ManyToManyField(RoomCapacity, null=True, blank=True)
  availability = models.ManyToManyField(RoomAvailability, null=True, blank=True)
  

  class Meta:
    ordering = [ 'isDefault', 'gridOrder' ]

  def __unicode__(self):
    return self.name

  @classmethod
  def find_default(cls):
    return cls.objects.filter(isDefault=True)[0]

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
  gender = models.ForeignKey(Gender, default=Gender.find_default)
  complete = models.CharField(max_length=4, choices=YesNo, default='No')
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No')
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No')
  tags = models.ManyToManyField(Tag,null=True,blank=True)
  availability = models.ManyToManyField(PersonAvailability, null=True, blank=True)

  class Meta:
    verbose_name_plural = 'People'
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

class ScheduledManager(models.Manager):
  def get_query_set(self):
    def_day = ConDay.find_default()
    def_slot = Slot.find_default()
    def_len = SlotLength.find_default()
    def_room = Room.find_default()
    return super(ScheduledManager, self).get_query_set().exclude(day=def_day).exclude(start=def_slot).exclude(length=def_len).exclude(room=def_room)

class UnscheduledManager(models.Manager):
  def get_query_set(self):
    def_day = ConDay.find_default()
    def_slot = Slot.find_default()
    def_len = SlotLength.find_default()
    def_room = Room.find_default()
    return super(UnscheduledManager, self).get_query_set().filter(Q(day=def_day) | Q(start=def_slot) | Q(length=def_len) | Q(room=def_room))

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
  day = models.ForeignKey(ConDay, null=True, default=ConDay.find_default)
  start = models.ForeignKey(Slot, null=True, default=Slot.find_default)
  length = models.ForeignKey(SlotLength, default=SlotLength.find_default)
  room = models.ForeignKey(Room, default=Room.find_default)
  kind = models.ForeignKey(ItemKind, default=ItemKind.find_default)
  seating = models.ForeignKey(SeatingKind, default=SeatingKind.find_default)
  frontLayout = models.ForeignKey(FrontLayoutKind, default=FrontLayoutKind.find_default)
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
  people = models.ManyToManyField(Person, through='ItemPerson')
  kitRequests = models.ForeignKey(KitRequest, null=True, blank=True)
  kit = models.ManyToManyField(KitThing, through='KitItemAssignment')
  audienceMics = models.BooleanField(default=False)
  allTechCrew = models.BooleanField(default=False)
  needsReset = models.BooleanField(default=False)
  needsCleanUp = models.BooleanField(default=False)
  mediaStatus = models.ForeignKey(MediaStatus, default=MediaStatus.find_default)
  follows = models.ForeignKey('self', null=True, blank=True)

  objects = models.Manager()
  scheduled = ScheduledManager()
  unscheduled = UnscheduledManager()

  class Meta:
    ordering = [ 'title', 'shortname' ]

  def __unicode__(self):
    if self.title:
      return self.title
    else:
      return self.shortname

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


class ItemPerson(models.Model):
  """
  An ItemPerson is the assignment of a Person to an Item.
  We should probably be implementing the Items -> People ManyToMany
  via a through field, rather than doing this.
  """
  item = models.ForeignKey(Item)
  person = models.ForeignKey(Person)
  role = models.ForeignKey(PersonRole, default=PersonRole.find_default)
  status = models.ForeignKey(PersonStatus, default=PersonStatus.find_default)
  visible = models.CharField(max_length=4, choices=YesNo, default='Yes')
  distEmail = models.CharField(max_length=4, choices=YesNo, default='No')
  recordingOkay = models.CharField(max_length=4, choices=YesNo, default='No')

  class Meta:
    verbose_name = 'Items-People'


class ItemPersonForm(ModelForm):
  fromPerson = forms.BooleanField(required=False, widget=forms.HiddenInput)
  class Meta:
    model = ItemPerson

class CheckResult(EnumTable):
  pass

class Check(models.Model):
  name = models.TextField(max_length=120)
  description = models.TextField(max_length=256)
  module = models.TextField(max_length=48)
  result = models.ForeignKey(CheckResult, default=CheckResult.find_default)

# Outstanding things that need thinking about:
# - Availability. Just make it a separate table, and add
# - Item Moves. Add when we need that.
# - Con Data, in various forms.

# Things that need something better than the admin interface:
# The slot form: need to be able to enter a time, and have that converted to mins.


