# tests/lib/shard_split.sh — ONE portable "split a line file into N shard
# files", the shape ncpu.sh established for CPU counts.
#
# WHY THIS EXISTS. Seven sweeps wrote `split -n l/N -d`, which is GNU-only.
# BSD split (darwin's /usr/bin/split) rejects `-n`, and every one of those
# sites carried a fallback `|| cp pats sh/p00; NSHARD=1` that turned the
# failure into a SILENT single shard: run_anchored_diff.sh's 3493-pattern
# sweep then ran serial (~55 min under load, S189's re-drive, s189tri_report.md)
# and PROCS=4 changed nothing. A fallback that hides the loss of the parallelism
# it exists to provide reads as "slow", not "broken".
#
# Usage: `. tests/lib/shard_split.sh`, then
#   shard_split N INFILE OUTPREFIX     # writes OUTPREFIX00, OUTPREFIX01, ...
# Contiguous LINE CHUNKS, ceil(lines/N) each (so fewer than N files when the
# input is short). Pure awk + wc: no GNU split needed.

shard_split() {
    _ss_n="$1"; _ss_in="$2"; _ss_pre="$3"
    _ss_lines="$(wc -l < "$_ss_in" | tr -d ' ')"
    [ "$_ss_n" -ge 1 ] 2>/dev/null || _ss_n=1
    _ss_per=$(( (_ss_lines + _ss_n - 1) / _ss_n ))
    [ "$_ss_per" -ge 1 ] || _ss_per=1
    awk -v per="$_ss_per" -v pre="$_ss_pre" \
        '{ print > sprintf("%s%02d", pre, int((NR - 1) / per)) }' "$_ss_in"
}
