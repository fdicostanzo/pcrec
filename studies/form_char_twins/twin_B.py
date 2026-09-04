#!/usr/bin/env python3
"""
[FORM-CHAR]/[OPT-CLSPACK] STEP 0, family (B): a single general VM class
site. Reads an emitted base .c with ONE rx*_class_bitmap0[32] site and
derives two twins:

  table    -- a 256-byte membership table, one load
  rangecmp -- an OR of the class's maximal contiguous runs, each tested by
              the standard unsigned-subtract compare (src/gen/emit_vm.c's
              own `vm_cls_test` range shape, generalized to N>1 disjoint
              runs by OR)

`bitmap` (today's 32-byte load+shift+and) is already `base.c` -- not
regenerated here. See docs/dev/form_char_step0.md for the design and the
measured results.

Usage: twin_B.py <base.c> <prefix> <out_dir> <tag>
Writes <out_dir>/<tag>_table.c and <out_dir>/<tag>_rangecmp.c.
"""
import re, sys, os, difflib


def main(base_path, prefix, out_dir, tag):
    with open(base_path) as f:
        base = f.read()

    m = re.search(
        r"static const unsigned char %s_class_bitmap0\[32\] = \{\n(.*?)\n\};\n" % re.escape(prefix),
        base, re.S)
    assert m, "no rx*_class_bitmap0[32] site found in %s" % base_path
    nums = [int(x.strip()) for x in m.group(1).replace("\n", " ").split(",") if x.strip() != ""]
    assert len(nums) == 32
    byteset = set()
    for byte_idx, v in enumerate(nums):
        for bit in range(8):
            if v & (1 << bit):
                byteset.add(byte_idx * 8 + bit)
    print(tag, "class bytes:", sorted(chr(b) if 32 <= b < 127 else hex(b) for b in byteset))

    decl_block = base[m.start():m.end()]
    test_str = ("((%s_class_bitmap0[(subject[scan_position]) >> 3] >> "
                "((subject[scan_position]) & 7)) & 1)" % prefix)
    assert test_str in base

    rows = []
    for b in range(0, 256, 8):
        rows.append("    " + ", ".join("1" if (b + j) in byteset else "0" for j in range(8)) + ",")
    table_decl = "static const unsigned char %s_scan_table0[256] = {\n%s\n};\n" % (prefix, "\n".join(rows))
    table_expr = "(%s_scan_table0[subject[scan_position]])" % prefix
    table_out = base.replace(decl_block, table_decl).replace(test_str, table_expr)

    bs = sorted(byteset)
    runs = []
    start = prev = bs[0]
    for b in bs[1:]:
        if b == prev + 1:
            prev = b
        else:
            runs.append((start, prev))
            start = prev = b
    runs.append((start, prev))
    terms = []
    for lo, hi in runs:
        if lo == hi:
            terms.append("subject[scan_position] == %d" % lo)
        else:
            terms.append("(unsigned)(subject[scan_position] - %d) <= %du" % (lo, hi - lo))
    rangecmp_expr = "(" + " || ".join(terms) + ")"
    rangecmp_out = base.replace(decl_block, "").replace(test_str, rangecmp_expr)
    print(tag, "runs:", runs)

    os.makedirs(out_dir, exist_ok=True)
    for name, text in (("table", table_out), ("rangecmp", rangecmp_out)):
        path = os.path.join(out_dir, "%s_%s.c" % (tag, name))
        with open(path, "w") as f:
            f.write(text)
        d = list(difflib.unified_diff(base.splitlines(), text.splitlines(), lineterm=""))
        changed = sum(1 for l in d if l.startswith("+") or l.startswith("-")) - 2
        print("  %-10s -> %s : diff lines changed = %d" % (name, path, changed))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: twin_B.py <base.c> <prefix> <out_dir> <tag>")
    main(*sys.argv[1:5])
