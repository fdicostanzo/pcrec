#!/usr/bin/env python3
"""docs/design/ctx_span/derive_rows.py -- ctx_span.md rev 2 §4.5.4's derived sabotage
list (B5/B6/C1: the hand-made re-aim list is replaced by a derivation).

Inputs: ROOT, the anchor map written by ../start_table/sabotage_anchors.py over
edit_set.tsv (sabotage_anchors.tsv), the call graph (call_graph.txt) and the edit set.
A row is selected by ANY of three facts, each computed here, none hand-listed:
  anchor   the anchor map classes it RE-AIM (its anchor text is in an edit-set
           def/token/line): the commit named there rewrites it;
  owner    its anchor's OWNER definition contains an edit-set occurrence (the body
           changes around an unchanged anchor): RE-RUN in that commit;
  witness  the row's SAB_* assignments (REACH, REACH_POP, DESC, DOC_FIGURE, SUITES)
           name `(?m)`, N_BOT_M/N_EOL_M, mlinectx or the newline row: its witness or
           detector is in the population P2c moves: RE-RUN at P2c, reach re-verified.
A row that names `(?m)` only in comments is printed as `comment` (no obligation).
The DISPOSITION (re-aim / retire / re-run) is the note's, by reading each row's intent;
this script only derives the population. Usage:
  python3 -I derive_rows.py ROOT sabotage_anchors.tsv call_graph.txt edit_set.tsv"""
import collections, glob, os, re, sys
root, amap, cgp, esp = sys.argv[1:5]
defs = collections.defaultdict(list)
for l in open(cgp):
    p = l.rstrip("\n").split("\t")
    if p[0].startswith("def-"):
        f, rng = p[2].rsplit(":", 1)
        a, b = map(int, rng.split("-"))
        defs[f].append((a, b, p[1]))
def owner(f, ln):
    best = None
    for a, b, n in defs.get(f, []):
        if a <= ln <= b and (best is None or b - a < best[1] - best[0]):
            best = (a, b, n)
    return best[2] if best else None
edits = []
for l in open(esp):
    if l.startswith("#") or not l.strip():
        continue
    k, v, c, why = l.rstrip("\n").split("\t")
    edits.append((k, v.strip(), c))
touched = collections.defaultdict(set)          # owner -> commits
why_t = collections.defaultdict(set)            # owner -> the edit text that touched it
COMMENT = re.compile(r"^\s*(/?\*|//)")
for f in defs:
    try:
        txt = open(os.path.join(root, f), encoding="latin-1").read()
    except OSError:
        continue
    for k, v, c in edits:
        if k == "def":
            continue
        i = txt.find(v)
        while v and i >= 0:
            ln = txt.count("\n", 0, i) + 1
            line = txt.split("\n")[ln - 1]
            o = owner(f, ln)
            # a comment mention is rewritten too, but moves no behaviour around an
            # anchor: it is not an owner fact (the comment re-wording is listed in
            # the note's comment census instead)
            if o and not COMMENT.match(line):
                touched[o].add(c)
                why_t[o].add(v[:24])
            i = txt.find(v, i + 1)
for k, v, c in edits:
    if k == "def":
        touched[v].add(c)
rows = {}
for l in open(amap):
    p = l.rstrip("\n").split("\t")
    if len(p) < 10 or not p[1].startswith("S"):
        continue
    rows.setdefault(p[0], []).append(p)
wit = re.compile(r"\(\?m\)|N_BOT_M|N_EOL_M|mlinectx|MLINECTX|CTXROW_NEWLINE|nl_bit")
out = []
for path in sorted(glob.glob(os.path.join(root, "tests/mech/sabotages/S*.sh"))):
    name = os.path.basename(path)[:-3]
    sid = name.split("_")[0]
    txt = open(path, encoding="latin-1").read()
    sab = "\n".join(l for l in txt.split("\n") if re.match(r"\s*SAB_[A-Z0-9_]*=", l))
    facts = []
    for p in rows.get(name, []):
        if p[8] == "RE-AIM":
            facts.append(f"anchor:{p[9]}:{p[4]}")
        o = p[4]
        if o in touched and p[8] != "RE-AIM":
            facts.append(f"owner:{','.join(sorted(touched[o]))}:{o}({'|'.join(sorted(why_t[o]))})")
    if wit.search(sab):
        facts.append("witness:P2c")
    elif wit.search(txt) and not facts:
        facts.append("comment")
    if facts:
        out.append((sid, name, ";".join(sorted(set(facts)))))
for sid, name, f in out:
    print(f"{sid}\t{name}\t{f}")
print(f"# derived rows {sum(1 for o in out if o[2] != 'comment')}, comment-only {sum(1 for o in out if o[2] == 'comment')}", file=sys.stderr)
