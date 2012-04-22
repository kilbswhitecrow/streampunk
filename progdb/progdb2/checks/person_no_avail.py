from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Person

def run_check(check):
  """
  Return the list of people who have no availability defined.
  """
  return CheckOutput(check, Person.objects.all().annotate(num_availability=Count('availability')).filter(num_availability=0))
