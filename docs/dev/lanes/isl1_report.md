# Lane isl1 — [ENG-ISL] STEP 1, the VM alternation island

Branch `lane/isl1`, worktree `worktrees/isl1`, based on `main` at `9d8401a`
(abi 17). Evening wave, lane A, TONIGHT's write-only items under the bench
hold (`.hold` present, `.hold_ack` written 2026-09-03 16:59 EDT; no `.lift`
at the time of writing). Everything below was measured on this box while the
hold was in force, so nothing here is a timing number: the only executions
were single `build/pcrec` invocations, single `gcc` compiles and single runs
of the resulting matchers.

## 1. What is on the branch

| | |
|---|---|
| `src/gen/emit_vm.c` | the island: `vm_isl_words` (the input), `vm_isl_build` (the trie + the per-node candidate lists), `vm_isl_emit` (the lowering), the `vm_alt` selection, the `vm_count_slots` push mirror, the `<PREFIX>_VM_ALT_ISLANDS` stamp |
| `lib/pcrec.h` | `PCREC_NO_ALT_ISLAND = 1u << 23` |
| `cli/main.c` | `-fno-alt-island` |
| `src/gen/emit_dfa.c` | `PCREC_NO_ALT_ISLAND` joins `emit_info_def`'s `strategy_denials` mask |
| `src/parse/axes_dump.c` | the `alt-island` axis, two rows |
| `docs/spec/tuning.md` | §2.20 + the `rx_info` flags-table row |
| `docs/spec/match_api.md` | §6.3 family (b): `<PREFIX>_VM_ALT_ISLANDS` |
| `docs/spec/cli.md` | the `-f`/`-fno-` family list |
| `tests/island/` | `island.rxt` (108 cases), `island_caseless.rxt` (6), `run_island_tests.sh`, `CLAUDE.md` |
| `Makefile` | `test-island`, in `TEST_SECTIONS` and `.PHONY` |
| `scripts/alt_census.py` | the corpus census, + its `scripts/CLAUDE.md` entry |
| `src/gen/CLAUDE.md` | the `[ENG-ISL]` section |

`make -j2` and `make strict` are clean. **The abi number is NOT bumped** —
prepared as a separate final commit tomorrow once the manager assigns it
(§6 is the site list).

## 2. The design as built, and where it deviates from the charter

Three deviations, all upward, each with the measurement that forced it.

### 2.1 There is no deferred mask and no slot

The charter says "the DEFERRED MASK lives in a slot, sized from tonight's
corpus census". **It does not need to exist.** Every trie edge is one BYTE, so
sibling edges are disjoint by construction and the walk is a single
deterministic path — there is no unvisited sibling subtree that could still
produce a candidate. The set of alternatives still live where the walk stops
is therefore a function of WHICH NODE it stopped at, which the emitter knows
while it is standing on that node.

The study's §3.2 commit rule (commit only if this accept beats everything
deeper in the subtree AND the best already deferred) is the RUNTIME form of
that same fact, needed by a walker that discovers the path as it goes. An
emitter already has the whole path, so it writes the candidate list out
directly, ascending original index, as a chain of try sites. The two-sided
check the study flags as its one correctness finding is discharged by
construction rather than implemented: the list is sorted by index, so the
lowest index is tried first whatever depth it sits at.

Consequences: `RX_NSLOTS` is unchanged by the island (asserted in
`run_island_tests.sh` block 6), and the study's `max_deferred` number sizes
nothing — it predicts the length of a compile-time chain instead.

### 2.2 The input is the subtree's LANGUAGE, not its branch list

This is the lane's one real finding and it cost a full rebuild of the
predicate.

The charter says "a SORTED TRIE over the LITERAL branches of a flat
alternation", and I built exactly that first. It is right about a pattern as
WRITTEN and wrong about the AST `emit_vm.c` is handed: `src/opt/altcls.c`'s
stage-2 factoring runs before the emitter and rewrites a wide alternation into
a shared first byte plus a nested alternation, so every branch it touched is
an `A_CAT` ending in an `A_ALT` — not a literal run.

**Measured on the branch-test build:**

| | |
|---|---|
| islands stamped on `w-256` | 11 — exactly that pattern's own `RX_ALTCLS_FACTORED` |
| emitted C, `w-256`, island vs chain | 369,847 / 359,001 B = **1.030** |
| `abc\|a\|abd`, `a\|ab`, `(ab\|abc)d`, `fo\|foo\|fool` | **0 islands each** — altcls factors them into a form with an EMPTY branch, which the branch test also refused |
| every answer check in `tests/island/` | PASSED |

So the first build took the island on nothing but the residues altcls had just
created, grew the artifact, and was invisible to the answer corpus. What sees
it is the COUNT, which is why `run_island_tests.sh` block 3 asserts "one
island, not one per factored run".

`vm_isl_words` asks the general question instead: is this subtree's language a
finite set of literal byte strings. Concatenation is a cross product taken
X-major, which is PCRE's own preference order — checked against a shape where
the naive reading differs, `(?:a|ab)(?:c|bc)` on `"abc"`, whose enumeration is
`ac`, `abc`, `abc`, `abbc` and whose lowest matching index is 1, the same word
PCRE reaches by taking `a` then `bc`.

It is budgeted in both directions and the budget is a DECLINE, never a
refusal: `VM_ISL_MAX_WORDS` 8192, `VM_ISL_MAX_BYTES` 262144,
`VM_ISL_MAX_DEPTH` 64. The first two bound the cross product
(`(?:a|b)(?:c|d)(?:e|f)…` is 2^k words in 6k characters); the third is D10 /
R-2's class, since the recursion is over alternation nesting and a pattern
controls that.

### 2.3 An empty alternative is admitted

A zero-length word is an accept at the ROOT node. It needs no machinery — its
candidate list is the root's and its try site adds nothing to
`scan_position` — and refusing it declines every prefix-related shape in the
corpus, since that is exactly what altcls's factoring produces. Found the same
way as §2.2: the four hazard patterns stamped zero islands.

### 2.4 The decline list as built

Stricter than the charter's "any branch whose first element is not a literal
byte", and the difference is worth a ruling (§7 Q2): the island requires
EVERY element to be a one-byte class, because a trie edge is a byte. A branch
like `ab[cd]` could in principle be a trie path plus a residual tail emitted
through `vm_emit`; that is a STEP 2 shape, not this one.

Declined, each a selection outcome with the chain emitting unchanged: any
non-singleton class (including a caseless literal, D23); a quantifier, group,
capture, backreference, lookaround, assertion or call; over budget; fewer than
`VM_ISL_MIN_BRANCHES` (2) literal alternatives; the flag.

## 3. The corpus census (T1)

`scripts/alt_census.py`, over `tests/**/*.rxt` (3,358 patterns in 224 files)
plus pcrec-bench's 33 `bench/altwide/patterns/*.rx`. It reports the pattern AS
WRITTEN, so its qualification is NARROWER than the emitter's (§2.2); every
number is a lower bound, which is the safe direction for sizing.

| | |
|---|---|
| flat alternations, ≥ 2 branches | 1,003 |
| all-literal (qualifying) | 429 |
| declined | 574 |

Top decline reasons: quantifier 166, group 104, an opaque `(?…)` construct 46,
mixed 44, class 41, lookahead 33, named group 29, lookbehind 20.

**Branch widths of the 429:** width 2 dominates at 368; then 3 (16), 4 (10),
5 (3), and the bench's ladder 8/64/96/128/192/256/384/512/1024/2048/4096
(1, 5, 1, 1, 1, 9, 1, 9, 1, 2, 1).

**Trie statistics** (min / median / max): nodes 2 / 3 / 12,364; depth 1 / 2 /
12; fan-out 1 / 2 / 26; **mask depth 1 / 1 / 4**; try sites 2 / 2 / 4,096;
resume points 0 / 0 / 6.

**Mask depth distribution:** 1 → 274, 2 → 150, 3 → 3, **4 → 2**. The two
deepest are `(?:abcd|abc|ab|a)z` and `fo|foo|fo|foo`, both in
`tests/base/alternation_trie.rxt`; every bench pattern reads 1, confirming the
study's `max_deferred` = 0 finding on the same population (the study counts
accepts BEYOND the first).

**The threshold.** `VM_ISL_MIN_BRANCHES` is 2, i.e. every qualifying
alternation. The census is why: 368 of 429 are width 2, so any higher
threshold leaves the mechanism essentially untested by the corpus. The
justification is that the island's forward pass is never MORE byte tests than
the chain it replaces — the same tests, factored — and emits no push where the
chain emits one per untried branch. **The region below the study's own
narrowest measured rung is UNMEASURED**; §5's hand-twin is what would move
the constant, and it is one line.

## 4. The width ladder (T3)

`build/pcrec -p rx --engine=vm` on the bench's `altwide` patterns, each
compiled once, both axes. "code" is comment-excluded bytes — the metric the
500,000 cap measures.

| pattern | code, island | code, chain | ratio | source, island | source, chain | ratio |
|---|---|---|---|---|---|---|
| w-8 | 24,830 | 25,351 | 0.979 | 28,191 | 27,811 | 1.014 |
| w-64 | 89,041 | 97,365 | 0.915 | 100,500 | 103,242 | 0.973 |
| w-256 | 291,958 | 341,071 | **0.856** | 331,467 | 359,001 | 0.923 |
| srt-256 | 291,956 | 301,919 | 0.967 | 331,465 | 320,725 | 1.033 |
| pfx3-256 | 231,577 | 285,269 | **0.812** | 271,794 | 304,135 | 0.894 |
| sh1-256 | 283,724 | 334,863 | 0.847 | 323,647 | 353,127 | 0.917 |
| s-256 | 184,959 | 242,246 | **0.764** | 223,114 | 258,754 | 0.862 |

Three things to read off it.

**The branch-ORDER effect is structurally gone.** `w-256` and `srt-256` emit
291,958 and 291,956 code bytes — two bytes apart. Under the chain they are
341,071 and 301,919, a 13% spread, which is the emitted half of the ×8.87 the
bench measured. Sort order affects the trie's construction only.

**The refusal wall moves.** `w-384` COMPILES on the VM route under the island
at 427,739 code bytes and is REFUSED without it at 508,477 (cap 500,000).
`w-512` is still refused both ways (563,738 island / 678,270 chain), so the
boundary moves from "256 < w ≤ 384" to "384 < w ≤ 512" on the VM route.

**Every island artifact on this ladder is FRAMELESS** (`RX_VM_FRAMELESS 1`),
because none of these branch sets has an alternative that is a prefix of
another, so no candidate chain has a second entry and nothing pushes.

### 4.1 Answer identity, spot checks

Hazard shapes, each compiled once per axis and run once per subject, compared
island vs `-fno-alt-island` vs python3 `re` (spans AND groups):

`abc|a|abd`, `a|ab`, `ab|a`, `(ab|abc)d`, `fo|foo|fool`, `fo|foo|fo|foo`,
`cat|dog|cow`, `(?:abcd|abc|ab|a)z`, `(?:a|ab)(?:c|bc)`, `(?i)cat|dog` — 34
subject cells, **all three agree on every one**. `(ab|abc)d` on `"abcd"`
returns `g0=(0,4) g1=(0,3)`: the island commits to `ab`, the continuation
fails, the candidate chain retries `abc`, and the capture written for `ab` is
rewound by the frame's own trail mark.

Ladder shapes `w-8`, `w-64`, `w-256`, `srt-256` × 7 subjects each (first
branch, last branch, a middle branch, a truncated branch, a non-match, a
branch at offset 1, a branch with a tail) — **28 cells, all three agree.**

### 4.2 The interaction nobody asked for, and it is the one to rule on

**The island makes wide-alternation artifacts frameless, which arms
[CC-DIFF] STEP 1(a)'s `always_inline` on the entry chain, which inlines the
whole island into all six entries.**

| `w-256` | island | chain |
|---|---|---|
| emitted code bytes | 291,958 | 341,071 |
| `.text` (gcc -O1 -c) | **270,544** | 71,293 |
| `.rodata` | 13,744 | 20 |
| gcc wall, whole driver | **5.91 s** | 1.38 s |
| gcc peak RSS | 240,476 kB | 95,340 kB |

`nm` names the cause exactly: on the chain artifact `rx_match_anchored` is one
70 KB static and the six entries are 75-176 bytes each; on the island artifact
there is no `rx_match_anchored` symbol at all and `rx_search` is 58 KB,
`rx_search_in` 51 KB, and `rx_match` / `rx_match_caps` / `rx_match_in` /
`rx_match_caps_in` about 40 KB each — six copies of the trie program.

[CC-DIFF] STEP 1's own measurement gated the attribute on `has_push` because
framed cells showed no benefit; the frameless population it measured was small
programs where inlining SHRINKS the artifact (its record: `.text` 1,561 →
1,417 B). The island creates a frameless population of large programs, where
the same gate costs 3.8× `.text` and 4.3× gcc. **The gate wants a size term.**
That is [CC-DIFF]'s mechanism and needs its own measurement, so I have changed
nothing there — see §7 Q1.

## 5. The hand-twin design (T4), to RUN tomorrow on a quiet box

The study could not measure the cost of a REAL resumed frame — its harness has
no continuation to fail against (its §5 items 5 and 9). That is the one number
this build's candidate chain is unmeasured on.

**What is being compared.** The per-call cost of "commit to a candidate, run
the continuation, fail, resume the next candidate" against the chain's
equivalent, on the SAME pattern and subject.

**Patterns** (each compiled twice, island and `-fno-alt-island`):

| id | pattern | what it exercises |
|---|---|---|
| `p1` | `(?:ab\|abc)d` | 2-deep chain, one push, the minimal resumed frame |
| `p2` | `(?:abcd\|abc\|ab\|a)z` | 4-deep chain, three pushes, the corpus's deepest |
| `p3` | `(?:<w-64's 64 branches, plus a prefix-extended copy of each>)X` | width 64 with a 2-deep chain at every leaf: the resumed frame at a width the study measured (its ×7.0 rung) |
| `p4` | `w-64` verbatim, continuation `X` appended | width 64, prefix-free: NO chain, so the forward pass alone. The CONTROL that separates "the island is faster" from "the resume is cheap" |

**Subjects.** Four per pattern, all 128 KiB, built from the bench's own
`t-128k-sparse` prose with the target placed 16 times (the study's §2.2
primary shape):

1. `hit-first` — the first candidate's continuation SUCCEEDS. Measures the
   forward pass only; the chain's second entry is never reached.
2. `hit-second` — the first candidate's continuation FAILS and the second
   succeeds. **The measurement this twin exists for**: one push, one pop, one
   resume, per hit.
3. `hit-last` — every candidate but the last fails. Depth-4 only (`p2`).
4. `miss` — no hit at all. Measures the walk's die path and the work charge.

**Protocol.** `<prefix>_search` in a find-all loop over the whole subject,
`N = 11` rounds per (pattern, subject, axis), MEDIAN reported, arms
INTERLEAVED round by round (never all-A-then-all-B), `/proc/loadavg`'s 1-minute
figure recorded per row. Answers checked against `-fno-alt-island` on every
round, not sampled. The box must read load1 < 0.5 at the start and the run is
discarded if it exceeds 2.0. Reported as ns/call and ns/subject-byte, with the
per-round range beside the median — [CC-DIFF] STEP 1's own acceptance found
medians that agreed with STEP 0 while the per-round ranges crossed 1.0, and
that is worth knowing before citing a ratio.

**What would falsify the design.** If `hit-second` under the island is not
materially cheaper than under the chain at `p3`, the candidate chain is
reproducing `vm_alt`'s O(n) behaviour in a different guise and the commit rule
buys only the forward pass. §7 Q3 says what I would propose then.

## 6. The abi site list (T5), by grep — do NOT bump tonight

Every reader of the current number, found by `grep -rn` for `abi.*17` /
`\.abi = 17` / `ABI_EXPECT` across the tree:

| # | site | what it holds |
|---|---|---|
| 1 | `src/gen/emit_dfa.c:1603` | `    .abi = 17,\n` — the stamp itself, both engines |
| 2 | `tests/codegen/run_codegen_tests.sh:2758` | `ABI_EXPECT=17` |
| 3 | `tests/codegen/run_codegen_tests.sh:2760` | the `[DD-14.FB]` failure message's bump narrative — one clause per bump; this change appends `17->18` |
| 4 | `tests/codegen/run_recursion_identity.sh:555` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-a3f40b1}"` — gate (B)'s pin, RE-PINNED to this change's last `src/` commit, not renumbered |
| 5 | `docs/spec/match_api.md:159` | "`rx_info.abi` is `17`" in the D76 scaffolding-rule paragraph |
| 6 | `docs/spec/match_api.md:1694` | "`rx_info.abi` is `17` on every artifact today ([CC-DIFF] STEP 1 bumped …)" |
| 7 | `docs/spec/match_api.md:2148` | "the abi-17 entry above lists them", inside `_VM_FRAMELESS`'s second-fact paragraph — **this is D94's fifth reader**, the one a hand-enumerated list missed last time |
| 8 | `src/gen/CLAUDE.md:2399` | the `[CC-DIFF] STEP 1 … abi 16 -> 17` section heading (documentation; the new section I added is undated on this axis and needs the number added) |

Not a reader, checked: pcrec-bench's `PB_SHIM_MIN_ABI` is 15, so 18 clears it
with no bench-side change.

**Why this IS an abi event.** The island adds a `#define
<PREFIX>_VM_ALT_ISLANDS N` line to every VM artifact (D76: changed emitted
scaffolding), and on any artifact that takes an island the emitted PROGRAM
text changes shape entirely. Comparison (A) of `run_recursion_identity.sh`
will move for any of its patterns carrying a literal alternation; (B) is
re-pinned by definition.

## 7. What I need ruled

**Q1 — [CC-DIFF]'s `always_inline` gate.** §4.2: the island creates a
frameless population of LARGE programs, and the attribute then replicates a
70 KB matcher six times (`.text` ×3.8, gcc ×4.3 on `w-256`). Three options, in
my order of preference: (a) add a size term to [CC-DIFF]'s gate (a lane of its
own, with its own hand-twin — the right fix, and it is that row's mechanism);
(b) land the island as it stands and file the interaction, since D82 rules
artifact gcc time an acceptable tradeoff and the `.text` growth is what
inlining always costs; (c) hold the island until (a). I recommend (b) plus a
filed row, because the runtime question the island exists to answer is
unaffected either way and (a) needs a measurement neither lane has.

**Q2 — the decline boundary.** The island requires EVERY element of an
alternative to be a one-byte class. The charter's weaker form ("any branch
whose first element is not a literal byte") would admit `ab[cd]|abx` as a trie
path plus a residual tail emitted through `vm_emit`, which is a real
generalization and a real amount of new machinery (a tail can fail, so the
candidate chain would have to interleave with it). I propose leaving it as a
STEP 2 shape and would like that confirmed rather than assumed.

**Q3 — if the hand-twin falsifies the chain.** If `hit-second` shows no win
(§5), I would propose keeping the island for prefix-FREE alternations only
(where it pushes nothing at all and is unambiguously better) and declining
prefix-bearing ones — a one-line predicate change, and the census says it
would still cover 274 of 429.

**Q4 — the threshold.** `VM_ISL_MIN_BRANCHES` is 2 on the argument in §3, not
on a measurement. The width-2 population is 368 of 429 corpus alternations, so
this is the decision with the widest blast radius in the change. Confirm, or
name the measurement that would move it.

**Q5 — the abi number**, and whether this lane or the manager writes the
`17->18` clause into `run_codegen_tests.sh`'s narrative string (site 3).

## 8. What is NOT verified

**SUPERSEDED BY §11 AND §12 — kept because a lane's own prediction of where it
would be wrong is worth reading against what happened.** Of the seven items
below, six are now measured; the seventh (the census's compiler cross-check)
stands. Two predictions were wrong in opposite directions and both are worth
noting: `tests/island/run_island_tests.sh` was expected to need "at least one
assertion adjusted" and passed 19/19 on its first run, while `make test` was
expected to be mechanical and turned up a REAL DEFECT in `vm_cost` (§11.1).
The original list follows unedited.

### 8.0 The original list, as written before the lift

Everything that needs a suite. Under the hold I ran no `make test`, no
`test-codegen`, no `test-axes`, no harness script, and no timing loop.
Specifically unverified:

- `make test` over the whole corpus with the island live. **The blast radius
  is large**: the census says 429 corpus alternations qualify as written, and
  the emitter's predicate is broader than the census's, so more will take it.
- `make test-codegen` — the byte-identity gates, which WILL move (§6).
- `make test-axes` — the answer-identity sweep over `-fno-alt-island`. The
  axis is auto-derived from `lib/pcrec.h` + `cli/main.c`, so it joins the
  sweep with no edit, and `tuning.md` §2.20 satisfies the sweep's own
  doc-heading cross-check.
- `tests/island/run_island_tests.sh` has never been RUN. It was written
  tonight from the emitted artifacts I did inspect by hand; expect at least
  one assertion to need adjusting.
- `tests/registry`'s axis-registry check against the new `--list-axes` row.
- Any timing number at all. §5 is a design, not a result.
- The census's own cross-check against the compiler (the script reports the
  pattern as written; a `--emitter` mode that reads `RX_VM_ALT_ISLANDS` back
  over the corpus is tomorrow's, and is what would turn §3's "lower bound"
  into a number).

### 8.1 What still stands, after §11 and §12

1. **The census's compiler cross-check.** `scripts/alt_census.py` still reports
   the pattern AS WRITTEN, so §3's 429 is a lower bound on what the emitter
   takes and nothing has closed that gap with a number. The identity gate's own
   run is an indirect answer — 166 of the default axis's call-free artifacts
   carry an island — but that is a different population (call-free, one axis)
   from the census's, and it is not the same question.
2. **The bench's altwide arms.** Every number in §12 is this box, `gcc -O2`,
   one subject shape and a find-all loop. The comparative figures belong to the
   bench at its next pin.
3. **`p3` is a constructed pattern**, not a corpus or bench one — built to
   stress the candidate chain, and labelled as such wherever it is cited.
4. **The `[ART-SIZE]` materiality bar** (§11.4) is the one red left anywhere,
   escalated rather than re-pinned.

## 9. Disclosure

Injected context that shaped decisions: the repo `CLAUDE.md` (the scope
mandate, the situation-index rows on `gnutimeout`/`watchdog`/spec-is-the-
contract/the abi ritual) and the memory index, of which two entries were
load-bearing — `pcrec-general-mechanisms-not-special-cases` (which is why
§2.2's fix generalises the predicate instead of adding an altcls-shaped
special case) and `pcrec-build-under-measurement` (which is why §3's
threshold is named as unmeasured rather than defended).

## 10. Addendum — the manager's rulings, and what is staged for tomorrow

The manager answered §7 in `docs/dev/lanes/isl1_rulings.md` (untracked by
design, never committed) at 2026-09-03 ~17:5x EDT. Recorded here because the
rulings file is not part of the branch and this report is:

| Q | ruling | effect on the branch |
|---|---|---|
| Q1 | **RULED BY FRANK 2026-09-03 ~18:1x EDT ("agree"): the island LANDS AS BUILT.** The size term in [CC-DIFF]'s gate becomes that row's STEP 2, filed by the manager; the lane changes nothing in the gate. The three-point knee ladder below is [CC-DIFF] STEP 2's STEP 0 | none |
| Q2 | CONFIRMED — every element a one-byte class; the tail form (`ab[cd]\|abx`) is a STEP 2 shape the manager files on the row | none, as built |
| Q3 | AGREED as the fallback, but ONLY on the hand-twin's numbers: report the measurement before touching the predicate | none, as built |
| Q4 | CONFIRMED — `VM_ISL_MIN_BRANCHES` 2. The measurement that would move it is a width-2 twin cell, added to tomorrow's timing. Answer identity over the whole corpus is what bounds the blast radius, not the threshold | none, as built |
| Q5 | the number arrives in the lift message; every site written by this lane as ONE separate final commit; the lane may not be first to merge, so 18 is not assumed | none tonight |

**Q1's ladder, as specified, and it is now [CC-DIFF] STEP 2's STEP 0 rather
than this row's own defence.** Single artifacts `w-8` / `w-64` / `w-256`,
island build, gcc each TWICE — as emitted, and with the `always_inline`
attribute hand-removed from the artifact TEXT (no emitter change) — recording
`.text`, gcc wall, peak RSS and one search call's runtime on the same subject
(median of a bounded loop, N stated). Three points are what a size term needs
to find a knee. It lands in §4.2 as a table.

**Q4's cells.** `foo|bar` (prefix-free, no candidate chain, frameless) and
`fo|foo` (prefix-bearing, one push), island vs chain, §5's protocol exactly.

**Staged, not run.** The twin harness is written and smoke-tested in the
session scratchpad (`twin_driver.c`, `twin_run.sh`): a find-all loop over the
whole subject, one line per round carrying `ns_per_call`, `ns_per_byte`,
`load1` and an answer checksum, with the two arms interleaved round by round
and a `load1 < 0.5` gate that REFUSES rather than warns. The checksum is the
answer check and it is per round, not sampled: `hits` plus a sum over every
span, so a build that finds the same NUMBER of matches in different places
still differs. Smoke-tested against an already-built artifact
(`(?:a|ab)(?:c|bc)` on a 17-byte subject, 3 hits, both rounds identical); no
timing was taken, the hold being in force. Nothing in the scratchpad is
committed — if the numbers land, whether the harness becomes a `tests/probes/`
probe is a question for the manager at delivery.

## 11. Validation after the lift (2026-09-03 evening)

Stages 1-4 of the manager's order are complete. Stage 5 (timing) is blocked on
a quiet box and stage 6's last step is the manager's merge re-pin.

### 11.1 `make test` — 16 reds in four families, all closed

`make -j4 test PROCS=3`, 33/33 sections launched, 18:37-18:55.

**One was a REAL DEFECT in this change, and the check that found it is the one
the charter never mentioned.** `tests/possessify`'s boundary row drives
`(x)(?:a|bc)+d`: the `-fno-possessify` build stamped `subject_ceiling` 1024
and then answered straight past 1088, so the row read "parted at never".
`vm_cost`'s `A_ALT` arm was still charging the chain's frame per alternation
while the island had stopped pushing — and `frames`/`pf` are what
`subject_ceiling` is DIVIDED from, so the artifact was DECLARING a smaller
subject than it could match. Over-charging frames is safe for the array and
UNSAFE for the declared limit, which is the half I had not thought through.
`vm_cost` is now the THIRD reader of `vm_isl_build`, alongside `vm_alt` and
`vm_count_slots`. The artifact stamps 2048 and parts at 2051 — inside the
row's own 64-byte window. `tests/possessify` 18/18, and no test was edited to
get there.

Worth recording separately: the first repair I reached for was to REPLACE the
row's witness with `(x)(?:a|b.)+e`, which the island declines and whose
ceiling numbers match the original's exactly. That would have gone green and
left the defect in the compiler. The check was right and the change was wrong.

**The other three families were mechanical, each closed with its diagnosis:**

| family | n | what moved |
|---|---|---|
| limits registry | 3 | `VM_ISL_MAX_WORDS`/`_BYTES`/`_DEPTH` joined the argued allowlist on `VM_MAX_STRIDE`'s rule: over any of them the island is not built and the chain emits unchanged, so none bounds what pcrec accepts, rejects or promises |
| `--emit-ir` ISLANDS | 2 | the section's producer now EXISTS. It was an honest-empty assertion; it is now a three-surface comparison — the `VE_ISLAND` event stream, `Vm.nislands` via the stamp, and the emitted text, none derived from another |
| corpus census pins | 9 | +2 files / +21 blocks / +114 cases for `tests/island/`. All 114 are python-expressible, so `C3_PASS` moves and NO skip bucket does — which is the corpus's own claim rather than an accident |

### 11.2 The identity gate — comparison (A) moves, for the first time ever

Every bump in `run_recursion_identity.sh`'s history says "(A) is still
expected byte-identical, and here that is a real check rather than a
formality". Each of them was a change ABOVE `goto <prefix>_L0;`. This one is
the VM program.

The exemption is an **IFF, not an allowance**: a moved region is excused only
where the subject artifact's own `RX_VM_ALT_ISLANDS` reads > 0, and the
CONVERSE is asserted in the same pass — an artifact that stamps an island
whose region is byte-identical to the pre-island reference FAILS, because the
stamp is then claiming a trie the program does not contain. The bucket also
carries a non-vacuity floor: zero excused patterns fails, so an emitter that
stopped building islands cannot read green.

| axis | same | differing | island-moved | island-stamped-unmoved |
|---|---|---|---|---|
| default | 2070 | **0** | 166 | **0** |
| vm | 2005 | **0** | 236 | **0** |
| noprefilter | 2071 | **0** | 166 | **0** |
| nocaptures | 2118 | **0** | 123 | **0** |

The biconditional is exact on every axis, not approximate.

Comparison (B)'s pre-re-pin footprint, recorded before the pin moved: 1,274 /
2,284 / 1,274 / 857 call-free patterns differ whole-file, and `[vm]`'s `same`
fell to 0 — every VM artifact gains the stamp line whatever its value, which
is the unconditional rule working as designed.

### 11.3 The rest of stages 2-4

| stage | result |
|---|---|
| `make test-codegen` | one red, the [ART-SIZE] bar (§11.4); everything else green |
| `tests/island/run_island_tests.sh` | **19/19 on its first run** — §8 predicted at least one assertion would need adjusting, and none did |
| `make test-registry` | 608 PASS after the axis-coverage pin moved 93 -> 96. **+3, not axis J's +5**: `RX_VM_ALT_ISLANDS` gains no value-set pair because it is an activity COUNT, which is `RX_ALTCLS_MERGES`/`_FACTORED`'s own shape |
| `make test-axes` | **all 22 axes answer-identical**, 2787 s. The new axis reads `agree=22407 budget=0 refused=0 lost=0 gained=0 mismatches=0`, and joined with no edit — the sweep derives its bit list from `lib/pcrec.h` and `cli/main.c`, and reported 20 documented bit mentions in `tuning.md` §2 against 20 derived bits |
| `make strict` | clean |

### 11.4 The one red left, and it is another row's instrument

`tests/codegen/run_size_term.sh` §9 pins the materiality constant (75%) from
both sides with two corpus patterns 0.73% apart. Both are alternation-bearing,
so the island moved both. Measured on the bar's own quantity (argmin rung
bytes over default-K bytes, `--engine=vm`):

| witness | was | now | cell |
|---|---|---|---|
| `((a)\|ab){4000}c` | 0.7475 | 0.7497 | still TAKEN, passes |
| `(?:aa\|a){8,12}+b` | 0.7548 | **0.7499** | now TAKEN, FAILS |

The constant has not moved; the witnesses have converged onto it and are now
0.02% apart, so the bracketing property is gone rather than off by one. Not
re-pinned here: finding a replacement pair means sweeping the corpus at eight
K values per pattern, it is [ART-SIZE]'s instrument, and a witness whose ratio
any future emitter change can move is not a pin on the constant. Escalated.

### 11.5 The abi ritual — 17 -> 18, all eight sites

Seven in `9bc7723` (the stamp, `ABI_EXPECT`, the bump narrative, three
`match_api.md` sentences, `src/gen/CLAUDE.md`); the eighth — `FILEPIN` — in a
follow-up that touches no `src/`, so `9bc7723` remains the change's last src
commit and the gate header's own pin rule holds for a lane that writes its own
bump. **The manager re-pins to the MERGE commit when it lands**, as at every
bump before this one; the header says so where a merger will read it.

VERIFIED after the bump: `tests/codegen/run_codegen_tests.sh` 109 checks
passed, 0 failed, with `[DD-14.FB] (§10.4): rx_info carries the four sizing
fields with abi 18 on both engines`. That is the gate the repo `CLAUDE.md`
names for an abi change.

## 12. The timing (stage 5), measured 2026-09-03 20:5x-21:0x on a quiet box

Protocol as §5 designed it: `<prefix>_search` in a find-all loop over a 131,072-byte
subject, 11 rounds, arms INTERLEAVED round by round, median reported with the
per-round range beside it, `load1` recorded and a `load1 < 0.5` gate that
REFUSES rather than warns (it fired twice on my own gcc's residual load and I
waited it out rather than caveat a number). Answers are checked EVERY round,
not sampled: the driver prints a hit count plus a checksum over every span, so
a build that finds the same NUMBER of matches in different places still parts.
**Every cell below agreed on every round.**

Subjects are built from an `xy`-only background, which contains no letter any
target uses — so a "miss" subject is a guaranteed miss and a placed target is
the only hit. That is why the miss cell is a clean read of the scan path.

### 12.1 The hand-twin, and the discriminator is NOT width

| cell | pattern | width | prefixes | frameless | island / chain | load1 |
|---|---|---|---|---|---|---|
| q4a | `foo\|bar` | 2 | free | **1** | **0.175** | 0.31 |
| pfree | `(?:cat\|dog\|cow)s` | 3 | free | **1** | **0.140** | 0.28 |
| q4b | `fo\|foo` | 2 | bearing | 0 | 1.131 | 0.30 |
| p1_fall | `(?:ab\|abc)d` | 2 | bearing | 0 | 1.144 | 0.41 |
| p1_miss | same, no hit anywhere | 2 | bearing | 0 | 1.146 | 0.46 |
| p2_fall | `(?:a\|ab\|abc\|abcd)z`, three falls per hit | 4 | bearing | 0 | 1.001 | 0.28 |
| p3 | `w-64`'s 64 words plus a one-byte-extended copy of each, then `Q` | 128 | bearing, EVERY path | 0 | **0.010** | 0.24 |

**What settles Q3.** The manager pre-agreed a fallback — island for prefix-FREE
alternations only — if the twin showed prefix-bearing chains not paying. **The
measurement refuses that fallback.** `p3` is the sharpest prefix-bearing shape I
could build: 128 alternatives, every root-to-leaf path carrying two accepts, and
a subject engineered so the FIRST candidate's continuation fails on every hit,
so the candidate chain runs at every one. The island is **99x faster** there.
The resumed frame is not reproducing `vm_alt`'s O(n) chain in a different guise;
it costs one push and an O(1) resume, exactly as §3.2's mechanism predicts.

**What moves Q4, in a direction neither of us named.** The threshold is not
about width. The only cells the island loses are prefix-BEARING and tiny
(1.13-1.15 at widths 2), and the loss is gone by width 4 (1.001) and inverted
by width 128 (0.010). Meanwhile the biggest per-pattern win in the whole set
outside `p3` is prefix-FREE at **width 2** (0.175), which the current floor of
2 correctly admits and any width-based raise would throw away.

The mechanism behind the split is visible in the `frameless` column and is not
a coincidence: a prefix-free island's candidate chain has one entry, so it
pushes nothing, the artifact is frameless, and [CC-DIFF]'s `always_inline` then
deletes the entry-chain call and its frame. A prefix-bearing island keeps a
push, stays framed, and at width 2 the trie walk plus the frame is simply more
work than two short byte runs.

**A refinement the data supports, NOT applied here** (it is a predicate change
and Q3/Q4 were ruled "only on the measurement"; this IS the measurement, so it
is the manager's call): decline where `pushes > 0 && words < 5`. One condition,
reading two numbers `vm_isl_build` already computes, and it removes every
losing cell while touching no winning one.

### 12.2 Q1's inline ladder — [CC-DIFF] STEP 2's STEP 0

Single artifacts, island build, `gcc -O2 -c` twice: as emitted, and with the
`always_inline` attribute hand-removed from the artifact TEXT. No emitter
change. Runtime is the same find-all loop, 11 interleaved rounds, median.

| pattern | .text as-emitted | .text no-inline | code cost | gcc s (as / no) | peak RSS kB (as / no) | ns/call as / no |
|---|---|---|---|---|---|---|
| w-8 | 6,345 | 2,457 | **2.58x** | 0.29 / 0.10 | 35,748 / 32,448 | **0.780** |
| w-64 | 66,777 | 17,081 | **3.91x** | 2.55 / 0.49 | 111,428 / 54,272 | **0.770** |
| w-256 | 280,393 | 43,049 | **6.51x** | 11.99 / 1.82 | 364,336 / 102,180 | **0.842** |

**The exchange rate is what a size term needs, and it is not flat.** The
attribute BUYS a real 16-23% of run time at every rung, and that benefit barely
decays with size. What explodes is the price: 2.6x the code and 2.9x the
compile at width 8, against 6.5x the code and 6.6x the compile at width 256.
At `w-256` an artifact pays six and a half times its machine code and six and a
half times its gcc for 16% of its run time.

So the honest reading is NOT "turn it off on big programs" — the win is real
there too. It is that the exchange rate degrades by a factor of two and a half
across two width decades, so where to stop is a judgement someone has to make
with these numbers rather than a defect to fix. Three points, no emitter
change, as chartered.

### 12.3 What the timing does NOT cover

The bench's own altwide arms. Everything above is this box, `gcc -O2`, one
subject shape (131,072 bytes, 16 placed hits) and a find-all loop. The
comparative numbers that belong in a ledger are the bench's to take at the next
pin. `p3` is a pattern I constructed to stress the candidate chain, not a
corpus or bench pattern, and it is labelled as such wherever it is cited.

## 13. A finding that is NOT this change's: the committed size log is stale

`make test`'s corpus stage rewrites `docs/dev/artifact_size_log.tsv`, so the
run in §11.1 left it modified. **It is restored, not committed**, on
`dd1a39b`'s precedent ("the harness rewrites it on every corpus run") — and
the reason is worth recording, because committing it would have credited this
change with a tree-wide growth that belongs to another row.

`scripts/size_diff` over the committed log against my run reports **2,933 of
2,933 common patterns moved**, total size +1.95%, with almost every row at
exactly **+31 bytes**. That is not the island. Checked directly on
`a{2,4}?b` (`tests/base/review_r2.rxt:52`, one of the movers): it is a
**DFA** artifact, it carries no `RX_VM_ALT_ISLANDS` at all, and it is
byte-for-byte identical under `-fno-alt-island`. The +31 is
`#define RX_DFA_UNIFORM_FOLDS 0` — 31 bytes including its newline —
[CC-DIFF] STEP 1's own stamp, which landed on main at `a3f40b1` AFTER the log
was last regenerated at `9dd1d4c`.

So the committed log is stale on main by one abi event, and the next change to
run a corpus stage inherits that +31 on every artifact in its own diff. The
island's real size movement is in §4 and it is measured per artifact rather
than read off this log: comment-excluded code bytes 0.76-0.98 of the chain's
from width 64 up, `w-256` and `srt-256` within two bytes of each other, and
`w-384` compiling where the chain is refused. The 22 `NEW` rows in the diff
are `tests/island/`'s own patterns and are real.

**For the merge battery:** regenerate the log there, where the corpus stage
runs against the merged tree, and read the per-pattern movement with
`scripts/size_diff` knowing that the first regeneration since `a3f40b1`
carries [CC-DIFF]'s +31 as well as the island's own.

## 14. The manager's rulings on the timing, applied

### 14.1 Q4 APPLIED — a pushing island declines below four alternatives

Ruled on §12.1's table. The predicate gains one condition,
`pushes > 0 && words < VM_ISL_MIN_BRANCHES_PREFIXED (4)`, reading two numbers
`vm_isl_build` already computes and read by all three callers through the same
return.

**The reason it is not a width floor** is the table itself: the discriminator
is prefix FREEDOM. `foo|bar` at width 2 is the biggest per-pattern win in the
whole set outside `p3` (0.175) because its chain has one entry, it pushes
nothing, the artifact is frameless and [CC-DIFF]'s `always_inline` deletes the
entry frame on top. A plain width floor would have thrown away exactly the
population that gains most.

**Four and not five** (the manager's call on the same table): width 4 measured
a wash at 1.001, so it keeps the mechanism at no cost; width 2 loses by 13-14%;
width 3 is unmeasured and sits on the losing side of the knee, so it declines
with 2 rather than being admitted on a guess.

The resulting population, verified against the emitter:

| pattern | islands | frameless |
|---|---|---|
| `foo\|bar` | 1 | 1 |
| `cat\|dog\|cow` | 1 | 1 |
| `fo\|foo` | **0** | 0 |
| `(?:ab\|abc)d` | **0** | 0 |
| `(?:a\|ab\|abc\|abcd)z` | 1 | 0 |
| `(?:abcd\|abc\|ab\|a)z` | 1 | 0 |

`tests/island/run_island_tests.sh` is 24/24 and asserts BOTH directions — the
two narrow declines AND that a narrow PREFIX-FREE alternation still takes the
island, because a floor that caught the prefix-free population is the real
hazard here. Its frame-witness moved from `(ab|abc)d` to `(?:abcd|abc|ab|a)z`:
at width 2 the former is now the chain's, so it would still read frameless=0
and the check would have been passing for a reason unrelated to the island.
Two `island.rxt` comments were corrected for the same reason — those cells are
now the chain's, and they stay in the file because a decline must answer
identically too.

### 14.2 [ART-SIZE] §9 — the fixed pair becomes a WITNESS POOL

The manager's ruling: **the instrument is the defect**, and island-free
witnesses would only move the same fragility to `[OPT-CLSPACK]`. So §9 no
longer pins two patterns' values. It measures a POOL, prints the whole table
whatever the verdict, and passes on the EXISTENCE of a straddling pair.

> **THE TABLE THAT WAS HERE WAS WRONG AND THE POOL IT DESCRIBED WAS VACUOUS —
> see §16.** It labelled three members "island TAKEN" and NOT ONE of the eight
> stamped an island; and the check compared its own computed ratios against a
> literal `0.75` in the script rather than reading the compiler, so the
> materiality constant could be changed to 60 or 85 and every cell stayed
> green. §16.1 carries the pool as it now stands and the sabotage that proves
> it bites. **The band is 0.05** and that is the half that keeps this a
pin rather than "some two patterns exist": a pair at 0.55 and 0.95 would
satisfy "one either side" while saying nothing about where the constant is.
The surviving claim is that a constant of 0.70 or 0.80 fails this file. The
measured pool brackets far tighter than the band demands — 0.7498 and 0.7571,
0.0074 apart — so there is real slack before the band needs revisiting.

No straddling pair is **RED with the table**, never a silent pass: that is the
honest "this population can no longer bracket the constant" finding, and the
failure text says in as many words not to adjust the constant to make it green.
Nothing was re-pinned by hand and the constant is untouched.

**A note on why the old cell would have gone green on its own.** Applying Q4
made `(?:aa|a){8,12}+b` decline the island, which moved it back from 0.7499 to
0.7571 — so the original fixed pair brackets again by accident. That is exactly
the argument for the pool rather than against it: the pair's health was a
coincidence of two unrelated rulings, and the next axis would have broken it
again.

The class-leading member is NEW to the corpus (`tests/counterk/counterk.rxt`,
4 `m` and 6 `n` cells, python-verified). §9's pool must be corpus patterns, and
the corpus had no class-bearing pattern that reaches the ladder.

### 14.3 Final state

| gate | result |
|---|---|
| `make strict` | clean |
| `make test-codegen` | **109 / 31 / 22 / 31 / 7, zero failures** |
| `tests/island/run_island_tests.sh` | 24 / 0 |
| `tests/codegen/run_size_term.sh` | rc=0, 31 / 0, pool brackets |
| `tests/rxtsource/run_rxtsource_tests.sh` | 94 / 0 |
| `make test-axes` | 22 / 22 answer-identical |
| identity gate (A) | differing=0, island-stamped-unmoved=0, all four axes |
| abi | 18 across all eight sites |

**There is no red left anywhere on this branch.** The one item outstanding is
the manager's at landing: (B)'s pin names `9bc7723`, this lane's last src
commit, and must become the merge commit.

## 16. Panel r53, checks lens — three checks that could not fail

The doc lens (§15 is its record in the commits) found five gaps. The CHECKS
lens found something worse in the same branch: **three of the checks this lane
wrote or touched were incapable of failing**, and two of them were checks I had
described in this report as evidence. What follows is what each could not see
and what it asserts now.

### 16.1 §9's pool compared the script against itself (F1)

The pool forced `--unroll=$k`, computed each member's argmin/K8 ratio itself,
and compared that ratio against a **literal `0.75` written in the script**.
Nothing in it read the compiler. `src/core/compile.c`'s materiality constant
could be changed to 60 or 85 and every cell stayed green — while the failure
text asserted "a constant of 0.70 or 0.80 would fail this file", which was
simply false.

The forced-K ladder is the INSTRUMENT now; the ASSERTION is that the
compiler's own `<PREFIX>_UNROLL_K_WHY` stamp at the default equals what the
ratio predicts against the bar, for members on both sides. **Sabotage, run and
recorded:**

| constant | result |
|---|---|
| 70 | RED — 4 members' stamp disagrees with their prediction |
| 75 (shipped) | green |
| 85 | RED — 3 members disagree |

Also in this pass: the byte extraction HARD-FAILS instead of falling back to
whole-file bytes (F9 — the [ART-SIZE] quantity confusion its own learnings
record); the band floor counts BAND-ELIGIBLE members rather than measured ones,
and both sides must carry two DISTINCT shapes (F10 — the whole above side had
been one shape, `(?:aa|a){8,12}+` with and without a trailing character); and
the band value is stated in the script as ASSERTED, not derived.

### 16.2 Not one pool member took an island (F2)

The pool shipped labelling three members "island TAKEN". Measured:
`RX_VM_ALT_ISLANDS` reads **0 on all eight**, and the artifacts are byte-
identical under `-fno-alt-island`. `((a)|ab)` was never eligible — `(a)` is a
capture inside a branch, which the predicate declines by construction. The
"families move in opposite directions" property I claimed for the pool had no
basis at all.

**And §11.4's diagnosis was half wrong.** Measured against a build of `main`
with ONE instrument rather than against the check's inherited comment:

| pattern | main | this branch | why it moved |
|---|---|---|---|
| `((a)\|ab){4000}c` | 0.7495 | 0.7497 | the unconditional stamp line, +0.0002 — it never took an island |
| `(?:aa\|a){8,12}+b` | 0.7569 | 0.7571 | same +0.0002 **post-Q4**; pre-Q4 it read 0.7499, and THAT was a real island effect |
| `(?:aa\|a){8,12}+ab` | 0.7583 | 0.7585 | the stamp line |

So the 0.7475 / 0.7548 in the old comment were a DIFFERENT instrument's and
were never comparable to mine; only one witness ever really moved, and the
island's whole effect on the pair was on that one, pre-Q4. The pool now carries
nine members with shape tags, two of which stamp an island (read off the
artifact, asserted, not labelled by hand).

### 16.3 The identity gate's excuse was a blanket exemption (F3, F4, F5)

`prog_region()` extracts the WHOLE program, and the bucket excused any byte
difference anywhere in an artifact whose island stamp read > 0 — so an
unrelated emitter regression inside an island-bearing artifact read green.
Three changes:

- **The excuse is a claim about the deny axis.** A moved region is excused IFF
  building the same pattern with the SUBJECT compiler under `-fno-alt-island`
  restores the PINNED region byte for byte. Anything else that moved is not the
  island's to excuse.
- **The converse is self-contained** against that same axis rather than against
  the August pin, which decays as the emitter moves: stamped ⇒ differs from its
  own denied build; unstamped ⇒ byte-identical to it. Sabotage run: a scratch
  build that sets the stamp and then falls through to the chain produces **13
  failures**, including the new region checks.
- **The non-vacuity floor is an enumerated manifest**, not a count. "At least
  one island moved" read green under any narrowing that left one island
  standing — raising `VM_ISL_MIN_BRANCHES_PREFIXED` to 40 passes it.

**And my first manifest was itself asserted from memory rather than measured.**
I wrote that "every entry was verified to stamp an island at the landing" and
had not verified them: three of eleven did not — `a|b|c|d|e|f|g|h` (altcls
MERGES single-byte alternatives into a class, so no alternation reaches the
emitter), `fo|foo|fool` and `(?:x|)y` (prefix-bearing at widths the Q4 knee
declines). It read green on the default axis, where all three route to the DFA
and are skipped, and failed only under `--engine=vm`. Every entry is verified
now, and the manifest is gated on the VM route because the stamp is VM-only.

**The post-Q4 island population, per axis** — §11.2's 166/236/166/123 were
PRE-Q4 and nobody had recounted them:

| axis | same | differing | island-moved | stamped-but-deny-is-a-noop | unstamped-but-deny-moves |
|---|---|---|---|---|---|
| default | 2167 | 0 | **74** | 0 | 0 |
| vm | 2144 | 0 | **102** | 0 | 0 |
| noprefilter | 2168 | 0 | **74** | 0 | 0 |
| nocaptures | 2190 | 0 | **56** | 0 | 0 |

**This gate is a byte-inequality gate, not a correctness gate**, and its header
now says so: it says which bytes moved and licenses exactly one reason for
them to have moved. Correctness is `tests/island/`'s oracle-verified corpus and
`make test-axes`.

### 16.4 The rest (F6-F14)

- **F6** — the three enumeration budgets are `limits.def` rows, not allowlist
  entries. The argument that put them on the allowlist was refuted by this
  lane's own §4: "over budget the chain emits unchanged" is true, but the chain
  is never SMALLER than the island, so a pattern that falls back can land above
  the 500,000-byte cap where the island fit under it — `w-384`, 427,739 island
  bytes against 508,477 chain bytes. A budget CAN trade an accept for a reject
  at a cap, which is what bounding acceptance means. Manifest 47 → 50.
- **F7 / F7b / F8** — `tests/island/run_island_tests.sh` read only stamps, and
  all three come from `vm_isl_build`, so an emitter that set `nislands` and fell
  through to the chain passed 24/24. It now asserts the emitted PROGRAM REGION
  differs from the pattern's own `-fno-alt-island` region for taking patterns
  and is identical for declined ones; that a pushing island declares STRICTLY
  FEWER frames than the chain (the frameless stamp reads 0 on both, so the
  witness swap in §14.1 did NOT fix the flaw it was meant to); and
  `RX_ALTCLS_FACTORED > 0` as the factoring precondition, which was printed and
  never checked. 32 checks.
- **F11 / F12** — the listing check compiles `--engine=vm` on both invocations,
  since it demands a stamp the spec makes VM-only; and its mismatch message
  reads correctly in both directions rather than always expanding one way.
- **F13 / F14** — `.gitignore` carries the `docs/dev/lanes/*_rulings.md` GLOB
  main already uses, rather than two named lines that would conflict at the
  merge; and `match_api.md`'s `always_inline` cross-reference is restored to
  "the abi-17 entry", which was correct and direct — that spelling is abi 17's,
  not this bump's.

### 16.5 What this pass says about the branch

Three checks I had cited in this report as evidence could not fail. Two of them
I wrote. The pattern in all three is the same and it is the one
`docs/dev/learnings.md` §3 already names: a check that shares a source with
what it controls. §9 compared the script's arithmetic against the script's own
constant; the island script read stamps that one function writes; the identity
bucket excused an artifact on the strength of a stamp that artifact carries.
The fix in each case was to introduce a term the emitter does not write — the
compiler's own decision stamp, the emitted program text, and the deny axis.

## 17. Panel r53, semantics lens — the island refused patterns pcrec accepts

The doc lens found five gaps and the checks lens found three checks that could
not fail. The semantics lens found the thing that actually mattered: **a
caller-observable acceptance regression**, shipped and invisible.

### 17.1 The regression

`((?:aa|bb)(?:aa|bb)…×10|zzz)` — 96 characters, DEFAULT flags, DEFAULT
engine — was **REFUSED**:

```
pcrec: pattern too large: 897,983 bytes of emitted code (limit 500,000)
```

and compiles at **30,179** bytes under `-fno-alt-island`. An optimization axis
had made pcrec REJECT a pattern it accepts without that axis. Reproduced on my
own build across a ladder: k=8 island 204,664 / chain 28,611; k=9 390,274 /
29,395; k=10 and up REFUSED.

**No check in this tree could see it, and the reason generalises.**
`make test-axes` sweeps the CORPUS for answer identity, no corpus pattern has
the cross-product shape, and its refusal counter therefore read 0. A sweep over
a population that lacks the shape cannot fail on it — the population WAS the
blind spot, not the assertions.

**The cause.** `vm_isl_words`' `A_CAT` cross product. `VM_ISL_MAX_WORDS` and
`_BYTES` bound the WORD LIST; the emitted size follows the TRIE, and the cross
product blows the second up while the first is still comfortable. At the byte
budget the trie reaches ~200,000 nodes, about 44 MB of C. **A budget on the
wrong quantity is not a smaller version of the right one** — and this is the
same sentence as §16's, one layer down: the bound and the thing bounded have to
be the same quantity.

### 17.2 The rule, and two corrections the estimator needed

Build the island only where its estimated emitted size is within
`VM_ISL_SIZE_FACTOR` of the chain's for the same subtree. Both sides come from
the analysis, with per-node constants that are `limits.def` rows and measured
rather than chosen.

**Correction 1 — nodes alone was the wrong estimate.** The census's worst
pattern builds a **12-node** trie with **3,404 try sites** and emits 682 KB of
program; a nodes-only estimator saw twelve nodes and admitted it. A try site
and a node cost about the same bytes, and with EMPTY alternatives in the cross
product the try sites outnumber the nodes by two orders of magnitude. Fitted on
three such shapes plus the narrow and wide populations, `(nodes + try sites) ×
180` tracks the measured program within 10% across four orders of magnitude.

**Correction 2 — "not larger than the chain" was the wrong rule**, which is
what the finding literally asked for. Measured program ratios, island over
chain, with the rule disabled:

| | ratio |
|---|---|
| `s-256` | 0.85 |
| `w-64` | 0.97 |
| `cat\|dog\|cow` | 1.10 |
| `abcdefghij\|abcdefghik\|abcdefghil` | 1.12 |
| `foo\|bar` | 1.23 |
| `thin\|think\|thinker\|thinking` | 1.45 |
| `((?:aa\|bb)×4\|zzz)` | 3.06 |
| `((?:aa\|bb)×6\|zzz)` | 8.78 |
| `((?:aa\|bb)×8\|zzz)` | 27.65 |
| the census's worst two | 31.67, 146.95 |

The island's program is LARGER than the chain's on every narrow shape — its
value there is SPEED (§12: 0.140-0.175 island/chain ns), not size — so "not
larger" would decline the entire population the Q4 knee had just been ruled to
keep. The two populations separate cleanly, so the rule is a FACTOR, chosen
inside the gap and validated rather than argued.

### 17.3 Acceptance: the critic's own random census

Both seeds, 100 patterns each, `--engine=vm`, artifact size island over chain:

| | before | after |
|---|---|---|
| seed 77 refused-only-with-island | **9 of 100** (at 4-8 factors) | **0** |
| seed 77 median / max | 1.77× / **30.04×** | 1.000 / **1.03×** |
| seed 88 refused / median / max | — / 1.235× / 7.84× | **0** / 1.000 / **1.02×** |
| above 1.05× | 73% (2-5 factors) | **0 of 200** |
| above 2× | 20 and 12 | **0** |

**Factor 3 was measured and refused.** It keeps one extra shape and takes the
census max from 1.03× to 1.18×. What factor 2 costs is stated at the rule
itself: the prefix LADDER `(?:abcd|abc|ab|a)z` declines, and its own hand-twin
cell measured **1.001** — a wash — so nothing measured is given up.

**Every measured winner survives**: `foo|bar`, `cat|dog|cow`,
`thin|think|thinker|thinking`, `w-8`/`w-64`/`w-256`, `srt-256`, `s-256`, and
`p3` (the 99× cell).

### 17.4 The tests the corpus could not supply

`tests/island/run_island_tests.sh` gains a constructed cross-product ladder,
because no corpus pattern has the shape:

- **refusal identity** over k=4..14: no rung may be refused with the island and
  accepted under `-fno-alt-island`. That is the regression as an assertion.
- **the top-level decline, by an EXACT count**: if the top-level alternation
  takes the island it subsumes the subtree and the artifact stamps 1; if it
  declines, each of the k inner factors becomes its own island and it stamps k.
  Anything else is neither.
- **non-vacuity**: a 1,024-word cross product, comfortably INSIDE
  `VM_ISL_MAX_WORDS`, must still decline — so the cell shows the SIZE rule and
  not the word budget doing the work.

**Three witnesses moved**, because the size rule declines deep prefix ladders,
and each was replaced with a verified one rather than left to fail: the
frame-capacity witness, the two-island count cell, and three `ISLAND_PATTERNS`
entries. The §9 pool's second island member went the same way — and the pool's
own island-coverage floor is what caught it, which is that floor working.

### 17.5 F4 and F5

**F4 — the census's "lower bound" was wrong in one direction.** `altcls-merge`
folds single-byte branches into a CLASS and `vm_isl_single` then declines the
whole subtree: `ab|cd|a|b` stamps 0 islands by default and 1 under
`-fno-altcls-merge`. So §3's 429 brackets nothing on its own; it is what the
pattern TEXT admits, not what the emitter takes. `scripts/alt_census.py`'s
header says so now. Teaching the island to expand a single-byte class into its
member words is a STEP 2 shape, filed with the tail form.

**F5 — a documented budget-bound class, no code change.** Under a binding step
budget the island ANSWERS where the chain reads `err:steps`, because the trie
walk charges the WORK counter while the chain spends a STEP per branch resume.
Measured at the shipped budget with no flags on three of 4,263 fuzz cells. The
direction is one-way and that is why it is safe: the island does strictly less
stepping, so it can only answer where the chain gives up, never the reverse —
and on those three cells the island's answer is libpcre2's.

**So this report's earlier "answer-identical over 22,407 corpus cells" is
qualified**: the sweep's budget-bound bucket reads 0 because no corpus cell
approaches the budget, and off-corpus fuzzing finds budget-bound divergence at
about 0.07% of cells, every one in the island's favour. The panel found NO
answer divergence in ~11,400 cells (island = chain = libpcre2 = python), and
the seven oracle-only disagreements were python-versus-PCRE2 with pcrec
agreeing with PCRE2.

### 17.6 What the three lenses have in common

The doc lens found stale prose. The checks lens found three checks that could
not fail. The semantics lens found a regression none of them covered. All three
reduce to the same defect in different clothes: **the instrument and the thing
measured shared a source, or the population lacked the shape.** §9 compared the
script's arithmetic to the script's own constant; the island script read stamps
one function writes; the identity bucket excused an artifact on its own stamp;
and the axis sweep looked for a refusal in a corpus with no pattern that could
produce one. The island's own size budget is the same error inside the
compiler: it bounded the word list and the cost was in the trie.

### 17.7 The identity gate after the size rule

The island population narrowed again, as the size rule intends, and the
biconditional holds unchanged on all four axes:

| axis | same | differing | island-moved | stamped-but-deny-is-a-noop | unstamped-but-deny-moves |
|---|---|---|---|---|---|
| default | 2209 | 0 | 34 | 0 | 0 |
| vm | 2198 | 0 | 50 | 0 | 0 |
| noprefilter | 2210 | 0 | 34 | 0 | 0 |
| nocaptures | 2225 | 0 | 23 | 0 | 0 |

Read against §16.3's post-Q4 counts (74 / 102 / 74 / 56) and §11.2's pre-Q4
ones (166 / 236 / 166 / 123), the island's corpus population has fallen by
about four fifths across the two rulings — the Q4 knee and the S1 size rule
each declining a shape the measurement said was not worth taking. What is left
is the population the timing actually measured a win on.

`checks passed: 16, checks failed: 0`.

### 17.8 S2 verified, and F10 confirmed

**S2** — `((?:aa|bb)×9|z×18)`, the gcc-cost witness, after the size rule:

| | before (the critic's) | after |
|---|---|---|
| emitted file | 481,490 B | **56,351 B** |
| gcc wall | 42.8 s | **0.15 s** |
| gcc peak RSS | 574 MB | **34.8 MB** |
| vs the chain | 53,804 B | 56,351 B (**1.048×**) |

Its top-level alternation declines and the nine inner 2-way factors each stay
an island, so the stamp reads 9 rather than 1 — the size rule acting per
subtree. **This sharpens [CC-DIFF] STEP 2's case rather than replacing it**:
the 42.8 s was frameless-plus-`always_inline` replicating an oversized trie six
times, and the size rule removed the oversized trie. The exchange-rate finding
in §12.2 stands on its own and still wants a size term in that gate.

**F10 confirmed** from the pool's own run: 9 members, both sides carrying ≥2
distinct shapes (4 below the bar, 3 above), 7 band-eligible, and **2 that
stamp an island**, read off the artifact.

### 17.9 The budget-bound class is asserted, not described

`tests/island/run_island_tests.sh` block 10 compiles the witness pattern both
ways under `--engine=vm`, runs four subjects through each, and asserts that
where the two arms differ the island ANSWERS and the chain returns
`PCREC_ERR_STEPS` (-2) — **and never the reverse**, which is the half that
would catch the island starting to spend steps the chain does not.

**It is not a `.rxt` cell, and the reason is worth recording.** The shapes that
exhaust the chain's step budget are backtracking bombs: python `re`, the corpus
oracle, needs **15-20 seconds on each of these subjects**, past
`verify_rxt.py`'s bound — measured, after a first attempt to add them as corpus
cells tripped exactly that. A corpus cell whose oracle cannot run is a cell
nobody checks. But this claim needs no external oracle: it is a statement about
the two ARMS of one axis, and both are in hand. The four witnesses are my own,
found by sweeping subjects rather than transcribed, and python agrees with the
island (nomatch) on every one of them.

## 18. The cap guard — and why a per-subtree rule could not close it

The manager accepted §17's factor rule and named one guard still missing: the
factor bounds the island RELATIVE to the chain, while acceptance is bounded by
an ABSOLUTE cap, so a chain around 300 KB with an island around 550 KB sits
inside a factor of 2 and is refused where the chain compiles.

**Adding that condition per subtree was not enough, and the witness search is
what said so.** With the per-subtree guard in place, a 1,360-word ladder was
still REFUSED under the island at 514,258 bytes where the chain compiles at
430,442. The top-level island declines on size, `src/opt/altcls.c`'s factoring
then leaves **fifteen** nested sub-alternations — each individually reasonable,
each passing its own size test — and their SUM crosses the cap. A per-subtree
rule cannot bound an artifact-wide quantity, which is the same sentence as
§17.1's about budgets and quantities, at a third level.

**So the rule has both halves.** The per-subtree guard, and an ARTIFACT-WIDE
budget accumulated once in the `vm_count_slots` PRE-PASS — which runs before
both `vm_cost` and emission, so `Vm.isl_over_cap` is a fact all three readers
of `vm_isl_build` see identically rather than a running total whose answer
would depend on which reader asked first. Over the budget an artifact takes NO
islands: coarse, deterministic, and it restores the one property that matters.

**The two sides take different thresholds, and the asymmetry is load-bearing.**
The ISLAND side is discounted (0.9 × cap). The CHAIN side compares against the
FULL cap, because its question is "would the chain be refused too" and a
discounted threshold answers yes too readily — which switches the guard OFF
exactly where it is needed. Measured: the N=340 rung estimates its chain at
471,811 and really emits 485,734, so a 0.9 threshold on that side called it
over-cap, declined to act, and let the artifact be refused.

### 18.1 A correction to my own comment

I had written that the estimate "errs low every time". It does on the
cross-product shapes it was fitted against — 7 to 10% under — and runs about
**48% OVER** on wide sets of short words (659,160 against a measured 445,269).
The comment says so now. The 0.9 is a margin against the LOW direction, where
being wrong costs the caller a pattern; where the estimate runs high the guard
fires early and costs only speed on a pattern that still compiles.

### 18.2 A truncating stack, found by the same search

`vm_isl_subtree_nodes` used a FIXED 256-entry stack and returned early past it.
The walk pushes the right child of every `A_CAT`/`A_ALT` it descends, so its
depth is the SPINE LENGTH — and `w-256` has 255 `A_ALT` nodes plus a 12-element
branch. **The chain estimate was being truncated on exactly the shapes the
island targets**, understating the chain, inflating the ratio and declining
islands that should be taken. It surfaced as a chain estimate collapsing from
93,982 to 25,186 as the literals grew past the bound — the shape of a silent
early return. Arena-allocated and doubling now, so the bound is the pattern's
own size.

### 18.3 The ladder, and its non-vacuity

`tests/island/run_island_tests.sh` gains a near-cap ladder (N=260/300/340)
asserting refusal identity AND that each rung's artifact is byte-identical to
the chain's, since over the budget every island is declined. Nothing in the
corpus sits near the cap and nothing small enough to embed would, so the
witnesses are generated.

The cell that keeps it honest is the last one: the top rung's CHAIN must emit
between 425,000 and 500,000 code bytes. It emits **485,734**. Without that,
three patterns that were never in danger would pass the ladder forever.

| rung | island | chain |
|---|---|---|
| N=260 | 375,157 | 375,157 |
| N=300 | 430,442 | 430,442 |
| N=340 | 485,728 | 485,728 |

All three identical, all three compiled, where before the guard N=300 and N=340
were refused.
