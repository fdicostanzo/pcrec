#!/usr/bin/env bash
# tests/codegen/run_mlinectx_identity.sh — [M6.2] WAVE C's BYTE-IDENTITY GATE.
#
# THE CLAIM. `(?m)` adds a NEWLINE half to the class axis wave B built: the
# byte class map is refined by `pcrec_cls_newline` (D64's one definition),
# every state gains a third closure for "the byte about to be consumed is a
# newline", the accept becomes class-indexed where it varies, the `pos == n`
# view goes live, and ENG_ATTEMPT gains D63's candidate-start prefilter. The
# claim is that a pattern WITHOUT a multiline `^`/`$` pays for NONE of it —
# the same alphabet, the same states, the same tables, the same emitted bytes,
# BY CONSTRUCTION.
#
# The construction is the same three guards wave B's gate names, one value
# wider:
#
#     eqclasses  refines by the newline set only when has_nl
#     make_state computes the UPC_NL closures only when upc_live[UPC_NL]
#     the emitter emits fseed/facc2/racc2/acc2/cand only where they DIFFER
#
# With no N_BOT_M/N_EOL_M in the machine, `right_nl`/`left_nl` gate nothing,
# so the newline closure of any pre-set IS its UPC_PLAIN closure element for
# element — so the two views share storage, every accept bit agrees across the
# axis, `dfa_has_clsacc` is unmoved, `s1u[UPC_NL] == s1u[UPC_PLAIN]`, and
# every emitter site takes the branch it took before this wave.
#
# WHY THE CHECK EXISTS EVEN THOUGH THE PROSE SAYS IT CANNOT FAIL. Wave A's
# answer, unchanged: the design's first draft of the ANALOGOUS claim was WRONG
# (R30 E3), argued from prose, and would have shipped. "X is impossible by
# construction" is precisely the claim a construction check is for, and a
# construction check with no measured failing direction is not a check. The
# sabotage row is S76.
#
# THIS WAVE'S EXTRA REASON, which wave B did not have. Wave C did not ADD a
# class view beside an existing one — it turned a BOOL into a three-valued
# enum, rewriting every site that read `waccept`, `wlist` or `s1w`. A
# mechanical refactor of that size is exactly where a `UPC_PLAIN` becomes a
# `UPC_WORD` in one arm and nothing notices, and the corpus cannot see it
# unless the arm is reachable. This gate can.
#
# HOW IT COMPARES, and why not against a pinned historical commit: the same
# argument run_trie_identity.sh, run_endvar_identity.sh and
# run_wordctx_identity.sh all state. The permanent form builds a REFERENCE
# COMPILER from THIS tree's own sources with `-DPCREC_NO_MLINECTX`, which pins
# `has_nl` false and nothing else, and requires byte-identical output over the
# whole corpus.
#
# THE POSITIVE CONTROL is not decoration. If `-DPCREC_NO_MLINECTX` disabled
# nothing, every comparison below would trivially agree and this script would
# report a clean bill of health for a dead knob. The `(?m)` patterns are the
# control and the two builds MUST differ on them. Note what the reference
# build DOES to a `(?m)$` pattern: with `has_nl` pinned false the closure
# reads `right_nl` stuck at false, so `(?m)$` can only pass through `end_ok`
# — it becomes `\z` — a WRONG matcher, which is why the knob is never defined
# in a shipped build and why the control cannot be silent.
#
# Usage: bash tests/codegen/run_mlinectx_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "mlinectx-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the shared scanner's own self-check --------------------------------
# tests/lib/mlscan.py decides this script's corpus SPLIT, so a drifted scanner
# would silently move patterns out of the identity population and this gate
# would go green over a smaller set. Its self-check is milliseconds and runs
# here rather than in a scripts/Makefile rule (D48's home for INDEPENDENT
# instruments) because it is not independent of this check — it is part of it.
if python3 "$ROOT_DIR/tests/lib/mlscan.py" > "$WORKDIR/mlscan.log" 2>&1; then
    ok "tests/lib/mlscan.py self-check: $(tail -1 "$WORKDIR/mlscan.log")"
else
    bad "tests/lib/mlscan.py self-check FAILED — the corpus split below is derived from it, so this gate's population cannot be trusted:"
    cat "$WORKDIR/mlscan.log" >&2
fi

# ---- the reference compiler ---------------------------------------------
# The source list is FOUND, not globbed at a fixed depth — src/gen/enc/ is two
# levels down and a hand-maintained `src/*/*.c` silently dropped it once
# already. A reference compiler quietly built from a different source set than
# the subject is the differential going vacuous.
REF="$WORKDIR/pcrec_nomlinectx"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | LC_ALL=C sort)"
if [ -z "$REF_SRCS" ]; then
    echo "FAIL: found no compiler sources under $ROOT_DIR/src for the reference build" >&2
    exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_NO_MLINECTX $SANFLAGS \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS \
        2>"$WORKDIR/refbuild.log"; then
    echo "FAIL: could not build the -DPCREC_NO_MLINECTX reference compiler:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    exit 1
fi
if [ -s "$WORKDIR/refbuild.log" ]; then
    echo "FAIL: the -DPCREC_NO_MLINECTX reference build produced warnings:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    fail=$((fail + 1))
fi

# Both builds emit SELF-CONTAINED C to stdout: writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason unrelated to the newline context.
gen_a() { pcrec_run "$PCREC" --features all -p rx -o - -- "$1" 2>/dev/null; }
gen_b() { "$REF"   --features all -p rx -o - -- "$1" 2>/dev/null; }

# ---- the corpus ----------------------------------------------------------
# Every `pattern` line from every .rxt under tests/, known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content. R24 M-F1 found, named and
# fixed that undercount; assertions_design.md §3.4 reproduced it verbatim
# after reading the entry that named it. It travels as committed tooling here
# for the same reason.
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

# THE SPLIT, and it is subtler than either predecessor's.
#
# `\z` means one thing everywhere, so run_endvar_identity.sh split on a
# substring. `\b` means two things, so run_wordctx_identity.sh split on
# bracket depth. `(?m)` means one thing but is SCOPED and SPELLED SEVERAL
# WAYS: `(?m)`, `(?im)`, `(?m:...)`, `(?^m)` all set it and `(?-m)`, `(?im-m)`
# and a bare `(?i)` do not. So the scanner walks the option-run grammar the
# parser walks — an optional leading `^`, then letters, with everything after
# a `-` on the unset side — rather than looking for a substring.
#
# It is deliberately NOT decided by anything pcrec computes: a split derived
# from `Dfa.clsctx` would be the check reading its own subject's verdict. Both
# counts print every run so the classification is visible rather than latent
# (§3.4's committed-tooling lesson).
python3 - "$ROOT_DIR" "$PATFILE" "$WORKDIR/mpat" "$WORKDIR/nompat" <<'PY'
import os, sys
root, src, mout, nout = sys.argv[1:5]
sys.path.insert(0, os.path.join(root, "tests", "lib"))
from mlscan import multiline_anchor      # ONE implementation, three readers

raw = [l.rstrip("\n") for l in open(src) if l.strip()]
mentions = [p for p in raw if '(?' in p and 'm' in p]
real = [p for p in raw if multiline_anchor(p)]
rest = [p for p in raw if not multiline_anchor(p)]
open(mout, "w").write("".join(p + "\n" for p in real))
open(nout, "w").write("".join(p + "\n" for p in rest))
print("mlinectx-identity: corpus %d patterns; contain both `(?` and an `m`: "
      "%d; carry a `^`/`$` IN SCOPE of a set `m`: %d; everything else "
      "(including patterns that set `m` with no anchor to receive it): %d"
      % (len(raw), len(mentions), len(real), len(rest)))
PY

nm=$(wc -l < "$WORKDIR/mpat")
nn=$(wc -l < "$WORKDIR/nompat")

if [ "$nn" -lt 100 ]; then
    bad "corpus extraction found only $nn (?m)-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nm" -lt 5 ]; then
    bad "corpus extraction found only $nm multiline-setting patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the positive control ------------------------------------------------
# SCOPED TO THE DFA, exactly as both predecessors are and for the identical
# reason: the newline context is a property of the SUBSET CONSTRUCTION. The VM
# emitter spells `(?m)^`/`(?m)$` as one guarded expression over the class pool
# and never consults a state's class view, so a `(?m)` pattern that routes to
# the VM — any capture-bearing one — legitimately emits IDENTICAL bytes from
# both builds.
#
# A pattern that can NEVER MATCH is the second legitimate non-difference,
# inherited from wave B's gate: the emitter's own "matches nothing" early-out
# leaves no automaton for a class view to change. Both are read off the
# ARTIFACT rather than off a maintained list of pattern texts.
ctl_diff=0; ctl_same_vm=0; ctl_same_empty=0; ctl_same_dfa=0; ctl_rej=0
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then ctl_rej=$((ctl_rej + 1)); continue; fi
    if [ "$a" != "$b" ]; then
        ctl_diff=$((ctl_diff + 1))
    elif printf '%s' "$a" | grep -q '^#define RX_ENGINE "vm"$'; then
        ctl_same_vm=$((ctl_same_vm + 1))
    elif printf '%s' "$a" | grep -q '^    (void)subject; (void)subject_length; (void)search_from; (void)capture_spans;$'; then
        ctl_same_empty=$((ctl_same_empty + 1))
        echo "  never-matching control (no automaton to change): $pat" >&2
    else
        ctl_same_dfa=$((ctl_same_dfa + 1))
        echo "  DFA-compiled control did NOT differ: $pat" >&2
    fi
done < "$WORKDIR/mpat"

if [ "$ctl_diff" -ge 5 ] && [ "$ctl_same_dfa" -eq 0 ]; then
    ok "positive control: $ctl_diff DFA-compiled multiline patterns differ between the two builds and 0 agree unexplained ($ctl_same_vm agreed and are VM artifacts, where the class views play no part; $ctl_same_empty are never-matching patterns whose artifact carries no automaton) — -DPCREC_NO_MLINECTX really disables it, so the identity comparisons below are not vacuous"
else
    bad "positive control: $ctl_diff multiline patterns differ, $ctl_same_dfa DFA-compiled ones AGREE UNEXPLAINED, $ctl_same_vm VM ones agree (expected), $ctl_same_empty never-matching ones agree (expected), $ctl_rej rejected by both. Every DFA-compiled (?m) pattern with a live automaton must differ; if none does, the reference knob is dead and this whole check is vacuous."
fi

# ---- the identity sweep --------------------------------------------------
same=0; diff=0; rej=0
: > "$WORKDIR/diffs.txt"
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then rej=$((rej + 1)); continue; fi
    if [ "$a" = "$b" ]; then
        same=$((same + 1))
    else
        diff=$((diff + 1))
        printf '%s\n' "$pat" >> "$WORKDIR/diffs.txt"
    fi
done < "$WORKDIR/nompat"

if [ "$((same + diff))" -lt 100 ]; then
    bad "only $((same + diff)) (?m)-free patterns compiled in both builds — too few to call this a corpus-wide gate"
else
    ok "coverage: $((same + diff)) of $nn (?m)-free corpus patterns compiled in both builds and were compared ($rej rejected by both)"
fi

if [ "$diff" -eq 0 ]; then
    ok "mlinectx identity: $same (?m)-free patterns emit BYTE-IDENTICAL C with and without the newline context"
else
    bad "mlinectx identity: $diff of $((same + diff)) (?m)-free patterns changed emitted bytes. Some site is paying for the newline context unconditionally — the alphabet refinement, the third class closure, the class-indexed accept, the seed table and D63's candidate prefilter are ALL supposed to be gated on the machine actually carrying an N_BOT_M/N_EOL_M. First offenders:"
    head -20 "$WORKDIR/diffs.txt" >&2
fi

echo
echo "== Summary =="
echo "  identity population   compared $((same + diff))  identical $same  differing $diff  rejected-by-both $rej"
echo "  positive control      differ $ctl_diff  agree-on-DFA(unexplained) $ctl_same_dfa  agree-on-VM $ctl_same_vm  agree-never-matching $ctl_same_empty  rejected-by-both $ctl_rej"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
