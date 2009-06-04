
####################### definitions #########################

PYTHON := python
VERSION := $(shell $(PYTHON) ./get_version.py)
DISTDIR := ./pybatis-$(VERSION)
DISTTGZ := $(DISTDIR).tar.gz
FIND := find
RM := rm -rf
MKDIR := mkdir -p
M4 := m4

####################### targets #########################

.PHONY: clean
clean:
	$(RM) $(DISTDIR)
	$(FIND) . -name '*.pyc' -exec rm -f {} \;
	$(FIND) . -name '*.pyo' -exec rm -f {} \;

.PHONY: xxx
xxx:
	$(FIND) . -name '*.py' -exec grep -l XXX {} \;
	$(FIND) . -name '*.html' -exec grep -l XXX {} \;
	$(FIND) . -name '*.pgsql' -exec grep -l XXX {} \;
	$(FIND) . -name '*.css' -exec grep -l XXX {} \;


.PHONY: release
release: clean
	$(MKDIR) $(DISTDIR)
	cp ./ACKNOWLEDGEMENTS $(DISTDIR)
	cp ./COPYING $(DISTDIR)
	cp ./COPYING.LESSER $(DISTDIR)
	cp ./doc.html $(DISTDIR)
	cp ./INSTALL $(DISTDIR)
	cp -r ./pybatis $(DISTDIR)
	cp ./README $(DISTDIR)
	tar -cvzf $(DISTTGZ) $(DISTDIR)

