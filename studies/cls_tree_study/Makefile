# studies/cls_tree_study — [CLS-TREE]'s prototype-before-commit study.
# Self-contained (studies/CLAUDE.md): pcrec's own make never enters here.

# `CC ?= gcc-16` DOES NOT WORK: make defines CC itself, so `?=` never fires
# and every target silently builds with `cc` — which on this Mac is Apple
# clang, not gcc. Caught here by `make discover` producing a clang binary
# after the measurements had all been taken with gcc-16 directly. It is the
# same defect `docs/dev/lanes/santriage_report.md` records for
# `scripts/battery.sh`'s san/lint stages, in a new place. Overriding only
# make's DEFAULT keeps `make CC=clang` and an exported CC working.
ifeq ($(origin CC),default)
CC := gcc-16
endif
CFLAGS  ?= -O2 -std=gnu11 -Wall -Wextra
PY      ?= python3

.PHONY: all discover populations k53 uprops byteclasses baseline \
        crosscheck proptest bench all-sweeps clean

all: discover

discover: discover.c
	$(CC) $(CFLAGS) discover.c -o discover -lm

populations:
	$(PY) clsets.py uprops
	$(PY) clsets.py k53

# --- sizing + EXHAUSTIVE verification arms (safe on a loaded box) ----------

k53: discover
	CC=$(CC) $(PY) sweep.py k53 --lams 0,4,16,64,256,1e9

uprops: discover
	CC=$(CC) $(PY) sweep.py uprops --lams 0,16,256

byteclasses: discover
	CC=$(CC) $(PY) extract_byteclasses.py
	CC=$(CC) $(PY) sweep.py byteclasses --lams 0,16,256

# what pcrec emits TODAY for the same sets; needs ../../build/pcrec
baseline:
	CC=$(CC) $(PY) baseline.py

crosscheck: discover
	$(PY) crosscheck.py --population k53 --lams 0,16,256 --no-tier2

proptest: discover
	CC=$(CC) $(PY) proptest.py --cases 40 --lams 0,16,256

all-sweeps: k53 baseline byteclasses uprops

# --- the stopwatch arm: REFUSES unless the box is quiet --------------------

bench: discover
	CC=$(CC) $(PY) bench.py --population k53 --lams 0,16,256 --rounds 11

clean:
	rm -rf build discover
