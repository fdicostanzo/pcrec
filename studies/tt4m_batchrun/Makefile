# studies/tt4m_batchrun/Makefile — [TT-4M] own build, never invoked by the
# top-level pcrec Makefile (studies/CLAUDE.md's standing rule).
#
# `make check` is a SMOKE TEST (8 patterns, seconds) that the tooling
# itself is correct — NOT the load-bearing measurement. The real sweep is
# run by hand per this directory's CLAUDE.md "Reproduce" section, because
# batch sizes / pool sizes / box-coordination timing are a judgement call
# each run, not a fixed target.

PCREC   ?= ../../build/pcrec
# CC is one of make's built-in variables (implicitly already defined as
# "cc" before this file is even read), so a plain `CC ?= gcc-16` is a
# SILENT NO-OP -- `?=` only assigns when the variable is UNSET, and CC
# never is. Found live (2026-09-08, lane tt4m2): `make check` was
# compiling the smoke pool with Apple clang (`/usr/bin/cc`) instead of
# gcc-16 the whole time, and happened to pass anyway since the 8-pattern
# smoke pool contains no shape clang rejects. `origin` distinguishes
# make's own built-in default from a caller's explicit `make CC=...`, so
# only the former is overridden here.
ifeq ($(origin CC),default)
CC := gcc-16
endif
POOL    ?= /tmp/tt4m_smoke_pool
DRIVER  ?= ../../tests/harness/driver.c

.PHONY: check clean

check:
	rm -rf $(POOL)
	mkdir -p $(POOL)
	python3 collect_patterns.py --pcrec $(PCREC) --outdir $(POOL) \
	    --count 8 --require-features "" ../../tests/base
	python3 extract_cases.py $(POOL)/manifest.tsv > $(POOL)/cases.tsv
	python3 batchrun.py baseline --pool $(POOL) --pcrec $(PCREC) --cc $(CC) \
	    --driver $(DRIVER) --out $(POOL)/baseline.json --workdir $(POOL)/base_wd
	python3 batchrun.py batched --pool $(POOL) --pcrec $(PCREC) --cc $(CC) \
	    --batch-size 4 --out $(POOL)/batched.json --workdir $(POOL)/batch_wd
	python3 -c "import json,sys; \
	    b=json.load(open('$(POOL)/baseline.json'))['cases']; \
	    t=json.load(open('$(POOL)/batched.json'))['cases']; \
	    mism=[k for k in b if b.get(k)!=t.get(k)]; \
	    print('cases:', len(b), 'mismatches:', len(mism)); \
	    sys.exit(1 if mism or not b else 0)"
	@echo "check: OK (tooling smoke test passed, answer identity confirmed)"

clean:
	rm -rf $(POOL)
