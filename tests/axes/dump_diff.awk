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
# Usage: awk -v BASEFILE=<default dump> -f dump_diff.awk <axis dump>
#
# Prints one summary line and, for MISMATCH/GAINED, one line per case
# (capped at 20, same convention as tests/possessify/possdiff_driver.c's
# divergence cap). Exit status: 0 if compared==keys && mismatches==0 &&
# gained==0 (missing keys, i.e. LOST, are reported as a population and are
# NOT by themselves a failure here — the caller decides whether this axis's
# own do-or-die posture permits them; see run_axes.sh's LOST-budget check).

BEGIN {
    FS = "\t"; OFS = "\t"
    if (BASEFILE == "") { print "dump_diff.awk: BASEFILE not set" > "/dev/stderr"; exit 2 }
    n_base = 0
    while ((getline line < BASEFILE) > 0) {
        split(line, f, "\t")
        key = f[1] ":" f[2]
        base_val[key] = f[5] "\t" f[6]
        base_kind[key] = f[3]
        base_seen[key] = 1
        n_base++
    }
    close(BASEFILE)
}
{
    key = $1 ":" $2
    axis_val[key] = $5 "\t" $6
    axis_seen[key] = 1
    n_axis++
    if (!(key in base_seen)) {
        gained++
        if (gained <= 20)
            print "GAINED (case ran under the axis but not under default — a new" \
                  " compile-population member, never expected): " key " kind=" $3 \
                  " out=" $6 > "/dev/stderr"
        next
    }
    if (base_val[key] != axis_val[key]) {
        mismatches++
        if (mismatches <= 20) {
            split(base_val[key], bv, "\t")
            print "MISMATCH " key " (" base_kind[key] "): default={trc=" bv[1] \
                  " out=" bv[2] "} axis={trc=" $5 " out=" $6 "}" > "/dev/stderr"
        }
    } else {
        agree++
    }
}
END {
    for (key in base_seen)
        if (!(key in axis_seen)) {
            lost++
            if (lost <= 20)
                print "LOST (case ran under default but not under the axis — the" \
                      " axis's block failed to compile/link/produce a binary for" \
                      " it): " key " kind=" base_kind[key] > "/dev/stderr"
        }
    printf "keys_base=%d keys_axis=%d agree=%d mismatches=%d lost=%d gained=%d\n", \
        n_base, n_axis, agree+0, mismatches+0, lost+0, gained+0
}
