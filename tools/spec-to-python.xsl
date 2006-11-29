<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0"
  exclude-result-prefixes="tp">

  <xsl:output method="text" indent="no" encoding="ascii"/>

  <xsl:template match="interface">
class <xsl:value-of select="translate(/node/@name, '/', '')"/>(dbus.service.Interface):
    """\<xsl:value-of select="tp:docstring"/>"""
    def __init__(self):
        self._interfaces.add(<xsl:value-of select="@tp:name-const"/>)

<xsl:apply-templates select="method"/>
<xsl:apply-templates select="signal"/>
  </xsl:template>

  <xsl:template match="method">
    @dbus.service.method(<xsl:value-of select="/node/interface/@tp:name-const"/>, in_signature='<xsl:for-each select="arg[@direction='in']"><xsl:value-of select="@type"/></xsl:for-each>', out_signature='<xsl:for-each select="arg[@direction='out']"><xsl:value-of select="@type"/></xsl:for-each>')
    def <xsl:value-of select="@name"/>(self<xsl:for-each select="arg[@direction='in']">, <xsl:value-of select="@name"/></xsl:for-each>):
        """<xsl:value-of select="tp:docstring"/>
        """
        raise NotImplementedError
  </xsl:template>

  <xsl:template match="signal">
    @dbus.service.signal(<xsl:value-of select="/node/interface/@tp:name-const"/>, signature='<xsl:for-each select="arg"><xsl:value-of select="@type"/></xsl:for-each>')
    def <xsl:value-of select="@name"/>(self<xsl:for-each select="arg">, <xsl:value-of select="@name"/></xsl:for-each>):
        """<xsl:value-of select="tp:docstring"/>
        """
        pass
  </xsl:template>

  <xsl:template match="/"># Generated from the Telepathy spec
"""<xsl:for-each select="node/tp:copyright">
  <xsl:apply-templates/><xsl:text>
</xsl:text></xsl:for-each>
<xsl:apply-templates select="node/tp:license"/>
"""

import dbus.service
<xsl:for-each select="node/interface">from telepathy._generated.interfaces import <xsl:value-of select="@tp:name-const"/><xsl:text>
</xsl:text>
</xsl:for-each>

<xsl:apply-templates select="node/interface"/>

  </xsl:template>

</xsl:stylesheet>

<!-- vim:set sw=2 sts=2 et noai noci: -->
