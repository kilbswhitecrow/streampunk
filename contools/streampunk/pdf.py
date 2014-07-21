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
    self.response = response
    self.logo = logo
    self.header_font = "Helvetica-Bold"
    self.row_font = "Helvetica"
    self.card_name_font_size = 72
    self.card_name_leading = self.card_name_font_size * 1.2
    self.card_mod_font_size = 20
    self.card_mod_leading = self.card_mod_font_size * 1.2
    self.drinks_font_size = 20
    self.drinks_leading = self.drinks_font_size * 2

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
    if canv==None:
      canv = canvas.Canvas(filename, pagesize)
    return canv.stringWidth(text, style.fontName, style.fontSize)

  def maxTextWidth(self, texts, style, canv=None, filename='dummy.pdf', pagesize=A4):
    if canv==None:
      canv = canvas.Canvas(filename, pagesize)
    max = 0
    for text in texts:
      width = self.textWidth(text, style, canv)
      max = width if max < width else max
    return max

  def begin_namecards(self):
    self.normstyle = self.styles['Normal']
    self.namestyle = self.styles['CardName']
    self.modstyle = self.styles['CardMod']
    self.tstyle = TableStyle([
        ('GRID', (0,0), (0, 0), 1, colors.black),
    ])
    self.story = [ ]
    self.doc = SimpleDocTemplate(self.response, pagesize=A4L)
    self.doc.streampunk_pdf = self

  def end_namecards(self):
    def namecard_template(canv, doc):
      canv.saveState()
      # Fold
      midline = A4L[1] / 2
      canv.line(0, midline, A4L[0], midline)
      # Logo
      canv.drawImage(image=doc.streampunk_pdf.logo, x=20, y=20)
      canv.restoreState()
    self.doc.build(self.story, onFirstPage=namecard_template, onLaterPages=namecard_template)

  def namecard(self, slot, room, title, name, is_mod):
    self.story.append(Paragraph(slot, self.normstyle))
    self.story.append(Paragraph(title, self.normstyle))
    self.story.append(Paragraph(room, self.normstyle))
    self.story.append(Spacer(1, A4L[1] * 0.35))
    self.story.append(Table([ [ Paragraph(name, self.namestyle) ] ], style=self.tstyle))
    if is_mod:
      self.story.append(Paragraph(room, self.modstyle))
    self.story.append(PageBreak())


  def begin_drinks_forms(self):
    self.normstyle = self.styles['Normal']
    self.rowstyle = self.styles['DrinksData']
    self.headstyle = self.styles['DrinksHeading']
    self.doc = SimpleDocTemplate(self.response)
    self.tstyle = TableStyle([
      ('GRID', (0,0), (-1, -1), 1, colors.black),
    ])
    self.colWidths=[ None, cm, cm, inch * 3 ]
    self.story = [ ]
    self.headers = [ [ Paragraph('Name', self.headstyle),
                       Paragraph('M', self.headstyle),
                       Paragraph('', self.headstyle),
                       Paragraph('Drink', self.headstyle) ] ]

  def end_drinks_forms(self):
    self.doc.build(self.story)

  def drinksform(self, slot, room, title, people):
    "People is a list of (badge, is_mod) tuples."
    def row(info, st):
      badge, is_mod = info
      m = 'M' if is_mod else ''
      return [ Paragraph(t, st) for t in [ badge, m, '', '' ] ]

    if len(people) == 0:
      return
    self.story.append(Paragraph(slot, self.headstyle))
    self.story.append(Paragraph(title, self.rowstyle))
    self.story.append(Paragraph(room, self.rowstyle))
    rows = [ row(person, self.rowstyle) for person in people ]
    data = self.headers + rows
    self.story.append(Table(data=data, style=self.tstyle, colWidths=self.colWidths))
    self.story.append(Paragraph('M indicates person is the moderator.', self.normstyle))
    self.story.append(PageBreak())

  def begin_door_listings(self):
    self.normstyle = self.styles['Normal']
    self.rowstyle = self.styles['DrinksData']
    self.headstyle = self.styles['DrinksHeading']
    self.doc = SimpleDocTemplate(self.response)
    self.doc.streampunk_pdf = self
    self.cellpad = 6 # Actually, this is the default
    self.tstyle = TableStyle([
      ('GRID', (0,0), (-1, -1), 1, colors.black),
      ('VALIGN', (0,0), (-1, -1), 'TOP'),
      ('LEFTPADDING', (0,0), (-1, -1), self.cellpad),
      ('RIGHTPADDING', (0,0), (-1, -1), self.cellpad),
    ])
    self.story = [ ]

  def end_door_listings(self):
    def drinksform_template(canv, doc):
      canv.saveState()
      canv.drawImage(image=doc.streampunk_pdf.logo, x=20, y=20)
      canv.restoreState()
    self.doc.build(self.story, onFirstPage=drinksform_template, onLaterPages=drinksform_template)
  def door_listing(self, day, room, items):
    "Items is a list of (title, starttext) tuples."
    if len(items) == 0:
      return
    start_width = self.maxTextWidth([ i[1] for i in items ], self.rowstyle)
    start_width = start_width + ( 2 * self.cellpad )
    self.story.append(Paragraph("%s %s" % (room, day), self.headstyle))
    data = [ [ Paragraph(i[1], self.rowstyle), Paragraph(i[0], self.rowstyle) ] for i in items ]
    self.story.append(Table(data, style=self.tstyle, colWidths=[ start_width, None ]))
    self.story.append(PageBreak())

