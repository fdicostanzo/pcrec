#!/usr/bin/env bash
# tests/codegen/run_ctext_ascii.sh -- [EMIT-BIDI]: pattern-derived text in
# emitted C goes through the ONE escaper (`pcrec_sb_ctext`, src/core/sb.c),
# so the artifact is pure ASCII and survives every frame it is written into.
#
# The pattern holds U+200E and U+200F (bidi controls: a raw copy into a C
# comment trips gcc's -Wbidi-chars, which the harness's -Werror makes fatal --
# the job-624 failure on tests/modifiers/xmode_utf8.rxt), a comment-closing
# and a comment-opening pair, a double quote, backslashes, a trigraph-forming
# `??(`, and a tab. Under `-fcomments` (the orientation block, the provenance
# line and the legends all echo it) and under the default build, per engine:
#   (1) the .c and the .h are pure ASCII (no byte >= 0x80);
#   (2) both compile under -Wall -Wextra -Werror -Wbidi-chars=any;
#   (3) `.pattern` round-trips: the string literal decodes to the original
#       bytes (octal never glues, `?` and `"` and `\` survive).
# A positive control proves the pattern's bytes really reach the artifact
# (the decoded `.pattern` equals them), so (1) cannot pass vacuously on an
# emitter that dropped the echo.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
GENCFLAGS_TEST="-Wall -Wextra -Werror -Wbidi-chars=any -O1"

PAT=$'\xe2\x80\x8e\xe2\x80\x8fx*/y/*z"\\\\"a??(b)\t'
printf '%s' "$PAT" > "$WORK/pat.bin"

# decode_pattern FILE.c -> the bytes of the `.pattern = "..."` literal on stdout
decode_pattern() {
    python3 -I - "$1" <<'PY'
import re, sys
src = open(sys.argv[1], 'rb').read().decode('ascii')
m = re.search(r'\.pattern = "((?:[^"\\]|\\.)*)"', src)
if not m:
    sys.exit(2)
s, out, i = m.group(1), bytearray(), 0
simple = {'n': 10, 't': 9, 'r': 13, '"': 34, '\\': 92, '?': 63}
while i < len(s):
    if s[i] != '\\':
        out.append(ord(s[i])); i += 1
    elif s[i + 1] in simple:
        out.append(simple[s[i + 1]]); i += 2
    else:
        out.append(int(s[i + 1:i + 4], 8)); i += 4
sys.stdout.buffer.write(bytes(out))
PY
}

for engine in auto vm; do
  for axis in default comments; do
    label="$engine-$axis"
    mkdir -p "$WORK/$label"
    out="$WORK/$label/t.c"
    flags=(-p rx --features all -e utf8)
    [ "$engine" = vm ] && flags+=(--engine=vm)
    [ "$axis" = comments ] && flags+=(-fcomments)
    if ! pcrec_run "$PCREC" "${flags[@]}" -o "$out" --pattern "$PAT" >"$WORK/$label.log" 2>&1; then
        bad "[$label] the build failed: $(head -2 "$WORK/$label.log")"; continue
    fi
    if LC_ALL=C grep -q -P '[\x80-\xff]' "$out" "${out%.c}.h"; then
        bad "[$label] the artifact holds a byte >= 0x80 (a raw echo of the pattern bypassed pcrec_sb_ctext)"
    else
        ok "[$label] the .c and .h are pure ASCII"
    fi
    if "$CC" $GENCFLAGS_TEST -I"$WORK/$label" -c -o "$WORK/$label/t.o" "$out" 2>"$WORK/$label.cc"; then
        ok "[$label] compiles clean under $GENCFLAGS_TEST"
    else
        bad "[$label] does not compile clean: $(grep -m2 -E 'error|warning' "$WORK/$label.cc")"
    fi
    if decode_pattern "$out" > "$WORK/$label/pat.out" && cmp -s "$WORK/pat.bin" "$WORK/$label/pat.out"; then
        ok "[$label] .pattern round-trips to the original ${#PAT} bytes"
    else
        bad "[$label] .pattern does not decode to the original pattern bytes"
    fi
  done
done

printf '\n== Summary ==\nchecks passed: %d\nchecks failed: %d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
