<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0"
  exclude-result-prefixes="tp">

  <xsl:output method="text" indent="no" encoding="ascii"/>

  <xsl:template match="tp:flags"># <xsl:value-of select="@name"/><xsl:text>
</xsl:text><xsl:apply-templates/><xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="tp:enum"># <xsl:value-of select="@name"/><xsl:text>
</xsl:text><xsl:apply-templates/><xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="tp:flags/tp:flag"><xsl:value-of select="@name"/> = <xsl:value-of select="@value"/><xsl:text>
</xsl:text></xsl:template>

  <xsl:template match="tp:enum/tp:enumvalue"><xsl:value-of select="@name"/> = <xsl:value-of select="@value"/><xsl:text>
</xsl:text></xsl:template>

  <xsl:template match="tp:flag"># at top level
<xsl:value-of select="@name"/> = <xsl:value-of select="@value"/><xsl:text>

</xsl:text></xsl:template>

  <xsl:template match="tp:enumvalue"># at top level
<xsl:value-of select="@name"/> = <xsl:value-of select="@value"/><xsl:text>

</xsl:text></xsl:template>

  <xsl:template match="text()"/>

  <xsl:template match="tp:interface">
    <xsl:apply-templates select="document(concat(translate(string(.), '.', ''), '.xml'), .)"/>
  </xsl:template>

  <xsl:template match="/tp:spec"># Generated from the Telepathy spec
"""\<xsl:value-of select="tp:docstring"/>
"""
<xsl:apply-templates select="tp:interface"/>
</xsl:template>

</xsl:stylesheet>

<!-- vim:set sw=2 sts=2 et noai noci: -->
