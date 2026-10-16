#!/bin/sh
# clsmask_candidates: the whole measurement, end to end (box rule: CPUs 0-3,
# -j4). Writes WORK (default build/cs, gitignored) and results/.
#   docs/dev/clsmask_candidates/run_all.sh   (from the repo root, after make)
# Needs: pcrec-bench read-only at ../pcrec-bench (archived into WORK, its
# subject generators run IN THE COPY), the [REGIME-CORPUS] cache at
# worktrees/.corpus (or CORPUS=...).
set -e
D=docs/dev/clsmask_candidates
W=${WORK:-build/cs}
CORPUS=${CORPUS:-$(git rev-parse --path-format=absolute --git-common-dir)/../worktrees/.corpus}
BENCH=${BENCH:-$(git rev-parse --path-format=absolute --git-common-dir)/../../pcrec-bench}
WS=studies/walk_survey
T="taskset -c 0-3"
mkdir -p "$W/bench"
git -C "$BENCH" archive HEAD bench pcrecbench | tar -x -C "$W/bench"
(cd "$W/bench" && for s in bench/*/; do for g in gen_subjects.py gen_throughput_subjects.py; do
    [ -f "$s$g" ] && $T python3 "$s$g" > /dev/null; done; done)
$T python3 $WS/pop_corpus.py build/pcrec . "$W/subj_corpus" > "$W/pop_corpus.tsv"
python3 $WS/pop_bench.py "$W/bench" > "$W/pop_bench.tsv"
python3 -I $D/pop_rw.py docs/dev/lanes/rwquest/questions.tsv "$CORPUS" "$W/subj_rw" > "$W/pop_rw.tsv"
python3 -I $D/pop_ref.py "$PWD/$W/bench" "$PWD/$W/subj_rw" > "$W/pop_ref.tsv"
$T python3 $D/compile_pop.py build/pcrec "$W" "$W"/pop_corpus.tsv "$W"/pop_bench.tsv "$W"/pop_rw.tsv "$W"/pop_ref.tsv > "$W/compiled.tsv"
$T python3 $D/run_pop.py "$W" "$CORPUS" 4 > "$W/run_pop.log" 2>&1
$T python3 $D/validate.py "$W" 40 > $D/results/validation.txt 2>&1
$T python3 $D/analyze.py "$W" $D/results > /dev/null
$T python3 $D/census.py "$W" $D/results > $D/results/census.txt
gzip -c "$W/runs.tsv" > $D/results/runs.tsv.gz
gzip -c "$W/static.tsv" > $D/results/static.tsv.gz
gzip -c "$W/compiled.tsv" > $D/results/compiled.tsv.gz
echo "== clsmask_candidates run_all COMPLETE"
