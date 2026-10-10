#!/usr/bin/env python3
"""[START-LANDING] hand-twin transformer (STUDY; never built or run by make).

    mktwin.py IN.c OUT.c PREFIX FORM MODE [--no-guard]

FORM   width:W    `end-minus-width`: start = end - W (W bytes)
       landing    `landing`: start = the NEXT block's last landing
       landing-u8 `landing` with the first-character well-formedness guard
                  (design §2.4): an ill-formed character at the landing
                  re-enters the forward scan at landing + 1 (a RAISE edge)
MODE   replace    the reverse block is DELETED (the timing / answer twin)
       assert     the reverse block is KEPT and its answer compared with the
                  row's on EVERY call: `<p>_tw_calls` / `<p>_tw_diff`
                  (extern globals) count calls and disagreements. On a VM
                  hybrid this is the inlined prefilter's WINDOW, so diff == 0
                  is window identity (NEUTRAL), read per call.
--no-guard  CONTROL: landing-u8 without its guard (must fail on ill-formed
            subjects).

Independent of the emitter: it edits today's artifact TEXT, anchored on the
emitted lines below; every anchor is asserted (count == the number of DFA
search bodies in the file, 1). Works on the DFA artifact's <p>_search and on
a VM hybrid's static <p>_prefilter alike (the same emitter writes both).
"""
import re, sys

src = open(sys.argv[1]).read()
out, P, form, mode = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
noguard = "--no-guard" in sys.argv[6:]


def need(c, m):
    if not c:
        sys.exit("mktwin: " + m)


# the reverse block: from the end-position line to the not-found return
B0 = "        size_t match_end_position = last_accept_position;\n"
B1 = "        if (match_start_position == (size_t)-1) return 0;\n"
need(src.count(B0) == 1 and src.count(B1) == 1, "reverse block anchors (not a reverse-pass DFA body?)")
i0 = src.index(B0)
i1 = src.index(B1, i0)
rev_block = src[i0 + len(B0):i1]   # declares match_start_position, walks back

if form.startswith("width:"):
    W = int(form.split(":")[1])
    row = "(match_end_position - %d)" % W
    decl = ""
else:
    need(form in ("landing", "landing-u8"), "form")
    a = "    %s_forward_state forward_state" % P
    m = re.search(r"\n(    %s_forward_state forward_state = [^;]*;\n)" % re.escape(P), src)
    need(m and len(re.findall(r"\n    %s_forward_state forward_state = " % re.escape(P), src)) == 1, "forward_state init")
    src = src[:m.end()] + "    size_t %s_landing = search_from;\n" % P + src[m.end():]
    # the NEXT block: the guard's `if (...) {` ... its matching `}`; the
    # record is its last statement (design §2.3: the one shared closer)
    g = "if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
    need(src.count(g) == 1, "NEXT guard (next-none, or two bodies)")
    j = src.index(g) + len(g)
    depth, k = 1, j
    while depth:
        c = src[k]
        if c == "{": depth += 1
        elif c == "}": depth -= 1
        k += 1
    close = k - 1          # index of the guard's closing brace
    line0 = src.rfind("\n", 0, close) + 1
    ind = src[line0:close]
    src = src[:line0] + ind + "    %s_landing = scan_position;\n" % P + src[line0:]
    row = "%s_landing" % P
    decl = ""
    if form == "landing-u8" and not noguard:
        # relocate on an ill-formed first character: restart the forward scan
        # at landing + 1 in the start state (the machine is unseeded, §2.1 L3)
        fl = "    for (;;) {\n"
        # the FORWARD loop is the first `for (;;)` after the landing decl
        d0 = src.index("    size_t %s_landing = search_from;\n" % P)
        f0 = src.index(fl, d0)
        src = src[:f0] + "  %s_land_restart:;\n" % P + src[f0:]
        decl = ("        if (!%s_tw_wf(subject, subject_length, %s_landing)) {\n"
                "            scan_position = %s_landing + 1; last_accept_position = (size_t)-1;\n"
                "            forward_state = 0; %s_landing = scan_position;\n"
                "            goto %s_land_restart;\n"
                "        }\n") % (P, P, P, P, P)

# re-find the reverse block (the landing edits moved offsets)
i0 = src.index(B0); i1 = src.index(B1, i0)
if mode == "replace":
    body = decl + "        size_t match_start_position = %s;\n" % row
    if decl:
        # the guard must run BEFORE the end is read
        body = decl + "        size_t match_end_position = last_accept_position;\n        size_t match_start_position = %s;\n" % row
        src = src[:i0] + body + src[i1:]
    else:
        src = src[:i0] + B0 + body + src[i1:]
else:
    need(mode == "assert", "mode")
    chk = ("        %s_tw_calls++;\n"
           "        if (match_start_position != (size_t)(%s)) %s_tw_diff++;\n") % (P, row, P)
    if decl:
        src = src[:i0] + decl + src[i0:]
        i0 = src.index(B0); i1 = src.index(B1, i0)
    src = src[:i1] + chk + src[i1:]

helpers = ("long %s_tw_calls, %s_tw_diff;\n" % (P, P) +
           "static inline int %s_tw_wf(const unsigned char *s, size_t n, size_t p)\n"
           "{   /* Unicode Table 3-7: is a well-formed character at p? */\n"
           "    if (p >= n) return 0;\n"
           "    unsigned c = s[p];\n"
           "    if (c < 0x80) return 1;\n"
           "    size_t k; unsigned lo = 0x80, hi = 0xBF;\n"
           "    if (c >= 0xC2 && c <= 0xDF) k = 1;\n"
           "    else if (c == 0xE0) { k = 2; lo = 0xA0; }\n"
           "    else if (c >= 0xE1 && c <= 0xEC) k = 2;\n"
           "    else if (c == 0xED) { k = 2; hi = 0x9F; }\n"
           "    else if (c >= 0xEE && c <= 0xEF) k = 2;\n"
           "    else if (c == 0xF0) { k = 3; lo = 0x90; }\n"
           "    else if (c >= 0xF1 && c <= 0xF3) k = 3;\n"
           "    else if (c == 0xF4) { k = 3; hi = 0x8F; }\n"
           "    else return 0;\n"
           "    if (p + k >= n) return 0;\n"
           "    if (s[p + 1] < lo || s[p + 1] > hi) return 0;\n"
           "    for (size_t i = 2; i <= k; i++) if (s[p + i] < 0x80 || s[p + i] > 0xBF) return 0;\n"
           "    return 1;\n"
           "}\n") % P
# helpers go before the first function that uses them: right after the includes
inc = src.rfind("#include")
nl = src.index("\n", inc) + 1
src = src[:nl] + helpers + src[nl:]
open(out, "w").write(src)
