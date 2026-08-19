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
# D45: one shared generated-code compile budget (docs/dev/decisions.md).
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
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
# [M4.5b] the anchor accepts an optional `static`: a VM artifact emits the DFA
# engine under a private name as its prefilter (engine_m4.md §6.1), which is
# the SAME emitter's output with a different storage class, and it must be
# extractable for the same per-engine scoping reason every other body is.
body() { # body <file> <entry-name> <out-file>
    awk -v fn="$2" '
        $0 ~ "^(static )?int " fn "\\(" { inside = 1 }
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
#
# [M4.5b] The group is NON-CAPTURING now. It was incidental to what this check
# measures (a DFA table's size) and became load-bearing in the wrong direction
# when D42.1 made captures the default: the capturing spelling routes to a VM
# artifact, where the table lives in `rx_prefilter` and not in the `rx_search`
# body `gen` extracts. Making the pattern say what it means is the fix; the
# prefilter's OWN minimization is then checked separately below, which is
# coverage this check did not have before.
if gen minim '(?:get|post|put|delete|patch)'; then
    entries=$(grep -oE 'rx_ftr\[[0-9]+\]' "$WORKDIR/minim.body" | grep -oE '[0-9]+' | head -1)
    if [ -z "${entries:-}" ]; then
        bad "minimization: could not find rx_ftr[] table in generated code"
    elif [ "$entries" -le 200 ]; then
        ok "minimization: keyword alternation table is $entries entries (<= 200)"
    else
        bad "minimization: keyword alternation table is $entries entries (> 200; minimization disabled/broken?)"
    fi
fi

# [M4.5b] ...and the VM's DFA PREFILTER is minimized too. The hybrid runs the
# same forward+reverse pair through the same passes (engine_m4.md §6.1, §2.8's
# "reused unchanged" table), so a minimization bug scoped to that path would be
# invisible to the check above — which only ever looks at an artifact where the
# DFA IS the engine. Same alternation, capturing, so the routing differs and
# nothing else does.
if "$PCREC" -p rx -o "$WORKDIR/minimvm.c" -- '(get|post|put|delete|patch)' >/dev/null 2>&1; then
    if ! body "$WORKDIR/minimvm.c" rx_prefilter "$WORKDIR/minimvm.body"; then
        bad "minimization/prefilter: could not extract rx_prefilter from the VM artifact"
    else
        ventries=$(grep -oE 'rx_ftr\[[0-9]+\]' "$WORKDIR/minimvm.body" | grep -oE '[0-9]+' | head -1)
        if [ -z "${ventries:-}" ]; then
            bad "minimization/prefilter: no rx_ftr[] table inside the VM artifact's prefilter"
        elif [ "$ventries" -le 200 ]; then
            ok "minimization/prefilter: the VM hybrid's prefilter table is $ventries entries (<= 200) — the same passes run on that path"
        else
            bad "minimization/prefilter: prefilter table is $ventries entries (> 200; minimization skipped on the hybrid's path?)"
        fi
    fi
else
    bad "minimization/prefilter: could not compile the capturing alternation"
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
#
# [M4.4] SCOPES the comparison down to the rx_search ENGINE BODY (via
# body()), not the whole file, and this is a deliberate narrowing, not a
# weakening: `rx_info` (D43.1) embeds the source PATTERN TEXT and the
# compiled `flags` word unconditionally, both of which legitimately differ
# between two DIFFERENT pattern spellings (or between -i and no -i, even on
# a pattern -i has no folding effect on — the flag was still set as
# compiled) — the same "the stamp differs by design" shape D37's [STD1]
# case9/case10 already established in tests/cli/. D18's zero-cost claim was
# always about the AUTOMATON specifically, which is exactly what body()
# extracts.
gensc() { # gensc <name> <pattern> [extra pcrec args...] -> <name>.body
    local name="$1" pat="$2"
    shift 2
    "$PCREC" -p rx "$@" -o - -- "$pat" 2>/dev/null > "$WORKDIR/$name.sc"
    [ -s "$WORKDIR/$name.sc" ] \
        || { bad "$name: pcrec produced no self-contained output for '$pat'"; return 1; }
    body "$WORKDIR/$name.sc" rx_search "$WORKDIR/$name.body" \
        || { bad "$name: could not extract the rx_search engine body"; return 1; }
}

if gensc foldi 'aBc' -i && gensc foldx '[aA][bB][cC]'; then
    if diff -q "$WORKDIR/foldi.body" "$WORKDIR/foldx.body" >/dev/null; then
        ok "OS-1: -i 'aBc' emits a byte-identical engine to '[aA][bB][cC]' (folding IS the automaton)"
    else
        bad "OS-1: -i 'aBc' differs from the hand-written '[aA][bB][cC]' — case folding is no longer a pure class-construction change"
    fi
fi

# THE ORDER CHECK. `[^a]` caseless must fold the POSITIVE set and then
# complement, i.e. be exactly '[^aA]'. Fold after negating and you get every
# byte instead. Both results are case-closed, so nothing else in the pipeline
# can tell them apart; the corpus pins the behaviour and this pins the shape.
if gensc negi '[^a]' -i && gensc negx '[^aA]' && gensc negwrong '[^A]'; then
    if diff -q "$WORKDIR/negi.body" "$WORKDIR/negx.body" >/dev/null; then
        ok "OS-1: -i '[^a]' emits a byte-identical engine to '[^aA]' (folded BEFORE negating)"
    else
        bad "OS-1: -i '[^a]' is not '[^aA]' — the fold is being applied on the wrong side of the negation"
    fi
    if diff -q "$WORKDIR/negi.body" "$WORKDIR/negwrong.body" >/dev/null; then
        bad "OS-1: -i '[^a]' collapsed to '[^A]' — one case is being dropped rather than added"
    else
        ok "OS-1: -i '[^a]' is distinct from '[^A]' (the check above is not vacuous)"
    fi
fi

# a pattern with no ASCII letters must have an untouched ENGINE BODY under
# -i (D18's zero-cost claim). [M4.4]: rx_info.flags legitimately differs
# (PCREC_CASELESS is set as COMPILED, whether or not it had any folding
# effect on this particular pattern) — see the gensc comment above.
if gensc nolet '[0-9]+-[0-9]+' && gensc nolet_i '[0-9]+-[0-9]+' -i; then
    if diff -q "$WORKDIR/nolet.body" "$WORKDIR/nolet_i.body" >/dev/null; then
        ok "OS-1: a letter-free pattern's engine body is byte-identical with and without -i"
    else
        bad "OS-1: -i changed the engine body of a pattern containing no ASCII letters"
    fi
fi

# no runtime case machinery anywhere, and no extra parameter on the entry point
if gen casehot 'Hello|World' -i; then
    if grep -nE 'tolower|toupper|0x20|0xdf|& *~ *32|\| *32' "$WORKDIR/casehot.body" >/dev/null; then
        bad "OS-1: the -i hot loop contains run-time case conversion: $(grep -nE 'tolower|toupper|0x20|0xdf' "$WORKDIR/casehot.body" | head -1)"
    else
        ok "OS-1: -i output contains no run-time case conversion at all"
    fi
    if grep -q '^int rx_search(const unsigned char \*s, size_t n, size_t startpos, ptrdiff_t (\*caps)\[2\])$' "$WORKDIR/casehot.body"; then
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
# will: keep the ABI-types block once for the file, give each engine its own
# entry name, and leave every other identifier alone (they are function-local
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
# SAN-1 LINTGEN: ride this GENCFLAGS compile with gcc -fanalyzer, opt-in.
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
if ! command -v "$CC" >/dev/null 2>&1; then
    bad "multi-engine: no C compiler ($CC) — this block cannot be skipped silently"
elif "$PCREC" -p rx -o - -- '.*=.*' > "$WORKDIR/multi.c" 2>/dev/null \
  && "$PCREC" -p rx -o - -- '^a|b'  > "$WORKDIR/engb.c"  2>/dev/null \
  && body "$WORKDIR/engb.c" rx_search "$WORKDIR/engb.body"; then
    # rename engine B's entry point; every other symbol in the body is
    # function-local and deliberately left untouched
    {
        echo
        echo "int rx_search_b(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2]);"
        sed 's/\brx_search\b/rx_search_b/g' "$WORKDIR/engb.body"
    } >> "$WORKDIR/multi.c"

    if [ "$(grep -c '^#define PCREC_RX_ABI_H$' "$WORKDIR/multi.c")" -eq 1 ]; then
        ok "OS-0b [M4.4]: two-engine file carries exactly ONE ABI-types block"
    else
        bad "OS-0b [M4.4]: the fixed ABI-types block is not emitted exactly once per file"
    fi

    if gen_cc "multi-engine fixture" "$CC" -c $GENCFLAGS -o "$WORKDIR/multi.o" "$WORKDIR/multi.c"; then
        ok "OS-0b: two engines compile in one file (shared ABI types, distinct entry names)"
    else
        bad "OS-0b: two-engine file failed to compile: $(head -3 "$WORKDIR/multi.log" | tr '\n' ' ')"
    fi

    # [M4.4] (D44/A-2) INVERTS the old assertion here on purpose, not by
    # oversight: the retired `<prefix>_span` typedef was NOT include-guarded,
    # so a second copy declared a second anonymous struct type and gcc
    # rejected the file ("conflicting types for 'rx_span'") — the panel
    # MEASURED that shape as a hazard for the fixed ABI types too (two
    # differently-prefixed generated headers in one TU each deriving their
    # OWN include guard), and the fix was a guard SPELLED THE SAME regardless
    # of --prefix. That guard's whole job is to make a second, byte-identical
    # copy of this block a harmless no-op, so the property worth asserting
    # flipped: duplicating the block must NOT break the build anymore. See
    # the two-differently-prefixed-headers-in-one-TU check this file's
    # CLAUDE.md documents as the sabotage-equivalent positive control.
    # Duplicate the WHOLE guarded block (guard included)
    # by re-emitting everything between its #ifndef and matching #endif a
    # second time, immediately after the first copy.
    awk '
        /^#ifndef PCREC_RX_ABI_H$/ { inblock = 1; block = $0 "\n"; next }
        inblock && /^#endif \/\* PCREC_RX_ABI_H \*\// {
            block = block $0 "\n"
            inblock = 0
            printf "%s", block
            printf "%s", block
            next
        }
        inblock { block = block $0 "\n"; next }
        { print }
    ' "$WORKDIR/multi.c" > "$WORKDIR/multi_dup.c"
    if [ "$(grep -c '^#define PCREC_RX_ABI_H$' "$WORKDIR/multi_dup.c")" -eq 2 ] \
        && gen_cc "duplicated ABI block" "$CC" -c $GENCFLAGS -o "$WORKDIR/multi_dup.o" "$WORKDIR/multi_dup.c"; then
        ok "OS-0b [M4.4]: a DUPLICATED (guard-included) ABI-types block still compiles — the prefix-independent #ifndef guard (D44/A-2) makes re-inclusion a no-op"
    else
        bad "OS-0b [M4.4]: duplicating the guarded ABI-types block broke the build: $(head -3 "$WORKDIR/multi_dup.log" 2>/dev/null | tr '\n' ' ')"
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

# ---- D44/A-2: the ABI-types guard is PREFIX-INDEPENDENT -------------------
# The fixed ABI types (rx_ctx, rx_matchfn, rx_callout_ref, rx_group_entry,
# rx_info, rx_renderfn) are shared, byte-for-byte, by every generated
# matcher regardless of its own --prefix — the entire point of the callout
# ABI's composability (a compiled matcher links directly as a callout for
# another, match_api_m4.md §7/§12.7). The R21 panel MEASURED that a guard
# DERIVED FROM --prefix breaks exactly this case: two differently-prefixed
# generated headers, in one TU, each spell a DIFFERENT guard name and so
# both bodies re-define rx_ctx/rx_matchfn/etc. — a hard redefinition error,
# not a harmless no-op. This check builds that TU for real, with two
# genuinely different prefixes, and is this file's positive control for the
# `#ifndef PCREC_RX_ABI_H` fix (D44, ratifying A-2).
if "$PCREC" -p rx -o "$WORKDIR/dprx.c" -- 'a(b|c)+d' >/dev/null 2>&1 \
   && "$PCREC" -p qq -o "$WORKDIR/dpqq.c" -- 'x(y|z)+w' >/dev/null 2>&1; then
    printf '#include "dprx.h"\n#include "dpqq.h"\nint main(void){return 0;}\n' > "$WORKDIR/dp_main.c"
    if gen_cc "cross-prefix one-TU" "$CC" -c $GENCFLAGS -I"$WORKDIR" -o "$WORKDIR/dp_main.o" "$WORKDIR/dp_main.c"; then
        ok "D44/A-2: two differently-prefixed generated headers compile together in one TU (prefix-independent ABI guard)"
    else
        bad "D44/A-2: two differently-prefixed generated headers FAILED to compile together: $(head -3 "$WORKDIR/dp_main.log" | tr '\n' ' ')"
    fi
else
    bad "D44/A-2: could not generate the two differently-prefixed fixtures"
fi

# ---- [ABI-NS]: an artifact's header and lib/pcrec.h compile together, -----
# ---- in BOTH include orders ------------------------------------------------
# D60's addendum named PCREC_ENGINE_DFA/PCREC_ENGINE_VM for rx_info.engine's
# outcome (this check's own file, emit_rx_abi_types) using the SAME spelling
# lib/pcrec.h already used for pcrec_options.engine's REQUEST — found during
# the [ABI-NS] lane, not anticipated by the ruling. The two are declared by
# DIFFERENT mechanisms (an emitted `#define`, a header `enum`), and an enum
# enumerator textually rewritten by an EARLIER `#define` of its own name is a
# hard syntax error, not a warning — measured directly against gcc. The fix
# (lib/pcrec.h §lib/CLAUDE.md's [ABI-NS] entry) converts lib/pcrec.h's two
# enumerators to plain `#define`s BYTE-IDENTICAL to what every artifact
# emits, so two identical `#define`s of one name are a silent no-op
# regardless of which file is included first. This is the model
# D44/A-2's own check above uses (build the real TU, both real headers,
# under -Wall -Wextra -Werror) applied to a NEW cross-file identity
# obligation this lane created: lib/pcrec.h's PCREC_ENGINE_DFA/PCREC_ENGINE_VM
# `#define` text must stay byte-identical to emit_rx_abi_types' emission
# FOREVER, or whichever file is included second breaks the other. An
# unchecked identity constraint between two independently-edited files is
# this project's own named failure class (see the pcrec-check-design-lessons
# memory this lane inherited); this is the check that makes a drift loud.
if "$PCREC" -p rx -o "$WORKDIR/eng.c" -- 'a(b|c)+d' >/dev/null 2>&1; then
    printf '#include "eng.h"\n#include "pcrec.h"\nint main(void){ return (int)PCREC_ENGINE_DFA + (int)PCREC_ENGINE_VM; }\n' \
        > "$WORKDIR/eng_order1.c"
    printf '#include "pcrec.h"\n#include "eng.h"\nint main(void){ return (int)PCREC_ENGINE_DFA + (int)PCREC_ENGINE_VM; }\n' \
        > "$WORKDIR/eng_order2.c"
    ok1=1; ok2=1
    gen_cc "[ABI-NS] artifact.h before pcrec.h" "$CC" -c $GENCFLAGS -I"$WORKDIR" -I"$ROOT_DIR/lib" \
        -o "$WORKDIR/eng_order1.o" "$WORKDIR/eng_order1.c" || ok1=0
    gen_cc "[ABI-NS] pcrec.h before artifact.h" "$CC" -c $GENCFLAGS -I"$WORKDIR" -I"$ROOT_DIR/lib" \
        -o "$WORKDIR/eng_order2.o" "$WORKDIR/eng_order2.c" || ok2=0
    if [ "$ok1" -eq 1 ] && [ "$ok2" -eq 1 ]; then
        ok "[ABI-NS]: an artifact's header and lib/pcrec.h compile together in one TU in BOTH include orders (PCREC_ENGINE_DFA/PCREC_ENGINE_VM stay byte-identical across the two declaration mechanisms)"
    else
        bad "[ABI-NS]: artifact-header/pcrec.h one-TU compile FAILED (order1 ok=$ok1, order2 ok=$ok2) — PCREC_ENGINE_DFA/PCREC_ENGINE_VM have drifted apart between emit_rx_abi_types (src/gen/emit_dfa.c) and lib/pcrec.h; they must stay byte-identical #define text"
    fi
else
    bad "[ABI-NS]: could not generate the split-header fixture for the pcrec.h include-order check"
fi

# ---- D37: emitted C is self-describing about its feature set -------------
# docs/dev/decisions.md D37 / [STD1] phase A: every emitted file carries a
# comment AND (in the .c) two macros stamping the enabled set's own NAME and
# its EXPANDED module list, rendered from the mask by src/parse/enabled.c so
# it can never say something the compile didn't actually do. Whole-file
# checks (not `body()` — the stamp is outside any engine function, at the
# very top).
if "$PCREC" -p rx --features std1 -o "$WORKDIR/stamp.c" -- 'a' >/dev/null 2>&1; then
    if grep -qF '/* Feature set: std1 (modules: classes,modifiers) */' "$WORKDIR/stamp.c" \
       && grep -qF '#define PCREC_FEATURE_SET "std1"' "$WORKDIR/stamp.c" \
       && grep -qF '#define PCREC_FEATURE_MODULES "classes,modifiers"' "$WORKDIR/stamp.c"; then
        ok "D37: --features std1 stamps its name and expanded module list in the .c"
    else
        bad "D37: --features std1 did not stamp the expected comment/macros" \
            "$(head -4 "$WORKDIR/stamp.c")"
    fi
    if grep -qF '/* Feature set: std1 (modules: classes,modifiers) */' "$WORKDIR/stamp.h" \
       2>/dev/null; then
        ok "D37: the paired .h carries the same stamp COMMENT"
    else
        bad "D37: the paired .h is missing the stamp comment"
    fi
    if grep -q 'PCREC_FEATURE_SET' "$WORKDIR/stamp.h" 2>/dev/null; then
        bad "D37: the paired .h must not carry the stamp MACROS (only the .c does)"
    else
        ok "D37: the paired .h carries no macros, so a .c that includes it defines PCREC_FEATURE_SET once"
    fi
else
    bad "D37: pcrec failed to compile 'a' under --features std1"
fi
# a bare invocation (no --features) still stamps — the resolved default,
# not silence: an unstamped artifact would be ambiguous the day the bare
# default itself changes (D37's own point, and [STD1b], 2026-08-13, is
# that day: the bare default moved from "none" to the frozen named set
# `std1` = {classes, modifiers}, so a bare invocation now stamps std1's own
# expansion). `--features none` is what now stamps "none" explicitly.
if "$PCREC" -p rx -o - -- 'a' 2>/dev/null | grep -qF '/* Feature set: std1 (modules: classes,modifiers) */'; then
    ok "D37: a bare invocation stamps the resolved default ('std1'), not nothing"
else
    bad "D37: a bare invocation's stamp is missing or wrong"
fi
if "$PCREC" -p rx --features none -o - -- 'a' 2>/dev/null | grep -qF '/* Feature set: none (modules: none) */'; then
    ok "D37: --features none stamps 'none' explicitly (the escape hatch, unaffected by [STD1b])"
else
    bad "D37: --features none's stamp is missing or wrong"
fi

# ---- TS-1: the generated matcher stays usable FROM threads (D19) ---------
# D19's property for GENERATED code reduces to two mechanical facts: every
# emitted `static` is `const` — so it is .rodata with a constant initialiser,
# no lazy init and nothing to race on — and the output references no
# non-reentrant or allocating libc.
#
# Both hold TODAY by construction, and both are invisible to every other test
# in this repo. That is the exact shape this project keeps losing: a
# memoisation cache, a hoisted scratch buffer, a diagnostics counter, an
# errno-setting call, or (under D18) a selector caching its choice in a global
# would each keep the whole corpus green while quietly making the matcher
# thread-hostile. No gcc needed, so this is the cheapest guard on the board.
#
# Line 1 of every emitted file is stripped before scanning: it is the
# `/* Generated by pcrec. Pattern: ... */` comment, which echoes the user's
# pattern text verbatim, so a pattern like `malloc` or `getenv` would
# otherwise fail its own denylist.
#
# The scan is textual and does NOT strip C comments, so an emitted comment that
# merely MENTIONS one of these symbols ("no malloc here") will trip it. That is
# deliberate and the fix is to reword the comment: a denylist that silently
# tolerates its own words in some contexts is a denylist nobody can reason
# about. Narrow it consciously if you ever need to, never accidentally.
TS1_DENY='malloc|calloc|realloc|free|errno|getenv|setenv|putenv|setlocale|strtok|rand|srand|asctime|ctime|gmtime|localtime|tmpnam|strerror|atexit'

ts1_scan() { # ts1_scan <label> <file>
    local lbl="$1" f="$2" hit
    # [M4.5b] NARROWED, and narrowed CONSCIOUSLY (this file's own instruction
    # two paragraphs up): a static FUNCTION is excluded, a static OBJECT is
    # not. D19's property is "no mutable file/function-scope STATE", and a
    # function has no storage to race on — but until the VM emitter existed,
    # every emitted `static` was a table, so "static and not const" and "mutable
    # state" were the same set and the check could not tell them apart. The VM
    # artifact emits five static functions (rx_match_impl, rx_work_init,
    # rx_unwind, rx_caps_out, rx_prefilter) and its whole mutable working set is
    # a LOCAL of the search entry, which is exactly what D19 asks for.
    #
    # The discriminator is C's declarator syntax, not a name list: a function
    # declarator has `(` with no `=`, `;` or `[` before it. So
    # `static void rx_unwind(rx_work *w)` is excluded and
    # `static unsigned char rx_tbl[256] = {` (S06's sabotage — a table with its
    # const dropped) still has no `(` at all and is still caught, as is anything
    # of the shape `static int rx_counter = f(0);`, where `=` precedes the `(`.
    # Validated by re-running S06 through tests/mech after the narrowing.
    hit="$(tail -n +2 "$f" | grep -nE '^[[:space:]]*static ' \
           | grep -vE ':[[:space:]]*static const ' \
           | grep -vE ':[[:space:]]*static [^=;[]*\(' | head -2)"
    if [ -n "$hit" ]; then
        bad "TS-1 [$lbl]: emitted a NON-CONST static OBJECT — generated code must have no mutable file/function-scope state (D19): $hit"
        return 1
    fi
    hit="$(tail -n +2 "$f" | grep -nE "\\b($TS1_DENY)\\b" | head -2)"
    if [ -n "$hit" ]; then
        bad "TS-1 [$lbl]: emitted code references a non-reentrant/allocating symbol: $hit"
        return 1
    fi
    return 0
}

ts1_files=0
ts1_bad=0
ts1_one() { # ts1_one <label> <pattern> [extra pcrec args...]
    local lbl="$1" pat="$2"
    shift 2
    "$PCREC" -p rx "$@" -o "$WORKDIR/ts1.c" -- "$pat" >/dev/null 2>&1 \
        || { bad "TS-1 [$lbl]: pcrec failed to compile '$pat'"; return; }
    local f
    for f in "$WORKDIR/ts1.c" "$WORKDIR/ts1.h"; do
        [ -f "$f" ] || continue
        ts1_files=$((ts1_files + 1))
        ts1_scan "$lbl $(basename "$f")" "$f" || ts1_bad=$((ts1_bad + 1))
    done
}

# every emission shape: both engines, EOL and non-EOL, both prefilter kinds,
# skip states, the degenerate never-matches path, folding, and --emit-main
ts1_one "memchr prefilter"  'needleXYZW'
ts1_one "bitmap prefilter"  '(error|warning|fatal)'
ts1_one "skip states"       '.*=.*'
ts1_one "EOL engine"        '.*=.*$'
ts1_one "attempt engine"    '^a|b'
ts1_one "fully anchored"    '^abc$'
ts1_one "never matches"     '[^\x00-\xff]'
ts1_one "case-folded"       'Hello|World' -i
ts1_one "emit-main"         'abc' --emit-main

if [ "$ts1_files" -lt 12 ]; then
    bad "TS-1: only $ts1_files emitted files scanned — the sweep is not covering the emission shapes it claims to"
elif [ "$ts1_bad" -eq 0 ]; then
    ok "TS-1: $ts1_files emitted files across 9 emission shapes — every static is const, no non-reentrant libc"
fi

# ---- [M4.4] structural checks (match_api_m4.md §11 item 9, D42.2/D44.5) ----
# rx_info.ncaps == RX_NCAPS is a BY-CONSTRUCTION invariant in this emitter
# (the initializer writes the macro's OWN NAME, never a second literal), and
# RX_NCAPS > 1 => VM (D42.2) is trivially green until [M4.5] since RX_NCAPS
# is 1 on every artifact this DFA-only emitter produces — asserted now, live
# from this commit, so a future emitter change that breaks either invariant
# fails here rather than being discovered once the VM exists.
if "$PCREC" -p rx -o - -- 'a(b|c)+d' > "$WORKDIR/m44info.c" 2>/dev/null; then
    if grep -qF '.ncaps = RX_NCAPS,' "$WORKDIR/m44info.c"; then
        ok "[M4.4]: rx_info.ncaps is written as the RX_NCAPS macro itself (structural ncaps == RX_NCAPS)"
    else
        bad "[M4.4]: rx_info.ncaps is not the RX_NCAPS macro — the ncaps==RX_NCAPS invariant is no longer structural"
    fi

    ncaps_val="$(grep -oE '^#define RX_NCAPS [0-9]+' "$WORKDIR/m44info.c" | awk '{print $3}')"
    engine_val="$(grep -oE '\.engine = [0-9]+' "$WORKDIR/m44info.c" | awk '{print $3}')"
    if [ -z "${ncaps_val:-}" ] || [ -z "${engine_val:-}" ]; then
        bad "[M4.4]: could not extract RX_NCAPS/rx_info.engine from generated output"
    elif [ "$ncaps_val" -gt 1 ] && [ "$engine_val" -ne 2 ]; then
        bad "[M4.4]: RX_NCAPS ($ncaps_val) > 1 but rx_info.engine ($engine_val) is not PCREC_ENGINE_VM (2) — RX_NCAPS>1 must imply the VM engine (D42.2)"
    else
        ok "[M4.4/M4.5b]: RX_NCAPS ($ncaps_val) > 1 => VM structural check holds — NON-VACUOUSLY since [M4.5b] (this cell had no population at all while the DFA was the only emitter; tests/codegen/run_vm_identity.sh runs it over the whole corpus)"
    fi
else
    bad "[M4.4]: pcrec failed to compile 'a(b|c)+d' for the structural NCAPS/engine checks"
fi

# ---- [M4.7c] rx_info.pattern_len — K9's API half (match_api_m4.md §5, D44.5) -
# K9 (docs/dev/known_issues.md): pcrec_compile() takes a NUL-terminated
# pattern and no length, so a pattern containing a NUL is silently truncated
# and the compile reports SUCCESS for a different, shorter pattern than the
# caller passed. `pattern_len` is the field that makes this detectable — a
# caller who independently knows the intended byte length can compare it
# against the artifact's own report. Two structural cells: an ordinary
# pattern (pattern_len is exactly the pattern's byte count) and a pattern
# whose SOURCE SPELLING is longer than what the matcher actually walks
# (`\n` is two source bytes — backslash, n — standing for one matched byte),
# so a pattern_len that quietly reported the matched-byte count instead of
# the source-byte count would pass the first cell and fail this one. The
# embedded-NUL cell itself (the K9 repro proper) cannot be expressed here —
# argv has no way to carry a NUL through to pcrec — so it lives as a direct
# library-API C probe in tests/cli/run_cli_tests.sh case16.
if "$PCREC" -p rx -o - -- 'abc' > "$WORKDIR/patlen1.c" 2>/dev/null; then
    if grep -qF '.pattern_len = 3,' "$WORKDIR/patlen1.c"; then
        ok "[M4.7c]: rx_info.pattern_len is 3 for the 3-byte pattern 'abc'"
    else
        bad "[M4.7c]: rx_info.pattern_len is not 3 for 'abc' (got: $(grep -oE '\.pattern_len = [0-9]+' "$WORKDIR/patlen1.c"))"
    fi
else
    bad "[M4.7c]: pcrec failed to compile 'abc' for the pattern_len structural check"
fi

if "$PCREC" -p rx -o - -- 'a\nb' > "$WORKDIR/patlen2.c" 2>/dev/null; then
    # source spelling is 4 bytes (a, \, n, b); the matcher itself walks 3
    # matched bytes (a, newline, b) — pattern_len must report the SOURCE
    # count, never the matched-byte count, which is the exact distinction
    # this pattern is chosen to force.
    if grep -qF '.pattern_len = 4,' "$WORKDIR/patlen2.c"; then
        ok "[M4.7c]: rx_info.pattern_len is 4 (source spelling) for 'a\\nb', not 3 (matched bytes)"
    else
        bad "[M4.7c]: rx_info.pattern_len is not 4 for 'a\\nb' (got: $(grep -oE '\.pattern_len = [0-9]+' "$WORKDIR/patlen2.c"))"
    fi
else
    bad "[M4.7c]: pcrec failed to compile 'a\\nb' for the pattern_len structural check"
fi

# ---- [K24] <prefix>_search must not be SPLIT by gcc's partial inliner -----
# This is the file's founding charter, exactly (see the header): a
# behaviour-preserving property whose absence produces ZERO signal from the
# corpus or from `make test`, and which cost a measured 1.33x on
# tests/bench/compare case (c) for three days with only a bench floor
# noticing. `emit_search_head` emits __attribute__((noclone)) to deny gcc
# -O2's partial-inlining pass the `<prefix>_search.part.0` clone; the ONLY
# symptom of that attribute going missing is throughput.
#
# TWO THINGS ABOUT THIS CHECK'S DESIGN, both learned the hard way in this repo:
#
# 1. IT COMPILES AT -O2 EXPLICITLY, not under $GENCFLAGS (which defaults to
#    -O1). Partial inlining is an -O2 pass; run at -O1 this check would pass
#    on every artifact forever, attribute or not — a green cell with no
#    population, which is the failure this directory's CLAUDE.md is about.
# 2. IT CARRIES ITS OWN CONTROL, and the control's source is INDEPENDENT of
#    what it controls. The positive asks `nm` — gcc's own output — whether a
#    clone exists; the control strips the attribute back out of the SAME
#    generated file and asserts gcc DOES clone it. Without the control, a
#    future gcc that stopped splitting (or a build where the pass is off)
#    would make the positive vacuously green and this guard would quietly
#    stop guarding. If the control fails, the check has lost its population
#    and says so, rather than reporting success.
if ! command -v nm >/dev/null 2>&1; then
    bad "[K24]: nm is unavailable — this check cannot be skipped silently (it is the only guard on the noclone lever; see docs/dev/known_issues.md K24)"
elif ! command -v "$CC" >/dev/null 2>&1; then
    bad "[K24]: no C compiler ($CC) — this check cannot be skipped silently"
elif "$PCREC" -p rx --no-captures -o - -- '(alpha|beta|gamma|delta|epsilon)' > "$WORKDIR/k24.c" 2>/dev/null; then
    # -O2 is the point, and -Werror stays so the attribute cannot be landing
    # only because nobody compiles this artifact strictly.
    K24FLAGS="-O2 -std=gnu11 -Wall -Wextra -Werror"
    sed '/__attribute__((noclone))/d' "$WORKDIR/k24.c" > "$WORKDIR/k24_stripped.c"

    if [ "$(grep -c '__attribute__((noclone))' "$WORKDIR/k24.c")" -lt 1 ]; then
        bad "[K24]: emitted artifact carries no __attribute__((noclone)) at all — the K24 lever has been removed from emit_search_head (docs/dev/known_issues.md K24, docs/design/k24bisect_impl/k24_fix_note.md)"
    elif ! gen_cc "K24 noclone subject" "$CC" -c $K24FLAGS -o "$WORKDIR/k24.o" "$WORKDIR/k24.c"; then
        bad "[K24]: the artifact failed to compile at -O2 -Werror: $(printf '%s' "$GEN_CC_LOG" | head -3 | tr '\n' ' ')"
    elif ! gen_cc "K24 noclone control" "$CC" -c $K24FLAGS -o "$WORKDIR/k24_stripped.o" "$WORKDIR/k24_stripped.c"; then
        bad "[K24]: the attribute-stripped CONTROL failed to compile at -O2 -Werror: $(printf '%s' "$GEN_CC_LOG" | head -3 | tr '\n' ' ')"
    else
        k24_clones="$(nm "$WORKDIR/k24.o" | grep -cE 'rx_search\.(part|constprop|isra)\.[0-9]+' || true)"
        k24_ctl_clones="$(nm "$WORKDIR/k24_stripped.o" | grep -cE 'rx_search\.(part|constprop|isra)\.[0-9]+' || true)"
        if [ "$k24_ctl_clones" -eq 0 ]; then
            bad "[K24]: the CONTROL did not fire — with __attribute__((noclone)) stripped, $CC at -O2 still emitted no rx_search clone, so this check has NO POPULATION and cannot certify the lever. Do not delete the attribute on the strength of a green run here; find out why the compiler stopped splitting first (docs/design/k24bisect_impl/k24_fix_note.md)"
        elif [ "$k24_clones" -ne 0 ]; then
            bad "[K24]: rx_search is SPLIT at -O2 despite the noclone attribute ($(nm "$WORKDIR/k24.o" | grep -oE 'rx_search\.[a-z]+\.[0-9]+' | paste -sd, -)) — the partial-inlining regression is back; case (c)'s D12 floor will follow"
        else
            ok "[K24]: rx_search stays monolithic at -O2 under noclone, and the attribute-stripped control DOES split ($k24_ctl_clones clone(s)) — the guard is live, not vacuous"
        fi
    fi
else
    bad "[K24]: pcrec failed to compile '(alpha|beta|gamma|delta|epsilon)' --no-captures for the partial-inlining split check"
fi

# ---- the ABI-types block is BYTE-IDENTICAL across prefixes ---------------
# §1 of docs/spec/match_api.md states this as measured, and the D44/A-2 check
# above tests the CONSEQUENCE (two differently-prefixed headers compile in one
# TU) rather than the property itself — which a block that merely happened to
# be free of prefix-dependent CONTENT would also satisfy. This asserts the
# property directly, so an edit that leaks the prefix (or, since [M5-SEAM],
# the ENCODING) into the shared block fails here rather than at whatever
# distance the consequence first shows up.
#
# Four prefixes of different lengths and shapes, because a prefix leak that
# happened to produce equal-length text would survive a two-prefix
# comparison. The CONTROL is the whole file: it MUST differ across prefixes,
# or the extractor is returning nothing and this check is comparing two empty
# strings to each other.
abi_block() { awk '/^#ifndef PCREC_RX_ABI_H$/,/^#endif \/\* PCREC_RX_ABI_H \*\//' "$1"; }
abi_md5=""
abi_ok=1
abi_files=""
for pfx in rx foo z_9 verylongprefixname; do
    if ! "$PCREC" -p "$pfx" -o - -- 'a(b|c)+d' > "$WORKDIR/abi_$pfx.c" 2>/dev/null; then
        bad "ABI block identity: pcrec failed to compile the fixture under -p $pfx"
        abi_ok=0
        continue
    fi
    abi_files="$abi_files $WORKDIR/abi_$pfx.c"
    m="$(abi_block "$WORKDIR/abi_$pfx.c" | md5sum | cut -d' ' -f1)"
    b="$(abi_block "$WORKDIR/abi_$pfx.c" | wc -l)"
    if [ "$b" -lt 20 ]; then
        bad "ABI block identity: the extracted block under -p $pfx is $b lines — the extractor is not finding the guarded block, so any comparison below is vacuous"
        abi_ok=0
    elif [ -z "$abi_md5" ]; then
        abi_md5="$m"
    elif [ "$m" != "$abi_md5" ]; then
        bad "ABI block identity: the PCREC_RX_ABI_H block under -p $pfx differs from the -p rx one — something prefix-dependent (or encoding-dependent) leaked into the block every artifact in a TU shares, where only the FIRST copy survives the include guard"
        abi_ok=0
    fi
done
if [ "$abi_ok" -eq 1 ]; then
    # the control: whole files across prefixes must NOT be identical
    if [ "$(cat $abi_files | md5sum | cut -d' ' -f1)" \
         = "$(cat "$WORKDIR/abi_rx.c" "$WORKDIR/abi_rx.c" "$WORKDIR/abi_rx.c" "$WORKDIR/abi_rx.c" | md5sum | cut -d' ' -f1)" ]; then
        bad "ABI block identity: the four differently-prefixed WHOLE artifacts are identical too — --prefix is not reaching the emitted text at all, so the block's identity proves nothing"
    else
        ok "[M4.4/D44/A-2]: the PCREC_RX_ABI_H block is byte-identical across four prefixes (md5 $abi_md5) while the surrounding artifacts differ"
    fi
fi

# ---- [ABI-NS] universal constants unified under PCREC_*, no per-prefix alias
# D60 + addendum (docs/dev/decisions.md): the give-up code space
# (PCREC_ERR_STEPS/_FRAMES/_WORK/_FLOOR), PCREC_UNSET, the two new engine
# constants (PCREC_ENGINE_DFA/_VM, naming rx_info.engine's formerly
# number-only contract) and the nine D46 stamp bit VALUES
# (PCREC_VM_RUNG_*/PCREC_VM_STRAT_*/PCREC_VM_PRUNE_*) moved from PER-PREFIX
# spellings (<PREFIX>_ERR_STEPS etc.) into the shared PCREC_RX_ABI_H block,
# emitted ONCE and unprefixed. The deletion of the old spellings is the
# point of the change, not a side effect, so it is pinned directly: a future
# edit that re-introduces an aliased <PREFIX>_ERR_STEPS (say, for
# "backward compatibility") must fail here even though every other check in
# this file would stay green, since the old spelling would once again
# resolve to a valid macro.
if [ -f "$WORKDIR/abi_rx.c" ]; then
    # abi_rx.c is a captures-on 'a(b|c)+d' build (the fixture the ABI-block
    # loop above already produced), which selects the VM — the engine that
    # used to emit the per-prefix D46 bit constants this check also covers.
    new_names="PCREC_ERR_STEPS PCREC_ERR_FRAMES PCREC_ERR_WORK PCREC_ERR_FLOOR PCREC_UNSET PCREC_ENGINE_DFA PCREC_ENGINE_VM PCREC_VM_RUNG_CURSOR PCREC_VM_RUNG_FRAMES_BOUNDED PCREC_VM_RUNG_FRAMES_UNBOUNDED PCREC_VM_RUNG_REVDET PCREC_VM_RUNG_COUNTER PCREC_VM_STRAT_POSSESSIVE PCREC_VM_STRAT_BACKTRACKING PCREC_VM_PRUNE_CLAMPED PCREC_VM_PRUNE_UNCLAMPED"
    new_missing=""
    for n in $new_names; do
        c="$(grep -cE "^#define $n\\b" "$WORKDIR/abi_rx.c")"
        [ "$c" -eq 1 ] || new_missing="$new_missing $n(x$c)"
    done
    if [ -n "$new_missing" ]; then
        bad "[ABI-NS]: universal constant(s) not emitted exactly once in a VM artifact:$new_missing"
    else
        ok "[ABI-NS]: all 16 universal constants (give-up codes, UNSET, ENGINE_DFA/VM, nine D46 stamp bits) are emitted exactly once in a VM artifact"
    fi

    old_names="RX_ERR_STEPS RX_ERR_FRAMES RX_ERR_WORK RX_ERR_FLOOR RX_UNSET RX_VM_RUNG_CURSOR RX_VM_RUNG_FRAMES_BOUNDED RX_VM_RUNG_FRAMES_UNBOUNDED RX_VM_RUNG_REVDET RX_VM_RUNG_COUNTER RX_VM_STRAT_POSSESSIVE RX_VM_STRAT_BACKTRACKING RX_VM_PRUNE_CLAMPED RX_VM_PRUNE_UNCLAMPED"
    old_found=""
    for n in $old_names; do
        grep -qE "^#define $n\\b" "$WORKDIR/abi_rx.c" && old_found="$old_found $n"
    done
    if [ -n "$old_found" ]; then
        bad "[ABI-NS]: DELETED per-prefix spelling(s) still emitted (no alias, D60):$old_found"
    else
        ok "[ABI-NS]: the fourteen deleted per-prefix spellings (RX_ERR_*/RX_UNSET/RX_VM_RUNG_*/RX_VM_STRAT_*/RX_VM_PRUNE_*) do not appear anywhere in a VM artifact"
    fi
else
    bad "[ABI-NS]: no VM fixture (\$WORKDIR/abi_rx.c) available from the ABI-block loop above — cannot check the universal-constant migration"
fi

# A DFA-only ('--no-captures') artifact never had the D46 stamp bits at all
# (VM-artifacts-only, src/gen/emit_vm.c) but DOES now carry the give-up
# codes, PCREC_UNSET and the two engine constants unconditionally — the same
# "reserved but unreachable" precedent PCREC_ERR_STEPS already had before
# this lane, extended to the two new constants and the D46 bits (D60's own
# membership rule: names are part of the CONTRACT even where this artifact's
# engine cannot produce the value).
if "$PCREC" -p rx --no-captures -o - -- 'a(b|c)+d' > "$WORKDIR/abins_dfa.c" 2>/dev/null; then
    dfa_missing=""
    for n in PCREC_ERR_STEPS PCREC_ERR_FRAMES PCREC_ERR_WORK PCREC_ERR_FLOOR PCREC_UNSET PCREC_ENGINE_DFA PCREC_ENGINE_VM PCREC_VM_RUNG_CURSOR PCREC_VM_STRAT_POSSESSIVE PCREC_VM_PRUNE_CLAMPED; do
        c="$(grep -cE "^#define $n\\b" "$WORKDIR/abins_dfa.c")"
        [ "$c" -eq 1 ] || dfa_missing="$dfa_missing $n(x$c)"
    done
    if grep -qE '^#define RX_ERR_STEPS\b|^#define RX_UNSET\b' "$WORKDIR/abins_dfa.c"; then
        bad "[ABI-NS]: a --no-captures (DFA) artifact still carries a deleted per-prefix spelling"
    elif [ -n "$dfa_missing" ]; then
        bad "[ABI-NS]: a --no-captures (DFA) artifact is missing universal constant(s) it should carry unconditionally:$dfa_missing"
    else
        ok "[ABI-NS]: a DFA-only artifact carries every universal constant (give-up codes, UNSET, ENGINE_DFA/VM, sampled D46 bits) unconditionally, and none of the deleted per-prefix spellings"
    fi
else
    bad "[ABI-NS]: pcrec failed to compile 'a(b|c)+d' --no-captures for the DFA-side universal-constant check"
fi

# ---- [M5-SEAM] RESIDUAL ENTRIES ARE NEVER CALLED FROM THE ENGINE ----------
# docs/dev/plan.md [DD-12] (7), ruled in as a requirement by Frank: "NO
# encoding conditionals anywhere ... per-encoding inline-function headers are
# the WRONG seam for the HOT PATH and the RIGHT seam for the enumerable
# runtime-identity RESIDUE", ENFORCED BY CHECK, NOT CONVENTION — "a
# codegen-structural check that no hot-loop label calls into the encoding
# header (allowlist of named residual sites)". This is that check.
#
# WHY IT CANNOT BE A BEHAVIOUR TEST. Under the byte backend a residual entry
# is the identity (`<prefix>_next_pos` returns `pos + 1`), so an engine that
# advanced through it would MATCH IDENTICALLY and every oracle in this tree
# would stay green — while the artifact had acquired exactly the cross-seam
# call DD-12 forbids, and the UTF-8 backend would then silently change the
# hot path's shape and speed. Same charter as this file's header: a property
# no correctness test can see.
#
# THE POPULATION IS DERIVED, NOT TYPED. The residual entry NAMES are read out
# of the artifact itself (every residual declaration is preceded by the
# backend's own "ENCODING RESIDUAL entry" comment line), so a backend that
# adds a second entry is covered the day it lands rather than the day someone
# remembers to extend a list here. Finding NO residual entry is a FAILURE,
# not a pass: that is the empty-population shape this directory's CLAUDE.md
# exists about.
#
# ALLOWLIST. A residual name may appear (a) in a comment, (b) as its own
# declaration, and (c) inside its OWN definition. Anywhere else inside a
# file-scope function body is a violation — which for a generated artifact
# means an engine body, since those are the only other functions in it.
#
# SABOTAGE: tests/mech/sabotages/S68_residual_in_hot_loop.sh, which makes
# emit_dfa.c's bitmap prefilter skip loop advance via `<prefix>_next_pos`.
# That sabotage changes NO answer, which is the point.

# residual_names <file> — the residual entry names this artifact declares.
residual_names() {
    awk '
        /ENCODING RESIDUAL entry/ { want = 1; next }
        want && /^[a-z_].*\(.*\);[[:space:]]*$/ {
            line = $0
            sub(/\(.*/, "", line)
            sub(/^.*[^A-Za-z0-9_]/, "", line)
            print line
            want = 0
        }
    ' "$1" | sort -u
}

# calls_in_bodies <file> <name> — lines referencing <name> inside a
# file-scope function body OTHER than <name>'s own definition and the
# artifact's `--emit-main` `main()`.
#
# `main` is ALLOWLISTED because it is a CALLER, not an engine: DD-12 (7)'s
# rule is about the artifact's matching machinery depending on the encoding,
# and a demo `main()` doing find-all through `<prefix>_next_pos` would be the
# documented caller protocol rather than a violation of it. It does not call
# it today; the allowlist entry is here so that a later `--emit-main` that
# does is not reported as a derailment it is not.
calls_in_bodies() {
    awk -v want="$2" '
        # a file-scope definition head: `<type> <name>(...)` at column 0,
        # followed by `{` at column 0. Track the name; the emitted artifact
        # puts every definition in exactly this shape.
        /^[A-Za-z_].*\(/ && !/;[[:space:]]*$/ { head = $0; next }
        /^\{/ && head != "" {
            fname = head
            sub(/\(.*/, "", fname)
            sub(/^.*[^A-Za-z0-9_]/, "", fname)
            inbody = 1
            head = ""
            next
        }
        /^\}/ { inbody = 0; fname = ""; next }
        inbody && fname != want && fname != "main" && index($0, want) {
            print FILENAME ":" FNR ": " $0
        }
    ' "$1"
}

resid_total=0
resid_bad=0
resid_files=0
while IFS=$'\t' read -r nm pat extra; do
    [ -n "$nm" ] || continue
    [ "$extra" = "-" ] && extra=""
    # BOTH artifact forms: split (.h carries the declaration) and
    # self-contained (the .c carries declaration AND definition).
    # shellcheck disable=SC2086
    if ! "$PCREC" -p rx $extra -o "$WORKDIR/$nm.c" -- "$pat" >/dev/null 2>&1 \
       || ! "$PCREC" -p rx $extra -o - -- "$pat" > "$WORKDIR/${nm}_sc.c" 2>/dev/null; then
        bad "[M5-SEAM] residual: pcrec failed to compile the fixture '$pat' ($extra)"
        continue
    fi
    for f in "$WORKDIR/$nm.h" "$WORKDIR/${nm}_sc.c"; do
        names="$(residual_names "$f")"
        [ -n "$names" ] || continue
        resid_files=$((resid_files + 1))
        for rn in $names; do
            resid_total=$((resid_total + 1))
            hits="$(calls_in_bodies "$WORKDIR/$nm.c" "$rn"; calls_in_bodies "$WORKDIR/${nm}_sc.c" "$rn")"
            if [ -n "$hits" ]; then
                resid_bad=$((resid_bad + 1))
                bad "[M5-SEAM/DD-12(7)] '$rn' is referenced from an engine body in the '$pat' artifact — a hot path calling into the encoding residual is the derailment DD-12 (7) forbids, and it changes no answer under the byte backend, so nothing else in this tree will tell you: $(printf '%s' "$hits" | head -2 | tr '\n' ' ')"
            fi
        done
    done
    # TAB-separated: name, pattern, extra pcrec args ('-' for none). The
    # separator is a TAB precisely because every other candidate ('|', ',')
    # is regex syntax the fixture patterns need.
done <<EOF
residmemchr	a(b|c)+d	--no-captures
residbitmap	[ab]c[de]	--no-captures
residanchor	^ab(c|d)	--no-captures
residvm	a(b|c)+d	-
residvmonly	(x)(a|bc)+d	--engine=vm
residmain	a(b|c)+d	--emit-main
EOF
if [ "$resid_files" -eq 0 ] || [ "$resid_total" -eq 0 ]; then
    bad "[M5-SEAM/DD-12(7)]: NO residual entry was found in any emitted artifact — this check has no population and cannot certify anything. Either the residual embed (src/gen/enc/) stopped emitting, or its 'ENCODING RESIDUAL entry' marker moved and this check's extractor went blind"
elif [ "$resid_bad" -eq 0 ]; then
    ok "[M5-SEAM/DD-12(7)]: $resid_total residual entr(y|ies) across $resid_files emitted surfaces, none referenced from any engine body"
fi

# ---- [K27] the emitted prefilter on the contract's legal NULL subject -----
# docs/spec/match_api.md §3.1: `s` may be NULL when `n == 0`. The emitted
# unanchored search body used to reach `memchr(s + pos, c, n - pos)` with
# s == NULL, pos == 0, n == 0 on exactly that input — technical UB in EMITTED
# code, which a user compiling a generated matcher under their own
# -fsanitize=undefined sees pcrec's name on (docs/dev/known_issues.md K27).
#
# This check COMPILES AND RUNS the artifact on that input. Under `make test`
# it pins the answers; under `make ubsan`/`make asan` (which run this script
# with an instrumented $GENCFLAGS and -fno-sanitize-recover) the RUN is the
# regression — that is why K27 was invisible to the battery before: the
# corpus never passes s == NULL, so the instrumented axis had nothing to see.
# The fixture pattern is chosen to take the single-escape-byte memchr arm,
# which is the arm that held the defect.
if "$PCREC" -p k27 --no-captures -o - -- 'abc' > "$WORKDIR/k27null.c" 2>/dev/null; then
    if ! grep -q 'memchr' "$WORKDIR/k27null.c"; then
        bad "[K27]: the fixture artifact carries no memchr prefilter at all — this check has lost the arm it exists to cover"
    else
        cat > "$WORKDIR/k27null_drv.c" <<'K27EOF'
#include <stdio.h>
#include "k27null.c"
int main(void)
{
    printf("%d %zu\n", k27_search(NULL, 0, 0, NULL), k27_next_pos(NULL, 0, 0));
    return 0;
}
K27EOF
        if ! gen_cc "K27 NULL-subject driver" "$CC" $GENCFLAGS -I"$WORKDIR" \
                    -o "$WORKDIR/k27null_drv" "$WORKDIR/k27null_drv.c"; then
            bad "[K27]: the NULL-subject driver failed to compile: $(printf '%s' "$GEN_CC_LOG" | head -3 | tr '\n' ' ')"
        else
            k27out="$(gen_run "K27 NULL subject" "$WORKDIR/k27null_drv" 2>&1)"; k27rc=$?
            if [ "$k27rc" -ne 0 ]; then
                bad "[K27]: <prefix>_search(NULL, 0, 0, NULL) did not run cleanly (status $k27rc): $(printf '%s' "$k27out" | head -3 | tr '\n' ' ')"
            elif [ "$k27out" = "0 1" ]; then
                ok "[K27]: the legal (s == NULL, n == 0) subject runs clean through the memchr prefilter and the residual entry (search 0, next_pos 1)"
            else
                bad "[K27]: NULL-subject probe answered '$k27out', want '0 1' (search must report no-match; next_pos must not read s)"
            fi
        fi
    fi
else
    bad "[K27]: pcrec failed to compile the NULL-subject fixture 'abc'"
fi

# ---- [M6.2-WORDB] the three structural rules `\b` lands with ---------------
#
# assertions_design.md §3.6.2, §3.8.3.1 and §7.2 each state a rule that NO
# CORRECTNESS TEST IN THIS TREE CAN SEE, which is this file's whole charter.
# Two of the three are memory-safety rules whose violation is UB rather than a
# wrong answer, and one is a two-sources-of-truth rule whose violation changes
# nothing until the day the two sources disagree.
#
# THE FIXTURE is `.*\b.*`, and the choice was CORRECTED by running the
# sabotage rather than by reasoning about it. It has to carry every emitted
# site at once — a class-indexed accept in BOTH machines (`facc2`/`racc2`),
# mechanism 4's seed in BOTH (`fseed`/`rseed`), and live forward AND reverse
# SKIP states, since the skip is what rule 2 is about.
#
# THAT IS NOT ENOUGH, and the first fixture (`\bx.*y\b`) had all of it and
# still made rule 2 VACUOUS. The blind writer rule 2 forbids is emitted under
# `if (!views && rd->st[K].accept)` — a COMPILE-TIME condition with TWO
# conjuncts. Removing the `!views` guard (sabotage S72) emits nothing at all
# unless the reverse skip state ALSO ACCEPTS, and `\bx.*y\b`'s does not. S72
# came back UNDETECTED on the whole suite: 0 codegen failures, 0 corpus
# failures, a check with no measured failing direction — the exact shape this
# directory's charter is about, found the only way it can be found.
#
# `.*\b.*`'s reverse skip state DOES accept, and the check now ASSERTS that
# rather than assuming it: `rx_racc[K]` is read out of the artifact and
# required to be 1, so a future fixture that quietly loses the property fails
# loudly instead of passing vacuously.
WB_PAT='.*\b.*'
if gen wordb "$WB_PAT" --features all; then
    wbb="$WORKDIR/wordb.body"

    # --- rule 1 (§3.6.2): NEVER index an accept table at `pos == n` ---------
    #
    # Two axes select an accept bit: the VIEW axis by position, the CLASS axis
    # by the next byte. At `pos == n` there IS no next byte, so the accept is
    # the view's SCALAR one. Indexing the wide table there would ask what the
    # accept is when the next byte is "whatever byte sits in that equivalence
    # class", which is meaningless — and reading `s[pos]` to get the class is
    # an out-of-bounds read in EMITTED code, K27's class.
    #
    # CHECKED TWO WAYS, because either alone is weak. (a) every `facc2` read
    # is indexed by the `cl` LOCAL and never by a subject read spelled inline,
    # so there is one named thing to guard rather than an expression to parse;
    # (b) the `pos >= n` guard, with the scalar accept inside it, appears
    # BEFORE the first `facc2` read in the body. (b) alone would pass if the
    # guard were present but the read moved above it in a later edit that also
    # moved the guard; (a) alone would pass if `cl` were computed at `pos ==
    # n`.
    # The table's own DECLARATION line matches the same grep and is not a
    # read, so it is dropped first -- an exclusion worth spelling out, since
    # forgetting it is a check that fails on its own subject rather than on a
    # defect.
    grep 'rx_facc2\[' "$wbb" | grep -v '^ *static const' > "$WORKDIR/f2reads"
    f2lines=$(grep -c . "$WORKDIR/f2reads" || true)
    f2bad=$(grep -cv 'rx_facc2\[[a-z]* \* [0-9]* + cl\]' "$WORKDIR/f2reads" || true)
    guard_ln=$(grep -n '^        if (pos >= n) {$' "$wbb" | head -1 | cut -d: -f1)
    first_f2=$(grep -n 'rx_facc2\[' "$wbb" | grep -v ':[[:space:]]*static const' \
               | head -1 | cut -d: -f1)
    scalar_in_guard=$(sed -n "${guard_ln:-0},$((${guard_ln:-0} + 2))p" "$wbb" \
                      | grep -c 'rx_facc\[' || true)
    if [ "$f2lines" -lt 1 ]; then
        bad "[M6.2-WORDB rule 1]: '$WB_PAT' emitted no class-indexed accept at all — the fixture no longer exercises §3.6, so this rule has no population"
    elif [ "$f2bad" -ne 0 ]; then
        bad "[M6.2-WORDB rule 1]: $f2bad of $f2lines class-indexed accept reads are not indexed by the 'cl' local; a read that computes its own class is a read this check cannot prove is guarded:"
        grep -v 'rx_facc2\[[a-z]* \* [0-9]* + cl\]' "$WORKDIR/f2reads" >&2
    elif [ -z "$guard_ln" ] || [ -z "$first_f2" ] || [ "$guard_ln" -ge "$first_f2" ]; then
        bad "[M6.2-WORDB rule 1]: the 'if (pos >= n)' guard is at line ${guard_ln:-MISSING} and the first class-indexed accept at line ${first_f2:-MISSING} — the guard must come FIRST, or the emitted loop reads s[pos] at pos == n"
    elif [ "$scalar_in_guard" -lt 1 ]; then
        bad "[M6.2-WORDB rule 1]: the 'pos >= n' arm does not read the SCALAR accept table, so the end-of-subject accept is being dropped rather than taken from the view (§3.6.2)"
    else
        ok "[M6.2-WORDB rule 1] (§3.6.2): all $f2lines class-indexed accept reads go through the guarded 'cl' local, and the 'pos >= n' arm takes the SCALAR accept before any of them — no accept table is indexed at pos == n"
    fi

    # --- rule 2 (§3.8.3.1): every `sfound` writer at the reverse boundary ---
    #
    # THE INVARIANT: no `sfound` is recorded at `pp == startpos` except through
    # the context-indexed accept. The design states it as an invariant rather
    # than a patch for a specific reason — there is MORE THAN ONE WRITER. The
    # loop-top one is obvious; the reverse SKIP's is not, and it is worse than
    # it looks: `emit_dfa.c`'s `if (!eol && rd->st[K].accept)` is a
    # COMPILE-TIME condition on whether to EMIT the line, so what would land
    # in the artifact is a BARE, UNCONDITIONAL `sfound = pp;` inside the skip
    # block with no runtime test to fail.
    #
    # So the check enumerates EVERY `sfound` assignment in the body and
    # requires each to be conditioned on an accept read — on its own line or
    # on the one above it, which is where the boundary arm's two-line ternary
    # puts it. A bare assignment fails no matter which writer emitted it,
    # which is what makes this an invariant check rather than a check of the
    # one site somebody remembered.
    #
    # THE FIXTURE HAS A LIVE REVERSE SKIP (`rx_rs<K>`), asserted below: without
    # one this rule would pass on an artifact that has no second writer to get
    # wrong.
    rskips=$(grep -c 'rx_rs[0-9]*\[s\[pp - 1\]\]' "$wbb" || true)
    # THE NON-VACUITY ASSERTION. Read the reverse skip state's index out of
    # its own emitted loop, then that state's SCALAR accept out of the
    # artifact's `rx_racc[]`. Both come from the artifact; neither is typed
    # here, so a fixture change cannot silently drop the property.
    rskip_k=$(grep -oE 'rx_rs[0-9]+\[s\[pp - 1\]\]' "$wbb" | head -1 \
              | grep -oE '[0-9]+' | head -1)
    rskip_acc=$(sed -n '/static const unsigned char rx_racc\[/,/};/p' "$wbb" \
                | tr -d ' \n' | sed 's/.*={//; s/};.*//' \
                | cut -d, -f$((${rskip_k:-0} + 1)))
    # `size_t sfound = (size_t)-1;` is the DECLARATION, not a record of a
    # match start, and is excluded by name rather than by pattern-matching
    # around it.
    sf_total=$(grep 'sfound = ' "$wbb" | grep -cv 'size_t sfound = ' || true)
    sf_bad=$(awk '
        /sfound = / && !/size_t sfound = / {
            if ($0 !~ /racc/ && prev !~ /racc/) { print NR": "$0; n++ }
        }
        { if ($0 !~ /^[[:space:]]*$/) prev = $0 }
        END { exit 0 }
    ' "$wbb")
    nsf_bad=$(printf '%s' "$sf_bad" | grep -c . || true)
    if [ "$rskips" -lt 1 ]; then
        bad "[M6.2-WORDB rule 2]: '$WB_PAT' emitted no reverse skip loop, so the second, blind sfound writer §3.8.3.1 is about cannot be present — this rule would pass vacuously"
    elif [ "${rskip_acc:-0}" != "1" ]; then
        bad "[M6.2-WORDB rule 2]: '$WB_PAT's reverse skip state $rskip_k does NOT accept (rx_racc[$rskip_k] = ${rskip_acc:-unread}), so the blind writer is gated off by its OTHER compile-time conjunct and no sabotage of the guard can emit it. This rule would pass vacuously — which is exactly how sabotage S72 first came back UNDETECTED. Pick a fixture whose reverse skip state accepts."
    elif [ "$sf_total" -lt 2 ]; then
        bad "[M6.2-WORDB rule 2]: only $sf_total sfound writers in the body; the boundary arm and the interior read are both expected"
    elif [ "$nsf_bad" -ne 0 ]; then
        bad "[M6.2-WORDB rule 2]: $nsf_bad sfound writer(s) are not conditioned on an accept read. A bare 'sfound = pp;' at pp == startpos records a match start whose leading \\b/\\B was never evaluated against s[startpos-1]:"
        printf '%s\n' "$sf_bad" >&2
    else
        ok "[M6.2-WORDB rule 2] (§3.8.3.1): all $sf_total sfound writers are conditioned on an accept read, with $rskips reverse skip loop(s) present AND skip state $rskip_k ACCEPTING (rx_racc[$rskip_k] = 1) — so the second, blind writer really would be emitted here if its guard were removed"
    fi

    # --- rule 2b: the boundary accept is ATTACHED TO THE BREAK (R30 N9) -----
    #
    # The reverse loop has TWO exits — the boundary and the dead state — and
    # an accept placed after the loop would run on BOTH: on the dead-state
    # exit it would record `sfound` at a position the walk never reached (a
    # WRONG ANSWER, worse than a lost match) and index the accept table with a
    # NEGATIVE state (out-of-bounds, K27's class). So the context-indexed
    # boundary read must sit INSIDE the `pp <= startpos` arm, and there must
    # be no accept read after the loop closes.
    b_arm=$(grep -n 'if (pp <= startpos) {' "$wbb" | head -1 | cut -d: -f1)
    b_read=$(grep -n 'rx_rcls\[s\[startpos - 1\]\]' "$wbb" | head -1 | cut -d: -f1)
    b_dead=$(grep -n 'if (rst < 0) break;' "$wbb" | head -1 | cut -d: -f1)
    if [ -z "$b_arm" ] || [ -z "$b_read" ] || [ -z "$b_dead" ]; then
        bad "[M6.2-WORDB rule 2b]: could not locate the boundary arm (${b_arm:-MISSING}), its context read (${b_read:-MISSING}) or the dead-state exit (${b_dead:-MISSING}) in the emitted reverse loop"
    elif [ "$b_read" -le "$b_arm" ] || [ "$b_read" -ge "$b_dead" ]; then
        bad "[M6.2-WORDB rule 2b]: the s[startpos-1] context read is at line $b_read, outside the 'pp <= startpos' arm (line $b_arm) and its window before the dead-state exit (line $b_dead). R30 N9: an epilogue below the loop runs on the dead-state exit too"
    else
        ok "[M6.2-WORDB rule 2b] (R30 N9): the reverse boundary's context-indexed accept is ATTACHED to the 'pp <= startpos' break (line $b_read, inside the arm at $b_arm), not peeled below a loop whose other exit is a dead state at $b_dead"
    fi
fi

# --- rule 3 (§7.2 item 3): ONE word-set spelling per artifact --------------
#
# "Whatever `\w` means, `\b` must agree with", and the only way to guarantee
# that is ONE definition with two readers. A second copy of the word bitmap in
# an artifact would change no answer on the day it landed and would drift on
# some later day when one copy is regenerated — this project's recorded
# check-design failure in its purest form.
#
# The DFA path has no word table at all (the set is folded into the byte
# equivalence class map), so the population is the VM artifact, where `\w` and
# `\b` both go through the class pool. `(\b\w+\b)` uses both in one pattern,
# and the pool interns by CONTENT, so agreement means literally one table.
if "$PCREC" -p rx --features all --engine=vm -o "$WORKDIR/wordset.c" \
        -- '(\b\w+\b)' >/dev/null 2>&1; then
    # The word set is 63 members: [0-9A-Za-z_]. Its first eight bitmap bytes
    # are unmistakable and are what a duplicate would repeat.
    nwordtab=$(grep -c '  0,   0,   0,   0,   0,   0, 255,   3,' "$WORKDIR/wordset.c" || true)
    # THE DISCRIMINATOR, and its first two drafts were both blind — see the
    # note above the third assertion below. Extract every byte-set MEMBERSHIP
    # TEST in the artifact (`vm_cls_test`'s three shapes: bitmap read, unsigned
    # range subtract, singleton compare), normalise away the subject-byte
    # expression each is applied to, and count the DISTINCT ones. `(\b\w+\b)`
    # asks the same question — is this byte a word character — in three places,
    # so a correct artifact has exactly ONE distinct test.
    ndistinct=$(grep -oE '\(rx_k[0-9]+\[\(s\[[^]]*\]\) >> 3\] >> \(\(s\[[^]]*\]\) & 7\)\) & 1|\(unsigned\)\(s\[[^]]*\] - [0-9]+\) <= [0-9]+u|s\[[^]]*\] == [0-9]+' \
                "$WORKDIR/wordset.c" | sed 's/s\[[^]]*\]/B/g' | sort -u | grep -c . || true)
    #
    # TWO ASSERTIONS, and the SECOND one took three tries — each earlier draft
    # was measured blind by running sabotage S75 rather than by reasoning:
    #
    #   draft 1: "exactly one copy of the word bitmap". Catches a literal
    #            duplicate. Does NOT catch `\b` reading a DIFFERENT set, which
    #            leaves exactly one word bitmap (from `\w`) and passes.
    #   draft 2: "exactly one class TABLE in the artifact". Does not catch it
    #            either, because a set that happens to be a contiguous RANGE
    #            (the digit set is [0-9]) compiles to a subtract-and-compare
    #            and emits no table at all — so the count stays 1.
    #   draft 3: exactly one distinct MEMBERSHIP TEST, normalised over the
    #            byte expression it is applied to. That is the property the
    #            rule is actually about — `\b` and `\w` asking ONE question —
    #            and it is blind to which of `vm_cls_test`'s three shapes the
    #            set compiles into.
    if [ "$nwordtab" -lt 1 ]; then
        bad "[M6.2-WORDB rule 3]: '(\\b\\w+\\b)' emitted no word bitmap at all — the fixture no longer exercises §7.2, so this rule has no population"
    elif [ "$nwordtab" -ne 1 ]; then
        bad "[M6.2-WORDB rule 3]: $nwordtab copies of the word bitmap in one artifact ($nk class tables total). \\b and \\w must READ ONE TABLE (§7.2 item 3); two copies agree today and drift the day one is regenerated"
    elif [ "$ndistinct" -lt 1 ]; then
        bad "[M6.2-WORDB rule 3]: no byte-set membership test found in '(\\b\\w+\\b)'s artifact at all — the extractor has stopped matching the emitted shapes, so this assertion is measuring nothing"
    elif [ "$ndistinct" -ne 1 ]; then
        bad "[M6.2-WORDB rule 3]: $ndistinct DISTINCT byte-set membership tests in '(\\b\\w+\\b)'s artifact, want 1. The pattern asks 'is this byte a word character' in three places; more than one distinct test means \\b resolved to a DIFFERENT set than \\w — §7.2 item 3's failure in its other direction: whatever \\w means, \\b must agree with"
    else
        ok "[M6.2-WORDB rule 3] (§7.2 item 3): '(\\b\\w+\\b)' emits exactly ONE word bitmap and exactly ONE distinct membership test — \\b and \\w read the same pcrec_cls_word_esc through the same pool, in both directions (no duplicate, and no divergence)"
    fi
else
    bad "[M6.2-WORDB rule 3]: pcrec failed to compile the one-word-set fixture '(\\b\\w+\\b)'"
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
