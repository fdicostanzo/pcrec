#!/usr/bin/env python3
"""tests/recursion/gen_cscan.py -- generates cscan.rxt, the C `(?{ ... })`
segment scanner written as ONE pcrec pattern ([SCANNER-DOGFOOD], lane scandog).

Rule source: docs/design/inline_c.md 2.3 "`(?{` spelling", rules 1-5.
Run:  python3 -I tests/recursion/gen_cscan.py [out.rxt]

ORACLE: every case below is driven through libpcre2 (the committed ctypes
binding, docs/design/eng_brep_measurements/probes/pcre2_ctypes.py) AND checked
against the RULE's expectation written here by hand; the generator aborts on
any disagreement, so cscan.rxt is only ever written when libpcre2 and the
rule agree. pcrec is never asked. The rule wins: a disagreement means the
pattern is fixed, never the expectation.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

PATTERN = r"""(?x)
# pcrec scanner for the C (?{ ... }) segment: docs/design/inline_c.md 2.3.
# S = phase-2 splices (backslash-newline), skipped between any two characters.
\G \(\?\{ (?<body> (?&items) (?&sp) ) (?: \} | % (?&sp) > ) (?&sp) \)

(?(DEFINE)
  (?<sp> (?: \\ \n )*+ )

  # a run of tokens, stopping (without consuming) at the closing } or %> of the current depth
  (?<items> (?:
      (?&sp) (?:
          # identifier: an encoding prefix (L u U u8) is ordinary identifier text
          [A-Za-z_$\x80-\xff] (?: (?&sp) [\w$\x80-\xff] )*+
          # pp-number: a ' followed by an identifier character is a C23 digit separator
        | (?: \d | \. (?&sp) \d ) (?: (?&sp) (?: [eEpP][+-] | [\w.$\x80-\xff] | ' (?= (?&sp) \w ) ) )*+
          # string and character literals, backslash escapes, a raw newline never inside
        | " (?: [^"\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ "
        | ' (?: [^'\\\n]++ | \\ \n | \\ (?&sp) [^\n] )*+ '
          # block comment, line comment (a spliced newline continues it)
        | / (?&sp) \* (?: [^*]++ | \* (?! (?&sp) / ) )*+ \* (?&sp) /
        | / (?&sp) / (?: [^\\\n]++ | \\ \n | \\ )*+
          # a nested block: { ... } or <% ... %>
        | (?: \{ | < (?&sp) % ) (?&items) (?&sp) (?: \} | % (?&sp) > )
          # everything else, one byte; < and % are plain unless they open a digraph
        | [^\w$\x80-\xff"'/{}<%] | / (?! (?&sp) [*/] ) | < (?! (?&sp) % ) | % (?! (?&sp) > )
      )
  )*+ )
)
"""

# (label, subject, body or None=refused). Subject is the whole text starting at "(?{"; trailing text after "})" allowed.
NL="\n"
C=[
("nonascii-ident","(?{ int \xc3\xa9 = 1'0; c = '}'; })"," int \xc3\xa9 = 1'0; c = '}'; "),
("nonascii-ident-digit","(?{ \xc3\xa91'}'; })"," \xc3\xa91'}'; "),
("empty","(?{})","") ,
("plain","(?{ x = 1; })"," x = 1; "),
("nested2","(?{ if (a) { b(); } })"," if (a) { b(); } "),
("depth2-close-then-})","(?{ { x } })"," { x } "),
("dq-brace",'(?{ s = "}"; })',' s = "}"; '),
("sq-brace","(?{ c = '}'; })"," c = '}'; "),
("sq-open-brace","(?{ c = '{'; })"," c = '{'; "),
("dq-escaped-quote",r'(?{ s = "a\"}"; })',r' s = "a\"}"; '),
("sq-escaped-quote",r"(?{ c = '\''; d = '}'; })",r" c = '\''; d = '}'; "),
("dq-backslash-end",r'(?{ s = "\\"; })',r' s = "\\"; '),
("block-comment","(?{ /* } */ x; })"," /* } */ x; "),
("block-comment-open","(?{ /* { */ x; })"," /* { */ x; "),
("block-comment-stars","(?{ /*** } ***/ x; })"," /*** } ***/ x; "),
("line-comment","(?{ // }"+NL+" x; })"," // }"+NL+" x; "),
("line-comment-brace-open","(?{ // {"+NL+"})"," // {"+NL),
("line-comment-no-nl-eof","(?{ // x })",None),
("div-not-comment","(?{ a = b / c; })"," a = b / c; "),
("div-then-star-char","(?{ a = b /c; })"," a = b /c; "),
("digraph-nest","(?{ if (a) <% b(); %> })"," if (a) <% b(); %> "),
("digraph-close-top","(?{ x; %>)"," x; "),
("digraph-open-brace-close","(?{ <% x; } })"," <% x; } "),
("brace-open-digraph-close","(?{ { x; %> })"," { x; %> "),
("lt-percent-mod","(?{ a < b % c; })"," a < b % c; "),
("percent-gt","(?{ a %b > c; })"," a %b > c; "),
("trigraph-not-recognised","(?{ x = '??<'; })"," x = '??<'; "),
("digit-sep","(?{ n = 1'000; })"," n = 1'000; "),
("digit-sep-brace-after","(?{ n = 1'000; if (n) { } })"," n = 1'000; if (n) { } "),
("digit-sep-hex","(?{ n = 0xFF'FF; })"," n = 0xFF'FF; "),
("digit-sep-float","(?{ f = .5'5e+1'0; })"," f = .5'5e+1'0; "),
("digit-sep-then-char","(?{ n = 1'000 + '}'; })"," n = 1'000 + '}'; "),
("ident-digit-then-char","(?{ x = a1'}'; })"," x = a1'}'; "),
("u8-string","(?{ s = u8\"}\"; })",' s = u8"}"; '),
("L-string","(?{ s = L\"}\"; })",' s = L"}"; '),
("U-char","(?{ c = U'}'; })"," c = U'}'; "),
("u-char","(?{ c = u'{'; })"," c = u'{'; "),
("splice-in-block-open","(?{ { x; \\"+NL+"} })"," { x; \\"+NL+"} "),
("splice-before-close","(?{ x; \\"+NL+"})"," x; "+"\\"+NL),
("splice-before-paren","(?{ x; }\\"+NL+")"," x; "),
("splice-in-comment-open","(?{ /\\"+NL+"* } */ x; })"," /\\"+NL+"* } */ x; "),
("splice-in-comment-close","(?{ /* } *\\"+NL+"/ x; })"," /* } *\\"+NL+"/ x; "),
("splice-in-linecomment-open","(?{ /\\"+NL+"/ }"+NL+"x; })"," /\\"+NL+"/ }"+NL+"x; "),
("splice-continues-linecomment","(?{ // c \\"+NL+" }"+NL+"})"," // c \\"+NL+" }"+NL),
("splice-continues-linecomment-multi","(?{ // a \\"+NL+" b \\"+NL+" }"+NL+" x; })"," // a \\"+NL+" b \\"+NL+" }"+NL+" x; "),
("backslash-backslash-nl-comment","(?{ // c \\\\"+NL+"})",None),
("splice-in-dq","(?{ s = \"a\\"+NL+"}b\"; })",' s = "a\\'+NL+'}b"; '),
("splice-after-escape-dq","(?{ s = \"\\\\"+NL+"\"}\"; })"," s = \"\\\\"+NL+"\"}\"; "),
("escaped-backslash-then-splice-dq","(?{ s = \"\\\\\\"+NL+"\"; })",' s = "\\\\\\'+NL+'"; '),
("splice-escape-quote-dq","(?{ s = \"\\\\"+NL+"\\\"}\"; })",None),
("splice-in-digraph","(?{ <\\"+NL+"% x; %\\"+NL+"> })"," <\\"+NL+"% x; %\\"+NL+"> "),
("splice-in-digitsep","(?{ n = 1\\"+NL+"'000; })"," n = 1\\"+NL+"'000; "),
("splice-in-ident-number","(?{ n = 1'0\\"+NL+"00 + '}'; })"," n = 1'0\\"+NL+"00 + '}'; "),
("pp-directive-unbalanced","(?{"+NL+"#define X {"+NL+"x; })",None),
("pp-directive-balanced","(?{"+NL+"#define X { 1 }"+NL+"x; })",NL+"#define X { 1 }"+NL+"x; "),
("unterminated-dq",'(?{ s = "abc; })',None),
("unterminated-sq","(?{ c = 'a; })",None),
("newline-in-dq",'(?{ s = "a'+NL+'b"; })',None),
("unterminated-comment","(?{ /* x; })",None),
("unterminated-eof","(?{ if (a) { x; }",None),
("depth-gt0-end","(?{ { x; })",None),
("not-followed-by-paren","(?{ x; } )",None),
("close-then-brace","(?{ x; }}",None),
("close-eof","(?{ x; }",None),
("close-then-x","(?{ x; }x)",None),
("first-close-not-paren-later-ok","(?{ x; } y; })",None),
("trailing-after-ok","(?{ x; }) and more (?{ y })"," x; "),
("two-segments-first","(?{a})(?{b})","a"),
("lone-paren","(?{ f(a, (b)); })"," f(a, (b)); "),
("dollar-ident","(?{ $x1'y; })",None),
("realistic-fn",
 "(?{"+NL+"    int i, n = 0;"+NL+"    /* count the } chars */"+NL+"    for (i = 0; i < len; i++) {"+NL+"        if (s[i] == '}') { n++; }  // brace }"+NL+"        else if (s[i] == '\"') continue;"+NL+"    }"+NL+"    printf(\"n=%d }\\n\", n);"+NL+"    return n > 1'000 ? 1 : 0;"+NL+"})",
 "\n    int i, n = 0;\n    /* count the } chars */\n    for (i = 0; i < len; i++) {\n        if (s[i] == '}') { n++; }  // brace }\n        else if (s[i] == '\"') continue;\n    }\n    printf(\"n=%d }\\n\", n);\n    return n > 1'000 ? 1 : 0;\n"),
("realistic-switch",
 "(?{ switch (c) { case '{': depth++; break; case '}': depth--; break; default: { x = \"{{\"; } } })",
 " switch (c) { case '{': depth++; break; case '}': depth--; break; default: { x = \"{{\"; } } "),
("realistic-macro-splice",
 "(?{"+NL+"#define M(x) \\"+NL+"  do { f(x); } while (0)"+NL+"  M(1);"+NL+"})",
 NL+"#define M(x) \\"+NL+"  do { f(x); } while (0)"+NL+"  M(1);"+NL),
]


def load_pcre2():
    p = os.path.join(ROOT, "docs/design/eng_brep_measurements/probes/pcre2_ctypes.py")
    spec = importlib.util.spec_from_file_location("pcre2_ctypes", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def esc_subject(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch == '"': out.append('\\"')
        elif ch == "\\": out.append("\\\\")
        elif ch == "\n": out.append("\\n")
        elif ch == "\t": out.append("\\t")
        elif ch == "\r": out.append("\\r")
        elif o < 0x20 or o >= 0x7f: out.append("\\x%02x" % o)
        else: out.append(ch)
    return '"' + "".join(out) + '"'


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cscan.rxt")
    pc = load_pcre2()
    rx = pc.compile(PATTERN)
    lines = []
    bad = 0

    def case(label, subj, exp, start=0):
        nonlocal bad
        r = rx.search(subj, start)
        got = None
        if r:
            (ms, me), grp = r
            got = subj[grp[0][0]:grp[0][1]]
        if got != exp:
            bad += 1
            sys.stderr.write("RULE/PCRE2 DISAGREE %s: rule %r pcre2 %r\n" % (label, exp, got))
            return
        lines.append("# " + label)
        sub = esc_subject(subj)
        if exp is None:
            lines.append(("n %s" if start == 0 else "ns %d %s") % ((sub,) if start == 0 else (start, sub)))
        else:
            head = "m" if start == 0 else "ms %d" % start
            lines.append("%s %s %d %d" % (head, sub, ms, me))
            lines.append("g 1 %d %d" % grp[0])

    for lab, subj, exp in C:
        case(lab, subj, exp)
    # \G anchors at the start offset: the same segment found at 1, not at 0.
    case("anchored: found at its start offset", "a(?{ x; })", " x; ", 1)
    case("anchored: not found from 0 when it starts later", "a(?{ x; })", None, 0)
    case("anchored: a later segment is not skipped to", "a(?{ x; })(?{ y; })", " y; ", 10)
    if bad:
        sys.exit("generation aborted: %d disagreement(s)" % bad)

    esc = PATTERN.strip("\n").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    head = HEAD
    with open(out, "w") as f:
        f.write(head)
        f.write('pattern-esc "%s"\nfeatures recursion,named-groups,conditionals,modifiers,classes,atomic-groups,lookaround,assertions\n' % esc)
        f.write("\n".join(lines) + "\n")
    print("wrote %s (%d cases)" % (out, len([l for l in lines if l[:2] in ("m ", "n ", "ms", "ns")])))


HEAD = """# tests/recursion/cscan.rxt -- the C `(?{ ... })` segment scanner as ONE pcrec pattern.
#
# GENERATED BY tests/recursion/gen_cscan.py (see its docstring); [SCANNER-DOGFOOD].
# The pattern is the scanner docs/design/inline_c.md 2.3 specifies (rules 1-5):
# phase-2 splices skipped between any two characters, string/character literals
# with escapes, both comment kinds, C23 digit separators inside pp-numbers,
# { } and the <% %> digraphs, the segment ending at the brace that closes
# depth 0 and must be followed by `)`. Group 1 (`body`) is the text between
# `(?{` and that closing brace; no match is the refusal. It is anchored (\\G)
# at the segment's `(?{`, as the compiler's scanner is called.
#
# ORACLE: libpcre2 10.46 via the ctypes binding, cross-checked against the
# hand-written 2.3 rule expectation in the generator (it refuses to write the
# file on any disagreement). There is no python arm: python `re` has no
# recursion. Where 2.3 is silent this pattern chose, and says so:
#   - a raw newline inside a "..." or '...' literal is a refusal (unterminated);
#   - a `//` comment that reaches the end of the pattern is a refusal (depth > 0);
#   - the body capture includes any splice immediately before the closing brace.

"""

main() if __name__ == "__main__" else None
