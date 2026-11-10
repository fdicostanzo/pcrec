# One format for ruling and tracker files: a tight index plus greppable details (rev 2)

**Rev 2 (lane docfmt2, 2026-11-10):** applies the manager's rulings on critic
round `docs/dev/reviews/2026-11-10-r1-docfmt.md` (every proposed disposition
accepted). Plan row [DOC-INDEX]; the owner's six answers are D192. Worked
tables moved to `doc_index_format_appendix.md` (A-I). Changes by finding:

| id | change |
|---|---|
| F1 | census corrected (appendix A); an OWNER TABLE from a script other than the converter, hand rulings for id-less markers, a per-owner multiset, numbering rules, witnesses; a<k> is no faithfulness control (§2.2, §5.2, appendix B) |
| F2 | G4 gets an instrument: `scripts/doc_cites.py` before/after unit 1, then doc_lint C13; `entry` aliases for old spellings; old labels stay greppable; `Dn.k` defined (§0, §2.3, §5.2, appendix C) |
| F3 | an inbound-cite pass for writer and critic; seven critic questions (state, n, keywords added); level 1 prints `later:` (§5.3, §2.3) |
| F4 | "one ruling" defined; a RULINGS LIST beside any statement with `(+n)`, n checked mechanically (C11); the three examples rewritten (§2.1, appendix D) |
| F5 | exclusion set, "already converted" test, idempotence, landing baseline recomputed from HEAD (§5.2) |
| F6 | the lint section is born in T1; T2's structural readers, hooks fail instead of skip, glob from the profile table, re-install per box, T2 acceptance (§2.4, §5) |
| F7 | C8's population, exemption set, per-profile waking, cite-to-id pass, path anchoring + bench-path plant, the critic recipe (§2.4, §5, appendix E) |
| F8 | accessor routing by full match, slug lookup across profiles, `.aN` rules, plan wins over the archive, completed-row level 0 (§2.3) |
| F9 | per-profile slug grammar; provisional slug `-` and its writers (§2.1, §2.4 C5); the plan `?` slot and `now` caps are PLAN for unit 2 (§10) |
| F10 | sizes recomputed; the plan index's always-on status is the manager's choice (§3) |
| F11 | G1 at wake and after compaction; `entry --rev`; freeze names details files; content greps (§0, §2.3, §5); unit 2/3 parts PLAN (§10) |
| F12, F13 | PLAN, owned by unit 2 (§10) |
| F14 | known/upstream census corrected now (§1.1); state mapping and sub-records PLAN for units 3/4 (§10) |
| F15 | cost, trigger and stop-point table; order T1 → 1 → 1.S → T2 → 2; one big transform per quiet window; D153 check; 1.S3-S8 gated on batch 1; FIXED known issues shrink (§5, §5.4, §10) |
| F16 | the family named; unlocks with triggers in §9 (no plan rows) |
| F17 | census nits (§1.1, appendix A) |

DESIGN ONLY: nothing here converts a real file. Owner's ask (Frank,
2026-11-10): decisions and plan should each be a short "simple statement" file that covers most cases and is easy to recall, plus a
details file from which one entry is easy to grep out by its slug; formalize
the shared format; say which other files fit. The consumer is the AI manager
session, which keeps the index in context, and its lanes, which read details
on demand through the accessor.

## 0. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the manager holds every ruling's CURRENT form in context | manager, owner | decisions index under its 48 KB soft cap, every D-id present, 0 `?` after 1.S8; read whole at wake (pcrec-manager skill) and re-read after a compaction (post_compact.sh prints the instruction); currency checked per statement (§5.3) |
| G2 | one command prints exactly one entry, at the level asked for | manager, lanes | `scripts/entry D47` prints D47 with all four addenda and nothing else; every witness of appendix B holds; 0 owner-table rows outside their entry |
| G3 | one format, one linter, one accessor for every tracker that fits | maintainers | one linter (plan_lint folded in at T2), one accessor; per-file differences are rows in ONE profile table (§2.4) |
| G4 | no citation breaks | everyone | `doc_cites.py`: every cite that resolved before unit 1 resolves to the same owner-table rows after (appendix C); 0 ids renumbered; then C13 on every commit |
| G5 | an index statement never says more or other than its details, and states the CURRENT ruling | owner | 100% of statements pass a fresh opus critic's seven questions with the inbound list (§5.3); every batch's planted lines caught |

Priority on conflict: G4 > G5 > G1 > G2 > G3. Non-goals: rewriting details
text; changing what a decision says; append-only journals and logs (§4).
Known exception to the order, stated: unit 1 lands the index with `?` lines
(old titles) before 1.S writes statements, so for that window G5 is unmet by
design; a `?` line is not acted on (read `entry` first; §6).

## 1. Census

Sizes are bytes at main 6638e3679. "Entries" counts the file's own heading
form. Size spread is per entry.

### 1.1 Candidate files

Fourteen files were measured (sizes, entries, heading forms, parsers):
appendix F. In short: decisions.md 832 KB, 191 ids under 198 headings in
three heading forms; plan.md 468 KB, 339 rows (296 not-started, 36 started,
2 blocked, 5 deferred), 31 child rows with 4-space attributes;
plan_row_bodies/ 21 bodies (~146 KB); plan_completed.md 1.2 MB, 397 heads
under 65 date headings, 297 of them prose, 6 tags also live in plan.md, 4
twice; known_issues.md 467 KB, 134 ids under 139 headings, states that are
not one set (FIXED 68, OPEN 35-37, CLOSED 6, ACCEPTED 1, other 24-27);
upstream_issues.md 70 KB, 25 ids + 1 id-less heading, state in a body
`**Status**:` bullet.

Decisions shape: 148 addendum markers by an open scan, about 40 outside their
entry's `^## Dn` cut plus 3 id-less ones filed under a foreign entry, and
seven numbering shapes the rev-1 rule could not keep (appendix A). D47's two
load-bearing addenda are top-level headings after D48, so reading `## D47`
alone today misses part of D47's current ruling. Supersession is prose (5
`SUPERSEDED`, 47 "supersed*"; no field). Cites tree-wide: ~36k `Dn`, ~26k
`Kn`, 2,494 `Dn add. k`/`Dn addendum k`, 1,011 dotted `Dn.k`: ids AND
addendum numbers are load-bearing (appendix C).

Plan shape: head lines total 36.2 KB with child indents (35.8 KB without;
median 110 B); everything else in the row is ~430 KB.

### 1.2 Who reads what, and how

The reader table (grep-found; each row moved by a named unit in §5) is
appendix H. Its classes: the parsers (plan_lint.py, rows_check.py +
stream_support.tsv); the structural name lists a lint section sits in
(shards.tsv, san lists, `.PHONY`); the hooks (a plan-only glob, a pre-push
lint that skips SILENTLY if its runner moves, hooks.test pinning it,
installed copies); pointers into plan_row_bodies/ (one an in-force
vlookbehind.md step); post_compact.sh; the skills (STATE greps, the critic
freeze of two files, `git show`/`^## Dn` recipes, the deny grep, `file:line`
records); ~187 line cites (appendix E); content greps in the manager's
memory (outside the repo: a manager step per unit); CLAUDE.md pointers; id
cites in tests and src, one an emitted string (name-keeping saves an abi
event).

Today a ruling is a grep for `^## D26` plus a Read of a line range (3-36 KB,
missing misplaced addenda); nothing gives the current ruling in one line or
every not-started row with its trigger short of reading the 468 KB file.

### 1.3 Files a session loads at start

Today's always-on manager load is ~85 KB (itemized in appendix F); §3 prices
what the indexes add.

## 2. The format

A file that adopts it is a PAIR:

- the INDEX keeps the file's current name (decisions.md, plan.md,
  known_issues.md), so every prose pointer ("decisions.md D26", 396 of them)
  and the one emitted string still land;
- the DETAILS file is `<name>_details.md` beside it, ONE per index (D192
  answer 2): the accessor hides the split either way, and one file keeps
  whole-details grep, the bijection check and the converter to one parse.

The shape is one member of a family already in the tree: index tier +
details tier (+ archive tier). MEMORY.md + fact files, CLAUDE.md + NOTES.md,
plan.md + plan_row_bodies/ + plan_completed.md are the other instances. This
design absorbs plan_row_bodies/ and keeps plan_completed.md as the archive
tier; MEMORY.md (outside the repo, owned by the harness's memory rules) and
CLAUDE.md/NOTES.md (own checker, check_claudemd_size.sh, a different
consumer: auto-injection) stay out until a trigger in §9 fires.

### 2.1 Index entry

One line per entry (plan rows: one line, or two for started/blocked rows).

    - <ID> <slug> <state>[ a<k>] — <statement>[ (+<n> more)][ {<keywords>}]

| field | rule | why |
|---|---|---|
| ID | existing id, never renumbered (`D26`, `K139`, `U22`; plan keeps `[TAG]`) | G4 |
| slug | per profile (§2.4 C5): decisions/known/upstream `^[a-z0-9]+(-[a-z0-9]+){1,3}$`, ≤ 28 chars, unique in the profile; plan: the `[TAG]` itself (PL07's grammar). PROVISIONAL `-` until written | a recall handle; mechanical slugs collide (22 D, 23 K ids), so the 1.S writers write them, C5 checking uniqueness per batch |
| state | decisions: `live`, `sup>Dm`, `part>Dm` (statement = the live remainder), `retired`, `absorbed>WHERE`, PROVISIONAL `?`. Known/upstream: set by units 3/4 (§10). Plan: `STATE:<s>` as today | supersession becomes a field; `?` = not yet written |
| a<k> | count of `### ID.aN` headings in the details entry; the linter checks it | forces an index touch at every addendum. NOT a faithfulness control (it shares the converter's source; attribution is the owner table's job, §5.2) |
| statement | ONE sentence, ≤ 200 chars, present tense, the CURRENT ruling with every addendum and every later entry's change applied (§5.3). Shape `<topic>: <rule>[; <rule>...].`, topic ≤ 4 words. No rationale, dates, history or lane names | what a session pattern-matches when about to act |
| (+n more) | n = rulings the statement leaves out; REQUIRES a rulings list in the details, and n = its unstarred lines (C11) | compression allowed, silent omission not; n becomes mechanical |
| keywords | optional, ≤ 40 chars, only words absent from slug and statement, each TRUE of the current ruling | grep recall; a false keyword misdirects recall |

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
non-verbatim text in a details entry, marked by its `rulings:` label.

Superseded, retired and absorbed entries shrink to ≤ 80 chars naming what
replaced them: the index grows by live rulings, not by history.

Plan rows keep their head line (title cap 100 → 90) and gain ONE second line
only when started or blocked:

    - [TAG] STATE:<s> — <title ≤ 90>
      now (<ISO date>): <≤ 160 chars: where it stands and the next step>

`now` is the status of record, rewritten in place, REQUIRED on started and
blocked rows and FORBIDDEN elsewhere. A not-started row's next step or
trigger stays OUT of the index (D192 answer 3); the accessor supplies it at
level 1. Children stay nested by two spaces. Sections stay. The Policy
section shrinks at unit 2 to a pointer at `docs/dev/doc_format.md` plus the
plan-only rules (PL16 keeps checking what remains).

### 2.2 Details entry

    ## <ID> <slug> — <the old heading's text after the id and its separator, verbatim>
    [rulings: block, when the statement has (+n)]
    <body, verbatim>
    ### <ID>.a<N> — <date, who>: <addendum title>
    [(was: "<old marker text>")   only for heading-form markers]
    <addendum body, verbatim>

- An entry runs from its `## ` heading to the next `## ` heading; a body
  never uses a level-2 heading (the seven `## Dn ADDENDUM` headings become
  `### Dn.aN`; C10). The heading keeps the old text after the id verbatim
  (all three heading forms; D98's wrapped continuation is joined, the one
  declared exception), so no title is reformatted.
- **Ownership** comes from the OWNER TABLE (§5.2, appendix B), never from
  position alone: a marker naming its id belongs to that id; an id-less one is
  ruled by hand (D89's "Addendum 2-4" inside D94 belong to D89).
- **Numbering.** `N` grammar: `[0-9]+(\.[0-9]+)?[a-z]?` (`D155.a4.1`,
  `D123.a3a`); C6 orders 4 < 4.1 < 5 and 3 < 3a < 4. A numbered addendum keeps
  its number; an ordinal word is its number (second = 2); an unnumbered one
  takes the owner table's ruled number (default: the lowest free number in
  date order, checked against today's cites, appendix B). A DUPLICATE (D162
  addendum 4 twice): the first keeps it, the second takes the next free number
  and the line `(was: "<label>", second of two)`. A NOTE on an addendum (D168
  "addendum 3 note" ×2) is a `####` sub-heading inside it, label verbatim,
  unnumbered. Addenda sit in number order. An undated label inherits the
  nearest earlier dated marker's date of the same owner. EXTENT: a marker to
  the next marker or `## ` heading, unless the owner table rules `old_end`
  (a marker inside a foreign entry, whose host text may resume after it).
- **Old labels stay greppable on EVERY converted addendum**: a heading-form
  marker (`##`, `###`) gets the `(was: "...")` line; an inline bold label
  (`**Addendum (DOC-1, ...)**`, `**RULING-5 ADDENDUM**`) stays as the
  unchanged first body line under its new heading. So `grep 'D163 addendum 7'`
  still lands, and `entry` resolves the same spellings as aliases (§2.3).
- Plan details hold what leaves the row: `filed:`, `next:`/`trigger:`
  (required for not-started, blocked, deferred), `refs:`, the charter, dated
  history, children's 4-space attributes, in today's spelling, so level-1
  fields read the same names before and after the split. plan_row_bodies/
  files fold in as their row's details body (completed rows: §10 unit 2).
- Cross-links are bare ids (`D26`, `[ANCH-AT]`, `K139`, `R-38`, `D163.a7`),
  never markdown links or line numbers.

### 2.3 The accessor: `scripts/entry`, by level

python3 stdlib, run `-I`; it reads the profile table (§2.4), so a new file or
a new level is a table row, not code.

| level | content | decisions | plan | known issues |
|---|---|---|---|---|
| 0 | the index line(s) | the line | head line (+ `now`), child head lines | the line |
| 1 | level 0 + the WORKING FIELDS | + rulings list, every `### Dn.aN` heading, and `later: D49* D58 ...` (later entries citing it, `*` = a supersede/amend verb; the §5.3 pass) | + `next:`, `trigger:`, `status (date):` / `now`, `refs:` lines | + first line of each `**Witness:**` / `**Fix:**` paragraph, cut at 240 chars |
| 2 | level 0 + the full details entry | whole entry | whole entry | whole entry |

A completed plan row (the archive tier) prints its head line cut at 160
chars + `…` at level 0, its attribute lines at level 1, the whole row at 2.

Commands:

    scripts/entry KEY [-l N] [--rev SHA]  one item; default level 2
    scripts/entry -g REGEX [-in N] [-l N] [-p PROFILE] [-s SECTION] [--state S] [--rev SHA]
    scripts/entry --work [-p PROFILE] [-s SECTION] [-k WORD]
    scripts/entry --levels [-p PROFILE]   print the level and work-view rows of the table
    scripts/entry --over-cap              soft-cap lines for scripts/gestalt (§2.4)
    scripts/entry --selftest              one planted fixture per routing row

**Routing of KEY** (first match; ids and tags case-sensitive, slugs
lower-case; each row has a selftest plant, including the ten id-shaped plan
tags K18-FIX, K38-FIX, K60-FIX, D105-BUILD, ..., and DD-14.A2, REVW.A1):

| # | KEY shape | goes to |
|---|---|---|
| 1 | an alias spelling: `Dn add. K`, `Dn addendum K`, `Dn ADDENDUM[ K]`, `Dn <ordinal> addendum`/`ADDENDUM` | decisions, via the owner table's `old_label`/`old_number`; a label shared by two rows (D162 a4) prints both, exit 0, the trailer names both; an unnumbered alias prints every unnumbered-origin addendum of Dn |
| 2 | FULL match of a profile id regex (`D[0-9]+`, `K[0-9]+`, `U[0-9]+[a-z]?`) | that profile |
| 3 | FULL match `D[0-9]+\.[0-9]+` (a ruling number, D47.6) | decisions entry Dn at level 2, trailer `ruling 6 is in the body` |
| 4 | an exact `[TAG]` of plan.md, else of plan_completed.md | plan wins; the archive only on absence; 2+ archive rows (PC-3, OPT-5, OPT-VMSEED, SR-8) print all, exit 2 |
| 5 | FULL match `(D[0-9]+)\.a(<N grammar>)`, lower-case `a` | that decisions addendum (after row 4, so a tag shaped like it wins) |
| 6 | a lower-case kebab slug | looked up in EVERY profile's index; 2+ hits exit 2 listing them |
| 7 | anything else | exit 1 |

- **Item grep** (`-g`): searches each item at level `-in` (0 = index lines,
  the default; 1 = + working fields; 2 = + full details) and prints every
  matching ITEM WHOLE at level `-l` (default: the search level). Items, never
  raw lines. `-s` restricts to an index section, `--state` to a state. The
  archive is read only with `-p completed`. CONTENT search (a topic word, a
  claim to verify) is `-g WORD -in 2`, never a grep of the index.
- **Work view** (`--work`): plan = every `STATE:not-started` and
  `STATE:blocked` row at level 1, by section; known = the open states at
  level 1 (§10 unit 3). It never reads plan_completed.md. `-s` and `-k` (a
  keyword, matched at level 1) narrow it.
- **`--rev SHA`** reads both files of the pair at that commit (`git show`,
  read-only): the critic freeze and every "read the rulings at the frozen
  commit" recipe use it.
- Output ends with `entry: <n> items (profile <p>, level <l>)`; exit 0 found,
  1 none, 2 ambiguous.
- With no tool, one line still prints one entry:

      awk '/^## /{p=($2=="D26"||$3=="pcre2-compat-tiers")} p' docs/dev/decisions_details.md

rows_check.py's cut works unchanged on the details file and becomes correct
for every misplaced addendum once it sits inside its entry.

### 2.4 One profile table, one linter, one test section

The PROFILES table is one declared module, `scripts/doc_profiles.py`, read by
the accessor, the linter, the hooks (`--paths` prints each pair's files) and
the selftests (one source; first-match rows per file pair):

| profile | index / details | id | states | soft cap: statement / line / FILE | level-1 fields | work view | form |
|---|---|---|---|---|---|---|---|
| decisions | decisions.md / decisions_details.md | `D[0-9]+` | live sup part retired absorbed `?` | 200 / 300 / 48 KB | rulings list, `### ID.aN` headings, `later:` | — | dormant until unit 1 |
| plan | plan.md / plan_details.md | `[TAG]` | the four STATEs | title 90, now 160 / 2 lines / 48 KB | `next:` `trigger:` `status (…):` `now` `refs:` | not-started + blocked, L1, by section | `single` until unit 2, then `pair` |
| completed | plan_completed.md (archive, no index) | `[TAG]` | as written | — | the row's attributes | — | `archive` (§10 unit 2) |
| known | known_issues.md / known_issues_details.md | `K[0-9]+` | unit 3's mapping table | 180 / 280 / 32 KB | `**Witness:**` `**Fix:**` first lines | open states, L1 | dormant until unit 3 |
| upstream | upstream_issues.md / upstream_issues_details.md | `U[0-9]+[a-z]?` | unit 4's census (the file's `**Status**:` values) | 180 / 280 / 12 KB | unit 4's census | unit 4 | dormant until unit 4 |

Each row also carries its C8 exemption prefixes (appendix E) and its section
list. The `single` form is the plan profile read in TODAY's shape, so the
accessor and work view serve before any split; unit 2 deletes it
(implement-then-replace).

**Soft caps (D192 answer 4).** A FILE cap never fails anything: doc_lint
prints `WARN C4 <file> ...` and exits 0, and `scripts/gestalt` gains one row
in its declared ROWS table: threshold "a `pair`-form index over its cap, or
the accessor unavailable". Gestalt runs `timeout 5 python3 -I scripts/entry
--over-cap`, which prints one line per over-cap index:

    docs: decisions.md 51.3 KB over soft cap 48 KB (+3.3 KB, 107%)

KB = 1024 B, one decimal; pct = size / cap, rounded down. A non-zero exit or
a timeout prints `docs: unavailable` (a check that cannot run must not read
as "under cap", K35). The per-LINE caps are the open question in §7.

Common rules (each FAILS, except the file cap):

- C1 ids unique in the index; C2 bijection: every index id has exactly one
  details heading and every heading one index entry, slugs equal on both;
  C3 heading grammar (§2.1, §2.2); C4 field caps (fail) and file cap (WARN);
  C5 slug per the profile's grammar, unique, or `-`; C6 every `### ID.aN`
  lies inside `## ID`, numbers unique and rising in the §2.2 order; C7 every
  id in an index line resolves; C8 below; C9 a parsed-entry floor per profile
  (K35); C10 no level-2 heading inside a details body; C11 `(+n)` equals the
  rulings list's unstarred lines, and a list exists iff n > 0; C12 (from unit
  2) no file under docs/design/plan_row_bodies/; C13 every `Dn.aN` and every
  alias-spelled cite in the tree resolves (G4, §5.2).
- **C8**, per profile, wakes when that profile becomes `pair`: no
  `<file>.md:<line>` cite of the profile's file outside its declared
  exemption prefixes. Anchored on the repo path: a cite counts when the
  basename is preceded by a non-path character or by `docs/dev/` at a path
  start, so `pcrec-bench/docs/dev/known_issues.md:N` (the bench's own file)
  never matches. Selftest plants: one positive, one bench-path negative, one
  exempt-prefix negative. The plan profile keeps PL14 as is; plan_completed
  stays exempt (append-only).
- `--selftest` plants one violation per rule per profile, plus one over-cap
  file that must WARN and exit 0; `--staged` lints staged content; `--stale`
  (exit 0) prints headroom under each file cap and the count of `?` and `-`
  left. The `?`+`-` count is a RATCHET: the linter refuses an increase.
- **The section.** T1 creates `tests/doc_lint/` and the `make test-doc-lint`
  section (entry's selftest; unit 1 adds doc_lint's decisions profile; T2
  folds plan_lint in). Born in T1 so the structural lists move once: a
  TEST_SECTIONS member + `.PHONY`, a tests/ci/shards.tsv row, a
  tests/lib/san_excluded.txt (or san_scripts.txt) row for
  `tests/doc_lint/run_doc_lint.sh`, tests/CLAUDE.md, docs/testing.md.
- **Hooks.** pre-commit reads its trigger paths from `doc_profiles.py
  --paths` (one source), so a commit staging only a details file is linted.
  Both hooks FAIL (exit non-zero, one line naming the missing path) when a
  linter path they expect is missing, never skip. Installed copies do not
  update on merge: every landing that changes a hook re-runs `make hooks
  HOOKS="pre-commit pre-push-light"` on each box that has them (dev box, Mac,
  ubuntubudu), named in the landing brief.

### 2.5 Worked examples

Appendix D: the decisions index lines for D26, D47 and D191 with their
rulings lists and inbound lists, each checked against §5.3's seven questions
(rev 1's three all failed G5: D47 omitted 6 rulings against `(+3)` and
carried stale "constant (8)"; D26 omitted 4 with no `(+n)`; D191 omitted 11
against `(+3)`), and the plan examples. Lines measure 222-276 B.

The D47 details headings (four addenda, two former top-level headings with
their `(was:)` lines, two inline labels kept as first body lines) are in
appendix D as well.

### 2.6 Where the format is defined

The format (this section's rules, without census or migration) moves to
`docs/dev/doc_format.md` in T1: the one definition the profile module's
docstring and every index header point at.

### 2.7 Writing an entry from now on

A new ruling = the details entry + the index line, in one commit (C2 refuses
one without the other, at commit time because the hook globs the pair). An
addendum = the `### ID.aN` block + the `a<k>` bump, with the statement and
rulings list rewritten if the ruling moved. A ruling that changes an EARLIER
entry's ruling also rewrites that entry's state and statement in the same
commit (`part>Dn`/`sup>Dn`). Statements are written by an opus session (D192
answer 1): the manager when it records a ruling, an opus lane in a batch. The
q and pcrec-manager skills' "write the ruling" steps name both files.

## 3. Size targets

Measured basis: the worked lines (decisions 222-276 B, mean 252; all
multi-ruling, so above typical, but the only sample); a `now` line is up to
185 B (24 B of prefix + 160).

| index | entries | per entry | projected | soft cap |
|---|---|---|---|---|
| decisions.md | 191 | 252 B at the examples' mean; superseded ≤ 100 B; single-ruling entries shorter (unmeasured) | 40-48 KB; no sample supports a lower central figure; 1.S1 measures it | 48 KB |
| plan.md | 339 rows; 38 `now` | heads 36.2 KB + now ≤ 6.7 KB | 42.9 KB (89% of cap) | 48 KB |
| known_issues.md | 134 | open ~180 B; FIXED/CLOSED ≤ 80 B (unit 3) | ~17 KB | 32 KB |
| upstream_issues.md | 25 | ~170 B | 4 KB | 12 KB |

Runway: decisions grows ~8.5 KB a month (45 ids in 34 days). Starting at
40-48 KB, the soft cap is reached in weeks, possibly on day one; then the
gestalt line fires every heartbeat, which is the owner's chosen revisit
trigger (D192 answer 4). The levers inside this design, in order: shrink
superseded/absorbed entries (built in), shorten single-ruling statements,
move rulings detail into the lists (it is already there).

**Always-on load.** ~4 B/token is an estimate, not a tokenizer count. The
decisions index (~46 KB, ~12k tokens) is always-on for the manager (read at
wake, re-read after a compaction; G1). Whether the PLAN index is also
always-on is the manager's choice (same answers either way): the manager
greps STATE:started at wake and 296 of 339 rows are not-started, so holding
it out and serving it by `entry --work` halves the add. Recommendation: hold
the plan index out. Lanes load neither index; they call `scripts/entry`.

## 4. Other files

Verdicts with reasons: appendix I. APPLY: known_issues.md (unit 3),
upstream_issues.md (unit 4, on its trigger). ARCHIVE TIER: plan_completed.md
(its own `archive` profile, §10 unit 2). ABSORBED: plan_row_bodies/ (unit 2;
C12 refuses new files). PROPOSAL: the kit ledgers (§8). SAME FAMILY, kept out:
MEMORY.md, CLAUDE.md/NOTES.md (§2, §9). DO NOT APPLY: ideas.md, learnings.md,
testing.md, the journal and ledger, REFERENCES.md, wake/owner files.

## 5. Migration plan

Every split is a re-runnable TRANSFORM, not a hand-made diff: the lane
delivers a converter plus its output, and the landing re-runs it on main HEAD
(§5.2). Order: **T1 → 1.0 → 1 → 1.S → T2 → 2 → 2.S → 3 → 4**; K beside them
once vetted. T2 moved after unit 1 (it serves unit 2; plan_lint stays
untouched across the 2026-11-11 freeze).

| unit | what | tier | readers moved in the same unit |
|---|---|---|---|
| T1 | `scripts/doc_profiles.py`, `scripts/entry` (levels, routing table, aliases dormant, item grep, `--work`, `--rev`, `--over-cap`, `--selftest`), the gestalt ROWS row, `docs/dev/doc_format.md`, the `test-doc-lint` section (entry's selftest). Plan profile `single`, others dormant | sonnet (+ optional D27 test cell, §10) | scripts/CLAUDE.md, gestalt header + scripts/tests/gestalt.test; root CLAUDE.md situation row ("look up a ruling or row, choose work, or search content → `scripts/entry`; content = `-g WORD -in 2`"); the section's lists (§2.4): Makefile TEST_SECTIONS + .PHONY, tests/ci/shards.tsv, tests/lib/san lists, tests/CLAUDE.md, docs/testing.md |
| 1.0 | `scripts/doc_census.py` + the owner table with its hand rulings, `scripts/doc_control.py`, `scripts/doc_cites.py` (resolver + `--inbound`); BEFORE-run of the resolver committed | sonnet; the ruled rows reviewed by the manager; NOT the converter's author | docs/dev/doc_index/ (new, its CLAUDE.md) |
| 1 | decisions split by converter (§2.2), index of `?` lines (old title, slug `-`); `entry`'s decisions profile wakes (aliases, `later:` via doc_cites); doc_lint.py with the decisions profile (C1-C13); the cite-to-id pass over the ~36 live line cites; AFTER-run of the resolver. ACCEPTANCE: appendix B's witnesses; control green (§5.2); idempotence; resolver before = after; `make test-doc-lint strict` green | sonnet (mechanical) | rows_check.py LEDGERS + stream_support.tsv paths; pre-commit (glob via `--paths`) + `make hooks` per box; post_compact.sh (one re-read line); skills: pcrec-manager (wake reads the index; `?` rule), q (writes both files), pcrec-critic (freeze diffs decisions.md AND decisions_details.md; COMMON recipes use `entry --rev`; rulings recorded by id, not `file:line`), pcrec-memfn-manager (main's file list names the details file); root CLAUDE.md "Where things are"; docs/dev/CLAUDE.md; MANAGER STEP: memory `pcrec-grep-plan-before-chartering` (decisions part) → `entry -g -in 2` |
| 1.S1-S8 | decisions statements, slugs and rulings lists, 8 batches of 24 ids, by §5.3. S1 (and S2 beside it) first; S3-S8 only after S1 passes. ACCEPTANCE of S8: 0 `?`, 0 `-` | OPUS writer + fresh OPUS critic, 100% | none (index lines, details headings, rulings lists) |
| T2 | plan_lint folded into doc_lint as the plan profile (PL01-PL17 unchanged in effect; PL16 keeps reading the Policy) | sonnet | Makefile (test-plan-lint out of TEST_SECTIONS and .PHONY); tests/ci/shards.tsv row; tests/lib/san_excluded.txt row; tests/plan_lint/ into tests/doc_lint/; pre-commit; pre-push-light:41 (fail, not skip); scripts/tests/hooks.test pins; the six `--stale` mentions (appendix H); docs/testing.md; skills. SHIMS at both old paths until every box re-ran `make hooks`. ACCEPTANCE: `make test-ci-shards test-codegen test-doc-lint testscripts` green + a plant that renames the linter and sees pre-push-light FAIL |
| 2 | plan split by converter (§10 unit 2 must first fix F9's `now`/`?`, F12, F13); `single` deleted | sonnet (mechanical) | boxqueue comment; skills' plan recipes; pcrec-critic deny (names the plan_details entry, bans `entry -g -in 2`/`--work` over a denied row) and freeze (plan_details.md); vlookbehind.md hunk; the ~46 plan_row_bodies readers; MANAGER STEP: memory `pcrec-grep-plan-before-chartering` (plan part) |
| 2.S | the 38 `now` lines and 36 over-cap titles | OPUS writer + OPUS critic, 100% | none |
| 3 | known_issues split (§10 unit 3 first); statements for open entries only, FIXED/CLOSED shrink to ≤ 80 chars | converter sonnet; ~2 opus batches + critics | known_fail instructions; pcrec-critic freeze; MANAGER STEP: memory `pcrec-done-line-verify-claims` |
| 4 | upstream_issues (§10 unit 4 first) | converter sonnet; statements OPUS + critic | pcrec-critic freeze |
| K | main sends §8 to the kit, after the re-check round | manager | none; the kit decides |

**Landing.** Freeze: no merges 2026-11-11 01:00 until the full suite ends
(~14:00). T1 writes no ruling file and may land before 01:00 if ready and
light. Units 1 and 2 are the BIG transforms: ONE per quiet window (the
14:00-20:00 window on 2026-11-11 fits one; 20:00-01:00 is the owner's hold).
Unit 1 lands with no open branch carrying a decisions.md hunk (the landing
brief lists them by `git diff --stat main...BRANCH -- docs/dev/decisions.md`;
each merges first or re-targets its hunk to the pair by §2.7). Unit 2 needs
every lane merged (plan.md takes ~13 commits a day, and an edit to an
existing row cannot be re-run, only re-applied). **D153 check:** before unit 1
the manager confirms with the stream thread (the live writer of rows_check.py
and stream_support.tsv) that no in-flight remodel branch edits them; if one
does, unit 1 waits or carries its repoint.

### 5.1 Standing questions (docs/design/CLAUDE.md)

1. Measurement regime: RELEVANT only for byte sizes (`wc -c`/python at
   6638e3679) and the token estimate (4 B/token; a 2x error moves the soft
   caps, not the design).
2. Independent control: RELEVANT, and §5.2 and §5.3 are its answer. The
   census and owner table are produced by a script the converter's author
   did not write, from an OPEN scan (never an enumerated spelling list), and
   the control reads them, not the converter's output; the witnesses were
   chosen by the review. a<k> is NOT a faithfulness control (it shares the
   converter's source). A statement is checked by a critic independent of its
   writer, against the details AND an inbound list neither of them wrote;
   each batch carries planted wrong lines the critic must catch (its control).
   C9 floors and C11 count populations; each `--selftest` plant reaches its
   rule.
3. What moves when regenerated: the indexes are hand-written; converters run
   once per unit and once per landing re-run; the owner table only appends.
   No emitted byte, abi or spec moves (process docs only; the emitted
   "known_issues.md K24" string lands unchanged because the name is kept);
   the readers that move are §1.2's rows, each named in its unit.

### 5.2 Converter, owner table, control and cite resolver (units 1.0 and 1)

- **Census and owner table** (appendix B): `doc_census.py` scans every line
  opening `**`, `- **`, `##` or `###` with "addend" in its first 120 chars,
  any case, with a declared exclusion list (each excluded line and why); one
  table row per marker; id-less rows get hand rulings with evidence. The
  converter refuses a marker with no row.
- **Control** (`doc_control.py`, from the census side): (i) the distinct id
  set is equal; (ii) every owner-table row is exactly one `### new_id`
  heading inside `## owner`, the marker's next non-blank line hashing to
  `body_hash`, and
  its old label survives (the `(was:)` text or the unchanged inline label
  equals `old_label`); (iii) PER-OWNER multiset: the non-blank lines the
  original assigns to an owner (its body plus every addendum the table gives
  it) equal its details entry's non-blank lines minus the EXCLUSION SET:
  heading lines on both sides, `(was: ...)` lines, the `rulings:` block, and
  D98's joined continuation. Lines moving between entries now fail.
- **Already converted** (declared test): in the index, `- <ID> ` lines are
  converted and any `## ` heading is old form (a pre-split branch's appended
  entry); in the details, a heading matching `^## <ID> (<slug>|-) — ` is
  converted. The census asserts no old heading matches the new grammar.
- **Idempotence:** `convert(convert(x)) == convert(x)` byte-identical on the
  real file, and converting an index with appended old-form entries leaves
  every converted byte unchanged (acceptance tests in unit 1).
- **Landing baseline:** the lane converts at its commit C0; the landing
  re-runs on HEAD H: census on H (new markers append rows; an id-less one
  stops for a ruling), converter on H, control recomputed from H (never C0's
  counts), idempotence, resolver before/after on H's tree. Post-landing
  re-runs of a mixed file check the converted part byte-identical to the
  previous output.
- **Cite resolver** (`doc_cites.py`): the forms of appendix C; BEFORE
  resolves through the owner table on the old file, AFTER through headings
  and aliases; every cite's resolved row set must be equal. After unit 1 the
  same code is C13.

### 5.3 Statements: writer, critic, inbound list (1.S, 2.S, 3, 4)

Before each batch, `doc_cites.py --inbound` lists for every id each line in
a LATER entry (owner-table attribution, so addenda count for their owner)
citing it in any form, with a flag where the line carries a verb from a
declared list (supersed, amend, replac, revers, overrid, retir, struck,
settl, re-open, withdraw). The writer (OPUS, D192 answer 1) reads the whole
details entry, addenda included, plus its inbound lines, and writes slug,
state, statement, rulings list, keywords; never from the old title (titles
state the first ruling, not the current one). A FRESH opus critic, one per
batch, reads the same entry and inbound lines and answers seven questions per
entry:

1. does the statement add a ruling the details do not make;
2. contradict the current ruling;
3. state a rule an addendum or a later entry replaced;
4. is the rulings list complete and only current (every ruling of §2.1's
   definition, none undone by a later entry, none extra);
5. does each starred line appear in the statement (n itself is C11's);
6. is the state right given the inbound list (`live`, `part>`, `sup>`);
7. is every keyword true of the current ruling?

The batch also carries three PLANTED lines the critic must flag (appendix D:
D42 `live` keeping the −1 collapse, a wrong n, a false keyword); a batch
whose critic misses one is re-run with a fresh critic. Disputes go to the
manager; no owner read-through (D192 answer 1). Gate (F15, COST-2): 1.S1 runs
first (S2 may run beside it); S3-S8 start only when S1's report shows every
plant caught and 0 open disputes.

### 5.4 Cost, triggers and stop points

| unit | lanes | landing | trigger (D77) | if the work stops here, what stays |
|---|---|---|---|---|
| T1 | 1 sonnet (+ D27 cell, optional) | light; before 01:00 allowed | D192 answers 3, 4 | `entry --work` on today's plan, `--rev`, doc_format.md |
| 1.0 | 1 sonnet | with unit 1 | D192 | the owner table: the first complete record of every addendum's owner |
| 1 | 1 sonnet | quiet window A | D192 | every D entry whole with its addenda (G2), G4's resolver and C13, a title index |
| 1.S1-S8 | 16 opus (8 + 8) | 8 light | D192 answer 1; S3-S8 gated on S1 | statements for the finished batches, `?` for the rest |
| T2 | 1 sonnet | light + hook re-install on 3 boxes | unit 2's go | one linter |
| 2 | 1 sonnet | quiet window B (all lanes merged) | D192; §10 unit 2's fixes | plan index + details + work view |
| 2.S | 2 opus | light | with unit 2 | `now` lines under cap |
| 3 | 1 sonnet + ~4 opus | light (19 commits in 14 days) | D192 answer 6 | known index |
| 4 | 1 sonnet + 2 opus | light | a re-filed U-n, or upstream_issues.md past 100 KB | upstream index |

Total: ~7 sonnet lanes, ~24 opus runs, ~9 landings (two in quiet windows).
The cost centre is opus reading, ~1.5 MB for decisions. `grep '^## D'`
already lists ids, titles and dates (30.7 KB); 1.S buys the current-ruling
sentence and the rulings list, the owner's ask (D192), so it stays, with
S1's gate as the stop point if the procedure fails.

## 6. Risks

- The index drifts from the details: `a<k>` forces a touch per addendum;
  §2.7 makes a later ruling rewrite the earlier entry's line; the manager
  skill gains "act on the index, but read `scripts/entry` before quoting,
  changing or building on a ruling's specifics; never act on a `?` line".
- An addendum under the wrong owner: the owner table, its independent
  control and appendix B's witnesses (§5.2).
- Big transforms collide with landings: re-run on HEAD, one transform per
  quiet window, the open-branch list (§5).
- A reader missed: §1.2 is grep-found in the repo; manager memory recipes
  get a named manager step per unit; D27 cell briefs that allowlist
  decisions.md add the details file.
- Old cites break: numbers kept, resolver before = after, old labels
  greppable, `entry` aliases.
- Soft caps ignored or full from day one (§3): the gestalt line repeats every
  heartbeat while over, the owner's revisit trigger.
- The `single` plan form outlives unit 2: unit 2 deletes it; the linter
  refuses a `single` profile once its details file exists.

## 7. Owner's answers (2026-11-10; recorded as D192)

1. Statements written by OPUS lanes, checked by a fresh OPUS critic against
   the details; no owner read-through. Applied: §2.7, §5.3.
2. One details file vs one per entry is our call. Kept one per index (§2).
3. A LEVELED accessor with item grep and a work view. Applied: §2.3, §2.4;
   triggers stay out of the index.
4. Soft caps now, revisit later; gestalt prints only when over. Applied:
   §2.4, §3.
5. Kit ledger: yes, send the proposal once vetted. Applied: §8, unit K.
6. Known issues third. Applied: unit 3.

Still open (from rev 1):

1. **Should the per-LINE limits (statement 200 chars, plan title 90, `now`
   160) also be soft, or only the file sizes?** Your answer named the caps in
   general; the question was about file size. Leaning: keep line limits
   HARD. They keep a statement a statement, a writer can always fix one line
   on the spot, and plan_lint already refuses over-long titles and status
   lines today. Rev 2 makes this easier to hold: what a sentence cannot carry
   now goes into the counted rulings list, so the 200-char cap does not force
   silent omission.

## 8. Proposal to the kit (sendable as is)

The proposal text, sendable as is, is appendix G: what pcrec is doing (the
pair, the accessor, the profile table), why, the facts about the two ledgers
(single-writer, read in order; an index block at the top of each would keep
both), and the ask (feedback, and whether the kit wants index blocks, a split
or neither). Unit K sends it after the re-check round; nothing changes in
either ledger without the kit's answer.

## 9. Later: the general form and its unlocks (F16; NOTED, not built)

General form: a TIERED-DOCUMENT profile table (index | details | archive tier
per file, id grammar, states, per-tier caps, level-1 fields) read by one
accessor and one linter. This design builds it for four files; each unlock
is a new row, built only when its trigger fires (D77):

| unlock | trigger |
|---|---|
| fold the CLAUDE.md/NOTES.md size check into doc_lint | a third size-checker script appears, or check_claudemd_size.sh needs a second rule |
| MEMORY.md over-cap line via `--over-cap` | MEMORY.md passes its cap or a brief reports it truncated |
| a `kit` profile for the ledgers | the kit answers §8 with adoption |
| cross-file `--work` (plan + open K + open U + open R) | the wake read needs more than two `entry --work` calls |
| "rulings touched since DATE" view | a session acts on a superseded ruling |
| an `entry --deny` list for blinded critics | a critic round's deny leaks through `entry` after unit 2 |

## 10. Readiness and the PLAN items by unit

**T1 — ready once a re-check confirms this text.** Gating findings and where
rev 2 discharges them: F8 routing (§2.3 routing table, selftest plants per
shape); F11's `--rev` (§2.3); F10's gestalt row (§2.4); F6's structural lists
for the new section (§2.4 "The section", §5 T1 row); F15 order and landing
(§5, §5.4). F9's slug grammar is not exercised (plan `single` form, no
index written). D27 (the review's recommendation; the launcher decides): a
spec-first author writes `entry`'s fixtures from §2.3 and appendices B/C in a
cell denied the implementation.

**Unit 1 (with 1.0) — ready once the re-check passes and T1 has landed.**
F1 (§2.2 ownership and numbering, §5.2 owner table, control, appendix B
witnesses); F2 (§5.2 resolver, C13, §2.3 aliases and row 3, appendix C); F5
(§5.2 exclusion set, converted test, idempotence, landing baseline); F7 (§2.4
C8, appendix E, the cite-to-id pass and the critic skill recipe in the unit-1
row); F9's C5 and slug writer (§2.1 slug row, provisional `-`, 1.S writes,
C5); F11's unit-1 parts (§0 G1, post_compact line, critic freeze both files,
`entry --rev` in COMMONs, the content-grep row and memory step); F15 (quiet
window A, the branch list, the D153 check); F17 (§1.1 heading forms; D98's
join). **1.S additionally:** F3 (§5.3 inbound list, questions 3, 6, 7, `later:`
at level 1) and F4 (§2.1 ruling definition and rulings list, C11, appendix D);
the COST-2 gate (S3-S8 after S1).

**PLAN items, each to be fixed in this doc before the named unit's go:**

- **Unit 2 (plan):** F9: the plan profile's `?` slot (leaning: provisional
  `now? (<date>): <today's status line>`, exempt from C4, counted by the
  ratchet, cleared by 2.S) and the `now` caps for the 31 status lines over
  160. F12: list the ~46 plan_row_bodies readers; rule where a COMPLETED row's
  body goes (leaning: BOXQUEUE.md becomes a design doc beside the queue's
  other docs, its archived pointer left as history); C12; a vlookbehind.md
  hunk for the VMREC.md and IFACE-PUSH.md steps. F13: plan_completed gets the
  `archive` profile (leaning: a moved row's details entry is demoted under its
  row as `### [TAG] ...`, keeping the date headings the only `##` level), and
  PL06/PL07/PL15/PL16/PL17 move with it. F11: the critic deny and freeze for
  plan_details.md; the memory step.
- **Unit 3 (known issues):** F14: a state-mapping table (INFRASTRUCTURE,
  CHECK DESIGN, RULED ACCEPTABLE, RE-SCOPED, unmarked → the profile's states;
  K24, K39, K58, K77 must land in the work view), a sub-record rule for the
  five "original entry" headings (leaning `### Kn.o1`), 134 ids not 139;
  COST-9: FIXED/CLOSED entries shrink to ≤ 80 chars, statements only for open
  ones; F11: memory `pcrec-done-line-verify-claims` step.
- **Unit 4 (upstream):** F14: the real states (the body `**Status**:` values)
  and the id-less `##` heading's fate; the trigger in §5.4.

A RE-CHECK critic round on rev 2 (fix-induced findings + readiness per unit)
is recommended before T1's and unit 1's build go (review verdict).
