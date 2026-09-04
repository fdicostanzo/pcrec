# studies/scan_edge_ladder — [OPT-EDGE]'s 1/2/3/4 ladder and its minimum-chain
# floor.  NOT built by pcrec's own make (studies/CLAUDE.md): its own Makefile,
# its own harness, nothing linked into the product.
#
#   make refs        build the two REFERENCE compilers (BEFORE and AFTER)
#   make rungs       regenerate + VERIFY the four rung artifacts
#   make floorcells  regenerate + VERIFY the floor's eight cells
#   make ladder      run the ladder      (refuses on load1 >= 0.5)
#   make floor       run the floor       (same)
#   make clean       remove out/
#
# PCREC is the compiler under test and has no default on purpose — a study
# that silently measured whatever happened to be in ../../build is how a
# number ends up attributed to the wrong commit.

PCREC   ?= ../../build/pcrec
OUT     ?= out
REPO    ?= ../..
BEFORE  ?= 9d8401a
AFTER   ?= b048fa61

.PHONY: refs rungs floorcells ladder floor clean

# The BEFORE compiler is the per-edge `if` chain on the generic path; the
# AFTER one is the shared-sentinel dispatch.  Both come from `git archive` so
# neither can pick up a working-tree edit.
refs:
	@set -e; for pair in before:$(BEFORE) after:$(AFTER); do \
	  n=$${pair%%:*}; sha=$${pair##*:}; \
	  if [ -x $(OUT)/c_$$n/build/pcrec ]; then echo "c_$$n already built"; continue; fi; \
	  rm -rf $(OUT)/c_$$n; mkdir -p $(OUT)/c_$$n; \
	  git -C $(REPO) archive $$sha | tar -x -C $(OUT)/c_$$n; \
	  $(MAKE) -C $(OUT)/c_$$n -j2 >/dev/null; \
	  echo "built c_$$n from $$sha"; \
	done

# THE RUNG ARTIFACTS, AND THE VERIFICATION IS THE POINT.  A rung is only a
# rung if its FORWARD machine really carries k edges; edge1's ladder had two
# rungs whose subject never entered the chain and one whose count was not
# what the pattern suggested.  The count is read from the artifact's own
# `[OPT-5] SCAN EDGE` markers, attributed by the state variable each block
# tests, and a mismatch is printed as a REFUSAL rather than a warning.
rungs: refs
	@mkdir -p $(OUT)/work
	@set -e; k=1; for p in '\d{2}y' '\d{2}y\d{2}' '\d{2}y\d{2}y\d{2}' '\d{2}y\d{2}y\d{2}y\d{4}'; do \
	  for arm in before after; do \
	    $(OUT)/c_$$arm/build/pcrec -p rx --features all -o $(OUT)/work/a_$${arm}_$$k.c -- "$$p" >/dev/null; \
	  done; \
	  $(PCREC) -p rx --features all -o $(OUT)/work/a_step11_$$k.c -- "$$p" >/dev/null; \
	  e=$$(awk '/\[OPT-5\] SCAN EDGE/{q=1;next} q && /if \(forward_state ==/{n++;q=0} END{print n+0}' $(OUT)/work/a_after_$$k.c); \
	  if [ "$$e" = "$$k" ]; then printf 'rung %s  %-26s forward edges = %s  OK\n' "$$k" "$$p" "$$e"; \
	  else printf 'rung %s  %-26s forward edges = %s  *** REFUSED (want %s) ***\n' "$$k" "$$p" "$$e" "$$k"; fi; \
	  k=$$((k+1)); \
	done

# The floor's cells, same discipline: a cell that takes no edge measures
# nothing and says so -- AND THIS ARM ALREADY EARNED ITS KEEP. The nullable
# family was first written `[a-z]{0,m}9` and takes NO forward edge: a literal
# on either side of the chain gives the counting states a class-dependent exit
# and breaks precondition (1)'s uniformity. Measured over eight spellings, the
# only forms that take one are the BARE nullable `[a-z]{0,m}` and the exact
# `[0-9]{m}x`. Timing the first version would have compared two identical
# machines and reported a ratio of 1.000 as a finding.
floorcells:
	@mkdir -p $(OUT)/fwork
	@set -e; for m in 2 3 4 8; do \
	  for fam in exact nullable; do \
	    case $$fam in exact) p="[0-9]{$$m}x";; nullable) p="[a-z]{0,$$m}";; esac; \
	    $(PCREC) -p rx --features all               -o $(OUT)/fwork/e_$${fam}_$$m.c -- "$$p" >/dev/null; \
	    $(PCREC) -p rx --features all -fno-scan-edge -o $(OUT)/fwork/n_$${fam}_$$m.c -- "$$p" >/dev/null; \
	    e=$$(awk '/\[OPT-5\] SCAN EDGE/{q=1;next} q && /if \(forward_state ==/{n++;q=0} END{print n+0}' $(OUT)/fwork/e_$${fam}_$$m.c); \
	    if [ "$$e" -ge 1 ]; then printf 'm=%-2s %-8s %-14s forward edges = %s  OK\n' "$$m" "$$fam" "$$p" "$$e"; \
	    else printf 'm=%-2s %-8s %-14s forward edges = 0  *** TAKES NO EDGE, cell measures nothing ***\n' "$$m" "$$fam" "$$p"; fi; \
	  done; \
	done

ladder: rungs
	OUT=$(OUT) PCREC=$(PCREC) ./run_ladder.sh

floor: floorcells
	OUT=$(OUT) PCREC=$(PCREC) ./run_floor.sh

clean:
	rm -rf $(OUT)
