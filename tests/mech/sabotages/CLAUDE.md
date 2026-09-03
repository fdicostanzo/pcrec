# tests/mech/sabotages — one file per sabotage row

Each `S<NN>_<name>.sh` is a shell fragment `../run_sabotage_matrix.sh` SOURCES.
It sets variables and nothing else: no command runs at source time, and a file
that executes anything (a stray backtick inside a double-quoted field, the
[M6.5.2] finding below) is a defect **that now HAS a check** — the driver's
field validation scans each row's TEXT for an UNESCAPED backtick in a
double-quoted field and FATALs ([DD-13b.W1.1]). **[r46chk finding 2 / w11f
fix lane, 2026-08-30]: the scan is now a QUOTE-STATE MACHINE over the
file's JOINED text, not a per-line one.** The per-line form matched
`^SAB_[A-Z_0-9]+="` and scanned only that one `$0`, so a double-quoted
field that does not CLOSE on the line it opens was invisible to it
however unescaped its backtick was — MEASURED, 43 of this directory's own
fields are multi-line. `run_sabotage_matrix.sh`'s `SAB_BT_AWK` (defined
once, with a permanent planted-good/planted-bad self-test run at script
start) is the fix.

It must read the TEXT and not the sourced value, and that is the whole trick:
an unescaped backtick is CONSUMED by command substitution at source time and
its span replaced by the output, so a value that still holds a backtick proves
it was escaped and safe, while a value that lost one shows nothing at all —
the defect destroys its own evidence. (A first version tested the value: it
passed every broken row and flagged six correct ones.) A backslash-escaped
backtick inside a double-quoted string is a literal backtick and is fine; most
rows here already write it that way.

The driver's own header is the normative field reference and
`bash tests/mech/run_sabotage_matrix.sh --help` prints it. This file is the
directory's conventions and the traps that have actually been hit.

## The fields

### Required

| field | meaning |
|---|---|
| `SAB_ID` | the row's identity in the matrix. Conventionally `S<NN>-<kebab-name>`; it is NOT the selector (see "Numbering" below) |
| `SAB_FILE` | the file the edit lands in, repo-relative |
| `SAB_SUITES` | space-separated arm names. **The vocabulary is CLOSED** — an unrecognised word scores `UNKNOWN-SUITE`, which is "not measured", not "failed". Register a word BEFORE the rows that need it (R31 C11). Newest: `vmframeless` ([OPT-VMFL] STEP 0, registered with the arm and before S224-S226, which name it); before it `searchpinned` ([OPT-5] STEP 2, registered with the arm and before S218-S222, which name it); before that `pfcollapse` ([OPT-4.1], registered with the arm and before S206-S207) and `rxtsource` ([DD-13b.W1.1], registered before S194-S203) |
| `SAB_DESC` | one sentence: what the edit makes the compiler do wrong |
| `SAB_BEFORE` / `SAB_AFTER` | the literal edit. `lib/replace.py` refuses unless BEFORE occurs exactly `SAB_COUNT` times and AFTER is present afterwards |

### Optional

| field | meaning |
|---|---|
| `SAB_COUNT` | how many occurrences BEFORE must have (default 1) |
| `SAB_FILE2` / `SAB_BEFORE2` / `SAB_AFTER2` / `SAB_COUNT2` | a SECOND coordinated site. Exists because **a one-hunk mutation cannot falsify a defence-in-depth pair** (S108: two independent gates on the same input, so removing either changed no emitted byte) |
| `SAB_HARNESS_TARGET` | scope the `harness` arm to one `.rxt` file or directory instead of the whole corpus |
| `SAB_DOC_FIGURE` | the row's own record of what it measured, for humans diffing a re-run against the docs. The matrix does not read it |
| `SAB_EXPECT` | `DETECTED` (default), `UNDETECTED`, or `UNREACHED`. Scored in BOTH directions; a mismatch either way exits non-zero |
| `SAB_EXPECT_REASON` | REQUIRED when `SAB_EXPECT=UNREACHED`, and printed in the verdict |

### `[MECH-REACH]` — the reach fields (2026-08-25)

| field | meaning |
|---|---|
| `SAB_REACH` | a command run on the CLEAN tree, BEFORE the sabotage. `$PCREC` is the clean binary, `$TREE` its root, `$REACH_TMP` a scratch dir which is also the cwd |
| `SAB_REACH_EXPECT` | ONE required literal substring PER LINE; ALL must appear in the probe's combined stdout+stderr. Required with `SAB_REACH` |
| `SAB_REACH_POP` | `FILE\|EREGEX\|MIN` lines: FILE must hold ≥ MIN lines matching EREGEX at HEAD. The count is PRINTED on pass and on fail |
| `SAB_REQUIRE` | instrument requirements; the vocabulary is CLOSED and holds exactly `asan` today. Unsatisfiable ⇒ ANOMALY, never a verdict about the code |

Failing a reach check is the verdict **UNREACHED**: the sabotaged tree is not
built or run, the headline counts it, and it is RED unless the row declares
`SAB_EXPECT=UNREACHED` with a reason. The reverse is checked too — a row that
declares its witness dead and is found live reads **NOW REACHED**.

**THE RULE: a row whose detector is a CONSTRUCT declares its reach.** S70 is
why. Its four escape witnesses (`\b \B \G \K`) were retired one per wave as
module `assertions` IMPLEMENTED them; after [M6.5.2] retired the last one, not
a single row in the tree still reached the site S70 deletes — and the row went
on scoring for two milestones, certifying nothing, until a full 180-row matrix
read UNDETECTED. The `SAB_EXPECT` doctrine watches `UNDETECTED → DETECTED`;
this direction had no checker at all.

**A REACH PROBE AND A POPULATION FLOOR ARE DIFFERENT CLAIMS AND EXPIRE
SEPARATELY.** The probe says the SITE still answers; the floor says the
WITNESS ROWS still exist in the suite that scores the row. S70 declares both:
a probe alone stays green if somebody retires the two `reject_gated` lines,
because the compiler goes on producing a sentence nobody asks for. S155 is the
same lesson from the other side — its `SAB_HARNESS_TARGET` pointed at a file
whose relevant population had been ZERO since [DD-14.EMPTY], and a re-anchor
had certified the EDIT still applied while saying nothing about that.

**ASSERT WHAT MOVES.** S27 and S30 do not change WHETHER a pattern is refused,
only WHERE it is blamed, so their `SAB_REACH_EXPECT` carries the
`(pattern offset N)` and would be worthless without it. S28 swaps two tables,
which a single probe cannot see, so it asserts BOTH sentences. S32/S33 assert
BOTH sides of a boundary, because an off-by-one is invisible from either side
alone.

## Checking a definition without running it

    VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh          # all 180
    VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S34      # one

Sources every selected file, runs the driver's field validations, prints one
`FIELDS OK` line each, builds nothing. Seconds. Use it after editing a
definition — the validations are otherwise raised when the row RUNS, which for
a full matrix is up to eighty minutes in. A malformed field is a named `FATAL`
and exit 2, never a quietly smaller matrix.

## Numbering

`SAB_ID` is NOT the selector. The driver matches on the BASENAME at the id
boundary — `S10` selects `S10_*.sh` and never `S100_*.sh` — so a file's name
carries the identity and `$SAB_ID` is a label. `rows_for.sh` prints the
basename selector for the same reason (until 2026-08-23 it printed `$SAB_ID`,
which the matrix FATALs on: 66 of 67 invocations had been failing).

Check the highest existing id before numbering a block:

    ls tests/mech/sabotages | sed 's/^S\([0-9]*\)_.*/\1/' | sort -n | tail -1

[M6.5.2] did not, and drafted nineteen rows onto ids `S100`/`S101` that were
already taken.

**AND THAT COMMAND IS NOT SUFFICIENT WHEN LANES RUN CONCURRENTLY** ([OPT-4.1],
2026-08-30). This lane DID run it, got `204`, and numbered `S205`/`S206` — and
still collided, because another lane merging ahead of it had minted `S205` on
a branch this worktree could not see. A worktree's `sabotages/` is the id space
as of ITS branch point, not the id space. **In a multi-lane session the id
range is the MANAGER's to arbitrate**: a lane numbers from the highest it can
see, states the range in its handback, and renumbers on instruction (here to
`S206`/`S207`, in one commit, with a SIMULTANEOUS substitution — bumping
`S205 -> S206` and then `S206 -> S207` in two passes carries the first row all
the way to `S207` and silently merges the pair). Nothing else in the tree is
touched: a mention of the colliding id in `docs/dev/dev_journal.md` belonged to
the OTHER lane's row and stayed put.

## Traps that have actually been hit

- **A stale anchor certifies nothing, silently.** Seven rows' anchors had
  drifted for weeks (2026-08-19; five from ONE struct-to-pointer refactor).
  Copy anchors from `git show HEAD:<path>`, never from a live working-tree
  read, and never weaken the count check. The standing tripwire is
  `python3 scripts/m6read_check_sab_anchors.py`.
- **…BUT `git show HEAD:` IS THE WRONG SOURCE WHEN YOU ARE THE ONE MOVING THE
  LINE**, and the two rules above and below read as a contradiction until you
  see which situation each is for. The rule above is for a re-anchor done on a
  CLEAN tree: take the committed text so you cannot capture uncommitted noise.
  When your own uncommitted change is what invalidated the anchor — you edited
  the very expression a row anchors on — `git show HEAD:` hands you the text
  you just replaced, and the anchor is stale the moment you commit.
  `run_codegen_tests.sh`'s own `[SABANCHOR]` failure message says this in the
  other direction ("never from `git show HEAD:<path>` alone once the working
  tree has moved past HEAD"); both are right, for opposite trees. Re-derive
  from whichever source is the text your change LEAVES BEHIND, then run the
  tripwire.
- **The tripwire checks that `SAB_BEFORE` is FINDABLE, not that `SAB_AFTER` is
  VALID C.** Those are two claims and a re-anchor can break the second while
  satisfying the first — re-indenting a multi-line `SAB_AFTER`, or dropping a
  conjunct that moved into it, leaves the row resolving cleanly and failing to
  build when it is finally applied. Apply the substitution to a scratch copy
  and `gcc -fsyntax-only` it. [OPT-4] (2026-08-29) hit the anchor half of this
  TWICE in one lane — S140 on `v.mrl_win`'s third conjunct, then S102/S165
  when `fit.prefilter`'s clause went from one line to three — and both times
  the staleness surfaced only from running the whole codegen group, never from
  the scripts the change appeared to touch.
- **`src/opt/select_engine.c`'s `fit.prefilter` CLAUSE MOVES EVERY TIME A
  CONJUNCT IS ADDED, and S102/S165 span the whole of it.** [OPT-4.1]
  (2026-08-30) broke the same two rows a THIRD time, adding the nullability
  decline. Two rows, one multi-line expression, one predictable cause — so
  this is no longer "a thing that happened twice", it is a STANDING
  consequence of how those two anchors are written, and each row's header now
  says so. **If you add a conjunct there, re-anchor S102 and S165 in the same
  change and run the tripwire before you believe anything else.** Whether the
  right long-term fix is to narrow both anchors to their own `has_bref` /
  `has_call` token is an open question nobody has ruled; narrowing costs the
  rows their "carries the rest through verbatim" property, which is what makes
  them readable as one-conjunct disables.
- **A re-anchor is not a re-point.** It certifies the EDIT still applies and
  says nothing about whether the POPULATION still reaches it. That is what the
  reach fields are for.
- **Backticks inside a double-quoted field are a live command substitution.**
  S115's `SAB_DESC` carried one and bash reported a syntax error in the middle
  of an unrelated `$( )`. Single-quote `SAB_BEFORE`/`SAB_AFTER` (they already
  are, for `$` and `\`) and keep backticks out of the double-quoted fields.
- **Nested single quotes in `SAB_REACH` break the assignment quietly.** The
  value is a single-quoted string, so a probe containing `'` terminates it and
  the row's reach silently becomes something else. Write probes with double
  quotes inside (`-- "\\d"`), and prefer `cut`/`tr` over `awk` programs. Found
  while retrofitting S17/S18/S19, whose first form parsed and meant nothing.
- **A sabotage whose own documentation says its count is unstable does not
  belong here.** See `../CLAUDE.md`, "Sabotages NOT encoded here".

## Maintenance

When a row is added or re-pointed, say so IN THE ROW'S OWN HEADER with the
measurement — this directory's rows carry their history, and the matrix output
is the citation, never a number copied into prose. When a corpus edit moves a
figure a row's `SAB_REACH_POP` states, move the row in the same change.

**Newest (r51fix, 2026-09-03):** S219 flipped `UNREACHED` → `UNDETECTED` (a
mis-declared reach claim, not a falsified derivation), S220's `SAB_REACH_POP`
re-derived to its own named manifest, and three new rows S224-S226 on the
`vmframeless` arm. See `../CLAUDE.md`'s own "[OPT-5]/[OPT-VMFL] r51fix" section
for the per-row narrative — this file carries the field reference and traps,
not the row history.
