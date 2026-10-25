# examples/subst — compiled substitution (docs/spec/subst_api.md): one
# pattern, two templates and the support unit, each a build step, and a
# program that substitutes through the spec's recipes (§6) and the setup
# wrapper (§6¶9).
#
# Works with a stranger's plain `make` from a fresh clone, PROVIDED `make`
# has already built `build/pcrec` at the repo root (`PCREC` below defaults
# to exactly that path). See README.md.

PCREC ?= ../../build/pcrec
CC    ?= gcc
CFLAGS ?= -O2 -std=gnu11 -Wall -Wextra

GEN := gen/date.c gen/iso.c gen/num.c

.PHONY: all clean

all: example

# The pattern: a day/month/year date with named groups.
gen/date.c: Makefile
	@mkdir -p gen
	$(PCREC) --features named-groups,classes -p date -o $@ --pattern '(?<d>\d\d)/(?<m>\d\d)/(?<y>\d{4})'

# Two templates: one by name (it needs a map, §3¶13), one by number.
gen/iso.c: Makefile
	@mkdir -p gen
	$(PCREC) -p iso -o $@ --subst '$${y}-$${m}-$${d}'

gen/num.c: Makefile
	@mkdir -p gen
	$(PCREC) -p num -o $@ --subst '$$3.$$2.$$1'

# The support unit: flatten, the by-name helper and replace-all (§10).
gen/support.h: Makefile
	@mkdir -p gen
	$(PCREC) --emit-support -o $@

example: main.c $(GEN) gen/support.h
	$(CC) $(CFLAGS) -I gen -o $@ main.c $(GEN)

clean:
	rm -rf gen example
