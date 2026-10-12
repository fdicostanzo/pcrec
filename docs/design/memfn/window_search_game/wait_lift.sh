#!/usr/bin/env bash
# wait_lift.sh WORKTREE -- the one waiter (lane wingame): polls WORKTREE/.lift
# every 60 s for at most 8 h, then runs chain.sh once.
W=${1:?worktree}
for i in $(seq 1 480); do
  [ -e "$W/.lift" ] && exec bash "$W/docs/design/memfn/window_search_game/chain.sh" "$W"
  sleep 60
done
printf '%s waiter expired without .lift\n' "$(date +%H:%M:%S)" >> "$W/build/wg/chain.log"
