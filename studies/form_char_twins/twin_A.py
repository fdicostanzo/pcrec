#!/usr/bin/env python3
"""
[FORM-CHAR]/[OPT-CLSPACK] STEP 0, family (A): the VM literal chain under
caselessness. Reads an emitted base .c (today's per-position two-member
class-bitmap form) and derives three twins that differ ONLY in the
class-test expression and the class-table declaration:

  fold   -- a folded compare per site: (b | 0x20) == lower (falls back to
            an OR of exact compares for a set that is not a case-fold pair)
  table  -- a 256-byte membership table per site, one load
  atom   -- ONE shared 256-byte byte->atom table plus a per-class 64-bit
            mask test: (mask_k >> atoms[byte]) & 1

See docs/dev/form_char_step0.md for the design and the measured results.

Usage: twin_A.py <base.c> <prefix> <out_dir>
Writes <out_dir>/A_fold.c, A_table.c, A_atom.c and prints a diff-line-count
report so "the transform changed only the test form" is checked
mechanically, not by eye.
"""
import re, sys, os, difflib


def main(base_path, prefix, out_dir):
    with open(base_path) as f:
        base = f.read()

    tbl_re = re.compile(
        r"static const unsigned char %s_class_bitmap(\d+)\[32\] = \{\n(.*?)\n\};\n" % re.escape(prefix),
        re.S)

    classes = {}
    decl_start = decl_end = None
    for m in tbl_re.finditer(base):
        idx = int(m.group(1))
        nums = [int(x.strip()) for x in m.group(2).replace("\n", " ").split(",") if x.strip() != ""]
        assert len(nums) == 32, (idx, len(nums))
        byteset = set()
        for byte_idx, v in enumerate(nums):
            for bit in range(8):
                if v & (1 << bit):
                    byteset.add(byte_idx * 8 + bit)
        classes[idx] = byteset
        if decl_start is None:
            decl_start = m.start()
        decl_end = m.end()

    assert classes, "no rx*_class_bitmapN[32] sites found in %s" % base_path
    print("Parsed %d class site(s):" % len(classes))
    for idx in sorted(classes):
        bs = sorted(classes[idx])
        print("  site %d: %s" % (idx, [chr(b) if 32 <= b < 127 else hex(b) for b in bs]))

    decl_block = base[decl_start:decl_end]

    def bitmap_test(idx):
        return ("((%s_class_bitmap%d[(subject[scan_position]) >> 3] >> "
                "((subject[scan_position]) & 7)) & 1)" % (prefix, idx))

    for idx in classes:
        assert bitmap_test(idx) in base, idx

    def make_fold():
        out = base.replace(decl_block, "")
        for idx, byteset in classes.items():
            bs = sorted(byteset)
            if len(bs) == 2 and (bs[0] | 0x20) == bs[1] and bs[0] != bs[1]:
                expr = "((subject[scan_position] | 0x20) == %d)" % bs[1]
            else:
                expr = "(" + " || ".join("subject[scan_position] == %d" % b for b in bs) + ")"
            out = out.replace(bitmap_test(idx), expr)
        return out

    def make_table():
        out = base
        decls = []
        for idx, byteset in classes.items():
            rows = []
            for b in range(0, 256, 8):
                rows.append("    " + ", ".join(
                    "1" if (b + j) in byteset else "0" for j in range(8)) + ",")
            decls.append(
                "static const unsigned char %s_scan_table%d[256] = {\n%s\n};\n"
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
        assert n_atoms <= 64, n_atoms
        print("atom form: %d atoms (<=64 required)" % n_atoms)

        rows = []
        for b in range(0, 256, 16):
            rows.append("    " + ", ".join(str(atoms[b + j]) for j in range(16)) + ",")
        atom_decl = "static const unsigned char %s_scan_atom[256] = {\n%s\n};\n" % (prefix, "\n".join(rows))

        mask_decls = []
        for idx, byteset in classes.items():
            mask = 0
            for b in byteset:
                mask |= (1 << atoms[b])
            mask_decls.append("static const unsigned long long %s_scan_mask%d = 0x%xULL;\n" % (prefix, idx, mask))

        out = out.replace(decl_block, atom_decl + "".join(mask_decls))
        for idx in classes:
            out = out.replace(bitmap_test(idx),
                               "((%s_scan_mask%d >> %s_scan_atom[subject[scan_position]]) & 1)" % (prefix, idx, prefix))
        return out

    os.makedirs(out_dir, exist_ok=True)
    for name, text in (("fold", make_fold()), ("table", make_table()), ("atom", make_atom())):
        path = os.path.join(out_dir, "A_%s.c" % name)
        with open(path, "w") as f:
            f.write(text)
        d = list(difflib.unified_diff(base.splitlines(), text.splitlines(), lineterm=""))
        changed = sum(1 for l in d if l.startswith("+") or l.startswith("-")) - 2
        print("%-6s -> %s : diff lines changed = %d" % (name, path, changed))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: twin_A.py <base.c> <prefix> <out_dir>")
    main(*sys.argv[1:4])
