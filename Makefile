# pcrec — GNU make build (see docs/dev/decisions.md D2).
# Targets: all (default), test, strict, ubsan, asan, lint, mech, bench, fuzz, clean.

CC      ?= gcc
CFLAGS  ?= -O2 -g
WARN     = -Wall -Wextra
ALLFLAGS = $(CFLAGS) $(WARN) -std=gnu11 -Ilib -Isrc

# BUILD_DIR (SAN-1): parameterizes every build output location so the
# sanitizer targets below can build a SEPARATE tree (build-ubsan/,
# build-asan/) without ever touching build/ — a stranger's plain `make`
# after `make ubsan` must still see a correct, unpolluted build/. Defaults to
# `build`, so nothing about plain `make`/`make test` changes.
BUILD_DIR ?= build

# LINTGEN (SAN-1, Frank directive 2026-08-13): opt-in "2-fer" that rides
# `make test`'s EXISTING generated-matcher compile pass (the GENCFLAGS hook)
# with gcc -fanalyzer, instead of requiring a separate lint-only run over
# generated code. `make test LINTGEN=1` — default unset/0 leaves plain
# `make test` byte-for-byte unchanged (verified: see docs/testing.md). The
# scripts that compile generated matchers (tests/harness, tests/cli,
# tests/codegen, tests/registry/run_pc4.sh) each read $LINTGEN themselves and
# append -fanalyzer to their own GENCFLAGS default or override, the same way
# they already read $GENCFLAGS — `export` here is what makes the value
# reach those child processes from a `make test LINTGEN=1` command line.
LINTGEN ?= 0
export LINTGEN

LIBSRCS := $(wildcard src/core/*.c) $(wildcard src/parse/*.c) \
           $(wildcard src/ir/*.c) $(wildcard src/opt/*.c) \
           $(wildcard src/gen/*.c)
LIBOBJS := $(patsubst src/%.c,$(BUILD_DIR)/obj/%.o,$(LIBSRCS))

all: $(BUILD_DIR)/pcrec $(BUILD_DIR)/libpcrec.a

# src/parse/cls_bits.inc joined the prerequisites at MOD-0.3e, found the
# hard way: a PC-4 bitmap sabotage produced ZERO disagreements because the
# edited .inc never entered the binary — hand-maintained header deps must
# grow with every new include, or a regenerated table (a libpcre2 version
# bump is a re-measurement event, D26) silently ships stale.
$(BUILD_DIR)/obj/%.o: src/%.c src/core/internal.h src/core/limits.h lib/pcrec.h src/parse/cls_bits.inc
	@mkdir -p $(dir $@)
	$(CC) $(ALLFLAGS) -c -o $@ $<

$(BUILD_DIR)/libpcrec.a: $(LIBOBJS)
	ar rcs $@ $^

$(BUILD_DIR)/pcrec: cli/main.c $(BUILD_DIR)/libpcrec.a lib/pcrec.h
	@mkdir -p $(BUILD_DIR)
	$(CC) $(ALLFLAGS) -o $@ cli/main.c $(BUILD_DIR)/libpcrec.a

# [TT-2] `test:` is PREREQUISITE-based, not a 13-line recipe of its own —
# each line moved to become the section target's OWN recipe below (unchanged
# byte for byte), and `test:` simply depends on all ten in the SAME order the
# old recipe ran them in. This is what "section composition" means
# concretely: GNU make runs a target's prerequisites in listed order when
# invoked without `-j` (so plain `make test` is UNCHANGED — same suites, same
# order, same claim — full suite, still the merge/close standard), and runs
# INDEPENDENT prerequisites concurrently under `-j` (so `make -j$(nproc)
# -Otarget test` parallelizes across suites with no interleaved output —
# `-Otarget`/`--output-sync=target` buffers each target's output and prints
# it as one contiguous block when that target finishes). No suite reads or
# writes another's output; each has always used its own `mktemp -d` workdir
# and only ever READS `build/pcrec`/`build/libpcrec.a`, so running them
# concurrently is safe by the same argument PROCS=N already relies on inside
# tests/harness/run.sh and (since [TT-2]) tests/reject/run_reject_tests.sh.
# See docs/testing.md "Section composition" for the measured wall-time.
test: test-corpus test-cli test-reject test-registry test-parse \
      test-gentimeout test-codegen test-vm test-possessify test-rungselect \
      test-counterk test-mrl test-known-fail test-thread

# [TT-1] SECTION TARGETS — thin wrappers over the same scripts `test:` above
# depends on, one target per section, so a developer can spot-check just the
# section a change touches instead of paying for the whole suite. See
# docs/testing.md "Tiered testing" for the measured per-section runtimes, the
# touched-path guidance table, and why `test-spec` exists even though it is
# not (yet) one of `test:`'s ten prerequisites above.
#
# Each target rebuilds `all` first (bar test-spec, which treats build/pcrec
# as a black box the way its own runner already does) so a stale binary never
# reads as a pass.
test-corpus: all
	TMPDIR=$${TMPDIR:-/var/tmp} PROCS=$${PROCS:-$$(nproc)} bash tests/harness/run.sh

test-cli: all
	bash tests/cli/run_cli_tests.sh

# [TT-2] PROCS defaults to nproc here too, same as test-corpus above:
# run_reject_tests.sh gained the harness's own worker-reinvocation pattern
# (sharded by CALL INDEX — see its own header comment), measured 59.5s at
# PROCS=1 down to ~5.8s at PROCS=12. Output at PROCS>1 is content-identical
# (same PASS/FAIL multiset, same Summary counts) but NOT byte-identical to a
# serial run — shard output is concatenated in shard order, not call order,
# so individual PASS/FAIL lines interleave differently (docs/testing.md
# "Internal parallelism"). `PROCS=1 make test-reject` (or `make test`) still
# gets the exact serial run, line order included — nothing about that path
# changed.
test-reject: all
	PROCS=$${PROCS:-$$(nproc)} bash tests/reject/run_reject_tests.sh

test-registry: all
	bash tests/registry/run_registry_tests.sh

test-parse: all
	bash tests/parse/run_parse_tests.sh

# Both scripts here are the "codegen structural checks" docs/testing.md
# already describes as one thing; `test:` runs them as consecutive lines
# at PROCS=1 (tests/lib/run_group.sh's serial path is byte-for-byte that),
# and concurrently otherwise — independent scripts, each its own `mktemp -d`
# workdir, read-only against build/pcrec (docs/testing.md "Internal
# parallelism"). Neither script alone is worth internally sharding
# (run_codegen_tests.sh is ~1.3s; run_trie_identity.sh, the long one at
# ~10s, is a differential over a fixed small pattern list, not hundreds of
# independent checks the way reject's table is) — running the TWO scripts
# side by side is the whole win here.
test-codegen: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/codegen/run_codegen_tests.sh' \
	    'bash tests/codegen/run_trie_identity.sh'

# [M4.5b/c] the VM engine's own section: the two bounds as MECHANISM, the
# honest artifact stamps, the capture oracle + the §3.7 differential, the
# §5.4 byte-identity gate, and DD-8's program listing held to the artifact.
#
# The last two SCRIPTS live in tests/codegen/ — they are identity and
# structural differentials, kin to run_trie_identity.sh by technique — but
# they run HERE by subject matter, and for a measured reason: `make smoke`
# includes test-codegen, and MEASURED 2026-08-15 those two add 8.0s and 2.9s
# to its 0.7s + 7.4s, which would take smoke from ~33s to ~44s against a
# documented 60s target. docs/testing.md asks for exactly this re-check when
# a section grows. The touched-path table already routes src/gen changes to
# test-vm, so nothing loses its inner-loop home.
#
# `make test-vm` runs the --quick oracle sweep (the same one `test:` runs);
# `bash tests/vm/run_vm_tests.sh full` adds the fuzzer's trap-template shapes
# under every quantifier and is a checkpoint-scale run, not an inner-loop one.
# [M4.5c fix] D45's own checks: the generated-code compile budget fires, says
# so, and every compile site routes through the one helper. Cheap (~2s) and in
# `test:` proper, because a test-infrastructure property nothing else can see
# is exactly the kind that erodes silently.
test-gentimeout: all
	bash tests/lib/run_gen_timeout_tests.sh

# [TT-2] the three scripts are independent (own mktemp -d workdir each,
# read-only against build/pcrec) and this section is the true long pole
# under `make -j -Otarget test` — sequentially ~32s (10.4 + 6.2 + 15.2),
# measured 2026-08-15 — so it gets the same tests/lib/run_group.sh treatment
# test-codegen above does. PROCS=1 keeps the exact old sequential order.
test-vm: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/codegen/run_vm_identity.sh' \
	    'bash tests/codegen/run_ir_listing.sh' \
	    'bash tests/vm/run_vm_tests.sh'

# [ENG-BREP] The possessification rung's two non-.rxt suites. Its .rxt corpus
# rides test-corpus like every other module's; these two check what a .rxt file
# structurally cannot — that the two builds AGREE over a subject sweep
# (run_possdiff.sh, the row's PRIMARY validation instrument), and that the
# rewrite happened where the artifact's stamp says it did and nowhere when
# denied (run_possessify_tests.sh). Independent scripts with their own
# mktemp -d workdirs, so they take run_group.sh's treatment like test-vm.
test-possessify: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/possessify/run_possdiff.sh' \
	    'bash tests/possessify/run_possessify_tests.sh'

# [ENG-BREP] The REVERSE-DETERMINISTIC rung's two non-.rxt suites, the same
# shape as test-possessify one rung up. Its .rxt corpus rides test-corpus like
# every other module's; these two check what a .rxt file structurally cannot —
# that the rung build and the -fno-revdet (replication = ground truth) build
# AGREE over a subject sweep (run_rungdiff.sh, the row's PRIMARY validation
# instrument), and that the rung was selected where the artifact's stamp says
# and nowhere when denied (run_rungselect_tests.sh).
test-rungselect: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/rungselect/run_rungdiff.sh' \
	    'bash tests/rungselect/run_rungselect_tests.sh'

# [ENG-BREP] The COUNTER rung's differential, the third member of the deny
# family's suite set and the same shape as the two above. `-fno-counter` is the
# ground truth for the same reason `-fno-revdet` is one rung up: denying the
# rung leaves the quantifier on FRAMES, which for a bounded repeat is literal
# replication -- what ships today.
#
# It carries RESIDUE and STRIDE axes the two suites above do not, and that is
# not symmetry for its own sake: this rung's boundary arithmetic is the mod-K
# lattice, and R26 E1/E2 measured a differential blessing an unsound clamp over
# 855 cells because its corpus had neither axis. See the script's header.
test-counterk: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/counterk/run_counterkdiff.sh' \
	    'bash tests/counterk/run_counterk_tests.sh'

# [M4.6d] MINIMUM-REMAINING-LENGTH pruning's two non-.rxt suites, the same
# shape as the three deny-family suites above. Its .rxt corpus rides
# test-corpus like every other module's -- and it is the D27-BLINDED one, so
# it is the half of this directory that was written from the promise rather
# than from the code.
#
# `-fno-length-prune` is the ground truth for a REASON the three above do not
# have: MRL is not a rung, it is a bound emitted ON whichever rung a
# quantifier already took, so denying it changes no rung, no slot and no
# capacity -- an artifact built with it is byte-for-byte the one pcrec emitted
# before MRL existed, which run_mrl_tests.sh asserts over the whole corpus.
#
# The differential sweeps BOTH ENGINES, and that is this suite's own axis: the
# two get different CEILINGS (`--engine=vm` measures to the subject end, the
# default path threads the prefilter's match-end window, D51 ruling 2), and
# the window form is both the one that ships and the one whose error direction
# is unsound if it is ever stale.
test-mrl: all
	GROUP_PROCS=$${PROCS:-$$(nproc)} bash tests/lib/run_group.sh \
	    'bash tests/mrl/run_mrldiff.sh' \
	    'bash tests/mrl/run_mrl_tests.sh'

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

# [TT-1] make smoke — MEASURED <60s inner-loop subset (docs/testing.md
# "Tiered testing" has the per-section numbers this was chosen from). The
# three slow sections are deliberately OUT: test-corpus (~304s), test-reject
# (~55s, which alone would eat the whole budget) and test-spec (~27s, which
# would leave the total too close to 60s to survive ordinary run-to-run
# variance — see the docs section for the arithmetic). What's IN runs the
# real section targets, not a weakened subset of any of them.
#
# SMOKE_FLOOR is a LITERAL, kept independent of SMOKE_SECTIONS on purpose
# (project lesson, memory: pcrec-check-design-lessons — every check here
# that failed shared a source with the thing it controlled). $$ran below is
# counted by the loop actually running each entry in SMOKE_SECTIONS, so it
# tracks the list; SMOKE_FLOOR does not auto-follow it, which is what makes
# shrinking the list (accidentally or not) without updating SMOKE_FLOOR in
# the same commit a loud, failing gate instead of a silent shrink.
SMOKE_SECTIONS = test-cli test-registry test-parse test-codegen test-known-fail test-thread
SMOKE_FLOOR    := 6

smoke: all
	@ran=0; \
	for sec in $(SMOKE_SECTIONS); do \
	    $(MAKE) --no-print-directory $$sec || exit 1; \
	    ran=$$((ran+1)); \
	done; \
	if [ "$$ran" -lt $(SMOKE_FLOOR) ]; then \
	    echo "smoke: FLOOR TRIPPED — ran $$ran section(s), expected at least $(SMOKE_FLOOR)." >&2; \
	    echo "smoke:   SMOKE_SECTIONS shrank without SMOKE_FLOOR being updated to match." >&2; \
	    echo "smoke:   Restore the missing section(s); if the shrink is deliberate, update" >&2; \
	    echo "smoke:   BOTH SMOKE_FLOOR here AND docs/testing.md's smoke composition in the" >&2; \
	    echo "smoke:   same commit." >&2; \
	    exit 1; \
	fi; \
	echo "smoke: ran $$ran/$(SMOKE_FLOOR) sections ($(SMOKE_SECTIONS))."

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

# Self-tests for scripts/ (watchdog today), run ON CHANGE via make dependency
# rather than per suite run — opt-in like strict, never part of `make test`
# (Frank, 2026-08-16; decisions.md D48; the mechanism is scripts/Makefile's
# one derived pattern rule).
testscripts:
	$(MAKE) -C scripts test

# ---------------------------------------------------------------------------
# SAN-1: the sanitizer + lint battery (docs/dev/plan_completed.md [SAN-1], R7/T-3 carry).
#
# OPT-IN like `make strict` — never part of `make test`, never default, writes
# nothing to the source tree, safe to run alongside `make test` (separate
# BUILD_DIR trees, D2 plain-make holds). BOTH AXES on ubsan/asan: the COMPILER
# (this BUILD_DIR's pcrec + libpcrec.a + every test-driver .c the suite
# builds, via SANFLAGS) and the COMPILEE (every generated matcher the harness
# compiles, via GENCFLAGS — see docs/testing.md's "Sanitizer + lint battery"
# section for the compile-site audit: which suites already honored GENCFLAGS
# and which needed plumbing).
#
# TSan already lives in tests/thread (make test); it is deliberately NOT
# re-run here — combining ASan/UBSan instrumentation with an already-TSan'd
# build is not how sanitizers compose on this toolchain, and the thread
# suite's own two checks are the right home for concurrency bugs. See
# docs/testing.md for the full exclusion list and reasoning (bench, mech,
# fuzz, spec_mod0, probes).

UBSAN_DIR   := build-ubsan
UBSAN_CFLAGS := -O1 -g -fsanitize=undefined -fno-sanitize-recover=undefined
UBSAN_ENV    = PCREC=$(CURDIR)/$(UBSAN_DIR)/pcrec CC=$(CC) \
               LIBPCREC=$(CURDIR)/$(UBSAN_DIR)/libpcrec.a \
               LIBA=$(CURDIR)/$(UBSAN_DIR)/libpcrec.a \
               GENCFLAGS="-O1 -std=gnu11 -Wall -Wextra $(UBSAN_CFLAGS)" \
               SANFLAGS="$(UBSAN_CFLAGS)" \
               UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1" \
               PROCS=$${PROCS:-$$(nproc)} TMPDIR=$${TMPDIR:-/var/tmp}

ubsan:
	@echo "== ubsan: building the compiler axis at $(UBSAN_DIR)/ =="
	$(MAKE) BUILD_DIR=$(UBSAN_DIR) CFLAGS="$(UBSAN_CFLAGS)" all
	@echo "== ubsan: running the suite, both axes instrumented =="
	@set -e; \
	for s in tests/harness/run.sh tests/cli/run_cli_tests.sh \
	         tests/reject/run_reject_tests.sh \
	         tests/registry/run_registry_tests.sh \
	         tests/parse/run_parse_tests.sh \
	         tests/codegen/run_codegen_tests.sh \
	         tests/codegen/run_trie_identity.sh \
	         tests/codegen/run_vm_identity.sh \
	         tests/codegen/run_ir_listing.sh \
	         tests/vm/run_vm_tests.sh \
	         tests/possessify/run_possdiff.sh \
	         tests/possessify/run_possessify_tests.sh \
	         tests/rungselect/run_rungdiff.sh \
	         tests/rungselect/run_rungselect_tests.sh \
	         tests/lib/run_gen_timeout_tests.sh \
	         tests/known_fail/run_known_fail.sh; do \
	    echo "-- ubsan: $$s --"; \
	    env $(UBSAN_ENV) bash "$$s" || exit 1; \
	done
	@echo "ubsan: suite green under -fsanitize=undefined, both axes"

ASAN_DIR    := build-asan
ASAN_CFLAGS := -O1 -g -fsanitize=address,leak
ASAN_ENV     = PCREC=$(CURDIR)/$(ASAN_DIR)/pcrec CC=$(CC) \
               LIBPCREC=$(CURDIR)/$(ASAN_DIR)/libpcrec.a \
               LIBA=$(CURDIR)/$(ASAN_DIR)/libpcrec.a \
               GENCFLAGS="-O1 -std=gnu11 -Wall -Wextra $(ASAN_CFLAGS)" \
               SANFLAGS="$(ASAN_CFLAGS)" \
               ASAN_OPTIONS="detect_leaks=1" \
               LSAN_OPTIONS="" \
               PROCS=$${PROCS:-$$(nproc)} TMPDIR=$${TMPDIR:-/var/tmp}

# K7 (docs/dev/known_issues.md) has NO automated repro in `make test` today — it
# is reproduced only by hand (`ulimit -v ...; pcrec -p rx ... 'a{0,65535}'`)
# and by the probes/spec-writer measurements the entry cites. There is
# therefore nothing K7-shaped to exclude here; see docs/testing.md for the
# valgrind-memcheck note recorded anyway, in case a K7 repro is ever added to
# the standing suite and hits the same rlimit-vs-ASan-shadow-memory conflict.
asan:
	@echo "== asan: building the compiler axis at $(ASAN_DIR)/ =="
	$(MAKE) BUILD_DIR=$(ASAN_DIR) CFLAGS="$(ASAN_CFLAGS)" all
	@echo "== asan: running the suite, both axes instrumented =="
	@set -e; \
	for s in tests/harness/run.sh tests/cli/run_cli_tests.sh \
	         tests/reject/run_reject_tests.sh \
	         tests/registry/run_registry_tests.sh \
	         tests/parse/run_parse_tests.sh \
	         tests/codegen/run_codegen_tests.sh \
	         tests/codegen/run_trie_identity.sh \
	         tests/codegen/run_vm_identity.sh \
	         tests/codegen/run_ir_listing.sh \
	         tests/vm/run_vm_tests.sh \
	         tests/possessify/run_possdiff.sh \
	         tests/possessify/run_possessify_tests.sh \
	         tests/rungselect/run_rungdiff.sh \
	         tests/rungselect/run_rungselect_tests.sh \
	         tests/lib/run_gen_timeout_tests.sh \
	         tests/known_fail/run_known_fail.sh; do \
	    echo "-- asan: $$s --"; \
	    env $(ASAN_ENV) bash "$$s" || exit 1; \
	done
	@echo "asan: suite green under ASan+LSan, both axes"

# `make lint` — static analysis survey (SAN-1 item 3). Adopts what earns its
# place, records rejections with reasons (OPT-A's convention). Degrades
# loudly-but-gracefully per tool, the PC-3 libpcre2-absent SKIP pattern:
# a stranger's box differs and the target must stay green either way.
lint:
	@echo "== lint: gcc -fanalyzer =="
	@if $(CC) -fanalyzer -fsyntax-only -x c -std=gnu11 - < /dev/null >/dev/null 2>&1; then \
	    set -e; for f in $(LIBSRCS) cli/main.c; do \
	        $(CC) $(ALLFLAGS) -fanalyzer -c -o /dev/null $$f; \
	    done; \
	    echo "lint: gcc -fanalyzer: whole tree analyzed clean ($(words $(LIBSRCS)) + 1 files)"; \
	else \
	    echo "lint: SKIP gcc -fanalyzer: $(CC) does not support -fanalyzer on this box"; \
	fi
	@if command -v clang-tidy >/dev/null 2>&1; then \
	    echo "lint: clang-tidy found but NOT adopted here -- see docs/testing.md rejection note"; \
	else \
	    echo "lint: SKIP clang-tidy: not installed"; \
	fi
	@if command -v cppcheck >/dev/null 2>&1; then \
	    echo "lint: cppcheck found but NOT adopted here -- see docs/testing.md rejection note"; \
	else \
	    echo "lint: SKIP cppcheck: not installed"; \
	fi
	@if command -v clang >/dev/null 2>&1; then \
	    echo "lint: clang found but not used as a second compiler here -- see docs/testing.md rejection note"; \
	else \
	    echo "lint: SKIP clang: not installed"; \
	fi
	@echo "lint: done"

# The sabotage detection matrix (MECH-1): applies every encoded sabotage to a
# pristine `git archive HEAD` copy, builds it there, runs the relevant suites
# and prints which checks caught it. NOT part of `make test` — it builds the
# tree ~20 times (about 6 minutes); run it when a sabotage table's figures are
# in doubt and after changing any file a sabotage targets.
mech:
	TMPDIR=$${TMPDIR:-/var/tmp} PROCS=$${PROCS:-$$(nproc)} bash tests/mech/run_sabotage_matrix.sh

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
	rm -rf build $(UBSAN_DIR) $(ASAN_DIR)

.PHONY: all test test-corpus test-cli test-reject test-registry test-parse \
        test-gentimeout test-codegen test-vm test-possessify test-rungselect \
        test-known-fail test-thread \
        test-spec smoke hooks strict testscripts ubsan asan lint mech bench \
        fuzz clean
