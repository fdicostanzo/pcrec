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
        crosscheck proptest bench bench2 bench2-bytes all-sweeps \
        whole-byteclasses asm-byteclasses clean

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

# [CLS-TREE] S0, a1's byte-tier remainder (design note §7 a1): does a
# whole-set indexed table ever beat the kit's own size-minimal answer over
# the 41 corpus byte classes?  Exhaustive verify + rodata, then the
# comparison that turns it into a verdict.  Reads the COMMITTED
# results/byteclasses.tsv/sweep_byteclasses.tsv (`make byteclasses` only if
# re-extracting from a rebuilt ../../build/pcrec is actually wanted).
whole-byteclasses:
	$(PY) verify_whole.py byteclasses > results/whole_byteclasses.tsv
	$(PY) compare_whole_kit.py

# [CLS-TREE] S0, a5: per-site instruction counts (gcc -O2 -S) for the kit's
# byte forms (ALL/RANGES/CUBES/MASK64) vs today's BITMAP, over the same 41
# classes -- the [FORM-CHAR2] (i) asm-counting method generalized off one
# hand-picked witness onto the real population.  Same committed-input rule.
asm-byteclasses:
	CC=$(CC) $(PY) asm_count.py byteclasses

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

# The [CLS-TREE] design note's owed arm (docs/design/cls_tree_design.md §7):
# the 2026-09-11 arms PLUS the whole-set indexed tables (wholeset.py) and the
# `runs` text-like regime. Same gate, same protocol; its own results file so
# the committed bench_ubuntubudu_20260911.tsv is never overwritten.
bench2: discover
	CC=$(CC) $(PY) bench.py --population k53 --lams 0,16,256 --rounds 11 \
	    --whole --regimes member,mixed,ascii,full,runs --out bench2.tsv

# [OPT-CLSPACK] timing arm (D129 item 5): N=4/16/32 live class sites in one
# loop, bitmap vs kit vs shared-atom-table, same gate/protocol as bench2.
# Separate target (not folded into bench.py's per-set driver, which times
# one class at a time) so it can ride the SAME executor invocation as bench2
# without changing that committed arm set; see docs/design/cls_tree_design.md
# §7(b)'s updated brief for the one exact-command sequence. Reads the
# COMMITTED results/byteclasses.tsv (same rule as whole-byteclasses/
# asm-byteclasses above) -- no build/pcrec needed, and it is the read-only
# study run's only input besides its own script.
bench2-bytes: discover
	CC=$(CC) $(PY) bench_bytes.py --ns 4,16,32 --lam 16 --rounds 11 \
	    --out bench2_bytes.tsv

clean:
	rm -rf build discover
