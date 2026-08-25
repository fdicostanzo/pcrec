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
# disjointness guard shows up on 2 cases in the whole .rxt corpus and on 64 of
# these 500 patterns; breaking rule 1's accept split shows up on 16 .rxt cases
# and 94 of 500 — and each failure names the exact pattern rather than a subject
# that happened to hit it. (Measured; the exact sabotage edits are recorded in
# tests/codegen/CLAUDE.md so they can be replayed. An earlier version of this
# comment said "~14 in 500", which was another corpus's figure repeated without
# re-running.)
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
#      500), TRIE_SEED (default 20260809), KEEP=1, SANFLAGS (default empty —
#      SAN-1: extra flags appended to the from-source $REF reference build;
#      $PCREC itself carries the compiler axis for free via the PCREC override)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
CC="${CC:-gcc}"
N="${TRIE_N:-500}"
SEED="${TRIE_SEED:-20260809}"
SANFLAGS="${SANFLAGS:-}"
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
#
# FLAGS carries the per-sweep compile options; the corpus is swept once
# case-sensitive and once with -i (OS-1). Folding is not cosmetic here: it
# rewrites the class bitmaps the trie keys on, so `Cat|CAT|cat` goes from three
# unrelated branches to three IDENTICAL ones, and patterns that shared no
# prefix at all start sharing a full one. That drives rule 1's accept split and
# rule 2's disjoint-run logic down paths the unfolded corpus never reaches, and
# the identity requirement is exactly as strong there.
FLAGS=()
gen_a() { "$PCREC" -p rx "${FLAGS[@]+"${FLAGS[@]}"}" -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   -p rx "${FLAGS[@]+"${FLAGS[@]}"}" -o - -- "$1" 2>/dev/null; }

# ---- the reference compiler ---------------------------------------------
# -DPCREC_NO_TRIE forces `elig[j] = false` in nfa.c's A_ALT path, i.e. the
# pre-M2.8 unfactored construction. -O0 on purpose: this build is never
# measured, only diffed, and -O0 keeps it under half a second. Warnings stay on
# so #ifdef rot is loud rather than silent.
#
# [M5-SEAM] The source list is FOUND, not globbed. It was `src/*/*.c`, which
# is a hand-maintained assumption about the tree's DEPTH: `src/gen/enc/`
# (the encoding backends) is two levels down and silently fell out of the
# reference build the day it landed. The failure was loud here (an undefined
# reference), but the same shape one directory over would be a reference
# compiler quietly built from a different source set than the subject — which
# is the differential going vacuous, this repo's recorded check-design defect.
REF="$WORKDIR/pcrec_notrie"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | LC_ALL=C sort)"
if [ -z "$REF_SRCS" ]; then
    echo "FAIL: found no compiler sources under $ROOT_DIR/src for the reference build" >&2
    exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_NO_TRIE $SANFLAGS \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS \
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

# ---- POSITIVE CONTROLS ---------------------------------------------------
# Without these the script is a guard that cannot fail: if the trie were
# disabled in the SHIPPED build too, every pattern below would trivially agree
# and this would report a clean bill of health for a deleted optimization.
# That is the exact failure mode R3 found in two guards written the same day.
#
# THERE ARE THREE, AT DIFFERENT BRANCH COUNTS, and that is the whole point.
# The first version of this script had only the 256-branch control, and a critic
# broke it in one clause: `elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)`
# — a plausible "only factor when it is worth it" heuristic — left all three
# checks green and `make test` entirely green, because every generated pattern
# has 3..8 branches (so both builds were unfactored and agreed) while the
# control has 256 (so it still factored). A control that only proves the
# optimization fires OUTSIDE the corpus's own range proves nothing about the
# corpus. Two of the three controls now sit INSIDE it.
#
# Each control is DETERMINISTIC, not timing-based: it is sized so the two builds
# fail at DIFFERENT STAGES, and the stage is visible in the error text:
#   unfactored -> "pattern too large (NFA exceeds ...)"   (never reaches the DFA)
#   factored   -> "pattern too complex for the DFA engine" (cleared the NFA cap)
# If either cap in src/core/internal.h moves, these fail loudly, not quietly.
#
# The two small-branch controls are `^`-ANCHORED on purpose. Without `^` the
# engine also builds a REVERSE machine, and a shared PREFIX barely factors in
# reverse (the reverse trie factors the branches' shared SUFFIX, which here is
# 2 bytes) — so the reverse NFA blows the cap in both builds and the control
# degenerates to unfactored/unfactored. `^` selects ENG_ATTEMPT, which builds no
# reverse machine, so the forward saving is what the cap sees. Measured
# forward NFA for the 4-branch shape: 213 states factored vs 812 unfactored.
check_control() { # check_control <label> <pattern>
    local lbl="$1" pat="$2" oa ob sa sb
    oa="$(pcrec_run "$PCREC" -p rx -o - -- "$pat" 2>&1 >/dev/null | head -1)"
    ob="$("$REF"   -p rx -o - -- "$pat" 2>&1 >/dev/null | head -1)"
    case "$oa" in *"DFA engine"*) sa=factored ;; *"NFA exceeds"*) sa=unfactored ;;
                  "") sa=compiled ;; *) sa="other:$oa" ;; esac
    case "$ob" in *"DFA engine"*) sb=factored ;; *"NFA exceeds"*) sb=unfactored ;;
                  "") sb=compiled ;; *) sb="other:$ob" ;; esac
    if [ "$sa" = factored ] && [ "$sb" = unfactored ]; then
        ok "positive control ($lbl): the shipped build really factors here"
    else
        bad "positive control ($lbl): shipped=$sa reference=$sb (expected factored/unfactored). Either the trie is disabled or thresholded OFF at this branch count — in which case the identity comparisons below are vacuous for it — or an NFA/DFA cap moved and this control needs re-sizing."
    fi
}

# nbr inside the corpus's own 3..8 range. `^(<nbr> branches sharing a 200- or
# 100-byte prefix){r}`: unfactored ~812/copy vs ~213/copy factored.
#
# [OPT-ALTCLS] (2026-08-17): EVERY shared-prefix byte is a two-member CLASS
# (`[aA]`, not bare `a`), not a cosmetic choice. src/opt/altcls.c's stage 2
# runs BEFORE this control's `-DPCREC_NO_TRIE` knob has any effect at all
# (it is a separate, gate-INDEPENDENT AST pass, upstream of nfa.c's trie
# entirely), and it ALSO prefix-factors a run of branches sharing a literal
# first byte -- which a bare-letter prefix like the pre-[OPT-ALTCLS] version
# of this control used IS. With a bare prefix, ALTCLS pre-factors the shared
# run itself, so BOTH the shipped and the `-DPCREC_NO_TRIE` reference build
# see an already-shrunk AST by the time nfa.c's own trie would have fired --
# reference stops being "trie disabled", it becomes "trie disabled AND
# nothing left for it to do", and the control reports factored/factored
# (measured: exactly this, the day [OPT-ALTCLS] landed). `src/opt/altcls.c`'s
# own eligibility test requires a branch's FIRST atom to be a class holding
# EXACTLY ONE byte (`altcls_single_bit`); nfa.c's `trie_key` (this file's own
# sibling comment, "every leaf is A_CLASS") has no such restriction -- ANY
# class-only leaf sequence is trie-eligible. A two-member class is therefore
# the minimal edit that keeps the pattern trie-eligible while making altcls
# DECLINE at the very first branch-peel call, restoring this control's
# original property: shipped=factored, reference=unfactored, driven by
# `-DPCREC_NO_TRIE` alone. (No subjects are ever run against these patterns —
# "no subjects, no gcc" per this file's own header — so widening what each
# position matches has no bearing on what this check verifies.)
ctl_small() { # ctl_small <nbr> <prefix len> <repeat>
    awk -v NB="$1" -v PL="$2" -v R="$3" 'BEGIN {
        p = ""
        for (k = 0; k < PL; k++) {
            c = 97 + k % 26
            p = p "[" sprintf("%c", c) sprintf("%c", c - 32) "]"
        }
        s = ""
        for (i = 0; i < NB; i++)
            s = s (i ? "|" : "") p sprintf("%c%c", 97 + int(i / 26), 97 + i % 26)
        printf "^(%s){%d}", s, R
    }'
}
check_control "4 branches"   "$(ctl_small 4 200 300)"
check_control "8 branches"   "$(ctl_small 8 100 300)"

# The original large-branch control: all 256 8-bit binary strings, x100.
# ~230k NFA states unfactored against the 131072 cap, ~51k factored.
#
# [OPT-ALTCLS] (2026-08-17): each binary digit is a two-member class
# (`[02]`/`[13]`), for the identical reason `ctl_small` above widens its
# prefix -- consecutive integers in this generator share long common BIT
# PREFIXES (0=00000000, 1=00000001, ...), which is exactly altcls stage 2's
# own adjacent-literal-prefix shape, and a bare-digit version of this
# control measured factored/factored the same way `ctl_small` did.
check_control "256 branches" "$(awk 'BEGIN {
    p = ""
    for (i = 0; i < 256; i++) {
        w = ""; v = i
        for (k = 0; k < 8; k++) {
            d = v % 2
            w = (d == 0 ? "[02]" : "[13]") w
            v = int(v / 2)
        }
        p = p (i ? "|" : "") w
    }
    printf "(%s){100}", p
}')"

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
#   8 words carrying a shared suffix as well as a shared prefix
#
# NOTE on the reverse path, because the first version of this comment was wrong
# in both directions (R3 critic): family 8 is NOT "the only family exercising
# trie_key's rev path", and it is not forward-unfactored either. Every pattern
# without `^` builds a reverse machine (src/core/compile.c), so 8 of the 9
# families drive the rev path at full strength — instrumenting trie_build over
# these 500 patterns shows 55-56 of 56 per family building a reverse trie, the
# sole exception being family 7's `^`-anchored half (23 of 55), which is
# ENG_ATTEMPT and has no reverse machine at all. Family 8 also builds a FORWARD
# trie in 55 of 55, because its words are drawn from a 3-letter alphabet and
# share prefixes by accident. The rev path is well covered; it is just not
# covered by the family that used to be credited with it.
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

sweep() { # sweep <label>; compares every pattern under the current FLAGS
    local lbl="$1"
    npat=0; nboth_fail=0; ndiff=0; nsplit=0
    while IFS= read -r pat; do
        npat=$((npat + 1))
        a_ok=1; b_ok=1
        gen_a "$pat" > "$WORKDIR/a.c" || a_ok=0
        gen_b "$pat" > "$WORKDIR/b.c" || b_ok=0
        if [ "$a_ok" != "$b_ok" ]; then
            nsplit=$((nsplit + 1))
            [ "$nsplit" -le 3 ] && bad "[$lbl] pattern #$npat '$pat': shipped ok=$a_ok, unfactored reference ok=$b_ok — factoring changed whether the pattern COMPILES"
            continue
        fi
        if [ "$a_ok" = 0 ]; then nboth_fail=$((nboth_fail + 1)); continue; fi
        if ! cmp -s "$WORKDIR/a.c" "$WORKDIR/b.c"; then
            ndiff=$((ndiff + 1))
            if [ "$ndiff" -le 3 ]; then
                bad "[$lbl] pattern #$npat '$pat': emitted C DIFFERS from the unfactored construction — the trie is not output-preserving, i.e. a rule-1/rule-2 soundness bug. Reference vs shipped:"
                diff "$WORKDIR/b.c" "$WORKDIR/a.c" | head -12 >&2
            fi
        fi
    done < "$WORKDIR/patterns.txt"

    # A corpus that compiles nothing proves nothing. This is a coverage FLOOR,
    # the thing gate.sh was found to be missing (R3 process critic).
    compiled=$((npat - nboth_fail - nsplit))
    if [ "$compiled" -ge $((N / 2)) ]; then
        ok "coverage [$lbl]: $compiled of $npat generated patterns compiled and were compared"
    else
        bad "only $compiled of $npat patterns compiled at all under $lbl (expected >= $((N / 2))) — the generated corpus is not exercising the compiler"
    fi
    if [ "$ndiff" -eq 0 ] && [ "$compiled" -gt 0 ]; then
        ok "trie identity [$lbl]: $compiled patterns emit byte-identical C with and without prefix factoring"
    elif [ "$ndiff" -gt 0 ]; then
        bad "trie identity [$lbl]: $ndiff of $compiled patterns differ (only the first 3 are shown above)"
    fi
    summary="$summary
$(printf '  %-22s compared %4d  identical %4d  differing %3d  rejected-by-both %3d' \
        "$lbl" "$npat" "$((compiled - ndiff))" "$ndiff" "$nboth_fail")"
}

summary=""
FLAGS=();   sweep "case-sensitive"
FLAGS=(-i); sweep "case-folded (-i)"

echo
echo "== Summary =="
echo "seed $SEED$summary"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && exit 0
exit 1
