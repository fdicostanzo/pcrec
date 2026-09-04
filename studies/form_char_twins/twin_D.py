#!/usr/bin/env python3
"""
[OPT-CLSPACK] STEP 0, family (D): the SHARED ATOM TABLE at a many-class VM
site (default recipe: N=16, well above the plan row's own ~10-class
crossover estimate). Generalizes twin_A.py's `atom` twin to an arbitrary
class count parsed straight off the base artifact, and additionally emits
the `table` (256-byte-per-site) twin so all three shapes (today's bit
array = base.c, table, atom) can be sized side by side.

See docs/dev/form_char_step0.md for the design and the measured results
(N=16: the atom twin wins BOTH .text and .rodata against base and table --
not a pure space-for-time trade at this scale on the axis measured).

Usage: twin_D.py <base.c> <prefix> <out_dir>
Writes <out_dir>/D_table.c and <out_dir>/D_atom.c.
"""
import re, sys, os, difflib


def main(base_path, prefix, out_dir):
    with open(base_path) as f:
        base = f.read()

    tbl_re = re.compile(
        r"static const unsigned char %s_class_bitmap(\d+)\[32\] = \{\n(.*?)\n\};\n" % re.escape(prefix), re.S)

    classes = {}
    decl_start = decl_end = None
    for m in tbl_re.finditer(base):
        idx = int(m.group(1))
        nums = [int(x.strip()) for x in m.group(2).replace("\n", " ").split(",") if x.strip() != ""]
        byteset = set()
        for bi, v in enumerate(nums):
            for bit in range(8):
                if v & (1 << bit):
                    byteset.add(bi * 8 + bit)
        classes[idx] = byteset
        if decl_start is None:
            decl_start = m.start()
        decl_end = m.end()

    assert classes, "no rx*_class_bitmapN[32] sites found in %s" % base_path
    print("N classes:", len(classes))
    decl_block = base[decl_start:decl_end]

    def bitmap_test(idx):
        return ("((%s_class_bitmap%d[(subject[scan_position]) >> 3] >> "
                "((subject[scan_position]) & 7)) & 1)" % (prefix, idx))

    for idx in classes:
        assert bitmap_test(idx) in base

    def make_table():
        out = base
        decls = []
        for idx, bs in classes.items():
            rows = []
            for b in range(0, 256, 8):
                rows.append("    " + ", ".join("1" if (b + j) in bs else "0" for j in range(8)) + ",")
            decls.append("static const unsigned char %s_scan_table%d[256] = {\n%s\n};\n"
                          % (prefix, idx, "\n".join(rows)))
        out = out.replace(decl_block, "".join(decls))
        for idx in classes:
            out = out.replace(bitmap_test(idx), "(%s_scan_table%d[subject[scan_position]])" % (prefix, idx))
        return out

    def make_atom():
        out = base
        sig_of_byte = {}
        for b in range(256):
            sig = tuple(idx for idx in sorted(classes) if b in classes[idx])
            sig_of_byte[b] = sig
        sigs = sorted(set(sig_of_byte.values()), key=lambda s: (s == (),))
        sig_to_atom = {s: i for i, s in enumerate(sigs)}
        atoms = [sig_to_atom[sig_of_byte[b]] for b in range(256)]
        n_atoms = len(sigs)
        print("n atoms:", n_atoms, "(<=64 required)")
        assert n_atoms <= 64

        rows = []
        for b in range(0, 256, 16):
            rows.append("    " + ", ".join(str(atoms[b + j]) for j in range(16)) + ",")
        atom_decl = "static const unsigned char %s_scan_atom[256] = {\n%s\n};\n" % (prefix, "\n".join(rows))

        mask_decls = []
        for idx, bs in classes.items():
            mask = 0
            for b in bs:
                mask |= (1 << atoms[b])
            mask_decls.append("static const unsigned long long %s_scan_mask%d = 0x%xULL;\n" % (prefix, idx, mask))

        out = out.replace(decl_block, atom_decl + "".join(mask_decls))
        for idx in classes:
            out = out.replace(bitmap_test(idx),
                               "((%s_scan_mask%d >> %s_scan_atom[subject[scan_position]]) & 1)" % (prefix, idx, prefix))
        return out

    os.makedirs(out_dir, exist_ok=True)
    for name, text in (("table", make_table()), ("atom", make_atom())):
        path = os.path.join(out_dir, "D_%s.c" % name)
        with open(path, "w") as f:
            f.write(text)
        d = list(difflib.unified_diff(base.splitlines(), text.splitlines(), lineterm=""))
        changed = sum(1 for l in d if l.startswith("+") or l.startswith("-")) - 2
        print(name, "-> diff lines changed =", changed)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: twin_D.py <base.c> <prefix> <out_dir>")
    main(*sys.argv[1:4])
