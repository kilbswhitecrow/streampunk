from django.db.models import Count
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, KitItemAssignment, KitRoomAssignment, Room

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same item assigned to them.
  # Also want items with kit assigned to them which overlaps with when same kit is
  # assigned to a room (which is not the room the item's in).
  # Also rooms where the same item is assigned concurrently.

  things = []

  kititems = KitItemAssignment.objects.all()
  kitrooms = KitRoomAssignment.objects.all()

  # Look for the same kithing assigned to overlapping items

  for kasx in kititems:
    for kasy in kititems:
      if not (kasx == kasy) and (kasx.thing == kasy.thing):
        if kasx.item.overlaps(kasy.item):
          things.append((kasx, kasy))

  # Look for rooms that have concurrent assignments

  for krax in kitrooms:
    for kray in kitrooms:
      if not (krax == kray) and (krax.thing == kray.thing):
        if krax.overlaps_room_assignment(kray):
          things.append((krax, kray))

  # Look for the same kit thing assigned to a room and item concurrently

  for kra in kitrooms:
    for kas in kititems:
      if kra.thing == kas.thing and not (kas.item.room == kra.room):
        if kra.overlaps(kas.item):
          things.append((kra, kas))

  # First part: Only interested in scheduled items that actually have kit things assigned
  return CheckOutput(check, things)
