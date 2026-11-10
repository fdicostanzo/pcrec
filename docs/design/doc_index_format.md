# One format for ruling and tracker files: a tight index plus greppable details (rev 0)

Lane docfmt, 2026-11-10. DESIGN ONLY: nothing here converts a real file.
Owner's ask (Frank, 2026-11-10): decisions and plan should each be a short
"simple statement" file that covers most cases and is easy to recall, plus a
details file from which one entry is easy to grep out by its slug; formalize
the shared format; say which other files fit. The consumer is the AI manager
session, which keeps the index in context, and its lanes, which grep details
on demand.

## 0. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the manager holds every ruling's CURRENT form in context | manager, owner | decisions index ≤ 48 KB (today the only whole-file form is 832 KB), every D-id present |
| G2 | one command prints exactly one entry, addenda included | manager, lanes | `scripts/entry D26` prints one entry and nothing else; 0 addenda sit outside their entry (17 do today, §1.2) |
| G3 | one format and one linter for every tracker that fits | maintainers | one linter (plan_lint folded in), one lookup tool; per-file differences are rows in one table |
| G4 | no citation breaks | everyone | every `Dn`, `Dn add. k`, `[TAG]`, `Kn` cite resolves after migration; 0 ids renumbered |
| G5 | an index statement never says more or other than its details | owner | 100% critic pass for decisions statements, 1-in-5 for plan rows (§5) |

Priority on conflict: G4 > G5 > G1 > G2 > G3. Non-goals: rewriting details
text; changing what a decision says; append-only journals and logs (§4).

## 1. Census

Sizes are bytes at main 6638e3679. "Entries" counts the file's own heading
form. Size spread is per entry.

### 1.1 Candidate files

| file | bytes | entries | entry heading | size median / p90 / max | parsed by |
|---|---|---|---|---|---|
| docs/dev/decisions.md | 832,382 | 191 ids, 198 `## D` headings | `## Dn — title (date, who)` | 2,834 / 9,279 / 36,010 (D29) | tests/memfn/rows_check.py (§1.3) |
| docs/dev/plan.md | 467,976 | 339 rows (296 not-started, 36 started, 2 blocked, 5 deferred) | `- [TAG] STATE:s — title` + 2-space attribute lines | 1,090 / 2,490 / 4,969 | scripts/plan_lint.py (PL1-PL15), pre-commit |
| docs/design/plan_row_bodies/ | 22 files, 177 KB | 1 file per row | file named `TAG.md` | 1.0-28 KB | plan_lint PL15 |
| docs/dev/plan_completed.md | 1,212,690 | 380 `STATE:completed` rows under date headings | same as plan.md | archive | plan_lint (moved-row check) |
| docs/dev/known_issues.md | 466,753 | 139 (`## Kn — STATE ... — title`; 71 FIXED, 42 OPEN, 7 CLOSED, 3 ACCEPTED, rest unmarked) | `## Kn` | 2,443 / 6,655 / 19,008 | none (cited by K-number from ~70 tests) |
| docs/dev/upstream_issues.md | 70,369 | 25 `## Un` | `## Un — engine: title` | small | none |
| memfn/docs/requests.md | 92,851 | 38 `## R-n` (main's single-writer file) | `## R-n (date, who) — title` | — | post_compact.sh names it |
| memfn/docs/responses.md | 300,327 | 16 `## R-n`/`## N-n` + `###` notices (kit's file) | `## R-n — title` | — | rows_check.py LEDGERS |
| docs/dev/learnings.md | 41,996 | numbered sections §1-§6, §3.a-§3.ac | `## n.` / `### 3.x` | — | none (cited as "learnings §3") |
| docs/testing.md | 344,067 | ~50 topical sections | `## The ...` | — | none (cited by section name) |
| docs/dev/dev_journal.md | 1,886,739 | 448 dated entries, append-only | `## date` | tail-read | known_fail, test_trailer (append) |
| docs/dev/full_suite_ledger.md | 50,678 | "since last green" section + landing lines | prose lines | — | queuemon, fullsuite_job.sh (append + grep) |
| memfn/docs/ideas.md | 54,470 | 28 dated raw notes, append-only | `## date — note` | — | none |
| REFERENCES.md | 41,510 | 55 `### [Key]` | `### [Key] authors (year)` | small | none |

Decisions shape, measured: 54 of 191 entries carry addenda, in SIX
spellings (70 `### Dn addendum[ k]`, 17 `- **Addendum`, 15 `**Addendum`,
6 `**ADDENDUM`, 6 separate `## Dn ADDENDUM` top-level headings, 1
`## Dn SECOND ADDENDUM`); 61 are numbered, the rest are not. 17 addenda
sit inside a LATER entry (D163's addenda inside D167 five times, D94's inside
D112, D161's inside D162, ...), so reading `## D163` alone today misses part
of D163's current ruling. Supersession is prose (10 "SUPERSEDED" marks, no
field). Citations: ~4,800 `Dn` tokens in src/tests/scripts/lib/cli, 2,708
`Dn add. k`/`Dn addendum k` cites tree-wide: ids AND addendum numbers are
load-bearing.

Plan shape: the head lines alone total 35,289 B (median 108 B); everything
else in the row (filed, status, next/trigger, refs, charter) is 430 KB.

### 1.2 Who reads what, and how

| reader | file | how |
|---|---|---|
| scripts/plan_lint.py (+ .sh wrapper, tests/plan_lint/, Makefile `test-plan-lint`, scripts/hooks/pre-commit) | plan.md, plan_completed.md, plan_row_bodies/ | full parse: row grammar, sections, caps (title 100, status/next 300, line 1000, row 12 lines / 6000 B), body pointers (PL15), no `plan.md:N` cites tree-wide (PL14), row floor 150 (K35) |
| tests/memfn/rows_check.py `support_faults` | decisions.md, memfn/docs/responses.md | opens the file; for a `D`-provenance basis cuts `^## Dn\b.*?(?=^## D[0-9]\|\Z)` and requires the quoted ruling sentence inside it |
| tests/memfn/stream_support.tsv | decisions.md | rows carry `"sentence" @ docs/dev/decisions.md D190` |
| scripts/hooks/pre-commit | plan files | path glob triggers plan_lint --staged |
| scripts/boxqueue header | plan_row_bodies/BOXQUEUE.md | comment pointer |
| scripts/hooks/post_compact.sh | owner.md, wake.md, memfn wake | injects owner.md + wake.md to WORK QUEUE (≤5,000 chars); kit role is told to read requests/responses |
| .claude/skills/pcrec-manager §1-§2, §6 | plan.md, decisions.md, journal | `grep -n "STATE:started"`, `grep -n "STATE:not-started"`; "add a decisions.md entry"; journal tail |
| .claude/skills/q | decisions.md, plan.md | writes rulings |
| .claude/skills/pcrec-critic | decisions.md, plan.md | freezes their commit; denies a plan row via `grep -n '^- \[TAG\]'` |
| .claude/skills/pcrec-memfn-manager | requests/responses, decisions | reads open items at wake; rulings live in decisions.md |
| root CLAUDE.md, docs/dev/CLAUDE.md, ~57 CLAUDE.md files | all | prose pointers ("decisions.md D26", "grep plan.md for rows naming it") |
| tests, src comments | all | cite ids only; no parse |

How the manager looks things up today: `grep -n` on STATE tags for the
plan; for a ruling, a grep for `^## D26` and a Read of a line range, which
misses misplaced addenda and costs 3-36 KB per entry. Nothing gives "the
current ruling in one line".

### 1.3 Files a session loads at start

| file | bytes | how |
|---|---|---|
| root CLAUDE.md | 17,876 | auto-injected (cap 20 KB) |
| ~/.claude/CLAUDE.md | 1,175 | auto-injected |
| memory MEMORY.md | 23,494 | auto-injected (manager and every lane) |
| docs/dev/owner.md | 5,430 | post_compact.sh injects it whole |
| docs/dev/wake.md | 22,115 | first 5,000 chars injected; skill §1 says read in full |
| pcrec-manager SKILL.md | 14,919 | on /pcrec-manager |
| dev_journal tail, plan STATE greps | variable | skill §1 |
| BOILERPLATE.md (+ RUNS.md on trigger) | 10,872 (+15,564) | every lane |

Today's always-on manager load is ~85 KB. The two proposed indexes add
~80 KB (§3), which nearly doubles it. That is the price of G1, and §3 caps it.

## 2. The format

One spec for every file that adopts it. A file that adopts it is a PAIR:

- the INDEX keeps the file's current name (decisions.md, plan.md,
  known_issues.md), so every existing prose pointer ("decisions.md D26")
  still lands on the right line;
- the DETAILS file is `<name>_details.md` beside it, ONE file per index (see
  open question 2). Details are never loaded whole; they are read one entry
  at a time.

### 2.1 Index entry

One line per entry (plan rows: one line, or two for started/blocked rows).

    - <ID> <slug> <state>[ a<k>] — <statement>[ (+<n> more)][ {<keywords>}]

| field | rule | why |
|---|---|---|
| ID | existing id, never renumbered (`D26`, `K139`, `U22`; plan keeps `[TAG]`) | G4: ~7,500 cites |
| slug | kebab-case, 2-4 words, ≤ 28 chars, unique in the file; the plan's `[TAG]` IS its slug (no second name) | a recall handle that survives a renamed title; `entry` takes it |
| state | decisions: `live`, `sup>Dm` (wholly superseded), `part>Dm` (partly; the statement is the live remainder), `retired` (no longer applies, no successor), `absorbed>WHERE` (the rule now lives in CLAUDE.md/spec/skill, which is the record). Known issues: `OPEN`, `FIXED`, `CLOSED`, `ACCEPTED`. Plan: `STATE:<s>` as today, so the skills' greps keep working | supersession becomes a field, not prose |
| a<k> | number of addenda in the details entry; the linter checks it equals the count of `### ID.aN` headings | adding an addendum FORCES a touch of the index line, the moment to rewrite the statement (G5, no git-diff machinery) |
| statement | ONE sentence, ≤ 200 chars, present tense, the CURRENT ruling with every addendum applied. Shape: `<topic>: <rule>[; <rule>...].`, topic a noun phrase of ≤ 4 words naming what is governed. No rationale, dates, history or lane names | the shape is what a session pattern-matches when it is about to act; 200 chars keeps 191 entries near 38 KB |
| (+n more) | count of rulings the statement left out | compression is allowed, silent omission is not; the critic checks n |
| keywords | optional, ≤ 40 chars, only words absent from slug and statement (synonyms, tag names, numbers) | grep recall for words the sentence did not need; no repeats keeps it from growing |

Superseded, retired and absorbed entries shrink to ≤ 80 chars naming what
replaced them: the index then grows by live rulings, not by history.

Plan rows keep their head line (title cap 100 → 90) and gain ONE second line
only when started or blocked:

    - [TAG] STATE:<s> — <title ≤ 90>
      now (<ISO date>): <≤ 160 chars: where it stands and the next step>

`now` is the status of record and is rewritten in place. It is REQUIRED on
started and blocked rows and FORBIDDEN elsewhere (no optional field, so the
index cannot creep): a not-started row's next step or trigger is in its
details. Children stay nested by two spaces, so umbrella structure stays
visible in the index. Sections (Active, Candidates, Backlog, Boonies,
Deferred) stay. The Policy section shrinks to a 1 KB pointer at the format
document (§2.6).

### 2.2 Details entry

    ## <ID> <slug> — <original title, verbatim> (<original date, who>)
    <body, verbatim>
    ### <ID>.a1 — <date, who>: <addendum title>
    <addendum body, verbatim>
    ### <ID>.a2 — ...

- An entry runs from its `## ` heading to the next `## ` heading. Body text
  never uses a level-2 heading (the linter checks; today's six `## Dn
  ADDENDUM` headings become `### Dn.ak`).
- Addenda live INSIDE their entry, in date order. Numbers: an addendum
  already numbered keeps its number ("D163 add. 7" stays `D163.a7`); an
  unnumbered one takes the lowest free number in date order and keeps its
  old label on its first line (`(was: "D26 addendum (owner, 2026-11-06)")`)
  so a grep for the old wording still lands.
- Plan details hold what leaves the row: `filed:`, `next:`/`trigger:`
  (required for not-started, blocked, deferred: the current PL rule moves
  here), `refs:`, the charter, dated history. plan_row_bodies/ files fold in
  verbatim as their row's details body.
- Cross-links are bare ids (`D26`, `[ANCH-AT]`, `K139`, `R-38`, `D163.a7`),
  never markdown links or line numbers.

### 2.3 Lookup: one tool, one awk line

`scripts/entry` (python3 stdlib, `-I`, ~120 lines; it reads the same
profile table as the linter, §2.4):

    scripts/entry D26 | pcre2-compat-tiers   index line, then the details entry with its addenda
    scripts/entry D26.a2                     the index line, then that one addendum
    scripts/entry -i D26                     the index line only
    scripts/entry -g WORD                    grep every index, one hit per line
    scripts/entry ANCH-AT                    plan rows: index lines (row + children), then details;
                                             falls through to plan_completed.md for a finished row

The id prefix picks the profile (`D` decisions, `K` known issues, `U`
upstream, bracketless TAG plan). Exit 1 not found, 2 ambiguous slug. With no
tool, one line does the same:

    awk '/^## /{p=($2=="D26"||$3=="pcre2-compat-tiers")} p' docs/dev/decisions_details.md

rows_check.py's existing regex (`^## D190\b ... (?=^## D[0-9]|\Z)`) works
unchanged on the details file and, once addenda sit inside their entry,
becomes correct for the 17 misplaced cases too.

### 2.4 One linter: plan_lint becomes doc_lint

`scripts/plan_lint.py` becomes `scripts/doc_lint.py` with a declared
PROFILES table, one row per file pair (Frank's first-match tables, and the
general-mechanism memory: one linter, not a second one beside plan_lint):

| profile | index | details | id | slug | states | caps (statement / line / file) | extra rules |
|---|---|---|---|---|---|---|---|
| decisions | decisions.md | decisions_details.md | `D[0-9]+` | required | live sup part retired absorbed | 200 / 300 / 48 KB | `a<k>` = addendum count; `sup>`/`part>` target exists |
| plan | plan.md | plan_details.md | `[TAG]` | = tag | the four STATEs | title 90, now 160 / 2 lines / 48 KB | today's PL rules: sections, TOP_STATES, next/trigger in details, finished rows absent, PL14 cites |
| known | known_issues.md | known_issues_details.md | `K[0-9]+` | required | OPEN FIXED CLOSED ACCEPTED | 180 / 280 / 32 KB | — |
| upstream | upstream_issues.md | upstream_issues_details.md | `U[0-9]+[a-z]?` | required | OPEN FILED FIXED-UPSTREAM CLOSED | 180 / 280 / 12 KB | — |

Common rules, every profile (each FAILS; no warning severity, as plan_lint):

- C1 ids unique in the index; C2 bijection: every index id has exactly one
  details heading and every details heading one index entry; C3 heading
  grammar (§2.1, §2.2); C4 field and file caps; C5 slug kebab, ≤ 28, unique;
  C6 every `### ID.aN` lies inside `## ID`, numbers unique and rising; C7
  every id cited in an index line resolves (index, or plan_completed for
  plan tags); C8 no `<file>.md:<line>` cite of any profile's file anywhere
  in the tree (PL14 generalized); C9 a parsed-entry floor per profile (K35:
  a linter that parsed nothing is green); C10 no level-2 heading inside a
  details body.
- `--selftest` plants one violation per rule per profile (today's
  plan_lint planting, widened); `--staged` lints the index content as now;
  `--stale` (informational, exit 0) adds each index's headroom under its
  file cap and the count of `?` statements left (§5).
- Readers kept whole: `scripts/plan_lint.sh` becomes `doc_lint.sh [profile]`;
  the Makefile target `test-plan-lint` is renamed `test-doc-lint` with every
  reader (Makefile, pre-commit glob, tests/plan_lint/ → tests/doc_lint/,
  docs/testing.md, skills) moved in the same unit.

### 2.5 Worked examples (real entries; bytes measured)

**Decisions index** (statement bytes 198 / 189 / 173):

    - D26 pcre2-compat-tiers live a3 — PCRE2 compatibility: matching and syntax recognition are exact; accept all PCRE2 accepts (more allowed); follow the standard over an evidenced PCRE2 bug; never chase unimplemented-construct wording. {diagnostics floor 10.46}
    - D47 brep-counterk live a4 — Bounded repeats: possessify, then rung select, then counter-K; K is one per-artifact named constant (8) in v1, never per quantifier; frameless forward work has its own bound and error code. (+3 more) {ENG-BREP}
    - D191 span-arms-go live — Span arms: build E1 R1 E2 L1 L3 (L2 after kit R-38); a run crosses as one uncut span of byte sets at signed offsets; repeats count as copies; zero-width items do not cut it. (+3 more)

Lines: 262, 243, 213 B (D26 against 9,723 B of details, D47 against 12,811,
D191 against 1,815).

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

D47 is the hard case in one entry: two addenda that were top-level `## `
headings (today a `^## D47\b` cut picks up only the first block, so the two
rulings that changed K and the work bound are invisible to it), and two
unnumbered inline ones, all four now numbered in date order.

    ## D191 span-arms-go — span arms: BUILD GO, and the owner's rulings on the open questions (Frank, 2026-11-08/09)

**Plan index** (three states):

    - [OPT-REVEND] STATE:started — reverse-from-end search for end-anchored patterns
      now (2026-10-26): B3 match-end mark landed (abi 78); stage 3 waits for a bench cell in the anc-tail family
    - [ANCH-AT] STATE:blocked — one anchored DFA run where the start is known (F-11: 328 _match bodies)
      now (2026-11-06): scheduled by Frank; starts once lookbehind stage 1 and the alternation build land
      - [XARCH-TOKERR] STATE:not-started — an unknown CPU token's refusal is cut at 256 bytes mid-text

Index bytes: OPT-REVEND 192 (row today 4,224), ANCH-AT 204 (today 919),
XARCH-TOKERR 101 (today 636).

**Plan details** (XARCH-TOKERR, whole row moved, 575 B; shown cut):

    ## [XARCH-TOKERR] — an unknown CPU token's refusal is cut at 256 bytes mid-text
    filed: 2026-11-08 manager (review 2026-11-08-r5-xarch CONTRACT-4, PLAN)
    next: size the joined refusal (or show the kit's target and family refusals separately) so cli.md §1.24¶2's "the kit's text unchanged" holds for any token length
    refs: src/gen/memfn_targets.c add_list; docs/spec/cli.md §1.24
    A 120-byte unknown token prints 263 bytes ending mid-token, without the "(known: ...)" lists; ...

ANCH-AT's details carry filed, trigger, refs and its two-line charter; its
old `status (2026-11-06)` line becomes the first dated history line.
OPT-REVEND's carry filed, trigger, refs, the charter, the EXACTNESS / D77
LINEAGE / timing paragraphs and the [REVEND-WALK-FORM] answer, verbatim.

### 2.6 Where the format is defined

The format (this section's rules, without the census or the migration) moves
to `docs/dev/doc_format.md` at unit M0, the one definition the linter's
docstring and every index's header point at. plan.md's Policy section today
plays that role for the plan; it shrinks to the pointer plus the plan-only
rules (sections, queue discipline).

### 2.7 Writing an entry from now on

A new ruling = the details entry + the index line, in one commit (the
linter's C2 refuses one without the other). An addendum = the `### ID.aN`
block + the index line's `a<k>` bump, with the statement rewritten if the
ruling moved (the bump is what makes the writer look). The q and
pcrec-manager skills' "write the ruling" steps change to name both files.

## 3. Size targets

Measured basis: the worked examples above (decisions lines 213-262 B, all
three multi-ruling, so above typical); today's decisions headings average
155 B and plan head lines 104 B (all 191 / 339 measured).

| index | entries | per entry | projected | cap (lint) |
|---|---|---|---|---|
| decisions.md | 191 live today | 190-200 B typical, 240 B if all were like the examples; superseded ones ≤ 100 B | 36-46 KB, central 38 KB | 48 KB |
| plan.md | 339 rows; 38 with a `now` line | head ~100 B; now line ~120 B | 34 KB + 4.6 KB + 1.5 KB headers/pointer ≈ 40 KB | 48 KB |
| known_issues.md | 139 | ~180 B | 25 KB | 32 KB |
| upstream_issues.md | 25 | ~170 B | 4 KB | 12 KB |

Why 48 KB: at ~4 bytes per token (an estimate, not a tokenizer count) the
two main indexes are ~20k tokens, beside ~85 KB (~21k tokens) already
always-on (§1.3). The manager's reset rule fires at 35% context; ~40k tokens
of standing context leaves most of the window for the work even on a 200k
window. A cap is needed, not just a target, because the index is
append-mostly: decisions grew 45 entries in the last 34 days (D146 on 10-05
to D191 on 11-08), about +8 KB a month at 200 B each, so the 48 KB cap
arrives in roughly 1-2 months unless superseded entries shrink (§2.1). What
happens at the cap is open question 4. Lanes do NOT load the indexes; they
call `scripts/entry`.

## 4. Other files

| file | verdict | reason |
|---|---|---|
| known_issues.md | APPLY | same shape as decisions: id, state, long body; 467 KB that today no one can hold; symptom-in-one-line recall prevents re-filing |
| upstream_issues.md | APPLY (small, last) | same shape, 25 entries; nearly free once the tool exists |
| plan_completed.md | PARTIAL | stays the archive: a finished row's index line(s) and details entry move there verbatim, appended under the date heading; no index of its own (it is grepped, never held); `entry` falls through to it |
| docs/design/plan_row_bodies/ | ABSORBED | its 22 files become plan_details.md entries; the directory and PL15 retire (open question 2) |
| memfn/docs/requests.md | PROPOSAL TO THE KIT, partial | main's single-writer file; an index block at its top (`- R-38 <slug> <open\|answered\|closed> — the ask in one line`) would serve the kit's wake read of "open items"; bodies stay in place (a dialogue reads in order); main writes it |
| memfn/docs/responses.md | PROPOSAL TO THE KIT, partial | the kit's file: the same index block, kit-written, states `ack\|done\|notice`; rows_check.py's LEDGERS reader is unaffected (it reads bodies) |
| memfn/docs/ideas.md | DO NOT APPLY | append-only raw log, evaluated later by design |
| docs/dev/learnings.md | DO NOT APPLY (now) | 42 KB of doctrine in numbered sections cited as "§3"; already the summary tier (the full catalogue is a memory file); a section-number index would add a reader for little |
| docs/testing.md | DO NOT APPLY | a handbook of topical sections cited by name, not a tracker of ids; a table of contents is a separate, smaller question |
| docs/dev/dev_journal.md | DO NOT APPLY | append-only, tail-read; its value is order |
| docs/dev/full_suite_ledger.md | DO NOT APPLY | append-only log written and grepped by scripts (queuemon, fullsuite_job.sh) |
| REFERENCES.md | DO NOT APPLY | entries already one heading + one citation each; it is its own index |
| wake.md, owner.md, memfn wake | DO NOT APPLY | rewritten whole each session |
| the memory index (MEMORY.md) | already this format | one line per fact, detail in its own file: the shape the manager already recalls well, and the model for this one |

## 5. Migration plan

Every unit is a re-runnable TRANSFORM, not a hand-made diff: the lane
delivers a converter script plus its output, and the landing re-runs the
script on main HEAD before committing. decisions.md and plan.md are written
by nearly every landing; a stale converted copy would conflict, a re-run
never does. The converter accepts a MIXED file (old-form entries appended
after conversion are converted on the next run), so branches in flight
across a unit need only a re-run, not a rebase by hand.

| unit | what | size | tier | readers moved in the same unit |
|---|---|---|---|---|
| M0 | `scripts/doc_lint.py` (plan_lint folded in as the plan profile, its PL rules and selftest plants unchanged in effect), the decisions/known/upstream profiles DORMANT (off until their unit), `scripts/entry`, docs/dev/doc_format.md | ~600 lines python, 1 doc | sonnet | Makefile target rename, pre-commit, tests/plan_lint → tests/doc_lint, docs/testing.md, scripts/CLAUDE.md |
| M1 | decisions split by converter: details file verbatim with new headings, addenda folded into their entries and numbered (§2.2), index generated with PROVISIONAL statements = the old title, state `?` | 191 entries, one run | sonnet | rows_check.py LEDGERS + stream_support.tsv paths; skills q, pcrec-manager, pcrec-critic (freeze both files), pcrec-memfn-manager; root CLAUDE.md "Where things are" and a situation-index row ("about to look up a ruling or row → `scripts/entry ID`"); docs/dev/CLAUDE.md |
| M2-M9 | decisions statements, 8 batches of 24 ids each, in id order | 24 statements | sonnet writer + sonnet critic | none (index lines only) |
| M10 | plan split by converter: details file, plan_row_bodies/ folded in, `now` lines provisional = today's status line (≤ 300 allowed while `?`), title cap 90 applied as `?` where over | 339 rows | sonnet | plan profile switched to the pair; boxqueue comment; skills' plan recipes; plan_completed move rule |
| M11 | plan `now` lines rewritten (38 rows) and over-cap titles cut | 2 batches of ~20 | sonnet + 1-in-5 critic | none |
| M12 | known_issues split + 6 statement batches of 24 | 139 | sonnet + critic | the known_fail instructions text |
| M13 | upstream_issues, one unit | 25 | sonnet | none |
| K | the requests/responses index blocks | — | the kit's choice | relayed by the manager; never edited by these lanes |

Faithfulness (G5). The writer reads the WHOLE details entry, addenda
included, and writes the current ruling; it never reads the old title as a
source of truth (titles often state the first ruling, not the current one).
A separate critic, fresh context, reads each details entry and its new
statement and answers four questions per entry: does the statement add a
ruling the details do not make; contradict the current ruling; state a rule
an addendum replaced; or omit a ruling without counting it in `(+n more)`?
Decisions: 100% of each batch (24 entries × ~4 KB is one critic's reading).
Plan `now` lines: 1 in 5 (lower stakes; the old status line is the
comparison). Disputes go to the manager; the owner reads the finished
decisions index once (~38 KB), the only reader whose memory of the rulings
does not share a source with the details text. The `?` count is a ratchet:
`--stale` reports it and the linter refuses an increase once M1 lands.

Order: M0 → M1 → M2-M9 (the owner's first question) → M10-M11 → M12 →
M13. M2-M9 batches touch disjoint lines of one file and can run 2-3 at a
time.

Freeze: NO merges to main from 2026-11-11 01:00 until the full suite ends
(about 14:00). M0 may land before 01:00 only if it is ready and light; M1
and M10, the two big transforms, land at a quiet point after the suite,
each with no other lane mid-landing on the same file, and after
`make test-doc-lint` + `make strict` green.

### 5.1 Standing questions (docs/design/CLAUDE.md)

1. Measurement regime: RELEVANT only for byte sizes (measured by `wc -c`/
   python at 6638e3679) and the token estimate (4 B/token, an estimate; a
   2x error moves the caps, not the design).
2. Independent control: RELEVANT. The converter's output is checked against
   counts taken from the ORIGINAL file by a different route: 191 distinct
   ids (`grep -oE '^## D[0-9]+' | sort -u`), the addendum census of §1.1,
   and a byte check (the multiset of non-heading body lines is identical
   before and after). Statements are checked by the critic and the owner
   (§5), not by the writer. C9 floors count the population.
3. What moves when regenerated: the indexes are hand-written, not
   generated; the converter runs once per unit. No emitted byte, abi or
   spec moves (process docs only); the readers that move are the §1.2
   rows, each named in its unit.

## 6. Risks

- The index becomes the record and drifts from the details. Mitigation: the
  `a<k>` count forces a touch at every addendum; the statement shape bans
  rationale, so a drift is a visible wrong rule, which the critic and the
  owner can catch; the rule "act on the index, but read `scripts/entry`
  before quoting, changing or building on a ruling's specifics" goes in the
  manager skill.
- Big transforms collide with landings. Mitigation: converter re-run on
  HEAD, mixed-file input, landing at quiet points.
- A reader missed. The §1.2 list is grep-found; rows_check.py is the one
  parser of decisions.md today. The D27 cell script takes explicit
  allowlists (no default), so briefs that allowlist decisions.md must add
  the details file: a brief-time miss, not a tool change.
- Addendum renumbering breaks old cites. Numbered addenda keep numbers;
  only unnumbered ones gain one, and their old label stays greppable.
- Write cost per ruling rises (two files). Small, and C2 makes forgetting
  one impossible.
- The cap arrives soon for decisions (§3).

## 7. Open questions for the owner (each with my leaning)

1. **Who writes the one-sentence statements, and must you see them?**
   Sonnet lanes write, a fresh critic checks every decision, the manager
   rules disputes. Leaning: you read the finished decisions index once
   (~38 KB, about 15 minutes), because you are the only check that does
   not depend on the text we summarise.
2. **One details file per index, or one file per entry (the way
   plan_row_bodies/ works today)?** One file per entry makes "print the
   entry" a plain `cat`, but means ~700 small files, each listed in a
   directory guide, and no single grep over all details. Leaning: one
   details file per index; the `entry` tool and a one-line awk print
   exactly one entry, and plan_row_bodies/ folds into plan's details file.
3. **Should a not-started plan row show its next step or trigger in the
   index?** Leaning no: 296 extra lines would add ~35 KB; the title says
   what the row is, and `scripts/entry TAG` gives the trigger when you
   are choosing work.
4. **What happens when the decisions index reaches its cap (in about one to
   two months at today's rate)?** Options: raise the cap; shrink superseded
   and absorbed rulings to one short line (built in already); or keep a
   second, "settled history" section with slug-only lines for rulings
   nobody needs day to day. Leaning: shrink first, then a settled section,
   with you choosing which rulings count as settled.
5. **Should the kit's request/response ledger get the same index block?**
   It is the kit's file on one side and main's on the other, so it is a
   proposal. Leaning yes, small and later, after decisions and plan.
6. **Known issues next, or stop after decisions and plan?** Leaning: do
   known issues (139 bug entries, 467 KB, the same shape) right after the
   plan.
