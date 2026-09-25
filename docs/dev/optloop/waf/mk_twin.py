#!/usr/bin/env python3
"""mk_twin.py -- build the two S3 hand-twins from a SHIPPED pcrec artifact.

Lane wafread (docs/dev/optloop/waf_attribution.md). Each twin moves ONE
variable against the base artifact so the Linux executor can time it with
cycle1_analysis.md's findall.c driver; every twin is answer-checked against
its base (spans.c + check.sh) before any timing is read.

  plainloop  delete the forward scan's candidate-skip block in rx_search:
             the `if (forward_state == 0 && last_accept_position == -1)
             { skip loop } else if (forward_state == K) { stay loop } ...`
             chain. Every removed loop only skips bytes the machine would
             have consumed without leaving its state, so the twin steps
             the DFA on every byte -- re2's shape (one transition per byte,
             no per-state loop exits). Asks: is the L3 skip machinery a net
             COST on this subject?
  ciprecheck RUN LETTER
             insert a whole-window caseless necessary-run pre-check at the
             top of rx_search: leapfrogged memchr() on the two case variants
             of LETTER (a letter of RUN), masked compare of RUN at each hit.
             RUN must be an all-ASCII-letter run that every match contains
             (the lane checks that by hand per pattern; the answer check
             catches a wrong one). Asks: what does S4(a) buy, and does the
             per-hit cost model (slack's measured memchr+memcmp rate) hold?

usage: mk_twin.py plainloop IN.c OUT.c
       mk_twin.py ciprecheck IN.c OUT.c RUN LETTER
"""
import re, sys

def plainloop(src):
    start = src.index("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n")
    # the chain ends at the first 8-space-indented statement that is not a
    # continuation of it (`}` / `else if` / deeper indentation)
    lines = src[start:].split("\n")
    n = 1
    while n < len(lines):
        l = lines[n]
        if l.startswith("         ") or l.startswith("        }") or l.startswith("        else"):
            n += 1
            continue
        break
    removed = "\n".join(lines[:n])
    if "while" not in removed or removed.count("{") != removed.count("}"):
        sys.exit("plainloop: unexpected block shape:\n" + removed)
    return src[:start] + "        /* wafread plainloop twin: candidate-skip block removed */\n" \
        + "\n".join(lines[n:]), removed.count("while")

HELPER = r'''
/* wafread ciprecheck twin: caseless necessary-run pre-check (S4(a) shape). */
static int wafread_ci_find(const unsigned char *s, size_t n, const char *run,
                           size_t len, size_t k)
{   /* run[k] is the scanned letter; leapfrog memchr over its two cases */
    unsigned char lo = (unsigned char)(run[k] | 0x20), up = (unsigned char)(lo ^ 0x20);
    const unsigned char *end, *from, *pl, *pu;
    if (n < len) return 0;
    from = s + k;
    end = s + (n - len) + k + 1;          /* one past the last hit that fits */
    pl = memchr(from, lo, (size_t)(end - from)); if (!pl) pl = end;
    pu = memchr(from, up, (size_t)(end - from)); if (!pu) pu = end;
    for (;;) {                            /* an exhausted case parks at end */
        const unsigned char *h = pl < pu ? pl : pu;
        if (h >= end) return 0;
        const unsigned char *c = h - k;
        size_t i = 0;
        while (i < len && (c[i] | 0x20) == (unsigned char)run[i]) i++;
        if (i == len) return 1;
        from = h + 1;
        if (pl == h) { pl = from < end ? memchr(from, lo, (size_t)(end - from)) : NULL; if (!pl) pl = end; }
        else         { pu = from < end ? memchr(from, up, (size_t)(end - from)) : NULL; if (!pu) pu = end; }
    }
}
'''

def ciprecheck(src, run, letter):
    run = run.lower()
    if not run.isalpha() or not run.isascii():
        sys.exit("ciprecheck: RUN must be ASCII letters (the mask is 0x20 on every byte)")
    k = run.index(letter.lower())
    sig = "int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n"
    i = src.index(sig)
    check = ('    if (search_from > subject_length || !wafread_ci_find(subject + search_from, '
             'subject_length - search_from, "%s", %d, %d)) return 0;\n' % (run, len(run), k))
    return src[:i] + HELPER + sig + check + src[i + len(sig):]

if __name__ == "__main__":
    mode, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
    src = open(inp).read()
    if mode == "plainloop":
        res, nloops = plainloop(src)
        print("plainloop: removed %d skip/stay loop(s)" % nloops)
    elif mode == "ciprecheck":
        res = ciprecheck(src, sys.argv[4], sys.argv[5])
        print("ciprecheck: run=%s letter=%s" % (sys.argv[4], sys.argv[5]))
    else:
        sys.exit(__doc__)
    open(out, "w").write(res)
