# lane w11 — [DD-13b.W1.1] report

Branch `lane/w11`, from main `1ac1405`. Written 2026-08-30.

> **STATUS: BUILT AND MEASURED.** The HOLD that covered this lane's first
> half was lifted at 06:24 and a bench window ran 07:10-10:45. Everything
> below that says MEASURED was executed; the few things that are still
> owed say so by name.

**Headline results — all MEASURED on the final tree**

| | |
|---|---|
| `make -j4`, `make strict` | **clean** (-Werror -Wshadow, whole tree) |
| **C1**, three-way | **leg A == leg B == leg C, BYTE-IDENTICAL** over 179 files / 3,265 blocks / 22,125 case rows |
| **C1 runtime** | **~8.2 s** — leg A 0.8, leg B 7.2, leg C 0.2 |
| **C2** `make test-corpus` PROCS=4 | **26,680 passed / 0 failed**, 0 compile failures, 0 pending-vm, **178 of 178 workers**, size-log 2,878 |
| **C3** the oracle, first run ever | **13,181 verified / 0 failed** over 179 files; every exclusion counted by reason; nine populations pinned |
| `make test-rxtsource` | **43 checks passed, 0 failed** |
| `make test-codegen` | **5/5 scripts**, K37 green |
| `make test-cli` | **287 cases / 0 failed** |
| sabotage rows S194-S204 | **11 of 11 DETECTED** (two needed witnesses built first) |
| the §7.4 discovery | **ZERO corpus defects** |

**Three defects in shipped code were found, none of them by a check that
already existed:**

1. **run.sh let a typo'd `features` list pass QUIETLY on a `perr` block** —
   found by building a sabotage *witness*, not by any check.
2. **`verify_rxt.py` could not parse 4 of the corpus's 14 line kinds** —
   found by pointing it at the corpus for the first time.
3. **The oracle had no time bound**, and one corpus file does not
   terminate under python `re` — found by the wiring hanging.

---

## (a) Commits on `lane/w11`

| commit | what |
|---|---|
| `da10212` | lane log — hold acked, worktree relocated, the brief's `verify_pcre2` path corrected |
| `4e4894f` | item 1 — `src/parse/rxt_source.c`, `RxtSource`/`RxtRow`, `--list-source`'s TSV; item 2's rxt-escape lands with it |
| `bbec837` | item 4 — run.sh: pin markers, the `have_block` guard generalised, three new block arms + `features only` |
| `d6e0a53` | items 5-6a — run.sh `--dump` (leg B), verify_rxt.py `--dump` (leg C) + the four kinds it could not parse |
| `96a05c9` | items 4/7 — the SEAM in run.sh, `tests/rxtsource/`, the Makefile section |
| `8a0a918` | spec hunks S1, S1b, S3, S10 (D80) |
| `eb5ce2a` | head-bearing fixtures + the head-path checks |
| `39c920f` | item 7 — sabotage rows S194-S203, the `rxtsource` arm, CLAUDE.md updates |
| `e708753` | three self-review defects found by reading + two parser-agreement fixes |

---

## (b) §7.2 "Green means, exactly" — the table, MEASURED

| # | criterion | result |
|---|---|---|
| 1 | C1 three-way byte-identical over 179/3,265; field manifest; leg B through the `$@` branch | **PASS.** leg A == leg B and leg B == leg C, `diff`-clean, over 3,265 block rows and 22,125 case rows. Manifest asserted: the 15 column names, 15 fields on every data row, and the row totals. |
| 2 | C2 equal to §3.1's pins over 178/3,262/26,680 | **PASS.** 26,680 / 0; compile failures 0; pending-vm 0; 178 of 178 workers. See the size-log note below — one number moved and it is derivable. |
| 3 | C3 runs at all, over its OWN discovery, short list HARD FAILING, totals pinned | **PASS.** 179 files (its own `find`-derived discovery, floored at the census), 13,181 verified, 0 failed. Nine populations pinned and asserted. |
| 4 | C0a's two independent assertions both 0 | **PASS**, and a third view agrees: the external invocation count is 0, the independent head-bearing census is 0, and pcrec's own dump emitted 0 head-declaration rows over the corpus. |
| 5 | every sabotage row turns its NAMED check red | **PASS — all 11 DETECTED** (S194-S204), run one at a time. Two scored UNDETECTED first and had to be given witnesses; see below. |
| 6 | the arm-block hash pin and the keyword census run as checks | **PASS.** Pin: 252 lines, unchanged. Census: 36 candidate keywords (the pinned 32 plus W1's 4), all 0 in first-token position. |
| 7 | **C1's runtime measured and recorded** | **8.2 s.** leg A 0.74 s (179 `--list-source`), leg B 7.32 s, leg C 0.17 s. §7.4's risk 1 is closed: ~0.2% of a `test-corpus`. |
| 8 | `make strict` clean; spec hunks in the same change | **PASS** both. |

**The one C2 number that moved, and it is a derivation not a drift.**
§3.1 pins `size-log rows: 2877`, taken on a run where 29 cases and **1
distinct pattern-compile** failed (the known `counterk` load cell). This
run had **0** of both. The size log takes one row per SUCCESSFUL compile,
so one fewer distinct compile failure is exactly one more row:
2877 + 1 = **2878**. The pinned value is the loaded-run figure; 2878 is
the clean-run figure the same section already describes as "clean 0".

### Measured facts §7.2 requires not to move — all re-derived here

| quantity | pinned | measured this lane | how |
|---|---|---|---|
| files / blocks / expectation lines | 179 / 3,265 / 26,691 | **179 / 3,265 / 26,691** | first-token census (awk), a 4th independent derivation |
| head-bearing files | 0 | **0** | awk over first non-comment line |
| leading-whitespace lines | 0 | **0** | grep |
| case lines before a `pattern` line | 0 of 26,691 | **0** | awk from run.sh's arm list |
| pattern lines with a literal tab | 3 | **3** | grep -P |
| the 32 candidate keywords in first-token position | 0 | **0** | the census, now a check |

### Other measurements taken (all new)

| fact | value |
|---|---|
| first-token census | m 10552, n 6780, g 3942, pattern 3265, ns 3167, features 2146, ms 1603, perr 384, gp 240, flags 36, gu 23, `frames-buffer=` 9, engine 5, budget 3 |
| pattern lines containing a backslash | **963** — the rxt-escape's `\\` arm is heavily exercised, not a dead path |
| pattern lines with a control byte other than TAB | **0** |
| corpus DIRECTIVE lines with trailing whitespace | **0** (3 files carry it on other lines, where it is data) |
| pattern lines using a TAB separator | **0** of 3,265 |
| files verify_rxt.py could not parse at all | **5** |
| longest corpus file | 3,804 lines (`tests/assertions/multiline.rxt`) |

---

## (c) What I could not do, and why

1. **`make test`, `make mech` in full, and the sanitizer battery** remain
   the manager's by the lane brief. I ran `test-corpus`, `test-rxtsource`
   and the eleven sabotage rows individually, as instructed.
2. **Two sabotage rows are DEFERRED**, with the reason written in
   `tests/rxtsource/CLAUDE.md`. **S-C8** has no composer to plant in.
   **S-C7** was not anticipated as an exclusion: its named detector is
   C0a's invocation counter, and in W1.1 the only way to move that counter
   is to make the head detector fire spuriously — which is **S-C12's plant
   exactly**, live as S203. The two are the same edit until a composer
   exists to distinguish them.
3. **`--source`, `--target`, `--lib-path`, `--emit-composed` are not
   built** — accepted by the manager; §5 corrected to move them to W1.2.

## (d) Findings for the manager

### 1. THE DISCOVERY (§7.4 risk 2): zero corpus defects, and the design predicted it

First corpus-wide run of an oracle nothing in the tree had ever invoked.
**1,847 reported failures. The split is the finding:**

| | count | what it is |
|---|---|---|
| python **cannot compile** the pattern | **1,814** (98.2%) | `(?(DEFINE)`, `(?1)`, PCRE2's `(?<n>` spelling, `\g<>`, `(?J)`, possessive `?+`, `(?0)` — constructs python `re` does not have |
| `perr` blocks python accepts | **28** | two engines, two grammars |
| **genuine answer differences** | **5** | `a\Z` vs `"a\n"`, and `(?m)^` at end-of-subject |
| **corpus defects** | **0** | |

**All five real differences are in `tests/assertions/`** — the one
directory `docs/spec/rxt_format.md` already declares has a REPLACEMENT
oracle, "because several of its constructs (`\Z`, `\G`, `\K`) have no
python equivalent at all". §3.1.1 predicted exactly this. **No corpus
expectation was edited.**

**Two things had to be built before the oracle could be wired at all.**

- **A PER-FILE WALL BOUND.** `tests/base/d27_k23_ambiguous_decomposition.rxt`
  (`(a{1,3}){65}`, subjects past 100 characters) **does not return** under
  python `re` — 64 characters answers instantly, 70 never does. A
  corpus-wide wiring with no bound hangs `make test` forever. `D45`
  already forbids exactly this for everything else the harness runs
  ("a loud, named FAILURE, never a hang or a silent skip"); the oracle sat
  outside it **because it had never run**. A subprocess, not
  `signal.alarm`: a long `re.search` is one C call that never returns to
  the interpreter, so SIGALRM cannot interrupt it.
- **THE OWN-ORACLE RULE**, which the spec has stated all along and nothing
  implemented. Read as a DECLARATION discovered by looking — the directory
  carries its own `verify_*.py`, excluding this script — never a path
  list. It selected **exactly 17 files / 10,274 expectation lines**,
  reproducing the design note's independently measured figure for
  `verify_pcre2.py`'s coverage with no number carried across.

**Result: 13,181 verified, 0 failed, and every exclusion counted by
reason** (pcre2-only 1,357; giveup 23; composed 0; no-python-expression
1,753; perr-python-accepts 14; own-oracle 10,274), all nine pinned. It
reconciles: 13,181 + 13,421 + 89 (the bounded file's own lines) = **26,691**.

**A correction I owed on this finding.** I first reported the four
unparsed line kinds as a new discovery. It is not:
`tests/harness/CLAUDE.md` recorded it at [DD-14] wave A, by name, as "a
live gap, recorded rather than silently worked around". That entry was
right that it was harmless *because nothing reached it* — and that reason
was a fact about the WIRING, which this step is what moves. **A gap
documented as harmless because nothing reaches it expires silently the
moment something does, and nothing watches that direction.**

### 2. Two of my own sabotage rows had EMPTY POPULATIONS, and one of them found a real bug

The eleven rows were run one at a time: **9 DETECTED, 2 UNDETECTED**.
Both failures are the same shape — a detector with nothing to detect,
[MECH-REACH], in rows written to guard against exactly that.

- **S199** plants "run.sh silently accepts an invalid `features` list".
  MEASURED: **all 59 distinct `features` lists in the corpus are valid**,
  so the plant has nothing to accept. (My first probe of this reported
  every list INVALID — because it passed `-o /dev/null` and pcrec tried to
  write `/dev/null.h`. Re-probed the way run.sh does it.)
- **S204** plants "verify_rxt swallows a line kind it does not know", and
  the sting is that **fixing the four-kinds gap is what emptied its
  population**: once the parser knows all 14 corpus kinds, no corpus line
  reaches its unknown-kind branch.

Both now have witnesses under `tests/rxtsource/fixtures/`, kept outside
`find … -name '*.rxt'` so the census is untouched. Both re-ran **DETECTED**.

**And building S199's witness found a PRE-EXISTING DEFECT IN SHIPPED
CODE.** run.sh validates each distinct `features` list, and its own
comment says why: *"a typo'd features line must be a loud harness
failure, never a quiet pass"* — because pcrec refuses an unknown module
with exit 1, and exit 1 is exactly what a `perr` block asserts. It
recorded that failure once **per case**. A `perr` block has no cases by
definition, so the loop ran zero times, nothing was recorded, and the
block silently never ran. **Exactly the quiet pass the comment forbids,
on exactly the block kind the comment names.** Fixed: the failure belongs
to the BLOCK, so with no cases to hang it on it is attributed to the
block's own `pattern` line. No corpus file is affected.

### 3. An unescaped backtick in a sabotage field, and the check that now sees it

`tests/mech/sabotages/CLAUDE.md` has said since [M6.5.2] that a stray
backtick in a double-quoted field is *"a defect no anchor check can
see"*. **Three of my rows landed with it** (S196/S197/S202), each
silently losing the one word naming what it sabotages. `VALIDATE_ONLY`
passed all three, because the row still loads.

The check now exists, and it must scan the row's **TEXT, not its sourced
value**: an unescaped backtick is *consumed* by command substitution and
its span replaced by the output, so a value that still holds a backtick
proves it was **escaped and safe**, while a value that lost one shows
nothing. **The defect destroys its own evidence.** Sabotage-validated in
both directions.

**I got this wrong first, and it is the more useful half of the story.** A
naive grep for a backtick anywhere in a double-quoted field reported nine
rows, six of them pre-existing. I acted on it and rewrote twelve files
before noticing the result had turned safe `\`` sequences into a literal
`\'`. Reverted. Against the correct, escape-aware predicate, **exactly
three rows are defective — all three mine, none pre-existing.** A measured
grep welded to an untested inference, which is the failure
`docs/dev/learnings.md` has just gained a bullet for.

### 4. A grammar contradiction, resolved conservatively — RATIFIED by the manager

`format_design.md` §1.3 gives a pattern block's `description` the full
`prose-value` production, which includes the `|` BLOCK SCALAR. §1.2's
lexical rules say a pattern block's lines are NOT indented, and a block
scalar IS indented continuation. **Both cannot hold in the body.**

RULED, in all three parsers: `|` is a HEAD form; a block's `description`
is one-line only, refused by name with the reason stated. Because (a) the
body's no-indent rule is what R-COMPAT-1 and 3,265 blocks depend on, and
§1.2 calls the head/body asymmetry "the only one"; (b) a body block
scalar needs continuation parsing inside run.sh's per-line loop — head-
shaped parsing back in the harness, which is what the seam ruling
removed. MEASURED FREE: 0 corpus lines indented, 0 blocks carry a
`description`. Per memory `pcrec-dd13b-syntax-is-managers` this is the
manager's call, so it is flagged, not buried. A fixture asserts all three
parsers agree.

### 5. The seam had ZERO population, and now has nine witnesses

0 of 179 corpus files are head-bearing. So the seam, the head grammar and
every refusal it carries would have shipped with an empty population, and
every check named as their detector would have been green while detecting
nothing. `tests/rxtsource/fixtures/*.rxtin` are the witnesses — named
`.rxtin` so `find tests -name '*.rxt'` cannot see them (they must not
join the corpus, move its pinned census, or be dispatched by run.sh's own
no-argument discovery). They make reachable: the seam end to end with the
`--list-source` call counted externally, the body-start line checked
against an independent `grep`, the head-and-no-body file as a distinct
observable, and five refusals each asserted to NAME what the author must
act on.

### 6. A population number in the design is the census's, not the mechanism's

w1_impl §3.1.1 gives S-C2 a population of **171** corpus lines / 90 in
`tests/base`. Both are right for "a line containing `\x` anywhere". Both
are wrong for the plant, which is in `decode_subject` — that function only
ever sees the text between a case line's quotes, so `\x` in PATTERN text
is not in its population. MEASURED: **115 corpus / 53 in `tests/base`**.
This is exactly the `# pcre2-only` 636-vs-571 lesson the same section
records, arriving one row over.

### 7. Two parser disagreements, both measured free, both fixed

- run.sh's directive arms all end `[[:space:]]*$` and ACCEPT trailing
  whitespace; pcrec would have refused it. 0 corpus directive lines carry
  it, so the disagreement was unreachable — which is why it was worth
  fixing now rather than leaving the two to agree by luck of the corpus.
- run.sh's `pattern` arm is `^pattern\ (.*)$` — a LITERAL space — and
  verify_rxt uses `startswith('pattern ')`; my parser accepted a tab. 0
  of 3,265 pattern lines use one. pcrec now requires the space too.

### 8. Defects found in three waves — by reading, by building, by running

Worth separating, because each wave found a class the previous one could
not, and the last two only became possible when the hold lifted.

**By READING** (while nothing could be compiled): a forward declaration
naming `RxtP` ~70 lines before the typedef — a hard error; a ternary
passed AS a printf format, visible only after giving `rxt_fail` the
format attribute the tree's other varargs formatters carry; and an
unbounded `snprintf`-return accumulation that could wrap a `size_t`.
**Evidence about the review, not reassurance about the code** — reading
found three, and reading is not a compiler.

**By BUILDING:**

1. **A `-Wformat-truncation` that would have failed `make strict`.**
   `rxt_fail` formatted the body into a scratch buffer as large as the
   destination and spliced the two, which is precisely what gcc warns
   about. Now composed in place.
2. **Four diagnostics repeated the file path INSIDE the sentence**, and
   `pcrec_error.msg`'s 256 bytes then truncated away the part the reader
   **cannot derive** — the *other* site's line number on a duplicate, and
   the boundary line on a misplaced head declaration. The path is already
   in the message's own prefix, so the repetition bought nothing and cost
   the only fact the author needed. Found by *reading actual output*, not
   by any check. **LEARNINGS CANDIDATE (the manager's flag): a diagnostic
   under a length cap should spend its budget on what the reader cannot
   work out for themselves; the redundant half is what truncation should
   be allowed to take, and here it was the other way round.**
3. **A bug in my own check.** `want_cases` subtracted only the `perr`
   lines from the census, forgetting that `g`/`gp` FOLD into the
   preceding case rather than being cases. Replaced with a derivation
   over the five subject-bearing kinds **plus a reconciliation** — cases
   + perr + g/gp must add back to 26,691 — so the two passes check each
   other instead of one being trusted.

**By RUNNING:** the three shipped-code defects above (the quiet `perr`
features pass, the four unparsed line kinds, the missing time bound), the
two empty-population sabotage rows, and — from `make test-codegen` — three
compiler invocations of mine with no visible bound, one of which was
bounded but split across a continuation line the K37 scanner reads as one
line.

### 9. A design-note nit — CORRECTED

§1.1 and §3.1 describe run.sh's chain as "13 `[[ =~ ]]` arms". I count
**17 elif arms plus the catch-all**: pattern, flags, features, engine-vm,
engine-bad, budget-steps, budget-frames, budget-bad, `frames-buffer=`,
perr, m, n, ms, ns, gu-internal, gu-typed, `g|gp`. Nothing depends on it
— N3 replaced the line range with markers, which is what I implemented —
but the pin's failure message should not repeat a number that is wrong.
It currently says "13-ARM REGION" in the marker text itself, which I kept
so the marker matches the design note; **if you want it corrected, the
marker text and `ARM_PIN` move together.**

### 10. Setup: the worktree was created in the wrong place

`git worktree add` had been run with a relative path from admin1's cwd,
so `lane/w11` was checked out at
`worktrees/admin1/worktrees/w11`. Tree was clean at 1ac1405, so I
`git worktree move`d it to the briefed path. Same family as the
`cd`-persistence pitfall CLAUDE.md's situation index already warns about
for the wrong-repo commit.

---

## What the next session must do first

1. **Lift, then compile.** `make -j4`, then `make strict`. Expect
   defects: none of this C has met a compiler.
2. **`make test-rxtsource`.** It is cheap (three parses, no compiles) and
   it is where C1's runtime gets measured — §7.4 requires that number
   *before* item 6.
3. **Then item 6's discovery run.** 139 files have never been through
   this oracle. Failures there are PRE-EXISTING expectations, not
   regressions from this change. Produce the triage list (file, line,
   pattern, python-re verdict) and **do not edit a corpus expectation
   inside W1.1** — and note that python `re` is the wrong oracle for some
   of them (`tests/assertions/` is libpcre2's for exactly that reason).
4. **`make test`** for C2 against the pinned baselines.
5. **`make mech`** for S194-S203 — the manager's, not this lane's.
