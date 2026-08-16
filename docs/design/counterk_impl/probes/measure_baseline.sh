#!/usr/bin/env bash
# docs/design/counterk_impl/probes/measure_baseline.sh — every MEASURED claim in
# counterk_design.md, reproduced from the committed tree in one run.
#
# R24 M-F4: a number that cannot be re-run is not a measurement. Each block
# below prints the table the note quotes, in the note's own order.
#
# Usage: measure_baseline.sh
# Env:   PCREC (default build/pcrec), CC (default cc), TIMEOUT (default 120)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
TMO="${TIMEOUT:-120}"
OUT=$(mktemp -d "${TMPDIR:-/tmp}/ckbase.XXXXXX")
trap 'rm -rf "$OUT"' EXIT

[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }

stamp () {  # stamp <file> <macro>   -> the hex value, or "-"
    grep -o "$2 0x[0-9a-f]*" "$1" 2>/dev/null | head -1 | grep -o '0x.*' || echo -
}

echo "== source =="
echo "repo    $ROOT_DIR"
echo "commit  $(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo '?')"
echo "gcc     $($CC --version | head -1)"
echo "date    $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo

# ---------------------------------------------------------------------------
# §1.2 -- a POSSESSIFIED bounded repeat still replicates.
# The claim the ladder's order invites and that this refutes: possessification
# is the cheapest rung by FRAMES and buys almost nothing in emitted SIZE, so
# possessify-first hands the quantifier to a rung that replicates it anyway.
# `-fno-revdet` on every row, because otherwise the reverse-deterministic rung
# takes these patterns and the frames rung is never reached.
# ---------------------------------------------------------------------------
echo "== S1.2: possessified bounded repeats still replicate =="
printf '%-18s %-30s %-8s %s\n' pattern flags lines VM_STRATS
for pat in '((a)|b){0,64}c' '((a)|b){0,16}c'; do
    for flags in "-fno-revdet" "-fno-revdet -fno-possessify"; do
        # shellcheck disable=SC2086
        if timeout "$TMO" "$PCREC" -p rx --engine=vm $flags \
               -o "$OUT/p.c" -- "$pat" 2>"$OUT/err"; then
            printf '%-18s %-30s %-8s %s\n' "$pat" "$flags" \
                   "$(wc -l < "$OUT/p.c")" "$(stamp "$OUT/p.c" VM_STRATS)"
        else
            printf '%-18s %-30s %s\n' "$pat" "$flags" \
                   "REFUSED: $(head -c 90 "$OUT/err" | tr -d '\n')"
        fi
    done
done
echo

# ---------------------------------------------------------------------------
# §2.2 -- the frame field the counter could have used is FREE, and is still the
# wrong mechanism (the note's counterexample is `(a|b){0,4}c`). Recorded so the
# refutation is against a measured alternative rather than an assumed cost.
# ---------------------------------------------------------------------------
echo "== S2.2: the resume frame's tail padding =="
cat > "$OUT/pad.c" <<'EOF'
#include <stdio.h>
#include <stddef.h>
typedef struct { const void *k; size_t pos; unsigned mark; }             F;
typedef struct { const void *k; size_t pos; unsigned mark; unsigned it; } Fit;
typedef struct { const void *k; size_t pos; unsigned mark; int id; }     Ftr;
int main(void) {
    printf("bt[] element today            %zu bytes\n", sizeof(F));
    printf("bt[] element + unsigned it    %zu bytes\n", sizeof(Fit));
    printf("bt[] element + --trace int id %zu bytes\n", sizeof(Ftr));
    return 0;
}
EOF
"$CC" -O2 -o "$OUT/pad" "$OUT/pad.c" && "$OUT/pad"
echo

# ---------------------------------------------------------------------------
# §8.1 / §8.5 -- the endgame cell must decline BOTH earlier rungs, which is
# what makes it counter-K's own rather than rung-select's. RUNGS 0x2 is
# frames-bounded; 0x8 is revdet. STRATS 0x2 is backtracking; 0x1 possessive.
# ---------------------------------------------------------------------------
echo "== S8.1: which candidate bodies reach the frames-bounded rung =="
printf '%-20s %-8s %-8s %-10s %s\n' pattern lines VM_RUNGS VM_STRATS note
for pat in '((a)|ab){0,16}c' '((ab)|b){0,16}b' '((a)|b){0,16}a' \
           '((aa?)|b){0,16}c' '(a(b|c)?){0,16}bd'; do
    if timeout "$TMO" "$PCREC" -p rx --engine=vm -o "$OUT/p.c" -- "$pat" \
           2>"$OUT/err"; then
        r=$(stamp "$OUT/p.c" VM_RUNGS)
        printf '%-20s %-8s %-8s %-10s %s\n' "$pat" "$(wc -l < "$OUT/p.c")" \
               "$r" "$(stamp "$OUT/p.c" VM_STRATS)" \
               "$([ "$r" = 0x2 ] && echo 'counter-K candidate' || echo 'taken by an earlier rung')"
    else
        printf '%-20s REFUSED: %s\n' "$pat" "$(head -c 90 "$OUT/err" | tr -d '\n')"
    fi
done
echo

echo "== S8.5: the acceptance cells, as they behave TODAY =="
# NOTE on the body choice: the mandatory-phase rows MUST use a body that
# declines revdet too. `((a)|bc){4000}` compiles in 299 lines TODAY -- an exact
# count over a reverse-deterministic body is already the rung-select landing's,
# not counter-K's. `(a|ab)` is the body that declines both earlier rungs.
for pat in '((a)|ab){0,4000}c' '((a)|b){0,4000}c' \
           '((a)|ab){4000}' '((a)|ab){4000,}' '((a)|ab){8,4000}c' \
           '((a)|bc){4000}'; do
    if timeout "$TMO" "$PCREC" -p rx --engine=vm -o "$OUT/p.c" -- "$pat" \
           2>"$OUT/err"; then
        printf '%-20s COMPILES, %s lines\n' "$pat" "$(wc -l < "$OUT/p.c")"
    else
        printf '%-20s REFUSED: %s\n' "$pat" "$(head -c 110 "$OUT/err" | tr -d '\n')"
    fi
done
echo

# ---------------------------------------------------------------------------
# §8.1 -- the cost baseline the trail arithmetic is predicted against.
# ---------------------------------------------------------------------------
echo "== S8.1: stamped capacities on the endgame body at N=16 =="
if timeout "$TMO" "$PCREC" -p rx --engine=vm --emit-ir -- '((a)|ab){0,16}c' \
       2>/dev/null | grep -E '^; (capacities|max replicas|rungs|strategies)'; then :; fi
