# examples/makefile — pcrec as a Makefile BUILD STEP (the [REL-1.10]/D118
# test case): `.rxt` sources compile to a `.c`/`.h` pair per target, the
# pairs become a static library, a small consumer links against it.
#
# Works with a stranger's plain `make` from a fresh clone, PROVIDED `make`
# has already built `build/pcrec` at the repo root (`PCREC` below defaults
# to exactly that path). See README.md for the walkthrough.

PCREC ?= ../../build/pcrec
CC    ?= gcc
AR    ?= ar

# One `pcrec` call compiles every target in every source file, POOLED
# ([REL-1.10] item 1) — three targets across two files here. The prefix
# list is named rather than derived from a post-build glob, because make
# resolves a rule's prerequisites before any recipe has run and `gen/`
# does not exist on a fresh checkout.
SRCS     := src/greeting.rxt src/numbers.rxt
PREFIXES := greet digits money
OBJS     := $(PREFIXES:%=gen/%.o)

.PHONY: all clean

all: example

gen/.stamp: $(SRCS)
	@mkdir -p gen
	$(PCREC) -o gen/ $(SRCS)
	@touch $@

gen/%.o: gen/.stamp
	$(CC) -O2 -I gen -c -o $@ gen/$*.c

libmatchers.a: $(OBJS)
	$(AR) rcs $@ $(OBJS)

example: main.c libmatchers.a
	$(CC) -O2 -I gen -o $@ main.c libmatchers.a

clean:
	rm -rf gen libmatchers.a example
