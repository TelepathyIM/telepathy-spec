all:

XSLTPROC = xsltproc --xinclude --nonet
CANONXML = xmllint --nsclean --noblanks --c14n --nonet
XML_LINEBREAKS = perl -pe 's/>/>\n/g'
DROP_NAMESPACE = perl -pe '$$hash = chr(35); s{xmlns:tp="http://telepathy\.freedesktop\.org/wiki/DbusSpec$${hash}extensions-v0"}{}g'

XMLS = $(wildcard spec/*.xml)
INTERFACE_XMLS = $(filter-out spec/all%.xml,$(filter-out spec/errors%.xml,$(XMLS)))
INTERFACE_PY = $(INTERFACE_XMLS:spec/%.xml=telepathy/_generated/%.py)
INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/%.xml)
ASYNC_INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/async/%.xml)
CANONICAL_NAMES = $(INTERFACE_XMLS:spec/%.xml=tmp/%.name)

GLIB_GLUE_STAMPS = $(INTERFACE_XMLS:spec/%.xml=tmp/stamp-%-glue)
GOBJECT_STAMPS = $(INTERFACE_XMLS:spec/%.xml=tmp/stamp-%-gobject)
GINTERFACE_STAMPS = $(INTERFACE_XMLS:spec/%.xml=tmp/stamp-%-ginterface)

$(CANONICAL_NAMES): tmp/%.name: spec/%.xml tools/extract-nodename.py
	@install -d tmp
	python tools/extract-nodename.py $< > $@
	tr a-z A-Z < $@ > $@.upper
	tr A-Z a-z < $@ > $@.lower
	tr -d _ < $@ > $@.camel

TEST_XMLS = $(wildcard test/input/*.xml)
TEST_INTERFACE_XMLS = test/input/_Test.xml
TEST_INTERFACE_PY = test/output/_Test.py
TEST_INTROSPECT = test/output/_Test.introspect.xml
TEST_ASYNC_INTROSPECT = test/output/_Test.async-introspect.xml
TEST_GENERATED_FILES = \
	test/output/spec.html \
	test/output/errors.h test/output/errors.py \
	test/output/interfaces.h test/output/interfaces.py \
	test/output/constants.py test/output/enums.h \
	$(TEST_INTROSPECT) $(TEST_ASYNC_INTROSPECT) $(TEST_INTERFACE_PY)

GENERATED_FILES = \
	doc/spec.html \
	telepathy/_generated/interfaces.py \
	telepathy/_generated/__init__.py \
	telepathy/_generated/errors.py \
	telepathy/_generated/constants.py \
	c/telepathy-enums.h \
	c/telepathy-errors.h \
	c/telepathy-interfaces.h \
	$(INTERFACE_PY) $(INTROSPECT) $(ASYNC_INTROSPECT) \
	$(CANONICAL_NAMES) \
	$(GLIB_GLUE_STAMPS) $(GOBJECT_STAMPS) $(GINTERFACE_STAMPS)

doc/spec.html: $(XMLS) tools/doc-generator.xsl
	$(XSLTPROC) tools/doc-generator.xsl spec/all.xml > $@
test/output/spec.html: $(TEST_XMLS) tools/doc-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/doc-generator.xsl test/input/all.xml > $@

telepathy/_generated/constants.py: $(XMLS) tools/python-constants-generator.xsl
	@install -d telepathy/_generated
	$(XSLTPROC) tools/python-constants-generator.xsl spec/all.xml > $@
test/output/constants.py: $(XMLS) tools/python-constants-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/python-constants-generator.xsl test/input/all.xml > $@

c/telepathy-enums.h: $(XMLS) tools/c-constants-generator.xsl
	@install -d c
	$(XSLTPROC) tools/c-constants-generator.xsl spec/all.xml > $@
test/output/enums.h: $(TEST_XMLS) tools/c-constants-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/c-constants-generator.xsl test/input/all.xml > $@

telepathy/_generated/interfaces.py: $(XMLS) tools/python-interfaces-generator.xsl
	@install -d telepathy/_generated
	$(XSLTPROC) tools/python-interfaces-generator.xsl spec/all.xml > $@
test/output/interfaces.py: $(TEST_XMLS) tools/python-interfaces-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/python-interfaces-generator.xsl test/input/all.xml > $@

c/telepathy-interfaces.h: $(XMLS) tools/c-interfaces-generator.xsl
	@install -d c
	$(XSLTPROC) tools/c-interfaces-generator.xsl spec/all.xml > $@
test/output/interfaces.h: $(TEST_XMLS) tools/c-interfaces-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/c-interfaces-generator.xsl test/input/all.xml > $@

telepathy/_generated/__init__.py:
	@install -d telepathy/_generated
	touch $@

telepathy/_generated/errors.py: spec/errors.xml tools/python-errors-generator.xsl
	@install -d telepathy/_generated
	$(XSLTPROC) tools/python-errors-generator.xsl spec/errors.xml > $@
test/output/errors.py: test/input/errors.xml tools/python-errors-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/python-errors-generator.xsl test/input/errors.xml > $@

c/telepathy-errors.h: spec/errors.xml tools/c-errors-enum-generator.xsl
	@install -d telepathy/_generated
	$(XSLTPROC) tools/c-errors-enum-generator.xsl spec/errors.xml > $@
test/output/errors.h: test/input/errors.xml tools/c-errors-enum-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/c-errors-enum-generator.xsl test/input/errors.xml > $@

$(INTROSPECT): introspect/%.xml: spec/%.xml tools/spec-to-introspect.xsl
	@install -d introspect
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@
$(TEST_INTROSPECT): $(TEST_INTERFACE_XMLS) tools/spec-to-introspect.xsl
	@install -d test/output
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@

$(ASYNC_INTROSPECT): introspect/async/%.xml: introspect/%.xml tools/make_all_async.py
	@install -d introspect/async
	python tools/make_all_async.py $< $@
$(TEST_ASYNC_INTROSPECT): $(TEST_INTROSPECT) tools/make_all_async.py
	@install -d test/output
	python tools/make_all_async.py $< $@

$(GLIB_GLUE_STAMPS): tmp/stamp-%-glue: introspect/async/%.xml Makefile tmp/%.name
	@install -d c/ginterfaces tmp
	dbus-binding-tool --mode=glib-server --output=c/ginterfaces/svc-$(shell tr _ - < tmp/$*.name.lower)-glue.h --prefix=tp_svc_$(shell cat tmp/$*.name.lower) $<
	touch $@

$(GOBJECT_STAMPS): tmp/stamp-%-gobject: introspect/async/%.xml tools/gengobject.py tmp/%.name
	@install -d c/gobjects tmp
	cd c/gobjects && \
	python ../../tools/gengobject.py ../../$< Tp$(shell cat tmp/$*.name.camel)Impl tp-$(shell tr _ - < tmp/$*.name.lower)-impl
	touch $@

$(GINTERFACE_STAMPS): tmp/stamp-%-ginterface: spec/%.xml tools/genginterface.py tmp/%.name
	@install -d c/ginterfaces tmp
	cd c/ginterfaces && \
	python ../../tools/genginterface.py ../../$< TpSvc$(shell cat tmp/$*.name.camel) svc-$(shell tr _ - < tmp/$*.name.lower) _tp
	touch $@

$(INTERFACE_PY): telepathy/_generated/%.py: spec/%.xml tools/spec-to-python.xsl
	@install -d telepathy/_generated
	$(XSLTPROC) tools/spec-to-python.xsl $< > $@
$(TEST_INTERFACE_PY): $(TEST_INTERFACE_XMLS) tools/spec-to-python.xsl
	@install -d test/output
	$(XSLTPROC) tools/spec-to-python.xsl $< > $@

all: $(GENERATED_FILES)

TEST_CANONICALIZED_FILES = test/output/spec.html.canon \
			   test/output/introspect.canon

test/output/spec.html.canon: test/output/spec.html
	$(CANONXML) $< > $@
test/output/introspect.canon: test/output/_Test.introspect.xml
	$(CANONXML) $< | $(XML_LINEBREAKS) > $@

check: all $(TEST_GENERATED_FILES) $(TEST_CANONICALIZED_FILES)
	@e=0; \
	diff -u test/expected/enums.h test/output/enums.h || e=1; \
	diff -u test/expected/constants.py test/output/constants.py || e=1; \
	diff -u test/expected/errors.h test/output/errors.h || e=1; \
	diff -u test/expected/errors.py test/output/errors.py || e=1; \
	diff -u test/expected/interfaces.h test/output/interfaces.h || e=1; \
	diff -u test/expected/interfaces.py test/output/interfaces.py || e=1; \
	diff -u test/expected/spec.html.canon test/output/spec.html.canon || e=1; \
	diff -u test/expected/introspect.canon test/output/introspect.canon || e=1; \
	diff -u test/expected/_Test.py test/output/_Test.py || e=1; \
	exit $$e

clean:
	rm -f $(GENERATED_FILES)
	rm -fr telepathy/_generated
	rm -fr introspect
	rm -rf test/output
	rm -rf c
	rm -rf tmp
