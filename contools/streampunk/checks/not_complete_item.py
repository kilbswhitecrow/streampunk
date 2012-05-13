from progdb2.checks.base import CheckOutput
from progdb2.models import Item

def run_check(check):
  return CheckOutput(check, Item.objects.exclude(complete='Yes'))
