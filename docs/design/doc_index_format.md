# One format for ruling and tracker files: a tight index plus greppable details (rev 1)

**Rev 1 (lane docfmt1, 2026-11-10):** the owner's six answers applied (§7):
opus statement writers and a fresh opus critic, no owner read-through; a
LEVELED accessor (`scripts/entry`, §2.3) with item grep and a work-choosing
view, levels declared in the profile table; SOFT size caps (linter warns,
`scripts/gestalt` prints one line per index over its cap); known issues as
the third file; a kit-facing proposal (§8) to send once this is vetted;
accessor + gestalt line are the FIRST tooling unit; D47's four addenda are
unit 1's acceptance test.

Lane docfmt, 2026-11-10. DESIGN ONLY: nothing here converts a real file.
Owner's ask (Frank, 2026-11-10): decisions and plan should each be a short
"simple statement" file that covers most cases and is easy to recall, plus a
details file from which one entry is easy to grep out by its slug; formalize
the shared format; say which other files fit. The consumer is the AI manager
session, which keeps the index in context, and its lanes, which read details
on demand through the accessor.

## 0. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the manager holds every ruling's CURRENT form in context | manager, owner | decisions index under its 48 KB soft cap (today the only whole-file form is 832 KB), every D-id present |
| G2 | one command prints exactly one entry, at the level asked for | manager, lanes | `scripts/entry D47` prints D47 with all four addenda and nothing else; 0 addenda outside their entry (17 today, §1.1) |
| G3 | one format, one linter, one accessor for every tracker that fits | maintainers | one linter (plan_lint folded in), one accessor; per-file differences are rows in ONE profile table (§2.4) |
| G4 | no citation breaks | everyone | every `Dn`, `Dn add. k`, `[TAG]`, `Kn` cite resolves after migration; 0 ids renumbered |
| G5 | an index statement never says more or other than its details | owner | 100% of statements pass a fresh opus critic (§5) |

Priority on conflict: G4 > G5 > G1 > G2 > G3. Non-goals: rewriting details
text; changing what a decision says; append-only journals and logs (§4).

## 1. Census

Sizes are bytes at main 6638e3679. "Entries" counts the file's own heading
form. Size spread is per entry.

### 1.1 Candidate files

| file | bytes | entries | entry heading | size median / p90 / max | parsed by |
|---|---|---|---|---|---|
| docs/dev/decisions.md | 832,382 | 191 ids, 198 `## D` headings | `## Dn — title (date, who)` | 2,834 / 9,279 / 36,010 (D29) | tests/memfn/rows_check.py (§1.2) |
| docs/dev/plan.md | 467,976 | 339 rows (296 not-started, 36 started, 2 blocked, 5 deferred) | `- [TAG] STATE:s — title` + 2-space attribute lines (`filed:` 308, `refs:` 292, `next:` 161, `trigger:` 138, `status (date):`) | 1,090 / 2,490 / 4,969 | scripts/plan_lint.py (PL1-PL15), pre-commit |
| docs/design/plan_row_bodies/ | 22 files, 177 KB | 1 file per row | file named `TAG.md` | 1.0-28 KB | plan_lint PL15 |
| docs/dev/plan_completed.md | 1,212,690 | 380 `STATE:completed` rows under date headings | same as plan.md | archive | plan_lint (moved-row check) |
| docs/dev/known_issues.md | 466,753 | 139 (`## Kn — STATE ... — title`; 71 FIXED, 42 OPEN, 7 CLOSED, 3 ACCEPTED, rest unmarked); bodies use `**Witness:**`, `**Fix:**` labels | `## Kn` | 2,443 / 6,655 / 19,008 | none (cited by K-number from ~70 tests) |
| docs/dev/upstream_issues.md | 70,369 | 25 `## Un` | `## Un — engine: title` | small | none |
| memfn/docs/requests.md | 92,851 | 38 `## R-n` (main's single-writer file) | `## R-n (date, who) — title` | — | post_compact.sh names it |
| memfn/docs/responses.md | 300,327 | 16 `## R-n`/`## N-n` + `###` notices (kit's file) | `## R-n — title` | — | rows_check.py LEDGERS |
| docs/dev/learnings.md | 41,996 | numbered sections §1-§6, §3.a-§3.ac | `## n.` / `### 3.x` | — | none |
| docs/testing.md | 344,067 | ~50 topical sections | `## The ...` | — | none |
| docs/dev/dev_journal.md | 1,886,739 | 448 dated entries, append-only | `## date` | tail-read | known_fail, test_trailer (append) |
| docs/dev/full_suite_ledger.md | 50,678 | landing lines | prose lines | — | queuemon, fullsuite_job.sh |
| memfn/docs/ideas.md | 54,470 | 28 dated raw notes, append-only | `## date — note` | — | none |
| REFERENCES.md | 41,510 | 55 `### [Key]` | `### [Key] authors (year)` | small | none |

Decisions shape, measured: 54 of 191 entries carry addenda, in SIX
spellings (70 `### Dn addendum[ k]`, 17 `- **Addendum`, 15 `**Addendum`,
6 `**ADDENDUM`, 6 separate `## Dn ADDENDUM` top-level headings, 1
`## Dn SECOND ADDENDUM`); 61 are numbered, the rest are not. 17 addenda
sit inside a LATER entry (D163's inside D167 five times, D94's inside D112,
D161's inside D162, ...), and D47's two load-bearing addenda are top-level
headings after D48, so reading `## D47` alone today misses part of D47's
current ruling. Supersession is prose (10 "SUPERSEDED" marks, no field).
Citations: ~4,800 `Dn` tokens in src/tests/scripts/lib/cli, 2,708
`Dn add. k`/`Dn addendum k` cites tree-wide: ids AND addendum numbers are
load-bearing.

Plan shape: the head lines alone total 35,289 B (median 108 B); everything
else in the row (filed, status, next/trigger, refs, charter) is 430 KB.

### 1.2 Who reads what, and how

| reader | file | how |
|---|---|---|
| scripts/plan_lint.py (+ .sh, tests/plan_lint/, Makefile `test-plan-lint`, pre-commit) | plan.md, plan_completed.md, plan_row_bodies/ | full parse: row grammar, sections, caps (title 100, status/next 300, line 1000, row 12 lines / 6000 B), PL15 body pointers, PL14 no `plan.md:N` cites, row floor 150 (K35) |
| tests/memfn/rows_check.py `support_faults` | decisions.md, memfn/docs/responses.md | cuts `^## Dn\b.*?(?=^## D[0-9]\|\Z)`, requires the quoted ruling sentence inside it |
| tests/memfn/stream_support.tsv | decisions.md | rows carry `"sentence" @ docs/dev/decisions.md D190` |
| scripts/boxqueue header | plan_row_bodies/BOXQUEUE.md | comment pointer |
| scripts/hooks/post_compact.sh | owner.md, wake.md, memfn wake | injects owner.md + wake.md (≤5,000 chars); kit role told to read requests/responses |
| .claude/skills pcrec-manager, q, pcrec-critic, pcrec-memfn-manager | plan.md, decisions.md, ledgers | `grep -n "STATE:started"`; write rulings; freeze commits; `grep -n '^- \[TAG\]'`; open items at wake |
| root CLAUDE.md, docs/dev/CLAUDE.md, ~57 CLAUDE.md files | all | prose pointers ("decisions.md D26") |
| tests, src comments | all | cite ids only; no parse |

How the manager looks things up today: `grep -n` on STATE tags for the plan;
for a ruling, a grep for `^## D26` and a Read of a line range, which misses
misplaced addenda and costs 3-36 KB per entry. Nothing gives "the current
ruling in one line", and nothing gives "every not-started row with its
trigger" short of reading the 468 KB file.

### 1.3 Files a session loads at start

root CLAUDE.md 17,876 B (auto, cap 20 KB); ~/.claude/CLAUDE.md 1,175;
MEMORY.md 23,494 (manager and every lane); owner.md 5,430 (post_compact);
wake.md 22,115 (5,000 injected, skill says read in full); pcrec-manager
SKILL.md 14,919; journal tail and plan greps, variable; lanes add
BOILERPLATE.md 10,872 (+ RUNS.md 15,564 on trigger). Today's always-on
manager load is ~85 KB. The two proposed indexes add ~80 KB (§3): the price
of G1, held by soft caps.

## 2. The format

A file that adopts it is a PAIR:

- the INDEX keeps the file's current name (decisions.md, plan.md,
  known_issues.md), so every prose pointer ("decisions.md D26") still lands;
- the DETAILS file is `<name>_details.md` beside it, ONE details file per
  index. Why one (owner's answer 2: our call, since access goes through the
  accessor): the accessor hides the split from readers either way, and one
  file keeps whole-details grep, the bijection check and the converter to
  one parse, instead of ~700 small files each listed in a directory guide.
  Details are read one entry at a time, never whole.

### 2.1 Index entry

One line per entry (plan rows: one line, or two for started/blocked rows).

    - <ID> <slug> <state>[ a<k>] — <statement>[ (+<n> more)][ {<keywords>}]

| field | rule | why |
|---|---|---|
| ID | existing id, never renumbered (`D26`, `K139`, `U22`; plan keeps `[TAG]`) | G4: ~7,500 cites |
| slug | kebab-case, 2-4 words, ≤ 28 chars, unique in the file; the plan's `[TAG]` IS its slug | a recall handle that survives a renamed title; `entry` takes it |
| state | decisions: `live`, `sup>Dm` (wholly superseded), `part>Dm` (partly; the statement is the live remainder), `retired`, `absorbed>WHERE` (the rule now lives in CLAUDE.md/spec/skill). Known issues: `OPEN`, `FIXED`, `CLOSED`, `ACCEPTED`. Plan: `STATE:<s>` as today, so the skills' greps keep working | supersession becomes a field, not prose |
| a<k> | number of addenda in the details entry; the linter checks it equals the count of `### ID.aN` headings | an addendum FORCES a touch of the index line, the moment to rewrite the statement (G5) |
| statement | ONE sentence, ≤ 200 chars, present tense, the CURRENT ruling with every addendum applied. Shape: `<topic>: <rule>[; <rule>...].`, topic ≤ 4 words. No rationale, dates, history or lane names | what a session pattern-matches when about to act; 200 chars keeps 191 entries near 38 KB |
| (+n more) | count of rulings the statement left out | compression allowed, silent omission not; the critic checks n |
| keywords | optional, ≤ 40 chars, only words absent from slug and statement | grep recall for words the sentence did not need |

Superseded, retired and absorbed entries shrink to ≤ 80 chars naming what
replaced them: the index then grows by live rulings, not by history.

Plan rows keep their head line (title cap 100 → 90) and gain ONE second line
only when started or blocked:

    - [TAG] STATE:<s> — <title ≤ 90>
      now (<ISO date>): <≤ 160 chars: where it stands and the next step>

`now` is the status of record, rewritten in place, REQUIRED on started and
blocked rows and FORBIDDEN elsewhere, so the index cannot creep. A
not-started row's next step or trigger stays OUT of the index (owner's
answer 3) and the accessor supplies it on demand at level 1 (§2.3).
Children stay nested by two spaces. Sections (Active, Candidates, Backlog,
Boonies, Deferred) stay. The Policy section shrinks to a pointer at the
format document (§2.6).

### 2.2 Details entry

    ## <ID> <slug> — <original title, verbatim> (<original date, who>)
    <body, verbatim>
    ### <ID>.a1 — <date, who>: <addendum title>
    <addendum body, verbatim>

- An entry runs from its `## ` heading to the next `## ` heading. Body text
  never uses a level-2 heading (today's six `## Dn ADDENDUM` headings become
  `### Dn.ak`).
- Addenda live INSIDE their entry, in date order. An addendum already
  numbered keeps its number ("D163 add. 7" stays `D163.a7`); an unnumbered
  one takes the lowest free number in date order and keeps its old label on
  its first line (`(was: "D26 addendum (owner, 2026-11-06)")`) so a grep for
  the old wording still lands.
- Plan details hold what leaves the row: `filed:`, `next:`/`trigger:`
  (required for not-started, blocked, deferred), `refs:`, the charter, dated
  history. These attribute lines keep today's spelling, so the accessor's
  level-1 fields read the same names before and after the split.
  plan_row_bodies/ files fold in verbatim as their row's details body.
- Cross-links are bare ids (`D26`, `[ANCH-AT]`, `K139`, `R-38`, `D163.a7`),
  never markdown links or line numbers.

### 2.3 The accessor: `scripts/entry`, by level

python3 stdlib, run `-I`; it reads the profile table (§2.4), so a new file
or a new level is a table row, not code. Three LEVELS, defined per profile
in the table:

| level | content | decisions | plan | known issues |
|---|---|---|---|---|
| 0 | the index line(s) | the line | head line (+ `now`), with child head lines | the line |
| 1 | level 0 + the WORKING FIELDS | + every `### Dn.ak` addendum heading (the addenda titles) | + `next:`, `trigger:`, `status (date):` / `now`, `refs:` lines | + the first line of each `**Witness:**` / `**Fix:**` paragraph, cut at 240 chars |
| 2 | level 0 + the full details entry with all addenda | whole entry | whole entry (charter, history) | whole entry |

Commands:

    scripts/entry ID|slug [-l N]          one item; default level 2
    scripts/entry ID.aN                   index line + that one addendum
    scripts/entry -g REGEX [-in N] [-l N] [-p PROFILE] [-s SECTION] [--state S]
    scripts/entry --work [-p PROFILE] [-s SECTION] [-k WORD]
    scripts/entry --levels [-p PROFILE]   print the level and work-view rows of the table
    scripts/entry --over-cap              soft-cap lines for scripts/gestalt (§2.4)

- **Item grep** (`-g`): searches each item's text AT level `-in` (0 = index
  lines only, the default; 1 = index + working fields; 2 = index + full
  details) and prints every matching ITEM WHOLE at level `-l` (default:
  the search level). Items, never raw lines: a hit deep in D47's third
  addendum prints D47, not one stranded line. `-s` restricts to an index
  section, `--state` to a state (`live`, `STATE:not-started`, `OPEN`).
- **Work view** (`--work`): the profile's declared view (§2.4): plan = every
  `STATE:not-started` and `STATE:blocked` row at level 1, i.e. its head line
  with its trigger/next and refs, grouped by section; known = every `OPEN`
  entry at level 1. `-s` and `-k` (a keyword, matched at level 1) narrow it.
  This is the "choose the next piece of work" read the index alone cannot
  give once triggers leave it.
- Output ends with one trailer line, `entry: <n> items (profile <p>,
  level <l>)`; exit 0 found, 1 none, 2 ambiguous slug. The id prefix picks
  the profile (`D`, `K`, `U`, bracketless TAG = plan); a finished plan tag
  falls through to plan_completed.md.
- With no tool, one line still prints one entry:

      awk '/^## /{p=($2=="D26"||$3=="pcre2-compat-tiers")} p' docs/dev/decisions_details.md

rows_check.py's existing cut (`^## D190\b ... (?=^## D[0-9]|\Z)`) works
unchanged on the details file and becomes correct for the 17 misplaced
addenda once they sit inside their entry.

### 2.4 One profile table, one linter: plan_lint becomes doc_lint

The PROFILES table is one declared module, `scripts/doc_profiles.py`, read
by both the accessor and the linter (one source; first-match rows per file
pair):

| profile | index / details | id | states | soft cap: statement / line / FILE | level-1 fields | work view | form |
|---|---|---|---|---|---|---|---|
| decisions | decisions.md / decisions_details.md | `D[0-9]+` | live sup part retired absorbed | 200 / 300 / 48 KB | `### ID.aN` headings | — | dormant until unit 1 |
| plan | plan.md / plan_details.md | `[TAG]` | the four STATEs | title 90, now 160 / 2 lines / 48 KB | `next:` `trigger:` `status (…):` `now` `refs:` | not-started + blocked, L1, by section | `single` (today's file) until unit 2, then `pair` |
| known | known_issues.md / known_issues_details.md | `K[0-9]+` | OPEN FIXED CLOSED ACCEPTED | 180 / 280 / 32 KB | `**Witness:**` `**Fix:**` first lines | OPEN, L1 | dormant until unit 3 |
| upstream | upstream_issues.md / upstream_issues_details.md | `U[0-9]+[a-z]?` | OPEN FILED FIXED-UPSTREAM CLOSED | 180 / 280 / 12 KB | set by unit 4's census | OPEN, L1 | dormant until unit 4 |

The `single` form is the plan profile read in TODAY's shape: its level-1
fields are already the row's own attribute lines, so the accessor and the
work view are useful before any split. It is deleted at unit 2
(implement-then-replace, not a second permanent mechanism).

**Soft caps (owner's answer 4: soft now, revisit later).** A FILE cap never
fails anything: doc_lint prints `WARN C4 <file> ...` and exits 0, and
`scripts/gestalt` (the heartbeat status) gets ONE line per index file that is
over its cap, nothing otherwise. Gestalt runs `timeout 5 python3 -I
scripts/entry --over-cap`, which prints, for `pair`-form profiles only:

    docs: <index file> <size> KB over soft cap <cap> KB (+<excess> KB, <pct>%)
    docs: decisions.md 51.3 KB over soft cap 48 KB (+3.3 KB, 107%)

KB = 1024 B, one decimal; pct = size / cap, rounded down. A non-zero exit or
a timeout prints `docs: unavailable` (a check that cannot run must not read
as "under cap", K35). Silent when every index is under its cap. The per-LINE
caps (statement, title, now) are the open question in §7.

Common rules (each FAILS, except the file cap):

- C1 ids unique in the index; C2 bijection: every index id has exactly one
  details heading and every heading one index entry; C3 heading grammar
  (§2.1, §2.2); C4 field caps (fail) and file cap (WARN only); C5 slug
  kebab, ≤ 28, unique; C6 every `### ID.aN` lies inside `## ID`, numbers
  unique and rising; C7 every id cited in an index line resolves; C8 no
  `<file>.md:<line>` cite of any profile's file anywhere in the tree (PL14
  generalized); C9 a parsed-entry floor per profile (K35); C10 no level-2
  heading inside a details body.
- `--selftest` plants one violation per rule per profile, plus one over-cap
  file that must WARN and exit 0; `--staged` lints staged index content as
  now; `--stale` (exit 0) prints headroom under each file cap and the count
  of `?` statements left (§5).
- Readers kept whole: `plan_lint.sh` becomes `doc_lint.sh [profile]`;
  `test-plan-lint` becomes `test-doc-lint` with every reader (Makefile,
  pre-commit glob, tests/plan_lint/ → tests/doc_lint/, docs/testing.md,
  skills) moved in the same unit.

### 2.5 Worked examples (real entries; bytes measured)

**Decisions index** (statement bytes 198 / 189 / 173):

    - D26 pcre2-compat-tiers live a3 — PCRE2 compatibility: matching and syntax recognition are exact; accept all PCRE2 accepts (more allowed); follow the standard over an evidenced PCRE2 bug; never chase unimplemented-construct wording. {diagnostics floor 10.46}
    - D47 brep-counterk live a4 — Bounded repeats: possessify, then rung select, then counter-K; K is one per-artifact named constant (8) in v1, never per quantifier; frameless forward work has its own bound and error code. (+3 more) {ENG-BREP}
    - D191 span-arms-go live — Span arms: build E1 R1 E2 L1 L3 (L2 after kit R-38); a run crosses as one uncut span of byte sets at signed offsets; repeats count as copies; zero-width items do not cut it. (+3 more)

Lines: 262, 243, 213 B (against 9,723 / 12,811 / 1,815 B of details).

**Decisions details headings** (bodies verbatim, not shown):

    ## D26 pcre2-compat-tiers — FUNCTIONAL compatibility with PCRE2, not bit-exact compatibility: effort tiers by distance from the core (2026-08-10)
    ### D26.a1 — 2026-08-11, DOC-1: which PCRE2 (the pinned oracle, 10.46)
    ### D26.a2 — Frank, 2026-10-24: compatible with PCRE2 unless PCRE2 has a bug
    ### D26.a3 — owner, 2026-11-06: the accept set is a FLOOR, not a ceiling
    (was: "D26 addendum (owner, 2026-11-06)")

    ## D47 brep-counterk — the six [ENG-BREP] §9 rulings (Frank, 2026-08-16, twenty-fourth session continuation)
    ### D47.a1 — Frank, 2026-08-16: F-1 ruled: K does NOT vary per-quantifier in v1; the clamp is DEFERRED to its own row
    (was: the top-level heading "D47 ADDENDUM")
    ### D47.a2 — Frank, 2026-08-17: F-2 ruled: the uncharged forward work gets its OWN bound (settlement 4); a pre-release ABI rider
    (was: "D47 SECOND ADDENDUM")
    ### D47.a3 — 2026-08-18: RULING-5 ADDENDUM (from the R30 ...)
    ### D47.a4 — 2026-08-19: RULING-5 ADDENDUM, LANDED NOTE

D47 is the hard case: two addenda that were top-level headings after D48
(a `^## D47\b` cut today misses the two rulings that changed K and the work
bound) and two unnumbered inline ones, all four numbered in date order.
`scripts/entry D47 -l 1` prints the index line and these four `###` lines.

**Plan index** (three states):

    - [OPT-REVEND] STATE:started — reverse-from-end search for end-anchored patterns
      now (2026-10-26): B3 match-end mark landed (abi 78); stage 3 waits for a bench cell in the anc-tail family
    - [ANCH-AT] STATE:blocked — one anchored DFA run where the start is known (F-11: 328 _match bodies)
      now (2026-11-06): scheduled by Frank; starts once lookbehind stage 1 and the alternation build land
      - [XARCH-TOKERR] STATE:not-started — an unknown CPU token's refusal is cut at 256 bytes mid-text

Index bytes: OPT-REVEND 192 (row today 4,224), ANCH-AT 204 (today 919),
XARCH-TOKERR 101 (today 636).

**Plan at level 1** (`scripts/entry --work -k token`, one item shown):

    - [XARCH-TOKERR] STATE:not-started — an unknown CPU token's refusal is cut at 256 bytes mid-text
      next: size the joined refusal (or show the kit's target and family refusals separately) so cli.md §1.24¶2's "the kit's text unchanged" holds for any token length
      refs: src/gen/memfn_targets.c add_list; docs/spec/cli.md §1.24
    entry: 1 items (profile plan, level 1)

Level 2 adds its `filed:` line and body (575 B). ANCH-AT's details carry
filed, trigger, refs and its charter; its old `status (2026-11-06)` line
becomes the first dated history line.

### 2.6 Where the format is defined

The format (this section's rules, without census or migration) moves to
`docs/dev/doc_format.md` in the first tooling unit: the one definition the
profile module's docstring and every index header point at. plan.md's
Policy section shrinks to that pointer plus the plan-only rules (sections,
queue discipline).

### 2.7 Writing an entry from now on

A new ruling = the details entry + the index line, in one commit (C2 refuses
one without the other). An addendum = the `### ID.aN` block + the `a<k>`
bump, with the statement rewritten if the ruling moved. Statements are
written by an opus session (owner's answer 1): the manager itself when it
records a ruling, an opus lane in a batch. The q and pcrec-manager skills'
"write the ruling" steps name both files.

## 3. Size targets

Measured basis: the worked examples (decisions lines 213-262 B, all
multi-ruling, so above typical); today's decisions headings average 155 B,
plan head lines 104 B (all 191 / 339 measured).

| index | entries | per entry | projected | soft cap |
|---|---|---|---|---|
| decisions.md | 191 live today | 190-200 B typical, 240 B if all were like the examples; superseded ≤ 100 B | 36-46 KB, central 38 KB | 48 KB |
| plan.md | 339 rows; 38 with a `now` line | head ~100 B; now ~120 B | ≈ 40 KB | 48 KB |
| known_issues.md | 139 | ~180 B | 25 KB | 32 KB |
| upstream_issues.md | 25 | ~170 B | 4 KB | 12 KB |

Why 48 KB: at ~4 bytes per token (an estimate, not a tokenizer count) the
two main indexes are ~20k tokens beside ~21k already always-on (§1.3); the
manager's reset rule fires at 35% context, so this leaves most of the window
for the work. Decisions grew 45 entries in 34 days (D146 on 10-05 to D191 on
11-08), about +8 KB a month, so the decisions soft cap is reached in roughly
1-2 months unless superseded entries shrink. Then gestalt prints its line
every heartbeat and the owner revisits the cap (answer 4). Lanes do NOT load
the indexes; they call `scripts/entry`.

## 4. Other files

| file | verdict | reason |
|---|---|---|
| known_issues.md | APPLY, unit 3 | same shape as decisions; 467 KB nobody can hold; symptom-in-one-line recall prevents re-filing |
| upstream_issues.md | APPLY (small, last) | same shape, 25 entries; nearly free once the tool exists |
| plan_completed.md | PARTIAL | stays the archive: a finished row's index line(s) and details entry move there verbatim under the date heading; no index of its own; `entry` falls through to it |
| docs/design/plan_row_bodies/ | ABSORBED | its 22 files become plan_details.md entries; the directory and PL15 retire |
| memfn/docs/requests.md, responses.md | PROPOSAL TO THE KIT (§8) | the kit adopts it or not; main sends §8 once this design is vetted |
| memfn/docs/ideas.md | DO NOT APPLY | append-only raw log, evaluated later by design |
| docs/dev/learnings.md | DO NOT APPLY (now) | 42 KB of doctrine cited by section number; already the summary tier |
| docs/testing.md | DO NOT APPLY | a handbook cited by section name, not a tracker of ids |
| dev_journal.md, full_suite_ledger.md | DO NOT APPLY | append-only; value is order; scripts append and grep |
| REFERENCES.md | DO NOT APPLY | one heading + one citation each; its own index |
| wake.md, owner.md, memfn wake | DO NOT APPLY | rewritten whole each session |
| MEMORY.md | already this format | one line per fact, detail in its own file: the model for this one |

## 5. Migration plan

Every split is a re-runnable TRANSFORM, not a hand-made diff: the lane
delivers a converter plus its output, and the landing re-runs the converter
on main HEAD before committing (decisions.md and plan.md are written by
nearly every landing; a re-run never conflicts). The converter accepts a
MIXED file (old-form entries appended after conversion are converted on the
next run), so in-flight branches need only a re-run.

| unit | what | tier | readers moved in the same unit |
|---|---|---|---|
| T1 (first) | `scripts/doc_profiles.py` (the §2.4 table: ids, states, soft caps, levels, work views, form), `scripts/entry` (levels, item grep, work view, `--over-cap`), the gestalt `docs:` line, `docs/dev/doc_format.md`. Plan profile in `single` form, others dormant: `entry --work` works on today's plan.md | sonnet | scripts/CLAUDE.md, scripts/gestalt header; root CLAUDE.md situation row ("about to look up a ruling or row, or choose work → `scripts/entry`") |
| T2 | `scripts/doc_lint.py`: plan_lint folded in as the plan profile (PL rules and plants unchanged in effect), C1-C10, file caps WARN only | sonnet | Makefile target rename, pre-commit, tests/plan_lint → tests/doc_lint, docs/testing.md |
| 1 | decisions split by converter: details verbatim with new headings, addenda folded into their entries and numbered (§2.2), index with PROVISIONAL statements = the old title, state `?`. ACCEPTANCE: `scripts/entry D47` prints D47.a1-a4 and no D48 text; C6 finds 0 addenda outside their entry (17 before); the converter's counts match the original's (§5.1) | sonnet (mechanical) | rows_check.py LEDGERS + stream_support.tsv paths; skills q, pcrec-manager, pcrec-critic (freeze both files), pcrec-memfn-manager; root CLAUDE.md "Where things are"; docs/dev/CLAUDE.md |
| 1.S1-S8 | decisions statements, 8 batches of 24 ids in id order | OPUS writer + fresh OPUS critic, 100% | none (index lines only) |
| 2 | plan split by converter: details file, plan_row_bodies/ folded in, `now` provisional = today's status line, title cap 90 applied as `?`; plan profile flips to `pair`, the `single` form is deleted | sonnet (mechanical) | boxqueue comment; skills' plan recipes; plan_completed move rule |
| 2.S | the 38 `now` lines and over-cap titles | OPUS writer + OPUS critic, 100% | none |
| 3 | known_issues split, then 6 statement batches of 24 | converter sonnet; statements OPUS + OPUS critic | the known_fail instructions text |
| 4 | upstream_issues, one unit | converter sonnet; statements OPUS + critic | none |
| K | main sends §8 to the kit for feedback, once this design has passed its critic round | manager | none; the kit decides its own adoption |

Faithfulness (G5; owner's answer 1). Every one-sentence statement (decisions,
plan `now`, known/upstream) is written by an OPUS lane that reads the WHOLE
details entry, addenda included, and never takes the old title as the source
(titles state the first ruling, not the current one). A FRESH opus critic,
one per batch, reads each details entry and its statement and answers four
questions per entry: does the statement add a ruling the details do not
make; contradict the current ruling; state a rule an addendum replaced; or
omit a ruling without counting it in `(+n more)`? 100% of every batch (24
entries × ~4 KB is one critic's reading). Disputes go to the manager. The
owner's read-through is not required. The `?` count is a ratchet: `--stale`
reports it and the linter refuses an increase once unit 1 lands.

Order: T1 → T2 → 1 → 1.S (2-3 batches at a time; disjoint lines) → 2 → 2.S
→ 3 → 4. K runs beside them once vetted.

Freeze: NO merges to main from 2026-11-11 01:00 until the full suite ends
(about 14:00). T1 may land before 01:00 only if ready and light; the two big
transforms (1 and 2) land at a quiet point after the suite, with no other
lane mid-landing on the same file, after `make test-doc-lint` (or
`test-plan-lint` before T2) + `make strict` green.

### 5.1 Standing questions (docs/design/CLAUDE.md)

1. Measurement regime: RELEVANT only for byte sizes (`wc -c`/python at
   6638e3679) and the token estimate (4 B/token; a 2x error moves the soft
   caps, not the design).
2. Independent control: RELEVANT. The converter's output is checked against
   counts taken from the ORIGINAL file by a different route: 191 distinct
   ids (`grep -oE '^## D[0-9]+' | sort -u`), the §1.1 addendum census, and a
   byte check (the multiset of non-heading body lines is identical before
   and after); unit 1's D47 test is a hand-picked witness the converter's
   author did not choose. A statement is checked by a critic independent of
   its WRITER (fresh context, no access to the writer's reasoning); both
   read the details, which is correct, since the claim checked is
   faithfulness to the details, the record. Whether the details themselves
   are right is outside this design. C9 floors count the population; the
   `--selftest` over-cap plant proves the WARN path reaches its site.
3. What moves when regenerated: the indexes are hand-written; converters run
   once per unit. No emitted byte, abi or spec moves (process docs only);
   the readers that move are the §1.2 rows, each named in its unit.

## 6. Risks

- The index drifts from the details. Mitigation: `a<k>` forces a touch at
  every addendum; the statement shape bans rationale, so drift is a visible
  wrong rule; the manager skill gains "act on the index, but read
  `scripts/entry` before quoting, changing or building on a ruling's
  specifics".
- Big transforms collide with landings. Mitigation: re-run on HEAD,
  mixed-file input, landing at quiet points.
- A reader missed. The §1.2 list is grep-found; rows_check.py is the one
  parser of decisions.md. D27 cell briefs that allowlist decisions.md must
  add the details file (a brief-time miss, not a tool change).
- Addendum renumbering breaks old cites. Numbered addenda keep numbers; only
  unnumbered ones gain one, and their old label stays greppable.
- Soft caps are ignored. Mitigation: the gestalt line repeats every
  heartbeat while over, which is the owner's chosen revisit trigger.
- The `single` plan form outlives unit 2. Mitigation: unit 2's delivery
  deletes it; the linter refuses a `single` profile once its details file
  exists.

## 7. Owner's answers (2026-11-10)

1. Statements written by OPUS lanes, checked by a fresh OPUS critic against
   the details (no ruling added or dropped, `(+n more)` right); no owner
   read-through. Applied: §2.7, §5.
2. One details file vs one per entry is our call, since access goes through
   the accessor. Kept one per index (§2 has the one-line reason).
3. A LEVELED accessor that supplies different levels and greps for items.
   Applied: §2.3 (levels 0/1/2, item grep, `--work`), levels and work views
   declared in the profile table (§2.4); triggers stay out of the index.
4. Soft caps now, revisit later; gestalt prints only when over. Applied:
   §2.4 (WARN, never fail; the `docs:` line format), §3.
5. Kit ledger: yes, ask the kit for feedback once vetted. Applied: §8,
   unit K.
6. Known issues third, right after decisions and plan. Applied: unit 3.

New open question:

1. **Should the per-LINE limits (statement 200 chars, plan title 90, `now`
   160) also be soft, or only the file sizes?** Your answer named the caps
   in general; the question you were answering was about file size. A soft
   file cap with hard line limits means a single long statement is refused
   at write time while the file as a whole is allowed to grow and is only
   reported. Leaning: keep the line limits HARD. They are what keeps a
   statement a statement, a writer can always fix one line on the spot,
   and plan_lint already refuses over-long titles and status lines today,
   so softening them would loosen a rule that works now. Only the file
   sizes become soft.

## 8. Proposal to the kit (sendable as is)

*From the pcrec manager to the kit manager, for feedback; the kit decides
whether and how its own files adopt any of it.*

**What pcrec is doing.** pcrec is moving its long ruling and tracker files
(decisions.md 832 KB, plan.md 468 KB, known_issues.md 467 KB) to a PAIR:
a short INDEX with one line per entry (id, a short slug, a state, and ONE
sentence stating the current ruling or status), and a DETAILS file holding
each full entry verbatim under a `## <ID> <slug> — title` heading, with any
later addenda INSIDE their entry as `### <ID>.aN`. Existing ids never
change. One accessor, `scripts/entry ID`, prints an entry at a chosen level
(0 the index line, 1 plus its working fields, 2 the full entry), greps by
item, and lists open work; one profile table declares each file's ids,
states, levels and soft size caps. Full design:
docs/design/doc_index_format.md.

**Why.** A session can hold the index (about 40 KB per file) in context and
know every current ruling in one line, and fetch exactly one full entry
when it needs specifics. Today an entry is found by grepping a heading and
reading a line range, which costs 3-36 KB per entry and misses addenda
filed under a later entry (17 such cases in decisions.md).

**What it would look like in the ledgers (facts about the files, for the
kit to weigh).** requests.md has 38 `## R-n (date, who) — title` items,
written only by main; responses.md has 16 `## R-n`/`## N-n` items plus
`###` notices, written only by the kit; they are read in order, as a
dialogue. A shape that fits them: an index block at the top of each file,
one line per item (`- R-38 <slug> <state> — the ask (or the answer) in one
sentence`), with the bodies left where they are, so the ledgers stay
single-writer and in order. Main would write the block in requests.md.
Adding a `kit` row to the profile table would give the kit `scripts/entry
R-38` and an open-items view from the same accessor. rows_check.py's LEDGERS
reader reads the bodies, so an index block does not touch it.

**What we ask.** Feedback on the format itself (anything that would not fit
the kit's files or its wake read), and whether the kit wants the ledger
index blocks, a split, or neither. No change to either ledger happens
without the kit's answer.
