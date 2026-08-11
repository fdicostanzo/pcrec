# pcrec — GNU make build (see docs/decisions.md D2).
# Targets: all (default), test, clean.

CC      ?= gcc
CFLAGS  ?= -O2 -g
WARN     = -Wall -Wextra
ALLFLAGS = $(CFLAGS) $(WARN) -std=gnu11 -Ilib -Isrc

LIBSRCS := $(wildcard src/core/*.c) $(wildcard src/parse/*.c) \
           $(wildcard src/ir/*.c) $(wildcard src/opt/*.c) \
           $(wildcard src/gen/*.c)
LIBOBJS := $(patsubst src/%.c,build/obj/%.o,$(LIBSRCS))

all: build/pcrec build/libpcrec.a

build/obj/%.o: src/%.c src/core/internal.h src/core/limits.h lib/pcrec.h
	@mkdir -p $(dir $@)
	$(CC) $(ALLFLAGS) -c -o $@ $<

build/libpcrec.a: $(LIBOBJS)
	ar rcs $@ $^

build/pcrec: cli/main.c build/libpcrec.a lib/pcrec.h
	@mkdir -p build
	$(CC) $(ALLFLAGS) -o $@ cli/main.c build/libpcrec.a

test: all
	bash tests/harness/run.sh
	bash tests/cli/run_cli_tests.sh
	bash tests/reject/run_reject_tests.sh
	bash tests/registry/run_registry_tests.sh
	bash tests/parse/run_parse_tests.sh
	bash tests/codegen/run_codegen_tests.sh
	bash tests/codegen/run_trie_identity.sh
	bash tests/known_fail/run_known_fail.sh
	bash tests/thread/run_thread_tests.sh

# `make strict` — R5-Q1, answered 2026-08-10: OPT-IN, never the default.
#
# The question was whether to adopt -Werror. The reason it matters is that the
# project already HAS a warnings-as-errors gate and acquired it by ACCIDENT:
# tests/codegen/run_trie_identity.sh compiles the whole tree and fails on any
# warning, and R7 measured that this accident was, for a while, the only thing
# catching one class of offset bug. A guard nobody chose is a guard nobody
# maintains.
#
# Not the default, because gcc's warning set moves between releases and a
# stranger's `make` must not fail on their newer compiler's new opinion — the
# same moving-target argument D26 makes about PCRE2. So: a target you ask for.
#
# It also promotes the ONE warning ext.c's header cares about. Every doorway
# function is `noreturn` today and that is TRUE today; when SR-6 lands the first
# module handler one of them starts returning and gcc warns. Under `make strict`
# that becomes an error at the exact moment the claim stops being true, which is
# what that comment has wanted since R5 disproved its "this fails the build".
# It writes NOTHING and touches build/ not at all — objects go to /dev/null. The
# first version ran `make clean` first, which deleted build/pcrec out from under
# a `make test` running in another shell and turned that suite into a screenful
# of exit-126 "HARNESS FAILURE" lines. A diagnostic target that can break a
# concurrent run is a trap; this one is safe to invoke at any time.
strict:
	@set -e; for f in $(LIBSRCS) cli/main.c; do \
	    $(CC) $(ALLFLAGS) -Werror -c -o /dev/null $$f; \
	done
	@echo "strict: whole tree compiles clean with -Werror"

# The sabotage detection matrix (MECH-1): applies every encoded sabotage to a
# pristine `git archive HEAD` copy, builds it there, runs the relevant suites
# and prints which checks caught it. NOT part of `make test` — it builds the
# tree ~20 times (about 6 minutes); run it when a sabotage table's figures are
# in doubt and after changing any file a sabotage targets.
mech:
	bash tests/mech/run_sabotage_matrix.sh

bench: all
	bash tests/bench/run_bench.sh

fuzz: all
	python3 tests/fuzz/fuzz.py

clean:
	rm -rf build

.PHONY: all test strict bench fuzz clean
