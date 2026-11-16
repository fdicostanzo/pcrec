#!/usr/bin/env bash
# span_cards/slot/sabotage.sh — the SLOT-LOCAL sabotage rows of unit S2c (span_cards.md §9 S2c, rev 1.2
# READY-5): their detectors run only in the slot harness's dry run (`run.py dry`), which no make suite runs, so this
# runner plants each in a SCRATCH COPY of slot/, runs the named job's dry run there under run id s2c-dry, and
# expects the named refusal (precedent: docs/design/r17b_prime/b3a/sabotage/run_skb3a.sh). A control run of
# the unplanted copy must be green first, ON EVERY JOB THE SELECTED ROWS SCORE ON (review 2026-11-15 r1 F3: J2 and
# the est self-test always, plus each other job a row names, so an unplanted regression of that job cannot score
# a row DETECTED). Each row scores DETECTED (the dry run refused with the expected text) or MISSED; exit 0 iff the
# control is green and every row is DETECTED.
#   slot/sabotage.sh SCRATCH [ROW..]      rows: j j2 k l1 l2 l3 g2 g3 f1 f2 f6 n1 n2 n3 s1 s2 s3 s4 s5 q1 b1 x1 x2 x3 d1
#                                         t1 t2 r1 r2 k1 v1 v2 w1 e1 e2 e3 e4 f8a f8b i1-i10 m1-m7 z1-z4
#                                         y1 y2 y3 y4 y5 y6 y7 y8 y9 y10 y11 (default all)
#   (j)  the placement draw ignores the launch (and so its re-draw index): every launch links the same pads;
#        the cross-launch constraint on `nm` of the seven executables refuses after the bounded re-draw
#   (j2) a twin linked at its arm's phase (its pad sized to land it there): the per-launch constraint
#        refuses, after the bounded re-draw
#   (k)  the libc arm rendered from another entry row (walk's): its site-text hash differs from
#        mf_form_hash(libc) (its facts walk's too, so walk's table compiles): the cell-text check refuses
#        (j4fix: was walk-from-libc, which since r6's TIMED_CALLEES the timed-shape check refuses first)
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
#   (n2) S2941 [rev1.4 R14-1, re-aimed r10-REV14-3] null_body KEEPS THE COMPARE (slot_null(<the whole arm body>),
#        the critic's slot_null(mf_w4(subject + pos) == K)): the check's independent half refuses (its argument is
#        not one load spelling); the equality half shares null_body with the render and cannot see this plant
#   (n3) S2946 [r10-REV14-3] the render keeps the arm's LAST load (null_body over the last ` && ` conjunct): a load
#        the arm makes, so only the equality half refuses, on the multi-word classes (w2, w3)
#   (s1) S2942 [rev1.4 R14-2, re-aimed r10-REV14-1] est.py's sub-resolution value not clamped: the self-test case
#        "signs mixed, a negative median within r" (value must be 0) goes WRONG
#   (s2) S2943 [rev1.4 R14-2] est.py's |med| <= r condition dropped (every failing delta row within its A/A
#        measured): the self-test case "signs mixed at a size above r: null" goes WRONG
#   (s3) S2947 [r10-REV14-1] est.py's all-negative rule dropped: the self-test case "negative on all six trimmed
#        launches within r: null" goes WRONG (the first window's l1 defect, priced at 0 under rev 1.4)
#   (s4) S2948 [r10-REV14-2] est.py's cap on r dropped: the self-test case "|med| within its own r but above
#        r_max: null" goes WRONG
#   (s5) S2949 [r10-REV14-2] est.py's paired A/A requirement in the branch dropped: the self-test case "within r,
#        its paired A/A above r: null" goes WRONG
#   (q1) S2944 [rev1.4 R14-3] the quiet check logs no co-runners: the dry run's quiet sample refuses QUIET-LOG
#   (b1) S2945 [rev1.4 R14-4] est.py's bimodal note names no row: the self-test case "a delta row in two
#        clusters is named by the bimodal note" goes WRONG
#   (x1) S2950 [rev1.5 R15-1] the fused-compare DERIVATION hands the fact to every class that reads the subject (a
#        non-fused class wearing the fact): the bytes' reading refuses FUSED-FACT MISMATCH, so the self-test's
#        "complete" case is refused
#   (x2) S2951 [rev1.5 R15-1] the fact CHECK removed (the bytes' reading never compared): the self-test case "a
#        non-fused class wearing the fact" (refused) goes WRONG
#   (x3) S2952 [rev1.5 R15-1] the fused branch applied WITHOUT the fact (every verify row): the self-test case "a
#        class NOT fused negative on all six: null (REV14-1 holds)" goes WRONG
#   review r11 (span_cards §R1.5's r11 table; each a self-test case, red planted, green reverted):
#   (y1) S2953 [r11-REV15-8, R15-2] the moved-timed-code refusal removed (`if moved:` never taken): the gate case "timed
#        code (src/) moved since code_commit" goes WRONG
#   (y2) S2954 [r11-REV15-8, R15-2] the uncommitted-estimator refusal removed (the blob comparison never refuses): the
#        gate case "est.py edited, uncommitted" goes WRONG
#   (y3) S2955 [r11-REV15-8, REV15-1] the launch executables' sha-256 check against the manifest removed: the case "a
#        launch executable not the manifest's (P3)" goes WRONG (it is refused later, UNSTABLE, not by the manifest)
#   (y4) S2956 [r11-REV15-8, REV15-6] a file not tracked at HEAD accepted (the ignored-copy bypass): the gate case "an
#        est.py copy under an ignored path" goes WRONG
#   (y5) S2957 [r11-REV15-2] the fact over ANY number of subject reads, all fused: the case "c1 compiled as two fused
#        compares: not fused, null" goes WRONG
#   (y6) S2958 [r11-REV15-10] the fused-base refusal removed: the case "a null base compiled fused" goes WRONG
#   (y7) S2959 [r11-REV15-5] a bound row's value 0 whatever its sign: the case "a fused class priced positive" goes WRONG
#   (y8) S2960 [r11-REV15-1] the stems taken from obj/tab.c (unpinned) instead of the pinned plan: the case "obj/tab.c's
#        stems swapped (P6)" goes WRONG
#   (y9) S2961 [r11-REV15-4] the symbol's range ignored (objdump's listing to the next symbol): the reading case "a load
#        past the symbol's size (padding) beside a fused compare: fused" goes WRONG
#   (y10) S2962 [r11-REV15-4] the bytes' reading does not recognise VEX/EVEX: the reading case "a fused compare beside a
#        VEX load of the subject" goes WRONG (a mismatch)
#   (y11) S2963 [r11-REV15-7] a path no NON_TIMED row names read as NOT timed (an inclusion list again): the gate case
#        "timed code (src/) moved since code_commit" goes WRONG
#   K38-3 (span_runs_sheet.md §5.2, [r1s1 S1-13], [r2s1 RK383-4]):
#   (d1) S3105 the DIM_FIELD line for `back` removed with the kit-grid@4 `enter_back` rows still planned: plan.py's
#        build()-time dim check refuses (`plan.py report` is the dry run here: no compile, no render). Without the
#        check the planner runs on (the refusal was link time only, and a card with no planned row loaded silently)
#   lane slotx (kit-grid@6's pieces: the per-arm target region, the reject dim, ver-6 planning; harness fidelity):
#   (t1) S3160 the w32 arm compiled at the DEFAULT target while keyed x86-64-v3: the frame's header lines kept, its
#        region dropped (every TU at -march=x86-64 alone): gcc refuses the AVX2 intrinsics outside the region
#   (t2) S3161 every cell TU compiled at -march=x86-64-v3 (a stray flag; the declared floor unchanged): the generic
#        arms keyed generic run v3 code; link.py's ISA check refuses (ISA MISMATCH ... keyed target generic)
#   (r1) S3162 the generator plants NO rejected hit (the reject rate dropped to 0) while the key, the table entry and
#        the record say 50/100: run.py's realized-reject check on the gate's `reject` lines refuses (the answer gate
#        alone is blind: gen.c's own expectation moves with it)
#   (r2) S3163 the table entry (tab.c) states reject 0 for every arm, the key 50/100: the generator plants 0; the
#        realized-reject check, holding the bytes to the KEY's percent, refuses
#   (k1) S3167 plan.py builds the reject-50 Arms with reject 0 (their keys keep 50): KEY-ARM MISMATCH on dim reject
#   (v1) S3164 a ver-6 card's rows written to ver 4's set (the writer's split moves a ver-6 key to ver 4): the split's
#        own per-set card check refuses (DRAFT-VER MISMATCH); the want names that refusal's text, not the case's
#        WRONG, which the case's own predicate gives without the check (review 2026-11-15 r1 F4)
#   (v2) S3165 card_of resolves by QUANTITY alone (deps ignored, the first card: ver 3's): a ver-6 key priced by the
#        ver-3 card of the same quantity; the plan's build-time key check refuses (a find_hit@6 key's 5 tokens
#        against find_hit@3's 4 dims; find_byte's equal dims alone would price it silently, so the dims are the
#        witness, and est's draft split checks the set's cards again)
#   (w1) S3166 est.py prices every frozen row, the window's or not: the mfcard self-test refuses (J3-J5 rows read
#        never-ran, their floor clauses fail)
#   review 2026-11-15 r1 (slotxfix):
#   (e1) S3168 [F1] the w32 TU (keyed x86-64-v3) compiled in a region that also enables AVX-512F/VL: gcc emits EVEX
#        code on %ymm, which a mnemonic/register reading takes for AVX2; the ISA check, classifying by ENCODING,
#        refuses (ISA MISMATCH ... keyed target x86-64-v3, its code needs avx512f,avx512vl)
#   (e2) S3169 [F2] the ISA table's `fma` row deleted: the table check over every planned target's --target-facts
#        refuses (ISA TABLE: planned target x86-64-v3 enables fma ...); no arm emits FMA, so no ISA check can
#   (e3) S3171 [F5] write_draft's per-ver selection also writes every ver-6 row into ver 3's set (draft_split
#        untouched): est.py's self-test case "[F5] write_draft on the mfcard window" goes WRONG
#   (e4) S3172 [F8] write_draft's mixed-ISA-level refusal removed: the self-test case "[F8] write_draft refuses a
#        set mixing ISA levels" goes WRONG
#   review 2026-11-15 r1 F8 (slotxf8b):
#   (f8a) S3183 [re-aimed r5] the level derivation files x86-64-v3 at the floor's level (the baseline set): the
#        guard, reading the needs link.py recorded, refuses (DRAFT-ISA-LEVEL MIXED) in the one-set-per-level case
#   (f8b) S3184 [re-aimed r5] the v3 set keeps the baseline class value: the guard reads the class back and refuses
#   review 2026-11-15 r5 memfn-mfindcomb (mcfixa):
#   (i1) S3188 [FIDELITY-1] the find wrapper's gate compiled back INTO the timed TU, no gate object (the critic's
#        shape: two callers of `step`): gcc keeps the w16/w32 finder out of line; the timed-shape check refuses (TIMED-SHAPE ...
#        calls mf_fn__w16)
#   (i2) S3189 [FIDELITY-2] est checks the manifests of verify jobs only (as before r5): the P11 case goes WRONG
#   (i3) S3190 [FIDELITY-2] the manifest's cell_text pin not compared: the P11 case goes WRONG
#   (i4) S3191 [FIDELITY-5] the duplicate-cell refusal removed: the one-cell-two-lines case goes WRONG
#   (i5) S3192 [DRAFTSETS-2] the cell_text-twice refusal removed: the P9 case goes WRONG
#   (i6) S3193 [contract-2] the unit row not repeated in the ver-6 sets: the tree's loader refuses them (LOAD)
#   (i7) S3194 [FIDELITY-3] a base's cells filed with every set: the guard refuses base.mfind-w32's
#        (x86-64-v3 needs) in the baseline set
#   (i8) S3195 [FIDELITY-3] every job control in every set: the levels case goes WRONG (JMB/JMH ctl in ver 3's)
#   (i9) S3196 [FIDELITY-4] the D197 rule's A/A floor dropped: the drill's within-floor tie reads WIN (WRONG)
#   (i10) S3197 [R3 (1)] a confirming run never clears a loss: the not-reproduced case reads CONFIRM (WRONG)
#   review 2026-11-15 r6 (lane mcfixb):
#   (m1) S3207 [FIDELITY-3] est's cells pin not compared: the swapped-cells case is priced (WRONG)
#   (m2) S3208 [RULE-2] a confirming record's run id not held apart: the first-run-id case passes (WRONG)
#   (m3) S3209 [RULE-1] the second-run-without-a-verdict row never matches: the second run's refused shipped
#        record reads INCONCLUSIVE, a third run (WRONG)
#   (m4) S3214 [RULE-7] the scan reads a key no row has (every ratio `-`): the end-to-end drill's number check
#        goes WRONG (job d197e2e: the drill with its SCRATCH)
#   (m5) S3215 [FIDELITY-1] TIMED-SHAPE's section-symbol refusal dropped: link.py shape-selftest's `section`
#        case goes WRONG (job shape). The four out-of-line plants S3210-S3213 are that self-test's own cases
#   lane j4fix:
#   (m6) S3221 a cell-less J4 null base left unkeyed (timed_form returns None: TIMED_CALLEES' "any external"):
#        link.py shape-selftest's out-of-line null-base plant S3220 goes WRONG (job shape)
#   lane pinfix:
#   (m7) S3226 [ADQ-3] est's absent cells pin tolerated on a windowed record again: the mfcard-window
#        pin-deleted case goes WRONG (job est)
#   lane scanrow (review 2026-11-16 r13 JF-4 (a): a refused find_byte@6 SCAN row never vetoes a level's verdict):
#   (z1) S3238 every refusal read as scan-only: the drill's "a DECIDING row's clause refused" case reads WIN (WRONG)
#   (z2) S3239 the old veto back (any REFUSED outcome refuses the arm): the CLI case "the scan row refused in both
#        records" (only the scan row noisy, est's real refusal) reads INCONCLUSIVE (WRONG; job d197e2e)
#   (z3) S3240 the scan line ignores est's gate (prints a gate-FAILED row's value and a ratio): the same CLI case's
#        `scan unpriced (gate FAIL: ...)` count goes WRONG (job d197e2e)
#   (z4) S3241 est's refusals name no keys: est's self-test case "the scan row ... noisy alone" goes WRONG (job est)
# `want` is an extended regex (grep -E). Ids S2934-S2939 are the kit's (span_cards §R1.3 r9 and r9fc rows), S2940-S2945
# rev 1.4's (§R1.4), S2946-S2949 review r10's (§R1.4's r10 table), S2950-S2952 rev 1.5's (§R1.5), S2953-S2963 review
# r11's (§R1.5's r11 table), S3105 K38-3's, S3160-S3167 lane slotx's, S3168 S3169 S3171 S3172 lane slotxfix's, S3183 S3184 lane slotxf8b's,
# S3188-S3197 lane mcfixa's, S3207-S3209 S3214 S3215 lane mcfixb's, S3220 S3221 lane j4fix's, S3224-S3226 lane pinfix's,
# S3238-S3241 lane scanrow's; they
# are slot-local rows, not tests/mech rows (no make suite runs their detectors).
set -u
export LC_ALL=C
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=${SLOT_TREE:-$(cd "$here/../../../../.." && pwd)}   # SLOT_TREE: the tree when slot/ runs from a copy
SCR=${1:?usage: sabotage.sh SCRATCH [ROW..]}
shift
ROWS=${*:-j j2 k l1 l2 l3 g2 g3 f1 f2 f6 n1 n2 n3 s1 s2 s3 s4 s5 q1 b1 x1 x2 x3 y1 y2 y3 y4 y5 y6 y7 y8 y9 y10 y11 d1 t1 t2 r1 r2 k1 v1 v2 w1 e1 e2 e3 e4 f8a f8b i1 i2 i3 i4 i5 i6 i7 i8 i9 i10 m1 m2 m3 m4 m5 m6 m7 z1 z2 z3 z4}
. "$TREE/tests/lib/timeout_bin.sh"
TO=$TIMEOUT_BIN
mkdir -p "$SCR"

copy() {   # a fresh copy of slot/ in $SCR/$1
    rm -rf "$SCR/$1"
    cp -r "$here" "$SCR/$1/"
}

patch() {  # FILE OLD NEW: exactly one occurrence, else the plant itself fails (loud); PLANT=0: plants nothing
    [ "${PLANT:-1}" = 1 ] || return 0
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
    if [ "$2" = plan ]; then          # JOB `plan`: the planner's report (build() and its checks), no render
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/plan.py" report > "$SCR/$n.out" 2>&1
    elif [ "$2" = d197 ]; then        # JOB `d197`: the D197 rule's drill (constructed outcomes)
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/d197_rule.py" drill > "$SCR/$n.out" 2>&1
    elif [ "$2" = d197e2e ]; then     # JOB `d197e2e`: the drill and its end-to-end cases on est's synth (r6)
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/d197_rule.py" drill "$SCR/run.$n" > "$SCR/$n.out" 2>&1
    elif [ "$2" = shape ]; then       # JOB `shape`: link.py's TIMED-SHAPE self-test (r6)
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/link.py" shape-selftest "$SCR/run.$n" > "$SCR/$n.out" 2>&1
    elif [ "$2" = est ]; then
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/est.py" selftest "$SCR/run.$n" > "$SCR/$n.out" 2>&1
    else
        SLOT_TREE=$TREE "$TO" 900 python3 -I "$SCR/$1/run.py" dry "$2" "$SCR/run.$n" s2c-dry > "$SCR/$n.out" 2>&1
    fi
}

row_def() {   # ROW: sets `job` and `want` and plants the row in $SCR/ROW (PLANT=0: sets them only)
    local row=$1
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
        patch "$SCR/$row/link.py" '    f = facts(fx, form, cls)' '    f = facts(fx, {"libc": "walk"}.get(form, form), cls)'
        patch "$SCR/$row/link.py" '    fi, bo = parts(fx, form, cls)' '    fi, bo = parts(fx, {"libc": "walk"}.get(form, form), cls)' ;;
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
        patch "$SCR/$row/est.py" '            G = plan.card_of(card, key)["gate"]' \
'            G = plan.card_of(plan.CARD, key)["gate"]   # SABOTAGE S2937 (re-anchored, slotxfix: the lookup is card_of since slotx)' ;;
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
    n2) job=J4 want='NULL-BASE MISMATCH base\.null\.[a-z0-9]+: its body .* is not slot_null\(one load its class arm'
        patch "$SCR/$row/link.py" '    return "slot_null(%s)\n" % min(hits)[1]' '    return "slot_null(%s)\n" % body.strip()   # SABOTAGE S2941' ;;
    n3) job=J4 want='NULL-BASE MISMATCH base\.null\.w[23]: its body .* is not null_body\(its class arm'
        patch "$SCR/$row/link.py" '        return src[:i] + null_body(src[i:j]) + src[j:], None, f' \
'        return src[:i] + null_body(src[i:j].split(" && ")[-1]) + src[j:], None, f   # SABOTAGE S2946' ;;
    s1) job=est want='selftest	\[r10-REV14-1\] signs mixed, a negative median within r: measured, its value clamped to 0	WRONG'
        patch "$SCR/$row/est.py" 'value=max(0, r["value"])' 'value=r["value"]' ;;
    s2) job=est want='selftest	\[R14-2\] signs mixed at a size above r: null	WRONG'
        patch "$SCR/$row/est.py" '            elif r["null"] and abs(r["value"]) <= res and r["aa"] <= res:' \
'            elif r["null"] and r["aa"] <= res:   # SABOTAGE S2943' ;;
    s3) job=est want='selftest	\[r10-REV14-1\] negative on all six trimmed launches within r: null \(a defect, whatever r\)	WRONG'
        patch "$SCR/$row/est.py" '            if r["null"] and all(d < 0 for d in trim(r["D"])):' '            if False:   # SABOTAGE S2947' ;;
    s4) job=est want='selftest	\[r10-REV14-2\] signs mixed, \|med\| within its own r but above r_max: null	WRONG'
        patch "$SCR/$row/est.py" '            res = min(resolution(x), R_MAX)' '            res = resolution(x)   # SABOTAGE S2948' ;;
    s5) job=est want='selftest	\[r10-REV14-2\] within r, its paired A/A above r: null	WRONG'
        patch "$SCR/$row/est.py" '            elif r["null"] and abs(r["value"]) <= res and r["aa"] <= res:' \
'            elif r["null"] and abs(r["value"]) <= res:   # SABOTAGE S2949' ;;
    q1) job=J2 want='QUIET-LOG'
        patch "$SCR/$row/run.py" '        a = cpu_ticks()' '        return "-"   # SABOTAGE S2944' ;;
    b1) job=est want='selftest	\[R14-4\] a delta row in two clusters is named by the bimodal note	WRONG'
        patch "$SCR/$row/est.py" 'and not r.get("fused") and split_gap(r["x"]) * 10**6 > NOTE_BIMODAL_E6 * r["value"])' \
'and not r.get("fused") and False)   # SABOTAGE S2945' ;;
    x1) job=est want='selftest	complete	WRONG	refused \(FUSED-FACT MISMATCH'
        # [r11] re-anchored: the derivation (fused_text) returns "reads the subject" in place of fact_of()
        patch "$SCR/$row/est.py" '                                             or bool(re.fullmatch(r"test[bwlq]?", m)) and first.startswith("$")))
    return fact_of(reads)' '                                             or bool(re.fullmatch(r"test[bwlq]?", m)) and first.startswith("$")))
    return bool(reads)   # SABOTAGE S2950' ;;
    x2) job=est want='selftest	\[R15-1\] a non-fused class wearing the fact	WRONG'
        patch "$SCR/$row/est.py" '                    if fused_bytes(ins) != f:' '                    if False:   # SABOTAGE S2951' ;;
    x3) job=est want='selftest	\[R15-1\] a class NOT fused negative on all six: null \(REV14-1 holds\)	WRONG'
        patch "$SCR/$row/est.py" '        if r["D"] is not None and fused.get(key):' \
'        if r["D"] is not None and key.startswith("kit.verify_cmp."):   # SABOTAGE S2952' ;;
    y1) job=est want='selftest	\[r11 gate\] timed code \(src/\) moved since code_commit	WRONG'
        patch "$SCR/$row/est.py" '    if moved:
        raise InputError("the timed code moved' '    if False:   # SABOTAGE S2953
        raise InputError("the timed code moved' ;;
    y2) job=est want='selftest	\[r11 gate\] est\.py edited, uncommitted	WRONG'
        patch "$SCR/$row/est.py" '        if git("-C", top, "hash-object", "--", os.path.realpath(p)).stdout.strip() != m.group(1):' \
'        if False:   # SABOTAGE S2954' ;;
    y3) job=est want='selftest	\[r11-REV15-1\] a launch executable not the manifest.s \(P3\)	WRONG'
        patch "$SCR/$row/est.py" '        if plan.sha256(exe) != m.get("L%d" % l):' '        if False:   # SABOTAGE S2955' ;;
    y4) job=est want='selftest	\[r11 gate\] an est\.py copy under an ignored path	WRONG'
        patch "$SCR/$row/est.py" '        if not m:
            return None, "%s is not tracked' '        if not m:
            continue   # SABOTAGE S2956
            return None, "%s is not tracked' ;;
    y5) job=est want='selftest	\[r11-REV15-2\] c1 compiled as two fused compares: not fused, null	WRONG'
        patch "$SCR/$row/est.py" '    return len(reads) == 1 and reads[0]' '    return bool(reads) and all(reads)   # SABOTAGE S2957' ;;
    y6) job=est want='selftest	\[r11-REV15-10\] a null base compiled fused	WRONG'
        patch "$SCR/$row/est.py" '            if fact((b,), b):' '            if False:   # SABOTAGE S2958' ;;
    y7) job=est want='selftest	\[R15-1, r11-REV15-5\] a fused class priced positive[^	]*	WRONG'
        patch "$SCR/$row/est.py" 'value=max(r["value"], 0), noise=max(R_MAX' 'value=0, noise=max(R_MAX' ;;
    y8) job=est want='selftest	\[r11-REV15-1\] obj/tab\.c.s stems swapped \(P6\)	WRONG'
        patch "$SCR/$row/est.py" '        if tab != stems:' '        stems = tab   # SABOTAGE S2960
        if tab != stems:' ;;
    y9) job=est want='selftest	\[r11 reading\] a load past the symbol.s size \(padding\) beside a fused compare: fused	WRONG'
        patch "$SCR/$row/est.py" '        if m and cur is not None and lim[0] <= int(m.group(1), 16) < lim[1]:' \
'        if m and cur is not None:   # SABOTAGE S2961' ;;
    y10) job=est want='selftest	\[r11 reading\] a fused compare beside a VEX load of the subject: not fused \(both read the VEX operand\)	WRONG'
        patch "$SCR/$row/est.py" '    vex = b[i] in (0xC4, 0xC5, 0x62)          # 64-bit mode: always VEX (C4/C5) or EVEX (62)' \
'    vex = False   # SABOTAGE S2962' ;;
    y11) job=est want='selftest	\[r11 gate\] timed code \(src/\) moved since code_commit	WRONG'
        patch "$SCR/$row/est.py" '            return t
    return True' '            return t
    return False   # SABOTAGE S2963' ;;
    d1) job=plan want='plan: card enter_back@4 dim back has no DIM_FIELD line'
        patch "$SCR/$row/plan.py" '    ("back",    lambda a: None if a.back is None else str(a.back)),    # kit-grid@4: the step-back t
' '' ;;
    t1) job=JMB want='inlining failed in call to .*target specific option mismatch'
        patch "$SCR/$row/link.py" '    return gd + pro + heads + ro + "#define CAT_(a, b) a##b\n" + rest + rc' \
'    return gd + pro + heads + "#define CAT_(a, b) a##b\n" + rest   # SABOTAGE S3160' ;;
    t2) job=JMB want='ISA MISMATCH [^ ]+: keyed target generic, its code needs'
        patch "$SCR/$row/link.py" '    sh(CC + ["-DSLOT_GATE_TU"] * gate + ["-c", "-DSYM=" + sym,' '    # SABOTAGE S3161
    sh(CC + ["-DSLOT_GATE_TU"] * gate + ["-march=x86-64-v3", "-c", "-DSYM=" + sym,' ;;
    r1) job=JMH want='REJECT-RATE MISMATCH kit\.find_hit\.[a-z0-9-]+\.periodic\.one\.[0-9]+\.(50|100)'
        patch "$SCR/$row/gen.c" '        uint32_t m = (uint32_t)((uint64_t)E * (uint64_t)a->reject / 100);' \
'        uint32_t m = 0;   /* SABOTAGE S3162 */' ;;
    r2) job=JMH want='REJECT-RATE MISMATCH kit\.find_hit\.[a-z0-9-]+\.periodic\.one\.[0-9]+\.(50|100)'
        patch "$SCR/$row/link.py" '               50 if a.pas == "p50" else 0, a.reject or 0, subj, expect))' \
'               50 if a.pas == "p50" else 0, 0, subj, expect))   # SABOTAGE S3163' ;;
    k1) job=JMH want='KEY-ARM MISMATCH kit\.find_hit\.[a-z0-9-]+\.periodic\.one\.[0-9]+\.50: dim reject: the key names 50, the Arm 0'
        patch "$SCR/$row/plan.py" '                           base=base_of(k), events=LEN // g, reject=r), base_of(k))' \
'                           base=base_of(k), events=LEN // g, reject=0 if r == 50 else r), base_of(k))   # SABOTAGE S3167' ;;
    v1) job=est want='selftest	\[slotx\] the draft split[^	]*	\(DRAFT-VER MISMATCH'
        patch "$SCR/$row/est.py" '            v = plan.card_of(rec["card"], r[0])["ver"]' \
'            v = plan.card_of(rec["card"], r[0])["ver"]
            v = "4" if v == "6" else v   # SABOTAGE S3164' ;;
    v2) job=plan want='plan: key kit\.find_hit\.[a-z0-9.-]+ has 5 tokens, its card.s dims'
        patch "$SCR/$row/plan.py" '           and (card_forms(c) is None or (len(q) > 2 and q[2] in card_forms(c)))]' \
'           ][:1]   # SABOTAGE S3165' ;;
    w1) job=est want='selftest	\[slotx\] window mfcard[^	]*	WRONG'
        patch "$SCR/$row/est.py" '    win = [(k, g, j) for k, g, j in rec["plan"] if j in rec["jobs"]]' \
'    win = [(k, g, j) for k, g, j in rec["plan"]]   # SABOTAGE S3166' ;;
    e1) job=JMB want='ISA MISMATCH kit\.find_byte\.mfind-w32(#b)?: keyed target x86-64-v3, its code needs avx512f,avx512vl'
        patch "$SCR/$row/link.py" '    return gd + pro + heads + ro + "#define CAT_(a, b) a##b\n" + rest + rc' \
'    return gd + pro + heads + ro.replace('"'"'target("avx2'"'"', '"'"'target("avx512f,avx512vl,avx2'"'"') + "#define CAT_(a, b) a##b\n" + rest + rc   # SABOTAGE S3168' ;;
    e2) job=J2 want='ISA TABLE: planned target x86-64-v3 enables fma above the floor'
        patch "$SCR/$row/link.py" '    ("vex", r"vf(n?m(add|sub)|maddsub|msubadd)\S*", r"", ("fma",)),
' '' ;;
    e3) job=est want='selftest	\[F5\] write_draft on the mfcard window[^	]*	WRONG'
        patch "$SCR/$row/est.py" '        vrows = groups[(v, suf, cls)]' \
'        vrows = groups[(v, suf, cls)] + (split.get("6", []) if v == "3" else [])   # SABOTAGE S3171' ;;
    e4) job=est want='selftest	\[F8, r5 P4\] write_draft refuses a set mixing ISA levels[^	]*	WRONG'
        # [r5] re-anchored: the guard's over-the-class test never refuses
        patch "$SCR/$row/est.py" '        if over:
            raise InputError("DRAFT-ISA-LEVEL MIXED' '        if False:   # SABOTAGE S3172
            raise InputError("DRAFT-ISA-LEVEL MIXED' ;;
    f8a) job=est want='selftest	\[F8\] write_draft writes one ver-6 set per ISA level[^	]*	\(DRAFT-ISA-LEVEL MIXED'
        # [r5] re-anchored: the level derivation files every target at the floor's level (the baseline set)
        patch "$SCR/$row/est.py" '        return self.floor if self.feats(tok) <= self.feats(self.floor) else tok' \
'        return self.floor   # SABOTAGE S3183: every target at the floor level' ;;
    f8b) job=est want='selftest	\[F8\] write_draft writes one ver-6 set per ISA level[^	]*	\(DRAFT-ISA-LEVEL MIXED'
        # [r5] re-anchored: the v3 set keeps the baseline class; the guard, reading the class back, refuses
        patch "$SCR/$row/est.py" '        return suf, "%s/%s" % (lvl.replace(self.floor, self.floor.replace("-", "_"), 1), BOX_UARCH)' \
'        return suf, "%s/%s" % (self.floor.replace("-", "_"), BOX_UARCH)   # SABOTAGE S3184' ;;
    i1) job=JMB want='TIMED-SHAPE kit\.find_byte\.mfind-w(16|32)(#b)?: a[0-9]+_time calls mf_fn__w(16|32)'
        patch "$SCR/$row/link.py" '#endif
#ifdef SLOT_GATE_TU
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)c; (void)nc;' '#endif
#if 1   /* SABOTAGE S3188: the gate back in the timed TU */
__attribute__((noinline)) uint64_t CAT(SYM, _gate)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                                                   uint64_t *sum, uint64_t *h)
{
    (void)c; (void)nc;'
        patch "$SCR/$row/link.py" '            gates.append(compile_tu(src, os.path.join(d, "arm%d.c" % k), sym, gate=True))' \
'            pass   # SABOTAGE S3188: no gate object (the timed TU holds the gate)' ;;
    i2) job=est want='selftest	\[r5 P11\][^	]*	WRONG'
        patch "$SCR/$row/est.py" '    pins = {j: manifest_check(rundir, rec, j, L) for j in sorted(ran)}' \
'    pins = {}   # SABOTAGE S3189: the manifests checked for verify jobs only (fused_facts), as before r5' ;;
    i3) job=est want='selftest	\[r5 P11\][^	]*	WRONG'
        patch "$SCR/$row/est.py" 'MANIFEST_FILES = ("cell_text", "placement")' 'MANIFEST_FILES = ("placement",)   # SABOTAGE S3190' ;;
    i4) job=est want='selftest	\[r5 FIDELITY-5\] one cell, two lines: refused	WRONG'
        patch "$SCR/$row/est.py" '            if ck in seen:' '            if False:   # SABOTAGE S3191' ;;
    i5) job=est want='selftest	\[r5 DRAFTSETS-2 P9\] one key, two cell_text lines: refused	WRONG'
        patch "$SCR/$row/est.py" '            if key in out:
                raise InputError("CELL-TEXT TWICE' '            if False:   # SABOTAGE S3192
                raise InputError("CELL-TEXT TWICE' ;;
    i6) job=est want='selftest	\[r5 contract-2\][^	]*	\(LOAD draft\.v6'
        patch "$SCR/$row/est.py" '        groups[g] = sorted(unit + groups[g], key=lambda r: r[0])' \
'        groups[g] = sorted((unit if g[0] == "3" and not g[1] else []) + groups[g], key=lambda r: r[0])   # SABOTAGE S3193' ;;
    i7) job=est want='selftest	\[F8\] write_draft writes one ver-6 set per ISA level[^	]*	\(DRAFT-ISA-LEVEL MIXED.*base base\.mfind-w32'
        patch "$SCR/$row/est.py" '        hs = [g for g, vr in groups.items() if any(plan.base_of(r[0]) == a and job_of[r[0]] == c["job"] for r in vr)]' \
'        hs = list(groups)   # SABOTAGE S3194: a base with every set' ;;
    i8) job=est want='selftest	\[F8\] write_draft writes one ver-6 set per ISA level[^	]*	WRONG'
        patch "$SCR/$row/est.py" '            return [g for g, vr in groups.items() if any(job_of[r[0]] == c["job"] for r in vr)]' \
'            return list(groups)   # SABOTAGE S3195: every job control in every set' ;;
    i9) job=d197 want='drill	within-floor tie[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '        lambda c: c["gain"] > c["floor"] and all(x > 0 for x in trim(c["gain_l"])),' \
'        lambda c: c["gain"] > 0 and all(x > 0 for x in trim(c["gain_l"])),   # SABOTAGE S3196: the A/A floor dropped' ;;
    i10) job=d197 want='drill	\[R3\] that one-cell loss does NOT reproduce[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '    "loss-not-reproduced": lambda c: c["gain"] < -c["floor"] and c["conf"] is not None' \
'    "loss-not-reproduced": lambda c: False and c["conf"] is not None   # SABOTAGE S3197: a confirming run never clears a loss' ;;
    m1) job=est want='selftest	\[r6 FIDELITY-3\] two keys. cells swapped after finalize[^	]*	WRONG'
        patch "$SCR/$row/est.py" '        elif got != pin:' '        elif False:   # SABOTAGE S3207: the cells pin not compared' ;;
    m2) job=d197 want='drill	\[r6 provenance\] a confirming record \(window mfconfirm\) carrying[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '        if role.startswith("confirm.") and m["run"].get("run_id") in this | first:' \
'        if False:   # SABOTAGE S3208: a confirming run id not held apart' ;;
    m3) job=d197 want='drill	\[r6 RULE-1\] the shipped record REFUSED on the second run[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '    "second-run-without-a-verdict": lambda v: v["second"] and (' \
'    "second-run-without-a-verdict": lambda v: False and v["second"] and (' ;;   # SABOTAGE S3209 (the plant carries no comment: the line continues)
    m4) job=d197e2e want='drill	end to end on est.s synthetic window	WRONG'
        patch "$SCR/$row/d197_rule.py" '"kit.%s.%s" % (t["deciding"]["scan"], f)' '"kit.%s_.%s" % (t["deciding"]["scan"], f)' ;;   # SABOTAGE S3214 (the plant carries no comment: mid-line)
    m5) job=shape want='shape	\[S3210\][^	]*	WRONG'
        patch "$SCR/$row/link.py" '        if callee.startswith("."):' '        if False:   # SABOTAGE S3215: section symbols not refused' ;;
    m6) job=shape want='shape	\[S3220\][^	]*	WRONG'
        patch "$SCR/$row/link.py" '        return "null"
' '        return None   # SABOTAGE S3221: the null base unkeyed
' ;;
    m7) job=est want='selftest	\[r8 ADQ-3 S3224\][^	]*	WRONG'
        patch "$SCR/$row/est.py" '        if pin is None and not legacy_record(rec):      # [r8 ADQ-3] only a legacy record may lack the pin' \
'        if False:      # SABOTAGE S3226: a windowed record may lack the cells pin' ;;
    z1) job=d197 want='drill	\[r13 JF-4\] a DECIDING row.s clause refused[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '    "every-refusal-names-only-scan-rows": lambda f: bool(f["refusals"]) and all(' \
'    "every-refusal-names-only-scan-rows": lambda f: True or all(' ;;   # SABOTAGE S3238 (no comment: the line continues)
    z2) job=d197e2e want='drill	\[r13 JF-4\] CLI: the scan row refused in both records[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '    "run-refused": lambda a: a["refusal"] == "run-refused",' \
'    "run-refused": lambda a: a["outcome"] == "REFUSED",   # SABOTAGE S3239: any REFUSED record vetoes' ;;
    z3) job=d197e2e want='drill	\[r13 JF-4\] CLI: the scan row refused in both records[^	]*	WRONG'
        patch "$SCR/$row/d197_rule.py" '    if r.get("gate") is False:
        return None, r.get("gate_why", "gate FAIL")' '    if False:   # SABOTAGE S3240: the scan line ignores est'"'"'s gate
        return None, r.get("gate_why", "gate FAIL")' ;;
    z4) job=est want='selftest	\[r13 JF-4\] the scan row kit\.find_byte\.mfind-swar noisy alone[^	]*	WRONG'
        patch "$SCR/$row/est.py" '                                  for cl in failed], [("floor:" + cl, sorted(clauses[cl])) for cl in failed])' \
'                                  for cl in failed], [("floor:" + cl, []) for cl in failed])   # SABOTAGE S3241' ;;
    *)  echo "sabotage: unknown row $row"; exit 2 ;;
    esac
}

pass=0 fail=0
# [F3] THE CONTROL RUNS EVERY JOB THE ROWS SCORE ON: each selected row's job read off row_def (nothing planted)
cjobs="J2 est"
for row in $ROWS; do
    PLANT=0 row_def "$row"
    case " $cjobs " in *" $job "*) ;; *) cjobs="$cjobs $job" ;; esac
done
copy control
for j in $cjobs; do
    dry control "$j" "control.$j"
    if [ $? -ne 0 ]; then
        echo "sabotage: CONTROL red (the unplanted copy's $j dry run):"; tail -5 "$SCR/control.$j.out"; exit 2
    fi
    echo "control   $j green (unplanted)"
done

for row in $ROWS; do
    copy "$row"
    row_def "$row"
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
