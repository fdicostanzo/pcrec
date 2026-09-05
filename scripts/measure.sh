#!/usr/bin/env bash
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
#
# A report is a PURE FUNCTION of its dependencies (Frank, same session,
# refining D35): the probe source, the ABI shim it includes, and the
# installed oracle. The header stamps all three, so validity is CHECKABLE
# WITHOUT RE-RUNNING: `scripts/measure.sh --stale` compares every report's
# stamps against the current tree and oracle and prints VALID or STALE with
# the reason. A report whose stamps match needs no regeneration, ever.
set -eu
cd "$(dirname "$0")/.."

ABI=tests/fuzz/pcre2_abi.h

oracle_now() {
    dpkg-query -W -f='${Package} ${Version}' libpcre2-8-0 2>/dev/null \
        || echo 'libpcre2 version UNKNOWN — record manually'
}

if [ "${1:-}" = "--stale" ]; then
    rc=0
    abi_now="$(git hash-object "$ABI")"
    orc_now="$(oracle_now)"
    for rep in docs/measurements/*.txt; do
        [ -e "$rep" ] || { echo "no reports found"; exit 0; }
        probe="$(basename "$rep" .txt)"
        src="tests/probes/${probe}.c"
        if [ ! -f "$src" ]; then
            echo "STALE  $rep — probe source $src no longer exists"; rc=1; continue
        fi
        want_src="$(sed -n 's/^# probe-blob: \([0-9a-f]*\).*/\1/p' "$rep")"
        want_abi="$(sed -n 's/^# abi-blob: \([0-9a-f]*\).*/\1/p' "$rep")"
        want_orc="$(sed -n 's/^# oracle: //p' "$rep")"
        cur_src="$(git hash-object "$src")"
        why=""
        [ "$want_src" = "$cur_src" ] || why="probe source changed"
        [ "$want_abi" = "$abi_now" ] || why="${why:+$why; }ABI shim changed"
        [ "$want_orc" = "$orc_now" ] || why="${why:+$why; }oracle changed ('$want_orc' -> '$orc_now')"
        if [ -z "$want_src" ] || [ -z "$want_abi" ]; then
            why="${why:+$why; }pre-stamp report (no dependency hashes) — regenerate once"
        fi
        if [ -n "$why" ]; then echo "STALE  $rep — $why"; rc=1
        else echo "VALID  $rep"; fi
    done
    exit $rc
fi

probe="${1:?usage: scripts/measure.sh <probe-name, e.g. probe_uprops> | --stale}"
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
    echo "# check validity without re-running: scripts/measure.sh --stale"
    echo "# date: $(date +%F)"
    echo "# repo: $(git rev-parse --short HEAD)$(git diff --quiet 2>/dev/null || echo ' +dirty')"
    echo "# probe-blob: $(git hash-object "$src") (git hash-object $src)"
    echo "# abi-blob: $(git hash-object "$ABI") ($ABI)"
    echo "# oracle: $(oracle_now)"
    echo "# compiler: $(gcc --version | head -1)"
    echo
    "$bin"
} > "$out"
echo "measure.sh: wrote $out"
