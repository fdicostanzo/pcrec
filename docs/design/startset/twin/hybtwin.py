import os, re, sys
keep = {ord(c) for c in os.environ["SET"].split(",")}
vals = ", ".join("1" if i in keep else "0" for i in range(256))
def narrow(path, pfx):
    src = open(path).read()
    m = re.search(r"(static const unsigned char %s_can_begin_match\[256\] = \{)(.*?)(\};)" % pfx, src, re.S)
    assert m, "no can_begin_match"
    open(path,"w").write(src[:m.start()] + m.group(1) + "\n        " + vals + "\n    " + m.group(3) + src[m.end():])
def reseed(path, pfx):
    src = open(path).read()
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
    open(path,"w").write(src.replace(old, new, 1))
narrow(sys.argv[1], "tw")
narrow(sys.argv[2], "rs"); reseed(sys.argv[2], "rs")
