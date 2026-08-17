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
        bad "[M4.4]: RX_NCAPS ($ncaps_val) > 1 but rx_info.engine ($engine_val) is not ENGM_VM (2) — RX_NCAPS>1 must imply the VM engine (D42.2)"
    else
        ok "[M4.4/M4.5b]: RX_NCAPS ($ncaps_val) > 1 => VM structural check holds — NON-VACUOUSLY since [M4.5b] (this cell had no population at all while the DFA was the only emitter; tests/codegen/run_vm_identity.sh runs it over the whole corpus)"
    fi
else
    bad "[M4.4]: pcrec failed to compile 'a(b|c)+d' for the structural NCAPS/engine checks"
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

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "codegen: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
