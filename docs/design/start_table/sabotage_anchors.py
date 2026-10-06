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
  5. `filescope` a file-scope preprocessor line (#include, #if, ...);
  6. `outside`  a file outside src/ (tests/, cli/, scripts/): the call graph
                is src/-only, so no such site is a start decision BY THE
                GRAPH'S DEFINITION (named, counted, never silently family);
  7. otherwise UNRESOLVED -- a hard error (exit 2) for a src/ file.

Also reports each site's occurrence count against SAB_COUNT (the rule
scripts/m6read_check_sab_anchors.py enforces in make test-codegen
[SABANCHOR], the per-commit gate), and every sabotage id shared by two row
FILES (rows are keyed by file, so a shared id is not merged away).

Usage: sabotage_anchors.py ROOT CALL_GRAPH_TSV EDIT_SET_TSV
Read-only; prints TSV (rowfile, id, site, file, owner, resolution, line,
count/want, class, commits, rerun_at, reason, reads) and a summary on stderr.
"""
import collections, glob, os, re, subprocess, sys

root, cgp, esp = sys.argv[1], sys.argv[2], sys.argv[3]
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
    if s.startswith("#"):
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


ORDER = ["C0", "C1", "C2", "C3", "C4", "C5", "C5b", "C6", "C7"]
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
            rows.append((rfile, rid, site, f, "?", "missing", 0, f"missing/{want}", "STALE", "", "", "", ""))
            bad += 1
            continue
        txt = text(f)
        occ = occurrences(txt, before)
        n = len(occ)
        if n != want:
            bad += 1
        if not occ:
            rows.append((rfile, rid, site, f, "?", "absent", 0, f"0/{want}", "STALE", "", "", "", ""))
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
        commits = sorted({c for c, _ in hits}, key=ORDER.index)
        why = "; ".join(sorted({w for _, w in hits}))[:120]
        rerun = ""
        if fam and commits:
            cls = "RE-AIM"
        elif fam:
            cls = "RE-RUN"
            t = sorted(touched(f, own), key=ORDER.index)
            rerun = "+".join(t) if t else "after-C5b"
        elif commits:
            cls, why = "RE-AIM", "outside-family " + why
        else:
            cls = "OTHER"
        rows.append((rfile, rid, site, f, own, res, line, f"{n}/{want}", cls,
                     "+".join(commits), rerun, why, ",".join(reads)))
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
print("RE_RUN_SITES_BY_COMMIT " + " ".join(f"{c} {v}" for c, v in
      sorted(rr.items(), key=lambda kv: ORDER.index(kv[0]) if kv[0] in ORDER else 99)),
      file=sys.stderr)
for u in unres_src:
    print("UNRESOLVED", *u, file=sys.stderr)
sys.exit(2 if unres_src else 0)
