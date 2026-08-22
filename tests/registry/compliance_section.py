#!/usr/bin/env python3
"""SR-4: make `pcrec --list-syntax` load-bearing for docs/pcre2_compliance.md.

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

Two checks, doing different jobs:

  --check   the generated section matches the current dump (inventory drift)
  --names   every ``module `X` `` named anywhere in the prose is a module the
            registry actually knows (analysis drift)

The second is the one that catches the realistic failure. A module renamed in
registry.c leaves the prose quietly describing a module that no longer exists,
and no test in this repo would have noticed before now.

Usage:
    compliance_section.py --render          print the section
    compliance_section.py --check           exit 1 on drift (used by make test)
    compliance_section.py --names           exit 1 on an unknown module name
    compliance_section.py --write           update the doc in place
"""
import subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
DOC = os.path.join(ROOT, "docs", "pcre2_compliance.md")

BEGIN = "<!-- BEGIN GENERATED: registry construct index (SR-4) -->"
END = "<!-- END GENERATED -->"

COLS = ["kind", "selector", "syntax", "module", "feature", "flavours",
        "engines", "status", "diag", "flags", "expect", "note", "roadmap",
        "quantifiable", "class_expect", "built"]


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
    if len(rows) != 100:
        sys.exit(f"compliance_section: dump has {len(rows)} rows, expected 100. "
                 "If you added or removed a construct deliberately, update this "
                 "number in the same commit; if not, coverage was lost")
    return rows


def md_escape(s):
    return s.replace("|", "\\|")


def render(rows):
    doorway = {"esc": "after `\\`", "group": "after `(?`", "verb": "after `(*`",
               "class-bracket": "after `[` in a class"}
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
           f"{len(rows)} rows from one declarative table (D24). The prose sections "
           "above carry the analysis; this is the inventory, and it cannot drift "
           "from the compiler because it is printed by it.",
           "",
           "| doorway | syntax | status | built | roadmap | module | engines | PCRE2 semantics |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        status = {"base": "`OK`", "module": "`REJECTED`",
                  "rejected": "`AGREES-REJECT`"}.get(r["status"], r["status"])
        # D65: `built` is orthogonal to `status`/`roadmap` (a THIRD axis —
        # has the owning module's producer landed for THIS construct,
        # derived live by pcrec_construct_built_status rather than a
        # hand-declared field). "—" for RS_BASE/RS_REJECTED rows, where the
        # question does not arise, matching `roadmap`'s own "—" convention
        # just to its right.
        built = {"built": "`built`", "unbuilt": "`unbuilt`"}.get(r["built"], "—")
        out.append("| {} | `{}` | {} | {} | {} | {} | {} | {} |".format(
            doorway.get(r["kind"], r["kind"]),
            md_escape(r["syntax"]),
            status,
            built,
            r["roadmap"] if r["roadmap"] != "-" else "—",
            f"`{r['module']}`" if r["module"] else "—",
            r["engines"] or "—",
            md_escape(r["note"] or "")))
    out += ["", END]
    return "\n".join(out) + "\n"


def splice(text, section):
    if BEGIN in text:
        head = text[:text.index(BEGIN)]
        tail = text[text.index(END) + len(END):].lstrip("\n")
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
        # consistent, so including it would dilute the check
        if BEGIN in text:
            text = text[:text.index(BEGIN)] + text[text.index(END) + len(END):]
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
        cur = text[text.index(BEGIN):text.index(END) + len(END)] + "\n"
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

    sys.exit(f"unknown mode {mode}")


if __name__ == "__main__":
    sys.exit(main())
