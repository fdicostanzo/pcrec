#!/usr/bin/env bash
# tests/lookaround/run_expansion_diff.sh — [M6.6.2] wave E2: THE SUBSTITUTION
# DRIVER (design `lookaround_design.md` §6.3, §11 wave E2).
#
# WHAT IT IS. `tests/assertions/` is 468 blocks and 10,120 behavioural cells,
# every expectation produced by libpcre2 rather than written by hand, for a
# module that already ships. Every assertion in it has a LOOKAROUND DEFINITION
# (§6.1). Textually replacing each assertion by its definition therefore turns
# that corpus into a LOOKAROUND corpus for free — 263 blocks and 8,260 cells of
# it, whose expectations are not this module's guesses.
#
# **IT IS A CORPUS GENERATOR, NOT A PRODUCT MECHANISM** (Frank, 2026-08-23;
# design §6.4). It emits PATTERN TEXT that the compiler sees as an ordinary
# user-written lookaround. Nothing here desugars anything inside pcrec, and
# nothing in `src/` changed for it. The product-side substitution is [DD-14]'s
# subroutine-call primitive, after this module lands — "I don't want parallel
# mechanisms if we can avoid it".
#
# ---------------------------------------------------------------------------
# THE THREE-WAY CHECK, PER CELL (§6.3), AND BOTH HALVES ARE REQUIRED
# ---------------------------------------------------------------------------
#
#   A   the EXPANDED pattern compiled by pcrec       (the new lookaround path)
#   B   the FOLDED pattern compiled by pcrec         (the shipped assertions path)
#   C   libpcre2 on the EXPANDED pattern             (the external oracle)
#
#   A == B  is D66's SELF-ORACLE: pcrec's two lowerings of one language must
#           agree. It needs no external oracle, which is what makes it usable
#           on every cell including the ones python cannot take (§7).
#   A == C  is the ordinary differential, and it is what stops `A == B` passing
#           because BOTH lowerings are wrong the same way.
#
# `A == B` alone is satisfiable by a compiler that is consistently wrong;
# `A == C` alone does not test the folded path the expansion is supposed to be
# equivalent to. Neither is sufficient and the driver asserts both.
#
# ---------------------------------------------------------------------------
# THE FIVE THINGS THAT KEEP THIS FROM BEING A TAUTOLOGY, because every check
# this project has written that FAILED, failed by sharing a source with the
# thing it controls
# ---------------------------------------------------------------------------
#
#  1. **THE EXPANSION TABLE IS LITERAL** (`expand_corpus.py`), transcribed from
#     design §6.1 / D66 / [DD-11] and never derived from the compiler. If it
#     were read out of `src/parse/mod_assertions.c`, `A == B` would be two
#     spellings of one source agreeing with themselves. §0 below RE-VERIFIES
#     the table against libpcre2 before a single row of it is used.
#  2. **§0 CARRIES ITS OWN FAILING DIRECTION** — the VACUITY GUARD. `\A|(?<=\n)`
#     (the D66 expansion with `(?!\z)` dropped) is a WRONG expansion of `(?m)^`,
#     and §0 asserts an EXACT NONZERO number of cells on which it disagrees. A
#     table check that could only report agreement would report agreement for a
#     table of nine identity rows.
#  3. **THE `--policy=none` CONTROL ARM.** Same pipeline, no substitution: the
#     generated pattern IS the original, and every cell must come out trivially
#     equal. Without it, `A == B` is not known to be comparing two lowerings at
#     all — it could be comparing one artifact with itself.
#  4. **AND ITS CONVERSE, which the control alone does not give.** §2 and §3
#     assert that the P1/P2 patterns they compiled are TEXTUALLY DIFFERENT from
#     their source, and count how many contain a lookaround at all. A driver
#     whose substitution silently became the identity would pass every
#     comparison in this file and test nothing; that number going to zero is
#     the shape it would take.
#  5. **THE CELL-FIDELITY GUARD (§1c).** Arm B's answers are compared against
#     the CORPUS'S OWN stated expectations, cell for cell. Without it, a bug in
#     this script's subject decoding would feed the same wrong subject to all
#     three arms, they would all agree, and the driver would be green while
#     measuring nothing. The corpus's expectations are the one input here that
#     no arm of this driver produced.
#
# ---------------------------------------------------------------------------
# THE POPULATION, AND WHY THE COUNTS ARE ASSERTED AND NOT PRINTED
# ---------------------------------------------------------------------------
# §6.3 measured 263 qualifying blocks / 8,260 cells with a per-rule
# disqualification table, and those numbers are guards here, not decoration: a
# qualification rule that quietly stopped firing would SHRINK this population,
# and a smaller population is the one failure mode a green run cannot show.
# When the assertions corpus grows, re-derive the numbers from a run and change
# them DELIBERATELY; never relax one to a floor.
#
# THE SIX QUALIFICATION RULES ARE PARSERS, NOT SUBSTRING TESTS (R33 C3-1/C3-2),
# and they live in `expand_corpus.py` with the reason each one exists. Q3's
# class walk consumes one literal `]` after `[`/`[^`; Q4 finds every `(?` +
# modifier letter set terminated by `:`/`)` and exempts only a bare LEADING
# `(?m)`.
#
# ---------------------------------------------------------------------------
# WHAT IT REUSES
# ---------------------------------------------------------------------------
# `tests/backrefs/bref_oracle.py` and `tests/backrefs/bref_batch.c`, unchanged,
# exactly as `run_lookaround_diff.sh` does. Neither is backref-specific: the
# oracle takes `<key>\t<ngroups>\t<pattern>` and sweeps every startpos over a
# subject directory, and the driver takes `<subject-file>\t<startpos>` on stdin
# and prints the span plus every `RX_NCAPS` group pair. D24 is the standing
# rule against a second home for one fact, and this would have been the THIRD.
#
# Usage: bash tests/lookaround/run_expansion_diff.sh [--policy=all|P1|P2|none]
# Env: PCREC, CC, GENCFLAGS, PROCS (default nproc), KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern), never silently.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11}"
ORACLE="$ROOT_DIR/tests/backrefs/bref_oracle.py"
BATCH="$ROOT_DIR/tests/backrefs/bref_batch.c"
GENERATOR="$SCRIPT_DIR/expand_corpus.py"
CORPUS="$ROOT_DIR/tests/assertions"
# shellcheck source=/dev/null
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
PROCS="${PROCS:-$(nproc 2>/dev/null || echo 2)}"

POLICY="all"
for a in "$@"; do
    case "$a" in
        --policy=*) POLICY="${a#--policy=}" ;;
        *) echo "usage: run_expansion_diff.sh [--policy=all|P1|P2|none]" >&2
           exit 2 ;;
    esac
done
case "$POLICY" in all|P1|P2|none) ;; *)
    echo "FATAL: unknown --policy '$POLICY'" >&2; exit 2 ;;
esac
# The control arm is spelled `none` on the command line (design §11's own
# wording) and `NONE` in the plan's policy column; the mapping is here, once,
# rather than in each of the two places that filter on it.
PFILT="$POLICY"; [ "$PFILT" = "none" ] && PFILT="NONE"

# =========================================================================
# THE WITNESS PRINTER, and it is a FUNCTION because it has to be called from
# TWO places: the worker (where it runs only when a cell disagrees) and §1d
# (where it runs on every green run, over a fixture built to disagree).
#
# IT IS A FUNCTION FOR A REASON THIS LANE LEARNED TWICE IN ONE DAY. A witness
# printer only ever executes when something ELSE has already failed, so on a
# green tree it is dead code that looks like coverage — and it was WRONG twice
# before §1d existed: first it passed the patterns through `awk -v`, which
# ESCAPE-PROCESSES its assignments and printed `\G` as `G` (caught by the
# "workers wrote to stderr" guard, on sabotage row S130); then the `ENVIRON`
# fix put the assignment on the `paste` that FEEDS the pipeline instead of on
# the `awk` that reads it, and every witness printed `A[]=`. A misquoted
# witness is worse than no witness: it sends the triage after a pattern that
# was never compiled. §1d is what makes this path measured rather than hoped.
#
# $1 cells  $2 A's answers  $3 B's answers  $4 C's answers
# $5 policy $6 block id     $7 generated id $8 expanded pat  $9 folded pat
emit_witnesses() {
    paste "$1" "$2" "$3" "$4" \
        | GPAT="$8" ORIGPAT="${9}" \
          awk -F'\t' -v pol="$5" -v bid="$6" -v gid="$7" '
            BEGIN { gp = ENVIRON["GPAT"]; orig = ENVIRON["ORIGPAT"]; n = 0 }
            $3 != $4 || $3 != $5 {
              if (n++ < 3)
                printf "W\t%s\t%s\t%s\tsubject %s startpos %s\tA[%s]=%s\tB[%s]=%s\tC=%s\n",
                       pol, bid, gid, $1, $2, gp, $3, orig, $4, $5
            }'
}

# =========================================================================
# THE PER-BLOCK WORKER, re-invoked through this same file (the shape
# tests/harness/run.sh and tests/reject/run_reject_tests.sh already use).
# Prints one TSV record per generated pattern to stdout; the parent
# aggregates. It never prints PASS/FAIL — the parent owns the verdict, so a
# worker that dies mid-block cannot leave a partial pass behind.
# =========================================================================
if [ -n "${EXPAND_WORKER:-}" ]; then
    bdir="$EXPAND_WORKER"
    bid="$(basename "$bdir")"
    d="$(mktemp -d)"
    trap 'rm -rf "$d"' EXIT
    # ONE ARTIFACT PER DIRECTORY: tests/backrefs/bref_batch.c includes
    # "gen.h" by that name, so the two arms cannot share a working
    # directory without one arm's header shadowing the other's.
    mkdir -p "$d/A" "$d/B"
    IFS= read -r pat < "$bdir/pattern"
    IFS= read -r feats < "$bdir/feats"
    IFS= read -r origin < "$bdir/origin"
    ncells="$(grep -c . "$bdir/cells")"
    if [ "$ncells" -eq 0 ]; then
        printf 'E\t%s\t%s\tblock has zero cells\n' "$bid" "$origin"; exit 0
    fi

    # ---- arm B: the FOLDED pattern, pcrec ------------------------------
    if ! "$TIMEOUT_BIN" 60 "$PCREC" --features "$feats" -p rx \
            -o "$d/B/gen.c" -- "$pat" 2>"$d/b.err"; then
        printf 'E\t%s\t%s\tpcrec REFUSED the folded pattern %s: %s\n' \
            "$bid" "$origin" "$pat" "$(head -1 "$d/b.err")"; exit 0
    fi
    ncaps_b="$(grep -m1 '^#define RX_NCAPS' "$d/B/gen.h" | awk '{print $3}')"
    if ! "$TIMEOUT_BIN" 120 $CC $GENCFLAGS -I"$d/B" -o "$d/b" \
            "$BATCH" "$d/B/gen.c" 2>"$d/bcc.err"; then
        printf 'E\t%s\t%s\tthe folded artifact did not compile: %s\n' \
            "$bid" "$origin" "$(head -1 "$d/bcc.err")"; exit 0
    fi
    if ! "$TIMEOUT_BIN" 120 "$d/b" < "$bdir/cells" > "$d/b.out"; then
        printf 'E\t%s\t%s\tthe folded artifact did not run\n' "$bid" "$origin"
        exit 0
    fi
    if [ "$(grep -c . "$d/b.out")" -ne "$ncells" ]; then
        printf 'E\t%s\t%s\tthe folded artifact answered %s of %s cells\n' \
            "$bid" "$origin" "$(grep -c . "$d/b.out")" "$ncells"; exit 0
    fi

    # ---- §1c THE CELL-FIDELITY GUARD -----------------------------------
    # Arm B against the CORPUS'S OWN expectations. The corpus is the one
    # input no arm of this driver produced, and this is what makes the
    # subject decoding load-bearing: without it a decoding bug feeds the
    # same wrong subject to all three arms and they agree about nothing.
    awk '{ if ($1 == "match") print $1, $2, $3; else print $1 }' \
        "$d/b.out" > "$d/b.span"
    fbad="$(diff "$d/b.span" "$bdir/expect" 2>/dev/null | grep -c '^<' || true)"
    printf 'F\t%s\t%s\t%s\t%s\n' "$bid" "$origin" "$fbad" "$ncells"

    # ---- arm C: libpcre2, ONE invocation for the whole block -----------
    # Every generated pattern of this block, plus the FOLDED pattern as a
    # diagnostic arm (B == C), in one process over the block's own subjects.
    : > "$d/pats.tsv"
    printf '%s.FOLDED\t%s\t%s\n' "$bid" "$((ncaps_b - 1))" "$pat" \
        >> "$d/pats.tsv"
    while IFS=$'\t' read -r gid pol ident haslook gpat; do
        case "$POLICY" in
            all) ;;
            *) [ "$pol" = "$PFILT" ] || continue ;;
        esac
        printf '%s\t%s\t%s\n' "$gid" "$((ncaps_b - 1))" "$gpat" >> "$d/pats.tsv"
    done < "$bdir/gen.tsv"
    if [ "$(grep -c . "$d/pats.tsv")" -le 1 ]; then
        printf 'E\t%s\t%s\tpolicy %s generated NO pattern for this block\n' \
            "$bid" "$origin" "$POLICY"; exit 0
    fi
    if ! "$TIMEOUT_BIN" 300 python3 "$ORACLE" "$d/pats.tsv" "$bdir/subjects" \
            "$d/otsv" 2>"$d/o.err"; then
        printf 'E\t%s\t%s\tthe libpcre2 oracle failed: %s\n' \
            "$bid" "$origin" "$(head -1 "$d/o.err")"; exit 0
    fi
    mkdir -p "$d/oracle"
    # Project the oracle's full startpos sweep onto the block's own cells,
    # in the block's own cell order, so the comparison is POSITIONAL against
    # the artifacts' output. A cell the oracle did not answer becomes the
    # literal `MISSING`, which can never equal an artifact's answer.
    awk -F'\t' -v celllist="$bdir/cells" -v od="$d/oracle" '
      BEGIN {
        nc = 0
        while ((getline line < celllist) > 0) {
          split(line, f, "\t"); nc++
          n = split(f[1], p, "/"); cs[nc] = p[n]; cp[nc] = f[2]
        }
      }
      { ans[$1 SUBSEP $2 SUBSEP $3] = $4
        if (!($1 in seen)) { seen[$1] = 1; order[++nk] = $1 } }
      END {
        for (k = 1; k <= nk; k++) {
          key = order[k]; out = od "/" key
          for (i = 1; i <= nc; i++) {
            v = ans[key SUBSEP cs[i] SUBSEP cp[i]]
            if (v == "") print "MISSING" > out; else print v > out
          }
          close(out)
        }
      }' "$d/otsv"

    # B == C, the diagnostic arm: it attributes a failure. If the FOLDED
    # path already disagrees with libpcre2 on a cell, that is a finding
    # about module `assertions`, not about the substitution.
    if [ -f "$d/oracle/$bid.FOLDED" ]; then
        bcd="$(diff "$d/b.out" "$d/oracle/$bid.FOLDED" 2>/dev/null \
               | grep -c '^<' || true)"
        printf 'BC\t%s\t%s\t%s\t%s\n' "$bid" "$origin" "$bcd" "$ncells"
    fi

    # ---- arm A, one artifact per generated pattern ---------------------
    while IFS=$'\t' read -r gid pol ident haslook gpat; do
        case "$POLICY" in
            all) ;;
            *) [ "$pol" = "$PFILT" ] || continue ;;
        esac
        if ! "$TIMEOUT_BIN" 60 "$PCREC" --features "$feats" -p rx \
                -o "$d/A/gen.c" -- "$gpat" 2>"$d/a.err"; then
            printf 'E\t%s\t%s\tpcrec REFUSED the %s pattern %s: %s\n' \
                "$bid" "$origin" "$pol" "$gpat" "$(head -1 "$d/a.err")"
            continue
        fi
        ncaps_a="$(grep -m1 '^#define RX_NCAPS' "$d/A/gen.h" | awk '{print $3}')"
        if [ "$ncaps_a" != "$ncaps_b" ]; then
            # THE BRACKETING RULE, checked rather than believed. `(?:` is
            # NON-CAPTURING, so the substitution must leave every group
            # number untouched — which is the whole reason the corpus's
            # `g`/`gp` cells can ride along verbatim.
            printf 'E\t%s\t%s\tGROUP COUNT MOVED under %s: folded RX_NCAPS %s, expanded %s, pattern %s\n' \
                "$bid" "$origin" "$pol" "$ncaps_b" "$ncaps_a" "$gpat"
            continue
        fi
        if ! "$TIMEOUT_BIN" 120 $CC $GENCFLAGS -I"$d/A" -o "$d/a" \
                "$BATCH" "$d/A/gen.c" 2>"$d/acc.err"; then
            printf 'E\t%s\t%s\tthe %s artifact did not compile: %s\n' \
                "$bid" "$origin" "$pol" "$(head -1 "$d/acc.err")"
            continue
        fi
        if ! "$TIMEOUT_BIN" 120 "$d/a" < "$bdir/cells" > "$d/a.out"; then
            printf 'E\t%s\t%s\tthe %s artifact did not run\n' \
                "$bid" "$origin" "$pol"
            continue
        fi
        if [ "$(grep -c . "$d/a.out")" -ne "$ncells" ]; then
            printf 'E\t%s\t%s\tthe %s artifact answered %s of %s cells\n' \
                "$bid" "$origin" "$pol" "$(grep -c . "$d/a.out")" "$ncells"
            continue
        fi
        abd="$(diff "$d/a.out" "$d/b.out" 2>/dev/null | grep -c '^<' || true)"
        acd="$(diff "$d/a.out" "$d/oracle/$gid" 2>/dev/null \
               | grep -c '^<' || true)"
        printf 'R\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$bid" "$gid" "$pol" "$ident" "$haslook" "$ncells" \
            "$abd" "$acd" "$gpat"
        if [ "$abd" != "0" ] || [ "$acd" != "0" ]; then
            # A DISAGREEING CELL IS A FINDING ABOUT THE COMPILER, and the
            # minimal witness is printed here so the triage does not need
            # the temp tree. The printer itself is `emit_witnesses` above,
            # shared with §1d's positive control.
            emit_witnesses "$bdir/cells" "$d/a.out" "$d/b.out" \
                "$d/oracle/$gid" "$pol" "$bid" "$gid" "$gpat" "$pat"
        fi
    done < "$bdir/gen.tsv"
    exit 0
fi

# =========================================================================
# THE PARENT
# =========================================================================
WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "expansion-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() { echo; echo "checks passed: $pass"; echo "checks failed: $fail"; \
           [ "$fail" -eq 0 ] || exit 1; exit 0; }
die()    { bad "$1"; finish; }

[ -x "$PCREC" ] || die "compiler $PCREC is missing or not executable — run \`make\` first"
[ -f "$ORACLE" ] || die "the shared libpcre2 oracle $ORACLE is missing"
[ -f "$BATCH" ]  || die "the shared batch driver $BATCH is missing"
[ -f "$GENERATOR" ] || die "the corpus generator $GENERATOR is missing"
[ -d "$CORPUS" ] || die "the assertions corpus $CORPUS is missing — this driver substitutes FROM it"

# ---- the libpcre2 oracle, or a LOUD skip --------------------------------
if ! python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT_DIR', 'docs', 'design',
                                'eng_brep_measurements', 'probes'))
import pcre2_ctypes" 2>"$WORKDIR/oracle.log"; then
    echo "SKIP: libpcre2 is not available, so this differential cannot run:"
    sed 's/^/  /' "$WORKDIR/oracle.log"
    echo "SKIP: the A == C arm has no oracle, and A == B ALONE IS NOT THE CHECK"
    echo "SKIP: (a compiler consistently wrong in both lowerings passes it)"
    echo "SKIP: tests/lookaround/run_expansion_diff.sh SKIPPED (no oracle)"
    echo
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

# =========================================================================
# §0 THE EXPANSION TABLE, RE-VERIFIED AGAINST libpcre2 BEFORE IT IS USED
# =========================================================================
# The table in `expand_corpus.py` is a TRANSCRIPTION (design §6.1 / D66 /
# [DD-11]). A transcription can be wrong, and a wrong one would generate a
# corpus of patterns that are not equivalent to their sources — which the
# three-way check would then report as a compiler failure. So the table is
# checked here first, by libpcre2 ALONE: folded vs expanded, both arms
# carrying the SAME option state, over a boundary subject set at every
# startpos. pcrec does not run in this section at all.
#
# THE SAME OPTION STATE IS NOT A DETAIL. §6.5 records that the first version
# of this measurement put `(?m)` on the FOLDED arm only, so a `$` tail meant
# `(?m)$` on one side and plain `$` on the other, and it reported 3
# disagreements — which, published, would have read as "the D66 expansion is
# not equivalent to `(?m)^`" and would have killed the hand-off.
#
# AND IT CARRIES ITS OWN FAILING DIRECTION. `\A|(?<=\n)` is the D66 expansion
# with the `(?!\z)` term DROPPED, and it is asserted to DISAGREE on an exact
# nonzero number of cells. A table check that could only report agreement
# would report agreement for a table of nine identity rows.
S0DIR="$WORKDIR/s0"
mkdir -p "$S0DIR/subjects"
python3 - "$S0DIR" <<'PY'
import os, sys
d = sys.argv[1]
# The boundary set: newlines first, last, doubled and absent; word/non-word
# transitions at both ends; an empty subject. §6.1 measured over 18 subjects.
subjects = ["", "a", "\n", "a\n", "\na", "ab", "a b", "a\nb", "ab\ncd",
            "a\n\nb", "\n\n", "_1", "a-b", "  ", "x\ny\nz", "\nab\n",
            "a\n\n", "q"]
for i, s in enumerate(subjects):
    open(os.path.join(d, "subjects", "s%02d" % i), "wb").write(
        s.encode("latin-1"))
# THE TABLE, WRITTEN OUT A SECOND TIME AND ON PURPOSE. This section exists to
# catch a mistranscription, so it may not import the table it is checking —
# it would then be checking a copy of itself. These rows are read off design
# §6.1's table independently.
rows = [
    ("bs_b",   r"\b",     r"(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))", ""),
    ("bs_B",   r"\B",     r"(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))", ""),
    ("bs_Z",   r"\Z",     r"(?=\n?\z)",                       ""),
    ("caret",  r"^",      r"\A",                              ""),
    ("dollar", r"$",      r"(?=\n?\z)",                       ""),
    ("mcaret", r"^",      r"(?:\A|(?<=\n)(?!\z))",            "(?m)"),
    ("mdollar", r"$",     r"(?:(?=\n)|\z)",                   "(?m)"),
]
# THE VACUITY GUARD: the same `(?m)^` row with the `(?!\z)` term dropped. It
# is a WRONG expansion and it must SHOW as one.
vac = ("vacuity", r"^", r"(?:\A|(?<=\n))", "(?m)")
tails = ["%s", "a%s", "%sa", "a%sb", "(a)%s", "%s|q"]
out = []
for name, folded, expanded, opt in rows + [vac]:
    for ti, t in enumerate(tails):
        out.append("%s.%d.f\t1\t%s%s" % (name, ti, opt, t % folded))
        out.append("%s.%d.e\t1\t%s%s" % (name, ti, opt, t % expanded))
open(os.path.join(d, "pats.tsv"), "w").write("\n".join(out) + "\n")
open(os.path.join(d, "nrows"), "w").write("%d\n" % (len(rows) * len(tails)))
PY
if ! "$TIMEOUT_BIN" 300 python3 "$ORACLE" "$S0DIR/pats.tsv" \
        "$S0DIR/subjects" "$S0DIR/otsv" 2>"$S0DIR/err"; then
    die "§0 the libpcre2 oracle failed on the expansion table: $(head -2 "$S0DIR/err")"
fi
s0_cells=0; s0_bad=0; s0_rows=0
for name in bs_b bs_B bs_Z caret dollar mcaret mdollar; do
    for ti in 0 1 2 3 4 5; do
        awk -F'\t' -v k="$name.$ti.f" '$1 == k {print $4}' "$S0DIR/otsv" \
            > "$S0DIR/f"
        awk -F'\t' -v k="$name.$ti.e" '$1 == k {print $4}' "$S0DIR/otsv" \
            > "$S0DIR/e"
        nf=$(grep -c . "$S0DIR/f"); ne=$(grep -c . "$S0DIR/e")
        if [ "$nf" -eq 0 ] || [ "$nf" -ne "$ne" ]; then
            bad "§0 row $name tail $ti produced $nf folded and $ne expanded cells"
            s0_bad=$((s0_bad + 1)); continue
        fi
        s0_rows=$((s0_rows + 1))
        s0_cells=$((s0_cells + nf))
        dd=$(diff "$S0DIR/f" "$S0DIR/e" | grep -c '^<' || true)
        if [ "$dd" -ne 0 ]; then
            bad "§0 THE EXPANSION TABLE IS WRONG: row $name tail $ti disagrees with its folded form on $dd of $nf cells under libpcre2 — the generated corpus would not be equivalent to its source"
            s0_bad=$((s0_bad + 1))
        fi
    done
done
if [ "$s0_bad" -eq 0 ] && [ "$s0_rows" -eq 42 ] && [ "$s0_cells" -gt 0 ]; then
    ok "§0 the expansion table: 7 expandable rows × 6 tails = $s0_rows patterns / $s0_cells cells under libpcre2 10.46, every startpos, BOTH ARMS carrying the same option state — 0 disagreements. The table this driver substitutes FROM is verified before it is used, and it is verified against something that is not pcrec"
else
    bad "§0 the expansion table check evaluated $s0_rows of 42 rows with $s0_bad failures over $s0_cells cells"
fi
# the failing direction
vac_bad=0
for ti in 0 1 2 3 4 5; do
    awk -F'\t' -v k="vacuity.$ti.f" '$1 == k {print $4}' "$S0DIR/otsv" > "$S0DIR/f"
    awk -F'\t' -v k="vacuity.$ti.e" '$1 == k {print $4}' "$S0DIR/otsv" > "$S0DIR/e"
    vac_bad=$((vac_bad + $(diff "$S0DIR/f" "$S0DIR/e" | grep -c '^<' || true)))
done
# EXACT, MEASURED on this subject set at this wave, never a floor: `(?m)^`
# expanded WITHOUT the `(?!\z)` conjunct is wrong on the cells where the
# subject ENDS in a newline — the expansion then asserts a line start at the
# very end of the subject, where PCRE2's `(?m)^` does not. MEASURED 16 cells
# over this 18-subject, 6-tail sweep. If this number moves, the subject set
# moved; re-derive it from a run and change it DELIBERATELY.
if [ "$vac_bad" -eq 16 ]; then
    ok "§0 THE VACUITY GUARD (the failing direction): the D66 expansion with its \`(?!\\z)\` term DROPPED disagrees with \`(?m)^\` on exactly $vac_bad cells. §0's zeros above are therefore RESULTS and not a property of a check that can only report agreement"
else
    bad "§0 the vacuity guard reports $vac_bad disagreeing cells, not the 16 measured at this wave — either the subject set moved or the guard has stopped discriminating, and a table check that cannot fail cannot pass either"
fi

# =========================================================================
# §1 THE POPULATION — generated, printed, and ASSERTED against §6.3
# =========================================================================
PLAN="$WORKDIR/plan"
if ! "$TIMEOUT_BIN" 300 python3 "$GENERATOR" "$CORPUS" "$PLAN" \
        > "$WORKDIR/pop.txt" 2>"$WORKDIR/pop.err"; then
    die "§1 the corpus generator failed: $(head -3 "$WORKDIR/pop.err")"
fi
sed 's/^/  /' "$WORKDIR/pop.txt"
cnt() { awk -F'\t' -v k="$1" '$1 == k {print $2}' "$PLAN/counts.tsv"; }
# §6.3's measured table, transcribed. A DELTA IS EXPLAINED, NEVER ABSORBED:
# the assertions corpus can grow, and when it does these numbers must be
# re-derived from a run and changed deliberately — a floor would let the
# population shrink, and a shrinking population is the one failure a green
# run cannot show.
exp_pop="tot_blocks=468 tot_beh=10120 tot_g=67 \
qual_blocks=263 qual_beh=8260 qual_g=13 \
q1_blocks=87 q1_cells=0 q2_blocks=87 q2_cells=754 \
q3_blocks=0 q3_cells=0 q4_blocks=31 q4_cells=1106 \
q5_blocks=0 q5_cells=0 q6_blocks=0 q6_cells=0 \
p1_patterns=263 p2_patterns=361 \
p1_identity=56 p2_identity=84 p1_lookaround=199 p2_lookaround=248"
pop_bad=0
for kv in $exp_pop; do
    k="${kv%%=*}"; want="${kv#*=}"; got="$(cnt "$k")"
    if [ "$got" != "$want" ]; then
        bad "§1 population: $k is $got on HEAD, not the $want design §6.3 measured — re-derive from this run and change the literal DELIBERATELY, with the corpus change that caused it named"
        pop_bad=$((pop_bad + 1))
    fi
done
if [ "$pop_bad" -eq 0 ]; then
    ok "§1 the population: 468 blocks / 10,120 behavioural cells re-counted on HEAD, 263 blocks / 8,260 cells QUALIFYING, and the six per-rule disqualification counts (Q1 87/0, Q2 87/754, Q3 0/0, Q4 31/1106, Q5 0/0, Q6 0/0) EXACT against design §6.3. No delta"
fi
# THE IDENTITY ROWS, asserted rather than tolerated. `\A` and `\z` are
# PRIMITIVES in §6.1, so an occurrence-level substitution of one of them is
# the identity — 56 of P1's 263 patterns and 84 of P2's 361. They are
# EXCLUDED from the headline below, because a row that substituted nothing
# proves nothing about the lookaround path. `p2_identity` is exactly the
# `\A` + `\z` occurrence count (37 + 47), which is what makes it a
# derivation rather than a tolerance.
na="$(cnt occ_bs_A)"; nz="$(cnt occ_bs_z)"
if [ "$(cnt p2_identity)" = "$((na + nz))" ]; then
    ok "§1 the identity rows are ACCOUNTED FOR, not tolerated: P2's $(cnt p2_identity) identical-to-source patterns are exactly the \`\\A\` ($na) + \`\\z\` ($nz) occurrences, the two rows §6.1 calls PRIMITIVES. They are excluded from the headline cell counts below"
else
    bad "§1 P2 has $(cnt p2_identity) identical-to-source patterns but $((na + nz)) \`\\A\`/\`\\z\` occurrences — a substitution that should have changed the pattern did not, and every cell it generates is a tautology"
fi
NBLOCKS="$(grep -c . "$PLAN/blocks")"
[ "$NBLOCKS" -gt 0 ] || die "§1 the generator emitted zero work items — a run over zero blocks is a FAILURE, never a pass"

# ---- §1b THE MODULE GUARD, in the failing direction ---------------------
# Every P1 pattern that contains a lookaround must REQUIRE module
# `lookaround` to compile. Without this the driver could be generating
# patterns the assertions module happens to accept, and `A` would not be the
# new path at all. Checked on one witness per expandable table row rather
# than on all 199, because it is a property of the TEXT and one witness per
# row is what makes it a per-row claim.
MGDIR="$WORKDIR/mg"
mkdir -p "$MGDIR"
mg_ok=0; mg_bad=0
for w in 'a(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))c' \
         'a(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))c' \
         'a(?=\n?\z)' 'a(?:\A|(?<=\n)(?!\z))b' 'a(?:(?=\n)|\z)'; do
    if "$TIMEOUT_BIN" 60 "$PCREC" --features assertions,modifiers,classes -p rx \
            -o "$MGDIR/g.c" -- "$w" >/dev/null 2>&1; then
        bad "§1b $w compiled WITHOUT module lookaround — arm A is not the lookaround path"
        mg_bad=$((mg_bad + 1))
    elif "$TIMEOUT_BIN" 60 "$PCREC" --features assertions,modifiers,classes,lookaround \
            -p rx -o "$MGDIR/g.c" -- "$w" >/dev/null 2>&1; then
        mg_ok=$((mg_ok + 1))
    else
        bad "§1b $w did not compile even WITH module lookaround"
        mg_bad=$((mg_bad + 1))
    fi
done
if [ "$mg_bad" -eq 0 ] && [ "$mg_ok" -eq 5 ]; then
    ok "§1b the module guard: all $mg_ok expansion shapes are REFUSED without module \`lookaround\` and accepted with it. Arm A is the lookaround path and not the assertions path wearing different text"
else
    bad "§1b the module guard: $mg_bad of 5 expansion shapes did not behave as \`lookaround\`-gated"
fi

# ---- §1d THE WITNESS PRINTER'S POSITIVE CONTROL -------------------------
# The one path in this file that CANNOT be exercised by a green run, because
# it only executes when a cell disagrees. That is the dead-branch-reading-as-
# coverage shape, and this driver produced TWO defects in that branch on the
# day it was written (see `emit_witnesses` above), both invisible until a
# SABOTAGED tree made a cell fail. So the branch is driven here, on every run,
# over a three-cell fixture built to disagree on exactly one cell — and the
# assertion is on the PATTERN TEXT, because misquoting it was the actual
# failure both times.
WD="$WORKDIR/witness"
mkdir -p "$WD"
printf '%s\t%d\n' "$WD/s0" 0 "$WD/s0" 1 "$WD/s1" 0 > "$WD/cells"
printf 'match 0 1\nnomatch\nmatch 0 2\n' > "$WD/a"
printf 'match 0 1\nnomatch\nmatch 1 2\n' > "$WD/b"
printf 'match 0 1\nnomatch\nmatch 1 2\n' > "$WD/c"
WPAT='a(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))\Gz'
emit_witnesses "$WD/cells" "$WD/a" "$WD/b" "$WD/c" P1 bTEST bTEST.P1 \
    "$WPAT" 'a\b\Gz' > "$WD/out" 2>"$WD/err"
w_bad=0
[ "$(grep -c . "$WD/out")" -eq 1 ] || {
    bad "§1d the witness printer emitted $(grep -c . "$WD/out") lines for a fixture with exactly ONE disagreeing cell"; w_bad=1; }
grep -qF -- "A[$WPAT]=match 0 2" "$WD/out" || {
    bad "§1d the witness printer did NOT reproduce the expanded pattern VERBATIM — a witness that misquotes the pattern sends the triage after a pattern that was never compiled. It printed: $(cat "$WD/out")"; w_bad=1; }
grep -qF -- 'B[a\b\Gz]=match 1 2' "$WD/out" || {
    bad "§1d the witness printer did not reproduce the FOLDED pattern verbatim"; w_bad=1; }
grep -qF -- 'C=match 1 2' "$WD/out" || {
    bad "§1d the witness printer did not report the oracle's answer"; w_bad=1; }
[ -s "$WD/err" ] && { bad "§1d the witness printer wrote to stderr: $(head -1 "$WD/err")"; w_bad=1; }
if [ "$w_bad" -eq 0 ]; then
    ok "§1d the witness printer's positive control: one disagreeing cell of three produces exactly one witness, carrying BOTH patterns byte for byte — backslashes intact. This is the only path in the file a green run cannot otherwise reach, and it was WRONG TWICE before this control existed (\`awk -v\` escape-processing, then an env prefix on the wrong pipeline stage)"
fi

# =========================================================================
# §2/§3/§4 THE THREE-WAY CHECK, one worker per block
# =========================================================================
echo
echo "  running the three-way check over $NBLOCKS blocks at PROCS=$PROCS"
echo "  (policy $POLICY; A = pcrec on the expanded pattern, B = pcrec on the"
echo "   folded pattern, C = libpcre2 on the expanded pattern)"
RECS="$WORKDIR/records"
sed "s#^#$PLAN/#" "$PLAN/blocks" \
  | PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" POLICY="$POLICY" \
    xargs -P "$PROCS" -I{} env EXPAND_WORKER={} bash "$SCRIPT_DIR/run_expansion_diff.sh" "--policy=$POLICY" \
  > "$RECS" 2>"$WORKDIR/worker.err"

nrec="$(awk -F'\t' '$1 == "R"' "$RECS" | grep -c . || true)"
nerr="$(awk -F'\t' '$1 == "E"' "$RECS" | grep -c . || true)"
if [ "$nerr" -gt 0 ]; then
    bad "$nerr generated pattern(s) could not be evaluated at all — a pattern that did not RUN is not a pattern that agreed"
    awk -F'\t' '$1 == "E"' "$RECS" | head -10 | sed 's/^/    /' >&2
fi
if [ -s "$WORKDIR/worker.err" ]; then
    bad "the workers wrote to stderr, which they must not: $(head -1 "$WORKDIR/worker.err")"
fi
[ "$nrec" -gt 0 ] || die "the three-way check evaluated ZERO generated patterns — a comparison that compares nothing is a FAILURE, never a pass"

# ---- §1c the cell-fidelity guard's verdict ------------------------------
fblocks="$(awk -F'\t' '$1 == "F"' "$RECS" | grep -c . || true)"
fbadn="$(awk -F'\t' '$1 == "F" {s += $4} END {print s + 0}' "$RECS")"
fcells="$(awk -F'\t' '$1 == "F" {s += $5} END {print s + 0}' "$RECS")"
if [ "$fblocks" -eq "$NBLOCKS" ] && [ "$fbadn" -eq 0 ] && [ "$fcells" -gt 0 ]; then
    ok "§1c the cell-fidelity guard: arm B answers all $fcells cells of all $fblocks blocks exactly as tests/assertions/ states them. The corpus's own expectations are the one input no arm of this driver produced, so this is what makes the subject decoding load-bearing — without it a decoding bug feeds the same wrong subject to all three arms and they agree about nothing"
elif [ "$fbadn" -eq 0 ]; then
    bad "§1c the cell-fidelity guard ran on only $fblocks of $NBLOCKS blocks (it disagreed on none of the $fcells cells it did reach) — a guard that skipped a block did not clear it"
else
    bad "§1c the cell-fidelity guard: $fbadn of $fcells cells in $fblocks/$NBLOCKS blocks disagree with the corpus's OWN expectations — this driver is not reading tests/assertions/ correctly, and every comparison below it is over the wrong cells"
    awk -F'\t' '$1 == "F" && $4 != 0' "$RECS" | head -5 | sed 's/^/    /' >&2
fi

# ---- the B == C diagnostic arm ------------------------------------------
bcblocks="$(awk -F'\t' '$1 == "BC"' "$RECS" | grep -c . || true)"
bcbad="$(awk -F'\t' '$1 == "BC" {s += $4} END {print s + 0}' "$RECS")"
bccells="$(awk -F'\t' '$1 == "BC" {s += $5} END {print s + 0}' "$RECS")"
if [ "$bcblocks" -gt 0 ] && [ "$bcbad" -eq 0 ] && [ "$bccells" -gt 0 ]; then
    ok "the B == C attribution arm: the FOLDED pattern agrees with libpcre2 on all $bccells cells of $bcblocks blocks. This arm exists to ATTRIBUTE a failure — a disagreement here would be a finding about module \`assertions\`, not about the substitution"
elif [ "$bcblocks" -eq 0 ]; then
    bad "the B == C attribution arm produced no rows"
else
    bad "the B == C attribution arm: the FOLDED pattern disagrees with libpcre2 on $bcbad of $bccells cells — that is a finding about module \`assertions\`, and it must be triaged before any A != C row below is read as a lookaround defect"
fi

# ---- the per-policy verdicts --------------------------------------------
report_policy() {
    local pol="$1" want_pats="$2" want_id="$3" want_look="$4"
    local n id look cells abbad acbad nzcells
    n="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p' "$RECS" | grep -c . || true)"
    if [ "$n" -eq 0 ]; then
        bad "policy $pol produced ZERO evaluated patterns — a policy that generates nothing is a FAILURE, never a skip"
        return
    fi
    id="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p && $5 == 1' "$RECS" | grep -c . || true)"
    look="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p && $6 == 1' "$RECS" | grep -c . || true)"
    cells="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p {s += $7} END {print s + 0}' "$RECS")"
    nzcells="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p && $5 == 0 {s += $7} END {print s + 0}' "$RECS")"
    abbad="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p {s += $8} END {print s + 0}' "$RECS")"
    acbad="$(awk -F'\t' -v p="$pol" '$1 == "R" && $4 == p {s += $9} END {print s + 0}' "$RECS")"
    if [ "$n" -ne "$want_pats" ]; then
        bad "policy $pol evaluated $n patterns, not the $want_pats design §6.3 measured"
        return
    fi
    if [ "$id" -ne "$want_id" ] || [ "$look" -ne "$want_look" ]; then
        bad "policy $pol: $id patterns are textually identical to their source (expected $want_id) and $look contain a lookaround (expected $want_look) — a substitution that silently became the identity passes every comparison below and tests nothing"
        return
    fi
    if [ "$abbad" -ne 0 ] || [ "$acbad" -ne 0 ]; then
        bad "policy $pol: $abbad cells where A != B (pcrec's two lowerings of one language DISAGREE) and $acbad where A != C (pcrec disagrees with libpcre2 on the expanded pattern), over $cells cells. EVERY ONE IS A FINDING ABOUT THE COMPILER — never an expectation to adjust, never a cell to exclude"
        awk -F'\t' -v p="$pol" '$1 == "W" && $2 == p' "$RECS" | head -12 | sed 's/^/    /' >&2
        return
    fi
    case "$pol" in
      NONE)
        ok "§4 the CONTROL ARM (--policy=none): $n patterns, all $id of them textually IDENTICAL to their source by construction, $cells cells, A == B and A == C on every one. This is what makes §2/§3's zeros mean \"two lowerings agreed\" rather than \"one artifact was compared with itself\" — and it is a SEPARATE compile of the same text, not a reuse of arm B's artifact, so it exercises the whole pipeline"
        ;;
      *)
        ok "§$([ "$pol" = P1 ] && echo 2 || echo 3) policy $pol: $n generated patterns / $cells cells, $look of them carrying a real lookaround and $nzcells cells generated from a pattern that is TEXTUALLY DIFFERENT from its source — A == B (pcrec's two lowerings agree) and A == C (both agree with libpcre2 10.46) on every cell, match span AND every group span, 0 disagreements"
        ;;
    esac
}
case "$POLICY" in
    all)  report_policy P1 263 56 199
          report_policy P2 361 84 248
          report_policy NONE 263 263 0 ;;
    P1)   report_policy P1 263 56 199 ;;
    P2)   report_policy P2 361 84 248 ;;
    none) report_policy NONE 263 263 0 ;;
esac

# ---- the headline, stated once ------------------------------------------
tot_cells="$(awk -F'\t' '$1 == "R" {s += $7} END {print s + 0}' "$RECS")"
nt_cells="$(awk -F'\t' '$1 == "R" && $5 == 0 {s += $7} END {print s + 0}' "$RECS")"
lk_cells="$(awk -F'\t' '$1 == "R" && $6 == 1 {s += $7} END {print s + 0}' "$RECS")"
echo
echo "  three-way comparisons: $tot_cells cells over $nrec generated patterns"
echo "  ... of which $nt_cells came from a pattern textually DIFFERENT from its source"
echo "  ... of which $lk_cells came from a pattern that contains a LOOKAROUND"
finish
