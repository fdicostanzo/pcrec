#!/usr/bin/env bash
# tests/findall/run_one_body.sh -- [FINDALL-NEXT] I4 (findall_iter_i2.md §5.3,
# ruling R1 of lane i2build): `<prefix>__one` IS I1's `<prefix>_next` body.
#
# I4 renamed I1's `_next` body to the static always_inline `<p>__one`, which
# `_next` and `_next_n`'s loop both inline. The check is on the TEXT: the body
# (from its `{` to its `}`) of `rx__one` in this compiler's artifact equals,
# byte for byte, the body of `rx_next` that the I1 COMPILER emitted for the
# same pattern. The expectations in one_body/ were written by the I1 compiler
# (lane/i1build at e0139d8c6, `-p rx`, default flags), never by this one, so
# the control shares no source with what it controls. One artifact per body
# shape: DFA unanchored (`\w+`), DFA attempt route (`^a|b`), VM (`(a)`).
#
# Why not the object code: adding `_next_n` gives the shared statics a second
# caller, and gcc then compiles I1's own `_next` text to different
# instructions (lane i2build, docs/dev/lanes/i2build/objdump/). "`_next`
# unharmed" is a MEASUREMENT (the I4 parity cell's gate 1), not this check.
#
# The control half: the same compare over a copy of each extracted body with
# one token changed must FAIL, so a compare that matches anything is caught.
# usage: run_one_body.sh   env: PCREC
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-onebody.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
fail=0; n=0
for spec in 'c3:\w+' 'c6:^a|b' 'c4:(a)'; do
    tag="${spec%%:*}"; pat="${spec#*:}"
    want="$SCRIPT_DIR/one_body/$tag.i1_next_body.txt"
    if ! pcrec_run "$PCREC" -p rx -o "$WORK/$tag.c" --pattern "$pat" 2> "$WORK/$tag.err"; then
        echo "FAIL: one-body: pcrec refused '$pat': $(head -1 "$WORK/$tag.err")" >&2; fail=1; continue
    fi
    awk '/^static inline __attribute__\(\(always_inline\)\) int rx__one\(rx_iter \*it,$/ {p = 1; getline; next}
         p {print} p && /^\}$/ {exit}' "$WORK/$tag.c" > "$WORK/$tag.got"
    if ! [ -s "$WORK/$tag.got" ]; then
        echo "FAIL: one-body: '$pat': no rx__one in the artifact" >&2; fail=1; continue
    fi
    if ! cmp -s "$WORK/$tag.got" "$want"; then
        echo "FAIL: one-body: '$pat': rx__one's body is not I1's rx_next body:" >&2
        diff "$want" "$WORK/$tag.got" | head -8 >&2
        fail=1; continue
    fi
    sed 's/return 1;/return 2;/' "$WORK/$tag.got" > "$WORK/$tag.plant"
    if cmp -s "$WORK/$tag.plant" "$want"; then
        echo "FAIL: one-body: '$pat': the planted one-token change still compares equal; the check reads nothing" >&2
        fail=1; continue
    fi
    n=$((n + 1))
done
if [ "$fail" -ne 0 ] || [ "$n" -ne 3 ]; then
    echo "FAIL: one-body: $n of 3 body shapes held" >&2
    exit 1
fi
echo "PASS: one-body: rx__one's body is I1's rx_next body on all 3 shapes (DFA unanchored, DFA attempt, VM); the planted change fails each"
