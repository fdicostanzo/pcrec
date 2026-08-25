#!/usr/bin/env bash
# tests/harness/run.sh — .rxt test runner for pcrec.
#
# Usage: bash tests/harness/run.sh [file-or-dir ...]
#   With no arguments, runs every *.rxt under <repo-root>/tests/, EXCEPT
#   tests/known_fail/ (deferred-bug regressions that are expected to fail —
#   see docs/dev/known_issues.md). Pass such a file explicitly to run it.
#   Arguments may be individual .rxt files or directories (searched
#   recursively for *.rxt).
#
# Env vars:
#   PCREC      path to the pcrec binary   (default: <repo-root>/build/pcrec)
#   RXTFLAGS   EXTRA pcrec flags appended to every compile in this run, for
#              running one corpus over a COMPILER AXIS the .rxt format has no
#              directive for. Empty by default, so a plain run is byte-for-byte
#              unchanged. [DD-14 wave G] added it for `-fno-splice-calls`
#              (design §9.2's `A == B` control: the SPLICE-linked and the
#              LINKAGE-linked artifact must agree on every cell), and it is
#              deliberately a general knob rather than that one flag — the
#              deny family already has five members and each of them is a
#              corpus-wide axis somebody will want to sweep. It is appended
#              LAST so a directive-supplied flag on the same axis wins.
#   RXTROUTE   ([DD-14.FB]) the INITIAL entry route for every block in this
#              run, overridden per block by a `frames-buffer=` directive.
#              Same spelling as that directive: default | null | <n> |
#              <frames>,<trail>. Empty (the default) means `default`, so a
#              plain run is byte-for-byte unchanged. `RXTROUTE=null` is the
#              interesting one: spec §10.3 defines a NULL descriptor to be
#              EXACTLY the un-suffixed call, so re-running any corpus under it
#              must reproduce that corpus's results cell for cell across a
#              whole spread of patterns — [DD-14.FB]'s NULL-equivalence cell,
#              as a corpus-wide axis rather than a handful of hand-picked
#              blocks. A numeric RXTROUTE is a blunter instrument (a capacity
#              that suits one block will starve another) and is offered for
#              symmetry, not because a sweep wants it.
#   CC         C compiler                 (default: gcc)
#   GENCFLAGS  flags for compiling generated code
#              (default: -O1 -std=gnu11 -Wall -Wextra -Werror)
#   LINTGEN=1  (SAN-1) ride this compile pass with gcc -fanalyzer on every
#              generated matcher — the compilee-axis half of `make lint`,
#              opt-in so a plain `make test` is byte-for-byte unchanged.
#              Findings surface the same way any other GENCFLAGS warning
#              does: -Werror is already in the default GENCFLAGS, so an
#              analyzer finding fails the compile loudly. See docs/testing.md
#              "Sanitizer + lint battery" for the shape survey that found
#              zero analyzer findings/false positives before this was wired.
#   KEEP=1     keep the temp working directory instead of deleting it
#   VERBOSE=1  print a line for every passing case, not just failures
#   PROCS=N    run N .rxt FILES concurrently (default 1 — serial, unchanged).
#              Each file runs in its own re-invocation of this script with its
#              own temp dir; the parent aggregates the per-file summaries and
#              HARD-FAILS if any worker vanished without one (a lost worker
#              must never read as a pass). Summary line format is identical in
#              both modes — tests/mech greps it. On this box prefer
#              TMPDIR=/var/tmp at higher PROCS: /tmp is a quota'd tmpfs.
#
# See docs/testing.md for the .rxt format and driver protocol.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# D45: ONE shared generated-code compile budget for the whole tree.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
RUN_SECS="$(gen_run_secs)"   # per-cell matcher-run budget; see the run site

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
RXTFLAGS="${RXTFLAGS:-}"
RXTROUTE="${RXTROUTE:-}"
KEEP="${KEEP:-0}"
VERBOSE="${VERBOSE:-0}"
PROCS="${PROCS:-1}"
case "$PROCS" in (''|*[!0-9]*) echo "run.sh: PROCS must be a positive integer, got '$PROCS'" >&2; exit 2;; esac
[ "$PROCS" -ge 1 ] || { echo "run.sh: PROCS must be >= 1, got '$PROCS'" >&2; exit 2; }

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then
        echo "run.sh: KEEP=1, temp dir preserved: $WORKDIR" >&2
    else
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

# ---- collect .rxt files -------------------------------------------------

files=()
if [ $# -eq 0 ]; then
    while IFS= read -r f; do files+=("$f"); done \
        < <(find "$ROOT_DIR/tests" -name '*.rxt' \
                 -not -path "*/known_fail/*" | sort)
else
    for arg in "$@"; do
        if [ -d "$arg" ]; then
            while IFS= read -r f; do files+=("$f"); done \
                < <(find "$arg" -name '*.rxt' | sort)
        else
            files+=("$arg")
        fi
    done
fi

# ---- parallel dispatch (PROCS > 1): one worker per FILE ---------------------
#
# Each worker is this same script, PROCS=1, one file, its own WORKDIR; stdout
# and stderr go to per-worker files replayed IN files[] ORDER after the wait,
# so the parallel output is deterministic and diffable. The parent judges a
# worker ONLY by its printed summary (never by exit code alone): a worker
# whose output lacks the "cases passed:" line is a HARD failure — the
# lost-worker-reads-as-pass shape is the one this block must never have.

if [ "$PROCS" -gt 1 ] && [ "${#files[@]}" -gt 1 ]; then
    pardir="$WORKDIR/par"
    mkdir -p "$pardir"

    running=0
    idx=0
    for f in "${files[@]}"; do
        idx=$((idx + 1))
        PROCS=1 PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
            RXTFLAGS="$RXTFLAGS" RXTROUTE="$RXTROUTE" \
            KEEP="$KEEP" VERBOSE="$VERBOSE" \
            bash "${BASH_SOURCE[0]}" "$f" \
            > "$pardir/$idx.out" 2> "$pardir/$idx.err" &
        running=$((running + 1))
        if [ "$running" -ge "$PROCS" ]; then
            wait -n || true
            running=$((running - 1))
        fi
    done
    wait

    total_pass=0
    total_fail=0
    total_cfail=0
    total_pending=0
    summaries=0
    fail_files=()

    idx=0
    for f in "${files[@]}"; do
        idx=$((idx + 1))
        # replay the worker's failure detail and any harness notes, in order
        cat "$pardir/$idx.err" >&2
        p="$(grep -m1 '^cases passed:' "$pardir/$idx.out" | grep -oE '[0-9]+')"
        x="$(grep -m1 '^cases failed:' "$pardir/$idx.out" | grep -oE '[0-9]+')"
        c="$(grep -m1 '^pattern-compile failures (distinct):' "$pardir/$idx.out" | grep -oE '[0-9]+$')"
        gp="$(grep -m1 '^group cases pending-vm:' "$pardir/$idx.out" | grep -oE '[0-9]+$')"
        if [ -z "$p" ] || [ -z "$x" ]; then
            echo "$f: HARNESS FAILURE: worker produced no summary (crashed or was killed) — counting as failed" >&2
            total_fail=$((total_fail + 1))
            fail_files+=("$f: worker lost")
            continue
        fi
        summaries=$((summaries + 1))
        total_pass=$((total_pass + p))
        total_fail=$((total_fail + x))
        total_cfail=$((total_cfail + ${c:-0}))
        total_pending=$((total_pending + ${gp:-0}))
        [ "$x" -gt 0 ] && fail_files+=("$f: $x")
    done

    echo
    echo "== Summary =="
    echo "cases passed: $total_pass"
    echo "cases failed: $total_fail"
    if [ ${#fail_files[@]} -gt 0 ]; then
        echo "failures by file:"
        for line in "${fail_files[@]}"; do echo "  $line"; done | sort
    fi
    echo "pattern-compile failures (distinct): $total_cfail"
    echo "group cases pending-vm: $total_pending"
    echo "parallel: $summaries of ${#files[@]} file workers reported (PROCS=$PROCS)"

    if [ "$summaries" -ne "${#files[@]}" ]; then
        echo "run.sh: HARD FAILURE: $((${#files[@]} - summaries)) worker(s) vanished without a summary" >&2
        exit 1
    fi
    if [ $((total_pass + total_fail)) -eq 0 ]; then
        echo "run.sh: NO CASES RUN — corpus missing or fully unparseable" >&2
        exit 1
    fi
    [ "$total_fail" -eq 0 ] && exit 0
    exit 1
fi

# ---- result tracking ------------------------------------------------------

total_pass=0
total_fail=0
total_pending=0        # [M4.5a] 'gp' (pending-VM) capture-group cases: out of
                        # the artifact's RX_NCAPS range, population-accounted
                        # separately from pass/fail — not skipped silently
declare -A file_fail_count=()
declare -A features_seen=()
compile_fail_set=()   # distinct "file:line" pattern-compile failures
block_counter=0

contains_fail() {
    local needle="$1" x
    for x in "${compile_fail_set[@]}"; do
        [ "$x" = "$needle" ] && return 0
    done
    return 1
}

record_fail() {
    # record_fail <file> <line> <message...>
    local f="$1" ln="$2"
    shift 2
    echo "$f:$ln: $*" >&2
    file_fail_count["$f"]=$(( ${file_fail_count["$f"]:-0} + 1 ))
    total_fail=$(( total_fail + 1 ))
}

record_pass() {
    total_pass=$(( total_pass + 1 ))
}

# [DD-14.FB] valid_route <spec> — the ONE definition of the route grammar,
# shared by the `frames-buffer=` directive and the RXTROUTE env var so the two
# cannot drift into accepting different spellings. driver.c parses the same
# four shapes and is the thing that would reject a fifth; this check is here so
# a typo'd directive is a LOUD parse-time harness failure rather than a driver
# exit 2 that some other arm reads as a crash.
valid_route() {
    case "$1" in
        ""|default|null) return 0 ;;
        *[!0-9,]*) return 1 ;;
        *,*,*) return 1 ;;
        *,) return 1 ;;
        ,*) return 1 ;;
        *) return 0 ;;
    esac
}

# [M4.5a] record_case_group_fail <file> <case-index> <reason> — fails every
# 'g'/'gp' capture-group expectation attached to case <case-index> (via
# case_gspec[<case-index>], "slot,start,end,pending;..."), for use when the
# WHOLE block never got far enough to check anything (pattern-compile
# failure, driver-build failure, missing gen.h, ...). A block-level failure
# must fail its attached group checks too, not leave them silently
# unaccounted — the same "no vacuous pass" discipline as the base m/n cases
# right next to them.
record_case_group_fail() {
    local f="$1" i="$2" reason="$3"
    [ -z "${case_gspec[$i]:-}" ] && return 0
    local gentries gentry gslot gstart gend gpend
    IFS=';' read -ra gentries <<< "${case_gspec[$i]}"
    for gentry in "${gentries[@]}"; do
        [ -z "$gentry" ] && continue
        IFS=',' read -r gslot gstart gend gpend <<< "$gentry"
        record_fail "$f" "${case_line[$i]}" "group slot $gslot: $reason"
    done
}

# Compile and run the current pattern block (globals cur_file, cur_pattern,
# cur_pattern_line, cur_is_perr) against its accumulated cases (parallel
# arrays case_kind/case_line/case_subject/case_start/case_end/case_gspec/
# case_gucode -- the last holding a "gu" case's expected give-up word).
flush_block() {
    block_counter=$((block_counter + 1))
    local bdir="$WORKDIR/b$block_counter"
    mkdir -p "$bdir"

    # per-block compile options (the `flags` directive); an unsupported letter
    # is rejected at parse time, so this can only hold letters we map here
    local pflags=()
    [[ "$cur_flags" == *i* ]] && pflags+=(-i)

    # per-block enabled modules (the `features` directive, MOD-0.3c). The
    # SPEC is validated once per distinct list against a trivially-valid
    # pattern, because pcrec refuses an unknown module name with exit 1 and
    # a perr block would read that as its expected rejection — a typo'd
    # features line must be a loud harness failure, never a quiet pass.
    if [ -n "$cur_features" ]; then
        if [ -z "${features_seen[$cur_features]:-}" ]; then
            if "$PCREC" --features "$cur_features" -p rxfc -o "$bdir/featprobe.c" -- 'a' >/dev/null 2>&1; then
                features_seen[$cur_features]=ok
            else
                features_seen[$cur_features]=bad
            fi
        fi
        if [ "${features_seen[$cur_features]}" = "bad" ]; then
            local i
            for i in "${!case_kind[@]}"; do
                record_fail "$cur_file" "${case_line[$i]}" \
                    "HARNESS FAILURE: --features '$cur_features' is not a valid enabled-set spec"
            done
            return 0
        fi
        pflags+=(--features "$cur_features")
    fi

    # [DD-14 wave A commit 3] the `engine`/`budget` directives -- the
    # minimal route to a corpus case that can reach `--engine=vm` with a
    # tiny budget, so `gu` has something to assert against without
    # inventing a new construct. Same "per-block, validated at parse time"
    # shape as flags/features above.
    [ -n "$cur_engine" ] && pflags+=(--engine="$cur_engine")
    [ -n "$cur_stepbudget" ] && pflags+=(--step-budget="$cur_stepbudget")
    [ -n "$cur_framebudget" ] && pflags+=(--backtrack-frames="$cur_framebudget")
    # LAST, so a directive on the same axis wins — see the env-var block above.
    # shellcheck disable=SC2206
    [ -n "$RXTFLAGS" ] && pflags+=($RXTFLAGS)

    local pcrec_err
    # The budget is AXIS-AWARE (R23 V1): pcrec's own invocation used to carry a
    # bare hardcoded `timeout 60` that did not scale with the sanitizer axes,
    # which is the one compile a change to the compiler can actually slow down.
    # gen_timeout.sh derives it from the same flags everything else does, and
    # carries the measurement the numbers come from.
    pcrec_err="$("$TIMEOUT_BIN" "$(pcrec_timeout_secs)" "$PCREC" -p rx "${pflags[@]+"${pflags[@]}"}" -o "$bdir/gen.c" -- "$cur_pattern" 2>&1 >/dev/null)"
    local pcrec_rc=$?

    if [ "$cur_is_perr" = "1" ]; then
        # exit 1 = clean rejection with a diagnostic; anything else (0 =
        # accepted, >=124 = timeout, 139 = crash, ...) is a failure — a crash
        # must never satisfy a perr expectation (R1 review P-C1)
        if [ $pcrec_rc -eq 1 ]; then
            [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$cur_pattern_line: perr '$cur_pattern'"
            record_pass
        elif [ $pcrec_rc -eq 0 ]; then
            record_fail "$cur_file" "$cur_pattern_line" \
                "expected pattern to fail to compile (perr) but pcrec succeeded: '$cur_pattern'"
        else
            record_fail "$cur_file" "$cur_pattern_line" \
                "pcrec CRASHED or timed out (exit $pcrec_rc) instead of cleanly rejecting: '$cur_pattern'"
        fi
        return 0
    fi

    if [ $pcrec_rc -ne 0 ]; then
        if [ $pcrec_rc -ge 124 ]; then
            echo "$cur_file:$cur_pattern_line: HARNESS FAILURE: pcrec crashed or timed out (exit $pcrec_rc) on pattern '$cur_pattern'" >&2
        fi
        local key="$cur_file:$cur_pattern_line"
        contains_fail "$key" || compile_fail_set+=("$key")
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" \
                "pattern '$cur_pattern' failed to compile: $pcrec_err"
            record_case_group_fail "$cur_file" "$i" "pattern failed to compile"
        done
        return 0
    fi

    if [ ! -f "$bdir/gen.c" ] || [ ! -f "$bdir/gen.h" ]; then
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" \
                "pcrec exited 0 but did not produce gen.c/gen.h for pattern '$cur_pattern'"
            record_case_group_fail "$cur_file" "$i" "gen.c/gen.h not produced"
        done
        return 0
    fi

    local build_log build_rc
    # D45: the budget comes from tests/lib/gen_timeout.sh, not a number here.
    # It was a hardcoded 120 -- generous enough that the bounded-repeat
    # pathology (100+ minutes) would have tripped it, but only after two
    # minutes per case, and nothing else in the tree shared the number.
    gen_cc "$cur_pattern" "$CC" $GENCFLAGS -I"$bdir" -o "$bdir/t" "$SCRIPT_DIR/driver.c" "$bdir/gen.c"
    build_rc=$?
    build_log="$GEN_CC_LOG"
    if [ "$build_rc" -ne 0 ]; then
        echo "$cur_file:$cur_pattern_line: HARNESS FAILURE: $CC failed to compile generated code for pattern '$cur_pattern'" >&2
        echo "$build_log" >&2
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" "compile failure (see above)"
            record_case_group_fail "$cur_file" "$i" "compile failure (see above)"
        done
        return 0
    fi

    # [M4.5a] the artifact's DELIVERED capture-slot count, read straight from
    # the generated header — this is what makes a 'g' (LIVE) expectation on a
    # slot beyond it a HARD failure (population accounting) rather than a
    # silent skip, and what makes a 'gp' (pending-VM) expectation on such a
    # slot self-activate into a real check the moment RX_NCAPS grows to cover
    # it, with no corpus edit required.
    local artifact_ncaps
    artifact_ncaps="$(grep -oE '^#define RX_NCAPS [0-9]+' "$bdir/gen.h" | awk '{print $3}')"
    if [ -z "$artifact_ncaps" ]; then
        echo "$cur_file:$cur_pattern_line: HARNESS FAILURE: RX_NCAPS not found in generated gen.h for pattern '$cur_pattern'" >&2
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" "HARNESS FAILURE: RX_NCAPS not found in gen.h"
            record_case_group_fail "$cur_file" "$i" "RX_NCAPS not found in gen.h"
        done
        return 0
    fi

    local i
    for i in "${!case_kind[@]}"; do
        local kind="${case_kind[$i]}" line="${case_line[$i]}" subj="${case_subject[$i]}"
        local pos="${case_startpos[$i]}"
        local out expect trc rtag=""
        [ -n "${case_route[$i]:-}" ] && [ "${case_route[$i]}" != "default" ] \
            && rtag=" via <prefix>_search_in route ${case_route[$i]}"
        # The run budget comes from tests/lib/gen_timeout.sh (gen_run_secs),
        # not a number here — the old hardcoded 10 was the R23-V1 shape
        # again: axis-blind, so sanitizer cells shared the plain budget.
        # Coreutils `timeout` rather than the full gen_run/watchdog wrapper,
        # deliberately: this loop runs thousands of sub-millisecond cells,
        # and watchdog's fixed per-invocation cost belongs on per-pattern
        # and long-run sites, not here. $RUN_SECS is computed once above.
        # [DD-14.FB] The third argument is the ENTRY ROUTE (driver.c's own
        # header comment). It is "" for every case in a corpus that has no
        # `frames-buffer=` line and no RXTROUTE, and the driver treats an
        # empty route exactly as "default" — so an unchanged corpus runs the
        # unchanged call, and the route is visible in every failure message
        # below because "which entry answered" is the first thing a reader of
        # one of these failures needs to know.
        local route="${case_route[$i]:-}"
        out="$("$TIMEOUT_BIN" "$RUN_SECS" "$bdir/t" "$subj" "$pos" "$route")"
        trc=$?
        if [ $trc -eq 124 ]; then
            record_fail "$cur_file" "$line" \
                "test binary TIMED OUT (>${RUN_SECS}s, gen_run_secs; raise GENRUNTIMEOUT only with the measurement recorded) for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            record_case_group_fail "$cur_file" "$i" "test binary timed out"
            continue
        elif [ $trc -ge 126 ]; then
            record_fail "$cur_file" "$line" \
                "test binary crashed (exit $trc) for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            record_case_group_fail "$cur_file" "$i" "test binary crashed"
            continue
        elif [ $trc -eq 4 ]; then
            # [DD-14.FB] driver.c's ANCHORED-ENTRY CROSS-CHECK failed: on a
            # non-default route the driver also runs <prefix>_match_in and
            # <prefix>_match_caps_in against their un-suffixed siblings, and
            # they disagreed by more than the one divergence a smaller caller
            # buffer is allowed (a give-up, downward only). Its own arm, ahead
            # of the `gu` branch, so it applies to EVERY case kind -- a `gu`
            # cell whose anchored entries disagree is as broken as an `m` one,
            # and folding this into the give-up branch would have let exactly
            # those cells hide it. The detail is on the driver's stderr, which
            # run.sh does not capture per case, so the message says where to
            # look rather than pretending to quote it.
            record_fail "$cur_file" "$line" \
                "<prefix>_match_in / <prefix>_match_caps_in DISAGREE with their un-suffixed siblings (driver exit 4; re-run the case by hand to see the two values) for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            record_case_group_fail "$cur_file" "$i" "anchored _in entries disagree with their siblings"
            continue
        elif [ "$kind" = "gu" ]; then
            # [DD-14 wave A commit 3, §10.3] the ONE case kind that WANTS
            # exit 3: this directive asserts the search GAVE UP with a
            # specific typed code, so — unlike every other kind, which
            # treats exit 3 as an unconditional HARD failure two arms below
            # — a "gu" case scores exit 3 against its expected word instead
            # of failing on sight. A non-3 exit (0, 1, timeout, crash — the
            # latter two already handled above) means the search did NOT
            # give up when the block said it must, which is exactly the
            # FAILING-direction property the landing bar requires: a
            # `gu frames` block on a pattern that MATCHES fails HERE, not
            # silently passes as a match.
            local want="${case_gucode[$i]}"
            if [ $trc -eq 3 ] && [ "$out" = "$want" ]; then
                [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$line: gu $want '$cur_pattern' subject=\"$subj\" startpos=$pos"
                record_pass
            elif [ $trc -eq 3 ]; then
                record_fail "$cur_file" "$line" \
                    "expected 'gu $want' but the search gave up with '$out' for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            else
                record_fail "$cur_file" "$line" \
                    "expected 'gu $want' (a give-up) but the search did not give up — got '$out' (exit $trc) for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            fi
            continue
        elif [ $trc -eq 3 ]; then
            # [K21-class fix, 2026-08-15] driver.c's own give-up exit (see its
            # header comment): rx_search returned a negative VM budget-give-up
            # sentinel, not a match or a no-match. A HARD harness-level
            # failure, same shape as the timeout/crash branches above and for
            # the same reason — the give-up path must never be compared
            # against a `match`/`nomatch` expectation and silently score as
            # whichever one it happens not to equal. Reached for every case
            # kind EXCEPT "gu" (handled above) — that includes a give-up on
            # an ordinary m/n/ms/ns case, still a hard failure, never a
            # silent pass. [DD-14 wave A] the `engine`/`budget` directives
            # below are what let a corpus case reach this path at all.
            record_fail "$cur_file" "$line" \
                "test binary GAVE UP ($out — VM budget exhausted) for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            record_case_group_fail "$cur_file" "$i" "test binary gave up ($out)"
            continue
        fi
        local base_ok=0
        if [ "$kind" = "m" ]; then
            expect="match ${case_start[$i]} ${case_end[$i]}"
            # [M4.5a fix, R-post-merge] compare only the WHOLE-MATCH pair
            # (the first two numbers after 'match'), not the whole line.
            # driver.c prints one pair per RX_NCAPS slot (this file's own
            # design, for the g/gp checks below to consume) — a byte-for-byte
            # whole-line compare against "match <start> <end>" only ever held
            # while RX_NCAPS was 1 (this lane's own DFA-only test
            # environment) and breaks the instant an artifact delivers real
            # group slots (RX_NCAPS > 1, [M4.5]'s VM). This is a PARSED-FIELD
            # compare, not a substring/prefix match: 'match' vs 'nomatch',
            # a malformed/short line, or a wrong whole-match pair all still
            # fail loudly below — only extra TRAILING group pairs are now
            # ignored by this specific check (the g/gp checks verify those).
            local outfields0
            read -ra outfields0 <<< "$out"
            if [ "${outfields0[0]:-}" = "match" ] && [ "${#outfields0[@]}" -ge 3 ] \
                && [ "${outfields0[1]}" = "${case_start[$i]}" ] \
                && [ "${outfields0[2]}" = "${case_end[$i]}" ]; then
                [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$line: '$cur_pattern' subject=\"$subj\" startpos=$pos"
                record_pass
                base_ok=1
            else
                record_fail "$cur_file" "$line" \
                    "expected '$expect' got '$out' for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            fi
        else
            expect="nomatch"
            if [ "$out" = "$expect" ]; then
                [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$line: '$cur_pattern' subject=\"$subj\" startpos=$pos"
                record_pass
                base_ok=1
            else
                record_fail "$cur_file" "$line" \
                    "expected '$expect' got '$out' for pattern '$cur_pattern' subject \"$subj\" startpos $pos$rtag"
            fi
        fi

        # [M4.5a] capture-group expectations ('g'/'gp' lines) attached to
        # this case. Only 'm'/'ms' cases can carry them (enforced at parse
        # time — an n/ns case's case_gspec is always empty).
        if [ -n "${case_gspec[$i]:-}" ]; then
            local gentries gentry gslot gstart gend gpend
            IFS=';' read -ra gentries <<< "${case_gspec[$i]}"
            for gentry in "${gentries[@]}"; do
                [ -z "$gentry" ] && continue
                IFS=',' read -r gslot gstart gend gpend <<< "$gentry"
                if [ "$gslot" -ge "$artifact_ncaps" ]; then
                    if [ "$gpend" = "1" ]; then
                        total_pending=$((total_pending + 1))
                        [ "$VERBOSE" = "1" ] && echo "PENDING-VM $cur_file:$line: group slot $gslot (artifact RX_NCAPS=$artifact_ncaps) for pattern '$cur_pattern' subject \"$subj\""
                    else
                        record_fail "$cur_file" "$line" \
                            "group slot $gslot claimed with 'g' (LIVE) but artifact's RX_NCAPS=$artifact_ncaps does not deliver it — use 'gp' (pending-VM) for a slot beyond today's DFA-only artifacts"
                    fi
                    continue
                fi
                if [ "$base_ok" != "1" ]; then
                    record_fail "$cur_file" "$line" \
                        "group slot $gslot: cannot verify, base match assertion failed for pattern '$cur_pattern' subject \"$subj\""
                    continue
                fi
                local outfields fi0 fi1 got_s got_e
                read -ra outfields <<< "$out"
                fi0=$((1 + 2 * gslot))
                fi1=$((2 + 2 * gslot))
                got_s="${outfields[$fi0]:-}"
                got_e="${outfields[$fi1]:-}"
                if [ "$got_s" = "$gstart" ] && [ "$got_e" = "$gend" ]; then
                    [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$line: group slot $gslot ($gstart,$gend) for pattern '$cur_pattern' subject \"$subj\""
                    record_pass
                else
                    record_fail "$cur_file" "$line" \
                        "group slot $gslot: expected ($gstart,$gend) got (${got_s:-?},${got_e:-?}) for pattern '$cur_pattern' subject \"$subj\""
                fi
            done
        fi
    done
}

# ---- parse and run each file ----------------------------------------------

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "run.sh: file not found: $file" >&2
        continue
    fi
    cur_file="$file"
    cur_pattern=""
    cur_pattern_line=0
    cur_is_perr=0
    cur_flags=""
    cur_features=""
    cur_engine=""
    cur_stepbudget=""
    cur_framebudget=""
    cur_route="$RXTROUTE"
    case_kind=(); case_line=(); case_subject=(); case_start=(); case_end=(); case_startpos=()
    case_route=()
    have_block=0
    blocks_in_file=0

    lineno=0
    while IFS= read -r line || [ -n "$line" ]; do
        lineno=$((lineno + 1))
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ ^# ]] && continue

        if [[ "$line" =~ ^pattern\ (.*)$ ]]; then
            [ "$have_block" = "1" ] && flush_block
            blocks_in_file=$((blocks_in_file + 1))
            cur_pattern="${BASH_REMATCH[1]}"
            cur_pattern_line=$lineno
            cur_is_perr=0
            cur_flags=""
            cur_features=""
            cur_engine=""
            cur_stepbudget=""
            cur_framebudget=""
            # [DD-14.FB] the route resets with the block, like every other
            # directive here — and resets to RXTROUTE, not to "default", so
            # the env axis is a floor a block can raise rather than a setting
            # the first `pattern` line silently discards.
            cur_route="$RXTROUTE"
            case_kind=(); case_line=(); case_subject=(); case_start=(); case_end=(); case_startpos=(); case_gspec=(); case_gucode=(); case_route=()
            have_block=1
        elif [[ "$line" =~ ^flags[[:space:]]+([a-zA-Z]+)[[:space:]]*$ ]]; then
            # per-block compile options. Only `i` (case-insensitive, OS-1) is
            # defined; an unknown letter is a HARD error rather than a silent
            # no-op, because a silently-dropped flag would compile the wrong
            # automaton and the block's expectations would then be verified
            # against something nobody asked for.
            # capture BEFORE any further [[ =~ ]] — that would clobber
            # BASH_REMATCH out from under us
            flag_letters="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'flags' line before any pattern block"
            elif [ "$flag_letters" != "i" ]; then
                record_fail "$file" "$lineno" \
                    "unknown flag letter(s) '$flag_letters' (only 'i' is defined)"
            else
                cur_flags="$flag_letters"
            fi
        elif [[ "$line" =~ ^features[[:space:]]+([a-zA-Z0-9,_-]+)[[:space:]]*$ ]]; then
            # captured BEFORE any further [[ =~ ]] clobbers BASH_REMATCH
            feat_list="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'features' line before any pattern block"
            else
                cur_features="$feat_list"
            fi
        elif [[ "$line" =~ ^engine[[:space:]]+vm[[:space:]]*$ ]]; then
            # [DD-14 wave A commit 3] the minimal ROUTE §10.3 asks for: a
            # block-scoped directive letting a case reach --engine=vm, the
            # same shape as `flags`/`features` (per-block, does not carry to
            # the next block, unknown value is a hard error). Only "vm" is
            # defined -- there is no `--engine=dfa` cell this wave needs.
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'engine' line before any pattern block"
            else
                cur_engine="vm"
            fi
        elif [[ "$line" =~ ^engine[[:space:]] ]]; then
            record_fail "$file" "$lineno" \
                "unknown 'engine' value (only 'vm' is defined)"
        elif [[ "$line" =~ ^budget[[:space:]]+steps=([0-9]+)[[:space:]]*$ ]]; then
            # [DD-14 wave A commit 3] the minimal BUDGET knob §10.3 asks
            # for, mirroring tests/vm/run_vm_tests.sh's own `--step-budget=N`
            # / `--backtrack-frames=N` cells (that file's `build()` calls the
            # SAME two pcrec flags this line and the next route into pflags)
            # -- this is the .rxt corpus's first way to reach either one.
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'budget' line before any pattern block"
            else
                cur_stepbudget="${BASH_REMATCH[1]}"
            fi
        elif [[ "$line" =~ ^budget[[:space:]]+frames=([0-9]+)[[:space:]]*$ ]]; then
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'budget' line before any pattern block"
            else
                cur_framebudget="${BASH_REMATCH[1]}"
            fi
        elif [[ "$line" =~ ^budget[[:space:]] ]]; then
            record_fail "$file" "$lineno" \
                "unknown 'budget' spec (only 'steps=<n>' and 'frames=<n>' are defined)"
        elif [[ "$line" =~ ^frames-buffer=(.*)$ ]]; then
            # [DD-14.FB] (D71 item 2, spec §10) THE ENTRY ROUTE, and it is
            # POSITIONAL WITHIN THE BLOCK rather than block-wide: it applies to
            # the cases BELOW it until another one changes it. That is what
            # lets one block hold the pair the design asks for -- the same
            # pattern and the same subject giving `gu frames` through
            # `<prefix>_search` and `m` through `<prefix>_search_in` with a
            # bigger buffer -- with ONE compile of ONE artifact, so the two
            # cells differ in the entry called and in nothing else. A
            # block-scoped directive could not express that pair at all, and a
            # per-case-kind spelling (`mb`, `nb`, `gub`, ...) would multiply
            # the corpus's case kinds by the number of routes, which is the
            # parallel-mechanism shape the house rule forbids.
            #
            # `budget frames=N` is NOT this and does not overlap it: that flag
            # sizes the ARTIFACT (it is `--backtrack-frames=N`, a compile-time
            # capacity), where this sizes the CALL. A block can carry both.
            route_spec="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'frames-buffer=' line before any pattern block"
            elif ! valid_route "$route_spec"; then
                record_fail "$file" "$lineno" \
                    "unknown 'frames-buffer=' route '$route_spec' (want default, null, <n>, or <frames>,<trail>)"
            else
                cur_route="$route_spec"
            fi
        elif [[ "$line" =~ ^perr[[:space:]]*$ ]]; then
            cur_is_perr=1
        elif [[ "$line" =~ ^m[[:space:]]+\"(.*)\"[[:space:]]+([0-9]+)[[:space:]]+([0-9]+)[[:space:]]*$ ]]; then
            case_kind+=("m")
            case_line+=("$lineno")
            case_subject+=("${BASH_REMATCH[1]}")
            case_start+=("${BASH_REMATCH[2]}")
            case_end+=("${BASH_REMATCH[3]}")
            case_startpos+=("0")
            case_gspec+=("")
            case_gucode+=("")
            case_route+=("$cur_route")
        elif [[ "$line" =~ ^n[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            case_kind+=("n")
            case_line+=("$lineno")
            case_subject+=("${BASH_REMATCH[1]}")
            case_start+=("")
            case_end+=("")
            case_startpos+=("0")
            case_gspec+=("")
            case_gucode+=("")
            case_route+=("$cur_route")
        elif [[ "$line" =~ ^ms[[:space:]]+([0-9]+)[[:space:]]+\"(.*)\"[[:space:]]+([0-9]+)[[:space:]]+([0-9]+)[[:space:]]*$ ]]; then
            case_kind+=("m")
            case_line+=("$lineno")
            case_startpos+=("${BASH_REMATCH[1]}")
            case_subject+=("${BASH_REMATCH[2]}")
            case_start+=("${BASH_REMATCH[3]}")
            case_end+=("${BASH_REMATCH[4]}")
            case_gspec+=("")
            case_gucode+=("")
            case_route+=("$cur_route")
        elif [[ "$line" =~ ^ns[[:space:]]+([0-9]+)[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            case_kind+=("n")
            case_line+=("$lineno")
            case_startpos+=("${BASH_REMATCH[1]}")
            case_subject+=("${BASH_REMATCH[2]}")
            case_start+=("")
            case_end+=("")
            case_gspec+=("")
            case_gucode+=("")
            case_route+=("$cur_route")
        elif [[ "$line" =~ ^gu[[:space:]]+internal([[:space:]]|$) ]]; then
            # [DD-14 wave A commit 3] refused BY NAME, not by falling through
            # to the unparseable-line catch-all below: nothing may EXPECT an
            # internal error. PCREC_ERR_INTERNAL is the artifact catching its
            # OWN analysis/emission bug, never a planned outcome a corpus
            # block gets to rely on -- that is what tests/mech's sabotage
            # rows are for (S136 exercises this exact code today). A clear,
            # named refusal here is the same discipline `flags`'s unknown-
            # letter check already applies two elif arms up.
            record_fail "$file" "$lineno" \
                "'gu internal' is refused: PCREC_ERR_INTERNAL is the artifact catching its own inconsistency, never a planned outcome a .rxt block may EXPECT (docs/testing.md's 'gu' directive; see tests/mech/sabotages/S136 for how this code IS exercised)"
        elif [[ "$line" =~ ^gu[[:space:]]+(steps|frames|work|recurse)[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            # [DD-14 wave A commit 3, §10.3] asserts the search GAVE UP with
            # this TYPED code, scored against driver.c's exit 3 + printed
            # word instead of the default HARD failure that branch below
            # gives every other case kind. Same shape as m/n: one directive
            # line naming a subject, startpos fixed at 0 (no `gus` variant --
            # nothing in this wave's landing bar needs one, and D42.3's own
            # "getting the partition wrong costs a renumber, not more" spirit
            # says add the knob when a real cell needs it, not speculatively).
            case_kind+=("gu")
            case_line+=("$lineno")
            case_subject+=("${BASH_REMATCH[2]}")
            case_start+=("")
            case_end+=("")
            case_startpos+=("0")
            case_gspec+=("")
            case_gucode+=("${BASH_REMATCH[1]}")
            case_route+=("$cur_route")
        elif [[ "$line" =~ ^(gp|g)[[:space:]]+([0-9]+)[[:space:]]+(-1|[0-9]+)[[:space:]]+(-1|[0-9]+)[[:space:]]*$ ]]; then
            # [M4.5a] capture-group expectation attached to the MOST RECENT
            # m/ms case in this block. 'g' = LIVE (must be checkable now: a
            # slot beyond the artifact's RX_NCAPS is a hard failure, never a
            # silent skip — population accounting). 'gp' = PENDING-VM (a slot
            # beyond RX_NCAPS is counted separately, not pass/fail; once
            # RX_NCAPS grows to cover it the line self-activates into a real
            # check with no corpus edit). RX_UNSET is spelled '-1 -1' (both
            # slots), matching the ABI's own convention exactly.
            gkind="${BASH_REMATCH[1]}"
            gslot="${BASH_REMATCH[2]}"
            gstart="${BASH_REMATCH[3]}"
            gend="${BASH_REMATCH[4]}"
            if { [ "$gstart" = "-1" ] && [ "$gend" != "-1" ]; } || { [ "$gstart" != "-1" ] && [ "$gend" = "-1" ]; }; then
                record_fail "$file" "$lineno" \
                    "'$gkind' line: RX_UNSET must be '-1 -1' in BOTH slots, not one (got '$gstart $gend')"
            elif [ "$have_block" != "1" ] || [ "${#case_kind[@]}" -eq 0 ] || [ "${case_kind[$((${#case_kind[@]} - 1))]}" != "m" ]; then
                record_fail "$file" "$lineno" \
                    "'$gkind' line must immediately follow (or otherwise attach to) an 'm'/'ms' case in the same block — no such case precedes it"
            else
                last_idx=$((${#case_kind[@]} - 1))
                gpend=0
                [ "$gkind" = "gp" ] && gpend=1
                case_gspec[$last_idx]="${case_gspec[$last_idx]}${gslot},${gstart},${gend},${gpend};"
            fi
        else
            # unparseable non-blank/non-comment lines are hard errors: a
            # corrupted corpus must not silently degrade to zero coverage
            # (R1 review P-C2)
            record_fail "$file" "$lineno" "unparseable .rxt line (hard error): $line"
        fi
    done < "$file"

    [ "$have_block" = "1" ] && flush_block
    if [ "$blocks_in_file" -eq 0 ]; then
        record_fail "$file" 0 "no pattern blocks parsed from file (P-C2 floor)"
    fi
done

# ---- summary ----------------------------------------------------------

echo
echo "== Summary =="
echo "cases passed: $total_pass"
echo "cases failed: $total_fail"
if [ ${#file_fail_count[@]} -gt 0 ]; then
    echo "failures by file:"
    for f in "${!file_fail_count[@]}"; do
        echo "  $f: ${file_fail_count[$f]}"
    done | sort
fi
echo "pattern-compile failures (distinct): ${#compile_fail_set[@]}"
echo "group cases pending-vm: $total_pending"

if [ $((total_pass + total_fail)) -eq 0 ]; then
    echo "run.sh: NO CASES RUN — corpus missing or fully unparseable" >&2
    exit 1
fi
[ "$total_fail" -eq 0 ] && exit 0
exit 1
