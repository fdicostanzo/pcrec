#!/usr/bin/env python3
"""[ENG-ISL] STEP 1 — the CORPUS CENSUS of alternation shapes.

Answers, over pcrec's own .rxt corpus and over pcrec-bench's altwide `.rx`
patterns, the four questions the alternation island's charter asks before a
line of `emit_vm.c` is written:

  1. how many FLAT alternations exist, and how many QUALIFY for the island
     (every branch a bare literal byte run — no class, no quantifier, no
     group, no assertion, no escape that is not a literal);
  2. the distribution of qualifying branch WIDTHS, which is what a decline
     threshold has to be chosen against;
  3. the TRIE the qualifying branches build — node count, depth, fan-out;
  4. the MASK DEPTH: the largest number of accepts that can be PENDING on a
     single root-to-leaf path, i.e. how many alternation branches can be
     simultaneously live candidates when the island's continuation fails.
     For a branch set in which no branch is a prefix of another this is 1,
     and the island needs no deferred machinery at all.

WHY THIS SCRIPT HAS ITS OWN PARSER, and what that costs.  Python's own
`re._parser` factors common prefixes as it parses (`abc|a|abd` comes back as
`a` followed by a three-way branch), which is precisely the structure this
census is trying to MEASURE — using it would report the post-factoring shape
and call it the input.  So the scanner below is a small, deliberately
CONSERVATIVE recursive-descent reader of the PCRE surface syntax: it
recognizes grouping, alternation, quantifiers, classes and escapes well
enough to decide "is this branch a bare literal run", and ANY construct it
is not certain about makes the branch (hence the alternation) unqualified.
Every number this prints is therefore a LOWER BOUND *ON THE SCANNER'S SIDE*.

IT IS NOT A LOWER BOUND OVERALL, and that claim (which this header used to
make flatly) is wrong in one direction — panel r53's semantics lens, F4. Two
upstream passes move the count the OTHER way before `src/gen/emit_vm.c` ever
sees a pattern:

  - `src/opt/altcls.c` stage 1 MERGES a run of single-byte alternatives into a
    CLASS, and a class is not a one-byte literal, so the island declines the
    whole subtree. MEASURED: `ab|cd|a|b` stamps 0 islands by default and 1
    under `-fno-altcls-merge`. This scanner counts it as qualifying.
  - the emitter's own SIZE RULE declines an alternation whose trie would cost
    more than the chain it replaces, which this scanner does not model at all.

So the qualifying count below brackets nothing on its own: it is what the
pattern text admits, not what the emitter takes. Read it as the shape census
it is, and read `RX_VM_ALT_ISLANDS` for what actually fired.

NOT ORACLE-VERIFIED SEMANTICS, and it does not need to be: nothing here
decides what a pattern MATCHES.  It counts shapes.

Usage:
    python3 scripts/alt_census.py [--json OUT] [ROOT ...]

with no ROOT, censuses `tests/` under the repo root plus, if it is readable,
`/home/duxevents/pcrec-bench/bench/altwide/patterns`.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# the conservative pattern scanner
# ---------------------------------------------------------------------------

# Escapes whose meaning is a CLASS, an assertion, a backreference, a call or a
# control operator — anything that is not "one literal byte".  A branch that
# contains one is unqualified.  Listed rather than derived so that an escape
# this project adds later defaults to the UNQUALIFIED side by falling into the
# "unknown escape" arm below.
NON_LITERAL_ESC = set("dDwWsShHvVRNXbBAZzGKQEpPuUlLCcxo0123456789kg")

# Escapes that stand for exactly one literal byte.
SIMPLE_ESC = {"n": 10, "r": 13, "t": 9, "f": 12, "a": 7, "e": 27}


class Lit:
    """one literal byte, unquantified"""
    __slots__ = ("b",)

    def __init__(self, b):
        self.b = b


class Other:
    """anything else — the scanner's honest 'I will not qualify this'"""
    __slots__ = ("why",)

    def __init__(self, why):
        self.why = why


class Alt:
    """a flat alternation: a list of branches, each a list of Lit/Other/Alt"""
    __slots__ = ("branches", "capturing")

    def __init__(self, branches, capturing):
        self.branches = branches
        self.capturing = capturing


class Scanner:
    def __init__(self, pat):
        self.s = pat
        self.i = 0
        self.n = len(pat)
        self.alts = []          # every Alt found, innermost-first
        self.caseless = False
        self.failed = None      # a syntax the scanner could not follow

    # -- helpers ------------------------------------------------------------
    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def at(self, chars):
        """`peek() in chars`, minus Python's empty-string-is-a-substring trap"""
        c = self.peek()
        return c != "" and c in chars

    def eat(self):
        c = self.s[self.i]
        self.i += 1
        return c

    # -- the grammar --------------------------------------------------------
    def parse(self):
        """the whole pattern, as one (possibly one-branch) alternation"""
        a = self.parse_alt(capturing=False)
        if self.i < self.n:
            self.failed = self.failed or "trailing %r" % self.s[self.i]
        return a

    def parse_alt(self, capturing):
        branches = [self.parse_seq()]
        while self.peek() == "|":
            self.eat()
            branches.append(self.parse_seq())
        a = Alt(branches, capturing)
        self.alts.append(a)
        return a

    def parse_seq(self):
        items = []
        while self.i < self.n and self.peek() not in "|)":
            items.append(self.parse_atom())
            # a quantifier consumes the atom it follows: the result is not a
            # bare literal any more, whatever the atom was.
            if self.at("*+?"):
                self.eat()
                while self.at("*+?"):   # possessive / lazy suffix
                    self.eat()
                items[-1] = Other("quantifier")
            elif self.peek() == "{" and self.brace_is_quantifier():
                depth = 0
                while self.i < self.n:
                    c = self.eat()
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            break
                while self.at("*+?"):
                    self.eat()
                items[-1] = Other("quantifier")
        return items

    def brace_is_quantifier(self):
        m = re.match(r"\{\d*(,\d*)?\}", self.s[self.i:])
        return m is not None

    def parse_atom(self):
        c = self.eat()
        if c == "(":
            return self.parse_group()
        if c == "[":
            return self.parse_class()
        if c == "\\":
            return self.parse_escape()
        if c and c in ".^$":
            return Other("meta " + c)
        # An ordinary character.  Non-ASCII is left unqualified rather than
        # guessed at: pcrec's own encodings work is a separate axis.
        if ord(c) < 128:
            return Lit(ord(c))
        return Other("non-ascii")

    def parse_escape(self):
        if self.i >= self.n:
            self.failed = "trailing backslash"
            return Other("trailing backslash")
        c = self.eat()
        if c in SIMPLE_ESC:
            return Lit(SIMPLE_ESC[c])
        if c in NON_LITERAL_ESC:
            # \x41 and friends are one byte, but spelling them out here buys
            # nothing for a census and risks getting the syntax wrong.
            return Other("escape \\" + c)
        if c.isalnum():
            return Other("unknown escape \\" + c)
        return Lit(ord(c))          # \. \* \\ \/ ...

    def parse_class(self):
        # [...] — consume to the matching ']' with PCRE's own first-] rule.
        if self.peek() == "^":
            self.eat()
        if self.peek() == "]":
            self.eat()
        while self.i < self.n:
            c = self.eat()
            if c == "\\":
                if self.i < self.n:
                    self.eat()
            elif c == "[" and self.peek() == ":":
                while self.i < self.n and self.eat() != "]":
                    pass
            elif c == "]":
                return Other("class")
        self.failed = "unterminated class"
        return Other("unterminated class")

    def parse_group(self):
        capturing = True
        why = "group"
        if self.peek() == "?":
            self.eat()
            capturing = False
            c = self.peek()
            if c == ":":
                self.eat()
                why = "non-capturing group"
            elif c == ">":
                self.eat()
                why = "atomic group"
            elif c == "=" or c == "!":
                self.eat()
                why = "lookahead"
            elif c == "<" and self.i + 1 < self.n and self.s[self.i + 1] in "=!":
                self.eat()
                self.eat()
                why = "lookbehind"
            elif c and c in "<'P":
                # named group — capturing after all
                capturing = True
                while self.i < self.n and self.eat() not in ">'":
                    pass
                why = "named group"
            elif c == "#":
                while self.i < self.n and self.eat() != ")":
                    pass
                return Other("comment")
            else:
                # (?i) and friends, (?R), (?1), (?(cond)... — a modifier run or
                # something this scanner will not follow.  Consume to ')' at
                # this nesting level and report it as opaque.
                start = self.i
                depth = 1
                while self.i < self.n:
                    ch = self.eat()
                    if ch == "\\":
                        if self.i < self.n:
                            self.eat()
                    elif ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            break
                body = self.s[start:self.i - 1]
                if re.fullmatch(r"[a-zA-Z]*-?[a-zA-Z]*", body) and "i" in body.split("-")[0]:
                    self.caseless = True
                return Other("opaque (?...) construct")
        inner = self.parse_alt(capturing=capturing)
        if self.peek() == ")":
            self.eat()
        else:
            self.failed = "unclosed group"
        return Other(why)


# ---------------------------------------------------------------------------
# qualification and trie statistics
# ---------------------------------------------------------------------------

def branch_literal(items):
    """the byte string of a branch that is a bare literal run, else None"""
    out = bytearray()
    for it in items:
        if not isinstance(it, Lit):
            return None
        out.append(it.b)
    return bytes(out)


def trie_stats(words):
    """node count, max depth, max fan-out, and the MASK DEPTH.

    `words` is the ordered list of qualifying branch literals.  Because every
    trie edge here is a single BYTE, sibling edges are disjoint by
    construction and a subject selects ONE root-to-leaf path — so the set of
    accepts reachable at a position is exactly the accepts along that path,
    which is what makes the mask depth a static per-node quantity rather than
    a runtime one.
    """
    root = {}
    nodes = 1
    accepts = {}            # node id -> count of branches ending there
    ids = {id(root): 0}
    nextid = 1
    maxdepth = 0
    for w in words:
        cur = root
        for b in w:
            if b not in cur:
                cur[b] = {}
                nextid += 1
                ids[id(cur[b])] = nextid - 1
                nodes += 1
            cur = cur[b]
        accepts[id(cur)] = accepts.get(id(cur), 0) + 1
        maxdepth = max(maxdepth, len(w))

    maxfan = 0
    maskdepth = 0
    pushes = 0              # the island's own resume-point count (see report)
    trysites = 0

    # iterative to keep a deep trie off Python's own stack
    stack = [(root, 0)]
    while stack:
        node, pending = stack.pop()
        maxfan = max(maxfan, len(node))
        here = pending + accepts.get(id(node), 0)
        maskdepth = max(maskdepth, here)
        if accepts.get(id(node), 0):
            trysites += here
            pushes += here - 1
        for ch in node.values():
            stack.append((ch, here))

    return {
        "nodes": nodes,
        "depth": maxdepth,
        "fanout": maxfan,
        "mask_depth": maskdepth,
        "try_sites": trysites,
        "pushes": pushes,
    }


def census_pattern(pat):
    """every flat alternation in one pattern, classified"""
    sc = Scanner(pat)
    try:
        sc.parse()
    except Exception as e:                       # noqa: BLE001 - a census, not a gate
        return [], "scanner error: %s" % e, False
    rows = []
    for a in sc.alts:
        nbr = len(a.branches)
        if nbr < 2:
            continue
        lits, reasons = [], Counter()
        for items in a.branches:
            w = branch_literal(items)
            if w is None:
                if not items:
                    reasons["empty branch"] += 1
                else:
                    for it in items:
                        if isinstance(it, Other):
                            reasons[it.why] += 1
                            break
                lits = None
            elif lits is not None:
                lits.append(w)
        qualifies = lits is not None and len(lits) == nbr and all(lits)
        row = {
            "branches": nbr,
            "capturing": a.capturing,
            "qualifies": bool(qualifies),
            "decline": None if qualifies else (
                reasons.most_common(1)[0][0] if reasons else "mixed"),
        }
        if qualifies:
            row.update(trie_stats(lits))
        rows.append(row)
    return rows, sc.failed, sc.caseless


# ---------------------------------------------------------------------------
# corpus readers
# ---------------------------------------------------------------------------

def patterns_from_rxt(path):
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            if line.startswith("pattern "):
                out.append((line[len("pattern "):].rstrip("\n"), ln))
    return out


def patterns_from_rx(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read().strip("\n")
    return [(text, 1)] if text else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the full per-alternation table here")
    ap.add_argument("roots", nargs="*")
    args = ap.parse_args()

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roots = args.roots
    if not roots:
        roots = [os.path.join(here, "tests")]
        bench = "/home/duxevents/pcrec-bench/bench/altwide/patterns"
        if os.path.isdir(bench):
            roots.append(bench)

    files = []
    for r in roots:
        if os.path.isfile(r):
            files.append(r)
            continue
        for dirpath, _dirs, names in os.walk(r):
            for nm in sorted(names):
                if nm.endswith(".rxt") or nm.endswith(".rx"):
                    files.append(os.path.join(dirpath, nm))
    files.sort()

    rows = []
    npat = 0
    nscanfail = 0
    ncaseless = 0
    for path in files:
        reader = patterns_from_rxt if path.endswith(".rxt") else patterns_from_rx
        for pat, ln in reader(path):
            npat += 1
            alts, failed, caseless = census_pattern(pat)
            if failed:
                nscanfail += 1
            if caseless:
                ncaseless += 1
            for a in alts:
                a["file"] = os.path.relpath(path, here) if path.startswith(here) else path
                a["line"] = ln
                a["pattern"] = pat if len(pat) <= 120 else pat[:117] + "..."
                a["caseless_pattern"] = caseless
                rows.append(a)

    q = [r for r in rows if r["qualifies"]]
    print("== [ENG-ISL] alternation census ==")
    print("files scanned          : %d" % len(files))
    print("patterns read          : %d" % npat)
    print("patterns the scanner could not fully follow : %d" % nscanfail)
    print("patterns with a (?i)-style modifier run     : %d" % ncaseless)
    print("flat alternations (>=2 branches)            : %d" % len(rows))
    print("  QUALIFYING (all branches bare literal)    : %d" % len(q))
    print("  declined                                  : %d" % (len(rows) - len(q)))
    print()
    print("-- decline reasons (first offending element per alternation) --")
    for why, k in Counter(r["decline"] for r in rows if not r["qualifies"]).most_common():
        print("  %-42s %6d" % (why, k))
    print()
    print("-- qualifying branch-width distribution --")
    widths = Counter(r["branches"] for r in q)
    for w in sorted(widths):
        print("  width %-6d %6d alternations" % (w, widths[w]))
    print()
    if q:
        print("-- qualifying trie statistics --")
        for key, label in (("nodes", "trie nodes"), ("depth", "trie depth"),
                           ("fanout", "max fan-out"), ("mask_depth", "MASK DEPTH"),
                           ("try_sites", "island try sites"),
                           ("pushes", "island resume points")):
            vals = sorted(r[key] for r in q)
            print("  %-20s min %-6d median %-6d max %-6d" %
                  (label, vals[0], vals[len(vals) // 2], vals[-1]))
        print()
        print("-- MASK DEPTH distribution (accepts pending on one path) --")
        for d, k in sorted(Counter(r["mask_depth"] for r in q).items()):
            print("  depth %-4d %6d alternations" % (d, k))
        print()
        print("-- the widest qualifying alternations --")
        for r in sorted(q, key=lambda r: -r["branches"])[:12]:
            print("  %4d branches  depth %-3d nodes %-7d mask %d  %s:%d" %
                  (r["branches"], r["depth"], r["nodes"], r["mask_depth"],
                   r["file"], r["line"]))
        print()
        print("-- qualifying alternations whose MASK DEPTH exceeds 1 --")
        deep = [r for r in q if r["mask_depth"] > 1]
        if not deep:
            print("  (none)")
        for r in sorted(deep, key=lambda r: -r["mask_depth"])[:20]:
            print("  mask %-3d width %-4d  %-40s  %s:%d" %
                  (r["mask_depth"], r["branches"], r["pattern"][:40],
                   r["file"], r["line"]))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)
        print("\nfull table -> %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
