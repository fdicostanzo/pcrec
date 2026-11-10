# One format for ruling and tracker files: index + details (the rules)

The format of record for tracker files that adopt the PAIR shape ([DOC-INDEX], D192). Census, migration and
reviews are not here: design `docs/design/doc_index_format.md` (rev 3) and its appendix. This file is the
rules, as built; `scripts/doc_profiles.py` is the one declared table that enforces them.

STATUS (T1): only the ACCESSOR and the soft-cap row are built. plan.md is the `single` form (rows read in
place), plan_completed.md the read-only `archive` form; decisions, known issues and upstream issues are DORMANT
(`entry` exits 1 with `entry: profile P dormant (unit N)`) until their units convert them.

## Reading: `scripts/entry`

    scripts/entry KEY [-l N] [--rev SHA]     one item; default level 2
    scripts/entry -g REGEX [-in N] [-l N] [-p PROFILE] [-s SECTION] [--state S] [--rev SHA]
    scripts/entry --work [-p PROFILE] [-s SECTION] [-k WORD]
    scripts/entry --levels [-p PROFILE]      the level and work-view rows of the profile table
    scripts/entry --over-cap                 the soft-cap line scripts/gestalt reads
    scripts/entry --selftest

| level | content | plan (today) |
|---|---|---|
| 0 | the index line(s) | the head line and its child head lines |
| 1 | + the working fields | + `next:` `trigger:` `status (date):` `refs:` |
| 2 | + the full details entry | the whole row |

A completed row (the archive) prints its head line cut at 160 characters at level 0, its attribute lines at
level 1, the whole row at level 2; an archive row is a `- [TAG] STATE:<s>` line at any indent (other `- [TAG]`
lines are body text of the row above). Plan wins over the archive for a tag in both; 2+ archive rows with one
tag print all and exit 2.

KEY routing, first match: (1) an alias spelling (`Dn addendum K`, `Dn add. K`, `Dn <ordinal> addendum`, `Dn
addendum YYYY-MM-DD`) to decisions; (2) a full profile id (`D26`, `K139`, `U22`); (3) `D47.6` (a ruling
number: entry Dn, trailer `ruling 6 is in the body`); (4) an exact `[TAG]` (brackets optional); (5) `Dn.aN` (one
addendum); (6) a lower-case kebab slug (every live pair profile; 2+ hits exit 2); (6b) a script name under `scripts/` (`boxqueue`, `plan_lint.py`, `hooks/pre-push`; an extension-less stem naming 2+ files exits 2); (7) anything else exits 1.
Plan linting refuses a `[TAG]` shaped like rows 2, 3, 5 or 6 (PL18), so a tag is always reachable.

`-g` searches each item at level `-in` (default 0 = index lines; 2 = full content) and prints every matching item
whole at level `-l` (default 0). The archive is read only with `-p completed`. `--work` = every not-started and
blocked plan row at level 1, by section; it never reads the archive. `--rev SHA` reads the files at that commit
(read-only `git show`) with the WORKING TREE's profile table, the form chosen by which files exist at SHA.
Output ends `entry: <n> items (profile <p>, level <l>)`; exit 0 found, 1 none, 2 ambiguous. Without the tool:
`awk '/^## /{p=($2=="D26")} p' docs/dev/decisions_details.md` prints one entry once a pair exists.

## The pair (unit 1 onward)

The INDEX keeps the file's current name (decisions.md); the DETAILS file is `<name>_details.md`.
Index entry, one line:

    - <ID> <slug> <state>[ a<k>] — <statement>[ (+<n> more)][ {<keywords>}]

ID existing and never renumbered; slug a recall handle (`^[a-z0-9]+(-[a-z0-9]+){1,3}$`, at most 28 characters,
unique in the profile; `-` only on a converted line until its statement is written); state `live`, `sup>Dm`,
`part>Dm`, `retired`, `absorbed>WHERE` (`?` = converted, statement not yet written); `a<k>` = the count of `###
ID.aN` headings in the details entry; statement = ONE sentence, at most 200 characters, present tense, the
CURRENT ruling with every addendum applied; `(+n more)` requires a rulings list of n unstarred lines.

Details entry: `## <ID> <slug> — <the old heading text, verbatim>`, the body verbatim, then `### <ID>.a<N> —
<date>[, <who>]: <title>` blocks (a heading-form old marker keeps its full text in a `(was: "...")` line). An
entry runs from its `## ` heading to the next `## `; a body never uses a level-2 heading. Cross-links are bare ids.

A new ruling = the details entry + the index line in ONE commit with slug, state and statement written at once.
A ruling that changes an EARLIER entry's ruling also rewrites that entry's state and statement in the same
commit.

## Soft caps

A FILE cap never fails a check: `scripts/gestalt` gains the `docs` row (`entry --over-cap`, `timeout 2`), which
prints at most one line, `docs: decisions.md 51.3 KB over soft cap 48 KB (+3.3 KB, 107%)` (KB = 1024 B, one
decimal, truncated; pct = floor), or `docs: unavailable` when the accessor fails, hangs or prints no trailer.
It is silent under every cap. The line is recorded, not acted on: it is the owner's revisit trigger. LINE caps
(statement 200, plan title 90) stay HARD.

## The profile table

| profile | index / details | id | form | soft caps: statement / line / FILE |
|---|---|---|---|---|
| decisions | decisions.md / decisions_details.md | `D[0-9]+` | dormant until unit 1 | 200 / 300 / 48 KB |
| plan | plan.md (details at unit 2) | `[TAG]` | `single` | title 90 / 300 / 48 KB |
| completed | plan_completed.md | `[TAG]` | `archive` (read-only) | none |
| known | known_issues.md / known_issues_details.md | `K[0-9]+` | dormant until unit 3 | 180 / 280 / 32 KB |
| upstream | upstream_issues.md / upstream_issues_details.md | `U[0-9]+[a-z]?` | dormant until unit 4 | 180 / 280 / 12 KB |
| scripts | scripts/INDEX.md (no details file) | file name under `scripts/` | `list` | none |

The `scripts` profile: `- <name> <live\|retired> — when: <situation>; does: <what>. {keywords}`, one line per file under
`scripts/` and `scripts/hooks/` (exempt: CLAUDE.md, NOTES.md, INDEX.md, `tests/`, `hooks/test_*`). Level 0/1 = the line;
level 2 adds the script's own header comment (no second file). `scripts/entry --lint-scripts` (`make test-doc-lint`)
fails on a script with no line, a live line naming no file, a missing `when:`/`does:`/`{keywords}`, a duplicate, or
a live script with no header comment.

Each row also names its linter, extra paths, C9 floor and exemptions in `scripts/doc_profiles.py`; a new file or
level is a row there, not code.
