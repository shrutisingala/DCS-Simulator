SRC = src
RES = res

SHELL := /bin/bash
MAIN := $(SRC)/simulator.py

test-in1: $(MAIN) $(RES)/in1.txt $(RES)/out1.txt
	diff <($(MAIN) $(RES)/in1.txt) $(RES)/out1.txt

tests: test-in1
