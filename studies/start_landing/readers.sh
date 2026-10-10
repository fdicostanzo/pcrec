#!/bin/bash
# [START-LANDING] rev 2 (lane landrev, SL-C2/SL-C10): the READER CENSUS, derived
# by grep, never a hand list (STUDY; read-only on both trees).
#   readers.sh ROOT BENCH > readers.tsv
# For each regex in reader_tokens.tsv, every CHECK SURFACE that names it:
# ROOT's tests/ scripts/ tools/ cli/ lib/ docs/spec/ and src/ (design and dev
# documents are records, not readers, and are left out), and BENCH's
# (pcrec-bench, read only) tools/ pcrecbench/ testees/ bench/. For a file
# under ROOT/tests or ROOT/scripts it names the RUNNER: every Makefile line or
# tests/ script that names the file's basename (so a reader no target runs is
# visible as `runner -`). Output: class token file nlines runner.
set -u
ROOT=$1; BENCH=$2; H=$(cd "$(dirname "$0")" && pwd)
printf 'class\ttoken\tfile\tnlines\trunner\n'
grep -v '^#' "$H/reader_tokens.tsv" | while IFS=$'\t' read -r cls re why; do
    [ -n "$re" ] || continue
    for base in "$ROOT" "$BENCH"; do
        if [ "$base" = "$ROOT" ]; then dirs="tests scripts tools cli lib docs/spec src"; tag=pcrec; else dirs="tools pcrecbench testees bench"; tag=bench; fi
        for d in $dirs; do
            [ -d "$base/$d" ] || continue
            grep -rcIE --exclude-dir=out --exclude-dir=throughput --exclude-dir=subjects -e "$re" "$base/$d" 2>/dev/null | grep -v ':0$'
        done | while IFS=: read -r f n; do
            rel=${f#$base/}
            runner=-
            if [ "$tag" = pcrec ]; then
                case "$rel" in
                    tests/mech/sabotages/*) runner="make mech (row)" ;;
                    tests/*|scripts/*)
                        b=$(basename "$rel")
                        r=$( { grep -nF "$b" "$ROOT/Makefile" | sed 's/^/Makefile:/'; grep -rlF "$b" "$ROOT/tests" --include='*.sh' --include='*.py' | grep -vF "$rel" | sed "s|^$ROOT/||"; } 2>/dev/null | head -3 | tr '\n' ' ')
                        runner=${r:--} ;;
                    src/*|lib/*|cli/*) runner=build ;;
                    docs/spec/*) runner=spec ;;
                esac
            else runner="bench:${rel%%/*}"; fi
            printf '%s\t%s\t%s:%s\t%s\t%s\n' "$cls" "$re" "$tag" "$rel" "$n" "$runner"
        done
    done
done
