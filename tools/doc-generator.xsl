<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0"
  exclude-result-prefixes="tp">
  <!--Don't move the declaration of the HTML namespace up here - XMLNSs
  don't work ideally in the presence of two things that want to use the
  absence of a prefix, sadly. -->

  <xsl:template match="tp:errors">
    <h1 xmlns="http://www.w3.org/1999/xhtml">Errors</h1>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="tp:error">
    <h2 xmlns="http://www.w3.org/1999/xhtml"><a name="{@name}"></a><xsl:value-of select="@name"/></h2>
    <pre xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring"/></pre>
  </xsl:template>

  <xsl:template match="/tp:spec/tp:copyright">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="/tp:spec/tp:license">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="tp:copyright"/>
  <xsl:template match="tp:license"/>

  <xsl:template match="interface">
    <h1 xmlns="http://www.w3.org/1999/xhtml"><a name="{@name}"></a><xsl:value-of select="@name"/></h1>
    <pre xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring"/></pre>

    <xsl:choose>
      <xsl:when test="method">
        <h2 xmlns="http://www.w3.org/1999/xhtml">Methods:</h2>
        <xsl:apply-templates select="method"/>
      </xsl:when>
      <xsl:otherwise>
        <p xmlns="http://www.w3.org/1999/xhtml">Interface has no methods.</p>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:choose>
      <xsl:when test="signal">
        <h2 xmlns="http://www.w3.org/1999/xhtml">Signals:</h2>
        <xsl:apply-templates select="signal"/>
      </xsl:when>
      <xsl:otherwise>
        <p>Interface has no signals.</p>
      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>

  <xsl:template match="method">
    <div xmlns="http://www.w3.org/1999/xhtml" class="method">
      <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/> (
        <xsl:for-each xmlns="" select="arg[@direction='in']">
          <xsl:value-of select="@type"/>: <xsl:value-of select="@name"/>
          <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
        ) ->
        <xsl:choose>
          <xsl:when test="arg[@direction='out']">
            <xsl:for-each xmlns="" select="arg[@direction='out']">
              <xsl:value-of select="@type"/>
              <xsl:if test="position() != last()">, </xsl:if>
            </xsl:for-each>
          </xsl:when>
          <xsl:otherwise>nothing</xsl:otherwise>
        </xsl:choose>
      </h3>
      <pre xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring"/></pre>
    </div>
  </xsl:template>

  <xsl:template match="signal">
    <div xmlns="http://www.w3.org/1999/xhtml" class="signal">
      <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/> ( 
        <xsl:for-each xmlns="" select="arg">
          <xsl:value-of select="@type"/>: <xsl:value-of select="@name"/>
          <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
        )</h3>
      <pre xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring"/></pre>
    </div>
  </xsl:template>

  <xsl:output method="xml" indent="no" encoding="ascii"
    omit-xml-declaration="yes"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" />

  <xsl:template match="/tp:spec">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Telepathy D-Bus Interface Specification</title>
        <style type="text/css">
        </style>
      </head>
      <body>
        <div class="topbox">Telepathy</div>
        <h3>Version <xsl:apply-templates select="tp:version"/></h3>
        <pre><xsl:apply-templates select="tp:docstring"/></pre>
        <xsl:apply-templates select="tp:interface"/>
        <xsl:apply-templates select="tp:include-errors"/>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>

<!-- vim:set sw=2 sts=2 et: -->
