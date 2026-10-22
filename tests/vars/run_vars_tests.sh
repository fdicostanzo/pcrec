#!/usr/bin/env bash
# tests/vars/run_vars_tests.sh — module `vars` ([VAR] M10): the corpus and
# its own oracle, in one section.
#
# THREE ARMS, AND THEY ANSWER THREE DIFFERENT QUESTIONS.
#
#   (1) THE CORPUS. `tests/harness/run.sh` over this directory: does the
#       compiled artifact answer what the `.rxt` file says? That is the same
#       question every other corpus directory asks, and it reaches this
#       directory through `test-corpus` too -- this arm exists so a targeted
#       `make test-vars` is one command and so the section's trailer names
#       this module.
#
#   (2) THE ORACLE. `verify_vars.py`: does the `.rxt` file say the RIGHT
#       thing? It quotemeta-splices each variable's value into the pattern as
#       a wrapped literal and asks libpcre2 the resulting ORDINARY pattern --
#       an authority outside pcrec entirely. Without this arm the corpus
#       would be scoring pcrec against expectations pcrec's own author wrote,
#       which is the shape `docs/dev/learnings.md` §3 opens with.
#
#   (3) THE ENTRIES (K129). `entries_driver.c` over a few artifacts: does
#       EVERY entry -- `_search`, `_match`, `_match_caps` and their `_in`
#       twins -- refuse an UNSET bare `${v}` with -8 on a subject where a
#       proof could answer first? The corpus's `gu` reaches `_search` alone,
#       and `_search` answered 0 here while `_match` refused: the
#       necessary-byte, start-set, root-width and end-window exits (and in
#       `_match`/`_match_caps` the K73 offset-0 rule) ran before the
#       variables (match_api.md §3.2¶2 says same checks, same order).
#       Each row names the exit its subjects reach.
#
# ARM 2 SKIPS LOUDLY when libpcre2 is absent (exit 3, PC-3's pattern) and the
# section reports the skip rather than reading green.
#
# Usage: bash tests/vars/run_vars_tests.sh
# Env: PCREC, CC, GENCFLAGS, PROCS — the harness's own (arm 3 reads PCREC,
# CC and GENCFLAGS).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

pass=0; fail=0; skip=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
note() { echo "SKIP: $1" >&2; skip=$((skip + 1)); }

# ---- arm 1: the corpus ----------------------------------------------------
echo "== [VAR] the corpus =="
if bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/"; then
    ok "the tests/vars/ corpus: every case answers what its .rxt file says"
else
    bad "the tests/vars/ corpus has failing cases — see above"
fi

# ---- arm 2: the splice oracle --------------------------------------------
echo
echo "== [VAR] the quotemeta-splice oracle =="
oracle_log="$(mktemp)"
trap 'rm -f "$oracle_log"' EXIT
python3 "$SCRIPT_DIR/verify_vars.py" "$SCRIPT_DIR"/*.rxt > "$oracle_log" 2>&1
orc=$?
cat "$oracle_log"
case "$orc" in
    0) ok "libpcre2 agrees with every splice-verifiable cell in tests/vars/" ;;
    3) note "libpcre2 is unavailable, so the splice oracle did not run — the corpus above is scored against its own file only (PC-3's shape)" ;;
    *) bad "the splice oracle disagrees with the corpus, or checked nothing — see above" ;;
esac

echo
echo "== [VAR] K129: every entry refuses an unset bare \${v} =="
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
ent_dir="$(mktemp -d)"
trap 'rm -f "$oracle_log"; rm -rf "$ent_dir"' EXIT
# encoding | pattern | hex subjects (- = empty) | the exit those subjects reach
nrow=0
while IFS='|' read -r enc pat subs why; do
    nrow=$((nrow + 1))
    d="$ent_dir/$nrow"; mkdir -p "$d"
    if ! "$TIMEOUT_BIN" 60 "$PCREC" -p rx --features all -e "$enc" --pattern "$pat" \
            -o "$d/art.c" > "$d/log" 2>&1 ||
       ! "$TIMEOUT_BIN" 120 $CC $GENCFLAGS -I"$d" -o "$d/e" \
            "$SCRIPT_DIR/entries_driver.c" "$d/art.c" >> "$d/log" 2>&1; then
        cat "$d/log"; bad "K129 [$enc] $pat: did not build"; continue
    fi
    # shellcheck disable=SC2086
    if out="$("$TIMEOUT_BIN" 30 "$d/e" $subs)"; then
        ok "K129 [$enc] $pat ($why): $out"
    else
        printf '%s\n' "$out"; bad "K129 [$enc] $pat ($why): an entry did not refuse"
    fi
done <<'ROWS'
byte|a${v}|- 626262 786178|the necessary-byte memchr
byte|[ab]${v}|- 636363|the start-set seek
byte|${v}abc|- 78|the root minimum width
byte|${v}x$|- 7979|the end-anchor window
byte|^${v}|- 61|no early exit (control)
utf8|${v}x|80 8078|a leading continuation byte
utf8|é${v}|- 7878|the necessary-byte memchr, utf8
utf8|${v}|80 8061|the offset-0 rule of the anchored entries
ROWS
[ "$nrow" -eq 8 ] || bad "K129: $nrow rows read, 8 expected"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks skipped: $skip"
[ "$fail" -eq 0 ] || exit 1
