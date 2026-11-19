#!/usr/bin/env -S python3 -I
"""mut.py -- the mutation gate for scripts/pred_doc_lint.py (review r56, the checks critic's harness, kept).

Each mutant is a one-place text edit of the lint (old -> new, the OLD text must occur exactly once). The lint is
copied with its .test, its fixture and tmpdir.sh into a scratch tree, the mutant is written over the copy, and
`scripts/tests/pred_doc_lint.py.test` is run there: a mutant is KILLED when that test fails. A mutant that survives
must be listed in EQUIVALENT with the reason it changes no behaviour a caller or the contract can see.
The expectations are not imported from the lint: the harness only edits its text and reads an exit code.

    python3 -I scripts/tests/pred_doc/mut.py [-v] [NAME-SUBSTRING ...]

Exit 0: every mutant killed or named equivalent (and every EQUIVALENT one really survived, and every OLD text
matched once); 1 otherwise. Last line: `mut: total T, killed K, equivalent E, SURVIVED S, NOMATCH N`.
"""
import concurrent.futures
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, "..", ".."))
LINT = os.path.join(SCRIPTS, "pred_doc_lint.py")

M = []


def m(name, old, new):
    M.append((name, old, new))


# --- L1
m("L1 dup tag off", "if tag in seen_tags:", "if False:")
m("L1 dup section off", "if sec in seen_secs:", "if False:")
m("L1 tag uniqueness per file", "seen_tags = {}\n    for word, P in pairs.items():", "for word, P in pairs.items():\n        seen_tags = {}")
# --- L2
m("L2 malformed piece fail off", 'rep.fail("L2", where, p["malformed"])', "pass")
m("L2 TAG_RE off", "if not TAG_RE.match(tag):", "if False:")
m("L2 tag file word off", 'if tag.split("/")[0] != word:', "if False:")
m("L2 tag-in-section off", 'if secname != "/".join(tag.split("/")[:2]):', "if False:")
m("L2 section grammar and word off", "if not SECTION_RE.match(sec) or sec.split(\"/\")[0] != word:", "if False:")
m("L2 section grammar only", "if not SECTION_RE.match(sec) or", "if")
m("L2 section word only", ' or sec.split("/")[0] != word:', ":")
m("L2 malformed section fail off", 'rep.fail("L2", "%s:%d" % (b, ln), msg)', "pass")
m("L2 was: excuses everything", "if p[\"was\"] is None:\n                    if secname", "if True:\n                    if secname")
m("L2 was: section check off", 'elif secname is None or "/".join(p["was"].split("/")[:2]) != secname:', "elif False:")
m("L2 was: parse off", 'mm = re.match(r"^was:\\s*(\\S+)", lines[j])', "mm = None")
m("L2 4th segment not allowed", "(?:/%s)?$\" % (SEG, SEG, SEG))\nSECTION_RE", "$\" % (SEG, SEG))\nSECTION_RE")
m("L2 unterminated fence (base) off", 'rep.fail("L2", b, "code fence opened', 'pass  # (')
# --- L3
m("L3 base without entry off", "if t not in sd:", "if False:")
m("L3 entry without base off", 'if e["tag"] not in sb:', "if False:")
m("L3 duplicate entry off", 'elif e["tag"] in seen_e and bt.count(e["tag"]) == 1:', "elif False:")
m("L3 order off", "if sb == sd and len(bt) == len(dt) and bt != dt:", "if False:")
m("L3 details absent off", 'rep.fail("L3", d, "details file absent for existing base %s" % P["base"])', "pass")
m("L3 malformed entry heading off", 'rep.fail("L3", "%s:%d" % (d, ln), msg)', "pass")
m("L3 orphan details off", 'rep.fail("L3", d, "details file has no base file %s" % b)', "pass")
m("L3 unterminated fence (details) off", 'rep.fail("L3", d, "code fence opened', 'pass  # (')
m("L3 fence ignored in details headings", 'if not mask[i] and ln.startswith("## "):', 'if ln.startswith("## "):')
m("L3 fence ignored in details fields", "mm = None if mask[i] else FIELD_RE.match(ln)", "mm = FIELD_RE.match(ln)")
# --- L4
m("L4 no date off", "rep.fail(\"L4\", where, \"no status date (want '<status> YYYY-MM-DD')\")", "pass")
m("L4 bad date off", 'rep.fail("L4", where, "bad status date %s" % date)', "pass")
m("L4 open slug off", 'if not st.startswith("open ") or not SLUG_RE.match(st[4:].strip()):', "if False:")
m("L4 open: kebab half off", 'if not st.startswith("open ") or not SLUG_RE.match(st[4:].strip()):', 'if not st.startswith("open "):')
m("L4 open: space half off", 'if not st.startswith("open ") or not SLUG_RE.match(st[4:].strip()):', "if not SLUG_RE.match(st[4:].strip()):")
m("L4 status set off", "elif st not in STATUSES:", "elif False:")
m("L4 parked only in parked off", 'elif st == "parked" and word != "parked":', "elif False:")
m("L4 ruled needs a rulings item off", "if not ruling_items(e):", "if False:")
m("L4 title: greedy quote match off", '(record:\\s*"(.+)"\\)', '(record:\\s*"([^"]+)"\\)')
m("L4 items: no continuation joining", 'items[-1][1] += " " + t.strip()', "pass")
m("L4 item without record off", 'rep.fail("L4", "%s:%d" % (d, ln), \'rulings item without', "pass  # (")
m("L4 title not found off", 'if " ".join(m.group(1).split()) not in titles:', "if False:")
m("L4 title blank-normalise off", 'if " ".join(m.group(1).split()) not in titles:', "if m.group(1) not in titles:")
m("L4 record absent off", 'rep.fail("L4", d, "record %s absent or unreadable: cannot check titles" % RECORD)', "pass")
m("L4 only ruled pieces' items cited", "        for e in dp[\"entries\"]:\n            for ln, t in ruling_items(e):",
  "        for e in [x for x in dp[\"entries\"] if x[\"tag\"] in {p['tag'] for p in bp['pieces'] if p['status'] == 'ruled'}]:\n            for ln, t in ruling_items(e):")
m("L4 non-ruled pieces need rulings", 'if p["status"] != "ruled" or e is None:', "if e is None:")
m("L4 title: dot strip off", 'full = " ".join(full.split()).rstrip(".")', 'full = " ".join(full.split())')
m("L4 title: part before ( off", 'titles.add(full.split(" (")[0])', "pass")
m("L4 title: whole title off", "        titles.add(full)\n", "        pass\n")
m("L4 title: ### off", 'if ln.startswith("### ") or ln.startswith("## "):\n            add', 'if ln.startswith("## "):\n            add')
m("L4 title: ## off", 'if ln.startswith("### ") or ln.startswith("## "):\n            add', 'if ln.startswith("### "):\n            add')
m("L4 title: bold opener off", "elif BOLD_OPEN_RE.match(ln) and", "elif False and")
m("L4 title: any bold paragraph", 'BOLD_OPEN_RE = re.compile(r"^\\*\\*\\d{4}-\\d{2}-\\d{2}\\b")', 'BOLD_OPEN_RE = re.compile(r"^\\*\\*")')
m("L4 title: no joining across lines", "while buf.find(\"**\", 2) < 0 and j + 1 < len(lines) and lines[j + 1].strip():", "while False:")
m("L4 title: paragraph start not required", "and (i == 0 or not lines[i - 1].strip() or lines[i - 1].startswith(\"#\")):", ":")
m("L4 title: fences not skipped", "    for i, ln in enumerate(lines):\n        if mask[i]:\n            continue\n        if ln.startswith(\"### \")", "    for i, ln in enumerate(lines):\n        if ln.startswith(\"### \")")
# --- L5
m("L5 names-no-piece off", 'rep.fail("L5", where, "%s: %s names no piece" % (kind, t))', "pass")
m("L5 by not principle off", 'if kind == "by" and not t.startswith("core/principles/"):', "if False:")
m("L5 later file off", "if RANK[tw] > RANK[word]:", "if False:")
m("L5 later in file off", "elif tw == word and own and tn >= own[1]:", "elif False:")
m("L5 self-needs allowed", "tn >= own[1]", "tn > own[1]")
m("L5 skipped-pair excuse off", "continue  # its pair was skipped (pilot mode): unresolvable, not a fault", "pass")
m("L5 skipped-pair excuse under require-all", "if tw in RANK and tw not in pairs and not require_all:", "if tw in RANK and tw not in pairs:")
m("L5 by: not checked", 'for kind in ("needs", "by"):', 'for kind in ("needs",):')
m("L5 only first tag of a list", 'p[mm.group(1)] += [x for x in re.split(r"[\\s,]+", mm.group(2)) if x]',
  'p[mm.group(1)] += [x for x in re.split(r"[\\s,]+", mm.group(2)) if x][:1]')
m("L5 comma separators off", 'p[mm.group(1)] += [x for x in re.split(r"[\\s,]+", mm.group(2)) if x]',
  'p[mm.group(1)] += [x for x in re.split(r"\\s+", mm.group(2)) if x]')
m("L5 ordinal always 0", "index[tag] = (word, len(index))", "index[tag] = (word, 0)")
m("L5 fenced needs: parsed", "            if mask[j]:\n                continue\n            mm = re.match(r\"^(needs|by):", "            mm = re.match(r\"^(needs|by):")
# --- L6
for w in ("withdrawn", "reversed", "superseded", "rev \\d+", "revision \\d+", "review r\\d+", "r\\d+"):
    m("L6 word %s removed" % w, "|%s" % w if w != "withdrawn" else "(?:withdrawn|", "" if w != "withdrawn" else "(?:")
m("L6 [REV removed", "\\[REV|", "")
m("L6 case-insensitivity off", "|r\\d+)\\b\", re.I)", "|r\\d+)\\b\")")
m("L6 word boundary off", "\\b(?:withdrawn|", "(?:withdrawn|")
m("L6 trailing boundary off", "|r\\d+)\\b\", re.I)", "|r\\d+)\", re.I)")
m("L6 date check off", "    for d in ISO_RE.findall(t):\n        if d != allowed_date:\n            return d", "    pass")
m("L6 any date allowed", "if d != allowed_date:", "if d not in (allowed_date, '2026-12-31', '2026-11-03'):")
m("L6 allowed date from nowhere", "allowed.get(i)", "None")
m("L6 code span exemption off", "t = CODE_SPAN_RE.sub(\"\", line)", "t = line")
m("L6 fence exemption off", "            if bp[\"mask\"][i]:\n                continue\n            rep.ok(\"L6\")", "            rep.ok(\"L6\")")
m("L6 whole check off", 'rep.fail("L6", "%s:%d" % (b, i + 1)', 'print("", ')
m("L6 first 30 lines only", 'for i, ln in enumerate(bp["lines"]):', 'for i, ln in enumerate(bp["lines"][:30]):')
m("L6 last 2 lines skipped", 'for i, ln in enumerate(bp["lines"]):', 'for i, ln in enumerate(bp["lines"][:-2]):')
# --- L7
m("L7 PIECE_MAX 41", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 200, 41")
m("L7 PIECE_MAX 39", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 200, 39")
m("L7 STATEMENT_MAX 201", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 201, 40")
m("L7 STATEMENT_MAX 199", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 199, 40")
m("L7 piece line miscount", 'nlines = p["end"] - p["line"] + 1', 'nlines = p["end"] - p["line"]')
m("L7 trailing blanks counted", "while body_end > i + 1 and not lines[body_end - 1].strip():\n            body_end -= 1", "pass")
m("L7 no-statement fail off", 'rep.fail("L7", where, "no statement line', 'pass  # (')
m("L7 ? may lack off (all may lack)", "if not is_q:\n                    rep.fail", "if False:\n                    rep.fail")
m("L7 ? must have a statement", "if not is_q:\n                    rep.fail", "if True:\n                    rep.fail")
m("L7 statement is first non-meta line", "if first is not None and not mask[first] and not META_RE.match(lines[first]):", "if first is not None:")
m("L7 statement may be fenced", "if first is not None and not mask[first] and", "if first is not None and")
m("L7 soft cap warn off", 'if P["size"] > caps[word]:', "if False:")
m("L7 soft cap becomes hard", 'rep.warns.append("L7 %s: base file', 'rep.fail("L7", b, "x"); rep.warns.append("L7 %s: base file')
m("L7 CAPS core 1K", '"core": 64 * 1024', '"core": 1024')
m("L7 CAPS lib 1K", '"lib": 24 * 1024', '"lib": 1024')
m("L7 CAPS parked 1K", '"parked": 16 * 1024', '"parked": 1024')
m("L7 statement cap off", "elif len(p[\"statement\"]) > STATEMENT_MAX:", "elif False:")
m("L7 piece cap off", "if nlines > PIECE_MAX:", "if False:")
# --- L8
m("L8 fail off", 'rep.fail("L8", where,', 'print("", ')
m("L8 ? exemption off", "if not is_q and st not in", "if st not in")
m("L8 parked exemption off", 'st not in ("parked", "under-construction")', 'st not in ("under-construction",)')
m("L8 under-construction exemption off", 'st not in ("parked", "under-construction")', 'st not in ("parked",)')
m("L8 principles exemption off", ' and not tag.startswith("core/principles/")', "")
m("L8 exemption widened to core", 'not tag.startswith("core/principles/")', 'not tag.startswith("core/")')
m("L8 all modes -> any", 'all(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))', 'any(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))')
m("L8 FIND-ALL not required", '("WHOLE", "SEARCHED", "FIND-ALL"))', '("WHOLE", "SEARCHED"))')
m("L8 SEARCHED not required", '("WHOLE", "SEARCHED", "FIND-ALL"))', '("WHOLE", "FIND-ALL"))')
m("L8 WHOLE not required", '("WHOLE", "SEARCHED", "FIND-ALL"))', '("SEARCHED", "FIND-ALL"))')
m("L8 modes: n/a off", 't.startswith("modes: n/a")', "False")
m("L8 heading line scanned", 'for t in p["text"][1:]', 'for t in p["text"]')
m("L8 first body line only", 'for t in p["text"][1:]', 'for t in p["text"][1:2]')
# --- L9
m("L9 kebab check off", 'rep.fail("L9", "%s:%d" % (P["details"], ln), "slug', 'pass  # (')
m("L9 shared always", "if len(tags) > 1 and s not in shared:", "if False:")
m("L9 shared never", "if len(tags) > 1 and s not in shared:", "if len(tags) > 1:")
m("L9 shared per file only", 'shared.update(P["dp"]["shared"])', "pass")
m("L9 none/- skip off", 's in ("none", "-")', "False")
m("L9 two tags -> three", "if len(tags) > 1 and", "if len(tags) > 2 and")
m("L9 owners reset per file", "for P in pairs.values():\n        if not P[\"dp\"]:\n            continue\n        for e in", "for P in pairs.values():\n        owners = {}\n        if not P[\"dp\"]:\n            continue\n        for e in")
m("L9 same tag twice counts", "tags = {t for t, _ in os_}", "tags = [t for t, _ in os_]")
# --- L10
m("L10 fail off", 'rep.fail("L10", P["base"],', 'print("", ')
m("L10 equality fails", 'elif P["qcount"] > rat[word]:', 'elif P["qcount"] >= rat[word]:')
m("L10 slack of one", 'elif P["qcount"] > rat[word]:', 'elif P["qcount"] > rat[word] + 1:')
m("L10 qcount zero", 'P["qcount"] = sum(1 for p in bp["pieces"] if p["status"] == "?")', 'P["qcount"] = 0')
m("L10 absent ratchet silent under require-all", 'if require_all:\n            rep.fail("L10", RATCHET, "ratchet file absent (--require-all)")', "if False:\n            pass")
m("L10 absent ratchet note off", 'rep.notes.append("L10: %s absent: ratchet not checked" % RATCHET)', "pass")
m("L10 missing row passes", 'if not writing:\n                    rep.fail("L10", RATCHET, "no ratchet row for %s" % word)', "pass")
m("L10 malformed line ignored", 'rep.fail("L10", "%s:%d" % (RATCHET, ln), msg)', "pass")
m("L10 duplicate row: last wins", 'elif f[0] in out:\n            errs.append((n, "duplicate ratchet row for %s" % f[0]))\n        else:', "else:")
m("L10 unknown word accepted", "or f[0] not in RANK or", "or")
m("L10 non-number accepted", "or not f[1].isdigit():", ":")
m("L10 field count not checked", "if len(f) != 2 or f[0]", "if f[0]")
m("L10 write: raises instead of lowers", "new[word] = min(old.get(word, P[\"qcount\"]), P[\"qcount\"])", "new[word] = max(old.get(word, P[\"qcount\"]), P[\"qcount\"])")
m("L10 write: ignores old", "new[word] = min(old.get(word, P[\"qcount\"]), P[\"qcount\"])", "new[word] = P[\"qcount\"]")
m("L10 write: after a failing lint", "    if rep.fails:\n        out(\"pred_doc_lint: --write-ratchet refused", "    if False:\n        out(\"pred_doc_lint: --write-ratchet refused")
m("L10 write: not-writing mode off", "rep, pairs = lint(root, writing=True)", "rep, pairs = lint(root)")
# --- L11
m("L11 no pieces off", 'rep.fail("L11", b, "no pieces (a base file with none is vacuous)")', "pass")
m("L11 no entries off", 'rep.fail("L11", P["details"], "no entries (a details file with none is vacuous)")', "pass")
m("L11 require-all absent off", 'rep.fail("L11", b, "base file absent (--require-all)")', "pass")
m("L11 nothing present silent", 'rep.fail("L11", root, "no pair present: nothing linted")', "pass")
m("L11 unreadable base off", 'rep.fail("L11", b, "unreadable: %s" % ex)', "pass")
m("L11 unreadable details off", 'rep.fail("L11", d, "unreadable: %s" % ex)', "pass")
m("L11 non-UTF-8 crashes", "    except UnicodeDecodeError:\n        raise Unreadable(\"not valid UTF-8\")", "    except KeyError:\n        raise Unreadable(\"not valid UTF-8\")")
m("L11 BOM not stripped", 'encoding="utf-8-sig"', 'encoding="utf-8"')
m("L11 CRLF not split", 'return re.split(r"\\r?\\n", text)', 'return text.split("\\n")')
# --- fences
m("fence: ~~~ closed by ```", "elif mark is not None and m and m.group(1) == mark:", "elif mark is not None and m:")
m("fence: unterminated not reported", "return mask, (opened if mark else None)", "return mask, None")
m("fence: lines inside not masked", "mask.append(mark is not None or bool(m))", "mask.append(bool(m))")
m("fence: ~~~ not a fence", 'FENCE_RE = re.compile(r"^\\s*(```|~~~)")', 'FENCE_RE = re.compile(r"^\\s*(```)")')
m("base heads: fence not skipped", "if not mask[i] and (ln.startswith(\"### \") or ln.startswith(\"## \"))]", "if (ln.startswith(\"### \") or ln.startswith(\"## \"))]")
# --- CLI
m("CLI exit code on fails -> 0", "return 1 if rep.fails else 0", "return 0")
m("CLI main always 0", "    rep, _ = lint(root, a.require_all)\n    report(rep)\n    return 1 if rep.fails else 0", "    rep, _ = lint(root, a.require_all)\n    report(rep)\n    return 0")
m("CLI main always 0 (whole)", "def main(argv=None):\n", "def main(argv=None):\n    return 0\n\n\ndef _main(argv=None):\n")
m("CLI fails not printed", 'for rule, where, msg in rep.fails:\n        out(', "for rule, where, msg in []:\n        out(")
m("CLI missing root accepted", "    if not os.path.isdir(root):\n        ap.error", "    if False:\n        ap.error")
m("CLI selftest takes other options", 'if a.root is not None or a.require_all or a.write_ratchet:\n            ap.error("--selftest takes no other option")', "pass")
m("CLI write-ratchet creates the root", "    if not os.path.isdir(root):\n        ap.error", "    if not os.path.isdir(root) and not a.write_ratchet:\n        ap.error")
# --- the selftest's own machinery
m("ST exact rule -> contains", "if got == {rule} and", "if rule in got and")
m("ST exact rule -> any failure", "if got == {rule} and", "if got and")
m("ST plant count ignored", "(want_n is None or cnt == want_n)", "True")
m("ST controls off", 'expect(rep.rules_failed() == want, "control', 'expect(True, "control')
m("ST clean control off", 'expect(not rep.fails, "clean sample fails: %r" % rep.fails)', "pass")
m("ST floors off", "expect(rep.checked[r] >= f,", "expect(True or rep.checked[r] >= f,")
m("ST covered-all off", 'expect(r in covered, "rule %s has no detected plant" % r)', "pass")
m("ST constants off", 'expect(CAPS == {"core": 65536', 'expect(True or CAPS == {"core": 65536')
m("ST plant text count check off", 'raise SystemExit("selftest: plant text', "pass  # (")
m("ST soft cap control off", 'expect(not rep.fails and any(w.startswith("L7") for w in rep.warns)', "expect(True or any(w.startswith(\"L7\") for w in rep.warns)")
m("ST write-ratchet lowers off", 'expect(read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 1', 'expect(True or read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 1')
m("ST write-ratchet raise off", 'expect(read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 0', 'expect(True or read_ratchet(os.path.join(d, RATCHET))[0].get("core") == 0')
m("ST load_pieces off", 'expect(len(got) == 9 and', 'expect(True or len(got) == 9 and')
# --- the parser the reader calls
m("RD level 2 omits details", "if level >= 2:", "if level >= 3:")
m("RD level 0 omits statement", '+ ([p["statement"]] if p["statement"] else [])', "")
m("RD slugs: none not dropped", 'if s and s not in ("none", "-")]', "if s]")
m("RD first entry of a tag wins", "by_tag.setdefault(e[\"tag\"], e)\n        for p in bp[\"pieces\"]:\n            if p[\"tag\"]:", "by_tag[e[\"tag\"]] = e\n        for p in bp[\"pieces\"]:\n            if p[\"tag\"]:")

# Survivors that are NOT bugs: each with the reason it changes nothing observable.
ASSERT_WEAKENED = ("an assertion of the selftest weakened or removed: it holds on the unmutated lint, so the test cannot go red; "
                   "it is killed only in combination with a lint mutant, and each such lint mutant is a row above")
EQUIVALENT = {
    "L6 word review r\\d+ removed": "'review r56' also matches the bare review-id alternative r\\d+; the named alternative is kept for the text's sake",
    "L10 write: ignores old": "write_ratchet writes only after a clean lint, and a clean lint means count <= ratchet, so min(old, count) == count",
    "ST exact rule -> contains": ASSERT_WEAKENED,
    "ST exact rule -> any failure": ASSERT_WEAKENED,
    "ST plant count ignored": ASSERT_WEAKENED,
    "ST controls off": ASSERT_WEAKENED,
    "ST clean control off": ASSERT_WEAKENED,
    "ST floors off": ASSERT_WEAKENED,
    "ST covered-all off": ASSERT_WEAKENED,
    "ST constants off": ASSERT_WEAKENED,
    "ST plant text count check off": ASSERT_WEAKENED,
    "ST soft cap control off": ASSERT_WEAKENED,
    "ST write-ratchet lowers off": ASSERT_WEAKENED,
    "ST write-ratchet raise off": ASSERT_WEAKENED,
    "ST load_pieces off": ASSERT_WEAKENED,
    "L1 tag uniqueness per file": "tags carry their file word and L2 fails a tag in the wrong file, so a cross-file duplicate always also fails L2; "
                                  "within one file the per-file reset is the same dict. Equivalent except under an L2 failure already reported.",
}


def run_one(i, name, old, new, src):
    d = tempfile.mkdtemp(prefix="m%d_" % i, dir=SCRATCH)
    try:
        os.makedirs(d + "/scripts/tests")
        shutil.copy(os.path.join(SCRIPTS, "tmpdir.sh"), d + "/scripts/")
        shutil.copy(os.path.join(SCRIPTS, "tests", "pred_doc_lint.py.test"), d + "/scripts/tests/")
        shutil.copytree(os.path.join(SCRIPTS, "tests", "pred_doc"), d + "/scripts/tests/pred_doc", ignore=shutil.ignore_patterns("mut.py", "__pycache__"))
        with open(d + "/scripts/pred_doc_lint.py", "w", encoding="utf-8") as f:
            f.write(src.replace(old, new))
        r = subprocess.run(["bash", d + "/scripts/tests/pred_doc_lint.py.test"], capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PCREC_TMPDIR=SCRATCH))
        return i, r.returncode, (r.stdout + r.stderr)[-300:]
    except subprocess.TimeoutExpired:
        return i, 124, "timeout"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    global SCRATCH
    verbose = "-v" in sys.argv
    only = [a for a in sys.argv[1:] if a != "-v"]
    base = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % os.environ.get("USER", "x")
    os.makedirs(os.path.join(base, "scratch"), exist_ok=True)
    SCRATCH = tempfile.mkdtemp(prefix="mut", dir=os.path.join(base, "scratch"))
    src = open(LINT, encoding="utf-8").read()
    todo, nomatch = [], []
    for i, (name, old, new) in enumerate(M):
        if only and not any(o in name for o in only):
            continue
        if src.count(old) != 1:
            nomatch.append("%s (matches %d)" % (name, src.count(old)))
        else:
            todo.append((i, name, old, new))
    killed = survived = equiv = 0
    bad = []
    try:
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            futs = [ex.submit(run_one, i, name, old, new, src) for i, name, old, new in todo]
            for (i, name, _, _), fu in zip(todo, futs):
                _, rc, tail = fu.result()
                if rc != 0:
                    killed += 1
                    if name in EQUIVALENT:
                        bad.append("KILLED but listed equivalent: %s" % name)
                    if verbose:
                        print("killed   %s" % name)
                elif name in EQUIVALENT:
                    equiv += 1
                    print("equivalent %s: %s" % (name, EQUIVALENT[name]))
                else:
                    survived += 1
                    print("SURVIVED %s" % name)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    for x in nomatch:
        print("NOMATCH  " + x)
    for x in bad:
        print(x)
    print("mut: total %d, killed %d, equivalent %d, SURVIVED %d, NOMATCH %d" % (len(todo) + len(nomatch), killed, equiv, survived, len(nomatch)))
    return 0 if not (survived or nomatch or bad) else 1


SCRATCH = ""
if __name__ == "__main__":
    sys.exit(main())
