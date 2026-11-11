#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's presence family,
#   lane k382a, R-38 K38-2a).
#
# memfn/tests/run_g2_pres.sh — G2'S PRESENCE FAMILY (docs/design/memfn/
# span_runs_sheet.md rev 1.3 §5's K38-2a row; §2.4 C2, §3.3, §3.5 W-K4).
# run_g2.sh's section 4p; runnable alone (~1-2 min, one process at a time).
#
#   1. g2/g2_pres_gen.c against the kit (LIB, default build/libpcrec.a):
#      GENERATED pre-check sites in today's statement form (MF_SITE_ABI 26:
#      omin 0, K >= 0) on the P0/P2/P3/P9 routes, laid out as a host lays
#      them out, defined, their entry and re-entry uses rendered; ONE PASS
#      PER TARGET of the U2 list (x86-64-v3, x86-64, generic: every admitted
#      level, both layers) and per lever state (default; run-tie-left);
#   2. the text compiles -Wall -Wextra -Werror;
#   3. g2/g2_pres_run.c over it, built twice: the RECORDING build (the kit's
#      text -fsanitize=kernel-address with every access an outlined call, so
#      the driver sees each read) runs the classifier (C2), the lever
#      witnesses, layouts U and L, and writes the ORACLE RECORDS
#      (docs/dev/lanes/k382a_oracle_iface.md); the ASan+UBSan build runs
#      the classifier, layouts U and L and layout A (W-K4b);
#   4. THE ORACLE STEP: the records piped to tests/memfn/occurrence_oracle.py;
#      the oracle file absent is a FAIL (`ORACLE OWED`, the records written,
#      NOT checked: review 2026-11-10 r2 k382a ORC-2; the oracle landed with
#      41ebc052b, and it is the family's only check of "least");
#   5. the lever's reach: every witness's text scan MOVED between the
#      default and the run-tie-left pass of the same target;
#   6. the floors (K35): literals below, sharing no source with the family.
#
#   --plant ID / --plants   the same passes (no ASan) over a COPY of memfn/src
#                           with one planted defect (the table below).
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

# --- the floors (K35): hand-written literals, measured 2026-11-10 on the
# Linux dev box (seed 20261110, 400 sites + 24 witnesses per pass, lane k382a;
# the measure, the least over the six passes, in parentheses), less ~10%. PER
# PASS (each target, each lever state). Raise them when the space grows; never
# lower one to make a run pass.
FLOOR_ROUTE_SITES="P0:83 P2:70 P3:158 P9:72"   # the generator's routes (92 77 175 80)
FLOOR_P2_REFUSED=70             # P2's control: a run part on an untested link refused (77)
FLOOR_REACH="P0:1920 P3:3750 P9:1830"          # run-part calls per route, entry + re-entry (2132 4162 2032)
FLOOR_REACH_RE="P0:670 P3:1390 P9:710"         # of them re-entry calls (744 1540 790)
FLOOR_SCAN_SITES="P0:83 P3:158 P9:72"          # sites whose text scan was read (92 175 80)
FLOOR_COVER=11450               # COVER probes (12729)
FLOOR_EXTENT=5630               # EXTENT probes (6254)
FLOOR_RECORDS=7500              # oracle records (8334)
# FAM-3's near-misses (review 2026-11-10 r2 k382a), measured 2026-11-10 by
# lane k382afix (same seed and sites; the least over the six passes):
FLOOR_NEARMISS=28540            # EXTENT's per-bit near-miss probes (31712)
FLOOR_NM_SOUND=3440             # near-miss occurrences in SOUND's subjects (3822)
FLOOR_NM_USES=4120              # near-miss occurrences in the uses' subjects (4583)
FLOOR_LAYOUT_A=14360            # layout A placements, ASan build (15962)
FLOOR_WITNESSES=24              # lever witnesses, every one rendered (24)
# THE LAYERS (D147; U2's admitted levels): per target, the sites whose run
# part has a w16 / w32 arm (the generator's census of the kit's own text), and
# the vector loads of the subject the recording build saw (the arms RAN).
# x86-64-v3 admits both levels, x86-64 w16 alone, generic (the OFF layer)
# none: a level the target does not admit must render NOTHING (exactly 0).
SIMD_FLOORS="x86-64-v3:18:18:1180 x86-64:18:0:990 generic:0:0:0"   # (20 20 1314; 20 0 1104; 0 0)

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
    *) return 1 ;;
    esac
}
plant_detector() { case "$1" in S3008|S3010) echo oracle ;; *) echo family ;; esac; }
PLANTS="S3007 S3008 S3009 S3010 S3011 S3012"

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

# one_pass TAG TARGET LEVER: render, compile, run (recording; ASan unless
# G2P_NOASAN). Logs in $WORK/TAG.*; records in $WORK/TAG.rec.tsv.
one_pass() {
    local tag="$1" tgt="$2" lev="$3" o="$WORK/$1.out"
    mkdir -p "$o"
    "$TIMEOUT_BIN" 300 "$WORK/$tag.gen" "$SEED" "$NSITES" "$o" "$tgt" "$lev" > "$WORK/$tag.gen.log" 2>&1
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

counts() {   # counts LOG: "P F" from its checks lines
    local p f
    p=$(grep -m1 '^checks passed:' "$1" 2>/dev/null | grep -oE '[0-9]+')
    f=$(grep -m1 '^checks failed:' "$1" 2>/dev/null | grep -oE '[0-9]+')
    echo "${p:-x} ${f:-x}"
}

# moved TARGET: "M W", the witnesses whose text scan moved between the
# default and the lever pass, and the witnesses read in both
moved() {
    join <(grep -h '^G2PW' "$WORK/$1.0.run.log" | awk '{print $3, $4}' | sort) \
         <(grep -h '^G2PW' "$WORK/$1.1.run.log" | awk '{print $3, $4}' | sort) \
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
    # C (and S3012's in-run stop): the lever witnesses rendered in the run-tie-left pass
    m=$(grep -oE 'G2PGEN generic.lever sites=[0-9]+ rendered=[0-9]+' "$WORK/reach.1.log" | grep -oE '[0-9]+$')
    [ "${m:-0}" -ge 300 ] && grep -q '^g2_pres_gen failures: 0' "$WORK/reach.1.log" \
        && echo "REACH-G2P-LEVER-PASS rendered=$m"
    exit 0
fi

# --- --plant / --plants -------------------------------------------------------
if [ "${1:-}" = "--plant" ] || [ "${1:-}" = "--plants" ]; then
    ids="${2:-}"
    [ "$1" = "--plants" ] && ids="$PLANTS"
    [ -n "$ids" ] || fail_setup "--plant needs an id ($PLANTS)"
    export G2P_NOASAN=1
    bad=0
    for id in $ids; do
        specs="$(plant_spec "$id")" || fail_setup "no plant $id"
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
        rm -f "$WORK"/*.rec.tsv
        for tgt in $TARGETS; do
            host_has "$tgt" || continue
            for lev in 0 1; do
                cp "$WORK/p$id.gen" "$WORK/$tgt.$lev.gen"
                built=$(one_pass "$tgt.$lev" "$tgt" "$lev" | grep -m1 '^FAIL')
                r=$(grep -h '^FAIL' "$WORK/$tgt.$lev.gen.log" "$WORK/$tgt.$lev.run.log" 2>/dev/null | head -1)
                [ -n "$r" ] || r="$built"
                [ -n "$red" ] || red="$r"
            done
            read -r mv nw < <(moved "$tgt")
            [ -n "$red" ] || [ "$mv" = "$nw" ] || red="LEVER: $mv of $nw witnesses moved on $tgt"
        done
        o=$(oracle_step)
        case "$o" in
        OWED) ostate="oracle OWED" ;;
        0\ *) ostate="oracle green ($o)" ;;
        *)    ostate="oracle RED ($o)"; [ -n "$red" ] || red="the oracle: $o" ;;
        esac
        if [ -n "$red" ]; then
            echo "PLANT $id RED   ($(plant_detector "$id"); $ostate): $red"
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
    done
    # the lever's reach (plant C's witness): every witness's scan moved
    read -r mv nw < <(moved "$tgt")
    echo "lever $tgt: $mv of $nw witnesses' text scan moved (default vs run-tie-left)"
    floor "$tgt lever witnesses read" "$nw" "$FLOOR_WITNESSES"
    if [ "$mv" = "$nw" ]; then tp=$((tp + 1)); else note "$tgt: only $mv of $nw witnesses' scan moved under run-tie-left"; fi
done

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
