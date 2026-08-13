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

# src/parse/cls_bits.inc joined the prerequisites at MOD-0.3e, found the
# hard way: a PC-4 bitmap sabotage produced ZERO disagreements because the
# edited .inc never entered the binary — hand-maintained header deps must
# grow with every new include, or a regenerated table (a libpcre2 version
# bump is a re-measurement event, D26) silently ships stale.
build/obj/%.o: src/%.c src/core/internal.h src/core/limits.h lib/pcrec.h src/parse/cls_bits.inc
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

# [TT-1] SECTION TARGETS — thin wrappers over the same scripts `test:` above
# runs, one target per section, so a developer can spot-check just the
# section a change touches instead of paying for the whole suite. `test:`
# itself is UNTOUCHED by this: it is still the full nine-script run above,
# byte for byte the same claim as before tiering existed. See docs/testing.md
# "Tiered testing" for the measured per-section runtimes, the touched-path
# guidance table, and why `test-spec` exists even though it is not (yet) one
# of the nine lines in `test:` above.
#
# Each target rebuilds `all` first (bar test-spec, which treats build/pcrec
# as a black box the way its own runner already does) so a stale binary never
# reads as a pass.
test-corpus: all
	bash tests/harness/run.sh

test-cli: all
	bash tests/cli/run_cli_tests.sh

test-reject: all
	bash tests/reject/run_reject_tests.sh

test-registry: all
	bash tests/registry/run_registry_tests.sh

test-parse: all
	bash tests/parse/run_parse_tests.sh

# Both scripts here are the "codegen structural checks" docs/testing.md
# already describes as one thing; `test:` runs them as consecutive lines,
# so this target does too.
test-codegen: all
	bash tests/codegen/run_codegen_tests.sh
	bash tests/codegen/run_trie_identity.sh

test-known-fail: all
	bash tests/known_fail/run_known_fail.sh

test-thread: all
	bash tests/thread/run_thread_tests.sh

# Not one of the nine `test:` lines — tests/spec_mod0/run_spec_mod0.sh is a
# standalone D27 suite, deliberately kept out of `make test` (its own
# CLAUDE.md: "Not part of `make test`, and it does not run `make`"). It gets
# a section target anyway because the plan row that created tiering named it
# explicitly as one of the eight tiers a developer should be able to run.
test-spec: all
	bash tests/spec_mod0/run_spec_mod0.sh

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

# [TT-1] OPT-IN local push gate. Copies scripts/hooks/pre-push into the
# resolved hooks directory — `git rev-parse --git-path hooks`, NOT a
# hardcoded .git/hooks, because in a worktree .git is a file pointing at the
# shared gitdir (see `git worktree`'s docs and docs/testing.md). Never run
# automatically by any other target and never by CI (D2, TT-1 principle 4):
# a stranger's plain `make`/`make test` must not install anything into their
# git config.
hooks:
	@hookdir="$$(git rev-parse --git-path hooks)"; \
	install -m 0755 scripts/hooks/pre-push "$$hookdir/pre-push"; \
	echo "hooks: installed scripts/hooks/pre-push -> $$hookdir/pre-push"

clean:
	rm -rf build

.PHONY: all test test-corpus test-cli test-reject test-registry test-parse \
        test-codegen test-known-fail test-thread test-spec smoke hooks \
        strict bench fuzz clean
