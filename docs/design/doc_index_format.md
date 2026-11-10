# One format for ruling and tracker files: a tight index plus greppable details (rev 3)

**Rev 3 (lane docfmt3, 2026-11-10):** applies the rulings on the re-check
round `docs/dev/reviews/2026-11-10-r2-docfmt2.md` (every proposed disposition
accepted; R2-24 decided by the owner, D192 item 7). Rev 2's own change map
(F1-F17 of round r1) is in `docs/dev/lanes/docfmt2_report.md`. Worked tables:
`doc_index_format_appendix.md` (A-J). Changes by finding:

| id | change (where) |
|---|---|
| R2-1 | T1 frees scripts/CLAUDE.md headroom first, runs `check_claudemd_size.sh --all` (§5 T1) |
| R2-2, R2-3 | gestalt row `docs`/`L_docs` replaces the placeholder; an empty line prints nothing under `--all` (general rule, deletes the idle-held special case); `GESTALT_ENTRY`; `timeout 2`; `"$here/entry"` (§2.4, appendix J) |
| R2-4 | a FIXTURE pair profile with over/under-cap and rounding-edge plants; `--over-cap` states its population; "one decimal, truncated" (§2.4, J) |
| R2-5 | dormant profile = exit 1 + trailer; router plants on fixture profiles; the archive is live at T1; T1's root row claims plan only (§2.3, §5) |
| R2-6 | an archive row is plan_lint's HEAD_OK form (§2.3) |
| R2-7, R2-8 | the section's full list (trailer touch, CLAUDE.md files, `NO-C-RUN`, shard row), T1 ACCEPTANCE, monitoring.md (§2.4, §5 T1) |
| R2-9 | `--rev` reads the working tree's table and picks the form by the files at SHA; `entry` imports plan_lint's grammar; PL18 refuses an id-shaped tag; both key spellings (§2.3) |
| R2-10, R2-13 | the census scans EVERY line; a stated marker-vs-mention criterion; 193 markers at e9687de27; a foreign-marker gate (§5.2, A) |
| R2-11, R2-12 | the control compares per EXTENT, byte-exact; (ii) a bijection; heading text checked; `extent_hash`; a named plant list in `doc_control --selftest` and 1.0 ACCEPTANCE (§5.2, B) |
| R2-14 | `who`, `title`, full `old_label` columns; the title rule; C3's addendum regex; `class=note` rows; D47's LANDED NOTE a ruled row (§2.2, B) |
| R2-15 | D147 = unnumbered + 2-16; D98's join is two lines, D98 only (A) |
| R2-16 | C9's floor column; lane/docfmt merges before 1.0; counts re-taken by the census (§2.4, §5) |
| R2-17 | cite-to-id by the named id, else by content anchor; mismatches listed (E) |
| R2-18 | a `?` line is exempt from C4; caps count characters (§2.1, §2.4) |
| R2-19 | C13 shares C8's exemptions; a committed dangling baseline that only shrinks; date alias (§2.4, C) |
| R2-20 | live population 26 cites in 11 files; C8's widened regex and anchor; plan_completed exempt for every profile (§2.4, E) |
| R2-21 | hooks live in the COMMON git dir: skip when the tree predates the profile module, fail when its linter is missing; `linter`/`extra_paths` columns; `--paths` format (§2.4) |
| R2-22 | the ratchet's committed baseline, birth and landing rules; new entries carry no `-`/`?` (§2.4, §2.7) |
| R2-23 | missing readers: bench inbox (MANAGER STEP, D78), docs/dev/NOTES.md, D27 allowlists, post_compact main role (§5 unit 1, H) |
| R2-24 | owner: decisions index at wake, plan index on first need, neither inlined (§0 G1, §3, §5) |
| R2-25, R2-26 | PLAN before T2 and before 1.S (§10) |
| R2-27 | one cite-form table for C8/C13 in unit 1; [CITE-FORMS] filed; hook manifest NOTED (§2.4, §9) |

DESIGN ONLY: nothing here converts a real file. Owner's ask (Frank,
2026-11-10): decisions and plan should each be a short "simple statement" file that covers most cases and is easy to recall, plus a
details file from which one entry is easy to grep out by its slug; formalize
the shared format; say which other files fit. The consumer is the AI manager
session, which keeps the decisions index in context, and its lanes, which
read details on demand through the accessor.

## 0. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the manager holds every ruling's CURRENT form in context, and finds existing plans on first need | manager, owner | decisions index under its 48 KB soft cap, every D-id present, 0 `?` after 1.S8; read whole at wake and re-read after a compaction (post_compact.sh, main role, prints the instruction); the plan index read the first time a session looks for existing plans, never inlined (D192 item 7); currency checked per statement (§5.3) |
| G2 | one command prints exactly one entry, at the level asked for | manager, lanes | `scripts/entry D47` prints D47 with all four addenda and nothing else; every witness and plant of appendix B holds; 0 owner-table rows outside their entry |
| G3 | one format, one linter, one accessor for every tracker that fits | maintainers | one linter (plan_lint folded in at T2), one accessor; per-file differences are rows in ONE profile table (§2.4) |
| G4 | no citation breaks | everyone | `doc_cites.py`: every cite that resolved before unit 1 resolves to the same owner-table rows after (appendix C); 0 ids renumbered; then C13 on every commit against a baseline that only shrinks |
| G5 | an index statement never says more or other than its details, and states the CURRENT ruling | owner | 100% of statements pass a fresh opus critic's seven questions with the inbound list (§5.3); every batch's planted lines caught |

Priority on conflict: G4 > G5 > G1 > G2 > G3. Non-goals: rewriting details
text; changing what a decision says; append-only journals and logs (§4).
Known exception to the order, stated: unit 1 lands the index with `?` lines
(old titles) before 1.S writes statements, so for that window G5 is unmet by
design; a `?` line is not acted on (read `entry` first; §6).

## 1. Census

Sizes are bytes at main 6638e3679 (decisions.md and plan.md are
byte-identical at e9687de27, the re-check's build tree). Every count below is
re-taken by `doc_census.py` at the unit's build commit; none is an input.

### 1.1 Candidate files

Fourteen files were measured: appendix F. In short: decisions.md 832 KB,
191 ids under 198 headings in three forms; plan.md 468 KB, 339 rows (296
not-started); plan_row_bodies/ 21 bodies; plan_completed.md 1.2 MB, 397
heads; known_issues.md 467 KB, 134 ids; upstream_issues.md 70 KB, 25 ids.

Decisions shape: 193 addendum MARKERS by the §5.2 scan at e9687de27 (250
candidate lines, 57 mentions excluded), in five typographies including 13
plain-line `D122/D123 ADDENDUM k` markers; 46 sit outside their entry's
`^## Dn` cut (36 id-named inside a later entry, among them D122.a4 in D123
and D123.a8 in D124; 7 own `## Dn ADDENDUM` headings; 3 id-less D89 markers
in D94); numbering shapes the rev-1 rule could not keep (appendix A). D47's
two load-bearing addenda are top-level headings after D48, so reading `## D47`
alone today misses part of D47's current ruling. Supersession is prose (no
field). Cites tree-wide: ~36k `Dn`, ~26k `Kn`, ~2.5k `Dn add. k`/`Dn
addendum k`, ~1k dotted `Dn.k`: ids AND addendum numbers are load-bearing
(appendix C).

Plan shape: head lines total 36.2 KB with child indents; everything else in
the row is ~430 KB.

### 1.2 Who reads what, and how

The reader table (grep-found; each row moved by a named unit in §5) is
appendix H: parsers, structural lists, hooks (installed ONCE in the common
git dir), post_compact.sh (role-split), gestalt's heartbeat prompts, skills,
line cites (appendix E; three in pcrec-bench), the manager's memory (outside
the repo: a manager step per unit), CLAUDE.md/NOTES.md pointers, id cites
in tests and src (one emitted string; name-keeping saves an abi event).

Today a ruling is a grep for `^## D26` plus a Read of a line range (3-36 KB,
missing misplaced addenda).

### 1.3 Files a session loads at start

Today's always-on manager load is ~85 KB (appendix F); §3 prices what the
decisions index adds.

## 2. The format

A file that adopts it is a PAIR:

- the INDEX keeps the file's current name (decisions.md, plan.md,
  known_issues.md), so every prose pointer ("decisions.md D26") and the one
  emitted string still land;
- the DETAILS file is `<name>_details.md` beside it, ONE per index (D192
  answer 2).

The shape (index + details + archive tier) has siblings in the tree:
MEMORY.md + fact files, CLAUDE.md + NOTES.md (out until §9's triggers),
plan.md + plan_row_bodies/ + plan_completed.md (absorbed; archive kept).

### 2.1 Index entry

One line per entry (plan rows: one line, or two for started/blocked rows).

    - <ID> <slug> <state>[ a<k>] — <statement>[ (+<n> more)][ {<keywords>}]

| field | rule | why |
|---|---|---|
| ID | existing id, never renumbered (`D26`, `K139`, `U22`; plan keeps `[TAG]`) | G4 |
| slug | per profile (C5): decisions/known/upstream `^[a-z0-9]+(-[a-z0-9]+){1,3}$`, ≤ 28 chars, unique in the profile; plan: the `[TAG]` itself. PROVISIONAL `-` only on a CONVERTED line until 1.S writes it | a recall handle; mechanical slugs collide |
| state | decisions: `live`, `sup>Dm`, `part>Dm` (statement = the live remainder), `retired`, `absorbed>WHERE`, PROVISIONAL `?` (converted lines only). Known/upstream: units 3/4 (§10). Plan: `STATE:<s>` | supersession becomes a field |
| a<k> | count of `### ID.aN` headings in the details entry (notes excluded); the linter checks it | forces an index touch at every addendum; NOT a faithfulness control |
| statement | ONE sentence, ≤ 200 characters, present tense, the CURRENT ruling with every addendum and later entry's change applied (§5.3). Shape `<topic>: <rule>[; <rule>...].` No rationale, dates, history or lane names. A `?` line carries the OLD TITLE verbatim instead, exempt from C4 | what a session pattern-matches when about to act |
| (+n more) | n = rulings the statement leaves out; REQUIRES a rulings list, n = its unstarred lines (C11) | compression allowed, silent omission not |
| keywords | optional, ≤ 40 characters, only words absent from slug and statement, each TRUE of the current ruling | grep recall |

**One ruling** = one operative clause a session could act on by itself: a
numbered or bulleted decision, a RULED paragraph, a consequence that changes
what is built, tested or refused. Not rulings: rationale, provenance,
revisit-when, measured facts, status or LANDED notes.

**Rulings list** (written with the statement, checked with it): a block right
under the details heading, one line per CURRENT ruling, `rK[*] <≤ 160 chars>`,
`*` marking those the statement carries, `(aN)` naming an addendum's ruling.
A ruling a later entry undid is not listed (the state says `part>`). Entries
whose statement carries every ruling have no list and no `(+n)`. Worked
examples (D26 8 rulings, D47 10, D191 15): appendix D. The list is the one
non-verbatim text in a details entry, marked by its `rulings:` label; unit 1
writes none.

Superseded, retired and absorbed entries shrink to ≤ 80 characters naming
what replaced them.

Plan rows keep their head line (title cap 100 → 90) and gain ONE second line
only when started or blocked:

    - [TAG] STATE:<s> — <title ≤ 90>
      now (<ISO date>): <≤ 160 chars: where it stands and the next step>

`now` is the status of record, rewritten in place, REQUIRED on started and
blocked rows and FORBIDDEN elsewhere. A not-started row's next step or
trigger stays OUT of the index (D192 answer 3); the accessor supplies it at
level 1. Children stay nested by two spaces. Sections stay. The Policy
section shrinks at unit 2 to a pointer at `docs/dev/doc_format.md` plus the
plan-only rules.

### 2.2 Details entry

    ## <ID> <slug> — <the old heading's text after the id and its separator, verbatim>
    [rulings: block, when the statement has (+n); none in unit 1]
    <body, verbatim>
    ### <ID>.a<N> — <date>[, <who>]: <title>
    [(was: "<full old marker text>")   heading-form markers only]
    <addendum body, verbatim>

- An entry runs from its `## ` heading to the next `## ` heading; a body
  never uses a level-2 heading (C10). The heading keeps the old text after the
  id verbatim (D98's two continuation lines are joined, D98 only).
- **Ownership** comes from the OWNER TABLE (§5.2, appendix B), never from
  position: a marker naming its id belongs to that id; an id-less one is
  ruled by hand (D89's "Addendum 2-4" inside D94 belong to D89).
- **The addendum heading** is copied from the table's `date`, `who` and
  `title` columns, which the CENSUS derives by appendix B's declared rule
  (the converter never derives them). C3's grammar:
  `^### D[0-9]+\.a<N> — ([0-9]{4}-[0-9]{2}-[0-9]{2}|-)(, (Frank|owner|manager|kit))?: .+$`.
- **Numbering.** `N` grammar: `[0-9]+(\.[0-9]+)?[a-z]?` (`D155.a4.1`,
  `D123.a3a`); C6 orders 4 < 4.1 < 5 and 3 < 3a < 4. A numbered addendum keeps
  its number; an ordinal word is its number (second = 2); an unnumbered one
  takes the table's ruled number (default: the lowest free number in date
  order, checked against today's cites). A DUPLICATE (D162 addendum 4 twice):
  the first keeps it, the second takes the next free number and the line
  `(was: "<label>", second of two)`. A NOTE: only a label of the form
  `addendum K note` (D168 ×2) is a `class=note` row, a `####` sub-heading
  inside `### Dn.aK`, label verbatim, `new_id` `Dn.aK#i`; D47's numbered
  "RULING-5 ADDENDUM, LANDED NOTE" is an ordinary ruled row (a4). An undated
  label inherits the nearest earlier dated marker's date of the same owner.
- **Extent:** a marker line to the line before the next marker or `## `
  heading, unless the table rules `old_end` (a marker inside a foreign entry
  whose host text resumes after it). The extent, not its first line, is what
  the control compares and hashes (§5.2).
- **Old labels stay greppable**: a heading-form marker (`##`, `###`) gets the
  `(was: ...)` line with its FULL text; an inline marker (bold label or a
  plain `Dn ADDENDUM k` line) stays as the unchanged first body line. So
  `grep 'D163 addendum 7'` still lands, and `entry` resolves the same
  spellings as aliases (§2.3).
- Plan details hold what leaves the row: `filed:`, `next:`/`trigger:`,
  `refs:`, the charter, dated history, children's attributes, in today's
  spelling. plan_row_bodies/ files fold in as their row's details body (§10
  unit 2).
- Cross-links are bare ids (`D26`, `[ANCH-AT]`, `K139`, `D163.a7`), never
  markdown links or line numbers.

### 2.3 The accessor: `scripts/entry`, by level

python3 stdlib, run `-I` (it puts its own directory on `sys.path` to import
the profile module, as scripts/emit_sweep.py does); it reads the profile
table (§2.4), so a new file or a new level is a table row, not code.

| level | content | decisions | plan | known issues |
|---|---|---|---|---|
| 0 | the index line(s) | the line | head line (+ `now`), child head lines | the line |
| 1 | level 0 + the WORKING FIELDS | + rulings list, every `### Dn.aN` heading, `later: D49* D58 ...` (later entries citing it, `*` = a supersede/amend verb) | + `next:`, `trigger:`, `status (date):` / `now`, `refs:` | + first line of each `**Witness:**` / `**Fix:**`, cut at 240 chars |
| 2 | level 0 + the full details entry | whole entry | whole entry | whole entry |

A completed plan row (the archive) prints its head line cut at 160 chars +
`…` at level 0, its attribute lines at level 1, the whole row at 2. An
ARCHIVE ROW is a line matching plan_lint's HEAD_OK form (`- [TAG]
STATE:<s> — ...`, any indent); other `- [TAG]` lines are body text of the row
above. The archive (`completed` profile) is LIVE from T1, read-only.

Commands:

    scripts/entry KEY [-l N] [--rev SHA]  one item; default level 2
    scripts/entry -g REGEX [-in N] [-l N] [-p PROFILE] [-s SECTION] [--state S] [--rev SHA]
    scripts/entry --work [-p PROFILE] [-s SECTION] [-k WORD]
    scripts/entry --levels [-p PROFILE]   print the level and work-view rows of the table
    scripts/entry --over-cap              soft-cap line for scripts/gestalt (§2.4)
    scripts/entry --selftest              planted fixtures: one per routing row, dormant, over-cap

**Routing of KEY** (first match; ids and tags case-sensitive, slugs
lower-case; a plan KEY may be written `PC-3` or `[PC-3]`; each row has a
selftest plant on FIXTURE profiles, so the router is tested before its
profiles wake):

| # | KEY shape | goes to |
|---|---|---|
| 1 | an alias spelling: `Dn add. K`, `Dn addendum K`, `Dn ADDENDUM[ K]`, `Dn <ordinal> addendum`, `Dn addendum YYYY-MM-DD` | decisions, via the table's `old_label`/`old_number`/`date`; a label shared by two rows (D162 a4) prints both, exit 0; an unnumbered alias prints every unnumbered-origin addendum of Dn; a date alias prints the rows of that date |
| 2 | FULL match of a profile id regex (`D[0-9]+`, `K[0-9]+`, `U[0-9]+[a-z]?`) | that profile |
| 3 | FULL match `D[0-9]+\.[0-9]+` (a ruling number, D47.6) | entry Dn at level 2, trailer `ruling 6 is in the body` |
| 4 | an exact `[TAG]` of plan.md, else of the archive | plan wins; the archive only on absence; 2+ archive rows (PC-3, OPT-5, OPT-VMSEED, SR-8) print all, exit 2 |
| 5 | FULL match `(D[0-9]+)\.a(<N grammar>)`, lower-case `a` | that decisions addendum |
| 6 | a lower-case kebab slug | EVERY non-dormant profile's index; 2+ hits exit 2 listing them |
| 7 | anything else | exit 1 |

A KEY routed to a DORMANT profile exits 1 with the trailer `entry: profile P
dormant (unit N)`. A plan tag that full-matches rows 2, 3, 5 or 6 would be
unreachable, so plan_lint gains PL18 at T1 refusing one (0 exist today; the
ten id-shaped tags such as K18-FIX fall to row 4).

- **Item grep** (`-g`): searches each item at level `-in` (0 = index lines,
  the default; 1 = + working fields; 2 = + full details) and prints every
  matching ITEM WHOLE at level `-l`. Items, never raw lines. The archive is
  read only with `-p completed`. CONTENT search is `-g WORD -in 2`.
- **Work view** (`--work`): plan = every `STATE:not-started` and
  `STATE:blocked` row at level 1, by section; known = the open states (§10
  unit 3). It never reads the archive.
- **Plan grammar:** the `single` plan form IMPORTS plan_lint's `HEAD`,
  `HEAD_OK`, `ATTR` and `SECTIONS` (one grammar, no second parser); Policy is
  not an item section.
- **`--rev SHA`** reads the pair at that commit (`git show`, read-only) with
  the WORKING TREE's profile table; the form is chosen by which files exist
  at SHA (no details file → the `single` form). Unit 1 adds a read-only
  decisions `single` form (the `^## Dn` cut, trailer `pre-split: addenda
  filed outside the entry are not shown`) so a freeze before the split still
  reads; selftest plants one SHA per form.
- Output ends with `entry: <n> items (profile <p>, level <l>)`; exit 0 found,
  1 none, 2 ambiguous.
- With no tool, one line still prints one entry:

      awk '/^## /{p=($2=="D26"||$3=="pcre2-compat-tiers")} p' docs/dev/decisions_details.md

rows_check.py's cut works unchanged on the details file.

### 2.4 One profile table, one linter, one test section

The PROFILES table is one declared module, `scripts/doc_profiles.py`, read by
the accessor, the linter, the hooks and the selftests:

| profile | index / details | id | states | soft cap: statement / line / FILE | level-1 fields | work view | form |
|---|---|---|---|---|---|---|---|
| decisions | decisions.md / decisions_details.md | `D[0-9]+` | live sup part retired absorbed `?` | 200 / 300 / 48 KB | rulings list, `### ID.aN` headings, `later:` | — | dormant until unit 1 |
| plan | plan.md / plan_details.md | `[TAG]` | the four STATEs | title 90, now 160 / 2 lines / 48 KB | `next:` `trigger:` `status (…):` `now` `refs:` | not-started + blocked, L1, by section | `single` until unit 2, then `pair` |
| completed | plan_completed.md (archive, no index) | `[TAG]` | as written | — | the row's attributes | — | `archive`, live from T1 |
| known | known_issues.md / known_issues_details.md | `K[0-9]+` | unit 3's mapping | 180 / 280 / 32 KB | `**Witness:**` `**Fix:**` first lines | open states, L1 | dormant until unit 3 |
| upstream | upstream_issues.md / upstream_issues_details.md | `U[0-9]+[a-z]?` | unit 4's census | 180 / 280 / 12 KB | unit 4's | unit 4 | dormant until unit 4 |

Each row also carries: `linter` (the script that lints it: plan_lint for
plan/completed until T2, doc_lint after), `extra_paths` (plan:
`docs/design/plan_row_bodies/` until unit 2), `floor` (C9: decisions = the
census's id count at the build commit, raised by each landing re-run), its
section list, and its exemption prefixes. Caps count CHARACTERS (titles hold
`—`, `×`, `−`), file caps bytes.

**One cite-form table** (R2-27), in the same module: form regex → resolver →
exemption prefixes → baseline file → fail or warn. C8 and C13 are its first
two readers (unit 1); spec_history and PL14 move onto it under [CITE-FORMS]
(§9).

**Soft caps (D192 answer 4).** A FILE cap never fails anything: doc_lint
prints `WARN C4 <file> ...` and exits 0. `scripts/gestalt` gains ONE row in
its ROWS table, kind `docs`, line `L_docs`, replacing its `docidx`
PLACEHOLDER: threshold "a `pair`-form index over its cap, or the accessor
unavailable". It runs `timeout 2 python3 -I "$here/entry" --over-cap` (or
`$GESTALT_ENTRY`, the file's test-hook convention), which prints at most
ONE line, then its trailer:

    docs: decisions.md 51.3 KB over soft cap 48 KB (+3.3 KB, 107%)
    entry: over-cap checked 1 pair index, 1 over

Several over-cap indexes join on the one line with `; `. KB = 1024 B, one
decimal, TRUNCATED; pct = floor(100 × size / cap). gestalt keeps only the
`docs:` line; a non-zero exit, a timeout or a missing trailer prints `docs:
unavailable` (K35). Under `--all`, a row whose line is EMPTY prints nothing:
one general rule that replaces gestalt's idle-held kind-name special case,
so `--all` stays ≤ 12 lines. The trailer counts the population: 0 pair
indexes from T1 to unit 1 (stated, not hidden). Plants: appendix J.

Common rules (each FAILS, except the file cap):

- C1 ids unique in the index; C2 bijection: every index id has one details
  heading and every heading one index entry, slugs equal; C3 heading grammar
  (§2.1, §2.2); C4 field caps (fail; a `?` line exempt) and file cap (WARN);
  C5 slug per the profile's grammar, unique, or `-` on a converted line; C6
  every `### ID.aN` inside `## ID`, numbers unique and rising (§2.2 order);
  C7 every id in an index line resolves; C8 below; C9 the profile's parsed
  entries ≥ its `floor` (K35); C10 no level-2 heading inside a details body;
  C11 `(+n)` equals the rulings list's unstarred lines, a list iff n > 0;
  C12 (from unit 2) no file under docs/design/plan_row_bodies/; C13 below.
- **C8** (per profile, from its `pair` form): no line cite of the profile's
  file outside the exemption prefixes. Form
  `<file>\.md:~?[0-9]+(-[0-9]+)?(, ?[0-9]+)*`, counted when the cite is NOT
  under a `pcrec-bench/` path (relative `../dev/decisions.md:N` counts). Plants:
  a positive, `:~N`, a comma list, a `../` path, a bench-path negative, an
  exempt-prefix negative. `docs/dev/plan_completed.md` is exempt for EVERY
  profile (append-only); PL14 keeps the plan profile's own rule.
- **C13**: every `Dn.aN` and alias-spelled cite (appendix C forms) outside
  C8's exemption prefixes resolves, except the rows of the committed BEFORE
  baseline `docs/dev/doc_index/dangling_before.tsv` (written by doc_cites.py
  in 1.0; today e.g. the PROPOSED `D155 addendum 6` ×5). The baseline only
  shrinks: a row whose cite now resolves or is gone must be deleted in the
  same change.
- **The ratchet** (`?` and `-` on converted lines, counted once per line): a
  committed count per profile in `docs/dev/doc_index/ratchet.tsv`; the
  linter requires count == baseline (more refused; fewer means the baseline is
  lowered in the same change, spec_history's baseline.tsv pattern), so CI and
  `make test` need no history. BIRTH: the commit that turns a profile
  `pair` writes its row (unit 1: one per converted line). A LANDING RE-RUN
  that converts entries appended on main since C0 raises the row in the
  landing commit, the one sanctioned raise, printed by the converter. After
  unit 1 a new entry carries no `-` or `?` (§2.7).
- `--selftest` plants one violation per rule per profile, plus an over-cap
  file that must WARN and exit 0; `--staged` lints staged content; `--stale`
  (exit 0) reports per profile (§10 R2-25).
- **The section.** T1 creates `tests/doc_lint/` (+ its CLAUDE.md) and
  `make test-doc-lint` (entry's selftest; unit 1 adds doc_lint's decisions
  profile; T2 folds plan_lint in). Born in T1 so the structural lists move
  once: a TEST_SECTIONS member + `.PHONY`, the recipe's FIRST line touching
  `$(TEST_TRAILER_DIR)/test-doc-lint.ran`; a tests/ci/shards.tsv row after
  test-plan-lint (`test-doc-lint 2 2 ESTIMATED`); a tests/lib/san_excluded.txt
  row `tests/doc_lint/run_doc_lint.sh NO-C-RUN`; tests/CLAUDE.md;
  docs/testing.md.
- **Hooks.** `make hooks` installs into the COMMON git dir, so ONE installed
  copy serves every linked worktree, old trees included. Rule: a tree WITHOUT
  `scripts/doc_profiles.py` predates the format and keeps today's "missing in
  this tree; skipped" line; a tree WITH it must have every linter its
  non-dormant profiles name, else the hook FAILS naming the path. pre-commit
  reads `doc_profiles.py --paths`: one `linter<TAB>path-regex` line per
  non-dormant profile (index, details, `extra_paths`). Plants: a missing
  linter in a tree with the module (pre-commit and pre-push-light fail), a
  tree without the module (skip). Every landing that changes a hook re-runs
  `make hooks HOOKS="pre-commit pre-push-light"` on each box that has them.

### 2.5 Worked examples

Appendix D: the decisions index lines for D26, D47 and D191 with their
rulings lists and inbound lists, each checked against §5.3's seven
questions, and the D47 details headings as the §2.2 rule derives them.

### 2.6 Where the format is defined

The format (this section's rules, without census or migration) moves to
`docs/dev/doc_format.md` in T1.

### 2.7 Writing an entry from now on

A new ruling = the details entry + the index line, in one commit (C2), with
slug, state and statement written at once (the ratchet refuses a new `-` or
`?`). An addendum = the `### ID.aN` block + the `a<k>` bump, with the
statement and rulings list rewritten if the ruling moved. A ruling that
changes an EARLIER entry's ruling also rewrites that entry's state and
statement in the same commit. Statements are written by an opus session (D192
answer 1). The q and pcrec-manager skills' "write the ruling" steps, and
docs/dev/NOTES.md's decisions bullet, name both files and the at-once rule.

## 3. Size targets

Measured basis: the worked lines (decisions 222-276 B, mean 252); a `now`
line is up to 185 B.

| index | entries | per entry | projected | soft cap |
|---|---|---|---|---|
| decisions.md | 192 | 252 B at the examples' mean; superseded ≤ 100 B | 40-48 KB; 1.S1 measures it (the `?` index of unit 1: ~31 KB) | 48 KB |
| plan.md | 339 rows; 38 `now` | heads 36.2 KB + now ≤ 6.7 KB | 42.9 KB | 48 KB |
| known_issues.md | 134 | open ~180 B; FIXED/CLOSED ≤ 80 B | ~17 KB | 32 KB |
| upstream_issues.md | 25 | ~170 B | 4 KB | 12 KB |

Runway: decisions grows ~8.5 KB a month. Starting at 40-48 KB, the soft cap
is reached in weeks, possibly on day one; then the gestalt line fires every
heartbeat, which is the owner's chosen revisit trigger (D192 answer 4). The
levers: shrink superseded/absorbed entries, shorten single-ruling statements,
move detail into the rulings lists.

**Which index is read when (owner, D192 item 7).** The DECISIONS index
(~46 KB, ~12k tokens at an estimated 4 B/token) is read whole at wake and
re-read after a compaction (post_compact.sh, main role, prints the
instruction; it inlines nothing). The PLAN index is read on FIRST NEED, the
first time a session looks for existing plans (before chartering, or "is
there a row for X"), through `scripts/entry`; it is never inlined. Lanes
load neither index; they call `scripts/entry`.

## 4. Other files

Verdicts with reasons: appendix I. APPLY: known_issues.md (unit 3),
upstream_issues.md (unit 4, on its trigger). ARCHIVE TIER: plan_completed.md.
ABSORBED: plan_row_bodies/ (unit 2). PROPOSAL: the kit ledgers (§8). SAME
FAMILY, kept out: MEMORY.md, CLAUDE.md/NOTES.md (§9). DO NOT APPLY: ideas.md,
learnings.md, testing.md, the journal and ledger, REFERENCES.md, wake/owner
files.

## 5. Migration plan

Every split is a re-runnable TRANSFORM: the lane delivers a converter plus
its output, and the landing re-runs it on main HEAD (§5.2). Order: **T1 → 1.0
→ 1 → 1.S → T2 → 2 → 2.S → 3 → 4**; K beside them once vetted. lane/docfmt
(D192) merges before 1.0 branches, so the census sees every entry.

| unit | what | tier | readers moved in the same unit |
|---|---|---|---|
| T1 | `scripts/doc_profiles.py`, `scripts/entry` (levels, routing, item grep, `--work`, `--rev`, `--over-cap`, `--selftest`), the gestalt `docs` row, PL18, `docs/dev/doc_format.md`, the `test-doc-lint` section. Plan `single`, completed `archive` live, others dormant. ACCEPTANCE: `make test-doc-lint test-ci-shards test-codegen test-claudemd-size test-plan-lint testscripts strict` green, appendix J's plants each red before its fix | sonnet (+ optional D27 test cell) | scripts/CLAUDE.md (4084 of 4096 B: FIRST move the `fullsuite_job.sh` parenthesis, ~450 B, to scripts/NOTES.md, then add the two scripts; run `scripts/check_claudemd_size.sh --all`); gestalt header + scripts/tests/gestalt.test; .claude/skills/pcrec-manager/monitoring.md (both heartbeat prompts: "docs over soft cap: record it, it is the owner's revisit trigger, no lane"); root CLAUDE.md situation row ("look up a plan row, choose work (`entry --work`), or search plan content (`-g WORD -in 2`) → `scripts/entry`"); the section's lists (§2.4); tests/doc_lint/CLAUDE.md; docs/dev/CLAUDE.md (doc_format.md; 539 B headroom); tests/plan_lint selftest (PL18 plant) |
| 1.0 | `scripts/doc_census.py` + the owner table with its hand rulings, `scripts/doc_control.py` (+ `--selftest`, appendix B's plants), `scripts/doc_cites.py` (resolver + `--inbound`); BEFORE-run committed with `dangling_before.tsv`. ACCEPTANCE: census gate green, every plant red, the table reviewed | sonnet; ruled rows reviewed by the manager; NOT the converter's author | docs/dev/doc_index/ (new, its CLAUDE.md) |
| 1 | decisions split by converter (§2.2), index of `?` lines (old title verbatim, slug `-`); `entry`'s decisions profile wakes (aliases, `later:`, the decisions `single` form for `--rev`); doc_lint.py with the decisions profile (C1-C13, the cite-form table, the ratchet row); the cite-to-id pass over the 26 live decisions line cites (appendix E); AFTER-run. ACCEPTANCE: appendix B's witnesses; control green; idempotence; resolver before = after; `make test-doc-lint strict` green | sonnet (mechanical) | rows_check.py LEDGERS + stream_support.tsv paths; pre-commit (`--paths`) + `make hooks` per box; post_compact.sh (MAIN role only: one re-read line); skills: pcrec-manager (wake reads the decisions index; `?` rule), q (writes both files at once), pcrec-critic (freeze both files; COMMONs use `entry --rev`; rulings by id, not `file:line`), pcrec-memfn-manager (main's file list); root CLAUDE.md (situation row adds rulings; "Where things are"); docs/dev/CLAUDE.md; docs/dev/NOTES.md (decisions write bullet); MANAGER STEPS: memory `pcrec-grep-plan-before-chartering` (decisions part); a pcrec-bench `[inbox]` note (D78: "decisions.md is an index; full entries via `scripts/entry Dn` or decisions_details.md; line cites are void"; the manager writes it, never a lane); D27 cell briefs that allowlist decisions.md add decisions_details.md |
| 1.S1-S8 | statements, slugs and rulings lists, 8 batches of 24 ids (§5.3). S3-S8 only after S1 passes. ACCEPTANCE of S8: ratchet row 0 | OPUS writer + fresh OPUS critic | none |
| T2 | plan_lint folded into doc_lint as the plan profile (PL01-PL18 unchanged in effect; `--stale` per §10) | sonnet | Makefile, shards.tsv, san list, tests/plan_lint/ into tests/doc_lint/; pre-commit; pre-push-light (module rule of §2.4); hooks.test pins; the `--stale` mentions (appendix H); docs/testing.md; skills. SHIMS at both old paths until every box re-ran `make hooks`. ACCEPTANCE: `make test-ci-shards test-codegen test-doc-lint testscripts` green + the missing-linter plants |
| 2 | plan split by converter (§10 unit 2 first); `single` deleted | sonnet | boxqueue comment; skills' plan recipes; pcrec-manager: "read the plan index on first need (`scripts/entry`)"; pcrec-critic deny and freeze (plan_details.md); vlookbehind.md hunk; the plan_row_bodies readers; MANAGER STEP: memory `pcrec-grep-plan-before-chartering` (plan part) |
| 2.S | the 38 `now` lines and 36 over-cap titles | OPUS writer + critic | none |
| 3 | known_issues split (§10 unit 3 first); statements for open entries only | converter sonnet; opus batches + critics | known_fail instructions; pcrec-critic freeze; MANAGER STEP: memory `pcrec-done-line-verify-claims` |
| 4 | upstream_issues (§10 unit 4 first) | sonnet; statements OPUS + critic | pcrec-critic freeze |
| K | main sends §8 to the kit | manager | none; the kit decides |

**Landing.** Freeze: no merges 2026-11-11 01:00 until the full suite ends
(~14:00). T1 writes no ruling file and may land before 01:00 if ready and
light. Units 1 and 2 are the BIG transforms: ONE per quiet window
(20:00-01:00 is the owner's hold). Unit 1 lands with no open branch carrying
a decisions.md hunk (the landing brief lists them by `git diff --stat
main...BRANCH -- docs/dev/decisions.md`; each merges first or re-targets its
hunk to the pair by §2.7). Unit 2 needs every lane merged. **D153 check:**
before unit 1 the manager confirms with the stream thread that no in-flight
remodel branch edits rows_check.py or stream_support.tsv.

### 5.1 Standing questions (docs/design/CLAUDE.md)

1. Measurement regime: RELEVANT only for byte/character sizes and the token
   estimate (4 B/token; a 2x error moves the soft caps, not the design).
2. Independent control: RELEVANT; §5.2 and §5.3 are its answer. The census,
   owner table and control are a script the converter's author did not
   write; the scan reads every line (no spelling list); the control compares
   EXTENTS from the table, byte-exact, so a converter that moves, reorders,
   drops or adds a line inside one owner fails; each rule has a plant that
   must go red (appendix B). a<k> is NOT a faithfulness control. A statement
   is checked by a critic independent of its writer, against the details and
   an inbound list neither wrote, with planted lines as the critic's control.
   C9 floors, C8/C13 trailers and the `--over-cap` trailer count their
   populations.
3. What moves when regenerated: the indexes are hand-written; converters run
   once per unit and once per landing re-run; the owner table only appends.
   No emitted byte, abi or spec moves (process docs only).

### 5.2 Census, owner table, control and cite resolver (units 1.0 and 1)

- **Scan** (`doc_census.py`): EVERY line of decisions.md. Strip an optional
  prefix (`>`, a list marker `- `/`* `/`N. `, `**`, or `#`s), kept as the
  `class` column (h2, h3, bold, bullet-bold, bullet, quote, plain). A line is
  a CANDIDATE when the remainder's first 120 characters carry `addend` (any
  case) or `Dn add.`.
- **Marker or mention**: a candidate is a MARKER when its LEADING LABEL
  names an addendum: the label is the bold span, or the heading text, or the
  plain line's start, each cut at its first ` — `, `(` or `:`, and it must
  match appendix A's label regex (optional id, optional tag like
  `RULING-5`, optional ordinal, the word addendum, optional number or date,
  optional `note`/`, LANDED NOTE`). A plain-class label must begin with its
  id (`D122 ADDENDUM 4`), since a bare "addendum 2" at a line start is a
  wrapped sentence. Every other candidate is a `mention`, listed with that
  reason. At e9687de27: 250 candidates = 193 markers + 57 mentions; the
  number of record is the census's count at the unit's build commit.
- **Gate**: the census FAILS on (a) an id-less marker without a hand ruling,
  (b) a line-start `Dm ADDENDUM|addendum|add.` (any class) inside entry Dh,
  m ≠ h, with no table row, (c) an old heading matching the new grammar.
- **Owner table** (appendix B): one row per marker with its EXTENT
  (`old_line..old_end`), `extent_hash` (sha256 of the extent's bytes), full
  `old_label`, `class`, `owner`, `new_id`, `date`, `who`, `title`. The
  converter copies rows; it refuses a marker with no row (matched by
  `old_label` + `extent_hash`).
- **Control** (`doc_control.py`, from the table, never from the converter's
  output): (i) the distinct id set is equal; (ii) BIJECTION: per owner, the
  `### Dn.aN` headings == the table's `new_id`s (notes: `####` headings ==
  note rows); (iii) EXTENTS, byte-exact with blank lines: each row's extent
  equals the text under its new heading after removing that heading and its
  one `(was:)` line, and each entry's body (its old `^## Dn` cut minus every
  extent inside it) equals the text between its `## ` heading and its first
  `###`; only leading/trailing blank lines of a piece are trimmed; (iv)
  HEADINGS: a `## ` heading's text after the slug equals the old heading's
  text (D98 joined), a `###` heading equals the table's columns, a `(was:)`
  equals `old_label`; (v) FORMS: exactly one `(was:)` per heading-form row,
  none elsewhere, 0 `rulings:` blocks in unit 1. The per-owner multiset of
  non-blank lines stays as a coarser sixth check. `doc_control --selftest`
  plants appendix B's list (P1-P21); each must go red by its named clause.
- **Already converted**: in the index, `- <ID> ` lines are converted and any
  `## ` heading is old form; in the details, `^## <ID> (<slug>|-) — ` is
  converted.
- **Idempotence:** `convert(convert(x)) == convert(x)` byte-identical, and
  converting an index with appended old-form entries leaves every converted
  byte unchanged.
- **Landing baseline:** the lane converts at its commit C0; the landing
  re-runs on HEAD H: census on H (new markers append rows; an id-less one
  stops for a ruling), converter, control recomputed from H, idempotence,
  resolver before/after on H's tree, the ratchet raise (§2.4).
- **Cite resolver** (`doc_cites.py`): appendix C's forms, population =
  outside C8's exemption prefixes; BEFORE resolves through the table on the
  old file, AFTER through headings and aliases; every cite's resolved row set
  must be equal; cites dangling BEFORE go to `dangling_before.tsv`. After
  unit 1 the same code is C13.
- **Cite-to-id pass** (unit 1, appendix E): a line cite with an id NAMED
  beside it becomes that id; an id-less one maps by CONTENT ANCHOR (the cited
  words found in the entry at the census commit), never by line offset;
  every disagreement between line and named id is listed in the lane report.

### 5.3 Statements: writer, critic, inbound list (1.S, 2.S, 3, 4)

Before each batch, `doc_cites.py --inbound` lists for every id each line in
a LATER entry (owner-table attribution) citing it in any form, flagged where
the line carries a declared supersede/amend verb (supersed, amend, replac,
revers, overrid, retir, struck, settl, re-open, withdraw). The writer (OPUS)
reads the whole details entry plus its inbound lines and writes slug, state,
statement, rulings list, keywords, never from the old title. A FRESH opus
critic, one per batch, reads the same and answers per entry:

1. does the statement add a ruling the details do not make;
2. contradict the current ruling;
3. state a rule an addendum or a later entry replaced;
4. is the rulings list complete and only current;
5. does each starred line appear in the statement (n itself is C11's);
6. is the state right given the inbound list;
7. is every keyword true of the current ruling?

The batch carries PLANTED lines the critic must flag (appendix D; the wrong-n
plant is replaced before 1.S, §10 R2-26); a batch whose critic misses one is
re-run with a fresh critic. Disputes go to the manager. Gate: S3-S8 start
only when S1's report shows every plant caught and 0 open disputes.

### 5.4 Cost, triggers and stop points

| unit | lanes | landing | trigger (D77) | if the work stops here, what stays |
|---|---|---|---|---|
| T1 | 1 sonnet (+ D27 cell) | light; before 01:00 allowed | D192 answers 3, 4 | `entry --work` on today's plan, `--rev`, doc_format.md |
| 1.0 | 1 sonnet | with unit 1 | D192 | the owner table: the first complete record of every addendum's owner |
| 1 | 1 sonnet | quiet window A | D192 | every D entry whole with its addenda (G2), C13, a title index |
| 1.S1-S8 | 16 opus | 8 light | D192 answer 1; S3-S8 gated on S1 | statements for finished batches |
| T2 | 1 sonnet | light + hook re-install on 3 boxes | unit 2's go | one linter |
| 2 | 1 sonnet | quiet window B | D192; §10 unit 2's fixes | plan index + details + work view |
| 2.S | 2 opus | light | with unit 2 | `now` lines under cap |
| 3 | 1 sonnet + ~4 opus | light | D192 answer 6 | known index |
| 4 | 1 sonnet + 2 opus | light | a re-filed U-n, or upstream_issues.md past 100 KB | upstream index |

Total: ~7 sonnet lanes, ~24 opus runs, ~9 landings; S1's gate is the stop
point.

## 6. Risks

- Index drift: `a<k>`, §2.7; the manager skill gains "read `scripts/entry`
  before quoting or building on a ruling's specifics; never act on a `?`
  line".
- Wrong owner or wrong cut: the every-line scan and gate, the extent control
  and its plants, the witnesses (§5.2, B).
- Transforms vs landings: re-run on HEAD, one per quiet window (§5).
- A reader missed: grep-found (§1.2); outside readers are manager steps.
- Old cites break: numbers kept, resolver before = after, the dangling
  baseline, old labels greppable, aliases.
- Soft caps full on day one (§3): recorded, not acted on (monitoring.md).

## 7. Owner's answers (2026-11-10; recorded as D192)

1. Statements by OPUS lanes, a fresh OPUS critic; no owner read-through
   (§2.7, §5.3). 2. One details file per index (§2). 3. A LEVELED accessor
   with item grep and a work view (§2.3). 4. Soft caps now, revisit later
   (§2.4, §3). 5. Kit ledger: a proposal once vetted (§8). 6. Known issues
   third (unit 3). 7. The decisions index is read at wake; the plan index on
   first need; neither inlined (§3; D192 item 7).

Still open: **should the per-LINE limits (statement 200 characters, plan
title 90, `now` 160) also be soft, or only the file sizes?** Leaning: keep
line limits HARD; a writer can always fix one line on the spot, plan_lint
already refuses over-long titles, and the counted rulings list means the cap
never forces silent omission. A `?` line is exempt (it is not a statement).

## 8. Proposal to the kit (sendable as is)

Appendix G: what pcrec is doing, why, the facts about the two ledgers, and
the ask. Unit K sends it; nothing changes in either ledger without the kit's
answer.

## 9. Later: the general form and its unlocks (NOTED, not built)

General form: a TIERED-DOCUMENT profile table (index | details | archive tier
per file, id grammar, states, per-tier caps, level-1 fields) read by one
accessor and one linter. Each unlock is built only when its trigger fires
(D77):

| unlock | trigger |
|---|---|
| fold the CLAUDE.md/NOTES.md size check into doc_lint | a third size-checker appears, or check_claudemd_size.sh needs a second rule |
| MEMORY.md over-cap line via `--over-cap` | MEMORY.md passes its cap or a brief reports it truncated |
| a `kit` profile for the ledgers | the kit answers §8 with adoption |
| cross-file `--work` | the wake read needs more than two `entry --work` calls |
| "rulings touched since DATE" view | a session acts on a superseded ruling |
| an `entry --deny` list for blinded critics | a critic round's deny leaks through `entry` after unit 2 |
| CITE-FORM family: spec_history and PL14 read the cite-form table ([CITE-FORMS], filed) | T2, or the next cite rule proposed |
| HOOK MANIFEST (path regex → linter → absent-in-tree policy) generated from doc_profiles.py, ending the per-hook "skipped" blocks | T2's hook edit |

## 10. Readiness by unit, and the PLAN items

Each table lists the findings that gate the unit, where rev 3 discharges
them, and the WITNESS that must be red when built from rev 2's text and green
after (plant ids: appendix B for 1.0/1, appendix J for T1).

**T1: ready.**

| finding | discharged in | witness red before the fix |
|---|---|---|
| R2-1 | §5 T1 readers | `check_claudemd_size.sh --all` with the two scripts named and nothing moved |
| R2-2 | §2.4 soft caps | gestalt.test `--all` ≤ 12 with the row printing an empty line (J1); real-tree "silent" over a stub over-cap accessor (J2) |
| R2-3 | §2.4 | gestalt.test `kinds()` names `docs`; a hung stub accessor exceeds 2 s (J3) |
| R2-4 | §2.4, J | fixture pair at 52592 B / 52593 B (106% / 107%) and 52633 B (51.3 KB, not 51.4) (J4) |
| R2-5 | §2.3, §5 T1 | `entry D26` exits 1 with the dormant trailer, not 0 or a crash (J5) |
| R2-6 | §2.3 | `entry FIX-2` prints one row, not two (J6) |
| R2-7 | §2.4, §5 T1 | `sections ran` without the trailer touch; TT-9 `UNLISTED`; check_shards `0 shard rows` (J7) |
| R2-8 | §5 T1 readers | none mechanical: the manager reads both prompts in the diff |
| R2-9 | §2.3 | `--rev` at a pre-T1 SHA serves plan `single` (J8); the Policy template rows are not items (J9); PL18 refuses a planted `[K50]` (J10) |

**Unit 1.0: ready once lane/docfmt has merged.**

| finding | discharged in | witness red before the fix |
|---|---|---|
| R2-10 | §5.2 scan + gate, A, B | census fixture with a plain-line `D122 ADDENDUM 4` inside D123: a row with owner D122 (P20); D122/D123 witnesses |
| R2-11, R2-12 | §5.2 control (ii)-(v), B | P3b, P4, P7, P8, P9, P10, P14, P15, P16, P17, P17b, P18, P19 each red by its clause; P21 (a one-line addendum moved) red on `extent_hash` |
| R2-13 | §5.2 marker rule, A | the census prints 193/57 at e9687de27; the wrapped "ADDENDUM, is ..." and "addendum 2 —" lines are mentions |
| R2-14 | §2.2, B | C3 refuses a heading off the table's columns (P16); D168's notes are `####` (witness D168); D47.a4 present |
| R2-15 | A | the D98 join applied to any other heading (P11) |
| R2-16 | §2.4, §5 | C9 refuses a fixture with fewer entries than `floor` |

**Unit 1: ready once 1.0 is in and T1 has landed.**

| finding | discharged in | witness red before the fix |
|---|---|---|
| R2-17 | §5.2, E | the 16 cites whose line falls in the preceding entry map to their named id (e.g. "D46 (decisions.md:4005)" stays D46) |
| R2-18 | §2.1, §2.4 | `make test-doc-lint` on the `?` index (33 titles > 200 characters) |
| R2-19 | §2.4 C13, C | C13 on today's tree without the baseline (D155 addendum 6); a resolved baseline row left in |
| R2-20 | §2.4 C8, E | C8 plants `:~N`, comma list, `../dev/decisions.md:N` |
| R2-21 | §2.4 hooks | a commit in a tree without doc_profiles.py (skip, not fail); a missing linter in a tree with it (fail) |
| R2-22 | §2.4 ratchet | a new entry with `-`; a landing re-run's raise without the baseline row |
| R2-23 | §5 unit 1 readers | none mechanical: the bench note and D27 step are manager steps, checked at landing |
| R2-24 | §0, §3, §5 | none mechanical: post_compact.sh's kit branch carries no decisions line (diff) |

**1.S: ready once R2-26 is fixed here** (and unit 1 has landed). Its gates
remain round r1's F3/F4 (§5.3, appendix D) plus R2-26.

**PLAN items, each fixed in this doc before the named unit's go:**

- **Before 1.S (R2-26):** replace the wrong-n plant (C11 catches it before
  the critic) with a reader-only plant. Leaning: a starred rulings line
  missing from the statement (question 5), and a rulings line an inbound
  entry undid (question 4).
- **Before T2 (R2-25):** doc_lint `--stale` reports per profile: decisions =
  cap headroom + ratchet count; plan = plan_lint's three stale classes (stale
  started rows, unresolved refs, MERGED-but-open) + headroom; T2's acceptance
  diffs the plan part against `plan_lint.py --stale` on the same tree.
- **Unit 2 (plan):** the plan `?` slot (leaning `now? (<date>): <today's
  status line>`, exempt from C4, counted by the ratchet, cleared by 2.S) and
  `now` caps for the 31 status lines over 160; the ~46 plan_row_bodies
  readers and where a COMPLETED row's body goes; C12; the vlookbehind.md
  hunk; the archive profile's moved-row shape; the critic deny/freeze; the
  memory step.
- **Unit 3 (known issues):** a state-mapping table (K24, K39, K58, K77 must
  land in the work view), a sub-record rule for the five "original entry"
  headings, FIXED/CLOSED shrink to ≤ 80 characters; the memory step.
- **Unit 4 (upstream):** the real states and the id-less heading's fate.
