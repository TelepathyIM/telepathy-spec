all:

XSLTPROC = xsltproc --xinclude
CANONXML = xmllint --nsclean --noblanks --c14n

XMLS = $(wildcard spec/*.xml)
INTERFACE_XMLS = $(filter-out spec/all%.xml,$(filter-out spec/errors%.xml,$(XMLS)))
INTERFACE_PY = $(INTERFACE_XMLS:spec/%.xml=telepathy/_generated/%.py)
INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/%.xml)

GENERATED_FILES = \
	doc/spec.html \
	telepathy/_generated/interfaces.py \
	telepathy/_generated/__init__.py \
	telepathy/_generated/errors.py \
	telepathy/_generated/constants.py \
	$(INTERFACE_PY) $(INTROSPECT)

doc/spec.html: $(filter-out spec/_Test.xml,$(wildcard spec/*.xml)) tools/doc-generator.xsl
	$(XSLTPROC) tools/doc-generator.xsl spec/all.xml > $@
	$(XSLTPROC) tools/doc-generator.xsl spec/all_test.xml > test/spec.html

telepathy/_generated/constants.py: $(wildcard spec/*.xml) tools/python-constants-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-constants-generator.xsl spec/all.xml > $@
#test/interfaces.py: $(wildcard spec/*.xml) tools/python-interfaces-generator.xsl
#	$(XSLTPROC) tools/python-interfaces-generator.xsl spec/all_test.xml > test/interfaces.py

telepathy/_generated/interfaces.py: $(wildcard spec/*.xml) tools/python-interfaces-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-interfaces-generator.xsl spec/all.xml > $@
test/interfaces.py: $(wildcard spec/*.xml) tools/python-interfaces-generator.xsl
	$(XSLTPROC) tools/python-interfaces-generator.xsl spec/all_test.xml > test/interfaces.py

telepathy/_generated/__init__.py:
	install -d telepathy/_generated
	touch $@

telepathy/_generated/errors.py: spec/errors.xml tools/python-errors-generator.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/python-errors-generator.xsl spec/errors.xml > $@
test/errors.py: spec/errors_test.xml tools/python-errors-generator.xsl
	$(XSLTPROC) tools/python-errors-generator.xsl spec/errors_test.xml > test/errors.py

$(INTROSPECT): introspect/%.xml: spec/%.xml tools/spec-to-introspect.xsl
	install -d introspect
	$(XSLTPROC) tools/spec-to-introspect.xsl $< > $@

$(INTERFACE_PY): telepathy/_generated/%.py: spec/%.xml tools/spec-to-python.xsl
	install -d telepathy/_generated
	$(XSLTPROC) tools/spec-to-python.xsl $< > $@

all: $(GENERATED_FILES)

check: all test/errors.py test/interfaces.py
	diff -u test/expected/errors.py test/errors.py
	diff -u test/expected/interfaces.py test/interfaces.py
	$(CANONXML) test/spec.html > test/spec.html.canon
	diff -u test/expected/spec.html.canon test/spec.html.canon
	$(CANONXML) introspect/_Test.xml > test/introspect.canon
	diff -u test/expected/introspect.canon test/introspect.canon
	diff -u test/expected/_Test.py telepathy/_generated/_Test.py

clean:
	rm -f $(GENERATED_FILES)
	rm -fr telepathy/_generated
	rm -fr introspect
	rm -f test/errors.py test/interfaces.py
	rm -f test/spec.html.canon test/spec.html
	rm -f test/introspect.canon
