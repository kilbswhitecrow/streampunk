from django.contrib.auth.models import Group, Permission

group_perms = {
  # Database Admins should get all permissions, plus is_staff, and probably superuser too.
  "progdbadmin" : [
        "edit_private",
        "edit_public",
        "read_public",
        "read_private",
        "config_db",
        "edit_programme",
        "edit_kit",
        "send_direct_email",
        "send_item_email",
        "send_mass_email",
        "import_data",
        "export_data",
        "edit_room",
        "edit_tags",
   ],
  # Con Committee should get all permissions except configdb - and is_staff, too?
  "concom" : [
        "edit_private",
        "edit_public",
        "read_public",
        "read_private",
        "edit_programme",
        "edit_kit",
        "send_direct_email",
        "send_item_email",
        "send_mass_email",
        "import_data",
        "export_data",
        "edit_room",
        "edit_tags",
   ],
  # Con Staff get to read everything and mail people, but
  # don't get to change anything
  "constaff" : [
        "read_public",
        "read_private",
        "send_direct_email",
        "send_item_email",
        "send_mass_email",
   ],
  # Programme Ops can change all the programme-related stuff, but not tech stuff
  "progops" : [
        "edit_private",
        "edit_public",
        "read_public",
        "read_private",
        "edit_programme",
        "send_direct_email",
        "send_item_email",
        "send_mass_email",
        "edit_room",
        "edit_tags",
   ],
  # Tech can edit all the tech stuff, but can't change the programme stuff.
  "tech" : [
        "edit_private",
        "edit_public",
        "read_public",
        "read_private",
        "edit_kit",
        "send_direct_email",
        "send_item_email",
        "send_mass_email",
        "edit_room",
        "edit_tags",
   ],
  # Participants can see all the public data, and can send emails to
  # people on items. Can't change anything, though.
  "participant" : [
        "read_public",
        "send_direct_email",
        "send_item_email",
   ],
}

def add_con_groups():
  added_perms = []
  for group_name in group_perms:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
      for perm_name in group_perms.get(group_name):
        perm = Permission.objects.get_by_natural_key(codename=perm_name, app_label='progdb2', model='UserProfile')
        group.permissions.add(perm)
        added_perms.append("%s:%s" % ( group_name, perm_name ))
      perm.save()
  return added_perms
