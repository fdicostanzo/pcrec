#!/usr/bin/env bash
# docs/design/counterk_impl/probes/work_charge.sh — counterk_design.md §10.5.4's
# CALIBRATION: does the shipped work bound consume exactly the number §7.4
# predicted?
#
# WHY THIS IS A SECOND INSTRUMENT AND NOT A RERUN OF THE FIRST. `step_charge.sh`
# answers "how much uncharged work is there" by SED-INSTRUMENTING the emitted
# artifact — it adds counters at the fail label, at both cut spellings and at the
# span scan, then runs a build that charges nothing. This probe answers "how much
# does the shipped bound actually charge" by running the REAL artifact, with the
# real charge, and finding the budget at which it gives up. It instruments
# NOTHING. It patches NOTHING. Its only input is `--work-budget=N` and the exit
# status.
#
# That independence is the point, and it is this project's own recorded lesson
# about controls that share a source with what they control. If the charge were
# calibrated by the same instrumentation that predicted it, agreement would be
# near-tautological — the sed anchors and the emitter's charge sites would be two
# renderings of one belief. Here the predicted number comes from an instrumented
# non-charging build and the measured number comes from an uninstrumented
# charging one, and they are computed by different code on different runs.
#
# WHAT IS PREDICTED, and from what. The possessified cursor rung scans forward
# once per start position and never retreats, so over a subject of n bytes that
# an unanchored search restarts at every position the frameless scan performs
# n + (n-1) + ... + 1 = n(n+1)/2 iterations, each one work unit under §7.4's
# rule. That closed form is what makes this a PIN rather than a fishing trip:
# the number is derived before the run, not read off it.
#
# HOW A CELL IS DECIDED. Three points, not a search, because the prediction is
# exact: at `predicted` the artifact must COMPLETE, at `predicted - 1` it must
# return RX_ERR_WORK, and the pair together says the boundary is exactly there.
# One point alone proves nothing — an artifact that never gives up passes a
# "completes" test at every budget, which is the vacuous-green shape §8.4 was
# rewritten to avoid. On a failed pin, --bisect finds the TRUE boundary and
# reports it, so a wrong prediction produces a number to think about rather than
# a bare red.
#
# THE NON-VACUITY CONTROL, and it is not optional. Row `mixed` is a shape whose
# frames all reach the fail label (§7.4's third class): it is charged nothing,
# so it must complete at a budget of 1. A probe that exhibits only the cases its
# rule fires on is not evidence that the rule has a boundary — `clamp_arith.py`
# carries the same rule and the same sentence.
#
# Usage: work_charge.sh [--bisect]
# Env:   PCREC (default build/pcrec), CC (default cc), TIMEOUT (default 300)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
TMO="${TIMEOUT:-300}"
BISECT=0
[ "${1:-}" = "--bisect" ] && BISECT=1

[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }

OUT=$(mktemp -d "${TMPDIR:-/tmp}/ckwork.XXXXXX")
trap 'rm -rf "$OUT"' EXIT

fails=0

# Build a subject of `size` bytes of `fill`, then run the artifact on it.
# Prints one of: match / nomatch / work / steps / frames / giveup N / timeout.
cat > "$OUT/driver.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.c"
/* driver SIZE FILL */
int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: driver SIZE FILL\n"); return 2; }
    size_t size = strtoul(argv[1], NULL, 10);
    const char *fill = argv[2];
    size_t fl = strlen(fill);
    if (fl == 0) { fprintf(stderr, "empty fill\n"); return 2; }
    unsigned char *s = malloc(size + 1);
    if (!s) { fprintf(stderr, "oom\n"); return 2; }
    for (size_t i = 0; i < size; i++) s[i] = (unsigned char)fill[i % fl];
    s[size] = 0;
    {
        ptrdiff_t caps[RX_NCAPS][2];
        int rc = rx_search(s, size, 0, caps);
        if (rc == 1)               puts("match");
        else if (rc == 0)          puts("nomatch");
        else if (rc == RX_ERR_WORK)   puts("work");
        else if (rc == RX_ERR_STEPS)  puts("steps");
        else if (rc == RX_ERR_FRAMES) puts("frames");
        else                       printf("giveup %d\n", rc);
    }
    free(s);
    return 0;
}
EOF

# compile_at BUDGET PATTERN EXTRA...  -> $OUT/run
compile_at() {
    local budget="$1" pat="$2"; shift 2
    rm -f "$OUT/gen.c" "$OUT/gen.h" "$OUT/run"
    "$PCREC" -p rx --engine=vm --work-budget="$budget" "$@" \
             -o "$OUT/gen.c" "$pat" >/dev/null 2>&1 || return 1
    "$CC" -O2 -I"$OUT" -o "$OUT/run" "$OUT/driver.c" >/dev/null 2>&1 || return 1
    return 0
}

# verdict BUDGET PATTERN SIZE FILL EXTRA... -> prints the artifact's verdict
verdict() {
    local budget="$1" pat="$2" size="$3" fill="$4"; shift 4
    compile_at "$budget" "$pat" "$@" || { echo "BUILDFAIL"; return; }
    timeout "$TMO" "$OUT/run" "$size" "$fill" 2>/dev/null || echo "timeout"
}

# ---- the cells -------------------------------------------------------------
printf '== work_charge: counterk_design.md §10.5.4 (settlement 4 calibration) ==\n'
printf 'commit         %s\n' "$(cd "$ROOT_DIR" && git rev-parse --short HEAD 2>/dev/null || echo '?')"
printf 'gcc            %s\n' "$($CC --version 2>/dev/null | head -1)"
printf 'default budget %s (VM_DEFAULT_WORK_BUDGET, src/gen/emit_vm.c; D49)\n' 1000000000
printf '\n'
printf 'A unit is one piece of otherwise-uncharged forward work: one frame\n'
printf 'discarded at a cut, one iteration of a frameless scan. The step budget is\n'
printf 'a SEPARATE counter and is not consulted here.\n\n'
printf '%-34s %8s %14s %14s %-9s %-9s\n' \
       shape n predicted at_predicted at_pred-1 verdict

pin_cell() {
    # pin_cell LABEL PATTERN SIZE FILL PREDICTED EXTRA...
    local label="$1" pat="$2" size="$3" fill="$4" pred="$5"; shift 5
    local at_p at_m1 ok
    at_p=$(verdict "$pred" "$pat" "$size" "$fill" "$@")
    at_m1=$(verdict "$((pred - 1))" "$pat" "$size" "$fill" "$@")
    if [ "$at_p" != "work" ] && [ "$at_p" != "BUILDFAIL" ] \
       && [ "$at_m1" = "work" ]; then
        ok=PIN
    else
        ok=FAIL; fails=$((fails + 1))
    fi
    printf '%-34s %8s %14s %14s %-9s %-9s\n' \
           "$label" "$size" "$pred" "$at_p" "$at_m1" "$ok"
    if [ "$ok" = FAIL ] && [ "$BISECT" = 1 ]; then
        bisect_cell "$pat" "$size" "$fill" "$pred" "$@"
    fi
}

# Find the smallest budget at which the artifact does NOT report `work`.
bisect_cell() {
    local pat="$1" size="$2" fill="$3" pred="$4"; shift 4
    local lo=1 hi=$((pred * 4 + 16)) mid v
    if [ "$(verdict "$hi" "$pat" "$size" "$fill" "$@")" = "work" ]; then
        printf '    bisect: still giving up at %s -- boundary is above the search range\n' "$hi"
        return
    fi
    while [ "$lo" -lt "$hi" ]; do
        mid=$(( (lo + hi) / 2 ))
        v=$(verdict "$mid" "$pat" "$size" "$fill" "$@")
        if [ "$v" = "work" ]; then lo=$((mid + 1)); else hi=$mid; fi
    done
    printf '    bisect: TRUE boundary is %s (predicted %s, off by %s)\n' \
           "$lo" "$pred" "$((lo - pred))"
}

# 1-2. The frameless scan, the class §7.4's measurement priced. n(n+1)/2.
pin_cell 'possessified cursor ([a-z]+)9'   '([a-z]+)9'  1000   a $(( 1000 * 1001 / 2 ))
pin_cell 'possessified cursor ([a-z]+)9'   '([a-z]+)9' 10000   a $(( 10000 * 10001 / 2 ))

# 3. The CUT class, the other half of the charged population. The count is not
#    a closed form the way the scan's is -- it depends on how many frames each
#    iteration leaves behind -- so this cell is BISECT-ONLY by construction and
#    is reported rather than pinned. Reporting a measured number the note can
#    quote is worth more here than a prediction invented to have something to
#    pin against.
printf '\n-- CUT class: measured, not predicted (see the comment in this script) --\n'
if compile_at 1000000000 '((a)|b){0,4}d' -fno-revdet; then
    bisect_cell '((a)|b){0,4}d' 10000 a 200000 -fno-revdet
else
    printf '    BUILDFAIL\n'; fails=$((fails + 1))
fi

# 4. NON-VACUITY CONTROL: a shape charged NOTHING must survive a budget of 1.
printf '\n-- non-vacuity control --\n'
v=$(verdict 1 '(a(b|c)?){0,4}d' 10000 a -fno-revdet)
if [ "$v" = "work" ] || [ "$v" = "BUILDFAIL" ]; then
    printf '%-58s %-9s\n' 'mixed (a(b|c)?){0,4}d at budget 1 charges nothing' "FAIL ($v)"
    fails=$((fails + 1))
else
    printf '%-58s %-9s\n' 'mixed (a(b|c)?){0,4}d at budget 1 charges nothing' "OK ($v)"
fi

# 5. The gate is REACHABLE only where the prefilter is off (§7.5). On the
#    DEFAULT path the DFA answers and the VM is never entered, so the same
#    pattern and subject must complete at a budget of 1.
v=$(compile_at 1 '([a-z]+)9' >/dev/null 2>&1; \
    rm -f "$OUT/gen.c" "$OUT/gen.h" "$OUT/run"; \
    "$PCREC" -p rx --work-budget=1 -o "$OUT/gen.c" '([a-z]+)9' >/dev/null 2>&1 \
      && "$CC" -O2 -I"$OUT" -o "$OUT/run" "$OUT/driver.c" >/dev/null 2>&1 \
      && timeout "$TMO" "$OUT/run" 10000 a 2>/dev/null || echo BUILDFAIL)
if [ "$v" = "work" ] || [ "$v" = "BUILDFAIL" ]; then
    printf '%-58s %-9s\n' 'DEFAULT path (prefilter on) at budget 1' "FAIL ($v)"
    fails=$((fails + 1))
else
    printf '%-58s %-9s\n' 'DEFAULT path (prefilter on) at budget 1' "OK ($v)"
fi

printf '\n'
if [ "$fails" -eq 0 ]; then
    printf 'ALL CELLS OK\n'
else
    printf '%d CELL(S) FAILED -- re-run with --bisect for the true boundaries\n' "$fails"
fi
exit $(( fails > 0 ))
