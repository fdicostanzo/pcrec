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
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR, G2W_SITES, G2W_SEED.
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
EFIND_FLOORS="libc:320 walk:103 hors:110 run:115 below:95 report:370 refused:17 pair:316 fn:48"

# THE PLANTS: id, then FILE@@FROM@@TO (FILE under memfn/src; FROM replaced
# by TO, `\n` a newline, `\&` an ampersand). Each must make the run red.
# Ids from the kit's S1400-S1429 (R-29): S1400-S1407 were wsc1's WSC1-P1..P8; S1540
# (code review r2, lane s3pair) and S1541-S1543 (the S3 final review, lane s3fix) are
# the kit's S1540-S1559.
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
        echo 'window.c@@        if (m->p[k].present \&\& m->p[k].core \&\& !count(m->p[k].set)) return 1;@@        if (0) return 1;' ;;
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
        # generator's D-hors scope census goes red)
        echo 'window.c@@    if (!dx->hw || dx->whi - dx->wlo < 1 || dx->whi < 0) return 0;@@    if (!dx->hw || dx->whi - dx->wlo < 1) return 0;' ;;
    S1543) # the S3 final review's EMIT-3: E-find's RAISE dropped (no expression floor):
        # with the test's lower half hoisted into it, a core position below the
        # candidate is read below the subject (layout L's guard page)
        echo 'window.c@@    } else {\n        kb_printf(b, "if (%s < %d) %s = %d; ", rc->C, -w->clo, rc->C, -w->clo);\n    }@@    } else {\n    }' ;;
    S1410) # a full-set position tested: C-yes takes a verify-YES position whose meet is every byte
        # (the kit manager's wsc3 ruling 1: such a position is the bound alone)
        echo 'window.c@@        if (m->p[k].present \&\& m->p[k].yes \&\& !full(m->p[k].yset))@@        if (m->p[k].present \&\& m->p[k].yes)' ;;
    *) return 1 ;;
    esac
}
PLANTS="S1400 S1401 S1402 S1403 S1404 S1405 S1406 S1407 S1409 S1410 S1422 S1423 S1425 S1426 S1427 S1428 S1429 S1540 S1541 S1542 S1543"

fail_setup() { echo "FAIL: $1"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }

# kit_objs SRCDIR OUTDIR: every kit source compiled into OUTDIR.
kit_objs() {
    local src="$1" out="$2"
    mkdir -p "$out"
    for s in "$src"/*.c; do
        "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -c -o "$out/$(basename "${s%.c}").o" "$s" \
            || return 1
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

echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
