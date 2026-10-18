#!/bin/bash
# docs/dev/lanes/b3b/derive_rows.sh -- writes mech_rows.txt beside it: R17-b' B3b's heavy-chain mech rows,
# DERIVED, so the list is reproducible (b3brev finding 1: the first list carried a bare `S` its hand union
# picked up). Run from the worktree at the tip the chain will pin:
#
#     bash docs/dev/lanes/b3b/derive_rows.sh SCRATCH_DIR
#
# SCRATCH_DIR receives the base's archive (ref/) and its call graph; nothing else is written outside this
# directory. The union of four parts, each a set of ids that must match ^S[0-9]+$ (the run fails otherwise):
#  (a) docs/design/start_table/sabotage_anchors.py --step b3b=BASE..HEAD over the base's archive: every row
#      the step's actual diff re-runs (hunk + reach), its last column;
#  (b) every row anchored (SAB_FILE/SAB_FILE2) in a memfn/ or tests/ file the branch edits, or detected by a
#      suite whose checks it changed (SAB_SUITES naming memfnfinder, candoracle, memfndeleg, memfnrows or
#      axesmemfn);
#  (c) mech_rows_judged.txt: the rows the lane added by judgment beside (b)'s rule (the first list's
#      suite-detected rows the rule does not reach), each one an id;
#  (d) the rows the branch adds or re-aims: every tests/mech/sabotages/ file it touches.
set -eu
BASE=c88537116
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(git -C "$HERE" rev-parse --show-toplevel)"
SCR="${1:?usage: derive_rows.sh SCRATCH_DIR}"
mkdir -p "$SCR"
cd "$TREE"
if [ ! -f "$SCR/ref/Makefile" ]; then
    mkdir -p "$SCR/ref"
    git archive "$BASE" | tar -x -C "$SCR/ref"
fi
[ -s "$SCR/cg_ref.tsv" ] || python3 -I docs/design/start_table/call_graph.py "$SCR/ref" > "$SCR/cg_ref.tsv" 2> "$SCR/cg_ref.err"
# rc 2 is the tool's UNRESOLVED-src report (8 rows on the base's archive, pre-existing: S571 S640
# S897 S906 S995 ...); the step's rows are still written. Any other failure stops here.
rc=0
python3 -I docs/design/start_table/sabotage_anchors.py "$SCR/ref" "$SCR/cg_ref.tsv" \
    docs/design/start_table/refactor_edit_set.tsv --repo "$TREE" --step "b3b=$BASE..HEAD" \
    > "$SCR/sa_step.tsv" 2> "$SCR/sa_step.err" || rc=$?
if [ "$rc" -ne 0 ] && { [ "$rc" -ne 2 ] || [ ! -s "$SCR/sa_step.tsv" ]; }; then
    echo "derive_rows.sh: sabotage_anchors.py failed (rc $rc), see $SCR/sa_step.err" >&2; exit 1
fi
grep -c '^UNRESOLVED' "$SCR/sa_step.err" | sed 's/^/derive_rows.sh: UNRESOLVED src anchors (listed, not derived): /' >&2
awk -F'\t' '$NF ~ /b3b:/{print $2}' "$SCR/sa_step.tsv" | sort -u > "$SCR/rows_a.txt"
git diff --name-only "$BASE" HEAD | grep -E '^(memfn|tests)/' > "$SCR/edited.txt" || true
python3 -I - "$SCR/edited.txt" > "$SCR/rows_b.txt" <<'PY'
import glob, os, re, sys
edited = set(open(sys.argv[1]).read().split())
want = {"memfnfinder", "candoracle", "memfndeleg", "memfnrows", "axesmemfn"}
out = set()
for f in glob.glob("tests/mech/sabotages/*.sh"):
    t = open(f, errors="replace").read()
    def g(k):
        m = re.search(r"^" + k + r"=([\"']?)(.*?)\1\s*$", t, re.M)
        return m.group(2) if m else ""
    files = {g("SAB_FILE"), g("SAB_FILE2")} - {""}
    if files & edited or set(g("SAB_SUITES").split()) & want:
        out.add(os.path.basename(f).split("_")[0])
print("\n".join(sorted(out)))
PY
grep -vE '^(#|$)' "$HERE/mech_rows_judged.txt" | sort -u > "$SCR/rows_c.txt"
git diff --name-only "$BASE" HEAD -- tests/mech/sabotages/ | sed 's#.*/##; s#_.*##' | sort -u > "$SCR/rows_d.txt"
sort -u "$SCR/rows_a.txt" "$SCR/rows_b.txt" "$SCR/rows_c.txt" "$SCR/rows_d.txt" > "$SCR/rows_all.txt"
bad=$(grep -vcE '^S[0-9]+$' "$SCR/rows_all.txt" || true)
if [ "$bad" -ne 0 ]; then
    echo "derive_rows.sh: $bad id(s) not ^S[0-9]+\$:" >&2; grep -vE '^S[0-9]+$' "$SCR/rows_all.txt" >&2; exit 1
fi
{
    echo "# R17-b' B3b's heavy-chain mech rows, each run SOLO by chain.sh and scored by its declared SAB_EXPECT."
    echo "# DERIVED by docs/dev/lanes/b3b/derive_rows.sh at $(git rev-parse --short=9 HEAD) (base $BASE): the union of"
    echo "# (a) sabotage_anchors.py --step b3b=$BASE..HEAD, $(wc -l < "$SCR/rows_a.txt") rows; (b) rows anchored in an"
    echo "# edited memfn/ or tests/ file or detected by a changed suite, $(wc -l < "$SCR/rows_b.txt"); (c) the judged"
    echo "# rows, mech_rows_judged.txt, $(wc -l < "$SCR/rows_c.txt"); (d) the rows the branch adds or re-aims,"
    echo "# $(wc -l < "$SCR/rows_d.txt"). $(wc -l < "$SCR/rows_all.txt") distinct ids. One id per line (no suffix)."
    sort -V "$SCR/rows_all.txt"
} > "$HERE/mech_rows.txt"
echo "mech_rows.txt: $(wc -l < "$SCR/rows_all.txt") ids (a $(wc -l < "$SCR/rows_a.txt"), b $(wc -l < "$SCR/rows_b.txt"), c $(wc -l < "$SCR/rows_c.txt"), d $(wc -l < "$SCR/rows_d.txt"))"
