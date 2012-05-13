from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, ItemPerson, Person

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same person assigned to them.
  # Result is interesting, because we really want to return an item/person pair here,
  # not just an item.

  things = []

  # Only interested in scheduled items that actually have people on them.
  items = Item.scheduled.all().annotate(num_people=Count('people')).filter(num_people__gt=0)
  for itemx in items:
    peoplex = itemx.people.all()
    for person in peoplex:
      # fetch the other items that person is on.
      person_items = ItemPerson.objects.filter(person=person).exclude(item=itemx)
      for pi in person_items:
        itemy = pi.item
        if itemx.overlaps(itemy):
          things.append((itemx, itemy, person))
  return CheckOutput(check, things)
