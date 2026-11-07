#!/usr/bin/env bash
# span_cards/slot/sabotage.sh — the SLOT-LOCAL sabotage rows of unit S2c (span_cards.md §9 S2c, rev 1.2
# READY-5): their detectors run only in the slot harness's dry run (`run.py dry`), which no make suite runs, so this
# runner plants each in a SCRATCH COPY of slot/, runs the named job's dry run there under run id s2c-dry, and
# expects the named refusal (precedent: docs/design/r17b_prime/b3a/sabotage/run_skb3a.sh). A control run of
# the unplanted copy must be green first. Each row scores DETECTED (the dry run refused with the expected
# text) or MISSED; exit 0 iff the control is green and every row is DETECTED.
#   slot/sabotage.sh SCRATCH [ROW..]      rows: j j2 k l1 l2 l3 g2 g3 f1 f2 f6 n1 n2 s1 s2 q1 b1 (default all)
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
#   (l3) S2934 [r9 G1] the TIMED loop alone scans half the subject (the gate loop untouched), in the ARMS' TUs
#        only ([rev1.3 r9fc-FIX-4]: the control is built from the unplanted text and gates green, so the refusal
#        is a LAUNCH gate's): the answer gate runs `_time` over every subject and its sentinel (a hit at the last
#        byte), so even the miss-only find_byte arms miss
#   (g2) S2935 [r9 G2] plan.py builds the libc row's Arm with walk's form: the KEY names libc, the render
#        refuses KEY-ARM MISMATCH (before r9 the cell-text check compared the Arm's form and stayed green)
#   (g3) S2936 [r9 G3] est.py's never-ran cross-check removed: est.py's self-test (a leftover cells file of a
#        job the record says never ran) goes red; this row runs the self-test, not a dry run
#   (f1) S2937 [r9fc FIX-1] est.py takes a cost row's gate from the LIVE cards (plan.CARD) instead of the run
#        record's pinned rows: est.py's self-test case "live card/policy edit after the run" (equal record and
#        cells, the live gate moved) moves the outcome; the self-test, not a dry run
#   (f2) S2938 [r9fc FIX-2] plan.py builds J3's periodic find_hit Arms with landing `random` (form and class
#        kept, so r9 G2's check alone stays green): the render's per-dim check refuses KEY-ARM MISMATCH on dim
#        landing
#   (f6) S2939 [r9fc FIX-6] the driver's call loop runs half its calls for a compare arm (the gate untouched):
#        the dry run's ROUND CHECK (`drv check`) refuses ROUND MISS on a p50 verify arm (its subjects' planted
#        counts differ, so ACC is short; a p0 arm plants 0 and cannot see it)
#   (n1) S2940 [rev1.4 R14-1] the null base rendered with ANOTHER LOOP (an indexed candidate loop where its class
#        arm bumps a pointer): link.py's null-base check refuses NULL-BASE MISMATCH (its text differs outside the
#        compare)
#   (n2) S2941 [rev1.4 R14-1] the null base keeps a BYTE load whatever its arm loads: the check refuses on the
#        word classes (l1's memcmp, w1-w3's words): the kept load is none its class arm's body makes
#   (s1) S2942 [rev1.4 R14-2] est.py's sub-resolution value not clamped: the self-test case "consistently
#        negative within r" (value must be 0) goes WRONG
#   (s2) S2943 [rev1.4 R14-2] est.py's |med| <= r condition dropped (every failing delta row measured): the
#        self-test case "consistently negative above r: null" goes WRONG
#   (q1) S2944 [rev1.4 R14-3] the quiet check logs no co-runners: the dry run's quiet sample refuses QUIET-LOG
#   (b1) S2945 [rev1.4 R14-4] est.py's bimodal note names no row: the self-test case "a delta row in two
#        clusters is named by the bimodal note" goes WRONG
# `want` is an extended regex (grep -E). Ids S2934-S2939 are the kit's (span_cards §R1.3 r9 and r9fc rows), S2940-S2945
# rev 1.4's (§R1.4); they
# are slot-local rows, not tests/mech rows (no make suite runs their detectors).
set -u
export LC_ALL=C
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../../.." && pwd)
SCR=${1:?usage: sabotage.sh SCRATCH [ROW..]}
shift
ROWS=${*:-j j2 k l1 l2 l3 g2 g3 f1 f2 f6 n1 n2 s1 s2 q1 b1}
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

dry() {    # COPY JOB [NAME]: the job's dry run in the copy COPY (a fresh RUNDIR run.NAME), its rc and output NAME.out
           # (NAME defaults to COPY; the control's two runs keep their own, r9fc FIX-4); JOB `est` runs est.py's
           # self-test instead
    local n=${3:-$1}
    rm -rf "$SCR/run.$n"
    if [ "$2" = est ]; then
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/est.py" selftest "$SCR/run.$n" > "$SCR/$n.out" 2>&1
    else
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/run.py" dry "$2" "$SCR/run.$n" s2c-dry > "$SCR/$n.out" 2>&1
    fi
}

pass=0 fail=0
copy control
dry control J2
if [ $? -ne 0 ]; then
    echo "sabotage: CONTROL red (the unplanted copy's J2 dry run):"; tail -5 "$SCR/control.out"; exit 2
fi
echo "control   J2 dry run green"
dry control est control.est
if [ $? -ne 0 ]; then
    echo "sabotage: CONTROL red (the unplanted copy's est.py self-test):"; tail -5 "$SCR/control.est.out"; exit 2
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
    l3) job=J2 want='GATE MISS kit\.find_byte\.walk len [0-9]+ subject [0-9]+ SENTINEL: found 1 sum [0-9]+ fnv [0-9a-f]+ timed 0, planted 1 '
        # the ARMS' TUs only: ctl (job "ctl") compiles the unplanted text and gates green first, so the miss is
        # a launch executable's (the control's gate line precedes it in the output)
        patch "$SCR/$row/link.py" '        o = compile_tu(src, os.path.join(d, "arm%d.c" % k), sym)' \
'        o = compile_tu(src if job == "ctl" else src.replace("for (size_t p = 0; p < n && step(s, n, &p); p++) k++;",
                       "for (size_t p = 0; p < n / 2 && step(s, n / 2, &p); p++) k++;"), os.path.join(d, "arm%d.c" % k), sym)   # SABOTAGE S2934' ;;
    g2) job=J2 want='KEY-ARM MISMATCH kit\.find_byte\.libc'
        patch "$SCR/$row/plan.py" 'row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "libc", lengths=LENGTHS))' \
'row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "walk", lengths=LENGTHS))   # SABOTAGE S2935' ;;
    g3) job=est want='selftest	leftover cells of a never-ran job	WRONG'
        patch "$SCR/$row/est.py" '        if j not in ran:
            raise InputError("%s holds cells of job %s' '        if False:   # SABOTAGE S2936
            raise InputError("%s holds cells of job %s' ;;
    f1) job=est want='selftest	live card/policy edit after the run	WRONG'
        patch "$SCR/$row/est.py" '            G = card[key.split(".")[1]]["gate"]' \
'            G = plan.CARD[key.split(".")[1]]["gate"]   # SABOTAGE S2937' ;;
    f2) job=J3 want='KEY-ARM MISMATCH kit\.find_hit\.(libc|walk)\.periodic\.one\.[0-9]+: dim landing: the key names periodic, the Arm random'
        patch "$SCR/$row/plan.py" '                row("J3", Arm(k, "J3.hit.%s.%d" % (ld, g), "find", f, landing=ld, split=sp, gap=g,' \
'                row("J3", Arm(k, "J3.hit.%s.%d" % (ld, g), "find", f, landing="random", split=sp, gap=g,   # SABOTAGE S2938' ;;
    f6) job=J4 want='ROUND MISS kit\.verify_cmp\.[a-z0-9-]+\.[a-z0-9]+\.p50(#b)? len [0-9]+: [0-9]+ calls, ACC [0-9]+, planted [0-9]+'
        patch "$SCR/$row/drv.c" '    for (uint64_t k = 0; k < n; k++) {' \
'    for (uint64_t k = 0; k < (a->kind == K_CMP ? n / 2 : n); k++) {   /* SABOTAGE S2939 */' ;;
    n1) job=J4 want='NULL-BASE MISMATCH base\.null\.[a-z0-9]+: its text differs from its class arm'"'"'s outside the compare'
        patch "$SCR/$row/link.py" '        return src[:i] + null_body(src[i:j]) + src[j:], None, f' \
'        return (src[:i] + null_body(src[i:j]) + src[j:]).replace("for (const uint32_t *p = c, *e = c + nc; p < e; p++) k += test(s, *p) != 0;",
                                                               "for (size_t q = 0; q < nc; q++) k += test(s, c[q]) != 0;"), None, f   # SABOTAGE S2940' ;;
    n2) job=J4 want='NULL-BASE MISMATCH base\.null\.(l1|w[123]): its body .* keeps no load its class arm'
        patch "$SCR/$row/link.py" '    return "slot_null(%s)\n" % min(hits)[1]' '    return "slot_null(subject[pos])\n"   # SABOTAGE S2941' ;;
    s1) job=est want='selftest	\[R14-2\] consistently negative within r: measured, its value clamped to 0	WRONG'
        patch "$SCR/$row/est.py" 'value=max(0, r["value"])' 'value=r["value"]' ;;
    s2) job=est want='selftest	\[R14-2\] consistently negative above r: null \(a fixture artifact\)	WRONG'
        patch "$SCR/$row/est.py" '            if r["null"] and abs(r["value"]) <= res:' '            if r["null"]:   # SABOTAGE S2943' ;;
    q1) job=J2 want='QUIET-LOG'
        patch "$SCR/$row/run.py" '    return ",".join(top) or "-"' '    return "-"   # SABOTAGE S2944' ;;
    b1) job=est want='selftest	\[R14-4\] a delta row in two clusters is named by the bimodal note	WRONG'
        patch "$SCR/$row/est.py" 'and not r.get("sub") and split_gap(r["x"]) * 10**6 > NOTE_BIMODAL_E6 * r["value"])' \
'and not r.get("sub") and False)   # SABOTAGE S2945' ;;
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
