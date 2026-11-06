"""altnf_proc.py -- the ONE sibling-merge procedure of alt_normal_form.md rev 2
§3.3, re-implemented from the text on equal-width and mixed-width LITERAL lists
(branches = tuples of frozensets; every branch effect-free, so the §3.2
adjacency test reduces to rows 1-2 over strings). Prints the result for the
review's three SIM-1 cells and checks every result against a brute-force
leftmost-first oracle on all strings up to length 4 with a continuation.
Lane altrev2, 2026-11-05.  python3 -I altnf_proc.py"""
import itertools

def passes(m, j):
    # §3.2 table: row 1 a disjoint position before both ends; row 2 equal width
    # (every branch here is effect-free); else refuse.
    for p in range(min(len(m), len(j))):
        if not (m[p] & j[p]):
            return True
    return len(m) == len(j)

def merge(L):
    L = [tuple(b) for b in L]
    changed = True
    while changed:
        changed = False
        for w in sorted({len(b) for b in L}):
            for p in range(w - 1, -1, -1):
                heads = {}            # key -> list of current slot indices (group heads)
                out = []
                for b in L:
                    if len(b) != w:
                        out.append(b); continue
                    key = b[:p] + b[p+1:]
                    target = None
                    for h in reversed(heads.get(key, [])):
                        between = out[h+1:]
                        if all(passes(m, b) for m in between):
                            target = h            # keep walking back: earliest reachable
                        else:
                            break
                    if target is None:
                        heads.setdefault(key, []).append(len(out)); out.append(b)
                    else:
                        g = out[target]
                        out[target] = g[:p] + (g[p] | b[p],) + g[p+1:]
                        changed = True
                L = out
    return L

def show(L):
    return "|".join("".join(next(iter(s)) if len(s) == 1 else "[" + "".join(sorted(s)) + "]" for s in b) for b in L)

def lit(s):
    return [tuple(frozenset(c) for c in w) for w in s.split("|")]

def lang_first(L, subj, cont):
    # leftmost-first over branches (each an exact product), continuation `cont`
    # anchored right after the branch: returns (branch index, length) or None
    for i, b in enumerate(L):
        n = len(b)
        if len(subj) >= n and all(subj[k] in b[k] for k in range(n)) and subj[n:].startswith(cont):
            return n
    return None

for case in ["aaa|aab|aba|bba", "aab|bbb|bab", "ab|ab", "ab|a|ad", "ab|xy|ad", "ab|abc|ad", "aaa|ab|aab"]:
    L = lit(case); R = merge(L)
    bad = 0
    for k in range(0, 5):
        for t in itertools.product("abcdxy", repeat=k):
            s = "".join(t)
            for cont in ("", "c", "d", "y"):
                if lang_first(L, s, cont) != lang_first(R, s, cont):
                    bad += 1
    print(f"{case:18s} -> {show(R):22s} branches {len(L)}->{len(R)}  oracle mismatches {bad}")
