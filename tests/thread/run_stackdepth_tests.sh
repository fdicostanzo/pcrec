#!/usr/bin/env bash
# tests/thread/run_stackdepth_tests.sh — [TS-4] for the EMITTED MATCHER, and
# [DD-14.FB]'s remedy, on a musl-default 128 KB thread stack.
#
# WHY THIS IS A SEPARATE SCRIPT FROM run_thread_tests.sh. That suite asks
# whether concurrent calls RACE and answers under ThreadSanitizer. This asks
# whether ONE call FITS, and TSan is exactly the wrong instrument for it: it
# changes the stack a call needs, so a stack-fit question asked under it is a
# question about TSan. No sanitizer here, deliberately.
#
# THE PROPERTY. A generated matcher's run state is a LOCAL of whichever entry
# was called (spec §5.2: no allocation, no match-data object), so the resume
# stack and trail live on the C stack of the function that declared them.
# MEASURED on this box, `^(a(?1)?b)$ --features recursion --engine=vm`: that
# storage is ~131.2 KB, and musl's default thread stack is 131,072 B. It does
# not fit.
#
# [OPT-1], 2026-08-25: WHICH FUNCTION DECLARES IT MOVED, and this script moved
# with it. `<prefix>_search` now runs on a page-sized fast tier (3,184 B
# MEASURED) and calls a `noinline` `<prefix>_search_deep` that owns the stamped
# default, only on a PCREC_ERR_FRAMES give-up. So the quantity that decides
# whether a call fits is the DEEP PATH — entry + deep — and `deep_path_frame`
# below computes it, reproducing the old number exactly on a single-tier
# artifact where there is no `_deep` row.
#
# FOUR ARMS ([OPT-1] added D). C is what makes A and B mean anything; D is
# what makes A's scope honest:
#
#   A  DEFAULT ENTRY, CALL-BEARING — expected to die of SIGSEGV. This is K33
#      (docs/dev/known_issues.md): a live defect against spec §5.3's
#      concurrency contract, which promises that any number of threads may
#      call an artifact's entry points concurrently given their own caps
#      buffers. For this artifact class on a small-stack thread that promise
#      is false, and the caps buffer has nothing to do with it. D73 KEEPS the
#      stamped 2048/3072 that causes it, on the reasoning that the caller
#      buffer is the path around it — so this arm is a PINNED KNOWN STATE, not
#      a pass. It is reported as KNOWN and, if it ever stops dying, this script
#      FAILS: the record would then be describing something that is no longer
#      true, and a check that quietly went green on a fixed defect is how a
#      known-issues file rots.
#
#   D  [OPT-1] DEFAULT ENTRY AGAIN, SAME ARTIFACT, SAME THREAD, a 2-BYTE
#      SUBJECT — must MATCH. Before the tiered entry this died exactly as A
#      does, because the stamped storage sat on the entry's frame whether the
#      subject needed it or not. It now runs entirely on the page-sized fast
#      tier. A and D differ in the SUBJECT and nothing else, which is what
#      makes "K33 is about DEPTH now" a measurement rather than a claim.
#
#   B  `_in` ENTRY, SAME ARTIFACT, SAME SUBJECT, SAME 128 KB THREAD, storage
#      from the heap — must MATCH. This is the remedy, and the reason arm A is
#      a documented limitation with a way out rather than an open wound.
#
#   C  THE CONTROL, and it is a CAUSAL one rather than a "the harness works"
#      one. `(a|aa)+b` is unbounded-but-CALL-FREE: design §3 MEASURES its
#      entry at ~98 KB, because [DD-14] waves B+C added `call_ret`/`call_top`
#      to every frame and 2048 x 16 B is exactly what pushes the call-bearing
#      artifact past 128 KB. Same driver, same thread, same subject, smaller
#      frame — and it must NOT die. Without this arm, "arm A crashed" would be
#      consistent with a driver bug, a pthread misuse, or any stack cost at
#      all; with it, the difference between crashing and not is the FRAME SIZE
#      and nothing else.
#
# The frame sizes are also read directly off `gcc -fstack-usage` and compared
# against the thread stack, so the script states its cause rather than
# inferring it from a signal number.
#
# Usage: bash tests/thread/run_stackdepth_tests.sh
# Env:   PCREC (default <root>/build/pcrec), CC (default gcc), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O2 -std=gnu11 -Wall -Wextra -Werror}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_stackdepth_tests.sh: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0; known=0; skipped=0
ok()    { echo "PASS: $*"; pass=$((pass + 1)); }
bad()   { echo "FAIL: $*"; fail=$((fail + 1)); }
pin()   { echo "KNOWN: $*"; known=$((known + 1)); }
note()  { echo "NOTE: $*"; skipped=$((skipped + 1)); }

# PREFLIGHT: this suite needs pthreads, and a box without them should get a
# LOUD SKIP rather than a hard failure -- the same shape run_thread_tests.sh
# uses for -fsanitize=thread and run_frame_buffer.sh uses for ASan. A missing
# toolchain feature is not a defect in the artifact under test, and reporting
# it as one trains a reader to ignore this suite's reds.
printf '#include <pthread.h>\nstatic void *f(void *p){return p;}\nint main(void){pthread_t t; pthread_create(&t,0,f,0); pthread_join(t,0); return 0;}\n' \
    > "$WORKDIR/pthread_probe.c"
# shellcheck disable=SC2086
if ! $CC -O0 -o "$WORKDIR/pthread_probe" "$WORKDIR/pthread_probe.c" -lpthread >/dev/null 2>&1; then
    note "[TS-4] SKIPPED LOUDLY: $CC cannot build a -lpthread program on this box, so the 128 KB-thread arms cannot run. Nothing about K33 or about <prefix>_search_in's stack frame is claimed by this run"
    echo
    echo "== Summary =="
    echo "checks passed: 0"
    echo "checks failed: 0"
    echo "known states pinned: 0"
    echo "sections skipped: $skipped"
    exit 0
fi

THREAD_STACK=131072   # must match TS4_STACK_BYTES in ts4_driver.c

# build <name> <pattern> <pcrec flags...>
build() {
    local name="$1" pat="$2"; shift 2
    local d="$WORKDIR/$name"
    mkdir -p "$d"
    pcrec_run "$PCREC" -p rx --engine=vm "$@" -o "$d/gen.c" -- "$pat" >/dev/null 2>&1 || return 1
    # shellcheck disable=SC2086
    (cd "$d" && $CC $GENCFLAGS -fstack-usage -I"$d" -o "$d/ts4" \
        "$SCRIPT_DIR/ts4_driver.c" "$d/gen.c" -lpthread) >/dev/null 2>&1 || return 1
    return 0
}

# frame_of <name> <function> — one function's own stack frame, in bytes, read
# off `gcc -fstack-usage`. Its rows are TAB-separated
# `file:line:col:function`, `bytes`, `qualifier`, and with several sources on
# one command line gcc names the files `<output>-<source>.su`, so the row is
# selected by its FUNCTION field rather than by the file it landed in. The
# match is anchored at the end of field 1 so `rx_search` cannot pick up
# `rx_search_run`, `rx_search_in` or `rx_search_deep`, which are the whole
# point of the comparisons this feeds.
frame_of() {
    local d="$WORKDIR/$1"
    awk -F'\t' -v f=":$2\$" '$1 ~ f {print $2}' "$d"/*.su 2>/dev/null | head -1
}

# entry_frame <name> — <prefix>_search's own frame. Since [OPT-1] this is the
# FAST TIER's frame on a tiered artifact and is under one page; it is no longer
# the number that decides whether a deep match fits a thread.
entry_frame() { frame_of "$1" rx_search; }

# deep_path_frame <name> — [OPT-1]: the stack a call that goes DEEP actually
# needs, which is what arms A and C are about and what `entry_frame` alone used
# to be.
#
# WHY THE CHECK MOVED RATHER THAN BEING RE-TUNED. Before [OPT-1] the stamped
# default storage was a local of `<prefix>_search`, so its frame WAS the deep
# path and this script read it directly. The tiered entry moves that storage to
# a `noinline` `<prefix>_search_deep` the entry CALLS, so the deep path is now
# two frames and reading either alone understates it. Summing them is the
# GENERAL form and reproduces the old number exactly on a single-tier artifact,
# where there is no `_deep` row and the sum is the entry's own frame — so this
# is one rule for both shapes, not a tiered special case beside the old one.
deep_path_frame() {
    local e d
    e="$(entry_frame "$1")"
    d="$(frame_of "$1" rx_search_deep)"
    [ -n "$e" ] || return 1
    echo $((e + ${d:-0}))
}

if ! build callbearing '^(a(?1)?b)$' --features recursion; then
    bad "[TS-4] could not build the call-bearing fixture '^(a(?1)?b)\$' — every arm below is unmeasured"
elif ! build callfree '(a|aa)+b'; then
    bad "[TS-4] could not build the call-free control fixture '(a|aa)+b' — arm A's cause would be unisolated, so no arm is reported"
else
    cb_frame="$(deep_path_frame callbearing)"
    cf_frame="$(deep_path_frame callfree)"
    cb_entry="$(entry_frame callbearing)"

    # ---- the CAUSE, stated rather than inferred --------------------------
    if [ -z "$cb_frame" ] || [ -z "$cf_frame" ]; then
        bad "[TS-4] gcc -fstack-usage produced no rx_search row (call-bearing='$cb_frame' call-free='$cf_frame') — this script cannot say WHY arm A dies, so it does not get to claim it knows"
    elif [ "$cb_frame" -le "$THREAD_STACK" ]; then
        bad "[TS-4] the call-bearing artifact's DEEP PATH is $cb_frame B, which FITS in a $THREAD_STACK B thread stack. K33's arithmetic no longer holds on this box/compiler; arm A below is measuring something else and docs/dev/known_issues.md K33 needs re-measuring"
    elif [ "$cf_frame" -gt "$THREAD_STACK" ]; then
        bad "[TS-4] the CALL-FREE control's deep path is $cf_frame B, also over the $THREAD_STACK B thread stack — arm C cannot isolate the cause, because both artifacts would be over the ceiling for the same reason"
    else
        ok "[TS-4] the cause is stated: the call-bearing artifact's DEEP PATH is $cb_frame B against a $THREAD_STACK B thread stack (over by $((cb_frame - THREAD_STACK)) B), while the call-free control's is $cf_frame B and fits — so arms A and C differ in FRAME SIZE and nothing else"
    fi

    # ---- [OPT-1] the SHALLOW path, which is what arm D is about ----------
    # The entry's own frame is the stack a call that does NOT go deep needs.
    # Stated here beside the deep number so the two are read together: the same
    # artifact needs $cb_entry B for a shallow subject and $cb_frame B for a
    # deep one, which is exactly why arms A and D now differ.
    if [ -z "$cb_entry" ]; then
        bad "[TS-4/OPT-1] gcc -fstack-usage produced no rx_search row for the call-bearing artifact — arm D's cause cannot be stated"
    elif [ "$cb_entry" -lt 4096 ]; then
        ok "[TS-4/OPT-1] the call-bearing entry's OWN frame is $cb_entry B, inside one 4096 B page — so a subject that stays on the fast tier needs $cb_entry B of thread stack where the deep path needs $cb_frame B, and arm D below must therefore MATCH where arm A dies"
    else
        bad "[TS-4/OPT-1] the call-bearing entry's own frame is $cb_entry B, NOT inside one 4096 B page. Either [OPT-1]'s tiered entry is not in this build or its budget no longer holds; arm D is then measuring something else and docs/spec/match_api.md §5.3's re-measured paragraph is out of date"
    fi

    # ---- arm C first: the control, so a broken harness is caught before ---
    # ---- a crash is read as a finding ------------------------------------
    c_out="$("$TIMEOUT_BIN" 60 "$WORKDIR/callfree/ts4" default 2>&1)"; c_rc=$?
    if [ "$c_rc" -eq 0 ] && [ "${c_out#callfree}" != "$c_out" ] || [ "$c_rc" -eq 0 ]; then
        if printf '%s' "$c_out" | grep -q 'rc=1'; then
            ok "[TS-4] arm C (control): the call-FREE unbounded artifact's DEFAULT entry runs to a match on the same $THREAD_STACK B thread — the driver, the thread and the subject are all sound, so a crash in arm A is about the artifact"
        else
            bad "[TS-4] arm C (control): the call-free artifact ran but did not match ('$c_out'). The control must MATCH; anything else leaves arm A's crash unattributed"
        fi
    else
        bad "[TS-4] arm C (control) exited $c_rc ('$c_out'). The call-free artifact must survive this thread — if it does not, this script cannot attribute arm A's crash to the call-bearing frame and reports nothing about K33"
    fi

    # ---- arm A: the K33 regression, PINNED --------------------------------
    # K33 IS A STACK OVERFLOW, SO THE SIGNAL IS PART OF THE CLAIM. Accepting
    # death by ANY signal would let this arm stay green on an abort, a bus
    # error or a kill from outside and still report "K33 confirmed" -- three
    # different events wearing one verdict, which is the mislabelled-evidence
    # shape DD-2 exists to prevent. A stack overflow on this platform is
    # SIGSEGV (11), i.e. exit 139; anything else is named and refused.
    a_out="$("$TIMEOUT_BIN" 60 "$WORKDIR/callbearing/ts4" default 2>&1)"; a_rc=$?
    if [ "$a_rc" -eq 139 ]; then
        pin "[TS-4] arm A (K33, EXPECTED): the call-bearing artifact's DEFAULT entry dies of SIGSEGV (exit 139) on a $THREAD_STACK B thread with a 684-byte subject it would otherwise MATCH. [OPT-1]: it now dies INSIDE the deep tier — the subject is deep enough to exhaust the fast tier, so the entry escalates into the $cb_frame B deep path and that is what does not fit. This is docs/dev/known_issues.md K33, narrowed but open, and D73 keeps the stamped default that causes it; arm B is the remedy and arm D is the narrowing. Pinned, not passed"
    elif [ "$a_rc" -gt 128 ] && [ "$a_rc" -ne 124 ]; then
        bad "[TS-4] arm A died of SIG$(kill -l "$((a_rc - 128))" 2>/dev/null || echo "?$((a_rc - 128))") (exit $a_rc), NOT SIGSEGV. K33 is a stack overflow and a stack overflow is SIGSEGV here; a different signal is a different event and must not be reported as K33 reproducing. Output: '$a_out'"
    elif [ "$a_rc" -eq 124 ]; then
        bad "[TS-4] arm A TIMED OUT rather than dying or returning — neither the pinned state nor a fix, and the run says nothing about K33"
    else
        bad "[TS-4] arm A did NOT die (exit $a_rc, '$a_out'). K33 is pinned as a LIVE defect here and in docs/dev/known_issues.md; if the default entry now survives a $THREAD_STACK B thread on a DEEP subject, that record is out of date and both it and this arm must be updated deliberately — a check that silently goes green on a closed defect is how a known-issues file rots. NOTE for whoever reads this next: [OPT-1] already narrowed K33 once, and the narrowing is arm D. A pass HERE would be a further narrowing (the deep tier fitting) and needs its own measurement, not an edit to this line"
    fi

    # ---- arm B: the remedy ------------------------------------------------
    b_out="$("$TIMEOUT_BIN" 60 "$WORKDIR/callbearing/ts4" buffered 2>&1)"; b_rc=$?
    if [ "$b_rc" -eq 0 ] && printf '%s' "$b_out" | grep -q 'rc=1'; then
        ok "[TS-4] arm B ([DD-14.FB]): the SAME artifact, the SAME subject and the SAME $THREAD_STACK B thread MATCH through <prefix>_search_in with heap storage ('$b_out') — the caller buffer takes the arrays off the C stack, which is what D71 item 2 asked for"
    else
        bad "[TS-4] arm B: <prefix>_search_in did not match on the 128 KB thread (exit $b_rc, '$b_out'). The remedy is broken, which makes arm A an open defect rather than a documented limitation"
    fi

    # ---- arm D: [OPT-1]'s NARROWING of K33 --------------------------------
    # SAME artifact, SAME entry, SAME thread as arm A. Only the SUBJECT differs
    # — "ab" instead of 684 bytes — so a difference in outcome between A and D
    # is a statement about DEPTH and nothing else.
    #
    # Before [OPT-1] this arm would have died exactly as arm A does, and spec
    # §5.3 said so in those words ("faults on any subject, a 2-byte one
    # included"). It is a PASS and not a pinned state, because unlike arm A
    # nothing here is a known defect: this is the shipped, intended behaviour
    # of the tiered entry, and if it stops holding the optimization is gone.
    d_out="$("$TIMEOUT_BIN" 60 "$WORKDIR/callbearing/ts4" shallow 2>&1)"; d_rc=$?
    if [ "$d_rc" -eq 0 ] && printf '%s' "$d_out" | grep -q 'rc=1'; then
        ok "[TS-4] arm D ([OPT-1]): the SAME artifact and the SAME DEFAULT entry that dies in arm A MATCH a 2-byte subject on the same $THREAD_STACK B thread ('$d_out') — the fast tier holds it, so the deep path is never entered. This is K33 narrowed from 'any subject' to 'a subject deep enough to escalate'"
    elif [ "$d_rc" -eq 139 ]; then
        bad "[TS-4] arm D: the default entry still SIGSEGVs on a 2-byte subject. [OPT-1]'s tiered entry is not doing what docs/spec/match_api.md §5.3 and docs/dev/known_issues.md K33 now say it does — the frame check above passed, so the storage moved and something else on the deep path is still being reached on a shallow call"
    else
        bad "[TS-4] arm D exited $d_rc ('$d_out') — neither a match nor the old SIGSEGV, so it says nothing about the narrowing either way"
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "known states pinned: $known"
echo "sections skipped: $skipped"
if [ $((pass + fail + known)) -eq 0 ]; then
    echo "run_stackdepth_tests.sh: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
