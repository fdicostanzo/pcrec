#!/usr/bin/env bash
# tests/codegen/run_ctext_ascii.sh -- [EMIT-BIDI]: pattern-derived text in
# emitted C goes through the ONE escaper (`pcrec_sb_ctext`, src/core/sb.c),
# so pattern-derived text is pure ASCII and survives every frame it is written into.
#
# The pattern holds U+200E and U+200F (bidi controls: a raw copy into a C
# comment trips gcc's -Wbidi-chars, which the harness's -Werror makes fatal --
# the job-624 failure on tests/modifiers/xmode_utf8.rxt), a comment-closing
# and a comment-opening pair, a double quote, backslashes, a trigraph-forming
# `??(`, and a tab. Under `-fcomments` (the orientation block, the provenance
# line and the legends all echo it) and under the default build, per engine:
#   (1) the .c and the .h are pure ASCII (no byte >= 0x80), the emitters' own
#       comment prose included (src/gen/CLAUDE.md "Emitted text and comments");
#   (2) both compile under -Wall -Wextra -Werror -Wbidi-chars=any;
#   (3) `.pattern` round-trips: the string literal decodes to the original
#       bytes (octal never glues, `?` and `"` and `\` survive).
# A fourth arm scans the STRING LITERALS of the pcrec-owned emitter files for a
# byte >= 0x80 (raw, or spelled as an octal/hex escape), whichever artifact
# shape reaches them, with a synthetic positive control for the scanner.
# Excluded by name: memfn/src (the in-tree kit is another owner's; its sites
# are reported to the kit, not edited here).
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
src = open(sys.argv[1], 'rb').read().decode('latin-1')
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
    # Every byte of the artifact is ASCII: the pattern-derived text (the bidi
    # controls above) through pcrec_sb_ctext, the emitter's own prose by the
    # literal scan below.
    if LC_ALL=C grep -q -P '[\x80-\xff]' "$out" "${out%.c}.h"; then
        bad "[$label] the artifact holds a byte >= 0x80: $(LC_ALL=C grep -h -m2 -P '[\x80-\xff]' "$out" "${out%.c}.h" | cut -c1-80 | head -2 | tr '\n' '|')"
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

# (4) the literal scan over the pcrec-owned emitters.
LITSCAN="$WORK/litscan.py"
cat > "$LITSCAN" <<'PY'
import re, sys
def scan(path):
    s = open(path, 'rb').read().decode('latin-1'); n = len(s); i = 0; line = 1; out = []
    while i < n:
        c = s[i]
        if c == '\n': line += 1; i += 1
        elif s.startswith('/*', i):
            j = s.find('*/', i + 2); j = n if j < 0 else j + 2
            line += s.count('\n', i, j); i = j
        elif s.startswith('//', i):
            j = s.find('\n', i); i = n if j < 0 else j
        elif c == "'":
            j = i + 1
            while j < n and s[j] != "'": j += 2 if s[j] == '\\' else 1
            i = j + 1
        elif c == '"':
            j = i + 1
            while j < n and s[j] != '"': j += 2 if s[j] == '\\' else 1
            lit = s[i + 1:j]
            if re.search(r'[\x80-\xff]|\\[23][0-7][0-7]|\\x[89a-fA-F][0-9a-fA-F]', lit):
                out.append((line, lit))
            line += lit.count('\n'); i = j + 1
        else: i += 1
    return out
rc = 0
for p in sys.argv[1:]:
    for line, lit in scan(p):
        rc = 1; print("%s:%d: %s" % (p, line, lit[:70].encode('latin-1').decode('utf8', 'replace')))
sys.exit(rc)
PY
# the scanner's own control: a literal with a raw dash and one with an octal
# escape are flagged, a comment and a char constant holding the same are not
printf '/* \xe2\x80\x94 */\nchar *a = "x \xe2\x80\x94 y";\nchar *b = "\\302\\247";\nint c = %s;\n' "'\\302'" > "$WORK/ctl.c"
nctl=$(python3 -I "$LITSCAN" "$WORK/ctl.c" | wc -l)
if [ "$nctl" -eq 2 ]; then ok "[litscan] the scanner flags exactly the 2 non-ASCII literals of its control file"
else bad "[litscan] control file: expected 2 flagged literals, got $nctl"; fi
EMITTERS=("$ROOT_DIR"/src/gen/*.c "$ROOT_DIR"/src/gen/*.h "$ROOT_DIR"/src/enc/*.c "$ROOT_DIR"/src/core/sb.c)
if [ "${#EMITTERS[@]}" -lt 10 ]; then bad "[litscan] only ${#EMITTERS[@]} emitter files found"
elif lit_out=$(python3 -I "$LITSCAN" "${EMITTERS[@]}"); then
    ok "[litscan] no string literal of ${#EMITTERS[@]} emitter files holds a byte >= 0x80"
else
    bad "[litscan] non-ASCII string literal(s) in an emitter: $(printf '%s' "$lit_out" | head -3 | tr '\n' '|')"
fi

printf '\n== Summary ==\nchecks passed: %d\nchecks failed: %d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
