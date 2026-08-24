#!/usr/bin/env python3
"""[DD-14] SELF-CONSISTENCY CHECKS for subroutines_design.md + its measurements.

Three checks, all of which exist because R34 found the class BY HAND and this
lane could not find it by reading:

  1. ARCHIVE FRESHNESS -- every probe has an archive and is not newer than it.
     R34 V-7 (a TIME table matching no archived run) and V-11 (a timing with
     no archive at all) are what this catches.
  2. SABOTAGE-ROW COVERAGE -- every S-SR id in §9.3's table appears in some
     §11 landing bar's DETECTED LIST.
  3. CORPUS-FILE COVERAGE -- every `*.rxt` in §10.2's table appears in some
     §11 landing bar.

IT FAILS LOUDLY: every problem is printed AND the exit status is nonzero.
A check whose failure looks like output is the thing it is here to catch.

TWO DEFECTS OF ITS OWN, both found by exercising it in the FAILING direction
rather than by reading it, and both recorded because they are the same shape
as the findings the file exists for:

  (a) the first draft matched a BARE `.rxt` produced by prose like "every
      `.rxt` file", and reported `ok` for it -- and `.rxt` is a substring of
      every real filename, so the row could never fail. The name is now
      required.
  (b) the first draft asked whether an id appeared ANYWHERE in §11, and
      PASSED a sabotage that deleted S-SR7 from every bar -- because a bar
      also contains the sentence "the range notation hid S-SR7 and S-SR9
      from this document's own coverage audit", so PROSE ABOUT an id
      satisfied the check FOR that id. That is this project's own
      check-design lesson (a control sharing a source with what it controls)
      reproduced inside the control written to enforce it. Check 2 now reads
      only the COMMA-SEPARATED DETECTED LIST, never the surrounding prose.

Read-only. Resolves paths from its own location.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.normpath(os.path.join(HERE, ".."))
DOC = os.path.normpath(os.path.join(MEAS, "..", "subroutines_design.md"))
PROBES, OUT = os.path.join(MEAS, "probes"), os.path.join(MEAS, "out")

problems = []


def bad(msg):
    print("  !! " + msg)
    problems.append(msg)


def section(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i)]


if not os.path.exists(DOC):
    print("no design doc at %s" % DOC)
    sys.exit(3)
doc = open(DOC).read()

print("=== CHECK 1: every probe has a CURRENT archive =======================")
probes = sorted(f for f in os.listdir(PROBES)
                if f.startswith("probe_") and f.endswith((".py", ".sh")))
if not probes:
    bad("no probes found -- the extractor is broken")
for b in probes:
    n = re.sub(r"^probe_", "", re.sub(r"\.(py|sh)$", ".txt", b))
    src, arc = os.path.join(PROBES, b), os.path.join(OUT, n)
    if not os.path.exists(arc):
        bad("%s has NO archive (expected out/%s)" % (b, n))
    elif os.path.getmtime(src) > os.path.getmtime(arc):
        bad("%s is NEWER than out/%s -- re-run probes/archive.sh" % (b, n))
    else:
        print("  ok  %-28s -> out/%s" % (b, n))
print()

# The landing bars, and within them ONLY the comma-separated DETECTED lists.
bars = section(doc, "## 11.", "## 12.")
# The separator is ordinary English list punctuation -- a comma OR "and" --
# because wave F's bar reads "**S-SR2a** and **S-SR13** DETECTED" while every
# other bar uses commas. The check verifies an ASSIGNMENT, not prose style,
# so it accepts both; requiring commas made it report S-SR13 unplaced when
# the bar plainly places it.
_ID = r"(?:\*\*)?S-SR[0-9a-z]+(?:\*\*)?"
_SEP = r"(?:\s*,\s*|\s+and\s+)"
detected = " ".join(re.findall(
    r"(%s(?:%s%s)*)[^.]{0,80}?DETECTED" % (_ID, _SEP, _ID), bars))
placed = set(re.findall(r"S-SR[0-9a-z]+", detected))

print("=== CHECK 2: every sabotage row is in a §11 bar's DETECTED list ======")
ids = sorted(set(re.findall(r"^\| \*\*(S-SR[0-9a-z]+)\*\*", doc, re.M)))
if not ids:
    bad("no S-SR rows found in §9.3 -- the extractor is broken")
if not placed:
    bad("no DETECTED lists found in §11 -- the extractor is broken, so every "
        "row below would fail for the wrong reason")
for i in ids:
    (print("  ok  " + i) if i in placed
     else bad("%s is in §9.3's table but in NO §11 DETECTED list" % i))
print()

print("=== CHECK 3: every .rxt corpus file is named in a §11 landing bar ====")
files = sorted(set(re.findall(r"[a-z][a-z_0-9]*\.rxt",
                              section(doc, "## 10.", "## 11."))))
if not files:
    bad("no .rxt files found in §10 -- the extractor is broken")
for f in files:
    (print("  ok  " + f) if f in bars
     else bad("%s is in §10.2's table but in NO §11 landing bar" % f))
print()

if problems:
    print("FAILED: %d problem(s) above." % len(problems))
    sys.exit(1)
print("PASSED: archives current; every sabotage row and corpus file placed.")
