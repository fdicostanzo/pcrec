#!/usr/bin/env bash
# tests/backrefs/run_dupnames_diff.sh — [M6.5.2] §8.3's RESOLUTION RULE, swept
# rather than sampled, and checked THREE ways.
#
# THE RULE IS A CHOICE AMONG CANDIDATES, which is why a sweep is owed here
# where a handful of cells would do elsewhere. `tests/backrefs/dupnames.rxt`
# carries the hand-picked cells that SEPARATE four readings — "first by
# number", "last set", "any one of them", "first NON-empty" — and each of them
# is caught by exactly one cell. What a hand-picked set cannot show is that no
# FIFTH rule fits, and that is this file's job.
#
# THE THREE WAYS, and the third is the one that makes this more than a
# regression test:
#
#   1. pcrec against libpcre2, over every generated cell.
#   2. AN INDEPENDENT MODEL of the rule — "walk the name's run in ASCENDING
#      GROUP NUMBER and take the FIRST entry that is SET" — implemented in
#      python from the RULE'S OWN TEXT, against libpcre2 over the same cells.
#      It shares no source with pcrec's emitted chain. If some cell in the
#      space disagrees with the model, the rule as written is wrong and this
#      says so BEFORE the compiler is blamed.
#   3. The two populations are asserted EXACT, because a sweep that generated
#      no run of size >= 2 would be a sweep of the ordinary numeric path
#      wearing a dupnames pattern's clothes.
#
# THE SPACE. For a run of size k, `(?J)^(?:(?<a>L1)|-)...(?:(?<a>Lk)|-)\k<a>$`
# lets a SUBJECT choose which members participate: each slot is either its own
# letter or a `-`. Sweeping every subject over the alphabet {L1..Lk, -} for
# the k slots therefore reaches EVERY SUBSET of participation, including the
# empty one (§3.3's unset rule, which has no special case for names), and the
# trailing reference text picks which member the answer has to agree with.
#
# Usage: bash tests/backrefs/run_dupnames_diff.sh
# Env: PCREC, CC, KEEP=1.  SKIPS LOUDLY when libpcre2 is absent.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
export ROOT_DIR
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
# See run_backref_diff.sh's own note: the generated-code axis is
# instrumentable, so `make ubsan` / `make asan` reach the emitted matchers this
# script compiles and runs.
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11}"
FEATS="backrefs,named-groups,modifiers"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "dupnames-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

if ! python3 -c "
import os,sys
sys.path.insert(0, os.path.join('$ROOT_DIR','docs','design','eng_brep_measurements','probes'))
import pcre2_ctypes" 2>/dev/null; then
    echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
    echo "checks passed: 0"; echo "checks failed: 0"; exit 0
fi

# ---- the space, and the INDEPENDENT MODEL of the rule ---------------------
python3 - "$WORKDIR" <<'PY'
import itertools, os, sys
sys.path.insert(0, os.path.join(os.environ["ROOT_DIR"], "docs", "design",
                                "eng_brep_measurements", "probes"))
import pcre2_ctypes as P

work = sys.argv[1]
subj_root = os.path.join(work, "subjects")
LET = "pqrs"

pats, cells, model_bad, model_cells, nmatch = [], [], 0, 0, 0
for k in range(1, 5):
    letters = LET[:k]
    slots = "".join("(?:(?<a>%s)|-)" % c for c in letters)
    pat = "(?J)^%s\\k<a>$" % slots
    d = os.path.join(subj_root, "k%d" % k)
    os.makedirs(d, exist_ok=True)
    subs = []
    for choice in itertools.product(*[(c, "-") for c in letters]):
        prefix = "".join(choice)
        for ref in list(letters) + ["-", ""]:
            subs.append(prefix + ref)
    subs = sorted(set(subs))
    for i, s in enumerate(subs):
        with open(os.path.join(d, "s%04d" % i), "wb") as f:
            f.write(s.encode("latin-1"))
    pats.append((k, pat, k, len(subs)))

    # THE MODEL, written from §8.3's own sentence and from nothing else:
    # every member of the run in ASCENDING NUMBER, take the FIRST that is SET
    # (set-to-empty included), compare its TEXT at the cursor.
    rx = P.Compiled(pat)
    for s in subs:
        # Which members participate is decided by the prefix; slot i is set
        # iff the i'th character is its own letter.
        prefix, ref = s[:k], s[k:]
        spans = []
        for i, c in enumerate(letters):
            spans.append((i, i + 1) if i < len(prefix) and prefix[i] == c
                         else None)
        first_set = next((sp for sp in spans if sp is not None), None)
        if first_set is None:
            predicted = None            # §3.3: an unset reference FAILS
        else:
            want_text = prefix[first_set[0]:first_set[1]]
            predicted = (0, len(s)) if ref == want_text else None
        got = rx.search(s, 0)
        got = None if got is None else got[0]
        model_cells += 1
        if got is not None:
            nmatch += 1
        if predicted != got:
            model_bad += 1
            if model_bad <= 5:
                sys.stderr.write(
                    "MODEL-DISAGREES\t%s\t%r\tmodel=%r\tlibpcre2=%r\n"
                    % (pat, s, predicted, got))

with open(os.path.join(work, "patterns.tsv"), "w") as f:
    for k, pat, ng, n in pats:
        f.write("k%d\t%d\t%s\n" % (k, ng, pat))
with open(os.path.join(work, "census"), "w") as f:
    f.write("%d %d %d\n" % (model_cells, model_bad, nmatch))
PY
read -r MODEL_CELLS MODEL_BAD MODEL_MATCH < "$WORKDIR/census"

# CHECK 2: the rule as WRITTEN reproduces libpcre2 over the whole space.
if [ "$MODEL_BAD" -ne 0 ]; then
    bad "§8.3 THE RULE ITSELF: an independent model of \"first of the name-run, by ascending number, that is SET\" disagrees with libpcre2 on $MODEL_BAD of $MODEL_CELLS cells — the rule as written is wrong, and no compiler change can fix that"
elif [ "$MODEL_CELLS" -ne 158 ]; then
    bad "§8.3 POPULATION: the model swept $MODEL_CELLS cells, expected EXACTLY 158 (runs of size 1..4, every subset of participation, every reference text). A shrinking space is how this file passes while measuring nothing"
elif [ "$MODEL_MATCH" -ne 26 ]; then
    bad "§8.3 NON-VACUITY: $MODEL_MATCH of $MODEL_CELLS model cells MATCH, expected EXACTLY 26 — a space in which nothing matches agrees with any rule, and one whose matching population MOVED is a space that stopped asking the same question"
else
    ok "§8.3 THE RULE: an INDEPENDENTLY WRITTEN model of the resolution rule reproduces libpcre2 on all $MODEL_CELLS cells ($MODEL_MATCH of them a match) over name-runs of size 1..4 with every subset participating — which is what a hand-picked cell set cannot show"
fi

# ---- CHECK 1: pcrec against libpcre2 over the same space -----------------
cmp_n=0; cmp_bad=0; run_ge2=0
while IFS=$'\t' read -r key ng pat; do
    [ -n "$key" ] || continue
    k="${key#k}"
    [ "$k" -ge 2 ] && run_ge2=$((run_ge2 + 1))
    d="$WORKDIR/$key"; mkdir -p "$d"
    if ! pcrec_run "$PCREC" -p rx --features "$FEATS" -o "$d/gen.c" -- "$pat" \
            >/dev/null 2>"$d/pc.log"; then
        bad "pcrec refused '$pat': $(head -1 "$d/pc.log")"; continue
    fi
    if ! $CC $GENCFLAGS -I"$d" -o "$d/drv" "$SCRIPT_DIR/bref_batch.c" \
            "$d/gen.c" 2>"$d/cc.log"; then
        bad "'$pat': the matcher did not compile: $(head -3 "$d/cc.log" | tr '\n' ' ')"
        continue
    fi
    printf '%s\t%s\t%s\n' "$key" "$ng" "$pat" > "$d/one.tsv"
    python3 "$SCRIPT_DIR/bref_oracle.py" "$d/one.tsv" \
        "$WORKDIR/subjects/$key" "$d/oracle.tsv" 2>/dev/null || {
        bad "'$pat': the oracle refused to run"; continue; }
    : > "$d/cells.txt"
    awk -F'\t' -v r="$WORKDIR/subjects/$key" '{ print r "/" $2 "\t" $3 }' \
        "$d/oracle.tsv" > "$d/cells.txt"
    awk -F'\t' '{ print $4 }' "$d/oracle.tsv" > "$d/want"
    "$d/drv" < "$d/cells.txt" > "$d/got" 2>/dev/null
    if [ "$(wc -l < "$d/got")" -ne "$(wc -l < "$d/want")" ]; then
        bad "'$pat': the batch driver produced $(wc -l < "$d/got") lines for $(wc -l < "$d/want") cells — the protocol shifted, and this file compares POSITIONALLY"
        continue
    fi
    n=0
    while IFS= read -r want && IFS= read -r got <&3; do
        n=$((n + 1)); cmp_n=$((cmp_n + 1))
        if [ "$want" != "$got" ]; then
            cmp_bad=$((cmp_bad + 1))
            [ "$cmp_bad" -le 5 ] && bad "'$pat' cell $n: libpcre2 '$want', pcrec '$got'"
        fi
    done < "$d/want" 3< "$d/got"
done < "$WORKDIR/patterns.tsv"

# CHECK 3: the populations, EXACT. A run of size 1 is the ordinary numeric
# path wearing a dupnames pattern's clothes, so "at least one run" is not the
# thing to assert.
if [ "$run_ge2" -ne 3 ]; then
    bad "POPULATION: $run_ge2 name-runs of size >= 2, expected EXACTLY 3 (sizes 2, 3 and 4). Size 1 exercises no resolution at all"
elif [ "$cmp_n" -eq 0 ]; then
    bad "POPULATION: pcrec was compared on 0 cells"
elif [ "$cmp_bad" -eq 0 ]; then
    ok "pcrec agrees with libpcre2 on all $cmp_n cells (match span AND every group span) across 4 name-runs, 3 of them of size >= 2"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
