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
#                            | "offset-set" | "offset-set-bounded"   [OPT-K]
#
# ...and, since [DD-13c], the RUNTIME MIRRORS of the last two in the emitted
# `struct rx_info` (`.scan`, `.prefilter`; docs/spec/match_api.md §6), which
# this file holds to the macros they mirror on every artifact of both engines.
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
# [DD-13c], 2026-08-25, lane srStamp2 — THREE MORE, one per rule this change
# added. Each planted in the emitter, rebuilt (`make -j4`), run at `PROCS=4`,
# and reverted; the clean baseline for all three is **26 passed / 0 failed**.
#
#   5. `emit_vm.c`'s `if (job->fit.prefilter) pcrec_emit_dfa_scan_stamps(...)`
#      REMOVED — r37 #6 restored as a defect, the hybrid silent again:
#      RED, 21/5 — both hybrid VM witnesses ("carries an inlined DFA scan, but
#      stamps scan=0 prefilter=0"), [iff] "1263 VM hybrid artifact(s) inline a
#      DFA scan and stamp nothing about it", AND the two comparison-shortfall
#      lines ("the SCAN comparison ran on 995 artifacts but 2258 contain a DFA
#      scan ... 1263 were routed past it"; the same for the prefilter axis).
#      The DFA half, the empty bucket and its manifest all stayed GREEN.
#      **THOSE LAST TWO REDS ARE WHY THE DENOMINATORS ARE COUNTED.** On the
#      first pass this plant scored 21/3: the [agreement] verdicts read "all
#      2258 artifacts" while 1,263 had been routed past the comparison by the
#      missing-stamp `continue` — a TRUE sentence about a population nobody
#      compared, which is docs/dev/learnings.md §3's failure appearing inside a
#      check written to that lesson. `SCANCMP`/`PFCMP` are counted at the
#      comparison sites now and the shortfall is asserted.
#   6. the same call left in but the `fit.prefilter` GATE dropped, so a
#      NON-hybrid VM artifact carries the macros too (`job->engine` unset =>
#      it stamps "empty"/"none" about a DFA that does not exist):
#      RED, 24/2 — the `(a)\1` witness and [iff] "225 VM artifact(s) carry a
#      RX_DFA_* macro with no DFA scan in the artifact to describe". The
#      hybrid direction of the iff stayed GREEN, which is the point of
#      asserting an iff as two verdicts rather than one.
#   7. `dfa_scan_name`'s `if (dfa_engine_is_empty(cx)) return "empty";`
#      REMOVED — r37 #5 restored as a defect:
#      RED, 23/3 — both `empty` witnesses (`\B\b` reverts to "unanchored",
#      `^\B\b` to "attempt": the two engines' different wrong answers) and
#      [agreement] "8 artifact(s) stamp a scan shape their emitted body does
#      not have" — 4 DFA artifacts + the 4 hybrids that inline an empty scan.
#      The printed scan tally reverts to `unanchored=815 attempt=180` with no
#      `empty` value at all, which is the distribution [DD-13] shipped. The
#      iff and the manifest stayed GREEN.
#
#   8. `emit_info_def`'s `.scan` written from a SECOND spelling (the literal
#      "unanchored") instead of `dfa_scan_name` — the runtime mirror and the
#      macro derived independently, which is the one thing the "one derivation,
#      two spellings" claim forbids:
#      RED, 28/1 — [mirror] "376 rx_info field(s) disagree with the macro they
#      mirror". **376 IS EXACTLY 368 `attempt` + 8 `empty`**, i.e. every
#      artifact whose scan is not the planted constant and nothing else, which
#      is the red localising to the defect rather than going uniformly red.
#   9. the mirror fields not emitted at all (`if (0)` on both arms):
#      RED, 27/2 — [mirror] "2483 artifact(s) are missing an rx_info mirror
#      field" AND [mirror] "the mirror comparison ran on 0 artifacts but 2483
#      compiled — 2483 were routed past it". **THE SECOND RED IS THE POINT.**
#      Without the line-count assertion and the counted denominator, a mirror
#      that silently stopped being emitted would make the value comparison
#      VACUOUSLY TRUE and this check would have gone green on an artifact
#      surface that no longer existed.
#
# Recorded as run, from `scratchpad/srStamp2/v_*.log`.
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
PF_VALUES="none memchr memchr-bounded byte-class byte-class-bounded offset-set offset-set-bounded"

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
        # [CC-DIFF] STEP 1(b): was rx_forward_next_state[ (the forward table
        # declaration itself) until the uniform-table fold made that
        # declaration OPTIONAL -- a folded machine emits no table at all, so
        # that anchor read no loop on every folded artifact (31 in the
        # corpus at this writing) though the unanchored scan is genuinely
        # there. The call site survives folding UNCHANGED (token_step keeps
        # the call and the state/class arguments; only the table argument
        # drops) and is unique to this shape -- attempt dispatches by
        # goto star, never by a _step call -- so it is the anchor that does
        # not go stale when the table it used to name stops existing.
        /forward_state = rx_forward_step\(/    { unanch = 1 }                   # emit_unanchored: the forward step call
        /const void \*q = memchr\(subject \+ start, /   { pf_at = 1 }           # emit_attempt: D63 attempt skip
        /const void \*q = memchr\(subject \+ scan_position, / {                 # emit_unanchored: the memchr arm
                                                 pf_mc = 1
                                                 if ($0 ~ /subject_length - 1 - scan_position\)/) bnd = 1 }
        /!rx_can_begin_match\[subject\[scan_position\]\]/ {                     # emit_unanchored: the bitmap arm
                                                 pf_bc = 1
                                                 if ($0 ~ /while \(scan_position \+ 1 < subject_length &&/) bnd = 1 }
        # [OPT-K] the offset-k arm. The CALL is the marker, not the body of
        # the helper: that body is emitted at file scope and its `memchr` and
        # bitmap lines read `pos` where the four older arms above read
        # `scan_position`, so no pattern of theirs can fire on it and the two
        # derivations stay independent by spelling rather than by order.
        # (NO APOSTROPHES IN THIS BLOCK: it is inside a single-quoted awk
        # program, and one closes it -- which is how this comment was written
        # the first time, and bash reported the syntax error 14 lines below.)
        /size_t cand = rx_ofsskip\(subject, subject_length, scan_position/ {
                                                 pf_ofs = 1 }
        /^            if \(cand < subject_length\) \{$/ { ofs_bnd = 1 }         # emit_unanchored: the D11 clamp arm
        # ---- (ii) STAMPED: the `#define` lines, and nothing else -----------
        /^#define RX_ENGINE "/        { ne++; s_eng  = substr($3, 2, length($3) - 2) }
        /^#define RX_DFA_SCAN "/      { ns++; s_scan = substr($3, 2, length($3) - 2) }
        /^#define RX_DFA_PREFILTER "/ { np++; s_pf   = substr($3, 2, length($3) - 2) }
        /^#define RX_VM_PREFILTER "/  { s_vmpf = substr($3, 2, length($3) - 2) }   # [DD-13c] the OTHER side of the iff
        # ---- (iii) MIRRORED: the rx_info struct literal, and nothing else ---
        # [DD-13c] A THIRD SOURCE, kept as separate from the other two as they
        # are from each other. These are emit_info_def initializer lines, not
        # #defines and not matcher text, so "macro == field" below is a claim
        # about the emitter rather than about arithmetic. NULL is carried
        # through as "-" so an absent field and a present-but-NULL one stay
        # distinguishable (nf* count the LINES).
        /^    \.scan = /      { nfscan++
                                f_scan = ($3 == "NULL,") ? "-" : substr($3, 2, length($3) - 3) }
        /^    \.prefilter = / { nfpf++
                                f_pf   = ($3 == "NULL,") ? "-" : substr($3, 2, length($3) - 3) }
        END {
            eng = vm ? "vm" : "dfa"
            scan = attempt ? "attempt" : (unanch ? "unanchored" : (mtnothing ? "empty" : "-"))
            if (pf_ofs)     pf = ofs_bnd ? "offset-set-bounded" : "offset-set"
            else if (pf_bc) pf = bnd ? "byte-class-bounded" : "byte-class"
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
                  (s_vmpf == "" ? "-" : s_vmpf), \
                  (f_scan == "" ? "-" : f_scan), (f_pf == "" ? "-" : f_pf), \
                  nfscan + 0, nfpf + 0
        }'
}

# ---------------------------------------------------------------------------
# [DD-13c] THE RUNTIME MIRRORS: `rx_info.scan` / `.prefilter` vs the macros.
# ---------------------------------------------------------------------------
# Frank's D40-addendum ruling gave the two selection facts RUNTIME mirrors, for
# a consumer with no header to read the macros from (dlopen, an FFI binding, a
# linker walking several `<prefix>_info` symbols). The emitter derives macro and
# field from ONE pair of functions, so what is worth checking is not the value
# — the corpus sweep above already holds the MACRO to the emitted loop — but
# that the two SPELLINGS of it did not come apart:
#
#     .scan       == <PREFIX>_DFA_SCAN        when the macro is present
#     .scan       == NULL                     when it is absent
#     .prefilter  == <PREFIX>_DFA_PREFILTER   when the macro is present
#     .prefilter  == "none"                   when it is absent (the VM's own
#                                             vocabulary: a non-hybrid VM
#                                             artifact has no candidate-start
#                                             filter, and RX_VM_PREFILTER reads
#                                             "none" on exactly those)
#
# BOTH FIELDS ARE ON EVERY ARTIFACT, both engines, so the LINE COUNT is checked
# too (exactly one of each): a mirror that silently stopped being emitted on one
# engine would otherwise leave the comparison vacuous on that half.
#
# Echoes MIRRORCMP per comparison so the verdict quotes a COUNTED population
# rather than one derived from bucket sizes — the lesson validation 5 below
# taught this file about its own agreement denominators.
mirror_check() {
    _ms="$1"; _mp="$2"; _fs="$3"; _fp="$4"; _nfs="$5"; _nfp="$6"; _what="$7"
    if [ "$_nfs" -ne 1 ] || [ "$_nfp" -ne 1 ]; then
        echo MIRRORMISS; echo "BAD: rx_info is missing a mirror field (scan lines=$_nfs prefilter lines=$_nfp): $_what"
        return
    fi
    echo MIRRORCMP
    _ws="$_ms"; [ "$_ms" = "-" ] && _ws="-"
    _wp="$_mp"; [ "$_mp" = "-" ] && _wp="none"
    [ "$_fs" = "$_ws" ] || { echo MIRRORBAD; echo "BAD: rx_info.scan '$_fs' vs macro '$_ms' (expected '$_ws'): $_what"; }
    [ "$_fp" = "$_wp" ] || { echo MIRRORBAD; echo "BAD: rx_info.prefilter '$_fp' vs macro '$_mp' (expected '$_wp'): $_what"; }
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
# [OPT-K] RE-ANCHORED, and the reason is the finding rather than a rename: the
# four patterns these rows used to name (`abc`, `[af]bc|[gz]bc`, `abc$`,
# `(?:[af]bc|[gz]bc)\z`) all have a SECOND selective offset and now take the
# offset-set form, measured 1.7x-3.5x faster for it. A witness for the
# offset-0 forms must therefore be a pattern with NO second offset at all --
# one byte long -- which is what these four are. They are strictly better
# witnesses than the old ones: each names its value for a structural reason
# (a one-byte pattern cannot have an offset 1) instead of by happening to
# fall on the near side of a cost model.
witness unanchored memchr             'a'
witness unanchored byte-class         '[af]'
witness unanchored memchr-bounded     'a$'
witness unanchored byte-class-bounded '[af]$'
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
# [OPT-K] THE TWO OFFSET-SET FORMS, and a REQUIRED synthetic witness each: the
# corpus's own patterns are short and mostly reach the form through `\b`, so
# the unbounded arm has no natural population at all ([CHK-2] piece 3's rule —
# a value with zero corpus witnesses gets a synthetic one or it is untested).
# `\d{4}-\d{2}-\d{2}` is `iso-ts`'s prefix: no view, no word context, so the
# skip keeps its early-out. `\b[0-9a-f]{8}-[0-9a-f]{4}` is `uuid`'s: the `\b`
# puts a word context on the machine, so it takes the D11 clamp.
witness unanchored offset-set         '\d{4}-\d{2}-\d{2}'
witness unanchored offset-set-bounded '\b[0-9a-f]{8}-[0-9a-f]{4}'

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
command -v mirror_check >/dev/null || { echo "BAD: worker did not inherit mirror_check"; exit 1; }
art="$WORKDIR/a.$$.c"
trap 'rm -f "$art"' EXIT
while IFS= read -r pat; do
    if ! pcrec_run "$PCREC" --features all -p rx -o - -- "$pat" > "$art" 2>/dev/null; then
        echo REFUSED; continue
    fi
    set -- $(read_artifact < "$art")
    d_eng="$1"; d_scan="$2"; d_pf="$3"
    s_eng="$4"; s_scan="$5"; s_pf="$6"; ne="$7"; ns="$8"; np="$9"; shift 9
    s_vmpf="$1"; f_scan="$2"; f_pf="$3"; nfscan="$4"; nfpf="$5"
    # [DD-13c] THE RUNTIME MIRRORS, on EVERY artifact of BOTH engines and
    # BEFORE the engine fork below, because the claim is not engine-specific:
    # whatever the macros say (including saying nothing), the struct must agree.
    mirror_check "$s_scan" "$s_pf" "$f_scan" "$f_pf" "$nfscan" "$nfpf" "$pat"
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
        echo SCANCMP; echo PFCMP
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
        echo SCANCMP
        [ "$s_scan" = "empty" ] || { echo SCANBAD; echo "BAD: SCAN: stamp '$s_scan' on a body that is one \`return 0\` (expected 'empty'): $pat"; }
        continue
    fi
    echo SCANCMP; echo PFCMP
    [ "$s_scan" = "$d_scan" ] || { echo SCANBAD; echo "BAD: SCAN: stamp '$s_scan' vs loop '$d_scan': $pat"; }
    [ "$s_pf"   = "$d_pf"   ] || { echo PFBAD;   echo "BAD: PREFILTER: stamp '$s_pf' vs loop '$d_pf': $pat"; }
done
WORKER

export WORKDIR PCREC SCAN_VALUES PF_VALUES ROOT_DIR
export -f read_artifact mirror_check
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
# [DD-13c] THE AGREEMENT DENOMINATORS ARE COUNTED AT THE COMPARISON SITES, not
# derived by arithmetic from the bucket sizes. MEASURED REASON, from this
# change's own validation V1 (the hybrid stamps removed): with the denominator
# written as `ndfa + nvmhy` the [agreement] line still read "all 2258
# artifacts" while 1,263 of them had been routed past the comparison by the
# missing-stamp `continue` — a true statement about a population nobody
# compared, which is docs/dev/learnings.md §3's failure exactly. A counted
# denominator collapses instead, and the assertion below makes the collapse a
# RED rather than a number a reader has to notice.
nscancmp=$(tok SCANCMP); npfcmp=$(tok PFCMP)
nmirror=$(tok MIRRORCMP); nmirrorbad=$(tok MIRRORBAD); nmirrormiss=$(tok MIRRORMISS)
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
# CEILING RE-PINNED 2026-09-05 (the first full battery after the utf8 corpus
# merged): 289 -> 468 measured, and the growth is EXPLAINED before re-pinned —
# this sweep compiles bare pattern LINES under the DEFAULT (byte) encoding,
# and tests/utf8/'s patterns carrying \x{>FF} or raw multi-byte literals are
# range-REFUSED there by design ([M5.0] stage 2: \x{} is base grammar
# range-checked per encoding). Those patterns' stamp coverage lives in their
# own encoding-aware suites; here they are honest refusals, not eaten
# population. Ceiling 550 keeps the guard's headroom shape (~1.18x, as 400
# was to 289).
[ "$nrefused" -le 550 ] || bad "[population] $nrefused patterns REFUSED (ceiling 550; 468 measured 2026-09-05, 289 2026-08-25) — a feature gate or a compiler bound is eating the population"
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
[ "$nscan" -eq 0 ] && ok "[agreement] RX_DFA_SCAN matches the emitted scan shape on all $nscancmp artifacts it was compared on" \
                   || bad "[agreement] $nscan artifact(s) stamp a scan shape their emitted body does not have"
[ "$npf"   -eq 0 ] && ok "[agreement] RX_DFA_PREFILTER matches the emitted prefilter on all $npfcmp artifacts it was compared on" \
                   || bad "[agreement] $npf artifact(s) stamp a prefilter their emitted loop does not have"
# ...and the COMPARED population is the one that should have been compared.
# Anything that routes an artifact past a comparison (a missing stamp, a
# duplicated one, an undocumented value) shows up here as a shortfall rather
# than as a green claim about a population nobody looked at.
if [ "$nscancmp" -eq $((ndfa + nvmhy)) ]; then
    ok "[agreement] the SCAN comparison ran on every artifact that contains a DFA scan: $nscancmp = $ndfa DFA (incl. $nempty empty-engine) + $nvmhy hybrid"
else
    bad "[agreement] the SCAN comparison ran on $nscancmp artifacts but $((ndfa + nvmhy)) contain a DFA scan ($ndfa DFA + $nvmhy hybrid) — $(( ndfa + nvmhy - nscancmp )) were routed past it, so the agreement verdict above is a claim about a population that was not compared"
fi
if [ "$npfcmp" -eq $((ndfa - nempty + nvmhy)) ]; then
    ok "[agreement] the PREFILTER comparison ran on every artifact with a loop: $npfcmp = $((ndfa - nempty)) DFA with a loop + $nvmhy hybrid (the $nempty empty-engine DFA artifacts are asserted \"none\" instead, below)"
else
    bad "[agreement] the PREFILTER comparison ran on $npfcmp artifacts but $((ndfa - nempty + nvmhy)) were due — $(( ndfa - nempty + nvmhy - npfcmp )) were routed past it"
fi
[ "$nemptypf" -eq 0 ] && ok "[agreement] all $nempty empty-engine artifacts (a proven-no-match pattern: body is one \`return 0\`) stamp RX_DFA_PREFILTER \"none\"" \
                      || bad "[agreement] $nemptypf empty-engine artifact(s) stamp a prefilter, on a search function with no loop in it"
# r37 #2 (critDD13b): a floor of one answers "did the bucket vanish", never
# "does it hold exactly the right ones" -- a marker that started matching
# artifacts WITH a loop would route them past the scan comparison while the
# floor stayed green. So the bucket is an EXACT, NAMED set: the four
# provably-empty patterns the corpus carries today. A fifth member is a
# finding (name it here after reading why), a missing one is a regression.
# [M5.0 stage 3] TWELVE NEW MEMBERS, NAMED, and they are a DIFFERENT KIND of
# empty from the four above. Those four are empty because two assertions
# CONTRADICT (`\B\b` can never both hold). These twelve are empty because a
# PROPERTY SET INTERSECTED WITH THE `byte` ENCODING'S UNIVERSE IS EMPTY:
# `pcrec_ast_class_from_iv` clamps a property to [0, max_cp] (PCRE2's own
# 8-bit non-UTF behaviour), and every member of these twelve lies above 0xFF.
# Titlecase letters start at U+01C5; the surrogates and the private-use area
# are wholly above it; Latin-1 is fully ASSIGNED, so `Cn` has nothing there;
# and no Latin-1 code point is a combining mark, a letter modifier, a
# letter-number, or a line/paragraph separator.
#
# **ORACLE-VERIFIED, not reasoned**: `tests/uprops/`'s membership differential
# compares exactly these twelve against libpcre2 over all 256 bytes and
# reports ZERO disagreements, so an empty artifact is the RIGHT artifact here.
#
# They land in this bucket rather than being routed past the scan comparison
# by accident: the assertion directly above this one confirms all 16 stamp
# `RX_DFA_PREFILTER "none"`, i.e. all 16 really are loop-free.
EMPTY_MANIFEST='\B\b
\b\B
\d\b\w
a\bb
\p{Cn}
\p{Co}
\p{Cs}
\p{Lm}
\p{Lt}
\p{M}
\p{Mc}
\p{Me}
\p{Mn}
\p{Nl}
\p{Zl}
\p{Zp}'
sed -n 's/^EMPTYPAT //p' "$WORKDIR/verdicts" | LC_ALL=C sort -u > "$WORKDIR/empty_seen"
printf '%s\n' "$EMPTY_MANIFEST" | LC_ALL=C sort -u > "$WORKDIR/empty_want"
if cmp -s "$WORKDIR/empty_seen" "$WORKDIR/empty_want"; then
    ok "[agreement] the empty-engine bucket is EXACTLY its named manifest ($(wc -l < "$WORKDIR/empty_want") patterns: $(paste -sd' ' "$WORKDIR/empty_want"))"
else
    bad "[agreement] the empty-engine bucket differs from its named manifest -- only: $(LC_ALL=C comm -23 "$WORKDIR/empty_seen" "$WORKDIR/empty_want" | paste -sd' ') ; missing: $(LC_ALL=C comm -13 "$WORKDIR/empty_seen" "$WORKDIR/empty_want" | paste -sd' ') -- a new member is a finding to name here, a lost one a regression; either way the scan comparison's population moved"
fi
[ "$nempty" -eq 0 ] && bad "[agreement] the empty-engine bucket is EMPTY — \`\\B\\b\` and its three siblings are in the corpus and must land here; a zero means the text marker stopped matching and the bucket is silently exempting nothing (or, worse, everything)" \
                    || ok "[agreement] the empty-engine bucket holds $nempty artifact(s), asserted non-vacuous"
# [DD-13c] the runtime mirrors, over the WHOLE population of both engines.
if [ "$nmirrormiss" -eq 0 ]; then
    ok "[mirror] every one of the $((ndfa + nvm)) artifacts carries exactly one rx_info.scan and one .prefilter field (both engines)"
else
    bad "[mirror] $nmirrormiss artifact(s) are missing an rx_info mirror field — the comparison below is vacuous on them"
fi
[ "$nmirrorbad" -eq 0 ] && ok "[mirror] rx_info.scan/.prefilter agree with <PREFIX>_DFA_SCAN/_DFA_PREFILTER on all $nmirror artifacts compared (NULL/\"none\" where the macros are absent) — one derivation, two spellings" \
                        || bad "[mirror] $nmirrorbad rx_info field(s) disagree with the macro they mirror"
if [ "$nmirror" -eq $((ndfa + nvm)) ]; then
    ok "[mirror] the mirror comparison ran on every compiled artifact: $nmirror = $ndfa DFA + $nvm VM"
else
    bad "[mirror] the mirror comparison ran on $nmirror artifacts but $((ndfa + nvm)) compiled — $(( ndfa + nvm - nmirror )) were routed past it"
fi
[ "$nvalue" -eq 0 ] && ok "[values] every stamped value is one of the documented set (scan: $SCAN_VALUES; prefilter: $PF_VALUES)" \
                    || bad "[values] $nvalue stamp(s) carry a value outside the documented set — a new mechanism needs its match_api.md §6.3 hunk and a line in this file"

if [ -s "$WORKDIR/bad" ]; then echo; echo "FAILURES:" >&2; head -30 "$WORKDIR/bad" >&2; fi
echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
