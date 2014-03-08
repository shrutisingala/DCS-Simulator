SRC = src
RES = res
TEST = test

SHELL := /bin/bash
MAIN := $(SRC)/simulator.py

tests:
	for test in $(TEST)/*; do \
		diff -q \
			<($(MAIN) $$test/in | sort -k4) \
			<(sort -k4 $$test/out) >/dev/null \
		&& echo -e "\033[1;32m[OK]\033[0m $$test" \
		|| echo -e "\033[1;31m[FAIL]\033[0m $$test" \
	; done
