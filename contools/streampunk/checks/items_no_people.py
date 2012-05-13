from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, ItemPerson, Person

def run_check(check):
  return CheckOutput(check, Item.objects.annotate(num_people=Count('people')).filter(num_people=0))
