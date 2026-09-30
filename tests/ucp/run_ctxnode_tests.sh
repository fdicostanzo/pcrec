#!/usr/bin/env bash
# tests/ucp/run_ctxnode_tests.sh — [UCP] U2's own checks: the CONTEXT NODE
# (A_CTX), T3's recognizer and the per-machine context-set table
# (docs/design/ucp_design.md §2.2-§2.4, §6's U2 row).
#
#   1. THE CORPUS: tests/ucp/ctxnode.rxt (the overlap witnesses, T3's rows
#      and declines, the startpos seeds, UCP `\b` under `-e byte`) and
#      tests/utf8/axis13_ctx_illformed.rxt (§2.3's hazard cells), through
#      tests/harness/run.sh — pcrec's live answers against the oracle's.
#   2. THE SAME CORPUS UNDER `-fno-ctx-node` — the GEN-4-SHAPED CHECK. With
#      T3's `ctx-node` row DENIED the walk must reach the `lookaround` row, a
#      sound VM sub-match, and answer every cell identically; a denial that
#      fell through to anything else (an erased lookaround, a truncated set)
#      is red here and nowhere else, because on the default path the row it
#      would replace never fires. Sabotage S342 is its failing direction.
#   3. THE ROUTE, BY NAMED MANIFEST (r49's rule — a population is a list, not
#      a count): every row of tests/ucp/ctxnode_route.tsv compiles to the
#      engine its `default` column names, and to its `denied` column's under
#      `-fno-ctx-node`. The manifest is the U2 mover census's own list
#      (a one-character lookaround that moved VM -> DFA) plus declines that
#      must stay VM; a floor on its size fails an emptied manifest (K35).
#
# Prints `checks passed: N` / `checks failed: N` (the mech `ctxnode` arm
# scrapes them). Exit 1 on any failure.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-ctxnode.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }

CORPUS=("$ROOT_DIR/tests/ucp/ctxnode.rxt" "$ROOT_DIR/tests/utf8/axis13_ctx_illformed.rxt")

# One harness run over the corpus with RXTFLAGS=$1; records its two counts.
corpus_run() {
    local flags="$1" label="$2" log="$WORKDIR/harness_$3.log"
    RXTFLAGS="$flags" PCREC="$PCREC" bash "$ROOT_DIR/tests/harness/run.sh" \
        "${CORPUS[@]}" > "$log" 2>&1
    local p f
    p="$(grep -m1 '^cases passed:' "$log" | grep -oE '[0-9]+')"
    f="$(grep -m1 '^cases failed:' "$log" | grep -oE '[0-9]+')"
    if [ -z "$p" ] || [ -z "$f" ]; then
        bad "$label: the harness printed no counts"; tail -5 "$log"; return
    fi
    if [ "$p" -lt 200 ]; then
        bad "$label: only $p cases ran (floor 200) — the corpus lost its population"
    elif [ "$f" -ne 0 ]; then
        bad "$label: $f of $((p + f)) cases disagree with the oracle"
        grep -m10 'expected' "$log"
    else
        ok "$label: $p cases agree with the oracle"
    fi
}

echo "== [UCP] U2 1. the corpus, default =="
corpus_run "" "ctxnode corpus (default)" default
echo "== [UCP] U2 2. the corpus with T3's ctx-node row DENIED (-fno-ctx-node) =="
corpus_run "-fno-ctx-node" "ctxnode corpus (-fno-ctx-node)" denied

echo "== [UCP] U2 3. the route, by named manifest (tests/ucp/ctxnode_route.tsv) =="
engine_of() {
    "$TIMEOUT_BIN" 120 "$PCREC" --features all -e "$1" $2 -p rx -o "$WORKDIR/r.c" \
        --pattern "$3" >/dev/null 2>&1 || { echo REFUSED; return; }
    sed -n 's/^#define RX_ENGINE "\(.*\)"$/\1/p' "$WORKDIR/r.c" | head -1
}
rows=0
while IFS=$'\t' read -r id enc flags want_def want_den pat; do
    case "$id" in ''|\#*) continue ;; esac
    rows=$((rows + 1))
    [ "$flags" = "-" ] && flags=""
    got_def="$(engine_of "$enc" "$flags" "$pat")"
    got_den="$(engine_of "$enc" "$flags -fno-ctx-node" "$pat")"
    if [ "$got_def" = "$want_def" ] && [ "$got_den" = "$want_den" ]; then
        pass=$((pass + 1))
    else
        bad "route $id [$enc] '$pat': default $got_def (want $want_def), -fno-ctx-node $got_den (want $want_den)"
    fi
done < "$SCRIPT_DIR/ctxnode_route.tsv"
if [ "$rows" -lt 100 ]; then
    bad "the route manifest has $rows rows (floor 100) — the mover population was emptied"
else
    ok "route manifest: $rows rows read"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
