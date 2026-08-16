#!/usr/bin/env bash
# docs/design/counterk_impl/probes/step_charge.sh — counterk_design.md S7's owed
# measurement, and the one that REFUTED the fix it was written to size.
#
# THE QUESTION AS ASKED. S7 proposed charging one step at every quantifier's
# loop ENTRY -- the E-5-shaped fix-of-record the possessify and rung-select
# lanes both recorded as owed -- and asked what it would COST, since "forward
# progress is FREE" (engine_m4.md S4.2) would stop being true.
#
# WHAT THE NUMBERS SAID INSTEAD. Block B below measures ENTRIES and STEPS side
# by side on the exact shape the possessify lane reported, and they are the
# SAME NUMBER at every size (n+1 and n+1). The entry charge therefore does not
# restore the property it was written to restore: the defect is not that the
# loop charges NOTHING, it is that the charge is LINEAR while the work is
# QUADRATIC, and adding a second linear term moves the crossover by a factor of
# two against a gap of three orders of magnitude. See the note's S7.
#
# HOW THE COUNTING IS DONE, WITHOUT WRITING THE CHARGE. The charge does not
# exist and this lane writes no engine code before its panel reports. So both
# counters live in the EMITTED ARTIFACT, at the two REAL charge sites rather
# than at proxies for them: `--emit-ir`'s RUNGS section names the label each
# quantifier's `vm_rung_mark(v, entry, ...)` was called with, which IS the label
# S7 proposes to charge at, and `rx_fail:` is the one charge site that exists
# today. Every insertion is verified; a probe that silently instruments nothing
# is the check-design failure this project has recorded twice.
#
# The step budget is raised out of the way for every run -- an artifact that
# gives up early UNDERCOUNTS the very thing being counted -- and the DEFAULT
# budget is then applied on paper as a crossover.
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
static unsigned long long rxprobe_entries = 0, rxprobe_steps = 0;
#include "gen.c"
/* driver SIZE FILL TAIL WHERE
 *   WHERE = none -> fill only (no match; the whole subject is swept)
 *           head -> tail then fill (the match is found at the first attempt)
 *           tail -> fill then tail */
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
    printf("%s %zu %llu %llu %.3f\n",
           rc == 1 ? "match" : rc == 0 ? "nomatch"
                  : rc == RX_ERR_STEPS ? "STEPS" : "FRAMES",
           off, rxprobe_steps, rxprobe_entries,
           (double)(t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9);
    free(s);
    return 0;
}
EOF

# measure <pattern> <flags> <size> <fill> <tail> <where>
measure () {
    pat=$1; flg=$2; size=$3; fill=$4; tail=$5; where=$6
    lbl=${flg:-DEFAULT}
    rm -f "$OUT/gen.c"
    # shellcheck disable=SC2086
    if ! timeout "$TMO" "$PCREC" -p rx $flg --step-budget=$BIG_BUDGET \
             -o "$OUT/gen.c" -- "$pat" >/dev/null 2>&1; then
        printf '%-16s %-22s %-9s REFUSED\n' "$pat" "$lbl" "$size"; return; fi
    # shellcheck disable=SC2086
    labels=$(timeout "$TMO" "$PCREC" -p rx $flg --emit-ir -- "$pat" 2>/dev/null \
             | sed -n '/^RUNGS/,/^$/p' | sed -n 's/^  at L\([0-9]*\) .*/\1/p')
    want=0
    for L in $labels; do
        sed -i "s/^rx_L${L}: __attribute__((unused));\$/& rxprobe_entries++;/" "$OUT/gen.c"
        want=$((want + 1))
    done
    sed -i 's/^rx_fail: __attribute__((unused));$/& rxprobe_steps++;/' "$OUT/gen.c"
    got=$(grep -c 'rxprobe_entries++;' "$OUT/gen.c" || true)
    gots=$(grep -c 'rxprobe_steps++;' "$OUT/gen.c" || true)
    # A DFA-only artifact has no quantifier rows and no fail label, and that is
    # a real answer (zero VM work), not a broken probe -- so it is reported,
    # not failed. Any OTHER mismatch is an instrumentation failure.
    if [ "$want" -gt 0 ] && { [ "$got" -ne "$want" ] || [ "$gots" -ne 1 ]; }; then
        printf '%-16s %-22s %-9s INSTRUMENTATION FAILED (%s/%s entry, %s fail)\n' \
               "$pat" "$lbl" "$size" "$got" "$want" "$gots"; return; fi
    if ! timeout "$TMO" "$CC" -O2 -I"$OUT" -o "$OUT/drv" "$OUT/driver.c" 2>"$OUT/cc.err"; then
        printf '%-16s %-22s %-9s CC-FAILED: %s\n' "$pat" "$lbl" "$size" \
               "$(head -1 "$OUT/cc.err")"; return; fi
    if ! res=$(timeout "$TMO" "$OUT/drv" "$size" "$fill" "$tail" "$where" 2>/dev/null); then
        printf '%-16s %-22s %-9s TIMEOUT >%ss -- A FINDING, recorded, not re-run longer\n' \
               "$pat" "$lbl" "$size" "$TMO"; return; fi
    # shellcheck disable=SC2086
    set -- $res
    verdict=$1; n=$2; steps=$3; entries=$4; secs=$5
    total=$((steps + entries))
    now=$([ "$steps" -gt "$DEFAULT_BUDGET" ] && echo GIVES-UP || echo answers)
    aft=$([ "$total" -gt "$DEFAULT_BUDGET" ] && echo GIVES-UP || echo answers)
    printf '%-16s %-22s %-9s %-8s %-9s %-14s %-12s %-9s %s\n' \
           "$pat" "$lbl" "$n" "$verdict" "$secs" "$steps" "$entries" "$now" "$aft"
}

header () {
    printf '\n%-16s %-22s %-9s %-8s %-9s %-14s %-12s %-9s %s\n' \
           pattern path bytes verdict seconds steps_today entries_new today proposed
}

echo "== step_charge: counterk_design.md S7 =="
echo "commit         $(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo "gcc            $($CC --version | head -1)"
echo "run budget     $BIG_BUDGET (raised, so the counts are not truncated)"
echo "default budget $DEFAULT_BUDGET (VM_DEFAULT_STEP_BUDGET -- applied on paper)"
echo
echo "steps_today = fail-label resumptions, the ONE charge site that exists"
echo "entries_new = quantifier-entry visits, what S7's uniform charge would ADD"

Q1='([a-z]+)9'
Q2='([a-z]+)-([0-9]+)9'
Q4='([a-z]+)-([0-9]+)-([a-z]+)-([0-9]+)9'

# ===========================================================================
# BLOCK A -- THE COST. Fill '.' is rejected by every body's first byte, so
# every start position fails in O(1) and the whole search is LINEAR and
# legitimate. This is the case where a uniform charge could newly refuse honest
# work, and it also refutes the "q*n" cost model the note first assumed: a
# quantifier the attempt never REACHES is never entered, so entries do not
# scale with the quantifier count.
# ===========================================================================
echo
echo "-- BLOCK A: what the charge COSTS on legitimate linear work --"
header
if [ "$FULL" -eq 1 ]; then SZA="1000 10000 100000 1000000"; else SZA="1000 100000 1000000"; fi
for pat in "$Q1" "$Q2" "$Q4"; do
  for sz in $SZA; do measure "$pat" "--engine=vm" "$sz" "." "" none; done
done
for sz in $SZA; do measure "$Q1" "" "$sz" "." "" none; done
measure "$Q1" "--engine=vm" 1000000 "." "abc9" head
measure "$Q1" ""            1000000 "." "abc9" head

# ===========================================================================
# BLOCK B -- WHAT THE CHARGE WAS FOR, and the refutation. Fill 'a' is consumed
# by the body, so every start position scans to the end before failing: O(n^2)
# real work. `-fno-possessify` is the CONTROL and it is the whole argument --
# denying possessification restores one frame per iteration, so the pops make
# the step count quadratic and the budget fires early. The possessified rows
# are the blind spot the possessify lane reported (0.033/0.581/2.297 s at
# 10/50/100 KB), reproduced here with its counters visible.
# ===========================================================================
echo
echo "-- BLOCK B: the blind spot, with ENTRIES measured beside STEPS --"
header
if [ "$FULL" -eq 1 ]; then SZB="10000 50000 100000 1000000"; else SZB="10000 50000 100000"; fi
for sz in $SZB; do
    measure "$Q1" ""                            "$sz" "a" "" none
    measure "$Q1" "--engine=vm"                 "$sz" "a" "" none
    measure "$Q1" "--engine=vm -fno-possessify" "$sz" "a" "" none
done

# ===========================================================================
# BLOCK C -- THE BLAST RADIUS. The same pathological input on the DEFAULT path,
# where the DFA prefilter chooses the start positions. `--engine=vm` disables
# it deliberately (R21 E-6) precisely so the VM can be cross-checked against
# the DFA rather than echo it, which is what makes that path diagnostic.
# ===========================================================================
echo
echo "-- BLOCK C: is the pathology reachable on the DEFAULT path? --"
header
for sz in 10000 100000 1000000; do measure "$Q1" "" "$sz" "a" "" none; done
echo
