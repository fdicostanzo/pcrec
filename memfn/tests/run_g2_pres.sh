#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's presence family,
#   lane k382a, R-38 K38-2a; moved to the seam event's form at R-38 K38-2,
#   lane k382).
#
# memfn/tests/run_g2_pres.sh — G2'S PRESENCE FAMILY (docs/design/memfn/
# span_runs_sheet.md rev 1.3 §5's K38-2a and K38-2 rows; §2.1-§2.4 C2, §3.3,
# §3.5 W-L1, W-K1..W-K4b).
# run_g2.sh's section 4p; runnable alone (~1-2 min, one process at a time).
#
#   1. g2/g2_pres_gen.c against the kit (LIB, default build/libpcrec.a):
#      GENERATED pre-check sites in the seam event's statement form
#      (MF_SITE_ABI 27: the run one presence span in SET form, its omin of
#      either sign, K signed; ONE run part the kit derives) on the
#      P0/P2/P3/P9 routes, laid out as a host lays them out, the run's
#      scan and verified extent read off the REPLY (mf_class.run, FAM-2),
#      defined, their entry and re-entry uses rendered; W-K3 (the twin's
#      admission bit at K < 0 equals K 0's) on every site; ONE PASS
#      PER TARGET of the U2 list (x86-64-v3, x86-64, generic: every admitted
#      level, both layers) and per lever state (default; run-tie-left);
#   2. the text compiles -Wall -Wextra -Werror;
#   3. g2/g2_pres_run.c over it, built twice: the RECORDING build (the kit's
#      text -fsanitize=kernel-address with every access an outlined call, so
#      the driver sees each read) runs the §3.5 witnesses (W-L1 a/b, W-K1,
#      W-K2), the classifier (C2), the lever witnesses, layouts U and L
#      (W-K4a), and writes the ORACLE RECORDS (docs/dev/lanes/
#      k382a_oracle_iface.md; run frame and the site's reply, ORC-3); the
#      ASan+UBSan build runs the witnesses, the classifier, layouts U and L
#      and layout A (W-K4b);
#   4. THE ORACLE STEP: the records piped to tests/memfn/occurrence_oracle.py;
#      the oracle file absent is a FAIL (`ORACLE OWED`, the records written,
#      NOT checked: review 2026-11-10 r2 k382a ORC-2; the oracle landed with
#      41ebc052b, and it is the family's only check of "least");
#   5. the lever's reach: every witness's text scan MOVED between the
#      default and the run-tie-left pass of the same target;
#   5g. THE GENERIC PASS (review 2026-11-11 r1 k382 F1): the same sites with
#      `on_miss_leaves` 0 (target generic, default lever), so no pre-check
#      row admits them and the GENERIC row renders every one (its run part
#      inline: no function for the classifier); its checks are the uses'
#      PRESENCE rule (every pass runs it; g2_pres_run.c pres_check) and the
#      §3.5 witnesses, both read off the stated rule, not the row;
#   6. the floors (K35): literals below, sharing no source with the family;
#   7. (R-38 K38-3) THE PER-LEVEL CELLS: per (level, layout U/L/A), the use
#      calls that ENTER the level's arm, floored where the pass's target
#      admits the level and exactly 0 where it does not (the kit's level
#      list and admission, read through tests/memfn/simd_levels.c and
#      target_text.py), and the level-list coverage (every kit level run by
#      a pass target on this host).
#
#   --plant ID / --plants   the same passes over a COPY of memfn/src with one
#                           planted defect (the table below); no ASan, except
#                           a plant plant_asan names (its asan.log is read).
#   --reach                 the mech rows' witness probe: renders the default
#                           and lever generic passes and prints one REACH
#                           token per plant site the text reaches.
#
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR, G2P_SITES, G2P_SEED,
# G2P_NOASAN (skip the ASan build), G2P_SKIP_ARMS (targets to skip, by name),
# G2P_KEEP (keep the work directory; its path is printed).
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
. "$ROOT/tests/lib/timeout_bin.sh"
LIB="${LIB:-$ROOT/build/libpcrec.a}"
G2="$ROOT/memfn/tests/g2"
NSITES="${G2P_SITES:-400}"
SEED="${G2P_SEED:-20261110}"
WORK="$(mktemp -d "${TMPDIR:-/var/tmp}/g2pres.XXXXXX")"
if [ -n "${G2P_KEEP:-}" ]; then echo "work directory: $WORK"; else trap 'rm -rf "$WORK"' EXIT; fi
TARGETS="x86-64-v3 x86-64 generic"
ORACLE="$ROOT/tests/memfn/occurrence_oracle.py"
RECFLAGS="-fsanitize=kernel-address --param asan-instrumentation-with-call-threshold=0 --param asan-stack=0 --param asan-globals=0"

# --- the floors (K35): hand-written literals, sharing no source with the
# family. PER PASS (each target, each lever state). Raise them when the space
# grows; never lower one to make a run pass.
# RE-MEASURED 2026-11-11 by lane k382 (R-38 K38-2) on the Linux dev box, seed
# 20261110, 400 sites + 24 lever witnesses + 4 §3.5 witness sites per pass;
# the least over the six passes in parentheses, less ~10%. The space changed
# FORM at K38-2 (one derived run part per site instead of the window and the
# whole run, half the runs a negative omin), so every literal below is this
# space's own measure, EXCEPT: (1) NEARMISS fell below K38-2a's floor with
# the retired second part (K38-2a 28540 over 31712 probes; now 28450 probes),
# so it and COVER/EXTENT are set to the MEASURED count with NO margin (kit
# manager's ruling, 2026-11-11); (2) no floor is below K38-2a's where K38-2a's
# still holds (P2 sites, P2_REFUSED, NM_SOUND keep K38-2a's literals).
# RE-PIN PROCEDURE (review 2026-11-11 r1 k382 F17): the seed is fixed, so a
# legitimate change to the space can shrink a count by one probe and red a
# no-margin floor. Lowering a floor is then a RE-PIN, never a fix: (a) name
# the change that moved the space and show the new count is that change's
# (the passes' own count lines, before and after); (b) get the kit
# manager's ruling; (c) record it here as a dated RE-MEASURED/RE-PINNED line
# naming the ruling, the old and new literal and the count. A floor lowered
# without (a)-(c) is a check made to pass. The 2026-11-11 F16 witness
# W-K1b (5 §3.5 witness sites per pass since) moved no floor; F14's
# controls (CTL_NOPART/CTL_TWO) are set like GENERIC (the least, less ~10%).
FLOOR_ROUTE_SITES="P0:86 P2:70 P3:159 P9:72"   # the generator's routes (96 75 177 80; P2 K38-2a's 70)
FLOOR_P2_REFUSED=70         # P2's control: the derived part on an untested link refused (75; K38-2a's 70)
FLOOR_REACH="P0:2190 P3:4010 P9:1820"          # run-part calls per route, entry + re-entry (2441 4460 2028)
FLOOR_REACH_RE="P0:850 P3:1520 P9:730"       # of them re-entry calls (947 1697 816)
FLOOR_SCAN_SITES="P0:86 P3:159 P9:72"        # sites whose text scan was read (96 177 80)
FLOOR_COVER=13992              # COVER probes, measured, no margin (13992)
FLOOR_EXTENT=6944            # EXTENT probes, measured, no margin (6944)
FLOOR_RECORDS=8030          # oracle records (8932)
FLOOR_NEARMISS=28450        # EXTENT's per-bit near-miss probes, FAM-3, measured, no margin (28450)
FLOOR_NM_SOUND=3440         # near-miss occurrences in SOUND's subjects (3611; K38-2a's 3440)
FLOOR_NM_USES=4250           # near-miss occurrences in the uses' subjects (4729)
FLOOR_LAYOUT_A=14610            # layout A placements, ASan build (16238 = 353 sites x 46)
FLOOR_WITNESSES=24              # lever witnesses, every one rendered (24)
# K38-2's populations (span_runs_sheet.md §3, §5 K38-2 PLAN (d)):
FLOOR_NEG_OMIN=153         # rendered sites whose run omin < 0 (171)
FLOOR_WK4_OMIN=117         # of them omin in -8..-32, W-K4a's range (130)
FLOOR_WK4_LOW=1550           # layout L calls on those with the origin below -omin (1727)
FLOOR_K_SIGNED=106         # ASSIGN sites stating K with omin < 0 (118)
FLOOR_K_NONPOS=64          # of them K <= 0 (72)
FLOOR_PARTIAL=65           # sites whose reply's extent is partial (73)
FLOOR_PARTIAL_HITS=539       # ORC-3: records hitting with a PARTIAL extent; 0 was right at K38-2a (599)
FLOOR_NEG_RECORDS=4090       # records with a negative omin (4547)
FLOOR_BELOW_HITS=1330        # hits below the attempt start, only a negative omin yields one (1480)
FLOOR_ROOM=24                # sites the C2 decision plant reaches: the extent ends before the run (27)
FLOOR_WK3_CASES=10160           # W-K3 checks: a K in -32..-1 on a site whose bit at K 0 is 1 (11296)
# THE USES' PRESENCE RULE and THE GENERIC PASS (lane k382fix, review 2026-11-11
# r1 k382 F1; measured 2026-11-11, seed 20261110, 400 sites; the least over the
# passes in parentheses, less ~10%):
FLOOR_PRES_CHECKS=5380    # uses checked by the presence rule, per pass (5977)
FLOOR_PRES_BELOW=2130     # of them the occurrence below the origin (2367)
FLOOR_GENERIC=318         # the generic pass: sites the generic row rendered (353)
FLOOR_CTL_NOPART=318      # F14 (ii): tested sites laid out with no run part, refused by its rule (353)
FLOOR_CTL_TWO=318         # F14 (iii): tested sites laid out with two derived parts, refused (353)
# THE LAYERS (D147; U2's admitted levels): per target, the sites whose run
# part has a w16 / w32 arm (the generator's census of the kit's own text), and
# the vector loads of the subject the recording build saw (the arms RAN).
# x86-64-v3 admits both levels, x86-64 w16 alone, generic (the OFF layer)
# none: a level the target does not admit must render NOTHING (exactly 0).
SIMD_FLOORS="x86-64-v3:19:19:1600 x86-64:19:0:1340 generic:0:0:0"   # (22 22 1786; 22 0 1495; 0 0)
# THE PER-LEVEL CELLS (R-38 K38-3; span_runs_sheet.md §5 K38-3 (1), [r1s1
# S1-10, S1-14, S1-15], [r2s1 RK383-1, RK383-5]): per (level, layout), the
# use calls that ENTER the level's arm (execute a load of its width W; the
# recording build's hooks, counted inside entry and re-entry calls only),
# layout U every use call, L W-K4a's population (omin -8..-32, the origin
# below -omin), A the count-only placements at W. The LEVEL LIST and which
# target admits which level are the KIT's (mf_levels/mf_targets through
# tests/memfn/simd_levels.c, admitted by tests/memfn/target_text.py's
# admitted()), never a copy here. The family rule: on a pass whose target
# admits the level, the least over those passes less ~10%, a cell at 0 a
# named failure; on a pass whose target does not admit it (and every cell of
# a generic pass, the OFF cell) EXACTLY 0. Every kit level needs a target
# the pass list runs on this host. MEASURED 2026-11-12 by lane k383 on the
# Linux dev box (main a9fc6dbd8, seed 20261110, 400 sites; the least over the
# admitting passes in parentheses):
CELL_FLOORS="w16:163:75:158 w32:100:72:455"   # level:U:L:A  (w16 181 84 176; w32 111 80 506)

# THE PLANTS: id, then one line FILE@@FROM@@TO per edit (FILE under
# memfn/src; FROM replaced by TO, `\n` a newline, `\\n` the C escape, `\&`
# an ampersand), then the detector. Ids from the top of the mech free range
# (S3005/S3006 the highest at K38-1): S3007-S3009, then S3010-S3012 (review
# 2026-11-10 r2 k382a's fixes, lane k382afix). The mech rows
# tests/mech/sabotages/S3007-S3012 plant the same text.
plant_spec() {
    case "$1" in
    S3007) # A: the run part drops one compare of its extent (the words form never
        # compares position 0): the classifier's EXTENT reds
        echo 'runcmp.c@@            int skip = proven \&\& (at + i < done || rc_proven(proven, np, at + i));@@            int skip = at + i == 0 || (proven \&\& (at + i < done || rc_proven(proven, np, at + i)));' ;;
    S3008) # B: the memchr form passes over an occurrence at its origin (a verified
        # candidate equal to the call's `lo` is skipped): the next occurrence above the
        # least is yielded (§3.3 item 2, "least"). The ORACLE's plant: the text's reads
        # are unchanged until a candidate verifies, and the classifier's probes put the
        # occurrence above `lo` (the occurrence contract is the oracle's, not a copy)
        echo 'ofsskip.c@@    int maxk = x->maxk, k = x->k, a = x->a;\n    kit_out(o, "    while (pos + %d < n) {\\n", maxk);@@    int maxk = x->maxk, k = x->k, a = x->a;\n    o->puts(o->u, "    size_t lo0 = pos;\\n");\n    kit_out(o, "    while (pos + %d < n) {\\n", maxk);'
        echo 'ofsskip.c@@    o->puts(o->u,   ") return cand;\\n");@@    o->puts(o->u,   ") { if (cand == lo0) { pos = cand + 1; continue; } return cand; }\\n");' ;;
    S3009) # C: the lever leaves the run decision's ties rightmost (kit_run_opts_of
        # ignores run-tie-left): the witnesses' text scan does not move
        echo 'presence.c@@    return (kit_run_opts){ st, left ? T_RUN_LEFT : T_MASS_STRETCH };@@    (void)left;\n    return (kit_run_opts){ st, T_MASS_STRETCH };' ;;
    S3010) # ORC-1: every use passes its run part the attempt start + 1 (the
        # position at the attempt start is never asked): the part's own call
        # is honest in its own frame, so only a record taken at the CALLER
        # boundary (the host's attempt start) sees the occurrence it skips
        echo 'ofsskip.c@@    kit_out(o, "%s(%s, %s, %s", fn, h->s, h->n, h->lo);@@    kit_out(o, "%s(%s, %s, %s + 1", fn, h->s, h->n, h->lo);' ;;
    S3011) # FAM-3: the words form's masked compare one bit looser (a mask byte of
        # more than one bit loses its lowest): a near-miss on that bit is
        # yielded as an occurrence; EXTENT's per-bit near-misses red
        echo 'runcmp.c@@            t[i] = skip ? 0x00 : r->t[at + i];@@            t[i] = skip ? 0x00 : r->t[at + i];\n            if (k[i] != 0xFF \&\& (k[i] \& (k[i] - 1))) { k[i] \&= (uint8_t)(k[i] - 1); t[i] \&= k[i]; }' ;;
    S3012) # FAM-5: a_mass_choose's in-run filter deleted (the in-run stop no longer
        # the run decision's): the lever pass's layouts are refused by
        # mf_define (decider_census D cannot see it: it counts the call)
        echo 'window.c@@        if (r \&\& p->stretch \&\& o >= r->start \&\& o < r->start + r->len \&\& o != rs)\n            continue;                   /* inside R: the run decision'"'"'s one */@@        (void)o; (void)rs;' ;;
    # R-38 K38-2 (lane k382; ids from the lane's range S3040-S3069): the
    # §3.5 witnesses' plants, and C2's decision plant (§2.4)
    S3060) # W-L1: the CANDIDATE floor is the origin `lo`, not max(0, lo + omin)
        echo 'presence.c@@    if (omin >= 0) return lo;@@    return lo;' ;;
    S3061) # W-K1: the floor spelled `lo + omin` in size_t, no clamp (wraps where lo < -omin)
        echo 'presence.c@@    kb_printf(\&f, "(%s >= %llu ? %s - %llu : 0)", lo, back, lo, back);@@    kb_printf(\&f, "(%s - %llu)", lo, back);' ;;
    S3062) # W-K2: the RE-ENTRY floor read from its `lo`: a use whose `lo` is not
        # the activation's origin (the define's `start` hook: a RE-ENTRY) floors
        # at lo; the entry keeps max(0, lo + omin)
        echo 'precheck.c@@    int part = 0;\n    for (uint32_t i = 0; i < s->npred; i++) {@@    { extern const char *s3062_origin; s3062_origin = h ? h->start : NULL; }\n    int part = 0;\n    for (uint32_t i = 0; i < s->npred; i++) {'
        echo 'presence.c@@const char *kit_run_floor(mf_art *art, const char *lo, const mf_site *s, const char *who)\n{\n    int run = kit_pres_run(s);\n    int32_t omin = run >= 0 ? s->pspans[run].omin : 0;\n    if (omin >= 0) return lo;@@const char *s3062_origin;\nconst char *kit_run_floor(mf_art *art, const char *lo, const mf_site *s, const char *who)\n{\n    int run = kit_pres_run(s);\n    int32_t omin = run >= 0 ? s->pspans[run].omin : 0;\n    if (omin >= 0 || (s3062_origin \&\& lo \&\& strcmp(lo, s3062_origin))) return lo;' ;;
    S3063) # W-K3: the twin admission reads K unsigned (a negative K a huge step back)
        echo 'presence.c@@        unsigned long long k = s->head_max > 0 ? (unsigned long long)s->head_max : 0;@@        unsigned long long k = (unsigned long long)s->head_max;' ;;
    # lane k382fix (review 2026-11-11 r1 k382; ids S3043-S3059 of k382's range)
    S3043) # F1: the GENERIC row's run part starts at the attempt start `lo`, not
        # the run's floor max(0, lo + omin): the generic pass's PRESENCE rule and
        # its §3.5 witnesses red
        echo 'generic.c@@            const char *from = s->preds[i].fn_ref ? kit_run_floor(rc->art, rc->LO, s, "generic")\n                                                  : rc->LO;@@            const char *from = rc->LO;' ;;
    S3044) # F13: the run span's link keeps its row template's `member` (P3's 1):
        # the generator's link check reds on every P3 site
        echo 'finder.c@@        if (!member) k.member = 0;@@        (void)0;' ;;
    S3045) # F12: P3 drops out of the stretch-mode table (a renamed row): every
        # P3 site's ask is REFUSED, never handed a catch-all's stretch
        echo 'finder.c@@    { "P3", KIT_RUN_WINDOW },@@    { "P3-renamed", KIT_RUN_WINDOW },' ;;
    S3046) # F14 (ii): the statement rule's "a tested link lays out its run part"
        # refusal deleted (compose.c pres_layout_check skips the run part's slot):
        # the generator's control (ii) is no longer refused by that rule
        echo 'compose.c@@        if (k >= s->npred || !s->preds[k].fn_ref)\n            return "its run part@@        if (0 \&\& (k >= s->npred || !s->preds[k].fn_ref))\n            return "its run part' ;;
    S3047) # F14 (iii): the "one run, one part" refusal deleted (window.c
        # wf_parts_check counts derived parts but never refuses a second)
        echo 'window.c@@            if (++nderived > 1) return "a second derived run part (one run, one part)";@@            ++nderived;' ;;
    S3064) # C2's DECISION plant: the reply (mf_ask's and mf_defined's mf_class.run)
        # says ver_len + 1 while the renderer (fd_pres_run's quiet ask) renders the
        # old extent; reaches where the extent ends before the run does
        echo 'compose.c@@        return fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, \&why) ? -1 : 0;@@        if (fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, \&why)) return -1;\n        { int r_ = kit_pres_run(s); if (r_ >= 0 \&\& out->pres[r_].verify \&\& out->run.ver_len \&\& out->run.ver_lo + out->run.ver_len < kit_pres_run_span(s, r_)->len) out->run.ver_len++; }\n        return 0;'
        echo 'compose.c@@            return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);@@            return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);\n        { int r_ = kit_pres_run(s); if (r_ >= 0 \&\& r->cls.pres[r_].verify \&\& r->cls.run.ver_len \&\& r->cls.run.ver_lo + r->cls.run.ver_len < kit_pres_run_span(s, r_)->len) r->cls.run.ver_len++; }' ;;
    # R-38 K38-3 (lane k383; ids S3098-S3105, from the top of the free range
    # above S3077, 3.0b's S3078-S3097 aside). THE W-K4 PLANTS, per admitted
    # level: the arm's first load starts below the run's floor. W-K4a's
    # UNALIGNED at floor - 1 (the KA load at subject + pos - 1): a fault in
    # layout L on that level's target passes, the generic passes unchanged.
    S3098) echo 'vrun.c@@    o->puts(o->u, "    size_t i = pos;\\n"\n                  "    for (;;) {\\n"@@    if (d->level == LV_X86_W16) kit_out(o, "    size_t i = pos - %d;\\n", ka + 1);\n    else o->puts(o->u, "    size_t i = pos;\\n");\n    o->puts(o->u, "    for (;;) {\\n"' ;;
    S3099) echo 'vrun.c@@    o->puts(o->u, "    size_t i = pos;\\n"\n                  "    for (;;) {\\n"@@    if (d->level == LV_X86_W32) kit_out(o, "    size_t i = pos - %d;\\n", ka + 1);\n    else o->puts(o->u, "    size_t i = pos;\\n");\n    o->puts(o->u, "    for (;;) {\\n"' ;;
    # W-K4b's ALIGNED DOWN ([r1s1 S1-11]): the ADDRESS s + floor + KA aligned
    # down to W, so the load never leaves its page (layout L cannot see it):
    # an ASan report in layout A, where off >= 8 poisons a granule below s
    S3100) echo 'vrun.c@@    o->puts(o->u, "    size_t i = pos;\\n"\n                  "    for (;;) {\\n"@@    if (d->level == LV_X86_W16) kit_out(o, "    size_t i = pos - (size_t)((uintptr_t)(subject + pos + %d) \& %u);\\n", ka, vw - 1);\n    else o->puts(o->u, "    size_t i = pos;\\n");\n    o->puts(o->u, "    for (;;) {\\n"' ;;
    S3101) echo 'vrun.c@@    o->puts(o->u, "    size_t i = pos;\\n"\n                  "    for (;;) {\\n"@@    if (d->level == LV_X86_W32) kit_out(o, "    size_t i = pos - (size_t)((uintptr_t)(subject + pos + %d) \& %u);\\n", ka, vw - 1);\n    else o->puts(o->u, "    size_t i = pos;\\n");\n    o->puts(o->u, "    for (;;) {\\n"' ;;
    # THE CELLS' CONTROL ([r1s1 S1-10]): the w32 arm entered only when n >=
    # run_len + 2W + 24, past the generator's longest subject; the text census
    # still reads __w32( (green), the w32 entry cells read 0
    S3102) echo 'vrun.c@@    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\\n", r, fall);@@    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\\n", d->level == LV_X86_W32 ? r + vw + 25 : r, fall);' ;;
    # THE EXACT-0 RULE's control ([r2s1 RK383-5]): the kit admits w32 on
    # x86-64 (its admission rule widened, the target's region given avx2 so the
    # text compiles) while the listing's facts do not: the x86-64 w32 cells
    # read nonzero
    S3103) echo 'levels.c@@        if (admits(t, \&level_table[lv])) m |= 1u << lv;@@        if (admits(t, \&level_table[lv]) || (lv == LV_X86_W32 \&\& !strcmp(t->name, "x86-64"))) m |= 1u << lv;'
        echo 'targets.def@@MF_NEEDS("sse2"), "fxsr,mmx,sse,sse2",@@MF_NEEDS("sse2,avx2"), "fxsr,mmx,sse,sse2",' ;;
    *) return 1 ;;
    esac
}
# plant_asan ID: 0 iff the plant's detector is ASan (layout A, the ASan+UBSan
# build): its passes run WITH that build (K38-3, [r1s1 S1-11] the per-plant
# opt-in) and the plant path reads each pass's asan.log ([r2s1 RK383-2])
plant_asan() { case "$1" in S3100|S3101) return 0 ;; *) return 1 ;; esac; }
# plant_absent ID: FAIL lines that must NOT occur (grep -E): a plant on one
# level leaves the passes of targets that do not admit it exactly unchanged
plant_absent() {
    case "$1" in
    S3098|S3100) echo '(^FAIL |CELL: )generic\.' ;;
    S3099|S3101) echo '(^FAIL |CELL: )(generic|x86-64)\.' ;;
    *) echo '' ;;
    esac
}
plant_detector() { case "$1" in S3008|S3010) echo oracle ;; *) echo family ;; esac; }
# plant_expect ID: the FAIL-line patterns (each grep -E, each required, `|`
# between them NOT an alternation: split below) naming the detector the plant
# is FOR; a plant red only by something else is not detected by its witness
# (an oracle plant: the oracle step's own verdict)
plant_expect() {
    case "$1" in
    S3007|S3011|S3064) echo ': EXTENT: ' ;;
    S3009) echo ': LEVER: ' ;;
    S3012) echo 'mf_define' ;;
    S3060) echo ': W-L1: ;: W-L1b: ' ;;
    S3061) # F16: W-K1b (scan k 0 < N - origin) moves its ANSWER: on the generic
        # pass in layout U, on the precheck pass in layout L (in U the wrapped
        # floor reads 2 bytes below the subject and the whole-run verify
        # rejects them: the answer holds, the read is the defect)
        echo ': W-K1b: U \(guard at s \+ n\): the entry from 1 on "foobar" yields -1;default site [0-9]+ \(precheck\): W-K1b: L [^:]*: the entry from 1 on "foobar" yields -1' ;;
    S3062) echo ': W-K2: ' ;;
    S3063) echo 'W-K3: the admission bit' ;;
    S3046) echo 'F14 \(ii\): no run part on a tested link' ;;
    S3047) echo 'F14 \(iii\): a second derived run part' ;;
    S3044) echo "the run's link \\(mf_ask\\): .member. is not 0 on the run span" ;;
    S3045) echo 'mf_ask \(the presence links\): refused' ;;
    S3043) echo 'default\.oml0 .*: PRESENCE: ;default\.oml0 .*: W-L1: ' ;;
    S3098|S3099) echo ': LAYOUT: L \(subject at a page start, guard below\): the (entry|re-entry) faulted' ;;
    S3100|S3101) echo 'ERROR: AddressSanitizer' ;;
    S3102) echo 'CELL: x86-64-v3\.[01]: w32 U: 0 arm entries;CELL: x86-64-v3\.[01]: w32 L: 0 arm entries;CELL: x86-64-v3\.[01]: w32 A: 0 arm entries' ;;
    S3103) echo 'CELL: x86-64\.[01]: w32 U: [0-9]+ arm entries where the target admits none' ;;
    *) echo '' ;;
    esac
}
PLANTS="S3007 S3008 S3009 S3010 S3011 S3012 S3043 S3044 S3045 S3046 S3047 S3060 S3061 S3062 S3063 S3064 S3098 S3099 S3100 S3101 S3102 S3103"

fail_setup() { echo "FAIL: $1"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }

kit_objs() {   # kit_objs SRCDIR OUTDIR: every kit source compiled into OUTDIR
    local src="$1" out="$2"
    mkdir -p "$out"
    for s in "$src"/*.c; do
        "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -c -o "$out/$(basename "${s%.c}").o" "$s" \
            || return 1
    done
}

host_has() {   # host_has TARGET: 0 iff this host runs TARGET's text
    case "$1" in
    x86-64-v3) grep -qw avx2 /proc/cpuinfo 2>/dev/null && grep -qw bmi2 /proc/cpuinfo 2>/dev/null ;;
    *) return 0 ;;
    esac
}

# build_gen TAG KIT...: the generator against KIT (an archive or objects)
build_gen() {
    local tag="$1"; shift
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$ROOT/memfn/include" -I"$G2" \
        "$G2/g2_pres_gen.c" "$@" -o "$WORK/$tag.gen" 2> "$WORK/$tag.genbuild" \
        || { echo "FAIL: $tag: the generator does not build"; head -20 "$WORK/$tag.genbuild"; return 1; }
}

# one_pass TAG TARGET LEVER [ON_MISS_LEAVES]: render, compile, run (recording; ASan unless
# G2P_NOASAN). Logs in $WORK/TAG.*; records in $WORK/TAG.rec.tsv.
one_pass() {
    local tag="$1" tgt="$2" lev="$3" o="$WORK/$1.out"
    mkdir -p "$o"
    # shellcheck disable=SC2086
    "$TIMEOUT_BIN" 300 "$WORK/$tag.gen" "$SEED" "$NSITES" "$o" "$tgt" "$lev" ${4:-} > "$WORK/$tag.gen.log" 2>&1
    local rc=$?
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$G2" -c "$o/g2p_sites.c" -o "$WORK/$tag.plain.o" \
        2> "$WORK/$tag.plainbuild" \
        || { echo "FAIL: $tag: the kit's text does not compile warning-free"; head -20 "$WORK/$tag.plainbuild"; return 1; }
    # shellcheck disable=SC2086
    "$CC" -std=gnu11 -O2 $RECFLAGS -DG2P_REC -I"$G2" -c "$o/g2p_sites.c" -o "$WORK/$tag.rec.o" \
        2> "$WORK/$tag.recbuild" \
        && "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -DG2P_REC -I"$G2" "$G2/g2_pres_run.c" \
            "$WORK/$tag.rec.o" -o "$WORK/$tag.rec" 2>> "$WORK/$tag.recbuild" \
        || { echo "FAIL: $tag: the recording build fails"; head -20 "$WORK/$tag.recbuild"; return 1; }
    "$TIMEOUT_BIN" 600 "$WORK/$tag.rec" --records "$WORK/$tag.rec.tsv" --seed "$SEED" \
        > "$WORK/$tag.run.log" 2>&1
    rc=$((rc || $?))
    if [ -z "${G2P_NOASAN:-}" ]; then
        "$CC" -std=gnu11 -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -DG2P_ASAN \
            -I"$G2" "$G2/g2_pres_run.c" "$o/g2p_sites.c" -o "$WORK/$tag.asan" 2> "$WORK/$tag.asanbuild" \
            || { echo "FAIL: $tag: the ASan+UBSan build fails"; head -20 "$WORK/$tag.asanbuild"; return 1; }
        ASAN_OPTIONS=detect_leaks=0:handle_segv=0 "$TIMEOUT_BIN" 900 "$WORK/$tag.asan" --seed "$SEED" \
            > "$WORK/$tag.asan.log" 2>&1
        rc=$((rc || $?))
    fi
    return "$rc"
}

# level_table: the kit's levels and each pass target's admitted levels,
# into $WORK/levels.txt ("level STAMP VW", "admits TARGET STAMP..."): the
# kit's own listing (tests/memfn/simd_levels.c against $LIB, the tree's
# committed kit even under --plant) through target_text.admitted()
level_table() {
    "$CC" -std=gnu11 -O2 -I"$ROOT/memfn/include" -o "$WORK/simd_levels" "$ROOT/tests/memfn/simd_levels.c" \
        "$LIB" 2> "$WORK/simd_levels.build" || { head -5 "$WORK/simd_levels.build"; return 1; }
    python3 -I - "$ROOT/tests/memfn" "$WORK/simd_levels" $TARGETS > "$WORK/levels.txt" <<'EOF' || return 1
import sys
sys.path.insert(0, sys.argv[1])
import target_text
levels, targets = target_text.read_table(sys.argv[2])
if not levels:
    sys.exit("the kit lists no level")
for l in levels:
    print("level", l["stamp"], l["vw"])
by = {t["name"]: t for t in targets}
for name in sys.argv[3:]:
    if name not in by:
        sys.exit("pass target %s is no kit target" % name)
    print("admits", name, *[l["stamp"] for l in target_text.admitted(by[name], levels)])
EOF
}

# cell_checks TAG TARGET: the per-level cells of one pass's recording log, by
# the family rule; one line per check, "CELLOK ..." or "CELLFAIL: ..."
cell_checks() {
    local tag="$1" tgt="$2" line adm stamp vw lay i c f v fl
    line=$(grep -h '^G2P cells ' "$WORK/$tag.run.log")
    [ -n "$line" ] || { echo "CELLFAIL: $tag: the recording driver printed no cells line"; return; }
    adm=" $(awk -v t="$tgt" '$1 == "admits" && $2 == t { $1 = ""; $2 = ""; print }' "$WORK/levels.txt") "
    while read -r _ stamp vw; do
        v=$(echo "$line" | grep -oE " vw$vw=[0-9]+,[0-9]+,[0-9]+" | cut -d= -f2)
        [ -n "$v" ] || { echo "CELLFAIL: $tag: level $stamp (W $vw): the driver counts no W-$vw cell"; continue; }
        fl=$(echo " $CELL_FLOORS " | grep -oE " $stamp:[0-9]+:[0-9]+:[0-9]+ " | tr -d ' ')
        case "$adm" in *" $stamp "*) [ -n "$fl" ] || { echo "CELLFAIL: level $stamp has no CELL_FLOORS literal"; continue; } ;; esac
        i=0
        for lay in U L A; do
            i=$((i + 1))
            c=$(echo "$v" | cut -d, -f$i)
            case "$adm" in
            *" $stamp "*)
                f=$(echo "$fl" | cut -d: -f$((i + 1)))
                if [ "$c" = 0 ]; then echo "CELLFAIL: $tag: $stamp $lay: 0 arm entries (a cell that measures 0)"
                elif [ "$c" -lt "$f" ]; then echo "CELLFAIL: $tag: $stamp $lay: $c arm entries < floor $f"
                else echo "CELLOK $tag $stamp $lay $c"; fi ;;
            *)
                if [ "$c" = 0 ]; then echo "CELLOK $tag $stamp $lay 0"
                else echo "CELLFAIL: $tag: $stamp $lay: $c arm entries where the target admits none"; fi ;;
            esac
        done
    done < <(grep '^level ' "$WORK/levels.txt")
}

counts() {   # counts LOG: "P F" from its checks lines
    local p f
    p=$(grep -m1 '^checks passed:' "$1" 2>/dev/null | grep -oE '[0-9]+')
    f=$(grep -m1 '^checks failed:' "$1" 2>/dev/null | grep -oE '[0-9]+')
    echo "${p:-x} ${f:-x}"
}

# moved TARGET: "M W", the witnesses whose text scan moved between the
# default and the lever pass, and the witnesses read in both
moved() {
    join <(grep -h '^G2PW ' "$WORK/$1.0.run.log" | awk '{print $3, $4}' | sort) \
         <(grep -h '^G2PW ' "$WORK/$1.1.run.log" | awk '{print $3, $4}' | sort) \
        | awk '{ w++; if ($2 != $3) m++ } END { print m + 0, w + 0 }'
}

# the oracle step over every pass's records: "rows violations" or OWED
oracle_step() {
    local all="$WORK/records.tsv"
    head -1 "$(ls "$WORK"/*.rec.tsv | head -1)" > "$all"
    for f in "$WORK"/*.rec.tsv; do tail -n +2 "$f" >> "$all"; done
    if [ ! -f "$ORACLE" ]; then echo OWED; return 0; fi
    "$TIMEOUT_BIN" 900 python3 -I "$ORACLE" < "$all" > "$WORK/oracle.log" 2>&1
    local rc=$?
    local tr; tr=$(grep -m1 '^oracle: rows=' "$WORK/oracle.log")
    echo "$rc ${tr:-none}"
}

# --- --reach: the mech rows' witness probe (the clean tree's kit) ------------
if [ "${1:-}" = "--reach" ]; then
    [ -f "$LIB" ] || { echo "no $LIB"; exit 1; }
    build_gen reach "$LIB" || exit 1
    for lev in 0 1; do
        mkdir -p "$WORK/reach.$lev"
        "$TIMEOUT_BIN" 120 "$WORK/reach.gen" "$SEED" "$NSITES" "$WORK/reach.$lev" generic "$lev" \
            > "$WORK/reach.$lev.log" 2>&1 || { echo "the generator failed (lever $lev)"; exit 1; }
    done
    f="$WORK/reach.0/g2p_sites.c"
    # A: a run part whose words compare masks a word (the plant drops position 0's byte)
    m=$(grep -c '(g2p[0-9]*_w[248](subject + cand) & g2p' "$f")
    [ "${m:-0}" -ge 50 ] && echo "REACH-G2P-WORDS-COMPARE n=$m"
    # B: the memchr form's loop (the plant starts it one above lo)
    m=$(grep -c 'const void \*q = memchr(subject + pos' "$f")
    [ "${m:-0}" -ge 50 ] && echo "REACH-G2P-MEMCHR-FORM n=$m"
    # S3010: the uses' run-part calls at the attempt start (the plant adds 1)
    m=$(grep -c '(subject, subject_length, \(search_from\|posvar\))' "$f")
    [ "${m:-0}" -ge 50 ] && echo "REACH-G2P-USE-CALL n=$m"
    # S3060-S3062: the run part's floor below the origin (a negative omin's
    # `lo >= N ? lo - N : 0`), entry and re-entry
    m=$(grep -cE 'subject_length, \((search_from|posvar) >= [0-9]+ \?' "$f")
    [ "${m:-0}" -ge 50 ] && echo "REACH-G2P-NEG-FLOOR n=$m"
    # S3063: the twin's admission at a negative K on sites whose bit at K 0 is 1
    m=$(grep -oE ' wk3_cases=[0-9]+' "$WORK/reach.0.log" | grep -oE '[0-9]+$')
    [ "${m:-0}" -ge 1000 ] && echo "REACH-G2P-TWIN-NEG-K n=$m"
    # S3064: sites whose reply's extent ends before the run does (the plant's +1 shows)
    m=$(grep -oE ' room=[0-9]+' "$WORK/reach.0.log" | grep -oE '[0-9]+$')
    [ "${m:-0}" -ge 20 ] && echo "REACH-G2P-REPLY-ROOM n=$m"
    # S3043: the GENERIC row's inline run-part loop starting at the run's floor
    # below the origin (the generic pass, on_miss_leaves 0)
    mkdir -p "$WORK/reach.g"
    "$TIMEOUT_BIN" 120 "$WORK/reach.gen" "$SEED" "$NSITES" "$WORK/reach.g" generic 0 0 \
        > "$WORK/reach.g.log" 2>&1 || { echo "the generator failed (generic pass)"; exit 1; }
    m=$(grep -cE '_c[0-9]+ = \(g2p[0-9]+_mf[0-9]+_lo >= [0-9]+ \?' "$WORK/reach.g/g2p_sites.c")
    [ "${m:-0}" -ge 50 ] && echo "REACH-G2P-GENERIC-FLOOR n=$m"
    # C (and S3012's in-run stop): the lever witnesses rendered in the run-tie-left pass
    m=$(grep -oE 'G2PGEN generic.lever sites=[0-9]+ rendered=[0-9]+' "$WORK/reach.1.log" | grep -oE '[0-9]+$')
    [ "${m:-0}" -ge 300 ] && grep -q '^g2_pres_gen failures: 0' "$WORK/reach.1.log" \
        && echo "REACH-G2P-LEVER-PASS rendered=$m"
    # K38-3 (S3098-S3103): the vrun arms the W-K4 plants and the cells'
    # controls edit, on the x86-64-v3 pass (w16 and w32 run parts)
    mkdir -p "$WORK/reach.v3"
    "$TIMEOUT_BIN" 120 "$WORK/reach.gen" "$SEED" "$NSITES" "$WORK/reach.v3" x86-64-v3 0 \
        > "$WORK/reach.v3.log" 2>&1 || { echo "the generator failed (x86-64-v3 pass)"; exit 1; }
    m=$(grep -c '__w16(const unsigned char \*subject' "$WORK/reach.v3/g2p_sites.c")
    [ "${m:-0}" -ge 10 ] && echo "REACH-G2P-W16-ARM n=$m"
    m=$(grep -c '__w32(const unsigned char \*subject' "$WORK/reach.v3/g2p_sites.c")
    [ "${m:-0}" -ge 10 ] && echo "REACH-G2P-W32-ARM n=$m"
    # S3104: the level list the coverage check walks (every level run by a pass target)
    level_table || { echo "the kit's level listing could not be read"; exit 1; }
    m=$(grep -c '^level ' "$WORK/levels.txt")
    a=$(grep '^level ' "$WORK/levels.txt" | while read -r _ st _; do
        grep -qE "^admits [^ ]+( .*)? $st( |$)" "$WORK/levels.txt" && echo "$st"; done | wc -l)
    [ "${m:-0}" -ge 2 ] && [ "$a" = "$m" ] && echo "REACH-G2P-LEVELS n=$m"
    exit 0
fi

# --- --plant / --plants -------------------------------------------------------
if [ "${1:-}" = "--plant" ] || [ "${1:-}" = "--plants" ]; then
    ids="${2:-}"
    [ "$1" = "--plants" ] && ids="$PLANTS"
    [ -n "$ids" ] || fail_setup "--plant needs an id ($PLANTS)"
    level_table || fail_setup "the kit's level listing could not be read"
    bad=0
    for id in $ids; do
        specs="$(plant_spec "$id")" || fail_setup "no plant $id"
        if plant_asan "$id"; then unset G2P_NOASAN; else export G2P_NOASAN=1; fi
        rm -rf "$WORK/src"; cp -rL "$ROOT/memfn/src" "$WORK/src"   # -L: a symlinked src is copied, never planted in place
        while IFS= read -r spec; do
        file="${spec%%@@*}"; rest="${spec#*@@}"; from="${rest%%@@*}"; to="${rest#*@@}"
        python3 -I - "$WORK/src/$file" "$from" "$to" <<'EOF' || fail_setup "$id: the plant does not apply"
import sys
p, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
def un(s):
    return s.replace('\\\\n', '\x00').replace('\\n', '\n').replace('\x00', '\\n').replace('\\&', '&')
a, b = un(a), un(b)
s = open(p).read()
if s.count(a) != 1:
    sys.exit("plant text found %d times" % s.count(a))
open(p, 'w').write(s.replace(a, b))
EOF
        done <<< "$specs"
        kit_objs "$WORK/src" "$WORK/pk_$id" || fail_setup "$id: the planted kit does not compile"
        build_gen "p$id" "$WORK/pk_$id"/*.o || fail_setup "$id: the generator does not build"
        red=""
        rm -f "$WORK"/*.rec.tsv "$WORK/fails.$id"
        for tgt in $TARGETS; do
            host_has "$tgt" || continue
            for lev in 0 1; do
                cp "$WORK/p$id.gen" "$WORK/$tgt.$lev.gen"
                built=$(one_pass "$tgt.$lev" "$tgt" "$lev" | grep -m1 '^FAIL')
                grep -h '^FAIL' "$WORK/$tgt.$lev.gen.log" "$WORK/$tgt.$lev.run.log" 2>/dev/null \
                    >> "$WORK/fails.$id"
                # the per-level cells (K38-3) and, on an ASan plant, the ASan
                # report: each a FAIL line of the pass
                cell_checks "$tgt.$lev" "$tgt" | sed -n 's/^CELLFAIL: /FAIL: CELL: /p' >> "$WORK/fails.$id"
                plant_asan "$id" && grep -h -m1 'ERROR: AddressSanitizer' "$WORK/$tgt.$lev.asan.log" 2>/dev/null \
                    | sed "s/^/FAIL: $tgt.$lev ASan: /" >> "$WORK/fails.$id"
                r=$(grep -h '^FAIL' "$WORK/$tgt.$lev.gen.log" "$WORK/$tgt.$lev.run.log" 2>/dev/null | head -1)
                [ -n "$r" ] || r=$(grep -m1 -E "^FAIL: (CELL: )?$tgt\.$lev[: ]" "$WORK/fails.$id")
                [ -n "$r" ] || r="$built"
                [ -n "$red" ] || red="$r"
            done
            read -r mv nw < <(moved "$tgt")
            [ -n "$red" ] || [ "$mv" = "$nw" ] || red="LEVER: $mv of $nw witnesses moved on $tgt"
        done
        cp "$WORK/p$id.gen" "$WORK/generic.oml0.gen"
        built=$(one_pass generic.oml0 generic 0 0 | grep -m1 '^FAIL')
        grep -h '^FAIL' "$WORK/generic.oml0.gen.log" "$WORK/generic.oml0.run.log" 2>/dev/null >> "$WORK/fails.$id"
        r=$(grep -h '^FAIL' "$WORK/generic.oml0.gen.log" "$WORK/generic.oml0.run.log" 2>/dev/null | head -1)
        [ -n "$r" ] || r="$built"
        [ -n "$red" ] || red="$r"
        o=$(oracle_step)
        case "$o" in
        OWED) ostate="oracle OWED" ;;
        0\ *) ostate="oracle green ($o)" ;;
        *)    ostate="oracle RED ($o)"; [ -n "$red" ] || red="the oracle: $o" ;;
        esac
        # by its own detector: every expected pattern among the FAIL lines
        # (an oracle plant: the oracle RED)
        byown=1 shown=""
        if [ "$(plant_detector "$id")" = oracle ]; then
            case "$ostate" in "oracle RED"*) ;; *) byown=0 ;; esac
        else
            IFS=';' read -ra pats <<< "$(plant_expect "$id")"
            for pat in "${pats[@]}"; do
                [ -n "$pat" ] || continue
                m=$(grep -E -m1 -- "$pat" "$WORK/fails.$id" 2>/dev/null)
                if [ -n "$m" ]; then shown="$m"; else byown=0; fi
            done
        fi
        ab="$(plant_absent "$id")"
        if [ -n "$ab" ] && grep -qE -- "$ab" "$WORK/fails.$id"; then
            echo "PLANT $id MOVED A PASS IT MUST LEAVE UNCHANGED: $(grep -E -m1 -- "$ab" "$WORK/fails.$id")"
            bad=$((bad + 1))
        fi
        if [ -n "$red" ] && [ "$byown" = 1 ]; then
            echo "PLANT $id RED   ($(plant_detector "$id"); $ostate): ${shown:-$red}"
        elif [ -n "$red" ]; then
            echo "PLANT $id RED BUT NOT BY ITS DETECTOR ($(plant_detector "$id") $(plant_expect "$id"); $ostate): $red"
            bad=$((bad + 1))
        elif [ "$(plant_detector "$id")" = oracle ] && [ "$o" = OWED ]; then
            echo "PLANT $id OWED  (its detector is the oracle step, and the oracle is OWED: NOT DETECTED)"
            bad=$((bad + 1))
        else
            echo "PLANT $id GREEN (NOT DETECTED; $ostate)"; bad=$((bad + 1))
        fi
    done
    [ "$bad" -eq 0 ]
    exit $?
fi

# --- the run ----------------------------------------------------------------------
[ -f "$LIB" ] || fail_setup "$LIB not built (make all first)"
tp=0 tf=0 skipped=0
note() { tf=$((tf + 1)); echo "FAIL: $1"; }
floor() { if [ "${2:-0}" -ge "$3" ]; then tp=$((tp + 1)); else note "floor $1: ${2:-0} < $3"; fi; }
build_gen main "$LIB" || fail_setup "the generator does not build"
level_table || fail_setup "the kit's level listing (tests/memfn/simd_levels.c, target_text.py) could not be read"
# THE LEVEL-LIST COVERAGE (K38-3, [r1s1 S1-15]): every level the kit lists is
# admitted by a target this run's pass list runs on this host, else its
# cells are never measured: a named failure, not a skip
while read -r _ stamp _; do
    run_by=""
    for tgt in $TARGETS; do
        case " ${G2P_SKIP_ARMS:-} " in *" $tgt "*) continue ;; esac
        host_has "$tgt" || continue
        grep -qE "^admits $tgt( .*)? $stamp( |$)" "$WORK/levels.txt" && run_by="$run_by $tgt"
    done
    if [ -n "$run_by" ]; then tp=$((tp + 1)); echo "level $stamp: run by$run_by"
    else note "level $stamp has no runnable target (pass list: $TARGETS)"; fi
done < <(grep '^level ' "$WORK/levels.txt")
for tgt in $TARGETS; do
    case " ${G2P_SKIP_ARMS:-} " in *" $tgt "*) skip_why="G2P_SKIP_ARMS" ;; *) skip_why="" ;; esac
    [ -n "$skip_why" ] || host_has "$tgt" || skip_why="this host lacks the target's ISA"
    if [ -n "$skip_why" ]; then
        echo "SKIPPED ARM $tgt: $skip_why; its passes NOT run"
        skipped=$((skipped + 1))
        continue
    fi
    for lev in 0 1; do
        tag="$tgt.$lev"
        cp "$WORK/main.gen" "$WORK/$tag.gen"
        one_pass "$tag" "$tgt" "$lev"
        grep -h '^FAIL' "$WORK/$tag.gen.log" "$WORK/$tag.run.log" | head -20
        grep -h '^G2PGEN' "$WORK/$tag.gen.log"
        gf=$(grep -h '^g2_pres_gen failures:' "$WORK/$tag.gen.log" | grep -oE '[0-9]+$')
        if [ "${gf:-x}" != 0 ]; then note "$tag: the generator failed ${gf:-?} sites"; else tp=$((tp + 1)); fi
        read -r p f < <(counts "$WORK/$tag.run.log")
        if [ "$p" = x ] || [ "$f" = x ]; then note "$tag: the recording driver printed no counts"
        else tp=$((tp + p)); tf=$((tf + f)); echo "$tag recording driver: passed $p failed $f"; fi
        grep -h '^G2P ' "$WORK/$tag.run.log"
        if [ -z "${G2P_NOASAN:-}" ]; then
            read -r p f < <(counts "$WORK/$tag.asan.log")
            if [ "$p" = x ] || [ "$f" = x ]; then
                note "$tag: the ASan+UBSan driver printed no counts ($(grep -m1 'ERROR\|runtime error' "$WORK/$tag.asan.log"))"
            else
                tp=$((tp + p)); tf=$((tf + f)); echo "$tag ASan+UBSan driver: passed $p failed $f"
                grep -h '^FAIL' "$WORK/$tag.asan.log" | head -10
                floor "$tag layout_A" "$(grep -h '^G2P layout_A=' "$WORK/$tag.asan.log" | cut -d= -f2)" "$FLOOR_LAYOUT_A"
            fi
        fi
        gv() { grep -h "^G2PGEN" "$WORK/$tag.gen.log" | grep -oE " $1=[0-9]+" | cut -d= -f2; }
        rv() { grep -h "^G2P $1" "$WORK/$tag.run.log" | grep -oE " $2=[0-9]+" | head -1 | cut -d= -f2; }
        for x in $FLOOR_ROUTE_SITES; do floor "$tag sites ${x%%:*}" "$(gv "${x%%:*}")" "${x#*:}"; done
        floor "$tag p2_refused" "$(gv p2_refused)" "$FLOOR_P2_REFUSED"
        floor "$tag ctl_nopart" "$(gv ctl_nopart)" "$FLOOR_CTL_NOPART"
        floor "$tag ctl_two" "$(gv ctl_two)" "$FLOOR_CTL_TWO"
        for x in $FLOOR_REACH; do floor "$tag reach ${x%%:*}" "$(rv reach "${x%%:*}")" "${x#*:}"; done
        re=$(grep -h '^G2P reach' "$WORK/$tag.run.log" | sed 's/.*reentry//')
        for x in $FLOOR_REACH_RE; do
            floor "$tag reentry ${x%%:*}" "$(echo "$re" | grep -oE "${x%%:*}=[0-9]+" | cut -d= -f2)" "${x#*:}"
        done
        sc=$(grep -h '^G2P checks' "$WORK/$tag.run.log" | sed 's/.*scan_sites//')
        for x in $FLOOR_SCAN_SITES; do
            floor "$tag scan sites ${x%%:*}" "$(echo "$sc" | grep -oE "${x%%:*}=[0-9]+" | cut -d= -f2)" "${x#*:}"
        done
        floor "$tag cover" "$(rv checks cover)" "$FLOOR_COVER"
        floor "$tag extent" "$(rv checks extent)" "$FLOOR_EXTENT"
        floor "$tag records" "$(rv checks records)" "$FLOOR_RECORDS"
        floor "$tag nearmiss" "$(rv checks nearmiss)" "$FLOOR_NEARMISS"
        floor "$tag nm_sound" "$(rv checks nm_sound)" "$FLOOR_NM_SOUND"
        floor "$tag nm_uses" "$(rv checks nm_uses)" "$FLOOR_NM_USES"
        floor "$tag witnesses" "$(rv sites witnesses)" "$FLOOR_WITNESSES"
        # K38-2's populations, the generator's census and the driver's
        floor "$tag neg_omin" "$(gv neg_omin)" "$FLOOR_NEG_OMIN"
        floor "$tag wk4_omin" "$(gv wk4_omin)" "$FLOOR_WK4_OMIN"
        floor "$tag k_signed" "$(gv k_signed)" "$FLOOR_K_SIGNED"
        floor "$tag k_nonpos" "$(gv k_nonpos)" "$FLOOR_K_NONPOS"
        floor "$tag partial" "$(gv partial)" "$FLOOR_PARTIAL"
        floor "$tag room" "$(gv room)" "$FLOOR_ROOM"
        floor "$tag wk3_cases" "$(gv wk3_cases)" "$FLOOR_WK3_CASES"
        floor "$tag partial_hits" "$(rv k382 partial_hits)" "$FLOOR_PARTIAL_HITS"
        floor "$tag neg_records" "$(rv k382 neg_records)" "$FLOOR_NEG_RECORDS"
        floor "$tag below_hits" "$(rv k382 below_hits)" "$FLOOR_BELOW_HITS"
        floor "$tag wk4_low" "$(rv k382 wk4_low)" "$FLOOR_WK4_LOW"
        floor "$tag presence checks" "$(rv presence checks)" "$FLOOR_PRES_CHECKS"
        floor "$tag presence below" "$(rv presence below)" "$FLOOR_PRES_BELOW"
        [ "$(rv presence generic)" = 0 ] && tp=$((tp + 1)) || note "$tag: $(rv presence generic) sites rendered by the generic row on an on_miss_leaves 1 pass"
        # the §3.5 witnesses: each green AND reached, in the recording driver
        # and the ASan+UBSan one; W-K3's own witness reached in the generator
        wk=$(grep -h '^G2P wk ' "$WORK/$tag.run.log")
        if [ "$wk" = "G2P wk L1=1/1 L1b=1/1 K1=1/1 K2=1/1 K1b=1/1 (green/reached)" ]; then tp=$((tp + 1))
        else note "$tag: the §3.5 witnesses are not all green and reached (${wk:-no line})"; fi
        if [ -z "${G2P_NOASAN:-}" ]; then
            wk=$(grep -h '^G2P wk ' "$WORK/$tag.asan.log")
            if [ "$wk" = "G2P wk L1=1/1 L1b=1/1 K1=1/1 K2=1/1 K1b=1/1 (green/reached)" ]; then tp=$((tp + 1))
            else note "$tag: the §3.5 witnesses (ASan+UBSan) are not all green and reached (${wk:-no line})"; fi
        fi
        if grep -qE "^G2PWK3 $tgt\.(default|lever) site [0-9]+ reached" "$WORK/$tag.gen.log"; then tp=$((tp + 1))
        else note "$tag: W-K3's witness (stated rates m > h) did not reach"; fi
        for x in $SIMD_FLOORS; do
            [ "${x%%:*}" = "$tgt" ] || continue
            IFS=: read -r _ f16 f32 fvec <<< "$x"
            s16=$(gv simd16); s32=$(gv simd32)
            vec=$(grep -h '^G2P vec_reads=' "$WORK/$tag.run.log" | cut -d= -f2)
            if [ "$f16" = 0 ]; then
                [ "${s16:-x}" = 0 ] && tp=$((tp + 1)) || note "$tag: ${s16:-?} w16 arms on a target that admits none"
            else floor "$tag simd16" "$s16" "$f16"; fi
            if [ "$f32" = 0 ]; then
                [ "${s32:-x}" = 0 ] && tp=$((tp + 1)) || note "$tag: ${s32:-?} w32 arms on a target that admits none"
            else floor "$tag simd32" "$s32" "$f32"; fi
            [ "$fvec" = 0 ] || floor "$tag vector loads" "$vec" "$fvec"
        done
        # the per-level cells (K38-3): arm ENTRIES per (level, layout)
        grep -h '^G2P cells ' "$WORK/$tag.run.log"
        while read -r cl; do
            case "$cl" in CELLOK*) tp=$((tp + 1)) ;; *) note "${cl#CELLFAIL: }" ;; esac
        done < <(cell_checks "$tag" "$tgt")
    done
    # the lever's reach (plant C's witness): every witness's scan moved
    read -r mv nw < <(moved "$tgt")
    echo "lever $tgt: $mv of $nw witnesses' text scan moved (default vs run-tie-left)"
    floor "$tgt lever witnesses read" "$nw" "$FLOOR_WITNESSES"
    if [ "$mv" = "$nw" ]; then tp=$((tp + 1)); else note "$tgt: only $mv of $nw witnesses' scan moved under run-tie-left"; fi
done

# 5g. THE GENERIC PASS: on_miss_leaves 0, every site the generic row's
tag=generic.oml0
cp "$WORK/main.gen" "$WORK/$tag.gen"
one_pass "$tag" generic 0 0
grep -h '^FAIL' "$WORK/$tag.gen.log" "$WORK/$tag.run.log" | head -20
grep -h '^G2PGEN' "$WORK/$tag.gen.log"
gf=$(grep -h '^g2_pres_gen failures:' "$WORK/$tag.gen.log" | grep -oE '[0-9]+$')
if [ "${gf:-x}" != 0 ]; then note "$tag: the generator failed ${gf:-?} sites"; else tp=$((tp + 1)); fi
read -r p f < <(counts "$WORK/$tag.run.log")
if [ "$p" = x ] || [ "$f" = x ]; then note "$tag: the recording driver printed no counts"
else tp=$((tp + p)); tf=$((tf + f)); echo "$tag recording driver: passed $p failed $f"; fi
grep -h '^G2P ' "$WORK/$tag.run.log"
if [ -z "${G2P_NOASAN:-}" ]; then
    read -r p f < <(counts "$WORK/$tag.asan.log")
    if [ "$p" = x ] || [ "$f" = x ]; then
        note "$tag: the ASan+UBSan driver printed no counts ($(grep -m1 'ERROR\|runtime error' "$WORK/$tag.asan.log"))"
    else
        tp=$((tp + p)); tf=$((tf + f)); echo "$tag ASan+UBSan driver: passed $p failed $f"
        grep -h '^FAIL' "$WORK/$tag.asan.log" | head -10
    fi
fi
gv() { grep -h "^G2PGEN" "$WORK/$tag.gen.log" | grep -oE " $1=[0-9]+" | cut -d= -f2; }
rv() { grep -h "^G2P $1" "$WORK/$tag.run.log" | grep -oE " $2=[0-9]+" | head -1 | cut -d= -f2; }
floor "$tag generic sites (generator)" "$(gv generic)" "$FLOOR_GENERIC"
floor "$tag generic sites (driver)" "$(rv presence generic)" "$FLOOR_GENERIC"
floor "$tag presence checks" "$(rv presence checks)" "$FLOOR_PRES_CHECKS"
floor "$tag presence below" "$(rv presence below)" "$FLOOR_PRES_BELOW"
floor "$tag neg_omin" "$(gv neg_omin)" "$FLOOR_NEG_OMIN"
wk=$(grep -h '^G2P wk ' "$WORK/$tag.run.log")
if [ "$wk" = "G2P wk L1=1/1 L1b=1/1 K1=1/1 K2=1/1 K1b=1/1 (green/reached)" ]; then tp=$((tp + 1))
else note "$tag: the §3.5 witnesses are not all green and reached (${wk:-no line})"; fi

# the records: the seam's format, held by the family before the oracle reads them
ls "$WORK"/*.rec.tsv > /dev/null 2>&1 || fail_setup "no pass wrote records"
bad=$(cat "$WORK"/*.rec.tsv | awk -F'\t' '
    /^#/ { next }
    NF != 10 || $2 !~ /^(entry|reentry)$/ || $3 !~ /^([0-9a-f][0-9a-f])*$/ || $4 !~ /^[0-9]+$/ ||
    $5 !~ /^-?[0-9]+$/ || $6 !~ /^[0-9a-f]{64}(,[0-9a-f]{64})*$/ || $7 !~ /^[0-9]+$/ ||
    $8 !~ /^[0-9]+$/ || $9 !~ /^([0-9]+|MISS)$/ || $10 !~ /^(-?[0-9]+(,-?[0-9]+)*)?$/ { b++ }
    END { print b + 0 }')
if [ "$bad" = 0 ]; then tp=$((tp + 1)); else note "$bad oracle records break the seam's format"; fi
o=$(oracle_step)
nrec=$(($(wc -l < "$WORK/records.tsv") - 1))
case "$o" in
OWED) note "ORACLE OWED: $ORACLE is absent; $nrec records written, NOT checked" ;;
0\ *) if echo "$o" | grep -q "rows=$nrec violations=0"; then tp=$((tp + 1)); echo "oracle: green over $nrec records ($o)"
      else note "the oracle's trailer does not count every record ($o; $nrec records)"; fi ;;
*)    note "the oracle: $o (see its VIOLATION lines)"; grep -m 20 '^VIOLATION' "$WORK/oracle.log" ;;
esac
echo "skipped arms: $skipped"
[ "$skipped" -eq 0 ] || note "$skipped target arm(s) skipped: the family's floors are per pass, a skip is not a pass"
echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
