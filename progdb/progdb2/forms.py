"""
Forms for editing the models in ProgDB 2.0
"""

from django.db import models
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from progdb2.models import ItemPerson, Item, Person, Tag, Room

class ItemPersonForm(ModelForm):
  fromPerson = forms.BooleanField(required=False, widget=forms.HiddenInput)
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

class PersonForm(ModelForm):
  class Meta:
    model = Person

class TagForm(ModelForm):
  class Meta:
    model = Tag

class RoomForm(ModelForm):
  class Meta:
    model = Room

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
