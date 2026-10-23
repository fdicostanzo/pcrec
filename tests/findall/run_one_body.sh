#!/usr/bin/env bash
# tests/findall/run_one_body.sh -- [FINDALL-NEXT] I4 (findall_iter_i2.md §5.3,
# ruling R1 of lane i2build), RE-PINNED by lane iteropt2: `<prefix>__one`'s
# text, the one search both controllers run, is pinned so that it changes
# only deliberately.
#
# I4 renamed I1's `_next` body to the static always_inline `<p>__one`, which
# `_next` and `_next_n`'s loop both inline, and this check held that body
# byte for byte to the I1 compiler's `rx_next` body (expectations written by
# lane/i1build at e0139d8c6, never by a later compiler). Lane iteropt2
# (2026-10-22, Frank's build go for causes (c)+(e)) retired that identity on
# purpose: `<p>__one` now takes a CURSOR (the subject, `*lop` and, with the
# retry, `*flp`) so that `_next_n` holds `lo`/`flags` in locals across its
# loop, and the bind moved out to `<p>__one_call` (`_next`'s body) and
# `_next_n`. The expectations in one_body/ were therefore re-written by the
# iteropt2 compiler (`-p rx`, default flags); that the iteration still
# answers as I1's did is carried by the answer checks (run_findall_tests.sh's
# differential arms, the twins), not by this text.
#
# Why not the object code: adding `_next_n` gives the shared statics a second
# caller, and gcc then compiles I1's own `_next` text to different
# instructions (lane i2build, docs/dev/lanes/i2build/objdump/).
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
    want="$SCRIPT_DIR/one_body/$tag.one_body.txt"
    if ! pcrec_run "$PCREC" -p rx -o "$WORK/$tag.c" --pattern "$pat" 2> "$WORK/$tag.err"; then
        echo "FAIL: one-body: pcrec refused '$pat': $(head -1 "$WORK/$tag.err")" >&2; fail=1; continue
    fi
    awk '/^static inline __attribute__\(\(always_inline\)\) int rx__one\(rx_iter \*it,/ {h = 1}
         h && /^\{$/ {p = 1} p {print} p && /^\}$/ {exit}' "$WORK/$tag.c" > "$WORK/$tag.got"
    if ! [ -s "$WORK/$tag.got" ]; then
        echo "FAIL: one-body: '$pat': no rx__one in the artifact" >&2; fail=1; continue
    fi
    if ! cmp -s "$WORK/$tag.got" "$want"; then
        echo "FAIL: one-body: '$pat': rx__one's body is not the pinned one (one_body/$tag.one_body.txt):" >&2
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
echo "PASS: one-body: rx__one's body is the pinned one on all 3 shapes (DFA unanchored, DFA attempt, VM); the planted change fails each"
