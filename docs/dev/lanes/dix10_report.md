# dix10 — [DOC-INDEX] unit 1.0: decisions census, owner table, per-extent control

Lane dix10 (opus), branch lane/dix10 off main ee25e11b3, 2026-11-10. BUILD GO quoted in the brief
(Frank, 2026-11-10, "Go on build"). Charter: design docs/design/doc_index_format.md rev 3 §2.2, §5.2,
§10; appendix A/B. No rulings file was named in the brief.

## STATE AT HANDOFF

STATE: delivered. Validation COMPLETE (all runs are seconds long). Nothing owed except the items in
"Not built" below.

**Commits on lane/dix10:** 82a0b0e11 (census + table + rulings), the control + toy fixtures commit,
8ce390a5f (runner, CLAUDE.md files, date rules, D76 ruling), and this report.

**Files:**
- `scripts/doc_census.py` — the scan, marker-vs-mention rule, gates (a)/(b)/(c), owner-table
  derivation (extent, extent_hash, label, class, owner, numbering, date, who, title, cites), `--emit`,
  `--check`, `--list`, `--summary`, `--selftest`.
- `docs/dev/doc_index/decisions_owners.tsv` — the owner table, 193 rows, GENERATED (`--emit`).
- `docs/dev/doc_index/decisions_owner_rulings.tsv` — 41 hand rulings (40 id-less markers + 1 date).
- `scripts/doc_control.py` — the per-extent control (clauses i-vi + pre + hash), `--witnesses`
  (converted side), `--witnesses-table` (table side), `--selftest` (plants).
- `tests/doc_lint/run_doc_index.sh` + `tests/doc_lint/fixtures/doc_control/` (toy old file, toy
  rulings, hand-written CORRECT toy conversion) + CLAUDE.md files (tests/doc_lint, fixtures,
  docs/dev/doc_index; one line each in tests/CLAUDE.md, docs/dev/CLAUDE.md, scripts/CLAUDE.md).

**Validation (re-run standalone, the file the section would run: `bash tests/doc_lint/run_doc_index.sh`):**
`checks passed: 5, checks failed: 0, run_doc_index: DONE rc=0` — census selftest; `--check` (table ==
fresh census, 193 markers / 57 mentions / 193 rows / 0 problems); control selftest (every plant red,
toy green); 14 table witnesses hold; the sabotage (D89 rulings flipped to D94) turns the witnesses red.
`scripts/check_claudemd_size.sh --all`: 359 files within limits. Not wired into `make test` (the
design wires the section at T1/unit 1; T1's `make test-doc-lint` may chain run_doc_index.sh).

**Mock converters (scratch, NOT committed: `$PCREC_TMPDIR/scratch/dix10/mockconv.py`) over the real
decisions.md + this table, through `doc_control.py --witnesses`:**

| mock | result |
|---|---|
| correct (follows the table) | 0 failures, every witness green |
| naive (id-less markers owned by POSITION, round 1's faith mock) | 17 failures: (ii) 6, (iii) 2, (iv) 2, (v) 3, (vi) 2, witness 2 (D89 holds only a1; D94 holds D89.a2's text) |
| positional (every marker under its enclosing entry) | 192 failures across (ii)-(vi), 23 witnesses red |

### Counts vs the design (at base ee25e11b3; decisions.md differs from e9687de27 only by D192, no addendum)

| | design (e9687de27) | census here | difference |
|---|---|---|---|
| candidates | 250 | 250 | — |
| markers | 193: h3 71, bold 85, bullet-bold 17, plain 13, h2 7 | 193: same per class | — |
| id-less markers | 40 (23 bold, 17 bullet-bold) | 40 (20 bold + 3 D89 bold ruled, 17 bullet-bold) | — |
| mentions | 57: plain 33, bullet-bold 17, bold 4, bullet 3 | 57: plain 33, bullet-bold 20, bold 4 | the 3 "bullet" lines are numbered-list bold lines (`8. **Bit spelling:**`, `1. **\`-fno-lit-run\` is REQUIRED**`, `1. **Q-R9-1** — resolved by D144 addendum`): the prototype classed `N. **` as bullet, this census as bullet-bold. Same lines, same verdict |
| title rule 1/2/3/4 | 136 / 45 / 7 / 5 | 132 / 53 / 6 / 2 | rule-1 remainder stripping differs at the margin (a label whose remainder is only punctuation goes to rule 2 here); rule 3 now also yields D89.a1 and D94.a1 because a group item that merely CONTAINS a date (`from lane battriage's triage of the 2026-09-15 ...`) is kept and items split at `,`, `;`, ` — `. Untitled: D147.a5, D147.a9 (label + group only, nothing after) |
| undated (inherit) | 28 | 27 + 1 ruled (D76's in D81) = 28 | — |
| outside own region | 46 (36 id-named, 7 own `##`, 3 id-less) | 43 + D106's 3 `## D106 ADDENDUM` | the control's region is "entry heading to the next ENTRY heading", so D106's `##` addenda sit in D106's own region (they are outside only the literal `^## D106` cut) |

### Hand rulings (decisions_owner_rulings.tsv; each reason cites its evidence)

- **D89.a2, a3, a4 (owner_src ruled)**: `**Addendum 2/3/4**` inside D94 continue `### D89 addendum`
  (same exchange, 18:3x/18:4x/18:5x after its 18:2x); src/parse/rxt_compose.c and src/gen/emit_vm.c
  cite `D89 addendum 4(1)`/`4(2)`; 0 cites of `D94 addendum 2-4`.
- **D81.a1 (enclosure, judgment)**: `ADDENDUM 2026-08-28` continues the D40 ADDENDUM paragraph with no
  blank line, but the tree cites the abi reset at 1.0 as `D81 addendum` (plan_completed.md [REL-1.9],
  docs/dev/lanes/rel1pre_facts.md, dev_journal.md), never as D40's. Ruled D81. **Manager: please
  confirm** (the one ruling where text position and cites disagree).
- **D76.a1 date ruled 2026-08-25 (id-named, not an owner ruling)**: `D76 ADDENDUM — abi 3→4` sits in
  D81 (2026-08-25); the design's inherit rule would give it D76 addendum 2's 2026-10-09. With the true
  date the default numbering makes IT D76.a1 and D76's own unnumbered addendum (2026-09-19) D76.a3.
  No numbered cite names either (16 bare `D76 addendum` cites resolve to both). **Manager: confirm the
  date ruling and the resulting numbering.**
- **D47.a3, a4**: `RULING-5 ADDENDUM` ×2 inside D47, amending D47's ruling 5.
- **D155.a4.1, D166.a1.1**: directly after `### D155 addendum 4` / `### D166 addendum 1`; 14 / 13 cites.
- **D136.a1**: comparison (A) is test-recursion-identity, D136 item 2; plan.md cites "D136; [RECID-A]".
- **D120.a1, D138.a1, D150.a1, D185.a1**: no tree cite; owned by text (Patfacts = D120's record; Q1 of
  D138's Q1-Q4; ARTREV's reviewers; the kit in D185's one stream).
- The other 27 (D26 ×2, D37 ×2, D60, D83, D84 ×3, D93, D114, D118, D119 ×3, D146, D163 ×3, D169,
  D172, D178, D186 ×2, D187, D188 ×2): inside their own entry after its body, with the tree-cite count
  of `Dh addendum[ n]` in the reason.

No marker inside a foreign entry has host text resuming after it, so no `old_end` ruling exists
(checked paragraph by paragraph over all 43 foreign-region extents).

### Plants (doc_control.py --selftest; toy original + hand-written correct conversion)

Correct toy conversion: GREEN (0 failures). Every plant RED by its named clause; clauses that fired:

| plant | wrong conversion | design's clause | fired |
|---|---|---|---|
| P1 | addendum under the wrong owner | (ii),(iii) | ii, vi |
| P2 | body line moved to another entry | (iii) | iii, vi |
| P3 | first line of an addendum moved to the next | (iii), extent_hash | iii |
| P3b | non-first lines moved between two addenda | (iii) | iii |
| P4 | addendum line moved into its owner's body | (iii) | iii |
| P5 | line dropped | (iii) | iii, vi |
| P6 | line duplicated | (iii) | iii, vi |
| P7 | fence dropped + fence duplicated (multiset-neutral) | (iii) | iii |
| P8 | body heading dropped | (iii) | iii, vi |
| P9 | body heading moved to another entry | (iii) | iii, vi |
| P10 | entry title rewritten | (iv) | iv |
| P11 | D98's join applied to another heading | (iii),(iv) | iii, iv, vi |
| P12 | body line rewritten into `(was:)` | (iii),(v) | iii, v, vi |
| P13 | body line rewritten into `rulings:` | (iii),(v) | iii, v, vi |
| P14 | blank line dropped | (iii) | iii |
| P15 | two lines reordered | (iii) | iii |
| P16 | addendum heading date differs from the table | (iv), C3 | iv (C3 is doc_lint's, unit 1) |
| P17 | invented `### D2.a1` inside a body | (ii) | ii, iii |
| P17b | real addendum split by an invented `### D3.a4` | (ii),(iii) | ii, iii |
| P18 | extra `(was:)` with a false label | (v) | iii, v |
| P19 | `rulings:` block in unit 1 | (v) | iii, v, vi |
| P20 | (census) plain-line `D122 ADDENDUM 4` inside D123 | gate (b) | doc_census --selftest: row owner D122; gate (b) red and `--check` "marker with no table row" when the row is deleted |
| P21 | one-line addendum (next marker directly after) moved | (iii), extent_hash | iii |
| extra P3h | stale `extent_hash` in the table | — | hash |
| extra Pi | an id missing from the index | (i) | i |
| extra Ppre | the old preamble dropped | — | pre |

P3/P21's "extent_hash" half: see DEVIATION 6. No plant was missed; no STOP condition hit.

### Witnesses

Table side (`doc_control.py --witnesses-table`, in run_doc_index.sh), all 14 hold: D47 (a1-a4: two
h2, two bold RULING-5, a4 = LANDED NOTE), D89 in D94 (a1 label, a2-a4 ruled), D122 (a1-a4, plain;
a4 in D123), D123 (a1-a8 + a3a, plain; a8 in D124), D162 a4 (a4 + a5 "second of two", both
old_number 4), D155 a4.1, D166 a1.1, D58 (two h2: in D96's and D154's regions), D84 (- / 2 / 3 →
a1-a3), D147 (a1 = the unnumbered one, a2-a16 incl. those in D149/D155/D159), D45 (second/third/
fourth → a2/a3/a4), D168 (two notes `D168.a3#1/#2`), D163 (a1-a12, a8-a12 in D167), D26 (three
unnumbered → a1-a3 by date, a3 h3). Converted side (`--witnesses`): the same list plus "holds none
of it" for D48, D94, D123, D124, D167, D96, D154, D149, D155, D159; the correct mock is green, the
naive mock red on D89. `entry 'D162 addendum 4'` printing both is the accessor's (T1/unit 1).

### DEVIATIONS and interpretations (for review)

1. DEVIATION: hand rulings live in their own committed input `decisions_owner_rulings.tsv` (keyed by
   host entry + exact old label); the table's `note` column carries each ruling's reason, so the
   table is fully regenerable. Rulings carry overrides `number`, `old_end` (`lines:N`), `title` and
   a `date` column the design does not list (used once, D76). An unused ruling fails `--check`.
2. Interpretation: (iii)'s "text between its `## ` heading and its first `###`" is read as the first
   `### Dn.a` heading; body headings like D30's `### 1. ...` stay body text.
3. Interpretation: an entry's region runs from its heading to the next ENTRY heading (`## Dn
   ADDENDUM` lines are markers, not entries), so a `## D58 ADDENDUM` section lies in its host's
   region and its extent is subtracted there.
4. Interpretation: the body's runs between subtracted extents are each trimmed and joined with ONE
   blank line (no host text resumes after a foreign extent today, so this only matters later).
5. Addition: clause (pre) — every non-blank old preamble line must survive in the index or details
   preamble (the design names no home for decisions.md's three-line header).
6. DEVIATION: `extent_hash` is checked as clause (hash): the table's hash must still describe the old
   file (a stale table is refused). A converted heading-form addendum cannot be re-hashed (its marker
   line became a heading + `(was:)`), so P3/P21 go red by (iii) only; the hash is also the
   converter's row-match key (`old_label` + `extent_hash`).
7. Interpretation: an undated marker with no earlier dated marker of its owner inherits the owner
   ENTRY's heading date (D60.a1 2026-08-18, D38.a1, D39-D44's `same session`); a date right after the
   label outside any group (`D11 addendum — 2026-08-09 (...)`, D13, D31) is the marker's date.
8. Interpretation: `who` is read from the group's first two items even when the item also holds a date
   (`build go, Frank 2026-10-21` → Frank).
9. Interpretation: a duplicate's "next free number" is the lowest free number: D162's second a4 is
   D162.a5 (appendix B's `D162.a13` reads as illustrative; D162 has a1-a4 only).
10. Note rows render as `#### <old_label verbatim>` with no `(was:)` line.
11. `--check` matches rows by (`old_label`, `extent_hash`): an EDITED extent on main re-emits as a
    changed row (visible in the diff), so the table "only appends" for appended markers, not for edits.
12. `cites` is a plain `git grep` count of `Dn [ordinal ]addendum|ADDENDUM|add.[ k]` and
    `addendum k of Dn` per (owner, old_number), excluding decisions.md and docs/dev/doc_index/; all
    unnumbered markers of an owner share one count. Informational; not resolver-grade.

### Not built (OWED, outside this brief's numbered list)

- `scripts/doc_cites.py` (resolver + `--inbound`) and `docs/dev/doc_index/dangling_before.tsv`:
  the §5 table lists them under 1.0, the brief's task list does not. A follow-up lane builds them
  over this table (owner + old_number + date are the alias keys).

### Merge notes

- dixt1 (T1) also creates tests/doc_lint/ and edits scripts/CLAUDE.md, docs/dev/CLAUDE.md,
  tests/CLAUDE.md: expect add/add on tests/doc_lint/CLAUDE.md and line conflicts in the three
  CLAUDE.md files (keep both lists). scripts/CLAUDE.md is at 4092 B: this lane shortened line 1
  ("Process tooling, ...") to fit its one addition on the Checkers line. Told dixt1 by message.
- docs/dev/decisions.md is untouched. The table is pinned to decisions.md's line numbers: a merge to
  main that edits decisions.md before unit 1 needs `python3 -I scripts/doc_census.py --emit` (then
  `--check`), the landing re-run of §5.2.
