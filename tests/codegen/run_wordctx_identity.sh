#!/usr/bin/env bash
# tests/codegen/run_wordctx_identity.sh — [M6.2] WAVE B's BYTE-IDENTITY GATE.
#
# THE CLAIM. `\b`/`\B` add a WORD CONTEXT to src/ir/dfa.c's subset
# construction — the byte class map is refined by the word set (§3.4), every
# state gains a second closure for "the byte about to be consumed is a word
# character" (§3.5), the accept becomes class-indexed where it varies (§3.6),
# and mechanism 4 gives the machine a third start state (§3.8). That is the
# largest change any wave of [M6.2] makes to the engine, and the claim is that
# a pattern WITHOUT `\b`/`\B` pays for none of it: the same alphabet, the same
# states, the same tables, the same emitted bytes, BY CONSTRUCTION.
#
# The construction is three guards, each with the same proof shape:
#
#     eqclasses  refines by the word set only when has_word
#     make_state computes the word closures only when has_word
#     the emitter emits fseed/facc2/racc2/acc2 only where they DIFFER
#
# With no N_WORDB/N_NWORDB in the machine, `up_word` gates nothing, so the
# word closure of any pre-set IS its ordinary closure, element for element —
# so `wlist` shares `list`'s storage, `waccept == accept` at every state,
# `dfa_has_wacc` is false, `s1w == s1`, and every emitter site takes the
# pre-wave branch.
#
# WHY THE CHECK EXISTS EVEN THOUGH THE PROSE SAYS IT CANNOT FAIL. Wave A's
# answer, and it is this project's recorded lesson rather than a habit: the
# design's first draft of the ANALOGOUS claim one wave earlier was WRONG (R30
# E3), argued from prose, and would have shipped. "X is impossible by
# construction" is precisely the claim a construction check is for, and a
# construction check with no measured failing direction is not a check. The
# sabotage row is S71.
#
# HOW IT COMPARES, and why not against a pinned historical commit: the same
# argument run_trie_identity.sh and run_endvar_identity.sh both state. The
# permanent form builds a REFERENCE COMPILER from THIS tree's own sources with
# `-DPCREC_NO_WORDCTX`, which pins `has_word` false and nothing else, and
# requires byte-identical output over the whole corpus.
#
# THE POSITIVE CONTROL is not decoration. If `-DPCREC_NO_WORDCTX` disabled
# nothing, every comparison below would trivially agree and this script would
# report a clean bill of health for a dead knob. The `\b`/`\B` patterns are
# the control and the two builds MUST differ on them. Note what the reference
# build DOES to a `\b` pattern: with `has_word` pinned false the closure reads
# `cons_word == up_word` with both bits stuck at false, so `\b` never passes
# and `\B` always does — a WRONG matcher, which is exactly why the knob is
# never defined in a shipped build and why the control cannot be silent.
#
# Usage: bash tests/codegen/run_wordctx_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "wordctx-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the reference compiler ---------------------------------------------
# The source list is FOUND, not globbed at a fixed depth — src/gen/enc/ is two
# levels down and a hand-maintained `src/*/*.c` silently dropped it once
# already. A reference compiler quietly built from a different source set than
# the subject is the differential going vacuous.
REF="$WORKDIR/pcrec_nowordctx"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | sort)"
if [ -z "$REF_SRCS" ]; then
    echo "FAIL: found no compiler sources under $ROOT_DIR/src for the reference build" >&2
    exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_NO_WORDCTX $SANFLAGS \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS \
        2>"$WORKDIR/refbuild.log"; then
    echo "FAIL: could not build the -DPCREC_NO_WORDCTX reference compiler:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    exit 1
fi
if [ -s "$WORKDIR/refbuild.log" ]; then
    echo "FAIL: the -DPCREC_NO_WORDCTX reference build produced warnings:" >&2
    cat "$WORKDIR/refbuild.log" >&2
    fail=$((fail + 1))
fi

# Both builds emit SELF-CONTAINED C to stdout: writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason unrelated to the word context.
#
# `--features all` because this is a pcrec-vs-pcrec BYTE comparison, not an
# oracle differential — what `all` buys is that the corpus's module-gated
# patterns reach the emitter instead of being refused before it.
gen_a() { "$PCREC" --features all -p rx -o - -- "$1" 2>/dev/null; }
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

# THE SPLIT, and the one place it is subtler than wave A's.
#
# `\z` means one thing everywhere, so run_endvar_identity.sh could split on
# `grep -F '\z'`. `\b` DOES NOT: inside a character class it is not an
# assertion at all, it is BASE syntax for backspace (0x08) — `[\b]` is in this
# corpus today and creates no word context whatever. A text split that ignored
# that would put `[\b]` in the CONTROL population, where it would correctly
# fail to differ and report a false alarm about a working knob.
#
# So the split is on `\b`/`\B` occurring OUTSIDE a bracket expression, decided
# by a scan of the pattern TEXT — deliberately not by anything pcrec computes,
# because a split derived from `Dfa.wordctx` would be the check reading its
# own subject's verdict. The scanner prints both counts every run so the
# exclusion is visible rather than latent (§3.4's committed-tooling lesson).
python3 - "$PATFILE" "$WORKDIR/bpat" "$WORKDIR/nobpat" <<'PY'
import sys
src, bout, nout = sys.argv[1], sys.argv[2], sys.argv[3]

def has_word_assertion(p):
    """True iff `\\b` or `\\B` occurs at an ATOM position, i.e. outside a
    bracket expression. Mirrors the base grammar's class scanning: `[` opens,
    a leading `^` and a leading `]` are literal members, `\\` escapes the next
    byte, `]` closes."""
    i, n, incls = 0, len(p), False
    while i < n:
        c = p[i]
        if c == '\\' and i + 1 < n:
            nxt = p[i + 1]
            if not incls and nxt in ('b', 'B'):
                return True
            i += 2
            continue
        if not incls and c == '[':
            incls = True
            i += 1
            if i < n and p[i] == '^': i += 1
            if i < n and p[i] == ']': i += 1
            continue
        if incls and c == ']':
            incls = False
        i += 1
    return False

raw = [l.rstrip("\n") for l in open(src) if l.strip()]
mentions = [p for p in raw if '\\b' in p or '\\B' in p]
real = [p for p in raw if has_word_assertion(p)]
rest = [p for p in raw if not has_word_assertion(p)]
open(bout, "w").write("".join(p + "\n" for p in real))
open(nout, "w").write("".join(p + "\n" for p in rest))
print("wordctx-identity: corpus %d patterns; MENTION \\b or \\B: %d; "
      "carry one as an ASSERTION (outside a class): %d; "
      "class-position-only (backspace, no word context): %d"
      % (len(raw), len(mentions), len(real), len(mentions) - len(real)))
PY

nb=$(wc -l < "$WORKDIR/bpat")
nn=$(wc -l < "$WORKDIR/nobpat")

if [ "$nn" -lt 100 ]; then
    bad "corpus extraction found only $nn \\b-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nb" -lt 5 ]; then
    bad "corpus extraction found only $nb word-assertion patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the positive control ------------------------------------------------
# SCOPED TO THE DFA, exactly as wave A's is and for the identical reason: the
# word context is a property of the SUBSET CONSTRUCTION. The VM emitter spells
# `\b` as one guarded expression over the class pool and never consults a
# state's word view, so a `\b` pattern that routes to the VM — any
# capture-bearing one, e.g. `(\bfoo)` — legitimately emits IDENTICAL bytes
# from both builds. The artifact says which engine it is in its own
# `RX_ENGINE` stamp (VM artifacts only), and reading THAT to explain a
# non-difference is a different fact from the one being measured.
ctl_diff=0; ctl_same_vm=0; ctl_same_dfa=0; ctl_rej=0
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    a="$(gen_a "$pat")"; b="$(gen_b "$pat")"
    if [ -z "$a" ] && [ -z "$b" ]; then ctl_rej=$((ctl_rej + 1)); continue; fi
    if [ "$a" != "$b" ]; then
        ctl_diff=$((ctl_diff + 1))
    elif printf '%s' "$a" | grep -q '^#define RX_ENGINE "vm"$'; then
        ctl_same_vm=$((ctl_same_vm + 1))
    else
        ctl_same_dfa=$((ctl_same_dfa + 1))
        echo "  DFA-compiled control did NOT differ: $pat" >&2
    fi
done < "$WORKDIR/bpat"

if [ "$ctl_diff" -ge 5 ] && [ "$ctl_same_dfa" -eq 0 ]; then
    ok "positive control: $ctl_diff DFA-compiled word-assertion patterns differ between the two builds and 0 agree ($ctl_same_vm agreed and are VM artifacts, where the word context plays no part) — -DPCREC_NO_WORDCTX really disables it, so the identity comparisons below are not vacuous"
else
    bad "positive control: $ctl_diff word-assertion patterns differ, $ctl_same_dfa DFA-compiled ones AGREE, $ctl_same_vm VM ones agree (expected), $ctl_rej rejected by both. Every DFA-compiled \\b/\\B pattern must differ; if none does, the reference knob is dead and this whole check is vacuous."
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
done < "$WORKDIR/nobpat"

if [ "$((same + diff))" -lt 100 ]; then
    bad "only $((same + diff)) \\b-free patterns compiled in both builds — too few to call this a corpus-wide gate"
else
    ok "coverage: $((same + diff)) of $nn \\b-free corpus patterns compiled in both builds and were compared ($rej rejected by both)"
fi

if [ "$diff" -eq 0 ]; then
    ok "wordctx identity: $same \\b-free patterns emit BYTE-IDENTICAL C with and without the word context"
else
    bad "wordctx identity: $diff of $((same + diff)) \\b-free patterns changed emitted bytes. Some site is paying for the word context unconditionally — the alphabet refinement, the second closure, the class-indexed accept and the seed table are ALL supposed to be gated on the machine actually carrying an N_WORDB. First offenders:"
    head -20 "$WORKDIR/diffs.txt" >&2
fi

echo
echo "== Summary =="
echo "  identity population   compared $((same + diff))  identical $same  differing $diff  rejected-by-both $rej"
echo "  positive control      differ $ctl_diff  agree-on-DFA $ctl_same_dfa  agree-on-VM $ctl_same_vm  rejected-by-both $ctl_rej"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
