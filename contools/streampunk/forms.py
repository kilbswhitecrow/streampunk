# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012 Stephen Kilbane
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
Forms for editing the models in Streampunk
"""

from django.db import models
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from django.forms.models import BaseModelFormSet
from streampunk.models import ItemPerson, Item, Person, Tag, Room, Check
from streampunk.models import KitThing, KitBundle, KitRequest, PersonList
from streampunk.models import KitRoomAssignment, KitItemAssignment, UserProfile

class ItemPersonForm(ModelForm):
  fromPerson = forms.BooleanField(required=False, widget=forms.HiddenInput)
  class Meta:
    model = ItemPerson

class DeleteItemPersonForm(ModelForm):
  confirm = forms.BooleanField(required=False, label='Okay to delete?')
  class Meta:
    model = ItemPerson

class ItemTagForm(ModelForm):
  """
  Used when we're modifying the tags of an item.
  """
  fromTag = forms.BooleanField(required=False, widget=forms.HiddenInput)
  class Meta:
    model = Item
    fields = ( 'tags', )

class ItemForm(ModelForm):
  class Meta:
    model = Item
    exclude = [ 'people', 'kit' ]

class PersonForm(ModelForm):
  class Meta:
    model = Person

class TagForm(ModelForm):
  class Meta:
    model = Tag

class RoomForm(ModelForm):
  class Meta:
    model = Room
    exclude = [ 'kit', ]

class KitThingForm(ModelForm):
  class Meta:
    model = KitThing

class KitBundleForm(ModelForm):
  class Meta:
    model = KitBundle

class KitRequestForm(ModelForm):
  class Meta:
    model = KitRequest

class KitRoomAssignmentForm(ModelForm):
  class Meta:
    model = KitRoomAssignment

class AddBundleToRoomForm(ModelForm):
  class Meta:
    model = KitRoomAssignment
    exclude = [ 'thing', ]

class AddBundleToItemForm(ModelForm):
  class Meta:
    model = KitItemAssignment
    exclude = [ 'thing', ]

class AddThingToRoomForm(ModelForm):
  class Meta:
    model = KitRoomAssignment
    exclude = [ 'bundle', ]

class AddThingToItemForm(ModelForm):
  class Meta:
    model = KitItemAssignment
    exclude = [ 'bundle', ]

class PersonTagForm(ModelForm):
  """
  Used when we're modifying the tags of a person
  """
  fromTag = forms.BooleanField(required=False, widget=forms.HiddenInput)
  class Meta:
    model = Person
    fields = ( 'tags', )

class AddMultipleTagsForm(forms.Form):
  tags = forms.ModelMultipleChoiceField(required=False, queryset=Tag.objects.all(),
                                        widget=forms.SelectMultiple(attrs={'size':'10'}))
  items = forms.ModelMultipleChoiceField(required=False, queryset=Item.objects.all(),
                                        widget=forms.SelectMultiple(attrs={'size':'10'}))
  people = forms.ModelMultipleChoiceField(required=False, queryset=Person.objects.all(),
                                        widget=forms.SelectMultiple(attrs={'size':'10'}))

class FillSlotUnschedForm(forms.Form):
  item = forms.ModelChoiceField(queryset=Item.unscheduled.all(),
                                widget=forms.Select(attrs={'size':'10'}))

class FillSlotSchedForm(forms.Form):
  item = forms.ModelChoiceField(queryset=Item.scheduled.all(),
                                widget=forms.Select(attrs={'size':'10'}))

class CheckModelFormSet(BaseModelFormSet):
  """
  Used as formset=CheckModelFormSet parameter to modelformset_factory
  Also want to use exclude=('x', 'y') parameter or fields=('a', 'b') option
  """
  def add_fields(self, form, index):
    super(CheckModelFormSet, self). add_fields(form, index)
    form.fields['enable'] = forms.BooleanField(required=False)

class EmailForm(forms.Form):
  subject = forms.CharField()
  message = forms.CharField(widget = forms.Textarea)
  includeItems = forms.BooleanField(label = u'Include items?', required=False)
  includeContact = forms.BooleanField(label = u"Include person's contact details?", required=False)
  includeAvail = forms.BooleanField(label = u'Include availability?', required=False)

class PersonListForm(ModelForm):
  class Meta:
    model = PersonList
    exclude = [ 'created', ]


class UserProfileForm(ModelForm):
  class Meta:
    model = UserProfile
    fields = [ 'show_shortname', 'show_tags', 'show_people', 'rooms_across_top', 'name_order', ]


class UserProfileFullForm(ModelForm):
  class Meta:
    model = UserProfile
    exclude = [ 'user', ]
