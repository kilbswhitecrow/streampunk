from progdb2.models import Check, CheckResult
from progdb2.models import Person, Item

class CheckOutput:
  def __init__(self, check, things):
    self.check = check
    self.things = things
    self.count = len(things)
    self.template = "progdb2/checks/%s.html" % (check.module,)
    self.person_list = check.result.name == 'Person List'
    self.item_list = check.result.name == 'Item List'
    self.mixed_tuple_list = check.result.name == 'Mixed Tuple List'
