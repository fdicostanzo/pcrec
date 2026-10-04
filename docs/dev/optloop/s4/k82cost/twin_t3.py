#!/usr/bin/env python3
"""k82cost T3: the HANDOFF twin of an emitted C3 artifact. The gate's
candidate (the run's start) becomes the DFA's scan start, less the run's
offset OFF from the match start (bounded and fixed for every cell T3 is used
on), instead of being discarded. Usage: twin_t3.py IN.c OUT.c OFF"""
import re, sys
src = open(sys.argv[1]).read(); off = int(sys.argv[3])
old = 'if (rx_reqrun(subject, subject_length, search_from) >= subject_length) return 0;'
assert src.count(old) == 1, 'gate line not found exactly once'
src = src.replace(old, 'size_t rx_cand = rx_reqrun(subject, subject_length, search_from);\n'
                  '    if (rx_cand >= subject_length) return 0;\n'
                  '    rx_cand = rx_cand >= search_from + %d ? rx_cand - %d : search_from;' % (off, off))
# the forward scan start of THIS function: the first one after the gate
a = 'size_t scan_position = search_from;'
g = src.index('size_t rx_cand'); i = src.index(a, g)
assert src.index('\n}\n', g) > i, 'scan start not inside the gated function'
src = src[:i] + 'size_t scan_position = rx_cand;' + src[i + len(a):]
open(sys.argv[2], 'w').write(src)
