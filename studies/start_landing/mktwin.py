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
--guard=G   [rev 2, SL-G1/SL-E1] which first-character guard `landing-u8`
            carries (default `skip`):
              skip     SL-G1's POST-LOOP SKIP (the design's primary, §2.5):
                       after the forward loop, if the character at the last
                       landing L does not decode, start = the first position
                       p > L at which one does (bounded by the end). No
                       re-entry, no hot-path statement.
              inblock  SL-E1's FIX A: the NEXT block's last statement tests the
                       candidate and steps past an ill-formed one exactly as
                       past a non-candidate (`continue`), then records.
              restart  REVISION 1's form (recorded, refuted): re-enter the
                       forward scan at L + 1 (QUADRATIC on lead runs).
              none     CONTROL: no guard (must fail on ill-formed subjects).
--no-guard  the old spelling of --guard=none.

The decode every guard calls is THE SEAM'S OWN `$_decode`
(`src/enc/enc_utf8.c` `u8_defs_decode`, read from the tree at twin time,
`$` -> `<p>_tw`), so the twin tests the text a build would emit; its
agreement with Unicode Table 3-7 is `decode_eq.py`'s separate, exhaustive
check.

Independent of the emitter: it edits today's artifact TEXT, anchored on the
emitted lines below; every anchor is asserted (count == the number of DFA
search bodies in the file, 1). Works on the DFA artifact's <p>_search and on
a VM hybrid's static <p>_prefilter alike (the same emitter writes both).
"""
import os, re, sys

src = open(sys.argv[1]).read()
out, P, form, mode = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
guard = "skip"
for a in sys.argv[6:]:
    if a == "--no-guard": guard = "none"
    elif a.startswith("--guard="): guard = a.split("=", 1)[1]
if guard not in ("skip", "inblock", "restart", "none"):
    sys.exit("mktwin: --guard=" + guard)


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
    u8 = form == "landing-u8"
    if u8 and guard == "inblock":
        # Fix A: an ill-formed candidate is stepped past like a non-candidate
        # (the block re-runs at the loop top with the state still s0)
        src = (src[:line0] + ind + "    if (scan_position < subject_length && !%s_tw_decode(subject, subject_length, scan_position, &%s_tw_cp)) { scan_position++; continue; }\n" % (P, P)
               + ind + "    %s_landing = scan_position;\n" % P + src[line0:])
    else:
        src = src[:line0] + ind + "    %s_landing = scan_position;\n" % P + src[line0:]
    row = "%s_landing" % P
    decl = ""
    if u8 and guard == "restart":
        # REVISION 1 (refuted, SL-G1/SL-E1): restart the forward scan at
        # landing + 1 in the start state -- a re-entry, quadratic on lead runs
        fl = "    for (;;) {\n"
        # the FORWARD loop is the first `for (;;)` after the landing decl
        d0 = src.index("    size_t %s_landing = search_from;\n" % P)
        f0 = src.index(fl, d0)
        src = src[:f0] + "  %s_land_restart:;\n" % P + src[f0:]
        decl = ("        if (!%s_tw_decode(subject, subject_length, %s_landing, &%s_tw_cp)) {\n"
                "            scan_position = %s_landing + 1; last_accept_position = (size_t)-1;\n"
                "            forward_state = 0; %s_landing = scan_position;\n"
                "            goto %s_land_restart;\n"
                "        }\n") % (P, P, P, P, P, P)
    elif u8 and guard == "skip":
        # SL-G1: no match starts at an ill-formed L; the leftmost start is the
        # first decodable position after it (design §2.5's proof), which lies
        # before the end; the bound is defensive, never reached when exact
        decl = ("        if (!%s_tw_decode(subject, subject_length, %s_landing, &%s_tw_cp)) {\n"
                "            do %s_landing++;\n"
                "            while (%s_landing < last_accept_position && !%s_tw_decode(subject, subject_length, %s_landing, &%s_tw_cp));\n"
                "        }\n") % (P, P, P, P, P, P, P, P)

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

def seam_decode():
    """`u8_defs_decode` from src/enc/enc_utf8.c, unescaped, `$` -> `<P>_tw`."""
    root = os.environ.get("PCREC_SRC") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    t = open(os.path.join(root, "src", "enc", "enc_utf8.c")).read()
    i = t.index("static const char u8_defs_decode[] =")
    j = t.index(";\n", i)
    lits = re.findall(r'^"((?:[^"\\]|\\.)*)"', t[i:j], re.M)
    need(lits, "u8_defs_decode literal")
    body = "".join(bytes(l, "ascii").decode("unicode_escape") for l in lits)
    need("$_decode(" in body, "u8_defs_decode spelling")
    return body.replace("$", "%s_tw" % P)


helpers = "long %s_tw_calls, %s_tw_diff;\nstatic unsigned %s_tw_cp;\n" % (P, P, P) + seam_decode()
# helpers go before the first function that uses them: right after the includes
inc = src.rfind("#include")
nl = src.index("\n", inc) + 1
src = src[:nl] + helpers + src[nl:]
open(out, "w").write(src)
