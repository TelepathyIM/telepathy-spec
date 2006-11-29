<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tp="http://telepathy.freedesktop.org/wiki/DbusSpec#extensions-v0"
  exclude-result-prefixes="tp">
  <!--Don't move the declaration of the HTML namespace up here - XMLNSs
  don't work ideally in the presence of two things that want to use the
  absence of a prefix, sadly. -->

  <xsl:template match="*" mode="identity">
    <xsl:copy>
      <xsl:apply-templates mode="identity"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="tp:docstring">
    <xsl:apply-templates select="node()" mode="identity"/>
  </xsl:template>

  <xsl:template match="tp:errors">
    <h1 xmlns="http://www.w3.org/1999/xhtml">Errors</h1>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="tp:error">
    <h2 xmlns="http://www.w3.org/1999/xhtml"><a name="{@name}"></a><xsl:value-of select="@name"/></h2>
    <xsl:apply-templates select="tp:docstring"/>
  </xsl:template>

  <xsl:template match="/tp:spec/tp:copyright">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  <xsl:template match="/tp:spec/tp:license">
    <div xmlns="http://www.w3.org/1999/xhtml" class="license">
      <xsl:apply-templates mode="identity"/>
    </div>
  </xsl:template>

  <xsl:template match="tp:copyright"/>
  <xsl:template match="tp:license"/>

  <xsl:template match="interface">
    <h1 xmlns="http://www.w3.org/1999/xhtml"><a name="{@name}"></a><xsl:value-of select="@name"/></h1>
    <xsl:apply-templates select="tp:docstring" />

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

    <xsl:if test="tp:enum">
      <h2 xmlns="http://www.w3.org/1999/xhtml">Enumerated types:</h2>
      <xsl:apply-templates select="tp:enum"/>
    </xsl:if>

    <xsl:if test="tp:flags">
      <h2 xmlns="http://www.w3.org/1999/xhtml">Sets of flags:</h2>
      <xsl:apply-templates select="tp:flags"/>
    </xsl:if>

  </xsl:template>

  <xsl:template match="tp:flags">
    <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/></h3>
    <xsl:apply-templates select="tp:docstring" />
    <dl>
      <xsl:for-each select="tp:flag">
        <dt xmlns="http://www.w3.org/1999/xhtml"><code><xsl:value-of select="@name"/> = <xsl:value-of select="@value"/></code></dt>
        <xsl:choose>
          <xsl:when test="tp:docstring">
            <dd xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring" /></dd>
          </xsl:when>
          <xsl:otherwise>
            (Undocumented)
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </dl>
  </xsl:template>

  <xsl:template match="tp:enum">
    <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/></h3>
    <xsl:apply-templates select="tp:docstring" />
    <dl>
      <xsl:for-each select="tp:enumvalue">
        <dt xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/> = <xsl:value-of select="@value"/></dt>
        <xsl:choose>
          <xsl:when test="tp:docstring">
            <dd xmlns="http://www.w3.org/1999/xhtml"><xsl:apply-templates select="tp:docstring" /></dd>
          </xsl:when>
          <xsl:otherwise>
            (Undocumented)
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </dl>
  </xsl:template>

  <xsl:template match="method">
    <div xmlns="http://www.w3.org/1999/xhtml" class="method">
      <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/> (
        <xsl:for-each xmlns="" select="arg[@direction='in']">
          <xsl:value-of select="@type"/>: <xsl:value-of select="@name"/>
          <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
        ) &#x2192;
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
      <div xmlns="http://www.w3.org/1999/xhtml" class="docstring">
        <xsl:apply-templates select="tp:docstring" />
      </div>

      <xsl:if test="arg[@direction='in']">
        <div xmlns="http://www.w3.org/1999/xhtml">
          <h4>Parameters</h4>
          <dl>
            <xsl:apply-templates select="arg[@direction='in']"
              mode="parameters-in-docstring"/>
          </dl>
        </div>
      </xsl:if>

      <xsl:if test="arg[@direction='out']">
        <div xmlns="http://www.w3.org/1999/xhtml">
          <h4>Returns</h4>
          <dl>
            <xsl:apply-templates select="arg[@direction='out']"
              mode="returns-in-docstring"/>
          </dl>
        </div>
      </xsl:if>

      <xsl:if test="tp:possible-errors">
        <div xmlns="http://www.w3.org/1999/xhtml">
          <h4>Possible errors</h4>
          <dl>
            <xsl:apply-templates select="tp:possible-errors/tp:error"/>
          </dl>
        </div>
      </xsl:if>

    </div>
  </xsl:template>

  <xsl:template match="arg" mode="parameters-in-docstring">
    <dt xmlns="http://www.w3.org/1999/xhtml">
      <code><xsl:value-of select="@name"/></code> -
      <code><xsl:value-of select="@type"/></code>
    </dt>
    <dd xmlns="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="tp:docstring" />
    </dd>
  </xsl:template>

  <xsl:template match="arg" mode="returns-in-docstring">
    <dt xmlns="http://www.w3.org/1999/xhtml">
      <xsl:if test="@name">
        <code><xsl:value-of select="@name"/></code> -
      </xsl:if>
      <code><xsl:value-of select="@type"/></code>
    </dt>
    <dd xmlns="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="tp:docstring"/>
    </dd>
  </xsl:template>

  <xsl:template match="tp:possible-errors/tp:error">
    <dt xmlns="http://www.w3.org/1999/xhtml">
      <code><xsl:value-of select="@name"/></code>
    </dt>
    <dd xmlns="http://www.w3.org/1999/xhtml">
        <xsl:variable name="name" select="@name"/>
        <xsl:choose>
          <xsl:when test="tp:docstring">
            <xsl:apply-templates select="tp:docstring"/>
          </xsl:when>
          <xsl:when test="//tp:errors/tp:error[@name=$name]/tp:docstring">
            <xsl:apply-templates select="//tp:errors/tp:error[@name=$name]/tp:docstring"/> <em xmlns="http://www.w3.org/1999/xhtml">(generic description)</em>
          </xsl:when>
          <xsl:otherwise>
            (Undocumented.)
          </xsl:otherwise>
        </xsl:choose>
    </dd>
  </xsl:template>

  <xsl:template match="signal">
    <div xmlns="http://www.w3.org/1999/xhtml" class="signal">
      <h3 xmlns="http://www.w3.org/1999/xhtml"><xsl:value-of select="@name"/> ( 
        <xsl:for-each xmlns="" select="arg">
          <xsl:value-of select="@type"/>: <xsl:value-of select="@name"/>
          <xsl:if test="position() != last()">, </xsl:if>
        </xsl:for-each>
        )</h3>
      <div xmlns="http://www.w3.org/1999/xhtml" class="docstring">
        <xsl:apply-templates select="tp:docstring"/>
      </div>

      <xsl:if test="arg">
        <div xmlns="http://www.w3.org/1999/xhtml">
          <h4>Parameters</h4>
          <dl>
            <xsl:apply-templates select="arg" mode="parameters-in-docstring"/>
          </dl>
        </div>
      </xsl:if>
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
        <h1 class="topbox">Telepathy D-Bus Interface Specification</h1>
        <h2>Version <xsl:apply-templates select="tp:version"/></h2>
        <xsl:apply-templates select="tp:copyright"/>
        <xsl:apply-templates select="tp:license"/>
        <xsl:apply-templates select="tp:docstring"/>
        <xsl:apply-templates select="node"/>
        <xsl:apply-templates select="tp:errors"/>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>

<!-- vim:set sw=2 sts=2 et: -->
