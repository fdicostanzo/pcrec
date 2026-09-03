# studies/alt_dispatch/Makefile -- [ENG-ISL.S0]. Self-contained: gcc -O2,
# no dependency on pcrec's own build (studies/CLAUDE.md's standing rule --
# never built by the top-level `make`, never run by `make test`).

CC      ?= gcc
CFLAGS  ?= -O2 -std=c11 -D_POSIX_C_SOURCE=199309L -Wall -Wextra -g
LDFLAGS ?= -lm

SRC := src/common.c src/algo_serial.c src/algo_firstbyte.c src/algo_trie.c src/algo_hash.c src/harness.c
OBJ := $(SRC:.c=.o)
BIN := altdispatch

UT_SRC := src/common.c src/algo_serial.c src/algo_trie.c tests/unit_trie.c
UT_BIN := tests/unit_trie

.PHONY: all run check clean unit

all: $(BIN)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Regenerate patterns/ and subjects/ from pcrec-bench's read-only altwide set.
inputs:
	python3 gen_inputs.py

# `make check` re-derives patterns/subjects and diffs against the committed
# copies -- the studies/ convention (studies/CLAUDE.md; mirrors the bench's
# own gen_*.py --check scripts this study reads).
check:
	python3 gen_inputs.py --check

unit: $(UT_BIN)
	./$(UT_BIN)

$(UT_BIN): $(UT_SRC)
	$(CC) $(CFLAGS) -o $@ $(UT_SRC) $(LDFLAGS)

# Full measurement run: every patterns/*.branches x every subjects/*.bin.
# TIMING is meaningful only under a stated, low load -- see README.md and
# the box rule in this lane's brief. `run` always does the (load-
# independent) answer-identity and tries-per-byte work; timing numbers ride
# along and must be read beside the load1 column results/timing.tsv prints.
run: $(BIN)
	mkdir -p results
	./$(BIN) --patterns patterns --subjects subjects --out results --rounds 11

clean:
	rm -f $(OBJ) $(BIN) $(UT_BIN) tests/*.o
