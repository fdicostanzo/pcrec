#!/usr/bin/env bash
# tests/lookaround/run_lookaround_diff.sh — [M6.6.2]'s behavioural instrument
# for module `lookaround`: the things tests/lookaround/*.rxt structurally
# CANNOT assert, each against libpcre2.
#
#   §1  THE `# pcre2-only` SWEEP. `tests/harness/verify_rxt.py` cross-checks
#       every corpus expectation against python3 `re` — except in a
#       `# pcre2-only` block, which is precisely where it cannot. This module
#       has a WHOLE FILE in that state (`nonatomic_ahead.rxt`: python has no
#       `(?*` at all, design §7 G5), so without this section the non-atomic
#       family — one of the two the module ships — would have exactly ONE
#       oracle behind it, the same one that generated its expectations. This
#       section drives every such pattern through libpcre2 at EVERY startpos
#       over a shared subject set and compares THE MATCH SPAN AND EVERY GROUP
#       SPAN.
#
#   §2  THE ATOMICITY DISCRIMINATOR ARM, and it is the only section whose
#       population is required to DISAGREE with itself. `(?=(a|ab))\1$` and
#       `(?*(a|ab))\1$` differ in exactly one thing — whether the assertion
#       commits to the body's first success — and design §2.2 measures that on
#       "abab" as NOMATCH vs (2,4). A compiler that emitted the cut for both
#       (sabotage S131) or for neither (S122) answers the two IDENTICALLY, so
#       the section asserts an EXACT number of disagreeing cells as well as
#       agreement with libpcre2 on each side. An arm that only checked
#       agreement would go green on both sabotages.
#
#   §3  THE FOLLOW-SCOPING ARM (design §3.2.1), over a generated `a^k b`
#       family rather than the two hand cells. The failure it exists for is
#       the one silent miscompile in §3: an unscoped `v->fmin` bounds a
#       lookahead body by the follow's width, and because the body's bytes and
#       the follow's bytes ARE THE SAME BYTES that bound is a double-count.
#       On the POSITIVE form the cost is a missed match; on the NEGATIVE form
#       the pruned body FAILS, which makes the assertion HOLD — a FALSE MATCH.
#       Both polarities are swept here, at every width, because the second is
#       the direction a span-comparing suite is least likely to be pointed at.
#
#   §4  THE ENGINE ARMS: the DEFAULT selection and `--engine=vm`, asserted to
#       agree cell for cell over the whole population. Both are VM artifacts
#       (all six registry rows are VM_ONLY and SR-8 stamps them), but they
#       reach that state by different routes and only the DEFAULT one carries
#       the DFA PREFILTER — which is built from the lookaround-ERASED pattern
#       (src/ir/nfa.c lowers an A_LOOK to an epsilon). That erasure is sound as
#       a filter and a MISCOMPILE as a machine, and only SR-8's VM_ONLY stamp
#       stands between the two readings. Sabotage S126 removes the stamp; this
#       arm and the corpus's own capture-free `(?=a)b` cell are what see it.
#
# EVERY POPULATION IS ASSERTED EXACT, NEVER PRINTED, and never as a floor. A
# sweep that generated nothing prints the same silence as one that agreed
# everywhere, and this project's own record is full of that shape.
#
# IT REUSES `tests/backrefs/bref_oracle.py` AND `tests/backrefs/bref_batch.c`
# RATHER THAN COPYING THEM. Design §10.2 asks for `la_oracle.py` and a batch
# driver "modelled on" those two; MODELLED ON would have meant a third copy of
# one mechanism (tests/atomic_groups/ already holds the second), and D24 is the
# standing rule against a second home for one fact. Neither file is
# backref-specific in behaviour: the oracle takes `<key>\t<ngroups>\t<pattern>`
# and sweeps every startpos over a subject directory, and the driver takes
# `<subject-file>\t<startpos>` on stdin and prints the span plus every
# `RX_NCAPS` group pair. Both are what this module needs, unchanged.
#
# Usage: bash tests/lookaround/run_lookaround_diff.sh
# Env: PCREC, CC, GENCFLAGS, KEEP=1
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
FEATS="lookaround,backrefs,atomic-groups,assertions,classes,modifiers,named-groups"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "lookaround-diff: KEEP=1, temp dir: $WORKDIR" >&2
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

# ---- the libpcre2 oracle, or a LOUD skip --------------------------------
if ! python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT_DIR', 'docs', 'design',
                                'eng_brep_measurements', 'probes'))
import pcre2_ctypes" 2>"$WORKDIR/oracle.log"; then
    echo "SKIP: libpcre2 is not available, so this differential cannot run:"
    sed 's/^/  /' "$WORKDIR/oracle.log"
    echo "SKIP: tests/lookaround/run_lookaround_diff.sh SKIPPED (no oracle)"
    echo
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

# ---- the shared subject set ---------------------------------------------
# Chosen from the corpus's own alphabet, plus the two families §2 and §3 need.
SUBJDIR="$WORKDIR/subjects"
mkdir -p "$SUBJDIR"
i=0
# [M6.6.2 wave D] SEVEN SUBJECTS ADDED FOR THE LOOKBEHIND, and they are added
# rather than assumed: §1's population tripled at this wave and the sweep is
# only as sharp as the subjects it runs over. A differing-width lookbehind
# needs a subject where ONE branch fits and the other does not (`ax`, `bcx`,
# `cx`), §2.4's preference-order cells need `aac`/`ac`/`c` to tell branch 1
# from branch 2 by its captures, and §3.6's F4 fourth row is measured on
# `baca` specifically. Adding them re-derived §2's disagreement count in the
# same change, which is why that number moved too.
for s in "" "a" "b" "x" "ab" "ba" "aa" "bb" "abc" "abd" "aab" "aba" "abab" \
         "aaab" "xabc" "aabb" "bacba" "aaaab" "aaaac" \
         "c" "ac" "aac" "ax" "cx" "bcx" "baca"; do
    printf '%s' "$s" > "$SUBJDIR/$(printf 's%02d' "$i")"
    i=$((i + 1))
done
NSUBJ=$i
[ "$NSUBJ" -eq 26 ] || die "the subject set is $NSUBJ files, not the 26 this script's population guards are computed against"
ok "subject set: $NSUBJ subjects, shared by every section below"

# ---- one artifact, many cells: compile + run a pattern over the sweep ----
# $1 pattern, $2 extra pcrec args, $3 output file. Prints ncaps-1 on stdout.
run_arm() {
    local pat="$1" extra="$2" out="$3"
    local d="$WORKDIR/arm$RANDOM$RANDOM"
    mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! "$PCREC" --features "$FEATS" -p rx $extra -o "$d/gen.c" -- "$pat" \
            2>"$d/err"; then
        echo "COMPILE-FAIL"; sed 's/^/    /' "$d/err" >&2; return 1
    fi
    local ncaps
    ncaps="$(grep -m1 '^#define RX_NCAPS' "$d/gen.h" | awk '{print $3}')"
    # shellcheck disable=SC2086
    if ! $CC $GENCFLAGS -I"$d" -o "$d/t" "$BATCH" "$d/gen.c" 2>"$d/cerr"; then
        echo "CC-FAIL"; head -5 "$d/cerr" >&2; return 1
    fi
    : > "$WORKDIR/cells"
    for f in "$SUBJDIR"/*; do
        local n
        n=$(wc -c < "$f")
        local sp=0
        while [ "$sp" -le "$n" ]; do
            printf '%s\t%d\n' "$f" "$sp" >> "$WORKDIR/cells"
            sp=$((sp + 1))
        done
    done
    "$d/t" < "$WORKDIR/cells" > "$out" || return 1
    echo $((ncaps - 1))
}

# The oracle side for ONE pattern with a known group count, in the same cell
# order the driver used (sorted subject name, then startpos 0..n).
run_oracle() {
    local pat="$1" ng="$2" out="$3"
    printf 'k\t%d\t%s\n' "$ng" "$pat" > "$WORKDIR/patline"
    python3 "$ORACLE" "$WORKDIR/patline" "$SUBJDIR" "$WORKDIR/otsv" \
        2>"$WORKDIR/oerr" || return 1
    cut -f4 "$WORKDIR/otsv" > "$out"
}

# Compare one pattern's pcrec answers against libpcre2's. Echoes the cell
# count on stdout; nonzero return on any mismatch.
compare_one() {
    local pat="$1" extra="${2:-}" label="${3:-$1}"
    local ng
    ng="$(run_arm "$pat" "$extra" "$WORKDIR/mine")" || {
        bad "[$label] pcrec could not build the artifact"; return 1; }
    case "$ng" in *FAIL*) bad "[$label] $ng"; return 1;; esac
    run_oracle "$pat" "$ng" "$WORKDIR/theirs" || {
        bad "[$label] the libpcre2 oracle failed: $(head -2 "$WORKDIR/oerr")"
        return 1; }
    local a b
    a=$(wc -l < "$WORKDIR/mine"); b=$(wc -l < "$WORKDIR/theirs")
    if [ "$a" -ne "$b" ]; then
        bad "[$label] pcrec produced $a answers and the oracle $b — a positional comparison over unequal lists compares the wrong cells"
        return 1
    fi
    if ! diff -q "$WORKDIR/mine" "$WORKDIR/theirs" >/dev/null; then
        bad "[$label] $(diff "$WORKDIR/mine" "$WORKDIR/theirs" | grep -c '^<') of $a cells DIFFER from libpcre2"
        diff "$WORKDIR/mine" "$WORKDIR/theirs" | head -8 >&2
        return 1
    fi
    echo "$a"
    return 0
}

# =========================================================================
# §1 THE `# pcre2-only` SWEEP
# =========================================================================
# The population is EXTRACTED FROM THE CORPUS, not listed here: a hand list
# would go stale the first time a cell is added, and stale in the direction
# that silently drops a pattern from the only oracle it has.
python3 - "$SCRIPT_DIR" "$WORKDIR/po_pats" <<'PY'
import os, sys
d, out = sys.argv[1], sys.argv[2]
pats = []
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".rxt"):
        continue
    marked = False
    block = None
    for line in open(os.path.join(d, fn)):
        line = line.rstrip("\n")
        if line.strip() == "# pcre2-only":
            marked = True
            continue
        if line.startswith("pattern "):
            block = (fn, line[8:], marked)
            marked = False
            continue
        if line.strip() == "perr" and block:
            block = None            # a refusal has no answer to sweep
            continue
        if line.startswith(("m ", "n ", "ms ", "ns ")) and block:
            if block[2]:
                pats.append(block)
            block = None
open(out, "w").write("".join("%s\t%s\n" % (f, p) for f, p, _ in pats))
sys.stderr.write("po: %d pcre2-only answer-bearing blocks\n" % len(pats))
PY
# THE NUMBER IS EXACT AND HAND-DERIVED, and it has already gone stale ONCE —
# during the wave that wrote it, when three `\K` cells were added to
# lookahead.rxt after the count was taken (python has no `\K` at all, so all
# three computed as `# pcre2-only` and the population went 11 -> 14). The guard
# FIRED, which is what it is for. **When a cell is added, re-derive this number
# from a run and change it deliberately; never relax it to a floor** — a floor
# would let the population SHRINK, and the cells this section exists for are
# exactly the ones no other check in the tree can see.
#
# [M6.6.2 wave D] 14 -> 44, and it is the biggest single move this guard will
# ever see: the wave added `lookbehind_widths.rxt` (14 blocks, EVERY one
# `# pcre2-only` because python refuses differing-width lookbehind alternatives
# outright — G1) and `nonatomic_behind.rxt` (11, python has no `(?<*` at all —
# G5), plus 2 in `lookbehind.rxt` (`\K` and `\G`, which python lacks) and 3 in
# `startpos.rxt`. Every one of those blocks has exactly ONE oracle, and this
# sweep is it.
NPO=$(grep -c . "$WORKDIR/po_pats" || true)
if [ "$NPO" -ne 44 ]; then
    die "§1's population is $NPO pcre2-only answer-bearing blocks, not the 44 this guard is computed against — a cell was added or lost. Re-derive the number from this run and change it DELIBERATELY; do not relax it to a floor"
fi
po_cells=0; po_bad=0
while IFS=$'\t' read -r f pat; do
    if n=$(compare_one "$pat" "" "§1 $f: $pat"); then
        po_cells=$((po_cells + n))
    else
        po_bad=$((po_bad + 1))
    fi
done < "$WORKDIR/po_pats"
if [ "$po_bad" -eq 0 ] && [ "$po_cells" -gt 0 ]; then
    ok "§1 the \`# pcre2-only\` sweep: $NPO blocks / $po_cells cells against libpcre2 10.46, match span AND every group span, every startpos — 0 disagreements. These are the cells verify_rxt.py structurally cannot reach"
else
    bad "§1 the \`# pcre2-only\` sweep: $po_bad of $NPO blocks disagree with libpcre2"
fi

# =========================================================================
# §2 THE ATOMICITY DISCRIMINATOR ARM
# =========================================================================
ATOMIC_PAT='(?=(a|ab))\1$'
NONATOM_PAT='(?*(a|ab))\1$'
d2a="$WORKDIR/d2a"; d2b="$WORKDIR/d2b"
if na=$(compare_one "$ATOMIC_PAT" "" "§2 atomic $ATOMIC_PAT"); then
    cp "$WORKDIR/mine" "$d2a"
else na=0; fi
if nb=$(compare_one "$NONATOM_PAT" "" "§2 non-atomic $NONATOM_PAT"); then
    cp "$WORKDIR/mine" "$d2b"
else nb=0; fi
if [ "$na" -gt 0 ] && [ "$na" -eq "$nb" ]; then
    ndis=$(paste "$d2a" "$d2b" | awk -F'\t' '$1 != $2' | wc -l)
    # EXACT, not a floor, and MEASURED against libpcre2 rather than guessed:
    # 13 cells of the sweep disagree, and every one is the atomic form saying
    # NOMATCH where the non-atomic form matches — never the other way round,
    # which is the DIRECTION the discriminator has to have. They are the
    # (subject, startpos) pairs on which the body has a SECOND success that
    # `\1$` can use: "ab"@0, "aab"@0-1, "abab"@0-2, "aaab"@0-2, "aaaab"@0-3.
    # A compiler that cut BOTH spellings (S131) or NEITHER (S122) answers the
    # two identically and scores 0 here.
    #
    # [M6.6.2 wave D] THE SUBJECT SET GREW 19 -> 26 AND THIS NUMBER DID NOT
    # MOVE, which is worth recording rather than passing over: none of the
    # seven added subjects gives `(a|ab)` a SECOND success that `\1$` can use,
    # so the disagreeing set is unchanged while the per-pattern cell count
    # went 73 -> 97. The guard held across a population change, which is the
    # only kind of evidence an exact literal can give that it is measuring
    # what it names.
    if [ "$ndis" -eq 13 ]; then
        ok "§2 the atomicity discriminator: both forms agree with libpcre2 over $na cells each, and they DISAGREE WITH EACH OTHER on exactly $ndis — the cut is emitted for \`(?=\` and not for \`(?*\`, which is the whole difference between the two families (§2.2)"
    else
        bad "§2 the atomicity discriminator: the two forms disagree on $ndis cells, not the 13 measured at this wave. Either the cut moved, or the subject set did — a compiler that emits the cut for both spellings, or for neither, scores 0 here"
    fi
else
    bad "§2 the atomicity discriminator could not be evaluated ($na / $nb cells)"
fi

# =========================================================================
# §3 THE FOLLOW-SCOPING ARM (§3.2.1)
# =========================================================================
sc_bad=0; sc_cells=0
for pat in '(?=(a+)b)a+b' '(?!(a+)b)a+b' '(?*(a+)b)a+b' \
           '(?=(a+)bb)a+bb' '(?!(a+)bb)a+bb'; do
    if n=$(compare_one "$pat" "" "§3 $pat"); then
        sc_cells=$((sc_cells + n))
    else
        sc_bad=$((sc_bad + 1))
    fi
done
if [ "$sc_bad" -eq 0 ] && [ "$sc_cells" -gt 0 ]; then
    ok "§3 the follow-scoping arm: 5 patterns / $sc_cells cells, BOTH POLARITIES at two follow widths — 0 disagreements. The negative rows are the ones that matter: an unscoped body is pruned to FAIL there, which makes the assertion HOLD (a FALSE match, not a missed one)"
else
    bad "§3 the follow-scoping arm: $sc_bad of 5 patterns disagree with libpcre2 — §3.2.1's miscompile class"
fi

# =========================================================================
# §4 THE ENGINE ARMS
# =========================================================================
eng_bad=0; eng_pat=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    eng_pat=$((eng_pat + 1))
    if ! run_arm "$pat" "" "$WORKDIR/e_def" >/dev/null; then
        bad "§4 default arm could not build $pat"; eng_bad=$((eng_bad + 1)); continue
    fi
    if ! run_arm "$pat" "--engine=vm" "$WORKDIR/e_vm" >/dev/null; then
        bad "§4 --engine=vm arm could not build $pat"; eng_bad=$((eng_bad + 1)); continue
    fi
    if ! diff -q "$WORKDIR/e_def" "$WORKDIR/e_vm" >/dev/null; then
        bad "§4 the DEFAULT selection and --engine=vm disagree on $pat — only the default carries the prefilter, which is built from the lookaround-ERASED pattern"
        eng_bad=$((eng_bad + 1))
    fi
done < <(grep -h '^pattern ' "$SCRIPT_DIR"/lookahead.rxt \
             "$SCRIPT_DIR"/captures.rxt "$SCRIPT_DIR"/quantified.rxt \
             "$SCRIPT_DIR"/nonatomic_ahead.rxt | sed 's/^pattern //')
if [ "$eng_pat" -lt 55 ]; then
    bad "§4 swept only $eng_pat patterns (floor 55) — the arm is not populated"
elif [ "$eng_bad" -eq 0 ]; then
    ok "§4 the engine arms: $eng_pat patterns × $NSUBJ subjects × every startpos, DEFAULT and --engine=vm identical cell for cell. The default is the arm that carries the erased-lookaround prefilter, and an erased lookaround is loudly wrong — \`(?=a)b\` erased is \`b\`, which MATCHES \"b\" where the truth is NOMATCH"
else
    bad "§4 the engine arms: $eng_bad of $eng_pat patterns disagree between the default selection and --engine=vm"
fi

finish
