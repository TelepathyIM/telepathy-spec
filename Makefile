all:

GIT = git
GZIP = gzip
TAR = tar
XSLTPROC = xsltproc --xinclude --nonet
CANONXML = xmllint --nsclean --noblanks --c14n --nonet
XML_LINEBREAKS = perl -pe 's/>/>\n/g'
DROP_NAMESPACE = perl -pe '$$hash = chr(35); s{xmlns:tp="http://telepathy\.freedesktop\.org/wiki/DbusSpec$${hash}extensions-v0"}{}g'
RST2HTML = rst2html
PYTHON = python

XMLS = $(wildcard spec/*.xml)
TEMPLATES = $(wildcard doc/templates/*)
INTERFACE_XMLS = $(filter spec/[[:upper:]]%.xml,$(XMLS))
INTROSPECT = $(INTERFACE_XMLS:spec/%.xml=introspect/%.xml)
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
TEST_GENERATED_FILES = $(TEST_INTROSPECT)

RST = \
    doc/cmcaps.txt \
    doc/clientcaps.txt \
    doc/open-issues.txt \
    doc/request.txt \
    doc/dispatch.txt

$(patsubst %.txt,%.html,$(RST)): %.html: %.txt Makefile
	$(RST2HTML) < $< > $@

GENERATED_FILES = \
	$(patsubst %.txt,%.html,$(RST)) \
	doc/spec.html \
	doc/spec/index.html \
	FIXME.out \
	$(INTROSPECT) \
	$(CANONICAL_NAMES)

doc/spec.html: doc/templates/oldspec.html
	cp $< $@

doc/spec/index.html: $(XMLS) tools/doc-generator.py tools/specparser.py $(TEMPLATES)
	@install -d doc
	$(PYTHON) tools/doc-generator.py spec/all.xml doc/spec/ telepathy-spec \
		org.freedesktop.Telepathy

$(INTROSPECT): introspect/%.xml: spec/%.xml tools/spec-to-introspect.xsl
	@install -d introspect
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@
$(TEST_INTROSPECT): $(TEST_INTERFACE_XMLS) tools/spec-to-introspect.xsl
	@install -d test/output
	$(XSLTPROC) tools/spec-to-introspect.xsl $< | $(DROP_NAMESPACE) > $@

all: $(GENERATED_FILES)
	@echo "Your spec HTML starts at:"
	@echo
	@echo file://$(CURDIR)/doc/spec/index.html
	@echo

TEST_CANONICALIZED_FILES = test/output/introspect.canon

test/output/introspect.canon: test/output/_Test.introspect.xml
	$(CANONXML) $< | $(XML_LINEBREAKS) > $@

CHECK_FOR_UNRELEASED = NEWS $(filter-out spec/template.xml,$(XMLS))

check: all $(TEST_GENERATED_FILES) $(TEST_CANONICALIZED_FILES) FIXME.out
	@e=0; \
	diff -u test/expected/introspect.canon test/output/introspect.canon || e=1; \
	exit $$e
	@version="`sed -ne s'!<tp:version>\(.*\)</tp:version>!\1!p' spec/all.xml`";\
	case "$$version" in \
		*.*.*.*) ;; \
		*) \
			if grep -r UNRELEASED $(CHECK_FOR_UNRELEASED); \
			then \
				echo "^^^ This is meant to be a release, but some files say UNRELEASED" >&2; \
				exit 2; \
			fi \
			;; \
	esac

FIXME.out: $(XMLS)
	@echo '  GEN   ' $@
	@egrep -A 5 '[F]IXME|[T]ODO|[X]XX' $(XMLS) \
		> FIXME.out || true

clean:
	rm -f $(GENERATED_FILES)
	rm -fr introspect
	rm -rf test/output
	rm -rf tmp

maintainer-upload-snapshot: doc/spec/index.html
	@install -d tmp
	rsync -rvzPp --chmod=Dg+s,ug+rwX,o=rX doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot/
	@echo The snapshot lives at:
	@echo '  ' http://telepathy.freedesktop.org/spec-snapshot/

maintainer-upload-release: doc/spec/index.html check
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
	rsync -rvzPp --chmod=Dg+s,ug+rwX,o=rX doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec/ ; \
	rsync -rvzPp --chmod=Dg+s,ug+rwX,o=rX doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot/

dist: check
	@install -d tmp
	set -e ;\
	version="`sed -ne s'!<tp:version>\(.*\)</tp:version>!\1!p' spec/all.xml`";\
	distname="telepathy-spec-$$version";\
	rm -f tmp/ChangeLog "$$distname".tar "$$distname".tar.gz; \
	$(GIT) archive --format=tar --prefix="$$distname"/ "HEAD^{tree}" \
		> "$$distname".tar;\
	rm -rf tmp/"$$distname";\
	mkdir tmp/"$$distname";\
	$(GIT) log telepathy-spec-0.16.0.. > tmp/"$$distname"/ChangeLog; \
	$(TAR) -rf "$$distname".tar -C tmp --owner 0 --group 0 --mode 0664 \
		"$$distname"/ChangeLog;\
	$(GZIP) -9 "$$distname".tar;\
	$(TAR) -ztvf "$$distname".tar.gz;\
	rm -rf tmp/"$$distname"

BRANCH = $(shell sh tools/git-which-branch.sh misc | tr -d '\n' | tr -C "[:alnum:]" _)
UPLOAD_BRANCH_TO = people.freedesktop.org:public_html/telepathy-spec

# Usage: make upload-branch BRANCH=discussion
upload-branch: all
	rsync -rzvP doc/spec.html $(patsubst %.txt,%.html,$(RST)) doc/spec \
		$(UPLOAD_BRANCH_TO)-$(BRANCH)/
	@echo Your spec branch might be at:
	@echo '  ' http://people.freedesktop.org/~$$USER/telepathy-spec-$(BRANCH)/spec/
