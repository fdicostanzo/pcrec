#!/usr/bin/env python3
r"""SR-4: make `pcrec --list-syntax` load-bearing for docs/pcre2_compliance.md.

WHAT THIS DOES NOT DO, and why. The plan text said the compliance document is
"RENDERED from" the dump. Taken literally that would replace a hand-written
survey — DFA-feasibility judgements, the reasoning behind each `PLANNED` vs
`PLANNED-HARD` call, the two divergence post-mortems, and every row about BASE
syntax, which the registry deliberately does not describe — with a table the
registry can already print. The document's value is the analysis, not the
inventory.

So the inventory is generated and the analysis is not. This script owns one
delimited section of the file, regenerates it from the dump, and fails the
build when the checked-in copy has drifted. Everything outside the markers is
written by a human and left alone.

[DOC-DRV], 2026-08-21: a THIRD component joined the first two — the hand-
written measurements and judgment that used to live inline in each prose
row's notes column now live construct-KEYED in
docs/pcre2_compliance_annotations.txt (component 3, format documented in
that file's own header) and are rendered back into the page as one small
generated block per section, immediately after that section's own
hand-written (component 2, survey) table. The survey itself — each
section's `syntax | status | becomes` table — is UNCHANGED by this: it
stays hand-written prose, same as always. Only the notes moved.

Four checks, doing different jobs:

  --check              the generated construct index matches the current
                        dump (component 1 inventory drift)
  --names              every ``module `X` `` named anywhere in the prose is a
                        module the registry actually knows (component 2
                        analysis drift)
  --check-annotations  every annotation KEY names a live construct (a stale
                        key — renamed/removed in registry.c, or a dropped
                        BASE_KEYS entry — fails naming it) and the page's
                        generated annotation blocks match the store
                        (component 3 drift, both the key-liveness sense and
                        the render-drift sense)
  --tension             informational: backtick-quoted tokens in the
                        hand-written survey prose vs. the registry's
                        RS_MODULE `syntax` set, both directions reported —
                        the CHECKED TENSION between components 1 and 2

The --names check is the one that catches the realistic component-2 failure:
a module renamed in registry.c leaves the prose quietly describing a module
that no longer exists, and no test in this repo would have noticed before
now. --check-annotations is the equivalent net for component 3: an
annotation whose construct moved or vanished is exactly the recurring
staleness [DOC-DRV] exists to retire (the `\b \B \G` row that read
`REJECTED` for two waves after both had shipped — see docs/dev/plan.md's
[DOC-DRV] row).

Usage:
    compliance_section.py --render              print the construct index
    compliance_section.py --check               exit 1 on index drift (make test)
    compliance_section.py --names               exit 1 on an unknown module name
    compliance_section.py --write                update the doc's construct index in place
    compliance_section.py --check-annotations    exit 1 on a stale key or render drift (make test)
    compliance_section.py --write-annotations    update the doc's annotation blocks in place
    compliance_section.py --tension              print the checked-tension report (informational)
"""
import subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
DOC = os.path.join(ROOT, "docs", "pcre2_compliance.md")
ANNOT_PATH = os.path.join(ROOT, "docs", "pcre2_compliance_annotations.txt")

BEGIN = "<!-- BEGIN GENERATED: registry construct index (SR-4) -->"
END = "<!-- END GENERATED -->"

# [DOC-DRV] component 3, KEYED ANNOTATIONS: the hand-written measurements
# and judgment migrated out of docs/pcre2_compliance.md's prose-row notes
# columns into docs/pcre2_compliance_annotations.txt (format documented in
# that file's own header), rendered back into the page by this script as
# one small generated block per section, immediately after that section's
# own hand-written (component 2, survey) table.
#
# SECTIONS — every section of docs/pcre2_compliance.md that carries a
# component-2 survey table and therefore may carry component-3
# annotations, in the order they appear in the page. A section with zero
# annotations still gets an (empty) generated block, so the marker pair
# always exists and `--check-annotations` can always find it.
SECTIONS = [
    "quoting", "braced-items", "escaped-characters", "character-types",
    "unicode-properties", "character-classes", "quantifiers",
    "anchors-assertions", "match-point", "alternation-capturing",
    "comment", "option-setting", "newline-convention", "lookaround",
    "substring-scan", "backreferences", "subroutine-recursion",
    "conditional-patterns", "backtracking-verbs", "callouts",
    "replacement-strings",
]

# BASE_KEYS — the annotation store's `base:*` keys' own inventory: the
# base-tier and cross-cutting constructs docs/pcre2_compliance.md discusses
# that the registry deliberately does not itemize (SR-4's own header: "the
# registry deliberately does not describe" base grammar), so nothing can
# generate this list the way `--list-syntax` generates the registry's own.
# Typed out INDEPENDENTLY of docs/pcre2_compliance_annotations.txt (not
# derived from it) so a `base:` key that drifts — renamed or deleted in one
# place and not the other — fails rather than silently agreeing with
# itself. Update this list in the SAME commit as any `base:` key change in
# the annotation store.
BASE_KEYS = frozenset([
    "base:alt-bsux-u-brace", "base:alt-bsux-U-uhhhh",
    "base:alternation-basic", "base:anchor-caret", "base:anchor-dollar",
    "base:braced-whitespace-scope", "base:capturing-group-limit",
    "base:class-brackets-basic", "base:class-escape-fallbacks",
    "base:class-quoting-e", "base:class-set-ops-uts18",
    "base:conditional-assert",
    # "base:conditional-define" RETIRED at [DD-14] wave F: `(?(DEFINE)` is
    # a real registry row now (module `recursion`, D71 item 4), so its
    # annotation is keyed to that row's own `syntax` and checked against a
    # live dump instead of against this allowlist. Left as a comment rather
    # than deleted so a reader who greps for the old key finds out where it
    # went; the entry itself must go, or a base key nothing uses would sit
    # here forever certifying a construct that no longer needs one.
    "base:conditional-name-disambiguation",
    "base:conditional-recursion-test", "base:conditional-version",
    "base:dot", "base:double-quantifier", "base:escapes-control-letters",
    "base:hex-escape-braced", "base:hex-escape-xhh",
    "base:lookaround-verb-spellings", "base:newline-bsr",
    "base:newline-convention-verbs", "base:option-run-doorway-ordering",
    "base:posix-word-boundary-classes", "base:quantifier-brace-precedence",
    "base:quantifier-brace-whitespace", "base:quantifier-count-overflow",
    "base:quantifier-large-bounded-repeat",
    "base:quantifier-nothing-to-quantify", "base:quantifier-on-anchors",
    "base:quantifiers-greedy", "base:quantifiers-lazy",
    "base:quantifiers-possessive", "base:quoting-backslash-nonalnum",
    "base:recursion-grouplist", "base:replacement-strings",
    "base:scan-substring", "base:script-run", "base:uprops-k16-byte-census",
    "base:verb-fail", "base:verbs-backtracking-control-family",
    "base:verbs-caseless-turkish", "base:verbs-doorway-q1",
    "base:verbs-k15-name-length", "base:verbs-limit-depth",
    "base:verbs-module-attribution-gap", "base:verbs-no-jit-family",
    "base:verbs-notempty", "base:verbs-out-of-scope-diagnostic",
    "base:verbs-utf-ucp",
])

ANNOT_KEY_RE = re.compile(r'(?m)^=== (\S+)\n')
BEGIN_ANNOT_RE = re.compile(r'<!-- BEGIN GENERATED ANNOTATIONS: (\S+) -->')


def parse_annotations():
    """Parse docs/pcre2_compliance_annotations.txt into a list of dicts
    {key, section, date, text}, in file order — see that file's own header
    for the format. A record with no `section: ` line gets section=None,
    which check_annotations() reports as a failure (every record must name
    where it renders)."""
    text = open(ANNOT_PATH).read()
    pieces = ANNOT_KEY_RE.split(text)
    records = []
    # pieces[0] is the file's leading comment block (discarded); then
    # alternating (key, body) pairs.
    for i in range(1, len(pieces), 2):
        key = pieces[i]
        lines = pieces[i + 1].splitlines()
        section = None
        date = None
        idx = 0
        if idx < len(lines) and lines[idx].startswith("section: "):
            section = lines[idx][len("section: "):].strip()
            idx += 1
        if idx < len(lines) and lines[idx].startswith("date: "):
            date = lines[idx][len("date: "):].strip()
            idx += 1
        body = "\n".join(lines[idx:]).strip("\n")
        records.append({"key": key, "section": section, "date": date,
                         "text": body})
    return records


def check_annotations(rows):
    """--check-annotations: every annotation key names a LIVE construct —
    a current `--list-syntax` `syntax` value for a plain key, or a
    BASE_KEYS entry for a `base:` key (a stale key, from a construct
    renamed/removed in src/parse/registry.c or a base: entry dropped from
    BASE_KEYS, fails here naming it) — plus no duplicate keys and every
    record names a section this script knows how to render. Returns the
    parsed records on success, None on failure (mirrors dump()'s
    exit-on-failure shape but as a return so --check-annotations can print
    its own PASS/FAIL rather than a bare traceback)."""
    records = parse_annotations()
    live_syntax = {r["syntax"] for r in rows}
    seen = set()
    dup = sorted({r["key"] for r in records if r["key"] in seen or seen.add(r["key"])})
    bad_section = [(r["key"], r["section"]) for r in records
                   if r["section"] not in SECTIONS]
    bad_keys = []
    for r in records:
        k = r["key"]
        if k.startswith("base:"):
            if k not in BASE_KEYS:
                bad_keys.append(k)
        elif k not in live_syntax:
            bad_keys.append(k)

    ok = True
    if dup:
        print(f"FAIL: duplicate annotation key(s) in {ANNOT_PATH}: "
              f"{', '.join(dup)}", file=sys.stderr)
        ok = False
    if bad_section:
        names = ", ".join(f"{k!r} -> {s!r}" for k, s in bad_section)
        print(f"FAIL: annotation(s) name a section this script does not "
              f"know (add it to SECTIONS if it's real): {names}",
              file=sys.stderr)
        ok = False
    if bad_keys:
        print(f"FAIL: {len(bad_keys)} stale annotation key(s) in {ANNOT_PATH} "
              f"do not name a live construct (a plain key must be a current "
              f"`pcrec --list-syntax` `syntax` value; a `base:` key must be "
              f"in this script's BASE_KEYS): {', '.join(bad_keys)}",
              file=sys.stderr)
        ok = False
    if not ok:
        return None
    nbase = len([r for r in records if r["key"].startswith("base:")])
    print(f"PASS: all {len(records)} annotation keys name live constructs "
          f"({len(records) - nbase} registry, {nbase} base), no duplicates, "
          f"no unknown section")
    return records


def render_annotations_block(slug, records):
    recs = [r for r in records if r["section"] == slug]
    out = [f"<!-- BEGIN GENERATED ANNOTATIONS: {slug} -->", "",
           "<!-- Generated by tests/registry/compliance_section.py from",
           "     docs/pcre2_compliance_annotations.txt. Do not edit by",
           "     hand: `make test` fails on drift. Edit the annotation",
           "     store and re-run with --write-annotations. -->", ""]
    if not recs:
        out.append("*(no annotations keyed to this section)*")
        out.append("")
    backtick = "`"
    for r in recs:
        stamp = f" ({r['date']})" if r["date"] else ""
        out.append(f"**{backtick}{r['key']}{backtick}**{stamp}")
        out.append("")
        out.append(r["text"])
        out.append("")
    out.append(END)
    # No trailing "\n" after END: splice_annotations's tail slice (the
    # untouched text starting right after the original END marker) begins
    # with the newline that terminates END's own line, so appending one
    # here too would double it — one extra blank line per section, growing
    # without bound across repeated --write-annotations runs. Measured
    # live: it did, before this fix.
    return "\n".join(out).rstrip("\n")


def splice_annotations(text, records):
    """Replace every existing `BEGIN GENERATED ANNOTATIONS: <slug>` ...
    `END GENERATED` region in `text` with a freshly rendered one for that
    slug. Returns (new_text, missing_slugs) — missing_slugs are SECTIONS
    entries with no marker pair in the page at all, which --check-
    annotations and --write-annotations both treat as a hard failure (a
    section that never got its marker pair added is not "no annotations",
    it is un-wired)."""
    out = []
    pos = 0
    found = set()
    for m in BEGIN_ANNOT_RE.finditer(text):
        slug = m.group(1)
        end_at = text.index(END, m.end())
        out.append(text[pos:m.start()])
        out.append(render_annotations_block(slug, records))
        pos = end_at + len(END)
        found.add(slug)
    out.append(text[pos:])
    missing = [s for s in SECTIONS if s not in found]
    return "".join(out), missing


def check_tension(rows, text):
    """The CHECKED-TENSION guard between component 1 (the registry) and
    component 2 (the independent survey): every backtick-quoted token in
    the page's hand-written survey prose (everything OUTSIDE any generated
    marker pair) is compared against the registry's own `syntax` set for
    `RS_MODULE` rows (the constructs PCRE2 has that pcrec's base grammar
    does not — the population a survey row should exist for; `RS_BASE` and
    `RS_REJECTED`/AGREES-REJECT rows are excluded: base grammar is the
    survey's whole subject rather than one token in it, and the five
    AGREES-REJECT rows — `\\N{name}`, `(?PX)`, `(?q)`, `[[.a.]]`,
    `[[=a=]]` — are "PCRE2 doesn't have this either" trivia the survey has
    never carried a row for). Reports BOTH directions and is informational
    by design (exit 0 regardless): a registry construct the survey prose
    never quotes verbatim is a real, occasionally legitimate gap (a
    generic placeholder like `(?n)` standing in for `(?0)`..`(?9)` is
    exactly this shape) rather than a defect, and this check's job is to
    surface it where nothing did before, not to force every gap to zero
    the way an exact-count check would."""
    # Strip every generated region (the SR-4 index AND all annotation
    # blocks) before scanning for survey tokens, so an annotation's own
    # backtick-quoted cross-references (rendered FROM the registry) cannot
    # be mistaken for hand-written survey coverage.
    stripped = []
    pos = 0
    markers = sorted(
        [(m.start(), m.end()) for m in BEGIN_ANNOT_RE.finditer(text)] +
        ([(text.index(BEGIN), text.index(BEGIN) + len(BEGIN))] if BEGIN in text else [])
    )
    for start, end in markers:
        end_at = text.index(END, end) + len(END)
        stripped.append(text[pos:start])
        pos = end_at
    stripped.append(text[pos:])
    survey_text = "".join(stripped)
    survey_tokens = set(re.findall(r'`([^`\n]+)`', survey_text))

    module_syntax = {r["syntax"] for r in rows if r["status"] == "module"}
    registry_only = sorted(module_syntax - survey_tokens)
    print(f"INFO: checked-tension (survey vs. registry, RS_MODULE "
          f"population {len(module_syntax)}): {len(registry_only)} "
          f"registry construct(s) never appear as a literal backtick token "
          f"in the hand-written survey prose (some legitimately — a "
          f"generic placeholder like `(?n)` standing in for the whole "
          f"`(?0)`..`(?9)` family is expected here, not a defect):")
    for s in registry_only:
        print(f"      registry-only: {s}")

    # The other direction: a backtick token that LOOKS like PCRE2 syntax
    # (opens with `\`, `(` or `[` — the three doorway bytes) but names no
    # registry row at all, module or base. Filtered to syntax-shaped
    # tokens on purpose: an unfiltered survey_tokens - all_syntax diff is
    # mostly noise (identifiers, file names, flag spellings quoted for
    # other reasons), and this direction's real audit value is narrower —
    # "the survey discusses a construct the registry has never heard of",
    # which base-tier notation (`\d`-shaped but never registry-tracked by
    # design) already accounts for most of, so this is reported but not
    # expected to run near zero the way the registry-only direction might.
    all_syntax = {r["syntax"] for r in rows}
    syntax_shaped = {t for t in survey_tokens if t[:1] in "\\([" and t not in all_syntax}
    print(f"INFO: checked-tension (registry vs. survey): "
          f"{len(syntax_shaped)} syntax-shaped backtick token(s) in the "
          f"survey prose name no registry row at all (expected for base-"
          f"tier notation, which the registry deliberately does not "
          f"track — SR-4's own header):")
    for s in sorted(syntax_shaped):
        print(f"      survey-only: {s}")
    return registry_only, sorted(syntax_shaped)

COLS = ["kind", "selector", "syntax", "module", "feature", "flavours",
        "engines", "status", "diag", "flags", "expect", "note", "roadmap",
        "quantifiable", "class_expect", "built", "family"]


def dump():
    out = subprocess.run([PCREC, "--list-syntax"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"compliance_section: pcrec --list-syntax failed: {out.stderr}")
    lines = out.stdout.splitlines()

    # [SR-11] GENERATOR AGREEMENT (docs/spec/table_contract.md, "The
    # checks"): COLS above is this script's own transcription of
    # --list-syntax's column order, and a transcription that stops matching
    # its source is exactly the D65 failure shape one level up
    # (docs/design/registry_built_status_memo.md's Correction section) — a
    # hardcoded field COUNT drifted silently until an appended column broke
    # two consumers. So COLS is cross-checked here against the dump's OWN
    # header line rather than trusted. tests/lib/table.sh implements the
    # identical contract rule for shell/awk consumers (comment-skip, "the
    # last `#` line before the first data row is the header"); this is
    # python and cannot source that file, so it re-implements the same rule
    # rather than diverging from it, and THIS check is what keeps the two
    # implementations from being able to disagree silently about what the
    # header says.
    header = None
    for line in lines:
        if line.startswith("#"):
            header = line
            continue
        break  # first data row: `header` is now fixed (table.sh's rule 3)
    if header is None:
        sys.exit("compliance_section: --list-syntax produced no header line")
    dump_cols = header[1:].split("\t")
    if dump_cols != COLS:
        sys.exit("compliance_section: COLS (this script's column list) does "
                  "not match --list-syntax's own header — a column was "
                  "appended, renamed or reordered in the dump without "
                  "updating COLS in the same commit.\n"
                  f"  COLS   = {COLS!r}\n"
                  f"  header = {dump_cols!r}")

    rows = []
    for line in lines:
        if line.startswith("#") or not line:
            continue
        f = line.split("\t")
        if len(f) != len(COLS):
            sys.exit(f"compliance_section: dump row has {len(f)} fields, "
                     f"expected {len(COLS)}: {line!r}")
        rows.append(dict(zip(COLS, f)))
    # EXACT, not a floor. This was `< 60` against 67 rows, i.e. seven rows of
    # slack in the one absolute anchor either doc-side check had (R6 T-4).
    # Bumping it is deliberate and belongs in the same commit as the row.
    # 100 -> 104 at [M6.4.2]: the four RK_QUANTSUFFIX rows (`a*+` `a++` `a?+`
    # `a{1,2}+`), module `atomic-groups`. They are the first rows in the table
    # that reach no doorway; they exist so the generated index below can say
    # something about the possessive spellings at all, instead of leaving a
    # reader unable to tell "not implemented" from "not in the table".
    # 104 -> 106 at [M6.5.2]: two new `RK_ESC` rows with tails `<` and `'`,
    # module `recursion`. The `\g` doorway carries TWO CONSTRUCTS and the table
    # had ONE row for it -- a subroutine call re-runs the group's PATTERN where
    # a backreference compares the captured TEXT (measured) -- so module
    # `backrefs` claims the brace-and-bare-digit half and the angle-bracket and
    # quote tails get rows of their own, born unbuilt. Without them the
    # generated index would say `\g` is built and say NOTHING about the
    # subroutine spellings, which is the same reader problem the quantifier
    # suffix rows were added to close.
    # 106 -> 118 at [M6.6.2] wave F: the twelve `(*` alpha lookaround
    # spellings (Frank's ASK 3 ruling, 2026-08-23). They are INDEX rows
    # (RF_INDEX, D71 item 3) -- real, distinct PCRE2 spellings a caller
    # writes, with no byte-keyed dispatch identity because the `(*` doorway
    # decides by NAME. The generated index below COLLAPSES them into their
    # primaries' family lines, so this count is of ROWS and the index's own
    # line count is smaller; both numbers are asserted, separately, because
    # they answer different questions.
    # 118 -> 128 at [DD-14] wave F: module `recursion`'s nine RF_INDEX rows
    # (design §8.1's four missing spelling families) plus the `(?(DEFINE)` row
    # (D71 item 4). Nine of the ten are spellings the compiler ALREADY handled
    # and no surface named; the tenth is a new construct.
    if len(rows) != 128:
        sys.exit(f"compliance_section: dump has {len(rows)} rows, expected 128. "
                 "If you added or removed a construct deliberately, update this "
                 "number in the same commit; if not, coverage was lost")
    return rows


def md_escape(s):
    return s.replace("|", "\\|")


def families(rows):
    """[M6.6.2 wave F / D71 item 3] Group the dump's rows into INDEX lines.

    A row's KEY is its `family` column if set and its own `syntax` otherwise,
    so a row with no family and no aliases pointing at it is a family of one
    and renders exactly as it always has — which is every row but the twelve
    `(*` alpha lookaround spellings today.

    Returns a list of (key, [rows]) in first-appearance order. The order is
    the DUMP's, deliberately: the generated index has always been the dump's
    own order, and a family that re-sorted itself would move unrelated lines
    in the page's diff every time a row was added.

    The rendering rules D71 item 3 states, applied by `render` below:
      - the line's SYNTAX is the key (the family's canonical spelling);
      - `built` is ANDed over the members — a family reads built only if
        EVERY member does;
      - every member's spelling is listed, so nothing becomes invisible by
        being grouped. That last one is the whole point: the reason these
        rows exist at all is that twelve spellings a caller can write were
        absent from this page (design §8.2, Frank's ASK 3 ruling).
    """
    order, by_key = [], {}
    for r in rows:
        key = r["family"] or r["syntax"]
        if key not in by_key:
            by_key[key] = []
            order.append(key)
        by_key[key].append(r)
    return [(k, by_key[k]) for k in order]


def render(rows):
    doorway = {"esc": "after `\\`", "group": "after `(?`", "verb": "after `(*`",
               "class-bracket": "after `[` in a class"}
    fams = families(rows)
    out = [BEGIN,
           "",
           "<!-- Generated by tests/registry/compliance_section.py from",
           "     `pcrec --list-syntax`. Do not edit by hand: `make test` fails",
           "     on drift. Add a construct by adding a row to",
           "     src/parse/registry.c, then re-run with --write. -->",
           "",
           "## Registry construct index (generated)",
           "",
           f"Every non-base construct pcrec knows, as the parser itself sees it — "
           f"{len(rows)} rows from one declarative table (D24), rendered as "
           f"{len(fams)} lines because a construct with several SPELLINGS gets "
           "one line naming them all (D71 item 3). The prose sections "
           "above carry the analysis; this is the inventory, and it cannot drift "
           "from the compiler because it is printed by it.",
           "",
           "`built` on a multi-spelling line is ANDed over its spellings: the "
           "line reads `built` only if every one of them does.",
           "",
           "| doorway | syntax | status | built | roadmap | module | engines | PCRE2 semantics |",
           "|---|---|---|---|---|---|---|---|"]
    for key, members in fams:
        # The line speaks for the family. Its non-`built` columns come from
        # the CANONICAL member — the row whose own `syntax` is the key — and
        # from the first member when the key is a family-level spelling no row
        # carries (recursion's `(?N)`, the next customer). Which one is read
        # cannot matter: tests/registry/registry_check.c's `check_families`
        # asserts the members agree on module, engines and status, and fails
        # loudly rather than letting this line pick a winner silently.
        r = next((m for m in members if m["syntax"] == key), members[0])
        status = {"base": "`OK`", "module": "`REJECTED`",
                  "rejected": "`AGREES-REJECT`"}.get(r["status"], r["status"])
        # D65: `built` is orthogonal to `status`/`roadmap` (a THIRD axis —
        # has the owning module's producer landed for THIS construct,
        # derived live by pcrec_construct_built_status rather than a
        # hand-declared field). "—" for RS_BASE/RS_REJECTED rows, where the
        # question does not arise, matching `roadmap`'s own "—" convention
        # just to its right.
        # D71 item 3's AND rule. A family whose members have no `built`
        # answer at all (RS_BASE/RS_REJECTED) reads "—", matching `roadmap`'s
        # own convention just to its right.
        vals = [m["built"] for m in members]
        if all(v not in ("built", "unbuilt") for v in vals):
            built = "—"
        elif all(v == "built" for v in vals):
            built = "`built`"
        else:
            built = "`unbuilt`"
        note = r["note"] or ""
        if len(members) > 1:
            others = [m["syntax"] for m in members if m["syntax"] != key]
            note = (note + (" — " if note else "")
                    + "also spelled "
                    + ", ".join("`%s`" % o for o in others))
        out.append("| {} | `{}` | {} | {} | {} | {} | {} | {} |".format(
            doorway.get(r["kind"], r["kind"]),
            md_escape(key),
            status,
            built,
            r["roadmap"] if r["roadmap"] != "-" else "—",
            f"`{r['module']}`" if r["module"] else "—",
            r["engines"] or "—",
            md_escape(note)))
    out += ["", END]
    return "\n".join(out) + "\n"


def splice(text, section):
    if BEGIN in text:
        begin_at = text.index(BEGIN)
        head = text[:begin_at]
        # [DOC-DRV]: search for END starting AFTER this BEGIN, not from
        # the start of the file — the annotation blocks this script also
        # generates now contribute their own earlier "<!-- END GENERATED
        # -->" occurrences, and an unqualified text.index(END) would find
        # the wrong one and slice backwards.
        tail = text[text.index(END, begin_at) + len(END):].lstrip("\n")
        return head + section + ("\n" + tail if tail else "")
    return text.rstrip("\n") + "\n\n" + section


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    rows = dump()

    if mode == "--names":
        known = {r["module"] for r in rows if r["module"]}
        # the compound row prints two module names joined by '/'
        known |= {p for m in list(known) for p in m.split("/")}
        text = open(DOC).read()
        # only the hand-written half: the generated section is by construction
        # consistent, so including it would dilute the check. Search for END
        # starting AFTER this BEGIN (not from the start of the file) — same
        # reasoning as splice()'s fix above: an unqualified text.index(END)
        # now finds an annotation block's earlier END instead of this one's.
        if BEGIN in text:
            begin_at = text.index(BEGIN)
            text = text[:begin_at] + text[text.index(END, begin_at) + len(END):]
        # [DOC-DRV]: same reasoning extends to the annotation blocks — their
        # "module `X`" mentions are rendered from docs/pcre2_compliance_
        # annotations.txt, not typed into the page, so scanning them here
        # would be scanning the store a second time under a different name
        # rather than checking anything new. Build the stripped text from
        # the ORIGINAL match offsets in one pass rather than mutating
        # `text` while iterating over them, which would read each
        # subsequent match's offset against an already-shortened string.
        kept, pos = [], 0
        for m in BEGIN_ANNOT_RE.finditer(text):
            end_at = text.index(END, m.end()) + len(END)
            kept.append(text[pos:m.start()])
            pos = end_at
        kept.append(text[pos:])
        text = "".join(kept)
        bad = sorted({m for m in re.findall(r"module `([a-z0-9/-]+)`", text)
                      if m not in known})
        if bad:
            print(f"FAIL: docs/pcre2_compliance.md names {len(bad)} module(s) the "
                  f"registry does not know: {', '.join(bad)}", file=sys.stderr)
            print("      (a module renamed in src/parse/registry.c leaves the "
                  "prose describing something that no longer exists)",
                  file=sys.stderr)
            return 1
        n = len(set(re.findall(r"module `([a-z0-9/-]+)`", text)))
        print(f"PASS: every module named in pcre2_compliance.md prose exists in "
              f"the registry ({n} distinct)")

        # K14 (MOD-0.1, design §17.2, R14/C2-F8: the one-source direction is
        # CHECKED, not generated): the survey's hand-written OUT-OF-SCOPE rows
        # and the table's ROADMAP_NEVER column must agree in BOTH directions,
        # so the independent home that caught K14 stays independent and cannot
        # drift from the diagnostics. Verb names are compared per-name against
        # `pcrec --list-verbs` (disposition is a per-name fact); registry rows
        # against the dump's roadmap column.
        vout = subprocess.run([PCREC, "--list-verbs"], capture_output=True, text=True)
        if vout.returncode != 0:
            print("FAIL: pcrec --list-verbs failed", file=sys.stderr)
            return 1
        never_dump = set()
        for line in vout.stdout.splitlines():
            if line.startswith("#") or not line:
                continue
            f = line.split("\t")
            if len(f) != 6:
                print(f"FAIL: --list-verbs row has {len(f)} fields, expected 6: "
                      f"{line!r}", file=sys.stderr)
                return 1
            if f[4] == "never":
                never_dump.add(f[1])
        # names inside OUT-OF-SCOPE prose table rows. `(*:NAME)` carries no
        # name and is MARK's synonym; MARK itself appears beside it.
        never_prose = set()
        for line in text.splitlines():
            if "OUT-OF-SCOPE" in line:
                never_prose |= set(re.findall(r"\(\*([A-Za-z_0-9]+)", line))
        only_prose = sorted(never_prose - never_dump)
        only_dump  = sorted(never_dump - never_prose)
        if only_prose:
            print(f"FAIL: pcre2_compliance.md marks these verb names OUT-OF-SCOPE "
                  f"but the tables do not carry ROADMAP_NEVER for them: "
                  f"{', '.join(only_prose)}", file=sys.stderr)
            return 1
        if only_dump:
            print(f"FAIL: the verb tables mark these names ROADMAP_NEVER but no "
                  f"OUT-OF-SCOPE row in pcre2_compliance.md's prose mentions them: "
                  f"{', '.join(only_dump)}", file=sys.stderr)
            return 1
        if not never_dump:
            print("FAIL: the OUT-OF-SCOPE <=> ROADMAP_NEVER check compared an "
                  "EMPTY set — that is vacuity, not agreement", file=sys.stderr)
            return 1
        print(f"PASS: OUT-OF-SCOPE prose and ROADMAP_NEVER agree, both directions "
              f"({len(never_dump)} verb names)")
        # ...and the RS_MODULE registry-row instances at non-verb doorways
        # (esc / group / class-bracket; verbs are the loop above via
        # --list-verbs). RS_MODULE + ROADMAP_NEVER is the K14 shape this
        # whole function is about — a construct real enough that PCRE2 has
        # it and pcrec's OWN table would otherwise promise a module for it,
        # deliberately refused instead. That is NOT the same population as
        # "RS_REJECTED rows carry ROADMAP_NEVER too" (D34 item 1's mandatory
        # pairing for constructs PCRE2 itself rejects — `(?PX)`, `(?q)`,
        # `[[.a.]]`, `[[=a=]]`, `\N{name}` today): agreement-with-PCRE2's-own-
        # rejection needs no OUT-OF-SCOPE prose link at all, and an earlier
        # version of this generalization wrongly flagged all five as missing
        # one (caught by running this check, not by inspection).
        #
        # UNTIL [M4-CALLOUTS] step 1 (2026-08-14) this block hardcoded the
        # callouts row as the one RS_MODULE instance, matching its canonical
        # syntax "(?C1)" against any prose line mentioning "(?C" OUT-OF-SCOPE
        # — a hand link rather than a generic one, because (unlike verb
        # names) a group-doorway row's canonical `syntax` and its prose
        # spelling do not share a token a regex can extract cleanly (the
        # prose row spelled three variants, `(?C)` `(?Cn)` `(?C"text")`, none
        # equal to the row's own `(?C1)`). The flip moved the callouts row to
        # PLANNED, dropping this population to ZERO. The branch stays
        # COLUMN-DERIVED rather than deleted — it reads `rows` fresh every
        # run, so a new RS_MODULE + ROADMAP_NEVER row makes it fail loudly
        # instead of silently passing, and the failure is where the next
        # author adds that row's own hand link (the way this comment now
        # documents the callouts row's, for the historical link see the
        # [M4-CALLOUTS] step 1 commit).
        never_module_rows = sorted(r["syntax"] for r in rows
                                   if r["roadmap"] == "never" and r["status"] == "module")
        if never_module_rows:
            print(f"FAIL: RS_MODULE registry rows are ROADMAP_NEVER but this "
                  f"check has no prose link wired for them yet: "
                  f"{never_module_rows} — add one (see this function's "
                  f"comment)", file=sys.stderr)
            return 1
        print("PASS: no RS_MODULE ROADMAP_NEVER rows today (population 0 "
              "since [M4-CALLOUTS] step 1's flip); the check stays "
              "column-derived and re-arms the day one exists")
        return 0

    section = render(rows)
    if mode == "--render":
        sys.stdout.write(section)
        return 0

    text = open(DOC).read()
    if mode == "--write":
        open(DOC, "w").write(splice(text, section))
        print(f"wrote {len(rows)} rows into {DOC}")
        return 0

    if mode == "--check":
        if BEGIN not in text:
            print("FAIL: docs/pcre2_compliance.md has no generated section — run "
                  "tests/registry/compliance_section.py --write", file=sys.stderr)
            return 1
        # search for END starting after this BEGIN — see splice()'s comment
        begin_at = text.index(BEGIN)
        cur = text[begin_at:text.index(END, begin_at) + len(END)] + "\n"
        if cur != section:
            print("FAIL: docs/pcre2_compliance.md's generated construct index has "
                  "drifted from `pcrec --list-syntax`", file=sys.stderr)
            print("      fix: tests/registry/compliance_section.py --write",
                  file=sys.stderr)
            for a, b in zip(cur.splitlines(), section.splitlines()):
                if a != b:
                    print(f"      doc:  {a}\n      dump: {b}", file=sys.stderr)
                    break
            return 1
        print(f"PASS: pcre2_compliance.md's construct index matches the dump "
              f"({len(rows)} rows)")
        return 0

    # [DOC-DRV] component 3: the annotation store <-> page seam. Same
    # render/--write/--check shape SR-4 already established for component 1
    # above, applied to N named blocks instead of one.
    if mode == "--check-annotations":
        records = check_annotations(rows)
        if records is None:
            return 1
        new_text, missing = splice_annotations(text, records)
        if missing:
            print(f"FAIL: docs/pcre2_compliance.md is missing the generated-"
                  f"annotations marker pair for section(s): "
                  f"{', '.join(missing)} — add\n"
                  f"      <!-- BEGIN GENERATED ANNOTATIONS: <slug> -->\n"
                  f"      <!-- END GENERATED -->\n"
                  f"      right after that section's survey table, then "
                  f"re-run --write-annotations", file=sys.stderr)
            return 1
        if new_text != text:
            print("FAIL: docs/pcre2_compliance.md's annotation blocks have "
                  "drifted from docs/pcre2_compliance_annotations.txt",
                  file=sys.stderr)
            print("      fix: tests/registry/compliance_section.py "
                  "--write-annotations", file=sys.stderr)
            for a, b in zip(text.splitlines(), new_text.splitlines()):
                if a != b:
                    print(f"      doc:  {a}\n      store: {b}", file=sys.stderr)
                    break
            return 1
        print(f"PASS: pcre2_compliance.md's {len(SECTIONS)} annotation "
              f"blocks match docs/pcre2_compliance_annotations.txt "
              f"({len(records)} records)")
        return 0

    if mode == "--write-annotations":
        records = check_annotations(rows)
        if records is None:
            return 1
        new_text, missing = splice_annotations(text, records)
        if missing:
            print(f"FAIL: cannot write — section(s) with no marker pair in "
                  f"the page yet: {', '.join(missing)}", file=sys.stderr)
            return 1
        open(DOC, "w").write(new_text)
        print(f"wrote {len(records)} annotation record(s) across "
              f"{len(SECTIONS)} section blocks into {DOC}")
        return 0

    if mode == "--tension":
        check_tension(rows, text)
        return 0

    sys.exit(f"unknown mode {mode}")


if __name__ == "__main__":
    sys.exit(main())
