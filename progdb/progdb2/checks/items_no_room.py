from progdb2.checks.base import CheckOutput
from progdb2.models import Item, Room

def run_check(check):
  return CheckOutput(check, Item.objects.filter(room=Room.objects.find_undefined()))
