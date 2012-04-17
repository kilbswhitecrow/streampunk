import datetime
from progdb.progdb2.models import SlotLength, Slot, Grid, ConDay, ItemKind, SeatingKind, PersonStatus, PersonRole, Room, Revision, Tag, ItemPerson, Item, Person



# Same argument applies to Revision.

def PopulateProgDB():
  cd = ConDay(name = 'Friday',
              date = datetime.date(2012, 4, 6),
              order = 2,
              visible = 1)
  cd.save()
  cd = ConDay(name = 'Saturday',
              date = datetime.date(2012, 4, 7),
              order = 2,
              visible = 1)
  cd.save()
  cd = ConDay(name = 'Sunday',
              date = datetime.date(2012, 4, 8),
              order = 2,
              visible = 1)
  cd.save()
  cd = ConDay(name = 'Monday',
              date = datetime.date(2012, 4, 9),
              order = 2,
              visible = 1)
  cd.save()

  rev0 = Revision(baseline = datetime.date.today(),
                  colour = 'black',
                  description = 'First draft')
  rev0.save()

  s = SlotLength(name = '30mins', length = 30)
  s.save()
  s60 = SlotLength(name = '1 hour', length = 60)
  s60.save()
  s = SlotLength(name = '90mins', length = 90)
  s.save()
  s = SlotLength(name = '2 hours', length = 120)
  s.save()
  
  s10am = Slot(start = (10 * 60),
               length = s60,
               startText = '10am',
               slotText = '10-11am')
  s10am.save()
  s11am = Slot(start = (11 * 60),
               length = s60,
               startText = '11am',
               slotText = '11am-Noon')
  s11am.save()
  s12pm = Slot(start = (12 * 60),
               length = s60,
               startText = 'Noon',
               slotText = 'Noon-1pm')
  s12pm.save()
  s1pm = Slot(start = (13 * 60),
               length = s60,
               startText = '1pm',
               slotText = '1-2pm')
  s1pm.save()
  
  s2pm = Slot(start = (14 * 60),
               length = s60,
               startText = '2pm',
               slotText = '2-3pm')
  s2pm.save()
  s3pm = Slot(start = (15 * 60),
               length = s60,
               startText = '3pm',
               slotText = '3-4pm')
  s3pm.save()
  s4pm = Slot(start = (16 * 60),
               length = s60,
               startText = '4pm',
               slotText = '4-5pm')
  s4pm.save()
  s5pm = Slot(start = (17 * 60),
               length = s60,
               startText = '5pm',
               slotText = '5-6pm')
  s5pm.save()
  
  s6pm = Slot(start = (18 * 60),
               length = s60,
               startText = '6pm',
               slotText = '6-7pm')
  s6pm.save()
  s7pm = Slot(start = (19 * 60),
               length = s60,
               startText = '7pm',
               slotText = '7-8pm')
  s7pm.save()
  s8pm = Slot(start = (20 * 60),
               length = s60,
               startText = '8pm',
               slotText = '8-9pm')
  s8pm.save()
  s9pm = Slot(start = (21 * 60),
               length = s60,
               startText = '9pm',
               slotText = '9-10pm')
  s9pm.save()
  
  s10pm = Slot(start = (22 * 60),
               length = s60,
               startText = '10pm',
               slotText = '10-11pm')
  s10pm.save()
  s11pm = Slot(start = (23 * 60),
               length = s60,
               startText = '11pm',
               slotText = '11pm-Midnight')
  s11pm.save()
  s12am = Slot(start = (24 * 60),
               length = s60,
               startText = 'Midnight',
               slotText = 'Midnight-1am')
  s12am.save()
  s1am = Slot(start = (25 * 60),
               length = s60,
               startText = '1am',
               slotText = '1-2am')
  s1am.save()
  
  g = Grid(name = '10am-2pm')
  g.save()
  g.slots.add(s10am)
  g.slots.add(s11am)
  g.slots.add(s12pm)
  g.slots.add(s1pm)
  g.save()

  g = Grid(name = '2-6pm')
  g.save()
  g.slots.add(s2pm)
  g.slots.add(s3pm)
  g.slots.add(s4pm)
  g.slots.add(s5pm)
  g.save()

  g = Grid(name = '6-10pm')
  g.save()
  g.slots.add(s6pm)
  g.slots.add(s7pm)
  g.slots.add(s8pm)
  g.slots.add(s9pm)
  g.save()

  g = Grid(name = '10pm-2am')
  g.save()
  g.slots.add(s10pm)
  g.slots.add(s11pm)
  g.slots.add(s12am)
  g.slots.add(s1am)
  g.save()
  
  ik = ItemKind(name = 'Panel',
                isDefault = True,
                gridOrder = 10,
                description = 'Standard Panel discussion')
  ik.save()
  ik = ItemKind(name = 'Talk',
                isDefault = False,
                gridOrder = 20,
                description = 'Someone presenting a talk or speech')
  ik.save()
  ik = ItemKind(name = 'Workshop',
                isDefault = False,
                gridOrder = 30,
                description = 'An activity that involves everyone attending')
  ik.save()
  ik = ItemKind(name = 'Exercise',
                isDefault = False,
                gridOrder = 40,
                description = 'A physical activity')
  ik.save()
  ik = ItemKind(name = 'Game',
                isDefault = False,
                gridOrder = 50,
                description = 'A item with rules and a winner')
  ik.save()
  ik = ItemKind(name = 'Other',
                isDefault = False,
                gridOrder = 200,
                description = "Something that doesn't fit into these categories")
  ik.save()
  
  
  sk = SeatingKind(name = 'Theatre',
                   isDefault = True,
                   gridOrder = 10,
                   description = 'Chairs in rows facing the front')
  sk.save()
  sk = SeatingKind(name = 'Chairs around wall',
                   isDefault = False,
                   gridOrder = 20,
                   description = 'Chairs against the walls, with the centre space empty')
  sk.save()
  sk = SeatingKind(name = 'Boardroom',
                   isDefault = False,
                   gridOrder = 30,
                   description = 'Chairs around a single table in the middle of the room')
  sk.save()
  sk = SeatingKind(name = 'Empty',
                   isDefault = False,
                   gridOrder = 40,
                   description = 'No chairs or tables')
  sk.save()
  sk = SeatingKind(name = 'Cabaret',
                   isDefault = False,
                   gridOrder = 50,
                   description = 'Chairs around circular tables')
  sk.save()
  
  pr = PersonRole(name = 'Panellist',
                  isDefault = True,
                  gridOrder = 10,
                  description = 'On a panel, but not running it')
  pr.save()
  pr = PersonRole(name = 'Moderator',
                  isDefault = False,
                  gridOrder = 20,
                  description = 'Running a panel')
  pr.save()
  pr = PersonRole(name = 'Speaker',
                  isDefault = False,
                  gridOrder = 30,
                  description = 'Presenting a talk or lecture')
  pr.save()
  pr = PersonRole(name = 'Interviewer',
                  isDefault = False,
                  gridOrder = 40,
                  description = 'Interviewing a guest')
  pr.save()
  pr = PersonRole(name = 'Interviewee',
                  isDefault = False,
                  gridOrder = 50,
                  description = 'Being interviewed')
  pr.save()
  
  ps = PersonStatus(name = 'Proposed',
                    isDefault = True,
                    gridOrder = 10,
                    description = 'Would be good for this item, but not contacted yet')
  ps.save()
  ps = PersonStatus(name = 'Invited',
                    isDefault = False,
                    gridOrder = 20,
                    description = 'Has been invited, not yet confirmed')
  ps.save()
  
  ps = PersonStatus(name = 'Confirmed',
                    isDefault = False,
                    gridOrder = 30,
                    description = 'Has confirmed item participation')
  ps.save()
  
  nowhere = Room(name = 'Nowhere',
                 description = 'For items that have not yet been allocated a room, or that do not need one.',
                 visible = False,
                 hasProj = 'No',
                 gridOrder = 99)
  
  nowhere.save()
  
  everywhere = Room(name = 'Everywhere',
                    description = 'For items that are in no fixed location, e.g. a treasure hunt.',
                    visible = True,
                    hasProj = 'No',
                    gridOrder = 95)
  everywhere.save()
  
