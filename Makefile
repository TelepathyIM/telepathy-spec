all:

XSLTPROC = xsltproc --xinclude --nonet
CANONXML = xmllint --nsclean --noblanks --c14n --nonet
XML_LINEBREAKS = perl -pe 's/>/>\n/g'
DROP_NAMESPACE = perl -pe '$$hash = chr(35); s{xmlns:tp="http://telepathy\.freedesktop\.org/wiki/DbusSpec$${hash}extensions-v0"}{}g'

XMLS = $(wildcard spec/*.xml)
INTERFACE_XMLS = $(filter-out spec/all%.xml,$(filter-out spec/errors%.xml,$(XMLS)))
INTERFACE_PY = $(INTERFACE_XMLS:spec/%.xml=telepathy/_generated/%.py)
INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/%.xml)

TEST_XMLS = $(wildcard test/input/*.xml)
TEST_INTERFACE_XMLS = test/input/_Test.xml
TEST_INTERFACE_PY = test/output/_Test.py
TEST_INTROSPECT = test/output/_Test.introspect.xml
TEST_GENERATED_FILES = \
	test/output/spec.html \
	test/output/errors.h test/output/errors.py \
	test/output/interfaces.h test/output/interfaces.py \
	test/output/constants.py test/output/enums.h \
	$(TEST_INTROSPECT) $(TEST_INTERFACE_PY)

GENERATED_FILES = \
	doc/spec.html \
	telepathy/_generated/interfaces.py \
	telepathy/_generated/__init__.py \
	telepathy/_generated/errors.py \
	telepathy/_generated/constants.py \
	c/telepathy-enums.h \
	c/telepathy-errors.h \
	c/telepathy-interfaces.h \
	$(INTERFACE_PY) $(INTROSPECT)

doc/spec.html: $(XMLS) tools/doc-generator.xsl
	$(XSLTPROC) tools/doc-generator.xsl spec/all.xml > $@
test/output/spec.html: $(TEST_XMLS) tools/doc-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/doc-generator.xsl test/input/all.xml > $@

telepathy/_generated/constants.py: $(XMLS) tools/python-constants-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-constants-generator.xsl spec/all.xml > $@
test/output/constants.py: $(XMLS) tools/python-constants-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/python-constants-generator.xsl test/input/all.xml > $@

c/telepathy-enums.h: $(XMLS) tools/c-constants-generator.xsl
	install -d c
	$(XSLTPROC) tools/c-constants-generator.xsl spec/all.xml > $@
test/output/enums.h: $(TEST_XMLS) tools/c-constants-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/c-constants-generator.xsl test/input/all.xml > $@

telepathy/_generated/interfaces.py: $(XMLS) tools/python-interfaces-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-interfaces-generator.xsl spec/all.xml > $@
test/output/interfaces.py: $(TEST_XMLS) tools/python-interfaces-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/python-interfaces-generator.xsl test/input/all.xml > $@

c/telepathy-interfaces.h: $(XMLS) tools/c-interfaces-generator.xsl
	install -d c
	$(XSLTPROC) tools/c-interfaces-generator.xsl spec/all.xml > $@
test/output/interfaces.h: $(TEST_XMLS) tools/c-interfaces-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/c-interfaces-generator.xsl test/input/all.xml > $@

telepathy/_generated/__init__.py:
	install -d telepathy/_generated
	touch $@

telepathy/_generated/errors.py: spec/errors.xml tools/python-errors-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-errors-generator.xsl spec/errors.xml > $@
test/output/errors.py: test/input/errors.xml tools/python-errors-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/python-errors-generator.xsl test/input/errors.xml > $@

c/telepathy-errors.h: spec/errors.xml tools/c-errors-enum-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/c-errors-enum-generator.xsl spec/errors.xml > $@
test/output/errors.h: test/input/errors.xml tools/c-errors-enum-generator.xsl
	install -d test/output
	$(XSLTPROC) tools/c-errors-enum-generator.xsl test/input/errors.xml > $@

$(INTROSPECT): introspect/%.xml: spec/%.xml tools/spec-to-introspect.xsl
	install -d introspect
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@
$(TEST_INTROSPECT): $(TEST_INTERFACE_XMLS) tools/spec-to-introspect.xsl
	install -d test/output
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@

$(INTERFACE_PY): telepathy/_generated/%.py: spec/%.xml tools/spec-to-python.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/spec-to-python.xsl $< > $@
$(TEST_INTERFACE_PY): $(TEST_INTERFACE_XMLS) tools/spec-to-python.xsl
	install -d test/output
	$(XSLTPROC) tools/spec-to-python.xsl $< > $@

all: $(GENERATED_FILES)

check: all $(TEST_GENERATED_FILES)
	diff -u test/expected/enums.h test/output/enums.h
	diff -u test/expected/constants.py test/output/constants.py
	diff -u test/expected/errors.h test/output/errors.h
	diff -u test/expected/errors.py test/output/errors.py
	diff -u test/expected/interfaces.h test/output/interfaces.h
	diff -u test/expected/interfaces.py test/output/interfaces.py
	$(CANONXML) test/output/spec.html > test/output/spec.html.canon
	diff -u test/expected/spec.html.canon test/output/spec.html.canon
	$(CANONXML) test/output/_Test.introspect.xml | $(XML_LINEBREAKS) > test/output/introspect.canon
	diff -u test/expected/introspect.canon test/output/introspect.canon
	diff -u test/expected/_Test.py test/output/_Test.py

clean:
	rm -f $(GENERATED_FILES)
	rm -fr telepathy/_generated
	rm -fr introspect
	rm -rf test/output
