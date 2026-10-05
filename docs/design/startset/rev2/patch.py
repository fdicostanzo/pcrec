#!/usr/bin/env python3
"""[START-SET] rev 2: write T into PFX_can_begin_match and add the re-seed on
skip exit (pf_emit_ofs_reseed's expression; dfatwin.py's patch text).
    patch.py ARTIFACT.c PFX COMMA_SEPARATED_DECIMAL_BYTES
"""
import re, sys
path, pfx, T = sys.argv[1], sys.argv[2], {int(x) for x in sys.argv[3].split(",") if x}
src = open(path).read()
m = re.search(r"(static const unsigned char %s_can_begin_match\[256\] = \{)(.*?)(\};)" % pfx, src, re.S)
assert m, "no can_begin_match"
src = src[:m.start()] + m.group(1) + "\n        " + ", ".join("1" if i in T else "0" for i in range(256)) + "\n    " + m.group(3) + src[m.end():]
old = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
       "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
       "        }\n") % pfx
assert src.count(old) == 1, "skip-loop block count %d" % src.count(old)
new = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
       "            size_t entry_position = scan_position;\n"
       "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
       "            if (scan_position > entry_position)\n"
       "                forward_state = %s_forward_seed_state[%s_forward_byte_class[subject[scan_position - 1]]];\n"
       "        }\n") % (pfx, pfx, pfx)
open(path, "w").write(src.replace(old, new, 1))
