from progdb2.checks.base import CheckOutput
from progdb2.models import Person

def run_check(check):
  return CheckOutput(check, Person.objects.filter(memnum = -1))
