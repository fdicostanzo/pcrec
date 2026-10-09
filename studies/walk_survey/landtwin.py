#!/usr/bin/env python3
"""walk_survey: the LANDING-START hand-twin (class K4; STUDY, not a build path).

    landtwin.py IN.c OUT.c

For a DFA artifact (`RX_DFA_SCAN "unanchored"`, `RX_DFA_START "reverse-pass"`,
prefix rx) whose pattern STARTS A MATCH AT EVERY START-SET BYTE (`\\w+`,
`[a-z]+`, `\\d+`, ...): record where the forward pass's start-byte skip loop
landed, and replace the reverse block by `start = landing`. Exact ONLY under
that property; the caller checks answer identity against the artifact on the
timed subject (fatime.c prints a span checksum). Every marker is asserted.
"""
import re, sys
src = open(sys.argv[1]).read()
def need(c, m):
    if not c:
        sys.exit("landtwin: " + m)
a = "    rx_forward_state forward_state = 0;\n"
need(src.count(a) == 1, "forward_state init")
src = src.replace(a, a + "    size_t rx_landing = search_from;\n")
m = re.search(r"( +)while \(scan_position < subject_length && !rx_can_begin_match\[subject\[scan_position\]\]\) scan_position\+\+;\n", src)
need(m, "skip loop")
src = src[:m.end()] + m.group(1) + "rx_landing = scan_position;\n" + src[m.end():]
b0 = src.index("        size_t match_end_position = last_accept_position;\n")
b1 = src.index("        if (match_start_position == (size_t)-1) return 0;\n", b0)
src = src[:b0] + "        size_t match_end_position = last_accept_position;\n        size_t match_start_position = rx_landing;\n" + src[b1:]
open(sys.argv[2], "w").write(src)
