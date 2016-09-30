<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="streampunk">
  <html>
  <head><title>Streampunk dump</title></head>
  <body bgcolor="#FFFFFF">
  <h1><xsl:value-of select="@name"/></h1>
  <em>Taken at <xsl:value-of select="@timestamp"/></em>
  <p><a href="#rooms">Rooms</a></p>
  <p><a href="#people">People</a></p>
  <p><a href="#items">Items</a></p>
    <xsl:apply-templates select="rooms"/>
    <xsl:apply-templates select="people"/>
    <xsl:apply-templates select="items"/>
    <xsl:apply-templates select="availability"/>
  </body>
  </html>
</xsl:template>

<xsl:template match="rooms">
  <a name="rooms"><h2>Rooms</h2></a>
  <table border="1">
  <tr>
    <th>Room name</th>
    <th>Grid Order</th>
    <th>Parent</th>
    <th>Visible</th>
  </tr>
  <tr>
    <th colspan="4">Description</th>
  </tr>
  <tr>
    <th colspan="4">Priv. Notes</th>
  </tr>
  <tr>
    <th colspan="4">Tech Notes</th>
  </tr>
  <tr>
    <th>Default?</th>
    <th>Undefined?</th>
    <th colspan="2">Can Clash?</th>
  </tr>
  <tr>
    <th>Disabled Access?</th>
    <th>Wifi?</th>
    <th colspan="2">In radio range?</th>
  </tr>
  <tr>
    <th>Needs Sound?</th>
    <th>Natural Light?</th>
    <th>Securable?</th>
    <th>Cable runs?</th>
  </tr>
  <tr>
    <th>Control lights in room?</th>
    <th>Control Aircon in room?</th>
    <th>Openable windows?</th>
    <th>Closable curtains?</th>
  </tr>
    <xsl:apply-templates select="room"/>
  </table>
</xsl:template>

<xsl:template match="room">
  <tr>
    <td><xsl:value-of select="@name"/></td>
    <td><xsl:value-of select="@gridorder"/></td>
    <td><xsl:value-of select="@parent"/></td>
    <td><xsl:value-of select="@visible"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@privNotes"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@desc"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@techNotes"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@isDefault"/></td>
    <td><xsl:value-of select="@isUndefined"/></td>
    <td colspan="2"><xsl:value-of select="@canClash"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@disabledAccess"/></td>
    <td><xsl:value-of select="@hasWifi"/></td>
    <td colspan="2"><xsl:value-of select="@inRadioRange"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@needsSound"/></td>
    <td><xsl:value-of select="@naturalLight"/></td>
    <td><xsl:value-of select="@securable"/></td>
    <td><xsl:value-of select="@hasCableRuns"/></td>
  </tr>
  <tr>
    <td><xsl:value-of select="@controlLightsInRoom"/></td>
    <td><xsl:value-of select="@controlAirConInRoom"/></td>
    <td><xsl:value-of select="@openableWindows"/></td>
    <td><xsl:value-of select="@closableCurtains"/></td>
  </tr>
  <tr>
    <td>
      <xsl:apply-templates select="capacities"/>
    </td>
  </tr>
</xsl:template>

<xsl:template match="capacities">
  <xsl:apply-templates select="room_capacity"/>
</xsl:template>

<xsl:template match="room_capacity">
  <xsl:value-of select="@name"/>
  <xsl:value-of select="@capacity"/>
  <br/>
</xsl:template>

<xsl:template match="people">
  <a name="people"><h2>People</h2></a>
  <table border="1">
  <tr>
     <td colspan="2">Name</td>
     <td>Badge</td>
     <td>Mem Num</td>
  </tr>
  <tr>
     <td>First</td>
     <td>Middle</td>
     <td colspan="2">Last</td>
  </tr>
  <tr>
     <td>Gender</td>
     <td>Complete?</td>
     <td>Dist email?</td>
     <td>Rec Okay?</td>
  </tr>
  <tr>
     <td colspan="4">Email</td>
  </tr>
  <tr>
     <td colspan="4">Contact</td>
  </tr>
  <tr>
     <td colspan="4">Notes</td>
  </tr>
  <tr>
     <td colspan="4">Private Notes</td>
  </tr>
  <tr>
     <td colspan="4">Tags</td>
  </tr>
    <xsl:apply-templates select="person"/>
</table>
</xsl:template>

<xsl:template match="person">
<tr>
  <th><xsl:value-of select="@name"/></th>
  <th><xsl:value-of select="@badge"/></th>
  <th><xsl:value-of select="@memnum"/></th>
</tr>
<tr>
  <td><xsl:value-of select="@firstName"/></td>
  <td><xsl:value-of select="@middleName"/></td>
  <td><xsl:value-of select="@lastName"/></td>
</tr>
<tr>
</tr>
<tr>
  <td><xsl:value-of select="@gender"/></td>
  <td><xsl:value-of select="@complete"/></td>
  <td><xsl:value-of select="@distEmail"/></td>
  <td><xsl:value-of select="@recordingOkay"/></td>
</tr>
<tr>
  <td><xsl:value-of select="@email"/></td>
</tr>
<tr>
  <td><xsl:value-of select="@contact"/></td>
</tr>
<tr>
  <td><xsl:value-of select="@notes"/></td>
</tr>
<tr>
  <td><xsl:value-of select="@privNotes"/></td>
</tr>
<tr>
  <xsl:apply-templates select="tag_uses"/>
</tr>
</xsl:template>

<xsl:template match="tag_uses">
    <td><xsl:apply-templates select="tag_use"/></td>
</xsl:template>

<xsl:template match="tag_use">
  <xsl:value-of select="@name"/><br />
</xsl:template>

<xsl:template match="items">
  <a name="items"><h2>Programme items</h2></a>
  <p>
  <table border="1">
    <xsl:apply-templates select="item"/>
  </table>
  </p>
</xsl:template>

<xsl:template match="item">
  <tr>
  <th><xsl:value-of select="@start"/></th>
  <th><xsl:value-of select="@title"/></th>
  <th><xsl:value-of select="@length"/></th>
  </tr>
  <tr>
    <xsl:apply-templates select="itemroom"/>
  <td><xsl:value-of select="@kind"/></td>
  <td><xsl:value-of select="@seating"/></td>
  <td>Visible: <xsl:value-of select="@visible"/></td>
  </tr>
  <tr>
  <td>Gophers: <xsl:value-of select="@gophers"/></td>
  <td>Stewards: <xsl:value-of select="@stewards"/></td>
  <td>Expected Audience: <xsl:value-of select="@exp"/></td>
  <td>Complete: <xsl:value-of select="@complete"/></td>
  </tr>
  <tr>
  <td colspan="3">Notes: <xsl:value-of select="@notes"/></td>
  </tr>
  <tr>
  <td colspan="3">Blurb: <xsl:value-of select="@blurb"/></td>
  </tr>
  <tr>
  <td colspan="3">Bring: <xsl:value-of select="@bring"/></td>
  </tr>
  <tr>
  <td colspan="3">Private Notes: <xsl:value-of select="@privNotes"/></td>
  </tr>
  <tr>
  <td colspan="3">Tech Notes: <xsl:value-of select="@tech_notes"/></td>
  </tr>
  <tr>
  <td>Budget: <xsl:value-of select="@budget"/></td>
  <td>Revision: <xsl:value-of select="@revision"/></td>
  <td>Follows: <xsl:value-of select="@follows"/></td>
  </tr>
  <tr>
  <td>Proj Needed: <xsl:value-of select="@projector"/></td>
  <td>Tech Needed: <xsl:value-of select="@tech_needed"/></td>
  <td>Front Layout: <xsl:value-of select="@frontLayout"/></td>
  </tr>
  <tr>
  <td>Aud. mics: <xsl:value-of select="@audienceMics"/></td>
  <td>Needs Reset: <xsl:value-of select="@needsReset"/></td>
  <td>Needs Cleanup: <xsl:value-of select="@needsCleanup"/></td>
  </tr>
  <tr>
  <td>Media Status: <xsl:value-of select="@mediaStatus"/></td>
  <td></td>
  <td></td>
  </tr>
  <tr>
    <xsl:apply-templates select="tag_uses"/>
  </tr>
    <xsl:apply-templates select="itempeople"/>
</xsl:template>

<xsl:template match="itemroom">
  <tr><td>Room: <xsl:value-of select="@name"/></td></tr>
</xsl:template>

<xsl:template match="availability">
  <table border="1">
    <tr>
      <th>Label</th>
      <th>From</th>
      <th>To</th>
    </tr>
  <xsl:apply-templates select="avail"/>
  </table>
</xsl:template>

<xsl:template match="avail">
  <tr>
    <td><xsl:value-of select="@label"/></td>
    <td><xsl:value-of select="@from"/></td>
    <td><xsl:value-of select="@to"/></td>
  </tr>
</xsl:template>

<xsl:template match="itempeople">
  <table border="1">
    <tr>
      <th>Name</th>
      <th>Visible</th>
      <th>Role</th>
      <th>Status</th>
    </tr>
  <xsl:apply-templates select="itemperson"/>
  </table>
</xsl:template>

<xsl:template match="itemperson">
  <tr>
    <td><xsl:value-of select="@name"/></td>
    <td><xsl:value-of select="@vis"/></td>
    <td><xsl:value-of select="@role"/></td>
    <td><xsl:value-of select="@status"/></td>
  </tr>
</xsl:template>

<xsl:template match="kitrequests">
  <table border="1">
    <tr>
      <th>Kind</th>
      <th>Count</th>
      <th>Setup</th>
      <th>Status</th>
    </tr>
    <tr>
      <th colspan="4">Notes</th>
    </tr>
  <xsl:apply-templates select="kitrequest"/>
  </table>
</xsl:template>

<xsl:template match="kitrequest">
  <tr>
    <td><xsl:value-of select="@kind"/></td>
    <td><xsl:value-of select="@count"/></td>
    <td><xsl:value-of select="@setup"/></td>
    <td><xsl:value-of select="@status"/></td>
  </tr>
  <tr>
    <td colspan="4"><xsl:value-of select="@notes"/></td>
  </tr>
</xsl:template>

<xsl:template match="kitthings">
  <p>Kit Things:<br/>
  <table border="1">
  <tr>
    <th>Name</th>
    <th>Kind</th>
    <th>Count</th>
    <th>Role</th>
  </tr>
  <tr>
    <th>Source</th>
    <th>Department</th>
    <th>Basis</th>
    <th>Status</th>
  </tr>
  <tr>
    <th>Cost</th>
    <th>Insurance</th>
    <th>Notes</th>
    <th>Coordinator</th>
  </tr>
  <tr>
    <th colspan="4">Description</th>
  </tr>
  <xsl:apply-templates select="tech_use"/>
  </table></p>
</xsl:template>

<xsl:template match="kitthing">
  <tr>
  <td><xsl:value-of select="@name"/></td>
  <td><xsl:value-of select="@kind"/></td>
  <td><xsl:value-of select="@role"/></td>
  <td><xsl:value-of select="@count"/></td>
  </tr>
  <tr>
  <td><xsl:value-of select="@source"/></td>
  <td><xsl:value-of select="@department"/></td>
  <td><xsl:value-of select="@basis"/></td>
  <td><xsl:value-of select="@status"/></td>
  </tr>
  <tr>
  <td><xsl:value-of select="@cost"/></td>
  <td><xsl:value-of select="@insurance"/></td>
  <td><xsl:value-of select="@notes"/></td>
  <td><xsl:value-of select="@coordinator"/></td>
  </tr>
  <tr>
  <td colspan="4"><xsl:value-of select="@description"/></td>
  </tr>
</xsl:template>

</xsl:stylesheet>
