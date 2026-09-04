CC ?= cc
CFLAGS ?= -O1 -g -std=gnu11 -Wall -Wextra
ROOT := ../..
LIB  := $(ROOT)/build/libpcrec.a

ifeq ($(WERROR),1)
CFLAGS += -Werror
endif

.PHONY: all census clean

all: lim2_census

# The study links the PARENT REPO's own build/libpcrec.a -- it is not built
# or run by the top-level `make`/`make test` (studies/CLAUDE.md's standing
# rule), but it is not self-contained either: `pcrec_build_dfa` and friends
# are Ctx-internal functions, so this binary needs the same library every
# ordinary `make` in the repo root already produces.
$(LIB):
	@echo "build/libpcrec.a not found -- run 'make' in the repo root first" >&2
	@exit 1

lim2_census: lim2_census.c $(LIB)
	$(CC) $(CFLAGS) -I $(ROOT)/lib -I $(ROOT)/src -o $@ lim2_census.c $(LIB)

# Re-runs the full census (corpus + pcrec-bench's altwide set, read-only,
# skipped loudly if the sibling repo is absent) and regenerates
# census_data.tsv / census_summary.txt in place. Does NOT commit them --
# re-measurement is a deliberate act (studies/CLAUDE.md: "re-measure before
# load-bearing use").
census: lim2_census
	bash run_census.sh

clean:
	rm -f lim2_census
