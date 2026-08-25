#!/usr/bin/env bash
# tests/codegen/run_dfa_stamps.sh — [DD-13]: the DFA artifact's D46 SELECTION
# STAMPS, held to the loop they describe.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `src/gen/emit_dfa.c` stamps three macros on every DFA artifact:
#
#     #define RX_ENGINE        "dfa"
#     #define RX_DFA_SCAN      "unanchored" | "attempt"
#     #define RX_DFA_PREFILTER "none" | "memchr" | "memchr-bounded"
#                            | "byte-class" | "byte-class-bounded"
#
# docs/spec/match_api.md §6.3 rules the first UNCONDITIONAL — present on every
# artifact both engines produce, so a consumer may `#if` on it without knowing
# which engine it got — and the other two DFA-only, because their VALUE SETS
# are the DFA's (the VM's own prefilter axis is `RX_VM_PREFILTER`, a different
# vocabulary). pcrec-bench buckets its rows by these.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3 is the rule this file is built against, and the
# obvious wrong version of this check is the one that reads the stamp and
# checks it is well-formed: that asserts the emitter can print a string.
#
# So EVERY verdict below is derived from the EMITTED MATCHER TEXT — the loop,
# the tables and the `memchr` call — and compared against the stamp. The two
# come out of different code paths in the emitter (`emit_dfa_stamps` writes the
# macros; `emit_unanchored`/`emit_attempt` write the loop), so a stamp that
# drifts from the mechanism it names is a RED here. That is the whole claim: a
# stamp nobody can check against the artifact is decoration, and D46 asks for
# an observable selection point, not a comment.
#
# THE ENGINE DISCRIMINATOR IS THE PROGRAM, NOT A MACRO. A VM artifact is one
# that contains `goto rx_L0;` (its computed-goto program's entry — the same
# marker `run_recursion_identity.sh`'s program-region extractor uses). Reading
# `RX_ENGINE` to decide which artifact kind to check `RX_ENGINE` on is the
# circularity this note exists to refuse. NOTE that a VM artifact may ALSO
# contain a DFA scan loop — the §6.1 hybrid inlines this same emitter's
# prefilter as a `static` — which is exactly why the VM test comes first.
#
# =========================================================================
# VALIDATION (the check was made to fail on purpose before it shipped)
# =========================================================================
# Recorded 2026-08-25, lane srStamp, each planted in src/gen/emit_dfa.c,
# rebuilt, run, and reverted:
#
#   1. `emit_dfa_stamps`'s `_DFA_SCAN` value inverted (attempt <-> unanchored):
#      RED, 386 artifacts disagreeing with their own loop shape.
#   2. `dfa_prefilter_name`'s bounded arms dropped (`us.views` ignored):
#      RED, 92 artifacts stamping "memchr"/"byte-class" for a loop bounded at
#      n-1 -- i.e. exactly plan.md [DD-13] (b)'s distinction going silent.
#   3. the whole `emit_dfa_stamps` call removed: RED on the presence checks,
#      2,022 DFA artifacts carrying no `RX_ENGINE` line.
#   4. the witness table pointed at a VM artifact (`(a)b` in place of `abc`):
#      RED -- the witness is asserted to be a DFA artifact before its value is
#      read, so a pattern that changes engine cannot quietly stop testing.
#
# THE POPULATION IS PRINTED AND FLOORED (K35's remedy): a check whose
# population comes from a pipeline nobody counts cannot report that the
# pipeline lost a third of it.
#
# Usage: bash tests/codegen/run_dfa_stamps.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run: a bounded compiler

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "dfa-stamps: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: dfa-stamps: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE DOCUMENTED VALUE SETS, spelled here so this file states the contract it
# checks rather than accepting whatever the emitter says. Any value outside
# these is a failure even if it agrees with the loop: a new mechanism needs a
# spec hunk (docs/spec/match_api.md §6.3) and a line here, in the same change.
SCAN_VALUES="unanchored attempt"
PF_VALUES="none memchr memchr-bounded byte-class byte-class-bounded"

# ---------------------------------------------------------------------------
# The per-artifact derivation: read an artifact on stdin, print
#     <engine> <scan> <prefilter>
# derived ENTIRELY from the emitted matcher text.
# ---------------------------------------------------------------------------
# `awk` and not a pile of `grep`s because each artifact is read ONCE and every
# marker is an anchored, exact-substring test on a line the emitter writes
# verbatim (the strings below are `sb_puts`/`sb_printf` literals in
# src/gen/emit_dfa.c; each is named in the comment beside it).
read_artifact() {
    # ONE PASS, ONE PROCESS. The sweep runs this ~2,800 times, so the derived
    # facts AND the stamps come out of a single `awk` rather than a `derive`
    # plus four `sed`/`grep` calls (measured: 3m50s -> 1m10s for the sweep).
    # The two halves stay VISIBLY SEPARATE inside it — the `d_*` fields are
    # built only from matcher text, the `s_*`/`n_*` fields only from `#define`
    # lines — because a single pass is a performance choice and must not
    # become a shared source (docs/dev/learnings.md §3).
    awk '
        # ---- (i) DERIVED: the emitted matcher text, and nothing else -------
        /^    goto rx_L0;$/                    { vm = 1 }                       # emit_vm.c: the program entry
        /^    \(void\)subject; \(void\)subject_length; \(void\)search_from; \(void\)capture_spans;$/ \
                                               { mtnothing = 1 }                # emit_dfa.c: the empty engine
        /^    const size_t start_max = /       { attempt = 1 }                  # emit_attempt: the per-start loop
        /rx_forward_next_state\[/              { unanch = 1 }                   # emit_unanchored: the forward table
        /const void \*q = memchr\(subject \+ start, /   { pf_at = 1 }           # emit_attempt: D63 attempt skip
        /const void \*q = memchr\(subject \+ scan_position, / {                 # emit_unanchored: the memchr arm
                                                 pf_mc = 1
                                                 if ($0 ~ /subject_length - 1 - scan_position\)/) bnd = 1 }
        /!rx_can_begin_match\[subject\[scan_position\]\]/ {                     # emit_unanchored: the bitmap arm
                                                 pf_bc = 1
                                                 if ($0 ~ /while \(scan_position \+ 1 < subject_length &&/) bnd = 1 }
        # ---- (ii) STAMPED: the `#define` lines, and nothing else -----------
        /^#define RX_ENGINE "/        { ne++; s_eng  = substr($3, 2, length($3) - 2) }
        /^#define RX_DFA_SCAN "/      { ns++; s_scan = substr($3, 2, length($3) - 2) }
        /^#define RX_DFA_PREFILTER "/ { np++; s_pf   = substr($3, 2, length($3) - 2) }
        END {
            eng = vm ? "vm" : "dfa"
            scan = attempt ? "attempt" : (unanch ? "unanchored" : (mtnothing ? "empty" : "-"))
            if (pf_bc)      pf = bnd ? "byte-class-bounded" : "byte-class"
            else if (pf_mc) pf = bnd ? "memchr-bounded"     : "memchr"
            else if (pf_at) pf = "memchr"
            else            pf = "none"
            if (vm) { scan = "-"; pf = "-" }
            print eng, scan, pf, (s_eng == "" ? "-" : s_eng), (s_scan == "" ? "-" : s_scan), \
                  (s_pf == "" ? "-" : s_pf), ne + 0, ns + 0, np + 0
        }'
}

# ---------------------------------------------------------------------------
# §1 THE NAMED WITNESSES — one pattern per documented value, expectation
#     spelled out here rather than harvested from the corpus.
# ---------------------------------------------------------------------------
# WHY BOTH THIS AND THE SWEEP. The sweep below asserts AGREEMENT (stamp ==
# loop) over the whole corpus, and agreement is a property two wrong answers
# can also have: an emitter that stamped "none" everywhere AND emitted no
# prefilter anywhere would sail through it. These rows pin the actual VALUES
# on patterns whose mechanism is known independently, so the sweep's agreement
# is a claim about a moving population and this is a claim about the mechanism.
# Each row: <expected-scan> <expected-prefilter> <pattern>
#
# `(?:...)\z` IS THE SPECIMEN CASE plan.md [DD-13] (b) names: the same
# `rx_can_begin_match` table as the plain form, but a loop bounded at n-1 that
# cannot early-exit, so it must NOT stamp the same value as its unbounded twin.
witness() {
    exp_scan="$1"; exp_pf="$2"; wpat="$3"
    art="$WORKDIR/w.c"
    if ! pcrec_run "$PCREC" --features all -p rx -o - -- "$wpat" > "$art" 2>/dev/null; then
        bad "[witness] '$wpat' does not compile — the row cannot assert anything"; return
    fi
    set -- $(read_artifact < "$art")
    if [ "$1" != "dfa" ]; then
        bad "[witness] '$wpat' is a $1 artifact, not a DFA one — this row has stopped testing what it names"; return
    fi
    gs="$4"; ss="$5"; ps="$6"
    if [ "$gs" = "dfa" ] && [ "$ss" = "$exp_scan" ] && [ "$ps" = "$exp_pf" ]; then
        ok "[witness] '$wpat' stamps RX_ENGINE \"dfa\" / RX_DFA_SCAN \"$exp_scan\" / RX_DFA_PREFILTER \"$exp_pf\""
    else
        bad "[witness] '$wpat' stamps engine '$gs' scan '$ss' prefilter '$ps', expected 'dfa'/'$exp_scan'/'$exp_pf'"
    fi
}
witness unanchored memchr             'abc'
witness unanchored byte-class         '[af]bc|[gz]bc'
witness unanchored memchr-bounded     'abc$'
witness unanchored byte-class-bounded '(?:[af]bc|[gz]bc)\z'
witness unanchored none               '.*'
witness attempt    memchr             '(?m)^ERROR'
witness attempt    none               '^abc'

# THE VM SIDE OF THE UNCONDITIONAL RULE: `RX_ENGINE` is present there too and
# says "vm", and NONE of the DFA-family names leak onto it (§6.3's (a)/(b)
# split: a selection fact is unconditional, an engine's own vocabulary is not).
vmart="$WORKDIR/vm.c"
if pcrec_run "$PCREC" --features all -p rx -o - -- '(a)\1' > "$vmart" 2>/dev/null; then
    set -- $(read_artifact < "$vmart")
    if [ "$1" != "vm" ]; then
        bad "[vm] '(a)\\1' is a $1 artifact — the VM half of this check has lost its subject"
    elif [ "$4" != "vm" ]; then
        bad "[vm] a VM artifact does not stamp RX_ENGINE \"vm\""
    elif [ "$8" -ne 0 ] || [ "$9" -ne 0 ]; then
        bad "[vm] a VM artifact carries a RX_DFA_* macro — those are the DFA's vocabulary (match_api.md §6.3)"
    else
        ok "[vm] a VM artifact stamps RX_ENGINE \"vm\" and carries no RX_DFA_* macro"
    fi
else
    bad "[vm] '(a)\\1' does not compile — the VM half of this check has no subject"
fi

# ---------------------------------------------------------------------------
# §2 THE CORPUS SWEEP: every artifact's stamps agree with its own loop.
# ---------------------------------------------------------------------------
# The population is every `pattern` line in every .rxt under tests/, so it
# grows with the corpus rather than with this script.
#
# [K35] `LC_ALL=C` ON THE `sort -u`: under the ambient collation punctuation is
# IGNORABLE, so `a{0,0}b` and `(a){0,0}b` compare EQUAL and `-u` drops the
# structured one. Measured on this tree: 1,784 ambient vs 2,758 under LC_ALL=C.
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
# THE FLOOR, ~95% of the 2,758 this tree measures (2026-08-25). If this goes
# red, read it as "the population moved" and find out why before re-pinning.
if [ "$npat" -lt 2620 ]; then
    bad "dfa-stamps: corpus extraction found only $npat patterns, below the 2620 floor (~95% of the 2758 this tree measures). Either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# THE EMPTY-ENGINE BUCKET IS NAMED AND COUNTED, NEVER FILTERED. A pattern the
# analysis proves can match nothing (`\B\b`, `\d\b\w`) emits a search function
# whose entire body is `(void)...; return 0;` — no table, no loop, no skip.
# There is therefore NO EMITTED SCAN SHAPE for `RX_DFA_SCAN` to be checked
# against, and asserting agreement on those four artifacts would be asserting
# against a `-`. What IS checkable on them, and is asserted below, is the
# prefilter: an artifact with no loop cannot carry a prefilter, so its stamp
# must read "none" — and that is a real red, because the stamp comes from
# `job->engine`+`unanch_start` while the emptiness comes from the emitted text.
# The bucket's own size is asserted NON-ZERO, so a marker that stopped matching
# announces itself instead of silently exempting the whole population.
#
# SHARDED, because the whole population is ~2,800 compiles and this script runs
# inside `make test-codegen` — the inner-loop group `make smoke` includes.
# MEASURED on this box: 3m50s with a `derive` plus four `sed`/`grep` per
# artifact, 2m03s after collapsing those into one `awk`, ~35s at PROCS=4.
# The shards are LINE CHUNKS of one pattern file (`split -n l/N`), not an
# `xargs` over pattern text: a pattern is arbitrary bytes and every quoting
# scheme for passing it as an argument is a bug waiting to be found by the
# corpus. Each worker writes VERDICT TOKENS to its own file and the parent
# tallies them, so no counter is shared across processes.
NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

cat > "$WORKDIR/worker.sh" <<'WORKER'
#!/usr/bin/env bash
# One shard. Reads patterns on stdin, writes verdict tokens to stdout.
# `pcrec_run` (D45's bounded compiler, [K37]) is sourced HERE rather than
# inherited, so the worker cannot silently run an unbounded compiler if an
# export ever stops arriving; `read_artifact` IS inherited (`export -f`),
# because a second copy of the derivation is the one thing this file's own
# check-design note forbids.
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD: worker could not load pcrec_run"; exit 1; }
command -v read_artifact >/dev/null || { echo "BAD: worker did not inherit read_artifact"; exit 1; }
art="$WORKDIR/a.$$.c"
trap 'rm -f "$art"' EXIT
while IFS= read -r pat; do
    if ! pcrec_run "$PCREC" --features all -p rx -o - -- "$pat" > "$art" 2>/dev/null; then
        echo REFUSED; continue
    fi
    set -- $(read_artifact < "$art")
    d_eng="$1"; d_scan="$2"; d_pf="$3"
    s_eng="$4"; s_scan="$5"; s_pf="$6"; ne="$7"; ns="$8"; np="$9"
    if [ "$d_eng" = "vm" ]; then
        echo VM
        [ "$ns" -eq 0 ] && [ "$np" -eq 0 ] || { echo VM_LEAK; echo "BAD: DFA-MACRO ON A VM ARTIFACT: $pat"; }
        [ "$s_eng" = "vm" ] || { echo MISS; echo "BAD: NO RX_ENGINE \"vm\": $pat"; }
        continue
    fi
    echo DFA
    if [ "$ne" -ne 1 ] || [ "$ns" -ne 1 ] || [ "$np" -ne 1 ]; then
        # ONE LINE EACH, ASSERTED IN BOTH DIRECTIONS: a missing stamp and a
        # doubled one are different bugs and both are failures here.
        if [ "$ne" -eq 0 ] || [ "$ns" -eq 0 ] || [ "$np" -eq 0 ]; then
            echo MISS; echo "BAD: MISSING STAMP (engine=$ne scan=$ns prefilter=$np): $pat"
        else
            echo DUP;  echo "BAD: DUPLICATED STAMP (engine=$ne scan=$ns prefilter=$np): $pat"
        fi
        continue
    fi
    echo "PFVAL $s_pf"
    echo "SCANVAL $s_scan"
    case " $SCAN_VALUES " in *" $s_scan "*) ;; *) echo VALUE; echo "BAD: UNDOCUMENTED RX_DFA_SCAN '$s_scan': $pat" ;; esac
    case " $PF_VALUES "   in *" $s_pf "*)   ;; *) echo VALUE; echo "BAD: UNDOCUMENTED RX_DFA_PREFILTER '$s_pf': $pat" ;; esac
    [ "$s_eng" = "dfa" ] || { echo MISS; echo "BAD: RX_ENGINE '$s_eng' on a DFA artifact: $pat"; }
    if [ "$d_scan" = "empty" ]; then
        echo EMPTY
        [ "$s_pf" = "none" ] || { echo EMPTYPF; echo "BAD: PREFILTER '$s_pf' on an artifact with NO LOOP: $pat"; }
        continue
    fi
    [ "$s_scan" = "$d_scan" ] || { echo SCANBAD; echo "BAD: SCAN: stamp '$s_scan' vs loop '$d_scan': $pat"; }
    [ "$s_pf"   = "$d_pf"   ] || { echo PFBAD;   echo "BAD: PREFILTER: stamp '$s_pf' vs loop '$d_pf': $pat"; }
done
WORKER

export WORKDIR PCREC SCAN_VALUES PF_VALUES ROOT_DIR
export -f read_artifact
for f in "$WORKDIR"/sh/p*; do
    bash "$WORKDIR/worker.sh" < "$f" > "$f.out" &
done
wait
cat "$WORKDIR"/sh/p*.out > "$WORKDIR/verdicts"
grep '^BAD: ' "$WORKDIR/verdicts" | sed 's/^BAD: //' > "$WORKDIR/bad"

tok() { grep -cx "$1" "$WORKDIR/verdicts" || true; }
ndfa=$(tok DFA);      nvm=$(tok VM);        nrefused=$(tok REFUSED)
nmiss=$(tok MISS);    ndup=$(tok DUP);      nleak=$(tok VM_LEAK)
nvalue=$(tok VALUE);  nempty=$(tok EMPTY);  nemptypf=$(tok EMPTYPF)
nscan=$(tok SCANBAD); npf=$(tok PFBAD)
sed -n 's/^PFVAL //p'   "$WORKDIR/verdicts" > "$WORKDIR/seen_pf"
sed -n 's/^SCANVAL //p' "$WORKDIR/verdicts" > "$WORKDIR/seen_scan"

echo
echo "== [DD-13] DFA selection stamps =="
echo "population: $npat distinct corpus patterns extracted (floor 2620; LC_ALL=C, K35)"
echo "artifacts : $ndfa DFA ($nempty of them the empty engine: no loop to compare a scan shape against), $nvm VM, $nrefused refused"
echo "prefilter values observed: $(LC_ALL=C sort "$WORKDIR/seen_pf" | uniq -c | LC_ALL=C sort -rn | awk '{printf "%s=%s ", $2, $1}')"
echo "scan values observed     : $(LC_ALL=C sort "$WORKDIR/seen_scan" | uniq -c | LC_ALL=C sort -rn | awk '{printf "%s=%s ", $2, $1}')"

if [ "$ndfa" -eq 0 ] || [ "$nvm" -eq 0 ]; then
    bad "dfa-stamps: the sweep saw $ndfa DFA and $nvm VM artifacts — a bucket with no members asserts nothing"
fi
[ "$nmiss" -eq 0 ] && ok "[stamps] all $ndfa DFA artifacts carry exactly one RX_ENGINE \"dfa\", and all $nvm VM artifacts one RX_ENGINE \"vm\"" \
                   || bad "[stamps] $nmiss artifact(s) are missing a selection stamp"
[ "$ndup"  -eq 0 ] && ok "[stamps] no artifact carries a duplicated RX_DFA_SCAN/RX_DFA_PREFILTER line" \
                   || bad "[stamps] $ndup artifact(s) carry a duplicated stamp line"
[ "$nleak" -eq 0 ] && ok "[stamps] no VM artifact carries a RX_DFA_* macro (§6.3's (a)/(b) split)" \
                   || bad "[stamps] $nleak VM artifact(s) carry a RX_DFA_* macro"
[ "$nscan" -eq 0 ] && ok "[agreement] RX_DFA_SCAN matches the emitted loop shape on all $((ndfa - nempty)) DFA artifacts that HAVE a loop" \
                   || bad "[agreement] $nscan artifact(s) stamp a scan shape their emitted loop does not have"
[ "$npf"   -eq 0 ] && ok "[agreement] RX_DFA_PREFILTER matches the emitted prefilter on all $((ndfa - nempty)) DFA artifacts that HAVE a loop" \
                   || bad "[agreement] $npf artifact(s) stamp a prefilter their emitted loop does not have"
[ "$nemptypf" -eq 0 ] && ok "[agreement] all $nempty empty-engine artifacts (a proven-no-match pattern: body is one \`return 0\`) stamp RX_DFA_PREFILTER \"none\"" \
                      || bad "[agreement] $nemptypf empty-engine artifact(s) stamp a prefilter, on a search function with no loop in it"
[ "$nempty" -eq 0 ] && bad "[agreement] the empty-engine bucket is EMPTY — \`\\B\\b\` and its three siblings are in the corpus and must land here; a zero means the text marker stopped matching and the bucket is silently exempting nothing (or, worse, everything)" \
                    || ok "[agreement] the empty-engine bucket holds $nempty artifact(s), asserted non-vacuous"
[ "$nvalue" -eq 0 ] && ok "[values] every stamped value is one of the documented set (scan: $SCAN_VALUES; prefilter: $PF_VALUES)" \
                    || bad "[values] $nvalue stamp(s) carry a value outside the documented set — a new mechanism needs its match_api.md §6.3 hunk and a line in this file"

if [ -s "$WORKDIR/bad" ]; then echo; echo "FAILURES:" >&2; head -30 "$WORKDIR/bad" >&2; fi
echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
