#!/usr/bin/env bash
# docs/design/artsize_impl/probes/bench_acceptance.sh — [ART-SIZE] STEP 2's
# ACCEPTANCE SURVEY OVER pcrec-bench's OWN PATTERNS.
#
# WHY IT EXISTS. The acceptance survey behind §4.3a covered this repository's
# populations — the `.rxt` corpus, tests/resource, tests/vm, the fuzz gate —
# and pcrec-bench is a CONSUMER whose patterns live in a different repository
# and are compiled under FLAGS the corpus never uses. A cap that refuses one
# of them is a refusal a consumer meets without warning, which is the failure
# mode D84's acceptance-change rule exists to stop. (Manager's addition to the
# delivery bar, 2026-08-29; the bench is told in I-16/I-17.)
#
# READ-ONLY IN THE BENCH. This script reads pattern files under
# $BENCH_ROOT and writes NOTHING there (CLAUDE.md's scope mandate: pcrec-bench
# is the sibling repo, one-writer-each-way, and this lane is not its writer).
#
# EMIT ONLY, NO gcc. Every row is one `pcrec` invocation writing a `.c`; the
# generated code is never compiled. That keeps the survey cheap enough to run
# beside nothing else and keeps it measuring the QUANTITY THE CAPS READ —
# emitted source bytes, comment-excluded, via tests/lib/size_count.sh, which
# is the same rule the caps and the size log use.
#
# THE FLAG SETS ARE THE BENCH'S OWN, not a guess: testees/pcrec/configs.toml
# pins three, and `--features all` is in all of them (the email set's
# subbench.toml explains why: `factored.rx` needs the named-groups and
# recursion modules, so it is part of every pcrec testee's flags rather than a
# variant of the pattern).
#
# Usage: bash docs/design/artsize_impl/probes/bench_acceptance.sh [OUT.tsv]
# Env:   PCREC (default <root>/build/pcrec), BENCH_ROOT (default
#        /home/duxevents/pcrec-bench)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
BENCH_ROOT="${BENCH_ROOT:-/home/duxevents/pcrec-bench}"
OUT="${1:-/dev/stdout}"
. "$ROOT_DIR/tests/lib/size_count.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //" | tr -d '"'; }

# The population. The 14 files the census counted, plus the four email-specimen
# patterns the bench pins copies of (they live in THIS repo, are not under
# tests/**/*.rxt, and were therefore in neither survey).
mapfile -t FILES < <(
    ls "$BENCH_ROOT"/bench/email/patterns/*.rx \
       "$BENCH_ROOT"/bench/loglines/patterns/*.rx \
       "$ROOT_DIR"/docs/design/subroutines_measurements/email_specimen/*.rx 2>/dev/null
)

printf 'set\tname\tflags\tverdict\tbytes\tK\twhy\tengine\tdetail\n' > "$OUT"
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
        out="$WORK/o.c"; rm -f "$out"
        # shellcheck disable=SC2086
        err="$("$TIMEOUT_BIN" -s KILL 180 "$PCREC" -p rx $fs -o "$out" -- "$pat" 2>&1 >/dev/null)"
        rc=$?
        if [ "$rc" -eq 0 ]; then
            b="$(size_count_bytes "$out")"
            printf '%s\t%s\t%s\tACCEPT\t%s\t%s\t%s\t%s\t-\n' \
                "$set_tag" "$name" "${fs// /_}" "$b" \
                "$(stamp UNROLL_K "$out")" "$(stamp UNROLL_K_WHY "$out")" \
                "$(stamp ENGINE "$out")" >> "$OUT"
        else
            msg="$(printf '%s' "$err" | head -1)"
            verdict=REFUSE-other; raise=""
            case "$msg" in
                *"bytes of emitted code"*)     verdict=REFUSE-code-cap;  raise=--max-emit-code-bytes ;;
                *"bytes of emitted C source"*) verdict=REFUSE-total-cap; raise=--max-emit-bytes ;;
            esac
            detail="$msg"
            if [ -n "$raise" ]; then
                # the message quotes the artifact's own size; the smallest
                # override that re-accepts it is that size, so try exactly it.
                sz="$(printf '%s' "$msg" | grep -oE '[0-9]+' | head -1)"
                rm -f "$out"
                # shellcheck disable=SC2086
                if "$TIMEOUT_BIN" -s KILL 180 "$PCREC" -p rx $fs "$raise=$sz" -o "$out" -- "$pat" >/dev/null 2>&1; then
                    detail="$msg | re-accepted with $raise=$sz"
                else
                    detail="$msg | NOT re-accepted at $raise=$sz"
                fi
            fi
            printf '%s\t%s\t%s\t%s\t-\t-\t-\t-\t%s\n' \
                "$set_tag" "$name" "${fs// /_}" "$verdict" "$detail" >> "$OUT"
        fi
    done <<'FLAGSETS'
--features all
--features all --no-captures
--features all --engine=vm
FLAGSETS
done
