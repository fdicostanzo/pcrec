#!/usr/bin/env python3
"""docs/design/start_table/sabotage_anchors.py -- revision 2 ([r2 sound-M6,
checks-M1]). Maps EVERY sabotage anchor site (SAB_FILE/SAB_BEFORE and
SAB_FILE2/SAB_BEFORE2, every target file, not only the two emitters) to the
definition it sits in, and classifies it -- with NO hand-written family list:

  FAMILY  the owner is a member of call_graph.py's derived start family, or
          one of its seeds (the landmark readers), or a definition the
          refactor edits (refactor_edit_set.tsv `def`).
  RE-AIM  the anchor sits in an edit-set `def`, contains an edit-set `token`,
          or contains an edit-set `line` (refactor_edit_set.tsv): the commit
          named there rewrites the anchor's text, so the row must be re-aimed
          in that commit, intent re-verified.
  RE-RUN  a FAMILY anchor the plan keeps byte-stable: the row is re-run, its
          SAB_REACH probe included ([MECH-REACH]).

The count of each is an OUTPUT of (the call graph, the edit set), never an
input. Also reports, per site, how many times the anchor occurs against
SAB_COUNT (the same exact-count rule scripts/m6read_check_sab_anchors.py
enforces in make test-codegen [SABANCHOR], which is the per-commit gate).

Usage: sabotage_anchors.py ROOT CALL_GRAPH_TSV EDIT_SET_TSV
Read-only; prints TSV (row, site, file, owner, line, count/want, class,
commit, reason) and a summary on stderr.
"""
import glob, os, re, subprocess, sys

root, cgp, esp = sys.argv[1], sys.argv[2], sys.argv[3]
defs = {}      # file -> [(start, end, name)]
family = set()
for l in open(cgp):
    p = l.rstrip("\n").split("\t")
    if p[0].startswith("def-"):
        f, rng = p[2].rsplit(":", 1)
        a, b = map(int, rng.split("-"))
        defs.setdefault(f, []).append((a, b, p[1]))
    elif p[0].startswith("family-") or p[0] == "seed":
        family.add(p[1])
edit = {"def": {}, "token": {}, "line": {}}
for l in open(esp):
    if l.startswith("#") or not l.strip():
        continue
    k, v, c, why = l.rstrip("\n").split("\t")
    edit[k][v] = (c, why)
family |= set(edit["def"])


def owner(f, line):
    best = None
    for a, b, n in defs.get(f, []):
        if a <= line <= b and (best is None or a >= best[0]):
            best = (a, n)
    return best[1] if best else "?"


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


rows, bad = [], 0
counts = {"FAMILY": 0, "RE-AIM": 0, "RE-RUN": 0, "OTHER": 0}
for path in sorted(glob.glob(os.path.join(root, "tests/mech/sabotages/S*.sh"))):
    rid = os.path.basename(path).split("_")[0]
    for f, before, want, site in shvars(path):
        if not f or not before:
            continue
        fp = os.path.join(root, f)
        if not os.path.exists(fp):
            rows.append((rid, site, f, "?", 0, f"missing/{want}", "STALE", "", "")); bad += 1
            continue
        txt = open(fp, encoding="utf-8", errors="replace").read()
        n = txt.count(before)
        idx = txt.find(before)
        line = txt[:idx].count("\n") + 1 if idx >= 0 else 0
        own = owner(f, line) if idx >= 0 else "?"
        cls, commit, why = "OTHER", "", ""
        if n != want:
            bad += 1
        if own in family:
            cls = "RE-RUN"
            hit = None
            if own in edit["def"]:
                hit = ("def " + own,) + edit["def"][own]
            for t, cw in edit["token"].items():
                if not hit and t in before:
                    hit = ("token " + t,) + cw
            for t, cw in edit["line"].items():
                if not hit and t.strip() in before:
                    hit = ("line " + t.strip()[:40],) + cw
            if hit:
                cls, why, commit = "RE-AIM", hit[0], hit[1]
        else:
            # a token/line hit outside the family is still a re-aim
            for t, cw in list(edit["token"].items()) + list(edit["line"].items()):
                if t.strip() in before:
                    cls, why, commit = "RE-AIM", "outside-family " + t.strip()[:40], cw[0]
                    break
        rows.append((rid, site, f, own, line, f"{n}/{want}", cls, commit, why))
fam_rows = {r[0] for r in rows if r[6] in ("RE-AIM", "RE-RUN")}
reaim = {r[0] for r in rows if r[6] == "RE-AIM"}
for r in rows:
    print("\t".join(map(str, r)))
print(f"SITES {len(rows)} ROWS {len({r[0] for r in rows})} FAMILY_ROWS {len(fam_rows)} "
      f"RE_AIM_ROWS {len(reaim)} RE_RUN_ROWS {len(fam_rows - reaim)} "
      f"COUNT_MISMATCH {bad}", file=sys.stderr)
