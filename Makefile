#!/usr/bin/make
# WARN: gmake syntax
########################################################
#
# useful targets:
#   make tests ---------------- run the test
#   make pyflakes, make pep8 -- source code checks

########################################################
# variable section

NAME = "simulux"
OS = $(shell uname -s)

NOSETESTS := nosetests

.PHONY: test

test:
	PYTHONPATH=./lib $(NOSETESTS) -d -v -w test

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 lib/ bin/
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 --filename "*"

pyflakes:
	pyflakes test/*.py test/*/*.py * lib/*py lib/*/*py bin/*