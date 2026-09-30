#!/usr/bin/env bash
# tests/anchored/run_anchored_dead_entry.sh — the anchored match-here entry
# ENTERED AT THE DEAD STATE: a machine entered dead has no match, and
# `<prefix>_match` must say -1 without reading the accept table.
#
# =========================================================================
# THE DEFECT THIS WITNESSES (triu2_report.md §4, fixed by lane ucpu3)
# =========================================================================
# [ENG-ABS]'s anchored machine has no start-anywhere self-loop, so where a
# match needs a LEFT context its no-context start (`s0`, used at pos 0) or a
# seed cell (the start chosen from subject[pos - 1]) is the DEAD state. The
# shared scan loop's first statement is the accept probe, which read
# `is_accepting[-1]` there: 57 SIGSEGVs and 2 divergences in
# run_anchored_diff.sh once [UCP] U2 routed one-character lookbehinds to the
# DFA. The fix is the direction's `dead_entry` statement in emit_dfa.c,
# emitted where `dfa_entry_can_be_dead` says the entry can be dead.
#
# THE WITNESSES REACH BOTH DEAD ENTRIES, and the reach is asserted off the
# artifact rather than assumed: `(?<=a)b` and `(?<*a)b` start dead at pos
# 0 (the initializer's no-context value is -1) AND for a non-`a` context
# byte (a -1 seed cell); `(?<!a)b` starts live at pos 0 and dead after an
# `a`. Each must select the DFA engine and the unwrapped form, or it no
# longer exercises the entry it names.
#
# =========================================================================
# THREE ARMS
# =========================================================================
#   [reach]   the artifact's anchored machine CAN start dead (read from its
#             emitted seed table and initializer, never from a stamp);
#   [answer]  `_match` and `_match_caps` agree with python3 `re` on every
#             cell below (oracle-verified 2026-09-29; `(?<*a)b` is PCRE2's
#             non-atomic positive lookbehind, which with no capture inside
#             matches exactly what `(?<=a)b` does, so it shares those cells);
#   [asan]    the same cells under -fsanitize=address, which reports the
#             out-of-bounds accept read directly rather than through whatever
#             byte happened to precede the table. SKIPPED LOUDLY where the
#             compiler cannot build an ASan binary; the [answer] arm then
#             stands alone and can miss a read that lands on a zero byte.
#
# FAILING DIRECTION, measured 2026-09-29 on the unfixed compiler (lane/ucpu2
# 61cbc894 + the triu2/tri220 merges): [answer] red on every witness (driver
# killed by SIGSEGV, rc 139, darwin) and [asan] red on every witness
# (global-buffer-overflow, 1 byte before <p>_anchored_is_accepting).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: anchored-dead-entry: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

cat > "$WORKDIR/pos.cells" <<'CELLS'
- 0 -1
a 0 -1
a 1 -1
b 0 -1
b 1 -1
ab 0 -1
ab 1 1
ab 2 -1
bb 0 -1
bb 1 -1
bb 2 -1
ba 0 -1
ba 1 -1
ba 2 -1
abab 0 -1
abab 1 1
abab 2 -1
abab 3 1
abab 4 -1
bab 0 -1
bab 1 -1
bab 2 1
bab 3 -1
CELLS
cat > "$WORKDIR/neg.cells" <<'CELLS'
- 0 -1
a 0 -1
a 1 -1
b 0 1
b 1 -1
ab 0 -1
ab 1 -1
ab 2 -1
bb 0 1
bb 1 1
bb 2 -1
ba 0 1
ba 1 -1
ba 2 -1
abab 0 -1
abab 1 -1
abab 2 -1
abab 3 -1
abab 4 -1
bab 0 1
bab 1 -1
bab 2 -1
bab 3 -1
CELLS

# Can this compiler build an AddressSanitizer binary at all? Asked once, on a
# trivial program, so a missing runtime is a SKIP and never a red witness.
asan=0
printf 'int main(void){return 0;}\n' > "$WORKDIR/probe.c"
if $CC -fsanitize=address -o "$WORKDIR/probe" "$WORKDIR/probe.c" >/dev/null 2>&1 \
        && "$WORKDIR/probe" >/dev/null 2>&1; then
    asan=1
else
    echo "SKIP: [asan] $CC cannot build and run an -fsanitize=address binary here — the [answer] arm stands alone" >&2
fi

# <pattern>~<cells file>
WITNESSES='
(?<=a)b~pos
(?<*a)b~pos
(?<!a)b~neg
'
nwit=0; reached=0
while IFS='~' read -r pat cells; do
    [ -n "${pat:-}" ] || continue
    nwit=$((nwit + 1))
    d="$WORKDIR/w$nwit"; mkdir -p "$d"
    if ! pcrec_run "$PCREC" -p on --features all -o "$d/on.c" --pattern "$pat" >/dev/null 2>&1; then
        bad "[reach] '$pat' did not compile"; continue
    fi
    if ! grep -q '^#define ON_ENGINE "dfa"' "$d/on.c" || ! grep -q '^#define ON_DFA_MATCH "unwrapped"' "$d/on.c"; then
        bad "[reach] '$pat' no longer selects the DFA engine's unwrapped anchored form — it does not reach the entry this file witnesses"
        continue
    fi
    # THE DEAD START, from matcher text: a -1 cell in the anchored seed table,
    # or -1 as the initializer's no-context value.
    dead="$(awk '
        /static const (unsigned )?short on_anchored_seed_state\[/ { ins = 1; next }
        ins && /\};/ { ins = 0 }
        ins && /(^|[ ,])-1,/ { seed = 1 }
        /on_anchored_state anchored_state = .* : -1;$/ { s0 = 1 }
        END { print (seed ? "seed" : "") (s0 ? "+s0" : "") }' "$d/on.c")"
    if [ -z "$dead" ]; then
        bad "[reach] '$pat': the anchored machine has no dead start (no -1 seed cell, no -1 no-context start) — the witness no longer reaches a dead entry"
        continue
    fi
    reached=$((reached + 1))
    if ! gen_cc "dead-entry $pat" $CC $GENCFLAGS -I"$d" -o "$d/drv" \
            "$ROOT_DIR/tests/anchored/dead_entry_driver.c" "$d/on.c" > "$d/cc.log" 2>&1; then
        bad "[answer] '$pat': the driver did not build: $(head -3 "$d/cc.log" | tr '\n' ' ')"; continue
    fi
    out="$(gen_run "dead-entry $pat" "$d/drv" < "$WORKDIR/$cells.cells" 2>&1)"; rc=$?
    [ "$rc" -eq 0 ] \
        && ok "[answer] '$pat' (dead start: $dead): _match and _match_caps agree with python3 re on ${out#cells } cells" \
        || bad "[answer] '$pat' (dead start: $dead): driver exit $rc — $(printf '%s' "$out" | head -2 | tr '\n' ' ')"
    [ "$asan" = 1 ] || continue
    if ! gen_cc "dead-entry asan $pat" $CC -O1 -g -std=gnu11 -fsanitize=address -I"$d" -o "$d/drv_asan" \
            "$ROOT_DIR/tests/anchored/dead_entry_driver.c" "$d/on.c" > "$d/cca.log" 2>&1; then
        bad "[asan] '$pat': the ASan driver did not build: $(head -3 "$d/cca.log" | tr '\n' ' ')"; continue
    fi
    out="$(ASAN_OPTIONS=detect_leaks=0 gen_run "dead-entry asan $pat" "$d/drv_asan" < "$WORKDIR/$cells.cells" 2>&1)"; rc=$?
    [ "$rc" -eq 0 ] \
        && ok "[asan] '$pat': no out-of-bounds read on any cell" \
        || bad "[asan] '$pat': exit $rc — $(printf '%s' "$out" | grep -m1 -E 'ERROR|DISAGREE' )"
done <<< "$WITNESSES"

[ "$reached" -eq 3 ] \
    && ok "[reach] all 3 witnesses select the unwrapped anchored form and start dead for some context" \
    || bad "[reach] only $reached of 3 witnesses reach a dead anchored entry"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
