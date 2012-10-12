from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from streampunk.models import ConInfoString

def myexample(request, bear, tom):
  print "Bear is %s, Tom is %s" % (bear, tom)
  return simplejson.dumps({'message': 'Hello world'})

def con_name(request):
  return simplejson.dumps({'con_name': ConInfoString.objects.con_name() })

dajaxice_functions.register(myexample)
dajaxice_functions.register(con_name)
