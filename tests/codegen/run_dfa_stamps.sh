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
#     #define RX_DFA_SCAN      "unanchored" | "attempt" | "empty"
#     #define RX_DFA_PREFILTER "none" | "memchr" | "memchr-bounded"
#                            | "byte-class" | "byte-class-bounded"
#
# docs/spec/match_api.md §6.3 rules `RX_ENGINE` UNCONDITIONAL — present on every
# artifact both engines produce, so a consumer may `#if` on it without knowing
# which engine it got. pcrec-bench buckets its rows by these.
#
# [DD-13c], 2026-08-25 — r37's TWO SCOPE FINDINGS, and both of them changed
# what this file has to assert:
#
#   (#5) `"empty"` IS A THIRD SCAN VALUE. A pattern the analysis proves can
#        match nothing emits a body that is one `return 0` — no table, no loop,
#        no skip — on BOTH engines (`\B\b` unanchored, `^\B\b` under
#        ENG_ATTEMPT). Those artifacts used to stamp the name of a loop they do
#        not contain, and this check EXEMPTED them from the scan comparison to
#        avoid asserting against a `-`. There is a value for them now, so the
#        bucket asserts `"empty"` instead of exempting.
#
#   (#6) THE SCAN FACTS ARE NOT DFA-ARTIFACTS-ONLY; they belong to every
#        artifact that CONTAINS a DFA scan. The §6.1 HYBRID is a VM artifact
#        that inlines this same emitter's scan as `static rx_prefilter` —
#        tables, D11 bound, candidate-start filter and all — and it stamps the
#        two DFA lines for it. So the old rule here ("no RX_DFA_* on a VM
#        artifact") is replaced by an IFF, asserted both ways over the corpus:
#
#            a VM artifact carries RX_DFA_SCAN + RX_DFA_PREFILTER
#              <=> its emitted text contains an inlined `rx_prefilter` body
#              <=> RX_VM_PREFILTER is "hybrid"
#
#        `RX_VM_PREFILTER` (does the VM RUN a capture-erased DFA ahead of the
#        program) and `RX_DFA_PREFILTER` (what candidate-start filter the DFA
#        scan itself carries) are two different selections and both are stamped;
#        they are not two spellings of one fact.
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
# come out of different WRITE SITES in the emitter (both read the ONE
# `unanch_start` derivation — a defect inside it leaves stamp and loop
# agreeing; that is the differential suites' job, r37 B3) (`emit_dfa_stamps` writes the
# macros; `emit_unanchored`/`emit_attempt` write the loop), so a stamp that
# drifts from the mechanism it names is a RED here. That is the whole claim: a
# stamp nobody can check against the artifact is decoration, and D46 asks for
# an observable selection point, not a comment.
#
# THE ENGINE DISCRIMINATOR IS THE PROGRAM, NOT A MACRO. A VM artifact is one
# that contains `goto rx_L0;` (its computed-goto program's entry — the same
# marker `run_recursion_identity.sh`'s program-region extractor uses). Reading
# `RX_ENGINE` to decide which artifact kind to check `RX_ENGINE` on is the
# circularity this note exists to refuse.
#
# THE HYBRID DISCRIMINATOR IS THE SAME KIND OF THING: the emitted DEFINITION
# `static int rx_prefilter(const unsigned char *subject, ...` — the line
# `emit_search_head` writes when emit_vm.c asks emit_dfa.c for a scan under a
# private name. It is matcher text, not a stamp, so BOTH `#define` families the
# iff relates are compared against it and neither is ever checked against the
# other alone. (MEASURED on this tree: on `(a)\1`, a non-hybrid VM artifact,
# every DFA marker in `read_artifact` reads 0.)
#
# =========================================================================
# VALIDATION (the check was made to fail on purpose before it shipped)
# =========================================================================
# Recorded 2026-08-25, lane srStamp, each planted in src/gen/emit_dfa.c,
# rebuilt, run, and reverted:
#
#   1. `emit_dfa_stamps`'s `_DFA_SCAN` value inverted (attempt <-> unanchored):
#      RED, 8 checks failed -- all 7 witnesses, plus [agreement] "991 artifacts
#      stamp a scan shape their emitted loop does not have" (991 = every DFA
#      artifact that HAS a loop; the 4 empty-engine ones are exempt from that
#      axis by construction and stayed green, which is the bucket working).
#   2. `dfa_prefilter_name`'s bounded arms dropped (`us.views` ignored):
#      RED, 3 checks failed -- the two `-bounded` witnesses, plus [agreement]
#      "112 artifacts stamp a prefilter their emitted loop does not have".
#      **112 is exactly the 61 `memchr-bounded` + 51 `byte-class-bounded` in
#      the corpus distribution below**, i.e. the red is precisely plan.md
#      [DD-13] (b)'s distinction going silent and nothing else. Note the SCAN
#      axis and the empty-engine bucket stayed GREEN through this one: the
#      check localises the defect to the axis that broke rather than going
#      uniformly red, which is what makes a failure here readable.
#   3. the whole `emit_dfa_stamps` call removed: RED, 9 checks failed -- all 7
#      witnesses, plus [stamps] "995 artifacts are missing a selection stamp"
#      (995 = every DFA artifact), plus the empty-engine bucket's own
#      non-vacuity check -- with every stamp absent nothing reaches the bucket
#      (r37 #5 spelled out the ninth). The VM half stayed green, correctly: the
#      VM stamps its own `RX_ENGINE` through the shared emitter.
#   4. the witness table pointed at a VM artifact (`(a)\1` in place of `abc`):
#      RED with "'(a)\1' is a vm artifact, not a DFA one -- this row has
#      stopped testing what it names", and the OTHER six witnesses stayed
#      green. A pattern that changes engine cannot quietly stop testing.
#
# THE COUNTS ABOVE ARE MEASURED, and the first draft of this comment had them
# wrong (386 / 92 / 2,022, written from expectation before the plants were
# run). They are recorded here as run, from
# `scratchpad/srStamp/validate.log`.
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
SCAN_VALUES="unanchored attempt empty"
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
        /^static int rx_prefilter\(const unsigned char \*subject, /            \
                                               { hybrid = 1 }                   # emit_search_head (emit_dfa.c) under the private name emit_vm.c gives it: THE INLINED DFA SCAN
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
        /^#define RX_VM_PREFILTER "/  { s_vmpf = substr($3, 2, length($3) - 2) }   # [DD-13c] the OTHER side of the iff
        END {
            eng = vm ? "vm" : "dfa"
            scan = attempt ? "attempt" : (unanch ? "unanchored" : (mtnothing ? "empty" : "-"))
            if (pf_bc)      pf = bnd ? "byte-class-bounded" : "byte-class"
            else if (pf_mc) pf = bnd ? "memchr-bounded"     : "memchr"
            else if (pf_at) pf = "memchr"
            else            pf = "none"
            # [DD-13c] (r37 #6) A VM ARTIFACT NO LONGER DISCARDS THESE. It used
            # to read `if (vm) { scan = "-"; pf = "-" }`, which threw away the
            # HYBRID inlined scan facts and left the check unable to say
            # anything about the artifact kind that carries the mechanism. The
            # markers above are emit_dfa.c literals and fire on the inlined
            # copy exactly as they do on a DFA-only artifact (MEASURED: on
            # the non-hybrid VM artifact (a)\1, every one of them is 0).
            #
            # `dfascan` is the INDEPENDENT discriminator, and it is the emitted
            # DEFINITION of the scan function rather than any stamp or any
            # derived value: emit_vm.c calls pcrec_emit_dfa_engine under the
            # private name <prefix>_prefilter, so the presence of that line IS
            # "this artifact contains a DFA scan". A non-hybrid VM artifact has
            # no such body and reports "-" on both axes, which is what the iff
            # below is asserted against.
            dfascan = vm ? hybrid : 1
            if (!dfascan) { scan = "-"; pf = "-" }
            print eng, scan, pf, (s_eng == "" ? "-" : s_eng), (s_scan == "" ? "-" : s_scan), \
                  (s_pf == "" ? "-" : s_pf), ne + 0, ns + 0, np + 0, \
                  (s_vmpf == "" ? "-" : s_vmpf)
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
# [DD-13c] (r37 #5) THE EMPTY ENGINE, ON BOTH SIDES OF THE ENG_UNANCH/
# ENG_ATTEMPT FORK. `\B\b` cannot match (a position is a word boundary or it is
# not, never both) and `^\B\b` cannot either; the two take DIFFERENT emitters
# to the same one-`return 0` body, and until [DD-13c] the first stamped
# "unanchored" and the second "attempt" — a loop neither contains. The second
# row is the one that makes this a general mechanism rather than a fix for the
# four unanchored artifacts the corpus happens to hold: it is NOT in the corpus,
# so nothing but this row tests it.
witness empty      none               '\B\b'
witness empty      none               '^\B\b'

# ---------------------------------------------------------------------------
# THE VM SIDE, AS AN IFF — [DD-13c], r37 finding #6.
# ---------------------------------------------------------------------------
# `RX_ENGINE` is present on a VM artifact too and says "vm" (§6.3's (a): a
# SELECTION fact is unconditional). What changed is the other half. The old
# rule here was "NONE of the DFA-family names may appear on a VM artifact",
# and it was wrong about the §6.1 HYBRID: that artifact INLINES this same
# emitter's forward+reverse scan as `static rx_prefilter`, tables, D11 bound,
# candidate-start filter and all, and stamping nothing about it left the
# artifact kind that carries the specimen's mechanism the one kind that could
# not say so.
#
# So the rule is now an IFF, asserted in BOTH directions on named witnesses
# and again over the whole corpus below:
#
#     a VM artifact carries RX_DFA_SCAN + RX_DFA_PREFILTER
#       <=>  it contains an inlined DFA scan  ( <=> RX_VM_PREFILTER "hybrid" )
#
# THE THREE SOURCES ARE KEPT APART, which is the point of writing it this way.
# The LEFT side is `#define` lines; the MIDDLE is the emitted DEFINITION of
# `rx_prefilter` (matcher text, `read_artifact`'s `hybrid` marker); the RIGHT
# is a different `#define`. The middle is what both sides are compared to, so
# neither stamp is ever checked against the other stamp alone — a stamp block
# that lied consistently would still be caught by the function body.
#
# Each row: <expect-hybrid: yes|no> <pattern>
vm_witness() {
    exp_hy="$1"; wpat="$2"
    vmart="$WORKDIR/vm.c"
    if ! pcrec_run "$PCREC" --features all -p rx -o - -- "$wpat" > "$vmart" 2>/dev/null; then
        bad "[vm] '$wpat' does not compile — this row has no subject"; return
    fi
    set -- $(read_artifact < "$vmart")
    d_eng="$1"; d_scan="$2"; s_eng="$4"; ns="$8"; np="$9"; shift 9; s_vmpf="$1"
    if [ "$d_eng" != "vm" ]; then
        bad "[vm] '$wpat' is a $d_eng artifact, not a VM one — this row has stopped testing what it names"; return
    fi
    if [ "$s_eng" != "vm" ]; then
        bad "[vm] '$wpat': a VM artifact does not stamp RX_ENGINE \"vm\""; return
    fi
    # the middle term, from the matcher text
    if [ "$d_scan" = "-" ]; then got_hy=no; else got_hy=yes; fi
    if [ "$got_hy" != "$exp_hy" ]; then
        bad "[vm] '$wpat': expected inlined-DFA-scan=$exp_hy, the emitted text says $got_hy — this row has stopped testing what it names"; return
    fi
    # the right term
    want_vmpf=none; [ "$exp_hy" = yes ] && want_vmpf=hybrid
    if [ "$s_vmpf" != "$want_vmpf" ]; then
        bad "[vm] '$wpat': RX_VM_PREFILTER '$s_vmpf', but the emitted text says inlined-DFA-scan=$got_hy (expected '$want_vmpf')"; return
    fi
    # the left term, both directions
    if [ "$exp_hy" = yes ]; then
        if [ "$ns" -eq 1 ] && [ "$np" -eq 1 ]; then
            ok "[vm] '$wpat' is a hybrid (inlined rx_prefilter, RX_VM_PREFILTER \"hybrid\") and stamps RX_DFA_SCAN + RX_DFA_PREFILTER for it"
        else
            bad "[vm] '$wpat' is a hybrid and carries an inlined DFA scan, but stamps scan=$ns prefilter=$np RX_DFA_* line(s) — the artifact kind that ships the mechanism cannot say so (r37 #6)"
        fi
    else
        if [ "$ns" -eq 0 ] && [ "$np" -eq 0 ]; then
            ok "[vm] '$wpat' is a non-hybrid VM artifact and carries NO RX_DFA_* macro"
        else
            bad "[vm] '$wpat' carries a RX_DFA_* macro with no DFA scan in the artifact to describe (scan=$ns prefilter=$np)"
        fi
    fi
}
vm_witness no  '(a)\1'
vm_witness yes 'a(b|c)+d'
vm_witness yes '^(a)b'

# ---------------------------------------------------------------------------
# §2 THE CORPUS SWEEP: every artifact's stamps agree with its own loop.
# ---------------------------------------------------------------------------
# The population is every `pattern` line in every .rxt under tests/, so it
# grows with the corpus rather than with this script.
#
# [K35] `LC_ALL=C` ON THE `sort -u`: under the ambient collation punctuation is
# IGNORABLE, so `a{0,0}b` and `(a){0,0}b` compare EQUAL and `-u` drops the
# structured one. Measured on this tree: 1,784 ambient vs 2,772 under LC_ALL=C
# (2,758 was written before the count was taken -- r37 #1; the check prints
# the live number every run, which is the only figure to trust).
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
# THE FLOOR, ~95% of the 2,772 this tree measures (2026-08-25). If this goes
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
    s_eng="$4"; s_scan="$5"; s_pf="$6"; ne="$7"; ns="$8"; np="$9"; shift 9; s_vmpf="$1"
    if [ "$d_eng" = "vm" ]; then
        echo VM
        [ "$s_eng" = "vm" ] || { echo MISS; echo "BAD: NO RX_ENGINE \"vm\": $pat"; }
        # [DD-13c] (r37 #6) THE IFF, OVER THE WHOLE CORPUS AND IN BOTH
        # DIRECTIONS. `d_scan` is "-" exactly when the artifact carries no
        # inlined `rx_prefilter` body (read_artifact's `hybrid` marker), so the
        # middle term of the iff is matcher TEXT and neither `#define` is ever
        # checked against the other alone.
        if [ "$d_scan" = "-" ]; then
            echo VMPLAIN
            [ "$s_vmpf" = "none" ] || { echo VMPFBAD; echo "BAD: RX_VM_PREFILTER '$s_vmpf' but no inlined DFA scan in the artifact: $pat"; }
            [ "$ns" -eq 0 ] && [ "$np" -eq 0 ] \
                || { echo VM_LEAK; echo "BAD: RX_DFA_* MACRO ON A VM ARTIFACT WITH NO DFA SCAN IN IT: $pat"; }
            continue
        fi
        echo VMHYBRID
        # the hybrid whose INLINED scan is itself the empty engine (`(a)\b\B`):
        # a real, small bucket, counted so it is never an uncounted population.
        [ "$d_scan" = "empty" ] && echo VMHYEMPTY
        [ "$s_vmpf" = "hybrid" ] || { echo VMPFBAD; echo "BAD: RX_VM_PREFILTER '$s_vmpf' on an artifact that inlines a DFA scan: $pat"; }
        if [ "$ns" -ne 1 ] || [ "$np" -ne 1 ]; then
            if [ "$ns" -eq 0 ] || [ "$np" -eq 0 ]; then
                echo VM_SILENT; echo "BAD: HYBRID CARRIES AN INLINED DFA SCAN AND STAMPS NOTHING ABOUT IT (scan=$ns prefilter=$np): $pat"
            else
                echo DUP; echo "BAD: DUPLICATED STAMP ON A HYBRID (scan=$ns prefilter=$np): $pat"
            fi
            continue
        fi
        # ... and the values agree with the inlined loop, on the same axes and
        # from the same markers the DFA-only artifacts are held to below.
        echo "HYPFVAL $s_pf"
        echo "HYSCANVAL $s_scan"
        case " $SCAN_VALUES " in *" $s_scan "*) ;; *) echo VALUE; echo "BAD: UNDOCUMENTED RX_DFA_SCAN '$s_scan' (hybrid): $pat" ;; esac
        case " $PF_VALUES "   in *" $s_pf "*)   ;; *) echo VALUE; echo "BAD: UNDOCUMENTED RX_DFA_PREFILTER '$s_pf' (hybrid): $pat" ;; esac
        [ "$s_scan" = "$d_scan" ] || { echo SCANBAD; echo "BAD: SCAN (hybrid): stamp '$s_scan' vs inlined loop '$d_scan': $pat"; }
        [ "$s_pf"   = "$d_pf"   ] || { echo PFBAD;   echo "BAD: PREFILTER (hybrid): stamp '$s_pf' vs inlined loop '$d_pf': $pat"; }
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
        echo EMPTY; echo "EMPTYPAT $pat"
        [ "$s_pf" = "none" ] || { echo EMPTYPF; echo "BAD: PREFILTER '$s_pf' on an artifact with NO LOOP: $pat"; }
        # [DD-13c] (r37 #5) NO LONGER EXEMPT ON THE SCAN AXIS. There IS a value
        # for this body now -- `"empty"` -- so the comparison below applies to
        # it like any other, and the `continue` is only here because the
        # prefilter half was already asserted one line up.
        [ "$s_scan" = "empty" ] || { echo SCANBAD; echo "BAD: SCAN: stamp '$s_scan' on a body that is one \`return 0\` (expected 'empty'): $pat"; }
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
# [DD-13c] the iff's two populations and its two failure directions.
nvmhy=$(tok VMHYBRID); nvmpl=$(tok VMPLAIN)
nvmsilent=$(tok VM_SILENT); nvmpfbad=$(tok VMPFBAD); nvmhyempty=$(tok VMHYEMPTY)
# [DD-13c] THE TWO ARTIFACT KINDS ARE TALLIED SEPARATELY AND THEN TOGETHER.
# The DFA-only distribution is the one [DD-13] recorded and the one
# docs/spec/tuning.md §3 quotes, so folding the 1,200-odd hybrids into it would
# silently redefine a published figure; the combined line is the honest total
# for "every artifact that contains a DFA scan". Printing both is also the only
# way a reader can see that the DFA half did not move when the hybrids joined.
sed -n 's/^PFVAL //p'     "$WORKDIR/verdicts" > "$WORKDIR/seen_pf"
sed -n 's/^SCANVAL //p'   "$WORKDIR/verdicts" > "$WORKDIR/seen_scan"
sed -n 's/^HYPFVAL //p'   "$WORKDIR/verdicts" > "$WORKDIR/seen_hypf"
sed -n 's/^HYSCANVAL //p' "$WORKDIR/verdicts" > "$WORKDIR/seen_hyscan"
dist() { LC_ALL=C sort "$1" | uniq -c | LC_ALL=C sort -rn | awk '{printf "%s=%s ", $2, $1}'; }

echo
echo "== [DD-13] DFA selection stamps =="
echo "population: $npat distinct corpus patterns extracted (floor 2620; LC_ALL=C, K35)"
# r37 A9: floor the ARTIFACT population too, and ceiling the refusals — a
# feature gate or a compiler bound that quietly moved hundreds of patterns
# into REFUSED would leave every agreement check green with nothing to
# agree on. Measured 2026-08-25: 995 DFA / 1,488 VM / 289 refused.
[ "$ndfa" -ge 900 ] || bad "[population] only $ndfa DFA artifacts (floor 900; 995 measured 2026-08-25) — the population moved, find out why before re-pinning"
[ "$nrefused" -le 400 ] || bad "[population] $nrefused patterns REFUSED (ceiling 400; 289 measured 2026-08-25) — a feature gate or a compiler bound is eating the population"
echo "artifacts : $ndfa DFA ($nempty of them the empty engine: body is one \`return 0\`), $nvm VM ($nvmhy of them hybrids that inline a DFA scan, $nvmhyempty of THOSE inlining an empty one; $nvmpl plain), $nrefused refused"
echo "DFA artifacts     prefilter: $(dist "$WORKDIR/seen_pf")"
echo "DFA artifacts     scan     : $(dist "$WORKDIR/seen_scan")"
echo "VM hybrids        prefilter: $(dist "$WORKDIR/seen_hypf")"
echo "VM hybrids        scan     : $(dist "$WORKDIR/seen_hyscan")"
echo "every DFA scan    prefilter: $(cat "$WORKDIR/seen_pf" "$WORKDIR/seen_hypf" | dist /dev/stdin)"
echo "every DFA scan    scan     : $(cat "$WORKDIR/seen_scan" "$WORKDIR/seen_hyscan" | dist /dev/stdin)"

if [ "$ndfa" -eq 0 ] || [ "$nvm" -eq 0 ]; then
    bad "dfa-stamps: the sweep saw $ndfa DFA and $nvm VM artifacts — a bucket with no members asserts nothing"
fi
[ "$nmiss" -eq 0 ] && ok "[stamps] all $ndfa DFA artifacts carry exactly one RX_ENGINE \"dfa\", and all $nvm VM artifacts one RX_ENGINE \"vm\"" \
                   || bad "[stamps] $nmiss artifact(s) are missing a selection stamp"
[ "$ndup"  -eq 0 ] && ok "[stamps] no artifact carries a duplicated RX_DFA_SCAN/RX_DFA_PREFILTER line" \
                   || bad "[stamps] $ndup artifact(s) carry a duplicated stamp line"
# [DD-13c] (r37 #6) THE IFF, both directions, both populations printed. Two
# separate verdicts and not one, because they are two different bugs: a stamp
# on an artifact with nothing to describe, and an artifact that carries the
# whole mechanism and says nothing.
[ "$nleak" -eq 0 ] && ok "[iff] none of the $nvmpl VM artifacts WITHOUT an inlined DFA scan carries a RX_DFA_* macro" \
                   || bad "[iff] $nleak VM artifact(s) carry a RX_DFA_* macro with no DFA scan in the artifact to describe"
[ "$nvmsilent" -eq 0 ] && ok "[iff] all $nvmhy VM HYBRID artifacts stamp RX_DFA_SCAN + RX_DFA_PREFILTER for the scan they inline (r37 #6)" \
                       || bad "[iff] $nvmsilent VM hybrid artifact(s) inline a DFA scan and stamp nothing about it"
[ "$nvmpfbad" -eq 0 ] && ok "[iff] RX_VM_PREFILTER \"hybrid\" agrees with the presence of an inlined rx_prefilter body on all $nvm VM artifacts" \
                      || bad "[iff] $nvmpfbad VM artifact(s) stamp an RX_VM_PREFILTER their emitted text contradicts"
if [ "$nvmhy" -eq 0 ] || [ "$nvmpl" -eq 0 ]; then
    bad "[iff] the sweep saw $nvmhy hybrid and $nvmpl plain VM artifacts — an iff with an empty side asserts only one implication"
else
    ok "[iff] both sides of the iff are populated ($nvmhy hybrid, $nvmpl plain)"
fi
# [DD-13c] THE COMPARED POPULATION IS EVERY ARTIFACT THAT CONTAINS A DFA SCAN —
# the DFA artifacts (empty engine included, which since r37 #5 has a value of
# its own rather than an exemption) AND the VM hybrids, which are held to the
# SAME two comparisons against the SAME markers.
[ "$nscan" -eq 0 ] && ok "[agreement] RX_DFA_SCAN matches the emitted scan shape on all $((ndfa + nvmhy)) artifacts that contain a DFA scan ($ndfa DFA incl. $nempty empty-engine, $nvmhy hybrid)" \
                   || bad "[agreement] $nscan artifact(s) stamp a scan shape their emitted body does not have"
[ "$npf"   -eq 0 ] && ok "[agreement] RX_DFA_PREFILTER matches the emitted prefilter on all $((ndfa - nempty + nvmhy)) artifacts it is compared on ($((ndfa - nempty)) DFA artifacts with a loop + all $nvmhy hybrids; the $nempty empty-engine DFA artifacts are asserted \"none\" on the line below instead)" \
                   || bad "[agreement] $npf artifact(s) stamp a prefilter their emitted loop does not have"
[ "$nemptypf" -eq 0 ] && ok "[agreement] all $nempty empty-engine artifacts (a proven-no-match pattern: body is one \`return 0\`) stamp RX_DFA_PREFILTER \"none\"" \
                      || bad "[agreement] $nemptypf empty-engine artifact(s) stamp a prefilter, on a search function with no loop in it"
# r37 #2 (critDD13b): a floor of one answers "did the bucket vanish", never
# "does it hold exactly the right ones" -- a marker that started matching
# artifacts WITH a loop would route them past the scan comparison while the
# floor stayed green. So the bucket is an EXACT, NAMED set: the four
# provably-empty patterns the corpus carries today. A fifth member is a
# finding (name it here after reading why), a missing one is a regression.
EMPTY_MANIFEST='\B\b
\b\B
\d\b\w
a\bb'
sed -n 's/^EMPTYPAT //p' "$WORKDIR/verdicts" | LC_ALL=C sort -u > "$WORKDIR/empty_seen"
printf '%s\n' "$EMPTY_MANIFEST" | LC_ALL=C sort -u > "$WORKDIR/empty_want"
if cmp -s "$WORKDIR/empty_seen" "$WORKDIR/empty_want"; then
    ok "[agreement] the empty-engine bucket is EXACTLY its named manifest ($(wc -l < "$WORKDIR/empty_want") patterns: $(paste -sd' ' "$WORKDIR/empty_want"))"
else
    bad "[agreement] the empty-engine bucket differs from its named manifest -- only: $(LC_ALL=C comm -23 "$WORKDIR/empty_seen" "$WORKDIR/empty_want" | paste -sd' ') ; missing: $(LC_ALL=C comm -13 "$WORKDIR/empty_seen" "$WORKDIR/empty_want" | paste -sd' ') -- a new member is a finding to name here, a lost one a regression; either way the scan comparison's population moved"
fi
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
