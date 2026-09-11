# The written fallback here used to be `cc` -- a no-op guard, since `cc` is
# also make's own built-in default. Set to gcc-16 instead: this study's own
# CLAUDE.md documents "macOS arm64, gcc-16 16.2.0, measured" as what the
# committed n1_data.tsv/n1_summary.txt were actually taken with (and its
# README's reproduce recipe always passed `make CC=gcc-16` explicitly,
# never relying on this fallback) -- so a bare `make` now gets the compiler
# the numbers were measured with, not Apple clang. See [CC-ORIGIN],
# docs/dev/plan.md, and studies/cls_tree_study/Makefile's own copy of this
# comment.
ifeq ($(origin CC),default)
CC := gcc-16
endif
CFLAGS ?= -O1 -g -std=gnu11 -Wall -Wextra
ROOT := ../..
LIB  := $(ROOT)/build/libpcrec.a

ifeq ($(WERROR),1)
CFLAGS += -Werror
endif

.PHONY: all sweep clean

all: n1_measure

# Links the PARENT REPO's own build/libpcrec.a (studies/CLAUDE.md's standing
# rule: never built or run by the top-level make/make test) -- not
# self-contained, since pcrec_build_dfa and friends are Ctx-internal.
$(LIB):
	@echo "build/libpcrec.a not found -- run 'make' in the repo root first" >&2
	@exit 1

n1_measure: n1_measure.c $(LIB)
	$(CC) $(CFLAGS) -I $(ROOT)/lib -I $(ROOT)/src -o $@ n1_measure.c $(LIB)

# Re-runs the full sweep (corpus + pcrec-bench's altwide set, read-only,
# skipped loudly if the sibling repo is absent) and regenerates
# n1_data.tsv / n1_summary.txt in place.
sweep: n1_measure
	bash run_sweep.sh

clean:
	rm -f n1_measure
