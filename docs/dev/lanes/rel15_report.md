# Lane rel15 report — [REL-1.5] contribution posture + [REL-1.7] darwin arm

Branch `lane/rel15` from main `f12e123d`. Commits: `3c8a8008` (RUN-STAMP),
and the CONTRIBUTING.md commit that follows it on the branch.

## What was already done before this lane started

Reading the tree before writing anything found several [REL-1] items
already landed on main by sibling/earlier lanes, so this lane's brief
items (2)-ish overlapped less than the charter implied:

- The root `CLAUDE.md` D116 preface (three-line "read README/CONTRIBUTING
  instead" note) is already in place at the top of `CLAUDE.md` — nothing
  to do for that half of item (1)/the public-CLAUDE.md ruling.
- [REL-1.10] (D118, the gcc-shaped CLI) is merged to main: positional
  operands are input files, `--pattern` is the literal-pattern flag,
  `examples/makefile/` exists and is wired into `make test` as
  `test-examples`. `--version` and `PCREC_VERSION` ([REL-1.4]) exist, and
  `CHANGELOG.md` exists. README's own quickstart already uses the new
  `--pattern` grammar.

This lane's actual new work was narrower: the RUN-STAMP mechanism (fully
unbuilt before this lane), CONTRIBUTING.md (did not exist), and the
darwin stranger's-build verification.

## (1) CONTRIBUTING.md

`CONTRIBUTING.md` (root, new file): build/test commands, a "Before you
open a PR" checklist, a "Where things are" paragraph pointing at the root
CLAUDE.md, the D26 compat standard in two sentences, and a closing note
that the internal lane/manager process (CLAUDE.md, docs/dev/, worktrees)
is not required reading for a contributor. Per Frank's 2026-09-21 ruling
recorded at `docs/dev/plan.md:587` ("leave extra docs"), no
SECURITY.md/CODE_OF_CONDUCT.md were added.

README.md's "More" list gained a `CONTRIBUTING.md` link (one line);
nothing else in README changed — it was already brought up to date by an
earlier lane (D116's "brief and friendly" rewrite, already on main).

## (2) PR template

Per the brief: **did not** create `.github/PULL_REQUEST_TEMPLATE.md`
(rel16 owns `.github/`). Took the **preferred** option instead: the PR
checklist is CONTRIBUTING.md's "Before you open a PR" section (`make
strict` clean, `make test` green or documented skips, paste the RUN-STAMP
line, `docs/spec/` hunk for observable changes, a test for behaviour
changes with its oracle named, `CLAUDE.md` maintenance). No file was
written for rel16/the manager to place — nothing to coordinate.

## (3) RUN-STAMP

Did not exist anywhere in the tree before this lane (`git grep` for
`RUN-STAMP`/`tree-SHA`/`dirty-flag` inside a runnable script found only
the plan.md prose defining it). Definition used, verbatim from
`docs/dev/plan.md:606`: *"`make test` emits tree-SHA/dirty-flag/counts/
duration; the template asks for the paste."*

Implementation rides the EXISTING completion trailer
(`tests/lib/test_trailer.sh`, [CHK-2 trailer]) rather than a parallel
mechanism, per `docs/dev/learnings.md` §3 and the
`pcrec-general-mechanisms-not-special-cases` memory:

- `Makefile`'s `test:` recipe (the one place it already runs `git` for
  nothing and does no timing) now computes `RUN_STAMP_SHA` (`git
  rev-parse HEAD`), `RUN_STAMP_DIRTY` (`git diff`/`git diff --cached`
  both empty ⇒ `clean`, else `dirty`), and `RUN_STAMP_DURATION` (wall
  time of the `$(MAKE) -k $(TEST_SECTIONS)` pass), and hands all three to
  `test_trailer.sh` as env vars.
- `test_trailer.sh` prints one extra line, only when at least one of the
  three vars is set (so a direct, non-`make test` invocation — as its own
  reproduction transcripts in `docs/testing.md` do — is unaffected):
  ```
  RUN-STAMP: tree=<sha> (clean|dirty) sections=N/M duration=<n>s
  ```
- "counts" in the definition is the trailer's own existing `sections
  ran: N/M` — restated in the stamp line rather than re-derived, so the
  one section-count aggregation in the tree stays the one place that
  counts sections (the same K35-shaped concern the trailer itself was
  built to avoid).
- Documented in `docs/testing.md`, new "RUN-STAMP ([REL-1.5],
  2026-09-21)" subsection immediately after the existing trailer
  write-up it extends.

Validated directly (not via a full `make test`, per the box's one-heavy-
suite-at-a-time rule): synthesized a two-marker directory and called
`tests/lib/test_trailer.sh` both with and without the three env vars set
— the stamp line appears correctly formatted in the first case and is
silent (unchanged old behaviour) in the second. `make -n test` confirmed
the recipe expands and quotes correctly (no `$$`/`$` escaping errors).

**Owed**: a first REAL RUN-STAMP line from an actual `make test` pass —
this lane never ran the full suite (scope + box-concurrency discipline).
The manager's own merge-time `make test` will produce the first live one;
worth eyeballing that its `sections ran` number matches the trailer's
existing count on the same run.

## (4) Stranger's build — darwin arm

Scratch clone at `/Users/fdicostanzo/pcrec` → session scratchpad
`.../scratchpad/stranger`, pinned at main `f12e123d` (confirmed with
`git log -1` post-clone), deleted at the end. Default `CC` (Apple clang,
`Apple clang version 21.0.0`) throughout — no `gcc-16` override, no
environment prep beyond the clone itself.

| step | command | result |
|---|---|---|
| build | `make` | clean, `build/pcrec` + `build/libpcrec.a` built |
| strict | `make strict` | `strict: whole tree compiles clean with -Werror -Wshadow` |
| version | `build/pcrec --version` | `pcrec 0.1.0-beta` |
| README example | the four lines verbatim (`make`; `build/pcrec -p rx --emit-main -o matcher.c --pattern 'a(b|c)+d'`; `gcc -O2 -o matcher matcher.c`; `./matcher 'xxabcbdyy'`) | `match 2 7`, exit 0 |
| examples build | `make -C examples/makefile PCREC=<clone>/build/pcrec` | builds `libmatchers.a` + `example`; one PRE-EXISTING `-Wcomment` warning from Apple clang on `main.c`'s `/*` inside a block comment (harmless, not introduced by this lane, `examples/` not in this lane's scope to fix — flagged here for whoever does own it) |
| smoke: CLI | `timeout 600 make test-cli` | 284 passed, 0 failed, 17s wall |
| smoke: examples | `timeout 900 make test-examples` | 3 passed, 0 failed, <1s wall (resolves `gcc-16` internally via `tests/lib/cc_resolve.sh` for its own GNU-gcc check, separate from the plain-`make` build above) |

**Prerequisites found unstated**: none. Everything the clone needed (a C
compiler + GNU make, nothing else) was already exactly what
README/CONTRIBUTING now say — no doc fix was needed as a result of this
run, unlike §6 of `rel1pre_facts.md`'s survey (which was written before
[REL-1.10]'s README pass and this lane's CONTRIBUTING.md landed).

### Linux arm command block

For the manager to post to the executor verbatim (ubuntu, real GNU `gcc`,
`libpcre2-dev` optional — swap in whatever path the executor clones to):

```sh
# Fresh scratch clone, pinned at the same commit as the darwin run above.
git clone /home/duxevents/pcrec /tmp/pcrec-stranger-linux
cd /tmp/pcrec-stranger-linux
git checkout f12e123d17d9c2c29d9bce411f6ebe354c06612d

# Build + strict, default CC (real gcc on this box, no override needed).
gcc --version | head -1
make
make strict

# Version + README's four-line example, verbatim.
build/pcrec --version
build/pcrec -p rx --emit-main -o matcher.c --pattern 'a(b|c)+d'
gcc -O2 -o matcher matcher.c
./matcher 'xxabcbdyy'        # expect: match 2 7

# The Makefile example (PCREC already defaults to ../../build/pcrec
# relative to examples/makefile, which is correct for this clone layout).
make -C examples/makefile PCREC="$PWD/build/pcrec"
./examples/makefile/example

# Smoke tier (NOT the full make test).
gnutimeout 600 make test-cli
gnutimeout 900 make test-examples

# Cleanup.
cd /
rm -rf /tmp/pcrec-stranger-linux
```

Notes for the executor: this box's bare `timeout` is uutils, not GNU —
use `gnutimeout` per `CLAUDE.md`'s situation index and
`docs/testing.md` "The `timeout` binary itself"; `libpcre2-8-0` is
optional for this smoke tier (neither `test-cli` nor `test-examples`
invokes the differential-only PC-3/PC-4 stages) so it does not need to be
installed just for this run.

## Validation (this worktree, docs-only control)

```
make -j4 CC=gcc-16 && make strict CC=gcc-16
```
Both clean (the tree's own changes here are Makefile/`.sh`/`.md` files;
the `make`/`make strict` run is a control that nothing else in the tree
regressed, not a test of the new content). No census/pin file references
`CONTRIBUTING.md` or `README.md` today (grepped: zero hits outside this
lane's own new/edited files), so no re-pin is owed. No `abi`-adjacent
files touched.

## Handback

Complete: CONTRIBUTING.md (with the PR checklist inline, not a separate
`.github` file), RUN-STAMP (implemented, documented, unit-validated —
first *live* stamp is owed at the manager's next real `make test`), the
darwin stranger's-build transcript above (clean, no undocumented
prerequisites found), and the Linux arm command block for the executor.
Not touched: `.github/`, `lib/`, `src/parse/` (sibling lanes' scope).
