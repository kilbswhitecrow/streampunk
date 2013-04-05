<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="streampunk">
  <html>
  <head><title>Streampunk dump</title></head>
  <body bgcolor="#FFFFFF">
  <h1><xsl:value-of select="@name"/></h1>
  <em>Taken at <xsl:value-of select="@timestamp"/></em>
    <xsl:apply-templates select="items"/>
    <xsl:apply-templates select="people"/>
    <xsl:apply-templates select="rooms"/>
    <xsl:apply-templates select="tech_items"/>
    <xsl:apply-templates select="tags"/>
  </body>
  </html>
</xsl:template>

<xsl:template match="rooms">
  <h2>Rooms</h2>
  <table border="1">
  <tr>
    <th>Room name</th>
    <th>Description</th>
    <th>Visible</th>
    <th>Grid Order</th>
    <th>Capacities</th>
  </tr>
    <xsl:apply-templates select="room"/>
  </table>
</xsl:template>

<xsl:template match="room">
  <tr>
    <td><xsl:value-of select="@name"/></td>
    <td><xsl:value-of select="@desc"/></td>
    <td><xsl:value-of select="@visible"/></td>
    <td><xsl:value-of select="@gridorder"/></td>
    <td>
      <xsl:apply-templates select="room_capacities"/>
    </td>
  </tr>
</xsl:template>

<xsl:template match="room_capacities">
  <xsl:value-of select="@name"/>
  <xsl:value-of select="@capacity"/>
  <br/>
</xsl:template>

<xsl:template match="people">
  <h2>People</h2>
    <xsl:apply-templates select="person"/>
</xsl:template>

<xsl:template match="person">
  <h3><xsl:value-of select="@name"/>
      (<xsl:value-of select="@memnum"/>)</h3>
  <p>Contact: <xsl:value-of select="@contact"/></p>
  <p>Email: <xsl:value-of select="@email"/></p>
  <p>Notes: <xsl:value-of select="@notes"/></p>
    <xsl:apply-templates select="tag_uses"/>
</xsl:template>

<xsl:template match="tag_uses">
  <p>Tags:
    <xsl:apply-templates select="tag_use"/>
  </p>
</xsl:template>

<xsl:template match="tag_use">
  <xsl:value-of select="@name"/>
</xsl:template>

<xsl:template match="tech_items">
  <h2>Tech</h2>
    <xsl:apply-templates select="tech_item"/>
</xsl:template>

<xsl:template match="tech_item">
  <h3><xsl:value-of select="@name"/></h3>
  <p><xsl:value-of select="@description"/></p>
  <p>Cost: <xsl:value-of select="@cost"/></p>
  <p>Notes: <xsl:value-of select="@notes"/></p>
  <p>Can move immediately after item: <xsl:value-of select="@move_immediately"/></p>
    <xsl:apply-templates select="class"/>
    <xsl:apply-templates select="department"/>
    <xsl:apply-templates select="source"/>
    <xsl:apply-templates select="basis"/>
</xsl:template>

<xsl:template match="class">
  <p>Class: <xsl:value-of select="@name"/></p>
</xsl:template>

<xsl:template match="department">
  <p>Department: <xsl:value-of select="@name"/></p>
</xsl:template>

<xsl:template match="source">
  <p>Source: <xsl:value-of select="@name"/></p>
</xsl:template>

<xsl:template match="basis">
  <p>Basis: <xsl:value-of select="@name"/></p>
</xsl:template>

<xsl:template match="items">
  <h2>Programme items</h2>
    <xsl:apply-templates select="item"/>
</xsl:template>

<xsl:template match="item">
  <h3><xsl:value-of select="@title"/></h3>
  <p>Start: <xsl:value-of select="@start"/></p>
  <p>Length: <xsl:value-of select="@length"/></p>
  <p>Kind: <xsl:value-of select="@kind"/></p>
  <p>Visible: <xsl:value-of select="@visible"/></p>
  <p>Expected Audience: <xsl:value-of select="@exp"/></p>
  <p>Seating: <xsl:value-of select="@seating"/></p>
  <p>Gophers: <xsl:value-of select="@gophers"/></p>
  <p>Complete: <xsl:value-of select="@complete"/></p>
  <p>Notes: <xsl:value-of select="@notes"/></p>
  <p>Blurb: <xsl:value-of select="@blurb"/></p>
  <p>Bring: <xsl:value-of select="@bring"/></p>
  <p>Budget: <xsl:value-of select="@budget"/></p>
  <p>Proj Needed: <xsl:value-of select="@projector"/></p>
  <p>Tech Needed: <xsl:value-of select="@tech_needed"/></p>
  <p>Tables: <xsl:value-of select="@tables"/></p>
    <xsl:apply-templates select="itemroom"/>
    <xsl:apply-templates select="participants"/>
    <xsl:apply-templates select="tech_uses"/>
    <xsl:apply-templates select="tag_uses"/>
</xsl:template>

<xsl:template match="itemroom">
  <p>Room: <xsl:value-of select="@name"/></p>
</xsl:template>

<xsl:template match="participants">
  <ul>
  <xsl:apply-templates select="participant"/>
  </ul>
</xsl:template>

<xsl:template match="participant">
  <li><xsl:value-of select="@name"/>
     (visible: <xsl:value-of select="@vis"/>,
               <xsl:value-of select="@role"/>,
               <xsl:value-of select="@status"/>) </li>
</xsl:template>

<xsl:template match="tech_uses">
  <p>Tech:<br/>
  <ul>
  <xsl:apply-templates select="tech_use"/>
  </ul></p>
</xsl:template>

<xsl:template match="tech_use">
  <li><xsl:value-of select="@name"/>: <xsl:value-of select="@setup"/></li>
</xsl:template>

</xsl:stylesheet>
