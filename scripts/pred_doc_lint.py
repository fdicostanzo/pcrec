#!/usr/bin/env python3
"""pred_doc_lint.py -- structure lint (L1-L11) and reader for the predicate documents.

The format is docs/dev/pred/doc_format.md (the spec; this file implements it).

    pred_doc_lint.py [--root DIR] [--require-all]    lint every existing pair
    pred_doc_lint.py --write-ratchet                 lower docs/dev/pred/doc_ratchet.tsv
    pred_doc_lint.py --selftest                      planted-fault selftest
    pred_doc_lint.py --show KEY [-l 0|1|2]           reader: KEY = tag or details slug
    pred_doc_lint.py --list [STATUS]                 level 0 of every piece

Output lines are `RULE file:line: message`, then per-rule counts of things
checked, then `pred_doc_lint: checks passed P, failed F`. Exit 0 clean, 1 failures
(selftest: 1 on any miss). Reader exit: 0 found, 1 none, 2 ambiguous.
Standard library only; run with `python3 -I`.

Readings the spec leaves open (the stricter was taken; see the lane report):
  - the "listed shared" of L9 is a line `shared: <slug> ...` in any details file;
  - L8 applies to every piece whose status is not `?`; L4 requires a date on
    every heading and `parked` only in the parked file;
  - a non-`?` piece without a statement line fails under L7;
  - a record title matches a `### ` heading or a `**...**` opener exactly, or
    that entry's text before its first ` (`; every `rulings:` item must carry a
    record title and it must exist (not only a ruled piece's).
"""
import argparse
import datetime
import os
import re
import shutil
import sys
import tempfile

PAIRS = [  # (file word, base, details)
    ("core", "docs/design/predicates.md", "docs/design/predicates_details.md"),
    ("lib", "docs/design/predicates_library.md", "docs/design/predicates_library_details.md"),
    ("parked", "docs/design/predicates_parked.md", "docs/design/predicates_parked_details.md"),
]
RECORD = "docs/design/plan_row_bodies/COND-FAMILY.md"
RATCHET = "docs/dev/pred/doc_ratchet.tsv"
RANK = {"core": 0, "lib": 1, "parked": 2}
CAPS = {"core": 64 * 1024, "lib": 24 * 1024, "parked": 16 * 1024}
STATEMENT_MAX, PIECE_MAX = 200, 40
RULES = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11"]
STATUSES = ("ruled", "reading", "under-construction", "parked", "?")

SEG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
TAG_RE = re.compile(r"^(core|lib|parked)/%s/%s(?:/%s)?$" % (SEG, SEG, SEG))
SECTION_RE = re.compile(r"^(core|lib|parked)/%s$" % SEG)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PIECE_RE = re.compile(r"^### (?P<name>.+?)\s+\[(?P<tag>[^\]\s]*)\]\s+(?P<rest>\S.*?)\s*$")
SECTION_HEAD_RE = re.compile(r"^## (?P<name>.+?)\s+\[(?P<tag>[^\]\s]*)\]\s*$")
ENTRY_RE = re.compile(r"^## (?P<tag>\S+) — (?P<name>.+?)\s*$")
DATE_RE = re.compile(r"^(?P<st>.*?)\s*(?P<date>\d{4}-\d{2}-\d{2})$")
FIELD_RE = re.compile(r"^(slugs|rulings|rejected|readings|evidence|history):(.*)$")
HIST_RE = re.compile(r"\[REV|WITHDRAWN|REVERSED|SUPERSEDED|(?i:review r\d+|rev \d+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


class Rep:
    """Collects violations, warnings and per-rule 'things checked' counts."""

    def __init__(self):
        self.fails, self.warns, self.notes = [], [], []
        self.checked = dict.fromkeys(RULES, 0)

    def ok(self, rule, n=1):
        self.checked[rule] += n

    def fail(self, rule, where, msg):
        self.fails.append((rule, where, msg))

    def rules_failed(self):
        return {f[0] for f in self.fails}


# ---------------------------------------------------------------- parsing

def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def parse_base(path):
    """-> dict(sections=[(tag,line,name)], pieces=[...], bad=[(line,msg,rule)], text lines)."""
    lines = read_lines(path)
    out = {"lines": lines, "sections": [], "pieces": [], "bad": []}
    infence, cur_sec = False, None
    heads = []  # (line index, kind)
    for i, ln in enumerate(lines):
        if FENCE_RE.match(ln):
            infence = not infence
            continue
        if infence:
            continue
        if ln.startswith("### "):
            heads.append((i, "p"))
        elif ln.startswith("## "):
            heads.append((i, "s"))
    for k, (i, kind) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        ln = lines[i]
        if kind == "s":
            m = SECTION_HEAD_RE.match(ln)
            if not m:
                out["bad"].append((i + 1, "malformed section heading (want '## name   [file/section]')"))
                cur_sec = None
                continue
            cur_sec = (m.group("tag"), i + 1)
            out["sections"].append((m.group("tag"), i + 1, m.group("name")))
            continue
        body_end = end
        while body_end > i + 1 and not lines[body_end - 1].strip():
            body_end -= 1
        p = {"line": i + 1, "end": body_end, "text": lines[i:body_end], "section": cur_sec,
             "tag": None, "name": None, "status": None, "date": None, "malformed": None,
             "statement": None, "statement_line": None, "needs": [], "by": [], "was": None}
        m = PIECE_RE.match(ln)
        if not m:
            p["malformed"] = "malformed piece heading (want '### name   [tag]   status date')"
        else:
            p["name"], p["tag"] = m.group("name"), m.group("tag")
            dm = DATE_RE.match(m.group("rest"))
            if dm:
                p["status"], p["date"] = dm.group("st").strip(), dm.group("date")
            else:
                p["status"] = m.group("rest").strip()
        # statement and metadata lines
        for j in range(i + 1, body_end):
            t = lines[j]
            if not t.strip():
                continue
            if p["statement_line"] is None and not re.match(r"^(needs|by|was|modes):", t):
                p["statement"], p["statement_line"] = t.strip(), j + 1
            mm = re.match(r"^(needs|by):(.*)$", t)
            if mm:
                p[mm.group(1)] += [x for x in re.split(r"[\s,]+", mm.group(2)) if x]
            mm = re.match(r"^was:\s*(\S+)", t)
            if mm:
                p["was"] = mm.group(1)
        out["pieces"].append(p)
    return out


def parse_details(path):
    lines = read_lines(path)
    out = {"lines": lines, "entries": [], "bad": [], "shared": []}
    cur, field = None, None
    infence = False
    for i, ln in enumerate(lines):
        if FENCE_RE.match(ln):
            infence = not infence
        if not infence and ln.startswith("## "):
            m = ENTRY_RE.match(ln)
            if not m:
                out["bad"].append((i + 1, "malformed entry heading (want '## <tag> — <name>')"))
                cur = None
                continue
            cur = {"tag": m.group("tag"), "line": i + 1, "start": i, "end": len(lines), "fields": {}}
            if out["entries"]:
                out["entries"][-1]["end"] = i
            out["entries"].append(cur)
            field = None
            continue
        if cur is None:
            mm = re.match(r"^shared:(.*)$", ln)
            if mm:
                out["shared"] += [x for x in re.split(r"[\s,]+", mm.group(1)) if x]
            continue
        mm = FIELD_RE.match(ln) if not infence else None
        if mm:
            field = mm.group(1)
            cur["fields"].setdefault(field, []).append((i + 1, mm.group(2)))
        elif field and ln.strip():
            cur["fields"][field].append((i + 1, ln))
    for e in out["entries"]:
        e["text"] = out["lines"][e["start"]:e["end"]]
        while e["text"] and not e["text"][-1].strip():
            e["text"].pop()
    return out


def record_titles(path):
    titles = set()
    for ln in read_lines(path):
        full = None
        if ln.startswith("### "):
            full = ln[4:]
        else:
            m = re.match(r"^\*\*(.+?)\*\*", ln)
            if m:
                full = m.group(1)
        if full is None:
            continue
        full = " ".join(full.split()).rstrip(".")
        titles.add(full)
        titles.add(full.split(" (")[0])
    return titles


# ------------------------------------------------------------------- lint

def load(root, require_all, rep):
    pairs = {}
    for word, b, d in PAIRS:
        bp, dp = os.path.join(root, b), os.path.join(root, d)
        if not os.path.isfile(bp):
            if require_all:
                rep.fail("L11", b, "base file absent (--require-all)")
            else:
                rep.notes.append("skip %s: %s absent" % (word, b))
            continue
        pairs[word] = {"base": b, "details": d, "bp": parse_base(bp),
                       "dp": parse_details(dp) if os.path.isfile(dp) else None, "size": os.path.getsize(bp)}
    return pairs


def lint(root, require_all=False, caps=None):
    caps = caps or CAPS
    rep = Rep()
    pairs = load(root, require_all, rep)
    if not pairs and not rep.fails:
        rep.notes.append("no pair present: nothing linted")
    # L1 / L2 / L4 / L6 / L7 / L8 per base file
    index = {}   # tag -> (word, ordinal)
    seen_tags = {}
    for word, P in pairs.items():
        b, bp = P["base"], P["bp"]
        for ln, msg in bp["bad"]:
            rep.ok("L2")
            rep.fail("L2", "%s:%d" % (b, ln), msg)
        for sec, ln, _ in bp["sections"]:
            rep.ok("L2")
            if not SECTION_RE.match(sec) or sec.split("/")[0] != word:
                rep.fail("L2", "%s:%d" % (b, ln), "section tag '%s' is not '%s/<kebab>'" % (sec, word))
        seen_secs = set()
        for sec, ln, _ in bp["sections"]:
            rep.ok("L1")
            if sec in seen_secs:
                rep.fail("L1", "%s:%d" % (b, ln), "duplicate section tag %s" % sec)
            seen_secs.add(sec)
        # L6: history words, every line outside fences
        infence = False
        for i, ln in enumerate(bp["lines"]):
            if FENCE_RE.match(ln):
                infence = not infence
                continue
            if infence:
                continue
            rep.ok("L6")
            m = HIST_RE.search(ln)
            if m:
                rep.fail("L6", "%s:%d" % (b, i + 1), "history word '%s' in a base file" % m.group(0))
        for n, p in enumerate(bp["pieces"]):
            where = "%s:%d" % (b, p["line"])
            rep.ok("L2")
            if p["malformed"]:
                rep.fail("L2", where, p["malformed"])
                continue
            tag = p["tag"]
            if not TAG_RE.match(tag):
                rep.fail("L2", where, "tag '%s' breaks the grammar <file>/<section>/<piece>[/<sub>] (lower-case kebab)" % tag)
            elif p["was"] is None:
                if tag.split("/")[0] != word:
                    rep.fail("L2", where, "tag '%s' is not in file '%s' (add a 'was:' line if moved)" % (tag, word))
                elif p["section"] is None or "/".join(tag.split("/")[:2]) != p["section"][0]:
                    rep.fail("L2", where, "tag '%s' is not in its section %s (add a 'was:' line if moved)"
                             % (tag, p["section"][0] if p["section"] else "(none)"))
            rep.ok("L1")
            if tag in seen_tags:
                rep.fail("L1", where, "duplicate tag %s (first at %s)" % (tag, seen_tags[tag]))
            else:
                seen_tags[tag] = where
                index[tag] = (word, len(index))
            # L4 status
            rep.ok("L4")
            st, date = p["status"], p["date"]
            if date is None:
                rep.fail("L4", where, "no status date (want '<status> YYYY-MM-DD')")
            else:
                try:
                    datetime.date.fromisoformat(date)
                except ValueError:
                    rep.fail("L4", where, "bad status date %s" % date)
                sw = st
                if st.startswith("open"):
                    sl = st[4:].strip()
                    if not st.startswith("open ") or not SLUG_RE.match(sl):
                        rep.fail("L4", where, "status 'open' needs one question slug (got '%s')" % st)
                elif st not in STATUSES:
                    rep.fail("L4", where, "status '%s' not in ruled|reading|open <slug>|under-construction|parked|?" % st)
                elif st == "parked" and word != "parked":
                    rep.fail("L4", where, "status 'parked' only in the parked file")
            is_q = st == "?"
            # L7 statement / piece caps
            rep.ok("L7")
            nlines = p["end"] - p["line"] + 1
            if nlines > PIECE_MAX:
                rep.fail("L7", where, "piece is %d lines (hard cap %d)" % (nlines, PIECE_MAX))
            if p["statement"] is None:
                if not is_q:
                    rep.fail("L7", where, "no statement line (only a '?' piece may lack one)")
            elif len(p["statement"]) > STATEMENT_MAX:
                rep.fail("L7", "%s:%d" % (b, p["statement_line"]), "statement is %d characters (hard cap %d)"
                         % (len(p["statement"]), STATEMENT_MAX))
            # L8 example line
            if not is_q:
                rep.ok("L8")
                body = p["text"][1:]
                if not any(t.startswith("modes: n/a") or all(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))
                           for t in body):
                    rep.fail("L8", where, "no example line naming WHOLE, SEARCHED and FIND-ALL (or 'modes: n/a (<why>)')")
        qn = sum(1 for p in bp["pieces"] if p["status"] == "?")
        P["qcount"] = qn
        if P["size"] > caps[word]:
            rep.warns.append("L7 %s: base file is %d bytes, over its soft cap %d" % (b, P["size"], caps[word]))
        # L11
        rep.ok("L11")
        if not bp["pieces"]:
            rep.fail("L11", b, "no pieces (a base file with none is vacuous)")
        if P["dp"] is not None and not P["dp"]["entries"]:
            rep.fail("L11", P["details"], "no entries (a details file with none is vacuous)")
    # L3 bijection and details-side checks
    titles = None
    rec = os.path.join(root, RECORD)
    for word, P in pairs.items():
        d, dp, bp = P["details"], P["dp"], P["bp"]
        rep.ok("L3")
        if dp is None:
            rep.fail("L3", d, "details file absent for existing base %s" % P["base"])
            continue
        for ln, msg in dp["bad"]:
            rep.fail("L3", "%s:%d" % (d, ln), msg)
        bt = [p["tag"] for p in bp["pieces"]]
        dt = [e["tag"] for e in dp["entries"]]
        if bt != dt:
            sb, sd = set(bt), set(dt)
            for t in bt:
                if t not in sd:
                    rep.fail("L3", d, "no details entry for base piece %s" % t)
            for e in dp["entries"]:
                if e["tag"] not in sb:
                    rep.fail("L3", "%s:%d" % (d, e["line"]), "details entry %s has no base piece" % e["tag"])
            if sb == sd and bt != dt and len(bt) == len(dt):
                rep.fail("L3", d, "details entries are not in the base file's order")
        # L4 rulings
        by_tag = {e["tag"]: e for e in dp["entries"]}
        for p in bp["pieces"]:
            e = by_tag.get(p["tag"])
            if p["status"] != "ruled" or e is None:
                continue
            items = [(ln, t) for ln, t in e["fields"].get("rulings", []) if t.strip().startswith("-")]
            rep.ok("L4")
            if not items:
                rep.fail("L4", "%s:%d" % (d, e["line"]), "ruled piece %s has no 'rulings:' item" % p["tag"])
        for e in dp["entries"]:
            for ln, t in e["fields"].get("rulings", []):
                if not t.strip().startswith("-"):
                    continue
                rep.ok("L4")
                m = re.search(r'\(record:\s*"([^"]+)"\)', t)
                if not m:
                    rep.fail("L4", "%s:%d" % (d, ln), 'rulings item without (record: "<entry title>")')
                    continue
                if titles is None:
                    titles = record_titles(rec) if os.path.isfile(rec) else False
                if titles is False:
                    rep.fail("L4", d, "record %s absent: cannot check titles" % RECORD)
                    break
                if " ".join(m.group(1).split()) not in titles:
                    rep.fail("L4", "%s:%d" % (d, ln), 'record title "%s" not found in %s' % (m.group(1), RECORD))
    # L5 references
    for word, P in pairs.items():
        for p in P["bp"]["pieces"]:
            if p["malformed"]:
                continue
            where = "%s:%d" % (P["base"], p["line"])
            for kind in ("needs", "by"):
                for t in p[kind]:
                    rep.ok("L5")
                    if t not in index:
                        tw = t.split("/")[0]
                        if tw in RANK and tw not in pairs and not require_all:
                            continue  # its pair was skipped: unresolvable, not a fault
                        rep.fail("L5", where, "%s: %s names no piece" % (kind, t))
                        continue
                    if kind == "by" and not t.startswith("core/principles/"):
                        rep.fail("L5", where, "by: %s is not under core/principles/" % t)
                    if kind == "needs":
                        tw, tn = index[t]
                        own = index.get(p["tag"])
                        if RANK[tw] > RANK[word]:
                            rep.fail("L5", where, "needs: %s is in a later file (read order core, lib, parked)" % t)
                        elif tw == word and own and tn >= own[1]:
                            rep.fail("L5", where, "needs: %s is not earlier in the file" % t)
    # L9 slugs
    shared = set()
    for P in pairs.values():
        if P["dp"]:
            shared.update(P["dp"]["shared"])
    owners = {}
    for P in pairs.values():
        if not P["dp"]:
            continue
        for e in P["dp"]["entries"]:
            for ln, t in e["fields"].get("slugs", []):
                for s in re.split(r"[\s,]+", t.strip().lstrip("-").strip()):
                    if not s or s in ("none", "-"):
                        continue
                    rep.ok("L9")
                    if not SLUG_RE.match(s):
                        rep.fail("L9", "%s:%d" % (P["details"], ln), "slug '%s' is not lower-case kebab" % s)
                    owners.setdefault(s, []).append((e["tag"], "%s:%d" % (P["details"], ln)))
    for s, os_ in sorted(owners.items()):
        tags = {t for t, _ in os_}
        if len(tags) > 1 and s not in shared:
            rep.fail("L9", os_[1][1], "slug '%s' is on %d tags (%s) and not listed 'shared:'"
                     % (s, len(tags), ", ".join(sorted(tags))))
    # L10 ratchet
    rp = os.path.join(root, RATCHET)
    if not os.path.isfile(rp):
        rep.notes.append("L10: %s absent: ratchet not checked" % RATCHET)
    else:
        rat = read_ratchet(rp)
        for word, P in pairs.items():
            if word in rat:
                rep.ok("L10")
                if P["qcount"] > rat[word]:
                    rep.fail("L10", P["base"], "%d '?' pieces, ratchet allows %d (it only shrinks)" % (P["qcount"], rat[word]))
    return rep, pairs


def read_ratchet(path):
    out = {}
    for ln in read_lines(path):
        f = ln.split("\t")
        if len(f) == 2 and f[1].strip().isdigit():
            out[f[0]] = int(f[1])
    return out


def write_ratchet(root):
    rep, pairs = lint(root)
    rp = os.path.join(root, RATCHET)
    old = read_ratchet(rp) if os.path.isfile(rp) else {}
    new = dict(old)
    for word, P in pairs.items():
        new[word] = min(old.get(word, P["qcount"]), P["qcount"])
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    with open(rp, "w", encoding="utf-8") as f:
        for w in RANK:
            if w in new:
                f.write("%s\t%d\n" % (w, new[w]))
    print("pred_doc_lint: wrote %s: %s" % (RATCHET, ", ".join("%s=%d" % (w, new[w]) for w in RANK if w in new)))
    return 0


def report(rep, out=print):
    for rule, where, msg in rep.fails:
        out("%s %s: %s" % (rule, where, msg))
    for w in rep.warns:
        out("WARN " + w)
    for n in rep.notes:
        out("note: " + n)
    out("checked: " + " ".join("%s=%d" % (r, rep.checked[r]) for r in RULES))
    passed = sum(rep.checked.values()) - len(rep.fails)
    out("pred_doc_lint: checks passed %d, failed %d" % (max(passed, 0), len(rep.fails)))


# ----------------------------------------------------------------- reader

def all_pieces(root):
    items = []  # (word, piece, base parse, entry or None)
    shared = set()
    for word, b, d in PAIRS:
        bp_, dp_ = os.path.join(root, b), os.path.join(root, d)
        if not os.path.isfile(bp_):
            continue
        bp = parse_base(bp_)
        dp = parse_details(dp_) if os.path.isfile(dp_) else {"entries": [], "shared": []}
        shared.update(dp["shared"])
        by_tag = {e["tag"]: e for e in dp["entries"]}
        for p in bp["pieces"]:
            if p["tag"]:
                items.append((word, p, bp, by_tag.get(p["tag"])))
    return items, shared


def piece_text(p, level, e):
    if level == 0:
        return [p["text"][0]] + ([p["statement"]] if p["statement"] else [])
    lines = list(p["text"])
    if level >= 2:
        lines += [""] + (e["text"] if e else ["(no details entry)"])
    return lines


def entry_slugs(e):
    out = set()
    if e:
        for _, t in e["fields"].get("slugs", []):
            out.update(s for s in re.split(r"[\s,]+", t.strip().lstrip("-").strip()) if s)
    return out


def show(root, key, level):
    items, shared = all_pieces(root)
    hit = [it for it in items if it[1]["tag"] == key]
    if not hit:
        hit = [it for it in items if key in entry_slugs(it[3])]
    if not hit:
        return 1, ["none: %s" % key]
    out = []
    for i, (_, p, _, e) in enumerate(hit):
        if i:
            out.append("")
        out += piece_text(p, level, e)
    return (2 if len(hit) > 1 and key not in shared and not any(it[1]["tag"] == key for it in hit) else 0), out


def list_pieces(root, status):
    items, _ = all_pieces(root)
    out = []
    for _, p, _, _ in items:
        if status and (p["status"] or "").split(" ")[0] != status:
            continue
        out += piece_text(p, 0, None)
    return (0 if out else 1), out


# --------------------------------------------------------------- selftest

def scratch_dir():
    base = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % (os.environ.get("USER") or os.getlogin())
    d = os.path.join(base, "scratch", "predlint")
    os.makedirs(d, exist_ok=True)
    return d


def sub(root, path, old, new, count=1):
    p = os.path.join(root, path)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    if t.count(old) != count:
        raise SystemExit("selftest: plant text %r occurs %d times in %s (want %d)" % (old, t.count(old), path, count))
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace(old, new))


CB, CD = PAIRS[0][1], PAIRS[0][2]
LB, LD = PAIRS[1][1], PAIRS[1][2]
XB, XD = PAIRS[2][1], PAIRS[2][2]


def p_dup_tag(r):
    sub(r, CB, "[core/holes/name]", "[core/holes/class]")
    sub(r, CD, "## core/holes/name —", "## core/holes/class —")


def p_bad_grammar(r):
    sub(r, CB, "[core/holes/name]", "[core/holes/Name]")
    sub(r, CD, "## core/holes/name —", "## core/holes/Name —")


def p_bad_path(r):
    sub(r, CB, "[core/holes/name]", "[core/principles/name]")
    sub(r, CD, "## core/holes/name —", "## core/principles/name —")


def p_drop_entry(r):
    sub(r, LD, "\n## lib/names/word — Word\nslugs:\n", "")


def p_swap_order(r):  # same two entries, details order reversed
    p = os.path.join(r, XD)
    t = open(p, encoding="utf-8").read()
    a = t.index("## parked/ideas/skip")
    b = t.index("## parked/ideas/swap")
    open(p, "w", encoding="utf-8").write(t[:a] + t[b:] + "\n" + t[a:b].rstrip("\n") + "\n")


def p_bad_status(r):
    sub(r, CB, "reading 2026-11-02", "blessed 2026-11-02")


def p_open_noslug(r):
    sub(r, LB, "open lib-trim-q 2026-11-04", "open 2026-11-04")


def p_ruled_no_rulings(r):
    sub(r, CD, '- 2026-11-01 "regex by default" (record: "2026-11-01 first words")', "")


def p_record_missing(r):
    sub(r, LD, '(record: "2026-11-02 bold words")', '(record: "2026-11-09 no such entry")')


def p_needs_missing(r):
    sub(r, CB, "needs: core/principles/regex-default", "needs: core/holes/nowhere")


def p_needs_later_in_file(r):
    sub(r, CB, "[core/principles/regex-default]   ruled 2026-11-01\nA bare slash form is a regex unless the owner says otherwise.\n",
        "[core/principles/regex-default]   ruled 2026-11-01\nA bare slash form is a regex unless the owner says otherwise.\nneeds: core/holes/class\n")


def p_needs_later_file(r):
    sub(r, CB, "needs: core/principles/regex-default", "needs: lib/names/padded")


def p_by_not_principle(r):
    sub(r, CB, "by: core/principles/regex-default", "by: core/holes/class")


def p_history_word(r):
    sub(r, CB, "Definition sentence.", "Definition sentence, WITHDRAWN once.")


def p_history_rev(r):
    sub(r, CB, "Definition sentence.", "Changed in Rev 29.")


def p_long_statement(r):
    sub(r, CB, "A hole stands for one pattern fragment of the named class.", "S" * 201)


def p_long_piece(r):
    sub(r, CB, "Definition sentence.", "\n".join("Definition line %d." % i for i in range(40)))


def p_no_example(r):
    sub(r, CB, "modes: n/a (a hole is not matched on its own)", "Example: WHOLE only.")


def p_slug_dup(r):
    sub(r, CD, "shared: shared-q\n", "")


def p_ratchet(r):
    sub(r, RATCHET, "core\t1", "core\t0")


def p_empty_file(r):
    open(os.path.join(r, XB), "w").write("# Parked (sample)\n\n## Ideas   [parked/ideas]\n")
    open(os.path.join(r, XD), "w").write("# Parked details (sample)\n")


# (rule, label, mutator, fail-rule expected)
PLANTS = [
    ("L1", "duplicate tag", p_dup_tag),
    ("L2", "tag grammar (upper case)", p_bad_grammar),
    ("L2", "tag path differs from its section", p_bad_path),
    ("L3", "base piece with no details entry", p_drop_entry),
    ("L3", "details entries out of order", p_swap_order),
    ("L4", "status outside the set", p_bad_status),
    ("L4", "open without a slug", p_open_noslug),
    ("L4", "ruled piece with no rulings line", p_ruled_no_rulings),
    ("L4", "record title absent from the record", p_record_missing),
    ("L5", "needs: names no piece", p_needs_missing),
    ("L5", "needs: target later in the file", p_needs_later_in_file),
    ("L5", "needs: target in a later file", p_needs_later_file),
    ("L5", "by: target not a principle", p_by_not_principle),
    ("L6", "WITHDRAWN in a base file", p_history_word),
    ("L6", "'Rev 29' in a base file", p_history_rev),
    ("L7", "statement of 201 characters", p_long_statement),
    ("L7", "piece of 41+ lines", p_long_piece),
    ("L8", "example line names one mode", p_no_example),
    ("L9", "slug on two tags, not shared", p_slug_dup),
    ("L10", "more '?' pieces than the ratchet", p_ratchet),
    ("L11", "base file with no pieces", p_empty_file),
]


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    sample = os.path.join(here, "tests", "pred_doc", "root")
    if not os.path.isdir(sample):
        print("selftest: sample %s missing" % sample)
        return 1
    scratch = tempfile.mkdtemp(prefix="st", dir=scratch_dir())
    bad = []
    n = 0

    def fresh(name):
        d = os.path.join(scratch, name)
        shutil.copytree(sample, d)
        return d

    def expect(cond, msg):
        if not cond:
            bad.append(msg)
            print("selftest: FAIL %s" % msg)

    try:
        # clean fixture: no failures, every rule ran, hand-written count floors
        c = fresh("clean")
        rep, _ = lint(c)
        expect(not rep.fails, "clean sample fails: %r" % rep.fails)
        floors = {"L1": 9, "L2": 12, "L3": 3, "L4": 9, "L5": 4, "L6": 30, "L7": 9, "L8": 6, "L9": 4, "L10": 3, "L11": 3}
        for r, f in floors.items():
            expect(rep.checked[r] >= f, "clean sample: rule %s checked %d, floor %d (a rule that checks nothing)" % (r, rep.checked[r], f))
        n += 1
        # plants: each detected by exactly its rule
        covered = set()
        for rule, label, mut in PLANTS:
            d = fresh("p%d" % n)
            mut(d)
            rep, _ = lint(d)
            got = rep.rules_failed()
            n += 1
            if got == {rule}:
                covered.add(rule)
                print("selftest: plant %-3s %-40s detected" % (rule, label))
            else:
                expect(False, "plant %s (%s): failed rules %s" % (rule, label, sorted(got)))
        for r in RULES:
            expect(r in covered, "rule %s has no detected plant" % r)
        # positive controls
        d = fresh("was")
        p_bad_path(d)
        sub(d, CB, "[core/principles/name]   ?  2026-11-03", "[core/principles/name]   ?  2026-11-03\nwas: core/holes/name")
        rep, _ = lint(d)
        expect(not rep.fails, "was: line did not excuse L2's path check: %r" % rep.fails)
        d = fresh("fence")
        sub(d, CB, "Definition sentence.", "```\nWITHDRAWN rev 3 [REV\n```\nDefinition sentence.")
        rep, _ = lint(d)
        expect(not rep.fails, "a fenced history word was not exempt: %r" % rep.fails)
        d = fresh("skip")
        os.remove(os.path.join(d, XB))
        os.remove(os.path.join(d, XD))
        rep, _ = lint(d)
        expect(not rep.fails and any("skip parked" in x for x in rep.notes), "an absent pair was not skipped")
        rep, _ = lint(d, require_all=True)
        expect(rep.rules_failed() == {"L11"}, "--require-all on an absent pair: %s" % sorted(rep.rules_failed()))
        d = fresh("noratchet")
        os.remove(os.path.join(d, RATCHET))
        rep, _ = lint(d)
        expect(not rep.fails and any(x.startswith("L10") for x in rep.notes), "an absent ratchet file was not a one-line note")
        d = fresh("soft")
        rep, _ = lint(d, caps={"core": 10, "lib": 1 << 20, "parked": 1 << 20})
        expect(not rep.fails and any(w.startswith("L7") for w in rep.warns), "soft cap: want a warning and no failure")
        # ratchet write only lowers
        d = fresh("wr")
        sub(d, RATCHET, "core\t1", "core\t5")
        write_ratchet(d)
        expect(read_ratchet(os.path.join(d, RATCHET)).get("core") == 1, "--write-ratchet did not lower 5 to 1")
        sub(d, RATCHET, "core\t1", "core\t0")
        write_ratchet(d)
        expect(read_ratchet(os.path.join(d, RATCHET)).get("core") == 0, "--write-ratchet raised 0")
        # reader, hand-written expectations
        c = fresh("rd")
        rc, out = show(c, "core/holes/class", 0)
        expect(rc == 0 and out == ["### Class   [core/holes/class]   reading 2026-11-02",
                                   "A hole stands for one pattern fragment of the named class."], "show level 0: %r" % out)
        rc, out = show(c, "core/holes/class", 1)
        expect(rc == 0 and len(out) == 6 and out[-1].startswith("modes: n/a"), "show level 1: rc %d, %d lines" % (rc, len(out)))
        rc, out = show(c, "hole-class", 2)
        expect(rc == 0 and any(x.startswith("## core/holes/class") for x in out) and any(x.startswith("slugs:") for x in out),
               "show by slug at level 2: %r" % out)
        rc, out = show(c, "no-such-thing", 0)
        expect(rc == 1, "show of nothing: rc %d" % rc)
        rc, out = show(c, "shared-q", 0)
        expect(rc == 0 and len([x for x in out if x.startswith("### ")]) == 2, "show of a shared slug: rc %d" % rc)
        rc, out = list_pieces(c, "ruled")
        expect(rc == 0 and len([x for x in out if x.startswith("### ")]) == 2, "list ruled: rc %d %r" % (rc, out))
        rc, out = list_pieces(c, "open")
        expect(rc == 0 and len(out) == 2 and "lib/names/trimmed" in out[0], "list open: %r" % out)
        d = fresh("amb")
        p_slug_dup(d)
        rc, out = show(d, "shared-q", 0)
        expect(rc == 2 and len([x for x in out if x.startswith("### ")]) == 2, "ambiguous slug: rc %d" % rc)
        # the committed sample, linted in place, through the CLI path
        rep, _ = lint(sample)
        expect(not rep.fails, "committed sample is not clean: %r" % rep.fails)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("selftest: %d runs, %d rules with a detected plant of %d, %d failures" % (n, len(covered), len(RULES), len(bad)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    ap.add_argument("--require-all", action="store_true")
    ap.add_argument("--write-ratchet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--show", metavar="KEY")
    ap.add_argument("-l", type=int, choices=(0, 1, 2), default=1)
    ap.add_argument("--list", nargs="?", const="", metavar="STATUS")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.show is not None:
        rc, out = show(a.root, a.show, a.l)
        print("\n".join(out))
        return rc
    if a.list is not None:
        rc, out = list_pieces(a.root, a.list)
        print("\n".join(out))
        return rc
    if a.write_ratchet:
        return write_ratchet(a.root)
    rep, _ = lint(a.root, a.require_all)
    report(rep)
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
