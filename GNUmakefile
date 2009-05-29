
####################### definitions #########################

FIND := find
RM := rm -rf
MKDIR := mkdir -p
M4 := m4

####################### targets #########################

.PHONY: clean
clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;

.PHONY: xxx
xxx:
	find . -name '*.py' -exec grep -l XXX {} \;
	find . -name '*.html' -exec grep -l XXX {} \;
	find . -name '*.pgsql' -exec grep -l XXX {} \;
	find . -name '*.css' -exec grep -l XXX {} \;

