#!/usr/bin/env bash
# span_cards/slot/sabotage.sh — the SLOT-LOCAL sabotage rows of unit S2c (span_cards.md §9 S2c, rev 1.2
# READY-5): their detectors run only in the slot harness's `--dry-run`, which no make suite runs, so this
# runner plants each in a SCRATCH COPY of slot/, runs the named job's dry run there under run id s2c-dry, and
# expects the named refusal (precedent: docs/design/r17b_prime/b3a/sabotage/run_skb3a.sh). A control run of
# the unplanted copy must be green first. Each row scores DETECTED (the dry run refused with the expected
# text) or MISSED; exit 0 iff the control is green and every row is DETECTED.
#   slot/sabotage.sh SCRATCH [ROW..]      rows: j j2 k l1 l2 (default all)
#   (j)  the placement draw ignores the launch (and so its re-draw index): every launch links the same pads;
#        the cross-launch constraint on `nm` of the seven executables refuses after the bounded re-draw
#   (j2) a twin linked at its arm's phase (its pad sized to land it there): the per-launch constraint
#        refuses, after the bounded re-draw
#   (k)  the walk's arm rendered from another entry row (libc's): its site-text hash differs from
#        mf_form_hash(walk): the cell-text check refuses
#   (l1) the generator plants libc's hits as another byte: the count gate (count 0 vs E)
#   (l2) the find wrapper returns each hit one byte late (count kept): the POSITION sum and FNV-1a-64 gate
set -u
export LC_ALL=C
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../../.." && pwd)
SCR=${1:?usage: sabotage.sh SCRATCH [ROW..]}
shift
ROWS=${*:-j j2 k l1 l2}
TO=$(command -v gnutimeout || command -v timeout)
mkdir -p "$SCR"

copy() {   # a fresh copy of slot/ in $SCR/$1
    rm -rf "$SCR/$1"
    cp -r "$here" "$SCR/$1/"
}

patch() {  # FILE OLD NEW: exactly one occurrence, else the plant itself fails (loud)
    python3 -I - "$1" "$2" "$3" <<'PY'
import sys
p, a, b = sys.argv[1:4]
t = open(p).read()
if t.count(a) != 1:
    sys.exit("sabotage: plant anchor not found exactly once in %s: %r" % (p, a))
open(p, "w").write(t.replace(a, b))
PY
}

dry() {    # NAME JOB: the job's dry run in the copy, its rc and output
    SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/run.py" dry "$2" "$SCR/run.$1" s2c-dry > "$SCR/$1.out" 2>&1
}

pass=0 fail=0
copy control
dry control J2
if [ $? -ne 0 ]; then
    echo "sabotage: CONTROL red (the unplanted copy's J2 dry run):"; tail -5 "$SCR/control.out"; exit 2
fi
echo "control   J2 dry run green"

for row in $ROWS; do
    copy "$row"
    case $row in
    j)  job=J2 want="the cross-launch constraint"
        patch "$SCR/$row/link.py" '("%s|%s|%d|%s|%d" % (run_id, job, l, arm, d))' '("%s|%s|%s" % (run_id, job, arm))' ;;
    j2) job=J2 want="the per-launch constraint"
        patch "$SCR/$row/link.py" '        cmd += [pad_obj(ld, seed_pad(run_id, job, l, a.name, d.get(a.name, 0)), k), o]' \
'        P = seed_pad(run_id, job, l, a.name, d.get(a.name, 0))
        if a.name.endswith("#b"):
            P = 64 + (-int(sh(["size", "-A", objs[k - 1][2]]).split(".text")[1].split()[0])) % 64
        cmd += [pad_obj(ld, P, k), o]' ;;
    k)  job=J2 want="CELL-TEXT MISMATCH"
        patch "$SCR/$row/link.py" '    fi, bo = parts(fx, form, cls)' '    fi, bo = parts(fx, {"walk": "libc"}.get(form, form), cls)' ;;
    l1) job=J3 want="GATE MISS kit.find_hit.libc"
        patch "$SCR/$row/gen.c" '            buf[p] = a->hit[a->split ? (k & 1) : 0];' \
'            buf[p] = (unsigned char)(a->hit[a->split ? (k & 1) : 0] + (a->hit[0] == 120));' ;;
    l2) job=J3 want="GATE MISS kit.find_hit.walk"
        patch "$SCR/$row/link.py" '    *io = pos;
    return pos < n;' '    *io = pos < n ? pos + 1 : pos;
    return pos < n;' ;;
    *)  echo "sabotage: unknown row $row"; exit 2 ;;
    esac
    [ $? -eq 0 ] || { echo "$row  PLANT FAILED"; fail=$((fail + 1)); continue; }
    dry "$row" "$job"
    rc=$?
    if [ $rc -ne 0 ] && grep -q -- "$want" "$SCR/$row.out"; then
        echo "$row  DETECTED ($job dry run rc $rc: $(grep -m1 -- "$want" "$SCR/$row.out" | cut -c1-140))"
        pass=$((pass + 1))
    else
        echo "$row  MISSED ($job dry run rc $rc; wanted '$want'):"; tail -3 "$SCR/$row.out"
        fail=$((fail + 1))
    fi
done
echo "== slot sabotage: $pass DETECTED, $fail MISSED of $(echo $ROWS | wc -w) rows"
[ $fail -eq 0 ]
