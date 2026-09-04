#!/usr/bin/env python3
"""
[FORM-CHAR]/[OPT-CLSPACK] STEP 0, family (C): the DFA scan edge's
run-extension body (axis I, `dfa_scans` in src/gen/emit_dfa.c). Reads an
emitted base .c carrying one or more `<m>_scan<N>[256]` membership tables
(today's `bitmap` body, `scan_test_bitmap`/`scan_tables_bitmap`) and
derives two twins, applied uniformly to EVERY scan-edge site in the file:

  range  -- the run's byte set replaced by an OR of maximal contiguous
            runs, each the standard unsigned-subtract compare
            (`scan_test_range`'s own shape) -- table declaration deleted
  fold   -- for a site whose set is EXACTLY a case-fold pair (a caseless
            literal's own shape), a folded compare `(b | 0x20) == lower`;
            falls back to the range form's OR-of-runs otherwise

See docs/dev/form_char_step0.md for the design and the measured results.

Usage: twin_C.py <base.c> <prefix> <out_dir> <tag>
Writes <out_dir>/<tag>_range.c and <out_dir>/<tag>_fold.c.
"""
import re, sys, os, difflib


def main(base_path, prefix, out_dir, tag):
    with open(base_path) as f:
        base = f.read()

    tbl_re = re.compile(
        r"    static const unsigned char (%s_\w+_scan\d+)\[256\] = \{\n(.*?)\n    \};\n" % re.escape(prefix),
        re.S)

    sites = []
    for m in tbl_re.finditer(base):
        name = m.group(1)
        nums = [int(x.strip()) for x in m.group(2).replace("\n", " ").split(",") if x.strip() != ""]
        assert len(nums) == 256, (name, len(nums))
        byteset = set(b for b in range(256) if nums[b])
        sites.append((name, m.start(), m.end(), byteset))

    assert sites, "no <m>_scan<N>[256] sites found in %s" % base_path
    print(tag, ": found", len(sites), "scan-edge site(s)")
    for name, _, _, bs in sites:
        print("  ", name, "bytes:", sorted(chr(b) if 32 <= b < 127 else hex(b) for b in bs))

    def runs_of(byteset):
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
        return runs

    def range_expr(byteset, peek):
        terms = []
        for lo, hi in runs_of(byteset):
            if lo == hi:
                terms.append("%s == %d" % (peek, lo))
            else:
                terms.append("(unsigned char)(%s - %d) <= %d" % (peek, lo, hi - lo))
        return "(" + " || ".join(terms) + ")"

    def fold_expr(byteset, peek):
        bs = sorted(byteset)
        if len(bs) == 2 and (bs[0] | 0x20) == bs[1] and bs[0] != bs[1]:
            return "((%s | 0x20) == %d)" % (peek, bs[1])
        return range_expr(byteset, peek)  # fallback

    def build(expr_fn):
        out = base
        for name, start, end, byteset in sites:
            decl_block = base[start:end]
            out = out.replace(decl_block, "")
            old_test = "%s[subject[scan_position]]" % name
            old_test_rw = "%s[subject[rewind_position - 1]]" % name
            if old_test in out:
                out = out.replace(old_test, expr_fn(byteset, "subject[scan_position]"))
            elif old_test_rw in out:
                out = out.replace(old_test_rw, expr_fn(byteset, "subject[rewind_position - 1]"))
            else:
                raise AssertionError("test site not found for %s" % name)
        return out

    os.makedirs(out_dir, exist_ok=True)
    for vname, text in (("range", build(range_expr)), ("fold", build(fold_expr))):
        path = os.path.join(out_dir, "%s_%s.c" % (tag, vname))
        with open(path, "w") as f:
            f.write(text)
        d = list(difflib.unified_diff(base.splitlines(), text.splitlines(), lineterm=""))
        changed = sum(1 for l in d if l.startswith("+") or l.startswith("-")) - 2
        print("  %-6s -> %s : diff lines changed = %d" % (vname, path, changed))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: twin_C.py <base.c> <prefix> <out_dir> <tag>")
    main(*sys.argv[1:5])
