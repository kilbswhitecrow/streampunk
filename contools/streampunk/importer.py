"""
Importer - class to read in existing con information in XML format.

We expect a structure of the form:
<outer>
  <inner field1="value1" field2="value2" ... />
  <inner field1="value1" field2="value2" ... />
  <inner field1="value1" field2="value2" ... />
</outer>

We want to map each "inner" element to a new instance of a model. To do
the importing, we provide a dict which maps field1, field2, etc. (as values)
to parameters X, Y, Z, etc (keys) in the model instance.
"""

import xml.etree.ElementTree as ET

class RowIter(object):
  """
  An iterator class to walk over the array of table rows, returning a dict: field => data.
  This resulting dict is suitable for use as a kwargs parameter to the create instance of
  a model. We hope.
  """
  
  def __init__(self, rows, fieldmap):
    self.fieldmap = fieldmap
    self.rows = rows
    self.idx = 0
  def next(self):
    if self.idx >= len(self.rows):
      raise StopIteration
    else:
      row = self.rows[self.idx]
      self.idx += 1
      return row

class XMLImporter(object):

  def row_to_dict(self, row):
    return dict([ ( paramname, row.attrib[self.fieldmap[paramname]] ) for paramname in self.fieldmap.keys() ])

  def parse(self, filename, outer, inner, fieldmap, model):
    """
    Parse the XML file and retrieve the table's column names and row contents.
    Outer is the name of the outer-level element, that contains multiple instances
    of inner, where each inner element is the thing we want to import.
    Fieldmap is a dict, where the keys are the attributes we want to set in our model,
    and the values are the names of the attributes, within the "inner" element.
    """
    self.fieldmap = fieldmap
    self.model = model
    tree = ET.parse(filename)
    root = tree.getroot()
    if inner:
      rowset = root.find(outer)
      self.rows = [ self.row_to_dict(r) for r in rowset.findall(inner) ]
    else:
      self.rows = [ self.row_to_dict(r) for r in root.findall(outer) ]

  def __iter__(self):
    "Create an iterator over the rows in the table."
    return RowIter(self.rows, self.fieldmap)

  def __len__(self):
    "How many rows in the table?"
    return len(self.rows)

  def import_data(self):
    for kwargs in self:
      print "creating(%s)" % kwargs
      obj = self.model.objects.create(**kwargs)
      obj.save()
