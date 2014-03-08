SRC = src
RES = res
TEST = test

SHELL := /bin/bash
MAIN := $(SRC)/simulator.py

tests:
	output=`mktemp` && \
	for test in $(TEST)/*; do \
		$(MAIN) $$test/in > $$output && \
		(diff --suppress-common-lines --side-by-side \
			  --ignore-blank-lines --ignore-all-space \
			<(sort -k4 $$output) \
			<(sort -k4 $$test/out) \
		 && echo -e "\033[1;32m[OK]\033[0m $$test" \
		 || echo -e "\033[1;31m[FAIL]\033[0m $$test") \
		|| break; \
	done && \
	rm -f $$output
