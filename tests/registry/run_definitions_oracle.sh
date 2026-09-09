#!/usr/bin/env bash
# tests/registry/run_definitions_oracle.sh — [DD-11.3]'s option-matrix
# self-oracle (definitions_table.md §3 item 4, the manager's brief): per
# row, over the option matrix (multiline x nocap) through the REAL tag
# evaluator, does the table's resolved definition (Pattern B) agree with
# the row's own shipped construct (Pattern A) -- and does Pattern A agree
# with libpcre2. run_pc4.sh's own shape, one table over: a cell generator
# (definitions_oracle_gen, linking libpcrec.a), a per-cell pcrec-compile-
# and-run sweep (two prefixes in one binary, possdiff_driver.c's shape),
# and a comparator that also drives libpcre2 directly (definitions_oracle_
# check.c, pc4_check.c's own shape).
#
# SKIPS LOUDLY without libpcre2 (probed FIRST via tests/lib/resolve_pcre2.sh,
# PC-3/PC-4's own convention). [ORACLE-LINK] (D98, 2026-09-09) NARROWED WHAT
# CAN RUN WITHOUT LIBPCRE2, and says so here rather than silently: before
# direct linking, definitions_oracle_check.c built via dlopen regardless of
# whether libpcre2 was present (no header/lib needed to declare its own
# prototypes), so a box with no libpcre2 still got the A==B self-consistency
# leg and only A==C (the external oracle comparison) skipped at runtime. That
# binary now #includes <pcre2.h> and links -lpcre2-8 unconditionally (the
# same header every other converted oracle check uses), so on a box where
# libpcre2 is not resolvable the binary cannot be BUILT at all -- A==B is
# bundled into the same comparator as A==C and skips WITH it. This is a real,
# disclosed narrowing (docs/dev/lanes/oralink_report.md), not an oversight:
# splitting the comparator into two binaries to keep A==B header-free was
# judged not worth the duplication for one self-consistency leg.
#
# cells.tsv is FIVE fields since the r43-third-round follow-up (2026-08-29,
# the DEFK_TEXTFN rows and the POSIX class-name family joining the sweep):
# id, pattern_a, pattern_b, oracle_a, description. This script only ever
# reads the first three (pattern_a/pattern_b are what gets compiled below);
# oracle_a is definitions_oracle_check.c's own field, read straight from
# the TSV file it opens itself.
#
# Env: PCREC, CC, KEEP=1, JOBS (parallel compile fan-out, default nproc/2),
#   GENCFLAGS (SAN-1, default -O0 -std=gnu11), SANFLAGS (SAN-1)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="registry"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O0 -std=gnu11}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer -Werror"; fi
SANFLAGS="${SANFLAGS:-}"
. "$ROOT_DIR/tests/lib/ncpu.sh"; ncpu="$NCPU"   # [MACPORT] a real reading on a box with no `nproc` on PATH at all
JOBS="${JOBS:-$(( ncpu / 2 > 1 ? ncpu / 2 : 1 ))}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-definitions-oracle.XXXXXX")"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_definitions_oracle.sh: KEEP=1, kept: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

# ---- build the generator and the comparator; the comparator doubles as
#      the oracle probe for the A==C leg -------------------------------
if ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
        -I "$ROOT_DIR/lib" -I "$ROOT_DIR/src" $SANFLAGS \
        -o "$WORKDIR/gen" "$SCRIPT_DIR/definitions_oracle_gen.c" \
        "$ROOT_DIR/build/libpcrec.a"; then
    echo "FAIL: definitions-oracle: definitions_oracle_gen.c does not build" >&2
    exit 1
fi
. "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
have_oracle=1
if [ "$PCRE2_AVAILABLE" != "1" ]; then
    have_oracle=0
    echo "SKIP: definitions-oracle: libpcre2 not resolvable (pkg-config" >&2
    echo "SKIP: definitions-oracle: libpcre2-8 absent or its .pc file not on" >&2
    echo "SKIP: definitions-oracle: PKG_CONFIG_PATH, and a bare '-lpcre2-8'" >&2
    echo "SKIP: definitions-oracle: compile+link probe with \$CC also failed)." >&2
    echo "SKIP: definitions-oracle: the whole comparator did not run — see" >&2
    echo "SKIP: definitions-oracle: this script's own header for why A==B" >&2
    echo "SKIP: definitions-oracle: (no external oracle needed) is bundled" >&2
    echo "SKIP: definitions-oracle: with A==C now, since [ORACLE-LINK]." >&2
    echo "definitions-oracle: 0 cells generated (oracle: unavailable)"
    exit 0
elif ! "$CC" -O1 -std=gnu11 -Wall -Wextra -Werror \
        -I "$ROOT_DIR/tests/fuzz" -I "$SCRIPT_DIR" $PCRE2_CFLAGS $SANFLAGS \
        -o "$WORKDIR/check" "$SCRIPT_DIR/definitions_oracle_check.c" $PCRE2_LIBS; then
    echo "FAIL: definitions-oracle: definitions_oracle_check.c does not build" >&2
    exit 1
fi

# ---- generate the cells ---------------------------------------------------
CELLS="$WORKDIR/cells.tsv"
if ! "$WORKDIR/gen" > "$CELLS" 2> "$WORKDIR/gen.log"; then
    echo "FAIL: definitions-oracle: cell generator exited nonzero" >&2
    cat "$WORKDIR/gen.log" >&2
    exit 1
fi
cat "$WORKDIR/gen.log" >&2
# [MACPORT] `tr -d ' '`: BSD/macOS `wc -l < file` right-justifies its
# count with LEADING SPACES (verified live: "       3" for a 3-line file
# via stdin redirection); GNU wc does not. Untrimmed, this broke
# run_registry_tests.sh's own downstream `grep -qE
# "^definitions-oracle: [0-9]+ cells generated"` needle, which requires
# exactly one space before the digits.
ncells=$(wc -l < "$CELLS" | tr -d ' ')
if [ "$ncells" -lt 1 ]; then
    echo "FAIL: definitions-oracle: 0 cells generated — the table is" >&2
    echo "FAIL: definitions-oracle: populated but nothing reached this sweep" >&2
    exit 1
fi

# ---- the sweep: (pattern A, pattern B) -> pcrec -> gcc -> run -------------
mkdir -p "$WORKDIR/results"
one_cell() {
    local id="$1" pa="$2" pb="$3"
    local d="$WORKDIR/c$id"
    mkdir -p "$d"
    # --features all: both Pattern A (module-gated constructs like \b, \R,
    # the possessive suffix, (?m)/(?n)) and Pattern B (their core-syntax
    # substitutions, which can themselves use gated constructs like
    # lookaround's (?=...)) need every module open, PC-4's own
    # `--features classes` precedent one gate wider.
    if ! pcrec_run "$PCREC" --features all -p pa -o "$d/pa.c" -- "$pa" \
            > "$d/pa.log" 2>&1; then
        echo "REFUSED-A" > "$WORKDIR/results/$id"
        return 0
    fi
    if ! pcrec_run "$PCREC" --features all -p pb -o "$d/pb.c" -- "$pb" \
            > "$d/pb.log" 2>&1; then
        echo "REFUSED-B" > "$WORKDIR/results/$id"
        return 0
    fi
    if ! gen_cc "definitions-oracle cell $id" "$CC" $GENCFLAGS \
            -I "$d" -I "$SCRIPT_DIR" \
            -o "$d/t" "$SCRIPT_DIR/definitions_oracle_driver.c" \
            "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc.log"
        echo "GCC-FAILED" > "$WORKDIR/results/$id"
        return 0
    fi
    gen_run "definitions-oracle cell $id" "$d/t" > "$WORKDIR/results/$id"
}

running=0
# [MACPORT] `wait -n` is bash 4.3+ and silently no-ops on this box's bash
# 3.2 — this was the concrete failure the manager's box survey named
# ("run_definitions_oracle.sh fails all 354 cells with 'result file
# truncated'", compounded by watchdog's own darwin gap). FIFO-throttle on
# tracked pids instead, tests/lib/run_san_group.sh's own precedent.
pids=()
while IFS=$'\t' read -r id pa pb _oracle_a _desc; do
    one_cell "$id" "$pa" "$pb" &
    pids+=("$!")
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then
        wait "${pids[0]}" 2>/dev/null || true
        pids=("${pids[@]:1}")
        running=$((running - 1))
    fi
done < "$CELLS"
wait

# A cell whose result file says REFUSED-A/REFUSED-B/GCC-FAILED never
# produced driver output for definitions_oracle_check.c to read — that is
# a harness defect (both Pattern A and Pattern B are meant to be
# ALWAYS-COMPILABLE core-syntax text) and must fail loudly rather than
# silently shrinking the comparison.
bad=0
for f in "$WORKDIR"/results/*; do
    head1=$(head -c 32 "$f")
    case "$head1" in
        REFUSED-A*|REFUSED-B*|GCC-FAILED*)
            id="$(basename "$f")"
            pa_pb=$(awk -F'\t' -v want="$id" '$1==want{print $2" / "$3}' "$CELLS")
            echo "FAIL: definitions-oracle: cell $id ($pa_pb) did not" >&2
            echo "FAIL: definitions-oracle:   compile/link/run: $head1" >&2
            bad=$((bad + 1))
            ;;
    esac
done
if [ "$bad" -gt 0 ]; then
    echo "FAIL: definitions-oracle: $bad of $ncells cells failed to" >&2
    echo "FAIL: definitions-oracle: produce comparable output" >&2
    exit 1
fi

# ---- the comparison --------------------------------------------------------
echo "definitions-oracle: $ncells cells generated (oracle: $([ "$have_oracle" = 1 ] && echo available || echo unavailable))"
"$WORKDIR/check" "$CELLS" "$WORKDIR/results"
exit $?
