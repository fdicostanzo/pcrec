#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (R-39, lane r39).
#
# memfn/tests/g2_parts_selftest.sh -- the plants for g2_parts.py: can its two judgements fail?
#
#   memfn/tests/g2_parts_selftest.sh [FLOORS_TSV]      (default tests/memfn/row_floors.tsv)
#
# Builds N part logs the way run_g2.sh --part K/N prints them (no kit, no compiler: the lines g2_parts.py
# reads are G2UNIT, G2PART and the `checks` trailer), one per part of the REAL unit table, with row
# counts a few over the REAL row floors. Then:
#   control   the clean logs must gather GREEN (rc 0), for N = 1, 2, 3 and 4 (N = 1: the unsplit shape);
#   plants    each must gather RED (rc 1) and name its cause:
#     missing   one G2UNIT line deleted from a part            -> "run by no part"
#     duplicate one part's unit also listed by another part    -> "more than one part"
#     extra     a unit the table does not list                 -> "does not list"
#     misdealt  two parts swap a unit                          -> "the rule deals it"
#     floor     one row's count one under its g2_floor         -> "(e)"
#     absent    one floored row never chosen in any part       -> "(e)" and "(b)"
#     zero      one row chosen 0 times                         -> "(b)"
#     dropped   one part's REACH_DROPPED nonzero               -> "(a)"
#     noreach   one process printed no REACH line              -> "(d)"
#     partfail  one part's own `checks failed` nonzero         -> "reports checks failed"
#     prelude   the prelude's rows differ between parts        -> "prelude generator"
# Prints PASS/FAIL per case and `checks failed: N`; exit 0 only when every case behaved.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
floors=${1:-$root/tests/memfn/row_floors.tsv}
: "${TMPDIR:?g2_parts_selftest.sh: set TMPDIR to a scratch directory}"
d=$(mktemp -d "$TMPDIR/g2parts.XXXXXX") || exit 2
trap 'rm -rf "$d"' EXIT
gp="python3 -I $here/g2_parts.py"
table=$here/g2_units.tsv
failed=0
ok()  { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; failed=$((failed + 1)); }

# mkparts N DIR: part logs 1..N
mkparts() {
    python3 -I - "$1" "$2" "$table" "$floors" "$here/g2_parts.py" <<'EOF'
import importlib.util, os, re, sys
n, out, table, floors, gp = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
spec = importlib.util.spec_from_file_location("g2_parts", gp)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
units = m.read_table(table)
deal = m.deal(units, n)
rows = []                               # (table, row, g2_floor)
for ln in open(floors):
    c = ln.rstrip("\n").split("\t")
    if ln.startswith("#") or len(c) < 4 or not re.fullmatch(r"[0-9]+", c[3]):
        continue
    rows.append((c[0], c[1], int(c[3])))
os.makedirs(out, exist_ok=True)
for k in range(1, n + 1):
    with open("%s/part%d.log" % (out, k), "w") as f:
        for u in deal[k - 1]:
            print("G2UNIT %s 7" % u, file=f)
        print("G2PART reach_procs 3", file=f)
        print("G2PART floor_rows 20", file=f)
        for t, r, fl in rows:               # the prelude: the same in every part
            print("G2PART rowchosen-prelude %s %s %d" % (t, r, 5), file=f)
        for t, r, fl in rows:               # the rest: floor + 5 over the parts, all in part 1's share + the rest
            share = (fl + 5) // n + (1 if k == 1 else 0) * ((fl + 5) % n)
            print("G2PART rowchosen-other %s %s %d" % (t, r, share), file=f)
        # n parts each count the prelude's 5; the sum is floor + 5 + 5 >= floor
        print("G2PART reach_dropped 0 3", file=f)
        print("G2PART part %d/%d units %s" % (k, n, " ".join(deal[k - 1])), file=f)
        print("G2PART prelude_passed 100", file=f)
        print("G2PART replicated_failed 0", file=f)
        print("G2PART wall %d" % (60 + k), file=f)
        print("checks passed: %d" % (100 + 10 * len(deal[k - 1])), file=f)
        print("checks failed: 0", file=f)
EOF
}
gather() { $gp gather --table "$table" --row-floors "$floors" "$@"; }
# expect NAME WANT_RC WANT_TEXT LOGS...
expect() {
    local name=$1 rc=$2 txt=$3; shift 3
    local o; o=$(gather "$@" 2>&1); local got=$?
    if [ "$got" != "$rc" ]; then bad "$name: rc $got, wanted $rc"; echo "$o" | sed 's/^/    /'
    elif [ -n "$txt" ] && ! echo "$o" | grep -q -- "$txt"; then bad "$name: rc $got but no \"$txt\" in the output"; echo "$o" | sed 's/^/    /'
    else ok "$name (rc $got${txt:+, \"$txt\"})"; fi
}

for n in 1 2 3 4; do
    mkparts "$n" "$d/n$n" || { bad "fixture N=$n"; continue; }
    expect "control: the clean $n part(s) gather green" 0 "ran all" "$d"/n$n/part*.log
done

n=3
fresh() { rm -rf "$d/p"; cp -r "$d/n$n" "$d/p"; }
fresh; sed -i '0,/^G2UNIT /{//d}' "$d/p/part2.log"
expect "plant missing: a unit's manifest line deleted" 1 "run by no part" "$d"/p/part*.log
fresh; grep -m1 '^G2UNIT ' "$d/p/part1.log" >> "$d/p/part2.log"
expect "plant duplicate: a unit listed by two parts" 1 "more than one part" "$d"/p/part*.log
fresh; echo "G2UNIT w2-99 3" >> "$d/p/part2.log"
expect "plant extra: a unit the table does not list" 1 "does not list" "$d"/p/part*.log
fresh
u1=$(grep -m1 '^G2UNIT ' "$d/p/part1.log"); u2=$(grep -m1 '^G2UNIT ' "$d/p/part2.log")
sed -i "0,/^G2UNIT /{//d}" "$d/p/part1.log"; sed -i "0,/^G2UNIT /{//d}" "$d/p/part2.log"
echo "$u2" >> "$d/p/part1.log"; echo "$u1" >> "$d/p/part2.log"
expect "plant misdealt: two parts swap a unit" 1 "the rule deals it" "$d"/p/part*.log

# a floored row: the first row of the floors file with a numeric g2_floor
read -r ft fr ff <<< "$(awk -F'\t' '!/^#/ && NF >= 4 && $4 ~ /^[0-9]+$/ && $4 > 12 {print $1, $2, $4; exit}' "$floors")"
# the row's total is 5 (prelude) + floor + 5 (other); take 11 off part 1's share to land one under the floor
fresh
sed -i "s/^G2PART rowchosen-other $ft $fr .*/G2PART rowchosen-other $ft $fr $((ff - 5 - 1))/" "$d/p/part1.log"
for k in 2 3; do sed -i "s/^G2PART rowchosen-other $ft $fr .*/G2PART rowchosen-other $ft $fr 0/" "$d/p/part$k.log"; done
expect "plant floor: row $ft/$fr one under its g2_floor $ff, summed over the parts" 1 "(e).*$ft/$fr" "$d"/p/part*.log
fresh
for k in 1 2 3; do sed -i "/^G2PART rowchosen-\(prelude\|other\) $ft $fr /d" "$d/p/part$k.log"; done
expect "plant absent: row $ft/$fr chosen by no part" 1 "(e)" "$d"/p/part*.log
fresh
for k in 1 2 3; do sed -i "s/^G2PART rowchosen-\(prelude\|other\) $ft $fr .*/G2PART rowchosen-\1 $ft $fr 0/" "$d/p/part$k.log"; done
expect "plant zero: row $ft/$fr chosen 0 times" 1 "(b) rows never chosen" "$d"/p/part*.log
fresh; sed -i 's/^G2PART reach_dropped .*/G2PART reach_dropped 4 3/' "$d/p/part2.log"
expect "plant dropped: REACH_DROPPED nonzero in a part" 1 "(a)" "$d"/p/part*.log
fresh; echo "G2PART reach_noreach gen-x.err" >> "$d/p/part3.log"
expect "plant noreach: a process printed no REACH line" 1 "(d)" "$d"/p/part*.log
fresh; sed -i 's/^checks failed: 0/checks failed: 2/' "$d/p/part1.log"
expect "plant partfail: a part's own verdict red" 1 "reports checks failed" "$d"/p/part*.log
fresh; sed -i "s/^G2PART rowchosen-prelude $ft $fr .*/G2PART rowchosen-prelude $ft $fr 6/" "$d/p/part2.log"
expect "plant prelude: the prelude's rows differ between parts" 1 "prelude generator" "$d"/p/part*.log

echo "checks failed: $failed"
[ "$failed" = 0 ]
