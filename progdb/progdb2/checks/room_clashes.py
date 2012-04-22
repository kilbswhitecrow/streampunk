from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, Room

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same room assigned to them.
  # Result is interesting, because we really want to return an item/room pair here,
  # not just an item.

  things = []

  # Only interested in scheduled items (that eliminates Nowhere) that are in
  # rooms that participate in clashes.
  rooms = Room.objects.filter(CanClash=True)
  for r in rooms:
    items = Item.scheduled.filter(room=r)
    for itemx in items:
      for itemy in items:
        if itemx.overlaps(itemy):
          things.append((itemx, itemy, r))
  return CheckOutput(check, things)
