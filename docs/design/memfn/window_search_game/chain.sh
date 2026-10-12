#!/usr/bin/env bash
# chain.sh WORKTREE -- the population run (lane wingame), after the box hold
# lifts. Builds this worktree's pcrec, regenerates the four bench subjects
# from a git-archive copy (sha-checked), runs the game over the population
# and writes data/ + data/summary.md. COUNTS ONLY: nothing here reads a clock.
set -u
W=${1:?worktree}
I=$W/docs/design/memfn/window_search_game
B=$W/build/wg
BENCH=/home/pcrec/projects/pcrec-bench
BREV=${BREV:-d359564f}
mkdir -p "$B" "$I/data"
log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*" >> "$B/chain.log"; }
log "chain start (bench $BREV)"
gnutimeout 600 make -C "$W" -j16 > "$B/make.log" 2>&1; log "make rc=$?"
if [ ! -f "$B/subj/syntax__t-256k.bin" ]; then
  rm -rf "$B/benchcopy"; mkdir -p "$B/benchcopy"
  git -C "$BENCH" archive "$BREV" bench pcrecbench | tar -x -C "$B/benchcopy"
  gnutimeout 600 python3 -B "$I/gen_subjects.py" "$B/benchcopy/bench" "$B/subj" > "$B/subj.log" 2>&1
  log "subjects rc=$? $(tr '\n' ' ' < "$B/subj.log")"
fi
rm -rf "$B/full"
( cd "$I" && gnutimeout 3600 nice python3 -B run_game.py "$W/build/pcrec" "$B/benchcopy/bench" \
    "$B/subj" "$W/tests/findings/default_ppm.tsv" "$W/tests" "$B/full" 150 ) > "$B/run.log" 2>&1
log "run_game rc=$?"
for f in spans spaninfo choices sim spanforms refine relcontrol; do cp "$B/full/$f.tsv" "$I/data/$f.tsv"; done
( cd "$I" && python3 -B summarize.py data ) > "$I/data/summary.md" 2> "$B/summ.err"
log "summarize rc=$?"

git -C "$W" add docs/design/memfn/window_search_game/data && \
  git -C "$W" commit -qm "wingame chain: population data + summary.md (counts only)" && log "committed $(git -C "$W" log -1 --format=%h)"
log "== wingame chain COMPLETE"
