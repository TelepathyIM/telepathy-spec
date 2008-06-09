all:

XSLTPROC = xsltproc --xinclude --nonet
CANONXML = xmllint --nsclean --noblanks --c14n --nonet
XML_LINEBREAKS = perl -pe 's/>/>\n/g'
DROP_NAMESPACE = perl -pe '$$hash = chr(35); s{xmlns:tp="http://telepathy\.freedesktop\.org/wiki/DbusSpec$${hash}extensions-v0"}{}g'
RST2HTML = rst2html

XMLS = $(wildcard spec/*.xml)
INTERFACE_XMLS = $(filter spec/[[:upper:]]%.xml,$(XMLS))
INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/%.xml)
ASYNC_INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/async/%.xml)
CANONICAL_NAMES = $(INTERFACE_XMLS:spec/%.xml=tmp/%.name)

$(CANONICAL_NAMES): tmp/%.name: spec/%.xml tools/extract-nodename.py
	@install -d tmp
	python tools/extract-nodename.py $< > $@
	tr a-z A-Z < $@ > $@.upper
	tr A-Z a-z < $@ > $@.lower
	tr -d _ < $@ > $@.camel

TEST_XMLS = $(wildcard test/input/*.xml)
TEST_INTERFACE_XMLS = test/input/_Test.xml
TEST_INTROSPECT = test/output/_Test.introspect.xml
TEST_GENERATED_FILES = \
	test/output/spec.html \
	$(TEST_INTROSPECT) $(TEST_ASYNC_INTROSPECT)

RST = doc/cmcaps.txt doc/clientcaps.txt doc/request.txt doc/dispatch.txt

$(patsubst %.txt,%.html,$(RST)): %.html: %.txt Makefile
	$(RST2HTML) < $< > $@

GENERATED_FILES = \
	$(patsubst %.txt,%.html,$(RST)) \
	doc/spec.html \
	doc/telepathy-spec.devhelp2 \
	$(INTROSPECT) $(ASYNC_INTROSPECT) \
	$(CANONICAL_NAMES)

doc/spec.html: $(XMLS) tools/doc-generator.xsl
	$(XSLTPROC) tools/doc-generator.xsl spec/all.xml > $@
doc/telepathy-spec.devhelp2: $(XMLS) tools/devhelp.xsl
	$(XSLTPROC) tools/devhelp.xsl spec/all.xml > $@
test/output/spec.html: $(TEST_XMLS) tools/doc-generator.xsl
	@install -d test/output
	$(XSLTPROC) tools/doc-generator.xsl test/input/all.xml > $@

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

all: $(GENERATED_FILES)

TEST_CANONICALIZED_FILES = test/output/spec.html.canon \
			   test/output/introspect.canon

test/output/spec.html.canon: test/output/spec.html
	$(CANONXML) $< > $@
test/output/introspect.canon: test/output/_Test.introspect.xml
	$(CANONXML) $< | $(XML_LINEBREAKS) > $@

check: all $(TEST_GENERATED_FILES) $(TEST_CANONICALIZED_FILES)
	@e=0; \
	diff -u test/expected/spec.html.canon test/output/spec.html.canon || e=1; \
	diff -u test/expected/introspect.canon test/output/introspect.canon || e=1; \
	exit $$e

clean:
	rm -f $(GENERATED_FILES)
	rm -fr introspect
	rm -rf test/output
	rm -rf tmp

maintainer-upload-snapshot: doc/spec.html
	@install -d tmp
	cp doc/spec.html tmp/spec.html
	sed -i~ -e 's,\(<h2>Version [0-9][0-9.]*\)\(</h2>\),\1 (darcs snapshot '`date +%Y%m%d`')\2,' \
		tmp/spec.html
	scp tmp/spec.html \
		telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot.html

maintainer-upload-release: doc/spec.html
	@install -d tmp
	set -e ; \
	version="`sed -ne s'!<tp:version>\(.*\)</tp:version>!\1!p' spec/all.xml`";\
	if ! echo $$version | egrep '[0-9]+\.[0-9]+\.[0-9]+'; then \
		echo 'This does not look like a spec release'; \
		exit 1; \
	fi; \
	test -f telepathy-spec-$$version.tar.gz; \
	test -f telepathy-spec-$$version.tar.gz.asc; \
	gpg --verify telepathy-spec-$$version.tar.gz.asc; \
	rsync -vzP telepathy-spec-$$version.tar.gz telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/releases/telepathy-spec/ ; \
	rsync -vzP telepathy-spec-$$version.tar.gz.asc telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/releases/telepathy-spec/ ; \
	rsync -vzP doc/spec.html telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot.html ; \
	rsync -vzP doc/spec.html telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec.html

dist:
	@install -d tmp
	set -e ;\
	version="`sed -ne s'!<tp:version>\(.*\)</tp:version>!\1!p' spec/all.xml`";\
	distname="telepathy-spec-$$version";\
	darcs dist -d dist;\
	tar -zxf- -C tmp < dist.tar.gz;\
	darcs changes > tmp/dist/ChangeLog;\
	rm -rf tmp/"$$distname";\
	mv tmp/dist tmp/"$$distname";\
	tar -zcvf- -C tmp "$$distname" > tmp/"$$distname".tar.gz;\
	mv tmp/"$$distname".tar.gz .;\
	rm -rf tmp/"$$distname";\
	rm -f dist.tar.gz

BRANCH = misc
UPLOAD_BRANCH_TO = people.freedesktop.org:public_html/telepathy-spec

# Usage: make upload-branch BRANCH=discussion
upload-branch: all
	rsync -zvP doc/spec.html $(patsubst %.txt,%.html,$(RST)) \
		$(UPLOAD_BRANCH_TO)-$(BRANCH)/
