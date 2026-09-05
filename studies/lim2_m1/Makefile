CC ?= gcc-16
CFLAGS ?= -O1 -g -std=gnu11 -Wall -Wextra
ROOT := ../..
LIB  := $(ROOT)/build/libpcrec.a

ifeq ($(WERROR),1)
CFLAGS += -Werror
endif

.PHONY: all sweep selftest clean

all: lim2_m1

# Same shape as studies/lim2_census/Makefile: this binary links the PARENT
# REPO's own build/libpcrec.a (Ctx-internal functions, not self-contained),
# is not built or run by the top-level `make`/`make test` (studies/CLAUDE.md's
# standing rule).
$(LIB):
	@echo "build/libpcrec.a not found -- run 'make CC=gcc-16' in the repo root first" >&2
	@exit 1

lim2_m1: lim2_m1.c $(LIB)
	$(CC) $(CFLAGS) -I $(ROOT)/lib -I $(ROOT)/src -o $@ lim2_m1.c $(LIB) -lm

# The failing-direction control (README "Failing-direction control"): run
# the lim2 census's own witness through honest and two sabotaged modes, and
# expect the SAB_SKIP_ACCEPT 100%-checkpoint self-check to disagree (MEASURED
# to do so on this witness: 1006 vs the true 1010 -- see README).
selftest: lim2_m1
	./lim2_m1 --sabotage-selftest '(1{0,30}?[^]abc][^abc]){28,30}0+|a'

# Re-runs the full sweep (repo corpus, force-included tests/counterk/ and
# tests/base/k18_cost_gates.rxt, plus pcrec-bench's altwide set read-only if
# present) and regenerates m1_data.tsv in place. Does NOT commit it --
# re-measurement is a deliberate act (studies/CLAUDE.md).
sweep: lim2_m1
	bash run_m1.sh

clean:
	rm -f lim2_m1
