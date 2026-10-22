#!/usr/bin/env bash
# tests/memfn/run_proof.sh — [MEMFN] R-26 (lane r26z1, MF_SITE_ABI 18): the
# kit's per-offset proof, prefix facts, context spans, absent rule, read
# floor and REPORT kind (tests/memfn/proof_check.c's header). Part `proof`
# of `make test-memfn-finder` (run_finder.sh); runnable alone.
#
#   1. proof_check against the kit (LIB, default build/libpcrec.a): families
#      A (refusals and their controls), B (the class) and C (C-PROOF and the
#      generated family, written to the work directory);
#   2. the same against the kit compiled -DMF_TRACE (every memfn/src/*.c), so
#      every define re-asks its class and checks, at every offset, that a
#      class searching nothing proves nothing and that proven0/proven_prev are
#      proven[0]/proven[-1] (Q-R17P-25, extended by R-26.4);
#   3. proof_run, the byte-loop oracle (proof_run.c), over the family the plain
#      kit rendered.
#
#   --plant NAME   the same run over a COPY of memfn/src with one planted
#                  defect (the six kit-side rows of R-26, S1221-S1226, and
#                  R-26.6's S1251-S1256 and the unnumbered ZK6/ZK7; the table
#                  below): the run must go red. Writes only the work
#                  directory. --plants runs them all and reports each.
#
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR.
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
LIB="${LIB:-$ROOT/build/libpcrec.a}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/proof.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# THE PLANTS: id, then FILE@@FROM@@TO (FILE under memfn/src; FROM replaced
# by TO, `\n` a newline, `\&` an ampersand). Each must make this run red.
plant_spec() {
    case "$1" in
    S1221) # a form claiming an untested offset (the class proves one past each run)
        echo 'compose.c@@long d = (long)t->offset + j;@@long d = (long)t->offset + j + (t->kind == MF_T_RUN);' ;;
    S1222) # an absent-SATISFIES candidate dropped (SATISFIES rendered as FAILS)
        echo 'generic.c@@if (p->span_class != MF_SPAN_CONTEXT || p->absent != MF_ABSENT_SATISFIES)@@if (1)' ;;
    S1223) # an absent-FAILS candidate yielded (every context item rendered SATISFIES)
        echo 'generic.c@@if (p->span_class != MF_SPAN_CONTEXT || p->absent != MF_ABSENT_SATISFIES)@@if (p->span_class != MF_SPAN_CONTEXT)' ;;
    S1224) # a proof bit set only by a SIMD layer (C-PROOF)
        echo 'compose.c@@    /* proven0 and proven_prev are COPIES@@    if (!(s->policy \& MF_P_PORTABLE_ONLY)) out->proven[0 - MF_PROOF_LO][0] \&= 0xFE;\n    /* proven0 and proven_prev are COPIES' ;;
    S1225) # an over-filter on an OPTIONAL position (an OPTIONAL SET term tests one member fewer)
        echo 'generic.c@@            if (tm->kind == MF_T_SET) {\n                if (member_test(rc, b, tm, id, bx)) {@@            if (tm->kind == MF_T_SET) {\n                mf_term nt = *tm;\n                for (int q = 0; tm->need == MF_OPTIONAL \&\& q < 256; q++)\n                    if (nt.set[q >> 3] >> (q \& 7) \& 1) { nt.set[q >> 3] \&= (uint8_t)~(1u << (q \& 7)); break; }\n                if (member_test(rc, b, \&nt, id, bx)) {' ;;
    S1226) # an UNSTATED field accepted (`absent` UNSTATED read as FAILS)
        echo 'compose.c@@    if (p->absent == MF_ABSENT_UNSTATED)\n        return@@    if (0)\n        return' ;;
    # R-26.6 (lane r26zk): the REPORT row and the preview. S1251-S1256 are
    # mech rows (ids reserved by main); ZK6/ZK7 are plants with no id yet.
    S1256) # the REPORT row applies without its exactness fact
        echo 'finder.c@@{ "RPT", FD_FIND, KN_P, SF_SPAN0 | SF_PROOF_EXACT, 0,@@{ "RPT", FD_FIND, KN_P, SF_SPAN0, 0,' ;;
    S1255) # the exactness test compares span 0's offsets only (d >= 0)
        echo 'compose.c@@    return !memcmp(req, c.proven, sizeof req);@@    return !memcmp(req[-MF_PROOF_LO], c.proven[-MF_PROOF_LO], sizeof req - (size_t)(-MF_PROOF_LO) * 32);' ;;
    S1252) # mf_preview accepted twice
        echo 'compose.c@@    if (art->preview)\n        return kit_fail(art, "mf_preview: called twice@@    if (0)\n        return kit_fail(art, "mf_preview: called twice' ;;
    S1251) # mf_preview accepted after the first define
        echo 'compose.c@@    if (art->nsites)\n        return kit_fail(art, "mf_preview: called after@@    if (0)\n        return kit_fail(art, "mf_preview: called after' ;;
    S1253) # mf_preview accepts any step a row names (B4, B1, ...)
        echo 'finder.c@@        if (strcmp(step, fd_previews[i])) continue;@@        if (0) continue;' ;;
    ZK6) # the preview leaks: the REPORT row decides on every art
        echo 'finder.c@@            return art->preview \&\& !strcmp(art->preview, r->step);@@            return 1;' ;;
    ZK7) # a preview art routes nothing (the REPORT row never decides)
        echo 'finder.c@@            return art->preview \&\& !strcmp(art->preview, r->step);@@            return 0;' ;;
    S1254) # a `--memfn=` spelling reaches the preview (an options.def row)
        echo 'options.def@@MF_OPT("vrun-w32", MF_OPT_DENY,@@MF_OPT("preview", MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR, "plant")\nMF_OPT("vrun-w32", MF_OPT_DENY,' ;;
    *) return 1 ;;
    esac
}
PLANTS="S1221 S1222 S1223 S1224 S1225 S1226 S1251 S1252 S1253 S1254 S1255 S1256 ZK6 ZK7"

fail_setup() { echo "FAIL: $1"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }

# kit_objs SRCDIR OUTDIR [FLAGS...]: every kit source compiled into OUTDIR.
kit_objs() {
    local src="$1" out="$2"; shift 2
    mkdir -p "$out"
    for s in "$src"/*.c; do
        "$CC" -std=gnu11 -O1 "$@" -I"$ROOT/memfn/include" -c -o "$out/$(basename "${s%.c}").o" "$s" \
            || return 1
    done
}

# one_run TAG KIT: build proof_check against KIT (an archive or an object
# list), generate, build the oracle, run both. Logs in $WORK/TAG.*.
one_run() {
    local tag="$1"; shift
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$ROOT/memfn/include" -I"$ROOT/tests/memfn" \
        "$ROOT/tests/memfn/proof_check.c" "$@" -o "$WORK/$tag.chk" 2> "$WORK/$tag.build" \
        || { echo "FAIL: $tag: proof_check does not build"; cat "$WORK/$tag.build"; return 1; }
    mkdir -p "$WORK/$tag.gen"
    "$WORK/$tag.chk" --gen "$WORK/$tag.gen" > "$WORK/$tag.chk.log" 2>&1
    local rc1=$?
    "$CC" -std=gnu11 -O1 -I"$ROOT/tests/memfn" "$ROOT/tests/memfn/proof_run.c" \
        "$WORK/$tag.gen/proof_sites.c" -o "$WORK/$tag.run" 2> "$WORK/$tag.runbuild" \
        || { echo "FAIL: $tag: the generated family does not compile"; head -20 "$WORK/$tag.runbuild"; return 1; }
    "${TIMEOUT_BIN:-timeout}" 600 "$WORK/$tag.run" > "$WORK/$tag.run.log" 2>&1
    local rc2=$?
    return $(( rc1 || rc2 ))
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
        c="$(counts "$WORK/plant_$id.chk.log") / $(counts "$WORK/plant_$id.run.log")"
        red=$(grep -h '^FAIL' "$WORK/plant_$id.chk.log" "$WORK/plant_$id.run.log" 2>/dev/null | head -1)
        if [ -n "$red" ]; then
            echo "PLANT $id RED   (proof_check / proof_run passed failed: $c): $red"
        else
            echo "PLANT $id GREEN (NOT DETECTED; $c)"; bad=$((bad + 1))
        fi
    done
    [ "$bad" -eq 0 ]
    exit $?
fi

[ -f "$LIB" ] || fail_setup "$LIB not built (make all first)"
tp=0 tf=0
add() {   # add LOG LABEL
    read -r p f < <(counts "$1")
    if [ "$p" = x ] || [ "$f" = x ]; then echo "FAIL: $2 printed no counts"; tf=$((tf + 1)); return; fi
    tp=$((tp + p)); tf=$((tf + f))
    grep -h '^FAIL' "$1" | head -20
}
one_run plain "$LIB"
add "$WORK/plain.chk.log" "proof_check"
add "$WORK/plain.run.log" "proof_run"
grep -h '^C family\|^proof_run\|^absent cells' "$WORK/plain.chk.log" "$WORK/plain.run.log"
kit_objs "$ROOT/memfn/src" "$WORK/kt" -DMF_TRACE || fail_setup "the kit does not compile with -DMF_TRACE"
one_run traced "$WORK/kt"/*.o 2>/dev/null
add "$WORK/traced.chk.log" "proof_check (traced)"
add "$WORK/traced.run.log" "proof_run (traced)"
echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
