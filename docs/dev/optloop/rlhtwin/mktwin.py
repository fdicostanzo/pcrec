#!/usr/bin/env python3
"""docs/dev/optloop/rlhtwin/mktwin.py -- derives the hand variants of the
one-byte handoff twin from the SCRATCH emitter's own artifact
(lane/rlhtwin-scratch, `RX_REQ_HANDOFF` = K, `RX_REQ_BYTE` = the landmark):

    mktwin.py MODE IN.c OUT.c

  MODE memchr   h1m: the kit's generic ASSIGN loop (a byte-at-a-time
                statement expression; the kit has no memchr arm for an
                ASSIGN over one SET term today) replaced by a libc memchr
                returning the same position. Nothing else moves.
  MODE plant    failing-direction control: h2 with its bound replaced by
                PLANT_K (env; default K - 1) at the entry and the re-entry.
  MODE reenter  h2: h1m plus the handoff RE-ENTERED at the forward scan's
                restart point: wherever the unanchored body is back in its
                start state with no accept pending (the point where it
                already skips to the next can-begin byte), it is a fresh
                search from scan_position, so the same gate applies again:
                find the landmark's least occurrence c >= scan_position
                (none: NOMATCH), and start at max(scan_position, c - K).

Each rewrite asserts it matched exactly once."""
import re, sys

mode, src, dst = sys.argv[1:4]
s = open(src).read()
k = int(re.search(r'#define RX_REQ_HANDOFF "(\d+)"', s).group(1))
b = int(re.search(r'#define RX_REQ_BYTE "(\d+)"', s).group(1))

def sub1(pat, rep, text):
    out, n = re.subn(pat, rep, text, flags=re.S)
    if n != 1:
        sys.exit("mktwin: %r matched %d times" % (pat, n))
    return out


if mode == "plant":
    import os
    pk = int(os.environ.get("PLANT_K", k - 1))
    s = sub1(r"> %d\) \{\n        handoff_position -= %d;" % (k, k),
             lambda m: "> %d) {\n        handoff_position -= %d;" % (pk, pk), s)
    k, mode = pk, "reenter"


gate = ("const unsigned char *rlh_q = subject_length > search_from ? "
        "memchr(subject + search_from, %d, subject_length - search_from) : NULL; "
        "size_t handoff_position = rlh_q ? (size_t)(rlh_q - subject) : subject_length;" % b)
s = sub1(r'size_t handoff_position = \(\{.*?\}\);', lambda m: gate, s)
if mode == "reenter":
    s = sub1(r'(    if \(handoff_position - search_from > %d\) \{)' % k,
             lambda m: "    size_t rlh_lm = handoff_position;   /* the landmark's least occurrence */\n" + m.group(1), s)
    reent = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
             "            /* [rlhtwin h2] the handoff, re-entered */\n"
             "            if (rlh_lm < scan_position) {\n"
             "                const unsigned char *q = scan_position < subject_length ? memchr(subject + scan_position, %d, subject_length - scan_position) : NULL;\n"
             "                if (!q) return 0;\n"
             "                rlh_lm = (size_t)(q - subject);\n"
             "            }\n"
             "            if (rlh_lm - scan_position > %d) scan_position = rlh_lm - %d;\n" % (b, k, k))
    s = sub1(r'        if \(forward_state == 0 && last_accept_position == \(size_t\)-1\) \{\n',
             lambda m: reent, s)
elif mode != "memchr":
    sys.exit("mktwin: MODE memchr|reenter")
open(dst, "w").write(s)
