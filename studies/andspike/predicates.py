"""predicates.py -- "the match where the predicate holds", by PCRE2 + callout.

The predicate rides X's end callout: return 0 (accept) iff it holds over the
captures as they stand at that point of PCRE2's backtracking, else 1 (keep
backtracking). PCRE2 therefore returns the FIRST match, in its own preference
order (leftmost start, then backtracking order), whose captures satisfy it.

The predicate language here is a tiny reference evaluator: a Python expression
over $1..$9 (the captured text, or None when unset), checked against an AST
whitelist. It is the spike's stand-in for the real predicate language, not a
proposal for its syntax.

  python3 -B predicates.py demo
  python3 -B predicates.py sweep N L SEED   # vs refmatch's own backtracker
"""
import ast
import itertools
import random
import re
import sys

import p2cb as p
import refmatch
import spanoracle as so

_OK = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare,
       ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.BinOp, ast.Add,
       ast.Sub, ast.Mult, ast.Mod, ast.FloorDiv, ast.Call, ast.Name, ast.Load, ast.Constant)
_FUNCS = {"int": int, "len": len, "str": str}


def compile_pred(src):
    """`int($1) <= 255` -> f(caps_text) -> bool. caps_text[k-1] is $k."""
    py = re.sub(r"\$(\d)", r"G\1", src)
    tree = ast.parse(py, mode="eval")
    for n in ast.walk(tree):
        if not isinstance(n, _OK):
            raise ValueError("predicate: %s not allowed" % type(n).__name__)
        if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id in _FUNCS):
            raise ValueError("predicate: only int/len/str calls")
    code = compile(tree, "<pred>", "eval")

    def f(texts):
        env = dict(_FUNCS)
        for k in range(1, 10):
            env["G%d" % k] = texts[k - 1] if k <= len(texts) else None
        try:
            return bool(eval(code, {"__builtins__": {}}, env))
        except (ValueError, TypeError):
            return False  # e.g. int('') or len(None): the predicate does not hold
    return f


def texts_of(caps, sb):
    return [None if c is None else sb[c[0]:c[1]].decode("latin-1") for c in caps]


def oracle_pred(o, x, src, s, anchored_at=None):
    f = compile_pred(src)
    if so.SABOTAGE == "pred":  # control: an oracle that ignores the predicate
        f = lambda texts: True
    ov = o.pred_match(x, lambda caps, sb: f(texts_of(caps, sb)), s, anchored_at)
    if ov is None or ov[0] == "status":
        return ov
    return [None if c == (None, None) else c for c in ov]


def ref_pred(x, src, s, anchored_at=None):
    """Independent route: refmatch's paths in order, first one that satisfies."""
    f = compile_pred(src)
    starts = [anchored_at] if anchored_at is not None else range(len(s) + 1)
    for i in starts:
        for e, caps in refmatch.matches(x, s, i):
            if f([None if c is None else s[c[0]:c[1]] for c in caps]):
                return [(i, e)] + list(caps)
    return None


DEMOS = [
    # pattern, predicate, subject, anchored_at, hand-derived [(whole), $1, ...]
    (r"(\d+)", "int($1) <= 255", "1234", 0, [(0, 3), (0, 3)],
     "order 1234,123,...: 1234 > 255, 123 holds"),
    (r"(\d+)", "int($1) <= 255", "999 1234", None, [(0, 2), (0, 2)],
     "leftmost start 0: 999 fails, 99 holds -- the predicate does not imply a token boundary"),
    (r"\b(\d+)\b", "int($1) <= 255", "999 12 300 255", None, [(4, 6), (4, 6)],
     "\\b forbids shrinking: 999 fails, 12 holds"),
    (r"(\w+)=(\w+)", "$1 == $2", "a=b x=x", None, [(4, 7), (4, 5), (6, 7)], ""),
    (r"(a+)(a+)", "len($1) == 2*len($2)", "aaaaaa", 0, [(0, 6), (0, 4), (4, 6)],
     "(5,1) fails; (4,2) holds"),
    (r"(a+?)(a*)", "len($1) == len($2)", "aaaa", 0, [(0, 2), (0, 1), (1, 2)],
     "lazy $1=a, $2 greedy aaa,aa,a: a==a at $2=a"),
    (r"(?:(a)|b)+", "$1 is None", "ab", 0, None,
     "every path from 0 starts with (a); $1 persists into the b iteration"),
    (r"(?:(a)|b)+", "$1 is None", "ba", None, [(0, 1), None],
     "from 0: ba sets $1, b alone leaves it unset"),
]


def demo():
    o = so.Oracle()
    nfail = 0
    for x, src, s, at, want, why in DEMOS:
        got = oracle_pred(o, x, src, s, at)
        got = None if got is None or want is None else got[:len(want)]
        ok = got == want
        nfail += not ok
        print("%s %-14s %-24s %-16r at=%-4s got=%r want=%r  %s"
              % ("PASS" if ok else "FAIL", x, src, s, at, got, want, why))
    print("predicate demos: %d  fail %d" % (len(DEMOS), nfail))


PRED_FAMILY = ["$1 is not None and len($1) % 2 == 0",
               "$1 == $2",
               "len($1 or '') > len($2 or '')",
               "$1 is None",
               "len($1 or '') == 1 and $2 is not None"]


def sweep(N, L, seed):
    rng = random.Random(seed)
    o = so.Oracle()
    agree = differ = withcap = 0
    bad = []
    subs = ["".join(t) for n in range(L + 1) for t in itertools.product("ab", repeat=n)]
    while agree + differ < N * len(subs) * 2:
        x = refmatch.gen_pattern(rng, depth=2, caps=True)
        ncap = refmatch.parse(x)[1]
        if ncap < 2:
            continue
        src = rng.choice(PRED_FAMILY)
        for s in subs:
            for at in (0, None):
                g = oracle_pred(o, x, src, s, at)
                r = ref_pred(x, src, s, at)
                if g is not None:
                    g = g[:ncap + 1]
                    withcap += 1
                if g == r:
                    agree += 1
                else:
                    differ += 1
                    if len(bad) < 15:
                        bad.append((x, src, s, at, g, r))
    print("predicate sweep N=%d L=%d seed=%d pcre2=%s: agree %d differ %d (matches found %d)"
          % (N, L, seed, p.version(), agree, differ, withcap))
    for b in bad:
        print("  DIFF", b)


if __name__ == "__main__":
    if sys.argv[1] == "demo":
        demo()
    else:
        sweep(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
