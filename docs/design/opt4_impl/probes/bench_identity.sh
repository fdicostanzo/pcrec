#!/usr/bin/env bash
# docs/design/opt4_impl/probes/bench_identity.sh — [OPT-4] STEP 3's
# NOTHING-MOVES SURVEY OVER pcrec-bench's OWN PATTERNS.
#
# WHY IT EXISTS, and why it is a DIFFERENT question from
# `artsize_impl/probes/bench_acceptance.sh`'s. [ART-SIZE] asked whether a cap
# would REFUSE a consumer's pattern. This row cannot refuse anything — it only
# ever makes an artifact smaller — so the question here is the opposite one:
# does it move an artifact it has no business moving? The claim being surveyed
# is design-note §8's last line, "13 of 14 stamps byte-identical", restated
# over the population [ART-SIZE] established is the right one (18 patterns, not
# 14) and asserted rather than eyeballed.
#
# THE CLAIM. A pattern with no counted repeat of replication factor >= 2 has
# nothing to collapse, so its artifact must be BYTE-IDENTICAL to the one the
# same compiler emits with the axis denied. The exceptions, if any, are the
# patterns that DO carry such a repeat, and they are named in the output rather
# than assumed absent.
#
# READ-ONLY IN THE BENCH, on bench_acceptance.sh's own terms: this script reads
# pattern files under $BENCH_ROOT and writes NOTHING there (CLAUDE.md's scope
# mandate — pcrec-bench is the sibling repo and this lane is not its writer).
#
# EMIT ONLY, NO gcc, and `-o -` so each comparison is over ONE self-contained
# file: with `-o FILE` the two artifacts differ in their `#include` line alone
# and every row would read as changed. (Measured: it did, on the first run of
# the corpus-delta harness this probe was factored out of.)
#
# Usage: bash docs/design/opt4_impl/probes/bench_identity.sh
# Env:   PCREC (default <root>/build/pcrec), BENCH_ROOT (default
#        /home/duxevents/pcrec-bench)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
BENCH_ROOT="${BENCH_ROOT:-/home/duxevents/pcrec-bench}"
. "$ROOT_DIR/tests/lib/size_count.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //" | tr -d '"'; }

# The SAME population bench_acceptance.sh surveys — the three email patterns,
# the eleven loglines patterns, and the four email-specimen patterns in THIS
# repo that the bench pins copies of.
mapfile -t FILES < <(
    ls "$BENCH_ROOT"/bench/email/patterns/*.rx \
       "$BENCH_ROOT"/bench/loglines/patterns/*.rx \
       "$ROOT_DIR"/docs/design/subroutines_measurements/email_specimen/*.rx 2>/dev/null
)
if [ "${#FILES[@]}" -eq 0 ]; then
    echo "SKIP: no bench patterns found under $BENCH_ROOT (is the sibling repo present?)" >&2
    exit 0
fi

n=0; nident=0; nmoved=0
printf '%-22s %-30s %-9s %-16s %s\n' set name verdict lang detail
for f in "${FILES[@]}"; do
    [ -r "$f" ] || continue
    pat="$(cat "$f")"
    name="$(basename "$f" .rx)"
    case "$f" in
        *"/bench/email/"*)    set_tag=bench-email ;;
        *"/bench/loglines/"*) set_tag=bench-loglines ;;
        *)                    set_tag=email-specimen ;;
    esac
    while IFS= read -r fs; do
        [ -n "$fs" ] || continue
        a="$WORK/a.c"; b="$WORK/b.c"
        # shellcheck disable=SC2086
        "$TIMEOUT_BIN" -s KILL 180 "$PCREC" -p rx $fs -o - -- "$pat" > "$a" 2>/dev/null || {
            printf '%-22s %-30s %-9s %-16s %s\n' "$set_tag" "$name" REFUSED - "${fs// /_}"; continue; }
        # shellcheck disable=SC2086
        "$TIMEOUT_BIN" -s KILL 180 "$PCREC" -p rx $fs -fno-prefilter-collapse -o - -- "$pat" > "$b" 2>/dev/null || {
            printf '%-22s %-30s %-9s %-16s %s\n' "$set_tag" "$name" DENY-REFUSED - "${fs// /_}"; continue; }
        n=$((n+1))
        lang="$(stamp VM_PREFILTER_LANG "$a")"; [ -n "$lang" ] || lang="(no prefilter)"
        if cmp -s "$a" "$b"; then
            nident=$((nident+1))
        else
            nmoved=$((nmoved+1))
            printf '%-22s %-30s %-9s %-16s %s\n' "$set_tag" "$name" MOVED "$lang" \
                "${fs// /_} $(size_count_bytes "$a") vs $(size_count_bytes "$b") code B; why=$(stamp VM_PREFILTER_LANG_WHY "$a")"
        fi
    done <<'FLAGSETS'
--features all
--features all --no-captures
--features all --engine=vm
FLAGSETS
done

printf '\nbench-identity: %d emits over %d pattern files: %d byte-identical, %d moved\n' \
       "$n" "${#FILES[@]}" "$nident" "$nmoved"
