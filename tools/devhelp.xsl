<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0">
  <xsl:template match="/">
    <book xmlns="http://www.devhelp.net/book" title="Telepathy Specification"
        name="telepathy-spec" link="spec.html">
      <xsl:text>&#x000a;</xsl:text>
      <chapters>
        <xsl:text>&#x000a;</xsl:text>
        <xsl:apply-templates select="//interface" />
      </chapters>
      <xsl:text>&#x000a;</xsl:text>
      <functions>
        <xsl:text>&#x000a;</xsl:text>
        <xsl:apply-templates select="//method" />
        <xsl:apply-templates select="//signal" />
        <xsl:apply-templates select="//tp:enum" />
      </functions>
      <xsl:text>&#x000a;</xsl:text>
    </book>
  </xsl:template>

  <xsl:template match="//interface">
    <xsl:text>  </xsl:text>
    <sub xmlns="http://www.devhelp.net/book" name="{@name}"
      link="{concat('spec.html#', @name)}" />
    <xsl:text>&#x000a;</xsl:text>
  </xsl:template>

  <xsl:template match="//method">
    <xsl:text>  </xsl:text>
    <keyword type="function" xmlns="http://www.devhelp.net/book" name="{@name}"
      link="{concat('spec.html#', concat(../@name, concat('.', @name)))}" />
    <xsl:text>&#x000a;</xsl:text>
  </xsl:template>

  <xsl:template match="//signal">
    <xsl:text>  </xsl:text>
    <keyword type="" xmlns="http://www.devhelp.net/book" name="{@name}"
      link="{concat('spec.html#', concat(../@name, concat('.', @name)))}" />
    <xsl:text>&#x000a;</xsl:text>
  </xsl:template>

  <xsl:template match="//tp:enum">
    <xsl:text>  </xsl:text>
    <keyword type="enum" xmlns="http://www.devhelp.net/book" name="{@name}"
      link="{concat('spec.html#', concat(../@name, concat('.', @name)))}" />
    <xsl:text>&#x000a;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
