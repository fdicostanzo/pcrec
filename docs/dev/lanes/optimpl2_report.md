# [OPTLOOP.1.impl] BATCH 2 — the necessary literal RUN and its scan pick (lane `optimpl2`)

Branch `lane/optimpl2` from `main` `c051a69b`. D119 cycle-2 batch 2 as Frank
ratified it on 2026-09-22 ("Agree with 15 design decisions"): **[OPT-FREQPICK]
+ [OPT-REQPOS] tier 2b**, landed as ONE `abi` **29 → 30** event because their
populations overlap and two bumps would re-pin the same manifests twice
(`reqpos_2b.md` §7 item 5).

| commit | what |
|---|---|
| `47f697db` | the analysis, the emitter, axis bit 31 with the `1ull` widening, the `REQ_RUN` stamp, `abi` 29 → 30 |
| `c403c672` | the gate (`run_prechecks.sh` §3 both stamps, §3.7 the pick, §4 the run), the `rx_info.flags` mask, the two spec hunks |
| `20a57e06` | sabotage rows S266/S267/S268; the two derived bit-table greps; the limits manifest and the registry axes-coverage pin |
| `b537c30f` | the rest of the D94 ritual (`ABI_EXPECT`, the cpset manifest, the identity gate's narrative), every CLAUDE.md, CHANGELOG |
| `d309641d` | the resource rescue pin, plan.md, `docs/design/CLAUDE.md` |

---

## 0. The three findings worth reading before anything else

**0.1 `reqbyte_freq_pick.md` §8 item 4's own acceptance measurement is
FALSIFIED by the combined event, and the corrected control is the sharper
one.** The note asks the `-e utf8` corpus arm to read **ZERO movers**, as the
assertion that the pick's encoding decline is real rather than a comment. Over
the whole corpus it reads **449**. Nothing is wrong: the note's item 4 was
written for event 1 ALONE, and the RUN is deliberately NOT encoding-gated (a
run of bytes is a run of bytes under either encoding, `reqpos_2b.md` §2.4 item
7) while only the CHOICE of which member to scan for is. All 449 are run
gains and **zero are byte-pick moves**, and the same corpus under
`-e utf8 -fno-req-run` reads **0 movers of 2,836** — which is item 4's control
in the only form the combined event admits, and it is a stronger one, because
it separates the two mechanisms instead of asserting a property of their sum.
The note's constructed witness still holds exactly: `é@` at `-e utf8` stamps
`RX_REQ_BYTE "64"` under `-fno-req-run` and `"195"` without it, `195` being the
run's leftmost member and not the prior's argmin.

**0.2 `reqpos_2b.md` §5.5 arm 2 — "`L == 1` byte identity against
`-fno-req-run`" — was UNAVAILABLE as written, and the reason is a property of
every axis in this family.** `rx_info.flags` mirrors the option word, so a
denied build differs from a default one on every artifact including ones the
axis cannot act on, in the five bytes of one initializer. That is the defect
the mask's own comment records as MEASURED on bit 19
(`-fno-prefilter-collapse`), and the fix is one line: `PCREC_NO_REQ_RUN` joins
`strategy_denials`, which is what makes §4.4b a real arm. **The three
`[OPTLOOP.1]` batch-1 bits are still outside that mask** — each of
`-fno-req-byte`, `-fno-end-window` and `-fno-vm-anchor-bound` moves
`rx_info.flags` on every artifact today — recorded here and in a comment at the
mask, and deliberately not changed: it changes those axes' own denied
artifacts and belongs to their delivery, not this one.

**0.3 THE ONE ARM OF THE RUN WALK WHERE THE CONSERVATIVE ANSWER DELETES A
MATCH IS NOT IN THE DESIGN'S TABLE, AND THE FIRST BUILD GOT IT WRONG.**
`reqpos_2b.md` §2.2 lists `A_REP` with `rmin == 0` as "EMPTY", which is right
about the byte SET and says nothing about CONTIGUITY. A min-0 repeat that
contributes no byte still sits BETWEEN two literals, and treating it as
transparent joins them: the first build of this walk reported the run
`/**/` — four bytes — for a C-comment pattern, true of the match where the
repeat takes zero iterations and false of every match where it takes one.
Caught by reading the emitted artifact of the note's own headline witness
(`nested-comment-rec`'s shape) before any suite ran, not by a check. The
landed arm breaks contiguity exactly as a multi-member class does, and that
pattern now reports the two-byte run every match really does end with. **The
general form: an accumulator that carries a JOIN needs an arm for every node
kind that can sit between the things being joined, which is a larger set than
the node kinds that contribute to the thing being accumulated.**

---

## 1. What landed

### 1.1 [OPT-FREQPICK] — `src/opt/reqbyte.c`'s `rb_pick`, a value under bit 30

The necessary SET and its threaded rightmost `pick` are computed exactly as
before; the choice happens once, at `pcrec_req_byte`'s single return. The
emitted byte is the ARGMIN of `pcrec_byte_freq_ppm` over the set, ties to the
threaded pick when it is among the minima and to the largest such byte
otherwise. No new axis bit (D119 rule 5 is satisfied by bit 30: the MECHANISM
is the pre-check, and which member it tests is a value, `--unroll=K`'s shape).

**The prior is read only under `byte`**, `reqbyte_freq_pick.md` §3.3 clause 3.
Elsewhere `rb_pick` returns the threaded pick, which is byte for byte the
pre-[OPT-FREQPICK] answer — so the fallback cannot regress anything and the
`-e utf8` gates are a control rather than an obligation.

### 1.2 [OPT-REQPOS] tier 2b — the second accumulator, axis bit 31

`RbRun` carries up to `PCREC_MAX_REQ_RUN_SCAN` (32) bytes plus a `trunc` flag;
`RbRuns` carries a subtree's best, head and tail runs plus `all` ("this
subtree's language is exactly the stored literal"). `A_CAT` joins the left
factor's tail to the right factor's head — which is what finds a run neither
factor carries alone — and `A_ALT` keeps only the branches' longest common
prefix and common suffix. Both spines stay ITERATIVE.

**Bounded rather than exact, stated as a limit and not as a silence.** A run is
tracked to 32 bytes and truncated beyond that, which is sound in the only
direction that matters — a contiguous substring of a necessary contiguous run
is itself one — and `PCREC_MAX_REQ_RUN_SCAN`'s `limits.def` row says so. 32 is
four times the emitted cap, so the window choice below is EXACT for every run
length the corpus and the bench contain (longest measured 11).

**The truncation rule is Frank's**: a run longer than
`PCREC_MAX_REQ_RUN_EMIT` (8) becomes the 8-byte window containing the scan
member whose bytes sum to the lowest prior, ties leftmost, and the leftmost
such window under any other encoding. On `github_pat_` the four candidate sums
are 203,444 / 254,232 / 268,188 / **200,619**, so the emitted run is
`hub_pat_` at scan index 3 — a rule that took the leftmost window containing
the member would have answered `github_p`, which is why `run_prechecks.sh`
§4.5 pins both.

**`Job.req_byte` becomes the run's scan member when a run ships**, chosen at
the same single return, because there is ONE emitted `memchr` and
`<PREFIX>_REQ_BYTE` reports what it tests. 245 of the 406 corpus run-gainers
move their emitted byte for this reason and not for the pick's.

### 1.3 The emitted text — one function, both engines

`emit_req_run_check` is a sibling branch inside
`pcrec_emit_req_byte_check`, and the `L == 1` text is left at its own indent,
un-nested, because sabotage row S265's anchor is in it. The window guard is two
conjuncts at scan index > 0 and ONE at index 0 — the always-true
`>= 0` is omitted rather than emitted, which is `edge1_report.md`'s recorded
`-Wtype-limits` class, and `run_prechecks.sh` §4.1d is its live detector (every
run artifact is compiled under the harness's own `-Wall -Wextra -Werror`).

**Two frames, two escapes.** The run's bytes reach a C comment and a C string
literal in the same function. The comment goes through
`emit_comment_safe_byte` with `*prevp` threaded, and this is not hypothetical:
the note's own headline witness has a star-then-slash run, whose emitted
comment reads `"*\x2fx"`. The literal goes through **`pcrec_sb_cstr`, the
emission kit's third vocabulary** (`src/core/sb.c`), whose numeric escape is
OCTAL and not hex — a hex escape in C consumes as many hex digits as follow
it, so `\x01` before a literal `2` would be ONE character of value 0x12 inside
a literal whose whole job is to be compared against a subject. Verified live:
a run of `y`, 0x01, `2`, `z` emits `"y\0012z"` and compiles clean.

---

## 2. The movers census — MEASURED, base-vs-tip, same `-o` basename

3,171 distinct corpus `pattern` lines, compiled by the branch-point binary and
by this tree's, both written to the SAME `-o` basename in two directories (the
house's four-times-recorded trap), with the `REQ_RUN` stamp line and the abi
digit normalized out so what is left is the mechanisms' own movement.

| arm | compiled by both | identical | MOVED | gained a RUN | byte moved, no run |
|---|---|---|---|---|---|
| default (`byte`) | 2,814 | 2,339 | **475** | 406 | 69 |
| `-e utf8` | 2,836 | 2,387 | **449** | 449 | **0** |
| `-e utf8 -fno-req-run` | 2,836 | 2,836 | **0** | 0 | 0 |

Zero asymmetric refusals on every arm: nothing started or stopped compiling.

**The 69 byte-only pick moves all go the right way.** Median ratio of the old
byte's ppm to the new one's is **13.16×**, range 1.53× to 109×, and **zero**
move to a commoner byte — which is a property of the argmin rather than
evidence, and is stated only because the note's own §4.3 out-of-sample
agreement is the claim a reader will want to see reproduced on a larger
population.

Run-length distribution of the 406 run-gainers (emitted length, so a longer run
appears at 8):

| L | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| patterns | 203 | 130 | 21 | 20 | 5 | 6 | 21 |

**The median case is the cheapest case** — one 16-bit load and one compare —
which is the opposite of what "word compare" sounds like, and is the census's
own finding reproduced on this tree.

---

## 3. Validation

Every log path below is in the worktree unless marked otherwise.

| what | log | verdict |
|---|---|---|
| `make -j4 CC=gcc-16` | `build/base_build.log` (branch point), rebuilt at every commit | clean |
| `make strict CC=gcc-16` | `build/strict.log` | **clean** (`whole tree compiles clean with -Werror -Wshadow`) |
| answer identity vs `-fno-req-run`, every startpos × 3 engines | scratchpad `ident/` | **0 mismatches**, 37 patterns × 3 engines × 36 subjects = **25,296 cells**, 9 engine-refusals |
| answer identity vs `-fno-req-byte`, same shape | scratchpad `ident/` | **0 mismatches**, 25,296 cells |
| every corpus pattern × 3 engine settings | `build/optimpl2_corpus3.log` | **9,513 compiles, 0 internal errors** (3,171 distinct patterns × default / `--engine=dfa` / `--engine=vm`) |
| `tests/codegen/run_prechecks.sh` | run live | **200 / 0** (was 113/0 at batch 1, 123/0 after admin3) |
| `make test-codegen CC=gcc-16` | `build/codegen2.log` | **9 of 10 scripts**; the sole red is the standing darwin `nm arm_a.o` probe (documented in 30 other lane reports) |
| `tests/codegen/run_cpset_structure.sh` | `build/cpset2.log` | **28 / 0** after re-recording the manifest |
| `tests/registry/axes_registry_check.sh` | run live | **123 / 0** (was 120; the pin moved with it) |
| `tests/registry/limits_check.sh` | run live | **27 / 0** after the manifest went 58 → 60 rows |
| `make test-registry` (whole suite) | scratchpad task log | **rc 0**, zero `FAIL:` lines |
| `tests/resource/run_resource_tests.sh` | `build/resource3.log` | **27 / 0** (1 platform-expected darwin skip) after re-pinning the rescue 762312 → 762338 |
| `scripts/m6read_check_sab_anchors.py` | run live | 276 sabotages / **292 anchor sites, all resolve** |
| `scripts/emit_sweep.py --ref c051a69b` | scratchpad `emit_sweep.log` | see below |
| `tests/rxtsource/run_rxtsource_tests.sh` | `build/rxtsource.log` | **212 / 0**, 1 RECORD (this box's documented darwin C3 population note); census 214 files / 3,957 blocks / 29,037 lines UNCHANGED |
| `make test-axes AXES="-fno-req-byte -fno-req-run"` | `build/optimpl2_axes.log` | **OWED**, §6 |
| `make test CC=gcc-16` | `build/optimpl2_test.log` | **OWED**, §6 |

### 3.1 `emit_sweep.py` — the five streams, and what each one's number means

| stream | population | reach | movers | asymmetric |
|---|---|---|---|---|
| `c-default` | 3,957 | 3,535 | 3,535 | 0 |
| `c-vm` | 3,957 | 3,536 | 3,536 | 0 |
| `emit-ir-vm` | 3,957 | 3,536 | **0** | 0 |
| `composition` | 307 | 33 | 98 | 0 |
| `dumps` | 7 | 7 | **2** | 0 |

The two `.c` streams and the composition stream move on EVERY artifact and that
is the abi bump's own point. The two figures worth reading are the other two.
**`emit-ir-vm` reads zero**, which says the `--emit-ir` listing is unchanged —
correct, and not a foregone conclusion: the run is an analysis fact carried in
`Job` and consumed by the search entry, so if it had leaked into the IR render
this stream would have caught it. **`dumps` reads exactly 2** — `--list-axes`
(the `req-run` axis's two rows) and `--list-limits` (the two new rows) — and
the other five registry surfaces are untouched, which is the assertion that
this change reached no caller-visible surface it should not have.

### 3.2 Sabotage rows — written and anchor-verified, solo runs OWED

| row | mechanism | plant | expected |
|---|---|---|---|
| S266 | [OPT-FREQPICK] | the set pick's `argmin` inverted to `argmax` | DETECTED; `prechecks` §3.7's four discriminating rows red, `corpus` **0fail** |
| S267 | [OPT-REQPOS] | the run compare's `!memcmp` sense inverted (`SAB_COUNT=2`, both emitted shapes) | DETECTED; `corpus` red at a large count, `prechecks` §4.1b red |
| S268 | [OPT-REQPOS] | an alternation's head run taken from ONE branch | DETECTED; `corpus` red, `prechecks` §4.7 red, §4.1's `(?:/user\|/users)` row GREEN by construction |

`scripts/m6read_check_sab_anchors.py` resolves all three. The solo `make mech`
runs are OWED (§6) — each rebuilds a tree, and the box had one heavy suite at a
time for this lane's whole working period.

**S266 is the second row in this tree whose only detector is one structural
arm**, and its reason differs from S263's in a way worth keeping straight:
S263's plant throws away a bound, so there is a missing instruction to grep
for; S266's plant keeps everything and picks differently, so the whole
difference is one decimal that is correct under either choice.

**S268 IS `reqpos_2b.md` §5.4's "a run one byte longer than the analysis
proved", in the form the shipped corpus reaches.** The note proposes taking
`.tar` to `.tarz` and observes in the same paragraph that such a row needs its
own witness — a subject carrying the short run and not the long one, which no
corpus file has a reason to hold — so it would ship UNREACHED. An
alternation's common prefix is the same property at a site every `A|B` pattern
exercises, so the plant deletes real matches with no bespoke fixture at all,
and no new `.rxt` file was added (which also means no `.rxt` census pin moved
anywhere in the tree).

---

## 4. The `abi` ritual — every reader, found BY GREP, and two that grep cannot find

Grepping the tree for `29` in an abi context found five live readers, all
re-pinned:

| reader | what moved |
|---|---|
| `src/gen/emit_dfa.c:51` | `PCREC_ARTIFACT_ABI` 29 → 30, the one home |
| `docs/spec/match_api.md` §6 | the abi CHANGE LOG, the only one ([REVW.A1]/D76 addendum) — a new bullet, the old one re-headed "was `29`" |
| `docs/spec/CLAUDE.md` | the batch-1 entry's own pointer |
| `tests/codegen/run_codegen_tests.sh` | `ABI_EXPECT` 29 → 30 plus its narrative clause, copied FROM §6 and never authored there |
| `CHANGELOG.md` | the `[Unreleased]` Added/Changed entries |

**And the two the grep is structurally blind to, both found by running the
suites that COUNT over the area touched** (the D94 addendum's own shape, and
`battriage_report.md`'s SECOND READER CLASS — a manifest whose rows hold byte
counts and cite no digit):

- `tests/codegen/manifests/m5_stage1_stamps.tsv`: **all twelve**
  `EMITTED_BYTES` rows. Read row by row rather than bumped — every delta is
  either **+26** (the eight rows that gain only the `REQ_RUN "none"` stamp
  line) or **+421/+423/+426/+458** (the four whose three-line `memchr` becomes
  the run scan loop, the spread being the run's own length in the comment, the
  literal and the guard).
- `tests/resource/run_resource_tests.sh`'s `[K59-PREMUL]` rescue pin:
  **762312 → 762338**, `+26`, **verified by DIFFING the two artifacts written
  to the same `-o` basename**, which prints exactly four changed lines (two abi
  digits and one inserted stamp). `a{5,25000}` declines the run for a reason
  worth stating: it is a repeat over a ONE-byte body and nothing is joined
  across a repeat's iterations, so its run is one byte and one byte is
  [OPT-REQBYTE]'s own `L = 1` case.

A third pin moved that cites neither a digit nor a byte count:
`tests/registry/run_registry_tests.sh`'s axes-coverage guard, **120 → 123**,
the fourth recorded instance of *a reader whose text never cites the number
still moves with it*.

The identity gate's **(B) pin is deliberately LEFT at `6ab2464e`** and is OWED
to the manager: D76's pin must name a commit REACHABLE AFTER THE MERGE, which a
lane branch's is not (opt5i / ccdiff1 / [EMIT-VERB] / [REL-1.4] / batch 1
precedent). `run_recursion_identity.sh` carries the batch-2 narrative paragraph
saying so, and comparison **(A)** is expected at zero movers — the stamp is a
`#define` above `goto <p>_L0;` and the scan loop replaces text that already sat
in the search entry, so nothing `prog_region()` reads moves.

---

## 5. The `1ull` widening, and the checks that derive their bit tables

`PCREC_NO_REQ_RUN` is **bit 31**, the last bit an `unsigned` constant can name,
so the whole flags enum in `lib/pcrec.h` is respelled `1ull << N` in this
change (Frank's ruling, `reqpos_2b.md` §8 question 4). No value moved and
`pcrec_options.flags` has always been `uint64_t`; what moved is the SPELLING,
which two checks derive their bit tables from by grepping the header and which
both hard-fail on deriving zero bits by design:

- `tests/registry/axes_registry_check.sh:179` and `tests/axes/run_axes.sh:247`
  now read `1u(ll)?`, so the extraction works either side of the widening
  rather than silently deriving zero on one of them. The tolerance is safe
  because the zero-bits hard fail is what it is guarded by.
- `run_axes.sh`'s bit RANGE went `4-31` → `4-63`, with the comment's "31 is
  the width of the `unsigned`" replaced by the width the constants can now
  name.
- Six prose sites (`tests/axes/CLAUDE.md` ×2, `tests/registry/CLAUDE.md`,
  `docs/testing.md` ×2, `tests/axes/run_ksweep.sh`) and two in-script comments.

One consequence the build found rather than the design: `pcrec_axis_on`'s
X-macro used a bare `(dm)` in a boolean context, and with the enum widened gcc
reads an enum constant there as a likely mistake (`-Wint-in-bool-context`,
which `make strict` promotes to an error). Spelled `(uint64_t)(dm) != 0`, same
value, same generated code.

---

## 6. OWED at hand-off

**Three chained runs, armed detached as this lane's last act** (BOILERPLATE's
DO-THEN-FINISH; `nohup … & disown`, so they survive this session's close), one
heavy suite at a time:

1. **Every corpus pattern compiled at the three engine settings** — RAN AND
   GREEN before hand-off: `9,513 compiles, internal errors: 0`
   (`build/optimpl2_corpus3.log`). It is item 1 of the chain rather than a §3
   row only because the chain is where it ran; the number is measured, not
   owed.
2. **`make test-axes CC=gcc-16 AXES="-fno-req-byte -fno-req-run"`** — the
   answer-identity sweep restricted to this batch's two axes, verified against
   `run_axes.sh`'s own spelling before citing it (the whole table is
   multi-hour on darwin). Log: **`build/optimpl2_axes.log`**. Completion line:
   `run_axes.sh:` with its verdict, followed by
   `tests/codegen/run_form_census.sh`'s summary. Expect both axes
   answer-identical to default. **The all-axes sweep is a Linux ask** (I-89).
3. **`make test CC=gcc-16`** — the full suite. Log:
   **`build/optimpl2_test.log`**. The verdict is make's `*** [test-X] Error`
   lines, never `sections ran: N/M` (which counts sections LAUNCHED —
   `learnings.md` §3, lane axesfix's finding).

All three are launched by `build/optimpl2_final.sh` in series; progress in
`build/optimpl2_chain.log`, whose last line is
`[chain] ALL OWED RUNS COMPLETE`. Kill with `scripts/safekill <pid>` (recorded
in that log) if the manager wants the box for a merge battery instead.

`tests/rxtsource` and `tests/resource` were owed at the time §3's table was
first written and BOTH RAN GREEN before hand-off — 212/0 and 27/0, in the table
above. The rxtsource census (214 files / 3,957 blocks / 29,037 lines) is
unchanged, which is this change adding no `.rxt` file measured rather than
predicted.

**Also owed:**

1. **The three sabotage rows SOLO** — `bash tests/mech/run_sabotage_matrix.sh
   S266` / `S267` / `S268`. Each rebuilds a tree; expectations in §3.2.
2. **The bench's own measurement** of the landing-bar cells, after merge, via
   the executor. `reqpos_2b.md` §6.1's four improve cells and
   `reqbyte_freq_pick.md` §7.1's two, plus every carve-out in both notes' §6.2
   / §7.2. **The two `logparse-atomic` cells are the ones to read first**:
   they are where §4.3's no-decline-rule recommendation is falsifiable.
   Nothing in this report is a timing claim — nothing was timed on this Mac.

### 6.1 [MECH-REACH] — the sites this batch will reach, predicted

Batch 1's triage fixed **seven** sites where a check's witness deliberately
omits the pattern's required byte and the pre-check therefore answered before
the mechanism under test ran; each took `-fno-req-byte` at its build site, and
`-fno-req-byte` denies the RUN too, so all seven stay covered.

**The new hazard is one grain over and the full `make test` is its detector**: a
witness whose subject contains the required BYTE but not the RUN now
short-circuits where it previously fell through. `-fno-req-run` at the exact
build site is the remedy where the check needs the byte check to stay, and
`-fno-req-byte` where it does not. I found no such site by inspection, and say
so as an absence of evidence rather than as evidence: batch 1's own seven were
found by running the suite, not by reading it.

---

## 7. Smaller findings

**7.1 `grep -qF`, not a BRE, for any needle containing run bytes.** §4.1's
`*/x` row read NOMATCH against text that was verbatim present, because the
quote before the `*` becomes a QUANTIFIER and the needle's literal prefix
anchors the failure. Every emitted-text needle in §4 is now a fixed string.
The general form: *a check whose needle is built from PATTERN-DERIVED bytes is
a check whose needle is an untrusted regex.*

**7.2 The `-Wcomment` hazard fired twice on this lane's own comments** before it
fired on any emitted text. Writing "the run is a star then a slash" as the two
characters closed the enclosing C comment in `src/gen/emit_dfa.c` and again in
`src/opt/reqbyte.c` — `coding_guide.md` §3.2's rule met from the author's side
rather than the artifact's, and the reason both files now spell the pair in
words.

**7.3 `pcrec_sb_cstr` belongs in the emission kit and not in the emitter**, and
the argument is the one `coding_guide` §4.1 already makes: the tree will want a
C-string escape the first time anything else emits pattern-derived bytes
outside a comment, and the necessary-run pre-check is simply the first. It is
the kit's THIRD vocabulary, and unlike the first two its escape set is not one
this project chooses — the frame is a C token read by the ARTIFACT's own
compiler, so the standard fixes it.

**7.4 `--list-limits` gained two rows and the manifest is a NAME list, not a
count**, so `limits_check.sh` named exactly what changed rather than reporting
a number that had moved. That is the shape r49 ruled for the cpset manifest
arriving from the other direction, and it is why this re-pin took one edit and
no investigation.

**7.5 The design's two `docs/` drive-by corrections were already fixed.** Lane
admin3 landed the `PCREC_ARTIFACT_ABI` citation fix at both live readers on
2026-09-22, before this lane started; `reqpos_2b.md` §5.1's note that they
were wrong is now historical and was deliberately left as it stands (D80: a
design document's own revision is its own change).
