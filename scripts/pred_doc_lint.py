#!/usr/bin/env -S python3 -I
"""pred_doc_lint.py -- structure lint (L1-L12) for the predicate documents, and their one parser.

The format is docs/dev/pred/doc_format.md (the spec; this file implements it, and its section "What the lint checks
beyond the rule sentences" is the list of the checks no rule sentence names).

    pred_doc_lint.py [--root DIR] [--require-all]    lint every existing pair
    pred_doc_lint.py --write-ratchet [--root DIR]    lower docs/dev/pred/doc_ratchet.tsv (only after a clean lint)
    pred_doc_lint.py --selftest                      planted-fault selftest (takes no other option)

Output lines are `RULE file:line: message`, then `checked:` (per rule, the number of THINGS VISITED -- a line, a
piece, a tag, a slug, a ratchet row -- not of distinct checks: a disabled check keeps its count, so the count only
shows that a rule's loop ran; the plants in --selftest are what show a rule bites), then
`pred_doc_lint: checks passed P, failed F`. Exit 0 clean, 1 failures, 2 usage error (an unknown option, conflicting
options, a --root that is not a directory). Standard library only.

THE READER is `scripts/entry` (a profile; scripts/doc_profiles.py `predicates`): it calls load_pieces() and
piece_text() below, so this module is the ONE parser. This file has no reader command of its own.

Readings the spec leaves open (the stricter was taken):
  - the "listed shared" of L9 is a line `shared: <slug> ...` before the first entry of any details file;
  - the statement is the first non-blank line after a piece's heading; it must not be a metadata line;
  - a `rulings:` item is a line starting `-`; its `(record: "<title>")` must be on that line;
  - a fence is ``` or ~~~ closed only by the same mark; an unterminated fence is a failure (L2 base, L3 details).

Where the post-pilot changes (doc_format.md, its last two sub-sections) are checked, by rule:
  L1  a details `was:` tag equals no live tag and is retired under one entry only;
  L2  a tag's path equals its file and section, always; `was: <tag> (<date>, <why>)` and
      `formerly: <module.name> (<date>, <why>)` grammar (module an identifier or `?`);
  L4  status `principle` only under core/principles/; a `principle` piece, as a `ruled` one, has a rulings item;
  L5  every `see:` tag exists in ANY file (forward allowed; pilot mode's skip rule as `needs:`), never the piece itself;
  L6  a `was:` line in a BASE file (history);
  L8  `skeleton: yes` exempts a piece from L8 (the value is `yes`, never on a `?` piece); the old marker
      `modes: n/a (skeleton ...)` fails;
  L10 the ratchet has a row `<word>-skeleton` per file beside the `?` row; both only shrink;
  L12 (library fields) `module: <dotted lower-case name>|?` exactly once on every non-`?` library piece;
      `module:` and `default:` only in the library file; `default:`'s one value is `yes`.
"""
import argparse
import datetime
import getpass
import os
import re
import shutil
import sys
import tempfile

PAIRS = [  # (file word, base, details)
    ("core", "docs/design/predicates/core.md", "docs/design/predicates/core_details.md"),
    ("lib", "docs/design/predicates/library.md", "docs/design/predicates/library_details.md"),
    ("parked", "docs/design/predicates/parked.md", "docs/design/predicates/parked_details.md"),
]
RECORD = "docs/design/plan_row_bodies/COND-FAMILY.md"
RATCHET = "docs/dev/pred/doc_ratchet.tsv"
RANK = {"core": 0, "lib": 1, "parked": 2}
CAPS = {"core": 64 * 1024, "lib": 24 * 1024, "parked": 16 * 1024}
STATEMENT_MAX, PIECE_MAX = 200, 40
RULES = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12"]
STATUSES = ("ruled", "principle", "reading", "under-construction", "parked", "?")
SKEL = "-skeleton"  # the ratchet row of a file's skeleton pieces is `<word>-skeleton`

SEG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
TAG_RE = re.compile(r"^(core|lib|parked)/%s/%s(?:/%s)?$" % (SEG, SEG, SEG))
SECTION_RE = re.compile(r"^(core|lib|parked)/%s$" % SEG)
SLUG_RE = re.compile(r"^%s$" % SEG)
PIECE_RE = re.compile(r"^### (?P<name>.+?)\s+\[(?P<tag>[^\]\s]*)\]\s+(?P<rest>\S.*?)\s*$")
SECTION_HEAD_RE = re.compile(r"^## (?P<name>.+?)\s+\[(?P<tag>[^\]\s]*)\]\s*$")
ENTRY_RE = re.compile(r"^## (?P<tag>\S+) — (?P<name>.+?)\s*$")
DATE_RE = re.compile(r"^(?P<st>.*?)\s*(?P<date>\d{4}-\d{2}-\d{2})$")
FIELD_RE = re.compile(r"^(slugs|rulings|rejected|readings|evidence|history):(.*)$")
META_RE = re.compile(r"^(needs|by|see|was|modes|skeleton|module|default):")
REF_RE = re.compile(r"^(needs|by|see):(.*)$")
# details-only lines: `was: <previous tag> (<date>, <why>)`, `formerly: <module.name> (<date>, <why>)`
MOVE_RE = re.compile(r"^(was|formerly):(.*)$")
WAS_RE = re.compile(r"^\s*(?P<what>\S+)\s+\((?P<date>\d{4}-\d{2}-\d{2}),\s*(?P<why>\S.*)\)\s*$")
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
FORMERLY_NAME_RE = re.compile(r"^(?:[a-z][a-z0-9_]*|\?)(?:\.%s)+$" % IDENT)
MODULE_RE = re.compile(r"^(?:\?|[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BOLD_OPEN_RE = re.compile(r"^\*\*\d{4}-\d{2}-\d{2}\b")
ISO_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
# L6's words (doc_format.md): case-insensitive, on word boundaries; the date clause is handled apart.
HIST_RE = re.compile(r"\[REV|\b(?:withdrawn|reversed|superseded|rev \d+|revision \d+|review r\d+|r\d+)\b", re.I)


class Unreadable(Exception):
    pass


class Rep:
    """Collects violations, warnings and per-rule 'things visited' counts."""

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

def text_lines(text):
    return re.split(r"\r?\n", text)


def read_lines(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return text_lines(f.read())
    except UnicodeDecodeError:
        raise Unreadable("not valid UTF-8")


def fence_mask(lines):
    """-> (mask, line number of an unterminated fence or None). mask[i]: line i is a fence line or inside a fence."""
    mask, mark, opened = [], None, 0
    for i, ln in enumerate(lines):
        m = FENCE_RE.match(ln)
        mask.append(mark is not None or bool(m))
        if mark is None and m:
            mark, opened = m.group(1), i + 1
        elif mark is not None and m and m.group(1) == mark:
            mark = None
    return mask, (opened if mark else None)


def parse_base(lines):
    """-> dict(lines, mask, unterminated, sections=[(tag,line,name)], pieces=[...], bad=[(line,msg)])."""
    mask, unterminated = fence_mask(lines)
    out = {"lines": lines, "mask": mask, "unterminated": unterminated, "sections": [], "pieces": [], "bad": []}
    heads = [(i, "p" if ln.startswith("### ") else "s") for i, ln in enumerate(lines)
             if not mask[i] and (ln.startswith("### ") or ln.startswith("## "))]
    cur_sec = None
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
             "statement": None, "statement_line": None, "needs": [], "by": [], "see": [], "was": [],
             "skeleton": [], "module": [], "default": [], "old_skeleton": []}
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
        first = next((j for j in range(i + 1, body_end) if lines[j].strip()), None)
        if first is not None and not mask[first] and not META_RE.match(lines[first]):
            p["statement"], p["statement_line"] = lines[first].strip(), first + 1
        for j in range(i + 1, body_end):
            if mask[j]:
                continue
            mm = REF_RE.match(lines[j])
            if mm:
                p[mm.group(1)] += [x for x in re.split(r"[\s,]+", mm.group(2)) if x]
            mm = re.match(r"^(was|skeleton|module|default):(.*)$", lines[j])
            if mm:
                p[mm.group(1)].append((j + 1, mm.group(2).strip()))
            if lines[j].startswith("modes: n/a (skeleton"):
                p["old_skeleton"].append(j + 1)
        out["pieces"].append(p)
    return out


def parse_details(lines):
    """-> dict(lines, unterminated, entries=[{tag,line,fields,text}], bad=[(line,msg)], shared=[slug])."""
    mask, unterminated = fence_mask(lines)
    out = {"lines": lines, "unterminated": unterminated, "entries": [], "bad": [], "shared": []}
    cur, field = None, None
    for i, ln in enumerate(lines):
        if not mask[i] and ln.startswith("## "):
            m = ENTRY_RE.match(ln)
            if not m:
                out["bad"].append((i + 1, "malformed entry heading (want '## <tag> — <name>')"))
                cur = None
                continue
            cur = {"tag": m.group("tag"), "line": i + 1, "start": i, "end": len(lines), "fields": {}, "was": [], "formerly": []}
            if out["entries"]:
                out["entries"][-1]["end"] = i
            out["entries"].append(cur)
            field = None
            continue
        if cur is None:
            mm = None if mask[i] else re.match(r"^shared:(.*)$", ln)
            if mm:
                out["shared"] += [x for x in re.split(r"[\s,]+", mm.group(1)) if x]
            continue
        mv = None if mask[i] else MOVE_RE.match(ln)
        if mv:
            cur[mv.group(1)].append((i + 1, mv.group(2)))
            field = None
            continue
        mm = None if mask[i] else FIELD_RE.match(ln)
        if mm:
            field = mm.group(1)
            cur["fields"].setdefault(field, []).append((i + 1, mm.group(2)))
        elif field and ln.strip():
            cur["fields"][field].append((i + 1, ln))
    # a bad heading (cur None) ends the previous entry's text too
    bad_lines = {b[0] - 1 for b in out["bad"]}
    for e in out["entries"]:
        e["end"] = next((j for j in range(e["start"] + 1, e["end"]) if j in bad_lines), e["end"])
        e["text"] = lines[e["start"]:e["end"]]
        while e["text"] and not e["text"][-1].strip():
            e["text"].pop()
    return out


def record_titles(lines):
    """The citable titles of the record: a `## ` or `### ` heading, or a bold opener that starts a paragraph and begins
    with a date, joined across lines to its closing `**`. Each title and its part before the first ' (' are returned."""
    mask, _ = fence_mask(lines)
    titles = set()

    def add(full):
        full = " ".join(full.split()).rstrip(".")
        titles.add(full)
        titles.add(full.split(" (")[0])

    for i, ln in enumerate(lines):
        if mask[i]:
            continue
        if ln.startswith("### ") or ln.startswith("## "):
            add(ln.split(" ", 1)[1])
        elif BOLD_OPEN_RE.match(ln) and (i == 0 or not lines[i - 1].strip() or lines[i - 1].startswith("#")):
            buf, j = ln, i
            while buf.find("**", 2) < 0 and j + 1 < len(lines) and lines[j + 1].strip():
                j += 1
                buf += " " + lines[j]
            k = buf.find("**", 2)
            if k > 0:
                add(buf[2:k])
    return titles


def ruling_items(e):
    """The `rulings:` items of a details entry: [(first line number, text)]; an item starts at a line beginning `-` and
    runs over its continuation lines (joined with a blank)."""
    items = []
    for ln, t in e["fields"].get("rulings", []):
        if t.strip().startswith("-"):
            items.append([ln, t.strip()])
        elif items and t.strip():
            items[-1][1] += " " + t.strip()
    return [(ln, t) for ln, t in items]


def piece_text(p, e, level):
    """A piece at an entry level: 0 heading + statement, 1 the base piece, 2 + the details entry."""
    if level == 0:
        return [p["text"][0]] + ([p["statement"]] if p["statement"] else [])
    lines = list(p["text"])
    if level >= 2:
        lines += [""] + (e["text"] if e else ["(no details entry)"])
    return lines


def entry_slugs(e):
    out = []
    if e:
        for _, t in e["fields"].get("slugs", []):
            out += [s for s in re.split(r"[\s,]+", t.strip().lstrip("-").strip()) if s and s not in ("none", "-")]
    return out


def load_pieces(read):
    """The reader's input: READ(path) -> text or None. -> [dict(word, piece, entry, slugs)] of every piece whose base
    file exists; an absent file contributes nothing (pilot mode); the first details entry of a tag wins."""
    out = []
    for word, b, d in PAIRS:
        bt = read(b)
        if bt is None:
            continue
        bp = parse_base(text_lines(bt))
        dt = read(d)
        dp = parse_details(text_lines(dt)) if dt is not None else {"entries": []}
        by_tag = {}
        for e in dp["entries"]:
            by_tag.setdefault(e["tag"], e)
        for p in bp["pieces"]:
            if p["tag"]:
                e = by_tag.get(p["tag"])
                out.append({"word": word, "piece": p, "entry": e, "slugs": entry_slugs(e), "was": entry_was(e)})
    return out


def entry_was(e):
    """The previous tags a details entry names on its `was:` lines (the reader resolves them to the entry's piece)."""
    out = []
    for _, t in (e or {}).get("was", []):
        m = WAS_RE.match(t)
        w = m.group("what") if m else (t.split() or [""])[0]
        if w:
            out.append(w)
    return out


# ------------------------------------------------------------------- lint

def load(root, require_all, rep):
    pairs = {}
    for word, b, d in PAIRS:
        bp, dp = os.path.join(root, b), os.path.join(root, d)
        if not os.path.isfile(bp):
            if os.path.isfile(dp):
                rep.fail("L3", d, "details file has no base file %s" % b)
            if require_all:
                rep.fail("L11", b, "base file absent (--require-all)")
            else:
                rep.notes.append("skip %s: %s absent" % (word, b))
            continue
        try:
            bparse = parse_base(read_lines(bp))
        except Unreadable as ex:
            rep.fail("L11", b, "unreadable: %s" % ex)
            continue
        try:
            dparse = parse_details(read_lines(dp)) if os.path.isfile(dp) else None
        except Unreadable as ex:
            rep.fail("L11", d, "unreadable: %s" % ex)
            continue
        pairs[word] = {"base": b, "details": d, "bp": bparse, "dp": dparse, "size": os.path.getsize(bp)}
    return pairs


def valid_date(s):
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def history_hit(line, allowed_date):
    """The first L6 word or foreign ISO date of a base-file line (code spans removed), else None."""
    t = CODE_SPAN_RE.sub("", line)
    m = HIST_RE.search(t)
    if m:
        return m.group(0)
    for d in ISO_RE.findall(t):
        if d != allowed_date:
            return d
    return None


def lint(root, require_all=False, caps=None, writing=False):
    caps = caps or CAPS
    rep = Rep()
    pairs = load(root, require_all, rep)
    rep.ok("L11")
    if not pairs:
        rep.fail("L11", root, "no pair present: nothing linted")
    index = {}   # tag -> (word, ordinal)
    seen_tags = {}
    for word, P in pairs.items():
        b, bp = P["base"], P["bp"]
        if bp["unterminated"]:
            rep.fail("L2", b, "code fence opened at line %d is never closed" % bp["unterminated"])
        for ln, msg in bp["bad"]:
            rep.ok("L2")
            rep.fail("L2", "%s:%d" % (b, ln), msg)
        seen_secs = set()
        for sec, ln, _ in bp["sections"]:
            rep.ok("L2")
            if not SECTION_RE.match(sec) or sec.split("/")[0] != word:
                rep.fail("L2", "%s:%d" % (b, ln), "section tag '%s' is not '%s/<kebab>'" % (sec, word))
            rep.ok("L1")
            if sec in seen_secs:
                rep.fail("L1", "%s:%d" % (b, ln), "duplicate section tag %s" % sec)
            seen_secs.add(sec)
        # L6: history words and foreign dates, every line outside fences; a line's allowed date is its piece's status date
        allowed = {}
        for p in bp["pieces"]:
            for j in range(p["line"] - 1, p["end"]):
                allowed[j] = p["date"] or (ISO_RE.findall(bp["lines"][p["line"] - 1]) or [None])[0]
        for i, ln in enumerate(bp["lines"]):
            if bp["mask"][i]:
                continue
            rep.ok("L6")
            hit = history_hit(ln, allowed.get(i))
            if hit:
                rep.fail("L6", "%s:%d" % (b, i + 1), "history word or foreign date '%s' in a base file" % hit)
        for p in bp["pieces"]:
            where = "%s:%d" % (b, p["line"])
            rep.ok("L2")
            if p["malformed"]:
                rep.fail("L2", where, p["malformed"])
                continue
            tag = p["tag"]
            secname = p["section"][0] if p["section"] else None
            if not TAG_RE.match(tag):
                rep.fail("L2", where, "tag '%s' breaks the grammar <file>/<section>/<piece>[/<sub>] (lower-case kebab)" % tag)
            else:
                # the section tag carries the file word (checked above), so this also puts the tag in its file
                if secname != "/".join(tag.split("/")[:2]):
                    rep.fail("L2", where, "tag '%s' is not in its section %s (a moved piece takes a new tag)" % (tag, secname))
            for ln, _ in p["was"]:
                rep.fail("L6", "%s:%d" % (b, ln), "a 'was:' line in a base file is history (it belongs in the details entry)")
            rep.ok("L1")
            if tag in seen_tags:
                rep.fail("L1", where, "duplicate tag %s (first at %s)" % (tag, seen_tags[tag]))
            else:
                seen_tags[tag] = where
                index[tag] = (word, len(index))
            # L4 status and date
            rep.ok("L4")
            st, date = p["status"], p["date"]
            if date is None:
                rep.fail("L4", where, "no status date (want '<status> YYYY-MM-DD')")
            elif not valid_date(date):
                rep.fail("L4", where, "bad status date %s" % date)
            if st.startswith("open"):
                if not st.startswith("open ") or not SLUG_RE.match(st[4:].strip()):
                    rep.fail("L4", where, "status 'open' needs one question slug (got '%s')" % st)
            elif st not in STATUSES:
                rep.fail("L4", where, "status '%s' not in ruled|principle|reading|open <slug>|under-construction|parked|?" % st)
            elif st == "parked" and word != "parked":
                rep.fail("L4", where, "status 'parked' only in the parked file")
            elif st == "principle" and not tag.startswith("core/principles/"):
                rep.fail("L4", where, "status 'principle' only under core/principles/")
            is_q = st == "?"
            # L12 library fields: module: on every non-? library piece, default: yes only in the library file
            rep.ok("L12")
            for key in ("module", "default"):
                if p[key] and word != "lib":
                    rep.fail("L12", "%s:%d" % (b, p[key][0][0]), "'%s:' only on a library piece" % key)
            if word == "lib":
                if len(p["module"]) > 1:
                    rep.fail("L12", "%s:%d" % (b, p["module"][1][0]), "more than one 'module:' line")
                if not p["module"]:
                    if not is_q:
                        rep.fail("L12", where, "library piece without 'module: <name>' (or 'module: ?')")
                elif not MODULE_RE.match(p["module"][0][1]):
                    rep.fail("L12", "%s:%d" % (b, p["module"][0][0]), "module '%s' is not a dotted lower-case name or '?'"
                             % p["module"][0][1])
                for ln, v in p["default"]:
                    if v != "yes":
                        rep.fail("L12", "%s:%d" % (b, ln), "'default: %s' (the only value is 'yes')" % v)
            # skeleton: yes (statement verified, body not converted): exempt from L8, counted by the ratchet
            skel = bool(p["skeleton"])
            for ln, v in p["skeleton"]:
                rep.ok("L8")
                if v != "yes" or is_q:
                    rep.fail("L8", "%s:%d" % (b, ln), "'skeleton: %s' (want 'skeleton: yes', never on a '?' piece)" % v)
            for ln in p["old_skeleton"]:
                rep.fail("L8", "%s:%d" % (b, ln), "'modes: n/a (skeleton ...)' is replaced by the line 'skeleton: yes'")
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
            if not is_q and not skel and st not in ("parked", "under-construction") and not tag.startswith("core/principles/"):
                rep.ok("L8")
                if not any(t.startswith("modes: n/a") or all(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))
                           for t in p["text"][1:]):
                    rep.fail("L8", where, "no example line naming WHOLE, SEARCHED and FIND-ALL (or 'modes: n/a (<why>)')")
        P["qcount"] = sum(1 for p in bp["pieces"] if p["status"] == "?")
        P["skcount"] = sum(1 for p in bp["pieces"] if p["skeleton"] and p["status"] != "?")
        if P["size"] > caps[word]:
            rep.warns.append("L7 %s: base file is %d bytes, over its soft cap %d" % (b, P["size"], caps[word]))
        rep.ok("L11")
        if not bp["pieces"]:
            rep.fail("L11", b, "no pieces (a base file with none is vacuous)")
        if P["dp"] is not None and not P["dp"]["entries"]:
            rep.fail("L11", P["details"], "no entries (a details file with none is vacuous)")
    # L3 bijection and details-side checks, L4 rulings
    titles = None
    for word, P in pairs.items():
        d, dp, bp = P["details"], P["dp"], P["bp"]
        rep.ok("L3")
        if dp is None:
            rep.fail("L3", d, "details file absent for existing base %s" % P["base"])
            continue
        if dp["unterminated"]:
            rep.fail("L3", d, "code fence opened at line %d is never closed" % dp["unterminated"])
        for ln, msg in dp["bad"]:
            rep.fail("L3", "%s:%d" % (d, ln), msg)
        bt = [p["tag"] for p in bp["pieces"] if p["tag"]]
        dt = [e["tag"] for e in dp["entries"]]
        sb, sd = set(bt), set(dt)
        for t in bt:
            if t not in sd:
                rep.fail("L3", d, "no details entry for base piece %s" % t)
        seen_e = set()
        for e in dp["entries"]:
            if e["tag"] not in sb:
                rep.fail("L3", "%s:%d" % (d, e["line"]), "details entry %s has no base piece" % e["tag"])
            elif e["tag"] in seen_e and bt.count(e["tag"]) == 1:
                rep.fail("L3", "%s:%d" % (d, e["line"]), "duplicate details entry %s" % e["tag"])
            seen_e.add(e["tag"])
        if sb == sd and len(bt) == len(dt) and bt != dt:
            rep.fail("L3", d, "details entries are not in the base file's order")
        by_tag = {}
        for e in dp["entries"]:
            by_tag.setdefault(e["tag"], e)
        for p in bp["pieces"]:
            e = by_tag.get(p["tag"])
            if p["status"] not in ("ruled", "principle") or e is None:
                continue
            rep.ok("L4")
            if not ruling_items(e):
                rep.fail("L4", "%s:%d" % (d, e["line"]), "%s piece %s has no 'rulings:' item" % (p["status"], p["tag"]))
        for e in dp["entries"]:
            for ln, t in ruling_items(e):
                rep.ok("L4")
                m = re.search(r'\(record:\s*"(.+)"\)', t)  # greedy: a title may contain a quote
                if not m:
                    rep.fail("L4", "%s:%d" % (d, ln), 'rulings item without (record: "<entry title>")')
                    continue
                if titles is None:
                    rec = os.path.join(root, RECORD)
                    try:
                        titles = record_titles(read_lines(rec)) if os.path.isfile(rec) else False
                    except Unreadable:
                        titles = False
                if titles is False:
                    rep.fail("L4", d, "record %s absent or unreadable: cannot check titles" % RECORD)
                    break
                if " ".join(m.group(1).split()) not in titles:
                    rep.fail("L4", "%s:%d" % (d, ln), 'record title "%s" not found in %s' % (m.group(1), RECORD))
    # L1/L2 moves and renames: details `was:` and `formerly:` lines
    retired = {}
    for word, P in pairs.items():
        if not P["dp"]:
            continue
        d = P["details"]
        for e in P["dp"]["entries"]:
            for ln, t in e["was"]:
                where = "%s:%d" % (d, ln)
                rep.ok("L2")
                m = WAS_RE.match(t)
                if not m or not TAG_RE.match(m.group("what")) or not valid_date(m.group("date")):
                    rep.fail("L2", where, "want 'was: <previous tag> (<YYYY-MM-DD>, <why>)', got 'was:%s'" % t)
                    continue
                w = m.group("what")
                rep.ok("L1")
                if w in index:
                    rep.fail("L1", where, "was: %s is a live tag (a retired tag is never reused)" % w)
                if w in retired:
                    rep.fail("L1", where, "was: %s is already retired under %s" % (w, retired[w]))
                else:
                    retired[w] = "%s (%s)" % (e["tag"], where)
            for ln, t in e["formerly"]:
                rep.ok("L2")
                m = WAS_RE.match(t)
                if not m or not FORMERLY_NAME_RE.match(m.group("what")) or not valid_date(m.group("date")):
                    rep.fail("L2", "%s:%d" % (d, ln), "want 'formerly: <module.name> (<YYYY-MM-DD>, <why>)', got 'formerly:%s'" % t)
    # L5 references
    for word, P in pairs.items():
        for p in P["bp"]["pieces"]:
            if p["malformed"]:
                continue
            where = "%s:%d" % (P["base"], p["line"])
            for kind in ("needs", "by", "see"):
                for t in p[kind]:
                    rep.ok("L5")
                    if t not in index:
                        tw = t.split("/")[0]
                        if tw in RANK and tw not in pairs and not require_all:
                            continue  # its pair was skipped (pilot mode): unresolvable, not a fault
                        rep.fail("L5", where, "%s: %s names no piece" % (kind, t))
                        continue
                    if kind == "see" and t == p["tag"]:
                        rep.fail("L5", where, "see: %s names the piece itself" % t)
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
        if require_all:
            rep.fail("L10", RATCHET, "ratchet file absent (--require-all)")
        else:
            rep.notes.append("L10: %s absent: ratchet not checked" % RATCHET)
    else:
        try:
            rat, errs = read_ratchet(rp)
        except Unreadable as ex:
            rat, errs = {}, [(0, "unreadable: %s" % ex)]
        for ln, msg in errs:
            rep.ok("L10")
            rep.fail("L10", "%s:%d" % (RATCHET, ln), msg)
        for word, P in pairs.items():
            for key, n, what in ((word, P["qcount"], "'?'"), (word + SKEL, P["skcount"], "skeleton")):
                rep.ok("L10")
                if key not in rat:
                    if not writing:
                        rep.fail("L10", RATCHET, "no ratchet row for %s" % key)
                elif n > rat[key]:
                    rep.fail("L10", P["base"], "%d %s pieces, ratchet row %s allows %d (it only shrinks)" % (n, what, key, rat[key]))
    return rep, pairs


def read_ratchet(path):
    """-> ({key: int}, [(line, message)]): every non-blank line is `<key><TAB><digits>`, once; a key is a file word
    (`core`, its '?' pieces) or a file word and `-skeleton` (`core-skeleton`, its skeleton pieces)."""
    out, errs = {}, []
    for n, ln in enumerate(read_lines(path), 1):
        if not ln.strip():
            continue
        f = ln.split("\t")
        if len(f) != 2 or f[0] not in RATCHET_KEYS or not f[1].isdigit():
            errs.append((n, "bad ratchet line %r (want '<core|lib|parked>[-skeleton]<TAB><count>')" % ln))
        elif f[0] in out:
            errs.append((n, "duplicate ratchet row for %s" % f[0]))
        else:
            out[f[0]] = int(f[1])
    return out, errs


RATCHET_KEYS = [k for w in RANK for k in (w, w + SKEL)]


def write_ratchet(root, out=print):
    """Lower the ratchet to the current '?' and skeleton counts. Only after a clean lint; never creates the root."""
    rep, pairs = lint(root, writing=True)
    if rep.fails:
        out("pred_doc_lint: --write-ratchet refused: the lint fails (%d failures); fix them first" % len(rep.fails))
        return 1
    rp = os.path.join(root, RATCHET)
    old = read_ratchet(rp)[0] if os.path.isfile(rp) else {}
    new = dict(old)
    for word, P in pairs.items():
        for key, n in ((word, P["qcount"]), (word + SKEL, P["skcount"])):
            new[key] = min(old.get(key, n), n)
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    with open(rp, "w", encoding="utf-8") as f:
        for w in RATCHET_KEYS:
            if w in new:
                f.write("%s\t%d\n" % (w, new[w]))
    out("pred_doc_lint: wrote %s: %s" % (rp, ", ".join("%s=%d" % (w, new[w]) for w in RATCHET_KEYS if w in new)))
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


# --------------------------------------------------------------- selftest

def scratch_dir():
    base = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % getpass.getuser()
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


def put(root, path, text, mode="w"):
    with open(os.path.join(root, path), mode, encoding="utf-8") as f:
        f.write(text)


CB, CD = PAIRS[0][1], PAIRS[0][2]
LB, LD = PAIRS[1][1], PAIRS[1][2]
XB, XD = PAIRS[2][1], PAIRS[2][2]
REC = RECORD
CLASS_HEAD = "### Class   [core/holes/class]   reading 2026-11-02\n"
DEF = "Definition sentence.\n"
NAME_HEAD = "### Name   [core/holes/name]   ?  2026-11-03"


def rename_name(r, new):
    sub(r, CB, "[core/holes/name]", "[%s]" % new)
    sub(r, CD, "## core/holes/name —", "## %s —" % new)


def lined(n):
    return "".join("Definition line %d.\n" % i for i in range(n))


def class_lines(r, n):
    """Make the Class piece exactly N lines (heading, statement, needs, by, see, DEF block, modes)."""
    sub(r, CB, DEF, lined(n - 6))


def rec_cite(r, title):
    sub(r, LD, '(record: "2026-11-02 bold words")', '(record: "%s")' % title)


RAT = "core\t1\ncore-skeleton\t0\nlib\t1\nlib-skeleton\t1\nparked\t1\nparked-skeleton\t0\n"  # the sample's own ratchet
SAMPLE_COUNTS = {"core": 1, "core-skeleton": 0, "lib": 1, "lib-skeleton": 1, "parked": 1, "parked-skeleton": 0}


def set_ratchet(r, text):
    put(r, RATCHET, text)


def no_example(r):
    sub(r, CB, "modes: n/a (a hole is not matched on its own)\n", "")


def l6_word(w):
    return lambda r: sub(r, CB, "Definition sentence.", "Definition sentence, %s." % w)


def l8_two(drop):
    return lambda r: sub(r, LB, "WHOLE: t; SEARCHED: t; FIND-ALL: t.", "; ".join(
        "%s: t" % m for m in ("WHOLE", "SEARCHED", "FIND-ALL") if m != drop) + ".")


def swap_entries(r):  # parked details: the two entries in the wrong order
    t = open(os.path.join(r, XD), encoding="utf-8").read()
    a, b = t.index("## parked/ideas/skip"), t.index("## parked/ideas/swap")
    put(r, XD, t[:a] + t[b:] + "\n" + t[a:b].rstrip("\n") + "\n")


def empty_parked(r):
    put(r, XB, "# Parked (sample)\n\n## Ideas   [parked/ideas]\n")
    put(r, XD, "# Parked details (sample)\n")


def plant_malformed_piece(r):
    sub(r, CB, NAME_HEAD, "### Name   core/holes/name   ?  2026-11-03")
    sub(r, CD, "\n## core/holes/name — Name\nslugs:\n", "")


def bom(r):
    raw = open(os.path.join(r, CB), "rb").read().replace(b"# Predicates (sample base file, core)\n\n", b"", 1)
    open(os.path.join(r, CB), "wb").write(b"\xef\xbb\xbf" + raw)


def plant_unreadable(r):
    with open(os.path.join(r, XB), "wb") as f:
        f.write(b"# Parked \xff\xfe\n")


# (rule, label, mutator, lint kwargs, expected count of that rule's failures or None for 'at least one').
# Every plant breaks ONE clause of ONE rule and must fail exactly that rule (and, where a count is given, that often).
PLANTS = [
    ("L1", "duplicate piece tag", lambda r: (sub(r, CB, "[core/holes/name]", "[core/holes/class]"),
                                             sub(r, CD, "## core/holes/name —", "## core/holes/class —"))),
    ("L1", "duplicate section tag", lambda r: put(r, CB, "\n## Holes again   [core/holes]\n", "a")),
    ("L1", "was: names a live tag", lambda r: sub(r, LD, "was: core/holes/word (", "was: core/holes/name (")),
    ("L1", "was: retired in two FILES", lambda r: sub(r, XD, "## parked/ideas/zip — Zip\n", "## parked/ideas/zip — Zip\nwas: core/holes/word (2026-11-07, again)\n")),
    ("L1", "was: retired under two entries",
     lambda r: sub(r, LD, "## lib/names/trimmed — Trimmed\n", "## lib/names/trimmed — Trimmed\nwas: core/holes/word (2026-11-04, again)\n")),
    ("L2", "tag grammar (upper case)", lambda r: rename_name(r, "core/holes/Name")),
    ("L2", "tag grammar (five segments)", lambda r: rename_name(r, "core/holes/name/sub/more")),
    ("L2", "tag in another section", lambda r: rename_name(r, "core/principles/name")),
    ("L2", "tag in another FILE", lambda r: rename_name(r, "lib/holes/name")),
    ("L2", "a moved piece's section is not excused by a details was: line",
     lambda r: (rename_name(r, "core/principles/name"),
                sub(r, CD, "## core/principles/name — Name\n", "## core/principles/name — Name\nwas: core/holes/name (2026-11-03, moved)\n"))),
    ("L2", "was: tag grammar", lambda r: sub(r, LD, "was: core/holes/word (", "was: Core/Holes (")),
    ("L2", "was: without a date", lambda r: sub(r, LD, "(2026-11-05, moved to the library)", "(moved to the library)")),
    ("L2", "was: with an impossible date", lambda r: sub(r, LD, "(2026-11-05, moved to the library)", "(2026-13-40, moved to the library)")),
    ("L2", "was: without a why", lambda r: sub(r, LD, "(2026-11-05, moved to the library)", "(2026-11-05)")),
    ("L2", "formerly: name grammar", lambda r: sub(r, LD, "formerly: text.pad (", "formerly: Text pad (")),
    ("L2", "formerly: a bare name, no module", lambda r: sub(r, LD, "formerly: text.pad (", "formerly: pad (")),
    ("L2", "formerly: with an impossible date", lambda r: sub(r, LD, "(2026-11-02, renamed)", "(2026-02-30, renamed)")),
    ("L2", "formerly: without a why", lambda r: sub(r, LD, "(2026-11-02, renamed)", "(2026-11-02)")),
    ("L2", "malformed piece heading", plant_malformed_piece),
    ("L2", "malformed section heading", lambda r: put(r, CB, "\n## Extra   core/extra\n", "a")),
    ("L2", "section tag grammar", lambda r: put(r, CB, "\n## Extra   [core/Extra]\n", "a")),
    ("L2", "section tag in another file", lambda r: put(r, CB, "\n## Extra   [lib/extra]\n", "a")),
    ("L2", "unterminated fence in a base file", lambda r: put(r, CB, "\n```\nopen forever\n", "a")),
    ("L3", "base piece with no details entry", lambda r: sub(r, LD, "\n## lib/names/word — Word\nwas: core/holes/word (2026-11-05, moved to the library)\nslugs:\n", "")),
    ("L3", "details entry with no base piece", lambda r: put(r, LD, "\n## lib/names/extra — Extra\nslugs:\n", "a")),
    ("L3", "duplicate details entry", lambda r: put(r, LD, "\n## lib/names/word — Word\nslugs:\n", "a")),
    ("L3", "details entries out of order", swap_entries),
    ("L3", "details file absent", lambda r: os.remove(os.path.join(r, XD))),
    ("L3", "details file with no base file", lambda r: os.remove(os.path.join(r, XB))),
    ("L3", "malformed entry heading", lambda r: put(r, LD, "\n## junk heading\n", "a")),
    ("L3", "unterminated fence in a details file", lambda r: put(r, LD, "\nhistory:\n```\nopen forever\n", "a")),
    ("L4", "status outside the set", lambda r: sub(r, CB, "reading 2026-11-02", "blessed 2026-11-02")),
    ("L4", "open without a slug", lambda r: sub(r, LB, "open lib-trim-q 2026-11-04", "open 2026-11-04")),
    ("L4", "open with a non-kebab slug", lambda r: sub(r, LB, "open lib-trim-q 2026-11-04", "open Lib_Trim 2026-11-04")),
    ("L4", "'openfoo' for open", lambda r: sub(r, LB, "open lib-trim-q 2026-11-04", "openlib 2026-11-04")),
    ("L4", "parked outside the parked file", lambda r: sub(r, CB, "reading 2026-11-02", "parked 2026-11-02")),
    ("L4", "principle outside core/principles (a piece with a rulings item)", lambda r: sub(r, LB, "ruled 2026-11-02", "principle 2026-11-02"), {}, 1),
    ("L4", "principle piece with no rulings item",
     lambda r: sub(r, CD, '- 2026-11-01 (class: a principle) "stated" (record: "2026-11-03 second words")\n', "")),
    ("L4", "no status date", lambda r: sub(r, CB, "reading 2026-11-02", "reading")),
    ("L4", "impossible status date", lambda r: sub(r, CB, "reading 2026-11-02", "reading 2026-13-45")),
    ("L4", "ruled piece with no rulings item",
     lambda r: sub(r, CD, '- 2026-11-01 "regex by default" (record: "2026-11-01 first words")', "")),
    ("L4", "rulings item without a record", lambda r: sub(r, CD, ' (record: "2026-11-01 first words")', "")),
    ("L4", "record title absent from the record", lambda r: rec_cite(r, "2026-11-09 no such entry")),
    ("L4", "record title from a plain bold paragraph", lambda r: rec_cite(r, "Note")),
    ("L4", "partial record title", lambda r: rec_cite(r, "2026-11-02 bold")),
    ("L4", "a wrong item beside a right one (every item must cite)",
     lambda r: sub(r, LD, '(record: "2026-11-02 bold words")', '(record: "2026-11-02 bold words")\n- 2026-11-02 "x" (record: "2026-11-09 nope")')),
    ("L4", "a bad item on a non-ruled piece",
     lambda r: sub(r, CD, "- hole as a token — UNTESTED (none)", "- hole as a token — UNTESTED (none)\nrulings:\n- 2026-11-02 \"x\" (record: \"2026-11-09 nope\")")),
    ("L4", "a dated bold line glued to a paragraph is not a title", lambda r: rec_cite(r, "2026-11-06 glued opener")),
    ("L4", "a title inside a fence is not a title", lambda r: rec_cite(r, "2026-11-07 fenced title")),
    ("L4", "record file absent", lambda r: os.remove(os.path.join(r, REC))),
    ("L5", "needs: names no piece", lambda r: sub(r, CB, "needs: core/principles/regex-default", "needs: core/holes/nowhere")),
    ("L5", "needs: second tag of a list names no piece",
     lambda r: sub(r, XB, "needs: lib/names/padded lib/names/trimmed", "needs: lib/names/padded lib/names/nowhere")),
    ("L5", "needs: itself", lambda r: sub(r, CB, "needs: core/principles/regex-default", "needs: core/holes/class")),
    ("L5", "needs: target later in the file", lambda r: sub(
        r, CB, "[core/principles/regex-default]   ruled 2026-11-01\nA bare slash form is a regex unless the owner says otherwise.\n",
        "[core/principles/regex-default]   ruled 2026-11-01\nA bare slash form is a regex unless the owner says otherwise.\nneeds: core/holes/class\n")),
    ("L5", "needs: target in a later file", lambda r: sub(r, CB, "needs: core/principles/regex-default", "needs: lib/names/padded")),
    ("L5", "see: names no piece", lambda r: sub(r, CB, "see: lib/names/word", "see: lib/names/nowhere")),
    ("L5", "see: second tag of a list names no piece", lambda r: sub(r, CB, "see: lib/names/word", "see: lib/names/word lib/names/nowhere")),
    ("L5", "see: the piece itself", lambda r: sub(r, CB, "see: lib/names/word", "see: core/holes/class")),
    ("L5", "by: names no piece", lambda r: sub(r, CB, "by: core/principles/regex-default", "by: core/principles/nowhere")),
    ("L5", "by: target not a principle", lambda r: sub(r, CB, "by: core/principles/regex-default", "by: core/holes/class")),
    ("L6", "WITHDRAWN", l6_word("WITHDRAWN")),
    ("L6", "withdrawn", l6_word("withdrawn")),
    ("L6", "REVERSED", l6_word("REVERSED")),
    ("L6", "reversed", l6_word("reversed")),
    ("L6", "SUPERSEDED", l6_word("SUPERSEDED")),
    ("L6", "superseded", l6_word("superseded")),
    ("L6", "[REV]", l6_word("[REV]")),
    ("L6", "Rev 29", l6_word("Rev 29")),
    ("L6", "revision 29.1", l6_word("revision 29.1")),
    ("L6", "review r56", l6_word("review r56")),
    ("L6", "a bare r56", l6_word("see r56")),
    ("L6", "a date other than the status date", l6_word("on 2026-12-31")),
    ("L6", "another piece's status date", l6_word("on 2026-11-03")),
    ("L6", "a history word on the last line of a long file", lambda r: put(r, CB, "\n## Extra   [core/extra]\n" + "\n" * 40 + "Withdrawn last line.\n", "a")),
    ("L6", "a was: line in a base file", lambda r: sub(r, CB, NAME_HEAD, NAME_HEAD + "\nwas: core/holes/old")),
    ("L6", "a history word in a section heading", lambda r: sub(r, CB, "## Holes   [core/holes]", "## Holes withdrawn   [core/holes]")),
    ("L7", "statement of 201 characters", lambda r: sub(r, CB, "A hole stands for one pattern fragment of the named class.", "S" * 201)),
    ("L7", "piece of 41 lines", lambda r: class_lines(r, PIECE_MAX + 1)),
    ("L7", "no statement line", lambda r: sub(r, CB, "A hole stands for one pattern fragment of the named class.\n", "")),
    ("L7", "a fenced block where the statement belongs", lambda r: sub(r, CB, "A hole stands for one pattern fragment of the named class.\n", "```\nA fenced line.\n```\n")),
    ("L7", "statement after a blank line", lambda r: sub(r, CB, "A hole stands for one pattern fragment of the named class.\nneeds:", "needs:")),
    ("L8", "example line names WHOLE and SEARCHED only", l8_two("FIND-ALL")),
    ("L8", "example line names WHOLE and FIND-ALL only", l8_two("SEARCHED")),
    ("L8", "example line names SEARCHED and FIND-ALL only", l8_two("WHOLE")),
    ("L8", "no example on a core piece", no_example),
    ("L8", "skeleton: no", lambda r: sub(r, LB, "skeleton: yes", "skeleton: no")),
    ("L8", "skeleton: yes on a '?' piece", lambda r: sub(r, LB, "### Word   [lib/names/word]   ?  2026-11-05", "### Word   [lib/names/word]   ?  2026-11-05\nskeleton: yes")),
    ("L8", "the old 'modes: n/a (skeleton ...)' marker", lambda r: sub(r, CB, "modes: n/a (a hole is not matched on its own)", "modes: n/a (skeleton: later)")),
    ("L8", "skeleton line removed: the piece owes its example", lambda r: sub(r, LB, "skeleton: yes\n", "")),
    ("L8", "the heading names the modes, no example", lambda r: (no_example(r), sub(r, CB, "### Class ", "### WHOLE SEARCHED FIND-ALL "))),
    ("L9", "slug on two tags, not shared", lambda r: sub(r, CD, "shared: shared-q\n", "")),
    ("L9", "slug on two tags in two files", lambda r: sub(r, LD, "slugs: shared-q", "slugs: shared-q regex-q")),
    ("L9", "slug not kebab", lambda r: sub(r, LD, "slugs: lib-trim-q", "slugs: Lib_Trim")),
    ("L10", "more '?' pieces than the ratchet", lambda r: set_ratchet(r, RAT.replace("core\t1", "core\t0"))),
    ("L10", "ratchet row with three fields", lambda r: set_ratchet(r, RAT.replace("core\t1", "core\t1\textra"))),
    ("L10", "ratchet row space-separated", lambda r: set_ratchet(r, RAT.replace("core\t1", "core 1"))),
    ("L10", "ratchet count not a number", lambda r: set_ratchet(r, RAT.replace("core\t1", "core\tone"))),
    ("L10", "ratchet row duplicated", lambda r: set_ratchet(r, RAT + "core\t99\n")),
    ("L10", "ratchet word unknown", lambda r: set_ratchet(r, RAT + "extra\t1\n")),
    ("L10", "ratchet lacks a file's row", lambda r: set_ratchet(r, RAT.replace("parked\t1\n", ""))),
    ("L10", "more skeleton pieces than the ratchet", lambda r: set_ratchet(r, RAT.replace("lib-skeleton\t1", "lib-skeleton\t0"))),
    ("L10", "ratchet lacks a skeleton row", lambda r: set_ratchet(r, RAT.replace("core-skeleton\t0\n", ""))),
    ("L10", "ratchet skeleton key misspelt", lambda r: set_ratchet(r, RAT.replace("core-skeleton", "core-skel"))),
    ("L10", "ratchet absent under --require-all", lambda r: os.remove(os.path.join(r, RATCHET)), {"require_all": True}),
    ("L11", "base and details with no pieces and no entries", empty_parked, {}, 2),
    ("L11", "base file absent under --require-all",
     lambda r: (os.remove(os.path.join(r, XB)), os.remove(os.path.join(r, XD))), {"require_all": True}),
    ("L12", "module: missing on a non-'?' library piece", lambda r: sub(r, LB, "module: ?\n", "")),
    ("L12", "module: not a dotted lower-case name", lambda r: sub(r, LB, "module: text", "module: Text")),
    ("L12", "module: with a blank inside", lambda r: sub(r, LB, "module: text", "module: te xt")),
    ("L12", "module: twice", lambda r: sub(r, LB, "module: text\n", "module: text\nmodule: other\n")),
    ("L12", "default: no", lambda r: sub(r, LB, "default: yes", "default: no")),
    ("L12", "default: in the core file", lambda r: sub(r, CB, "see: lib/names/word\n", "see: lib/names/word\ndefault: yes\n")),
    ("L12", "module: in the core file", lambda r: sub(r, CB, "see: lib/names/word\n", "see: lib/names/word\nmodule: ?\n")),
    ("L12", "module: in the parked file", lambda r: sub(r, XB, "Swapping is not in the language until a measured need names it.\n",
                                                      "Swapping is not in the language until a measured need names it.\nmodule: ?\n")),
    ("L11", "no pair at all", lambda r: [os.remove(os.path.join(r, f)) for f in (CB, CD, LB, LD, XB, XD)]),
    ("L11", "a base file that is not UTF-8", plant_unreadable),
    ("L11", "a details file that is not UTF-8", lambda r: put(r, XD, "# Parked \udcff\n") if False else open(os.path.join(r, XD), "wb").write(b"\xff\xfe\n")),
]

CONTROLS = [  # (label, mutator, lint kwargs, expected failing rules after the mutation)
    ("a details was: of a tag retired to another file, and a 'formerly: ?.name'",
     lambda r: (sub(r, LD, "formerly: text.pad (", "formerly: ?.pad.inner ("),
                sub(r, CD, "## core/holes/name — Name\n", "## core/holes/name — Name\nwas: parked/ideas/name (2026-11-03, promoted)\n")), {}, set()),
    ("a 'module: a.b' dotted name, 'module: ?' on a '?' piece",
     lambda r: (sub(r, LB, "module: text", "module: rx.sub"), sub(r, LB, "### Word   [lib/names/word]   ?  2026-11-05", "### Word   [lib/names/word]   ?  2026-11-05\nmodule: ?")), {}, set()),
    ("a fenced was: line in a details entry is not a move",
     lambda r: sub(r, CD, "- hole as a token — UNTESTED (none)", "- hole as a token — UNTESTED (none)\n```\nwas: core/holes/name (2026-11-02, x)\nwas: bad\n```"), {}, set()),
    ("see: into a skipped pair, pilot mode", lambda r: (os.remove(os.path.join(r, LB)), os.remove(os.path.join(r, LD))), {}, set()),
    ("a four-segment tag", lambda r: rename_name(r, "core/holes/name/sub"), {}, set()),
    ("a statement of exactly 200 characters", lambda r: sub(r, CB, "A hole stands for one pattern fragment of the named class.", "S" * 200), {}, set()),
    ("a piece of exactly 40 lines, trailing blank trimmed", lambda r: class_lines(r, PIECE_MAX), {}, set()),
    ("a fenced history word and date", lambda r: sub(r, CB, DEF, "```\nWITHDRAWN rev 3 [REV 2026-12-31\n```\n" + DEF), {}, set()),
    ("an inline-code history word and date", lambda r: sub(r, CB, "Definition sentence.", "Example `Rev 3 on 2026-12-31`."), {}, set()),
    ("prev 2 is not a revision", l6_word("prev 2"), {}, set()),
    ("the piece's own status date in its body", l6_word("on 2026-11-02"), {}, set()),
    ("a fenced needs: line is not a reference", lambda r: sub(r, CB, DEF, "```\nneeds: core/holes/nowhere\n```\n" + DEF), {}, set()),
    ("a record title containing a quote", lambda r: rec_cite(r, '2026-11-08 OWNER, on x: what "flags propagate" meant'), {}, set()),
    ("a rulings item wrapped onto a second line", lambda r: sub(r, LD, ' (record: "2026-11-02 bold words")', '\n  (record: "2026-11-02 bold words")'), {}, set()),
    ("a fence inside a details field", lambda r: sub(r, CD, "- hole as a token — UNTESTED (none)", "- hole as a token — UNTESTED (none)\n```\n## not an entry\nslugs: Bad_Slug\n```"), {}, set()),
    ("a ~~~ fence is not closed by ```", lambda r: sub(r, CB, DEF, "~~~\n```\nWITHDRAWN\n~~~\n" + DEF), {}, set()),
    ("CRLF line ends", lambda r: put(r, CB, open(os.path.join(r, CB), encoding="utf-8").read().replace("\n", "\r\n")), {}, set()),
    ("a '?' piece with no example (L8 not asked)", lambda r: None, {}, set()),
    ("a parked piece with no example", lambda r: sub(r, XB, "\nmodes: n/a (an idea, no mode defined)", "", 2), {}, set()),
    ("an under-construction piece with no example", lambda r: (sub(r, CB, "reading 2026-11-02", "under-construction 2026-11-02"), no_example(r)), {}, set()),
    ("a principle with no example", lambda r: sub(r, CB, "WHOLE: /a/ matches; SEARCHED: /a/ finds; FIND-ALL: /a/g iterates.\n", ""), {}, set()),
    ("slugs: none on two tags and slugs: -", lambda r: (sub(r, XD, "slugs: skip-q", "slugs: none"), sub(r, XD, "slugs: swap-q", "slugs: -"),
                                                         sub(r, XD, "## parked/ideas/zip — Zip\nslugs:", "## parked/ideas/zip — Zip\nslugs: none")), {}, set()),
    ("a comma-separated needs: list", lambda r: sub(r, XB, "needs: lib/names/padded lib/names/trimmed", "needs: lib/names/padded, lib/names/trimmed"), {}, set()),
    ("r2d2 is not a review id", l6_word("the r2d2 droid"), {}, set()),
    ("a fenced heading line is not a piece", lambda r: sub(r, CB, DEF, "```\n### Fake   [core/holes/fake]   ruled 2026-11-01\n```\n" + DEF), {}, set()),
    ("a BOM before the first heading", lambda r: bom(r), {}, set()),
    ("one slug twice on one tag", lambda r: sub(r, CD, "slugs: hole-class shared-q", "slugs: hole-class hole-class shared-q"), {}, set()),
    ("a pair skipped in pilot mode, its needs: not a failure",
     lambda r: (os.remove(os.path.join(r, LB)), os.remove(os.path.join(r, LD))), {}, set()),
    ("the same skipped pair under --require-all fails L5 and L11",
     lambda r: (os.remove(os.path.join(r, LB)), os.remove(os.path.join(r, LD))), {"require_all": True}, {"L5", "L11"}),
    ("an absent ratchet file is a note", lambda r: os.remove(os.path.join(r, RATCHET)), {}, set()),
    ("a ratchet equal to the count", lambda r: None, {}, set()),
    ("citation of a ## heading title", lambda r: rec_cite(r, "2026-11-03 second words"), {}, set()),
    ("citation of a whole ### title with its parenthesis", lambda r: rec_cite(r, "2026-11-01 first words (Frank)"), {}, set()),
    ("citation of a two-line bold opener", lambda r: rec_cite(r, "2026-11-04 wrapped words here"), {}, set()),
    ("citation of a bold title ending in a dot", lambda r: rec_cite(r, "2026-11-05 dotted words"), {}, set()),
    ("citation with doubled blanks", lambda r: rec_cite(r, "2026-11-02  bold   words"), {}, set()),
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
        # the constants the spec states (a mutated constant must not stay green)
        expect(CAPS == {"core": 65536, "lib": 24576, "parked": 16384} and (STATEMENT_MAX, PIECE_MAX) == (200, 40),
               "a cap constant differs from doc_format.md (core 64 KB, lib 24 KB, parked 16 KB, statement 200, piece 40)")
        # clean fixture: no failures, every rule ran, hand-written counts (floors)
        c = fresh("clean")
        rep, _ = lint(c)
        expect(not rep.fails, "clean sample fails: %r" % rep.fails)
        floors = {"L1": 11, "L2": 15, "L3": 3, "L4": 12, "L5": 6, "L6": 50, "L7": 10, "L8": 3, "L9": 5, "L10": 6, "L11": 4, "L12": 10}
        for r, f in floors.items():
            expect(rep.checked[r] >= f, "clean sample: rule %s visited %d, floor %d (a rule that checks nothing)" % (r, rep.checked[r], f))
        n += 1
        covered = set()
        for pl in PLANTS:
            rule, label, mut = pl[:3]
            kw = pl[3] if len(pl) > 3 else {}
            want_n = pl[4] if len(pl) > 4 else None
            d = fresh("p%d" % n)
            mut(d)
            rep, _ = lint(d, **kw)
            got = rep.rules_failed()
            cnt = sum(1 for f in rep.fails if f[0] == rule)
            n += 1
            if got == {rule} and (want_n is None or cnt == want_n):
                covered.add(rule)
                print("selftest: plant %-3s %-52s detected" % (rule, label))
            else:
                expect(False, "plant %s (%s): failed rules %s, %d of %s: %r" % (rule, label, sorted(got), cnt, rule, rep.fails))
        for r in RULES:
            expect(r in covered, "rule %s has no detected plant" % r)
        for label, mut, kw, want in CONTROLS:
            d = fresh("c%d" % n)
            mut(d)
            rep, _ = lint(d, **kw)
            n += 1
            expect(rep.rules_failed() == want, "control '%s': failed rules %s, want %s: %r" % (label, sorted(rep.rules_failed()), sorted(want), rep.fails))
        d = fresh("noratchet")
        os.remove(os.path.join(d, RATCHET))
        rep, _ = lint(d)
        expect(not rep.fails and any(x.startswith("L10") for x in rep.notes), "an absent ratchet file was not a one-line note")
        d = fresh("soft")
        rep, _ = lint(d, caps={"core": 10, "lib": 1 << 20, "parked": 1 << 20})
        expect(not rep.fails and any(w.startswith("L7") for w in rep.warns), "soft cap: want a warning and no failure")
        rep, _ = lint(d, caps={"core": 1 << 20, "lib": 1 << 20, "parked": 1 << 20})
        expect(not rep.warns, "soft cap: a warning under the cap")
        # --write-ratchet: only lowers, only after a clean lint, never creates a root
        d = fresh("wr")
        set_ratchet(d, RAT.replace("core\t1", "core\t5").replace("lib-skeleton\t1", "lib-skeleton\t7"))
        write_ratchet(d, out=lambda s: None)
        got = read_ratchet(os.path.join(d, RATCHET))[0]
        expect(got.get("core") == 1 and got.get("lib-skeleton") == 1, "--write-ratchet did not lower 5 to 1 and 7 to 1: %r" % got)
        set_ratchet(d, RAT.replace("core\t1", "core\t0"))
        write_ratchet(d, out=lambda s: None)
        expect(read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 0, "--write-ratchet raised 0")
        d = fresh("wr2")
        set_ratchet(d, RAT.replace("core\t1", "core\t5"))
        put(d, CB, "", "w")
        expect(write_ratchet(d, out=lambda s: None) == 1 and read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 5,
               "--write-ratchet ratcheted down after a failing lint")
        d = fresh("wr3")
        set_ratchet(d, "core 1\n")
        expect(write_ratchet(d, out=lambda s: None) == 1 and open(os.path.join(d, RATCHET)).read() == "core 1\n",
               "--write-ratchet rewrote a malformed ratchet")
        d = fresh("wr5")
        set_ratchet(d, "core\t5\n")
        expect(write_ratchet(d, out=lambda s: None) == 0 and read_ratchet(os.path.join(d, RATCHET))[0] == SAMPLE_COUNTS,
               "--write-ratchet refused a ratchet that only lacks rows")
        d = fresh("wr4")
        os.remove(os.path.join(d, RATCHET))
        expect(write_ratchet(d, out=lambda s: None) == 0 and read_ratchet(os.path.join(d, RATCHET))[0] == SAMPLE_COUNTS,
               "--write-ratchet did not create the first ratchet from the counts")
        # the parser the reader uses (scripts/entry), hand-written expectations
        got = load_pieces(lambda p: open(os.path.join(sample, p), encoding="utf-8").read() if os.path.isfile(os.path.join(sample, p)) else None)
        by = {g["piece"]["tag"]: g for g in got}
        expect(len(got) == 10 and by["core/holes/class"]["slugs"] == ["hole-class", "shared-q"]
               and by["lib/names/word"]["was"] == ["core/holes/word"] and by["core/holes/name"]["was"] == []
               and piece_text(by["core/holes/class"]["piece"], by["core/holes/class"]["entry"], 0)
               == ["### Class   [core/holes/class]   reading 2026-11-02", "A hole stands for one pattern fragment of the named class."],
               "load_pieces / piece_text level 0: %d pieces" % len(got))
        cp, ce = by["core/holes/class"]["piece"], by["core/holes/class"]["entry"]
        l1, l2 = piece_text(cp, ce, 1), piece_text(cp, ce, 2)
        expect(len(l1) == 7 and l1[-1].startswith("modes: n/a") and l2[:7] == l1 and "## core/holes/class — Class" in l2
               and "slugs: hole-class shared-q" in l2, "piece_text levels 1 and 2: %r" % l2)

        def rd(edit):
            def read(p):
                f = os.path.join(sample, p)
                t = open(f, encoding="utf-8").read() if os.path.isfile(f) else None
                return edit(p, t) if t is not None else None
            return read
        g2 = {g["piece"]["tag"]: g for g in load_pieces(rd(lambda p, t: t.replace("slugs: skip-q", "slugs: none") if p == XD else t))}
        expect(g2["parked/ideas/skip"]["slugs"] == [], "slugs: none is not a slug")
        g3 = {g["piece"]["tag"]: g for g in load_pieces(rd(lambda p, t: t + "\n## parked/ideas/skip — Again\nslugs: other\n" if p == XD else t))}
        expect(g3["parked/ideas/skip"]["slugs"] == ["skip-q"], "the first details entry of a tag must win")
        g4 = load_pieces(rd(lambda p, t: t.replace("\n", "\r\n")))
        g4 = {g["piece"]["tag"]: g for g in g4}["core/holes/class"]
        expect(piece_text(g4["piece"], g4["entry"], 0) == ["### Class   [core/holes/class]   reading 2026-11-02",
               "A hole stands for one pattern fragment of the named class."], "CRLF files: level 0 carries a carriage return")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("selftest: %d runs, %d rules with a detected plant of %d, %d failures" % (n, len(covered), len(RULES), len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root")
    ap.add_argument("--require-all", action="store_true")
    ap.add_argument("--write-ratchet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        if a.root is not None or a.require_all or a.write_ratchet:
            ap.error("--selftest takes no other option")
        return selftest()
    if a.write_ratchet and a.require_all:
        ap.error("--write-ratchet and --require-all conflict")
    root = a.root if a.root is not None else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if not os.path.isdir(root):
        ap.error("--root %s is not a directory" % root)
    if a.write_ratchet:
        return write_ratchet(root)
    rep, _ = lint(root, a.require_all)
    report(rep)
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
