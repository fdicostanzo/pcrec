#!/bin/bash
# scripts/measure.sh — build and run a design probe from tests/probes/,
# archiving its output as a diffable report in docs/measurements/ (D35).
#
# The report filename is STABLE per probe (not dated) ON PURPOSE: a
# re-measurement lands as a git diff against the previous report, so "what
# changed since last time" is one `git diff` away (Frank, 2026-08-12). The
# run's date and source information live in the header lines; history lives
# in git log. The report is HISTORICAL EVIDENCE for reviews — never an
# oracle, never something a check reads (D35; the live re-measured checks
# in tests/registry/ are the strong form).
set -eu
cd "$(dirname "$0")/.."
probe="${1:?usage: scripts/measure.sh <probe-name, e.g. probe_uprops>}"
src="tests/probes/${probe}.c"
[ -f "$src" ] || { echo "measure.sh: no such probe: $src" >&2; exit 1; }
mkdir -p docs/measurements
out="docs/measurements/${probe}.txt"
bin="$(mktemp /var/tmp/measure.XXXXXX)"
trap 'rm -f "$bin"' EXIT
TMPDIR=/var/tmp gcc -I tests/fuzz -o "$bin" "$src" -ldl
{
    echo "# ${probe} — archived measurement report (D35: evidence, never an oracle)"
    echo "# regenerate: scripts/measure.sh ${probe}   (git diff shows what changed)"
    echo "# date: $(date +%F)"
    echo "# repo: $(git rev-parse --short HEAD)$(git diff --quiet 2>/dev/null || echo ' +dirty')"
    echo "# oracle: $(dpkg-query -W -f='${Package} ${Version}' libpcre2-8-0 2>/dev/null || echo 'libpcre2 version UNKNOWN — record manually')"
    echo "# compiler: $(gcc --version | head -1)"
    echo
    "$bin"
} > "$out"
echo "measure.sh: wrote $out"
