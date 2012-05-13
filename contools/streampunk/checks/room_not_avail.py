from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, Room

def run_check(check):

  things = []

  # Only interested in scheduled items (that eliminates Nowhere) that are in
  # rooms that participate in clashes.
  rooms = Room.objects.filter(CanClash=True)
  for r in rooms:
    items = Item.scheduled.filter(room=r)
    for itemx in items:
      if not r.available_for(itemx):
        things.append((itemx, r))
  return CheckOutput(check, things)
