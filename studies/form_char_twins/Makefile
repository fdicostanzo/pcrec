# studies/form_char_twins/Makefile -- [FORM-CHAR] STEP 0 + [OPT-CLSPACK]
# STEP 0. Self-contained per studies/CLAUDE.md's standing rule: never built
# by pcrec's top-level `make`, never run by `make test`. Regenerates the
# hand-twins docs/dev/form_char_step0.md's tables were measured from.
#
#   make base    -- regenerate base/*.c from a real build/pcrec (gen_base.sh)
#   make twins   -- derive twins/*.c from base/*.c (the four twin_*.py transforms)
#   make check   -- compile every base+twin, run the per-family subjects,
#                   check every twin's answer against its OWN base's answer
#   make sizes   -- `size` on every compiled base+twin object
#   make asm     -- gcc -S the three-spelling/non-fold-pair evidence
#                   (asm_evidence.c) into results/three_spellings.s
#   make clean   -- remove generated base/, twins/, .bin/, .obj/ (never committed)
#
# PCREC and BENCH_CI256 (see gen_base.sh) may be overridden, e.g.
#   make base PCREC=/path/to/pcrec

PYTHON ?= python3

.PHONY: all base twins check sizes asm clean

all: check sizes asm

# The compiler-equivalence evidence behind docs/dev/form_char_step0.md's
# fold-vs-bitarray claim (family A) -- see asm_evidence.c's own header.
asm:
	$(CC) -O2 -S -fverbose-asm -o results/three_spellings.s asm_evidence.c

base:
	./gen_base.sh

twins: base
	mkdir -p twins
	$(PYTHON) twin_A.py base/A_abcdef.c rxA twins
	$(PYTHON) twin_B.py base/B_general.c rxG twins general
	$(PYTHON) twin_B.py base/B_sparse.c rxS twins sparse
	$(PYTHON) twin_C.py base/C_small.c rxSM twins small
	$(PYTHON) twin_C.py base/C_nonpair.c rxNP twins nonpair
	if [ -f base/C_ci256.c ]; then $(PYTHON) twin_C.py base/C_ci256.c rxCI twins ci256; \
	else echo "twins: base/C_ci256.c absent (pcrec-bench sibling not present) -- skipping ci256 twins"; fi
	$(PYTHON) twin_D.py base/D_n16.c rxD16 twins

check: twins
	./check_twins.sh

sizes: twins
	./sizes.sh

clean:
	rm -rf base twins .bin .obj
