#!/usr/bin/awk -f
# tests/axes/dump_diff.awk — [CHK-2] piece 2's comparator.
#
# Compares two RXTDUMP files (tests/harness/run.sh's RXTDUMP=, this suite's
# own hook) produced from the SAME .rxt corpus under two different compiler
# axes: the file named by BASEFILE (the default build) and stdin/ARGV[1]
# (one axis build). Each line is
#     <file>\t<line>\t<kind>\t<route>\t<trc>\t<out>
# and the KEY is <file>:<line> — unique because .rxt cases are one per
# source line (tests/harness/run.sh's own RXTDUMP doc comment). The VALUE
# compared is <trc>\t<out> — the raw outcome of running the compiled test
# binary on that case's subject, before either run's pass/fail machinery
# touches it. This is deliberately NOT "do the two runs' pass/fail counts
# agree": two runs can have equal counts while disagreeing on which
# specific cases passed (tests/axes/CLAUDE.md's own rationale for the hook).
#
# THE CLASSIFICATION (manager's rule, 2026-08-26, from the first full-corpus
# sweep's own findings — four axes FAILED with zero genuine answer
# disagreement, purely because the comparator had only two buckets,
# AGREE/MISMATCH+LOST+GAINED, and every documented, EXPECTED shape a
# tuning axis can legitimately produce landed in the failing ones). Per
# BASE key, in this order:
#
#   AGREE            trc and out identical on both sides.
#   REFUSED          the axis side is a compile-time refusal (tests/harness/
#                    run.sh's RXTDUMP REFUSED producer: pcrec itself
#                    declined the pattern under this axis's flag). This
#                    script does NOT know whether a given axis's own
#                    documented limit produced it — that is axis-specific
#                    knowledge dump_diff.awk has no business holding (it
#                    would be re-deriving tests/spec/tuning.md's own axis
#                    table inside a generic comparator) — so every REFUSED
#                    case is reported as its own bucket, with the pcrec
#                    diagnostic TEXT carried in the rows stream, and
#                    run_axes.sh (which DOES hold the per-axis expected-
#                    refusal pattern) does the documented-vs-undocumented
#                    split.
#   BUDGET           neither side is REFUSED, the two disagree, and EITHER
#                    side's trc is 3 (a give-up: steps/frames/work — driver.c
#                    exits 3 for all three uniformly) or 124 (a per-case
#                    timeout, tests/harness/run.sh's own TIMEOUT_BIN wrap).
#                    tuning.md §2.5's "identity holds modulo which budget
#                    binds" is the spec sentence this extends to the
#                    harness's own per-case wall timeout: a budget boundary
#                    moving under a denied optimization is not an answer
#                    disagreement.
#   LOST             the axis produced NO record for this key at all —
#                    neither an ordinary case line nor a REFUSED line. What
#                    remains after the REFUSED producer above: a PROCS
#                    worker that vanished, a whole FILE that failed to
#                    parse, or some other structural gap — never routine,
#                    always worth a name.
#   MISMATCH         neither side is REFUSED or budget-bound, and the two
#                    disagree: a genuine answer difference (match vs
#                    nomatch, a different span, a different capture).
#   GAINED           the axis produced a record for a key the BASELINE
#                    never had — never documented as possible for any axis.
#
# Usage: awk -v BASEFILE=<default dump> [-v ROWSFILE=<path>] -f dump_diff.awk <axis dump>
#   ROWSFILE, if given, receives ONE MACHINE-READABLE ROW per non-AGREE key:
#     <classification>\t<key>\t<base_trc>\t<base_out>\t<axis_trc>\t<axis_out-or-reason>
#   — uncapped, for run_axes.sh's own REFUSED-text matching and floor
#   counting. Human-readable detail (capped at 20 per bucket, the
#   tests/possessify/possdiff_driver.c divergence-cap convention) still
#   goes to stderr regardless of ROWSFILE.
#
# Prints one summary line to stdout:
#   keys_base=N keys_axis=N agree=N budget=N refused=N lost=N gained=N mismatches=N
# Exit status is always 0 — classification is this script's whole job;
# PASS/FAIL is run_axes.sh's call, made only after it has re-split REFUSED
# into documented/undocumented.

BEGIN {
    FS = "\t"; OFS = "\t"
    if (BASEFILE == "") { print "dump_diff.awk: BASEFILE not set" > "/dev/stderr"; exit 2 }
    n_base = 0
    while ((getline line < BASEFILE) > 0) {
        split(line, f, "\t")
        key = f[1] ":" f[2]
        base_trc[key] = f[5]
        base_out[key] = f[6]
        base_kind[key] = f[3]
        base_seen[key] = 1
        n_base++
    }
    close(BASEFILE)
}
{
    key = $1 ":" $2
    n_axis++
    if (!(key in base_seen)) {
        gained++
        emit_row("GAINED", key, "", "", $5, $6)
        if (gained <= 20)
            print "GAINED (case ran under the axis but not under default — a new" \
                  " compile-population member, never expected): " key " kind=" $3 \
                  " out=" $6 > "/dev/stderr"
        next
    }
    axis_trc[key] = $5
    axis_out[key] = $6
    axis_seen[key] = 1
}
function emit_row(cls, key, btrc, bout, atrc, aout) {
    if (ROWSFILE != "")
        printf "%s\t%s\t%s\t%s\t%s\t%s\n", cls, key, btrc, bout, atrc, aout >> ROWSFILE
}
END {
    for (key in base_seen) {
        if (!(key in axis_seen)) {
            lost++
            emit_row("LOST", key, base_trc[key], base_out[key], "", "")
            if (lost <= 20)
                print "LOST (case ran under default but not under the axis — no" \
                      " record at all, not even a REFUSED one — a structural gap" \
                      " beyond a documented compile-time refusal): " key \
                      " kind=" base_kind[key] > "/dev/stderr"
            continue
        }
        b_trc = base_trc[key]; b_out = base_out[key]
        a_trc = axis_trc[key]; a_out = axis_out[key]
        if (a_trc == "REFUSED") {
            refused++
            emit_row("REFUSED", key, b_trc, b_out, a_trc, a_out)
            if (refused <= 20)
                print "REFUSED " key " (" base_kind[key] "): axis pattern-compile" \
                      " refused it — \"" a_out "\"" > "/dev/stderr"
            continue
        }
        if (b_trc == a_trc && b_out == a_out) {
            agree++
            continue
        }
        if (b_trc == "3" || b_trc == "124" || a_trc == "3" || a_trc == "124") {
            budget++
            emit_row("BUDGET", key, b_trc, b_out, a_trc, a_out)
            if (budget <= 20)
                print "BUDGET-BOUND " key " (" base_kind[key] "): default={trc=" \
                      b_trc " out=" b_out "} axis={trc=" a_trc " out=" a_out \
                      "} — a give-up/timeout on one side, not an answer" \
                      " disagreement" > "/dev/stderr"
            continue
        }
        mismatches++
        emit_row("MISMATCH", key, b_trc, b_out, a_trc, a_out)
        if (mismatches <= 20)
            print "MISMATCH " key " (" base_kind[key] "): default={trc=" b_trc \
                  " out=" b_out "} axis={trc=" a_trc " out=" a_out "}" > "/dev/stderr"
    }
    printf "keys_base=%d keys_axis=%d agree=%d budget=%d refused=%d lost=%d gained=%d mismatches=%d\n", \
        n_base, n_axis, agree+0, budget+0, refused+0, lost+0, gained+0, mismatches+0
}
