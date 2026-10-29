#!/usr/bin/env python3
"""tests/callouts/verify_callouts.py — module `callouts`' ORACLE for its
`.rxt` corpus ([INLINE-C] stage 1b; docs/spec/match_api.md §11.6).

WHAT IT CHECKS. Every `m`/`n` cell and every `g` line in tests/callouts/ is
scored by the harness against an expectation a human wrote; this program
checks those expectations against libpcre2 10.46, driven by co_oracle.c with
the answer-moving optimizations off (that file's header says why). The
callees on both sides are behaviors.h's rows.

A `consume` site has no PCRE2 form, so each `(?C"NAME,consume")` with NAME a
consumer row is spliced to `(?:EQUIV)` before asking (gen_diff.py does the
same). A NUMBERED site declared `consume` by a `callout` line binds a check
row (stubs.c), so it needs no splice: a consumer that returns 0 or -1 is a
check.

THE NAME IS THE MECHANISM: verify_rxt.py's `declares_own_oracle` sees a
`verify_*.py` here and skips this directory's cells with a counted
`own-oracle` skip. Python `re` has no callout.

Usage: verify_callouts.py <file.rxt>...
Exit 0 green, 1 on any disagreement, an empty sweep, an `m`/`n` line it
cannot read, or a co_oracle.c that does not build against a libpcre2 that
is present; 3 only when libpcre2 itself is absent (PC-3's shape:
`build_oracle`).
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_ESC = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t',
        'r': '\r', 'f': '\f', 'v': '\v'}


def unesc(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c != '\\' or i + 1 >= len(s):
            out.append(c)
            i += 1
            continue
        n = s[i + 1]
        if n == 'x' and i + 3 < len(s):
            out.append(chr(int(s[i + 2:i + 4], 16)))
            i += 4
            continue
        out.append(_ESC.get(n, n))
        i += 2
    return "".join(out)


def consumers():
    rows = {}
    with open(os.path.join(HERE, "behaviors.h")) as f:
        for m in re.finditer(r'\{ "(\w+)",\s*co_\w+,\s*"((?:[^"\\]|\\.)*)"\s*\}', f.read()):
            rows[m.group(1)] = m.group(2).replace("\\\\", "\\")
    return rows


PROBE = (b"#define PCRE2_CODE_UNIT_WIDTH 8\n#include <pcre2.h>\n"
         b"int main(void) { return pcre2_config(PCRE2_CONFIG_UNICODE, 0) < 0; }\n")


def build_oracle(cc, out):
    """Build co_oracle.c into `out`: (0, ""), or (3, why) when libpcre2 is
    ABSENT (a one-line probe that only includes and links it does not
    build), or (1, why) when libpcre2 is present and co_oracle.c is what
    fails. An absent library is a loud SKIP; a broken oracle is a FAIL,
    never a skip that silently drops the arms it feeds (gen_diff.py shares
    this)."""
    d = os.path.dirname(out)
    probe = os.path.join(d, "pcre2_probe.c")
    with open(probe, "wb") as f:
        f.write(PROBE)
    r = subprocess.run([cc, "-o", probe[:-2], probe, "-lpcre2-8"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return 3, "libpcre2 unavailable: " + r.stderr.strip()[:300]
    r = subprocess.run([cc, "-O1", "-I", HERE, "-o", out,
                        os.path.join(HERE, "co_oracle.c"), "-lpcre2-8"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return 1, "co_oracle.c did not build (libpcre2 is present): " + \
            r.stderr.strip()[:600]
    return 0, ""


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: verify_callouts.py <file.rxt>...\n")
        return 2
    cons = consumers()
    with tempfile.TemporaryDirectory() as td:
        oracle = os.path.join(td, "co_oracle")
        rc, why = build_oracle(os.environ.get("CC", "gcc"), oracle)
        if rc:
            sys.stderr.write("verify_callouts: %s\n" % why)
            if rc == 1:
                print("FAIL: verify_callouts: %s" % why)
            return rc
        cells = []          # (path, lineno, pattern, subject, kind, span, gl)
        unread = []         # `m`/`n` lines the cell reader did not parse
        for path in sys.argv[1:]:
            pattern, last = None, None
            for lineno, raw in enumerate(open(path, encoding="latin-1"), 1):
                line = raw.rstrip("\n")
                if line.startswith("pattern "):
                    pattern, last = line[8:], None
                elif line.startswith(("m ", "n ")) and pattern is not None:
                    m = re.match(r'([mn])\s+"(.*?)"(?:\s+(\d+)\s+(\d+))?\s*$', line)
                    if not m:
                        unread.append("%s:%d" % (path, lineno))
                        continue
                    span = (int(m.group(3)), int(m.group(4))) if m.group(3) else None
                    last = [path, lineno, pattern, unesc(m.group(2)), m.group(1), span, []]
                    cells.append(last)
                elif line.startswith("g ") and last is not None:
                    g = line.split()
                    last[6].append((lineno, int(g[1]), int(g[2]), int(g[3])))
        qs = []
        for c in cells:
            pat = c[2]
            for name, eq in cons.items():
                pat = pat.replace('(?C"%s,consume")' % name, "(?:%s)" % eq)
            qs.append("%s\t%s\t0" % (pat.encode("latin-1").hex(),
                                     c[3].encode("latin-1").hex()))
        r = subprocess.run([oracle], input="\n".join(qs) + "\n",
                           capture_output=True, text=True, timeout=300)
        ans = r.stdout.splitlines()
    if len(ans) != len(cells):
        print("FAIL: the oracle answered %d of %d cells" % (len(ans), len(cells)))
        return 1
    agree = bad = groups = 0
    for c, a in zip(cells, ans):
        path, lineno, pat, subj, kind, span, gl = c
        f = a.split()
        if f[0] == "error":
            print("FAIL %s:%d %r: the oracle could not answer: %s" % (path, lineno, pat, a))
            bad += 1
            continue
        ok = (kind == "n" and f[0] == "nomatch") or \
             (kind == "m" and f[0] == "match" and (int(f[1]), int(f[2])) == span)
        for gline, gi, gs, ge in gl:
            if f[0] != "match" or len(f) <= 2 + 2 * gi:
                ok = False
                continue
            groups += 1
            if (int(f[1 + 2 * gi]), int(f[2 + 2 * gi])) != (gs, ge):
                print("FAIL %s:%d group %d: file says [%d,%d), libpcre2 says %s"
                      % (path, gline, gi, gs, ge, a))
                ok = False
        if ok:
            agree += 1
        else:
            print("FAIL %s:%d pattern %r subject %r: file says %s %s, libpcre2 says %s"
                  % (path, lineno, pat, subj, kind, span, a))
            bad += 1
    print("verify_callouts: %d cells agree (%d group lines), %d disagree" % (agree, groups, bad))
    # A line the reader skipped is a cell nobody checked (K35): counted and
    # failed, never dropped.
    if unread:
        print("FAIL: %d m/n line(s) the cell reader could not parse: %s"
              % (len(unread), ", ".join(unread[:10])))
        return 1
    # An empty sweep reads like a clean one (K35). Floor 45 against the 49
    # cells measured at lane ic1bfix (2026-10-26): a few cells may move, a
    # reader that stops reaching a section may not.
    if agree < 45:
        print("FAIL: only %d cells checked — the extraction stopped reaching the corpus" % agree)
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
