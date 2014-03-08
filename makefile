SRC = src
RES = res
TEST = test

SHELL := /bin/bash
MAIN := $(SRC)/simulator.py

tests:
	for test in $(TEST)/*; do \
		diff --suppress-common-lines --side-by-side \
			<($(MAIN) $$test/in | sort -k4) \
			<(sort -k4 $$test/out) \
		&& echo -e "\033[1;32m[OK]\033[0m $$test" \
		|| echo -e "\033[1;31m[FAIL]\033[0m $$test" \
	; done
