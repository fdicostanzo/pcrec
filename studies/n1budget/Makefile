CC ?= cc
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
