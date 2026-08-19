#!/bin/sh
# probe_gstart_prefilter.sh — [M6.2] WAVE D: does partial `\G` warrant a THIRD
# INSTANCE of D63's candidate-start prefilter?
#
# D63 charters ENG_ATTEMPT's candidate-start prefilter as a TOOL and names
# three instances: `(?m)^` (first, built at wave C), D8's `^`-on-some-branches
# shape (second, PREDICTED, gated on its own measurement), and **partial `\G`
# (third, wave D's population)** — each gated on its own measurement. This
# probe is that measurement. It is run whichever way it comes out, because
# D63's own text requires the number rather than the outcome.
#
# WHAT THE DERIVATION ACTUALLY ASKS, which is what decides this. D63's shipped
# derivation (`cand_from_live_seeds`, src/gen/emit_dfa.c) is over PREDECESSOR
# BYTES: an attempt at `start > startpos` enters `s1u[upc_of_class(s[start-1])]`,
# so a predecessor byte whose seeded start state is DEAD cannot begin a match
# and the attempt loop may skip it. Wave D's `s1g[]` family is deliberately NOT
# in that derivation — it is the state for the ONE attempt at `start ==
# startpos`, which is never skipped.
#
# So a partial-`\G` pattern's filterability is decided ENTIRELY by its
# `\G`-FREE branches, which is exactly what the shipped derivation already
# computes. The prediction this probe tests:
#
#   (P1) a partial-`\G` pattern whose `\G`-free branch is itself BOT-family
#        anchored gets a prefilter TODAY, from instance one, with no new code;
#   (P2) a partial-`\G` pattern whose `\G`-free branch is unanchored gets NONE,
#        and cannot: any predecessor byte can precede that branch, so the
#        candidate set is all 256 and `cand_derive` reports it unusable;
#   (P3) therefore a THIRD instance would have to derive over a DIFFERENT
#        quantity — the non-`\G` branches' FIRST-BYTE set at offset 0 — which
#        is D63's SECOND instance (the D8 shape), not a third.
#
# Column 3 is read off the ARTIFACT (`memchr` present in the emitted C), never
# off a compiler internal, so this probe measures what ships.
#
# Usage: sh probe_gstart_prefilter.sh   (from anywhere in the repo)
set -e
REPO=$(git rev-parse --show-toplevel)
PCREC="${PCREC:-$REPO/build/pcrec}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "== 1. THE CENSUS: which \\G shapes get a prefilter today =="
echo
printf '%-24s %-10s %-9s %s\n' 'pattern' 'class' 'prefilter' 'start dispatch'
printf '%-24s %-10s %-9s %s\n' '------------------------' '----------' '---------' '--------------------'

n_full=0; n_partial=0; n_partial_pre=0; n_partial_nopre=0
census() {   # census <class> <pattern>
    cls=$1; pat=$2
    "$PCREC" --features all -p rx -o "$WORK/g.c" -- "$pat" 2>/dev/null || {
        printf '%-24s %-10s %-9s %s\n' "$pat" "$cls" "REFUSED" "-"; return; }
    pre=no
    grep -q 'memchr' "$WORK/g.c" && pre=MEMCHR
    dis=two-way
    grep -q '(start == startpos)' "$WORK/g.c" && dis=three-way
    grep -q 'const size_t start_max = startpos' "$WORK/g.c" && dis='start_max=startpos'
    grep -q 'const size_t start_max = 0' "$WORK/g.c" && dis='start_max=0'
    printf '%-24s %-10s %-9s %s\n' "$pat" "$cls" "$pre" "$dis"
    case "$cls" in
      full)    n_full=$((n_full + 1)) ;;
      partial) n_partial=$((n_partial + 1))
               if [ "$pre" = "MEMCHR" ]; then n_partial_pre=$((n_partial_pre + 1))
               else n_partial_nopre=$((n_partial_nopre + 1)); fi ;;
    esac
}

# FULLY-\G: D63's own text already answers these — "fully-anchored and
# whole-pattern-\G shapes get nothing, one attempt already".
census full    '\Gfoo'
census full    '\G[a-z]+'
census full    '\Gabc|\Gxy'

# PARTIAL, \G-free branch UNANCHORED (P2's population).
census partial '\Gfoo|bar'
census partial '\Gfoo|xbar'
census partial '\Ga|b'
census partial '\G[a-z]+|ERROR'
census partial '\Gfoo|[0-9]+'

# PARTIAL, \G-free branch BOT-FAMILY ANCHORED (P1's population).
census partial '\Gfoo|(?m)^ERROR'
census partial '(?m)^a|\Gb'
census partial '\Gxy|(?m)^ab'

# CONTROLS: instance one on its own, with no \G anywhere.
census control '(?m)^ERROR'
census control '(?m)^a|b'

echo
echo "partial-\\G patterns: $n_partial total, $n_partial_pre with a prefilter, $n_partial_nopre without"
echo

echo "== 2. THE COST THERE IS TO RECOVER, on P2's population =="
echo
echo "If a third instance were worth building, the shape it would target is a"
echo "partial \\G whose \\G-free branch is a narrow literal. Measured on a"
echo "1 MB subject with no match, so every attempt runs and dies:"
echo
python3 - "$WORK" "$PCREC" <<'PY'
import os, subprocess, sys, time
work, pcrec = sys.argv[1], sys.argv[2]
subj = os.path.join(work, "big")
open(subj, "wb").write(b"z" * (1 << 20))
drv = os.path.join(work, "drv.c")
open(drv, "w").write(r'''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "gen.h"
int main(int argc, char **argv){
  FILE *f = fopen(argv[1], "rb");
  static unsigned char buf[1<<21];
  size_t n = fread(buf, 1, sizeof buf, f); fclose(f);
  int reps = atoi(argv[2]);
  ptrdiff_t caps[RX_NCAPS][2];
  struct timespec a, b;
  int r = 0;
  clock_gettime(CLOCK_MONOTONIC, &a);
  for (int i = 0; i < reps; i++) r |= rx_search(buf, n, 0, caps);
  clock_gettime(CLOCK_MONOTONIC, &b);
  double s = (b.tv_sec-a.tv_sec) + (b.tv_nsec-a.tv_nsec)/1e9;
  printf("%.6f s / %d reps  (r=%d)\n", s, reps, r);
  return 0;
}
''')
for pat, note in [(r'\Gfoo|xbar', 'partial \\G, unanchored literal branch'),
                  (r'xbar',       'the \\G-free branch ALONE (ENG_UNANCH, has every mechanism)'),
                  (r'(?m)^xbar',  'instance one for scale (ENG_ATTEMPT + memchr)')]:
    d = os.path.join(work, "t%d" % abs(hash(pat)))
    os.makedirs(d, exist_ok=True)
    subprocess.run([pcrec, "--features", "all", "-p", "rx", "-o", d + "/gen.c", "--", pat],
                   check=True, capture_output=True)
    subprocess.run(["gcc", "-O2", "-I", d, "-o", d + "/t", drv, d + "/gen.c"],
                   check=True, capture_output=True)
    out = subprocess.run([d + "/t", subj, "5"], capture_output=True, text=True).stdout.strip()
    eng = "ATTEMPT" if "start_max" in open(d + "/gen.c").read() else "UNANCH"
    print("  %-14s %-9s %-52s %s" % (pat, eng, note, out))
PY

echo
echo "== 3. THE VERDICT =="
cat <<'EOF'

Read column 3 of the census against P1/P2/P3.

Partial `\G` needs NO NEW CALLER of `cand_derive` and NO new loop
integration. The shipped derivation is over the PREDECESSOR-BYTE liveness of
`s1u[]`, and a partial-`\G` pattern's `s1u[]` is exactly the closure of its
`\G`-FREE branches — so instance one already answers this population, giving
a prefilter to the shapes that admit one and correctly declining the rest.
What a "third instance" would have to add is a derivation over a DIFFERENT
quantity (the non-`\G` branches' FIRST-BYTE set, at offset 0), and that is
D63's SECOND named instance — the D8 `^`-on-some-branches shape — which D63
gates on its own separate measurement and which would serve `^`-partial and
`\G`-partial patterns alike from one place.

So the honest ruling for D63's item 2 is not "the third instance is not worth
building" but "there is no third instance to build": its population is served
by the first and its unserved remainder belongs to the second.

WHAT WAVE D DID ADD to the prefilter is a SOUNDNESS bound rather than a new
instance — the guard's lower limit moves from `start > 0` to
`start > startpos` whenever the machine has a `\G` family, because the
derivation's domain is `start > startpos` and the attempt AT `startpos`
enters a state the derivation never looked at. Sabotage S82 is that line's
measured failing direction: `(?m)^a|\Gb` on "xb" at startpos 1 loses its
match under the wave-C bound.
EOF
