#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's window family, lane
#   wsc1, D172 S2 commit 1).
#
# memfn/tests/run_g2_win.sh — G2'S WINDOW FAMILY (docs/design/memfn/
# window_site.md rev 3.2; the kit's window family, memfn/src/window.c,
# reachable only under mf_preview(art, "window-family")). run_g2.sh's section
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
# when the space grows; never lower one to make a run pass.
FLOOR_SITES=1500                # every generated site renders (no refusal)
FLOOR_CONTROLS=23               # the lever's controls and the NOP refusals (26)
FLOOR_QUERIES=1500              # mf_ask equal to a same-phase define, every site
FLOOR_CALLS=3300000             # answer calls, each in four layouts (3745812)
FLOOR_HITS=550000               # (622264)
PATH_FLOORS="empty:175 parked:285 reseed:105 mass:670 floor:110"
MARGIN_FLOORS="reseed:105 parked:135"
FLOOR_PINNED=34                 # (39)
FLOOR_RESEED_BIT=230            # (257)
TIE_FLOORS="mass:230 model:55"
CELL_FLOORS="edge_rejects:22000 core_off:1600000 noncore_off:490000 neg_reads:920000 nop_empty:130000"
FORM_FLOORS="wf-floor:740 generic:355 pf_memchr:210 ofsskip:26 pf_walk:15"

# THE PLANTS: id, then FILE@@FROM@@TO (FILE under memfn/src; FROM replaced
# by TO, `\n` a newline, `\&` an ampersand). Each must make the run red.
# Placeholder ids until the kit manager assigns S1400-S1429 ones.
plant_spec() {
    case "$1" in
    WSC1-P1) # the edge guard dropped: a non-core position below the candidate read inside [0, F)
        echo 'window.c@@                kb_printf(t, "(%s >= %s + %d \&\& ", rc->C, rc->FL, -d);\n                rc->used |= PARAM_FL;@@                kb_printf(t, "(");' ;;
    WSC1-P2) # C-run merging singletons: positions one-position spans cover grouped into one compare
        echo 'window.c@@                join = !p->one_pos \&\& !q->one_pos \&\&@@                join =' ;;
    WSC1-P3) # the MARGIN's direction flipped
        echo 'window.c@@    return l < r || (l == r \&\& wf_ties[T_MARGIN].to == TIE_RESEED);@@    return l > r || (l == r \&\& wf_ties[T_MARGIN].to == TIE_RESEED);' ;;
    WSC1-P4) # a tie flipped: A-mass at a set position to the HIGHER offset
        echo 'window.c@@    [T_MASS_SET]     = { "A-mass at a set position", TIE_LOWER,@@    [T_MASS_SET]     = { "A-mass at a set position", TIE_HIGHER,' ;;
    WSC1-P5) # a core position read as outside the core: the plan's LAST tested position
        # (the hoisted bound's upper end; a core position inside the bound is
        # tested by the bound, so a per-position plant there is equivalent)
        echo 'window.c@@        w->core[i] = (uint8_t)rd_core(d, p);@@        w->core[i] = (uint8_t)(rd_core(d, p) \&\& i + 1 < n);' ;;
    WSC1-P6) # an empty meet inside a core not sent to the floor row
        echo 'window.c@@        if (m->p[k].present \&\& m->p[k].core \&\& !count(m->p[k].set)) return 1;@@        if (0) return 1;' ;;
    WSC1-P7) # C-pin splitting the stretch: the pinned positions not one compare
        echo 'window.c@@                join = in_pinned(d, o) \&\& in_pinned(d, o - 1);@@                join = 0;' ;;
    WSC1-P8) # an untested offset claimed: the class proves one past each tested position
        echo 'window.c@@        for (unsigned x = 0; x < 32; x++) out->proven[d - MF_PROOF_LO][x] \&= w->set[i][x];@@        for (unsigned x = 0; x < 32; x++) out->proven[d - MF_PROOF_LO][x] \&= w->set[i][x];\n        if (d + 1 < MF_MAX_FWD) for (unsigned x = 0; x < 32; x++) out->proven[d + 1 - MF_PROOF_LO][x] \&= w->set[i][x];' ;;
    *) return 1 ;;
    esac
}
PLANTS="WSC1-P1 WSC1-P2 WSC1-P3 WSC1-P4 WSC1-P5 WSC1-P6 WSC1-P7 WSC1-P8"

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
        one_run "plant_$id" "$WORK/pk_$id"/*.o
        c="$(counts "$WORK/plant_$id.run.log")"
        red=$(grep -h '^FAIL' "$WORK/plant_$id.gen.log" "$WORK/plant_$id.run.log" 2>/dev/null | head -1)
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
floor calls "$(grep -h '^G2W sites' "$WORK/plain.run.log" | awk '{print $5}')" "$FLOOR_CALLS"
floor hits "$(grep -h '^G2W sites' "$WORK/plain.run.log" | awk '{print $7}')" "$FLOOR_HITS"
for pf in $PATH_FLOORS; do floor "path ${pf%%:*}" "$(val paths "${pf%%:*}")" "${pf#*:}"; done
floor pinned "$(val paths pinned)" "$FLOOR_PINNED"
floor reseed_bit "$(val paths reseed_bit)" "$FLOOR_RESEED_BIT"
for mf in $MARGIN_FLOORS; do floor "margin ${mf%%:*}" "$(val margin "${mf%%:*}")" "${mf#*:}"; done
for tf_ in $TIE_FLOORS; do floor "tie ${tf_%%:*}" "$(val ties "${tf_%%:*}")" "${tf_#*:}"; done
for cf in $CELL_FLOORS; do floor "cell ${cf%%:*}" "$(val cells "${cf%%:*}")" "${cf#*:}"; done
for ff in $FORM_FLOORS; do floor "form ${ff%%:*}" "$(val forms "${ff%%:*}")" "${ff#*:}"; done

echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
