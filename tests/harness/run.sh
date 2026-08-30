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
#   RXTDUMP    ([CHK-2], tests/axes/run_axes.sh) path to a file that
#              receives ONE LINE PER CASE OUTCOME. Two producers: every case
#              whose test binary actually ran (every case that reaches the
#              `out=` assignment below — match/nomatch/gu/timeout/crash all
#              produce a line), AND — since the manager's 2026-08-26
#              finding — every case whose BLOCK failed to COMPILE (pcrec
#              itself refused the pattern), which now produces a line too,
#              with a sentinel `trc` field of `REFUSED` and `<out>` carrying
#              pcrec's own diagnostic text (flattened to one line). Without
#              this second producer, a consumer had NO way to tell "pcrec
#              refused this pattern, here is why" apart from "this case's
#              key is silently absent" — indistinguishable from any other
#              cause of absence, which is exactly what let a documented,
#              expected refusal population (e.g. -fno-counter's replication
#              cap) read as an undifferentiated, unexplained LOST count. A
#              case whose block fails to LINK (gcc/driver build failure)
#              still produces NO line — that failure is per-CC-invocation,
#              not per-pattern, and is not this hook's concern. Empty (the
#              default) means no dump, so a plain run
#              is byte-for-byte unchanged; this is the "ONE env var in the
#              house style" tests/axes/CLAUDE.md's brief asked for rather
#              than a new directive, the same shape RXTFLAGS/RXTROUTE took.
#              Format, tab-separated: `<file>\t<line>\t<kind>\t<route>\t
#              <trc>\t<out>` where <out> has its own embedded tabs/newlines
#              impossible by construction (subjects and driver output are
#              single .rxt lines with C-style backslash escapes, never raw
#              control bytes — tests/harness/driver.c's decode()). `<out>`
#              for a REFUSED line is the one exception (pcrec's own
#              diagnostic, not driver output) and is flattened for exactly
#              this reason. The KEY a
#              consumer diffs two dumps by is `<file>\t<line>`: it is unique
#              within one run because .rxt cases are one per source line, and
#              a case that compiled under one RXTFLAGS axis and NOT under
#              another shows up with the SAME key in both dumps but a
#              `trc=REFUSED` value on the axis side that failed to compile
#              (rather than a missing key — the whole point of the REFUSED
#              producer above), which is exactly the "this axis changed what
#              refuses to compile, and here is why" signal a pass/fail COUNT
#              comparison would hide (two
#              runs can have equal fail counts while disagreeing on which
#              cases passed). Under PROCS>1 each worker gets its own dump
#              path (`$RXTDUMP.$idx`, threaded through the same re-invocation
#              env block RXTFLAGS/RXTROUTE already ride) and the parent cats
#              them together, in `files[]` order, once every worker has
#              reported — so `RXTDUMP=x PROCS=4` and `RXTDUMP=x PROCS=1`
#              produce the same LINE SET (order may differ across files,
#              never across PROCS values within one file, since one file is
#              always one worker) — a consumer that diffs by key rather than
#              by line position is unaffected either way.
#
# See docs/spec/rxt_format.md for the .rxt format and driver protocol (the
# contract, [SPEC-1.6]); docs/testing.md for runtimes, batteries and history.

set -u

# [K35, ruled by Frank at the [DD-14] close, 2026-08-25] THE GENERAL FIX:
# NO SCRIPT BELOW THIS ONE INHERITS THE AMBIENT LOCALE. Under `en_US.UTF-8`
# `sort` collates at a level that treats punctuation as IGNORABLE, so for a
# corpus of REGEXES `a{0,0}b` and `(a){0,0}b` compare EQUAL and `sort -u`
# silently drops one — and the survivor is the spelling WITHOUT punctuation,
# i.e. the STRUCTURED half of every collision is what is lost. MEASURED on
# this tree 2026-08-25: the corpus pattern extraction yields 1,784 patterns
# in the ambient locale and 2,758 under LC_ALL=C, a 35% silent shrink.
# K35's own history is why this is here and not only at each site: the
# hazard was written down at tests/cli/run_cli_tests.sh:786 and then recurred
# five times, because a lesson recorded in one file does not reach the next
# author. Every site is ALSO guarded individually (belt and braces — a script
# run directly from a Makefile recipe never passes through here), and
# run_codegen_tests.sh carries a structural check that greps for an
# unguarded `sort` in any tests/**/run_*.sh and fails naming it.
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# D45: ONE shared generated-code compile budget for the whole tree.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
RUN_SECS="$(gen_run_secs)"   # per-cell matcher-run budget; see the run site

# [ART-SIZE.1b] the artifact-size log's comment-stripped byte counter —
# see that file's own header for why a flat scan agrees with the census's
# depth-aware classifier byte for byte.
. "$ROOT_DIR/tests/lib/size_count.sh"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
RXTFLAGS="${RXTFLAGS:-}"
RXTROUTE="${RXTROUTE:-}"
RXTDUMP="${RXTDUMP:-}"
# a stale dump from a previous run must never silently grow — this run's
# lines are the whole content, so start empty when a path is given (the
# PROCS>1 branch below writes to per-worker paths instead and cats them
# here fresh; the serial path below appends to this same truncated file).
[ -n "$RXTDUMP" ] && : > "$RXTDUMP"
# [ART-SIZE.1b] SIZELOG — same shape as RXTDUMP immediately above (per-
# worker path under PROCS>1, parent cats them back together in files[]
# order once every worker reports): when set, one TSV row is appended per
# SUCCESSFUL corpus compile at the existing gen_cc call site — riding that
# compile rather than adding one (docs/dev/plan.md [ART-SIZE.1b]'s "zero
# cost" charter). Empty (the default) means no rows are ever computed or
# written, so a plain run pays nothing and is byte-for-byte unchanged; see
# tests/size/CLAUDE.md for the row format and tests/size/run_size_log.sh
# for the wrapper that turns a run's rows into the stable, diffable log.
SIZELOG="${SIZELOG:-}"
[ -n "$SIZELOG" ] && : > "$SIZELOG"
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

# [DD-13b.W1.1] `--dump` — LEG B of the C1 parse differential (w1_impl
# §3.1). It PARSES the named files and prints one TSV row per pattern
# block and per expectation case, and COMPILES NOTHING: the point is to
# expose what THIS parser understood, so a third parser (pcrec's
# `--list-source`, leg A) and a fourth (verify_rxt.py `--dump`, leg C)
# can be compared against it byte for byte.
#
# IT IS FED BY flush_block AND NOT BY THE ARM CHAIN, deliberately. The
# arms are inside the hash-pinned region, and threading an emit call
# through each of them would move the pin on every arm at once — the
# protection would be spent on the change that installed the dump. Every
# fact a row carries is already in flush_block's own per-block state, so
# the dump reads what the parse produced rather than re-deriving it.
#
# It is invoked through the ARGUMENT branch below, never the no-argument
# one: the default branch excludes tests/known_fail/ and yields 178 files,
# while C1's population is all 179. The two run the same script over
# different populations on purpose (§3.0).
# a head-bearing file with NO `pattern` row: every line is head, so the
# body loop starts past the end. Larger than any .rxt file's line count
# (the corpus's longest is four figures) and it is compared with -le, so
# it is a skip-everything sentinel rather than a magic line number.
RXT_SKIP_WHOLE_FILE=1000000000

RXT_DUMP=0
if [ $# -gt 0 ] && [ "$1" = "--dump" ]; then
    RXT_DUMP=1
    shift
    # serial, so the row order is the file order the caller gave and a
    # differential can compare streams rather than sorted multisets
    PROCS=1
    if [ $# -eq 0 ]; then
        echo "run.sh: --dump needs at least one file or directory" >&2
        exit 2
    fi
fi

files=()
if [ $# -eq 0 ]; then
    while IFS= read -r f; do files+=("$f"); done \
        < <(find "$ROOT_DIR/tests" -name '*.rxt' \
                 -not -path "*/known_fail/*" | LC_ALL=C sort)
else
    for arg in "$@"; do
        if [ -d "$arg" ]; then
            while IFS= read -r f; do files+=("$f"); done \
                < <(find "$arg" -name '*.rxt' | LC_ALL=C sort)
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
        # RXTDUMP: each worker gets its OWN path ($RXTDUMP.$idx) — the
        # worker's own top-of-script "[ -n "$RXTDUMP" ] && : > "$RXTDUMP""
        # truncate would otherwise race every other worker on one shared
        # path. Empty when RXTDUMP itself is empty, so an ordinary parallel
        # run threads nothing new.
        w_rxtdump=""
        [ -n "$RXTDUMP" ] && w_rxtdump="$RXTDUMP.$idx"
        # [ART-SIZE.1b] SIZELOG: identical per-worker-path shape to RXTDUMP
        # just above, for the identical reason (a shared path would race
        # every worker's own truncate-then-append against its siblings).
        w_sizelog=""
        [ -n "$SIZELOG" ] && w_sizelog="$SIZELOG.$idx"
        PROCS=1 PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
            RXTFLAGS="$RXTFLAGS" RXTROUTE="$RXTROUTE" RXTDUMP="$w_rxtdump" \
            SIZELOG="$w_sizelog" \
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
    total_sizelog=0
    summaries=0
    fail_files=()

    idx=0
    for f in "${files[@]}"; do
        idx=$((idx + 1))
        # replay the worker's failure detail and any harness notes, in order
        cat "$pardir/$idx.err" >&2
        # RXTDUMP: append this worker's per-file dump into the merged path,
        # IN files[] ORDER (the same order the .err replay above uses) — so
        # two runs of the same file list produce the SAME LINE SET regardless
        # of which worker finished first; a consumer diffing by "file:line"
        # key is unaffected by any residual within-file order difference.
        if [ -n "$RXTDUMP" ] && [ -f "$RXTDUMP.$idx" ]; then
            cat "$RXTDUMP.$idx" >> "$RXTDUMP"
            rm -f "$RXTDUMP.$idx"
        fi
        # [ART-SIZE.1b] SIZELOG: same append-in-files[]-order shape.
        if [ -n "$SIZELOG" ] && [ -f "$SIZELOG.$idx" ]; then
            cat "$SIZELOG.$idx" >> "$SIZELOG"
            rm -f "$SIZELOG.$idx"
        fi
        p="$(grep -m1 '^cases passed:' "$pardir/$idx.out" | grep -oE '[0-9]+')"
        x="$(grep -m1 '^cases failed:' "$pardir/$idx.out" | grep -oE '[0-9]+')"
        c="$(grep -m1 '^pattern-compile failures (distinct):' "$pardir/$idx.out" | grep -oE '[0-9]+$')"
        gp="$(grep -m1 '^group cases pending-vm:' "$pardir/$idx.out" | grep -oE '[0-9]+$')"
        sl="$(grep -m1 '^size-log rows:' "$pardir/$idx.out" | grep -oE '[0-9]+$')"
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
        total_sizelog=$((total_sizelog + ${sl:-0}))
        [ "$x" -gt 0 ] && fail_files+=("$f: $x")
    done

    echo
    echo "== Summary =="
    echo "cases passed: $total_pass"
    echo "cases failed: $total_fail"
    if [ ${#fail_files[@]} -gt 0 ]; then
        echo "failures by file:"
        for line in "${fail_files[@]}"; do echo "  $line"; done | LC_ALL=C sort
    fi
    echo "pattern-compile failures (distinct): $total_cfail"
    echo "group cases pending-vm: $total_pending"
    [ -n "$SIZELOG" ] && echo "size-log rows: $total_sizelog"
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
total_sizelog=0         # [ART-SIZE.1b] SIZELOG rows actually written — read
                        # back by the PROCS>1 aggregation above and by
                        # tests/size/run_size_log.sh's own header stamp.
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
# [DD-13b.W1.1] THE RXT-ESCAPE, leg B's half. Same vocabulary as
# src/parse/rxt_source.c's `put_escaped` and as the .rxt format's own
# subject escape (`\t \n \r \\ \xNN`, docs/spec/rxt_format.md) — one
# vocabulary, three implementations, which is what a differential over
# three parsers requires and is why no second decoder is invented.
#
# It is NOT `RXTDUMP`'s lossy `tr '\n\t' '  '` squash (run.sh:~56). That
# squash is correct THERE — that dump is diffed against ITSELF across
# optimization axes, so an identical squash on both sides loses nothing —
# and would be WRONG here, where the whole job is to find a
# cross-implementation disagreement a squash could hide.
#
# THE FAST PATH IS PURE BASH, because this runs ~13,000 times over the
# corpus and a fork per field would dominate C1's runtime. MEASURED: 3
# corpus patterns carry a literal TAB (the thing under test in all three),
# 963 pattern lines carry a backslash, and 0 carry any other control byte
# — so the three substitutions below cover the corpus exactly. The
# fallback exists anyway: a byte the fast path cannot spell must not
# silently emit raw and shift every later column.
rxt_escape() {
    local s=$1
    s=${s//\\/\\\\}
    s=${s//$'\t'/\\t}
    s=${s//$'\r'/\\r}
    case $s in
        *[$'\x01'-$'\x08\x0b\x0c\x0e'-$'\x1f\x7f']*)
            # a control byte the fast path does not spell: fall back to the
            # per-byte form, which is the SAME `\xNN` rendering pcrec emits
            s=$(printf '%s' "$s" | LC_ALL=C awk '{
                    out=""
                    for (i = 1; i <= length($0); i++) {
                        c = substr($0, i, 1)
                        n = index(CTRL, c)
                        if (n > 0) out = out sprintf("\\x%02x", n)
                        else out = out c
                    }
                    print out
                }' CTRL=$'\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f')
            ;;
    esac
    REPLY=$s
}

# ONE `block` row and one `case` row per expectation, in the schema
# tests/rxtsource/run_rxtsource_tests.sh projects all three legs onto.
# `perr` is a BLOCK field rather than a case row because that is how this
# parser models it (a perr block has no m/n lines and the pattern text is
# the whole test) and because the directive's own line number is not
# retained — recording one would be an edit inside the pinned region.
rxt_dump_block() {
    # no command substitution anywhere in here: this runs once per block
    # (3,265 times over the corpus) and a fork per boolean field would be
    # most of C1's runtime.
    local desc pat only perr
    rxt_escape "$cur_description"; desc=$REPLY
    rxt_escape "$cur_pattern";     pat=$REPLY
    only=""; [ "$cur_features_only" = "1" ] && only=1
    perr=""; [ "$cur_is_perr" = "1" ] && perr=1
    printf 'block\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$cur_file" "$cur_pattern_line" "$cur_name" "$desc" "$pat" \
        "$cur_flags" "$cur_features" "$only" \
        "$cur_encoding" "$cur_engine" "$cur_stepbudget" "$cur_framebudget" \
        "$perr"
    local i
    for i in "${!case_kind[@]}"; do
        printf 'case\t%s\t%s\t%s\t%s\t%s\n' \
            "$cur_file" "${case_line[$i]}" "${case_kind[$i]}" \
            "${case_startpos[$i]}" "${case_gspec[$i]}"
    done
}

flush_block() {
    # [DD-13b.W1.1] leg B: report what the parse understood and compile
    # NOTHING. Placed at the top of the one function every block already
    # passes through, so the dump cannot see a different set of blocks
    # than the runner does.
    if [ "$RXT_DUMP" = "1" ]; then
        rxt_dump_block
        return 0
    fi
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
            if pcrec_run "$PCREC" --features "$cur_features" -p rxfc -o "$bdir/featprobe.c" -- 'a' >/dev/null 2>&1; then
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
            # [DD-13b.W1.1] A BLOCK WITH NO CASES STILL HAS TO FAIL, and
            # until this line it did not. The failure was recorded once
            # PER CASE, so a `perr` block — which by definition has no
            # m/n/... lines — recorded NOTHING and returned quietly, which
            # is precisely the "quiet pass" the comment above forbids. It
            # is also the worst block kind to lose it on: pcrec refuses an
            # unknown module name with exit 1, and exit 1 is exactly what
            # `perr` asserts, so the typo'd block would have gone on to
            # certify the typo rather than the pattern.
            #
            # Found by building a WITNESS for sabotage row S199, which
            # scored UNDETECTED because the corpus contains no invalid
            # features list to expose it. The fix is the general form of
            # what the loop above was reaching for: the failure belongs to
            # the BLOCK, so when there are no cases to hang it on it is
            # attributed to the block's own `pattern` line.
            if [ "${#case_kind[@]}" -eq 0 ]; then
                record_fail "$cur_file" "$cur_pattern_line" \
                    "HARNESS FAILURE: --features '$cur_features' is not a valid enabled-set spec (block has no cases; a perr block would otherwise have read pcrec's refusal of this typo as its own expected rejection)"
            fi
            return 0
        fi
        pflags+=(--features "$cur_features")
    fi

    # [DD-14 wave A commit 3] the `engine`/`budget` directives -- the
    # minimal route to a corpus case that can reach `--engine=vm` with a
    # tiny budget, so `gu` has something to assert against without
    # inventing a new construct. Same "per-block, validated at parse time"
    # shape as flags/features above.
    # [DD-13b.W1.1] `encoding` (D58's per-pattern axis, format_design's W1
    # row). Per-COMPILE like every other directive here, never global: two
    # blocks in one file may use different encodings. MEASURED free — no
    # corpus block carries one today, so this appends nothing to any
    # existing invocation.
    [ -n "$cur_encoding" ] && pflags+=(--encoding="$cur_encoding")
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
            # RXTDUMP ([CHK-2] extension, manager finding 2026-08-26): a
            # case whose BLOCK failed to compile never reaches the `out=`
            # line below, so a RXTDUMP consumer used to see nothing at all
            # for it — no record of WHY the case is missing, only that it
            # is (an axis-vs-default diff reads this as an undifferentiated
            # "LOST"). Dump the pcrec diagnostic itself, flattened to one
            # line (a TSV row, and a multi-line ctx_fail message would
            # otherwise corrupt the format), with a sentinel `trc` field
            # (REFUSED, never a real exit code) so a consumer can tell "the
            # pattern was refused, here is why" apart from "the case ran
            # and gave up" (trc=3) or "the case ran and disagreed" (trc=0/1
            # with a different `out`).
            if [ -n "$RXTDUMP" ]; then
                local flat_err
                flat_err="$(printf '%s' "$pcrec_err" | tr '\n\t' '  ')"
                printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
                    "$cur_file" "${case_line[$i]}" "${case_kind[$i]}" "refused" \
                    "REFUSED" "$flat_err" \
                    >> "$RXTDUMP"
            fi
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
    #
    # [ART-SIZE.1b] gcc CPU/wall time for THIS EXACT compile, at
    # (measured, see tests/lib/size_count.sh's size_count_row header)
    # near-zero extra cost: bash's own `time` reserved word wraps the call
    # rather than re-running it, with TIMEFORMAT set to a fixed, parseable
    # one-line shape and its output redirected to a private file so it
    # cannot collide with gen_cc's own stderr (gen_cc captures the
    # compiler's stdout+stderr itself, into $GEN_CC_LOG, via an internal
    # command substitution — nothing escapes to this shell's real fd 2 for
    # `time` to mix with; verified empirically before wiring this in).
    # EVERYTHING below `time gen_cc` that computes a row is gated on
    # SIZELOG being set AND zero subprocesses beyond ONE (`size_count_row`,
    # which folds the size scan and stamp grep into a single awk call —
    # see its own header for the 8-spawns-to-1 measurement that made this
    # gate necessary): the CPU-time sum and the load reading are pure bash
    # builtins (`read` sourcing a file directly, `printf -v`, and stripping
    # decimal points to sum two fixed-3-decimal numbers as integer
    # milliseconds), so a plain run (SIZELOG unset) pays for exactly one
    # `time` builtin per compile and nothing else this block adds.
    local _sz_tf
    _sz_tf="$WORKDIR/.sz_time.$$"
    {
        TIMEFORMAT='ARTSIZE_TIME %3R %3U %3S'
        time gen_cc "$cur_pattern" "$CC" $GENCFLAGS -I"$bdir" -o "$bdir/t" "$SCRIPT_DIR/driver.c" "$bdir/gen.c"
    } 2> "$_sz_tf"
    build_rc=$?
    build_log="$GEN_CC_LOG"
    if [ -n "$SIZELOG" ] && [ "$build_rc" -eq 0 ]; then
        local _sz_tag _sz_wall _sz_user _sz_sys _sz_cpu _sz_cpu_ms _sz_load1 _sz_row
        read -r _sz_tag _sz_wall _sz_user _sz_sys < "$_sz_tf"
        # Sum user+sys as integer milliseconds (both are fixed 3-decimal
        # strings from TIMEFORMAT's %3U/%3S — stripping the '.' turns
        # "6.995" into "6995" exactly): `10#` forces base-10 so a value
        # with a leading zero ("0.089" -> "0089") is never misread as
        # octal (bash's default for a leading-0 numeral, which would
        # error on an 8 or 9 digit). Falls back to 0 on a missing/short
        # read (a timed-out or crashed compile never reaches this branch,
        # since build_rc must be 0, but a malformed TIMEFORMAT line is
        # cheap to guard against explicitly).
        local _sz_ums _sz_sms
        _sz_ums="${_sz_user//./}"; _sz_sms="${_sz_sys//./}"
        _sz_cpu_ms=$(( 10#${_sz_ums:-0} + 10#${_sz_sms:-0} ))
        printf -v _sz_cpu '%d.%03d' "$((_sz_cpu_ms / 1000))" "$((_sz_cpu_ms % 1000))"
        read -r _sz_load1 _ < /proc/loadavg
        _sz_row="$(size_count_row "$bdir/gen.c" "$bdir/gen.h")"
        # Pattern id is ROOT-RELATIVE, never absolute: a no-args (full
        # corpus) run discovers files via `find "$ROOT_DIR/tests" ...`
        # (absolute paths), while a targeted run's own argv is whatever
        # the caller typed (often already relative) — without stripping
        # $ROOT_DIR/ here, the SAME pattern would log under a DIFFERENT
        # id depending on which invocation shape produced the row, which
        # breaks scripts/size_diff's whole "compare the same pattern
        # across two logs" premise the moment a log is regenerated from a
        # different checkout path (a merge to main, a different worktree
        # name). `${cur_file#$ROOT_DIR/}` no-ops (leaves cur_file
        # unchanged) when it does not already start with `$ROOT_DIR/`, so
        # this is safe for every existing call shape.
        # $_sz_row already carries FOUR tab-separated fields of its own
        # (engine, rungs, prefilter, bytes — size_count_row's own header)
        # as ONE argument here, so this format string has 5 %s for 5
        # arguments, not 8 — the logical row is 8 TSV columns wide.
        printf '%s\t%s\t%s\t%s\t%s\n' \
            "${cur_file#$ROOT_DIR/}:$cur_pattern_line" "$_sz_row" "$_sz_cpu" "${_sz_wall:-}" "${_sz_load1:-0}" \
            >> "$SIZELOG"
        total_sizelog=$((total_sizelog + 1))
    fi
    rm -f "$_sz_tf"
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
        # RXTDUMP (see the header comment): the RAW case identity, dumped
        # BEFORE any pass/fail interpretation below so it captures every
        # evaluated case in one uniform shape regardless of which branch
        # eventually scores it — a diff between two dumps compares ANSWERS,
        # not the PASS/FAIL verdict the harness derives from them.
        if [ -n "$RXTDUMP" ]; then
            printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
                "$cur_file" "$line" "$kind" "${route:-default}" "$trc" "$out" \
                >> "$RXTDUMP"
        fi
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
    cur_name=""
    cur_description=""
    cur_encoding=""
    cur_features_only=0
    cur_route="$RXTROUTE"
    case_kind=(); case_line=(); case_subject=(); case_start=(); case_end=(); case_startpos=()
    case_route=()
    have_block=0
    blocks_in_file=0

    # ---- [DD-13b.W1.1] THE SEAM (w1_impl §1.1, the manager's ruling) ----
    #
    # This script gains NO HEAD ARMS and no head recogniser. For a file
    # whose first non-comment line is not `pattern`, it calls pcrec
    # `--list-source` ONCE, reads the `line` column of the FIRST `pattern`
    # row, and starts the loop below AT that line. The head is an
    # UNTOUCHED BYTE RANGE whose boundary comes from the one head parser.
    #
    # That is the whole point: the head grammar has exactly one
    # implementation, so the two cannot drift. What this script decides
    # for itself is only "is there a head at all" — one token compare
    # against `pattern`, which is not head syntax and cannot go stale as
    # the head grammar grows. Everything past that boundary is this
    # script's own business, unchanged.
    #
    # MEASURED: 0 of the corpus's 179 files are head-bearing, so the call
    # is never made and all 179 take a byte-identical code path. That zero
    # is asserted TWICE and from two sources in
    # tests/rxtsource/run_rxtsource_tests.sh — an external count of what
    # pcrec was actually invoked with, and an independent census of the
    # corpus — because a counter that shares a source with the thing it
    # counts cannot see machinery that is simply absent.
    #
    # THE `line` COLUMN IS LOAD-BEARING, which is why it has its own
    # sabotage row: reported too early, the loop starts on a head line and
    # the catch-all hard-errors; too late with one block, the P-C2 floor
    # fires; too late with several, the `have_block` guard above catches
    # what used to be silent.
    head_skip=0
    head_probe=""
    while IFS= read -r probe_line || [ -n "$probe_line" ]; do
        case $probe_line in
            '#'*) continue ;;
        esac
        case $probe_line in
            *[![:space:]]*) ;;
            *) continue ;;
        esac
        head_probe=${probe_line%%[[:space:]]*}
        break
    done < "$file"

    if [ -n "$head_probe" ] && [ "$head_probe" != "pattern" ]; then
        ls_out=""
        if ! ls_out="$("$TIMEOUT_BIN" "$(pcrec_timeout_secs)" \
                        "$PCREC" --list-source "$file" 2>&1)"; then
            # THE CALL FAILED. A distinct observable from "the file has no
            # pattern rows" (below): different exit status, and pcrec's own
            # diagnostic — which names the file, the line and the construct
            # — is carried through verbatim rather than replaced.
            record_fail "$file" 1 \
                "HARNESS FAILURE: pcrec --list-source failed on this head-bearing file: $ls_out"
            continue
        fi
        head_body_line="$(printf '%s\n' "$ls_out" \
            | LC_ALL=C awk -F'\t' '$1 == "pattern" { print $2; exit }')"
        if [ -z "$head_body_line" ]; then
            # A HEAD AND NO PATTERN BLOCKS. The grammar permits it (a pure
            # library file is exactly that shape), so it is not an error
            # HERE — the whole file is head, nothing is parsed below, and
            # blocks_in_file stays 0, which the P-C2 floor at the end of
            # this loop reports on its own. Two observables, never confused.
            head_skip=$RXT_SKIP_WHOLE_FILE
        else
            head_skip=$((head_body_line - 1))
        fi
    fi

    lineno=0
    while IFS= read -r line || [ -n "$line" ]; do
        lineno=$((lineno + 1))
        [ "$lineno" -le "$head_skip" ] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ ^# ]] && continue

        # [DD-13b.W1.1 / R-COMPAT-1] Everything between these two markers is
        # the arm chain 3,265 existing blocks and 26,691 existing expectation
        # lines are parsed by. MEASURED: 17 `[[ =~ ]]` elif arms plus the
        # catch-all `else` — the design note says "13", which was never the
        # count; the marker is deliberately named without a number so it
        # cannot go stale again as arms are appended. It is HASH-PINNED by
        # tests/rxtsource/run_rxtsource_tests.sh, so a change here cannot
        # land unnoticed. The pin is over the TEXT BETWEEN THE MARKERS and
        # not over a line range, deliberately: this very step edits inside
        # the region (the `have_block` guard, `features only`), and a
        # line-range hash would be broken by the change it exists to protect.
        # New arms are appended AFTER the END marker; edits INSIDE the region
        # are changes to the arms R-COMPAT-1 protects and are meant to move
        # the hash, which is what forces a deliberate re-pin. The update rule
        # lives in the check's own failure message, where a person looking at
        # the failure will actually read it. This explanation sits ABOVE the
        # marker on purpose: the pin covers the ARMS, and prose about the pin
        # should not be able to move the pin.
        # --- BEGIN PINNED ARM REGION (w1 N3) ---
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
            # [DD-13b.W1.1] the three new block-scoped directives reset with
            # the block exactly as the five above do — block-scoped means
            # block-scoped, and a directive that carried to the next block
            # would compile the following pattern under something nobody
            # wrote (S-C3's shape, one directive over).
            cur_name=""
            cur_description=""
            cur_encoding=""
            cur_features_only=0
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
            # [DD-13b.W1.1] THE `have_block` GUARD, generalised. Six of the
            # directive arms above already carried it and the CASE arms did
            # not, so a case line with no open block was silently DROPPED
            # rather than refused — the EOF flush is gated on have_block too,
            # so those cases simply never ran and nothing counted them. This
            # is the GENERAL form of a guard seven arms already had, not a
            # new special case. MEASURED FREE: 0 of the corpus's 26,691 case
            # lines precede a `pattern` line, so no existing file can reach
            # any of these new branches. It is what makes S-C10's "line
            # reported too late, several blocks" case LOUD instead of silent.
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'perr' line before any pattern block"
            else
                cur_is_perr=1
            fi
        elif [[ "$line" =~ ^m[[:space:]]+\"(.*)\"[[:space:]]+([0-9]+)[[:space:]]+([0-9]+)[[:space:]]*$ ]]; then
            # [DD-13b.W1.1] the `have_block` guard (see the `perr` arm
            # above for why the case arms lacked it and what it makes loud).
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'m' line before any pattern block"
            else
                case_kind+=("m")
                case_line+=("$lineno")
                case_subject+=("${BASH_REMATCH[1]}")
                case_start+=("${BASH_REMATCH[2]}")
                case_end+=("${BASH_REMATCH[3]}")
                case_startpos+=("0")
                case_gspec+=("")
                case_gucode+=("")
                case_route+=("$cur_route")
            fi
        elif [[ "$line" =~ ^n[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            # [DD-13b.W1.1] the `have_block` guard (see the `perr` arm
            # above for why the case arms lacked it and what it makes loud).
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'n' line before any pattern block"
            else
                case_kind+=("n")
                case_line+=("$lineno")
                case_subject+=("${BASH_REMATCH[1]}")
                case_start+=("")
                case_end+=("")
                case_startpos+=("0")
                case_gspec+=("")
                case_gucode+=("")
                case_route+=("$cur_route")
            fi
        elif [[ "$line" =~ ^ms[[:space:]]+([0-9]+)[[:space:]]+\"(.*)\"[[:space:]]+([0-9]+)[[:space:]]+([0-9]+)[[:space:]]*$ ]]; then
            # [DD-13b.W1.1] the `have_block` guard (see the `perr` arm
            # above for why the case arms lacked it and what it makes loud).
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'ms' line before any pattern block"
            else
                case_kind+=("m")
                case_line+=("$lineno")
                case_startpos+=("${BASH_REMATCH[1]}")
                case_subject+=("${BASH_REMATCH[2]}")
                case_start+=("${BASH_REMATCH[3]}")
                case_end+=("${BASH_REMATCH[4]}")
                case_gspec+=("")
                case_gucode+=("")
                case_route+=("$cur_route")
            fi
        elif [[ "$line" =~ ^ns[[:space:]]+([0-9]+)[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            # [DD-13b.W1.1] the `have_block` guard (see the `perr` arm
            # above for why the case arms lacked it and what it makes loud).
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'ns' line before any pattern block"
            else
                case_kind+=("n")
                case_line+=("$lineno")
                case_startpos+=("${BASH_REMATCH[1]}")
                case_subject+=("${BASH_REMATCH[2]}")
                case_start+=("")
                case_end+=("")
                case_gspec+=("")
                case_gucode+=("")
                case_route+=("$cur_route")
            fi
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
            # [DD-13b.W1.1] the `have_block` guard (see the `perr` arm
            # above for why the case arms lacked it and what it makes loud).
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'gu' line before any pattern block"
            else
                case_kind+=("gu")
                case_line+=("$lineno")
                case_subject+=("${BASH_REMATCH[2]}")
                case_start+=("")
                case_end+=("")
                case_startpos+=("0")
                case_gspec+=("")
                case_gucode+=("${BASH_REMATCH[1]}")
                case_route+=("$cur_route")
            fi
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
        # --- END PINNED ARM REGION ---
        #
        # [DD-13b.W1.1] W1's THREE NEW BLOCK ARMS plus `features only`,
        # APPENDED here rather than inserted above, for two reasons. The
        # region above is hash-pinned (see the BEGIN marker), and an
        # `if/elif` chain is ORDER-SENSITIVE: `[[ =~ ]]` clobbers
        # BASH_REMATCH, so every arm must capture before the next one runs,
        # and appending is the only edit that cannot change which arm an
        # EXISTING line reaches.
        #
        # WHY APPENDING IS SAFE, and it is a census rather than an argument:
        # a line these arms newly parse is a line that previously hit the
        # catch-all and was a HARD ERROR, so the only files whose meaning can
        # change are files that do not parse today. The corpus's first-token
        # census (asserted as a check in tests/rxtsource/) is what keeps that
        # true — `name`, `description` and `encoding` appear as a first token
        # in 0 of the corpus's lines.
        elif [[ "$line" =~ ^features[[:space:]]+only[[:space:]]+([a-zA-Z0-9,_-]+)[[:space:]]*$ ]]; then
            # [M14] `features only <list>`: the list REPLACES what a config
            # would otherwise union in, rather than adding to it. W1.1 has no
            # `config` in the body and therefore nothing to override — the
            # flag is PARSED and RECORDED here so the dump can carry it and
            # the two parsers agree about the line, and it becomes operative
            # when W1.2 lands config composition. Its own arm rather than an
            # optional group in the arm above: that one is inside the pinned
            # region, and `only` is a real word a module could be called.
            feat_list="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'features' line before any pattern block"
            else
                cur_features="$feat_list"
                cur_features_only=1
            fi
        elif [[ "$line" =~ ^name[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
            # [DD-13b.W1] the block's NAME — an `ident`, which is a PCRE2
            # group name AND a C identifier, one rule so a name that can be a
            # group cannot fail to be a symbol later. It is in the FILE
            # namespace, not the pattern's (w1_impl DECIDED (7)).
            #
            # RECORDED, NOT USED, in W1.1: `rx_info.name` is W1.2's and the
            # abi does not move in this step. The harness records it so the
            # C1 dump carries it and so the two parsers are compared on a
            # line one of them would otherwise never see. A DUPLICATE name is
            # pcrec's refusal to make, not this loop's — a duplicate is a
            # whole-FILE fact and this parser is the body's.
            blk_name="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'name' line before any pattern block"
            else
                cur_name="$blk_name"
            fi
        elif [[ "$line" =~ ^description[[:space:]]+(.*)$ ]]; then
            # [DD-13b.W1] `description` is a FIELD, not a comment (Frank,
            # r44): machine-readable, so a script can summarize what a file
            # holds, which is why it is not spelled `#`.
            #
            # THE ONE-LINE FORM ONLY. format_design §1.3 gives a block-line
            # `description` the same `prose-value` the head's takes, which
            # includes the `|` block scalar — but §1.2 says a pattern block's
            # lines are NOT indented, and a block scalar IS indented
            # continuation. Both cannot hold in the body, and the body's rule
            # is the one 3,265 blocks depend on. So `|` is a head form, and
            # this loop needs no continuation mechanism — which is also what
            # keeps head-shaped parsing out of the harness, the thing the
            # seam ruling removed. src/parse/rxt_source.c refuses `|` here
            # with that reason named, so the two parsers agree.
            blk_desc="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'description' line before any pattern block"
            elif [ "$blk_desc" = "|" ]; then
                record_fail "$file" "$lineno" \
                    "a pattern block's 'description' takes the one-line form only: the '|' block scalar is continuation, and a pattern block's lines are not indented (the head is where '|' belongs)"
            else
                cur_description="$blk_desc"
            fi
        elif [[ "$line" =~ ^encoding[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
            # [DD-13b.W1] D58's PER-PATTERN encoding axis reaching the corpus.
            # Block-scoped like `flags`/`features`/`engine`/`budget`, and it
            # routes to `--encoding=` in flush_block. WHETHER the named
            # encoding is implemented is pcrec's refusal to make, not this
            # loop's — `utf8` is refused until M5 and a block asking for it
            # should hear that from the compiler, in the compiler's words.
            blk_enc="${BASH_REMATCH[1]}"
            if [ "$have_block" != "1" ]; then
                record_fail "$file" "$lineno" "'encoding' line before any pattern block"
            else
                cur_encoding="$blk_enc"
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

# [DD-13b.W1.1] in --dump mode STDOUT is the TSV and nothing else: a
# differential compares streams, and a summary appended to one of them
# would be a disagreement about the corpus that is really a disagreement
# about this script's chattiness. Parse failures still reach STDERR —
# `record_fail` writes there — so nothing is hidden, it is merely kept out
# of the data.
#
# THE EXIT STATUS STILL MEANS SOMETHING. `--dump` is a parse, so a file it
# cannot parse must not exit 0: a caller that checks the status (the
# block-scalar refusal in tests/rxtsource/ is one) would otherwise read
# "this file was rejected" as "this file was fine and produced no rows",
# which is the same absence-reads-as-success shape the short-list hard
# fail exists to refuse one directory over.
if [ "$RXT_DUMP" = "1" ]; then
    [ "$total_fail" -eq 0 ] || exit 1
    exit 0
fi

echo
echo "== Summary =="
echo "cases passed: $total_pass"
echo "cases failed: $total_fail"
if [ ${#file_fail_count[@]} -gt 0 ]; then
    echo "failures by file:"
    for f in "${!file_fail_count[@]}"; do
        echo "  $f: ${file_fail_count[$f]}"
    done | LC_ALL=C sort
fi
echo "pattern-compile failures (distinct): ${#compile_fail_set[@]}"
echo "group cases pending-vm: $total_pending"
[ -n "$SIZELOG" ] && echo "size-log rows: $total_sizelog"

if [ $((total_pass + total_fail)) -eq 0 ]; then
    echo "run.sh: NO CASES RUN — corpus missing or fully unparseable" >&2
    exit 1
fi
[ "$total_fail" -eq 0 ] && exit 0
exit 1
