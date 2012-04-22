"""
Forms for editing the models in ProgDB 2.0
"""

from django.db import models
from django import forms
from django.forms import ModelForm, BooleanField, HiddenInput
from django.forms.models import BaseModelFormSet
from progdb2.models import ItemPerson, Item, Person, Tag, Room, Check

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
