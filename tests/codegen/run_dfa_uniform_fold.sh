#!/usr/bin/env bash
# tests/codegen/run_dfa_uniform_fold.sh — [CC-DIFF] STEP 1 (b):
# `<PREFIX>_DFA_UNIFORM_FOLDS`, held to the artifact's own text rather than to
# the scan that wrote it.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# pcrec BUILDS its DFA tables, so at emission time it knows whether every cell
# of one holds the same value. When one does, the indexed load is a CONSTANT:
# the table is NOT EMITTED and the accessor returns the constant instead
# (`docs/spec/match_api.md` §6.3; `docs/dev/ccdiff_step0.md` §1 is the
# measurement — gcc 15 does not fold a variable-index load from an all-equal
# `static const` array, and LLVM does).
#
#     #define RX_DFA_UNIFORM_FOLDS 4   /* four tables folded out */
#     #define RX_DFA_UNIFORM_FOLDS 0   /* every table is really there */
#
# THE CONTRACT, in the spec's own words: the number of this artifact's DFA
# tables whose cells were ALL EQUAL and which are therefore NOT EMITTED. Two
# per machine are foldable (`<m>_next_state`, `<m>_is_accepting`), over the
# machines the artifact actually CONTAINS — forward always, reverse unless the
# search is start-pinned, anchored under `_DFA_MATCH "unwrapped"` — so `0..6`.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3, and it is the whole design of this file. The
# stamp's value comes from `fold_tr`/`fold_acc` scanning the Dfa. This check
# never scans a Dfa and never re-reads uniformity: it reads the EMITTED TEXT
# for two facts that the fold makes true TOGETHER and that nothing else in the
# emitter makes true at all —
#
#   (1) the accessor lost its TABLE PARAMETER, so its declaration reads
#       `<m>_step(<m>_state s, unsigned cl)` rather than
#       `<m>_step(const unsigned short *transitions, ...)`; and
#   (2) the table's NAME does not occur anywhere in the file.
#
# and asserts the biconditional between them, and then the stamp against their
# count. A fold that emitted a constant while leaving the table is a RED here;
# so is a table deleted from under an accessor that still takes it (which
# would not compile, but this file says so BEFORE the compiler does, and names
# the reason); so is a stamp that has drifted from either.
#
# WHY (2) IS "ANYWHERE IN THE FILE" AND NOT "NO ARRAY DEFINITION". The fold's
# real hazard is a READ SITE the change missed — `emit_dfa.c` names these
# tables at seven emitted call sites and the omission of any one of them is
# how the fold ships a matcher that names an array that is not there. A
# whole-file absence test covers every one of them without enumerating them,
# which is the property an enumerated list of read sites would lose the next
# time a site is added.
#
# THE ENGINE DISCRIMINATOR IS `_byte_class[256]` — machine text, emitted
# unconditionally by every DFA scan of either engine and never folded by this
# change — and NOT `RX_DFA_SCAN`. Reading a macro to decide which artifacts to
# check the macros on is the circularity `run_dfa_stamps.sh` refuses in a
# comment, and this file inherits the refusal.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "dfa-uniform-fold: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: dfa-uniform-fold: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

emit() { # emit <outfile> <pattern> [extra args...]
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --features all "$@" -o "$out" -- "$pat" >/dev/null 2>&1
}

# THE TEXT READER, one `awk` per artifact. Prints five numbers:
#
#   dfa       1 if the artifact contains a DFA scan (a `_byte_class[256]`)
#   nstamp    how many times the macro is defined (must be 0 or 1)
#   stamp     its value, or -1 when absent
#   folded    accessors whose parameter list has lost its table pointer
#   ghost     folded accessors whose table name STILL occurs in the file,
#             plus unfolded accessors whose table name does NOT
#
# `ghost` is the biconditional of the header, counted rather than described,
# and any nonzero value is a red.
read_art() {
    awk '
      /_byte_class\[256\]/                       { dfa = 1 }
      # [CC-DIFF] STEP 1(b) FAMILY 4 FIX: the empty-engine bucket
      # ("\\B\\b" and its three run_dfa_stamps.sh-documented siblings --
      # a pattern proven to match nothing) has RX_DFA_SCAN "empty" and
      # RX_DFA_UNIFORM_FOLDS 0 legitimately stamped, but its rx_search
      # body is one `return 0;` with no loop and therefore no
      # _byte_class[256] table at all -- the "every DFA scan emits it
      # unconditionally" premise this file states at its own top does
      # not cover this named, narrow exception. Its body is this exact,
      # deterministic two-cast-then-return shape (verified against all
      # four corpus members: \\B\\b, \\b\\B, \\d\\b\\w, a\\bb), so it is
      # its own independent text signal rather than a read of RX_DFA_SCAN
      # (which would be exactly the circularity this file refuses).
      emptycast && /^    return 0;$/                 { dfa = 1 }
      /^    \(void\)subject; \(void\)subject_length; \(void\)search_from; \(void\)capture_spans;$/ { emptycast = 1 }
      !/^    \(void\)subject; \(void\)subject_length; \(void\)search_from; \(void\)capture_spans;$/ { emptycast = 0 }
      /^#define RX_DFA_UNIFORM_FOLDS /            { nstamp++; stamp = $3 }
      # An accessor declaration names its machine in the function name; the
      # table it reads is that machine name plus a fixed suffix, so the two
      # halves of the biconditional are derived from ONE capture and cannot
      # be pointed at different machines by a typo here.
      /^static inline .*_step\(/ {
          split($0, a, "_step\\("); split(a[1], b, " "); fn = b[length(b)]
          tbl = fn "_next_state"
          if (index($0, "_step(const ")) unf[tbl] = 1; else fld[tbl] = 1
      }
      /^static inline int .*_accepts\(/ {
          split($0, a, "_accepts\\("); split(a[1], b, " "); fn = b[length(b)]
          tbl = fn "_is_accepting"
          if (index($0, "_accepts(const ")) unf[tbl] = 1; else fld[tbl] = 1
      }
      { line[NR] = $0 }
      END {
          folded = 0; ghost = 0
          # [CC-DIFF] STEP 1(b) FAMILY 4 FIX: a bare substring test on the
          # folded table NAME false-positives on a [M6.2-WORDB] class-
          # indexed sibling table -- rx_forward_is_accepting_by_class
          # CONTAINS rx_forward_is_accepting as a leading substring, and is
          # a real, unfolded, unrelated table (the machine reads it through
          # a DIFFERENT accessor, rx_forward_accepts_class, whenever a
          # word-boundary construct routes accept through the class axis
          # instead of the scalar one). A true leftover reference to the
          # folded name is never followed by another identifier
          # character, so requiring that boundary keeps the real-leftover
          # case (a ghost table pointer or a stray mention) while dropping
          # this one, verified on \\Bcat / \\B\\w+\\B.
          for (t in fld) {
              folded++
              re = t "([^A-Za-z0-9_]|$)"
              for (i = 1; i <= NR; i++) if (line[i] ~ re) { ghost++; break }
          }
          for (t in unf) {
              seen = 0
              # the DEFINITION, `static const <type> <t>[`, not a mention
              for (i = 1; i <= NR; i++)
                  if (index(line[i], " " t "[") && index(line[i], "static const")) { seen = 1; break }
              if (!seen) ghost++
          }
          printf "%d %d %s %d %d\n", dfa+0, nstamp+0, (nstamp ? stamp : -1), folded, ghost
      }' "$1"
}

# =========================================================================
# §1 NAMED WITNESSES — expectations are LITERALS, never harvested
# =========================================================================
# Each row states the count it expects, so a compiler that stamped `folded`
# back to itself would still have to produce the right NUMBER of folded
# accessors for the right pattern.
witness() { # witness <label> <pattern> <expected count> [args...]
    local lbl="$1" pat="$2" want="$3"; shift 3
    local f="$WORKDIR/w.c"
    emit "$f" "$pat" "$@" || { bad "§1 [$lbl] '$pat' did not compile"; return; }
    set -- $(read_art "$f")
    local dfa="$1" nstamp="$2" stamp="$3" folded="$4" ghost="$5"
    [ "$dfa" -eq 1 ] || { bad "§1 [$lbl] '$pat' contains no DFA scan — this witness cannot test a DFA-scan macro"; return; }
    [ "$nstamp" -eq 1 ] || { bad "§1 [$lbl] '$pat' defines RX_DFA_UNIFORM_FOLDS $nstamp times, expected exactly 1 (spec §6.3: unconditional on every artifact containing a DFA scan)"; return; }
    [ "$stamp" = "$want" ] || bad "§1 [$lbl] '$pat' stamps RX_DFA_UNIFORM_FOLDS $stamp, expected $want"
    [ "$folded" = "$want" ] || bad "§1 [$lbl] '$pat' stamps $stamp but carries $folded folded accessors, expected $want — the stamp and the emitted text have come apart"
    [ "$ghost" -eq 0 ] || bad "§1 [$lbl] '$pat': $ghost accessor/table pairs disagree — a folded accessor whose table is still named, or an unfolded one whose table is missing"
}

# `[a-z]{0,4}` is the bench's `cls-upto-4`, the cell [CC-DIFF] STEP 0 measured
# at 0.589: [OPT-5]'s scan edge absorbs every real transition, leaving the
# forward AND anchored machines' four tables uniform, and axis J pins the
# search so there is no reverse machine to fold. `abc` is the control at the
# other end — a literal machine whose tables are full of real work.
witness "bounded class, everything folds" '[a-z]{0,4}' 4
witness "literal, nothing folds"          'abc'        0
witness "digits, nothing folds"           '[0-9]+x'    0
[ "$fail" -eq 0 ] && ok "§1 three named witnesses stamp the documented count, and it equals the folded accessors they actually carry"

# THE NEGATIVE CONTROL FOR THE VALUE SET (K35): without it every row above
# would pass on a compiler that stamped one constant. Two rows expect 0 and
# one expects 4 — but only if both a folding and a non-folding artifact are
# genuinely reachable, which this asserts rather than infers.
nz=0; z=0
for p in '[a-z]{0,4}' 'abc' '[0-9]+x' '[a-f]{0,8}'; do
    emit "$WORKDIR/n.c" "$p" || continue
    v="$(grep -m1 '^#define RX_DFA_UNIFORM_FOLDS ' "$WORKDIR/n.c" | awk '{print $3}')"
    [ "${v:-0}" -gt 0 ] 2>/dev/null && nz=$((nz + 1)) || z=$((z + 1))
done
if [ "$nz" -ge 1 ] && [ "$z" -ge 1 ]; then
    ok "§1 both outcomes are live in the witness set ($nz folding, $z not) — a compiler stamping a constant fails this file"
else
    bad "§1 only ONE outcome is reachable in the witness set ($nz folding, $z not): every row above is comparing a build against one constant"
fi

# =========================================================================
# §2 A PURE-VM ARTIFACT DOES NOT DEFINE IT — the other half of the IFF
# =========================================================================
# The macro is emitted by `pcrec_emit_dfa_scan_stamps`, which a VM HYBRID also
# reaches (it inlines this emitter's scan). A NON-hybrid VM artifact contains
# no DFA scan and must carry neither the macro nor a `_byte_class`.
emit "$WORKDIR/v.c" '(a)\1' --engine=vm || bad "§2 '(a)\\1 --engine=vm' did not compile"
if grep -q '_byte_class\[256\]' "$WORKDIR/v.c"; then
    bad "§2 the pure-VM witness contains a DFA scan — this section cannot test the VM side"
elif grep -q 'RX_DFA_UNIFORM_FOLDS' "$WORKDIR/v.c"; then
    bad "§2 an artifact with no DFA scan defines RX_DFA_UNIFORM_FOLDS — it has no table to fold, so the macro is meaningless there (spec §6.3: the _DFA_* family's IFF)"
else
    ok "§2 an artifact with no DFA scan defines NO RX_DFA_UNIFORM_FOLDS, which is the other half of the macro's IFF"
fi

# A FORCED HYBRID is the population where "hybrids INCLUDED" is actually at
# risk: nothing else in the tree compiles a VM artifact that carries a DFA
# scan, so a macro emitted one level too low would pass a default-only sweep.
if emit "$WORKDIR/h.c" '(foo)[0-9]+bar' -fprefilter; then
    if grep -q '_byte_class\[256\]' "$WORKDIR/h.c" && grep -q '^    goto rx_L0;' "$WORKDIR/h.c"; then
        if grep -qc '^#define RX_DFA_UNIFORM_FOLDS ' "$WORKDIR/h.c" >/dev/null && \
           [ "$(grep -c '^#define RX_DFA_UNIFORM_FOLDS ' "$WORKDIR/h.c")" -eq 1 ]; then
            ok "§2 a FORCED HYBRID — a VM program carrying an inlined DFA scan — defines the macro exactly once"
        else
            bad "§2 a forced hybrid contains a DFA scan and does NOT define RX_DFA_UNIFORM_FOLDS exactly once"
        fi
    else
        bad "§2 '(foo)[0-9]+bar -fprefilter' did not produce a hybrid (VM program + inlined DFA scan) — this row cannot test hybrids"
    fi
else
    bad "§2 '(foo)[0-9]+bar -fprefilter' did not compile"
fi

# =========================================================================
# §3 THE CORPUS SWEEP
# =========================================================================
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -lt 2620 ]; then
    bad "dfa-uniform-fold: corpus extraction found only $npat patterns, below the 2620 floor (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

# Sharded by LINE CHUNKS of the pattern file, never an `xargs` over pattern
# TEXT: a pattern is arbitrary bytes and every quoting scheme for passing one
# as an argument is a bug waiting to be found by the corpus.
cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD: worker could not load pcrec_run"; exit 1; }
art="$WORKDIR/a.$$.c"
trap 'rm -f "$art"' EXIT
one() { # one <axis-label> <extra pcrec args...>
    local ax="$1"; shift
    if ! pcrec_run "$PCREC" --features all -p rx "$@" -o - -- "$pat" > "$art" 2>/dev/null; then
        echo "REFUSED-$ax"; return
    fi
    set -- $(READ_ART "$art")
    local dfa="$1" nstamp="$2" stamp="$3" folded="$4" ghost="$5"
    if [ "$dfa" -eq 0 ]; then
        echo "NODFA-$ax"
        [ "$nstamp" -eq 0 ] || echo "BAD: RX_DFA_UNIFORM_FOLDS on an artifact with no DFA scan ($ax): $pat"
        return
    fi
    echo "DFA-$ax"
    [ "$nstamp" -eq 1 ] || { echo "BAD: RX_DFA_UNIFORM_FOLDS appears $nstamp times on an artifact containing a DFA scan, expected exactly 1 ($ax): $pat"; return; }
    case "$stamp" in ''|*[!0-9]*) echo "BAD: RX_DFA_UNIFORM_FOLDS '$stamp' is not a non-negative integer ($ax): $pat"; return ;; esac
    [ "$stamp" -le 6 ] || echo "BAD: RX_DFA_UNIFORM_FOLDS $stamp exceeds the documented 0..6 (two tables over at most three machines) ($ax): $pat"
    # THE BICONDITIONAL, against the emitted TEXT and never against the scan.
    [ "$stamp" -eq "$folded" ] || echo "BAD: stamps $stamp but carries $folded folded accessors ($ax): $pat"
    [ "$ghost" -eq 0 ] || echo "BAD: $ghost accessor/table pairs disagree — a folded accessor whose table is still named, or an unfolded one whose table is missing ($ax): $pat"
    [ "$stamp" -gt 0 ] && echo "FOLDING-$ax"
    return 0
}
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    one def
    one pf -fprefilter
done
WORKER

# `read_art`'s body is shared with the worker by TEXT rather than re-written,
# so the sweep and §1 cannot read an artifact two different ways.
#
# [CC-DIFF] STEP 1(b) FAMILY 4 FIX (2026-09-03): `declare -f read_art`
# formats the definition on (at least) FOUR lines, with the opening brace on
# its OWN line ("read_art () " then "{ " then the body then the closing
# "}") -- not the one-line "read_art() {" the old `sed '1d;$d'` assumed.
# Deleting only line 1 left line 2's bare "{ " in the reconstructed
# function, stacked under the manually-echoed "READ_ART() {" opener, with
# only ONE closing brace to match TWO opens. Every worker's w2.sh therefore
# failed to PARSE AT ALL ("syntax error: unexpected end of file from `{`
# command on line 1"), silently producing zero DFA-/BAD-/FOLDING- lines
# from EVERY shard -- which is why the corpus sweep's population read
# 0 of 0 (nothing to do with load, PROCS or the corpus path: reproduced
# standalone on an idle box, with PROCS unset and with PROCS=3 alike).
# Fixed by renaming the function IN PLACE (its own header line, whatever
# `declare -f` happens to format it as) instead of stripping and
# re-wrapping braces by line position.
{ declare -f read_art | sed '1s/^read_art (/READ_ART (/'; \
  cat "$WORKDIR/worker.sh"; } > "$WORKDIR/w2.sh"

for s in "$WORKDIR"/sh/p*; do
    ROOT_DIR="$ROOT_DIR" WORKDIR="$WORKDIR" PCREC="$PCREC" \
        bash "$WORKDIR/w2.sh" < "$s" > "$s.out" 2>&1 &
done
wait
cat "$WORKDIR"/sh/*.out > "$WORKDIR/all.out"

ndfa=$(grep -c '^DFA-' "$WORKDIR/all.out" || true)
nfold=$(grep -c '^FOLDING-' "$WORKDIR/all.out" || true)
nbad=$(grep -c '^BAD:' "$WORKDIR/all.out" || true)

echo "dfa-uniform-fold: sweep — $ndfa artifact/axis cells contain a DFA scan, $nfold of them fold at least one table, $nbad disagreements"

if [ "$nbad" -eq 0 ]; then
    ok "§3 the corpus sweep found no disagreement between RX_DFA_UNIFORM_FOLDS, the folded accessors and the tables actually present, on the default and -fprefilter axes"
else
    grep '^BAD:' "$WORKDIR/all.out" | head -20 >&2
    bad "§3 the corpus sweep found $nbad disagreements (first 20 above)"
fi

# THE POPULATION FLOOR (K35, and this file's own §1 negative control is not a
# substitute): a sweep in which NOTHING folds asserts nothing about the fold,
# and would go green if the fold were deleted from the emitter entirely. The
# floor is a fraction of the DFA-carrying population rather than a harvested
# count, so it survives corpus growth; [CC-DIFF] STEP 0 measured 22/90 (24 %)
# on the bench's own sets and the first run of this file measures the corpus's
# own number, recorded in docs/dev/lanes/ccdiff1_report.md.
if [ "$ndfa" -gt 0 ] && [ "$nfold" -gt $((ndfa / 50)) ] && [ "$nfold" -ge 20 ]; then
    ok "§3 the folding population is non-vacuous: $nfold of $ndfa DFA-carrying cells fold at least one table"
else
    bad "§3 the folding population is too small to assert anything ($nfold of $ndfa): a sweep in which nothing folds would be green with the fold deleted from the emitter"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
