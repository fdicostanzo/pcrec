# CRITIC contract: predlint (r56)

## Findings

Method: rules_from_text.md (this dir) was written from doc_format.md before the script was opened. Cases are built by
tools/run_cases.py (copies of scripts/tests/pred_doc/root under cases/); output is in cases_out.txt. Each run:
`PCREC_TMPDIR=<lens> python3 -I <review tree>/scripts/pred_doc_lint.py --root cases/<C> --require-all`.

### CONTRACT-1: L6 is case-sensitive, so the text's own words in lower case pass
CONFIRMED. Severity: silent-pass. Effort: trivial. Blast radius: every base file. pred_doc_lint.py:56 (HIST_RE).
§Rules of use lists "withdrawn" and "reversed" in lower case, and L6 says "the word list above". HIST_RE matches only
upper-case WITHDRAWN|REVERSED|SUPERSEDED. C01 (`This rule was withdrawn once.` in a piece body) -> rc=0, "failed 0".
C02 (`Reversed by the owner.`) -> rc=0. Expected: an L6 failure. Fix: `(?i:...)`.

### CONTRACT-2: L6 does not check "dates other than the status date"
CONFIRMED. Severity: silent-pass. Effort: small. Blast radius: every base file. pred_doc_lint.py:242-253 has no date
clause at all. §Rules of use: "no revision marks, review ids, 'withdrawn', 'reversed', dates other than the status date".
C03 (`Decided on 2026-01-05 after a long talk.` in a piece body) -> rc=0. Expected: an L6 failure.

### CONTRACT-3: L6 misses revision marks and review ids the text names, and `rev \d+` matches inside other words
CONFIRMED. Severity: wrong-verdict in both directions. Effort: small. Blast radius: every base file. pred_doc_lint.py:56.
- Misses: C04 `As of revision 29.1 this holds.` -> rc=0. C05 `Raised as r56 item 3.` -> rc=0. Only the two-word form
  `review r12` is caught (C30 -> L6).
- False fail: C06 `Matches the prev 2 fragments.` -> `L6 ... history word 'rev 2'`, because there is no `\b`.
- Invented: `SUPERSEDED` (C26 -> L6) has no sentence in the text; add it to the doc's word list.
Fix: `\b` anchors, `revision \d`, a stated review-id shape, and a doc word list matching the code.

### CONTRACT-4: L8 exempts `?` pieces; the text does not, and the committed sample depends on that
CONFIRMED. Severity: doc (text/code divergence; under the text the sample is RED). Effort: one clause. Blast radius:
every `?` piece, and the pilot skeleton is mostly `?`. pred_doc_lint.py:307 (`not is_q`); docstring l.19 "(R1)".
L8: "(not asked of a `parked` or `under-construction` piece, nor of a principle)"; `?` is not listed. The sample's
three `?` pieces have no example and pass. C07 (a `?` piece with a definition line and no example) -> rc=0. The
docstring says the stricter reading was taken, but this one is the LOOSER reading. Likely fix: name `?` in L8's sentence.

### CONTRACT-5: a `was:` line excuses the path check whatever it says, including the FILE check
CONFIRMED. Severity: silent-pass. Effort: small. Blast radius: any moved or mis-filed piece. pred_doc_lint.py:138-140,
263-268. §Tags: "the lint's path check reads a `was:` line". The code never reads the line's content.
- C08 (`was: zzz` on core/principles/name under section core/holes) -> rc=0.
- C09 (a `[lib/holes/name]` piece in predicates.md with `was: core/holes/name`) -> rc=0: a tag naming the wrong file passes.
The selftest's positive control (l.719-723) proves only that a `was:` excuses, never that a wrong one does not.

### CONTRACT-6: L3 passes a duplicated details entry
CONFIRMED. Severity: silent-pass. Effort: trivial. Blast radius: every details file. pred_doc_lint.py:336-345.
L3 says "in bijection"; §Tags says "one per tag". When `bt != dt`, the code reports only missing or extra tags, plus an
order fault gated on `len(bt) == len(dt)`, so a repeated entry gets past all three. C10 (a second
`## core/holes/name — Name again`) -> rc=0. `by_tag` (l.347) then silently keeps the last copy. Fix: a fallback failure
whenever `bt != dt` and nothing else fired.

### CONTRACT-7: L10 is skipped silently when the ratchet is absent, unparsable, or lacks a file's row
CONFIRMED. Severity: silent-pass. Effort: small. Blast radius: the whole `?` ratchet. pred_doc_lint.py:420-439.
- C31 (ratchet file removed) -> rc=0 even with --require-all; it prints only a note.
- C35 (rows separated by spaces instead of tabs, then one more `?` in core and in lib) -> rc=0.
- C34 (only a core row, one more `?` in core and in lib) -> only core fails; lib's growth passes.
Expected, at least under --require-all: an L10 failure.

### CONTRACT-8: an absent base file switches off L11 (and L5 into it) unless --require-all, a flag the text never names
CONFIRMED. Severity: design/doc (silent-pass in the default mode). Effort: a doc hunk. Blast radius: default runs.
pred_doc_lint.py:203-215, 383-384. L11: "a file with no pieces fails".
- C32 (parked pair removed): default -> rc=0 with a note; --require-all -> L11.
- C33 (only predicates_parked.md removed): default -> rc=0, and the orphan details file is not linted at all (no L3, no L9).
- A `needs:` into a skipped file is dropped.
The text should name the pilot-mode skip. An orphan details file should fail L3 in either mode.

### CONTRACT-9: "record title" is defined only by code; it misses the real record's `## ` entries and admits any bold paragraph
CONFIRMED. Severity: wrong-verdict in both directions. Effort: small, plus a doc sentence. Blast radius: every L4
citation. pred_doc_lint.py:183-198 accepts a `### ` heading or a `**...**` opener; the text defines no title.
- The real COND-FAMILY.md (review tree) has 53 `### ` and 311 `**` openers, plus two entries under `## ` (l.5, l.15):
  the earliest rulings, which cannot be cited. C12 (fixture title moved to `## `) -> L4 "record title ... not found".
- C17 (a non-entry paragraph `**Note** ...` cited as `(record: "Note")`) -> rc=0.
Fix: state the title shape in doc_format.md and match only that shape.

### CONTRACT-10: checks the code makes with no sentence in the text (each needs a doc_format.md hunk or removal)
CONFIRMED. Severity: doc. Effort: one doc paragraph.
(a) Section headings must be `## <name>   [<file>/<section>]` (l.52, 103-108); any other `## ` in a base file fails
    L2 (C11).
(b) An ISO status date is mandatory on every heading, including `?` (l.278-284; C15 -> L4).
(c) Every piece except `?` needs a statement line, reported as L7 (l.300-302).
(d) EVERY `rulings:` item must cite an existing record title (l.356-371). C13 (a ruled piece with one good and one
    missing title) -> L4, though L4 says "at least one". C14 (a `reading` piece's item with no record) -> L4.
(e) Slugs must be kebab case, under L9 (l.411).
(f) An empty details file fails L11 (l.321).
(g) Duplicate SECTION tags fail L1 (l.236-241).
(h) SUPERSEDED and `rev N` in L6.
(i) `by:` targets must be core/principles/ (l.387): in the template (l.45), so held as a faithful reading.

### CONTRACT-11: piece-body parsing ignores fences, so a fenced `needs:` line is linted as a reference
CONFIRMED. Severity: wrong-verdict (false fail), low. Effort: trivial. pred_doc_lint.py:129-140. L6 exempts fences, but
the body parse does not. C21 (a fenced `needs: core/holes/nowhere` in a piece body) -> L5 "names no piece".

### CONTRACT-12: the statement is the first non-metadata line, not the line after the heading
CONFIRMED. Severity: silent-pass, low. Effort: small. pred_doc_lint.py:133-134. C20 (statement deleted; `needs:` follows
the heading, a definition sentence comes later) -> rc=0: the definition is taken as the statement, and L7's cap is
applied to it. Matters for SCANNING and `--show -l 0`.

### CONTRACT-13: a heading without a status is reported as L2 with cascading L3/L5, never L4
CONFIRMED. Severity: maintenance (rule attribution). Effort: small. pred_doc_lint.py:51, 257-259. C16 -> L2 malformed
heading, L3 "base piece None", an L3 orphan, and L5 "needs: core/holes/class names no piece".

### CONTRACT-14: positive-case coverage of the committed sample
Severity: test-coverage. Effort: small. scripts/tests/pred_doc/root/**. Each rule has a passing case. Absent from the
sample: a 4-word tag (it passes, C38, but is never tested), a `was:` line (selftest only, excuse direction only), an
under-construction piece, a principle piece without an example, and an `evidence:` field. L8 passes only through the
`?` exemption the text does not state (CONTRACT-4). The selftest's per-rule floors (l.699) are hand counts of this same
sample, so they share a source with what they control (learnings §3).

## PROBED-AND-HELD

- L1: tag uniqueness is global across the three base files.
- L2: 3- and 4-word tags pass (C38). Digits pass (C19); the text leaves this open.
- L3: missing, extra and swapped entries are caught (selftest plus a read of the code).
- L4: the status set, `open` without a slug, `parked` outside the parked file (C28), and a ruled piece with no rulings
  are all caught. The same-line `rulings:   - ...` form parses.
- L5: a missing target, a later file, a later-in-file target and a `by:` that is not a principle are all caught.
- L7: 200 characters passes, 201 fails (C24, C37). 40 lines passes, 41 fails (C23, C36). The soft cap only warns.
- L8: the parked, under-construction and principle exemptions match the text (C27). A three-mode statement satisfies
  L8 (C25); acceptable.
- L9: cross-file duplicates are caught. `shared:` in any details file exempts globally (C18; the text allows it).
  A `shared:` below an entry does not exempt (C29), which matches "at the head".
- 39 crafted cases (C01-C39). Clean sample: rc=0, "checks passed 120, failed 0".

CRITIC COMPLETE

