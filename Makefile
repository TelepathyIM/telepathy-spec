all:

GIT = git
GZIP = gzip
TAR = tar
PYTHON = python

DOC_RSYNC_FLAGS=-rvzPp --chmod=Dg+s,ug+rwX,o=rX --delete

XMLS = $(wildcard spec/*.xml)
TEMPLATES = $(wildcard doc/templates/*)

GENERATED_FILES = \
	doc/spec/index.html \
	FIXME.out \
	$(NULL)

doc/spec/index.html: $(XMLS) tools/doc-generator.py tools/specparser.py $(TEMPLATES)
	@install -d doc
	$(PYTHON) tools/doc-generator.py spec/all.xml doc/spec/ telepathy-spec \
		org.freedesktop.Telepathy

all: $(GENERATED_FILES)
	@echo "Your spec HTML starts at:"
	@echo
	@echo file://$(CURDIR)/doc/spec/index.html
	@echo

CHECK_FOR_UNRELEASED = NEWS $(filter-out spec/template.xml,$(XMLS))

check: all FIXME.out
	$(PYTHON) test/test-specparser.py
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
	rm -rf test/output
	rm -rf tmp

maintainer-upload-snapshot: doc/spec/index.html
	@install -d tmp
	rsync $(DOC_RSYNC_FLAGS) doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot/
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
	rsync $(DOC_RSYNC_FLAGS) doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec/ ; \
	rsync $(DOC_RSYNC_FLAGS) doc/spec/ telepathy.freedesktop.org:/srv/telepathy.freedesktop.org/www/spec-snapshot/

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
	rsync -rzvP --delete doc/spec \
		$(UPLOAD_BRANCH_TO)-$(BRANCH)/
	@echo Your spec branch might be at:
	@echo '  ' http://people.freedesktop.org/~$$USER/telepathy-spec-$(BRANCH)/spec/

# automake requires these rules for anything that's in DIST_SUBDIRS
distclean: clean
maintainer-clean: clean
distdir:
	@echo distdir not implemented yet; exit 1

.PHONY: \
    all \
    check \
    clean \
    dist \
    distclean \
    distdir \
    maintainer-clean \
    maintainer-upload-release \
    maintainer-upload-snapshot \
    upload-branch \
    $(NULL)
