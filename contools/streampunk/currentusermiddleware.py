# This file is part of Streampunk, a Django application for convention programmes
# This file was originally copied almost verbatim from this Stack Overflow post:
# http://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
# It's since been updated for revisions to the middleware model in Django.

from threading import local

_user = local()

class CurrentUserMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    _user.value = request.user
    response = self.get_response(request)
    return response

def get_current_username():
  try:
    return _user.value.username
  except AttributeError:
    return 'Unknown'
