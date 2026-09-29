#!/usr/bin/env python3
"""asm_count.py -- [CLS-TREE] S0, a5: the [FORM-CHAR2] (i) asm-counting half
(docs/design/cls_tree_design.md sect. 7(a), a5), EXTENDED from the single
hand-picked fold-vs-bitmap witness (`studies/form_char_twins/asm_evidence.c`,
`docs/dev/form_char_step0.md` family A) to every kit byte form the emitter can
build (`ALL`, `RANGES`, `CUBES`, `MASK64`), against `BITMAP` (today's shipped
form, `vm_cls_test`'s bit array), over the REAL 41-class corpus population
(`results/byteclasses.tsv`).

METHOD, box-independent, `gcc -O2 -S` (no stopwatch): for each byte class,
treat its whole interval list as ONE section (`kit.candidates` finds every
kit member that fits it whole, exactly the single-section/no-dispatch-tree
degenerate case `kit.py`'s docstring names) and emit that member's real
matcher body via `emit.emit` -- the SAME emitter `sweep.py`/`verify_whole.py`
use, not a hand-written twin. Every candidate function is compiled together
in one `gcc -O2 -S -std=gnu11` invocation (non-static, external linkage, so
none of them can be discarded as dead code at -O2 without LTO -- the same
reasoning `asm_evidence.c`'s top-level `int test_or(...)` functions rely on).
Then it is a matter of counting: real instruction lines per function (every
non-directive, non-label, non-comment-only line between one `.globl` and the
next), not sampling a stopwatch.

CAVEAT NAMED ONCE: this box is Apple Silicon (`arm64`/Mach-O), NOT the
x86_64 target `studies/form_char_twins/results/three_spellings.s` was last
regenerated on. Per-mnemonic text does not compare across the two files;
instruction COUNTS (load vs. no-load, branch vs. branchless) are the
portable comparison this script makes, and it says so in its own output.

Usage:
    python3 asm_count.py [population]      (default: byteclasses)

Writes results/asm_count_<population>.tsv and a summary to stdout.
"""
import os
import re
import subprocess
import sys

import clsets
import emit
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")

# The forms this arm compares: the kit's no-load/low-load byte-tier members
# (per docs/design/cls_tree_design.md a5's own list) plus BITMAP, today's
# shipped form and the one every other member is measured against.
FORMS = ["ALL", "RANGES", "CUBES", "MASK64", "BITMAP"]

GLOBL_RE = re.compile(r"^\s*\.globl\s+_?(\w+)\s*$")
# A GAS/Mach-O local label of the compiler's own making (LFB0:, LBB3:, ...) --
# never a real instruction, but distinguishable from an emitted symbol only by
# NOT matching a directive/comment and being label-shaped.
LABEL_RE = re.compile(r"^[A-Za-z_.$][\w.$]*:\s*$")


# EXACT mnemonic match, not a prefix test: `bic`/`bfi`/`bfxil`/`bfc`/`bfm`
# (ARM64 bit-field ops) and `bsr`/`bswap` (x86) all start with `b` but are not
# branches, and a prefix test over-fires on them. ARM64 conditional branches
# are spelled `b<cond>` with NO dot by this toolchain's assembler (`bhi`,
# `beq`, ... -- checked against this box's own `-S` output, not assumed);
# `b.<cond>` is accepted too in case a different assembler spells it with the
# dot. x86 uses `j<cond>`/`jmp`/`call`.
BRANCH_RE = re.compile(
    r"^(b\.?(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al|nv)"
    r"|b|bl|br|cbz|cbnz|tbz|tbnz"
    r"|jmp|call|j(e|ne|z|nz|l|le|g|ge|a|ae|b|be|s|ns|o|no|c|nc|p|np))$")


def instructions_of(block_lines):
    """Real instruction lines in one function's assembly block: strip
    directives (`.foo ...`), bare labels (`LFB3:`), comment-only lines, and
    blank lines; an inline trailing comment on a real instruction does not
    disqualify the line."""
    n = 0
    branchy = False
    for raw in block_lines:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("."):
            continue
        if LABEL_RE.match(line):
            continue
        n += 1
        mnem = line.split()[0].lower()
        if BRANCH_RE.match(mnem):
            branchy = True
    return n, branchy


def parse_functions(asm_text):
    """{name: (n_instructions, has_branch)} for every `.globl`-marked function
    in one `gcc -S` output, Mach-O or ELF alike (`.globl` is common to both)."""
    # eh_frame / debug tail is unrelated data, not code; cut it off so its
    # `.long`/`.quad`/label noise never gets attributed to the last function.
    text = asm_text.split(".section __TEXT,__eh_frame")[0]
    text = text.split("\n\t.section\t.eh_frame")[0]
    lines = text.split("\n")
    starts = [(i, m.group(1)) for i, l in enumerate(lines)
              if (m := GLOBL_RE.match(l))]
    out = {}
    for k, (i, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        n, branchy = instructions_of(lines[i + 1:end])
        out[name] = (n, branchy)
    return out


def build_source(pop_rows):
    """One C file: for every class, every kit form that fits the WHOLE
    interval list as a single section, emitted by `emit.emit` exactly as the
    real compiler's kit would for a one-section sectioning."""
    parts = ["#include <stdint.h>\n"]
    jobs = []   # (fn_name, set_name, form_name, width, nintervals, rodata)
    for name, iv in pop_rows:
        tag = "".join(c if c.isalnum() else "_" for c in name)
        section = list(iv)
        w = section[-1][1] - section[0][0] + 1
        for F in kit.candidates(section, allow=set(FORMS)):
            fn = "f_%s_%s" % (tag, F.name)
            src, ro = emit.emit(fn, iv, [(0, len(iv) - 1)], [F.name],
                                 static=False)
            parts.append(src)
            jobs.append((fn, name, F.name, w, len(section), ro))
    return "".join(parts), jobs


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "byteclasses"
    pop = clsets.population(which)
    src, jobs = build_source(pop)

    out = os.path.join(HERE, "build", "asm_count")
    os.makedirs(out, exist_ok=True)
    c_path = os.path.join(out, "%s.c" % which)
    s_path = os.path.join(out, "%s.s" % which)
    open(c_path, "w").write(src)
    subprocess.run([CC, "-O2", "-std=gnu11", "-w", "-S", c_path, "-o", s_path],
                   check=True)
    asm_text = open(s_path, encoding="utf-8").read()
    funcs = parse_functions(asm_text)

    missing = [fn for fn, *_ in jobs if fn not in funcs]
    if missing:
        raise SystemExit("asm_count: %d function(s) not found in %s "
                          "(.globl parsing mismatch): %s"
                          % (len(missing), s_path, ", ".join(missing[:5])))

    import platform
    arch = platform.machine()
    out_tsv = os.path.join(HERE, "results", "asm_count_%s.tsv" % which)
    lines = ["# arch=%s cc=%s (gcc -O2 -S; instruction COUNTS are the "
             "portable comparison, mnemonic text is not -- see file header)"
             % (arch, CC),
             "set\tform\twidth\tintervals\trodata\tn_instr\thas_branch"]
    by_form = {}
    for fn, name, form, w, k_intervals, ro in jobs:
        n, branchy = funcs[fn]
        lines.append("%s\t%s\t%d\t%d\t%d\t%d\t%d"
                      % (name, form, w, k_intervals, ro, n, int(branchy)))
        by_form.setdefault(form, []).append(n)

    with open(out_tsv, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    print("#")
    print("# summary (mean n_instr, sets counted), arch=%s:" % arch)
    for form in FORMS:
        ns = by_form.get(form, [])
        if not ns:
            print("#   %-8s (fits no class in this population)" % form)
            continue
        print("#   %-8s n=%-3d mean=%.2f min=%d max=%d"
              % (form, len(ns), sum(ns) / len(ns), min(ns), max(ns)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
