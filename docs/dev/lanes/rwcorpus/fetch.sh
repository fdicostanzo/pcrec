#!/usr/bin/env bash
# Re-fetch the rwcorpus subject corpus into worktrees/.corpus/ and verify sha256.
# Usage: fetch.sh [--write-manifest]     (run from anywhere)
# Sequential, 2 s apart, GNU timeout on every network call.  Downloads are
# UNTRUSTED data: nothing from them is executed; prep.py only reads archives.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(git -C "$HERE" rev-parse --show-toplevel)
# worktrees/rwcorpus/.. = worktrees/ ; the corpus is a sibling of the worktree
CORPUS=${CORPUS:-$(dirname "$ROOT")/.corpus}
TO=$(command -v gnutimeout || command -v timeout)
mkdir -p "$CORPUS"
tail -n +2 "$HERE/sources.tsv" | while IFS=$'\t' read -r cls rel url lic date; do
    f="$CORPUS/$cls/$rel"
    [ -s "$f" ] && continue
    mkdir -p "$(dirname "$f")"
    "$TO" 600 curl -sfL --retry 2 -o "$f.part" "$url" && mv "$f.part" "$f" || { echo "FETCH FAIL $url" >&2; rm -f "$f.part"; }
    sleep 2
done
python3 -I "$HERE/prep.py" "$CORPUS" || exit 1
if [ "${1:-}" = "--write-manifest" ]; then
    python3 -I "$HERE/manifest.py" "$CORPUS" --write "$HERE/sources.tsv" "$HERE/manifest.tsv"
else
    python3 -I "$HERE/manifest.py" "$CORPUS" --check "$HERE/sources.tsv" "$HERE/manifest.tsv"
fi
