#!/usr/bin/env python3
"""tests/code/verify_code.py — module `code-c`'s ORACLE for its `.rxt` corpus
([INLINE-C] stage 2; docs/spec/match_api.md §11.9).

WHAT IT CHECKS. Every `m`/`n` cell and `g` line in the files named is scored
by the harness against an expectation a human wrote; this program checks the
expectations against libpcre2 10.46 running THE SAME SEGMENT TEXT. The tagged
spelling ``(?C`c: ...`)`` is PCRE2's own string callout, so libpcre2 compiles
the pattern as written; its callout function dispatches on the callout string
to the segment, compiled here into a C program of its own. What the two sides
share is the user's text and nothing of pcrec's matcher: the macro set
(RX_SUBJ ... RX_G_<name>) is written HERE, from §11.9's table, as functions
over this program's view, so a wrong accessor in the artifact cannot agree
with itself. The span helpers and `rx_ctx` come from an emitted artifact
header (they have their own unit check, span_check.c).

The view handed to a segment is co_oracle.c's (tests/callouts/): every group,
each its last closed value, pair 0 `{start_match, -1}`; a segment's RX_FAIL
maps to PCRE2's 1. A `consume` segment has no PCRE2 form: its block is a
counted skip. THE FLAGS ARE THE ORACLE'S DEFINITION (co_oracle.c's header):
the answer-moving optimizations off.

Usage: verify_code.py <file.rxt>...
Exit 0 green; 1 on any disagreement, an empty sweep, a line it cannot read
or an oracle that does not build with libpcre2 present; 3 only when libpcre2
itself is absent (PC-3's shape)."""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tests", "callouts"))
from verify_callouts import unesc, PROBE  # noqa: E402

DELIMS = {'`': '`', "'": "'", '"': '"', '^': '^', '%': '%', '#': '#',
          '$': '$', '{': '}'}
TAG = re.compile(r'c(,[a-z]+(?:,[a-z]+)*)?:')

HEAD = r'''#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
%(headers)s
/* The macro set, from match_api.md section 11.9's table: functions, so an
 * argument is evaluated once by construction. */
static int orc_set(const rx_ctx *c, ptrdiff_t n)
{ return n >= 1 && (size_t)n < c->ncap && c->caps[n][1] >= 0; }
static ptrdiff_t orc_s(const rx_ctx *c, ptrdiff_t n)
{ return orc_set(c, n) ? c->caps[n][0] : -1; }
static ptrdiff_t orc_e(const rx_ctx *c, ptrdiff_t n)
{ return orc_set(c, n) ? c->caps[n][1] : -1; }
static ptrdiff_t orc_len(const rx_ctx *c, ptrdiff_t n)
{ return orc_set(c, n) ? c->caps[n][1] - c->caps[n][0] : -1; }
static const unsigned char *orc_p(const rx_ctx *c, ptrdiff_t n)
{ return orc_set(c, n) ? c->subject + c->caps[n][0] : NULL; }
static rx_span orc_cap(const rx_ctx *c, ptrdiff_t n)
{ rx_span s = { NULL, -1 }; if (orc_set(c, n)) { s.p = orc_p(c, n); s.len = orc_len(c, n); } return s; }
/* A name's number: the lowest-numbered member of its run that is set at
 * this fire, else the run's lowest number (section 11.9, (?J)). */
static PCRE2_SPTR orc_names; static uint32_t orc_nnames, orc_nesz;
static int orc_g(const rx_ctx *c, const char *name)
{
    int first = -1, set = -1;
    for (uint32_t i = 0; i < orc_nnames; i++) {
        PCRE2_SPTR e = orc_names + i * orc_nesz;
        int num = (e[0] << 8) | e[1];
        if (strcmp((const char *)e + 2, name)) continue;
        if (first < 0 || num < first) first = num;
        if (orc_set(c, num) && (set < 0 || num < set)) set = num;
    }
    return set >= 0 ? set : first;
}
#define RX_SUBJ (ctx->subject)
#define RX_LEN (ctx->len)
#define RX_POS (ctx->pos)
#define RX_START (ctx->caps[0][0])
#define RX_CAP_SET(n) orc_set(ctx, (n))
#define RX_CAP_S(n) orc_s(ctx, (n))
#define RX_CAP_E(n) orc_e(ctx, (n))
#define RX_CAP_LEN(n) orc_len(ctx, (n))
#define RX_CAP_P(n) orc_p(ctx, (n))
#define RX_CAP(n) orc_cap(ctx, (n))
#define RX_USER (ctx->user)
%(gnames)s
%(segments)s
static const struct { const char *s; size_t n; ptrdiff_t (*fn)(const rx_ctx *); } orc_segs[] = {
%(table)s
};

#define MAXG 64
typedef struct { uint32_t ngroups; } CoData;

static int orc_callout(pcre2_callout_block *b, void *data)
{
    const CoData *d = data;
    ptrdiff_t caps[MAXG + 1][2];
    caps[0][0] = (ptrdiff_t)b->start_match;
    caps[0][1] = -1;
    for (uint32_t g = 1; g <= d->ngroups && g <= MAXG; g++) {
        if (g < b->capture_top && b->offset_vector[2 * g] != PCRE2_UNSET) {
            caps[g][0] = (ptrdiff_t)b->offset_vector[2 * g];
            caps[g][1] = (ptrdiff_t)b->offset_vector[2 * g + 1];
        } else {
            caps[g][0] = caps[g][1] = -1;
        }
    }
    const rx_ctx v = { b->subject, b->subject_length, b->current_position,
                       (size_t)d->ngroups + 1,
                       (const ptrdiff_t (*)[2])caps, NULL, NULL, 0 };
    for (size_t i = 0; i < sizeof orc_segs / sizeof orc_segs[0]; i++)
        if (b->callout_string && b->callout_string_length == orc_segs[i].n &&
            !memcmp(b->callout_string, orc_segs[i].s, orc_segs[i].n)) {
            ptrdiff_t r = orc_segs[i].fn(&v);
            if (r == RX_PASS) return 0;
            if (r == RX_FAIL) return 1;
            fprintf(stderr, "verify_code: segment %%zu returned %%td\n", i, r);
            exit(2);
        }
    fprintf(stderr, "verify_code: a callout with no segment\n");
    exit(2);
}

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = 0;
    while (h[0] && h[1] && h[0] != '\t' && h[0] != '\n') {
        unsigned v;
        sscanf(h, "%%2x", &v);
        out[n++] = (unsigned char)v;
        h += 2;
    }
    return n;
}

int main(void)
{
    const uint32_t off = PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE |
                         PCRE2_NO_DOTSTAR_ANCHOR;
    static char line[1 << 16];
    static unsigned char pat[1 << 15], subj[1 << 15];
    while (fgets(line, sizeof line, stdin)) {
        char *t1 = strchr(line, '\t');
        if (!t1) { puts("error 0 bad input line"); continue; }
        size_t plen = unhex(line, pat), slen = unhex(t1 + 1, subj);
        int ec;
        PCRE2_SIZE eo;
        pcre2_code *re = pcre2_compile(pat, plen, off, &ec, &eo, NULL);
        if (!re) {
            PCRE2_UCHAR msg[256];
            pcre2_get_error_message(ec, msg, sizeof msg);
            printf("error %%d %%s\n", ec, (char *)msg);
            fflush(stdout);
            continue;
        }
        CoData d;
        pcre2_pattern_info(re, PCRE2_INFO_CAPTURECOUNT, &d.ngroups);
        pcre2_pattern_info(re, PCRE2_INFO_NAMECOUNT, &orc_nnames);
        pcre2_pattern_info(re, PCRE2_INFO_NAMEENTRYSIZE, &orc_nesz);
        pcre2_pattern_info(re, PCRE2_INFO_NAMETABLE, &orc_names);
        pcre2_match_context *mc = pcre2_match_context_create(NULL);
        pcre2_set_callout(mc, orc_callout, &d);
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        int rc = pcre2_match(re, subj, slen, 0, 0, md, mc);
        if (rc == PCRE2_ERROR_NOMATCH) {
            puts("nomatch");
        } else if (rc < 0) {
            PCRE2_UCHAR msg[256];
            pcre2_get_error_message(rc, msg, sizeof msg);
            printf("error %%d %%s\n", rc, (char *)msg);
        } else {
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            fputs("match", stdout);
            for (uint32_t g = 0; g <= d.ngroups; g++) {
                if ((int)g < rc && ov[2 * g] != PCRE2_UNSET)
                    printf(" %%zu %%zu", (size_t)ov[2 * g], (size_t)ov[2 * g + 1]);
                else
                    fputs(" -1 -1", stdout);
            }
            putchar('\n');
        }
        fflush(stdout);
        pcre2_match_data_free(md);
        pcre2_match_context_free(mc);
        pcre2_code_free(re);
    }
    return 0;
}
'''


def segments(pattern):
    """Every tagged code string in `pattern`: (decoded string, attrs, code).
    PCRE2's end rule: the first lone closing delimiter; doubled is one."""
    out, i = [], 0
    while True:
        i = pattern.find("(?C", i)
        if i < 0 or i + 3 >= len(pattern):
            return out
        o = pattern[i + 3]
        if o not in DELIMS:
            i += 3
            continue
        close, j, s = DELIMS[o], i + 4, []
        while j < len(pattern):
            if pattern[j] == close:
                if j + 1 < len(pattern) and pattern[j + 1] == close:
                    s.append(close)
                    j += 2
                    continue
                break
            s.append(pattern[j])
            j += 1
        s = "".join(s)
        m = TAG.match(s)
        if m:
            out.append((s, (m.group(1) or "").lstrip(",").split(","), s[m.end():]))
        i = j + 1


def c_string(s):
    b = s.encode("latin-1")
    return '"' + "".join("\\%03o" % c for c in b) + '"'


def manifest_links(d):
    mf = os.path.join(d, "harness.manifest")
    if not os.path.exists(mf):
        return []
    links = []
    for line in open(mf):
        w = line.split()
        if len(w) == 2 and w[0] == "link":
            links.append(os.path.join(d, w[1]))
    return links


def read_file(path):
    """(headers, blocks, unread): blocks are [lineno, pattern, consume,
    cells]; a cell is [lineno, subject, kind, span, groups]."""
    headers, blocks, unread, cur, last = [], [], [], None, None
    for lineno, raw in enumerate(open(path, encoding="latin-1"), 1):
        line = raw.rstrip("\n")
        if line.startswith("code-header ") and cur is None:
            w = line.split(None, 2)
            if len(w) == 3 and w[1] == "c":
                headers.append(w[2].strip())
        elif line.startswith("pattern "):
            segs = segments(line[8:])
            cur = [lineno, line[8:], any("consume" in a for _, a, _ in segs), [], segs]
            blocks.append(cur)
            last = None
        elif line.startswith("pattern-esc"):
            unread.append("%s:%d (pattern-esc)" % (path, lineno))
            cur = None
        elif line.startswith(("m ", "n ")) and cur is not None:
            m = re.match(r'([mn])\s+"(.*?)"(?:\s+(\d+)\s+(\d+))?\s*$', line)
            if not m:
                unread.append("%s:%d" % (path, lineno))
                continue
            span = (int(m.group(3)), int(m.group(4))) if m.group(3) else None
            last = [lineno, unesc(m.group(2)), m.group(1), span, []]
            cur[3].append(last)
        elif line.startswith("g ") and last is not None:
            g = line.split()
            last[4].append((lineno, int(g[1]), int(g[2]), int(g[3])))
    return headers, blocks, unread


def build(path, headers, segs, td, cc, rxh):
    gnames = sorted({n for _, _, code in segs for n in re.findall(r'\bRX_G_(\w+)', code)})
    body, table = [], []
    for k, (s, _, code) in enumerate(segs):
        body.append("static ptrdiff_t orc_seg%d(const rx_ctx *ctx)\n{\n(void)ctx;\n%s\n"
                    "fprintf(stderr, \"verify_code: segment %d fell off its end\\n\"); exit(2); }\n"
                    % (k, code, k))
        table.append("    { %s, %d, orc_seg%d }," % (c_string(s), len(s.encode("latin-1")), k))
    src = HEAD % {
        "headers": "\n".join("#include %s" % h for h in headers),
        "gnames": "\n".join('#define RX_G_%s orc_g(ctx, "%s")' % (n, n) for n in gnames),
        "segments": "\n".join(body),
        "table": "\n".join(table) or "    { \"\", 0, NULL },",
    }
    base = os.path.join(td, re.sub(r'\W', '_', os.path.basename(path)))
    with open(base + ".c", "w") as f:
        f.write(src)
    d = os.path.dirname(os.path.abspath(path))
    r = subprocess.run([cc, "-O1", "-std=gnu11", "-include", rxh, "-I", d,
                        "-o", base, base + ".c"] + manifest_links(d) + ["-lpcre2-8"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()[:800]
    return base, ""


# The checkable (non-`consume`) cells of tests/code/ and tests/code/frag/
# (36 at lane ic2fix; +5 at [INLINE-C] stage 3: pin_ok, pin_mid, pin_entry).
CELLS_PIN = 41


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: verify_code.py <file.rxt>...\n")
        return 2
    cc = os.environ.get("CC", "gcc")
    pcrec = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
    agree = bad = skipped = groups = 0
    unread = []
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        probe = os.path.join(td, "probe.c")
        with open(probe, "wb") as f:
            f.write(PROBE)
        if subprocess.run([cc, "-o", probe[:-2], probe, "-lpcre2-8"],
                          capture_output=True).returncode != 0:
            sys.stderr.write("verify_code: libpcre2 unavailable\n")
            return 3
        # rx_ctx, rx_span and its helpers, RX_PASS/RX_FAIL: an emitted header.
        r = subprocess.run([pcrec, "--allow-code=c", "-p", "orc", "-o",
                            os.path.join(td, "orc.c"), "--pattern",
                            "a(?C`c: return RX_PASS;`)"], capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL: pcrec did not emit the header the oracle includes: " + r.stderr)
            return 1
        rxh = os.path.join(td, "orc.h")
        for path in sys.argv[1:]:
            headers, blocks, un = read_file(path)
            unread += un
            segs = [s for b in blocks if not b[2] for s in b[4]]
            exe, why = build(path, headers, segs, td, cc, rxh)
            if exe is None:
                print("FAIL: the oracle for %s did not build (libpcre2 is present): %s" % (path, why))
                return 1
            qs, cells = [], []
            for blk in blocks:
                if blk[2]:
                    skipped += len(blk[3])
                    continue
                for c in blk[3]:
                    qs.append("%s\t%s" % (blk[1].encode("latin-1").hex(),
                                          c[1].encode("latin-1").hex()))
                    cells.append((blk, c))
            if not qs:
                continue        # a file of perr blocks has no cell to ask
            out = subprocess.run([exe], input="\n".join(qs) + "\n",
                                 capture_output=True, text=True, timeout=300)
            ans = out.stdout.splitlines()
            if len(ans) != len(cells):
                print("FAIL %s: the oracle answered %d of %d cells: %s"
                      % (path, len(ans), len(cells), out.stderr.strip()[:300]))
                return 1
            for (blk, c), a in zip(cells, ans):
                lineno, subj, kind, span, gl = c
                f = a.split()
                ok = f[0] != "error" and (
                    (kind == "n" and f[0] == "nomatch") or
                    (kind == "m" and f[0] == "match" and (int(f[1]), int(f[2])) == span))
                for gline, gi, gs, ge in gl:
                    groups += 1
                    if f[0] != "match" or len(f) <= 2 + 2 * gi or \
                            (int(f[1 + 2 * gi]), int(f[2 + 2 * gi])) != (gs, ge):
                        print("FAIL %s:%d group %d: file says [%d,%d), libpcre2 says %s"
                              % (path, gline, gi, gs, ge, a))
                        ok = False
                if ok:
                    agree += 1
                else:
                    print("FAIL %s:%d pattern %r subject %r: file says %s %s, libpcre2 says %s"
                          % (path, lineno, blk[1], subj, kind, span, a))
                    bad += 1
    print("verify_code: %d cells agree (%d group lines), %d disagree, %d skipped (consume)"
          % (agree, groups, bad, skipped))
    if unread:
        print("FAIL: %d line(s) the reader could not check: %s" % (len(unread), ", ".join(unread[:10])))
        return 1
    # An empty sweep reads like a clean one (K35). EXACT, not a floor (review
    # 2026-10-27-r1-ic2 F24): 34 checkable cells in tests/code/*.rxt and 2 in
    # tests/code/frag/ (entry.rxt's, frag_code.rxt's code-free block), 36 at
    # lane ic2fix (2026-10-27). A cell added or lost moves this number.
    if agree + bad != CELLS_PIN:
        print("FAIL: %d cells checked, the corpus has %d — the reader stopped reaching "
              "a cell, or one was added (move CELLS_PIN)" % (agree + bad, CELLS_PIN))
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
