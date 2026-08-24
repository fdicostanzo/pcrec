#!/usr/bin/env bash
# tests/reject/run_reject_tests.sh — the mandate's central guarantee, tested.
#
# WHY THIS EXISTS. The project rule is that a construct outside the base tier
# must "fail with a clean 'requires module X' error, never miscompile". Until
# this file, NOTHING checked that. The .rxt corpus cannot: a `perr` block
# asserts only THAT the pattern is rejected, never WHY, and the module name is
# the whole point (assertion 2 below).
#
# CORRECTED 2026-08-10 (FIX-1). This comment used to add a second reason — that
# a `perr` block also needs the PYTHON oracle to fail, and that `# pcre2-only`
# cannot rescue it "because verify_rxt.py's perr branch does not consult it".
# The first half is true; the second is FALSE, and it was never measured. The
# skip test at verify_rxt.py:218 sits BEFORE the perr branch at :222, so a
# `# pcre2-only` block's perr line is skipped like any other case. Measured:
# tests/base/syntax_errors.rxt now carries seven such blocks for K5 and
# verify_rxt.py reports them as skipped while run.sh still asserts every one
# against pcrec. So the mechanism exists — it just cannot assert a NAME, which
# is why this file is still the only home for that.
#
# The gap was not hypothetical. `\v` was decoded as vertical tab (0x0B) when
# PCRE2 defines it as vertical WHITESPACE (0x0a 0x0b 0x0c 0x0d 0x85) — a silent
# miscompile that survived because python `re` reads `\v` as 0x0B too, so the
# base-tier oracle agreed with the bug. It was found by reading the PCRE2
# syntax reference against the parser, not by any test. This file is the net
# that should have caught it.
#
# WHAT IT ASSERTS, per construct:
#   1. pcrec exits exactly 1 — not 0 (accepted, i.e. possibly miscompiled) and
#      not >=124 (crash/timeout). A crash must never satisfy a rejection
#      expectation (the same rule the .rxt harness applies to perr, R1 P-C1).
#   2. the diagnostic contains the expected text, normally "requires module
#      'NAME'". Getting the NAME right matters: it is the caller's only
#      pointer to what would implement the construct.
#   3. no output file is left behind by a failed compile.
#
# Usage: bash tests/reject/run_reject_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# [SR-11] table_contract.md's one implementation (tests/lib/table.sh):
# resolves `--list-syntax` columns by NAME rather than this file hand-rolling
# its own index map, which is what let a `NF != 15` hardcode drift silently
# past D65's appended 16th column (docs/design/registry_built_status_memo.md's
# Correction section) until the iteration's own non-vacuity floor caught it.
. "$ROOT_DIR/tests/lib/table.sh"
# [TT-6] resolves TIMEOUT_BIN once for this file's own bare `timeout` calls
# below (this suite does not otherwise source tests/lib/gen_timeout.sh).
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "reject: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
    if [ -n "${pardir:-}" ]; then
        if [ "$KEEP" = "1" ]; then echo "reject: KEEP=1, shard temp dir: $pardir" >&2
        else rm -rf "$pardir"; fi
    fi
}
trap cleanup EXIT

# [TT-2] internal parallelism, PROCS=N (default 1, unchanged behaviour).
# run.sh's own worker-reinvocation pattern, sharded by CALL INDEX rather
# than by FILE: this is one file with hundreds of independent
# subprocess-bound checks (`timeout ... $PCREC ...`), not many files, so
# there is no natural file-level split — see docs/testing.md "Internal
# parallelism" for the design and the measured wall-time.
#
# Every reject/accept/reject_gated/row_reject/pinned call increments ONE
# shared `callidx` and only does its real work when
# `callidx % SHARD_TOTAL == SHARD_INDEX` — SHARD_TOTAL=1 (PROCS=1, the
# default) makes every call match (n % 1 == 0 always), so serial behaviour
# is untouched, byte for byte, and not one check call site changes.
PROCS="${PROCS:-1}"
case "$PROCS" in (''|*[!0-9]*) echo "reject: PROCS must be a positive integer, got '$PROCS'" >&2; exit 2;; esac
[ "$PROCS" -ge 1 ] || { echo "reject: PROCS must be >= 1, got '$PROCS'" >&2; exit 2; }
SHARD_INDEX="${REJECT_SHARD_INDEX:-0}"
SHARD_TOTAL="${REJECT_SHARD_TOTAL:-1}"
callidx=0

pass=0; fail=0
seen=""   # every pattern that actually PASSED a check, for the manifest below
# [TT-2] every counter EACH check function drives is initialized HERE, once,
# rather than scattered as a bare `nrej=0`/`naccept=0`/... right before each
# function's own definition (where it used to live) — those are ordinary
# top-level statements, not inside any function, so they run unconditionally
# every time execution reaches them. The PARENT process in the PROCS>1
# dispatch below (see the DISPATCHER block a few lines down) sets these same
# variables to the AGGREGATED totals and then falls through the rest of this
# file with every check call gated into a no-op — and a stray `nrej=0`
# sitting later in the file, reached by that same fallthrough, would silently
# re-zero the aggregate the instant execution passed it. Consolidating them
# here, before the dispatcher can possibly run, is what makes that
# impossible rather than merely unlikely.
nrej=0; naccept=0; ngated=0; niter=0; nwrong=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# [TT-2] the PROCS>1 DISPATCHER. Only the TOP-LEVEL invocation takes this
# branch (a re-invoked shard child always has REJECT_SHARD_TOTAL set, so it
# skips straight past this whole block and into the real body below). It
# spawns PROCS shard workers — each the WHOLE, UNMODIFIED rest of this
# script, re-invoked with REJECT_SHARD_INDEX/REJECT_SHARD_TOTAL set — waits,
# and aggregates. "aggregates" means literally: sum every shard's counters,
# concatenate every shard's `$seen` slice into THIS process's own `$seen`,
# then fall through into the body with SHARD_INDEX/SHARD_TOTAL set so every
# check call below no-ops (n % 1 == -1 can never hold) — the real work
# already happened in the children, so the parent must not redo it. The
# UNCHANGED tail at the end of this file (duplicate check, MANIFEST,
# final-count assertions, summary) then runs ONCE, here, against the true
# aggregate — exactly the same logic a plain PROCS=1 run reaches at the same
# place, just fed pre-summed numbers instead of directly-accumulated ones.
if [ "$PROCS" -gt 1 ] && [ -z "${REJECT_SHARD_TOTAL:-}" ]; then
    pardir="$(mktemp -d)"
    for ((_i = 0; _i < PROCS; _i++)); do
        REJECT_SHARD_INDEX="$_i" REJECT_SHARD_TOTAL="$PROCS" \
            REJECT_SEEN_FILE="$pardir/$_i.seen" \
            REJECT_RESULT_FILE="$pardir/$_i.result" PCREC="$PCREC" KEEP="$KEEP" \
            bash "${BASH_SOURCE[0]}" > "$pardir/$_i.out" 2> "$pardir/$_i.err" &
    done
    wait

    pass=0; fail=0; nrej=0; naccept=0; ngated=0; niter=0; nwrong=0; seen=""
    reports=0
    for ((_i = 0; _i < PROCS; _i++)); do
        # replay each shard's own DISPLAY output only (PASS/FAIL lines and
        # any diagnostics) — the machine-readable result block lives in its
        # own .result file (below), never mixed into .out/.err, so it can
        # never leak into what a human reading `make test-reject` sees. In
        # shard order, so nothing interleaves mid-line — the same
        # legibility rule run.sh's own PROCS>1 parent aggregation follows.
        cat "$pardir/$_i.err" >&2
        cat "$pardir/$_i.out"
        p="$(grep -m1 '^shard_pass:'    "$pardir/$_i.result" 2>/dev/null | grep -oE '[0-9]+$')"
        x="$(grep -m1 '^shard_fail:'    "$pardir/$_i.result" 2>/dev/null | grep -oE '[0-9]+$')"
        if [ -z "$p" ] || [ -z "$x" ]; then
            # [TT-2 discipline] a lost/crashed worker is a HARD FAIL, never
            # read as a pass — it never gets to contribute a shard_pass/
            # shard_fail line, so its absence is what this branch catches.
            echo "reject: HARD FAILURE: shard $_i produced no result block (crashed, timed out, or was killed) — counting as failed" >&2
            fail=$((fail + 1))
            continue
        fi
        reports=$((reports + 1))
        r="$(grep -m1  '^shard_nrej:'    "$pardir/$_i.result" | grep -oE '[0-9]+$')"
        a="$(grep -m1  '^shard_naccept:' "$pardir/$_i.result" | grep -oE '[0-9]+$')"
        g="$(grep -m1  '^shard_ngated:'  "$pardir/$_i.result" | grep -oE '[0-9]+$')"
        it="$(grep -m1 '^shard_niter:'   "$pardir/$_i.result" | grep -oE '[0-9]+$')"
        w="$(grep -m1  '^shard_nwrong:'  "$pardir/$_i.result" | grep -oE '[0-9]+$')"
        pass=$((pass + p)); fail=$((fail + x))
        nrej=$((nrej + ${r:-0})); naccept=$((naccept + ${a:-0}))
        ngated=$((ngated + ${g:-0})); niter=$((niter + ${it:-0}))
        nwrong=$((nwrong + ${w:-0}))
        [ -s "$pardir/$_i.seen" ] && seen="$seen
$(cat "$pardir/$_i.seen")"
    done
    if [ "$reports" -ne "$PROCS" ]; then
        echo "reject: HARD FAILURE: $((PROCS - reports)) of $PROCS shard worker(s) vanished without a result block — a lost worker is never counted as a pass" >&2
    fi

    # From here on this process must NOT also run the checks for real (the
    # children already did): SHARD_INDEX=-1 can never equal callidx %
    # SHARD_TOTAL for any SHARD_TOTAL >= 1 (a mod is never negative), so
    # every reject/accept/reject_gated/row_reject/pinned call below is a
    # guaranteed no-op and the counters/`$seen` set above survive untouched
    # into the tail.
    SHARD_INDEX=-1
    SHARD_TOTAL=1
fi

reject() { # reject <pattern> <expected-substring> [display-label]
    # [TT-2] internal-parallelism gate: one shared call counter across every
    # check function in this file; a call only does its real work (the
    # `timeout ... $PCREC` invocation and every counter it drives) in the
    # shard it belongs to. SHARD_TOTAL=1 (PROCS=1, the default) makes this
    # always true -- n % 1 == 0 for every n -- so serial behaviour is
    # untouched, byte for byte. See the PROCS dispatch block near the top of
    # this file and docs/testing.md's "Internal parallelism" section.
    callidx=$((callidx + 1))
    [ $((callidx % SHARD_TOTAL)) -eq "$SHARD_INDEX" ] || return 0
    # `timeout` on every invocation is load-bearing, not defensive (R7/T-11):
    # this file's header promises rc >= 124 is a failure, and without it that
    # branch was UNREACHABLE — pcrec cannot return 124 on its own, so a hanging
    # or ballooning compile hung the suite instead of failing it. Not
    # hypothetical: dropping the `big_n` raise turns three of the K5 rows into
    # legal multi-GB bounded repeats, and a critic observed a 6.5 GB allocation
    # inside an un-timeout-ed call here.
    local pat="$1" want="$2" show="${3:-$1}" out rc
    # A logged pattern containing a NEWLINE splits `seen` into two lines, and
    # the duplicate detector then compares fragments — a two-line pattern whose
    # halves read like unrelated single-line rows reports a FALSE duplicate for
    # rows that are not duplicated at all (R9/C4V-1). `accept()` has carried a
    # display label for this hazard since it was written; `reject()` did not,
    # and the duplicate detector is what made the omission matter. Third
    # argument is that label. Refusing the newline outright rather than only
    # offering the label is deliberate: an optional guard that must be
    # remembered is the same shape as the bug.
    case "$show" in
        *"
"*) bad "reject: a logged pattern contains a newline, which would split the coverage log and confuse the duplicate check. Pass a single-line display label as the third argument"
            return ;;
    esac
    # An EMPTY `want` silently turns assertion 2 back into assertion 1. The text
    # check below is `case "$out" in *"$want"*`, and `*""*` matches every string
    # — so a blanked expectation degrades "rejected for the stated reason" to
    # "rejected at all", passes, and prints `PASS: reject 'X' -> ` with nothing
    # after the arrow, which nothing greps for. Getting the NAME right is this
    # file's entire reason to exist over a `perr` block, so refuse the call
    # rather than let it pass vacuously (R9/C4-1). A genuinely MISSING argument
    # is already loud — `set -u` kills the script — it is the empty string that
    # is quiet. The iterated path guards its own inputs the same way, at the
    # `$3 == "" || $11 == ""` BADROW check.
    #
    # BLANK-ONLY, not merely empty. `[ -z "$want" ]` was the first version and a
    # critic defeated it with a single space: every diagnostic this compiler
    # prints is an English sentence, so `want=" "` is a substring of all of them
    # and asserts nothing (R9/C4V-2). A tab does NOT currently defeat it — no
    # message contains one — but that is a property of today's message corpus,
    # not of the guard, so the guard rejects all whitespace.
    #
    # What this canNOT do, stated rather than implied: a short but non-blank
    # expectation like `:` or `pcrec` is equally uninformative and equally
    # legal. No length or content floor distinguishes a lazy expectation from a
    # legitimately short one, so the guard stops at "asserts literally nothing"
    # and review is what covers the rest.
    case "$want" in
        *[![:space:]]*) ;;
        *) bad "reject '$show': expected-substring is empty or all whitespace. Every pcrec diagnostic contains a space, so that asserts only that pcrec exited 1 — name the diagnostic"
           return ;;
    esac
    # AND THE BLANK GUARD WAS NOT ENOUGH EITHER (R9/C4V-4). Every diagnostic this
    # compiler prints has the identical envelope `pcrec: <message> (pattern
    # offset N)`. A critic ran the whole suite, collected all 200 real
    # diagnostics, and measured which `want` literals match all of them:
    # `:`, `pcrec`, `pattern offset`, `(`, `)` and the single letters
    # a e s n r t o are each 200/200. None is blank, so none was caught.
    #
    # The discriminating rule is not a LENGTH floor — `:` is one character and
    # `(pattern offset 4)` is eighteen, and 31 rows legitimately pin an offset
    # with that suffix, so no floor separates them. What distinguishes them is
    # that everything dangerously generic lives entirely inside the CONSTANT
    # part. So: reject a `want` that is a substring of the envelope itself. It
    # asserts nothing about which construct or module was named.
    # `(pattern offset 4)` is not a substring of it — the digit is real content —
    # so the offset-pinning rows are unaffected.
    case "pcrec: (pattern offset )" in
        *"$want"*)
            bad "reject '$show': expected-substring \"$want\" is part of the envelope EVERY pcrec diagnostic has (\"pcrec: ... (pattern offset N)\"), so it matches all 200 of them and names no construct. Assert the message, not the frame"
            return ;;
    esac
    nrej=$((nrej + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$("$TIMEOUT_BIN" 60 "$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -eq 0 ]; then
        bad "reject '$pat': ACCEPTED (exit 0) — an unsupported construct was compiled instead of diagnosed, which is the miscompile the mandate forbids"
        return
    fi
    if [ "$rc" -ne 1 ]; then
        bad "reject '$pat': exit $rc (crash or timeout), not a clean exit-1 rejection"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "reject '$pat': wrong diagnostic. want substring: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "reject '$pat': rejected but still wrote an output file"
        return
    fi
    seen="$seen
$show"
    ok "reject '$show' -> $want"
}

accept() { # accept <pattern> [display-label]
    # [TT-2] internal-parallelism gate; see reject()'s comment above.
    callidx=$((callidx + 1))
    [ $((callidx % SHARD_TOTAL)) -eq "$SHARD_INDEX" ] || return 0
    # The control: the table must not pass by rejecting everything.
    # The optional label is for patterns containing RAW control bytes, which
    # would otherwise put a newline or a non-UTF-8 byte into this script's own
    # output and break anything that reads it as text.
    local pat="$1" show="${2:-$1}" out rc
    naccept=$((naccept + 1))
    rm -f "$WORKDIR/ok.c" "$WORKDIR/ok.h"
    out="$("$TIMEOUT_BIN" 60 "$PCREC" -p rx -o "$WORKDIR/ok.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -ge 124 ]; then
        bad "accept '$show': exit $rc — timed out or was killed, which is not 'compiles'"
        return
    fi
    if [ "$rc" -ne 0 ]; then
        bad "accept '$show': base-tier construct was REJECTED ($out) — the reject table has swallowed supported syntax"
        return
    fi
    # Exit 0 is not the whole claim (R7/T-10). reject() makes three assertions
    # and this made ONE, so "compiles" meant only "did not say no" — a pcrec
    # that exited 0 and emitted nothing would have satisfied all 45 controls.
    # The `rm` above is as load-bearing as the test: without it a stale file
    # from the previous accept satisfies this vacuously.
    if [ ! -s "$WORKDIR/ok.c" ]; then
        bad "accept '$show': exit 0 but no non-empty output was written — 'compiles' has to mean something was emitted"
        return
    fi
    seen="$seen
$show"
    ok "accept '$show' (base tier still compiles)"
}

# ---- reject_gated: an explicit-features rejection, for pins whose
# diagnostic (or whose very refusal) only holds under a NON-default
# `--features` spec. Originally MOD-0.5c's mechanism for gate-OPEN-only
# diagnostics (`--features modifiers`); [STD1b] (D37, 2026-08-13) also uses
# it as `reject_gated none ...` to keep the PRE-flip bare behaviour pinned
# verbatim now that the bare default itself is `std1` rather than empty —
# moved up here (from its original home just above the MOD-0.5c block much
# further down) so rows anywhere in the file, including the ones the flip
# touches, can call it. Counted in `ngated` either way: a features spec
# other than the bare default is the same kind of pin regardless of WHICH
# named set it pins against.
reject_gated() { # reject_gated <features> <pattern> <expected-substring>
    # [TT-2] internal-parallelism gate; see reject()'s comment above.
    callidx=$((callidx + 1))
    [ $((callidx % SHARD_TOTAL)) -eq "$SHARD_INDEX" ] || return 0
    local feats="$1" pat="$2" want="$3" out rc
    case "$want" in
        *[![:space:]]*) ;;
        *) bad "reject_gated '$pat': blank expectation asserts nothing"; return ;;
    esac
    ngated=$((ngated + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features "$feats" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -eq 0 ]; then
        bad "reject_gated '$pat' (features $feats): ACCEPTED — the gate-open refusal this pin exists for has vanished"
        return
    fi
    if [ "$rc" -ne 1 ]; then
        bad "reject_gated '$pat': exit $rc, not a clean exit-1 rejection"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "reject_gated '$pat': wrong diagnostic. want substring: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ]; then
        bad "reject_gated '$pat': rejected but still wrote an output file"
        return
    fi
    ok "reject_gated [$feats] '$pat' -> $want"
}

# ---- a class-opening construct as a RANGE ENDPOINT (R9/SPEC-FA) ----
# PCRE2 error 150. pcrec read the `[` as an ordinary literal upper bound and
# EMITTED A MATCHER — the silent wrong matcher the mandate forbids, 546
# instances in a 1,530-pattern sweep, and invisible to every suite here.
#
# WHY IT WAS INVISIBLE, which is the part worth keeping: `a` is 0x61 and `[` is
# 0x5b, so `[a-[:digit:]]` is rejected as an out-of-order range long before the
# endpoint matters — and every range in this repository is `a`-based. The bug
# needed a lower bound BELOW `[`. It was found by a test writer working from the
# spec with no sight of the code, which is why the alphabet was `0-` and not
# `a-`. A test derived from the implementation inherits the implementation
# author's alphabet.
reject '[0-[:digit:]]'  "invalid range in character class"
reject '[*-[..]]'       "invalid range in character class"
reject '[A-[=b=]]'      "invalid range in character class"
reject '[0-[.a.]]'      "invalid range in character class"
reject '[0-[:foo:]]'    "invalid range in character class"   # position beats the name
reject '[0-[:digit:]'   "invalid range in character class"   # class never closes
# And the accept-controls that pin where the boundary is NOT. The test is the
# construct's own recognition rule, not "the byte is `[`": each of these has a
# `[` in the endpoint and no pair that closes, and libpcre2 compiles all four.
accept '[0-[a]'
accept '[0-[]'
accept '[0-[:]'
accept '[0-[:digit]'

# ---- the K12 endpoint rule (MOD-0.1, design §16 as R14-corrected) ----
# PCRE2's five-step order: low's own error -> high pair-open short-circuit ->
# high's own error -> either side certifiably SET-shaped -> 150 -> scalar
# ordering. pcrec certifies SET-shape only where the row's measured
# class_expect covers EVERY form that reaches it: the ten char-type escapes
# (the construct IS its selector byte) and the bracket doorway's KNOWN POSIX
# names (the 14-name table validates the body). Every cell below measured
# against libpcre2 10.46 first — tests/probes/probe_endpoint_k12.c.
reject '[0-\d]'         "invalid range in character class"
reject '[\d-z]'         "invalid range in character class"
reject '[z-\d]'         "invalid range in character class"
reject '[\d-\w]'        "invalid range in character class"   # both sides constructs
reject '[0-\V]'         "invalid range in character class"
reject '[\v-z]'         "invalid range in character class"
reject '[[:alpha:]-z]'  "invalid range in character class"   # bracket doorway, LOW side
reject '[x[:alpha:]-z]' "invalid range in character class"   # ...and mid-class
reject '[\d-\A]'        'is not valid inside a character class'  # step 3 beats step 4: PCRE2 107, the high side's OWN error
reject '[\d-\p{Foo}]'   "\\p requires module 'unicode-props' (pattern offset 11)"  # high's own refusal beats low's SET
# The deliberate NON-certified boundary (journal 2026-08-11): \p is
# body-dependent and pcrec has no property table until MOD-0.6, so the module
# promise stays even where PCRE2 says 150 — answering 150 for [0-\p{Foo}]
# would be wrong (PCRE2 147), and the promise stays true (the module owns
# deciding the body). MOD-0.6 phase 2: the WORDING moved from "in a class
# requires module" to the position-invariant mod_uprops.c text (this
# module's messages do not vary by position — same shape as an RD_FIXED
# row's, deliberate, D26 tier 3), so these two re-pin the new text +
# offset rather than the old one.
reject '[0-\p{L}]'      "\\p requires module 'unicode-props' (pattern offset 8)"
reject '[\p{L}-z]'      "\\p requires module 'unicode-props' (pattern offset 6)"
# Non-range dash and truncation: the construct's ordinary class answer USED
# TO stay the standard unimplemented answer (PCRE2 compiles [\d-]; pcrec
# refused it for lacking module 'classes'). [STD1b] (D37, 2026-08-13) flips
# that: `classes` is default-on, so `[\d-]` now compiles (PCRE2 agrees —
# trailing `-` in a class is literal) and `[\d-` now reaches ITS OWN error
# (unterminated class, "missing terminating ]") instead of the classes-gate
# refusal, since `\d` is recognised before the truncation is noticed. Old
# bare behaviour kept pinned verbatim via `--features none`; new bare
# behaviour pinned alongside (the truncated form as a `reject`, since it is
# still a rejection just for a different, now-real reason; the well-formed
# form as an `accept`, since it now compiles).
reject_gated none '[\d-]' "in a class requires module 'classes'"
reject_gated none '[\d-'  "in a class requires module 'classes'"
accept '[\d-]'
reject '[\d-'  "missing terminating ] for character class (pattern offset 0)"
# Own-error rows at a low endpoint keep their own errors (steps 1/3, measured
# 130/130/113): the rule must not swallow them into 150.
reject '[[:foo:]-z]'    "unknown POSIX class name"
reject '[[:<:]-z]'      "unknown POSIX class name"
reject '[[.a.]-z]'      "POSIX collating elements are not supported"
# And the accept side: RF_CLASS_BASE endpoints ride (FIX-3) — the rule must
# not over-reach onto literal-fallback escapes. libpcre2 compiles both.
accept '[0-\8]'
accept '[\8-z]'
echo "== base tier must still compile (control) =="
# Without these, a parser that rejected EVERYTHING would score 100% below.
accept 'abc'
accept 'a|b'
accept '(a)(?:b)'
accept 'a*b+c?d{2,3}e{2,}f{3}'
accept 'a*?b+?'
accept '[a-z^]'
accept '[^a-z]'
accept '.'
accept '^a$'
accept '\n\t\r\f\a\e'
accept '\x41\x2e'   # \x{...} is NOT base tier — it is in the reject table below
accept '\.\*\+\?\[\]\(\)\{\}\|\^\$\\'

# The MALFORMED braces, and they are load-bearing rather than decorative.
# K6's fix rejects a `{` in ATOM position only when it parses as a quantifier;
# the obvious over-reach — "a `{` where no atom precedes it is an error" —
# passes every K6 rejection row below and breaks all of these. Every one
# compiles as ordinary literal text in libpcre2 10.46, measured, not assumed.
accept 'a{'
accept 'a{}'
accept 'a{,}'
accept 'a{1'
accept 'a{2,3,4}'
accept '}'
accept '{'
accept '{}'
accept '{,}'
accept '{1'
accept '{}{1}'      # literal `{`, then a `}` quantified by {1} — PCRE2 compiles it
# K5's over-reach guard, the same shape one level down: a count above 65535 in
# a form that is NOT a quantifier stays literal. If the overflow were judged
# where it is DETECTED rather than where the quantifier is CONFIRMED, these
# three would become errors and PCRE2 accepts all three.
accept 'a{65536'
accept 'a{65536x}'
accept 'a{65536,x}'
# ...and the SECOND number's half of the same guard, which was missing until
# R7/T-5 measured it: all three rows above overflow the FIRST number, so
# hoisting the `big_n` raise above its decline test — the identical mistake,
# mirrored — rejected five patterns libpcre2 compiles with every suite green.
# A guard that is symmetric in the code needs coverage that is symmetric too.
accept 'a{1,65536x}'
accept 'a{,65536x}'
accept 'a{1,65536'
accept '{1,65536x}'
# The BOUNDARY itself, which nothing else pins: 65535 is a legal count, so an
# off-by-one in K5's ceiling turns this into "number too big". The empty group
# is what makes it cheap — `a{65535}` would need 65535 NFA states and dies on
# the DFA cap long before it could say anything about the parser. libpcre2
# answers error 120 "regular expression is too large" here, which is PCRE2's
# own size ceiling rather than a syntax verdict (the same class tests/fuzz/
# already excludes), so the comparison legitimately stops at pcrec's parser.
accept '(?:){65535}'
# K8's over-reach guard: PCRE2 skips SPACE and TAB inside `{...}` and NO other
# whitespace. `isspace()` would have been the obvious spelling and is wrong.
#
# This has to live here rather than in the corpus, and the reason is worth
# keeping. A `.rxt` pattern line cannot carry a raw control byte — a newline
# ends the line, and `\n` WRITTEN in a pattern is an escape that pcrec decodes
# in atom position, long after try_quant has already declined the brace. So a
# corpus case spelled `a{\n1}` exercises the escape decoder and never shows
# try_quant a newline at all. Measured: with `isspace()` substituted for the
# real test, every such corpus case still passes and this file still passed
# too until these five rows existed.
#
# The discriminating shape is a TOO-BIG count behind the byte. If the byte were
# skipped the count would be read and rejected (105); because it is not, the
# whole brace is literal text and compiles. libpcre2 10.46 compiles all five.
#
# Only the four C0 bytes, deliberately. A 0xa0 row was written first — it would
# guard against an `isspace()` under a Latin-1 locale — and then removed,
# because this box's `timeout` (see the wrapper in accept()) rejects invalid
# UTF-8 in argv and exits 125, and the row measured nothing anyway: the
# `isspace()` sabotage costs 4 checks, all of them C0. If you re-add a
# high-byte row, it cannot go through `timeout`.
for b in 'n:\n' 'r:\r' 'v:\v' 'f:\f'; do
    accept "$(printf "a{${b#*:}65536}")" "a{<${b%%:*}>65536}"
done

echo
echo "== character-type escapes -> module 'classes' =="
# [STD1b] (D37, 2026-08-13): `classes` is now default-on, so all 20 of these
# (ten letters, two positions each) now ACCEPT bare instead of refusing. Old
# bare behaviour kept pinned verbatim via `--features none`
# (`reject_gated`); the new bare-accepts fact is pinned as an `accept`
# control per cell — match/nomatch semantics for these same constructs are
# already oracle-verified under explicit `features classes` in
# tests/classes/classes.rxt, so this file's job is only the GATE state, same
# as every other row here.
for e in d D s S w W h H v V; do
    reject_gated none "\\$e"     "\\$e requires module 'classes'"
    reject_gated none "[\\$e]"   "\\$e in a class requires module 'classes'"
    accept "\\$e"
    accept "[\\$e]"
done
# `\N` is the exception and PCRE2 is the reason: the ATOM is a real construct
# module `classes` will implement, and INSIDE a class PCRE2 forbids it outright
# (error 71) and always will. So the two positions get two different KINDS of
# answer, and the in-class one must promise no module (R9/SPEC-classes-F1).
# [STD1b]: the ATOM position is default-on now (`classes`), the IN-CLASS
# position is a permanent PCRE2 rule unrelated to any gate — only the first
# needs a gate-state pin.
reject_gated none '\N'  "\N requires module 'classes'"
accept '\N'
reject '[\N]'  "\N is not valid inside a character class"
# K10 FIX (MOD-0.6 phase 2): `\N{U+hhhh}` is the OPPOSITE case from bare `\N`
# just above — libpcre2 recognises it in every class position (error 193,
# recognition-then-mode-refusal, not permanent rejection; measured against
# libpcre2 10.46 in tests/probes/probe_uprops.c), so unlike bare `\N` it MUST
# promise module 'unicode-props' rather than refuse with no module. Offsets
# load-bearing (the S27 lesson: these pin pcrec's OWN blame-position
# convention, not PCRE2's number, though they happen to agree here — see D26's
# addendum). Before this fix these five cells all read "\N is not valid inside
# a character class" instead (the RF_CLASS_INVALID row this fixed); measured
# failing against the unpinned pre-fix HEAD before landing.
reject '[\N{U+41}]'    "\N in a class requires module 'unicode-props' (pattern offset 1)"
reject '[x\N{U+41}]'   "\N in a class requires module 'unicode-props' (pattern offset 2)"
reject '[\N{U+41}x]'   "\N in a class requires module 'unicode-props' (pattern offset 1)"
reject '[a-\N{U+41}]'  "\N in a class requires module 'unicode-props' (pattern offset 3)"
reject '[^\N{U+41}]'   "\N in a class requires module 'unicode-props' (pattern offset 2)"
# The K12 endpoint rule's SCALAR-shaped exception, re-pinned for this row
# specifically now that it can promise a module at all: `\N{U+41}` is a
# SCALAR (one code point), not a certified SET, so it keeps its OWN error at
# a range endpoint rather than being overridden by PCRE2's "invalid range"
# (contrast the SET-shaped `[0-\p{L}]` pins below, which DO get overridden).
reject '[0-\N{U+41}]'    "\N in a class requires module 'unicode-props' (pattern offset 3)"
reject '[\N{U+41}-z]'    "\N in a class requires module 'unicode-props' (pattern offset 1)"
# MOD-0.3f (R16 engine critic): a quantifier-SHAPED brace after \N is bare
# \N quantified — PCRE2's fallback rule, measured in probe_nbrace.c — so in
# the default state it refuses as the GATED module construct, not as the
# \N{name} construct pcrec called it before R16 (the guarded exception to
# the pre-MOD-0.3 differential). Non-quantifier bodies keep the 137 text.
# [STD1b]: quantifier-shaped `\N{...}` is bare \N quantified (see comment
# above), and bare \N is default-on now too — both now accept.
reject_gated none '\N{2,3}' "\N requires module 'classes'"
reject_gated none '\N{,3}'  "\N requires module 'classes'"
accept '\N{2,3}'
accept '\N{,3}'
reject '\N{abc}' "PCRE2 does not support"

# The other nine escapes PCRE2 forbids inside a class, same rule, error 107.
# The atom is real and owed a module; the in-class position is not a construct,
# so naming one there is the over-promise D26 calls a defect. Found by a test
# writer reading the spec with no sight of src/ — the knowledge was already in
# the `\N` row's own note, in a field nothing reads.
for e in A B G K Z z C R X; do
    reject "[\\$e]"  "\\$e is not valid inside a character class"
done
# ...and the control that keeps the rule from swallowing the whole doorway:
# `\b` inside a class is BASE syntax (backspace), and `\d` is a real construct
# PCRE2 supports there — under `--features none` it still names its module
# (the "for e in d D s S w W h H v V" loop above pins both directions, gated
# and default-accepting, now that [STD1b] makes `classes` default-on). Both
# directions pinned.
accept '[\b]'
reject_gated none '[[:alpha:]]' "POSIX class [:...:] requires module 'classes'"
reject_gated none '[[:^alpha:]]' "POSIX class [:...:] requires module 'classes'"   # ^ negates
reject_gated none '[[:xdigit:]]' "POSIX class [:...:] requires module 'classes'"
# [STD1b]: same three, bare default now accepts (`classes` default-on).
accept '[[:alpha:]]'
accept '[[:^alpha:]]'
accept '[[:xdigit:]]'
# NAMES PCRE2 DOES NOT KNOW, and these three rows CHANGED at FIX-2 — which is
# the comment that used to sit here being right in advance. It said they "are
# exactly the rows a name-keyed table would have to get right (R6 fidelity
# critic F13: the list is 14 names and case-sensitive)". FIX-2 built that table,
# so pcrec no longer promises module 'classes' for a name no module can ever
# implement; it says what libpcre2 says. Case-sensitivity is pinned by
# `[[:AlPhA:]]`, which R6 added for precisely this moment.
reject '[[:foo:]]'    "unknown POSIX class name"
reject '[[::]]'       "unknown POSIX class name"
reject '[[:AlPhA:]]'  "unknown POSIX class name"
reject '[[:ALPHA:]]'  "unknown POSIX class name"
reject '[[:^foo:]]'   "unknown POSIX class name"
reject '[[:al pha:]]' "unknown POSIX class name"
# ...and the POSITION rule wins over the NAME rule, which is libpcre2's own
# order: an unknown name at a class's own bracket is still the position error,
# because the construct is in the wrong place before its name comes up.
reject '[:foo:]'      "POSIX class [:...:] is only valid inside a character class"
reject '\x{41}'      "\\x{...} requires module 'unicode-props'"

# POSIX collating elements / equivalence classes. PCRE2 REJECTS these rather
# than treating them as literals, so rejecting them IS compliance and the
# message deliberately mirrors PCRE2's own. pcrec accepted all of these
# silently until 2026-08-09, as a class of literal `[` `.` `a` characters —
# a pattern PCRE2 refuses, given a meaning PCRE2 never assigns it.
#
# The trigger requires a matching `.]` / `=]` terminator, so the forms without
# one are ORDINARY class members and must still compile. Those live in the
# accept list below, and they matter more than the rejections: over-rejecting
# here would break patterns that PCRE2 accepts, which is the opposite failure
# and just as wrong. Every row on both sides was checked against libpcre2 10.46.
for p in '[.a.]' '[=a=]' '[[.a.]]' '[[=a=]]' '[..]' '[.a.b.]' '[x[.a.]y]' '[a[=b=]c]'; do
    reject "$p" "POSIX collating elements are not supported"
done
accept '[.a]'    # no terminator -> ordinary members
accept '[=a]'
accept '[.]'
accept '[[.]'
accept '[a[.b]'
accept '[^.a.]'  # `^` sits between the bracket and the delimiter
accept '[a.b.]'  # the `.` is not preceded by `[`
# DOORWAY 4a — the class's OWN bracket as the opener. Every other probe of this
# doorway in the whole repo (the corpus, the rows above, and registry_check's
# `[[%ca%c]]` sweep template) puts a literal `[` between the class bracket and
# the delimiter byte, so all of them test 4b and NONE tests 4a. That is why
# deleting SR-2's `at_class_open` guard changed 0 of 4173 hashed cases and broke
# no test: the guard was not invisible, it was simply never entered (R5
# behaviour critic, FINDING 1). These two enter it, and both are accepted by
# libpcre2 10.46 as well.
#
# The clause that stood here — "deliberately not `[::]` or `[:a:]`, which PCRE2
# REJECTS and pcrec wrongly accepts (K3); pinning those would cement the bug" —
# described the tree before FIX-2. K3 is fixed and both patterns are now pinned
# as rejections in the K3 section below, which is where that sentence should
# have been updated (R9). This is also the only home for these two rows: FIX-2
# added a second copy of both in that section, and the duplicate check above is
# what surfaced it.
accept '[:]'
accept '[:a]'
# The `]` half of "a matching `.]` appears later". Every other control here
# either has no second delimiter or has a real `.]`, so replacing the
# terminator test with a bare `pat[i] == c2` was invisible to the whole suite
# (R5 tests critic, F-7b). PCRE2 accepts this one.
accept '[.a.b]'

# A letter with NO registry row falls through to "unknown escape", and the
# IN-CLASS spelling is a separate message that no test reached before R5 —
# deleting it changed nothing anywhere in the suite.
reject '\q'   "unknown escape \\q"
reject '[\q]' "unknown escape \\q in class"

# The five escapes below are REAL PCRE2 constructs (\U and \u under ALT_BSUX;
# \F, \L, \l in no mode — PCRE2 error 137 groups all five with \N{name}) that
# pcrec currently answers through the same rowless fall-through as \q, because
# there was nowhere to put "real construct, mode not offered" (R11
# disposition 14; extension design §7.1). The design gives all five ROWS with a
# status of their own. These pins are what make that change arrive as a
# deliberate edit here rather than a silent rewording — the atom and in-class
# spellings are separate messages, per letter (A1, approved 2026-08-11).
for e in U u F L l; do
    reject "\\$e"   "unknown escape \\$e"
    reject "[\\$e]" "unknown escape \\$e in class"
done

echo
echo "== assertions =="
# GATE CLOSED — the bare invocation, and the surface [M6.2] wave A must not
# move. All six still name the module, including the three the wave BUILDS:
# a construct whose module is off is refused exactly as it always was.
for e in b A Z z G K; do reject "\\$e" "\\$e requires module 'assertions'"; done

# GATE OPEN, and this is a DIFFERENT SENTENCE for a reason ([M6.2] wave A;
# assertions_design.md §9.2). The module lands its eight constructs across
# five waves, so there is an interval where `--features assertions` is on and
# `\b` has no producer — and "requires module 'assertions'" is then a lie of
# the most annoying kind: it tells the user to enable what they have already
# enabled. The refusal names the CONSTRUCT instead, on `--encoding=utf8`'s
# principle (a name pcrec knows but cannot compile is refused BY ITS OWN NAME,
# never as unknown), and the wording is D26 tier 3.
#
# The pair matters more than either row: these two sit directly under the six
# above so that a reader sees ONE construct answering two ways depending on a
# fact about the user's invocation rather than about the pattern. `\A`, `\Z`
# and `\z` are deliberately absent from this list — they COMPILE with the gate
# open, which tests/assertions/run_assertions_tests.sh asserts as the control
# that stops these rows passing on a build that produces nothing at all.
#
# [M6.2 wave B] `\b` and `\B` LEFT THIS LIST, and that is the whole visible
# surface of the wave at this file: they now compile with the gate open, so
# the enabled-but-unbuilt sentence would be the lie in the other direction.
# The wave's own control for the move is in
# tests/assertions/run_assertions_tests.sh, which asserts they COMPILE — the
# same control `\A`/`\Z`/`\z` have had since wave A, and the reason this list
# shrinking is evidence rather than erosion.
#
# [M6.2 wave D] `\G` LEFT IT TOO, on the same move and for the same reason:
# it compiles with the gate open now, so the enabled-but-unbuilt sentence
# would be the lie in the other direction. Its control — that BOTH a leading
# and a mid-pattern spelling actually build — is in
# tests/assertions/run_assertions_tests.sh beside `\b`/`\B`'s.
#
# [M6.2 WAVE E] `\K` LEFT IT, AND WITH IT THE WHOLE `assertions` PARAGRAPH:
# the module has no unbuilt construct left, so this list is EMPTY by
# construction rather than by omission, and every one of the module's eight
# constructs is now pinned above (gate closed) and asserted to COMPILE in
# tests/assertions/run_assertions_tests.sh (gate open).
#
# **WAVE D'S OWN NOTE PREDICTED THE NEXT STEP AND WAS WRONG ABOUT IT, MEASURED
# BY WAVE E.** It said that when `\K` left, "the row that has to go WITH them
# is the epilogue's own pin in `src/parse/ext.c` (the `UNBUILT` arm). A refusal
# mechanism with no population is machinery nothing can test." The mechanism's
# population is not the `assertions` module's rows — it is EVERY registry row
# whose module is enabled and whose port is unwired, and that set is large and
# live today:
#
#     --features backrefs       '\k'     -> "module 'backrefs' is enabled but
#                                            \k is not implemented yet"
#     --features lookaround     '(?<=a)' -> ... '(?<=...)' ...
#     --features atomic-groups  '(?>a)'  -> ... '(?>...)' ...
#     --features quoting        '[\Q]'   -> ... '\Q in a class' ...
#
# (measured on the shipped compiler by wave E). So the arm is not unpopulated
# machinery and deleting it would delete a live diagnostic. What WAS true is
# narrower and is the thing this paragraph has to fix: `\K`'s row was the ONLY
# hand-written pin on that arm anywhere in the tree, so retiring it would have
# left the mechanism with a big population and no literal expectation — the
# exact shape tests/reject/ exists to prevent, arriving through a wave doing
# the right thing to its own rows.
#
# The four rows below are that pin, RE-HOMED to modules that will not build
# their constructs for milestones. THREE MODULES, not one, because the
# diagnostic is assembled from the row's own `module` and `syntax`, so a single
# module's row cannot tell "the sentence is right" from "the sentence happens
# to be right for `backrefs`"; and BOTH POSITIONS, because ext.c splices the
# in-class wording at a different site from the macro's (`res.msg` beside the
# K12 endpoint payload, not through `UNBUILT`) and a pin on one has never
# covered the other.
# [M6.5.2] THE `backrefs` ROW MOVED, it did not retire. `--features backrefs
# '\k'` COMPILES its way to a SHAPE error now ("\k must be followed by a name
# in <>, '' or {}"), because the module builds that row — so a pin asserting
# the enabled-but-unbuilt sentence would be pinning a lie, exactly as
# `atomic-groups`' was one module earlier.
#
# BUT THE ARM STILL NEEDS THREE MODULES (see above: a single module's row
# cannot tell "the sentence is right" from "the sentence happens to be right
# for THAT module"), so the pin moves to a row that is still unbuilt rather
# than leaving two. `\g<` is module `recursion`'s, and it is a row THIS module
# ADDED: the `\g` doorway carries two different constructs — braces and bare
# digits are BACKREFERENCES, angle brackets and quotes are SUBROUTINE CALLS
# (measured, backrefs_design.md §2) — so claiming the second half would be the
# miscompile D26 tier 1 forbids, and it is born unbuilt naming `recursion`.
# §11.5 named this move in advance as one of the three pins this module
# disturbs.
#
# [DD-14] WAVE D RETIRED THIS ROW, exactly as `atomic-groups`' and
# `lookaround`'s did before it and for the same reason: `--features recursion
# '\g<1>'` no longer says "not implemented yet" — `pcrec_brport_g`
# (src/parse/mod_backrefs.c) gained the `<`/`'` arms, both `\g<` / `\g'` rows'
# `aport` now points at it, and neither has a tail left to decline, so a pin
# asserting the enabled-but-unbuilt sentence here would be pinning a lie.
# `\g<1>` alone (no group declared) now compiles its way to the ordinary
# error-115-class refusal instead ("refers to capture group 1, but this
# pattern has 0"), ASSERTED BELOW with the SAME `reject_gated` call (`ngated`
# unmoved — still one gate-open refusal pinned at this exact spot, just a
# different sentence) rather than left unpinned, so the retirement is not
# merely an absence. The count going DOWN in the "unbuilt" sense is the module
# LANDING, not coverage eroding; the control that says so is
# tests/recursion/leadingzero.rxt and spellings.rxt, which assert the same
# spelling compiles and matches. The arm's remaining two modules
# (`conditionals`, `quoting`, below) are still enough to keep the
# enabled-but-unbuilt sentence from being read as module-specific rather than
# general.
reject_gated recursion '\g<1>' "refers to capture group 1, but this pattern has 0"
# [M6.6.2] wave B+C moved THE `lookaround` ROW WITHIN ITS OWN MODULE, from
# `(?=a)` to `(?<=a)`: the lookahead half had landed, so the old pin would have
# been pinning a lie, while the module's three LOOKBEHIND rows were still
# unbuilt and could carry it. That was explicitly a loan against wave D.
#
# [M6.6.2] WAVE D CALLED THE LOAN IN AND THE ROW RETIRED. `--features
# lookaround '(?<=a)'` COMPILES now — module `lookaround` has no unbuilt
# construct left, all six rows read `built` — so there is no spelling of this
# module that can carry the enabled-but-unbuilt sentence any more, and the
# count going DOWN here is the module LANDING rather than coverage eroding.
# The control that says so is tests/lookaround/lookbehind.rxt, which asserts
# the same pattern compiles and matches, and tests/registry's built-status
# tally, which asserts the three rows moved and that NO ROW OUTSIDE THIS
# MODULE MOVED WITH THEM.
#
# SO THE ARM'S THIRD MODULE COMES FROM `conditionals`, and the row is chosen
# rather than picked. The arm needs THREE modules for the reason the paragraph
# above states — a single module's row cannot tell "the sentence is right" from
# "the sentence happens to be right for THAT module" — and `(?(` is the row
# lookaround_design.md R33 C1-9 names by name: a reader must not take three
# lookbehind rows going `built` as unlocking ASSERTION-CONDITIONS, which are a
# different construct in a different module. Pinning it here says that in the
# one place a wave that got it wrong would trip over. It is also a row that
# will not build for milestones (module `conditionals` is not in Frank's ruled
# M6 list at all), which is what the re-homing paragraph above asks of a
# candidate.
reject_gated conditionals  '(?(1)a|b)' "module 'conditionals' is enabled but (?(...) is not implemented yet"
# [M6.4.2] THE `atomic-groups` ROW RETIRED HERE, exactly as `\b`/`\B`'s did in
# [M6.2] wave B and the two `(?m)` spellings' did in wave C, and for the same
# reason: `--features atomic-groups '(?>a)'` COMPILES now, so a pin asserting
# it refuses would be pinning a lie. The count going DOWN is the module
# LANDING, not coverage eroding; the control that says so is
# tests/atomic_groups/'s corpus, which asserts the same pattern compiles and
# matches. The arm itself keeps three modules and both positions above.
reject_gated quoting       '[\Q]'  "module 'quoting' is enabled but \Q in a class is not implemented yet"
# The `m` LETTER's own arm (src/parse/mod_modifiers.c), which produces its
# refusal per letter rather than through the `(?` doorway's row — so it needs
# its own copy of the rule and its own pin.
#
# [M6.2 WAVE C] THE TWO ENABLED-BUT-UNBUILT ROWS RETIRED, exactly as `\b` and
# `\B`'s did in wave B and for the same reason: `(?m)a` and `(?m:a$)` COMPILE
# now, so a pin asserting they refuse would be pinning a lie. The count going
# DOWN is the wave landing, not coverage eroding — and the control that stops
# this being erosion is in tests/assertions/run_assertions_tests.sh, which
# asserts BOTH spellings compile with the gate open.
#
# What stays is the module-OFF row, which is still true and is now the ONLY
# `(?m)`-specific gated pin: with `assertions` disabled the letter is refused
# by its own name. Both spellings are kept here, because the bare run and the
# scoping form take different paths through the port and only one of them was
# ever pinned on this side.
reject_gated modifiers '(?m)a' \
    "inline option 'm' (multiline) requires module 'assertions'"
reject_gated modifiers '(?m:a$)' \
    "inline option 'm' (multiline) requires module 'assertions'"

echo
echo "== backreferences =="
for e in k g; do reject "\\$e" "\\$e requires module 'backrefs'"; done
# ALL TEN digits, by hand. It was `for d in 1 2 8 9`, and R6's testability
# critic used the gap: it deleted the rows for 0,3,4,5,6,7 — chosen precisely
# because those six were covered ONLY by dump iteration — bumped the exact row
# count as registry_check's own failure message invites, re-ran
# compliance_section.py --write as ITS failure message invites, and every suite
# passed. `\3` then reported "unknown escape \3", i.e. pcrec claiming it is not
# a PCRE construct at all. An exact count disarms itself for anyone who follows
# the instructions; a hand-written row does not.
for d in 0 1 2 3 4 5 6 7 8 9; do reject "\\$d" "requires module 'backrefs'"; done

echo
echo "== unicode properties, quoting, misc escapes =="
# R19 checks-CONFIRMED: these two rows — the module's own canonical syntax
# examples — were the LAST message-only \p pins, predating the offset slice
# that landed around them (the S27 lesson recurring inside the commit whose
# comment claims to have learned it). Offsets added at R19 close.
reject '\p{L}' "\\p requires module 'unicode-props' (pattern offset 5)"
reject '\P{L}' "\\P requires module 'unicode-props' (pattern offset 5)"
# MOD-0.6 phase 2 (mod_uprops.c): the malformed-vs-unknown-name split, offset
# pinned (the S27 lesson — a message-only pin cannot distinguish a refactor
# that moves the blame position from one that does not). Measured against
# libpcre2 10.46 in tests/probes/probe_uprops.c: EVERY byte after \p/\P
# lands on one of PCRE2's two "yes, dispatched" errors (146 malformed, 147
# unknown name) and never a THIRD kind that would mean "not a \p construct" —
# so pcrec promises the module unconditionally, but the OFFSET and the
# malformed-vs-not wording now carry that split. Before this landed, every
# one of the cells below read the single generic "\p requires module
# 'unicode-props'" text at the BACKSLASH's offset (0) — measured failing
# against the pre-mod_uprops.c HEAD before landing.
reject '\p'      "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 2)"  # truncated at EOF
reject '\p!'     "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 3)"  # not a letter, not {
reject '\p9'     "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 3)"
reject '\p{'     "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 3)"  # unterminated, empty
reject '\p{L'    "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 4)"  # unterminated, valid prefix
reject '\p{}'    "\\p{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 4)"  # well-formed, empty name
reject '\pA'     "\\p: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 3)"  # well-formed, unknown 1-letter name (A is not in {C,L,M,N,P,S,Z})
reject '\p{Foo}' "\\p requires module 'unicode-props' (pattern offset 7)"  # well-formed, multi-char name — pcrec's table does not cover this axis (manager ruling 3, phase-2 authorization), no "not recognised" claim
reject '\P'      "\\P: malformed property escape — requires module 'unicode-props' (pattern offset 2)"
reject '\P!'     "\\P: malformed property escape — requires module 'unicode-props' (pattern offset 3)"
reject '\P9'     "\\P: malformed property escape — requires module 'unicode-props' (pattern offset 3)"
reject '\P{'     "\\P: malformed property escape — requires module 'unicode-props' (pattern offset 3)"
reject '\P{L'    "\\P: malformed property escape — requires module 'unicode-props' (pattern offset 4)"
reject '\P{}'    "\\P{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 4)"
reject '\PA'     "\\P: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 3)"
reject '\P{Foo}' "\\P requires module 'unicode-props' (pattern offset 7)"
# case-insensitive single-letter short names, both directions of the
# 14-of-52 table (C L M N P S Z, hand-written — see mod_uprops.c's header;
# PC-3 sweeps all 52 letters independently): a KNOWN short name gets the
# GENERIC message (no "not recognised" claim — pcrec just has not built the
# module yet), an unknown one names pcrec's own gap explicitly.
reject '\pC'     "\\p requires module 'unicode-props' (pattern offset 3)"
reject '\pc'     "\\p requires module 'unicode-props' (pattern offset 3)"   # case-insensitive
# insignificant-byte skip (space/tab/hyphen/underscore never enter the
# significant-character count): a padded UNKNOWN single letter must still
# read as a single-character name, not a multi-character one — sig_count
# staying at 1 is what keeps this in the "not recognised" bucket rather
# than silently falling through to the generic message once padding is
# added (S35's catch).
reject '\p{ A}'  "\\p{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 6)"
# the 48/49 significant-character boundary (R10 disposition 5, PCREC_UPROP_NAME_MAX
# in src/core/limits.h): 48 significant characters is a well-formed (if
# unknown) name; 49 is malformed, blamed ONE PAST the 49th significant
# character consumed — not at the closing brace, which is the streaming
# proof (tests/probes/probe_uprops.c: the same blame position holds even
# when insignificant filler is interleaved between every character).
reject '\p{AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}' \
       "\\p requires module 'unicode-props' (pattern offset 52)"            # 48 A's, well-formed
reject '\p{AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}' \
       "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 52)"  # 49 A's, malformed
# the same boundary CARET-PREFIXED — S33's guard, added after mech measured
# the caret-consume drop UNDETECTED against the original pin set (design
# note §8): \p{^L} never flips under that sabotage, because a two-char name
# gets the GENERIC message either way (ruling 3's design); what MOVES is
# the 48/49 boundary for a caret-prefixed body. Probe: caret + 48 A's is
# ERR 147 at 53, caret + 49 A's is ERR 146 at 53 — the caret costs one
# OFFSET byte but zero BUDGET.
reject '\p{^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}' \
       "\\p requires module 'unicode-props' (pattern offset 53)"            # caret + 48 A's, well-formed
reject '\p{^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}' \
       "\\p: malformed property escape — requires module 'unicode-props' (pattern offset 53)"  # caret + 49 A's, malformed
# the accumulator-fold guard — S34's, same mech finding: a lowercase KNOWN
# letter in braces must still read as known. The brace path's table lookup
# is deliberately FOLD-FREE (mod_uprops.c uprops_short_lookup), so this pin
# fails the moment the accumulator stops folding, instead of the lookup
# silently repairing the buffer on the way in.
reject '\p{c}' "\\p requires module 'unicode-props' (pattern offset 5)"
# R19 close: the axes the differential's generator cannot produce (its
# alphabet is letters-only, no '=' — its own comment says so). The has_eq
# branch (a '='-bearing body promises the module with NO table lookup,
# ruling 3) had ZERO coverage anywhere; the digit and hostile-byte cells
# had none either. The '!' pin is K16's representative: libpcre2 calls 164
# of 256 body bytes MALFORMED at the byte (err 146); pcrec scans past them
# and answers its own category at its own offset — ruled acceptable tier-2
# and deferred to the first producer (Frank, 2026-08-12; docs/
# known_issues.md K16, docs/pcre2_compliance.md). These pins claim PCREC'S
# OWN current behavior, not oracle agreement.
reject '\p{=}' "\\p requires module 'unicode-props' (pattern offset 5)"
reject '\p{Script=Latin}' "\\p requires module 'unicode-props' (pattern offset 16)"
reject '\p{9}' "\\p{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 5)"
reject '\p{!}' "\\p{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 5)"
reject '\Q'    "\\Q requires module 'quoting'"
reject '\E'    "\\E requires module 'quoting'"
reject '\R'    "\\R requires module 'misc'"
reject '\X'    "\\X requires module 'misc'"
reject '\C'    "\\C requires module 'misc'"
reject '\cA'   "\\c requires module 'misc'"
reject '\o{101}' "\\o requires module 'misc'"

echo
echo "== (?...) constructs =="
reject '(?=a)'    "requires module 'lookaround'"
reject '(?!a)'    "requires module 'lookaround'"
# The three lookbehind TAILS on `<`, split from the named group at Q2/SR-9.
# These read 'lookaround/named-groups' until then — a compound module name that
# was a true sentence and an inexact answer, where D26 makes attribution tier 2.
# Measured over all 256 tails: exactly `=`, `!` and `*` are lookaround and every
# other byte is the named-group path. Hand-written HERE because that is the only
# check of a module NAME — libpcre2 can say the construct exists and can never
# say pcrec should call it 'lookaround'.
reject '(?<=a)'   "requires module 'lookaround'"
reject '(?<!a)'   "requires module 'lookaround'"
reject '(?<*a)'   "requires module 'lookaround'"
reject '(?<n>a)'  "requires module 'named-groups'"
# `(?P` is three constructs and three modules, and answered 'named-groups' for
# all three until Q2 (R8/C4-7, re-derived independently by a spec-first writer).
reject '(?P=n)'   "requires module 'backrefs'"
reject '(?P>n)'   "requires module 'recursion'"
# ...and every other tail after `(?P` is PCRE2 error 141 with its own message,
# which the byte-keyed row promised a module for. Found by the tail sweep this
# step added, not by the plan.
reject '(?PX)'    "unrecognized character after (?P"
# ...but a TRUNCATED `(?P` is not one of them, and that cell went unpinned for
# two eras (R20/OPTRUN-1). "unrecognized character after (?P" is a claim about
# the byte AFTER `(?P`, and when the pattern ENDS there is no such byte — the
# sentence is false by construction. libpcre2 10.46 gives err 114 "missing
# closing parenthesis" at offset 3, exactly what it gives bare `(?`, which is
# R17's finding one row over. The tail sweep could not see this: its template
# `"%s(?%s%c%s"` always inserts a byte after the prefix, so `(?P` is a pattern
# it structurally cannot generate (OPTRUN-B1 — truncated completion shapes
# land with this fix).
reject '(?P'      "missing closing ) for group"
# The relative subroutine calls. Both fell to the `(?` catch-all and were called
# 'modifiers'; `(?+N)` and `(?-N)` are the relative spellings of `(?1)`..`(?9)`,
# which this table has always called 'recursion'.
reject '(?+1)'    "requires module 'recursion'"
reject '(a)(?-1)' "requires module 'recursion'"
# `-` is the one byte at this doorway carrying two modules, which is why it has
# ten digit tails AND a bare row rather than a compound name.
# [STD1b]: `modifiers` is default-on now, so this bare row accepts too.
reject_gated none '(?-i)' "requires module 'modifiers'"
accept '(?-i)'

# ---- GATED pins (MOD-0.5c): diagnostics whose text only exists with the
# gate OPEN. The corpus's perr blocks assert only THAT these fail; the
# MODULE NAME in the answer is the tier-2 fact under D26, and these are its
# only pins (the .rxt format cannot assert message content — found by the
# corpus author at this landing). Counted separately (ngated) so the
# default-config ratchet above stays exactly what it says it is.
# `reject_gated` itself now lives earlier in the file (right after
# `accept()`), because [STD1b] needs it — as `reject_gated none ...` — for
# rows far above this point in the file. See its definition there.
# The two per-letter attributions (MOD-0.5a rulings, flagged to Frank).
# J's wording has moved THREE TIMES the same day ([M6.3], 2026-08-18) and
# this is the FINAL one, per manager ruling citing the ratified D38
# PCRE2_DUPNAMES row (RIDES(M4/captures), a PLANNED-LATER disposition, not
# NEVER) and docs/pcre2_compliance.md's own REJECTED/planned status for
# `(?J)`:
#   1. "requires module 'named-groups'" — the ORIGINAL MOD-0.5a wording,
#      true while that module did not exist, a LIE the moment it shipped
#      WITHOUT dupnames support (the "requires X" framing reads as
#      "enabling X fixes this", which named-groups landing disproved).
#   2. K14's ROADMAP_NEVER shape ("...is outside pcrec's scope and no
#      module will implement it...") — a same-day intermediate fix that
#      was ALSO wrong: (?J) does not meet K14's bar (real PCRE2 the
#      SURVEY calls architecturally excluded), it is PLANNED-LATER.
#   3. THE RULING: names the true owning module (named-groups — duplicate
#      NAMES are named-group semantics, same dispatch logic 'm' already
#      uses for 'assertions') without the false "requires" framing.
#   4. [M6.5.2] THE LETTER IS BUILT, and the owner turns out to be
#      `backrefs` (ASK-1, ruled with R32). Wording 3 was right about the
#      DECLARING half and silent about the RESOLVING one: what makes `(?J)`
#      mean anything is the resolution rule for a reference to a duplicated
#      name — first of the name-run by ascending number that is SET
#      (backrefs_design.md §8.3, measured against four candidate rules) —
#      and that machinery is module `backrefs`'. So the split the compliance
#      page now records is: declaring a duplicate name is `named-groups`,
#      resolving a reference to one and the letter itself are `backrefs`.
#      With `backrefs` OFF the letter refuses naming it, and "requires
#      module 'backrefs'" is TRUE in the way wording 1 was not — enabling
#      it does fix this.
reject_gated modifiers '(?J)a'     "inline option 'J' (dupnames) requires module 'backrefs'"
# [STD1b] (D37, 2026-08-13): `modifiers` is default-on now, so `(?m)a`/
# `(?J)a` reach this SAME diagnosis bare, with no `--features` at all — the
# std1-BOUNDARY proof: std1 = {classes, modifiers} and nothing wider, so
# `m`'s real module ('assertions') and J's owning module ('backrefs' since
# [M6.5.2]) must both still be refused by a bare invocation. If std1's mask
# ever silently grew to include 'assertions' or 'backrefs', the
# corresponding row is what would flip from reject to accept.
# (`(?m)a`'s bare pin already lives further down, alongside its five
# sibling letters' gate conversion — not duplicated here.)
reject '(?J)a'     "inline option 'J' (dupnames) requires module 'backrefs'"

# ---- [M6.3] module `named-groups` — GATED pins. The producer's own
# corpus (tests/named_groups/) carries the MATCH-semantics half; these are
# the tier-2 attribution/boundary facts a `perr`/`m`/`n` block cannot
# assert (WHY a pattern refuses, or that a construct in a DIFFERENT
# module still refuses once this one is enabled) plus two syntax-boundary
# refusals python `re` cannot co-verify (name length; see
# docs/dev/upstream_issues.md U10). Name-syntax refusals PYTHON DOES agree
# on (leading digit, duplicate name) live in tests/named_groups/'s own
# `.rxt` corpus as ordinary oracle-verified `perr` blocks instead — this
# file is for what a `.rxt` block structurally cannot express.
#
# THE BOUNDARY, proven both ways: a backreference-BY-NAME spelling and the
# DUPNAMES option letter must both keep refusing once named-groups is
# enabled — the module's whole point is the three DECLARING spellings,
# nothing else at the `(?` doorway moves.
reject_gated named-groups '(?<x>a)\k<x>'   "requires module 'backrefs'"
reject_gated named-groups '(?<x>a)(?P=x)'  "requires module 'backrefs'"
# [M6.5.2] the SAME boundary, now proven from the other side: with
# `backrefs` still off the letter refuses naming it, so enabling
# named-groups and modifiers alone does NOT make a duplicate name legal.
reject_gated named-groups,modifiers '(?J)(?<dup>a)(?<dup>b)' \
    "inline option 'J' (dupnames) requires module 'backrefs'"
# And with all three on, the duplicate DECLARATION is legal and the thing
# that still refuses is a name pcrec does not know — the error-115 class.
reject_gated named-groups,modifiers,backrefs '(?J)(?<dup>a)(?<dup>b)\k<nope>' \
    "does not declare"

# ---- [M6.5.2] module `backrefs`' PARTIAL-ENABLE MATRIX ------------------
# backrefs_design.md §10's after-table, as pins. It is the module's real
# partial-enable boundary and it needs THREE modules to state: the numeric
# spellings need `backrefs` alone; the by-name spellings additionally need
# `named-groups`, because without it there is no such thing as a group NAME;
# and `(?J)` additionally needs `modifiers`, because the LETTER lives in that
# module's option-run dispatch even though `backrefs` owns what it means. A
# `.rxt` block can assert THAT a pattern refuses but not WHICH module it
# names, and which module a diagnostic promises is the tier-2 fact under D26 —
# so the matrix lives here.
#
# ONE CELL OF THE DESIGN'S TABLE IS CORRECTED HERE, measured: it predicts that
# `(?<n>a)\k<n>` under `std1` refuses naming `backrefs`. It refuses naming
# `named-groups`, and that is right — pcrec reports the LEFTMOST construct it
# cannot handle, and the DECLARATION comes first. The design's table read the
# reference as the leftmost construct because that is the one the row is about.
reject_gated backrefs '(?J)(?<a>x)(?<a>y)'   "requires module 'modifiers'"
reject_gated backrefs '\k<n>'                "requires module 'named-groups'"
reject_gated backrefs '(?<n>a)\k<n>'         "requires module 'named-groups'"
reject_gated backrefs,modifiers '(?J)(?<a>x)(?<a>y)' \
    "requires module 'named-groups'"
reject_gated backrefs,named-groups '(?J)(?<a>x)(?<a>y)' \
    "requires module 'modifiers'"
# The by-name spelling with BOTH modules on: a well-formed name the pattern
# never declares is the error-115 class, raised by §5.3's END-OF-PARSE pass
# rather than at the escape. R32 C7 caught the first design's table pinning
# this cell as COMPILING, which `gated.rxt` would have turned into a tier-1
# divergence against libpcre2.
reject_gated backrefs,named-groups '\k<n>'   "does not declare"
reject_gated backrefs,modifiers,named-groups '\k<n>' "does not declare"
# And the bare default (std1 = {classes, modifiers}) refuses all three of the
# module's own spellings by ITS name — the std1-BOUNDARY proof for this
# module, the shape `(?J)a` already carries above.
reject '(a)\1'    "\\1 (backreference/octal) requires module 'backrefs'"
reject '\k<n>'    "\\k requires module 'backrefs'"
reject '(a)\g{-1}' "\\g requires module 'backrefs'"
# The measured wall (tests/probes/probe_named_groups.c, U10): 128 bytes is
# the longest name PCRE2 accepts; python `re` has no such ceiling, so this
# is the one boundary in this block that cannot be a co-verified `.rxt`
# `perr` — the 128-accepts half lives in tests/named_groups/ instead,
# where it IS python-verifiable (no length limit on the python side to
# diverge on an ACCEPTING case).
reject_gated named-groups \
  '(?<aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa>x)' \
  "subpattern name is too long (maximum 128 bytes)"

# The recognised-malformed shape (PCRE2 error 194's analogue) and the
# truncated run (error 114's): the module diagnoses its own body.
reject_gated modifiers '(?i-m-s)a' "invalid hyphen in option setting"
reject_gated modifiers '(?i'       "missing closing ) for inline option setting"
# R20/SPEC-1, a TIER-1 MISCOMPILE found by the D27 blinded writer: A BARE
# OPTION RUN IS NOT A REPEATABLE ITEM. `--features modifiers --emit-main
# 'a(?i)*'` exited 0 and the emitted matcher matched a/aa/aaa; libpcre2 gives
# err 109 at offset 5. The producing port modelled a bare run as a lexical
# no-atom construct (A_EMPTY), so the quantifier bound to it and matched
# empty — and pcrec's OWN registry disagreed with the producer all along, the
# GROUP_OPT rows' `quantifiable` column reading `form`.
#
# THE OFFSETS ARE PINNED, not just the sentence: this refusal shares one
# wording with three other sites in p_rep, so a message-only pin cannot tell
# them apart (the S27 lesson). They are also pcrec's OWN convention agreeing
# with PCRE2's, cell for cell, measured — the quantifier byte for `*`/`+`,
# the closing `}` for a brace form.
# [STD1b]: this is the TIER-1 MISCOMPILE GUARD (see the R20/SPEC-1 note
# above), and it is worth its own bare proof rather than trusting the mask
# equivalence by inference — a silently-wrong std1 expansion here would be
# exactly the kind of regression this class of pin exists to catch.
reject 'a(?i)*'     "quantifier does not follow a repeatable item (pattern offset 5)"
reject_gated modifiers 'a(?i)*'     "quantifier does not follow a repeatable item (pattern offset 5)"
reject_gated modifiers 'a(?i)+'     "quantifier does not follow a repeatable item (pattern offset 5)"
reject_gated modifiers 'a(?i)?'     "quantifier does not follow a repeatable item (pattern offset 5)"
reject_gated modifiers 'a(?i){2}'   "quantifier does not follow a repeatable item (pattern offset 7)"
reject_gated modifiers 'a(?i){2,3}' "quantifier does not follow a repeatable item (pattern offset 9)"
# at the START of the pattern, and after a group: the quantifier has an atom
# to its left in the second, and it still must not reach past the run
reject_gated modifiers '(?i)*'      "quantifier does not follow a repeatable item (pattern offset 4)"
reject_gated modifiers '(a)(?i)*'   "quantifier does not follow a repeatable item (pattern offset 7)"
# other accepted bare spellings — the boundary is bare-vs-scoping, not the
# letter: an unsetting run, a caret run, a two-letter x level, and a run
# following another run
reject_gated modifiers 'a(?i-m)*'   "quantifier does not follow a repeatable item (pattern offset 7)"
reject_gated modifiers 'a(?^)*'     "quantifier does not follow a repeatable item (pattern offset 5)"
reject_gated modifiers 'a(?xx)*'    "quantifier does not follow a repeatable item (pattern offset 6)"
reject_gated modifiers '(?i)(?i)*'  "quantifier does not follow a repeatable item (pattern offset 8)"
# The extended character class, the third misattribution: a class with set
# operations, not an option setting. MOD-0.3a split it out of 'classes' the
# day classes gained producers — an enabled module must never refuse a
# construct while naming itself.
reject '(?[[a]])' "requires module 'extended-classes'"
reject "(?'n'a)"  "requires module 'named-groups'"
reject '(?P<n>a)' "requires module 'named-groups'"
reject '(?>a)'    "requires module 'atomic-groups'"
reject '(?#c)'    "requires module 'comments'"
# THE GENUINELY-LEXICAL ROWS, quantified — R20/SPEC-1's other control, and
# the reason that fix is keyed to the option-run node and not to "produces
# no atom". libpcre2 COMPILES `a\Q\E*` and `a(?#c)*`: a quote span and a
# comment are transparent, so the quantifier reaches back to the `a`. A bare
# option run is NOT transparent — `a(?i)*` is err 109 — which is the whole
# distinction. pcrec refuses all three today, but for the lexical two it
# refuses at the MODULE (leftmost construct, offset 1), and these pins are
# what say that answer must not move when the option-run fix lands.
reject 'a\Q\E*'   "\\Q requires module 'quoting'"
reject 'a(?#c)*'  "(?#...) requires module 'comments'"
# [M4-CALLOUTS] step 1 (D36, flipped 2026-08-14): callouts moved from
# ROADMAP_NEVER (K14's OUT-OF-SCOPE ruling) to a PLANNED module, LOW
# priority, M4-hosted. The diagnostic now promises 'callouts' like any other
# module row.
reject '(?C1)'    "(?C...) requires module 'callouts'"
reject '(?|a)'    "requires module 'branch-reset'"
reject '(?(1)a)'  "requires module 'conditionals'"
reject '(?R)'     "requires module 'recursion'"
reject '(?&n)'    "requires module 'recursion'"
# `(?*...)` is the NON-ATOMIC positive lookahead, not an option setting. It was
# answered "requires module 'modifiers'" by the `(?` catch-all until R8/C4-8,
# while pcrec's own verb table already knew `(*napla:...)` and
# docs/pcre2_compliance.md already called it non-atomic lookaround — three
# homes, one disagreeing, which is the `\v` bug's exact shape. Hand-written
# here because the iterated probe reads the module from the same row the parser
# renders from and so cannot see a wrong name.
reject '(?*a)'    "requires module 'lookaround'"
# All ten numeric recursion rows, by hand. Iterating the dump probes them, but
# reads the module name from the same row the parser renders from, so it cannot
# see a wrong name — these nine were the largest block of rows with no
# independent human source (R5 tests critic).
for d in 0 1 2 3 4 5 6 7 8 9; do
    reject "(?$d)" "requires module 'recursion'"
done
# The pattern ENDS at the doorway. `c2 == -1` is also REG_SEL_ANY's value, so
# the lookup lands on the catch-all twice over. This pin's THIRD answer in
# three eras, each one measured: pre-Q2 it promised module 'modifiers' for a
# truncated pattern ("(??...)..."); Q2 changed it to the catch-all's
# "unrecognized character", with prose here claiming PCRE2 agreement; R17's
# engine critic MEASURED that claim false — PCRE2 gives `(?` error 114,
# "missing closing parenthesis", the SAME error bare `(` gets (as do `(?i`,
# `(?^`, `(?-`): an unclosed group, not an unrecognisable byte. ext.c now
# answers `(?`-at-end in the family pcrec already used for bare `(`.
reject '(?'       "missing closing ) for group"
# THE Q2 ROWS. 217 of the 255 probeable bytes after `(?` were told a pcrec module
# would implement syntax libpcre2 rejects outright (error 111). A sample is
# pinned by hand here because PC-3's generated differential and this table fail
# differently: the differential proves the POPULATION agrees with libpcre2, and
# these prove the SENTENCE, which libpcre2 cannot judge.
reject '(?q)'     "unrecognized character after (? or (?-"
reject '(?Z)'     "unrecognized character after (? or (?-"
reject '(?~)'     "unrecognized character after (? or (?-"
# ...and the same over-promise one level down, which splitting the catch-all
# into eleven option-letter rows did NOT fix: the row is chosen by the first
# byte, so `(?iZ)` still promised 'modifiers' until the doorway read the whole
# option RUN. Found while writing the differential, not before it.
reject '(?iZ)'    "unrecognized character after (? or (?-"
reject '(?-Z)'    "unrecognized character after (? or (?-"
reject '(?i-Z)'   "unrecognized character after (? or (?-"
reject '(?aPP)'   "unrecognized character after (? or (?-"
# The other direction, and the mirror mistake: these ARE option settings PCRE2
# recognises (error 194, "invalid hyphen in option setting"), so refusing them a
# module would be an UNDER-promise. The first version of the run rule got this
# wrong for 24 shapes and the differential refused it.
# [STD1b] (D37, 2026-08-13): `modifiers` is default-on now, and these three
# were all answered "requires module 'modifiers'" only because the module
# itself was absent — bare now reaches the SAME malformed-run diagnosis
# `--features modifiers` already gets (`reject_gated modifiers '(?i-m-s)a'`
# above), since the mask is identical. Old behaviour kept pinned via
# `--features none`; new bare behaviour pinned alongside as its own
# `reject` (still a rejection, now for the module's OWN reason).
reject_gated none '(?i-m-s)' "requires module 'modifiers'"
reject_gated none '(?^-i)'   "requires module 'modifiers'"
reject_gated none '(?--D)'   "requires module 'modifiers'"
reject '(?i-m-s)' "invalid hyphen in option setting (pattern offset 5)"
reject '(?^-i)'   "invalid hyphen in option setting (pattern offset 3)"
reject '(?--D)'   "invalid hyphen in option setting (pattern offset 3)"
# `a` takes exactly one ASCII-restrict sub-option, which is invisible to any
# rule derived from single letters: `(?aP)` compiles and `(?aPP)` is error 111.
# [STD1b]: bare now accepts too (a measured no-op at options=0, per
# tests/modifiers/letters.rxt's `(?aP)x` cell under `features modifiers`).
reject_gated none '(?aP)' "requires module 'modifiers'"
accept '(?aP)a'
# `(*` used to be answered "requires module 'verbs'" here. Q1 changed it, and
# the change is a correction: PCRE2 reads a bare `(*` as `(` followed by a
# quantifier with nothing to quantify (error 109), and there is no verb name at
# all to route to a module. Pinned as its own row rather than merged with the
# other quantifier rows because THIS one is the doorway declining.
reject '(*'       "quantifier does not follow a repeatable item"
# [STD1b]: all six below are default-on constructs now (`modifiers`); old
# bare-refusal behaviour is kept pinned via `--features none`. The new
# bare-accepts fact does not need a fresh oracle here — MATCH semantics for
# `(?i)`/`(?-i)`/`(?i:...)`/`(?s)`/`(?x)` are already oracle-verified under
# explicit `features modifiers` in tests/modifiers/scope.rxt, letters.rxt
# and xmode.rxt, and the bare/default PATH itself (not just the mask) is
# separately proven equivalent to `--features modifiers` for this same
# module by tests/modifiers/malformed_and_gate.rxt's [STD1b] bare section
# and by tests/cli's case14 std1-vs-explicit byte-diff — so a plain
# `accept` control per cell is enough to close this file's own job (the
# GATE state), without re-deriving six more oracle cells. `(?m)a` is the
# ONE exception: it is not an accept at all, even bare — `m`'s home is
# module 'assertions' (not in std1), so it stays a rejection and is the
# std1-BOUNDARY proof (std1 = {classes, modifiers} and nothing wider).
reject_gated none '(?i)a'    "requires module 'modifiers'"
reject_gated none '(?-i)a'   "requires module 'modifiers'"
reject_gated none '(?i:a)'   "requires module 'modifiers'"
reject_gated none '(?s)a'    "requires module 'modifiers'"
reject_gated none '(?m)a'    "requires module 'modifiers'"
reject_gated none '(?x)a'    "requires module 'modifiers'"
accept '(?i)a'
accept '(?-i)a'
accept '(?i:a)'
accept '(?s)a'
reject '(?m)a'    "requires module 'assertions'"
accept '(?x)a'

echo
echo "== (*...) verbs, option settings and script runs =="
# These used to report "quantifier does not follow a repeatable item", which is
# a clean rejection of something that is not a quantifier — technically correct
# behaviour, useless diagnosis.
#
# THE TWO ROWS BELOW CHANGED THEIR EXPECTED TEXT AT Q1, and the old text was
# the bug. `(*MARKx)` and `(*NOTAVERB)` are not verb names; PCRE2 rejects both
# with "(*VERB) not recognized or malformed", and pcrec used to answer
# "requires module 'verbs'" — promising a module that will never implement them,
# because there is nothing to implement. R6 recorded that the doorway is TWO
# name tables selected by the CASE of the first byte and that nothing here could
# see it. Q1 built the tables; these rows now pin which one answered.
#
# Everything below is hand-written on purpose. tests/registry/pcre2_check.c
# sweeps ~75k generated names against libpcre2 and is a far wider net — but it
# is a net woven from libpcre2's own binary, and if that library is missing it
# SKIPS. These rows are what still holds when it does.
#
# MEASURE THAT CLAIM RATHER THAN BELIEVING IT (R8/C3-F1). A critic deleted verb
# rows one at a time on a box with PC-3 disabled: deleting `F`, `NO_JIT` or
# `scs` fails here, and deleting `LIMIT_HEAP` or `naplb` failed NOTHING. So the
# rows below pin one name per FORM GROUP — there are five — rather than one per
# name, and the honest statement is that the other 26 names are covered by PC-3
# alone. Do not read this block as "the verb tables are pinned".
# MOD-0.4d: `(*NOTAVERB)`, `(*CR:x)`, `(*pla)`, `a(*CR)`, `(*:x)`, `(*scs:x)`
# and the two 129-byte boundary rows below all gain an offset suffix here,
# for the SAME reason line 670's `(*)` row did (MOD-0.4c/S27): each is a
# message-only pin for a REFUSE(at, ...) call, so a future "blame a more
# precise position" refactor that keeps the SAME message text is invisible
# to it. Every offset below is `at` — the doorway's own default, the `(`'s
# position — because that IS what pcrec_ext_verb correctly reports at each
# of these sites today; this pins pcrec's OWN stability against a silent
# regression, not agreement with PCRE2 (PC-3 never compares offsets).
reject '(*MARKx)'    "(*VERB) not recognized or malformed"
reject '(*NOTAVERB)' "(*VERB) not recognized or malformed (pattern offset 0)"
reject '(*ACCPET)'   "(*VERB) not recognized or malformed"
# Offset pinned too (MOD-0.4c), matching the brace-quantifier family's own
# convention (R7, below): the empty-name branch blames `star` (the '*', one
# past `at`), not the doorway's own default `at` (the '('), and a message-only
# check cannot tell those apart — both produce this exact sentence.
reject '(*)'         "quantifier does not follow a repeatable item (pattern offset 1)"
# The lower table: PCRE2 picks it by the case of the first byte and says
# something different. `(*accept)` is not `(*ACCEPT)` misspelt — it is a lookup
# in a table that has no ACCEPT.
reject '(*accept)'   "(*alpha_assertion) not recognized (pattern offset 0)"
# `(*pla)` hits a DIFFERENT branch than `(*accept)` despite the shared
# message: pla IS a known lower-table name, just not in BARE form (its
# forms are ARG|EMPTYARG|GROUPARG) — this is the lower-table representative
# of the form-mismatch REFUSE, `(*CR:x)` below is the upper-table one.
# ...AND THIS ROW IS ASSERTED UNCHANGED BY [M6.6.2] WAVE F (R33 C2-6), which
# is why it is not in the block of moves below it. `(*pla)` is a REAL name in
# a form PCRE2 does not accept, and a FORM MISMATCH IS DECIDED BEFORE MODULE
# ATTRIBUTION — in pcrec as in PCRE2 — so wave F giving the name `pla` a
# module of its own must not change what a caller is told here.
#
# **AND THIS ROW CANNOT SEE THE ORDERING THAT MAKES THAT TRUE**, which is
# worth saying at the row rather than leaving as a comfortable assumption.
# The first draft of this comment claimed that moving mod_verbs.c's name→row
# lookup one statement earlier would turn this row red; BUILT AND MEASURED, it
# does not. The form refusal's TEXT comes from the VerbName TABLE
# (`t->unknown_msg`), not from the elected row, so it is byte-identical with
# the lookup on either side of the form check — and a message-only pin is
# structurally blind to the difference.
#
# WHAT THE ORDERING ACTUALLY PROTECTS IS THE ANSWER LEVEL, measured on a
# control build with the lookup moved: `--features lookaround --probe-ask
# result -- '(*pla)'` answers at `verdict` on the shipped compiler and at
# `result` on the control. `answered_at == WANT_RESULT` is the externally
# visible "gate was OPEN and the port had nothing to say" signal (D33, and
# what D65 classifies `built` on), so the control makes a FORM ERROR — a thing
# PCRE2 decides before any module question — report itself as an answer given
# with module `lookaround`'s gate open. That is the same misattribution wave F
# exists to remove, one level down. tests/cli/'s case10 pins it, because
# `--probe-ask` is the channel that can see it and this table is not.
reject '(*pla)'      "(*alpha_assertion) not recognized (pattern offset 0)"
reject '(*SCRIPT_RUN:a)' "(*VERB) not recognized or malformed"
# Real names in a form PCRE2 does not accept. Each of these is a DIFFERENT rule
# in the table, and each was measured against libpcre2 10.46 rather than read:
reject '(*MARK)'          "(*MARK) must have an argument"   # the one name with its own message
reject '(*:)'             "(*MARK) must have an argument"   # (*:...) is a MARK synonym
reject 'a(*CR)'           "(*VERB) not recognized or malformed (pattern offset 1)"  # options are start-only
reject '(*CR:x)'          "(*VERB) not recognized or malformed (pattern offset 0)"  # ... and take no argument
reject '(*LIMIT_MATCH)'   "(*VERB) not recognized or malformed"  # ... but LIMIT_* needs =n
reject '(*LIMIT_MATCH=x)' "(*VERB) not recognized or malformed"  # ... and n must be digits
reject '(*ACCEPT:x'       "(*VERB) not recognized or malformed"  # a name-run arg needs its ')'
reject '(*ACCEPT'         "(*VERB) not recognized or malformed"
# LEFTMOST ERROR WINS, pinned deliberately rather than left to be rediscovered
# (R8/C2). libpcre2 rejects `(*FAIL)*` with "quantifier does not follow a
# repeatable item" — the verb is real, but PCRE2 will not quantify it — while
# pcrec answers about the construct it met FIRST and never reads the `*`. That
# is pcrec's rule at every doorway, not a verb-doorway defect: `\d{3,1}` USED
# TO BE "requires module 'classes'" here and "numbers out of order" in PCRE2
# — different answers for the SAME reason (leftmost-wins), since `\d` itself
# was the leftmost unhandled construct under the old empty bare default.
# [STD1b] (D37, 2026-08-13) changes which doorway is leftmost: `classes` is
# now default-on, so `\d` is no longer unhandled and the pattern reaches its
# OWN quantifier — pcrec now agrees with PCRE2's wording on this cell (both
# say "numbers out of order", verified below), which is a coincidence of
# what pcrec's base-grammar message happens to say, not a new promise (D26
# still does not require wording agreement). The row is kept as
# `reject_gated none` for the OLD leftmost-wins witness (still true under
# the literal old-default spec) plus a new bare row for what leftmost-wins
# now answers by default — both are here so that if anyone ever changes
# either, they change it ON PURPOSE.
reject '(*FAIL)*'         "requires module 'verbs'"
reject_gated none '\d{3,1}' "requires module 'classes'"
reject '\d{3,1}'          "numbers out of order in {m,n} quantifier (pattern offset 6)"
# The THIRD leftmost-policy witness, ruled by Frank 2026-08-11 (§18.2 of the
# extension design): `(a)(?(1)x|y|z)` is PCRE2 error 127 — more than two
# branches, PERMANENTLY invalid, a defect module 'conditionals' can never
# repair — and pcrec still answers with the module name, because pcrec reports
# the LEFTMOST construct it cannot handle and does not read a disabled
# construct's body to rank its defects. "This is not an exercise in emulating
# the exact interface of pcre2." The exact E127 becomes part of the
# conditionals module's landing bar instead.
reject '(a)(?(1)x|y|z)'   "requires module 'conditionals'"
# THE TWO BOUNDARIES, both found by the R8 panel and both pinned on BOTH SIDES.
# A boundary row on one side only says a number exists, not where it is.
# `=digits` has a MAGNITUDE rule, not a length one: libpcre2 refuses while
# accumulating, one digit before its 32-bit counter would overflow.
reject '(*LIMIT_MATCH=4294967289)' "is outside pcrec's scope and no module will implement it"
reject '(*LIMIT_MATCH=4294967290)' "(*VERB) not recognized or malformed"
reject '(*LIMIT_MATCH=00000000000000000001)' "is outside pcrec's scope and no module will implement it"
# A verb NAME over 128 bytes is a LENGTH complaint in PCRE2, not a "no such
# name" one, and it is the same complaint from both name tables.
name128="$(printf 'A%.0s' $(seq 1 128))"
name129="$(printf 'A%.0s' $(seq 1 129))"
lname129="$(printf 'a%.0s' $(seq 1 129))"
reject "(*$name128)"  "(*VERB) not recognized or malformed"
# Offset pinned too (MOD-0.4d): the too-long-name REFUSE is `at`, not the
# name's own start — see the block comment above `(*NOTAVERB)`.
reject "(*$name129)"  "subpattern name is too long (maximum 128 code units) (pattern offset 0)"
reject "(*$lname129)" "subpattern name is too long (maximum 128 code units) (pattern offset 0)"

for v in '(*ACCEPT)' '(*FAIL)' '(*F)' '(*ACCEPT:)' '(*CR)' '(*LF)' '(*CRLF)' \
         '(*ANYCRLF)' '(*UTF)' '(*UCP)' '(*NUL)' '(*BSR_UNICODE)' '(*NOTEMPTY)' \
         '(*script_run:a)' '(*sr:a)' '(*atomic:a)' \
         '(*atomic:)'; do
    reject "$v" "requires module 'verbs'"
done
# [M6.6.2] WAVE F MOVED THREE ROWS OUT OF THE LOOP ABOVE, and the move IS the
# defect being fixed rather than bookkeeping around it. `(*pla:a)`,
# `(*naplb:a)` and `(*negative_lookbehind:a)` sat in that loop asserting
# "requires module 'verbs'" — the WRONG MODULE, which is the one fact the
# diagnostic exists to carry. Design §8.2 measured the cause at P3: the `(*`
# doorway was ONE row whose module answered for every name in both VerbName
# tables, so an alpha lookaround assertion was promised a module that will
# never implement it while the module that WILL was never named.
#
# They keep their identity as hand-written rows here rather than being left to
# the dump-driven loop further down, for this file's standing reason: the
# iteration reads the same registry the parser renders from and therefore
# cannot see a WRONG module name, while these lines are a SECOND, HUMAN source
# for it. That is precisely the property that was missing when the answer was
# wrong — the dump loop agreed with the parser, in unison, that `(*pla:a)`
# required module `verbs`, because the row it read said so.
#
# ONE FROM EACH SHAPE, deliberately: a SHORT name (`(*pla:`), a NON-ATOMIC one
# (`(*naplb:`) and a LONG spelling (`(*negative_lookbehind:`) — the three axes
# on which a name-to-row resolution can go wrong independently. The other nine
# are covered by the dump-driven loop and by PC-3.
for v in '(*pla:a)' '(*naplb:a)' '(*negative_lookbehind:a)'; do
    reject "$v" "requires module 'lookaround'"
done
# Pulled out of the loop above (MOD-0.4d) to carry its own OFFSET
# expectation: the terminal "requires module 'verbs'" REFUSE is `at` too,
# and this is the one member of the loop with a non-zero `at` to pin it
# against (the rest all start at offset 0) — see the block comment above
# `(*NOTAVERB)`.
reject 'a(*ACCEPT)' "requires module 'verbs' (pattern offset 1)"
# THE K14 FIX (MOD-0.1, 2026-08-11; ruled at design §17.2 / D34 item 1).
# These names are real PCRE2 syntax that pcrec's own compliance survey calls
# OUT-OF-SCOPE — the backtracking verbs (defined in terms of a backtracking
# tree a simulation engine does not have), the LIMIT_* family (they bound a
# backtracking search), the PCRE2-internals knobs, the Unicode-casing options,
# and scan-substring. (?C callouts carried the same K14 disposition at the
# GROUP doorway until [M4-CALLOUTS] step 1 (D36, 2026-08-14) moved it to
# PLANNED — see the `(?C1)` reject() call above, outside this loop.)
# Promising "module 'verbs'" for them was
# K14: naming a module that will never implement a construct, which D26's
# tier-2 row calls a defect in as many words. The disposition is a COLUMN
# (ROADMAP_NEVER, per-row and per-VerbName), the diagnostic names no module,
# and compliance_section.py asserts prose-OUT-OF-SCOPE <=> ROADMAP_NEVER in
# both directions so the survey and the table cannot drift apart. A malformed
# FORM of a NEVER name keeps PCRE2's own form error — the roadmap answer is
# only for constructs PCRE2 would accept ('(*MARK)' bare still gets "must
# have an argument"; 'a(*CR)' still gets the position error).
# NOTE ([M4-CALLOUTS] step 1, 2026-08-14): the verb-table LIMIT_* / NO_* /
# casing / scan-substring names below are still ROADMAP_NEVER; `(?C1)` (the
# GROUP-doorway instance, at its own reject() call above) is not — it moved
# to PLANNED the same session this note was added.
for v in '(*COMMIT)' '(*PRUNE)' '(*SKIP)' '(*THEN)' '(*MARK:x)' \
         '(*LIMIT_MATCH=1)' '(*LIMIT_HEAP=1)' '(*TURKISH_CASING)' \
         '(*NO_JIT)'; do
    reject "$v" "is outside pcrec's scope and no module will implement it"
done
# Offset pinned too (MOD-0.4d): the ROADMAP_NEVER REFUSE is `at` in both
# tables — see the block comment above `(*NOTAVERB)`.
reject '(*:x)'    "(*MARK) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md) (pattern offset 0)"   # the MARK synonym resolves to MARK's row
reject '(*scs:x)' "(*scs) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md) (pattern offset 0)"    # lower table carries the column too

# THE FIVE GRADUATED K3/K4 ROWS (FIX-2, 2026-08-10). Each was a `pinned`
# known-wrong line until the fix landed; each is now an ordinary expectation.
# Kept in one block, with its history, because a reader who finds `[[:]]` in a
# reject table deserves to know it was once the opposite.
reject '[:alpha:]' "POSIX class [:...:] is only valid inside a character class"
reject '[::]'      "POSIX class [:...:] is only valid inside a character class"
reject '[:a:]'     "POSIX class [:...:] is only valid inside a character class"
# ...and the OTHER half of the same flag, which was an over-REJECTION: nothing
# closes the pair, so PCRE2 reads ordinary members and so must pcrec.
accept '[a[:b]'
accept '[[:alpha]'
accept '[[:]]'
accept '[[:]'
# `[:]` and `[:a]` belong here too — they are the 4a doorway's accept-controls —
# but they are asserted ONCE, in the doorway-4a section above, with the R5
# FINDING 1 provenance that explains why they exist. FIX-2 added a second copy
# here; a duplicate gives the MANIFEST a spare and inflates the counts (R9/C4-2).
# K4's terminator scan. Every one of these has the `.]` or `=]` OUTSIDE the
# class, which is the shape the old scan could not see.
accept '[.a]x.]'
accept '[=a]x=]'
accept '[a[.b]c]d.]'
accept '[[.a].]'
accept '[.a].]'
# ...and the escape rule, which is why the three had to land together: the `]`
# that ends the scan here is one a backslash was hiding, so a `]`-rule without
# an escape-rule turns this correct rejection into an over-acceptance. The `[.`
# form of that is the rule-3 discriminator eleven lines down and is NOT repeated
# here — it used to be, and the duplicate is what made the MANIFEST's claim
# about it false (R9/C4-2). `[=` is the same statement at the other delimiter.
reject '[a[=b\]=]'  "POSIX collating elements are not supported"
# K4's RULE 3, and these four are the only thing that distinguishes it from the
# two weaker rules I tried first. It is "`\]` and `\\` are units", not "skip any
# `\X`" and not "suppress only a class-ending `]`" — each weaker rule gets one of
# these four wrong, and all four came from PC-3's generated sweep rather than
# from anyone's reading.
reject '[[.\.]]'      "POSIX collating elements are not supported"   # \. is NOT a unit
accept '[[.a\\]x.]'                                                  # \\ IS a unit
reject '[a[.b\].]'    "POSIX collating elements are not supported"   # \] IS a unit
accept '[[.b].]'                                                     # a bare ] ends it
accept '[[.b\]]'
reject '[[:\:]]'      "unknown POSIX class name"
# The two class-bracket constructs that are not classes at all: zero-width word
# boundary assertions. My hand-written list of fourteen names missed both, and
# the generated differential found them on its first run.
# MOD-0.3a: their honest module is 'assertions' (\b's own module) — a
# boundary assertion is not a set of characters, and 'classes' with its
# producers landed could never make these compile.
reject '[[:<:]]'      "word-boundary assertion and requires module 'assertions'"
reject '[[:>:]]'      "word-boundary assertion and requires module 'assertions'"
reject '[[:^<:]]'     "unknown POSIX class name"   # ^ negates a CLASS; these are not
# A NESTED opener wins: PCRE2 abandons the outer one and recognises the inner.
# THESE THREE PIN THE OFFSET, and that is the whole point of them. Rule 2 of
# K4's scan changes NOTHING about the verdict — with it or without it pcrec
# rejects all three — so it was an INVISIBLE branch, which is the shape R5 and
# R7 both got burned by. What it changes is WHICH CONSTRUCT gets blamed: with
# rule 2 the error points at the inner opener (offset 4), which is the one PCRE2
# recognises; without it, at the outer bracket PCRE2 abandoned (offset 1).
# Deleting rule 2 leaves tests/registry/pcre2_check.c's 1680-pattern sweep at
# zero failures, because that sweep compares VERDICTS. These rows are what sees
# it. (PCRE2 reports offset 9 here — it points at the end. pcrec's convention is
# the construct START and D26 puts the exact number in tier 3; pointing at the
# right construct is the part worth having.)
reject '[[.a[.b.].]'  "POSIX collating elements are not supported (pattern offset 4)"
reject '[a[.b[.c.].]' "POSIX collating elements are not supported (pattern offset 5)"
reject '[[=a[=b=]=]'  "POSIX collating elements are not supported (pattern offset 4)"

echo
echo "== possessive quantifiers =="
# THE MODULE-OFF ROWS. `atomic-groups` is not in std1, so a bare invocation
# still reaches the refusal, and these three are unchanged by [M6.4.2] — the
# desugaring in `p_rep` consults the RK_QUANTSUFFIX row's own `module` to build
# exactly this sentence, so the wording has one home and the pin is the
# independent, hand-written second source for it.
reject 'a*+' "possessive quantifier requires module 'atomic-groups'"
reject 'a++' "possessive quantifier requires module 'atomic-groups'"
reject 'a?+' "possessive quantifier requires module 'atomic-groups'"
# The BRACE form, which had no pin at all before [M6.4.2] and is a different
# path: `try_quant` has already consumed `{1,2}` when the `+` is seen, so the
# blame offset is the `+` at 6 rather than at 2. `{n}+`, `{n,}+` and `{,n}+`
# take the same path and are corpus cells rather than four more rows.
reject 'a{1,2}+' "possessive quantifier requires module 'atomic-groups'"

# THE LAZY-THEN-POSSESSIVE FAMILY (atomic_groups_design.md §6.3). After the
# lazy `?` has been consumed a following `+` is an ERROR, not a possessive
# marker — libpcre2 10.46 refuses all three with "quantifier does not follow a
# repeatable item", pcrec refuses them through `p_rep`'s
# "multiple quantifiers on the same item" guard, and D26 tier 2 (both REFUSE)
# is what is owed; the wording is tier 3 and ours. DO NOT "fix" the wording to
# chase 10.46's phrasing — that is exactly the tier-3 effort D26 exists to
# prevent, and pcrec already carries libpcre2's own sentence at a different
# site (parse.c's bare-anchor rejection) where it IS the right answer.
reject 'a*?+'  "multiple quantifiers on the same item (pattern offset 3)"
reject 'a*?+b' "multiple quantifiers on the same item (pattern offset 3)"
# THE CONTROL: the pre-existing base-grammar path the two rows above fall into,
# pinned so a change that moved them would have to move this too.
reject 'a**'   "multiple quantifiers on the same item (pattern offset 2)"
# `a*++` IS THE ROW A REJECT-SUITE AUTHOR WOULD NOT THINK TO RE-PIN, and its
# message CHANGES WITH THE GATE. Module off, the first `+` is still the
# unimplemented possessive marker. Module ON, the first `+` is CONSUMED as that
# marker and the SECOND re-enters the quantifier loop, so the guard fires one
# byte later — still a clean tier-2 refusal, at offset 3 rather than 2. Both
# halves are pinned because only pinning one would let the other move silently.
reject 'a*++' "possessive quantifier requires module 'atomic-groups' (pattern offset 2)"
reject_gated atomic-groups 'a*++' "multiple quantifiers on the same item (pattern offset 3)"
reject_gated atomic-groups 'a*?+' "multiple quantifiers on the same item (pattern offset 3)"

echo
echo "== [DD-14.LB] the DEFERRED lookbehind width re-check: WHICH construct is blamed =="
# THE ONLY PLACE THIS CONTRACT CAN BE TESTED. A `.rxt` `perr` block asserts a
# nonzero exit and nothing else (docs/testing.md), so the corpus can say THAT
# these refuse and cannot say WHERE — and `where` is the whole content of what
# [DD-14.LB] changed. Module `lookaround`'s §2.5 width rule for a body carrying
# a subroutine call is no longer decided in the parse hook (the callee is not
# bound there, and a FORWARD call's target is not even parsed): the hook
# RECORDS the assertion's offset in `Ast.u.look.at` and `pcrec_postresolve`
# (src/opt/postresolve.c) re-asks the rule once `pcrec_callgraph_build` has run.
# An offset is exactly what such a move can silently lose.
#
# THE FIRST THREE ROWS ARE THE ORDER CONTRACT, and they are a TRIPLE because no
# pair of them pins it. `pcrec_postresolve` visits recorded constructs in
# ASCENDING PATTERN OFFSET rather than in walk order, and walk order is not
# close to it — a flat concatenation is LEFT-NESTED, so a spine walk reaches
# the RIGHTMOST element first and an unsorted pass blames the LAST offending
# lookbehind in the pattern.
#
#   row 1  both lookbehinds refusable, first calls the first-declared callee
#   row 2  both refusable, first calls the SECOND-declared callee — so an
#          implementation ordering by callee declaration, by `A_CAP` number, or
#          by call-graph target index answers 45 here and 33 in row 1
#   row 3  ONLY THE SECOND is refusable — the row that stops "always blame the
#          first lookbehind" from passing rows 1 and 2 for the wrong reason
#
# ALL THREE OFFSETS ARE LIBPCRE2 10.46's OWN, measured through the committed
# ctypes binding: 33, 33 and 45, err 125 each. That is agreement on the tier-2
# fact D26 puts the OFFSET convention in, not merely internal consistency.
LBF=recursion,lookaround,named-groups
reject_gated "$LBF" '^(?:(?<g>a+)){0}(?:(?<h>b+)){0}ab(?<=(?&g))ab(?<=(?&h))$' "(this one is unbounded) (pattern offset 33)"
reject_gated "$LBF" '^(?:(?<g>a+)){0}(?:(?<h>b+)){0}ab(?<=(?&h))ab(?<=(?&g))$' "(this one is unbounded) (pattern offset 33)"
reject_gated "$LBF" '^(?:(?<h>ab)){0}(?:(?<g>a+)){0}ab(?<=(?&h))ab(?<=(?&g))$' "(this one is unbounded) (pattern offset 45)"
# A RECURSIVE callee has no bounded width — libpcre2 refuses it too (err 125),
# AT OFFSET 26, which is the offset pcrec now names from a pass that runs long
# after the parse hook that used to name it.
reject_gated "$LBF" '^(?:(?<g>a(?&g)?b)){0}aabb(?<=(?&g))$' "(this one is unbounded) (pattern offset 26)"
# AND THE ROW WHOSE SENTENCE IS THE EVIDENCE. This cell was PARKED in
# tests/known_fail/ by [DD-14] wave B+C as a tier-2 over-rejection caused by
# TIMING. It is not: its lookbehind body is ONE top-level branch of width 1..2,
# because the alternation lives inside the CALLEE — `(?<=(a|bc))x` reached
# through a call, which `lookaround_design.md` §2.5 charters the longest-first
# step-back loop for and does not ship. Closing the timing gap left the refusal
# standing and changed the SENTENCE from "this one is unbounded" (a claim about
# the call graph, and false) to "this one can match 1..2 characters" (a claim
# about the shipped subset, and true), at the same offset. **The wording is
# pinned here precisely because it is what told the two questions apart** — a
# regression to "unbounded" would be a true refusal for a false reason, which
# no exit code and no `perr` block can see.
reject_gated "$LBF" '^(?:(?<g>a|ab)){0}ab(?<=(?&g))$' "(this one can match 1..2 characters) (pattern offset 20)"

echo
echo "== base-grammar MISCOMPILES, fixed 2026-08-10 (K5, K6) =="
# The only rows in this file with no registry row behind them, and the reason
# they are here rather than only in the corpus is worth stating: a `.rxt` `perr`
# block asserts a REJECTION, and for these two the REASON is the whole fix.
# Both were the class the charter forbids — a quantifier silently reinterpreted
# as literal text, compiling a matcher for a different language than the pattern
# named, with no diagnostic at all. Being base-grammar errors they carry PCRE2's
# own wording rather than a "requires module" name.
#
# Every verdict below was measured against libpcre2 10.46.

# K5 — a count above 65535 is PCRE2 error 105. The overflow is remembered and
# raised only where try_quant would have succeeded, so it must reach all three
# of its return paths, not just `{m}`.
#
# THESE ROWS PIN THE OFFSET, and that is deliberate: `try_quant` keeps a
# separate end position for each of the two numbers for no other purpose, and
# until 2026-08-10 NOTHING in the repo asserted an error offset at all (R7,
# C2/T-0 — `grep -rn "pattern offset" tests/` returned nothing). Every offset
# below equals the one libpcre2 10.46 reports for the same pattern, so these
# are a conformance claim and not just a change detector. Note which byte each
# one lands on: the first number's end may be a `}` or a `,`, and the second
# number's end is a different variable.
reject 'a{65536}'       "number too big in {m,n} quantifier (pattern offset 7)"
reject 'a{100000}'      "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{0,65536}'     "number too big in {m,n} quantifier (pattern offset 9)"
reject 'a{65536,}'      "number too big in {m,n} quantifier (pattern offset 7)"
reject 'a{,65536}'      "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{65535,65536}' "number too big in {m,n} quantifier (pattern offset 13)"
# Too-big beats out-of-order — measured: PCRE2 answers 105 here, not 104. The
# clamped accumulator makes `a{65536,1}` look out-of-order internally, so
# checking in the other order is a live mistake, not a hypothetical one. The
# offset also discriminates: 7 is the FIRST number's end, which is the one that
# overflowed.
reject 'a{65536,1}'     "number too big in {m,n} quantifier (pattern offset 7)"
# Twenty digits. NOTE what this does and does not buy (R7/T-3): it pins the
# OFFSET, which the clamp would otherwise get wrong, and it exercises the same
# too-big path `a{100000}` does. It does NOT test the clamp's actual purpose —
# `big_m` is sticky and ctx_fail fires before `m` is read, so removing the
# clamp changes no observable output at all. The signed-overflow UB it prevents
# is only visible to a UBSan build, which this repo does not have.
reject 'a{99999999999999999999}' "number too big in {m,n} quantifier (pattern offset 22)"

# K6 — a well-formed quantifier with nothing to quantify is PCRE2 error 109.
# `*`, `+` and `?` were always rejected in this position; `{` was not, because
# try_quant is only reached from p_rep, AFTER an atom.
#
# The offsets are pinned here too, and they carry a claim of their own: PCRE2
# reports the CLOSING BRACE, which is exactly where try_quant leaves the cursor,
# so `cx->pos - 1` is a conformance decision rather than a convenience. Each
# value below matches libpcre2 10.46 on the same pattern.
reject '{1}'      "quantifier does not follow a repeatable item (pattern offset 2)"
reject '{2,3}'    "quantifier does not follow a repeatable item (pattern offset 4)"
reject '{,5}'     "quantifier does not follow a repeatable item (pattern offset 3)"
reject '{1,}'     "quantifier does not follow a repeatable item (pattern offset 3)"
reject '{0}'      "quantifier does not follow a repeatable item (pattern offset 2)"
reject '{1}a'     "quantifier does not follow a repeatable item (pattern offset 2)"
reject 'a|{1}'    "quantifier does not follow a repeatable item (pattern offset 4)"
reject '({1})'    "quantifier does not follow a repeatable item (pattern offset 3)"
reject '(?:{1})'  "quantifier does not follow a repeatable item (pattern offset 5)"
reject '{1}{2}'   "quantifier does not follow a repeatable item (pattern offset 2)"
# The ORDER between the three brace diagnostics in atom position, which is also
# measured: PCRE2 answers 105 for a too-big count and 104 for an out-of-order
# pair, NOT 109. A fix that asked "is anything repeatable" first would pass
# every K6 row above and get both of these wrong.
reject '{65536}'  "number too big in {m,n} quantifier (pattern offset 6)"
# K8 (found by R7's spec critic, fixed in the same checkpoint) — PCRE2 skips
# SPACE and TAB in each of the four gaps inside `{...}`, so both rules above
# have to see THROUGH the whitespace. These rows also pin the offsets, which is
# where the subtlety lives: PCRE2 reports where the DIGITS ran out, so trailing
# whitespace does not move it (`a{65536 }` is offset 7, the space itself) while
# leading whitespace does (`a{ 65536}` is offset 8, the `}`).
reject 'a{ 65536}' "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{65536 }' "number too big in {m,n} quantifier (pattern offset 7)"
reject '{ 65536}'  "number too big in {m,n} quantifier (pattern offset 7)"
reject '{ 1}'      "quantifier does not follow a repeatable item (pattern offset 3)"
reject 'a{3, 1}'   "numbers out of order in {m,n} quantifier (pattern offset 6)"
# the p_rep path takes the same offset, and it is pre-existing code
reject 'a{3,1}'    "numbers out of order in {m,n} quantifier (pattern offset 5)"
reject 'ab{5,2}'   "numbers out of order in {m,n} quantifier (pattern offset 6)"
# Out-of-order reported the `{` until R7 (offset 0 here) where PCRE2 reports
# the `}`. It was the only one of the three brace diagnostics whose offset
# disagreed, and two critics flagged it independently; aligned deliberately.
reject '{3,1}'    "numbers out of order in {m,n} quantifier (pattern offset 4)"
# FIX-3 (K13, 2026-08-11) — the in-class octal escape's 8-bit ceiling. With the
# twelve class-position fallbacks implemented ([\1] is octal, [\8] [\9] [\g]
# [\k] are literals — the accept side lives in
# tests/base/class_escape_fallbacks.rxt, 127 oracle-verified cases), the class
# decoder gained the first NEW base-grammar diagnostic since K8: a consumed
# octal value above \377 cannot be a byte. PCRE2 error 151, wording AND offset
# reproduced — the offset is where the digits ran out, measured on both cells
# by tests/probes/probe_fix3.c. The boundary is pinned on BOTH sides, per the
# K5 lesson (a boundary row on one side says a number exists, not where it
# is): \377 is the largest legal value, so an off-by-one in the ceiling flips
# the accept-control, and the .rxt perr blocks beside these assert only THAT
# [\400] fails — this is the only home for the message.
reject '[\400]' "octal value is greater than \377 in 8-bit non-UTF-8 mode (pattern offset 5)"
reject '[\777]' "octal value is greater than \377 in 8-bit non-UTF-8 mode (pattern offset 5)"
accept '[\377]'

echo
echo "== KNOWN-WRONG, pinned so a change is VISIBLE (K3, K4) =="
# These assert what pcrec does TODAY, and what it does today is WRONG. They are
# not certifications — each line records a measured disagreement with libpcre2
# 10.46 that is deliberately unfixed, so that changing it produces a signal
# instead of silence.
#
# WHY THIS EXISTS. tests/known_fail/ is the project's ratchet for deferred bugs,
# and it structurally cannot hold any of these: a `.rxt` `perr` block requires
# the PYTHON oracle to fail too, and python `re` accepts every pattern below.
# That is the same blindness that let the bugs exist (R5 F-4).
#
# WHAT IT BUYS. An R5 critic replaced the `RF_CLASS_DELIM` flag test with `if
# (1)` — a one-token edit that FIXES K3 and the `[a[:b]` half of it, moving
# pcrec strictly closer to PCRE2 — and all seven suites stayed green. The suite
# could not tell K3-fixed from K3-unfixed in either direction. Now it can.
#
# WHEN YOU FIX K3/K4: these lines must move to the normal accept/reject tables
# above, in the same commit. A failure here means "you changed the behaviour" —
# check it against libpcre2, then move the line. It does not mean "you broke
# something".
pinned() { # pinned <pattern> <accept|reject> <expected-msg-or-dash> <why it is wrong>
    # [TT-2] internal-parallelism gate; see reject()'s comment above.
    callidx=$((callidx + 1))
    [ $((callidx % SHARD_TOTAL)) -eq "$SHARD_INDEX" ] || return 0
    local pat="$1" want="$2" msg="$3" why="$4" rc out
    nwrong=$((nwrong + 1))
    out="$("$TIMEOUT_BIN" 60 "$PCREC" -p rx -o "$WORKDIR/kw.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if { [ "$want" = accept ] && [ "$rc" -eq 0 ]; } || \
       { [ "$want" = reject ] && [ "$rc" -eq 1 ]; }; then
        # verdict pinned; also pin the MESSAGE where one was given. A
        # verdict-only pin says something moved, not that it moved somewhere
        # right (R6 testability critic, T-9).
        case "$msg" in
            *[![:space:]]*) ;;
            *) bad "known-wrong '$pat': blank expected message. Use '-' to pin the VERDICT only and say so, or name the diagnostic — a blank string matches any output (R9/C4-1, C4V-2)"
               return ;;
        esac
        if [ "$msg" != "-" ]; then
            case "$out" in
                *"$msg"*) ;;
                *) bad "known-wrong '$pat': verdict unchanged but the DIAGNOSTIC changed. want: $msg ; got: $out"
                   return ;;
            esac
        fi
        seen="$seen
$pat"
        ok "known-wrong '$pat' still ${want}s — $why"
    else
        bad "known-wrong '$pat': behaviour CHANGED (expected to $want, rc=$rc). $why. If you fixed K3/K4, move this line into the tables above; if not, you have regressed something"
    fi
}
# EMPTY, and that is the point: all five lines that stood here were K3 and K4,
# and FIX-2 (2026-08-10) fixed both. Each one fired on the way past — "behaviour
# CHANGED... if you fixed K3/K4, move this line into the tables above" — which
# is the mechanism working exactly as designed, and each has moved into the
# normal accept/reject tables where it is now an ordinary expectation rather
# than a pinned defect.
#
# Keep this block and its helper. A known-wrong pin is how this project records
# a defect it has decided not to fix yet WITHOUT letting the defect become
# invisible, and the next one will want the same machinery. The helper is
# validated by the five that just graduated.

echo
echo "== every registry row covers itself (SR-4) =="
# Iterate `pcrec --list-syntax` and probe EVERY non-base row with its own
# `syntax` field. This is the half of SR-4 that makes the table load-bearing:
# a construct added to src/parse/registry.c is tested here the moment its row
# exists, with no edit to this file, so coverage cannot lag the table.
#
# WHAT THIS CANNOT DO, and why the hand-written rows above are still here.
# SR-4's plan text said to iterate the dump INSTEAD of them. That trade was not
# taken, because it gives away the property that matters most. Since SR-2 the
# module names live in exactly ONE place — the registry — and the parser renders
# its diagnostics from it. A test that reads the same table and asks "does the
# diagnostic match the table" therefore cannot see a WRONG module name: change
# `\d`'s row from `classes` to `misc` and the parser and this loop agree
# perfectly, in unison, about the wrong answer.
#
# The hand-written rows are a SECOND, HUMAN source for that name. That is the
# same rule the accept-controls follow and the same lesson the trie-identity
# check learned: a control must not share a source with the thing it controls.
# So the two layers do different jobs — iteration guarantees COVERAGE (no row
# escapes a probe), the hand-written table guarantees CORRECTNESS (the name a
# caller is given is one a human wrote down independently). Neither subsumes
# the other, and the maintenance cost of the second one IS the check.
#
# Three things iteration structurally cannot reach, which is the R4 warning
# restated with its consequence: `\x{...}` and the possessive `+` have NO row
# (they are sub-cases of base constructs, deliberately — see D24), and the
# in-class spelling of an escape (`[\d]`) is a different diagnostic from the
# atom spelling that the `syntax` field probes. All three are covered above,
# by hand, and iteration must never be read as covering them.
row_reject() { # like reject(), but counted separately so the floors stay honest
    # [TT-2] internal-parallelism gate; see reject()'s comment near the top
    # of this file.
    callidx=$((callidx + 1))
    [ $((callidx % SHARD_TOTAL)) -eq "$SHARD_INDEX" ] || return 0
    local pat="$1" want="$2" mod="${3:-}" out rc
    # Same empty-expectation trap as reject() (R9/C4-1). The BADROW filter below
    # already drops dump rows with an empty `expect` field, so this is the
    # second line rather than the first — but it is the line that survives
    # someone rewriting the awk.
    case "$want" in
        *[![:space:]]*) ;;
        *) bad "row '$pat': blank 'expect' text reached row_reject — it would match any output (R9/C4V-2)"
           return ;;
    esac
    niter=$((niter + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    # [STD1b] (D37, 2026-08-13): every row's `expect` field is the CLOSED-gate
    # answer — the row-level attribution the registry declares, which is what
    # a fully bare invocation always got back when the enabled set was empty.
    # `classes`/`modifiers` are default-on now, so a genuinely bare probe for
    # one of THEIR rows no longer reaches that answer (it either accepts, or
    # — for `(?J)`/`(?m)`, whose live per-letter attribution dissents from
    # their own row's declared 'modifiers' — reaches a DIFFERENT rejection).
    # Probing those rows with `--features none` instead keeps testing the
    # exact thing this loop has always tested (the row's own declared
    # closed-gate expectation) rather than silently starting to test
    # something else. Every other module keeps the original bare probe,
    # unchanged.
    case "$mod" in
        classes|modifiers)
            out="$("$TIMEOUT_BIN" 60 "$PCREC" --features none -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$? ;;
        *)
            out="$("$TIMEOUT_BIN" 60 "$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$? ;;
    esac
    if [ "$rc" -ne 1 ]; then
        bad "row '$pat': exit $rc, not a clean exit-1 rejection"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "row '$pat': diagnostic does not contain the dump's own 'expect' text. want: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "row '$pat': rejected but still wrote an output file"
        return
    fi
    ok "row '$pat' -> $want"
}

"$PCREC" --list-syntax > "$WORKDIR/syntax.tsv" 2>"$WORKDIR/syntax.err"
if [ ! -s "$WORKDIR/syntax.tsv" ]; then
    # K30 (found 2026-08-23 by [TT-8]'s PROCS sweep; fixed at [M6.6.2] wave F,
    # the next change to touch this table). THE VACUITY GUARD IS REPORTED
    # ONCE, not once per shard.
    #
    # THE DEFECT: this `bad` sat outside any shard gate, so under sabotage
    # S18-tsv-empty (pcrec_syntax_tsv returns "" early) EVERY shard child
    # reported it and the top-level dispatcher reported it again — the row's
    # measured figure was shards + 1, i.e. `reject:5fail` at the old leaked
    # width, `4fail` at PROCS=4 and `3fail` at PROCS=6. That made [TT-2]'s
    # "same Summary counts at any PROCS" claim false for this section, and a
    # mech figure that moves with the harness's own parallelism is a figure
    # nobody can read.
    #
    # THE FIX IS THE GUARD, NOT THE DUMP. K30's entry offered two remedies and
    # only one of them is available: "run the dump once" is not, because every
    # shard child runs its OWN slice of the `row_reject` loop below and needs
    # its own `probe.tsv` to do it — a shard that skipped the dump would skip
    # its rows, and the global coverage assertion would then correctly report
    # that the table was not covered. So the dump stays per-shard (it is one
    # `--list-syntax` call) and the REPORT is confined to the one process that
    # owns the global view, using this file's existing idiom for exactly that
    # (`[ -z "${REJECT_SHARD_TOTAL:-}" ]` — the same gate the BADROW report and
    # the coverage-count assertion below already use, which is a plain PROCS=1
    # run or the top-level dispatcher after aggregation, never a child).
    #
    # DETECTION IS UNCHANGED, which is the property that mattered: S18 still
    # fails this section, once, at every width — the figure becomes CONSTANT
    # rather than smaller. Verified at PROCS=4 and PROCS=6 in the same change.
    if [ -z "${REJECT_SHARD_TOTAL:-}" ]; then
        bad "--list-syntax produced no dump ($(cat "$WORKDIR/syntax.err")) — every check below would pass vacuously"
    fi
else
    # Field extraction goes through awk, NOT `IFS=$'\t' read -r a b c...`.
    # Tab is IFS *whitespace*, so bash collapses runs of it and strips leading
    # and trailing ones: any row with an empty field shifts every column after
    # it, and the loop then compares the wrong strings while still reporting
    # PASS/FAIL as though it were working. That is precisely how this section
    # first "ran" — it read each row's `note` as its `expect` and iterated the
    # one base row it was supposed to skip.
    #
    # Two columns are enough, and neither may be empty. A row whose `syntax` or
    # `expect` is blank is reported as a bad row rather than silently probed
    # with an empty pattern or matched against an empty substring — the latter
    # matches ANY diagnostic and would pass while testing nothing.
    #
    # [SR-11] columns resolved BY NAME (tests/lib/table.sh), not a hardcoded
    # `NF != 16`: D65 (2026-08-21) appended a 16th column, `built`, and the
    # previous hardcoded `NF != 15` guard here silently zeroed this whole
    # section until the loop's own non-vacuity floor below caught it (see
    # docs/design/registry_built_status_memo.md's Correction section). The
    # field-count guard now reads the header's OWN declared count
    # (table_header_ncols), so the NEXT appended column changes nothing here.
    # Column resolution itself must fail LOUDLY, not leave $AWKVARS/$NHDR
    # empty and let awk run with undefined `$status`/`$syntax`/... (every
    # unset awk field variable reads as the WHOLE line's field 0, or as
    # 0/"" — a silent mis-parse of exactly the shape this contract exists to
    # prevent). So both calls are gated on success before the awk ever runs;
    # a header this suite cannot resolve fails the section instead of
    # quietly iterating nothing (or the wrong columns).
    resolved=1
    AWKVARS="$(table_awk_map "$WORKDIR/syntax.tsv" status syntax module expect)" || resolved=0
    NHDR="$(table_header_ncols "$WORKDIR/syntax.tsv")" || resolved=0
    if [ "$resolved" -ne 1 ]; then
        bad "could not resolve --list-syntax's columns by name (tests/lib/table.sh) — the dump's header is not what this suite expects"
        : > "$WORKDIR/probe.tsv"
        : > "$WORKDIR/badrows.txt"
    else
    awk -F'\t' $AWKVARS -v nhdr="$NHDR" '
        /^#/ || NF != nhdr || $status == "base" { next }
        $syntax == "" || $expect == "" { print "BADROW\t" $0 > "/dev/stderr"; next }
        { print $syntax "\t" $expect "\t" $module }
    ' "$WORKDIR/syntax.tsv" 2>"$WORKDIR/badrows.txt" > "$WORKDIR/probe.tsv"
    fi

    # [TT-2] the BADROW diagnostic and the coverage-count assertion below are
    # GLOBAL: a child shard's own $niter is only a partial slice (never 99),
    # so evaluating "did we iterate every row" against a fraction would
    # spuriously fail there. Both run once — a plain PROCS=1 run or the
    # top-level dispatcher after aggregation, never a child (which would
    # otherwise fail a check that only looks wrong because it only ran a
    # fraction of the rows).
    if [ -s "$WORKDIR/badrows.txt" ] && [ -z "${REJECT_SHARD_TOTAL:-}" ]; then
        bad "dump rows with an empty syntax or expect field: $(wc -l < "$WORKDIR/badrows.txt")"
        cat "$WORKDIR/badrows.txt" >&2
    fi

    while IFS=$'\t' read -r syntax expect module; do
        row_reject "$syntax" "$expect" "$module"
    done < "$WORKDIR/probe.tsv"

    # The loop must have seen every non-base row: a `read` that silently stops
    # early would make this whole section quietly shrink to nothing. -1 when
    # column resolution itself failed above (never a legitimate count), so
    # this can never coincidentally agree with `niter` and mask that failure.
    if [ "$resolved" -eq 1 ]; then
        nexpected=$(awk -F'\t' $AWKVARS -v nhdr="$NHDR" '!/^#/ && NF == nhdr && $status != "base"' "$WORKDIR/syntax.tsv" | wc -l)
    else
        nexpected=-1
    fi
    # `-eq 66`, not `-ge 60`: the floor had six rows of slack, and R6 measured
    # what slack buys — see the summary block below.
    # 67 -> 99 at Q2/SR-9 (100 rows, of which `(?:` is the one base row).
    if [ -z "${REJECT_SHARD_TOTAL:-}" ]; then
        # 99 -> 103 at [M6.4.2]: the four RK_QUANTSUFFIX rows. This is the
        # NON-BASE count (`(?:` is the one RS_BASE row), and all four new rows
        # are RS_MODULE, so it moves by exactly four. They join this iteration
        # for free because their `expect` — "requires module 'atomic-groups'" —
        # really is a substring of what running their own `syntax` prints at
        # the closed gate, and module `atomic-groups` is not in std1.
        #
        # 103 -> 105 at [M6.5.2]: the two new `RK_ESC` rows with tails `<` and
        # `'`, module `recursion`, which split the `\g` doorway's two
        # constructs apart (§9). Both are RS_MODULE and both refuse at the
        # closed gate naming `recursion`, so they join the iteration on the
        # same terms the quantifier-suffix rows did. Nothing RETIRED from this
        # count: every row module `backrefs` built was already in it and still
        # refuses at the CLOSED gate, which is what this loop measures.
        # 105 -> 117 at [M6.6.2] WAVE F: the twelve `(*` alpha lookaround
        # spellings (Frank's ASK 3 ruling). They join this iteration on the
        # same terms every other row does — their `expect` is "requires module
        # 'lookaround'" and that really is a substring of what running their
        # own `syntax` prints at the closed gate, since module `lookaround` is
        # not in std1. Three of them ALSO have hand-written rows above (one
        # short, one non-atomic, one long spelling), which is the layering
        # this section's own header describes: iteration guarantees coverage,
        # the hand-written table guarantees the module NAME is one a human
        # wrote down independently. Nothing RETIRED: the three rows that moved
        # in this wave moved WITHIN the hand-written table, out of the `verbs`
        # loop and into a `lookaround` one, and both loops still probe at the
        # closed gate.
        # 117 -> 127 at [DD-14] WAVE F: module `recursion`'s nine RF_INDEX
        # spellings (design §8.1's four missing families) plus the
        # `(?(DEFINE)` row (D71 item 4). They join this iteration on the same
        # terms every other row does — MEASURED at the closed gate, each one
        # really does print "requires module 'recursion'" for its own
        # `syntax`: `(?10)` through the `(?1` doorway, `(?01)` through
        # `(?0`, `\g<0>` through `\g`, and `(?(DEFINE)(?<w>a))` through the
        # `DEFINE)` tail on `(?(`. That last one is the load-bearing case
        # for this wave, because the TAIL-LESS `(?(` row beside it is module
        # `conditionals`': if the tail ever stopped winning the arbitration,
        # this loop would see the wrong module name in the refusal.
        #
        # NOTHING RETIRED. The nine index rows are spellings the compiler
        # ALREADY handled; before this wave they had no row and so no probe
        # here, which is precisely the coverage gap the wave closed.
        if [ "$niter" -eq "$nexpected" ] && [ "$niter" -eq 127 ]; then
            ok "iterated every non-base row in the dump ($niter)"
        else
            bad "iterated $niter rows, dump has $nexpected non-base rows (floor 60) — the iteration is not covering the table"
        fi
    fi
fi

# [TT-2] a CHILD shard worker (REJECT_SHARD_TOTAL was set by the dispatcher
# above when it spawned this process) stops HERE: it writes a compact,
# machine-readable result block to its OWN result file (never to stdout —
# stdout is what the parent `cat`s verbatim for a human to read, so a result
# block written there would leak into `make test-reject`'s visible output)
# plus its own slice of `$seen`, then exits. The duplicate-check/MANIFEST/
# final-count tail below needs the FULL aggregate — every shard's
# pass/fail/.../seen — which only the top-level dispatcher (after collecting
# every shard's files, see above) or a plain PROCS=1 run (which never sets
# REJECT_SHARD_TOTAL at all) ever has.
if [ -n "${REJECT_SHARD_TOTAL:-}" ]; then
    if [ -z "${REJECT_RESULT_FILE:-}" ]; then
        echo "reject: shard $REJECT_SHARD_INDEX invoked with no REJECT_RESULT_FILE — dispatcher bug, refusing to leak the result block onto a displayed stream" >&2
        exit 3
    fi
    {
        echo "shard_pass: $pass"
        echo "shard_fail: $fail"
        echo "shard_nrej: $nrej"
        echo "shard_naccept: $naccept"
        echo "shard_ngated: $ngated"
        echo "shard_niter: $niter"
        echo "shard_nwrong: $nwrong"
    } > "$REJECT_RESULT_FILE"
    [ -n "${REJECT_SEEN_FILE:-}" ] && printf '%s\n' "$seen" > "$REJECT_SEEN_FILE"
    exit 0
fi

echo
echo "== Summary =="
echo "rejections checked: $nrej"
echo "rows iterated:      $niter"
echo "accept controls:    $naccept"
echo "known-wrong pinned: $nwrong"
echo "checks passed: $pass"
echo "checks failed: $fail"
# EXACT counts, not floors. These were `-lt 90` and `-lt 18` against 93 and 19
# actual, and an R5 critic showed what three checks of slack buys an attacker:
# delete `\R`, `\X` and `\C`, then change `\R`'s registry row from 'misc' to
# 'classes', and pcrec tells the caller to enable the WRONG module — the one
# fact the diagnostic exists to carry — with all seven suites green. The
# registry conformance check cannot object because since SR-2 both sides read
# the same row, and the feature/module bijection stays consistent.
#
# A floor guards a COUNT; the thing worth guarding is a SET.
#
# THE COUNT ALONE IS NOT ENOUGH, and R7/T-7 measured exactly how it fails. A
# critic moved the 65535 ceiling to 65534 — rejecting every legal count at the
# documented boundary — then deleted the single row that caught it and bumped
# the expected count by one, which is what THIS FILE'S OWN FAILURE MESSAGE
# invites. `make test` went green in a two-line diff. The count made the
# deletion visible in the diff; it did not make it fail. That is the same
# "exact counts disarm themselves" hazard R6 recorded, and a number cannot fix
# it because the number is what the attacker is told to edit.
#
# So the rows whose absence would be silent are named HERE, by pattern. A
# manifest is not a count: deleting the row makes this fail, and the failure
# message does not tell you to edit a number. Keep it short — it is for rows
# that are the ONLY check of something, not for coverage in general.
# AND THE MANIFEST ASSUMES EVERY ROW IS UNIQUE, so enforce that rather than
# assume it. `seen` is a flat log of every pattern that passed ANY check, and
# `must_have` only asks whether a pattern appears in it — so a row that is
# written TWICE has a spare. Delete either copy and the manifest still finds the
# other, which is precisely the "delete the row, bump the count" attack the
# manifest exists to defeat, with the count edit made unnecessary.
#
# Measured: `[a[.b\].]` was written twice, and it was the ONLY duplicated
# pattern in this file. A critic deleted one copy, bumped the exact count 201 →
# 200 exactly as the failure message below forbids, and the suite went green
# with one of the two witnesses for K4's rule 3 physically gone (R9/C4-2).
#
# A pattern cannot legitimately appear twice: it is either accepted or rejected,
# never both, and asserting the same thing twice also inflates the exact counts.
dupes="$(printf '%s\n' "$seen" | sed '/^$/d' | LC_ALL=C sort | LC_ALL=C uniq -d)"
if [ -n "$dupes" ]; then
    while IFS= read -r d; do
        [ -z "$d" ] && continue
        bad "duplicate row: '$d' is asserted more than once. A duplicated row gives the MANIFEST a spare copy, so deleting the real check goes undetected — and it inflates the exact counts. Keep one."
    done <<DUPES
$dupes
DUPES
else
    ok "no pattern is asserted twice (the MANIFEST's uniqueness assumption holds)"
fi

manifest_missing=0
must_have() { # must_have <pattern> <why it is irreplaceable>
    # Match a WHOLE recorded line, not a substring. `[:alpha:]` is a substring
    # of the unrelated row `[[:alpha:]]`, so a substring test would have made
    # this entry silently vacuous — the exact failure mode the manifest exists
    # to prevent, found while writing it.
    case "
$seen
" in
        *"
$1
"*) ;;
        *) echo "reject: MANIFEST — no check exercised '$1'." >&2
           echo "reject:   why it must exist: $2" >&2
           echo "reject:   do NOT satisfy this by editing a count; restore the row." >&2
           manifest_missing=1 ;;
    esac
}
must_have '(?:){65535}' \
    "the only check in the repo that sees an off-by-one in K5's 65535 ceiling"
must_have 'a{1,65536x}' \
    "the only check of the big_n half of K5's over-reach guard (R7/T-5)"
must_have 'a{65536x}' \
    "the big_m half of the same guard"
must_have '[:alpha:]' \
    "K3's over-ACCEPTANCE: pcrec compiled this into a matcher for {: a l p h}"
must_have '[a[:b]' \
    "K3's over-REJECTION, the same missing flag from the other side"
must_have '[\N]' \
    "R9/SPEC-classes-F1: the in-class position of a REAL construct that PCRE2 forbids there permanently. Without it, promising module 'classes' for [\\N] returns unnoticed"
must_have '[0-[:digit:]]' \
    "R9/SPEC-FA: a class construct as a range ENDPOINT is PCRE2 error 150, and pcrec emitted a matcher for it. The only reject row for a tier-1 miscompile found by spec-first testing"
must_have '[0-[:digit]' \
    "R9/SPEC-FA: the accept side of the same rule — the test is whether the PAIR CLOSES, not whether the byte is '['. Without this the fix could over-reject every '[' endpoint and nothing would notice"
must_have '[a[.b\].]' \
    "the ONLY row where K4's escape rule is load-bearing; without it this flips to over-acceptance"
must_have '[a[.b]c]d.]' \
    "K4's sharpest case: the '.]' matched sits outside the class that closed before it"
must_have '[[.a[.b.].]' \
    "the ONLY check of K4's nested-opener rule; it is invisible to every verdict-level sweep"
must_have '[[:AlPhA:]]' \
    "the only pin that the 14 POSIX class names are CASE-SENSITIVE"
must_have '[:foo:]' \
    "the only pin that POSITION beats NAME: wrong place is reported before unknown name"
must_have '[[.a\\]x.]' \
    "the ONLY case that rules out 'suppress only a class-ending ]' for K4 rule 3"
must_have '[[.\.]]' \
    "the ONLY case that rules out 'skip any \\X' for K4 rule 3"
must_have '[[:<:]]' \
    "a class-bracket construct that is a word-boundary ASSERTION, not a class"
must_have 'a{2,3,4}' \
    "the only malformed-brace control with a SECOND comma"
# Q1's outcomes. Each of these five is the ONLY hand-written check of one rule,
# and all five are answered far more broadly by tests/registry/pcre2_check.c —
# which SKIPS without libpcre2 installed. That is exactly when a manifest earns
# its keep: it names what stops being covered on a box the wide net cannot run.
must_have '(*NOTAVERB)' \
    "the only pin that a name PCRE2 does not have is NOT promised a module (Q1)"
must_have '(*accept)' \
    "the only pin of the LOWER verb table — the case of the first byte picks it"
must_have '(*MARK)' \
    "the only pin of a verb name carrying its own message rather than the generic one"
must_have 'a(*CR)' \
    "the only pin that a start-of-pattern option is invalid away from the start"
must_have '(*)' \
    "the only pin that an empty verb name is a quantifier error, not a verb"
must_have '(*FAIL)*' \
    "the only pin that pcrec reports the LEFTMOST error, where libpcre2 reports a later one"
must_have '(a)(?(1)x|y|z)' \
    "the leftmost policy RULED (2026-08-11, design §18.2): a permanently-invalid body (PCRE2 E127) behind a disabled doorway still gets the module answer; exact E127 is the conditionals module's landing bar"
must_have '(*LIMIT_MATCH=4294967290)' \
    "the only pin of the =digits MAGNITUDE boundary; 4294967289 beside it is the control"
must_have '\U' \
    "representative of the five rowless REAL escapes (\\U \\u \\F \\L \\l) the extension design §7.1 plans to give rows — their fall-through wording is otherwise the project's only unguarded diagnostic surface (R11 disposition 14, A1)"
must_have '[\400]' \
    "the only pin of the in-class octal \\377 ceiling's DIAGNOSTIC (FIX-3/K13) — the .rxt perr beside it asserts only that the pattern fails, and '[\\377]' is its accept-side boundary control"
must_have '(*scs:x)' \
    "the only pin that the LOWER verb table carries the ROADMAP_NEVER column too (K14) — every other NEVER pin is an upper-table name"
must_have '(?C1)' \
    "[M4-CALLOUTS] step 1 (D36, 2026-08-14): was the only pin of ROADMAP_NEVER at the GROUP doorway (K14); the flip moved the row to PLANNED, so this is now the only pin that the callouts row promises module 'callouts' — deleting it leaves the row's diagnostic text unguarded"
must_have '[0-\d]' \
    "K12's row: a certifiably SET-shaped escape at a range endpoint is PCRE2 error 150, and pcrec promised module 'classes' for it — a promise no module could keep"
must_have '[0-\p{L}]' \
    "the K12 boundary's other side: a BODY-dependent row keeps its module promise because pcrec cannot certify 150 for an arbitrary body ([0-\\p{Foo}] is 147). Deleting it frees the endpoint rule to over-reach onto \\p"
must_have '[0-\8]' \
    "the K12 accept side: a literal-fallback escape at an endpoint RIDES (FIX-3). Without it the endpoint rule could over-reject every escape endpoint and nothing would notice"
if [ "$manifest_missing" -ne 0 ]; then
    echo "reject: one or more irreplaceable checks are gone — see above" >&2
    exit 1
fi

# Exact numbers do not give you the set either, but they make every deletion
# deliberate and visible in the diff, which is what the slack removed. If you
# added or removed coverage on purpose, update these three numbers in the same
# commit — and check first whether the row belongs in the manifest above.
#
# 201 → 200 and 59 → 57 on 2026-08-10 (R9/C4-2), and this is the one kind of
# count edit that is legitimate: three rows were DUPLICATES, not coverage.
# `[a[.b\].]`, `[:]` and `[:a]` were each asserted twice, so those three checks
# were counted twice while testing nothing extra — and the spare copy is what
# made the MANIFEST unable to notice the real row being deleted. The duplicate
# detector above now fails if it happens again, which is what makes lowering
# these numbers safe rather than the very move this file warns about.
#
# 306/65/0/15 -> 274/99/0/55 at [STD1b] (D37, 2026-08-13): the bare-default
# flip (`classes`+`modifiers` now default-on) moved every row whose OLD bare
# behaviour depended on the empty default from `reject` to `reject_gated
# none` (same assertion, same diagnostic, now pinned under an explicit
# spec instead of the bare invocation) — read the per-row [STD1b] comments
# above for which, do not hand-derive the arithmetic here (this paragraph
# is the exact "hand-copied figures go stale" trap this file's CLAUDE.md
# warns about; the harness's own summary block is the source of truth,
# always re-read from a run before editing these four numbers). New
# `accept` controls pin the bare-default POSITIVE half (these constructs
# now compile with no `--features` flag at all); a handful of rows also
# gained a fresh `reject`/`reject_gated` pair where the bare diagnostic
# genuinely changed TEXT rather than just moving behind `--features none`
# (`\d{3,1}`, the three malformed-hyphen runs, the tier-1 miscompile guard
# proof, the std1-boundary proof for `(?J)a`).
# [M6.5.2] gated 65 -> 66: module `backrefs` landed and the arm's pin MOVED
# rather than retiring. `--features backrefs '\k'` now reaches a SHAPE error
# (the module builds that row), so the enabled-but-unbuilt pin moved to
# `recursion`'s `\g<1>` — a row THIS module added, born unbuilt, splitting the
# `\g` doorway's SUBROUTINE half away from its BACKREFERENCE half. Net zero
# there; the +1 is a NEW gated row asserting that with all three of
# backrefs/named-groups/modifiers enabled a duplicate name is legal and what
# still refuses is a reference to a name the pattern never declares (the
# error-115 class). Rejections and controls are unmoved: every construct this
# module built already refused at the CLOSED gate and still does.
#
# [DD-14.LB] (2026-08-24) gated 73 -> 78, rejections and controls unmoved. The
# five rows are the deferred lookbehind width re-check's OFFSET contract; the
# echo below carries the argument. Note also that this echo's BACKTICKS were
# live command substitution inside a double-quoted string — the guard's own
# message lost several fragments to it and printed "command not found" every
# time it fired — and are single quotes now.
if [ "$nrej" -ne 282 ] || [ "$naccept" -ne 99 ] || [ "$nwrong" -ne 0 ] || [ "$ngated" -ne 78 ]; then
    echo "reject: COVERAGE CHANGED — $nrej rejections / $naccept controls / $nwrong known-wrong / $ngated gated, expected 282 / 99 / 0 / 78 ([DD-14.LB] moved gated 73 -> 78 and rejections not at all. The five new gated rows are the DEFERRED lookbehind width re-check's OFFSET contract, and they are in this file rather than in tests/recursion/inlookaround.rxt because a '.rxt' 'perr' asserts a nonzero exit and nothing else -- while WHERE the refusal points is the whole content of what that wave changed, module 'lookaround''s SS2.5 rule having moved out of the parse hook and into 'pcrec_postresolve'. Three of them pin the ORDER ('pcrec_postresolve' visits recorded constructs in ASCENDING PATTERN OFFSET, not walk order, which for a left-nested A_CAT spine would blame the LAST offending lookbehind); the triple is irreducible, since row 3 is what stops 'always blame the first lookbehind' passing rows 1 and 2 for the wrong reason, and all three offsets are libpcre2 10.46's own. The fifth pins a WORDING, which this file normally leaves to D26 tier 3 and which earns a pin here for one reason: that sentence is what proved wave B+C's parked cell 2 was a SS2.5 capability limit rather than the timing bug it was filed as, so a regression to 'unbounded' would be a true refusal for a false reason and no exit code could see it. Before those, [M6.5.2] moved rejections 279 -> 282 and gated 65 -> 73. The three new rejections are the module's own std1-BOUNDARY proof -- (a)\\1, \\k<n> and (a)\\g{-1} refused by the BARE default naming backrefs, the shape (?J)a already carried. The seven new gated rows are backrefs_design.md S10's partial-enable MATRIX, which needs THREE modules to state and which a .rxt block cannot express because which module a diagnostic PROMISES is the tier-2 fact under D26; one of its cells CORRECTS the design (under std1 '(?<n>a)\\k<n>' names named-groups, not backrefs, because pcrec reports the LEFTMOST construct it cannot handle and the DECLARATION comes first). Before those, gated 65 -> 66: the enabled-but-unbuilt pin MOVED backrefs -> recursion (\\g<1>, a row that module added born unbuilt) rather than retiring, net zero, and one NEW gated row asserts that with backrefs+named-groups+modifiers a duplicate NAME is legal while a reference to an undeclared one is still the error-115 class. Before that, [M6.4.2] moved both: +5 rejections (the brace-form module-off row a{1,2}+, which had none; the a*?+ / a*?+b lazy-then-possessive pair and their a** base-grammar control, design 6.3; and a*++, whose message CHANGES when the module is enabled) and +1 net gated (the atomic-groups enabled-but-unbuilt row RETIRED -- (?>a) compiles now -- while a*++ and a*?+ gained gate-OPEN pins, which is where a*++'s changed message lives). Before that, [M6.2] wave A added 7: the four enabled-but-unbuilt escape rows \\b/\\B/\\G/\\K, the two (?m) spellings under an ENABLED assertions module, and the assertions-OFF twin that is their failing direction; [M6.2] wave B took 2 back — \\b and \\B COMPILE now; [M6.2] wave C took 2 more — the two (?m) spellings COMPILE now, their enabled-but-unbuilt rows retired, and one duplicate module-OFF row was merged into the pair beside them; [M6.2] wave D took 1 more — \\G COMPILES now, leaving \\K as the sole enabled-but-unbuilt row in the tree. [M6.2] wave E took that one back and then added FOUR, +3 net: module 'assertions' has no unbuilt construct left, and \\K's row was the tree's ONLY hand-written pin on ext.c's enabled-but-unbuilt arm — an arm whose real population is every module with rows and no producer (backrefs, lookaround, atomic-groups, quoting, all MEASURED live by that wave), so the pin is RE-HOMED there across three modules and BOTH positions rather than lost. The count going DOWN is the wave landing rather than coverage eroding, and the control that says so is tests/assertions/run_assertions_tests.sh's compile assertions)." >&2
    echo "reject: if that was deliberate, update the expected counts in this file's summary block; if not, coverage was removed" >&2
    exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
