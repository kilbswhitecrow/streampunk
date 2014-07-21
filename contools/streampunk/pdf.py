# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2014 Stephen Kilbane
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, TableStyle, Table, PageBreak

A4L = landscape(A4)

class StreampunkPdf(object):
  """
  A wrapper around a PDF output library, to insulate the Django ORM
  from the PDF generation, and vice versa.
  """

  def __init__(self, response, logo, borders=0):
    """
    Response is the HttpResponse to the Django view. Logo is the name of
    the file we should use to whack the Con's logo onto official publications.
    If borders is true, we'll see the bounding boxes of text, for debugging.
    """
    self.response = response
    self.logo = logo

    # Set up some fonts and respective sizes. The leading is how much
    # vertical space a line of text takes, for the font. This is necessary
    # where we emit several lines of text (so that Platypus can advance the
    # correct amount), but it's also vital for tables, so that the rows get
    # the right height. For the drinks form, we deliberately make the leading
    # larger than it would be normally, so that there's more space to write
    # in the drinks request.
    self.header_font = "Helvetica-Bold"
    self.row_font = "Helvetica"
    self.card_name_font_size = 72
    self.card_name_leading = self.card_name_font_size * 1.2
    self.card_mod_font_size = 20
    self.card_mod_leading = self.card_mod_font_size * 1.2
    self.drinks_font_size = 20
    self.drinks_leading = self.drinks_font_size * 2

    # Grab Platypus's default styles, and create a few more.
    # Mainly, we're changing the font style/size, but we'll
    # also create a red bounding box if borders was non-zero.

    self.styles = getSampleStyleSheet()

    self.styles.add(ParagraphStyle(name='CardName',
                          fontName=self.header_font,
                          fontSize=self.card_name_font_size,
                          borderWidth=borders,
                          borderColor=colors.red,
                          leading=self.card_name_leading))

    self.styles.add(ParagraphStyle(name='CardMod',
                          fontName=self.header_font,
                          fontSize=self.card_mod_font_size,
                          borderWidth=borders,
                          borderColor=colors.red,
                          leading=self.card_mod_leading))

    self.styles.add(ParagraphStyle(name='DrinksData',
                          fontName=self.row_font,
                          fontSize=self.drinks_font_size,
                          borderWidth=borders,
                          borderColor=colors.red,
                          leading=self.drinks_leading))

    self.styles.add(ParagraphStyle(name='DrinksHeading',
                          fontName=self.header_font,
                          fontSize=self.drinks_font_size,
                          borderWidth=borders,
                          borderColor=colors.red,
                          leading=self.drinks_leading))

  def textWidth(self, text, style, canv=None, filename='dummy.pdf', pagesize=A4):
    "How wide is this text, for a given style?"
    # We need an instance of the Canvas, in order to determine the width. Create
    # one if we haven't been given one. XXX we should really write to a temporary
    # file object that doesn't get created.
    if canv==None:
      canv = canvas.Canvas(filename, pagesize)
    return canv.stringWidth(text, style.fontName, style.fontSize)

  def maxTextWidth(self, texts, style, canv=None, filename='dummy.pdf', pagesize=A4):
    "Determine the width of the widest of the strings in texts, using the given style."
    # We create a canvas if we don't have one. XXX Shouldn't really give a filename,
    # but a temporary file object that doesn't emit output.
    if canv==None:
      canv = canvas.Canvas(filename, pagesize)
    max = 0
    for text in texts:
      width = self.textWidth(text, style, canv)
      max = width if max < width else max
    return max

  def begin_namecards(self):
    "Prepare to emit one or more namecards."
    # Choose styles for the output text
    self.normstyle = self.styles['Normal']    # Item info, above the fold.
    self.namestyle = self.styles['CardName']  # The person's name
    self.modstyle = self.styles['CardMod']    # Identify the person as a moderator

    # We emit the person's name as a single-celled table, so that we get a nice border.
    self.tstyle = TableStyle([
        ('GRID', (0,0), (0, 0), 1, colors.black),
    ])

    # We set of a Platypus story on a landscape page, so that it can be
    # folded in half along its length, and propped up on the table.
    self.story = [ ]
    self.doc = SimpleDocTemplate(self.response, pagesize=A4L)

    # Attach ourselves to the Platypus doc, so that we can get at our
    # logo later.
    self.doc.streampunk_pdf = self

  def end_namecards(self):
    "Finalise the generation of one or more namecards."

    # Create a template func, which paints the same constructs onto
    # each and every page, before adding the variable info.
    def namecard_template(canv, doc):
      "Mark the page with a fold line and a logo."
      canv.saveState()
      # Draw a line along the midline of the page, where it should be folded.
      midline = A4L[1] / 2
      canv.line(0, midline, A4L[0], midline)
      # Put the con's logo along the bottom.
      canv.drawImage(image=doc.streampunk_pdf.logo, x=20, y=20)
      canv.restoreState()

    # Tell Platypus to generate the document, using our page template for each page.
    self.doc.build(self.story, onFirstPage=namecard_template, onLaterPages=namecard_template)

  def namecard(self, slot, room, title, name, is_mod):
    "Emit a single namecard to the document."
    # In each case, the parameters are just the text to be drawn on the page,
    # apart from is_mod, which is boolean.

    # Draw the info for the item at the top left, which gives Green Room something
    # to use to sort name cards. This info appears above the fold, so isn't visible
    # to the audience when the card is folded.
    self.story.append(Paragraph(slot, self.normstyle))
    self.story.append(Paragraph(title, self.normstyle))
    self.story.append(Paragraph(room, self.normstyle))

    # Emit a somewhat-arbitrarily-sized chunk of vertical space, to move the cursor
    # to below the fold.
    self.story.append(Spacer(1, A4L[1] * 0.35))

    # Append a single-celled table containing the person's name.
    self.story.append(Table([ [ Paragraph(name, self.namestyle) ] ], style=self.tstyle))

    # If the person is a moderator, indicate this by another line beneath their name.
    if is_mod:
      self.story.append(Paragraph("Moderator", self.modstyle))
    # Start a new page, ready for the next name card.
    self.story.append(PageBreak())


  def begin_drinks_forms(self):
    "Prepare to emit one or more drinks forms."
    # Get references to a number of styles.
    self.normstyle = self.styles['Normal']        # For explaining the 'M' column
    self.rowstyle = self.styles['DrinksData']     # The persons' names.
    self.headstyle = self.styles['DrinksHeading'] # The column headers

    # Set up a Platypus doc, A4 layout.
    self.doc = SimpleDocTemplate(self.response)

    # We create a straightforward table. The first column is the name, and that
    # gets its width from the text within it. The remaining columns are given
    # fixed widths. They're mostly write-in.
    self.tstyle = TableStyle([
      ('GRID', (0,0), (-1, -1), 1, colors.black),
    ])
    self.colWidths=[ None, cm, cm, inch * 3 ]
    self.story = [ ]
    self.headers = [ [ Paragraph('Name', self.headstyle),      # The person's name.
                       Paragraph('M', self.headstyle),         # 'M', if they're the moderator.
                       Paragraph('', self.headstyle),          # A tick, for 'Drink bought'.
                       Paragraph('Drink', self.headstyle) ] ]  # Space to write in the drink request.

  def end_drinks_forms(self):
    "Finalise the generation of one or more drinks forms."
    # Generate the PDF document.
    self.doc.build(self.story)

  def drinksform(self, slot, room, title, people):
    "Add a drinks form to the document. People is a list of (badge, is_mod) tuples."

    # We get (badge name, is_mod) pairs - we want to convert that into a row of
    # four cells, each containing a Paragraph object for Platypus to render.
    def row(info, st):
      "Generate the row of the table, for a given person."
      badge, is_mod = info
      # If a person is the moderator, then stick 'M' into the second column.
      m = 'M' if is_mod else ''
      # Produce and return a list of four Paragraph cells.
      return [ Paragraph(t, st) for t in [ badge, m, '', '' ] ]

    # Don't create a drinks form unless there's someone to order the drink for.
    if len(people) == 0:
      return

    # Info about the item, so that Green Room know when to use it.
    self.story.append(Paragraph(slot, self.headstyle))
    self.story.append(Paragraph(title, self.rowstyle))
    self.story.append(Paragraph(room, self.rowstyle))

    # Create the rows of the table, for the people on this item.
    rows = [ row(person, self.rowstyle) for person in people ]
    data = self.headers + rows
    # Emit the table, followed by an explanation of the M column. Then start a new
    # page ready for the next drinks form.
    self.story.append(Table(data=data, style=self.tstyle, colWidths=self.colWidths))
    self.story.append(Paragraph('M indicates person is the moderator.', self.normstyle))
    self.story.append(PageBreak())

  def begin_door_listings(self):
    "Prepare to generate door listings."
    # Prepare our styles
    self.normstyle = self.styles['Normal']        # Not currently used.
    self.rowstyle = self.styles['DrinksData']     # For the items in the table.
    self.headstyle = self.styles['DrinksHeading'] # For the table headings.

    # Create a Platypus doc, and attach ourselves to it, so that we can get
    # at the Logo later.
    self.doc = SimpleDocTemplate(self.response)
    self.doc.streampunk_pdf = self

    # Our columns are startTime, item. We want to size the first column
    # based on the widest start time in the table. If we *just* do that,
    # then the times won't fit, because the table styles put padding to
    # the left and the right of the cell contents (and top and bottom,
    # but they don't interest us right now). That default padding happens
    # to be 6, but we want to set it explicitly so that we know we're
    # using the right amount when we take it into account for the column
    # width.
    self.cellpad = 6 # Actually, this is the default
    self.tstyle = TableStyle([
      ('GRID', (0,0), (-1, -1), 1, colors.black),
      ('VALIGN', (0,0), (-1, -1), 'TOP'),              # Put text at the top; items often wrap.
      ('LEFTPADDING', (0,0), (-1, -1), self.cellpad),
      ('RIGHTPADDING', (0,0), (-1, -1), self.cellpad),
    ])
    self.story = [ ]

  def end_door_listings(self):
    "Finalise generation of one or more door listings."
    # A page template for the door listings, to draw the
    # constant content, prior to painting on the variable content.
    def drinksform_template(canv, doc):
      "Draw the con logo on every page."
      canv.saveState()
      # Include the con's logo at the bottom of the page.
      canv.drawImage(image=doc.streampunk_pdf.logo, x=20, y=20)
      canv.restoreState()
    # Generate the PDF, putting the con logo on each page.
    self.doc.build(self.story, onFirstPage=drinksform_template, onLaterPages=drinksform_template)

  def door_listing(self, day, room, items):
    "Emit a single door listing. Items is a list of (title, starttext) tuples."
    # Don't emit a page if there are no items to list.
    if len(items) == 0:
      return
    # Obtain the width of the widest start time in the item list, and then
    # add on the width of the left and right padding, to give the actual
    # column width.
    start_width = self.maxTextWidth([ i[1] for i in items ], self.rowstyle)
    start_width = start_width + ( 2 * self.cellpad )

    # Explain which room and day this listing covers.
    self.story.append(Paragraph("%s %s" % (room, day), self.headstyle))

    # Convert the (item, time) tuples into rows containing Paragraph objects.
    data = [ [ Paragraph(i[1], self.rowstyle), Paragraph(i[0], self.rowstyle) ] for i in items ]

    # Emit the table, then start a new page, ready for the next door listing.
    self.story.append(Table(data, style=self.tstyle, colWidths=[ start_width, None ]))
    self.story.append(PageBreak())

