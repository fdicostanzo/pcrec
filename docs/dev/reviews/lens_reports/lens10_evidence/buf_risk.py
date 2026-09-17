#!/usr/bin/env python3
"""lens10kit RISK measurement -- which fragment buffers can TRUNCATE at a
legal maximum-length -p prefix, today.

src/core/limits.def:133  PCREC_MAX_PREFIX_LEN     = 60
src/core/limits.def:134  PCREC_MAX_EMIT_NAME_LEN  = 60 + 96 = 156

K38 (src/core/limits.h) is the recorded MISCOMPILE of this class: a real
60-character -p prefix met a family of buffers sized for "rx" and produced
uncompilable C, invisible to every corpus artifact because they all use the
2-char "rx" prefix.  The cure was PCREC_MAX_EMIT_NAME_LEN; it is partially
adopted.  This script asks the residual question directly.

For each `char NAME[<literal>]` declaration, find the snprintf calls writing
NAME and compute a LOWER BOUND on the longest string the writer can produce:

    bound = len(fixed format text) + 60 * (number of %s bound to the prefix)

Everything else (%d, %s bound to a non-prefix, etc.) is scored ZERO, so the
bound is a strict UNDER-estimate: a site this flags can definitely truncate;
a site it does not flag may still be able to.  That asymmetry is the point --
the output is a CANDIDATE LIST, not a clean bill of health.
"""
import re, sys, os, collections
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from count_runs import (strip_map, split_args, is_string_literal,
                        literal_body, conversions, CONV, PREFIX_EXPRS)
from decompose_652 import conv_positions, expand_macros

MAX_PREFIX_LEN = 60
MAX_EMIT_NAME_LEN = 156

DECL = re.compile(r"\bchar\s+(\w+)\s*\[\s*(\d+)\s*\]")


def fixed_text_len(fmt):
    """Length of the format with every conversion removed, escapes counted
    as one byte."""
    out, i = [], 0
    cps = {c[0]: c[2] for c in conv_positions(fmt)}
    while i < len(fmt):
        if i in cps:
            i = cps[i]
            continue
        if fmt[i] == "\\":
            out.append("x"); i += 2; continue
        out.append(fmt[i]); i += 1
    return len(out)


def fn_start(src, pos):
    """Offset of the start of the top-level function body containing `pos`.
    A `}` at column 0 ends a top-level definition, so the character after the
    last such `}` before `pos` begins the current one."""
    i = src.rfind("\n}", 0, pos)
    return 0 if i < 0 else i + 2


def main():
    rows = []
    sizes = collections.Counter()
    for path in sys.argv[1:]:
        src = open(path, encoding="utf-8", errors="replace").read()
        kind = strip_map(src)
        # declarations (code positions only)
        decls = {}
        for m in DECL.finditer(src):
            if kind[m.start()] != "c":
                continue
            decls.setdefault(m.group(1), []).append(
                (int(m.group(2)), src.count("\n", 0, m.start()) + 1, m.start()))
            sizes[int(m.group(2))] += 1
        # snprintf calls
        for m in re.finditer(r"\bsnprintf\s*\(", src):
            if kind[m.start()] != "c":
                continue
            depth, i = 0, m.end() - 1
            while i < len(src):
                if kind[i] == "c":
                    if src[i] == "(":
                        depth += 1
                    elif src[i] == ")":
                        depth -= 1
                        if depth == 0:
                            break
                i += 1
            args = split_args(src[m.end():i], kind[m.end():i])
            if len(args) < 3:
                continue
            dst = args[0][0].strip()
            if dst not in decls:
                continue
            a2t, a2k = args[2]
            if not is_string_literal(a2t, a2k):
                continue
            fmt = literal_body(a2t, a2k)
            cps = conv_positions(fmt)
            rest = expand_macros([a.strip() for a, _ in args[3:]])
            npfx = 0
            if len(cps) == len(rest):
                npfx = sum(1 for (fi, L, e), a in zip(cps, rest)
                           if L == "s" and a in PREFIX_EXPRS)
            line = src.count("\n", 0, m.start()) + 1
            # FUNCTION-LOCAL scoping: the declaration must precede the use AND
            # lie inside the same top-level function body. Without the second
            # test a use binds to an unrelated same-named buffer elsewhere in
            # the file (measured: it did, six times, before this was fixed).
            lo = fn_start(src, m.start())
            cand = [d for d in decls[dst] if lo <= d[2] < m.start()]
            if not cand:
                continue                      # no in-scope declaration found
            size, dline = cand[-1][0], cand[-1][1]
            bound = fixed_text_len(fmt) + MAX_PREFIX_LEN * npfx
            rows.append(dict(file=os.path.basename(path), line=line, buf=dst,
                             size=size, declline=dline, npfx=npfx,
                             fixed=fixed_text_len(fmt), bound=bound,
                             over=bound + 1 > size))
    print("char NAME[<literal>] sizes across the scanned files:")
    for s, n in sorted(sizes.items()):
        print("   %5d x%d%s" % (s, n, "   <-- >= MAX_EMIT_NAME_LEN" if s >= MAX_EMIT_NAME_LEN else ""))
    print("\nsnprintf writes into a literal-sized buffer: %d" % len(rows))
    over = [r for r in rows if r["over"]]
    print("PROVABLY TRUNCATING at a legal 60-byte -p prefix: %d\n" % len(over))
    print("%-13s %6s %-26s %5s %6s %5s %6s" %
          ("file", "line", "buffer", "size", "fixed", "%s_p", "bound"))
    for r in sorted(over, key=lambda r: -(r["bound"] - r["size"])):
        print("%-13s %6d %-26s %5d %6d %5d %6d" %
              (r["file"], r["line"], "%s (decl :%d)" % (r["buf"], r["declline"]),
               r["size"], r["fixed"], r["npfx"], r["bound"]))
    print("\n--- sites with a prefix substitution that do NOT provably overflow ---")
    for r in sorted(rows, key=lambda r: (r["file"], r["line"])):
        if r["npfx"] and not r["over"]:
            print("%-13s %6d %-22s size=%-4d bound=%d" %
                  (r["file"], r["line"], r["buf"], r["size"], r["bound"]))


if __name__ == "__main__":
    main()
