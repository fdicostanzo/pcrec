#!/usr/bin/env bash
# tests/codegen/run_trie_identity.sh — differential codegen check for the M2.8
# alternation prefix trie.
#
# WHY THIS EXISTS (checkpoint review R3, semantics critic F4). The M2 journal
# concluded that M2.8 was NOT structurally testable, because the trie changes
# the NFA and the NFA is not an output. That was wrong. The trie is required to
# be OUTPUT-PRESERVING: subset construction plus minimization must erase the
# difference entirely, so a compiler built with the factoring path switched off
# must emit BYTE-IDENTICAL C. That makes M2.8's two soundness rules checkable
# with no subject strings and no gcc.
#
# It is also a far stronger net than sampling subjects. Breaking the
# disjointness guard shows up on 2 cases in the whole .rxt corpus; here it
# shows up on ~14 patterns in 500, and each failure names the exact pattern
# rather than a subject that happened to hit it.
#
# WHAT THIS DOES AND DOES NOT GUARD. It guards the trie's SOUNDNESS. The
# trie's PRESENCE is guarded by the KEYWORD-SCALE compile-time budget in
# `make bench` (removing the trie is a 15x compile-time regression there) —
# but a soundness check whose two builds were BOTH unfactored would be vacuous,
# so the positive control below re-establishes presence here rather than
# relying on a different target being run.
#
# Usage: bash tests/codegen/run_trie_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, TRIE_N (pattern count, default
#      500), TRIE_SEED (default 20260809), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
N="${TRIE_N:-500}"
SEED="${TRIE_SEED:-20260809}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "trie-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# Both builds are always invoked with `-o -`, which emits SELF-CONTAINED C to
# stdout. Writing to two different paths would emit two different
# `#include "<name>.h"` lines and every single comparison would "differ" for a
# reason that has nothing to do with the trie.
gen_a() { "$PCREC" -p rx -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   -p rx -o - -- "$1" 2>/dev/null; }

# ---- the reference compiler ---------------------------------------------
# -DPCREC_NO_TRIE forces `elig[j] = false` in nfa.c's A_ALT path, i.e. the
# pre-M2.8 unfactored construction. -O0 on purpose: this build is never
# measured, only diffed, and -O0 keeps it under half a second. Warnings stay on
# so #ifdef rot is loud rather than silent.
REF="$WORKDIR/pcrec_notrie"
if ! $CC -O0 -std=gnu11 -Wall -Wextra -Ilib -Isrc -DPCREC_NO_TRIE \
        -o "$REF" "$ROOT_DIR"/cli/main.c "$ROOT_DIR"/src/*/*.c \
        2>"$WORKDIR/refbuild.log"; then
    echo "FAIL: could not build the -DPCREC_NO_TRIE reference compiler:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    exit 1
fi
if [ -s "$WORKDIR/refbuild.log" ]; then
    echo "FAIL: the -DPCREC_NO_TRIE reference build produced warnings:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    fail=$((fail + 1))
fi

# ---- POSITIVE CONTROL ----------------------------------------------------
# Without this the script is a guard that cannot fail: if the trie were
# disabled in the SHIPPED build too, every pattern below would trivially agree
# and this would report a clean bill of health for a deleted optimization.
# That is the exact failure mode R3 found in two guards written the same day.
#
# The control is DETERMINISTIC, not timing-based. `(<all 256 8-bit binary
# strings>){100}` needs ~230k NFA states unfactored — over PCREC_MAX_NFA_STATES
# (131072) — and ~51k factored, comfortably under it. So the two builds fail at
# DIFFERENT STAGES, and the stage is visible in the error text:
#   unfactored -> "pattern too large (NFA exceeds ...)"   (never reaches the DFA)
#   factored   -> "pattern too complex for the DFA engine" (got past the NFA cap)
# Both margins are ~1.75x and ~2.5x, so this is not knife-edge. If either cap
# in src/core/internal.h moves, this fails loudly instead of going quiet.
ctl_pat=$(awk 'BEGIN {
    p = ""
    for (i = 0; i < 256; i++) {
        w = ""; v = i
        for (k = 0; k < 8; k++) { w = sprintf("%d", v % 2) w; v = int(v / 2) }
        p = p (i ? "|" : "") w
    }
    printf "(%s){100}", p
}')
ctl_a="$("$PCREC" -p rx -o - -- "$ctl_pat" 2>&1 >/dev/null | head -1)"
ctl_b="$("$REF"   -p rx -o - -- "$ctl_pat" 2>&1 >/dev/null | head -1)"
case "$ctl_a" in *"DFA engine"*) ca=factored ;; *"NFA exceeds"*) ca=unfactored ;; *) ca="other:$ctl_a" ;; esac
case "$ctl_b" in *"DFA engine"*) cb=factored ;; *"NFA exceeds"*) cb=unfactored ;; *) cb="other:$ctl_b" ;; esac
if [ "$ca" = factored ] && [ "$cb" = unfactored ]; then
    ok "positive control: the shipped build really factors (its NFA clears the cap the unfactored build dies on)"
else
    bad "positive control: shipped=$ca reference=$cb (expected factored/unfactored). Either the trie is disabled in the shipped build — in which case every comparison below is vacuous — or an NFA/DFA cap moved and this control needs re-sizing."
fi

# ---- deterministic pattern corpus ---------------------------------------
# Generated in awk from a fixed seed, so any failure is reproducible from the
# printed pattern index. MINSTD (48271, 2^31-1) rather than the usual
# glibc constants because awk arithmetic is double-precision: 48271*(2^31-1)
# is ~1.0e14 and exact in a double, where 1103515245*(2^31) is not.
#
# The families exist to hit specific trie paths, not to look varied:
#   0 flat alternation over a 3-letter alphabet — dense prefix sharing, and at
#     length 1..4 many branches END at an interior node, which is rule 1
#   1 an explicit shared prefix on every branch — deep tries
#   2 duplicate branches — rule 1's one-pass accept split (`a|a|...|a` was a
#     segfault before R3 hardened it)
#   3 classes and `.` mixed into the words — rule 2 overlap and the
#     disjoint_run_len run split, i.e. the 56x-cliff path
#   4 one INELIGIBLE branch spliced in — the contiguous eligible-run rule
#   5 a literal wrapped around the alternation — trie inside a concatenation
#   6 two alternations concatenated — independent tries in sequence
#   7 `$`- and `^`-bearing variants — EOL variant states and the attempt engine
#   8 shared SUFFIXES — the reverse machine factors these and the forward one
#     does not, so this is the only family exercising trie_key's rev path
awk -v n="$N" -v seed="$SEED" '
function rnd(m) { s = (s * 48271) % 2147483647; return int(s / 65536) % m }
BEGIN {
    s = seed % 2147483647; if (s == 0) s = 1
    split("a b c [ab] [bc] [ac] . [a-c]", atom, " ")
    split("a* b+ c{2,3} (ab|c) a? (a|b)*", inel, " ")
    for (i = 0; i < n; i++) {
        fam = i % 9
        nbr = 3 + rnd(6)
        pfx = ""
        if (fam == 1) { L = 1 + rnd(3); for (k = 0; k < L; k++) pfx = pfx atom[1 + rnd(3)] }
        p = ""; prev = ""
        inel_at = 1 + rnd(nbr - 1)
        for (j = 0; j < nbr; j++) {
            w = pfx
            L = 1 + rnd(4)
            for (k = 0; k < L; k++) w = w atom[1 + rnd(fam >= 3 ? 8 : 3)]
            if (fam == 8) {
                L = 1 + rnd(3)
                for (k = 0; k < L; k++) w = w atom[1 + rnd(3)]
            }
            if (fam == 2 && j > 0 && rnd(2) == 0) w = prev
            prev = w
            if (fam == 4 && j == inel_at) w = inel[1 + rnd(6)]
            p = p (j ? "|" : "") w
        }
        if (fam == 5) p = atom[1 + rnd(3)] "(" p ")" atom[1 + rnd(3)]
        if (fam == 6) {
            q = ""; m2 = 2 + rnd(3)
            for (j = 0; j < m2; j++) {
                w = ""; L = 1 + rnd(3)
                for (k = 0; k < L; k++) w = w atom[1 + rnd(3)]
                q = q (j ? "|" : "") w
            }
            p = "(" p ")(" q ")"
        }
        if (fam == 7) p = (rnd(2) ? p "$" : "^" p)
        print p
    }
}' > "$WORKDIR/patterns.txt"

npat=0; nboth_fail=0; ndiff=0; nsplit=0
while IFS= read -r pat; do
    npat=$((npat + 1))
    a_ok=1; b_ok=1
    gen_a "$pat" > "$WORKDIR/a.c" || a_ok=0
    gen_b "$pat" > "$WORKDIR/b.c" || b_ok=0
    if [ "$a_ok" != "$b_ok" ]; then
        nsplit=$((nsplit + 1))
        [ "$nsplit" -le 3 ] && bad "pattern #$npat '$pat': shipped ok=$a_ok, unfactored reference ok=$b_ok — factoring changed whether the pattern COMPILES"
        continue
    fi
    if [ "$a_ok" = 0 ]; then nboth_fail=$((nboth_fail + 1)); continue; fi
    if ! cmp -s "$WORKDIR/a.c" "$WORKDIR/b.c"; then
        ndiff=$((ndiff + 1))
        if [ "$ndiff" -le 3 ]; then
            bad "pattern #$npat '$pat': emitted C DIFFERS from the unfactored construction — the trie is not output-preserving, i.e. a rule-1/rule-2 soundness bug. Reference vs shipped:"
            diff "$WORKDIR/b.c" "$WORKDIR/a.c" | head -12 >&2
        fi
    fi
done < "$WORKDIR/patterns.txt"

# A corpus that compiles nothing proves nothing. This is a coverage FLOOR, the
# thing gate.sh was found to be missing (R3 process critic).
compiled=$((npat - nboth_fail - nsplit))
if [ "$compiled" -ge $((N / 2)) ]; then
    ok "coverage: $compiled of $npat generated patterns compiled and were compared"
else
    bad "only $compiled of $npat patterns compiled at all (expected >= $((N / 2))) — the generated corpus is not exercising the compiler"
fi
if [ "$ndiff" -eq 0 ] && [ "$compiled" -gt 0 ]; then
    ok "trie identity: $compiled patterns emit byte-identical C with and without prefix factoring"
elif [ "$ndiff" -gt 0 ]; then
    bad "trie identity: $ndiff of $compiled patterns differ (only the first 3 are shown above)"
fi

echo
echo "== Summary =="
echo "patterns compared:        $npat (seed $SEED)"
echo "byte-identical:           $((compiled - ndiff))"
echo "differing:                $ndiff"
echo "rejected by both builds:  $nboth_fail"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && exit 0
exit 1
