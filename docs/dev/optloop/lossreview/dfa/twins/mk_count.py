#!/usr/bin/env python3
"""mk_count.py IN.c OUT.c — a COUNTING copy of a DFA artifact whose forward
scan has the DFA-hat skip block (`forward_state == 0 && last_accept ...` with
a start-bytes skip loop): counts skip-block entries, bytes the skip loop
advanced, seed-state reloads, and forward DFA steps, into globals
lr_entries/lr_skipped/lr_seeds/lr_steps (read by stepcount.c). No clock."""
import sys, re
s = open(sys.argv[1]).read()
hdr = "unsigned long long lr_entries, lr_skipped, lr_seeds, lr_steps;\n"
a = "        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n            size_t skip_from = scan_position;\n"
assert s.count(a) == 1, "skip block"
s = s.replace(a, a + "            lr_entries++;\n")
b = re.search(r"( +)if \(scan_position > skip_from\) forward_state = rx_forward_seed_state", s)
assert b, "seed line"
s = s[:b.start()] + b.group(1) + "lr_skipped += scan_position - skip_from; if (scan_position > skip_from) lr_seeds++;\n" + s[b.start():]
c = "            unsigned forward_class = rx_forward_byte_class[subject[scan_position]];\n"
assert s.count(c) == 1, "step"
s = s.replace(c, c + "            lr_steps++;\n")
i = s.index("int rx_search(")
s = s[:i] + hdr + s[i:]
open(sys.argv[2], "w").write(s)
