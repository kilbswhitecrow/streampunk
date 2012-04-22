#!/bin/sh
set +x
python manage.py dumpdata --indent 2 \
  progdb2.ConDay \
  progdb2.SlotLength \
  progdb2.Slot \
  progdb2.Grid \
  progdb2.Gender \
  progdb2.ItemKind \
  progdb2.SeatingKind \
  progdb2.FrontLayoutKind \
  progdb2.PersonRole \
  progdb2.PersonStatus \
  progdb2.Revision \
  progdb2.KitKind \
  progdb2.KitRole \
  progdb2.KitDepartment \
  progdb2.KitBasis \
  progdb2.KitStatus \
  progdb2.MediaStatus \
  progdb2.CheckResult \
  progdb2.Check \
  progdb2.ConInfoBool \
  progdb2.ConInfoInt \
  progdb2.ConInfoString \
> progdb2/fixtures/initial_data.json

python manage.py dumpdata --indent 2 \
  progdb2.Room > progdb2/fixtures/room.json

