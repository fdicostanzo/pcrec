# lane w11 — [DD-13b.W1.1] report

Branch `lane/w11`, from main `1ac1405`. Written 2026-08-30.

> **STATUS: CODE COMPLETE, NOTHING EXECUTED.** The manager's measurement
> HOLD was in force for the whole of this lane's life and was never
> lifted. Every one of §7.2's eight acceptance criteria requires running
> something the hold forbids by shape. **Not one of them has been
> measured.** What follows separates, line by line, what was BUILT from
> what was VERIFIED — which on this lane is: everything, and nothing.

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

## (b) §7.2 "Green means, exactly" — the table, filled

**Every MEASURED value below came from `grep`/`awk`/`wc`, which the hold
allows. Every value marked OWED requires an execution the hold forbids.**

| # | criterion | status |
|---|---|---|
| 1 | C1 three-way byte-identical over 179/3,265; field manifest asserted; leg B through the `$@` branch | **BUILT, UNMEASURED.** All three legs and both projections are written; the manifest asserts the 15 column names, the per-row field count and the row totals; leg B is invoked through the argument branch. Never run. |
| 2 | C2 equal to the pins over 178/3,262/26,680 | **NOT RUN, and NOT THIS SECTION.** C2 *is* `make test-corpus`; re-running it here would double the suite's most expensive section to assert numbers it already asserts. What `tests/rxtsource/` adds is C2's DENOMINATORS, asserted as a subtraction. |
| 3 | C3 runs at all, over its own discovery, short list HARD FAILING, two totals pinned | **BUILT, UNMEASURED.** `--min-files` is a hard fail whose floor comes from the caller and never from the discovery it checks; `FILES=` and `SKIP=` (broken out by reason) are new output lines. The totals themselves are **OWED** — they cannot exist until it runs. |
| 4 | C0a's two independent assertions both 0 | **BUILT, UNMEASURED.** Assertion (a) is an EXTERNAL count via a wrapper around the binary, not a counter inside run.sh — a counter maintained by the script that decides whether to call shares a source with what it counts. Assertion (b) is an awk census over raw bytes. A disagreement between them is its own failure mode. |
| 5 | every sabotage row turns its NAMED check red | **CANNOT BE MEASURED BY THIS LANE.** Measuring it is `make mech`, which the lane brief forbids me by name. Ten rows are written (S194-S203) with anchors verified unique against the tree and reach populations verified non-empty; the DETECTED/UNDETECTED measurement is the manager's. **Two rows are deferred, not dropped** — see (c). |
| 6 | the arm-block hash pin and the 32-keyword census run as checks | **BUILT, UNMEASURED.** Pin: 252 lines between the markers, `sha256 3e945390…`, update rule in the failure message. Census: the pinned 32 verbatim from format_design §1.1, plus 4 this step adds arms for. |
| 7 | **C1's runtime measured and recorded** | **OWED.** The runner times and prints all three legs per run; the number does not exist until it runs. §7.4 named this as risk 1 and required it *before* item 6. |
| 8 | `make strict` clean; spec hunks S1/S1b/S3/S10 in the same change | **Spec hunks: DONE** (`8a0a918`). **`make strict`: NOT RUN.** Nothing in this lane has been compiled. |

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

1. **Everything in §7.2 that requires execution.** The hold was never
   lifted. I did not run `make`, `gcc`, any built binary, any
   `tests/**/run*.sh`, or any corpus pass. I also did not run
   `bash -n` on the two scripts I edited or a single-file
   `verify_rxt.py` smoke test, reading the hold's shape list as covering
   them; I asked the manager for a ruling on that narrow point and had no
   answer by the time this was written. **The C code has never been
   compiled.** Three compile-class defects were found by reading (below);
   there may be more.

2. **Sabotage validation is structurally out of this lane's reach.**
   §7.2 item 5 requires each row to turn its named check red. That
   measurement is `make mech`, which my brief forbids me by name
   ("NEVER `make test`, `make san`, `make ubsan`, `make asan`, mech, or
   the full battery — those are the manager's"). I have written the rows,
   verified every anchor occurs exactly once in the tree, and verified
   every `SAB_REACH_POP` names a real file with a non-empty population.
   The verdicts are the manager's to take.

3. **Two sabotage rows are DEFERRED with the reason written down**
   (`tests/rxtsource/CLAUDE.md`). §7.2 anticipated one exclusion; there
   are two:
   - **S-C8** — as the design says, there is no composer to plant in and
     no corpus file that composes. Arrives at W1.3.
   - **S-C7** — *not* anticipated as an exclusion. Its named detector is
     C0a's invocation counter, and in W1.1 the only way to move that
     counter is to make the head detector fire spuriously, which is
     **S-C12's plant exactly** (live as S203). The two rows are the same
     edit until a composer exists to distinguish them. Flagged rather
     than quietly counted as covered.

4. **`--source`, `--target`, `--lib-path`, `--emit-composed` are not
   built.** §5's prose lists the first two under W1.1; §7.1's build
   order, §7.2's acceptance and §4's spec-hunk table all name only
   `--list-source` (S11, the flag surface, is assigned to W1.2). W1.1 has
   no build path and no store scan for them, so they would be flags whose
   only behaviour is to refuse — built ahead of a consumer, which D77
   forbids. **If the manager wants them anyway, say so; it is a small
   change.**

---

## (d) Findings for the manager

### 1. `verify_rxt.py` could not parse 4 of the corpus's 14 line kinds

`parse_rxt` knows 10 kinds. The corpus uses 14. `gu` (23 lines),
`frames-buffer=` (9), `engine` (5) and `budget` (3) each reach
`raise ValueError("unrecognized line")`, so wiring the oracle over the
corpus dies on **5 files** — `tests/harness/giveup.rxt`,
`tests/recursion/d27/sr_depth.rxt`, `tests/recursion/framebuffer.rxt`,
`tests/recursion/quantified.rxt`, `tests/size/size_term.rxt` — before
scoring a single expectation. Fixed here (it is F14's territory): all
four parse, `engine`/`budget`/`frames-buffer=` are recognised and ignored
(they configure pcrec's own machinery and mean nothing to python `re`),
and `gu` is a COUNTED skip.

**CORRECTION TO MY OWN FIRST REPORT OF THIS.** I sent it to the manager
as a new finding. It is not. `tests/harness/CLAUDE.md` has recorded it
since [DD-14] wave A — by name, with all three kinds listed, and
explicitly as *"a live gap, recorded rather than silently worked
around"*. That entry was right that it was harmless and right to write it
down. What it could not see is that its own reason — *"no automated
invocation reaches it"* — was a fact about the WIRING, and W1.1 is the
change that moves the wiring. **The general shape is worth keeping: a
gap documented as harmless BECAUSE nothing reaches it expires silently
the moment something does, and nothing watches that direction.** That is
[MECH-REACH] read backwards, and the tree has no checker for it either.

### 2. A grammar contradiction, resolved conservatively — needs ratification

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

### 3. The seam had ZERO population, and now has seven witnesses

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

### 4. A population number in the design is the census's, not the mechanism's

w1_impl §3.1.1 gives S-C2 a population of **171** corpus lines / 90 in
`tests/base`. Both are right for "a line containing `\x` anywhere". Both
are wrong for the plant, which is in `decode_subject` — that function only
ever sees the text between a case line's quotes, so `\x` in PATTERN text
is not in its population. MEASURED: **115 corpus / 53 in `tests/base`**.
This is exactly the `# pcre2-only` 636-vs-571 lesson the same section
records, arriving one row over.

### 5. Two parser disagreements, both measured free, both fixed

- run.sh's directive arms all end `[[:space:]]*$` and ACCEPT trailing
  whitespace; pcrec would have refused it. 0 corpus directive lines carry
  it, so the disagreement was unreachable — which is why it was worth
  fixing now rather than leaving the two to agree by luck of the corpus.
- run.sh's `pattern` arm is `^pattern\ (.*)$` — a LITERAL space — and
  verify_rxt uses `startswith('pattern ')`; my parser accepted a tab. 0
  of 3,265 pattern lines use one. pcrec now requires the space too.

### 6. Three compile-class defects found by reading

Because nothing could be compiled: a forward declaration naming `RxtP`
~70 lines before the typedef (a hard error); a ternary passed AS a printf
format (found only after giving `rxt_fail` the format attribute the
tree's other varargs formatters carry); and an unbounded
`snprintf`-return accumulation that could wrap a `size_t`. **This is
evidence about the review, not reassurance about the code** — reading
found three, and reading is not a compiler.

### 7. A design-note nit

§1.1 and §3.1 describe run.sh's chain as "13 `[[ =~ ]]` arms". I count
**17 elif arms plus the catch-all**: pattern, flags, features, engine-vm,
engine-bad, budget-steps, budget-frames, budget-bad, `frames-buffer=`,
perr, m, n, ms, ns, gu-internal, gu-typed, `g|gp`. Nothing depends on it
— N3 replaced the line range with markers, which is what I implemented —
but the pin's failure message should not repeat a number that is wrong.
It currently says "13-ARM REGION" in the marker text itself, which I kept
so the marker matches the design note; **if you want it corrected, the
marker text and `ARM_PIN` move together.**

### 8. Setup: the worktree was created in the wrong place

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
