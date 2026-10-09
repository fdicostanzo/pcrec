#!/usr/bin/env python3
"""docs/design/start_table/sabotage_anchors.py -- revision 2.1 ([r2 sound-M6,
checks-M1]; [r2.1 C-N1, C-N5, S-N3, S-N4]). Maps EVERY sabotage anchor site
(SAB_FILE/SAB_BEFORE and SAB_FILE2/SAB_BEFORE2, every target file, not only
the two emitters) to the definition it sits in, and classifies it -- with NO
hand-written family list:

  FAMILY  the owner is a member of call_graph.py's derived start family, or
          one of its seeds (the landmark readers), or a definition the
          refactor edits (refactor_edit_set.tsv `def`).
  RE-AIM  the anchor sits in an edit-set `def`, or its text OVERLAPS an
          occurrence of an edit-set `token` or `line` in its file: each commit
          named there rewrites the anchor's text, so the row is re-aimed in
          that commit, intent re-verified. A row moved by two commits (S441:
          C5 deletes the tag switch, C5b makes R3 read BOUND) lists both.
  RE-RUN  a FAMILY anchor the plan keeps byte-stable. `rerun_at` names every
          commit whose edit set touches the anchor's OWNER definition (its
          body changes around the unchanged anchor) -- the row re-runs in that
          commit, not only once after C5b [r2.1 C-N5]; a row whose owner no
          commit touches re-runs once after C5b.
  OTHER   not in the family. The `reads` column lists every seed, VM seed
          field or family member the ANCHOR TEXT names, so an OTHER row that
          plants a landmark read is visible rather than silently excluded
          [r2.1 S-N4]; the summary counts them.

OWNER RESOLUTION [r2.1 C-N1]. Revision 2 left 61 sites with owner "?" (an
anchor in a comment block, a struct, a .def row, a header) and classed them
OTHER, which silently dropped start-family rows (S282, S299, S475, S479,
S496). Now, in order:
  1. `def`      the innermost call_graph.py definition containing the line
                (functions, tables, data, types, function-like and object-like
                macros, headers included);
  2. `factrow`  a src/facts/facts.def PF_FACT(NAME, ...) row -> the seed
                pcrec_fact_<name> (the SAME rule call_graph.py uses to derive
                the seeds from that file);
  3. `datarow`  a row of any other .def X-macro file -> `row:<file>:<ARG>`;
                FAMILY iff ARG is named on a call-graph decision SITE line
                (a start decision reads the row), not merely somewhere in a
                family body (pcrec_emit_vm is a family member and names
                nearly everything);
  4. `lead`     a line in a comment block (or blank) whose next code line
                starts a definition -> that definition (its header comment);
  5. `filescope` a file-scope preprocessor line (#include, #if, ...) or a
                file-scope `_Static_assert` (a declaration outside every
                definition; its anchor may span lines, the first line decides);
  6. `outside`  a file outside src/ (tests/, cli/, scripts/): the call graph
                is src/-only, so no such site is a start decision BY THE
                GRAPH'S DEFINITION (named, counted, never silently family);
  7. otherwise UNRESOLVED -- a hard error (exit 2) for a src/ file.

Also reports each site's occurrence count against SAB_COUNT (the rule
scripts/m6read_check_sab_anchors.py enforces in make test-codegen
[SABANCHOR], the per-commit gate), and every sabotage id shared by two row
FILES (rows are keyed by file, so a shared id is not merged away).

STEPS (`--step NAME=A..B`, repeatable; [admin1008b], stc4_report.md §4 item
3 / stc5_report.md §4 item 6). `rerun_at` as derived above reads the PLAN's
edit set, so it misses (a) a row whose predicate is REACHED differently by a
commit -- a walk replaced -- and (b) a row in a definition a later commit
edits that the edit set names only at an earlier commit. Given the steps' git
ranges, `rerun_at` ALSO takes, per step, from the commit's ACTUAL diff
(`git diff -U0 A B -- src`, ROOT being the A tree):
  hunk    the anchor's owner is a definition whose OLD-side range a hunk
          overlaps (a pure insertion counts when it lands inside the body):
          commit diff hunks -> enclosing definitions;
  reach   the walk-reach relation. The anchor's owner is (0) NAMED by a
          hunk's changed text (either side), (1) stored in a TABLE the
          REMOVED text names (the walk that was replaced), (2..K) called by
          what hop 1 reached (`--reach-hops K`, default 2), or a CALLER of a
          definition whose removed text names a table (its answer now comes
          from the new walk). A hunk that only renames identifiers
          (consistently across the whole step) moves no behaviour and is
          ignored.
Derived commits are added for EVERY class except a row the same commit
RE-AIMs (its anchor text moves there; the re-aim re-runs it). The new last
column `rerun_via` says why, per step: `C4:hunk`, `C4:reach(<via>)`,
`C4:edit-set`. `--compare NAME=S1,S2,...` prints the difference between a
step's derived rows and a hand list (the rows a lane re-ran by judgment).

Usage: sabotage_anchors.py ROOT CALL_GRAPH_TSV EDIT_SET_TSV
           [--repo REPO] [--step NAME=A..B]... [--reach-hops K]
           [--compare NAME=S1,S2,...]... [--final LABEL] [--edit-names]
--final LABEL names the single re-run of a RE-RUN row whose owner no commit
touches (default after-C5b, the start table's last commit; the fallback
family passes after-B6, dec_fallback.md §4.2 item 9). --edit-names adds, for
a RE-RUN row, every commit whose edit-set token/line text NAMES the owner
(`rerun_via` edit-names): the plan-level form of the --step reach hop 0;
and every commit that REWRITES (edit-set `def`) a definition the owner's
body names (`calls-rewritten`).
CALL_GRAPH_TSV may be either family's call_graph.py output.
Read-only; prints TSV (rowfile, id, site, file, owner, resolution, line,
count/want, class, commits, rerun_at, reason, reads, rerun_via) and a summary
on stderr. Without --step the output is byte-identical to the earlier form
apart from the empty last column.
"""
import collections, glob, os, re, subprocess, sys

import argparse
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("root")
_ap.add_argument("cgp")
_ap.add_argument("esp")
_ap.add_argument("--repo")
_ap.add_argument("--step", action="append", default=[])
_ap.add_argument("--reach-hops", type=int, default=2)
_ap.add_argument("--compare", action="append", default=[])
_ap.add_argument("--final", default="after-C5b")
_ap.add_argument("--edit-names", action="store_true")
_a = _ap.parse_args()
root, cgp, esp = _a.root, _a.cgp, _a.esp
defs = collections.defaultdict(list)   # file -> [(start, end, name, kind)]
defrange = {}                          # name -> (file, start, end)
family, seeds = set(), set()
site_lines = []                        # (file, line) of every decision site
for l in open(cgp):
    p = l.rstrip("\n").split("\t")
    if p[0].startswith("def-"):
        f, rng = p[2].rsplit(":", 1)
        a, b = map(int, rng.split("-"))
        defs[f].append((a, b, p[1], p[0][4:]))
        defrange.setdefault(p[1], (f, a, b))
    elif p[0].startswith("family-"):
        family.add(p[1])
    elif p[0] == "site":
        f, ln = p[2].rsplit(":", 1)
        site_lines.append((f, int(ln)))
    elif p[0] == "seed":
        family.add(p[1])
        seeds.add(p[1])
SEED_FIELDS = {"root_minw", "mrl_win", "nclamp", "prefilter_collapsed"}
edit = {"def": {}, "token": collections.defaultdict(list), "line": collections.defaultdict(list)}
for l in open(esp):
    if l.startswith("#") or not l.strip():
        continue
    k, v, c, why = l.rstrip("\n").split("\t")
    if k == "def":
        edit["def"][v] = (c, why)
    else:
        edit[k][v].append((c, why))
family |= set(edit["def"])

_txt, _lines = {}, {}


def text(f):
    if f not in _txt:
        _txt[f] = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        _lines[f] = _txt[f].split("\n")
    return _txt[f]


def lineno(f, idx):
    return text(f).count("\n", 0, idx) + 1


def innermost(f, line):
    best = None
    for a, b, n, k in defs.get(f, []):
        if a <= line <= b and (best is None or a >= best[0]):
            best = (a, n)
    return best[1] if best else None


sitetext = None


def named_by_site(tok):
    global sitetext
    if sitetext is None:
        text("src/gen/emit_dfa.c")
        sitetext = "\n".join(text(f).split("\n")[ln - 1] for f, ln in site_lines)
    return re.search(r'\b' + re.escape(tok) + r'\b', sitetext) is not None


def resolve(f, line):
    """(owner, resolution) for a site at f:line, or (None, 'unresolved')."""
    if not f.startswith("src/"):
        own = innermost(f, line)
        return (own, "def") if own else (f"file:{f}", "outside")
    own = innermost(f, line)
    if own:
        return own, "def"
    L = _lines[f]
    cur = L[line - 1]
    if f.endswith(".def"):
        m = re.match(r'^\s*([A-Z_][A-Z0-9_]*)\(\s*([A-Za-z_]\w*)', cur)
        if m:
            if f == "src/facts/facts.def" and m.group(1) == "PF_FACT":
                return f"pcrec_fact_{m.group(2).lower()}", "factrow"
            return f"row:{os.path.basename(f)}:{m.group(2)}", "datarow"
    s = cur.strip()
    if not s or s.startswith(("/*", "*", "//")):
        k = line - 1
        while k < len(L):
            t = L[k].strip()
            if not t or t.startswith(("/*", "*", "//")) or t.endswith("*/"):
                k += 1
                continue
            break
        starts = {a: n for a, b, n, kd in defs.get(f, [])}
        if k + 1 in starts:
            return starts[k + 1], "lead"
    if s.startswith(("#", "_Static_assert", "static_assert")):
        return f"file:{f}", "filescope"
    return None, "unresolved"


def shvars(path):
    r = subprocess.run(
        ["bash", "-c",
         'set -a; SAB_FILE=; SAB_BEFORE=; SAB_COUNT=; SAB_FILE2=; SAB_BEFORE2=; '
         'SAB_COUNT2=; . "$1" >/dev/null 2>&1; '
         'printf "%s\\0%s\\0%s\\0%s\\0%s\\0%s" "$SAB_FILE" "$SAB_BEFORE" '
         '"${SAB_COUNT:-1}" "$SAB_FILE2" "$SAB_BEFORE2" "${SAB_COUNT2:-1}"', "_", path],
        capture_output=True, text=True)
    v = r.stdout.split("\0")
    return [(v[0], v[1], int(v[2] or 1), 1), (v[3], v[4], int(v[5] or 1), 2)]


def occurrences(txt, s):
    out, i = [], txt.find(s)
    while s and i >= 0:
        out.append((i, i + len(s)))
        i = txt.find(s, i + 1)
    return out


_edits = {}


def edit_spans(f):
    """[(start, end, commit, why)] for every token/line occurrence in f."""
    if f not in _edits:
        sp = []
        txt = text(f)
        for k in ("token", "line"):
            for v, cws in edit[k].items():
                for a, b in occurrences(txt, v.strip()):
                    for c, why in cws:
                        sp.append((a, b, c, f"{k} {v.strip()[:40]}"))
        _edits[f] = sp
    return _edits[f]


def named_in_edits(own):
    """commits whose edit-set token/line TEXT names `own` as a word: a row
    that stores or calls it is rewritten there (fit_rungs[]'s rows name each
    fit_*_applies), so its anchor's behaviour is reached by that commit even
    though the owner's own body is untouched (--edit-names)."""
    out = set()
    rx = re.compile(r'\b' + re.escape(own) + r'\b')
    for k in ("token", "line"):
        for v, cws in edit[k].items():
            if rx.search(v):
                out |= {c for c, _ in cws}
    return out


def calls_rewritten(f, own):
    """commits that REWRITE (edit-set `def`) a definition `own`'s body names:
    the owner's answer now comes from the new body (S40 calls esel_of)."""
    out = set()
    if own not in defrange or defrange[own][0] != f:
        return out
    _, a, b = defrange[own]
    ids = set(re.findall(r'[A-Za-z_]\w*', "\n".join(code_of(l) for l in text(f).split("\n")[a - 1:b])))
    for d, (c, _w) in edit["def"].items():
        if d != own and d in ids:
            out.add(c)
    return out


def touched(f, own):
    """commits whose edit set touches definition `own`'s range in f."""
    out = set()
    if own in edit["def"]:
        out.add(edit["def"][own][0])
    if own not in defrange or defrange[own][0] != f:
        return out
    _, a, b = defrange[own]
    for s, e, c, _w in edit_spans(f):
        if a <= lineno(f, s) <= b:
            out.add(c)
    return out


ORDER = ["C0", "C1", "C2", "C3", "C4", "C5", "C5b", "C6", "C7",
         "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "L0", "L2"]

# ---- [admin1008b] STEPS: rerun_at from each commit's actual diff ----------
kindof = {}
for _f, _ds in defs.items():
    for _a2, _b2, _n2, _k2 in _ds:
        kindof.setdefault(_n2, _k2)
IDENT = re.compile(r'\b[A-Za-z_]\w*\b')


def code_of(l):
    l = re.sub(r'"(\\.|[^"\\])*"', '""', l)
    return re.sub(r'/\*.*?\*/|//.*$', '', l)


def parse_diff(repo, a, b):
    """{file: [(old_start, old_len, [old lines], [new lines])]} of
    `git diff -U0 --no-renames A B -- src` (the hunks' OLD-side coordinates
    are the A tree's, which is ROOT's)."""
    r = subprocess.run(["git", "-C", repo, "diff", "-U0", "--no-renames", "--no-color",
                        a, b, "--", "src"], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        sys.exit(f"sabotage_anchors: git diff {a} {b} failed: {r.stderr.strip()}")
    out, cur, hk = collections.defaultdict(list), None, None
    for l in r.stdout.split("\n"):
        if l.startswith("--- "):
            cur = None if l == "--- /dev/null" else l[6:]
        elif l.startswith("+++ "):
            if l != "+++ /dev/null" and cur is None:
                cur = l[6:]
        elif l.startswith("@@"):
            m = re.match(r'@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@', l)
            hk = (int(m.group(1)), 1 if m.group(2) is None else int(m.group(2)), [], [])
            out[cur].append(hk)
        elif hk is not None and l[:1] == "-" and not l.startswith("--- "):
            hk[2].append(l[1:])
        elif hk is not None and l[:1] == "+" and not l.startswith("+++ "):
            hk[3].append(l[1:])
    return out


_edgecache = {}


def def_edges(n):
    """Definitions a definition's body names (call_graph.py's edge rule,
    re-derived from the def ranges: comments and strings out, no self edge)."""
    if n not in _edgecache:
        f, a, b = defrange[n]
        text(f)
        out = set()
        for ln in _lines[f][a - 1:b]:
            if ln.lstrip().startswith(("*", "/*")):
                continue
            for t in IDENT.findall(code_of(ln)):
                if t in defrange and t != n:
                    out.add(t)
        _edgecache[n] = out
    return _edgecache[n]


TOK = re.compile(r'[A-Za-z_]\w*|\s+|.', re.S)


def rename_pairs(old, new):
    """{old_ident: new_ident} when `new` is `old` with identifiers substituted
    (same line count, same tokens everywhere but identifier positions), else
    None. A pure rename moves no behaviour, so it re-runs no row."""
    if len(old) != len(new):
        return None
    pairs = {}
    for lo, ln in zip(old, new):
        to, tn = TOK.findall(lo), TOK.findall(ln)
        if len(to) != len(tn):
            return None
        for x, y in zip(to, tn):
            if x == y:
                continue
            if not (IDENT.fullmatch(x) and IDENT.fullmatch(y)):
                return None
            if pairs.setdefault(x, y) != y:
                return None
    return pairs


def step_sets(repo, a, b, hops):
    """(touched, reach): touched = definitions of ROOT a hunk's old-side range
    overlaps; reach = {definition: via} -- named by a hunk's changed text
    (via itself), stored in a TABLE so named (hop 1), or called by such a
    stored definition (hop 2+)."""
    touched, named, walkers, oldnamed = set(), {}, set(), set()
    diff = parse_diff(repo, a, b)
    # consistent renames across the WHOLE step: an identifier renamed to two
    # different names (or by a hunk that changes anything else) is not one
    ren, bad = {}, set()
    for hunks in diff.values():
        for os_, ol, old, new in hunks:
            pr = rename_pairs(old, new)
            for x, y in (pr or {}).items():
                if ren.setdefault(x, y) != y:
                    bad.add(x)
    renamed_hunks = 0
    for f, hunks in diff.items():
        for os_, ol, old, new in hunks:
            pr = rename_pairs(old, new)
            if pr and not (set(pr) & bad):
                renamed_hunks += 1
                continue
            for da, db, dn, dk in defs.get(f, []):
                if ol > 0:
                    hit = os_ <= db and os_ + ol - 1 >= da
                else:
                    hit = da <= os_ < db    # insertion after line os_, inside the body
                if hit:
                    touched.add(dn)
                    # a WALK REPLACED: the removed text names a table (the old
                    # walk's `DFA_SELECT(..., req_admits, ...)` spelling)
                    if any(kindof.get(t) in ("table", "data") and t != dn
                           for ln in old for t in IDENT.findall(code_of(ln))
                           if t in defrange) and dk in ("func", "macro"):
                        walkers.add(dn)
            for side, lns in ((0, old), (1, new)):
                for ln in lns:
                    if ln.lstrip().startswith(("*", "/*")):
                        continue
                    for t in IDENT.findall(code_of(ln)):
                        if t in defrange:
                            named.setdefault(t, t)
                            if side == 0:
                                oldnamed.add(t)
    reach = dict(named)
    # level 1: what a TABLE named by the removed text stores; level k+1: what level k calls. Only
    # what is reached THROUGH a table expands -- a named walker's callees
    # (the emitter hubs) would reach the world.
    # (only a table the REMOVED text names: the walk that was replaced)
    frontier = {y: via for x, via in named.items()
                if x in oldnamed and kindof.get(x) in ("table", "data")
                for y in def_edges(x) if kindof.get(y) != "type"}
    for hop in range(1, hops + 1):
        for y, via in frontier.items():
            reach.setdefault(y, via)
        if hop == hops:
            break
        frontier = {z: via for y, via in frontier.items() for z in def_edges(y)
                    if kindof.get(z) != "type"}
    # the walk's CONSUMERS: whatever calls a definition whose walk was replaced
    # now gets its answer from the new walk (one hop of callers).
    for w in walkers:
        for c in callers_of(w):
            reach.setdefault(c, f"caller of {w}")
    return touched, reach, renamed_hunks


_rev = None


def callers_of(n):
    global _rev
    if _rev is None:
        _rev = collections.defaultdict(set)
        for x in defrange:
            for y in def_edges(x):
                _rev[y].add(x)
    return _rev[n]


steps = []          # [(name, touched, reach)] in the order given
for st in _a.step:
    nm, _, rng = st.partition("=")
    ra, _, rb = rng.partition("..")
    if not nm or not ra or not rb:
        sys.exit(f"sabotage_anchors: --step wants NAME=A..B, got {st!r}")
    t_, r_, nren = step_sets(_a.repo or root, ra, rb, _a.reach_hops)
    steps.append((nm, t_, r_))
    print(f"STEP {nm} {ra}..{rb}: {len(t_)} definitions edited, {len(r_)} reached, "
          f"{nren} pure-rename hunks ignored", file=sys.stderr)
stepnames = [n for n, _, _ in steps]


def ckey(c):
    return (ORDER.index(c), 0, "") if c in ORDER else (len(ORDER), stepnames.index(c) if c in stepnames else 0, c)

rows, bad, unresolved = [], 0, []
ids = collections.defaultdict(list)
for path in sorted(glob.glob(os.path.join(root, "tests/mech/sabotages/S*.sh"))):
    rfile = os.path.basename(path)[:-3]
    rid = rfile.split("_")[0]
    ids[rid].append(rfile)
    for f, before, want, site in shvars(path):
        if not f or not before:
            continue
        if not os.path.exists(os.path.join(root, f)):
            rows.append((rfile, rid, site, f, "?", "missing", 0, f"missing/{want}", "STALE", "", "", "", "", ""))
            bad += 1
            continue
        txt = text(f)
        occ = occurrences(txt, before)
        n = len(occ)
        if n != want:
            bad += 1
        if not occ:
            rows.append((rfile, rid, site, f, "?", "absent", 0, f"0/{want}", "STALE", "", "", "", "", ""))
            continue
        line = lineno(f, occ[0][0])
        own, res = resolve(f, line)
        if own is None:
            unresolved.append((rfile, site, f, line))
            own = "?"
        fam = own in family or (res == "datarow" and named_by_site(own.split(":")[-1]))
        hits = []
        if own in edit["def"]:
            hits.append((edit["def"][own][0], "def " + own))
        for a, b in occ:
            for s, e, c, why in edit_spans(f):
                if s < b and a < e:
                    hits.append((c, why))
        reads = sorted(set(re.findall(r'\b[A-Za-z_]\w*\b', before)) & (family | SEED_FIELDS))
        commits = sorted({c for c, _ in hits}, key=ckey)
        why = "; ".join(sorted({w for _, w in hits}))[:120]
        rerun = ""
        via = {}                       # step -> why it re-runs the row
        if fam and commits:
            cls = "RE-AIM"
        elif fam:
            cls = "RE-RUN"
            for c in touched(f, own):
                via[c] = "edit-set"
            if _a.edit_names:
                for c in named_in_edits(own):
                    via.setdefault(c, "edit-names")
                for c in calls_rewritten(f, own):
                    via.setdefault(c, "calls-rewritten")
        elif commits:
            cls, why = "RE-AIM", "outside-family " + why
        else:
            cls = "OTHER"
        # [admin1008b] the steps' ACTUAL diffs: a hunk in the owner, or the
        # owner reached through what the changed text names. A step that
        # RE-AIMs the row is not also a re-run of it.
        for nm, t_, r_ in steps:
            if nm in commits or own not in defrange:
                continue
            if own in t_:
                via[nm] = "hunk" if via.get(nm) in (None, "edit-set") else via[nm]
            elif own in r_:
                via.setdefault(nm, f"reach({r_[own]})")
        if via:
            rerun = "+".join(sorted(via, key=ckey))
        elif cls == "RE-RUN":
            rerun = _a.final
        rvia = ";".join(f"{c}:{via[c]}" for c in sorted(via, key=ckey))
        rows.append((rfile, rid, site, f, own, res, line, f"{n}/{want}", cls,
                     "+".join(commits), rerun, why, ",".join(reads), rvia))
for r in rows:
    print("\t".join(map(str, r)))
byfile = collections.defaultdict(set)
for r in rows:
    byfile[r[0]].add(r[8])
fam_rows = {f for f, c in byfile.items() if c & {"RE-AIM", "RE-RUN"}}
reaim = {f for f, c in byfile.items() if "RE-AIM" in c}
other_reads = {r[0] for r in rows if r[8] == "OTHER" and r[12]}
res_count = collections.Counter(r[5] for r in rows)
per_commit = collections.Counter()
for r in rows:
    if r[8] == "RE-AIM":
        for c in r[9].split("+"):
            per_commit[(c, r[0])] += 1
pc = collections.Counter(c for c, _ in per_commit)
rr = collections.Counter()
for r in rows:
    if r[8] == "RE-RUN":
        for c in r[10].split("+"):
            rr[c] += 1
# [admin1008b] per-step derived re-run rows (any class), by reason
step_rows = {nm: collections.defaultdict(set) for nm in stepnames}
for r in rows:
    for item in filter(None, r[13].split(";")):
        c, _, why = item.partition(":")
        if c in step_rows:
            step_rows[c][why.split("(")[0]].add(r[0])
dups = {i: fs for i, fs in ids.items() if len(fs) > 1}
unres_src = [u for u in unresolved if u[2].startswith("src/")]
print(f"SITES {len(rows)} ROW_FILES {len(byfile)} DISTINCT_IDS {len(ids)} "
      f"DUP_IDS {len(dups)} ({' '.join(f'{i}={len(fs)}' for i, fs in sorted(dups.items()))}) "
      f"FAMILY_ROWS {len(fam_rows)} RE_AIM_ROWS {len(reaim)} "
      f"RE_RUN_ROWS {len(fam_rows - reaim)} COUNT_MISMATCH {bad} "
      f"UNRESOLVED_SRC {len(unres_src)} UNRESOLVED_OTHER {len(unresolved) - len(unres_src)} "
      f"OTHER_ROWS_NAMING_FAMILY {len(other_reads)}", file=sys.stderr)
print("RESOLUTION " + " ".join(f"{k} {v}" for k, v in sorted(res_count.items())), file=sys.stderr)
print("RE_AIM_BY_COMMIT " + " ".join(f"{c} {pc[c]}" for c in ORDER if pc[c]), file=sys.stderr)
for nm in stepnames:
    allrows = set().union(*step_rows[nm].values()) if step_rows[nm] else set()
    print(f"STEP {nm}: {len(allrows)} rows re-run ("
          + ", ".join(f"{k} {len(v)}" for k, v in sorted(step_rows[nm].items())) + ")",
          file=sys.stderr)
for cmp_ in _a.compare:
    nm, _, lst = cmp_.partition("=")
    want = {("S" + x.strip().lstrip("S")) for x in lst.split(",") if x.strip()}
    got = {r[1] for r in rows if nm in [i.split(":")[0] for i in r[13].split(";") if i]}
    reaimed = {r[1] for r in rows if nm in r[9].split("+")}
    print(f"COMPARE {nm}: derived {len(got)} judged {len(want)} both {len(got & want)} "
          f"judged-not-derived {sorted(want - got)} derived-not-judged {len(got - want)}"
          f" (of the judged-not-derived, re-aimed at {nm}: {sorted((want - got) & reaimed)})",
          file=sys.stderr)
print("RE_RUN_SITES_BY_COMMIT " + " ".join(f"{c} {v}" for c, v in
      sorted(rr.items(), key=lambda kv: ORDER.index(kv[0]) if kv[0] in ORDER else 99)),
      file=sys.stderr)
for u in unres_src:
    print("UNRESOLVED", *u, file=sys.stderr)
sys.exit(2 if unres_src else 0)
