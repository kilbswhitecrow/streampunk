# This file is part of Streampunk, a Django application for convention programmes
# This file is copied almost verbatim from this Stack Overflow post:
# http://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model

from threading import local

_user = local()

class CurrentUserMiddleware(object):
  def process_request(self, request):
    _user.value = request.user

def get_current_username():
  try:
    return _user.value.username
  except AttributeError:
    return 'Unknown'
