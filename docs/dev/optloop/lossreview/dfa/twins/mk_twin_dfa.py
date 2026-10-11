#!/usr/bin/env python3
"""[LOSS-REVIEW] lrdfa hand-twins, each moving ONE variable of a SHIPPED
artifact (abi 74). Answer-checked by check_twins.sh against the base and
against libpcre2 10.46; NEVER timed by this lane (time_twins.sh is owed).

  k101   IN OUT          K101's fix shape on the two-stream folded run gate
                         (rx_reqrun__body): the common case's stream (the
                         lowercase byte) is searched as today; the other is
                         searched only BELOW the common stream's pending hit,
                         with a none-below memo, so no stream is searched past
                         a position the gate already holds (find-all linear).
  precheck IN OUT BYTE   G2-off: a whole-window memchr(BYTE) pre-check at the
                         top of rx_search (what req-admit `emitted` writes when
                         the `one-attempt` row does not fire).
  k101plant IN OUT   a PLANTED k101 (the rare stream never searched): must DIFF
  deferpre IN OUT BYTE K  G2 refined: the one-attempt artifact tests the
                         necessary BYTE once, only after its attempt has walked K
                         bytes alive without accepting (K = 64, an UNMEASURED
                         default); exact because no accept precedes the byte.
  hiskip IN OUT          the start-skip loop over rx_can_begin_match when the
                         start set is exactly 0x80-0xFF, spelled as 8-byte
                         words tested against 0x8080..80 (SWAR; the open
                         ruling waf_attribution.md §5 Q1).
"""
import re, sys

def k101(src):
    m = re.search(r"(    size_t ha = 0, hb = 0;\n    int fresh = 1;\n    while \(pos \+ (\d+) < n\) \{\n        size_t cand;\n)"
                  r"        if \(fresh \|\| ha < pos(?: \+ (\d+))?\) \{\n"
                  r"            const void \*q = memchr\(subject \+ pos(?: \+ \d+)?, (\d+), n - pos(?: - \d+)?\);\n"
                  r"            ha = q \? \(size_t\)\(\(const unsigned char \*\)q - subject\) : n;\n        \}\n"
                  r"        if \(fresh \|\| hb < pos(?: \+ \d+)?\) \{\n"
                  r"            const void \*q = memchr\(subject \+ pos(?: \+ \d+)?, (\d+), n - pos(?: - \d+)?\);\n"
                  r"            hb = q \? \(size_t\)\(\(const unsigned char \*\)q - subject\) : n;\n        \}\n"
                  r"        fresh = 0;\n        cand = ha < hb \? ha : hb;\n", src)
    if not m:
        sys.exit("k101: two-stream gate not found")
    R, K, a, b = m.group(2), m.group(3) or "0", int(m.group(4)), int(m.group(5))
    common, rare = (b, a) if b >= 0x61 else (a, b)   # the lowercase case is the common stream
    P = "pos + %s" % K
    new = ("    size_t hc = 0, hr = 0;   /* lrdfa k101 twin: common stream hc, rare stream hr */\n"
           "    int fresh = 1, hr_hit = 0;\n    while (pos + %s < n) {\n        size_t cand;\n"
           "        if (fresh || hc < %s) {\n"
           "            const void *q = memchr(subject + %s, %d, n - (%s));\n"
           "            hc = q ? (size_t)((const unsigned char *)q - subject) : n;\n        }\n"
           "        if (fresh || (hr_hit && hr < %s) || (!hr_hit && hr < hc)) {\n"
           "            size_t lo = %s;\n"
           "            if (!fresh && !hr_hit && hr > lo) lo = hr;   /* no rare byte in [.., hr) */\n"
           "            const void *q = hc > lo ? memchr(subject + lo, %d, hc - lo) : NULL;\n"
           "            if (q) { hr = (size_t)((const unsigned char *)q - subject); hr_hit = 1; }\n"
           "            else { hr = hc > lo ? hc : lo; hr_hit = 0; }\n        }\n"
           "        fresh = 0;\n        cand = (hr_hit && hr < hc) ? hr : hc;\n") % (R, P, P, common, P, P, P, rare)
    return src[:m.start()] + new + src[m.end():]

def precheck(src, byte):
    if "#include <string.h>" not in src:
        src = "#include <string.h>\n" + src
    sig = "int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{\n"
    i = src.index(sig)
    chk = ("    /* lrdfa precheck twin: G2-off, the whole-window necessary-byte check */\n"
           "    if (search_from > subject_length || !memchr(subject + search_from, %d, subject_length - search_from)) return 0;\n" % byte)
    return src[:i] + sig + chk + src[i + len(sig):]

def deferpre(src, byte, k):
    """ENG_ATTEMPT (computed-goto) artifact: after K bytes of a still-alive,
    not-yet-accepted attempt, test the necessary byte once over [start, n)."""
    lab = re.findall(r"rx_s\d+: __attribute__\(\(unused\)\);\n", src)
    if not lab:
        sys.exit("deferpre: no computed-goto state labels")
    chk = ("        if (scan_position == start + %d && last_accept_position == (size_t)-1"
           " && !memchr(subject + start, %d, subject_length - start)) goto rx_done;"
           "   /* lrdfa deferpre twin */\n" % (k, byte))
    for l in set(lab):
        src = src.replace(l, l + chk)
    if "#include <string.h>" not in src:
        src = "#include <string.h>\n" + src
    return src

def hiskip(src):
    old = "            while (scan_position < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;\n"
    if src.count(old) != 1:
        sys.exit("hiskip: skip loop not found once")
    for b in range(256):
        pass
    new = ("            while (scan_position + 8 <= subject_length) {   /* lrdfa hiskip twin (SWAR) */\n"
           "                uint64_t w; memcpy(&w, subject + scan_position, 8);\n"
           "                if (w & 0x8080808080808080ULL) break;\n"
           "                scan_position += 8;\n            }\n" + old)
    return src.replace(old, new)

if __name__ == "__main__":
    mode, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
    s = open(inp).read()
    if mode == "k101": s = k101(s)
    elif mode == "k101plant":   # failing-direction control: the rare stream is never searched
        s = k101(s).replace("const void *q = hc > lo ? memchr(subject + lo,", "const void *q = 0 && hc > lo ? memchr(subject + lo,")
    elif mode == "precheck": s = precheck(s, int(sys.argv[4]))
    elif mode == "deferpre": s = deferpre(s, int(sys.argv[4]), int(sys.argv[5]))
    elif mode == "hiskip":
        if "rx_can_begin_match[256]" in s:
            tbl = re.search(r"rx_can_begin_match\[256\] = \{([^}]*)\}", s).group(1)
            v = [int(x) for x in tbl.replace("\n", " ").split(",") if x.strip()]
            if v != [0] * 128 + [1] * 128:
                sys.exit("hiskip: start set is not exactly 0x80-0xFF")
        s = hiskip(s)
    else:
        sys.exit(__doc__)
    open(out, "w").write(s)
    print(mode, "ok", out)
