#!/usr/bin/env bash
# tests/codegen/run_endvar_identity.sh — [M6.2] WAVE A's BYTE-IDENTITY GATE.
#
# THE CLAIM. `\z` adds a THIRD closure view to src/ir/dfa.c's subset
# construction, and assertions_design.md §3.3 claims that costs a `\z`-free
# pattern NOTHING — not "almost nothing", not "nothing measurable": the same
# states, the same tables, the same emitted bytes, BY CONSTRUCTION rather than
# by a `has_z` flag. The construction is one line of canonicalization:
#
#     eolvar = interned iff eolv != base     ; -1 means "same as base"
#     endvar = interned iff endv != EOLV     ; -1 means "same as the EOL view"
#
# With no `\z` in the pattern there is no N_END state, so `end_ok` gates
# nothing, so `endv == eolv` everywhere, so `endvar` is -1 everywhere, so
# `dfa_has_endvar` is false and the emitter takes the pre-wave branch at every
# site.
#
# WHY THE CHECK EXISTS EVEN THOUGH THE PROSE SAYS IT CANNOT FAIL. Because the
# prose said the opposite thing first and was WRONG. The design's first draft
# canonicalized `endvar` against the BASE view and argued zero regression from
# it; the R30 panel (finding E3) showed that makes every eol-differing state
# of every `$`-bearing pattern intern a live `endvar`, so the artifact is not
# byte-identical — the exact opposite of the claim. "X is impossible by
# construction" is precisely the claim a construction check is for, and the
# sabotage row below (S69) restores the refuted form and measures this script
# going red on it.
#
# HOW IT COMPARES, and why not against a pinned historical commit. Same
# reasoning tests/codegen/run_vm_identity.sh states for its own formulation: a
# check that pins a commit has a built-in expiry date and teaches people to
# edit the pin. The permanent form builds a REFERENCE COMPILER from THIS
# tree's own sources with `-DPCREC_NO_ENDVAR` — which compiles the third
# view's INTERNING out and nothing else, so `endvar` is -1 everywhere and the
# emitter reproduces the pre-wave text — and requires byte-identical output
# over the whole corpus. `-DPCREC_NO_TRIE` and run_trie_identity.sh are the
# established shape; this is that shape one view over.
#
# (The one-time literal diff against a compiler built from the pre-wave
# commit WAS run over the whole corpus as landing evidence. It lives in the
# commit message, not here.)
#
# THE POSITIVE CONTROL is not decoration either: if `-DPCREC_NO_ENDVAR` did
# not actually disable anything, every comparison below would trivially agree
# and this script would report a clean bill of health for a knob that does
# nothing. The `\z` patterns are the control — the two builds MUST differ on
# them.
#
# Usage: bash tests/codegen/run_endvar_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "endvar-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the reference compiler ---------------------------------------------
# The source list is FOUND, not globbed at a fixed depth — src/gen/enc/ is two
# levels down and a hand-maintained `src/*/*.c` silently dropped it once
# already (run_trie_identity.sh's own [M5-SEAM] note). A reference compiler
# quietly built from a different source set than the subject is the
# differential going vacuous.
REF="$WORKDIR/pcrec_noendvar"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | sort)"
if [ -z "$REF_SRCS" ]; then
    echo "FAIL: found no compiler sources under $ROOT_DIR/src for the reference build" >&2
    exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_NO_ENDVAR $SANFLAGS \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS \
        2>"$WORKDIR/refbuild.log"; then
    echo "FAIL: could not build the -DPCREC_NO_ENDVAR reference compiler:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    exit 1
fi
if [ -s "$WORKDIR/refbuild.log" ]; then
    echo "FAIL: the -DPCREC_NO_ENDVAR reference build produced warnings:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    fail=$((fail + 1))
fi

# Both builds emit SELF-CONTAINED C to stdout. Writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason that has nothing to do with the third
# view — the trap run_trie_identity.sh and run_vm_identity.sh both document.
#
# `--features all` because this is a pcrec-vs-pcrec BYTE comparison, not an
# oracle differential: the focused-per-module rule (docs/testing.md, Frank
# 2026-08-12) is about attribution and coverage honesty in a differential
# against libpcre2, and neither applies here. What `all` buys is that the
# corpus's own module-gated patterns — including tests/assertions/'s `\A` and
# `\Z` cells, which are `\z`-FREE and must therefore be byte-identical — reach
# the emitter instead of being refused before it.
gen_a() { "$PCREC" --features all -p rx -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx -o - -- "$1" 2>/dev/null; }

# ---- the corpus ----------------------------------------------------------
# Every `pattern` line from every .rxt under tests/, known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move. The
# population grows with the corpus rather than with this script.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content. R24 M-F1 found, named and
# fixed that undercount; assertions_design.md §3.4 reproduced it verbatim in
# an uncommitted one-liner (1030 true, 609 reported, 421 patterns silently
# merged away) after reading the entry that named it. It travels as committed
# tooling here for the same reason.
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

# The split: a pattern MENTIONING `\z` is the control population (the two
# builds must differ), everything else is the identity population. The test is
# on the pattern TEXT rather than on anything pcrec computes, deliberately —
# a split derived from `dfa_has_endvar` would be the check reading its own
# subject's verdict.
grep -F '\z' "$PATFILE" > "$WORKDIR/zpat" || true
grep -vF '\z' "$PATFILE" > "$WORKDIR/nozpat" || true
nz=$(wc -l < "$WORKDIR/zpat")
nn=$(wc -l < "$WORKDIR/nozpat")

if [ "$nn" -lt 100 ]; then
    bad "corpus extraction found only $nn \\z-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nz" -lt 5 ]; then
    bad "corpus extraction found only $nz \\z-bearing patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the positive control ------------------------------------------------
# THE CONTROL IS SCOPED TO THE DFA, and the scoping is a finding rather than a
# convenience. The third view is a property of the SUBSET CONSTRUCTION: the VM
# emitter spells `\z` as a literal `if (pos == n)` and never consults a view
# table at all, so a `\z` pattern that routes to the VM — any capture-bearing
# one, e.g. `(\z)*` — legitimately emits IDENTICAL bytes from both builds.
# Demanding that EVERY compilable `\z` pattern differ was this script's own
# first draft and it failed on exactly that pattern.
#
# So: a `\z` pattern that agrees must be one the DFA never compiled, and the
# artifact says which engine it is in its own `RX_ENGINE` stamp (VM artifacts
# only — a DFA artifact carries no such line, src/gen/CLAUDE.md). That is a
# DIFFERENT fact from the one being measured here, which is why reading it to
# explain a non-difference is legitimate and reading `dfa_has_endvar` would
# not be.
ctl_diff=0; ctl_same_vm=0; ctl_same_dfa=0; ctl_rej=0
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then ctl_rej=$((ctl_rej + 1)); continue; fi
    if [ "$a" != "$b" ]; then
        ctl_diff=$((ctl_diff + 1))
    elif printf '%s' "$a" | grep -q '^#define RX_ENGINE "vm"$'; then
        ctl_same_vm=$((ctl_same_vm + 1))
    else
        ctl_same_dfa=$((ctl_same_dfa + 1))
        echo "  DFA-compiled control did NOT differ: $pat" >&2
    fi
done < "$WORKDIR/zpat"

if [ "$ctl_diff" -ge 5 ] && [ "$ctl_same_dfa" -eq 0 ]; then
    ok "positive control: $ctl_diff DFA-compiled \\z patterns differ between the two builds and 0 agree ($ctl_same_vm agreed and are VM artifacts, where the third view plays no part) — -DPCREC_NO_ENDVAR really disables it, so the identity comparisons below are not vacuous"
else
    bad "positive control: $ctl_diff \\z patterns differ, $ctl_same_dfa DFA-compiled ones AGREE, $ctl_same_vm VM ones agree (expected), $ctl_rej rejected by both. Every DFA-compiled \\z pattern must differ; if none does, the reference knob is dead and this whole check is vacuous."
fi

# ---- the identity sweep --------------------------------------------------
same=0; diff=0; rej=0
: > "$WORKDIR/diffs.txt"
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then rej=$((rej + 1)); continue; fi
    if [ "$a" = "$b" ]; then
        same=$((same + 1))
    else
        diff=$((diff + 1))
        printf '%s\n' "$pat" >> "$WORKDIR/diffs.txt"
    fi
done < "$WORKDIR/nozpat"

if [ "$((same + diff))" -lt 100 ]; then
    bad "only $((same + diff)) \\z-free patterns compiled in both builds — too few to call this a corpus-wide gate"
else
    ok "coverage: $((same + diff)) of $nn \\z-free corpus patterns compiled in both builds and were compared ($rej rejected by both)"
fi

if [ "$diff" -eq 0 ]; then
    ok "endvar identity: $same \\z-free patterns emit BYTE-IDENTICAL C with and without the third closure view"
else
    bad "endvar identity: $diff of $((same + diff)) \\z-free patterns changed emitted bytes. The three-way canonicalization is wrong: \`endvar\` must be interned against the EOL VIEW, not against the base (R30 E3). First offenders:"
    head -20 "$WORKDIR/diffs.txt" >&2
fi

echo
echo "== Summary =="
echo "  identity population   compared $((same + diff))  identical $same  differing $diff  rejected-by-both $rej"
echo "  positive control      differ $ctl_diff  agree-on-DFA $ctl_same_dfa  agree-on-VM $ctl_same_vm  rejected-by-both $ctl_rej"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
