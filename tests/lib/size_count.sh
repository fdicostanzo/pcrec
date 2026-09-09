# tests/lib/size_count.sh — [ART-SIZE.1b] ONE implementation of "the
# census's own definition" of an artifact's SIZE: total source bytes minus
# COMMENT bytes (the [M6-READ] `/* ... */` and `//` prose the census's
# byte-attribution classifier buckets as `prose` — docs/dev/
# artifact_size_census.md §5). Sourced by tests/harness/run.sh at its
# compile site so the size ratchet's LOG rides the corpus's existing
# compile pass instead of adding one.
#
# WHY THIS IS A SEPARATE, SIMPLER RULE THAN THE CENSUS'S OWN CLASSIFIER,
# AND STILL "THE SAME DEFINITION" (verified, not assumed — see below). The
# census's `attribute_source()` (docs/dev/artifact_size_census/census.py)
# sorts every line into FIVE buckets (program/tables/prose/scaffold/main)
# by tracking brace depth through function and table bodies, because it
# needs to know WHICH function or table a line belongs to. This script only
# needs ONE bit per line — comment or not — and the census's own comment
# detection (`stripped.startswith("/*")` / `"//"` / in-block-comment state)
# is applied VERBATIM at both its top level and inside every nested
# function/table scan, with no depth-dependent variation: a line that opens
# a block comment is `prose` whether it appears at file scope or nested
# three braces deep inside the VM's one giant search function. That means a
# FLAT top-to-bottom scan with the identical three-state comment tracker
# (outside / in a `/* */` block / a `//` line) yields the exact same PROSE
# byte total as the census's depth-aware classifier, without needing brace
# tracking or function-name recognition at all. VERIFIED byte-for-byte
# against `census.py`'s own `attribute_source()` on both halves of a real
# split artifact (`a(b|c)+d`, VM engine): gen.c total 34,809 / prose
# 15,226 / non-prose 19,583, gen.h total 11,159 / prose 4,794 / non-prose
# 6,365 — this script's output and the census's `total - attrib['prose']`
# agree exactly on every one of those six numbers (docs/testing.md
# "The artifact-size log" has the transcript).
#
# WHY LC_ALL=C (K35, restated for this new site rather than trusted from an
# inherited export — every site guards individually per CLAUDE.md's
# instruction). MEASURED on the same real artifact above: under this box's
# ambient `en_US.UTF-8`, `awk`'s `length()` counts characters, not bytes,
# and a handful of pcrec's own [DD-14.FB]-annotation comments contain
# multi-byte UTF-8 punctuation (section-mark and similar glyphs) — this
# undercounted gen.c's prose bytes by 8 and gen.h's by 1, silently, with no
# error. Forcing `LC_ALL=C` inside this function (not just at the caller)
# makes `length()` byte-exact regardless of what locale sources it.
#
# size_count_bytes FILE [FILE ...]
#   Prints one integer: the sum, over every FILE given, of (that file's
#   total byte count minus its comment-line byte count). Reads each FILE
#   with `cat`, so it works identically whether FILE ends in a trailing
#   newline or not (a missing final newline is rare in this emitter's own
#   output, and if one occurred it would only miscount that one file's
#   last line by at most 1 byte — noted here rather than engineered around,
#   since this is a metrics LOG, not an exact pin: docs/dev/plan.md
#   [ART-SIZE.1b]'s own ruling is that per-pattern movement is a diff line
#   a reviewer reads, not a gate that must be byte-exact).
size_count_bytes() {
    local f total=0 n
    for f in "$@"; do
        [ -r "$f" ] || continue
        # Command substitution captured into a plain variable FIRST, then
        # added by itself — nesting `$(...)` directly inside `$((...))`
        # is ambiguous to bash's own parser once the substituted command
        # is this long (confirmed: the combined form threw "unexpected
        # EOF while looking for matching `)'" on this exact awk body), so
        # the two expansions are kept apart rather than fought with.
        n="$(LC_ALL=C awk '
            BEGIN { in_comment = 0; t = 0; prose = 0 }
            {
                lb = length($0) + 1
                t += lb
                line = $0
                gsub(/^[ \t]+/, "", line)
                if (in_comment) {
                    prose += lb
                    if (index($0, "*/") > 0) in_comment = 0
                    next
                }
                if (line ~ /^\/\*/) {
                    prose += lb
                    rest = substr($0, index($0, "/*") + 2)
                    if (index(rest, "*/") == 0) in_comment = 1
                    next
                }
                if (line ~ /^\/\//) { prose += lb; next }
            }
            END { print t - prose }
        ' "$f")"
        total=$((total + n))
    done
    printf '%d\n' "$total"
}

# size_count_row FILE_C FILE_H [PREFIX]
#   ONE-SUBPROCESS combination of size_count_bytes(FILE_C, FILE_H) with the
#   D46 stamp extraction (<PREFIX>_ENGINE/<PREFIX>_VM_RUNGS/
#   <PREFIX>_VM_PREFILTER, uppercased, read from FILE_C the same way
#   docs/dev/artifact_size_census/census.py's extract_stamps() does).
#   PREFIX is the artifact's OWN `-p` prefix (default "rx", matching every
#   caller before [TT-4M] STEP 2c — NEVER derived from FILE_C/FILE_H's
#   names, which are independent of `-p`: run.sh's unbatched path always
#   names its output "gen.c"/"gen.h" regardless of prefix, so a filename-
#   derived guess is wrong for the very call site this function has always
#   served). Prints one TSV line: `engine<TAB>rungs<TAB>
#   prefilter<TAB>bytes` (a field is empty when the artifact has no such
#   stamp — a DFA artifact carries no <PREFIX>_VM_RUNGS/<PREFIX>_VM_PREFILTER
#   at all). This column ORDER (stamps, then the byte count) is what lets a
#   caller splice this function's output straight into a wider row — see
#   tests/harness/run.sh's SIZELOG call site.
#
#   WHY THIS EXISTS SEPARATELY FROM size_count_bytes ABOVE. The harness's
#   compile site (tests/harness/run.sh) calls this on EVERY corpus compile,
#   thousands of times per run — MEASURED (docs/testing.md "The
#   artifact-size log"): the first cut of this instrumentation spawned 8
#   short-lived processes per compile (2x awk for size, 3x sed for stamps,
#   1x awk for a CPU-time sum, 1x cut for load, 1x grep to parse the `time`
#   builtin's own output) and cost 20.4% of the harness's own wall time on a
#   40-file/712-artifact sample (75.6s -> 91.1s) — nowhere near
#   docs/dev/plan.md [ART-SIZE.1b]'s "zero cost" charter. This function
#   folds the size scan and the stamp grep into ONE awk process (both files
#   are read by the SAME awk invocation; FNR==1 resets the comment-tracking
#   state at each file boundary so a file's own trailing open comment, if
#   any, cannot bleed into the next), and the call site does the CPU-time
#   sum and the load reading in pure bash builtins instead of forking `awk`/
#   `cut`/`grep` for them (bash's own `read` can source a file line
#   directly, `printf -v` formats a result without a subshell, and summing
#   two fixed-3-decimal numbers is exact integer arithmetic on milliseconds
#   with the decimal point stripped — see the call site's own comment).
#   Net: 8 subprocess spawns per compile down to 1.
size_count_row() {
    local fc="$1" fh="$2" prefix="${3:-rx}"
    # [TT-4M] STEP 2c FINDING, fixed here rather than worked around at the
    # call site: the stamp grep below used to hardcode the LITERAL macro
    # names `RX_ENGINE`/`RX_VM_PREFILTER`/`RX_VM_RUNGS`, which only exist
    # under those exact spellings when the artifact's own `-p` prefix is
    # "rx" — every caller in this tree until HARNESS_BATCH's per-member
    # `-c` sub-compiles (tests/harness/run.sh) used exactly that prefix, so
    # the assumption never showed up as false. A batch member compiled
    # under `-p hb000001` emits `HB000001_ENGINE` etc, and the old hardcoded
    # patterns matched nothing — SILENTLY, three empty stamp columns rather
    # than a loud failure, on every single batched SIZELOG row (measured:
    # `tests/base/dot.rxt:12` read `dfa` unbatched, `` (empty) batched,
    # bytes unaffected). Fixed by taking the prefix as an explicit
    # parameter (default "rx", unchanged for every existing caller) rather
    # than guessing from FILE_C/FILE_H's own names — a first attempt at
    # this fix derived it from FILE_H's basename instead, which is WRONG
    # for the very call site this function has always served: run.sh's
    # unbatched path names its output "gen.c"/"gen.h" always, independent
    # of `-p`, so that guess silently produced "GEN" instead of "RX" and
    # blanked the stamp on every unbatched row too — caught by re-running
    # this smoke on the unbatched leg, not assumed fixed from the batched
    # leg alone.
    local upfx
    upfx="$(printf '%s' "$prefix" | LC_ALL=C tr '[:lower:]' '[:upper:]')"
    LC_ALL=C awk -v FC="$fc" -v UPFX="$upfx" '
        BEGIN {
            in_comment = 0; t = 0; prose = 0; engine = ""; rungs = ""; prefilter = ""
            eng_pat = "^#define " UPFX "_ENGINE \""
            pf_pat  = "^#define " UPFX "_VM_PREFILTER \""
            rg_pat  = "^#define " UPFX "_VM_RUNGS "
        }
        FNR == 1 { in_comment = 0 }
        {
            lb = length($0) + 1
            t += lb
            line = $0
            gsub(/^[ \t]+/, "", line)
            if (in_comment) {
                prose += lb
                if (index($0, "*/") > 0) in_comment = 0
                next
            }
            if (line ~ /^\/\*/) {
                prose += lb
                rest = substr($0, index($0, "/*") + 2)
                if (index(rest, "*/") == 0) in_comment = 1
                next
            }
            if (line ~ /^\/\//) { prose += lb; next }
            if (FILENAME == FC) {
                if ($0 ~ eng_pat) {
                    engine = $0
                    sub(eng_pat, "", engine)
                    sub(/"$/, "", engine)
                } else if ($0 ~ pf_pat) {
                    prefilter = $0
                    sub(pf_pat, "", prefilter)
                    sub(/"$/, "", prefilter)
                } else if ($0 ~ rg_pat) {
                    rungs = $0
                    sub(rg_pat, "", rungs)
                    sub(/u$/, "", rungs)
                }
            }
        }
        END { printf "%s\t%s\t%s\t%d\n", engine, rungs, prefilter, t - prose }
    ' "$fc" "$fh"
}
