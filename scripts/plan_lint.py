#!/usr/bin/env python3
"""scripts/plan_lint.py -- the plan.md linter ([PLAN-LINT] step 3).

Run through scripts/plan_lint.sh. Every rule here FAILS (exit 1) or is not in
this file: there is no warning severity and no baseline. The informational
checks (stale `started` rows, unresolved [ID] references, MERGED-but-open
rows) are the separate `--stale` report mode, run by hand, which always exits
0. docs/dev/plan.md's Policy section is the format's definition; the rule
table is in tests/plan_lint/CLAUDE.md.

    plan_lint.py [--root DIR]            lint the working-tree files
    plan_lint.py --staged                lint the INDEX content (git show :path),
                                         what a commit would record; skips the
                                         tree-wide PL14 scan (kept in make test)
    plan_lint.py --selftest              plant one violation per rule; every
                                         plant MUST be reported
    plan_lint.py --stale [--today D]     informational report, exit 0
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

PLAN = "docs/dev/plan.md"
COMPLETED = "docs/dev/plan_completed.md"
BODIES = "docs/design/plan_row_bodies"

# K35: a linter that parsed nothing is green. 150 rows, against 162 at adoption.
ROW_FLOOR = 150
STATES = ("not-started", "started", "blocked", "deferred")
SECTIONS = ["Policy", "Active", "Candidates ([OPTLOOP])", "Backlog", "Boonies", "Deferred"]
TOP_STATES = {  # the state a TOP-LEVEL row of each section must carry
    "Active": ("started", "blocked"),
    "Candidates ([OPTLOOP])": ("not-started",),
    "Backlog": ("not-started",),
    "Boonies": ("not-started",),
    "Deferred": ("deferred",),
}
STATUS_MAX = 300
NEXT_MAX = 300
TITLE_MAX = 100
LINE_MAX = 1000
CHARTER_MAX_LINES = 6
ROW_MAX_LINES = 12
ROW_MAX_CHARS = 6000

HEAD = re.compile(r"^( *)- \[([^\]\n]+)\] (.*)$")
HEAD_OK = re.compile(r"^( *)- \[([^\]\n]+)\] STATE:(not-started|started|blocked|deferred) — (\S.*)$")
ID_OK = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*(?:\.[A-Za-z0-9]+)*$")
MILESTONE_STEP = re.compile(r"^M[0-9]+\.[0-9]+$")
ATTR = re.compile(r"^(filed|status \((\d{4}-\d{2}-\d{2})\)|next|trigger|refs): ?(.*)$")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CITE_ERE = r"(^|[^_a-z])plan\.md:[0-9]+"  # plan_completed.md is append-only: its line numbers do not rot
CITE = re.compile(CITE_ERE)
CITE_EXEMPT = (
    "docs/dev/reviews/plan_triage_2026-10-12.md",  # quotes them as the thing it counts
    "scripts/plan_lint.py",
    "tests/plan_lint/",
    "docs/dev/lanes/planlint_report.md",
    "docs/dev/lanes/plclean_report.md",
)

RULES = {
    "PL01": "structure: title, then the six fixed sections in order, no other heading",
    "PL02": "no free text outside Policy: every line is a row head, a row's own line, or a heading",
    "PL03": "row head: - [ID] STATE:<not-started|started|blocked|deferred> — <title 1-100 chars>",
    "PL04": "finished rows leave the file: no completed/done/HOLD/stub heads",
    "PL05": "ids unique within plan.md",
    "PL06": "a live id has no completed row in plan_completed.md",
    "PL07": "id syntax; a dotted id's parent is a row in plan.md or plan_completed.md",
    "PL08": "nesting: a child is its parent's indent + 2, no jumps, first row at indent 0",
    "PL09": "head line: balanced parentheses, even backticks, no bold",
    "PL10": "attribute lines: filed, status (date), next|trigger (required unless started), refs; in order, once, valid",
    "PL11": "sizes: line <= 1000 chars; charter <= 6 lines; row <= 12 own lines and 6000 chars",
    "PL12": "no bold blob in a head or attribute line",
    "PL13": "section membership: top-level rows carry their section's state; started/blocked only in Active",
    "PL14": "no plan.md:<line> citation anywhere in the tracked tree",
    "PL15": "docs/design/plan_row_bodies: every pointer resolves, every body file is named by a row",
    "PL16": "Policy carries no hand-typed state counts",
    "PL17": "non-vacuity: the linter parsed at least the row floor",
}


class Row:
    __slots__ = ("id", "state", "indent", "line", "section", "title", "own", "attrs", "charter", "parent", "head")

    def __init__(self):
        self.attrs = {}
        self.charter = []
        self.own = []
        self.parent = None


def lint_plan(text, completed_text, body_names, cite_hits=None):
    """Return (errors, rows). errors: list of (rule, lineno, message)."""
    errs = []

    def err(rule, ln, msg):
        errs.append((rule, ln, msg))

    lines = text.split("\n")
    rows = []
    section = None
    seen_sections = []
    stack = []  # open rows by indent
    cur = None
    in_pre = True
    pre_nonblank = 0
    prev_blank = False
    policy_text = []
    body_refs = []

    for i, raw in enumerate(lines, 1):
        l = raw
        if len(l) > LINE_MAX:
            err("PL11", i, "line of %d chars (max %d)" % (len(l), LINE_MAX))
        if l.startswith("## ") or l.startswith("### ") or (l.startswith("#") and not l.startswith("# ")):
            cur = None
            stack = []
            if l.startswith("## "):
                name = l[3:].strip()
                seen_sections.append(name)
                section = name
                in_pre = False
            else:
                err("PL01", i, "heading other than the six sections: %r" % l[:60])
            prev_blank = False
            continue
        if l.strip() == "":
            prev_blank = True
            if section not in (None, "Policy"):
                cur = None  # a blank line ends a row: no continuation across it
            continue
        if in_pre:
            pre_nonblank += 1
            if pre_nonblank == 1 and not l.startswith("# "):
                err("PL01", i, "the file must open with a '# ' title")
            if pre_nonblank > 6:
                err("PL02", i, "free text before the first section (preamble is at most 6 lines)")
            continue
        if section == "Policy":
            policy_text.append((i, l))
            continue
        # ---- inside a row section
        if section not in TOP_STATES:
            continue  # PL01 already reported the unknown section
        m = HEAD.match(l)
        if m:
            prev_blank = False
            indent = len(m.group(1))
            row = Row()
            row.line = i
            row.id = m.group(2)
            row.indent = indent
            row.section = section
            row.head = l
            row.state = None
            mo = HEAD_OK.match(l)
            if not mo:
                rest = l[l.index("] ") + 2:] if "] " in l else ""
                if re.match(r"(STATE:(completed|done)\b|STATE\s|COMPLETED|ARCHIVED|archived|HOLD)", rest) or not rest.startswith("STATE:"):
                    err("PL04", i, "[%s] is a finished/stub head (%r): move the row to plan_completed.md" % (row.id, rest[:30]))
                else:
                    err("PL03", i, "[%s] head does not match '- [ID] STATE:<state> — <title>': %r" % (row.id, l[:90]))
                # still track the row for nesting/attribute checks
                row.title = ""
            else:
                row.state = mo.group(3)
                row.title = mo.group(4)
                if len(row.title) > TITLE_MAX:
                    err("PL03", i, "[%s] title is %d chars (max %d)" % (row.id, len(row.title), TITLE_MAX))
            if indent % 2:
                err("PL08", i, "[%s] odd indent %d" % (row.id, indent))
            # nesting
            while stack and stack[-1].indent >= indent:
                stack.pop()
            if stack:
                par = stack[-1]
                if indent != par.indent + 2:
                    err("PL08", i, "[%s] indent %d under [%s] at %d (a child is the parent's indent + 2)" % (row.id, indent, par.id, par.indent))
                row.parent = par
            elif indent != 0:
                err("PL08", i, "[%s] indented %d with no parent row above it" % (row.id, indent))
            stack.append(row)
            rows.append(row)
            cur = row
            continue
        # a non-head, non-blank line
        if cur is None:
            err("PL02", i, "text outside any row: %r" % l[:80])
            continue
        want = cur.indent + 2
        ind = len(l) - len(l.lstrip(" "))
        if ind != want:
            err("PL02", i, "[%s] own line at indent %d (expected %d): %r" % (cur.id, ind, want, l.strip()[:60]))
            continue
        cur.own.append((i, l.strip()))

    # sections
    if seen_sections != SECTIONS:
        err("PL01", 1, "sections are %r, expected %r" % (seen_sections, SECTIONS))

    # ---- per-row checks
    ids = {}
    done_ids = set(re.findall(r"^- \[([^\]\n]+)\] STATE:(?:completed|done)\b", completed_text, re.M))
    any_ids = set(re.findall(r"^\s*- \[([^\]\n]+)\] STATE:", completed_text, re.M))
    for r in rows:
        # PL05 / PL06
        if r.id in ids:
            err("PL05", r.line, "[%s] duplicates the row at line %d" % (r.id, ids[r.id]))
        else:
            ids[r.id] = r.line
        if r.id in done_ids:
            err("PL06", r.line, "[%s] has a completed row in plan_completed.md" % r.id)
    allids = set(ids) | any_ids
    for r in rows:
        # PL07
        if not ID_OK.match(r.id):
            err("PL07", r.line, "[%s] is not a valid id" % r.id)
        elif "." in r.id and not MILESTONE_STEP.match(r.id):
            parent = r.id.rsplit(".", 1)[0]
            if parent not in allids:
                err("PL07", r.line, "[%s]: its parent id [%s] is a row in neither plan.md nor plan_completed.md" % (r.id, parent))
        # PL09 / PL12
        h = r.head
        if "**" in h:
            err("PL12", r.line, "[%s] bold in the head line" % r.id)
        stripped = re.sub(r"`[^`]*`", "", h)
        if h.count("`") % 2:
            err("PL09", r.line, "[%s] odd number of backticks in the head" % r.id)
        elif stripped.count("(") != stripped.count(")"):
            err("PL09", r.line, "[%s] unbalanced parentheses in the head" % r.id)
        # PL13
        if r.state:
            if r.state in ("started", "blocked") and r.section != "Active":
                err("PL13", r.line, "[%s] STATE:%s outside Active" % (r.id, r.state))
            if r.state == "deferred" and r.section != "Deferred":
                err("PL13", r.line, "[%s] STATE:deferred outside Deferred" % r.id)
            if r.indent == 0 and r.state not in TOP_STATES[r.section]:
                err("PL13", r.line, "[%s] top-level STATE:%s in %s (expects %s)" % (r.id, r.state, r.section, "/".join(TOP_STATES[r.section])))
        # ---- own lines: attributes then charter
        order = {"filed": 0, "status": 1, "next": 2, "trigger": 2, "refs": 3}
        last = -1
        seen = set()
        for ln, s in r.own:
            m = ATTR.match(s)
            if m and r.charter:
                err("PL10", ln, "[%s] attribute line %r after charter text" % (r.id, s[:30]))
            elif m:
                key = m.group(1).split(" ")[0]
                if key in seen:
                    err("PL10", ln, "[%s] repeats %s:" % (r.id, key))
                seen.add(key)
                if order[key] < last:
                    err("PL10", ln, "[%s] %s: out of order (filed, status, next|trigger, refs)" % (r.id, key))
                last = max(last, order[key])
                val = m.group(3)
                if "**" in s:
                    err("PL12", ln, "[%s] bold in %s:" % (r.id, key))
                if key == "filed":
                    d = val.split(" ", 1)[0]
                    if not _valid_date(d) or len(val.split(" ", 1)) < 2 or not val.split(" ", 1)[1].strip():
                        err("PL10", ln, "[%s] filed: needs '<ISO date> <who>': %r" % (r.id, val[:50]))
                elif key == "status":
                    if not _valid_date(m.group(2)):
                        err("PL10", ln, "[%s] status date %r is not a real ISO date" % (r.id, m.group(2)))
                    if not val.strip():
                        err("PL10", ln, "[%s] empty status" % r.id)
                    if len(val) > STATUS_MAX:
                        err("PL10", ln, "[%s] status is %d chars (max %d)" % (r.id, len(val), STATUS_MAX))
                    r.attrs["status_date"] = m.group(2)
                    r.attrs["status"] = val
                elif key in ("next", "trigger"):
                    if not val.strip():
                        err("PL10", ln, "[%s] empty %s:" % (r.id, key))
                    if len(val) > NEXT_MAX:
                        err("PL10", ln, "[%s] %s: is %d chars (max %d)" % (r.id, key, len(val), NEXT_MAX))
                    r.attrs["next"] = val
                elif key == "refs":
                    for p in re.findall(BODIES + r"/([A-Za-z0-9_.\-]+\.md)", val):
                        pass
                r.attrs[key] = val
            else:
                r.charter.append((ln, s))
        for need in ("filed", "status"):
            if need not in seen:
                err("PL10", r.line, "[%s] missing %s:" % (r.id, need))
        if r.state in ("not-started", "blocked", "deferred") and not ({"next", "trigger"} & seen):
            err("PL10", r.line, "[%s] STATE:%s needs next: or trigger:" % (r.id, r.state))
        if "next" in seen and "trigger" in seen:
            err("PL10", r.line, "[%s] has both next: and trigger:" % r.id)
        # PL11
        if len(r.charter) > CHARTER_MAX_LINES:
            err("PL11", r.line, "[%s] charter is %d lines (max %d): move the long form to %s/%s.md" % (r.id, len(r.charter), CHARTER_MAX_LINES, BODIES, r.id))
        nlines = 1 + len(r.own)
        nchars = len(r.head) + sum(len(s) + 2 for _, s in r.own)
        if nlines > ROW_MAX_LINES:
            err("PL11", r.line, "[%s] row is %d lines (max %d)" % (r.id, nlines, ROW_MAX_LINES))
        if nchars > ROW_MAX_CHARS:
            err("PL11", r.line, "[%s] row is %d chars (max %d)" % (r.id, nchars, ROW_MAX_CHARS))

    # PL15: pointers from plan.md / plan_completed.md rows to body files
    pat = re.compile(re.escape(BODIES) + r"/([A-Za-z0-9_.\-]+\.md)")
    named = set()
    for src, t in (("plan.md", text), ("plan_completed.md", completed_text)):
        for m in pat.finditer(t):
            fn = m.group(1)
            if fn == "CLAUDE.md":
                continue
            named.add(fn)
            if fn not in body_names:
                ln = t.count("\n", 0, m.start()) + 1
                err("PL15", ln, "%s:%d points at %s/%s, which does not exist" % (src, ln, BODIES, fn))
    for fn in sorted(body_names):
        if fn != "CLAUDE.md" and fn not in named:
            err("PL15", 1, "%s/%s is named by no row in plan.md or plan_completed.md" % (BODIES, fn))

    # PL16
    for ln, s in policy_text:
        if s.startswith("    "):
            continue  # code block
        if re.search(r"\b\d{2,}\s+(?:rows|not-started|started|blocked|deferred|STATE)\b", s):
            err("PL16", ln, "hand-typed state count in Policy: %r" % s[:80])

    # PL14
    for path, ln, s in (cite_hits or []):
        err("PL14", ln, "%s:%d cites a plan line number: %r" % (path, ln, s[:70]))

    # PL17
    if len(rows) < ROW_FLOOR:
        err("PL17", 1, "parsed %d rows, floor %d: the linter is not reading the file it thinks it is" % (len(rows), ROW_FLOOR))
    return errs, rows


def _valid_date(s):
    if not s or not ISO.match(s):
        return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------- inputs

def _git(root, *args, check=False):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, check=check)


def read_files(root, staged):
    if staged:
        def show(p):
            r = _git(root, "show", ":" + p)
            if r.returncode:
                return ""
            return r.stdout
        text = show(PLAN)
        comp = show(COMPLETED)
        ls = _git(root, "ls-files", "--cached", "--", BODIES).stdout.split("\n")
        names = {os.path.basename(p) for p in ls if p}
        return text, comp, names
    with open(os.path.join(root, PLAN), encoding="utf-8") as f:
        text = f.read()
    with open(os.path.join(root, COMPLETED), encoding="utf-8") as f:
        comp = f.read()
    d = os.path.join(root, BODIES)
    names = set(os.listdir(d)) if os.path.isdir(d) else set()
    return text, comp, names


def tree_cites(root, subdir=None, no_index=False):
    """plan.md:<digits> citations in the tracked tree. git grep when root is a
    repository (a walk when it is not: a mech scratch tree is git archive output).
    A grep that FAILS (rc >= 2: a bad pattern, no repository) raises instead of
    reading as "no hits": this rule once went green on a pattern git rejected."""
    hits = []
    base = os.path.join(root, subdir) if subdir else root
    if os.path.exists(os.path.join(root, ".git")):
        args = ["grep", "-n", "-I", "-E"] + (["--no-index"] if no_index else []) + [CITE_ERE]
        if subdir:
            args += ["--", subdir]
        r = _git(root, *args)
        if r.returncode not in (0, 1):
            raise RuntimeError("git grep failed (rc %d): %s" % (r.returncode, r.stderr.strip()[:200]))
        for ln in r.stdout.split("\n"):
            m = re.match(r"^([^:]+):(\d+):(.*)$", ln)
            if m and not any(m.group(1).startswith(e) for e in CITE_EXEMPT):
                hits.append((m.group(1), int(m.group(2)), m.group(3)))
        return hits
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ("build", "worktrees", ".git") and not d.startswith("build-")]
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if any(rel.startswith(e) for e in CITE_EXEMPT):
                continue
            try:
                with open(p, encoding="utf-8") as fh:
                    for n, s in enumerate(fh, 1):
                        if CITE.search(s):
                            hits.append((rel, n, s.rstrip()))
            except (UnicodeDecodeError, OSError):
                pass
    return hits


def report(errs, rows, label):
    for rule, ln, msg in sorted(errs, key=lambda e: (e[1], e[0])):
        print("%s: %s:%d: %s" % (rule, label, ln, msg))
    return len(errs)


# ---------------------------------------------------------------- self-test

def _first_row_lines(text, state):
    """Index range [a, b) of the first top-level row with the given state (head + own lines)."""
    ls = text.split("\n")
    for i, l in enumerate(ls):
        if re.match(r"^- \[[^\]]+\] STATE:" + state + " ", l):
            j = i + 1
            while j < len(ls) and ls[j].startswith("  ") and not HEAD.match(ls[j]):
                j += 1
            return ls, i, j
    raise RuntimeError("selftest: no %s row" % state)


def _mut(fn):
    return fn


def planted(text):
    """(rule, label, mutated_text, extra) -- each plant MUST draw its rule."""
    out = []
    ls, a, b = _first_row_lines(text, "not-started")
    row = ls[a:b]

    def with_row(newrow, at=None):
        x = list(ls)
        x[a:b] = newrow
        return "\n".join(x)

    def row_has_attr(prefix):
        return [k for k, s in enumerate(row) if s.lstrip().startswith(prefix)][0]

    # PL01
    out.append(("PL01", "extra section", text + "\n## Extras\n", {}))
    out.append(("PL01", "section order", text.replace("\n## Backlog\n", "\n## Boonies-tmp\n").replace("\n## Boonies\n", "\n## Backlog\n").replace("\n## Boonies-tmp\n", "\n## Boonies\n"), {}))
    # PL02
    out.append(("PL02", "unindented prose in a section", with_row(row + ["Stray prose that belongs nowhere."]), {}))
    out.append(("PL02", "blank-line wedge", with_row(row[:2] + [""] + row[2:]), {}))
    # PL03
    r = list(row); r[0] = r[0].replace(" — ", " - ", 1)
    out.append(("PL03", "no em dash", with_row(r), {}))
    r = list(row); r[0] = re.sub(r" — .*$", " — " + "t" * 101, r[0])
    out.append(("PL03", "title over 100", with_row(r), {}))
    r = list(row); r[0] = r[0].replace("STATE:not-started", "STATE:wip", 1)
    out.append(("PL03", "unknown state", with_row(r), {}))
    # PL04
    r = list(row); r[0] = r[0].replace("STATE:not-started", "STATE:completed", 1)
    out.append(("PL04", "completed head", with_row(r), {}))
    # PL05
    out.append(("PL05", "duplicate id", with_row(row + row), {}))
    # PL06
    rid = re.match(r"^- \[([^\]]+)\]", row[0]).group(1)
    out.append(("PL06", "id completed elsewhere", text, {"completed": "- [%s] STATE:completed — x\n" % rid}))
    # PL07
    r = list(row); r[0] = r[0].replace("[" + rid + "]", "[lower-case]", 1)
    out.append(("PL07", "bad id syntax", with_row(r), {}))
    r = list(row); r[0] = r[0].replace("[" + rid + "]", "[NOSUCH-PARENT.child]", 1)
    out.append(("PL07", "dotted id with no parent", with_row(r), {}))
    # PL08
    out.append(("PL08", "child jumps two levels", with_row(row + ["      - [SELFTEST-CHILD] STATE:not-started — x"]), {}))
    out.append(("PL08", "orphan indent", with_row(["  " + row[0]] + row[1:]), {}))
    # PL09
    r = list(row); r[0] = r[0] + " (unbalanced"
    out.append(("PL09", "unbalanced paren", with_row(r), {}))
    # PL10
    for pre, what in (("filed:", "filed"), ("status (", "status")):
        k = row_has_attr(pre)
        out.append(("PL10", "missing " + what, with_row(row[:k] + row[k + 1:]), {}))
    k = row_has_attr("status (")
    r = list(row); r[k] = re.sub(r"\(\d{4}-\d{2}-\d{2}\)", "(2026-13-45)", r[k])
    out.append(("PL10", "impossible status date", with_row(r), {}))
    r = list(row); r[k] = r[k] + "x" * 320
    out.append(("PL10", "status over 300", with_row(r), {}))
    nk = [j for j, s in enumerate(row) if s.lstrip().startswith(("next:", "trigger:"))][0]
    out.append(("PL10", "missing next|trigger", with_row(row[:nk] + row[nk + 1:]), {}))
    r = list(row); r[1], r[2] = r[2], r[1]
    out.append(("PL10", "attributes out of order", with_row(r), {}))
    out.append(("PL10", "repeated filed", with_row(row + [row[1]]), {}))
    # PL11
    out.append(("PL11", "line over 1000", with_row(row + ["  " + "x" * 1001]), {}))
    out.append(("PL11", "charter over 6 lines", with_row(row + ["  charter line %d" % n for n in range(8)]), {}))
    # PL12
    r = list(row); k = row_has_attr("status ("); r[k] = r[k] + " **bold**"
    out.append(("PL12", "bold in status", with_row(r), {}))
    # PL13
    r = list(row); r[0] = r[0].replace("STATE:not-started", "STATE:started", 1)
    # place the not-started row's section is not Active in general: a started row there is the plant
    out.append(("PL13", "started outside Active", with_row(r), {}))
    # PL14
    out.append(("PL14", "line-number citation", text, {"cites": [("docs/x.md", 3, "see plan.md:123")]}))
    # PL15
    out.append(("PL15", "dangling body pointer", with_row(row + ["  refs-free charter naming %s/NOSUCH-ROW.md" % BODIES]), {}))
    out.append(("PL15", "unnamed body file", text, {"bodies": {"ORPHAN-BODY.md"}}))
    # PL16
    out.append(("PL16", "hand-typed count", text.replace("\n## Active\n", "\nThere are 99 rows in this file.\n\n## Active\n", 1), {}))
    # PL17
    out.append(("PL17", "empty parse", "# pcrec Project Plan\n\n## Policy\n\nx\n" + "".join("\n## %s\n" % s for s in SECTIONS[1:]), {}))
    return out


def selftest(text, comp, names, root):
    errs, rows = lint_plan(text, comp, names, [])
    bad = 0
    if errs:
        print("selftest: the unmutated plan is not clean (%d errors); fix the file first" % len(errs))
        for e in errs[:5]:
            print("   %s line %d: %s" % e)
        return 1
    covered = set()
    n = 0
    for rule, label, mt, extra in planted(text):
        n += 1
        e, _ = lint_plan(mt, extra.get("completed", comp), extra.get("bodies", names) if "bodies" in extra else names, extra.get("cites"))
        hit = [x for x in e if x[0] == rule]
        if hit:
            covered.add(rule)
        else:
            bad += 1
            print("selftest: PLANT NOT DETECTED %s (%s); got %s" % (rule, label, sorted({x[0] for x in e})))
    # the tree scanner itself (PL14's plant above bypasses it): plant a file and require the hit
    d = os.path.join(root, "build", "plan_lint_selftest")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "planted.txt"), "w") as fh:
        fh.write("clean line\nsee plan.md:123 for the row\nplan_completed.md:77 is stable and not a hit\n")
    n += 1
    got = [(h[1]) for h in tree_cites(root, subdir="build/plan_lint_selftest", no_index=True)]
    if got != [2]:
        bad += 1
        print("selftest: the tree scanner returned %r on its planted file (want [2])" % got)
    try:
        os.remove(os.path.join(d, "planted.txt"))
        os.rmdir(d)
    except OSError:
        pass
    missing = sorted(set(RULES) - covered)
    for rule in missing:
        bad += 1
        print("selftest: rule %s has no detected plant" % rule)
    print("selftest: %d plants, %d rules covered of %d, %d failures" % (n, len(covered), len(RULES), bad))
    return 1 if bad else 0


# ---------------------------------------------------------------- stale report

def stale_report(text, comp, today):
    errs, rows = lint_plan(text, comp, set(), [])
    ids = {r.id for r in rows} | set(re.findall(r"^\s*- \[([^\]\n]+)\] STATE:", comp, re.M))
    print("plan_lint --stale (informational; always exit 0), today=%s, %d rows" % (today, len(rows)))
    old = []
    for r in rows:
        d = r.attrs.get("status_date")
        if r.state == "started" and d:
            age = (today - datetime.date.fromisoformat(d)).days
            if age > 30:
                old.append((age, r.id, d))
    print("\nP13  started rows whose status is older than 30 days:")
    for age, rid, d in sorted(old, reverse=True):
        print("  %4d days  [%s]  status (%s)" % (age, rid, d))
    if not old:
        print("  none")
    print("\nP14  not-started rows whose status says MERGED/BUILT/LANDED/DONE (re-read: is the row finished?):")
    n = 0
    for r in rows:
        s = r.attrs.get("status", "")
        if r.state == "not-started" and re.search(r"\b(MERGED|BUILT|LANDED|DONE)\b", s):
            print("  [%s] not-started: %s" % (r.id, s[:110]))
            n += 1
    if not n:
        print("  none")
    print("\nP15  [ID] references that resolve to no row in plan.md or plan_completed.md (K/D/S/O/I/B ids and PCRE2 option names excluded):")
    unknown = {}
    for i, l in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"\[([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*(?:\.[A-Za-z0-9]+)*)\]", l):
            t = m.group(1)
            if t in ids or re.match(r"^(?:[KDSOIBRQ]-?\d+[a-z]?|PCRE2_\w+|ID|CHILD-ID|Mx\.y|A-Z|N\d+)$", t):
                continue
            unknown.setdefault(t, i)
    for t, ln in sorted(unknown.items(), key=lambda kv: kv[1]):
        print("  [%s]  first at plan.md line %d" % (t, ln))
    if not unknown:
        print("  none")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--today", default=None)
    ap.add_argument("--rules", action="store_true")
    a = ap.parse_args()
    if a.rules:
        for k in sorted(RULES):
            print("%s  %s" % (k, RULES[k]))
        return 0
    text, comp, names = read_files(a.root, a.staged)
    if not text.strip():
        print("plan_lint: %s is empty or unreadable (root %s)" % (PLAN, a.root))
        return 1
    if a.selftest:
        return selftest(text, comp, names, a.root)
    if a.stale:
        today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
        return stale_report(text, comp, today)
    cites = [] if a.staged else tree_cites(a.root)
    errs, rows = lint_plan(text, comp, names, cites)
    n = report(errs, rows, "staged:" + PLAN if a.staged else PLAN)
    print("plan_lint: %d rows parsed, %d violations%s" % (len(rows), n, " (staged content; PL14's tree scan runs in make test)" if a.staged else ""))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
