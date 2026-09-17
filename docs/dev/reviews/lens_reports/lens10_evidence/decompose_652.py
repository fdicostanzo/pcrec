#!/usr/bin/env python3
"""lens10kit MEASUREMENT part 3 -- decompose lens 2 L2-3's `652 %s_
substitutions` by WHICH ARGUMENT each one binds.

`grep -o '%s_' | wc -l` gives 652 (347 emit_vm.c + 305 emit_dfa.c), which
this script reproduces. The claim attached to that number is that each is
"pcrec_enc_emit_text's `$` performed by hand" -- i.e. a PREFIX substitution.
Test it: pair conversions with varargs positionally and report, for every
`%s` whose next format character is `_`, what expression is actually bound.
"""
import re, sys, collections
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from count_runs import (strip_map, find_calls, split_args, is_string_literal,
                        literal_body, CONV, PREFIX_EXPRS)


def conv_positions(fmt):
    """[(index_in_fmt, letter, end_index)] skipping %%."""
    out, i = [], 0
    while i < len(fmt):
        if fmt[i] != "%":
            i += 1
            continue
        m = CONV.match(fmt, i)
        if not m:
            out.append((i, "?", i + 1))
            i += 1
            continue
        if m.group(0) == "%%":
            i = m.end()
            continue
        out.append((i, m.group(1), m.end()))
        i = m.end()
    return out


# emit_dfa.c:4262-4263 -- ARG-PAIR MACROS. Each expands to several varargs, so
# a naive positional pairing sees a conversion/arg count mismatch. Expanded
# here so those calls pair exactly rather than being lumped as UNPAIRABLE.
ARG_MACROS = {
    "VROW": ["(f)->p", "(f)->dir->c.name", "(f)->dir->statev"],
    "VTBL": ["(f)->p", "(f)->dir->c.name"],
}
NORMALISE = {"(f)->p": "f->p", "(f)->dir->c.name": "f->dir->c.name",
             "(f)->dir->statev": "f->dir->statev"}


def expand_macros(rest):
    out = []
    for a in rest:
        m = re.fullmatch(r"(VROW|VTBL)\s*\(\s*f\s*\)", a)
        if m:
            out.extend(NORMALISE[x] for x in ARG_MACROS[m.group(1)])
        else:
            out.append(a)
    return out


def main():
    hist = collections.Counter()
    total_grep = 0
    accounted = 0
    unmatched_calls = 0
    for path in sys.argv[1:]:
        src = open(path, encoding="utf-8", errors="replace").read()
        total_grep += len(re.findall(r"%s_", src))
        kind = strip_map(src)
        for c in find_calls(src, kind):
            args = split_args(c["args"], c["argkind"])
            if len(args) < 2:
                continue
            a1t, a1k = args[1]
            if not is_string_literal(a1t, a1k):
                continue
            fmt = literal_body(a1t, a1k)
            cps = conv_positions(fmt)
            rest = expand_macros([a.strip() for a, _ in args[2:]])
            if len(cps) != len(rest):
                # can't pair positionally (varargs count mismatch: %*d, etc.)
                for (i, letter, e) in cps:
                    if letter == "s" and fmt[e:e+1] == "_":
                        hist["<UNPAIRABLE CALL>"] += 1
                        accounted += 1
                unmatched_calls += 1
                continue
            for (i, letter, e), a in zip(cps, rest):
                if letter == "s" and fmt[e:e+1] == "_":
                    hist[a] += 1
                    accounted += 1
    print("grep -o '%%s_' total across the files: %d" % total_grep)
    print("accounted for by positional pairing:  %d" % accounted)
    print("calls whose varargs could not be paired: %d" % unmatched_calls)
    pfx = sum(n for k, n in hist.items() if k in PREFIX_EXPRS)
    print("\n--> bound to a PREFIX expression %s: %d (%.1f%% of %d)"
          % (sorted(PREFIX_EXPRS), pfx, 100.0 * pfx / max(1, accounted), accounted))
    print("--> bound to something else:        %d\n" % (accounted - pfx))
    print("full binding histogram:")
    for k, n in hist.most_common():
        mark = "PREFIX" if k in PREFIX_EXPRS else "      "
        print("  %5d  %s  %s" % (n, mark, k))


if __name__ == "__main__":
    main()
