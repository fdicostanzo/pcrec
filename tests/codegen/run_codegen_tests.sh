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
# tool the moment there is more than one: `rx_forward_stay[0-9]+\[256\]` would then be
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
    # The `!~ ";[ \t]*$"` guard matches the DEFINITION, not the DECLARATION.
    # A self-contained artifact declares the entry near the top and defines it
    # far below, and both lines start `int <fn>(` -- so without the guard this
    # captured from the DECLARATION and swept up everything in between.
    # [M6-READ] exposed it: the orientation block sits in that window and
    # quotes the PATTERN, so the OS-1 folding checks (which compare two
    # patterns compiling to the same engine) began reporting a difference that
    # is not in the engine at all. The extractor was always wrong; nothing
    # pattern-dependent had ever landed between the two lines before.
    awk -v fn="$2" '
        $0 ~ "^(static )?int " fn "\\(" && $0 !~ ";[ \t]*$" { inside = 1 }
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
    if grep -qE 'rx_(forward|reverse)_stay[0-9]+\[256\]' "$WORKDIR/skip.body"; then
        ok "skip states: '.*=.*' emits a self-loop skip table"
    else
        bad "skip states: '.*=.*' emitted NO skip table (pick_skip_states disabled/broken?)"
    fi
    if grep -qE 'while \(scan_position < subject_length && rx_forward_stay[0-9]+\[subject\[scan_position\]\]\) scan_position\+\+;' "$WORKDIR/skip.body"; then
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
    entries=$(grep -oE 'rx_forward_next_state\[[0-9]+\]' "$WORKDIR/minim.body" | grep -oE '[0-9]+' | head -1)
    if [ -z "${entries:-}" ]; then
        bad "minimization: could not find rx_forward_next_state[] table in generated code"
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
        ventries=$(grep -oE 'rx_forward_next_state\[[0-9]+\]' "$WORKDIR/minimvm.body" | grep -oE '[0-9]+' | head -1)
        if [ -z "${ventries:-}" ]; then
            bad "minimization/prefilter: no rx_forward_next_state[] table inside the VM artifact's prefilter"
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
    if grep -q 'rx_forward_eol_view\[' "$WORKDIR/dollar.body"; then
        ok "M2.7: 'a*b\$' uses the unanchored engine with EOL variants"
    else
        bad "M2.7: 'a*b\$' did NOT use the unanchored engine (reverted to O(n^2) attempts?)"
    fi
    if grep -q 'for (start = search_from' "$WORKDIR/dollar.body"; then
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
    if grep -qE 'rx_(forward|reverse)_stay[0-9]+\[256\]' "$WORKDIR/dense.body"; then
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
    acc_line=$(grep -nE 'if \(rx_forward_is_accepting\[forward_state\]\) last_accept_position = scan_position;' "$WORKDIR/ordnoeol.body" | head -1 | cut -d: -f1)
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
    if grep -qE 'rx_forward_stay[0-9]+\[256\]' "$WORKDIR/eolskip.body"; then
        ok "M2.12: '.*=.*\$' emits a skip table on the EOL path"
    else
        bad "M2.12: '.*=.*\$' emitted NO skip table (EOL path lost scan avoidance again?)"
    fi
    # bounded at n-1, never n: a state may accept at an EOL position
    if grep -qE 'while \(scan_position \+ 1 < subject_length && rx_forward_stay[0-9]+\[subject\[scan_position\]\]\) scan_position\+\+;' "$WORKDIR/eolskip.body"; then
        ok "M2.12: EOL forward skip loop is bounded at n-1"
    else
        bad "M2.12: EOL forward skip loop missing or not bounded at n-1"
    fi
    if grep -qE 'reverse_state == [0-9]+ && rewind_position \+ 1 < subject_length' "$WORKDIR/eolskip.body"; then
        ok "M2.12: EOL reverse skip loop carries the pp+1<n entry guard"
    else
        bad "M2.12: EOL reverse skip loop missing its pp+1<n entry guard"
    fi
    # ORDER MATTERS, and getting it wrong is what the first M2.12 attempt did:
    # a skip landing on n-1 must not consume that byte before the EOL view of
    # it has been taken. So the accept evaluation must come AFTER the skips.
    skip_line=$(grep -nE 'while \(scan_position \+ 1 < subject_length && rx_forward_stay[0-9]+' "$WORKDIR/eolskip.body" | tail -1 | cut -d: -f1)
    acc_line=$(grep -nE 'if \(rx_forward_is_accepting\[forward_view_state\]\) last_accept_position = scan_position;' "$WORKDIR/eolskip.body" | head -1 | cut -d: -f1)
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
    if grep -qE 'memchr\(subject \+ scan_position, [0-9]+, subject_length - 1 - scan_position\)' "$WORKDIR/eolpre.body"; then
        ok "M2.12: EOL memchr is bounded at n-1"
    else
        bad "M2.12: EOL memchr not bounded at n-1"
    fi
fi

# ^ patterns legitimately stay on the attempt engine (documented limitation)
if gen caret '^a|b'; then
    if grep -q 'for (start = search_from' "$WORKDIR/caret.body"; then
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
    if grep -q '^int rx_search(const unsigned char \*subject, size_t subject_length, size_t search_from, ptrdiff_t (\*capture_spans)\[2\])$' "$WORKDIR/casehot.body"; then
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
    if grep -qE 'rx_forward_stay[0-9]+\[256\]' "$WORKDIR/multi.c"; then
        if body "$WORKDIR/multi.c" rx_search "$WORKDIR/multi.a.body" \
        && body "$WORKDIR/multi.c" rx_search_b "$WORKDIR/multi.b.body"; then
            if grep -qE 'rx_forward_stay[0-9]+\[256\]' "$WORKDIR/multi.a.body"; then
                ok "OS-0b: scoped grep finds the skip table in the engine that has one"
            else
                bad "OS-0b: scoped grep MISSED the skip table in '.*=.*' (body() extracting nothing?)"
            fi
            if grep -qE 'rx_forward_stay[0-9]+\[256\]' "$WORKDIR/multi.b.body"; then
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
    # artifact emits five static functions (rx_match_anchored, rx_work_init,
    # rx_unwind, rx_report_captures, rx_prefilter) and its whole mutable working set is
    # a LOCAL of the search entry, which is exactly what D19 asks for.
    #
    # The discriminator is C's declarator syntax, not a name list: a function
    # declarator has `(` with no `=`, `;` or `[` before it. So
    # `static void rx_unwind(rx_run_state *w)` is excluded and
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
    new_names="PCREC_ERR_STEPS PCREC_ERR_FRAMES PCREC_ERR_WORK PCREC_ERR_RECURSE PCREC_ERR_FLOOR PCREC_ERR_INTERNAL PCREC_UNSET PCREC_ENGINE_DFA PCREC_ENGINE_VM PCREC_VM_RUNG_CURSOR PCREC_VM_RUNG_FRAMES_BOUNDED PCREC_VM_RUNG_FRAMES_UNBOUNDED PCREC_VM_RUNG_REVDET PCREC_VM_RUNG_COUNTER PCREC_VM_STRAT_POSSESSIVE PCREC_VM_STRAT_BACKTRACKING PCREC_VM_PRUNE_CLAMPED PCREC_VM_PRUNE_UNCLAMPED"
    # [DD-14 wave A, D71 item 1]: PCREC_ERR_RECURSE joins the universal
    # give-up code space (reserved, no producer this wave) and the count
    # below moves 16 -> 17. [DD-14 wave A commit 2]: PCREC_ERR_INTERNAL
    # (below the floor, NOT a give-up, but the SAME shared unprefixed
    # block for the SAME "one contract fact, one spelling" reason) joins
    # too, 17 -> 18.
    new_missing=""
    for n in $new_names; do
        c="$(grep -cE "^#define $n\\b" "$WORKDIR/abi_rx.c")"
        [ "$c" -eq 1 ] || new_missing="$new_missing $n(x$c)"
    done
    if [ -n "$new_missing" ]; then
        bad "[ABI-NS]: universal constant(s) not emitted exactly once in a VM artifact:$new_missing"
    else
        ok "[ABI-NS]: all 18 universal constants (give-up codes incl. PCREC_ERR_RECURSE, the below-floor PCREC_ERR_INTERNAL, UNSET, ENGINE_DFA/VM, nine D46 stamp bits) are emitted exactly once in a VM artifact"
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
    for n in PCREC_ERR_STEPS PCREC_ERR_FRAMES PCREC_ERR_WORK PCREC_ERR_RECURSE PCREC_ERR_FLOOR PCREC_ERR_INTERNAL PCREC_UNSET PCREC_ENGINE_DFA PCREC_ENGINE_VM PCREC_VM_RUNG_CURSOR PCREC_VM_STRAT_POSSESSIVE PCREC_VM_PRUNE_CLAMPED; do
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

# ---- [M5-SEAM] EVERY RESIDUAL ENTRY IS CALLED EXACTLY AS DECLARED ---------
# docs/dev/plan.md [DD-12] (7), ruled in as a requirement by Frank: "NO
# encoding conditionals anywhere ... per-encoding inline-function headers are
# the WRONG seam for the HOT PATH and the RIGHT seam for the enumerable
# runtime-identity RESIDUE", ENFORCED BY CHECK, NOT CONVENTION — "a
# codegen-structural check that no hot-loop label calls into the encoding
# header (allowlist of named residual sites)". This is that check.
#
# WHY IT CANNOT BE A BEHAVIOUR TEST. Under the byte backend a residual entry
# is the identity or near it (`<prefix>_next_pos` returns `pos + 1`; the
# backreference compare is a memcmp), so an engine that advanced through the
# first, or INLINED the second, would MATCH IDENTICALLY and every oracle in
# this tree would stay green — while the artifact had acquired exactly the
# cross-seam coupling DD-12 (7) forbids, or lost the seam routing D58 scope
# item 3 requires. Same charter as this file's header: a property no
# correctness test can see.
#
# [M6.5.2] THE CHECK CHANGES SHAPE, because the seam gained its SECOND and
# THIRD entries and they are not like the first.
#
# [M6.6.2 wave D] THE FOURTH ENTRY, `<prefix>_back_step`, NEEDED NO CHANGE TO
# THE MECHANISM AT ALL — only fixture rows and a second exact-count guard,
# which is lookaround_design.md §4.4's own prediction and §12 P-1's falsifiable
# form of it. A lookbehind steps back `k` CHARACTERS, which is the one step in
# §3.4's shape whose answer depends on the encoding; inlining it as
# `scan_position - k` changes NO ANSWER under the byte backend and is silently
# wrong under any other, so the fixture-declared per-site count below is the
# only instrument that can see it (sabotage row S133, S109's shape one
# construct over).
#
# `<prefix>_next_pos` has no business anywhere inside the matcher:
# unanchoredness is the automaton's own self-loop, so there is no external
# advance for an engine to route through. A BACKREFERENCE COMPARE has no
# automaton representation whatsoever — forbidding the call forbids the
# construct. So "never called from an engine body" stops being the rule and
# becomes the DECLARED COUNT ZERO case of one:
#
#     the number of CALL SITES of <prefix>_<entry> inside file-scope function
#     bodies other than the entry's own definition and main() must EXACTLY
#     equal the count the FIXTURE TABLE declares.
#
# THE EXPECTATION COMES FROM THE TEST, NOT FROM THE ARTIFACT, and that is
# R32 E7/C2's whole finding about the first draft of this change. A check whose
# population is read out of the artifact's own residual declarations goes GREEN
# exactly when the thing it guards is broken: an emitter that inlines the
# compare AND drops the entry from the artifact's mask leaves nothing to
# assert, and :1013's global empty-population guard does not notice, because
# `next_pos` is unconditional and keeps it satisfied.
#
# AND THE COUNT IS A DECLARED INTEGER, NOT A COUNT OF ANYTHING. Deriving it by
# scanning the fixture's PATTERN for `\<digit>` would be a SECOND
# IMPLEMENTATION of PCRE2's octal disambiguation (backrefs_design.md §5), and
# it would get the same cells wrong that rule exists to get right: `(a)\10` is
# octal and contains ZERO backreferences, `(a)\18` is `\01` then a literal '8'
# and contains zero. Worse, a scanner and the emitter would drift in the SAME
# direction — green on an incorrect compiler. So a human wrote the integer
# beside the pattern, and every octal-ambiguous spelling is kept OUT of the
# fixture set (every fixture below uses a single-digit reference, which rule 2
# makes unconditionally a backreference).
#
# COMMENT STRIPPING IS TOKEN-LEVEL AND HAPPENS FIRST. The emitted call spans
# three physical lines and carries an intent comment on the label above it, so
# a line-level strip leaves text a count rule could satisfy from a comment
# alone. The strip removes /* */ and // regions — carrying in-comment state
# ACROSS records, since a block comment spans lines — and it runs BEFORE
# head-detection and the column-0 brace rules, because a comment can otherwise
# contain something that looks like a definition head or a `}` at column 0 and
# desynchronise the `inbody` tracking. String and character literals are
# skipped so a `/*` inside one cannot open a comment.
#
# THIS CHANGES `next_pos`'s OWN CHECK IN EXACTLY ONE DIRECTION, and saying so
# matters because it is the direction that HIDES things: today a COMMENT naming
# `<prefix>_next_pos` inside an engine body IS reported as a violation, which
# is STRICTER than this check's own stated allowlist ("a residual name may
# appear (a) in a comment"). Demonstrated before this rewrite: the shipped
# `index($0, want)` rule flags a body whose only mention is a comment. Token
# stripping brings the implementation INTO LINE with its documented contract
# rather than loosening it past one. S68 still fires either way: its sabotage
# plants a real CALL in a hot loop, and stripping comments cannot hide a call.
#
# SABOTAGES: tests/mech/sabotages/S68_residual_in_hot_loop.sh (a real call to
# next_pos in the DFA's skip loop) and S109 (the backreference compare
# inlined instead of routed through the seam). Neither changes an answer.

# residual_names <file> — the residual entry names this artifact declares.
# Reads the RAW file: the marker it keys on lives in a comment, which is
# exactly what the stripper below removes.
residual_names() {
    awk '
        /ENCODING RESIDUAL entry/ { want = 1; next }
        # The first line at column 0 after the marker that looks like a
        # declaration HEAD. Matching the head rather than the terminating `;`
        # is what makes this work for an entry whose declaration spans several
        # physical lines, which the two backreference entries do.
        want && /^[A-Za-z_][A-Za-z0-9_ *]*[ *][a-z_][A-Za-z0-9_]*\(/ {
            line = $0
            sub(/\(.*/, "", line)
            sub(/^.*[^A-Za-z0-9_]/, "", line)
            print line
            want = 0
        }
    ' "$1" | sort -u
}

# calls_in_bodies <file> <name> — how many TOKEN occurrences of <name> sit
# inside a file-scope function body other than <name>'s own definition and the
# artifact's `--emit-main` `main()`. Prints the count, then the offending
# lines (which the caller shows only on a mismatch).
#
# `main` is ALLOWLISTED because it is a CALLER, not an engine: DD-12 (7)'s
# rule is about the artifact's matching machinery depending on the encoding,
# and a demo `main()` doing find-all through `<prefix>_next_pos` would be the
# documented caller protocol rather than a violation of it.
#
# TOKEN, not substring: `rx_bref_match` is a proper prefix of
# `rx_bref_match_caseless`, so a substring rule would count every caseless call
# as a case-sensitive one and both fixtures would pass with the emitter wired
# backwards.
# [M6.6.2 wave D] AN OPTIONAL THIRD ARGUMENT, `$3`, NAMES THE FUNCTION WHOSE
# OWN BODY IS SKIPPED, defaulting to `$2`. The default IS the rule as written —
# an entry is not "called from an engine body" inside its own definition — and
# the argument exists because the fourth entry has a companion TOKEN that is
# not a function name: `<prefix>_BACK_STEP_NONE` is the sentinel, and the one
# body that legitimately mentions it besides the call sites is
# `<prefix>_back_step`'s own `return k > pos ? ... : pos - k;`. Passing the
# defining function keeps ONE exclusion rule rather than adding a second, and
# keeps the declared count equal to the call count instead of `count + 1`.
calls_in_bodies() {
    awk -v want="$2" -v skipfn="${3:-$2}" '
        # ---- token-level comment/literal stripping, state carried across
        # records (a /* ... */ region spans lines) ----
        function strip(s,   out, i, n, c2, c1, d) {
            out = ""; i = 1; n = length(s)
            while (i <= n) {
                if (incomment) {
                    d = index(substr(s, i), "*/")
                    if (d == 0) return out
                    i += d + 1; incomment = 0; continue
                }
                c1 = substr(s, i, 1); c2 = substr(s, i, 2)
                if (c2 == "/*") { incomment = 1; i += 2; continue }
                if (c2 == "//") return out
                if (c1 == "\"" || c1 == "'"'"'") {
                    # A STRING OR CHARACTER LITERAL IS ONE TOKEN, and its
                    # contents are not identifiers: a `/*` inside one does not
                    # open a comment, and a residual NAME inside one is not a
                    # call. Both halves matter — the first would desynchronise
                    # the comment state, the second would make a correct
                    # compiler go red on an exact count. Escapes are honoured
                    # so a literal `\"` does not end the token early.
                    i++
                    while (i <= n) {
                        if (substr(s, i, 1) == "\\") { i += 2; continue }
                        if (substr(s, i, 1) == c1) { i++; break }
                        i++
                    }
                    out = out "\"\""
                    continue
                }
                out = out c1; i++
            }
            return out
        }
        # how many TOKEN occurrences of `want` are in `s`
        function ntok(s, want,   k, cnt, before, after, pos) {
            cnt = 0; pos = 1
            while ((k = index(substr(s, pos), want)) > 0) {
                k += pos - 1
                before = (k == 1) ? "" : substr(s, k - 1, 1)
                after  = substr(s, k + length(want), 1)
                if (before !~ /[A-Za-z0-9_]/ && after !~ /[A-Za-z0-9_]/) cnt++
                pos = k + length(want)
            }
            return cnt
        }
        {
            line = strip($0)
            if (line ~ /^[A-Za-z_].*\(/ && line !~ /;[[:space:]]*$/) { head = line; next }
            if (line ~ /^\{/ && head != "") {
                fname = head
                sub(/\(.*/, "", fname)
                sub(/^.*[^A-Za-z0-9_]/, "", fname)
                inbody = 1; head = ""; next
            }
            if (line ~ /^\}/) { inbody = 0; fname = ""; next }
            if (inbody && fname != skipfn && fname != "main") {
                k = ntok(line, want)
                if (k > 0) { total += k; hits = hits FILENAME ":" FNR ": " line "\n" }
            }
        }
        END { print total + 0; printf "%s", hits }
    ' "$1"
}

resid_total=0
resid_bad=0
resid_files=0
resid_brefdecl=0
resid_backdecl=0
while IFS=$'\t' read -r nm pat extra decl; do
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
    # The DECLARED entry set, from the TEST. `decl` is a comma-separated list
    # of `<suffix>:<expected engine-body call count>` pairs.
    want_set=""
    nbref=0
    nback=0
    for pair in $(printf '%s' "$decl" | tr ',' ' '); do
        want_set="$want_set rx_${pair%%:*}"
        case "${pair%%:*}" in bref_match|bref_match_caseless) nbref=$((nbref + 1)) ;; esac
        case "${pair%%:*}" in back_step) nback=$((nback + 1)) ;; esac
    done
    want_set="$(printf '%s\n' $want_set | sort -u | tr '\n' ' ')"
    [ "$nbref" -gt 0 ] && resid_brefdecl=$((resid_brefdecl + 1))
    [ "$nback" -gt 0 ] && resid_backdecl=$((resid_backdecl + 1))

    for f in "$WORKDIR/$nm.h" "$WORKDIR/${nm}_sc.c"; do
        [ -f "$f" ] || continue
        got_set="$(residual_names "$f" | tr '\n' ' ')"
        resid_files=$((resid_files + 1))
        # (1) THE ARTIFACT CARRIES EXACTLY THE DECLARED ENTRIES. This is the
        # half that stops an emitter from inlining the compare AND dropping the
        # entry from the artifact's mask, which would otherwise leave the
        # count rule below with nothing to count.
        if [ "$(printf '%s' "$got_set" | tr -s ' ')" != "$(printf '%s' "$want_set" | tr -s ' ')" ]; then
            resid_bad=$((resid_bad + 1))
            bad "[M5-SEAM/D58] '$pat' ($extra): the artifact declares residual entries [$got_set] where this fixture declares [$want_set] — the encoding seam's per-artifact mask moved. An entry that vanishes from the mask takes its call-count check with it, which is why this is asserted from the TEST and not read off the artifact"
        fi
    done
    # (2) THE PER-SITE COUNT, over both artifact forms' definitions (.c).
    for pair in $(printf '%s' "$decl" | tr ',' ' '); do
        rn="rx_${pair%%:*}"
        wantn="${pair##*:}"
        resid_total=$((resid_total + 1))
        out1="$(calls_in_bodies "$WORKDIR/$nm.c" "$rn")"
        out2="$(calls_in_bodies "$WORKDIR/${nm}_sc.c" "$rn")"
        n1="$(printf '%s' "$out1" | head -1)"
        n2="$(printf '%s' "$out2" | head -1)"
        hits="$(printf '%s\n%s' "$out1" "$out2" | tail -n +2)"
        for got in "$n1" "$n2"; do
            [ "$got" = "$wantn" ] && continue
            resid_bad=$((resid_bad + 1))
            if [ "$wantn" = "0" ]; then
                bad "[M5-SEAM/DD-12(7)] '$rn' is referenced $got time(s) from an engine body in the '$pat' artifact and this fixture declares 0 — a hot path calling into the encoding residual is the derailment DD-12 (7) forbids, and it changes no answer under the byte backend, so nothing else in this tree will tell you: $(printf '%s' "$hits" | head -2 | tr '\n' ' ')"
            else
                bad "[M5-SEAM/D58] '$rn' is called $got time(s) from engine bodies in the '$pat' artifact, where this fixture declares $wantn — either the compare stopped routing through the seam (D58 scope item 3: encoding-sensitive byte arithmetic in shared emitter code is what the seam exists to prevent, and it changes no answer under the byte backend) or a call site appeared that the test did not write"
            fi
        done
    done
    # (3) [M6.6.2 wave D] THE SENTINEL IS CHECKED AT EVERY CALL SITE.
    # lookaround_design.md §4.2(3): under the byte backend the caller's
    # `scan_position < k` guard is EXACT, so `<prefix>_BACK_STEP_NONE` can
    # never come back and the comparison is dead code that changes NO ANSWER.
    # Under UTF-8 `k` characters is at least `k` bytes, so the guard still
    # soundly rejects but stops being exact, and the sentinel is what makes
    # the shape correct — which is why deleting the comparison is a row FOR
    # THE BACKEND THAT DOES NOT EXIST YET (S134) and why nothing behavioural
    # can see it. The count is the SAME declared integer as the call count,
    # because §3.4 emits exactly one sentinel check per back-step call; a
    # separate literal would be a second place to get the same fact wrong.
    #
    # `calls_in_bodies` is reused unchanged and that is the point: the
    # `#define <prefix>_BACK_STEP_NONE` sits at FILE SCOPE, so the body
    # tracking excludes it without a rule of its own, and the token rule keeps
    # `<prefix>_BACK_STEP_NONE` from being confused with `<prefix>_back_step`.
    for pair in $(printf '%s' "$decl" | tr ',' ' '); do
        [ "${pair%%:*}" = "back_step" ] || continue
        wantn="${pair##*:}"
        for af in "$WORKDIR/$nm.c" "$WORKDIR/${nm}_sc.c"; do
            got="$(calls_in_bodies "$af" "rx_BACK_STEP_NONE" "rx_back_step" | head -1)"
            [ "$got" = "$wantn" ] && continue
            resid_bad=$((resid_bad + 1))
            bad "[M5-SEAM/D58] the '$pat' artifact compares against 'rx_BACK_STEP_NONE' $got time(s) from engine bodies, where this fixture declares $wantn back-step call site(s) — every back-step call owes a sentinel check (lookaround_design.md §4.2(3)). Deleting the check changes NO ANSWER under the byte backend, where the caller's own guard is exact, so this is the only instrument that can see it"
        done
    done
    # TAB-separated: name, pattern, extra pcrec args ('-' for none), and the
    # DECLARED residual entries as `<suffix>:<engine-body call count>`. The
    # separator is a TAB precisely because every other candidate ('|', ',')
    # is regex syntax the fixture patterns need — and the count column is a
    # HUMAN-WRITTEN integer, never derived: see this block's header for the
    # `(a)\10` / `(a)\18` cells that a pattern scanner would get wrong.
done <<EOF
residmemchr	a(b|c)+d	--no-captures	next_pos:0
residbitmap	[ab]c[de]	--no-captures	next_pos:0
residanchor	^ab(c|d)	--no-captures	next_pos:0
residvm	a(b|c)+d	-	next_pos:0
residvmonly	(x)(a|bc)+d	--engine=vm	next_pos:0
residmain	a(b|c)+d	--emit-main	next_pos:0
residbref1	(a|b)\1	--features backrefs	next_pos:0,bref_match:1
residbref3	(a)(b)\2\1\2	--features backrefs	next_pos:0,bref_match:3
residbrefci	(?i:(a))(?i:\1)	--features backrefs,modifiers	next_pos:0,bref_match_caseless:1
residbrefboth	(a)\1(?i:\1)	--features backrefs,modifiers	next_pos:0,bref_match:1,bref_match_caseless:1
residlb1	(?<=ab)c	--features lookaround	next_pos:0,back_step:1
residlb2	(?<=a|bc)x	--features lookaround	next_pos:0,back_step:2
residlb3	(?<=a|bc|def)x	--features lookaround	next_pos:0,back_step:3
residlbneg	(?<!ab|cd)x	--features lookaround	next_pos:0,back_step:2
residlbna	(?<*a|bc)x	--features lookaround	next_pos:0,back_step:2
residlbtwo	(?<=ab)(?<=b)c	--features lookaround	next_pos:0,back_step:2
residlbbref	(a)(?<=a)\1	--features backrefs,lookaround	next_pos:0,bref_match:1,back_step:1
EOF
# THE SCOPED NON-VACUITY GUARD, EXACT AND NOT A FLOOR (R32 C2(b), and the
# final re-check's wording item 1). The GLOBAL guard below cannot serve here:
# `next_pos` is unconditional, so it stays satisfied even if every
# backref-bearing fixture were deleted, and the check would go green over an
# empty population — the diagnosed shape relocated into the fixture table.
#
# A FLOOR IS THE WRONG SHAPE FOR A CONCRETE REASON: four fixtures declare a
# bref entry, so "at least 3" passes while one of them silently loses its
# declaration — which is the population-shrinking failure the guard exists to
# catch, arriving through the guard itself. EXACT is this file's own
# convention (check_class_ports, check_class_syntax_reach).
if [ "$resid_brefdecl" -ne 5 ]; then
    bad "[M5-SEAM/D58]: $resid_brefdecl fixtures declare a backreference residual entry, expected EXACTLY 5 — the population this check's second entry pair is asserted over moved. Deleting a fixture row must go RED here, which is the whole reason this guard is not the global one below"
fi
# [M6.6.2 wave D] THE SAME GUARD FOR THE FOURTH ENTRY, WITH ITS OWN LITERAL,
# and it is a SECOND guard rather than a wider first one — lookaround_design.md
# §4.4(3) states the number here rather than leaving it to be discovered,
# because R32 C5 found "the built column gains this module's rows for free"
# asserted by nothing and a guard whose literal nobody wrote down is the same
# shape. Two reasons not to fold lookbehind fixtures into the bref count: the
# counts measure DIFFERENT THINGS, and R32's own argument against a floor
# applies WITHIN a family rather than across families.
#
# SEVEN, and every one of them is a hand-written integer beside a pattern.
# R32 C2(a)'s ruling applies here with a sharper edge than it had for
# backrefs: deriving `back_step:<n>` by counting `|` in the body would be A
# SECOND IMPLEMENTATION OF §2.5's BRANCH-SPLITTING RULE, and it would get
# `(?<=(a|bc))x` (REFUSED, one branch) and `(?<=a|bc)x` (two branches) exactly
# backwards — which are the two cells §2.5 exists to distinguish. The fixture
# set is chosen so the number is not always the same fact: `residlbtwo` is TWO
# one-branch lookbehinds and declares 2, so a reader cannot conclude that the
# column counts lookbehinds OR that it counts `|`s. It counts CALL SITES, one
# per top-level branch per lookbehind, which is what §3.4 emits.
if [ "$resid_backdecl" -ne 7 ]; then
    bad "[M5-SEAM/D58]: $resid_backdecl fixtures declare a lookbehind back-step residual entry, expected EXACTLY 7 — the population this check's FOURTH entry is asserted over moved. S133 inlines the back-step as 'scan_position - k' and drops the mask OR, which changes NO ANSWER under the byte backend, so this fixture-declared per-site count is its only possible detector and a shrinking population would take the detector with it"
fi
if [ "$resid_files" -eq 0 ] || [ "$resid_total" -eq 0 ]; then
    bad "[M5-SEAM/DD-12(7)]: NO residual entry was found in any emitted artifact — this check has no population and cannot certify anything. Either the residual embed (src/gen/enc/) stopped emitting, or its 'ENCODING RESIDUAL entry' marker moved and this check's extractor went blind"
elif [ "$resid_bad" -eq 0 ]; then
    ok "[M5-SEAM/DD-12(7)+D58]: $resid_total declared residual entr(y|ies) across $resid_files emitted surfaces, each called EXACTLY as its fixture declares ($resid_brefdecl fixtures declare a backreference compare, $resid_backdecl a lookbehind back-step, each population guarded by its own EXACT literal; comment stripping is token-level and runs before the body tracking)"
fi

# ---- [M6.5-DUPNAMES] THE REFLECTION TABLE'S ORDER, READ OFF THE ARTIFACT ---
# backrefs_design.md §8.2, and R32's re-check is why this is STRUCTURAL rather
# than a behavioural `.rxt` cell.
#
# THE FACT. `rx_info.groups` is documented "sorted, bsearch-able", and with
# `(?J)` the table can now hold ADJACENT ROWS WITH EQUAL NAMES. libpcre2's own
# `PCRE2_INFO_NAMETABLE` is sorted (name ASCENDING, then number ASCENDING) —
# measured over ten patterns — and `docs/spec/match_api.md` §6's caller
# algorithm (bsearch, walk BACK to the run's first row, then FORWARD to the
# first participating one) selects the LOWEST-numbered participating member
# ONLY IF the within-name order is ascending. Get it backwards and the table
# encodes the "last set" rule §8.3's `"xyy"` cell rules out.
#
# WHY NOT A BEHAVIOURAL ROW. Without the tiebreak, whether the emitted order
# is wrong depends on TWO unspecified properties agreeing: `qsort`'s stability
# and the direction `Ctx.named_groups` is walked in. `mod_named_groups.c`
# PREPENDS and `emit_dfa.c` walks from the head, so on glibc (a stable merge
# sort) a name-only comparator yields DESCENDING numbers within a run — but a
# check that depends on that coincidence is not a control. Reading the order
# off the ARTIFACT depends on neither.
#
# STRICTLY increasing, not merely non-decreasing, and that is the COMPARATOR
# TOTALITY half: a comparator returning 0 for rows that differ in NUMBER would
# leave them in whatever order the sort happened to produce, and two rows equal
# in BOTH fields would be a duplicate the table must never contain. The order
# half is live exactly when a dup-name pattern is compiled; the totality half
# is exercisable on every fixture with two or more names, which is why the
# fixture set below has both kinds.
#
# SABOTAGE: S120 removes the number tiebreak from `ng_cmp_name`.
dup_bad=0; dup_files=0; dup_rows=0; dup_dupname=0
while IFS=$'\t' read -r nm feats pat; do
    [ -n "$nm" ] || continue
    if ! "$PCREC" -p rx --features "$feats" -o - -- "$pat" \
            > "$WORKDIR/$nm.c" 2>"$WORKDIR/$nm.err"; then
        bad "[M6.5-DUPNAMES] pcrec refused the fixture '$pat': $(head -1 "$WORKDIR/$nm.err")"
        dup_bad=$((dup_bad + 1)); continue
    fi
    # The emitted rows, as `<name>\t<number>` in artifact order.
    sed -n 's/^    { "\([^"]*\)", \([0-9-]*\), .*/\1\t\2/p' "$WORKDIR/$nm.c" \
        > "$WORKDIR/$nm.rows"
    n=$(grep -c . "$WORKDIR/$nm.rows" || true)
    if [ "$n" -lt 2 ]; then
        bad "[M6.5-DUPNAMES] the fixture '$pat' emitted $n reflection rows — fewer than two cannot exhibit an ORDER at all"
        dup_bad=$((dup_bad + 1)); continue
    fi
    dup_files=$((dup_files + 1)); dup_rows=$((dup_rows + n))
    if [ "$(cut -f1 "$WORKDIR/$nm.rows" | sort | uniq -d | wc -l)" -gt 0 ]; then
        dup_dupname=$((dup_dupname + 1))
    fi
    if ! out=$(awk -F'\t' '
        NR > 1 {
            if ($1 < pn || ($1 == pn && $2 <= pv)) {
                printf "row %d (%s,%s) does not strictly follow (%s,%s)\n", NR, $1, $2, pn, pv
                bad = 1
            }
        }
        { pn = $1; pv = $2 }
        END { exit bad }
    ' "$WORKDIR/$nm.rows"); then
        bad "[M6.5-DUPNAMES] '$pat': the emitted rx_group_entry rows are not STRICTLY increasing in (name, number) — $out. A caller doing match_api.md §6's bsearch-then-walk would select the wrong member of a duplicated name's run, which is the resolution rule §8.3's \"xyy\" cell rules out"
        dup_bad=$((dup_bad + 1))
    fi
    # TAB-separated: name, features, pattern.
done <<EOF
dupA	backrefs,named-groups,modifiers	(?J)(?<z>1)(?<a>2)(?<z>3)(?<a>4)\k<a>
dupB	backrefs,named-groups,modifiers	(?J)(?<b>x)(?<a>y)(?<b>z)\k<b>
dupC	backrefs,named-groups,modifiers	(?J)(?<n>1)|(?<n>2)|(?<n>3)
dupD	named-groups	(?<zeta>a)(?<alpha>b)(?<mu>c)
dupE	named-groups	(?<a>1)(?<aa>2)(?<b>3)
EOF
if [ "$dup_files" -ne 5 ] || [ "$dup_dupname" -ne 3 ]; then
    bad "[M6.5-DUPNAMES] POPULATION: $dup_files fixtures emitted a table and $dup_dupname of them carry a DUPLICATED name, expected EXACTLY 5 and 3. The ORDER half of this check is vacuous while every name is unique — it goes live exactly when a dup-name pattern is in the set — so losing those three would leave the totality half alone"
elif [ "$dup_bad" -eq 0 ]; then
    ok "[M6.5-DUPNAMES] §8.2: $dup_rows reflection rows across $dup_files artifacts ($dup_dupname with a duplicated name) are STRICTLY increasing in (name, number), read off the ARTIFACT — so neither qsort's stability nor the declaration list's direction is being trusted"
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
# rather than assuming it: `rx_reverse_is_accepting[K]` is read out of the artifact and
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
    grep 'rx_forward_is_accepting_by_class\[' "$wbb" | grep -v '^ *static const' > "$WORKDIR/f2reads"
    f2lines=$(grep -c . "$WORKDIR/f2reads" || true)
    f2bad=$(grep -cv 'rx_forward_is_accepting_by_class\[[a-z_]* \* [0-9]* + forward_class\]' "$WORKDIR/f2reads" || true)
    guard_ln=$(grep -n '^        if (scan_position >= subject_length) {$' "$wbb" | head -1 | cut -d: -f1)
    first_f2=$(grep -n 'rx_forward_is_accepting_by_class\[' "$wbb" | grep -v ':[[:space:]]*static const' \
               | head -1 | cut -d: -f1)
    scalar_in_guard=$(sed -n "${guard_ln:-0},$((${guard_ln:-0} + 2))p" "$wbb" \
                      | grep -c 'rx_forward_is_accepting\[' || true)
    if [ "$f2lines" -lt 1 ]; then
        bad "[M6.2-WORDB rule 1]: '$WB_PAT' emitted no class-indexed accept at all — the fixture no longer exercises §3.6, so this rule has no population"
    elif [ "$f2bad" -ne 0 ]; then
        bad "[M6.2-WORDB rule 1]: $f2bad of $f2lines class-indexed accept reads are not indexed by the 'cl' local; a read that computes its own class is a read this check cannot prove is guarded:"
        grep -v 'rx_forward_is_accepting_by_class\[[a-z_]* \* [0-9]* + forward_class\]' "$WORKDIR/f2reads" >&2
    elif [ -z "$guard_ln" ] || [ -z "$first_f2" ] || [ "$guard_ln" -ge "$first_f2" ]; then
        bad "[M6.2-WORDB rule 1]: the 'if (pos >= n)' guard is at line ${guard_ln:-MISSING} and the first class-indexed accept at line ${first_f2:-MISSING} — the guard must come FIRST, or the emitted loop reads s[pos] at pos == n"
    elif [ "$scalar_in_guard" -lt 1 ]; then
        bad "[M6.2-WORDB rule 1]: the 'pos >= n' arm does not read the SCALAR accept table, so the end-of-subject accept is being dropped rather than taken from the view (§3.6.2)"
    else
        ok "[M6.2-WORDB rule 1] (§3.6.2): all $f2lines class-indexed accept reads go through the guarded 'cl' local, and the 'pos >= n' arm takes the SCALAR accept before any of them — no accept table is indexed at pos == n"
    fi

    # --- rule 2 (§3.8.3.1): every `match_start_position` writer at the reverse boundary ---
    #
    # THE INVARIANT: no `match_start_position` is recorded at `pp == startpos` except through
    # the context-indexed accept. The design states it as an invariant rather
    # than a patch for a specific reason — there is MORE THAN ONE WRITER. The
    # loop-top one is obvious; the reverse SKIP's is not, and it is worse than
    # it looks: `emit_dfa.c`'s `if (!eol && rd->st[K].accept)` is a
    # COMPILE-TIME condition on whether to EMIT the line, so what would land
    # in the artifact is a BARE, UNCONDITIONAL `match_start_position = pp;` inside the skip
    # block with no runtime test to fail.
    #
    # So the check enumerates EVERY `match_start_position` assignment in the body and
    # requires each to be conditioned on an accept read — on its own line or
    # on the one above it, which is where the boundary arm's two-line ternary
    # puts it. A bare assignment fails no matter which writer emitted it,
    # which is what makes this an invariant check rather than a check of the
    # one site somebody remembered.
    #
    # THE FIXTURE HAS A LIVE REVERSE SKIP (`rx_reverse_stay<K>`), asserted below: without
    # one this rule would pass on an artifact that has no second writer to get
    # wrong.
    rskips=$(grep -c 'rx_reverse_stay[0-9]*\[subject\[rewind_position - 1\]\]' "$wbb" || true)
    # THE NON-VACUITY ASSERTION. Read the reverse skip state's index out of
    # its own emitted loop, then that state's SCALAR accept out of the
    # artifact's `rx_reverse_is_accepting[]`. Both come from the artifact; neither is typed
    # here, so a fixture change cannot silently drop the property.
    rskip_k=$(grep -oE 'rx_reverse_stay[0-9]+\[subject\[rewind_position - 1\]\]' "$wbb" | head -1 \
              | grep -oE '[0-9]+' | head -1)
    rskip_acc=$(sed -n '/static const unsigned char rx_reverse_is_accepting\[/,/};/p' "$wbb" \
                | tr -d ' \n' | sed 's/.*={//; s/};.*//' \
                | cut -d, -f$((${rskip_k:-0} + 1)))
    # `size_t match_start_position = (size_t)-1;` is the DECLARATION, not a record of a
    # match start, and is excluded by name rather than by pattern-matching
    # around it.
    sf_total=$(grep 'match_start_position = ' "$wbb" | grep -cv 'size_t match_start_position = ' || true)
    sf_bad=$(awk '
        /match_start_position = / && !/size_t match_start_position = / {
            # `racc` was how the accept table was spelled before [M6-READ]; the
            # two tables are now rx_reverse_is_accepting[] and
            # rx_reverse_is_accepting_by_class[], and matching on the shared
            # substring keeps this blind to which of the two a writer reads --
            # which is the property the rule wants.
            if ($0 !~ /reverse_is_accepting/ && prev !~ /reverse_is_accepting/) { print NR": "$0; n++ }
        }
        { if ($0 !~ /^[[:space:]]*$/) prev = $0 }
        END { exit 0 }
    ' "$wbb")
    nsf_bad=$(printf '%s' "$sf_bad" | grep -c . || true)
    if [ "$rskips" -lt 1 ]; then
        bad "[M6.2-WORDB rule 2]: '$WB_PAT' emitted no reverse skip loop, so the second, blind match_start_position writer §3.8.3.1 is about cannot be present — this rule would pass vacuously"
    elif [ "${rskip_acc:-0}" != "1" ]; then
        bad "[M6.2-WORDB rule 2]: '$WB_PAT's reverse skip state $rskip_k does NOT accept (rx_reverse_is_accepting[$rskip_k] = ${rskip_acc:-unread}), so the blind writer is gated off by its OTHER compile-time conjunct and no sabotage of the guard can emit it. This rule would pass vacuously — which is exactly how sabotage S72 first came back UNDETECTED. Pick a fixture whose reverse skip state accepts."
    elif [ "$sf_total" -lt 2 ]; then
        bad "[M6.2-WORDB rule 2]: only $sf_total match_start_position writers in the body; the boundary arm and the interior read are both expected"
    elif [ "$nsf_bad" -ne 0 ]; then
        bad "[M6.2-WORDB rule 2]: $nsf_bad match_start_position writer(s) are not conditioned on an accept read. A bare 'match_start_position = pp;' at pp == startpos records a match start whose leading \\b/\\B was never evaluated against s[startpos-1]:"
        printf '%s\n' "$sf_bad" >&2
    else
        ok "[M6.2-WORDB rule 2] (§3.8.3.1): all $sf_total match_start_position writers are conditioned on an accept read, with $rskips reverse skip loop(s) present AND skip state $rskip_k ACCEPTING (rx_reverse_is_accepting[$rskip_k] = 1) — so the second, blind writer really would be emitted here if its guard were removed"
    fi

    # --- rule 2b: the boundary accept is ATTACHED TO THE BREAK (R30 N9) -----
    #
    # The reverse loop has TWO exits — the boundary and the dead state — and
    # an accept placed after the loop would run on BOTH: on the dead-state
    # exit it would record `match_start_position` at a position the walk never reached (a
    # WRONG ANSWER, worse than a lost match) and index the accept table with a
    # NEGATIVE state (out-of-bounds, K27's class). So the context-indexed
    # boundary read must sit INSIDE the `pp <= startpos` arm, and there must
    # be no accept read after the loop closes.
    b_arm=$(grep -n 'if (rewind_position <= search_from) {' "$wbb" | head -1 | cut -d: -f1)
    b_read=$(grep -n 'rx_reverse_byte_class\[subject\[search_from - 1\]\]' "$wbb" | head -1 | cut -d: -f1)
    b_dead=$(grep -n 'if (reverse_state < 0) break;' "$wbb" | head -1 | cut -d: -f1)
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
    ndistinct=$(grep -oE '\(rx_class_bitmap[0-9]+\[\(subject\[[^]]*\]\) >> 3\] >> \(\(subject\[[^]]*\]\) & 7\)\) & 1|\(unsigned\)\(subject\[[^]]*\] - [0-9]+\) <= [0-9]+u|subject\[[^]]*\] == [0-9]+' \
                "$WORKDIR/wordset.c" | sed 's/subject\[[^]]*\]/B/g' | sort -u | grep -c . || true)
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

# =========================================================================
# [M6.2 WAVE E] `\K` — assertions_design.md §6.3's THREE RULES, structurally
# =========================================================================
#
# WHAT THESE ASSERT THAT NO CORPUS CAN. §6.3 rule 1 is a provenance rule:
# `caps[0][0]` on a `\K` artifact must come FROM THE VM, and the number it
# must NOT come from is the prefilter's span start — which under the hybrid is
# the REVERSE PASS's answer. On most cells the two agree, so a corpus catches
# a violation only where they differ; the emitted text either reads slot 0 or
# it does not, and that is what is checked here.
#
# `\K` IS VM-FORCED, so a `\K` pattern never HAS a DFA artifact and rule 3's
# DFA half cannot be checked on one. It is checked the other way round: a
# `\K`-FREE artifact's entries and caps_out must be the pre-wave text,
# character for character. That is also the whole byte-identity claim of this
# wave, stated where it is cheap — the emitter reads `v.nkreset` at exactly
# ONE site, so "a `\K`-free pattern pays nothing" is a claim about one
# predicate rather than the multi-site construction waves B, C and D each had
# to build a full corpus gate for. (The corpus-wide measurement was taken once
# against the genuine PRE-WAVE COMPILER — a reference sharing no sources with
# the subject, which is strictly stronger than a knob build and is what wave
# D's own knob-placement finding argues for. The numbers are in the wave's
# plan row.)
#
# The sabotage is tests/mech/sabotages/S85_kreset_caps_from_prefilter.sh, and
# it is R30 C3's: make the emitted `\K` artifact take `caps[0][0]` from the
# prefilter's span. Rule 1 below goes red on it.

# --- rule 1: a \K artifact's caps[0][0] comes from the trailed slot --------
if "$PCREC" -p rx --features assertions -o "$WORKDIR/kres.c" -- 'a\Kb' >/dev/null 2>&1; then
    # The whole of the emitted caps_out, so both the presence of the \K form
    # and the ABSENCE of the plain one are read from the same text.
    awk '/^static void rx_report_captures\(/,/^}/' "$WORKDIR/kres.c" > "$WORKDIR/kres.capsout"
    if [ ! -s "$WORKDIR/kres.capsout" ]; then
        bad "[M6.2-KRESET rule 1]: could not extract rx_report_captures from the 'a\\Kb' artifact — the extractor has stopped matching the emitted shape, so this rule is measuring nothing"
    elif ! grep -q 'run->slot_values\[0\] != PCREC_UNSET' "$WORKDIR/kres.capsout"; then
        bad "[M6.2-KRESET rule 1]: 'a\\Kb's caps_out does not read the trailed \\K slot at all. §6.3 rule 1: caps[0][0] on a \\K pattern comes from the VM, never from the prefilter's span start (which is the REVERSE PASS's answer)"
    elif grep -qE '^ *capture_spans\[0\]\[0\] = \(ptrdiff_t\)match_start;' "$WORKDIR/kres.capsout"; then
        bad "[M6.2-KRESET rule 1]: 'a\\Kb's caps_out still contains the unconditional 'caps[0][0] = (ptrdiff_t)start;'. That is the prefilter's span start — the pre-\\K start — and writing it out reports where matching BEGAN where PCRE2 reports where the last \\K was crossed"
    elif grep -qE '^ *slot_values\[0\] = ' "$WORKDIR/kres.c"; then
        # ORDERED BEFORE the missing-RX_SET branch below, because a DIRECT
        # write satisfies "no RX_SET" too and the specific diagnosis is the
        # useful one. Measured: sabotage S86 lands here.
        bad "[M6.2-KRESET rule 1]: 'a\\Kb' writes slot_values[0] DIRECTLY rather than through RX_SET. The macro is what records the old value on the trail, so a direct write cannot be undone when a backtrack passes back over it — '(?:a\\K|ax)c' on \"axc\" is the cell that then reports (1,3) instead of (0,3)"
    elif ! grep -q 'RX_SET(RX_SLOT_WHOLE_START, (ptrdiff_t)scan_position)' "$WORKDIR/kres.c"; then
        bad "[M6.2-KRESET rule 1]: 'a\\Kb' emits no trailed write to slot 0 — caps_out reads a slot nothing ever fills, so every match reports the fallback and the construct is inert"
    else
        ok "[M6.2-KRESET rule 1] (§6.3): 'a\\Kb's caps[0][0] comes from the TRAILED slot 0 and the unconditional 'caps[0][0] = start' (the prefilter's, i.e. the reverse pass's, span start) is GONE from its caps_out — both directions, in one artifact"
    fi
else
    bad "[M6.2-KRESET rule 1]: pcrec failed to compile the fixture 'a\\Kb'"
fi

# --- rule 1b: a \K-FREE artifact keeps the pre-wave caps_out ---------------
#
# THE SAME TEXT, PINNED AS A LITERAL, and that is deliberate rather than lazy:
# an assertion written as "does not contain the \K form" would pass on an
# emitter that had rewritten the line into some third shape. The two lines
# below are what the emitter produced BEFORE this wave, quoted here so the
# check has a source independent of the emitter it checks.
if "$PCREC" -p rx --engine=vm -o "$WORKDIR/nok.c" -- '(a)(b)' >/dev/null 2>&1; then
    awk '/^static void rx_report_captures\(/,/^}/' "$WORKDIR/nok.c" > "$WORKDIR/nok.capsout"
    if [ ! -s "$WORKDIR/nok.capsout" ]; then
        bad "[M6.2-KRESET rule 1b]: could not extract rx_report_captures from the \\K-free VM artifact"
    elif ! grep -qF '    capture_spans[0][0] = (ptrdiff_t)match_start;' "$WORKDIR/nok.capsout" \
      || ! grep -qF '    capture_spans[0][1] = (ptrdiff_t)match_start + match_length;' "$WORKDIR/nok.capsout"; then
        bad "[M6.2-KRESET rule 1b]: the \\K-free VM artifact '(a)(b)' no longer emits the pre-wave caps_out body verbatim. Wave E's claim is that a \\K-free pattern pays NOTHING for \\K, and the emitter reads v.nkreset at exactly one site — this is that site"
    elif grep -q 'PCREC_UNSET' "$WORKDIR/nok.capsout"; then
        bad "[M6.2-KRESET rule 1b]: the \\K-free VM artifact's caps_out mentions PCREC_UNSET — the \\K arm is being emitted for a pattern with no \\K in it"
    else
        ok "[M6.2-KRESET rule 1b]: a \\K-FREE VM artifact emits the pre-wave caps_out body character for character (the two lines are pinned as literals here, so a rewrite into a third shape fails too) — wave E's byte-identity claim at its one emitter decision point"
    fi
else
    bad "[M6.2-KRESET rule 1b]: pcrec failed to compile the \\K-free VM fixture '(a)(b)'"
fi

# --- rule 3: the match-here entries -----------------------------------------
#
# §6.3 rule 3 says the match-here entry must filter on the PRE-\K start and
# return the CONSUMED length. On the VM — the only engine a \K pattern can
# reach — BOTH are structural rather than computed, and this asserts the
# structure rather than the answers (tests/assertions/run_kreset_diff.sh §2
# asserts the answers, against libpcre2):
#
#   the filter   there is none, and there must be none. The entry calls
#                <prefix>_match_impl at ctx->pos directly, so "anchored at the
#                requested position" is a property of the call. A
#                `caps[0][0] != ctx->pos` test appearing here would be the
#                DFA's shape imported into the VM's, which is exactly the
#                confusion R30 E8 corrected.
#   the return   `return r;` — match_impl's own `pos - ctx->pos`, computed
#                from positions. A `caps[0][1] - caps[0][0]` here would be the
#                post-\K length, and a D38 callout advancing by it would never
#                move on 'ab\K'.
if "$PCREC" -p rx --features assertions -o "$WORKDIR/kent.c" -- 'a\Kb' >/dev/null 2>&1; then
    awk '/^ptrdiff_t rx_match\(const rx_ctx \*ctx\)/,/^}/' "$WORKDIR/kent.c" > "$WORKDIR/kent.match"
    if [ ! -s "$WORKDIR/kent.match" ]; then
        bad "[M6.2-KRESET rule 3]: could not extract rx_match from the 'a\\Kb' artifact"
    elif grep -q 'ctx->pos' "$WORKDIR/kent.match" && grep -q 'caps\[0\]\[0\]' "$WORKDIR/kent.match"; then
        bad "[M6.2-KRESET rule 3]: 'a\\Kb's rx_match compares caps[0][0] against ctx->pos. That is the DFA artifact's start filter, and under \\K it compares against the POST-\\K start and REJECTS a genuine anchored match — 'a\\Kb' at ctx->pos 0 returns -1 where PCRE2 matches (1,2)"
    elif grep -q 'caps\[0\]\[1\] - caps\[0\]\[0\]' "$WORKDIR/kent.match"; then
        bad "[M6.2-KRESET rule 3]: 'a\\Kb's rx_match returns caps[0][1] - caps[0][0], the POST-\\K length. A D38 callout uses that return as its ADVANCE, so on 'ab\\K' it would advance by 0 and loop forever"
    elif ! grep -q 'rx_match_anchored(ctx' "$WORKDIR/kent.match"; then
        bad "[M6.2-KRESET rule 3]: 'a\\Kb's rx_match does not call rx_match_anchored directly. The VM's match-here entry is anchored BY CONSTRUCTION (it starts at ctx->pos and never moves it); routing it through rx_search would reintroduce the filter this rule forbids"
    else
        ok "[M6.2-KRESET rule 3] (R30 E8): 'a\\Kb's rx_match calls rx_match_anchored at ctx->pos directly — no start filter to compare against a post-\\K start, and no caps-derived return. Both halves of §6.3 rule 3 hold structurally on the only engine a \\K pattern can reach"
    fi
else
    bad "[M6.2-KRESET rule 3]: pcrec failed to compile the fixture 'a\\Kb'"
fi

# --- rule 3b: the DFA artifact's entry is UNTOUCHED --------------------------
#
# The other half of rule 3, and it can only be checked on a \K-FREE pattern
# because a \K pattern is VM-forced and has no DFA entry at all. The DFA's
# match-here entry is the shape §6.3 quotes — rx_search plus a start filter
# plus a caps-derived return — and wave E must not have touched it: the filter
# and the return are CORRECT there, because no DFA artifact can contain a \K.
if "$PCREC" -p rx --no-captures -o "$WORKDIR/dent.c" -- 'a(b|c)d' >/dev/null 2>&1; then
    awk '/^ptrdiff_t rx_match\(const rx_ctx \*ctx\)/,/^}/' "$WORKDIR/dent.c" > "$WORKDIR/dent.match"
    if [ ! -s "$WORKDIR/dent.match" ]; then
        bad "[M6.2-KRESET rule 3b]: could not extract rx_match from the DFA artifact"
    elif ! grep -qF '(size_t)capture_spans[0][0] != ctx->pos' "$WORKDIR/dent.match" \
      || ! grep -qF 'return capture_spans[0][1] - capture_spans[0][0];' "$WORKDIR/dent.match"; then
        bad "[M6.2-KRESET rule 3b]: the DFA artifact's rx_match no longer carries the start filter and the caps-derived return verbatim. Wave E changed nothing there BY DESIGN — a \\K pattern is VM-forced, so the shape §6.3 quotes as broken-under-\\K is unreachable-with-\\K and correct as it stands"
    else
        ok "[M6.2-KRESET rule 3b]: the DFA artifact's rx_match still carries its start filter and its caps-derived return, verbatim and untouched by wave E — correct there precisely because a \\K pattern can never reach that engine"
    fi
else
    bad "[M6.2-KRESET rule 3b]: pcrec failed to compile the DFA fixture 'a(b|c)d'"
fi

# ===========================================================================
# [M6.4-ATOMIC] module `atomic-groups` ([M6.4.2]) — FIVE STRUCTURAL RULES
# ===========================================================================
#
# EVERY RULE BELOW MATCHES **BOTH SPELLINGS OF A CUT**, and that is a
# correction to the design's first form rather than caution. `vm_revdet_rep`
# cuts by assigning `run->resume_depth = <prefix>_rvN_frame_mark` and its own
# comment says it "never goes near the RX_CUT macro"; `vm_cut`'s header records
# what that cost once — a step-charge probe "reported a confident zero for the
# revdet rung because the first version instrumented only the `RX_CUT` macro".
# A rule that matched one spelling would inherit that same zero.
#
# AND EVERY RULE MATCHES **CALL SITES**, never `grep RX_CUT`. R31 C3, and the
# failing direction is demonstrable on a SHIPPED artifact with no sabotage at
# all — `#define RX_CUT(slot_)` is emitted UNCONDITIONALLY on every VM artifact,
# so `grep -c RX_CUT` is at least 1 on every artifact pcrec has ever produced.
# MEASURED on this tree, `--engine=vm --no-captures`:
#
#     a*+b            grep -c RX_CUT = 1   '^ *RX_CUT(' = 0   2nd spelling = 0
#     (?>a*)b         grep -c RX_CUT = 1   '^ *RX_CUT(' = 0   2nd spelling = 0
#     (?:a|bc)*+d     grep -c RX_CUT = 1   '^ *RX_CUT(' = 0   2nd spelling = 1
#
# The first two are the CURSOR rung, which is frameless and correctly emits no
# cut; the third is REVDET, which cuts in the second spelling only. A rule
# spelled "the artifact contains RX_CUT" is green on all three and would be
# green on a compiler that emitted no cut at all.

AG='--features atomic-groups'
agcuts() { grep -c '^ *RX_CUT(' "$1"; }          # spelling 1: the macro call
agrv()   { grep -cE '^ *run->resume_depth = rx_rv[0-9]+_frame_mark;' "$1"; }  # spelling 2

# --- rule 1: THE CEILING, on ITS FOUR READERS, scoped to nclamp > 0 --------
#
# The prefilter is the capture-erased DFA. For a CUT-bearing pattern it
# therefore answers for the UNCUT language (src/ir/nfa.c lowers an atomic body
# transparently), and for a LOOKAROUND-bearing pattern it answers for the
# lookaround-ERASED language (nfa.c's A_LOOK arm is an epsilon). Both times the
# window's span END stops being a bound on the real match's end, and both times
# `v.mrl_win` in src/gen/emit_vm.c switches the MRL ceiling off.
#
# ONE CHECK, TWO MODULES, and that is deliberate: lookaround_design.md §5.6(3)
# says this module "extends the same assertion rather than adding a parallel
# one". The predicate differs by one conjunct; the thing being asserted — that
# every reader of `v.mrl_win` agrees with every other — does not. So the
# assertion is a FUNCTION and each module supplies a fixture.
#
# FOUR READERS, AND THE FOUR-NESS IS R31 E3's FINDING. The design's first form
# asserted on the STAMP alone, and the stamp is read from `v.mrl_win` while the
# lines that BUILD the ceiling were gated on `prefn` and `v.nclamp > 0` and
# never on that flag. MEASURED on this tree by making exactly that half-done
# edit — the stamp reading the predicate, the two emission sites reading the
# raw prefilter flag:
#
#     half-done edit : stamp "subject-end"   window[0][1] assignments left: 2
#     as shipped     : stamp "subject-end"   window[0][1] assignments left: 0
#
# 1(b) is GREEN on the bug. A check that agrees with the bug is worse than no
# check, so the two BUILDERS are asserted too (1(a)) — and so is `--emit-ir`'s
# PRUNING description (1(d)), the FOURTH reader, which lookaround_design.md
# §9.3 S-LA13 names and which no check covered before wave E.
#
# SCOPED TO `nclamp > 0`, which is R31 C5: `RX_VM_PRUNE_CEILING` is
# THREE-valued, and with `nclamp == 0` an artifact stamps "none", declares no
# `window_end` local and has no ceiling to get wrong. Over the design's own 46
# R3a patterns the histogram is {prefilter-window 42, none 4}, so an unscoped
# rule would be RED on four CORRECT artifacts. Each fixture below is chosen
# BECAUSE it clamps, and the check asserts that it does before asserting
# anything else — a fixture that stopped clamping would make this rule vacuous
# rather than failing.

ceil_win_sites() { grep -c 'window_end = (size_t)window\[0\]\[1\]' "$1"; }
ceil_stamp()     { sed -n 's/.*RX_VM_PRUNE_CEILING "\(.*\)"/\1/p' "$1"; }
# The --emit-ir description's prefilter-window form, verbatim from emit_vm.c.
ceil_ir_win()    { grep -c 'ceiling: min(subject_length, prefilter window end)' "$1"; }

# ceil_drop <tag> <features> <fixture> <hazard sentence>
#   the DROP direction: a clamping artifact whose pattern carries the
#   suppressing construct must have NO ceiling, on all four readers.
ceil_drop() {
    local tag="$1" feats="$2" pat="$3" haz="$4"
    local c="$WORKDIR/ceil_drop_$tag.c" ir="$WORKDIR/ceil_drop_$tag.ir"
    if ! "$PCREC" $feats -p rx -o "$c" -- "$pat" >/dev/null 2>&1; then
        bad "[$tag rule 1]: pcrec failed to compile the fixture '$pat'"
        return
    fi
    "$PCREC" $feats -p rx --emit-ir -- "$pat" > "$ir" 2>&1
    local stamp win irwin
    stamp="$(ceil_stamp "$c")"; win=$(ceil_win_sites "$c"); irwin=$(ceil_ir_win "$ir")
    if [ "$stamp" = "none" ]; then
        bad "[$tag rule 1]: the fixture '$pat' stamps \"none\" (nclamp == 0), so it has no ceiling to get wrong and this rule is measuring NOTHING. Pick a clamping fixture — C5 measured the R3a family at {prefilter-window 42, none 4} and this rule is only meaningful on the first population"
    elif [ "$win" -ne 0 ]; then
        bad "[$tag rule 1(a)]: '$pat' still assigns window_end from the prefilter's window END ($win sites). $haz"
    elif [ "$stamp" != "subject-end" ]; then
        bad "[$tag rule 1(b)]: '$pat's RX_VM_PRUNE_CEILING reads \"$stamp\", expected \"subject-end\". The stamp must describe the code beside it; E3's defect was exactly the two disagreeing"
    elif [ "$irwin" -ne 0 ]; then
        bad "[$tag rule 1(d)]: '$pat's --emit-ir PRUNING description still reads \"min(subject_length, prefilter window end)\" while the emitted code carries no such ceiling. That description is the FOURTH reader of v.mrl_win (S-LA13), and a listing that disagrees with the artifact is how E3's defect was missed the first time"
    else
        ok "[$tag rule 1]: a CLAMPING artifact carrying the construct drops the prefilter's window END as its MRL ceiling — asserted on ALL FOUR readers of v.mrl_win (0 window[0][1] assignments in the two BUILDERS, the stamp reads \"subject-end\", and --emit-ir's description agrees), because a half-done edit satisfies any one alone"
    fi
}

# ceil_keep <tag> <features> <fixture>
#   the OTHER direction, and without it ceil_drop would be green on an emitter
#   that had switched the ceiling off for EVERY pattern — losing D51 ruling 1's
#   whole optimisation on the entire corpus while changing no answer.
ceil_keep() {
    local tag="$1" feats="$2" pat="$3"
    local c="$WORKDIR/ceil_keep_$tag.c" ir="$WORKDIR/ceil_keep_$tag.ir"
    if ! "$PCREC" $feats -p rx -o "$c" -- "$pat" >/dev/null 2>&1; then
        bad "[$tag rule 1c]: pcrec failed to compile the free fixture '$pat'"
        return
    fi
    "$PCREC" $feats -p rx --emit-ir -- "$pat" > "$ir" 2>&1
    local stamp win irwin
    stamp="$(ceil_stamp "$c")"; win=$(ceil_win_sites "$c"); irwin=$(ceil_ir_win "$ir")
    if [ "$stamp" = "prefilter-window" ] && [ "$win" -ge 1 ] && [ "$irwin" -ge 1 ]; then
        ok "[$tag rule 1c]: the CONSTRUCT-FREE twin '$pat' KEEPS its prefilter-window ceiling ($win assignment sites, stamp \"prefilter-window\", --emit-ir agrees) — the suppression is scoped to artifacts that carry the construct, not applied to everything"
    else
        bad "[$tag rule 1c]: the construct-free twin '$pat' stamps \"$stamp\" with $win window[0][1] assignments and $irwin prefilter-window listing lines, expected \"prefilter-window\", >= 1 and >= 1. The suppression must not cost the ceiling on patterns that do not carry the construct"
    fi
}

# [M6.4.2] the ATOMIC pair. atomic_groups_design.md §4.4 H3.
ceil_drop 'M6.4-ATOMIC' "$AG" 'x*(?>a|ab)c|abcd' \
    "The prefilter answers for the UNCUT language, so that number is not a bound on this match's end — '(?>a|ab)c|abcd' on \"abcd\" is (0,4) and its uncut twin is (0,3), and a ceiling of 3 prunes the real match away silently"
# The twin CAPTURES, because a capture-free pattern with no cut compiles to a
# pure DFA and has no VM ceiling to keep. `(x)*` is the same quantifier the cut
# fixture carries, with a group around it so `forces_captures` selects the VM
# and the hybrid's prefilter is live.
ceil_keep 'M6.4-ATOMIC' '' '(x)*(?:a|ab)c|abcd'

# [M6.6.2 wave E] the LOOKAROUND pair. lookaround_design.md §5.6.
# THE FIXTURE IS §5.5's MEASURED WITNESS, not an invention: it is one of the 16
# shapes the design's sweep found carrying a LIVE "prefilter-window" ceiling AND
# a window end strictly below the true match's end, and before wave E landed the
# predicate this exact artifact answered NOMATCH on all three of its subjects.
# Its erasure is the twin below, which is the pattern the prefilter actually
# compiles — so the two fixtures are the two halves of one measurement.
ceil_drop 'M6.6-LOOKAROUND' '--features lookaround' '((?:a(?!q)|aq)(?:xy){0,4}q)' \
    "The prefilter answers for the lookaround-ERASED language (nfa.c's A_LOOK arm is an epsilon), so that number is not a bound on this match's end — '((?:a(?!q)|aq)(?:xy){0,4}q)' on \"aqq\" is (0,3) while the erasure '((?:a|aq)(?:xy){0,4}q)' anchored there ends at 2, and a ceiling of 2 prunes the real match away silently (tests/lookaround/prefilter.rxt is the corpus half of this)"
ceil_keep 'M6.6-LOOKAROUND' '' '((?:a|aq)(?:xy){0,4}q)'

# --- rule 2: -fno-possessify STILL EMITS A WRITTEN CUT ----------------------
#
# §3.2 RULE 2: the module never writes `Ast.possessive`, so `-fno-possessify`
# — which denies possessify's REWRITE — cannot reach a possessive the USER
# wrote. Storing the module's semantics in that field would make an
# optimisation flag a MISCOMPILER, which is sabotage row S92.
#
# SCOPED TO AN UNDISCHARGED POSSESSIVE, and the scoping is load-bearing rather
# than cautious (§5.4's carve-out): on a DISCHARGED possessive there is
# correctly no cut under the flag, because the discharge deleted the node while
# `run_possessify` did not run to re-mark the quantifier. `(?:a|ab){1,3}+c`'s
# §2.2 verdict is NEGATIVE — its body's iteration can end in two places — so
# the discharge declines it and the cut must survive.
if "$PCREC" $AG -p rx --engine=vm --no-captures -fno-possessify \
        -o "$WORKDIR/ag_np.c" -- '(?:a|ab){1,3}+c' >/dev/null 2>&1; then
    ag_c=$(agcuts "$WORKDIR/ag_np.c"); ag_r=$(agrv "$WORKDIR/ag_np.c")
    if [ $((ag_c + ag_r)) -ge 1 ]; then
        ok "[M6.4-ATOMIC rule 2] (§3.2 RULE 2): '(?:a|ab){1,3}+c' under -fno-possessify still emits a cut ($ag_c RX_CUT call sites + $ag_r second-spelling) — the flag denies possessify's REWRITE and cannot reach a possessive the USER wrote"
    else
        bad "[M6.4-ATOMIC rule 2]: '(?:a|ab){1,3}+c' under -fno-possessify emits NO cut in either spelling. The module has stored its semantics somewhere -fno-possessify can deny, which makes an optimisation flag a miscompiler: the artifact now answers the UNCUT language"
    fi
else
    bad "[M6.4-ATOMIC rule 2]: pcrec failed to compile '(?:a|ab){1,3}+c' under -fno-possessify"
fi

# --- rule 3: THE MARK IS SET BEFORE THE BODY PUSHES ANYTHING ---------------
#
# CUT-INV clause 2, and the sharpest structural property in the lowering: every
# frame below the mark was pushed BEFORE the body's first trail entry, which is
# what makes "discard the frames and leave the trail alone" safe. Sabotage row
# S90 moves the `RX_SET` after the body's first `RX_PUSH`.
#
# THE SECOND CLAUSE THE DESIGN FIRST PROPOSED IS DELETED — R31 C15. It asserted
# that every `RX_CUT(k)` is "textually reachable only from labels after it",
# and this VM dispatches by COMPUTED GOTO, where textual position carries no
# reachability at all. An unfalsifiable clause is worse than an absent one.
if "$PCREC" $AG -p rx --engine=vm --no-captures \
        -o "$WORKDIR/ag_mark.c" -- '(?>a|ab)c' >/dev/null 2>&1; then
    ag_set=$(grep -n 'RX_SET(RX_SLOT_CUT_MARK' "$WORKDIR/ag_mark.c" | head -1 | cut -d: -f1)
    ag_push=$(grep -n '^ *RX_PUSH' "$WORKDIR/ag_mark.c" | head -1 | cut -d: -f1)
    ag_cut=$(agcuts "$WORKDIR/ag_mark.c")
    if [ -z "$ag_set" ]; then
        bad "[M6.4-ATOMIC rule 3]: '(?>a|ab)c' emits no RX_SET of a cut mark at all — the group records no resume depth, so its cut has nothing to cut back TO"
    elif [ -z "$ag_push" ]; then
        bad "[M6.4-ATOMIC rule 3]: '(?>a|ab)c' emits no RX_PUSH at all, so this rule is measuring nothing — the fixture's alternation must push a choice point for the cut to have something to discard"
    elif [ "$ag_set" -ge "$ag_push" ]; then
        bad "[M6.4-ATOMIC rule 3]: '(?>a|ab)c' sets its cut mark at line $ag_set, AFTER the body's first RX_PUSH at line $ag_push. CUT-INV clause 2 requires the mark to be recorded before ANY frame the body pushes, or the cut truncates to a depth that already includes some of them"
    elif [ "$ag_cut" -lt 1 ]; then
        bad "[M6.4-ATOMIC rule 3]: '(?>a|ab)c' records a cut mark and never CUTS to it ($ag_cut call sites) — a dead slot and the uncut language, which is K29's shape one construct over"
    else
        ok "[M6.4-ATOMIC rule 3] (CUT-INV clause 2): '(?>a|ab)c' sets its cut mark (line $ag_set) BEFORE the body's first RX_PUSH (line $ag_push) and cuts to it ($ag_cut call sites)"
    fi
else
    bad "[M6.4-ATOMIC rule 3]: pcrec failed to compile '(?>a|ab)c'"
fi

# --- rule 4: A DISCHARGED PATTERN EMITS NO CUT AND NO VM -------------------
#
# TWO INDEPENDENT FACTS, and K29 is why they have to be asserted separately: an
# artifact can allocate the mark SLOT and emit no CUT (that was K29 exactly,
# for years), so "no slot" and "no cut" are not each other's proxy.
#
# MEASURED on this tree, --no-captures:
#     a*+b        RX_ENGINE defines = 0   RX_SLOT_CUT_MARK = 0
#     (?>a|ab)c   RX_ENGINE defines = 2   RX_SLOT_CUT_MARK = 2
if "$PCREC" $AG -p rx --no-captures -o "$WORKDIR/ag_dis.c" -- 'a*+b' >/dev/null 2>&1; then
    ag_slot=$(grep -c 'RX_SLOT_CUT_MARK' "$WORKDIR/ag_dis.c")
    ag_c=$(agcuts "$WORKDIR/ag_dis.c"); ag_r=$(agrv "$WORKDIR/ag_dis.c")
    ag_eng=$(grep -c '#define RX_ENGINE' "$WORKDIR/ag_dis.c")
    if [ "$ag_slot" -ne 0 ]; then
        bad "[M6.4-ATOMIC rule 4]: the DISCHARGED 'a*+b' still allocates a cut-mark slot ($ag_slot references). Its §2.2 verdict is positive, so src/opt/atomic.c must have deleted the A_ATOMIC before emission"
    elif [ $((ag_c + ag_r)) -ne 0 ]; then
        bad "[M6.4-ATOMIC rule 4]: the DISCHARGED 'a*+b' still emits a cut ($ag_c RX_CUT call sites + $ag_r second-spelling)"
    elif [ "$ag_eng" -ne 0 ]; then
        bad "[M6.4-ATOMIC rule 4]: the DISCHARGED, CAPTURE-FREE 'a*+b' still carries a VM ($ag_eng RX_ENGINE defines). The discharge deletes the node BEFORE SR-8's consultation runs, so nothing forces the VM and the artifact must be a pure DFA — that per-pattern split is the whole payoff, and its absence means the discharge ran too late or not at all"
    else
        ok "[M6.4-ATOMIC rule 4] (§5.3): the DISCHARGED capture-free 'a*+b' emits no cut-mark slot, no cut in EITHER spelling, and no VM at all — a pure DFA artifact. The slot and the cut are asserted separately because K29 shows an artifact can have one without the other"
    fi
else
    bad "[M6.4-ATOMIC rule 4]: pcrec failed to compile 'a*+b'"
fi

# --- rule 5: ONE ASSERTION PER DISPATCH PATH, BOTH PREFERENCES -------------
#
# `vm_rep` has FIVE dispatch paths and the design's first form named THREE; the
# one it missed emitted NO CUT AT ALL, which is K29. Without a per-path check a
# future rung change silently drops a path again, which is exactly how K29
# happened.
#
# THE REQUIREMENT IS NOT "EVERY PATH ENDS IN A CUT". That is wrong for the
# CURSOR rung, whose possessive arm is FRAMELESS — `vm_cursor_rep` sets `low`,
# `retry` and `again` to -1, so there is no slot, no label and no push, and
# nothing a cut would remove. The requirement is CUT-EQUIVALENCE: emit a cut in
# EITHER spelling, or provably push no frame.
#
# BOTH PREFERENCES PER PATH, which is R31's re-check N1: the proof-gated
# population these witnesses are drawn from is NOT the population the LIFT
# creates, and the cursor rung SATISFIES cut-equivalence while answering the
# wrong language on a lazy body. A greedy witness alone would have been green
# on the lift that miscompiles 7 of 8 lazy cells. The LAZY witnesses take the
# general shape (rung stamp plus the group's own cut), which is what "the
# carve-out fired" looks like from outside.
ag_paths=0; ag_pathbad=0
ag_path() {  # ag_path <label> <pattern> <expect-rungs-mask> <min-cut> <min-2nd> <max-push>
    local lbl="$1" pat="$2" want="$3" mincut="$4" min2="$5" maxpush="$6"
    local f="$WORKDIR/ag_path.c" rungs c r p
    if ! "$PCREC" $AG -p rx --engine=vm --no-captures -o "$f" -- "$pat" >/dev/null 2>&1; then
        bad "[M6.4-ATOMIC rule 5/$lbl]: pcrec failed to compile '$pat'"
        ag_pathbad=$((ag_pathbad + 1)); return
    fi
    rungs="$(sed -n 's/^#define RX_VM_RUNGS \(.*\)u$/\1/p' "$f")"
    c=$(agcuts "$f"); r=$(agrv "$f"); p=$(grep -c '^ *RX_PUSH' "$f")
    ag_paths=$((ag_paths + 1))
    if [ "$rungs" != "$want" ]; then
        bad "[M6.4-ATOMIC rule 5/$lbl]: '$pat' took rung mask $rungs, expected $want — the dispatch moved, so whatever this row asserts below is about a different path than the one it names"
        ag_pathbad=$((ag_pathbad + 1)); return
    fi
    if [ "$c" -lt "$mincut" ] || [ "$r" -lt "$min2" ]; then
        bad "[M6.4-ATOMIC rule 5/$lbl]: '$pat' emits $c RX_CUT call sites and $r second-spelling cuts, expected at least $mincut and $min2. Cut-equivalence: this path pushes frames, so it owes a cut in one spelling or the other"
        ag_pathbad=$((ag_pathbad + 1)); return
    fi
    if [ "$maxpush" -ge 0 ] && [ "$p" -gt "$maxpush" ]; then
        bad "[M6.4-ATOMIC rule 5/$lbl]: '$pat' emits $p RX_PUSH sites, expected at most $maxpush. This path claims cut-equivalence by pushing NOTHING, and it is pushing"
        ag_pathbad=$((ag_pathbad + 1)); return
    fi
    ok "[M6.4-ATOMIC rule 5/$lbl]: '$pat' -> rungs $rungs, $c RX_CUT call sites, $r second-spelling, $p pushes"
}
# CURSOR: frameless. NO cut and NO push — cut-equivalent by pushing nothing.
ag_path "cursor-greedy"   '(?>a*)b'                 0x1  0 0 0
# CURSOR, LAZY: the carve-out fires, so this is the GENERAL shape — a rung with
# no collapse (the cut is the group's own, not the rung's).
ag_path "cursor-lazy"     '(?>a*?)b'                0x1  1 0 -1
ag_path "frames-bounded-greedy" '(?>(?:ab|b){1,3})c'      0x2  1 0 -1
ag_path "frames-bounded-lazy"   '(?>(?:ab|b){1,3}?)c'     0x2  1 0 -1
ag_path "frames-unbounded-greedy" '(?>(?:ab|b)*)c'        0x4  1 0 -1
ag_path "frames-unbounded-lazy"   '(?>(?:ab|b)*?)c'       0x4  1 0 -1
# REVDET: cuts in the SECOND SPELLING ONLY. A rule matching `RX_CUT` alone
# reports a confident zero here — vm_cut's own header records a probe that did.
ag_path "revdet-greedy"   '(?>(?:a|bc)*)d'          0x8  0 1 -1
ag_path "revdet-lazy"     '(?>(?:a|bc)*?)d'         0x8  1 1 -1
ag_path "counter-bounded-greedy" '(?>(?:ab|b){8,12})c'    0x10 1 0 -1
ag_path "counter-bounded-lazy"   '(?>(?:ab|b){8,12}?)c'   0x10 1 0 -1
# COUNTER, UNBOUNDED: K29's path. It emitted NEITHER spelling before [M6.4.2]
# — stamped POSSESSIVE, allocated and WROTE the mark, and read it nowhere.
ag_path "counter-unbounded-greedy" '(?>(?:ab|b){8,})c'    0x10 1 0 -1
ag_path "counter-unbounded-lazy"   '(?>(?:ab|b){8,}?)c'   0x10 1 0 -1
if [ "$ag_paths" -ge 12 ] && [ "$ag_pathbad" -eq 0 ]; then
    ok "[M6.4-ATOMIC rule 5] (§3.2.1): all $ag_paths dispatch-path witnesses answered — six paths x both preferences, each naming which cut-equivalence answer its path gives"
else
    bad "[M6.4-ATOMIC rule 5]: only $ag_paths path witnesses ran ($ag_pathbad failed); the per-path coverage this rule exists for is incomplete"
fi

# --- rule 5b: THE SUFFIX SPELLING REPRODUCES THE GROUP SPELLING ------------
#
# `X q+` is `(?>X q)` — PCRE2's own definition, and src/parse/parse.c desugars
# to the same tree. So the two must produce the SAME artifact, and that is a
# far stronger statement than "both compile": it says the lift routes a written
# possessive onto exactly the rung the proof-gated one takes, with the same
# slots, the same pushes and the same cuts.
ag_eq=0; ag_eqbad=0
# Written as EXPLICIT PAIRS rather than derived by wrapping, because the two
# spellings do not bracket the same text: `a*+b` is `(?>a*)b`, NOT `(?>a*b)`.
# A derivation that wrapped the whole pattern would compare a different
# construct and call the difference a failure — measured, on the first run of
# this rule.
#
# TAB-SEPARATED, and the separator is not arbitrary: the first version used
# `|`, which is ALTERNATION, so `${agp%%|*}` cut `(?:ab|b){1,3}+c` down to
# `(?:ab` and five of the six pairs silently vanished into the `|| continue`
# below. The floor caught it (1 pair against a floor of 6) — which is what
# floors on a generated population are for.
#
# THE COMPARISON NORMALISES TWO AXES AND NOTHING ELSE. Every artifact embeds
# its own pattern text (the header comment and `rx_info.pattern`) and its own
# header name, and those MUST differ between two spellings of one construct.
# What must not differ is the machinery, so those lines are dropped and
# everything else is compared byte for byte.
ag_strip() { grep -vE '^( \*     |/\* Generated by pcrec\.|#include "|    \.pattern(_len)? = )' "$1"; }
while IFS=$'\t' read -r ag_poss ag_grp; do
    [ -n "$ag_poss" ] || continue
    "$PCREC" $AG -p rx --engine=vm --no-captures -o "$WORKDIR/ag_s.c" -- "$ag_poss" >/dev/null 2>&1 || continue
    "$PCREC" $AG -p rx --engine=vm --no-captures -o "$WORKDIR/ag_g.c" -- "$ag_grp"  >/dev/null 2>&1 || continue
    ag_eq=$((ag_eq + 1))
    ag_strip "$WORKDIR/ag_s.c" > "$WORKDIR/ag_s.stripped"
    ag_strip "$WORKDIR/ag_g.c" > "$WORKDIR/ag_g.stripped"
    if ! cmp -s "$WORKDIR/ag_s.stripped" "$WORKDIR/ag_g.stripped"; then
        ag_eqbad=$((ag_eqbad + 1))
        bad "[M6.4-ATOMIC rule 5b]: '$ag_poss' and '$ag_grp' emit DIFFERENT C. PCRE2 defines the suffix AS the group spelling and parse.c desugars to the same tree, so any difference is the lift routing one of them somewhere the other does not go: $(diff "$WORKDIR/ag_s.stripped" "$WORKDIR/ag_g.stripped" | head -4 | tr '\n' ' ')"
    fi
done <<AGPAIRS
a*+b	(?>a*)b
(?:ab|b){1,3}+c	(?>(?:ab|b){1,3})c
(?:ab|b)*+c	(?>(?:ab|b)*)c
(?:a|bc)*+d	(?>(?:a|bc)*)d
(?:ab|b){8,12}+c	(?>(?:ab|b){8,12})c
(?:ab|b){8,}+c	(?>(?:ab|b){8,})c
AGPAIRS
if [ "$ag_eq" -ge 6 ] && [ "$ag_eqbad" -eq 0 ]; then
    ok "[M6.4-ATOMIC rule 5b] (§3.2 RULE 1): all $ag_eq suffix/group spelling pairs emit BYTE-IDENTICAL C across all six dispatch paths — the desugaring is real at the emitter, not only at the parser"
else
    bad "[M6.4-ATOMIC rule 5b]: $ag_eqbad of $ag_eq spelling pairs differ (floor 6 pairs)"
fi

# --- rule 5c: PRE-PASS AND EMITTER AGREE ABOUT SLOTS -----------------------
#
# E4/S98's detector, generalised. `vm_count_slots` allocates the cut-mark slot
# and MUST agree with the emitter exactly; when they disagree the mark lands on
# another family's slot and two live loops share one. FOUND THIS WAY during
# [M6.4.2]: with RULE 3's condition-(d) decline in `vm_rep` alone, `-fno-
# possessify '(?>(?:a|bc){2})d'` emitted `RX_SET(RX_SLOT_REVDET0_ENTRY, ...)`
# and `RX_CUT(2)` onto the revdet loop's OWN entry slot.
#
# The signal is read off the ARTIFACT: every `RX_CUT(n)` must name a slot the
# legend declares as a CUT MARK. A raw `RX_SET(<digit>` is the same defect seen
# from the other side — `vm_slot_name` could not resolve the slot at all.
ag_slots=0; ag_slotbad=0
for agf in '' '-fno-possessify' '-fno-revdet' '-fno-counter'; do
    for agp in '(?>a*)b' '(?>(?:a|bc){2})d' '(?>(?:ab|b){8,})c' '(?>(?:a|bc)*)d' \
               '(?>(?:ab|b){1,3})c' '(?>a|ab)c' '(?>ab)+c' '(?>(?:a*)*)b'; do
        "$PCREC" $AG -p rx --engine=vm --no-captures $agf -o "$WORKDIR/ag_sl.c" \
            -- "$agp" >/dev/null 2>&1 || continue
        ag_slots=$((ag_slots + 1))
        if grep -qE '^ *RX_SET\([0-9]' "$WORKDIR/ag_sl.c"; then
            ag_slotbad=$((ag_slotbad + 1))
            bad "[M6.4-ATOMIC rule 5c]: '$agp' [$agf] emits an RX_SET to a RAW SLOT NUMBER — vm_slot_name could not resolve it, so the emitter asked for a slot outside every family vm_count_slots counted"
            continue
        fi
        for ag_n in $(grep -oE '^ *RX_CUT\([0-9]+' "$WORKDIR/ag_sl.c" | grep -oE '[0-9]+' | sort -u); do
            grep -qE "^#define RX_SLOT_CUT_MARK[0-9]+ +$ag_n\$" "$WORKDIR/ag_sl.c" || {
                ag_slotbad=$((ag_slotbad + 1))
                bad "[M6.4-ATOMIC rule 5c]: '$agp' [$agf] emits RX_CUT($ag_n) where slot $ag_n is NOT a cut mark in the legend — the pre-pass and the emitter disagree about the slot map, so the cut is truncating to whatever another family stored there"
            }
        done
    done
done
if [ "$ag_slots" -ge 30 ] && [ "$ag_slotbad" -eq 0 ]; then
    ok "[M6.4-ATOMIC rule 5c] (§3.2.5/E4): $ag_slots artifacts across 8 shapes x 4 flag modes — every RX_CUT names a slot the legend declares a CUT MARK, and no RX_SET reaches a slot vm_slot_name cannot resolve"
else
    bad "[M6.4-ATOMIC rule 5c]: $ag_slotbad of $ag_slots artifacts have a pre-pass/emitter slot disagreement (floor 30 artifacts)"
fi

# ===========================================================================
# [DD-14 RECURSION] THE SUBROUTINE CALL: the two claims no .rxt cell can make
# ===========================================================================
#
# RULE 1 (design §5.8, sabotage row S166) -- THE `goto *` RELATION.
#
# `src/gen/emit_vm.c`'s own opening comment states, as a design decision, that
# there is "exactly ONE indirect jump in the whole function -- the `goto *` at
# the fail label, which fires once per backtrack and never per byte". `RX_RETURN`
# is a SECOND, and design §5.8 amends the invariant to a RELATION rather than a
# constant:
#
#     `goto *` count == 1 (the fail label) + one per emitted SHARED CALLEE BODY
#
# A CONSTANT WOULD BE WRONG IN BOTH DIRECTIONS and R34's LENS2-5 measured it:
# a call-free artifact is 1, a pattern calling ONE group is 2, a pattern
# calling THREE DISTINCT groups is 4 however many call SITES there are (the
# sites share the body), and a wave-G fully-spliced artifact is back to 1. A
# hard-coded "two" fires on three of those four.
#
# [DD-14 WAVE F] THE LAST FOUR FIXTURES ARE THE `(?(DEFINE)` SPELLING, and
# they are here because D71 item 4's claim is that the DEFINE lowers to the
# `{0}`-callee shape and adds NO MECHANISM. If that claim were false, the
# relation is where it would break first: a DEFINE that emitted its body
# lexically would change the count, and one that emitted a region per call
# SITE rather than per group would too. `(?(DEFINE)(a))b` -- a definition
# NOBODY CALLS -- is the floor of the set and MEASURED at 1: the definition
# costs no region at all, which is the same thing `X{0}` has always done.
#
# THE RELATION IS ASSERTIBLE ONLY BECAUSE THE `goto *` IS WRITTEN INLINE. The
# design's §5.1 sketches `RX_RETURN` as a MACRO, which would put one `goto *`
# in the definition and none at the uses -- making the artifact's count
# `1 + (has_calls ? 1 : 0)` and this rule unstateable. Emitting it per region
# is a deliberate deviation recorded at `vm_region`, and this check is what it
# buys.
for dd14_row in \
    '1|(a)b' \
    '2|(a)(?1)' \
    '2|(a)(?1)(?1)(?1)' \
    '4|(a)(b)(c)(?1)(?2)(?3)' \
    '2|a(?R)?b' \
    '2|(?(DEFINE)(a))(?1)b' \
    '4|(?(DEFINE)(a)(b)(c))(?1)(?2)(?3)' \
    '1|(?(DEFINE)(a))b' \
    '2|(?(DEFINE)(?<w>a(?&w)?b))(?&w)' ; do
    dd14_want="${dd14_row%%|*}"
    dd14_pat="${dd14_row#*|}"
    if "$PCREC" -p rx --features all --engine=vm -o "$WORKDIR/dd14.c" -- "$dd14_pat" >/dev/null 2>&1; then
        dd14_got=$(grep -c 'goto \*' "$WORKDIR/dd14.c")
        if [ "$dd14_got" -ne "$dd14_want" ]; then
            bad "[DD-14-RECURSION rule 1] (§5.8): '$dd14_pat' emits $dd14_got 'goto *' and the relation requires $dd14_want (1 for the fail label plus one per DISTINCT called group). A count that is too HIGH means a region was emitted per call SITE instead of per group; too LOW means a region's return was folded into something shared, which §6.3 forbids -- the body may be shared, the EXIT may never be"
        else
            ok "[DD-14-RECURSION rule 1] (§5.8): '$dd14_pat' emits exactly $dd14_want 'goto *' -- 1 + the number of emitted shared callee bodies"
        fi
    else
        bad "[DD-14-RECURSION rule 1]: pcrec failed to compile the fixture '$dd14_pat'"
    fi
done

# RULE 2 (design §9.1, sabotage rows S143..S165 collectively) -- A CALL-FREE
# ARTIFACT CARRIES NONE OF THIS MODULE'S MACHINERY.
#
# The resume frame gains TWO FIELDS, `RX_PUSH` gains a line, the fail label
# gains a line, both reset functions gain a line, and `RX_CALL` appears -- all
# of it gated on ONE flag (`Vm.has_calls`, i.e. `cx->callgraph != NULL`). That
# is what makes §9.1's byte-identity claim STRUCTURAL rather than something an
# identity sweep has to discover, and it is checked here in the cheap
# direction: the four names must be ABSENT from a call-free VM artifact and
# PRESENT in a call-bearing one, in the same run, so a check that had stopped
# looking at anything cannot pass.
if "$PCREC" -p rx --features all --engine=vm -o "$WORKDIR/dd14_free.c" -- '(a)(b)+c' >/dev/null 2>&1 \
   && "$PCREC" -p rx --features all --engine=vm -o "$WORKDIR/dd14_call.c" -- '(a)(?1)' >/dev/null 2>&1; then
    dd14_leak=0
    for dd14_tok in 'call_top' 'call_ret' 'RX_CALL' 'CALL_TOP_NONE'; do
        if grep -q "$dd14_tok" "$WORKDIR/dd14_free.c"; then
            dd14_leak=$((dd14_leak + 1))
            bad "[DD-14-RECURSION rule 2] (§9.1): the CALL-FREE artifact '(a)(b)+c' mentions '$dd14_tok'. Every byte this module adds is gated on ONE flag so a call-free pattern's emitted C is what it always was; a leak here is a byte-identity failure the corpus cannot see, because no answer changes"
        fi
        if ! grep -q "$dd14_tok" "$WORKDIR/dd14_call.c"; then
            dd14_leak=$((dd14_leak + 1))
            bad "[DD-14-RECURSION rule 2]: the CALL-BEARING artifact '(a)(?1)' does NOT mention '$dd14_tok' -- the absence check above would then be vacuous, which is this directory's own recurring failure shape"
        fi
    done
    [ "$dd14_leak" -eq 0 ] && ok "[DD-14-RECURSION rule 2] (§9.1): a call-FREE VM artifact carries none of call_top / call_ret / RX_CALL / CALL_TOP_NONE, and a call-BEARING one carries all four -- both directions in one run"
else
    bad "[DD-14-RECURSION rule 2]: pcrec failed to compile one of the two fixtures"
fi

# RULE 3 (wave A2's PASS-ORDERING FINDING, sabotage row S166) -- THE CALLEE
# REGION AND THE LEXICAL OCCURRENCE ARE EMITTED FROM THE SAME NODE.
#
# `Ast.u.call.body` is a CACHE of "which subtree is that group's, IN THE TREE
# THE EMITTER WILL WALK", and `src/opt/altcls.c` REBUILDS nodes rather than
# mutating them -- its `A_CAP` arm does `*r = *a; r->l = body;`, allocating a
# fresh node over the merged class. A `.body` captured at END OF PARSE, where
# design §4.2 and wave A2's `PendingRef` comment both put it, therefore names a
# subtree that is NO LONGER IN THE TREE.
#
# MEASURED ON THIS TREE, by moving `pcrec_callgraph_build` above
# `pcrec_altcls` and diffing the artifacts: on `((?:a|b))(?1)` the LEXICAL
# occurrence emits a merged class test (`(unsigned)(subject[p] - 97) <= 1u`)
# while the CALLEE REGION emits the un-merged two-branch alternation with its
# own `RX_PUSH` and two extra labels -- **two different programs for one
# group** -- and `RX_RESUME_FRAMES` moves 2 -> 3 with it. The ANSWERS are
# unchanged, because `altcls` is answer-preserving in both directions, which is
# exactly why no corpus cell can see this and it needs a structural rule.
#
# THE DISCHARGE WITNESS IS NOT A HAZARD, and measuring that is what stops this
# rule being over-stated: `((?>a)b)(?1)` compiles BYTE-IDENTICALLY under the
# same sabotage, because `pcrec_discharge_atomic` splices by rewriting the
# parent's `->l` IN PLACE, so the `A_CAP` this module binds to keeps its
# identity and sees the discharge. Wave A2 named both passes; only one of them
# rebuilds the node a callee is rooted at.
if "$PCREC" -p rx --features all --engine=vm -o "$WORKDIR/dd14_rb.c" -- '((?:a|b))(?1)' >/dev/null 2>&1; then
    dd14_merges=$(grep -m1 '^#define RX_ALTCLS_MERGES' "$WORKDIR/dd14_rb.c" | awk '{print $3}')
    dd14_push=$(grep -c 'RX_PUSH(' "$WORKDIR/dd14_rb.c")
    if [ "${dd14_merges:-0}" -lt 1 ]; then
        bad "[DD-14-RECURSION rule 3]: '((?:a|b))(?1)' stamps RX_ALTCLS_MERGES ${dd14_merges:-?} -- altcls no longer merges this alternation, so the fixture cannot express the hazard and this rule is measuring nothing"
    elif [ "$dd14_push" -ne 1 ]; then
        bad "[DD-14-RECURSION rule 3]: '((?:a|b))(?1)' emits $dd14_push RX_PUSH( sites, expected 1 (the macro definition alone). altcls merged the only alternation, so NEITHER the lexical occurrence NOR the callee region should need a resume frame -- an extra push means the region was emitted from a STALE u.call.body naming the pre-altcls subtree, i.e. two different programs for one group"
    else
        ok "[DD-14-RECURSION rule 3] (wave A2's pass-ordering finding): '((?:a|b))(?1)' merges its alternation AND emits no resume push in either program -- the callee region and the lexical occurrence come from the same node"
    fi
else
    bad "[DD-14-RECURSION rule 3]: pcrec failed to compile the fixture '((?:a|b))(?1)'"
fi

# RULE 4 ([DD-14] wave F, D71 item 4) -- `(?(DEFINE)X)` AND `(?:X){0}` EMIT
# THE SAME PROGRAM, and this is the rule that makes "one row, zero new
# mechanism" checkable rather than merely asserted.
#
# The port produces an `A_REP` with rmin == rmax == 0 over the parsed body --
# the node `p_rep` builds for `(?:X){0}` -- so every pass below the parser
# sees a shape it already had. If that is true, the two spellings' artifacts
# can differ ONLY in the places the PATTERN TEXT itself appears: the header
# echo, the `#include` of the per-output header, and the byte OFFSET in the
# engine-selection reason (the capture group sits at a different column in the
# two spellings). Everything else -- every label, every frame, every slot,
# every stamped constant -- must be identical byte for byte.
#
# THE NORMALISATION IS DELIBERATELY NARROW: the pattern's own text and any
# `offset N` are erased, and NOTHING ELSE. A rule that filtered more would
# start hiding the differences it exists to find.
#
# AND IT CARRIES ITS OWN POSITIVE CONTROL. A comparison that normalised away
# everything would pass on any two patterns, so a THIRD pattern that is
# genuinely a different program is run through the identical pipeline and must
# NOT compare equal. Without it this rule would go green on a normaliser that
# had quietly started deleting the whole file.
dd14_norm() {   # $1 = artifact, $2 = the pattern text to erase
    # FOUR THINGS ARE ERASED AND NOTHING ELSE, each of them a fact about the
    # pattern's TEXT rather than about the program:
    #   * the pattern verbatim (the header echo and the IR listing),
    #   * the `.pattern` / `.pattern_len` stamp -- one whole line, because the
    #     emitter writes it C-string-escaped (`?` becomes `\?` to keep a
    #     trigraph out of the source) and re-deriving that escaping here would
    #     be a second copy of the emitter's rule,
    #   * any byte OFFSET (the capture group sits at a different column in the
    #     two spellings),
    #   * the `#include` of the per-output header.
    # A fifth erasure would start hiding the differences this rule exists to
    # find, which is what the positive control below is watching for.
    dd14_raw=$(printf '%s' "$2" | sed 's/[][\\.*^$/&|]/\\&/g')
    sed -e "s|$dd14_raw||g" \
        -e 's/^\( *\)\.pattern = ".*",$/\1.pattern = "P",/' \
        -e 's/offset [0-9][0-9]*/offset N/g' \
        -e 's/\.pattern_len = [0-9][0-9]*/.pattern_len = N/' \
        -e 's/^#include ".*\.h"$/#include "H"/' "$1"
}
dd14_zero='(?:(a)){0}(?1)b'
dd14_def='(?(DEFINE)(a))(?1)b'
dd14_ctl='(?:(a)){1}(?1)b'
if "$PCREC" -p rx --features all -o "$WORKDIR/dd14_z.c" -- "$dd14_zero" >/dev/null 2>&1 &&
   "$PCREC" -p rx --features all -o "$WORKDIR/dd14_d.c" -- "$dd14_def"  >/dev/null 2>&1 &&
   "$PCREC" -p rx --features all -o "$WORKDIR/dd14_c.c" -- "$dd14_ctl"  >/dev/null 2>&1; then
    dd14_norm "$WORKDIR/dd14_z.c" "$dd14_zero" > "$WORKDIR/dd14_z.n"
    dd14_norm "$WORKDIR/dd14_d.c" "$dd14_def"  > "$WORKDIR/dd14_d.n"
    dd14_norm "$WORKDIR/dd14_c.c" "$dd14_ctl"  > "$WORKDIR/dd14_c.n"
    if ! cmp -s "$WORKDIR/dd14_z.n" "$WORKDIR/dd14_d.n"; then
        bad "[DD-14-RECURSION rule 4] (D71 item 4): '$dd14_def' and '$dd14_zero' emit DIFFERENT programs once the pattern text and offsets are normalised away -- $(diff "$WORKDIR/dd14_z.n" "$WORKDIR/dd14_d.n" | grep -c '^[<>]') differing lines. The DEFINE lowering has grown a mechanism of its own, which is exactly what 'one row, zero new mechanism' rules out"
    elif cmp -s "$WORKDIR/dd14_z.n" "$WORKDIR/dd14_c.n"; then
        bad "[DD-14-RECURSION rule 4]: THE POSITIVE CONTROL FAILED -- '$dd14_ctl' normalises equal to '$dd14_zero' too, so the normaliser is erasing the program and this rule proves nothing about the DEFINE"
    else
        ok "[DD-14-RECURSION rule 4] (D71 item 4): '$dd14_def' and '$dd14_zero' emit the SAME program byte for byte (pattern text and offsets normalised), while the '{1}' control does not -- the DEFINE really is the {0}-callee shape"
    fi
else
    bad "[DD-14-RECURSION rule 4]: pcrec failed to compile one of the three fixtures"
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
