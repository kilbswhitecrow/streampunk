# Some support for connecting up items and people, after doing
# an import.

from streampunk.models import Item, Person, ItemPerson, Tag

def get_person(first=None, middle=None, last=None):
  if first and middle and last:
    return Person.objects.get(firstName=first, middleName=middle, lastName=last)
  elif first and last:
    return Person.objects.get(firstName=first, lastName=last)
  elif first:
    return Person.objects.get(firstName=first)
  else:
    return Person.objects.get(lastName=last)

def get_item(short=None, title=None):
  if short == None:
    i = Item.objects.get(title=title)
  else:
    i = Item.objects.get(shortname=short)
  return i

def get_tag(name):
  return Tag.objects.get(name=name)

def add_item_person(item, person):
  ItemPerson.objects.create(item=item, person=person)

def add_item_tag(item, tag):
  item.tags.add(tag)

def add_person_tag(person, tag):
  person.tags.add(tag)

def connect_people():
  book = get_person(last='Book')
  jayne = get_person(first='Jayne')
  giles = get_person(last='Giles')
  xander = get_person(last='Harris')
  willow = get_person(first='Willow')
  dawn = get_person(first='Dawn')
  buffy = get_person(first='Buffy')
  river = get_person(first='River')
  simon = get_person(first='Simon')
  mal = get_person(first='Malcolm')

  cons_old_and_new = get_item(short='cons: old vs new')
  art_auction = get_item(short='Art Auction')
  bid_session = get_item(short='bid session')
  ceilidh = get_item(short='Ceilidh')
  opening_ceremony = get_item(short='opening ceremony')
  closing_ceremony = get_item(short='closing ceremony')
  disco = get_item(short='Disco')

  art = get_tag('Art')
  books = get_tag('Books')
  comics = get_tag('Comics')
  filk = get_tag('Filk')
  science = get_tag('Science')

  add_item_person(opening_ceremony, giles)
  add_item_person(opening_ceremony, buffy)
  add_item_person(opening_ceremony, xander)
  add_item_person(opening_ceremony, willow)
  add_item_person(closing_ceremony, mal)
  add_item_person(closing_ceremony, jayne)
  add_item_person(closing_ceremony, simon)
  add_item_person(closing_ceremony, river)
  add_item_person(closing_ceremony, book)
  add_item_person(cons_old_and_new, giles)
  add_item_person(cons_old_and_new, willow)
  add_item_person(cons_old_and_new, mal)
  add_item_person(disco, river)
  add_item_person(disco, willow)
  add_item_person(disco, buffy)
  add_item_person(disco, xander)
  add_item_person(ceilidh, river)
  add_item_person(ceilidh, willow)
  add_item_person(ceilidh, simon)
  add_item_person(ceilidh, mal)
  add_item_person(bid_session, mal)
  add_item_person(bid_session, book)
  add_item_person(art_auction, mal)
  add_item_person(art_auction, book)
  add_item_person(art_auction, simon)

  add_item_tag(disco, filk)
  add_item_tag(opening_ceremony, comics)
  add_item_tag(closing_ceremony, science)
  add_item_tag(closing_ceremony, books)
  add_item_tag(art_auction, art)
  add_item_tag(art_auction, comics)
  add_item_tag(art_auction, books)

  add_person_tag(giles, filk)
  add_person_tag(giles, books)
  add_person_tag(xander, comics)
  add_person_tag(jayne, comics)
  add_person_tag(willow, books)
  add_person_tag(willow, science)
  add_person_tag(river, science)
  add_person_tag(river, filk)
  add_person_tag(simon, science)
