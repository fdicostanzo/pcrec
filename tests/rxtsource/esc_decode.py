r"""Leg B's `pattern-esc` rows, brought to leg A's spelling (C1's seam).

`pcrec --list-source` (leg A) reports a `pattern-esc` block's DECODED bytes;
run.sh --dump (leg B) reports the text AS WRITTEN, quotes included
(docs/spec/rxt_format.md section 1.5 para 3, "the dump-value seam"). The
differential cannot compare those two spellings raw, so this filter decodes
leg B's side with its own, independent copy of the seven-escape table
(`\" \\ \n \t \r \f \v \xHH`) and re-escapes it in the dump's vocabulary.
A disagreement between pcrec's decoder and this one then shows as a diff.

usage: esc_decode.py ESCKEYS < projB12.tsv > projB12.decoded.tsv
ESCKEYS is lines `<file>\t<line>`: the blocks leg A says opened with
`pattern-esc`. Every such block must be present and quoted, or this exits 1.
"""
import sys

SIMPLE = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r', 'f': '\f', 'v': '\v'}
CTRL = {c: '\\x%02x' % c for c in list(range(0x01, 0x20)) + [0x7f]}
CTRL.update({0x09: '\\t', 0x0a: '\\n', 0x0d: '\\r'})


def unescape(s):
    r"""Undo the dump's field escape (\\\\ \\t \\n \\r \\xNN) -> the raw text."""
    out, i = [], 0
    while i < len(s):
        if s[i] != '\\':
            out.append(s[i]); i += 1; continue
        c = s[i + 1]
        if c == 'x':
            out.append(chr(int(s[i + 2:i + 4], 16))); i += 4
        else:
            out.append({'\\': '\\', 't': '\t', 'n': '\n', 'r': '\r'}[c]); i += 2
    return ''.join(out)


def decode_quoted(s):
    assert len(s) >= 2 and s[0] == '"' and s[-1] == '"', "not a quoted operand"
    body, out, i = s[1:-1], [], 0
    while i < len(body):
        if body[i] != '\\':
            out.append(body[i]); i += 1; continue
        c = body[i + 1]
        if c == 'x':
            out.append(chr(int(body[i + 2:i + 4], 16))); i += 4
        else:
            out.append(SIMPLE[c]); i += 2
    return ''.join(out)


def escape(s):
    return ''.join('\\\\' if ch == '\\' else CTRL.get(ord(ch), ch) for ch in s)


def main():
    keys = set()
    with open(sys.argv[1], encoding='utf-8', errors='surrogateescape') as f:
        for ln in f:
            a, b = ln.rstrip('\n').split('\t')
            keys.add((a, b))
    seen = set()
    for ln in sys.stdin.buffer.read().decode('utf-8', 'surrogateescape').split('\n')[:-1]:
        cols = ln.split('\t')
        if cols[0] == 'block' and (cols[1], cols[2]) in keys:
            cols[5] = escape(decode_quoted(unescape(cols[5])))
            seen.add((cols[1], cols[2]))
        sys.stdout.buffer.write(('\t'.join(cols) + '\n').encode('utf-8', 'surrogateescape'))
    if seen != keys:
        sys.stderr.write("esc_decode: %d pattern-esc block(s) leg A reports are absent from leg B\n"
                         % len(keys - seen))
        sys.exit(1)


main()
