#!/usr/bin/env bash
# tests/assertions/run_mline_diff.sh — [M6.2] WAVE C's DIFFERENTIAL SWEEP over
# the `(?m)$` family, against libpcre2 and python3 `re`.
#
# WHY THIS FILE EXISTS AND THE .rxt CORPUS DOES NOT COVER IT.
# tests/assertions/multiline.rxt pins hand-chosen cells. This sweeps a
# generated subject space, and it does so over exactly the population
# assertions_design.md §3.6.1 names as the one that can break:
#
#     `\b`'s accept bit is pinned across a skipped run (its LEFT operand is
#     part of the state identity and its right operand is a class fact).
#     `(?m)$`'s is NOT: "is the next byte a newline" genuinely varies inside
#     a run a skip set admits, so a scan-avoidance mechanism that advances
#     `pos` without consulting the accept flags can jump straight past an
#     accepting position.
#
# D11's own record is the reason this is measured rather than argued: the
# first attempt at M2.12 got rule 1 right and still produced 53 divergences
# over 27 patterns x 69 subjects.
#
# THE POPULATION CLAIM IS CHECKED, NOT ASSUMED. A sweep over `(?m)$` patterns
# that happened to emit no skip state and no prefilter would be green against
# a completely broken cure. So every pattern's artifact is inspected for a
# LIVE scan-avoidance mechanism (`_fs<N>`/`_rs<N>` skip tables, a `memchr`, or
# a `_first[]` bitmap walk), the counts are printed every run, and the script
# FAILS if too few patterns carry one. That is the check on the check.
#
# BOTH ORACLES, and both pcrec engines. libpcre2 is the source of truth (D26);
# python3 `re` runs as an independent second opinion wherever it can express
# the pattern, which for a leading `(?m)` it can. Both pcrec artifacts are
# compared — the DFA (where the whole cure lives) and the VM (which shares no
# machinery with it, so an agreeing VM says the DFA's answer is not an echo of
# its own construction).
#
# Usage: bash tests/assertions/run_mline_diff.sh
# Env: PCREC, CC, KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern), never silently.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "mline-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the oracle ----------------------------------------------------------
ORACLE="$WORKDIR/pcre2_oracle"
if ! $CC -O1 -std=gnu11 -Wall -Wextra -Werror -o "$ORACLE" \
        "$ROOT_DIR/tests/fuzz/pcre2_oracle.c" -ldl 2>"$WORKDIR/ob.log"; then
    echo "FAIL: could not build tests/fuzz/pcre2_oracle:" >&2
    cat "$WORKDIR/ob.log" >&2
    exit 1
fi
printf 'a' > "$WORKDIR/probe"
if ! "$ORACLE" 'a' "$WORKDIR/probe" >/dev/null 2>&1; then
    echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

# ---- the subject space ---------------------------------------------------
# NEWLINE-RICH BY CONSTRUCTION, and that is the whole design of the sweep:
# assertions_design.md §3.7.1 records a probe of its own that measured NOTHING
# because its subject had no newline in it, and reported the wrong conclusion.
# A `(?m)` sweep over subjects without line breaks is that mistake.
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
alpha = "ab\nc"
subs = []
# EXHAUSTIVE up to length 3 over {a, b, \n, c} — 85 subjects. Exhaustive
# rather than curated because every newline placement (leading, trailing,
# doubled, absent, adjacent to the pattern's own alphabet) is then present by
# ENUMERATION rather than by someone remembering to add it, and `c` is in the
# alphabet because half the patterns are `[^c]`-shaped and a subject set
# without their excluded byte measures the generator (D47.6).
for n in range(0, 4):
    for t in itertools.product(alpha, repeat=n):
        subs.append("".join(t))
# LENGTH 4 AND 5, curated to the shapes exhaustion at those lengths would be
# spent on: a newline at every interior offset, doubled and tripled runs, and
# the `[^c]`-crossing forms.
subs += ["a\nbc", "ab\nc", "abc\n", "\nabc", "a\n\nb", "\n\nab", "ab\n\n",
         "a\nb\nc", "\na\nb\n", "aa\nbb", "\naabb", "aabb\n", "ac\nca",
         "c\nc\nc", "\nc\nc\n", "aaaa", "\n\n\n\n", "abca\n", "\nabca"]
# LONGER ONES, to reach past the two-position window plain `$` lives in and
# into runs a skip loop actually skips — a 40-byte stay run is well past any
# threshold `pick_skip_states` uses.
subs += ["aaaa\nbbbb", "aaaaaaaa\n", "\naaaaaaaa", "aaaa\n\naaaa",
         "x" * 40 + "\n" + "x" * 40, "\n".join(["abc"] * 8),
         "ERROR\n" + "ok\n" * 5 + "ERROR", "\n" * 12, "a" * 64,
         "a" * 63 + "\n", "\n" + "a" * 63]
for i, s in enumerate(subs):
    with open(os.path.join(out, "s%04d" % i), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(subs))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)
if [ "$NSUBJ" -lt 100 ]; then
    bad "subject generation produced only $NSUBJ subjects — the sweep has no space"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the patterns --------------------------------------------------------
# The `(?m)$` family with a QUANTIFIER, which is what creates a state that
# self-loops widely enough to be skip-eligible, plus the `(?m)^` shapes that
# exercise D63's candidate-start prefilter on the other engine.
PATTERNS=(
    '(?m)[^c]*$'
    '(?m)[^c]+$'
    '(?m)[^c]{1,3}$'
    '(?m).*$'
    '(?m)a*$'
    '(?m)a+$'
    '(?m)[ab]*$'
    '(?m)x*$'
    '(?m)b?$'
    '(?m)$'
    '(?m)a$'
    '(?m)ab$'
    '(?m)[^c]*b$'
    '(?m)a[^c]*$'
    '(?m)^a'
    '(?m)^ab'
    '(?m)^[^c]*'
    '(?m)^'
    '(?m)^a$'
    '(?m)^[^c]*$'
    '(?m)^a|b'
    '(?m)a$|^b'
)

gen() { # gen <outdir> <pattern> [extra pcrec args]
    local d="$1" pat="$2"; shift 2
    mkdir -p "$d"
    "$PCREC" --features all -p rx "$@" -o "$d/gen.c" -- "$pat" 2>"$d/err" || return 1
    $CC -O2 -I"$d" -c -o "$d/gen.o" "$d/gen.c" 2>>"$d/err" || return 1
    $CC -O2 -I"$d" -o "$d/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$d/gen.o" \
        2>>"$d/err" || return 1
}

# ---- the sweep -----------------------------------------------------------
npat=0; nlive=0; ncells=0; ndiff=0; nvm=0; npy=0; nskip=0
: > "$WORKDIR/diffs.txt"
mechlist=""
for pat in "${PATTERNS[@]}"; do
    d="$WORKDIR/p$npat"; npat=$((npat + 1))
    if ! gen "$d" "$pat"; then
        bad "could not build a DFA artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    dv="$d/vm"
    if ! gen "$dv" "$pat" --engine=vm; then
        bad "could not build a VM artifact for '$pat': $(head -2 "$dv/err")"
        continue
    fi

    # THE POPULATION CHECK, read off the artifact rather than assumed.
    mech=""
    grep -qE '^    static const unsigned char rx_(fs|rs)[0-9]+\[' "$d/gen.c" && mech="${mech}skip,"
    grep -q 'memchr' "$d/gen.c" && mech="${mech}memchr,"
    grep -q 'rx_first\[' "$d/gen.c" && mech="${mech}bitmap,"
    grep -q 'rx_facc2\[' "$d/gen.c" && mech="${mech}clsacc,"
    if [ -n "$mech" ]; then nlive=$((nlive + 1)); fi
    mechlist="$mechlist  $(printf '%-18s' "$pat") ${mech:-none}
"

    for f in "$WORKDIR"/subjects/*; do
        for sp in 0 1; do
            want="$("$ORACLE" "$pat" "$f" "$sp" 2>/dev/null)"
            # A CELL THE ORACLE CANNOT ANSWER IS NOT A CELL, and the two
            # reasons are different: `cerr` is a pattern libpcre2 refuses, and
            # `inconclusive -33` is PCRE2_ERROR_BADOFFSET — `startpos` past the
            # end of THIS subject, which the empty subject makes true for every
            # nonzero startpos. Skipping only `cerr` reported 366 "divergences"
            # that were entirely this, on the first run of this script.
            case "$want" in
                "match "*|nomatch) ;;
                *) nskip=$((nskip + 1)); continue ;;
            esac
            printf '%s\t%s\t%s\t%s\n' "$pat" "$(basename "$f")" "$sp" "$want" \
                >> "$WORKDIR/oracle.tsv"
            got="$("$d/t" "$f" "$sp" 2>/dev/null)"
            ncells=$((ncells + 1))
            if [ "$got" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'DFA %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$got" "$want" >> "$WORKDIR/diffs.txt"
            fi
            gotv="$("$dv/t" "$f" "$sp" 2>/dev/null)"
            nvm=$((nvm + 1))
            if [ "$gotv" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'VM  %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$gotv" "$want" >> "$WORKDIR/diffs.txt"
            fi
        done
    done
done

printf 'mline-diff: scan-avoidance mechanisms live in each pattern'\''s DFA artifact:\n%s' "$mechlist"

# ---- the independent second oracle --------------------------------------
# python3 `re` against LIBPCRE2's OWN ANSWERS, cell for cell, on exactly the
# cells the sweep above used.
#
# WHAT THIS ARM IS FOR, stated precisely because it is easy to mistake for a
# second check on pcrec. D26 makes libpcre2 the source of truth, and every
# comparison above is against it; if pcrec agrees with libpcre2 on a cell,
# adding "and python agrees with pcrec" says nothing new. What python CAN say
# is whether the ORACLE ITSELF is being used correctly — a wrong startpos
# convention, a subject that lost a byte in transit, a `(?m)` that means
# something different to the two engines. python `re` shares no code with
# libpcre2, so a systematic mistake in how this script drives the oracle shows
# up here as a divergence and nowhere else.
#
# It carries its own KNOWN exclusion rather than a blanket tolerance: python's
# non-multiline `$` and `\Z` differ from PCRE2's (docs/dev/upstream_issues.md
# U11), so a pattern python cannot express is SKIPPED and counted, never
# silently passed.
python3 - "$WORKDIR/oracle.tsv" "$WORKDIR/subjects" > "$WORKDIR/py.txt" 2>&1 <<'PY'
import os, re, sys
tsv, subdir = sys.argv[1], sys.argv[2]
cache = {}
def subj(name):
    if name not in cache:
        cache[name] = open(os.path.join(subdir, name), "rb").read().decode("latin-1")
    return cache[name]
rxs, skipped_pats = {}, set()
n = bad = skipped = 0
for line in open(tsv):
    pat, name, sp, want = line.rstrip("\n").split("\t", 3)
    if pat not in rxs:
        try:
            rxs[pat] = re.compile(pat)
        except re.error:
            rxs[pat] = None
            skipped_pats.add(pat)
    rx = rxs[pat]
    if rx is None:
        skipped += 1
        continue
    m = rx.search(subj(name), int(sp))
    got = "nomatch" if m is None else "match %d %d" % (m.start(), m.end())
    # libpcre2's line carries every capture pair; these patterns are
    # capture-free, so the whole-match pair is the whole line.
    n += 1
    if got != want:
        bad += 1
        if bad <= 10:
            print("PYDIFF %r [%s] startpos %s: python %s / libpcre2 %s"
                  % (pat, name, sp, got, want))
print("PYSTATS %d %d %d %d" % (n, bad, skipped, len(skipped_pats)))
PY
read -r _ npy npybad npyskip npyskippat <<< "$(grep '^PYSTATS ' "$WORKDIR/py.txt")"
if [ "${npybad:-1}" -eq 0 ] && [ "${npy:-0}" -gt 1000 ]; then
    ok "second oracle: python3 re and libpcre2 agree on all $npy python-expressible cells (${npyskip:-0} cells over ${npyskippat:-0} patterns python cannot express were SKIPPED, not passed) — the oracle is being driven correctly"
else
    bad "second oracle: python3 re and libpcre2 disagree on ${npybad:-?} of ${npy:-?} cells, which means this script is driving one of them wrongly rather than that pcrec is wrong:"
    grep '^PYDIFF ' "$WORKDIR/py.txt" >&2
fi

if [ "$ndiff" -eq 0 ]; then
    ok "differential: $ncells DFA cells and $nvm VM cells over $npat (?m) patterns x $NSUBJ subjects x 2 startpos agree with libpcre2 exactly"
else
    bad "differential: $ndiff disagreements with libpcre2 over $((ncells + nvm)) cells. First offenders:"
    head -20 "$WORKDIR/diffs.txt" >&2
fi

if [ "$nlive" -ge 8 ]; then
    ok "population: $nlive of $npat patterns emit a LIVE scan-avoidance mechanism (skip table, memchr, first-set bitmap) or a class-indexed accept — the sweep is over the population §3.6.1 says can actually break, not over patterns the cure never touches"
else
    bad "population: only $nlive of $npat patterns emit any scan-avoidance mechanism at all. A green differential over this set would prove nothing about the cure — the sweep has gone vacuous."
fi

echo
echo "== Summary =="
echo "  patterns $npat   subjects $NSUBJ   DFA cells $ncells   VM cells $nvm   disagreements $ndiff   oracle-unanswerable cells skipped $nskip"
echo "  patterns carrying a live scan-avoidance mechanism: $nlive"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
