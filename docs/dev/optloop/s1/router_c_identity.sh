#!/usr/bin/env bash
# S1 review C1's reproducible recipe: is router's arm (c) (HEAD compiled
# with -fno-req-run) program-identical to 25b1984f's own artifact (the
# pin S1's cost model solves its per-step constant from, litscan_s1.md
# §4)? git-archives both pins to a scratch dir, builds each with the
# pinned compiler, emits router's pattern (/user|/users) from each, and
# diffs. Cited from litscan_s1.md §10. Recorded output:
# router_c_identity_output.txt (this script's own run, 2026-09-25).
#
# Usage: SCR=<scratch> REPO=/Users/fdicostanzo/pcrec HEAD=<head-ref> \
#        ./router_c_identity.sh
set -euo pipefail
SCR="${SCR:?set SCR to a scratch directory}"
REPO="${REPO:?set REPO to the pcrec worktree to archive HEAD from}"
HEADREF="${HEAD:-HEAD}"
PIN=25b1984f
CC=gcc-16

mkdir -p "$SCR/pin_25b1984f" "$SCR/pin_head"
git -C "$REPO" archive "$PIN" | tar -x -C "$SCR/pin_25b1984f"
git -C "$REPO" archive "$HEADREF" | tar -x -C "$SCR/pin_head"

make -C "$SCR/pin_25b1984f" -j4 CC=$CC build/pcrec >/dev/null
make -C "$SCR/pin_head" -j4 CC=$CC build/pcrec >/dev/null

# 25b1984f predates -fno-req-run (predates req-run itself, abi 27): its
# default artifact for this pattern IS what "no req-run pre-check" means
# there, and its CLI is positional (no --pattern flag yet).
"$SCR/pin_25b1984f/build/pcrec" -p rx -o "$SCR/router_pin25b1984f.c" \
    '/user|/users'
# HEAD: arm (c), -fno-req-run.
"$SCR/pin_head/build/pcrec" -p rx -o "$SCR/router_head_fno_req_run.c" \
    --pattern '/user|/users' -fno-req-run

echo "=== diff: 25b1984f default vs HEAD -fno-req-run ==="
diff -u "$SCR/router_pin25b1984f.c" "$SCR/router_head_fno_req_run.c" || true
echo "=== end diff ==="
echo "(a clean run shows only: the header comment line, the new stamp"
echo " #defines a later feature introduced, and rx_info's .abi/.vars/"
echo " .nvars fields -- no change to any function body)"
