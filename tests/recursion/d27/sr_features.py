#!/usr/bin/env python3
"""sr_features.py -- does every block declare ALL the modules it needs?

A block that forgets a feature is REFUSED by pcrec and, if it is a `perr`
block, PASSES VACUOUSLY: it was rejected, just not for the reason the block
claims to test. The previous module's blinded corpus lost 365 first-pass
cells to exactly this, so the brief requires this check to come from a
DIFFERENT derivation than the writer. It has two arms, and neither of them
is "read sr_gen.py's feature lists":

  ARM A -- LEXICAL. Scan the PATTERN TEXT for construct spellings and derive
  the module set from the text alone, character by character, with a scanner
  written here and nowhere else. Compare to what the .rxt file declares.
  Declared must be a SUPERSET of required.

  ARM B -- EXISTENCE, through the compiler, which D27 permits for exactly
  this question ("you may compile a cell to see whether it is REFUSED").
  This arm never reads an expectation and never sources one:
    B1 SUFFICIENCY. Every non-perr block must COMPILE under its declared
       features. A missing module shows up as a refusal.
    B2 ANTI-VACUITY, the one that matters. Every `perr` block is compiled
       AGAIN with `--features all`. If it now compiles, the block was being
       rejected by a FEATURE GATE rather than by the rule it claims to
       test, and the block is vacuous. This is the check that a corpus
       author cannot fake by declaring features carefully, because it does
       not look at the declaration at all.
    B3 MINIMALITY. Each declared feature is dropped in turn; the block
       should then be refused. A feature that can be dropped with no effect
       was not needed -- reported as INFO rather than as a failure, since
       the brief mandates `recursion` on every block of this corpus whether
       or not the block's own pattern contains a call.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
PCREC = os.path.join(CELL, "build", "pcrec")

ALL = ("recursion,named-groups,backrefs,assertions,lookaround,atomic-groups,"
       "modifiers,classes,conditionals,branch-reset,comments,quoting,misc,"
       "verbs,unicode-props,extended-classes")


# ---------------------------------------------------------------------------
# ARM A: a lexical scanner over the pattern text.
# ---------------------------------------------------------------------------
def header_len(rest):
    """How many characters of `rest` (which starts with `(?`) belong to the
    construct's HEADER rather than to its body. Without this the `+` in
    `(?+1)` and the `?` in `(?:` get re-read as quantifier suffixes, which
    is a bug in THIS scanner and would report a module the pattern does not
    use. Found by arm B1 disagreeing with arm A on seven blocks."""
    t = rest[2:]
    if t.startswith("(DEFINE)"):
        return 2 + len("(DEFINE)")
    if t.startswith("P<") or t.startswith("P=") or t.startswith("P>"):
        j = rest.find(">" if t[1] == "<" else ")", 2)
        return (j + 1) if j > 0 else len(rest)
    if t[:1] in "<'" and not t.startswith("<=") and not t.startswith("<!") \
            and not t.startswith("<*"):
        close = ">" if t[0] == "<" else "'"
        j = rest.find(close, 3)
        return (j + 1) if j > 0 else len(rest)
    if t.startswith("<=") or t.startswith("<!") or t.startswith("<*"):
        return 4
    if t[:1] in "=!>:*|":
        return 3
    if t[:1] == "&" or t[:1] == "R" or t[:1] == "C" or t[:1] == "#" \
            or re.match(r"[-+]?\d", t):
        j = rest.find(")", 2)
        return (j + 1) if j > 0 else len(rest)
    if t[:1] == "(":
        return 3
    j = min([x for x in (rest.find(")", 2), rest.find(":", 2)) if x > 0]
            or [len(rest) - 1])
    return j + 1


def required(pat):
    """The module set the pattern's TEXT demands, by direct scan."""
    need = set()
    i = 0
    inclass = False
    n = len(pat)
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            e = pat[i + 1]
            if inclass:
                # inside a class \b is a backspace, \g and \k are literals
                if e in "dDsSwWhHvVnN":
                    need.add("classes")
                i += 2
                continue
            if e in "dDsSwWhHvVN":
                need.add("classes")
            elif e in "bBAzZG":
                need.add("assertions")
            elif e == "K":
                need.add("assertions")
            elif e == "k":
                need.add("backrefs")
                need.add("named-groups")
            elif e in "pP":
                need.add("unicode-props")
            elif e in "QE":
                need.add("quoting")
            elif e in "RXC":
                need.add("misc")
            elif e == "g":
                # \g<...> and \g'...' are CALLS (recursion); \g{...} and
                # \gN are REFERENCES (backrefs). One character apart.
                j = i + 2
                if j < n and pat[j] in "<'":
                    need.add("recursion")
                    close = ">" if pat[j] == "<" else "'"
                    k = pat.find(close, j + 1)
                    body = pat[j + 1:k] if k > 0 else ""
                    if body and not re.fullmatch(r"[-+]?\d+", body):
                        need.add("named-groups")
                elif j < n and pat[j] == "{":
                    need.add("backrefs")
                    k = pat.find("}", j)
                    body = pat[j + 1:k] if k > 0 else ""
                    if body and not re.fullmatch(r"[-+]?\d+", body):
                        need.add("named-groups")
                else:
                    need.add("backrefs")
            elif e.isdigit() and e != "0":
                need.add("backrefs")
            i += 2
            continue
        if inclass:
            if c == "]":
                inclass = False
            i += 1
            continue
        if c == "[":
            inclass = True
            i += 1
            continue
        if c == "(":
            rest = pat[i:]
            if rest.startswith("(?"):
                skip = header_len(rest)
                t = rest[2:]
                if t.startswith("(DEFINE)"):
                    need.add("recursion")
                elif t[:1] == "&":
                    need.add("recursion")
                    need.add("named-groups")
                elif t.startswith("P>"):
                    need.add("recursion")
                    need.add("named-groups")
                elif t.startswith("P<"):
                    need.add("named-groups")
                elif t.startswith("P="):
                    need.add("backrefs")
                    need.add("named-groups")
                elif t[:1] in "=!":
                    need.add("lookaround")
                elif t[:1] == "*":
                    need.add("lookaround")
                elif t.startswith("<=") or t.startswith("<!") \
                        or t.startswith("<*"):
                    need.add("lookaround")
                elif t[:1] == "<" or t[:1] == "'":
                    need.add("named-groups")
                elif t[:1] == ">":
                    need.add("atomic-groups")
                elif t[:1] == "R":
                    need.add("recursion")
                elif t[:1] == "#":
                    need.add("comments")
                elif t[:1] == "C":
                    need.add("callouts")
                elif t[:1] == "|":
                    need.add("branch-reset")
                elif t[:1] == "(":
                    need.add("conditionals")
                elif re.match(r"[-+]?\d", t):
                    need.add("recursion")
                elif t[:1] == ":":
                    pass
                elif re.match(r"[a-zA-Z^-]*[):]", t):
                    need.add("modifiers")
                i += skip
                continue
            i += 1
            continue
        # possessive quantifier suffixes
        if c == "+" and i > 0 and pat[i - 1] in "*+?}":
            need.add("atomic-groups")
        i += 1
    return need


# ---------------------------------------------------------------------------
# ARM B: the compiler, asked only whether it refuses.
# ---------------------------------------------------------------------------
def compiles(pat, feats, tmp):
    cmd = [PCREC, "-p", "rx", "-o", os.path.join(tmp, "g.c")]
    if feats:
        cmd += ["--features", feats]
    cmd += ["--", pat]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or "").strip()


def blocks_of(path):
    """(lineno, pattern, features-list, is_perr) for each block."""
    out = []
    cur = None
    for lineno, raw in enumerate(open(path), 1):
        line = raw.rstrip("\n")
        if line.startswith("#") or not line.strip():
            continue
        head, _, rest = line.partition(" ")
        if head == "pattern":
            if cur:
                out.append(cur)
            cur = [lineno, rest, [], False]
        elif cur is None:
            continue
        elif head == "features":
            cur[2] = [x for x in rest.split(",") if x]
        elif head == "perr":
            cur[3] = True
    if cur:
        out.append(cur)
    return out


def main():
    if not os.path.exists(PCREC):
        print("no build/pcrec at", PCREC)
        return 1
    files = sorted(f for f in os.listdir(HERE) if f.endswith(".rxt"))
    fails, infos = [], []
    nblocks = 0
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            for lineno, pat, feats, is_perr in blocks_of(os.path.join(HERE, f)):
                nblocks += 1
                where = "%s:%d" % (f, lineno)
                decl = set(feats)

                # ARM A
                req = required(pat)
                missing = req - decl
                if missing:
                    fails.append("A %s: pattern needs %s but declares %s -- "
                                 "%r" % (where, sorted(missing),
                                         sorted(decl) or "nothing", pat))

                if "recursion" not in decl:
                    fails.append("A %s: every block of this corpus must "
                                 "declare `recursion` -- %r" % (where, pat))

                # ARM B1 / B2
                ok, err = compiles(pat, ",".join(feats), tmp)
                if is_perr:
                    ok_all, _ = compiles(pat, ALL, tmp)
                    if ok_all:
                        fails.append("B2 %s: perr block COMPILES under "
                                     "--features all -- whatever refused it "
                                     "under its own feature list was a "
                                     "FEATURE GATE, not the rule the block "
                                     "claims to test. VACUOUS. -- %r"
                                     % (where, pat))
                    elif ok:
                        fails.append("B2 %s: perr block COMPILES under its "
                                     "own declared features -- %r"
                                     % (where, pat))
                else:
                    if not ok:
                        fails.append("B1 %s: block with cases is REFUSED "
                                     "under its declared features %s: %s -- "
                                     "%r" % (where, sorted(decl),
                                             err[:160], pat))

                # ARM B3
                for drop in sorted(decl):
                    reduced = ",".join(x for x in feats if x != drop)
                    ok2, _ = compiles(pat, reduced, tmp)
                    if is_perr:
                        continue
                    if ok2:
                        infos.append("B3 %s: feature %r can be dropped and "
                                     "the block still compiles -- %r"
                                     % (where, drop, pat))

    print("checked %d blocks in %d files" % (nblocks, len(files)))
    if infos:
        print("\n%d INFO (over-declared features; `recursion` on a "
              "call-free control block is required by the brief and "
              "expected here):" % len(infos))
        for i in infos[:40]:
            print("  -", i)
        if len(infos) > 40:
            print("  … and %d more" % (len(infos) - 40))
    if fails:
        print("\n%d FEATURES FAILURE(S):" % len(fails))
        for e in fails:
            print("  *", e)
        return 1
    print("\nNo block under-declares a feature; no perr block is vacuous.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
