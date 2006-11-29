<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0"
  exclude-result-prefixes="tp">

  <xsl:output method="text" indent="no" encoding="ascii"/>

  <xsl:param name="mixed-case-prefix" select="'Tp'"/>
  <xsl:param name="upper-case-prefix" select="'TP_'"/>

  <xsl:template match="tp:flags">
    <xsl:if test="tp:docstring">/* <xsl:value-of select="tp:docstring"/> */</xsl:if>
typedef enum {
<xsl:apply-templates/>} <xsl:value-of select="$mixed-case-prefix"/>
    <xsl:value-of select="@name"/>;

</xsl:template>

  <xsl:template match="tp:enum">
    <xsl:if test="tp:docstring">/* <xsl:value-of select="tp:docstring"/> */</xsl:if>
typedef enum {
<xsl:apply-templates/>} <xsl:value-of select="$mixed-case-prefix"/>
    <xsl:value-of select="@name"/>;

</xsl:template>

  <xsl:template match="tp:flags/tp:flag">
    <xsl:variable name="name" select="concat($upper-case-prefix, @name)"/>
    <xsl:text>    </xsl:text><xsl:value-of select="$name"/> = <xsl:value-of select="@value"/>,
#   define <xsl:value-of select="$name"/> (<xsl:value-of select="$name"/>)
</xsl:template>

  <xsl:template match="tp:enum/tp:enumvalue">
    <xsl:variable name="name" select="concat($upper-case-prefix, @name)"/>
    <xsl:text>    </xsl:text><xsl:value-of select="$name"/> = <xsl:value-of select="@value"/>,
#   define <xsl:value-of select="$name"/> (<xsl:value-of select="$name"/>)
</xsl:template>

  <xsl:template match="tp:flag">
    <xsl:message terminate="yes">tp:flag found outside tp:flags
</xsl:message>
  </xsl:template>

  <xsl:template match="tp:enumvalue">
    <xsl:message terminate="yes">tp:enumvalue found outside tp:enum
</xsl:message>
  </xsl:template>

  <xsl:template match="text()"/>

  <xsl:template match="/tp:spec">/* Generated from the Telepathy spec, version <xsl:value-of select="tp:version"/><xsl:text>

</xsl:text><xsl:for-each select="tp:copyright">
      <xsl:value-of select="."/><xsl:text>
</xsl:text>
</xsl:for-each>
    <xsl:value-of select="tp:license"/><xsl:text>
</xsl:text><xsl:value-of select="tp:docstring"/>
*/

#ifdef __cplusplus
extern "C" {
#endif

<xsl:apply-templates select="node"/>

#ifdef __cplusplus
}
#endif

</xsl:template>

</xsl:stylesheet>

<!-- vim:set sw=2 sts=2 et noai noci: -->
