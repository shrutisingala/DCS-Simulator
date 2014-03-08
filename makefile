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
		&& echo "$$test OK" \
		|| echo "$$test FAILED" \
	; done
