#!/usr/bin/env bash
# tests/codegen/run_codegen_tests.sh — structural assertions on generated code.
#
# WHY THIS EXISTS (checkpoint review R2, finding R2-PR3): three M2 optimizations
# — self-loop skip states, the anchored fast path, and DFA minimization — could
# be completely disabled with ZERO signal from `make test` or `make bench`.
# They are all behavior-preserving by design, so no correctness test can catch
# their absence, and the benchmark budgets were too loose (or, for
# minimization, exercised patterns that were already minimal). These tests
# assert the OPTIMIZATION IS PRESENT in the emitted C, not that the matcher is
# correct — correctness is the .rxt corpus's job.
#
# Usage: bash tests/codegen/run_codegen_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "codegen: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- engine-scoped extraction (OS-0b) -----------------------------------
# Every symbol checked below — skip tables, transition tables, the prefilter,
# start_max, the attempt loop — is a function-local static or a statement
# INSIDE the engine function. That is exactly what lets several engines share
# one file (D18/D20), and it is also what makes a whole-file grep the wrong
# tool the moment there is more than one: `rx_fs[0-9]+\[256\]` would then be
# satisfied by ANY engine present, so a check that reads "this pattern emits a
# skip table" quietly weakens to "some engine in here does" WITHOUT failing.
#
# So the checks run against one engine's body, extracted by entry name. The
# extractor is not trusted on inspection: the multi-engine block at the end of
# this file builds a two-engine file and requires a scoped grep to find the
# skip table in the engine that has one and NOT in the engine that does not —
# which neither a whole-file extractor nor an empty one can satisfy.
body() { # body <file> <entry-name> <out-file>
    awk -v fn="$2" '
        $0 ~ "^int " fn "\\(" { inside = 1 }
        inside                { print }
        inside && /^\}/       { exit }
    ' "$1" > "$3"
    [ -s "$3" ] && tail -n 1 "$3" | grep -q '^}$'
}

gen() { # gen <name> <pattern> [extra pcrec args...] -> <name>.c plus <name>.body
    local name="$1" pat="$2"
    shift 2
    "$PCREC" -p rx "$@" -o "$WORKDIR/$name.c" -- "$pat" >/dev/null 2>&1 \
        || { bad "$name: pcrec failed to compile pattern '$pat'"; return 1; }
    body "$WORKDIR/$name.c" rx_search "$WORKDIR/$name.body" \
        || { bad "$name: could not extract the rx_search engine body from the generated C"; return 1; }
}

# ---- skip states (src/gen/emit_dfa.c pick_skip_states) -------------------
# '.*=.*' has states that self-loop on nearly every byte; the emitter must
# produce a skip table for them. Disabling pick_skip_states removes these.
if gen skip '.*=.*'; then
    if grep -qE 'rx_(fs|rs)[0-9]+\[256\]' "$WORKDIR/skip.body"; then
        ok "skip states: '.*=.*' emits a self-loop skip table"
    else
        bad "skip states: '.*=.*' emitted NO skip table (pick_skip_states disabled/broken?)"
    fi
    if grep -qE 'while \(pos < n && rx_fs[0-9]+\[s\[pos\]\]\) pos\+\+;' "$WORKDIR/skip.body"; then
        ok "skip states: forward skip loop present"
    else
        bad "skip states: forward skip loop missing"
    fi
fi

# a long-literal pattern should NOT waste tables on skip states
if gen noskip 'needleXYZW'; then
    if grep -qE 'memchr' "$WORKDIR/noskip.body"; then
        ok "prefilter: single-escape-byte pattern uses memchr"
    else
        bad "prefilter: 'needleXYZW' did not emit a memchr prefilter"
    fi
fi

# ---- anchored fast path (emit_dfa.c start_max) ---------------------------
# Fully ^-anchored patterns must not loop over start positions.
if gen anch '^abc$'; then
    if grep -q 'start_max = 0' "$WORKDIR/anch.body"; then
        ok "anchored fast path: '^abc\$' emits start_max = 0"
    else
        bad "anchored fast path: '^abc\$' still scans all start positions"
    fi
fi
# A pattern anchored on only ONE branch must NOT get the fast path.
if gen partanch '^a|b'; then
    if grep -q 'start_max = 0' "$WORKDIR/partanch.body"; then
        bad "anchored fast path: '^a|b' wrongly anchored (only one branch has ^)"
    else
        ok "anchored fast path: partially-anchored pattern correctly not anchored"
    fi
fi

# ---- DFA minimization (src/opt/minimize.c) ------------------------------
# Minimization is behavior-preserving, so only table SIZE can detect it.
# This alternation is provably non-minimal after subset construction: the
# five branches converge on equivalent tail states that must merge.
if gen minim '(get|post|put|delete|patch)'; then
    entries=$(grep -oE 'rx_ftr\[[0-9]+\]' "$WORKDIR/minim.body" | grep -oE '[0-9]+' | head -1)
    if [ -z "${entries:-}" ]; then
        bad "minimization: could not find rx_ftr[] table in generated code"
    elif [ "$entries" -le 200 ]; then
        ok "minimization: keyword alternation table is $entries entries (<= 200)"
    else
        bad "minimization: keyword alternation table is $entries entries (> 200; minimization disabled/broken?)"
    fi
fi

# ---- M2.7: `$` patterns must use the O(n) engine, not per-start attempts ----
if gen dollar 'a*b$'; then
    if grep -q 'rx_fev\[' "$WORKDIR/dollar.body"; then
        ok "M2.7: 'a*b\$' uses the unanchored engine with EOL variants"
    else
        bad "M2.7: 'a*b\$' did NOT use the unanchored engine (reverted to O(n^2) attempts?)"
    fi
    if grep -q 'for (start = startpos' "$WORKDIR/dollar.body"; then
        bad "M2.7: 'a*b\$' still emits a per-start-position attempt loop"
    else
        ok "M2.7: no per-start attempt loop for a \$-bearing pattern"
    fi
fi
# ---- M2.10 (NEGATIVE result): narrow-alphabet states stay skip-INELIGIBLE --
# M2.10 tried admitting skip states by fraction-of-LIVE-bytes instead of the
# absolute ">= 192 of 256" rule, so that '[01]*1[01]{8}' (2 live bytes, 100%
# stay) would qualify — R2-A5 had called that case "no skip-eligible states".
# It MEASURED 27% SLOWER on exactly that case (158.6/159.1 -> 118.7 MB/s
# compare, 159.1/157.5 -> 115.9/115.8 bdriver) and was reverted. This check
# exists so the idea cannot be re-landed on plausibility alone: if you change
# eligibility, this fails, and you owe a measurement of the REVERSE machine
# before deciding the new numbers are better.
if gen dense '[01]*1[01]{8}'; then
    if grep -qE 'rx_(fs|rs)[0-9]+\[256\]' "$WORKDIR/dense.body"; then
        bad "M2.10: '[01]*1[01]{8}' now emits a skip table — eligibility was widened; re-measure case (f) (it was 27% SLOWER when this last changed) before accepting"
    else
        ok "M2.10: narrow-alphabet dense pattern stays skip-ineligible (measured regression)"
    fi
fi

# ---- M2.12 ordering is ASYMMETRIC, and deliberately so ------------------
# EOL machines must evaluate accept AFTER scan avoidance (checked below).
# Non-EOL machines must NOT: hoisting the prefilter above the accept check
# cost 43% on '[01]*1[01]{8}' (158.4 -> 90.8 MB/s). Both orders are correct;
# only one is fast, and which one depends on the path.
if gen ordnoeol '[01]*1[01]{8}'; then
    acc_line=$(grep -nE 'if \(rx_facc\[st\]\) last = pos;' "$WORKDIR/ordnoeol.body" | head -1 | cut -d: -f1)
    pre_line=$(grep -nE 'const void \*q = memchr' "$WORKDIR/ordnoeol.body" | head -1 | cut -d: -f1)
    if [ -n "${acc_line:-}" ] && [ -n "${pre_line:-}" ] && [ "$acc_line" -lt "$pre_line" ]; then
        ok "M2.12: non-EOL path keeps accept BEFORE scan avoidance (the fast order)"
    else
        bad "M2.12: non-EOL path moved accept after the prefilter (measured 43% slower on '[01]*1[01]{8}')"
    fi
fi

# ---- M2.12: scan avoidance must be PRESENT on the `$` path too ----------
# M2.7 traded the prefilter and skip loops away for correctness on the EOL
# path and left `$` patterns at ~291 MB/s where the same pattern without `$`
# ran at ~22 GB/s. Nothing in the corpus or the budgets could see that.
if gen eolskip '.*=.*$'; then
    if grep -qE 'rx_fs[0-9]+\[256\]' "$WORKDIR/eolskip.body"; then
        ok "M2.12: '.*=.*\$' emits a skip table on the EOL path"
    else
        bad "M2.12: '.*=.*\$' emitted NO skip table (EOL path lost scan avoidance again?)"
    fi
    # bounded at n-1, never n: a state may accept at an EOL position
    if grep -qE 'while \(pos \+ 1 < n && rx_fs[0-9]+\[s\[pos\]\]\) pos\+\+;' "$WORKDIR/eolskip.body"; then
        ok "M2.12: EOL forward skip loop is bounded at n-1"
    else
        bad "M2.12: EOL forward skip loop missing or not bounded at n-1"
    fi
    if grep -qE 'rst == [0-9]+ && pp \+ 1 < n' "$WORKDIR/eolskip.body"; then
        ok "M2.12: EOL reverse skip loop carries the pp+1<n entry guard"
    else
        bad "M2.12: EOL reverse skip loop missing its pp+1<n entry guard"
    fi
    # ORDER MATTERS, and getting it wrong is what the first M2.12 attempt did:
    # a skip landing on n-1 must not consume that byte before the EOL view of
    # it has been taken. So the accept evaluation must come AFTER the skips.
    skip_line=$(grep -nE 'while \(pos \+ 1 < n && rx_fs[0-9]+' "$WORKDIR/eolskip.body" | tail -1 | cut -d: -f1)
    acc_line=$(grep -nE 'if \(rx_facc\[est\]\) last = pos;' "$WORKDIR/eolskip.body" | head -1 | cut -d: -f1)
    if [ -n "${skip_line:-}" ] && [ -n "${acc_line:-}" ] && [ "$acc_line" -gt "$skip_line" ]; then
        ok "M2.12: EOL accept/eolvar evaluation happens after the skip loops"
    else
        bad "M2.12: EOL accept evaluated BEFORE the skip loops (skip can land on n-1 and lose the match)"
    fi
fi
# the memchr prefilter must survive on the EOL path as well
if gen eolpre 'a*b$'; then
    if grep -q 'memchr' "$WORKDIR/eolpre.body"; then
        ok "M2.12: 'a*b\$' keeps the memchr prefilter on the EOL path"
    else
        bad "M2.12: 'a*b\$' lost its memchr prefilter"
    fi
    # ...but WITHOUT the non-EOL early `return 0`, since the start state's EOL
    # view may still accept at n-1 or n
    if grep -qE 'memchr\(s \+ pos, [0-9]+, n - 1 - pos\)' "$WORKDIR/eolpre.body"; then
        ok "M2.12: EOL memchr is bounded at n-1"
    else
        bad "M2.12: EOL memchr not bounded at n-1"
    fi
fi

# ^ patterns legitimately stay on the attempt engine (documented limitation)
if gen caret '^a|b'; then
    if grep -q 'for (start = startpos' "$WORKDIR/caret.body"; then
        ok "engine selection: partially-^-anchored pattern uses the attempt engine"
    else
        bad "engine selection: '^a|b' unexpectedly on the unanchored engine (^ needs a reverse BOT variant)"
    fi
fi

# ---- OS-1: case-insensitivity FOLDS, it does not become an engine ---------
# D18 predicted case 1 for this dimension: the option changes what the
# automaton is built FROM, not how it runs. These checks assert that in the
# only place it can be observed — the emitted C — because "zero runtime cost"
# is not something the corpus can see. If someone later implements caselessness
# as a runtime check (a tolower() in the hot loop, a folded-lookup table, a
# flag parameter), every one of these fails.
#
# The comparisons use `-o -` (SELF-CONTAINED output) and strip line 1. Line 1
# is the `/* Generated by pcrec. Pattern: ... */` comment, which differs by
# construction. `-o -` is not a detail: writing to two paths emits two
# different `#include "<name>.h"` lines and every comparison would then differ
# for a reason that has nothing to do with folding — the same trap
# run_trie_identity.sh documents at its own gen_a/gen_b.
gensc() { # gensc <name> <pattern> [extra pcrec args...] -> <name>.sc
    local name="$1" pat="$2"
    shift 2
    "$PCREC" -p rx "$@" -o - -- "$pat" 2>/dev/null | tail -n +2 > "$WORKDIR/$name.sc"
    [ -s "$WORKDIR/$name.sc" ] \
        || { bad "$name: pcrec produced no self-contained output for '$pat'"; return 1; }
}

if gensc foldi 'aBc' -i && gensc foldx '[aA][bB][cC]'; then
    if diff -q "$WORKDIR/foldi.sc" "$WORKDIR/foldx.sc" >/dev/null; then
        ok "OS-1: -i 'aBc' emits byte-identical C to '[aA][bB][cC]' (folding IS the automaton)"
    else
        bad "OS-1: -i 'aBc' differs from the hand-written '[aA][bB][cC]' — case folding is no longer a pure class-construction change"
    fi
fi

# THE ORDER CHECK. `[^a]` caseless must fold the POSITIVE set and then
# complement, i.e. be exactly '[^aA]'. Fold after negating and you get every
# byte instead. Both results are case-closed, so nothing else in the pipeline
# can tell them apart; the corpus pins the behaviour and this pins the shape.
if gensc negi '[^a]' -i && gensc negx '[^aA]' && gensc negwrong '[^A]'; then
    if diff -q "$WORKDIR/negi.sc" "$WORKDIR/negx.sc" >/dev/null; then
        ok "OS-1: -i '[^a]' emits byte-identical C to '[^aA]' (folded BEFORE negating)"
    else
        bad "OS-1: -i '[^a]' is not '[^aA]' — the fold is being applied on the wrong side of the negation"
    fi
    if diff -q "$WORKDIR/negi.sc" "$WORKDIR/negwrong.sc" >/dev/null; then
        bad "OS-1: -i '[^a]' collapsed to '[^A]' — one case is being dropped rather than added"
    else
        ok "OS-1: -i '[^a]' is distinct from '[^A]' (the check above is not vacuous)"
    fi
fi

# a pattern with no ASCII letters must be completely untouched by -i
if gensc nolet '[0-9]+-[0-9]+' && gensc nolet_i '[0-9]+-[0-9]+' -i; then
    if diff -q "$WORKDIR/nolet.sc" "$WORKDIR/nolet_i.sc" >/dev/null; then
        ok "OS-1: a letter-free pattern is byte-identical with and without -i"
    else
        bad "OS-1: -i changed the output of a pattern containing no ASCII letters"
    fi
fi

# no runtime case machinery anywhere, and no extra parameter on the entry point
if gen casehot 'Hello|World' -i; then
    if grep -nE 'tolower|toupper|0x20|0xdf|& *~ *32|\| *32' "$WORKDIR/casehot.body" >/dev/null; then
        bad "OS-1: the -i hot loop contains run-time case conversion: $(grep -nE 'tolower|toupper|0x20|0xdf' "$WORKDIR/casehot.body" | head -1)"
    else
        ok "OS-1: -i output contains no run-time case conversion at all"
    fi
    if grep -q '^int rx_search(const unsigned char \*s, size_t n, size_t startpos, rx_span \*m)$' "$WORKDIR/casehot.body"; then
        ok "OS-1: -i leaves the entry-point signature unchanged (a singleton dimension is not in the signature)"
    else
        bad "OS-1: -i changed the entry-point signature — a compiled-away option must not appear at run time (D18)"
    fi
fi

# ---- OS-0b: multi-engine output, and the control for every check above ----
# D18/D20 let one file carry several engines chosen by a generated selector.
# Nothing in pcrec emits two engines yet — the FINDER that would (OS-0) is
# deliberately unbuilt until a dimension earns an axis — so this block builds
# the two-engine file by hand, applying exactly the transformation the finder
# will: keep ONE span typedef for the file, give each engine its own entry
# name, and leave every other identifier alone (they are function-local
# statics and cannot collide, which is the measured finding OS-0b rests on).
#
# It buys two things at once. It proves the output contract compiles, and it
# is the positive+negative control for `body()`: engine A ('.*=.*') has skip
# tables and engine B ('^a|b') has none, so a scoped grep must find them in A
# and NOT in B. A `body()` that returned the whole file would fail the B
# check; one that returned nothing would fail the A check. Neither can pass
# by accident, which is what the 256-branch-control lesson in CLAUDE.md is
# about — a control has to fire inside the range of what it certifies.
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if ! command -v "$CC" >/dev/null 2>&1; then
    bad "multi-engine: no C compiler ($CC) — this block cannot be skipped silently"
elif "$PCREC" -p rx -o - -- '.*=.*' > "$WORKDIR/multi.c" 2>/dev/null \
  && "$PCREC" -p rx -o - -- '^a|b'  > "$WORKDIR/engb.c"  2>/dev/null \
  && body "$WORKDIR/engb.c" rx_search "$WORKDIR/engb.body"; then
    # rename engine B's entry point; every other symbol in the body is
    # function-local and deliberately left untouched
    {
        echo
        echo "int rx_search_b(const unsigned char *s, size_t n, size_t startpos, rx_span *m);"
        sed 's/\brx_search\b/rx_search_b/g' "$WORKDIR/engb.body"
    } >> "$WORKDIR/multi.c"

    if [ "$(grep -c 'typedef struct { size_t start, end; } rx_span;' "$WORKDIR/multi.c")" -eq 1 ]; then
        ok "OS-0b: two-engine file carries exactly ONE rx_span typedef"
    else
        bad "OS-0b: rx_span typedef is not emitted exactly once per file"
    fi

    if $CC -c $GENCFLAGS -o "$WORKDIR/multi.o" "$WORKDIR/multi.c" 2>"$WORKDIR/multi.log"; then
        ok "OS-0b: two engines compile in one file (shared span typedef, distinct entry names)"
    else
        bad "OS-0b: two-engine file failed to compile: $(head -3 "$WORKDIR/multi.log" | tr '\n' ' ')"
    fi

    # ...and the shared typedef is a REQUIREMENT, not a tidiness preference:
    # a second copy declares a second anonymous struct type, so gcc rejects
    # the file ("conflicting types for 'rx_span'"). Asserted rather than
    # asserted-in-a-comment, so nobody later "simplifies" emit_span_typedef
    # into the per-engine path and finds out at integration time.
    sed '0,/typedef struct { size_t start, end; } rx_span;/s//typedef struct { size_t start, end; } rx_span;\ntypedef struct { size_t start, end; } rx_span;/' \
        "$WORKDIR/multi.c" > "$WORKDIR/multi_dup.c"
    if $CC -c $GENCFLAGS -o "$WORKDIR/multi_dup.o" "$WORKDIR/multi_dup.c" 2>/dev/null; then
        bad "OS-0b: a DUPLICATED rx_span typedef compiled — the emit-once rule is not load-bearing here; recheck the multi-engine contract"
    else
        ok "OS-0b: duplicating the rx_span typedef breaks the build (emit-once is load-bearing)"
    fi

    # the control for every engine-scoped grep above
    if grep -qE 'rx_fs[0-9]+\[256\]' "$WORKDIR/multi.c"; then
        if body "$WORKDIR/multi.c" rx_search "$WORKDIR/multi.a.body" \
        && body "$WORKDIR/multi.c" rx_search_b "$WORKDIR/multi.b.body"; then
            if grep -qE 'rx_fs[0-9]+\[256\]' "$WORKDIR/multi.a.body"; then
                ok "OS-0b: scoped grep finds the skip table in the engine that has one"
            else
                bad "OS-0b: scoped grep MISSED the skip table in '.*=.*' (body() extracting nothing?)"
            fi
            if grep -qE 'rx_fs[0-9]+\[256\]' "$WORKDIR/multi.b.body"; then
                bad "OS-0b: scoped grep attributed engine A's skip table to engine B — body() is not scoping, so every symbol check above has silently weakened to 'some engine here does'"
            else
                ok "OS-0b: scoped grep does NOT attribute engine A's skip table to engine B"
            fi
        else
            bad "OS-0b: could not extract both engine bodies from the two-engine file"
        fi
    else
        bad "OS-0b: two-engine file has no skip table at all — the control cannot discriminate"
    fi
else
    bad "multi-engine: could not build the two-engine fixture"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "codegen: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
