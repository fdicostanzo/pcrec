#!/usr/bin/env bash
# docs/design/counterk_impl/probes/step_charge.sh — counterk_design.md §7's
# measurement. It has now refuted TWO proposals, the note's own both times.
#
# ROUND 1 (b0b9b8c) refuted the E-5-shaped ENTRY charge: entries and steps are
# the same number at every size, so an entry charge halves a crossover that is
# three orders of magnitude out.
#
# ROUND 2 (R25 finding 17) refuted the replacement's PREDICATE. §7.3 said
# "charge loops that push no per-iteration resume frame", justified by "a loop
# that pushes one is already charged through the fail label". Those coincide
# only when every pushed frame is POPPED THROUGH THE FAIL LABEL — and RX_CUT
# truncates `w->btn` with no charge at all. So the revdet forward scan and
# counter-K's own possessive arm PUSH per iteration and CUT, landing in the
# EXCLUDED class while charging nothing in fact. Round 1's probe could not see
# it: its single shape `([a-z]+)9` is the possessified CURSOR rung, the one
# genuinely frameless member, so the class boundary the rule turns on was
# invisible to the instrument that priced the rule.
#
# WHAT THIS VERSION MEASURES, and why these three quantities. The charged class
# is defined by WHAT THE FAIL LABEL DOES NOT SEE, so the probe counts all three
# populations separately, each at its real site in the emitted artifact:
#
#   steps  `rx_fail:` resumptions           — what the budget is charged TODAY
#   cut    frames discarded by RX_CUT       — pushed, then made invisible to
#                                             the fail label. `w->btn - stv[slot]`
#                                             at the cut IS the count, exactly
#   scan   frameless span-loop iterations   — never pushed at all, so neither
#                                             the fail label nor a cut sees them
#
# `cut + scan` is the uncharged work. `steps` is the charged work. A rule that
# claims to cover the blind spot must cover both of the first two, and §7.3's
# predicate covered only the second.
#
# The step budget is raised out of the way for every run — an artifact that
# gives up early UNDERCOUNTS the very thing being counted — and the DEFAULT
# budget is applied on paper afterwards.
#
# INSTRUMENTATION, and its verification. FOUR sed anchors, each counted and
# REPORTED in the `sites` column (fail/cut/scan), because a probe that
# silently instruments nothing is the check-design failure this project has
# recorded twice. A DFA-only artifact legitimately has none of the three and
# reports zeros rather than failing.
#   - `rx_fail:` label                       -> steps
#   - the RX_CUT macro body                  -> cut (possessified rungs)
#   - `w->btn = rx_rvN_mk;`                  -> cut (REVDET, which never uses
#                                                    the macro -- missing this
#                                                    anchor produced a wrong zero)
#   - the forward span-scan `while` line     -> scan
# The scan shapes here are all stride 1, so `rx_cur - pos` IS the iteration
# count; a general instrument would divide by the stride.
#
# Usage: step_charge.sh [--full]
# Env:   PCREC (default build/pcrec), CC (default cc), TIMEOUT (default 300)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
TMO="${TIMEOUT:-300}"
BIG_BUDGET=1000000000000        # out of the way; the DEFAULT is applied on paper
DEFAULT_BUDGET=1000000          # VM_DEFAULT_STEP_BUDGET, src/gen/emit_vm.c
FULL=0
[ "${1:-}" = "--full" ] && FULL=1

OUT=$(mktemp -d "${TMPDIR:-/tmp}/ckstep.XXXXXX")
trap 'rm -rf "$OUT"' EXIT
[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }

cat > "$OUT/driver.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static unsigned long long rxprobe_steps = 0, rxprobe_cut = 0, rxprobe_scan = 0;
#include "gen.c"
/* driver SIZE FILL TAIL WHERE */
int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage: driver SIZE FILL TAIL WHERE\n"); return 2; }
    size_t size = strtoul(argv[1], NULL, 10);
    const char *fill = argv[2], *tail = argv[3], *where = argv[4];
    size_t fl = strlen(fill), tl = strlen(tail);
    if (fl == 0) { fprintf(stderr, "empty fill\n"); return 2; }
    int with_tail = strcmp(where, "none") != 0;
    unsigned char *s = malloc(size + tl + 1);
    if (!s) { fprintf(stderr, "oom\n"); return 2; }
    size_t off = 0;
    if (with_tail && strcmp(where, "head") == 0) { memcpy(s, tail, tl); off = tl; }
    for (size_t i = 0; i < size; i++) s[off + i] = (unsigned char)fill[i % fl];
    off += size;
    if (with_tail && strcmp(where, "tail") == 0) { memcpy(s + off, tail, tl); off += tl; }
    ptrdiff_t caps[RX_NCAPS][2];
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    int rc = rx_search(s, off, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("%s %zu %llu %llu %llu %.3f\n",
           rc == 1 ? "match" : rc == 0 ? "nomatch"
                  : rc == RX_ERR_STEPS ? "STEPS" : "FRAMES",
           off, rxprobe_steps, rxprobe_cut, rxprobe_scan,
           (double)(t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9);
    free(s);
    return 0;
}
EOF

# measure <label> <pattern> <flags> <size> <fill> <tail> <where>
measure () {
    lab=$1; pat=$2; flg=$3; size=$4; fill=$5; tail=$6; where=$7
    path=${flg:-DEFAULT}
    rm -f "$OUT/gen.c"
    # shellcheck disable=SC2086
    if ! timeout "$TMO" "$PCREC" -p rx $flg --step-budget=$BIG_BUDGET \
             -o "$OUT/gen.c" -- "$pat" >/dev/null 2>&1; then
        printf '%-11s %-22s %-24s %-8s REFUSED\n' "$lab" "$pat" "$path" "$size"; return; fi

    # --- the charge sites --------------------------------------------------
    # THERE ARE TWO WAYS TO CUT, and instrumenting only one is how the first
    # version of this block reported a confident zero. `RX_CUT` is the macro
    # the possessified rungs use; the REVDET rung cuts by assigning `w->btn`
    # from its own per-loop local (`w->btn = rx_rvN_mk;`) and never touches the
    # macro. Both are anchored; the emitted `sites` column below reports how
    # many of each were instrumented, so "0 discarded" is distinguishable from
    # "0 instrumented" -- which is the distinction that produced a wrong
    # reading here once already.
    sed -i 's/^rx_fail: __attribute__((unused));$/& rxprobe_steps++;/' "$OUT/gen.c"
    sed -i 's|^        w->btn = (unsigned)stv\[(slot_)\];\( *\)\\$|        rxprobe_cut += (unsigned long long)(w->btn - (unsigned)stv[(slot_)]); w->btn = (unsigned)stv[(slot_)];\1\\|' "$OUT/gen.c"
    sed -i 's|^\( *\)w->btn = \(rx_[a-z0-9_]*\);$|\1rxprobe_cut += (unsigned long long)(w->btn - \2); w->btn = \2;|' "$OUT/gen.c"
    sed -i 's|^\( *\)\(while (rx_cur + [0-9]* <= n.*{ rx_cur += [0-9]*; }\)$|\1\2 rxprobe_scan += (unsigned long long)(rx_cur - pos);|' "$OUT/gen.c"

    nf=$(grep -c 'rxprobe_steps++;' "$OUT/gen.c" || true)
    nc=$(grep -c 'rxprobe_cut +=' "$OUT/gen.c" || true)
    ns=$(grep -c 'rxprobe_scan +=' "$OUT/gen.c" || true)
    isvm=$(grep -c '^rx_fail:' "$OUT/gen.c" || true)
    # A DFA-only artifact has no fail label, no cut site and no span loop --
    # a real answer (zero VM work), not a broken probe. Anything else is.
    if [ "$isvm" -gt 0 ] && [ "$nf" -ne 1 ]; then
        printf '%-11s %-22s %-24s %-8s INSTRUMENTATION FAILED (fail=%s cut=%s scan=%s)\n' \
               "$lab" "$pat" "$path" "$size" "$nf" "$nc" "$ns"; return; fi
    sites="$nf/$nc/$ns"

    if ! timeout "$TMO" "$CC" -O2 -I"$OUT" -o "$OUT/drv" "$OUT/driver.c" 2>"$OUT/cc.err"; then
        printf '%-11s %-22s %-24s %-8s CC-FAILED: %s\n' "$lab" "$pat" "$path" "$size" \
               "$(head -1 "$OUT/cc.err")"; return; fi
    if ! res=$(timeout "$TMO" "$OUT/drv" "$size" "$fill" "$tail" "$where" 2>/dev/null); then
        printf '%-11s %-22s %-24s %-8s TIMEOUT >%ss -- A FINDING, recorded, not re-run longer\n' \
               "$lab" "$pat" "$path" "$size" "$TMO"; return; fi
    # shellcheck disable=SC2086
    set -- $res
    verdict=$1; n=$2; steps=$3; cut=$4; scan=$5; secs=$6
    unch=$((cut + scan))
    printf '%-11s %-22s %-24s %-8s %-8s %-7s %-8s %-12s %-12s %-12s %s\n' \
           "$lab" "$pat" "$path" "$n" "$verdict" "$sites" "$secs" "$steps" "$cut" "$scan" "$unch"
}

header () {
    printf '\n%-11s %-22s %-24s %-8s %-8s %-7s %-8s %-12s %-12s %-12s %s\n' \
           block pattern path bytes verdict sites seconds steps_today cut_frames scan_iters UNCHARGED
}

echo "== step_charge: counterk_design.md §7 =="
echo "commit         $(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo "gcc            $($CC --version | head -1)"
echo "run budget     $BIG_BUDGET (raised, so the counts are not truncated)"
echo "default budget $DEFAULT_BUDGET (VM_DEFAULT_STEP_BUDGET -- applied on paper)"
echo
echo "steps_today = fail-label resumptions: what the budget charges TODAY"
echo "cut_frames  = frames RX_CUT discarded: pushed, then hidden from the fail label"
echo "scan_iters  = frameless span-loop iterations: never pushed at all"
echo "UNCHARGED   = cut + scan, the work no budget sees. THIS is what §7 must cover."

Q1='([a-z]+)9'                      # possessified CURSOR rung: frameless
Q2='([a-z]+)-([0-9]+)9'
Q4='([a-z]+)-([0-9]+)-([a-z]+)-([0-9]+)9'
# B2's witnesses. THE LOOP MUST BE REACHABLE AT EVERY START POSITION: the
# first draft prefixed these with `(x)`, which never matches a subject of 'a',
# so the loop never ran and every row read a confident zero. Same failure as
# round 1, one level down -- a probe whose subject cannot reach the construct
# it is pricing measures the subject.
QP='((a)|b){0,4}d'                  # vm_poss_chain: 0x2 frames-bounded / 0x1 possessive
QR='((a)|b){0,4}d'                  # revdet at default routing: 0x8 / 0x1
QN='(a(b|c)?){0,4}d'                # mixed strategies in one artifact: 0x2 / 0x3

if [ "$FULL" -eq 1 ]; then SZA="1000 10000 100000 1000000"; SZB="10000 50000 100000"
else                       SZA="1000 100000 1000000";       SZB="10000 50000 100000"; fi

# ===========================================================================
# BLOCK A -- THE COST of charging, on legitimate linear work. Fill '.' is
# rejected by every body's first byte, so each start position fails in O(1).
# ===========================================================================
echo
echo "-- BLOCK A: legitimate linear work (what any charge would cost) --"
header
for pat in "$Q1" "$Q2" "$Q4"; do
  for sz in $SZA; do measure LINEAR "$pat" "--engine=vm" "$sz" "." "" none; done
done
for sz in $SZA; do measure LINEAR "$Q1" "" "$sz" "." "" none; done

# ===========================================================================
# BLOCK B -- THE BLIND SPOT, across the CLASS BOUNDARY finding 17 turns on.
# Round 1 measured only the first row group -- the possessified cursor rung,
# the one genuinely frameless shape -- which is why the boundary was invisible.
# ===========================================================================
echo
echo "-- BLOCK B1: frameless (possessified CURSOR) -- scan_iters is the blind spot --"
header
for sz in $SZB; do
    measure QUADRATIC "$Q1" ""                            "$sz" "a" "" none
    measure QUADRATIC "$Q1" "--engine=vm"                 "$sz" "a" "" none
    measure CONTROL   "$Q1" "--engine=vm -fno-possessify" "$sz" "a" "" none
done

echo
echo "-- BLOCK B2: PUSH-then-CUT shapes -- cut_frames is the blind spot, and"
echo "   these are the shapes §7.3's withdrawn predicate EXCLUDED (finding 17) --"
header
for sz in 1000 10000; do
    measure POSSCHAIN "$QP" "--engine=vm -fno-revdet" "$sz" "a" "" none
    measure REVDET    "$QR" "--engine=vm"             "$sz" "a" "" none
    measure MIXED     "$QN" "--engine=vm -fno-revdet" "$sz" "a" "" none
done

echo
echo "-- BLOCK B3: the MATCH-SUCCEEDS rows (every row above is a nomatch) --"
header
measure MATCH "$Q1" "--engine=vm" 100000 "a" "9"   tail
measure MATCH "$Q1" ""            100000 "a" "9"   tail
measure MATCH "$QP" "--engine=vm -fno-revdet" 10000 "a" "d" tail
measure MATCH "$QR" "--engine=vm"             10000 "a" "d" tail

# ===========================================================================
# BLOCK C -- THE BLAST RADIUS. The prefilter picks start positions on the
# default path, so the VM is never entered and none of this is reachable.
# ===========================================================================
echo
echo "-- BLOCK C: is any of it reachable on the DEFAULT path? --"
header
for sz in 10000 100000 1000000; do measure DEFAULT "$Q1" "" "$sz" "a" "" none; done
echo
