#!/bin/sh
python manage.py dumpdata --indent 2 \
  progdb2.ConDay \
  progdb2.SlotLength \
  progdb2.Slot \
  progdb2.Grid \
  progdb2.Gender \
  progdb2.ItemKind \
  progdb2.SeatingKind \
  progdb2.PersonRole \
  progdb2.PersonStatus \
  progdb2.Revision \
> progdb2/fixtures/initial_data.json

python manage.py dumpdata --indent 2 \
  progdb2.Room > progdb2/fixtures/room.json

