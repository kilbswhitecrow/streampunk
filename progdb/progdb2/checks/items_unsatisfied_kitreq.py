from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, Room

def run_check(check):
  """
  To find the items with unsatisfied kit requests, we need to find the items that:
  - have kit requests
  - but do not have kit-thing-item-assignments that satisfy the request
  - and are not in rooms that have kit-thing-room-assignments that satisfy the request
  """
  problem_items = []
  items = Item.scheduled.annotate(num_reqs=Count('kitRequests')).exclude(num_reqs=0)
  for item in items:
    if not (item.satisfies_kit_requests() or item.room_satisfies_kit_requests()):
      problem_items.append(item)
  return CheckOutput(check, problem_items)
