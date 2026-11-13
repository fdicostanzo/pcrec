#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's window family, lane
#   wsc1, D172 S2 commit 1).
#
# memfn/tests/run_g2_win.sh — G2'S WINDOW FAMILY (docs/design/memfn/
# window_site.md rev 3.2; the kit's window family, memfn/src/window.c,
# every art's since D172 S2 commit 6). run_g2.sh's section
# 4w; runnable alone.
#
#   1. g2/g2_win_gen.c against the kit (LIB, default build/libpcrec.a; the
#      generator alone includes memfn.h): GENERATED window sites, the phase-1
#      reply, the phase-2 text in every frame Table E serves, and the lever's
#      CONTROLS (no decision and no spans-only render without the preview);
#   2. g2/g2_win_run.c, the driver, over the generated text: DECIDE (the reply
#      against g2/g2_win_ref.c's decision, written from the design), PLAN,
#      BIND, COMPL and READS (guard pages at s + n and at s + F, and
#      SENTINEL-padded buffers: review S2) per (subject, lo, F), built plain
#      and with ASan+UBSan;
#   3. W1: the reference's own planted defects (--ref-defect 2..5) must turn
#      the driver red;
#   4. the floors (K35), literals below, sharing no source with the family.
#
#   --plant NAME   the same run over a COPY of memfn/src with one planted
#                  defect (the table below): the run must go red. --plants
#                  runs them all. Writes only the work directory.
#
# G2W_TRACE=1 (plan_frame.md 3.0b, run by run_g2.sh against
# libpcrec_mftrace.a): the TRACED pass. LIB is an MF_TRACE kit, the plant
# path's kit_objs compile -DMF_TRACE, and the kit's agreement at every window
# define (compose.c define_sel) runs on G2's sites; a disagreement refuses the
# render (a generator FAIL). Its populations, the window defines per Table E
# row read off the generator's MFTRACE END records, are floored.
#
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR, G2W_SITES, G2W_SEED (and the
# appended streams' sizes: G2W_S3_SITES, G2W_C1_SITES, G2W_R2_SITES, G2W_H2_SITES,
# G2W_K3_SITES, the in-run sites under the lever run-tie-left).
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
. "$ROOT/tests/lib/timeout_bin.sh"
LIB="${LIB:-$ROOT/build/libpcrec.a}"
G2="$ROOT/memfn/tests/g2"
NSITES="${G2W_SITES:-1500}"
SEED="${G2W_SEED:-20261022}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/g2win.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# --- the floors (K35): hand-written literals, measured 2026-10-22 on the
# Linux dev box (seed 20261022, 1500 sites, lane wsc1), less ~10%. Raise them
# when the space grows; never lower one to make a run pass. D172 S3 (lane s3,
# 2026-10-22) appended 400 DENSE REPORT sites from their own stream (the 1500
# before them unchanged) and moved the S2 sites E-find renders off the floor:
# wf-floor's floor fell with them (792 -> 486 measured; pinned AT 486, the
# seeded space's deterministic count, at the S3 review), window-search's is new.
# Code review r1 (lane s3, 2026-10-23) appended 300 CASELESS REPORT sites from
# a stream of their own (G2W_C1_SITES; the 1900 before them unchanged): the
# population of Table B's PAIR in E-find, both renderers. Code review r2 (lane
# s3pair, 2026-10-23) appended 300 TWO-BYTE REPORT sites from a stream of their
# own (G2W_R2_SITES; the 2200 before them unchanged): the widened PAIR's
# population, any two bytes at any position.
FLOOR_SITES=2500                # every generated site renders (no refusal)
FLOOR_CONTROLS=104              # the controls, the NOP and REPORT refusals (116)
FLOOR_QUERIES=1500              # mf_ask equal to a same-phase define, every site
FLOOR_TWO_RUNS=77               # alternatives stating two R-shaped spans, refused (F-8 ruling; 86, lane wsc2)
FLOOR_CALLS=3300000             # answer calls, each in four layouts (3745812)
FLOOR_HITS=550000               # (622264)
PATH_FLOORS="empty:175 parked:285 reseed:105 mass:670 floor:110"
MARGIN_FLOORS="reseed:105 parked:135"
FLOOR_PINNED=34                 # (39)
FLOOR_RESEED_BIT=230            # (257)
TIE_FLOORS="mass:230 model:55"
CELL_FLOORS="edge_rejects:22000 core_off:1600000 noncore_off:490000 neg_reads:920000 nop_empty:130000"
FORM_FLOORS="window-search:630 wf-floor:486 generic:380 pf_memchr:215 ofsskip:27 pf_walk:15"
# D172 S3: E-find's reach by its text's parts (the generator's census of the
# kit's own text, a population count, never a verdict): B's LIBC and WALK
# forms, D-hors, a C-run compare, a stop below the candidate, REPORT sites;
# and the REPORT sites E-find cannot render, each refused (measured 357 220
# 124 129 110 413 19); code review r1: PAIR in the loop (B-pair) and through
# the offset-skip function (B-fn) (measured 141 54, with the caseless sites).
# Code review r2 R2-1 (PAIR widened to any two bytes): on the SAME 2200 sites
# 103 stops moved from the walk to PAIR (walk 217 -> 114, pair 141 -> 244,
# libc 598 -> 701: B-pair calls memchr), a JUDGED TRADE, not a lowered bar: the
# walk's floor follows its population to PAIR (pinned 103, the 114 measured
# less ~10%); with the two-byte sites pair measures 352 (floor 316).
# The S3 final review (lane s3fix, 2026-10-24): 100 BELOW-WINDOW sites appended from their own
# stream (G2W_H2_SITES; the 2500 before them unchanged): `hwin`, every site whose stop window lies
# wholly below the candidate (D-hors's scope, the generator's own census; measured 163), and the
# two-stream sites' LONG SUBJECTS (`long pair`, measured 406), each floor the measure less ~10%.
EFIND_FLOORS="libc:320 walk:103 hors:110 run:115 below:95 report:370 refused:17 pair:316 fn:48 hwin:146"
FLOOR_LONG_PAIR=365             # two-stream sites given the long subjects (406)
# plan_frame.md 3.0b: the framed EMIT ask's (frame_row, stream) cells and the
# frame part's classes, each at the measured count less ~10% (seed 20261022,
# 1500 sites: E-func/none 233, E-func/restart 38, E-stmt/none 355,
# E-stmt/restart 257, E-find/restart 1219, E-find/shift 131, E-generic/restart
# 567; fn 54, pair 409, hors 131, libc 684, walk 126, method 1607; table 61,
# noffer 4642 (a stated hook with no offer: OWN), below 40 (the stop below a
# TABLE plan position), stop_own 1264, af_walk 24 (row AF's population: B-walk
# sites whose stop marker is read). The impossible cells (MASK anywhere, SHIFT
# off E-find, E-generic off RESTART, E-func/E-stmt off RESTART/NONE, NONE not
# exactly ARM) are the generator's own failures, never a floor.
FRAME_CELL_FLOORS="E-func/none:210 E-func/restart:34 E-stmt/none:320 E-stmt/restart:231 E-find/restart:1097 E-find/shift:118 E-generic/restart:510"
# the TRACED pass's window defines per Table E row (G2W_TRACE=1; measured
# E-func 542, E-stmt 1227, E-find 2702, E-generic 1135), less ~10%: the
# agreement holds over each frame's sites, never over nothing
TRACED_FLOORS="E-func:487 E-stmt:1104 E-find:2431 E-generic:1021"
FRAME_CLASS_FLOORS="fn:48 pair:368 hors:118 libc:615 walk:113 method:1446 table:55 noffer:4178 below:36 stop_own:1138 af_walk:21"
# R-38 K38-2 PLAN (e) (EMIT-3 of code review 2026-11-10 r2 k382a; lane k382, 2026-11-11): 200
# IN-RUN sites appended from their own stream (G2W_K3_SITES; the 2700 before them unchanged),
# three in four on an art carrying the lever run-tie-left. Under the lever, the reference's own
# census of the in-run stop's branches: a candidate outside the run decision's own competing
# with R's stop at no greater mass (and winning), and a meet that moves R's stop (measured
# lever 159 set 60 set_won 15 meet 67), each floor the measure less ~10%.
INRUN_FLOORS="lever:143 set:54 set_won:13 meet:60"

# THE PLANTS: id, then FILE@@FROM@@TO (FILE under memfn/src; FROM replaced
# by TO, `\n` a newline, `\&` an ampersand). Each must make the run red.
# Ids from the kit's S1400-S1429 (R-29): S1400-S1407 were wsc1's WSC1-P1..P8; S1540
# (code review r2, lane s3pair), S1541-S1543 (the S3 final review, lane s3fix) and S1549
# (the span_pick 1e review, lane sp1efix) are the kit's S1540-S1559.
plant_spec() {
    case "$1" in
    S1400) # the edge guard dropped: a non-core position below the candidate read inside [0, F)
        # (re-aimed at D172 S3: the guard moved into wf_pos_test, which the floor and E-find share)
        echo 'window.c@@        kb_printf(t, "(%s >= %s + %d \&\& ", rc->C, rc->FL, -d);\n        rc->used |= PARAM_FL;@@        kb_printf(t, "(");' ;;
    S1401) # C-run merging singletons: positions one-position spans cover grouped into one compare
        echo 'window.c@@                join = !p->one_pos \&\& !q->one_pos \&\&@@                join =' ;;
    S1402) # the MARGIN's direction flipped
        echo 'window.c@@    return l < r || (l == r \&\& wf_ties[T_MARGIN].to == TIE_RESEED);@@    return l > r || (l == r \&\& wf_ties[T_MARGIN].to == TIE_RESEED);' ;;
    S1403) # a tie flipped: A-mass at a set position to the HIGHER offset
        echo 'window.c@@    [T_MASS_SET]     = { "A-mass at a set position", TIE_LOWER,@@    [T_MASS_SET]     = { "A-mass at a set position", TIE_HIGHER,' ;;
    S1404) # a core position read as outside the core: the plan's LAST tested position
        # (the hoisted bound's upper end; a core position inside the bound is
        # tested by the bound, so a per-position plant there is equivalent)
        echo 'window.c@@        w->core[i] = (uint8_t)rd_core(d, p);@@        w->core[i] = (uint8_t)(rd_core(d, p) \&\& i + 1 < n);' ;;
    S1405) # an empty meet inside a core not sent to the floor row
        # (re-anchored at span_pick 1d's cands, the one candidate builder: A-empty's fact is set there)
        echo 'window.c@@        m->any_empty |= p->core \&\& !count(p->set);@@        m->any_empty |= 0;' ;;
    S1406) # C-pin splitting the stretch: the pinned positions not one compare
        echo 'window.c@@                join = in_pinned(d, o) \&\& in_pinned(d, o - 1);@@                join = 0;' ;;
    S1407) # an untested offset claimed: the class proves one past each tested position
        echo 'window.c@@        for (unsigned x = 0; x < 32; x++) out->proven[d - MF_PROOF_LO][x] \&= w->set[i][x];@@        for (unsigned x = 0; x < 32; x++) out->proven[d - MF_PROOF_LO][x] \&= w->set[i][x];\n        if (d + 1 < MF_MAX_FWD) for (unsigned x = 0; x < 32; x++) out->proven[d + 1 - MF_PROOF_LO][x] \&= w->set[i][x];' ;;
    S1409) # two spans of R's shape in one alternative not refused (the F-8 ruling: R is unique)
        echo 'window.c@@        if (nrun > 1)\n            return "an alternative states two spans@@        if (0)\n            return "an alternative states two spans' ;;
    S1422) # D172 S3: E-find denied but rendering (`--memfn=no-window-search` ignored): the
        # control's REPORT site renders where it must be refused (window_site.md §5.2)
        # (re-anchored at code review r1 C17: E-find's id is spelled once, WF_FIND_ID)
        echo 'window.c@@    [E_FIND]    = { e_find_holds,    \&wf_find_ct,  WF_FIND_ID },@@    [E_FIND]    = { e_find_holds,    \&wf_find_ct,  NULL },' ;;
    S1423) # D172 S3: D-hors's bound one short (job 581's own plant: `c + K > n` read
        # as `c + K - 1 > n`): the probe and the verify read s[n] (re-aimed at code review
        # r2 R2-7: the bound moved, verbatim but for its indent and `b`, into d_hors_head;
        # re-aimed at the S3 final review's HOUSE-7: d_hors_head writes the shared bound)
        echo 'window.c@@    int ih = plan_ix(w, w->hl);\n    kb_printf(b, "if (!(%s)) break; ", bound);@@    int ih = plan_ix(w, w->hl);\n    kb_printf(b, "if (%s + %d > %s) break; ", rc->C, w->chi, rc->N);' ;;
    # code review r1 C13 (S1424 was the S3 review's fix C plant, withdrawn with it: not reused)
    S1425) # code review r1 C13: D-hors's shift VALUE one too far (sh[b] + 1): a candidate
        # the window's last byte admits is skipped
        echo 'window.c@@        sh[b] = (uint8_t)t;@@        sh[b] = (uint8_t)(t + 1);' ;;
    S1426) # code review r1 C13: C-run's mask word dropped: a cube stretch compared as its
        # lower bytes (an exact compare), so a candidate holding an upper member fails
        # (re-aimed at code review r2 R2-7: the term building moved into build_runs)
        echo 'window.c@@        t->mask = exact ? NULL : mask;@@        t->mask = NULL;' ;;
    S1427) # code review r1 C13: the walk's set short one entry (B-walk tests the stop's set
        # less its highest member, a set of two or more), so a candidate whose stop byte is
        # that member is walked past
        echo 'window.c@@    if (wf_member(rc, b, (unsigned)rc->w->stop_ix)) return -1;@@    { uint8_t t[32]; memcpy(t, rc->w->set[rc->w->stop_ix], 32); for (unsigned x = 256; x-- > 0 \&\& count(t) > 1;) if (in_set(t, x)) { t[x >> 3] \&= (uint8_t)~(1u << (x \& 7)); break; } kb by; kb_init(\&by, rc->art->a); kb_printf(\&by, "%s[%s]", rc->S, p); kit_set_test(b, t, by.p); }' ;;
    S1428) # code review r1 C13: Table B's PAIR in the loop (B-pair) with one stream dropped:
        # both streams search the stop's first byte (re-aimed at code review r2 R2-6: B-pair's
        # members, handed to the shared renderer)
        echo 'window.c@@    two(w->set[w->stop_ix], m);@@    two(w->set[w->stop_ix], m); m[1] = m[0];' ;;
    S1429) # code review r1 C13: PAIR through the offset-skip function (B-fn; fn-pair's body,
        # the native sites' too) with its second stream searching the first member
        # (re-aimed at code review r2 R2-6: fn-pair's members, handed to the shared renderer)
        echo 'ofsskip.c@@    const int m[2] = { a, b };@@    const int m[2] = { a, a };' ;;
    S1540) # code review r2 R2-6: THE SHARED two-stream renderer (ofs_pair_text) searches its
        # first byte in both streams: B-pair and fn-pair (B-fn, native) both lose a byte
        # (re-aimed at the S3 final review's EMIT-1: the renderer's members, at its entry)
        echo 'ofsskip.c@@void ofs_pair_text(kb *o, const ofs_pair *t, const int m[2], int k)\n{@@void ofs_pair_text(kb *o, const ofs_pair *t, const int m2[2], int k)\n{\n    const int m[2] = { m2[0], m2[0] };' ;;
    S1541) # the S3 final review's EMIT-1: a stream's bounded look-ahead that comes up empty
        # sets its frontier one PAST its end, so a byte sitting exactly there is skipped
        # (the long subjects' clusters straddle the first two look-aheads' ends)
        echo 'ofsskip.c@@} else { %s = %s; %s += %s; }%s"@@} else { %s = %s + 1; %s += %s; }%s"' ;;
    S1542) # the S3 final review's CHECK-2: D-hors's `whi >= 0` scope dropped, so D-hors
        # renders a window wholly below the candidate (the below-window sites; the
        # generator's D-hors scope census goes red). Re-aimed at span_pick 1e (lane
        # sp1e): D-hors's predicate left window.c's Table D for finder.c's hors_facts
        echo 'finder.c@@    if (!st->hw || st->whi - st->wlo < 1 || st->whi < 0) return;@@    if (!st->hw || st->whi - st->wlo < 1) return;' ;;
    S1543) # the S3 final review's EMIT-3: E-find's RAISE dropped (no expression floor):
        # with the test's lower half hoisted into it, a core position below the
        # candidate is read below the subject (layout L's guard page)
        echo 'window.c@@    } else {\n        kb_printf(b, "if (%s < %d) %s = %d; ", rc->C, -w->clo, rc->C, -w->clo);\n    }@@    } else {\n    }' ;;
    S1410) # a full-set position tested: C-bound-yes keeps a verify-YES position whose meet is every byte
        # (the kit manager's wsc3 ruling 1: such a position is the bound alone)
        # (re-anchored at span_pick 1d, which made C-bound an applied step: bound_by; the
        # plant drops the verify-YES case, C-bound-floor still drops its own)
        echo 'window.c@@        if (full(yes ? p->yset : rd_set(d, p))) plan_drop(d, d->poff[i]);@@        if (!yes \&\& full(rd_set(d, p))) plan_drop(d, d->poff[i]);' ;;
    S1549) # the sp1e review's F1: D-hors's `core` contract the opposite (CM(NOCORE)), the
        # contract fd_find's gate_in now reaches (it states the window family's facts): D-hors
        # refuses every E-find stop, whose core the alternative states, so no site resumes by
        # the shift table (the generator's hors census goes red)
        echo 'finder.c@@        MF_ANY, CM(CORED))@@        MF_ANY, CM(NOCORE))' ;;
    S3089) # plan_frame.md 3.0b (X): the reply writes MASK for one frame (E-generic): G2's
        # impossible-cell assertion (MASK 0 anywhere) is red, so the tally reads the field
        echo 'window.c@@    out->stream = fp->stream;@@    out->stream = fp->erow == E_GENERIC ? MF_WSTREAM_MASK : fp->stream;' ;;
    S3090) # 3.0b (Y): E-find's method reported R7w for a PAIR pick: the ids resolve, the bytes
        # are SAME, and G2's class (method's row picks WALK, the text's two memchr frontiers) is red
        echo 'window.c@@        if (r == E_FIND) fp->method = fx->brow;@@        if (r == E_FIND) fp->method = fx->pick == FF_PAIR ? "R7w" : fx->brow;' ;;
    S3091) # 3.0b (Z): fused left NO on B-fn: G2's class (the text calls _ofsskip) is red
        echo 'window.c@@        fp->fused = MF_WFUSED_FN;\n        fp->search = wsearch_of(fx->fused->search);@@        fp->fused = MF_WFUSED_NO;\n        fp->search = wsearch_of(fx->fused->search);' ;;
    S3092) # 3.0b (AA): frame_row swapped E-find <-> E-generic on REPORT sites: G2's form class is red
        echo 'window.c@@            reply_frame(fp, out);@@            reply_frame(fp, out);\n            if (site->site_kind == MF_SK_REPORT \&\& (r == E_FIND || r == E_GENERIC)) snprintf(out->frame_row, sizeof out->frame_row, "%s", r == E_FIND ? "E-generic" : "E-find");' ;;
    S3093) # 3.0b (AB): plan_test always OWN: G2's table_name population (the hook's own marker
        # g2w_t<id>_<ref>[ matched by offset) is red
        echo 'window.c@@            if (w->off[k] == d->poff[i]) fp->plan_test[i] = test_of(w, k);@@            if (w->off[k] == d->poff[i]) fp->plan_test[i] = MF_WTEST_OWN;' ;;
    S3096) # 3.0b (AF): stop_test always OWN while plan_test is right: red on G2's B-walk sites
        # whose stop alone is offered (the counted af_walk population). Re-aimed (lane d27fix):
        # the stop's kind is C-table's alone, written out, no longer test_of's
        echo 'window.c@@        fp->stop_test = w->table[w->stop_ix] ? MF_WTEST_TABLE : MF_WTEST_OWN;@@        fp->stop_test = MF_WTEST_OWN;' ;;
    S3084) # 3.0b (J): a reply's method filled from search's spelling: the id-resolution check
        # (method names a FIND row whose pick is search) is red
        echo 'window.c@@    snprintf(out->method, sizeof out->method, "%s", fp->method ? fp->method : "");@@    snprintf(out->method, sizeof out->method, "%s", fp->method \&\& *fp->method ? (const char *[]){ "", "LIBC", "LIBC_BACK", "WALK", "PAIR", "HORS" }[fp->search] : "");' ;;
    S2987) # plan_frame.md 3.0a (L): S-restart's text resumes C += 2, so E-find (every non-HORS,
        # non-B-fn site: B-fn is fused, its function's own loop) and the floor (it reads its
        # stream row) skip candidates; the plant is the shared text, so both S-restart rows carry it
        echo 'window.c@@    kb_printf(b, "%s++", rc->C);@@    kb_printf(b, "%s += 2", rc->C);' ;;
    S2989) # plan_frame.md 3.0a (N): E-generic's S-restart stream renderer row deleted (keys
        # none; E-find's row stays): the floor has no stream and every floor site is refused
        echo 'window.c@@{ { E_GENERIC, WF_ST_RESTART, "S-restart", NULL }@@{ { E_GENERIC, 0, "S-restart", NULL }' ;;
    S2991) # plan_frame.md 3.0a (P): B-pair's loop-state slot emptied: the frontiers are
        # undeclared, so every B-pair site's text fails to compile (the pair census)
        echo 'window.c@@    ofs_pair_decl(b, \&t);@@    (void)t;' ;;
    S2986) # plan_frame.md 3.0a (K): the support table's SHIFT cell for HORS removed: Table S
        # answers ST-none for HORS on E-find, the renderable set drops it and T-FIND never
        # picks it (the hors census falls below its floor; no dense window gets a D-hors table)
        echo 'window.c@@    { "HORS",      FF_HORS,      WF_ST_SHIFT,@@    { "HORS",      FF_HORS,      0,' ;;
    S3040) # R-38 K38-2 PLAN (e) (EMIT-3 of code review 2026-11-10 r2 k382a): the in-run stop
        # OVERRIDES a set candidate: where R has one, it is the stop, so a set position cheaper
        # than every position of R loses (the in-run sites' `set` witnesses)
        echo 'window.c@@    m->has_stop = 1;\n    m->stop = best.key;\n}\n\nstatic int a_floor_holds@@    m->has_stop = 1;\n    m->stop = rs != INT32_MIN ? rs : best.key;\n}\n\nstatic int a_floor_holds' ;;
    S3041) # R-38 K38-2 PLAN (e): the in-run order reads R's OWN stated sets, not the meet C-meet
        # left at each offset, so a position a set span narrows is not R's stop (the in-run
        # sites' `meet` witnesses)
        echo 'window.c@@        const wf_pos *p0 = \&m->p[r->start - WF_LO];\n        kit_run_reply rr = KIT_RUN_NONE;@@        const wf_pos *p00 = \&m->p[r->start - WF_LO];\n        static wf_pos pl[MF_WSPAN_POS];\n        for (unsigned j = 0; j < r->len; j++) { pl[j] = p00[j]; memcpy(pl[j].set, r->set[j], 32); }\n        const wf_pos *p0 = pl;\n        kit_run_reply rr = KIT_RUN_NONE;' ;;
    *) return 1 ;;
    esac
}
PLANTS="S1400 S1401 S1402 S1403 S1404 S1405 S1406 S1407 S1409 S1410 S1422 S1423 S1425 S1426 S1427 S1428 S1429 S1540 S1541 S1542 S1543 S1549 S2986 S2987 S2989 S2991 S3040 S3041 S3084 S3089 S3090 S3091 S3092 S3093 S3096"

fail_setup() { echo "FAIL: $1"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }

# kit_objs SRCDIR OUTDIR: every kit source compiled into OUTDIR.
kit_objs() {
    local src="$1" out="$2"
    mkdir -p "$out"
    for s in "$src"/*.c; do
        "$CC" -std=gnu11 -O1 ${G2W_TRACE:+-DMF_TRACE} -I"$ROOT/memfn/include" \
            -c -o "$out/$(basename "${s%.c}").o" "$s" || return 1
    done
}

# one_run TAG KIT...: generate against KIT (an archive or objects), build the
# driver plain (and ASan+UBSan unless G2W_NOASAN), run. Logs in $WORK/TAG.*.
one_run() {
    local tag="$1"; shift
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$ROOT/memfn/include" -I"$G2" \
        "$G2/g2_win_gen.c" "$G2/g2_win_ref.c" "$@" -o "$WORK/$tag.gen" 2> "$WORK/$tag.genbuild" \
        || { echo "FAIL: $tag: the generator does not build"; head -20 "$WORK/$tag.genbuild"; return 1; }
    mkdir -p "$WORK/$tag.out"
    "$TIMEOUT_BIN" 600 "$WORK/$tag.gen" "$SEED" "$NSITES" "$WORK/$tag.out" > "$WORK/$tag.gen.log" 2>&1
    local rc1=$?
    # the kit's text compiles warning-free (the artifacts' -Wall -Wextra -Werror)
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$G2" "$G2/g2_win_run.c" "$G2/g2_win_ref.c" \
        "$WORK/$tag.out/g2w_sites.c" -o "$WORK/$tag.run" 2> "$WORK/$tag.runbuild" \
        || { echo "FAIL: $tag: the generated family does not compile warning-free"; head -20 "$WORK/$tag.runbuild"; return 1; }
    "$TIMEOUT_BIN" 900 "$WORK/$tag.run" > "$WORK/$tag.run.log" 2>&1
    local rc2=$?
    local rc3=0
    if [ -z "${G2W_NOASAN:-}" ]; then
        "$CC" -std=gnu11 -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all \
            -I"$G2" "$G2/g2_win_run.c" "$G2/g2_win_ref.c" "$WORK/$tag.out/g2w_sites.c" \
            -o "$WORK/$tag.asan" 2> "$WORK/$tag.asanbuild" \
            || { echo "FAIL: $tag: the ASan+UBSan driver does not build"; return 1; }
        ASAN_OPTIONS=detect_leaks=0:handle_segv=0 "$TIMEOUT_BIN" 1800 "$WORK/$tag.asan" \
            > "$WORK/$tag.asan.log" 2>&1
        rc3=$?
    fi
    return $(( rc1 || rc2 || rc3 ))
}

counts() {   # counts LOG: "P F" from its checks lines
    local p f
    p=$(grep -m1 '^checks passed:' "$1" | grep -oE '[0-9]+')
    f=$(grep -m1 '^checks failed:' "$1" | grep -oE '[0-9]+')
    echo "${p:-x} ${f:-x}"
}

if [ "${1:-}" = "--plant" ] || [ "${1:-}" = "--plants" ]; then
    ids="${2:-}"
    [ "$1" = "--plants" ] && ids="$PLANTS"
    [ -n "$ids" ] || fail_setup "--plant needs an id ($PLANTS)"
    export G2W_NOASAN=1
    bad=0
    for id in $ids; do
        spec="$(plant_spec "$id")" || fail_setup "no plant $id"
        file="${spec%%@@*}"; rest="${spec#*@@}"; from="${rest%%@@*}"; to="${rest#*@@}"
        rm -rf "$WORK/src"; cp -r "$ROOT/memfn/src" "$WORK/src"
        python3 -I - "$WORK/src/$file" "$from" "$to" <<'EOF' || fail_setup "$id: the plant does not apply"
import sys
p, a, b = sys.argv[1], sys.argv[2].replace('\\n', '\n'), sys.argv[3].replace('\\n', '\n')
a = a.replace('\\&', '&'); b = b.replace('\\&', '&')
s = open(p).read()
if s.count(a) != 1:
    sys.exit("plant text found %d times" % s.count(a))
open(p, 'w').write(s.replace(a, b))
EOF
        kit_objs "$WORK/src" "$WORK/pk_$id" || fail_setup "$id: the planted kit does not compile"
        # a planted kit whose text no longer compiles warning-free is red too
        # (one_run says so on its own output; D172 S3: E-find declares F only
        # where its text reads it, so S1400's dropped read is a compile error)
        built=$(one_run "plant_$id" "$WORK/pk_$id"/*.o | grep -m1 '^FAIL')
        c="$(counts "$WORK/plant_$id.run.log" 2>/dev/null)"
        red=$(grep -h '^FAIL' "$WORK/plant_$id.gen.log" "$WORK/plant_$id.run.log" 2>/dev/null | head -1)
        [ -n "$red" ] || red="$built"
        if [ -n "$red" ]; then
            echo "PLANT $id RED   (driver passed failed: $c): $red"
        else
            echo "PLANT $id GREEN (NOT DETECTED; $c)"; bad=$((bad + 1))
        fi
    done
    [ "$bad" -eq 0 ]
    exit $?
fi

[ -f "$LIB" ] || fail_setup "$LIB not built (make all first)"
tp=0 tf=0
note() { tf=$((tf + 1)); echo "FAIL: $1"; }
one_run plain "$LIB"
grep -h '^FAIL' "$WORK/plain.gen.log" | head -20
grep -h '^g2_win_gen' "$WORK/plain.gen.log"
read -r p f < <(counts "$WORK/plain.run.log")
if [ "$p" = x ] || [ "$f" = x ]; then note "the driver printed no counts"; else tp=$((tp + p)); tf=$((tf + f)); fi
grep -h '^FAIL\|^G2W' "$WORK/plain.run.log" | head -40
gf=$(grep -h '^g2_win_gen failures:' "$WORK/plain.gen.log" | grep -oE '[0-9]+$')
if [ "${gf:-x}" != 0 ]; then note "the generator failed ${gf:-?} sites"; else tp=$((tp + 1)); fi
if [ -z "${G2W_NOASAN:-}" ]; then
    read -r p f < <(counts "$WORK/plain.asan.log")
    if [ "$p" = x ] || [ "$f" = x ]; then
        note "the ASan+UBSan driver printed no counts ($(grep -m1 'ERROR\|runtime error' "$WORK/plain.asan.log"))"
    else
        echo "ASan+UBSan driver: passed $p failed $f"
        tp=$((tp + p)); tf=$((tf + f))
        grep -h '^FAIL' "$WORK/plain.asan.log" | head -10
    fi
fi

# --- W1: the reference's planted defects must turn the driver red ----------
for k in 2 3 4 5; do
    "$TIMEOUT_BIN" 900 "$WORK/plain.run" --ref-defect "$k" > "$WORK/w1_$k.log" 2>&1
    if grep -q '^FAIL' "$WORK/w1_$k.log"; then
        tp=$((tp + 1)); echo "W1 ref-defect $k: red (as it must be)"
    else
        note "W1 ref-defect $k went undetected"
    fi
done

# --- the floors (K35) --------------------------------------------------------
val() { grep -h "^G2W $1" "$WORK/plain.run.log" | grep -oE "$2=[0-9]+" | head -1 | cut -d= -f2; }
floor() {   # floor LABEL GOT WANT
    if [ "${2:-0}" -ge "$3" ]; then tp=$((tp + 1)); else note "floor $1: ${2:-0} < $3"; fi
}
sites=$(grep -h '^G2W sites' "$WORK/plain.run.log" | awk '{print $3}')
floor sites "${sites:-0}" "$FLOOR_SITES"
ctl=$(grep -h '^g2_win_gen:' "$WORK/plain.gen.log" | grep -oE 'controls refused [0-9]+' | grep -oE '[0-9]+$')
floor controls "${ctl:-0}" "$FLOOR_CONTROLS"
qry=$(grep -h '^g2_win_gen:' "$WORK/plain.gen.log" | grep -oE 'queries agreeing [0-9]+' | grep -oE '[0-9]+$')
floor queries "${qry:-0}" "$FLOOR_QUERIES"
two=$(grep -h '^g2_win_gen:' "$WORK/plain.gen.log" | grep -oE 'two runs refused [0-9]+' | grep -oE '[0-9]+$')
floor two_runs "${two:-0}" "$FLOOR_TWO_RUNS"
floor calls "$(grep -h '^G2W sites' "$WORK/plain.run.log" | awk '{print $5}')" "$FLOOR_CALLS"
floor hits "$(grep -h '^G2W sites' "$WORK/plain.run.log" | awk '{print $7}')" "$FLOOR_HITS"
for pf in $PATH_FLOORS; do floor "path ${pf%%:*}" "$(val paths "${pf%%:*}")" "${pf#*:}"; done
floor pinned "$(val paths pinned)" "$FLOOR_PINNED"
floor reseed_bit "$(val paths reseed_bit)" "$FLOOR_RESEED_BIT"
for mf in $MARGIN_FLOORS; do floor "margin ${mf%%:*}" "$(val margin "${mf%%:*}")" "${mf#*:}"; done
for tf_ in $TIE_FLOORS; do floor "tie ${tf_%%:*}" "$(val ties "${tf_%%:*}")" "${tf_#*:}"; done
for cf in $CELL_FLOORS; do floor "cell ${cf%%:*}" "$(val cells "${cf%%:*}")" "${cf#*:}"; done
for ff in $FORM_FLOORS; do floor "form ${ff%%:*}" "$(val forms "${ff%%:*}")" "${ff#*:}"; done
efv() { grep -h '^g2_win_gen: e-find' "$WORK/plain.gen.log" | grep -oE "$1 [0-9]+" | head -1 | grep -oE '[0-9]+$'; }
for ef in $EFIND_FLOORS; do floor "e-find ${ef%%:*}" "$(efv "${ef%%:*}")" "${ef#*:}"; done
floor "long pair" "$(val long pair)" "$FLOOR_LONG_PAIR"
fcv() { grep -h "^g2_win_gen: $1" "$WORK/plain.gen.log" | grep -oE " $2 [0-9]+" | head -1 | grep -oE '[0-9]+$'; }
for cf in $FRAME_CELL_FLOORS; do floor "frame cell ${cf%%:*}" "$(fcv cells "${cf%%:*}")" "${cf#*:}"; done
for cf in $FRAME_CLASS_FLOORS; do floor "frame class ${cf%%:*}" "$(fcv classes "${cf%%:*}")" "${cf#*:}"; done
if [ -n "${G2W_TRACE:-}" ]; then
    for tr in $TRACED_FLOORS; do
        floor "traced defines ${tr%%:*}" "$(grep -cE "^MFTRACE END table=wfE art=[0-9]+ site=[0-9]+ phase=define chosen=${tr%%:*} " "$WORK/plain.gen.log")" "${tr#*:}"
    done
fi
for inf in $INRUN_FLOORS; do floor "inrun ${inf%%:*}" "$(val inrun "${inf%%:*}")" "${inf#*:}"; done

echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
