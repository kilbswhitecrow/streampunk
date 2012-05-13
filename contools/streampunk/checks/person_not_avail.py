from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, ItemPerson, Person, ConInfoBool

def run_check(check):
  """
  List of people who are not available for items on which they've been scheduled.
  """
  if ConInfoBool.objects.no_avail_means_always_avail():
    return []

  things = []

  # Only interested in scheduled items that actually have people on them.
  items = Item.scheduled.all().annotate(num_people=Count('people')).filter(num_people__gt=0)
  for itemx in items:
    peoplex = itemx.people.all()
    for person in peoplex:
      if not person.available_for(itemx):
        things.append((itemx, person))
  return CheckOutput(check, things)
