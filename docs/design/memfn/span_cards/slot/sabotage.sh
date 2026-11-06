#!/usr/bin/env bash
# span_cards/slot/sabotage.sh — the SLOT-LOCAL sabotage rows of unit S2c (span_cards.md §9 S2c, rev 1.2
# READY-5): their detectors run only in the slot harness's `--dry-run`, which no make suite runs, so this
# runner plants each in a SCRATCH COPY of slot/, runs the named job's dry run there under run id s2c-dry, and
# expects the named refusal (precedent: docs/design/r17b_prime/b3a/sabotage/run_skb3a.sh). A control run of
# the unplanted copy must be green first. Each row scores DETECTED (the dry run refused with the expected
# text) or MISSED; exit 0 iff the control is green and every row is DETECTED.
#   slot/sabotage.sh SCRATCH [ROW..]      rows: j j2 k l1 l2 l3 g2 g3 (default all)
#   (j)  the placement draw ignores the launch (and so its re-draw index): every launch links the same pads;
#        the cross-launch constraint on `nm` of the seven executables refuses after the bounded re-draw
#   (j2) a twin linked at its arm's phase (its pad sized to land it there): the per-launch constraint
#        refuses, after the bounded re-draw
#   (k)  the walk's arm rendered from another entry row (libc's): its site-text hash differs from
#        mf_form_hash(walk): the cell-text check refuses
#   (l1) the generator plants libc's hits as another byte: the count gate (count 0 vs E; the libc base's
#        sentinel subject misses first since r9)
#   (l2) the find wrapper returns each hit one byte late (count kept): the POSITION sum and FNV-1a-64 gate
#        (the wrapper is every find arm's and the control's, so the miss is matched by its shape: found =
#        timed = planted, sum differs; the control's sentinel misses first since r9)
#   (l3) S2934 [r9 G1] the TIMED loop alone scans half the subject (the gate loop untouched): the answer gate
#        runs `_time` over every subject and its sentinel (a hit at the last byte), so even the miss-only
#        find_byte arms miss
#   (g2) S2935 [r9 G2] plan.py builds the libc row's Arm with walk's form: the KEY names libc, the render
#        refuses KEY-ARM MISMATCH (before r9 the cell-text check compared the Arm's form and stayed green)
#   (g3) S2936 [r9 G3] est.py's never-ran cross-check removed: est.py's self-test (a leftover cells file of a
#        job the record says never ran) goes red; this row runs the self-test, not a dry run
# `want` is an extended regex (grep -E). Ids S2934-S2936 are the kit's (span_cards §R1.3 r9 rows); they are
# slot-local rows, not tests/mech rows (no make suite runs their detectors).
set -u
export LC_ALL=C
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../../.." && pwd)
SCR=${1:?usage: sabotage.sh SCRATCH [ROW..]}
shift
ROWS=${*:-j j2 k l1 l2 l3 g2 g3}
. "$TREE/tests/lib/timeout_bin.sh"
TO=$TIMEOUT_BIN
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

dry() {    # NAME JOB: the job's dry run in the copy (a fresh RUNDIR), its rc and output; JOB `est` runs est.py's
           # self-test instead
    rm -rf "$SCR/run.$1"
    if [ "$2" = est ]; then
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/est.py" selftest "$SCR/run.$1" > "$SCR/$1.out" 2>&1
    else
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/run.py" dry "$2" "$SCR/run.$1" s2c-dry > "$SCR/$1.out" 2>&1
    fi
}

pass=0 fail=0
copy control
dry control J2
if [ $? -ne 0 ]; then
    echo "sabotage: CONTROL red (the unplanted copy's J2 dry run):"; tail -5 "$SCR/control.out"; exit 2
fi
echo "control   J2 dry run green"
dry control est
if [ $? -ne 0 ]; then
    echo "sabotage: CONTROL red (the unplanted copy's est.py self-test):"; tail -5 "$SCR/control.out"; exit 2
fi
echo "control   est.py self-test green"

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
    l1) job=J3 want='GATE MISS (base|kit\.find_hit)\.libc'
        patch "$SCR/$row/gen.c" '            buf[p] = a->hit[a->split ? (k & 1) : 0];' \
'            buf[p] = (unsigned char)(a->hit[a->split ? (k & 1) : 0] + (a->hit[0] == 120));' ;;
    l2) job=J3 want='GATE MISS [^ ]+ len [0-9]+ subject [0-9]+( SENTINEL)?: found ([0-9]+) sum [0-9]+ fnv [0-9a-f]+ timed \2, planted \2 '
        # the count is KEPT (found = planted) and the miss is the position sum / FNV (the find wrapper is
        # shared, so every find arm misses, libc's first)
        patch "$SCR/$row/link.py" '    *io = pos;
    return pos < n;' '    *io = pos < n ? pos + 1 : pos;
    return pos < n;' ;;
    l3) job=J2 want='GATE MISS (ctl|kit\.find_byte\.walk) len [0-9]+ subject [0-9]+ SENTINEL: found 1 sum [0-9]+ fnv [0-9a-f]+ timed 0, planted 1 '
        patch "$SCR/$row/link.py" '    for (size_t p = 0; p < n && step(s, n, &p); p++) k++;' \
'    for (size_t p = 0; p < n / 2 && step(s, n / 2, &p); p++) k++;   /* SABOTAGE S2934 */' ;;
    g2) job=J2 want='KEY-ARM MISMATCH kit\.find_byte\.libc'
        patch "$SCR/$row/plan.py" 'row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "libc", lengths=LENGTHS))' \
'row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "walk", lengths=LENGTHS))   # SABOTAGE S2935' ;;
    g3) job=est want='selftest	leftover cells of a never-ran job	WRONG'
        patch "$SCR/$row/est.py" '        if j not in ran:
            raise InputError("%s holds cells of job %s' '        if False:   # SABOTAGE S2936
            raise InputError("%s holds cells of job %s' ;;
    *)  echo "sabotage: unknown row $row"; exit 2 ;;
    esac
    [ $? -eq 0 ] || { echo "$row  PLANT FAILED"; fail=$((fail + 1)); continue; }
    dry "$row" "$job"
    rc=$?
    if [ $rc -ne 0 ] && grep -Eq -- "$want" "$SCR/$row.out"; then
        echo "$row  DETECTED ($job dry run rc $rc: $(grep -E -m1 -- "$want" "$SCR/$row.out" | cut -c1-140))"
        pass=$((pass + 1))
    else
        echo "$row  MISSED ($job dry run rc $rc; wanted '$want'):"; tail -3 "$SCR/$row.out"
        fail=$((fail + 1))
    fi
done
echo "== slot sabotage: $pass DETECTED, $fail MISSED of $(echo $ROWS | wc -w) rows"
[ $fail -eq 0 ]
