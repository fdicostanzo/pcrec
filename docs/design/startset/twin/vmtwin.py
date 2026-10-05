#!/usr/bin/env python3
"""[START-SET] the VM hat's hand twin (docs/design/startset.md §4.2): patch a
prefilter-less VM artifact's attempt loop so the entry and every retry skip
to the next position whose byte is in the AST start set (fs_probe's set),
exactly the emitted shape §5.2 proposes.  ANSWERS ONLY -- no clock.

    vmtwin.py <twin.c> <prefix> <set_hex64>
"""
import re, sys
path, p, hx = sys.argv[1], sys.argv[2], sys.argv[3]
b = bytes.fromhex(hx)
vals = ", ".join("1" if b[i >> 3] >> (i & 7) & 1 else "0" for i in range(256))
src = open(path).read()
assert "_prefilter(" not in src, "hybrid artifact: the VM hat's twin applies to prefilter-less VM only"
skip = ("    {\n        static const unsigned char %s_start_set[256] = { %s };\n"
        "        while (attempt_position < subject_length && !%s_start_set[subject[attempt_position]]) attempt_position++;\n"
        "        if (attempt_position >= subject_length) return 0;\n    }\n") % (p, vals, p)
old_e = "    attempt_position = search_from;\n"
assert src.count(old_e) == 1, "entry count %d" % src.count(old_e)
src = src.replace(old_e, old_e + skip, 1)
# the retry: insert at the END of the attempt loop's body, after whatever
# advance the encoding backend emitted (byte: `attempt_position++;`; utf8:
# its character-start SEEK), so the twin is encoding-agnostic.
old_r = "\n    }\n    if (capture_spans)"
n = src.count(old_r)
assert n == 1, "loop-end count %d" % n
src = src.replace(old_r, "\n" + skip.replace("\n    ", "\n        ").replace("    {\n", "        {\n", 1).rstrip("\n") + "\n    }\n    if (capture_spans)", 1)
import os
drop = os.environ.get("DROP")      # the failing-direction CONTROL: remove one member
if drop:
    d = int(drop, 16)
    vals2 = ", ".join("1" if (b[i >> 3] >> (i & 7) & 1) and i != d else "0" for i in range(256))
    src = src.replace(vals, vals2)
open(path, "w").write(src)
