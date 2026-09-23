# [OPT-PRECHECK-ADMIT] — ADMITTING THE WHOLE-WINDOW PRE-CHECKS BY COST

Lane `admitimpl`, branch `lane/admitimpl` from `ed9c9392`, 2026-09-23, opus.
Ratified by Frank the same morning as **G1 + G2 ONLY** (G3 PLACEMENT dropped —
refuted on x86_64, `cycle1_ledger_reading.md` §9 (C)). Sources: that reading's
§3-§6 and §9, and the plan row.

**Delivered:** one emit-time predicate with four readers, `abi` 30 → 31 for its
one new stamp, `tests/codegen/run_prechecks.sh` §5 (213 → 250 checks), sabotage
rows S269/S270, spec hunks in `tuning.md` and `match_api.md`, and every pin the
change moves. Never merged; parked on `lane/admitimpl`.

---

## §0 THREE FINDINGS

### F1. Folding the decline into `<PREFIX>_REQ_BYTE` makes the suite vacuous, and the brief's own example spelling is that fold

The brief proposes `RX_REQ_BYTE "none: admitted-out (pinned start)"`, and the
first build did essentially that — `REQ_BYTE`/`REQ_RUN` read `"none"` on a
declined artifact, since those stamps' own comments say the value "is the
decimal the emitted `memchr` carries". **Running the suite refuted it in one
step.** `tests/codegen/run_prechecks.sh` §3.7 is `[OPT-FREQPICK]`'s entire
assertion surface — eight witnesses, each expecting a hand-derived byte — and
three of its sibling §3.1 rows (`<[a-z]+>`, `(?:ab)*c`, `q`) plus one §3.6 row
(`(?i)é` under `-e utf8`) went red **because the artifact no longer says which
byte the analysis found**. Those four are all G1-declined, and G1's population
grows with the corpus.

The general form: *a stamp that reports "what was emitted" where the tree also
needs "what was derived" makes the derivation untestable on exactly the
population the new rule reaches — and a compiler that stopped deriving bytes
altogether would then read identical to one that derived them and declined.*

So the split shipped instead, which is the tree's own shape twice over
(`<PREFIX>_ENGINE`/`_ENGINE_WHY`, `<PREFIX>_VM_PREFILTER_LANG`/`_LANG_WHY`):
`REQ_BYTE` and `REQ_RUN` keep naming the ANALYSIS, byte for byte unchanged, and
a new `<PREFIX>_REQ_WHY` names the EMISSION with a closed four-token set. Four
of the six reds cleared by reverting the fold; the other two were the
biconditional arms themselves, which now read `REQ_WHY` and gained a
cross-check between the two stamps asserted on **every** row rather than only
the declining ones. No witness in §3 or §4 had to be rewritten, which was the
alternative and would have changed what each documented row tests.

### F2. G1's fire condition has collapsed to IDENTITY under `byte`, and `[OPT-FREQPICK]` is why

The rule as ratified is "decline unless the pre-check's byte `q` is STRICTLY
rarer than the prefilter's byte `p`". Since batch 2, `q` is the **argmin** of
the necessary set. And whenever a DFA start state has exactly one escaping byte
— which is what makes the prefilter the single-byte `memchr` form at all — that
byte is necessary, so `p` is a member of the set and `ppm(q) ≤ ppm(p)` always.
Combined with the rule's `ppm(p) ≤ ppm(q)` decline test, G1 can fire only where
the two are EQUAL, which in practice means `q == p`.

That is not a defect, it is the mechanism's shape: the ledger's own G1 witness
(`wild-codegrammar-json-array-begin`, `memchr(91)` twice) is exactly the
identity case, and the density comparison earns its place as the rule that
stays correct if the pick ever changes again. But it means **the non-identity
arm of G1 has an empty population under `byte` today**, and the only witness
that exercises the comparison as a comparison is one where it must NOT fire
(`x[0-9]+Q`: `Q` at 66 ppm against the prefilter's `x` at 997). §5.3 carries
that direction deliberately.

The encoding rule makes the same pair discriminate twice: under `-e utf8` the
pick reverts to the RIGHTMOST member, so `Q[0-9]+x` declines under `byte`
(pick `Q` = the prefilter's byte) and **emits** under `-e utf8` (pick `x` ≠ `Q`,
and identity is the whole rule there). One pattern, two encodings, opposite
answers — which is what makes the encoding gate more than a comment.

### F3. G1 is scoped to the ONE-BYTE form, and `router-prefix-order` is no longer the cell the ledger measured

`cycle1_ledger_reading.md` §3 ranks "the pre-check is strictly DOMINATED on
this artifact" as its first hypothesis for `router-prefix-order`
(`/user|/users`), on the ground that the pre-check's byte `r` is 1.85× commoner
than the prefilter's `/`. **At today's tip that cell is a different shape.**
Batch 2 moved the pick to `/` (47) AND gave the pattern a RUN, so the artifact
now runs `memchr(47)` + `memcmp("/user")` against a prefilter on the same byte
47. Compiled and read: `RX_REQ_BYTE "47"`, `RX_REQ_RUN` non-`"none"`,
`RX_DFA_PREFILTER "memchr"` on 47.

G1 is implemented for the **one-byte form only**, and the reason is the
dominance claim's own content rather than caution. The claim is "this pass
dismisses no window the existing pass would not dismiss sooner". That is true
of one `memchr` against another on a byte at least as rare. It is **false** of
tier 2b's run check, which dismisses a window holding the byte and not the run
— strictly more than the prefilter's pass does. So a run check is not dominated
by a `memchr` on its scan byte, the ledger measured only the one-byte shape,
and D77 says not to widen a rule past its measurement. Consequence, stated
plainly: **`router-prefix-order` keeps its pre-check under this change.** The
ledger disposed of its +1.19%/+1.21% as indistinguishable from a null band
measured at +8.46% and did not list it in the row's improve set, so the landing
bar is unaffected — but anyone reading §3 expecting G1 to remove it should read
this paragraph instead. The trigger for widening is a measured run-rate
analysis, which `reqpos_2b.md` §5 already names as tier 2b's own missing
instrument.

---

## §1 WHAT LANDED

One predicate, `req_admit` (`src/gen/emit_dfa.c`), declared beside
`dfa_search_is_pinned`'s forward declaration and defined next to the two
prefilter derivations it reads. **Four readers**, which is why it is a function
and not a clause: `pcrec_emit_req_byte_check` (whether to write the text),
`<PREFIX>_REQ_WHY` (what to say), and `pcrec_emit_prologue`'s
`#include <string.h>` decision (whether the body calls `memchr` at all — the
one reader that would have been wrong had it kept reading `Job.req_byte`).

**G2 ADMISSION — `req_route_one_attempt`.** Inherited, not re-invented.
`attempt_cand`'s own header already declines the candidate-start prefilter on a
fully-anchored machine ("`start_max` is the literal 0, so there is nothing
between attempts to skip"), which is why the ledger's one-attempt artifacts read
`RX_DFA_PREFILTER "none"`. The predicate asks each route the same question from
the field that route's own emitted bound is written from:
`dfa_interior_dead(cx->job->dfa.s1u)` on the DFA side and
`cx->job->start_anchor != PCREC_SANCH_NONE` on the VM's.

Two notes on that. First, **BOTH one-attempt rows of the three-valued
`start_max` are covered**, not just the literal `0` the ledger's rule text
names: `dfa_interior_dead(s1u)` is true for the `^`-anchored row (`start_max`
= 0) and for the `\G`-anchored row (`start_max` = `search_from`), and both run
at most one iteration. That is also what makes the DFA vocabulary match the
VM's `"anchored"`/`"gstart"` pair the same rule names, so the two routes decline
the same set of patterns rather than two overlapping sets. Second, **the DFA's
answer is deliberately the tighter one** — the subset construction has already
pruned unsatisfiable branches, so `dfa_interior_dead` can hold where
`Job.start_anchor` could not prove it; `emit_attempt` already asserts the other
direction at the one site holding both answers.

**G1 DOMINANCE — `dfa_cand_scan_byte` + `req_byte_dominated_by`.** The first
returns the byte the artifact's own candidate-start `memchr` scans, or −1,
reading axis B's **selection** (`dfa_pf_of`, compared by the chosen object's own
name) rather than `UnanchStart.kind` — because the deny mask and the offset-set
candidates sit between the two, so a `DFA_PF_MEMCHR` machine may still have had
an offset-set form selected over it. The VM HYBRID needs no clause of its own:
`pcrec_artifact_has_dfa_scan` is true for it and its inlined
`static <prefix>_prefilter` IS this emitter's output on the same machine. The
second compares densities: identity first (sound under every encoding), then
`pcrec_byte_freq_ppm(p) <= pcrec_byte_freq_ppm(q)` under `byte` only, which is
`src/opt/reqbyte.c`'s own encoding rule and for its reason
(`reqbyte_freq_pick.md` §3).

**The stamp.** `<PREFIX>_REQ_WHY`, unconditional on every artifact of both
engines, values `"emitted"` / `"none"` / `"one-attempt"` / `"dominated"`.
`"none"` holds iff `REQ_BYTE` is `"none"`, which is the pair's cross-check.
`"none"` rather than `"no-necessary-byte"` because `src/core/compile.c` skips
the analysis entirely under `-fno-req-byte`, so "found nothing" and "never ran"
are one state here and a token claiming the first would be a second undeclared
claim.

---

## §2 THE MOVERS CENSUS

Base `ed9c9392` (a compiler built by `git archive` of the branch point) against
the tip, every `pattern` line of every `.rxt` file in the tree, **both sides
writing to the SAME `-o` basename in their own directory** (the house's
recorded basename trap). The abi digit is normalised and the tip's new
`REQ_WHY` line stripped before comparison, so a "mover" is an artifact whose
PROGRAM text moved.

| axis | patterns | compiled by both | refused by both | refusal mismatch | movers | `one-attempt` | `dominated` |
|---|---|---|---|---|---|---|---|
| default | 3,171 | 1,163 | 2,008 | **0** | 330 | 21 | 309 |
| `--features all` | 3,171 | 2,814 | 357 | **0** | 1,100 | 294 | 806 |
| `--features all -e utf8` | 3,171 | 2,836 | 335 | **0** | 1,035 | 294 | 741 |

**Zero answer movers, and the census proves it structurally rather than by
assertion.** Every changed line of every mover was classified, and the
classification is exhaustive: **1,100 of 1,100 / 1,035 of 1,035 / 330 of 330
CLEAN**, where clean means the only removed lines are the pre-check's own text
(its comment, the one-byte `if`, or tier 2b's whole scan loop) plus
`#include <string.h>`, and **nothing is added at all**. No mover gains a line.
An artifact that only ever loses a conservative early `return 0` cannot answer
differently unless the removed check was wrong, in which case the BASE was the
miscompile.

The first run of this census read 112 "unexplained" removals and they were one
line my own classifier's pattern list missed (`rp_c = (size_t)…`, part of the
run scan loop) — recorded because the number a classifier reports is only as
good as its vocabulary, and the honest way to find that out is to print the
unexplained lines rather than the count.

**Refusal-set identity is the other half**: 0 refusal mismatches on all three
axes, in either direction. The change removes emitted bytes, so the only
plausible direction was a pattern newly fitting under a size cap, and none
does.

Two rows verified by DIFFING rather than by size (the manifest's own rule):
`a` loses its three-line `memchr` and KEEPS `<string.h>` (its own prefilter is
the caller); `^foo$` loses the whole run scan loop AND `<string.h>`, and
nothing else in either file moves but the two abi digits and the inserted
stamp.

---

## §3 THE `abi` ARGUMENT

**It IS an `abi` event, 30 → 31, and the ritual ran.** One new stamp line joins
every artifact of both engines — that is emitted scaffolding by D76's own
definition, and no argument that it is not was attempted. The alternative
(fold the decline into an existing value, no new line, no bump) was tried and
is refuted on its own merits in §0 F1, not on abi grounds.

Readers found BY GREP of the current number, and their dispositions:

| reader | disposition |
|---|---|
| `src/gen/emit_dfa.c:51` `PCREC_ARTIFACT_ABI` | 30 → 31 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` | 30 → 31, and the bump appended to the `[DD-14.FB]` narrative |
| `docs/spec/match_api.md` §6 (the ONE change log, [REVW.A1]) | new `31` entry; the old `30` entry re-headed "was"; **and its "gap-free from `2` to `29`" sentence corrected to `31`** — pre-existing drift, batch 2 bumped the log and not that sentence |
| `tests/codegen/run_recursion_identity.sh` `RECURSION_IDENTITY_FILEPIN` | **OWED to the manager at merge**, deliberately: D76's (B) pin must name a commit reachable AFTER the merge, which a lane branch's is not (opt5i/ccdiff1/optimpl2 precedent). Comparison (B) is therefore RED on this branch, by design. **It surfaces in neither `make test` nor `make test-codegen`**: `run_recursion_identity.sh` is `make test-recursion-identity`, an on-demand gate absent from `TEST_SECTIONS`, so the manager must run it deliberately after re-pinning |
| `tests/rxtsource/run_rxtsource_tests.sh:1457` `n30` | NOT a reader — a 30-word keyword census that collides with the digit |
| `src/gen/CLAUDE.md`, `docs/dev/decisions.md` | pointers only, by [REVW.A1]'s own cut; no digit to move |

And the **SECOND READER CLASS** the ritual's grep is structurally blind to
(`battriage_report.md`: a reader whose text cites no abi digit but whose VALUES
move with it) — found by running the suites, which is the D94 addendum's own
instruction:

| reader | disposition |
|---|---|
| `tests/resource/run_resource_tests.sh` `a{5,25000}` byte pin | 762338 → **762367**, +29 verified by diffing the two artifacts (two same-length abi digits, one inserted `#define RX_REQ_WHY "emitted"`). Eighth instance of this class, third from the abi digit |
| `tests/codegen/run_cpset_structure.sh` CHECK 3 manifest | all **twelve** `EMITTED_BYTES` rows re-recorded, read row by row: +29 on seven (`"emitted"`), +26 on three (`"none"`), −102 on `a` (G1, keeps `<string.h>`), −514 on `^foo$` (G2, loses it). Seventh manifest event, fourth from this class |

---

## §4 [MECH-REACH] — WITNESSES WHOSE EXPECTATION DEPENDED ON THE PRE-CHECK FIRING

The sweep is the suite run, not a grep: the change's whole effect is "the
pre-check is not there", and only a check that reads for it can notice.

**Six reds, all in `tests/codegen/run_prechecks.sh`, and all six were the
FOLD's fault rather than the admission's** — which is why the fix was the stamp
split (§0 F1) and not six witness rewrites:

| site | witness | why it went red |
|---|---|---|
| §3.1 | `<[a-z]+>` | G1 declines: `<` and `>` both read 332 ppm, so the pick ties the prefilter's byte |
| §3.1 | `(?:ab)*c` | G1 declines by identity — the DFA proves `c` is the ONLY byte escaping its start state, so the prefilter scans 99 too |
| §3.1 | `q` | G1 declines by identity on a single literal |
| §3.6 | `(?i)é` (`-e utf8`) | G1 declines by identity: the fold's two encodings share only lead byte 0xC3, which is also the prefilter's |
| §4.7 | `a(?i)bc`, `(?:ab)*c` | the same two declines reaching the run section's "declines the run and keeps the byte" arm |

Under the shipped split all six are green with their original witnesses and
original expected values: §3 and §4 assert the DERIVATION (unmoved), and the
new `REQ_WHY`-reading arms assert the EMISSION. **No `.rxt` corpus cell moved
anywhere**, which the census's zero-added-lines result predicts and
`test-registry`/`test-codegen`/`resource`/`cpset` confirm.

Two witnesses were checked for the opposite hazard and are fine:
`tests/harness/giveup.rxt`'s two patterns (axesfix's own [MECH-REACH] repair,
which works by making `REQ_BYTE` read `"none"`) are unaffected — a decline
cannot un-decline them.

---

## §5 VALIDATION

All logs in `build/` of the worktree `/Users/fdicostanzo/pcrec/worktrees/admitimpl`.

| run | log | verdict |
|---|---|---|
| `make -j4 CC=gcc-16` | — | clean |
| `make strict CC=gcc-16` | — | `strict: whole tree compiles clean with -Werror -Wshadow` |
| `tests/codegen/run_prechecks.sh` | `build/pc7.log` | **checks passed: 250 / checks failed: 0** (213/0 before §5) |
| `tests/resource/run_resource_tests.sh` | `build/res2.log` | **27/0**, 1 platform-expected darwin skip |
| `tests/codegen/run_cpset_structure.sh` | `build/cpset3.log` | **28/0** |
| `make test-registry CC=gcc-16` | `build/reg1.log` | **rc=0**, 649 PASS, 0 failed (PC-4 354 cells / 0 disagreements) |
| `tests/codegen/run_prechecks.sh` re-run after every edit | `build/pc7.log` | 250/0 |
| mech field validation (`VALIDATE_ONLY=1`) | `build/mechvalid.log` | **278 definitions valid**, 0 rows measured; S269/S270 FIELDS OK with their reach probes validated |
| movers census ×3 axes | `build/census_{dflt,feat,utf8}.log`, `build/census2_*.tsv` | §2's table; 0 refusal mismatches, 0 unexplained movers |
| REF-vs-TIP ANSWER differential | `build/adiff_feat.log`, `build/adiff_dflt.log` | see §5.1 |
| `make test-codegen CC=gcc-16` | `build/codegen1.log` | **9/10 scripts**, sole red the standing darwin `nm arm_a.o` probe |
| `make test-axes AXES="-fno-req-byte -fno-req-run"` | `build/axes1.log` | see §5.1 |
| `scripts/emit_sweep.py --ref ed9c9392` | `build/sweep1.log` | see §5.1 |
| S269 solo, S270 solo | `build/S269.log`, `build/S270.log` | see §5.1 |
| **full `make test CC=gcc-16`** | `build/admitimpl_test.log` | see §5.1 |

### §5.1 THE CHAINED RUNS — OWED, WITH THEIR LOG PATHS AND COMPLETION LINES

Per BOILERPLATE's DO-THEN-FINISH the heavy runs are the lane's LAST act,
chained DETACHED in one sequential script (`build/chain.sh`, `nohup … & disown`)
so the box runs one at a time. The chain writes `build/chain.done` when every
stage has finished and `build/chain_status.txt` with one line per stage.

Order and what to read:

1. **REF-vs-TIP answer differential** (`build/adiff_feat.log`,
   `build/adiff_dflt.log`) — for a stratified sample of the DECLINING
   population (every Nth row of each `why` class, cap 120 / 60), both
   compilers' `--emit-main` artifacts are built with `gcc-16 -O1` and run over
   26 subjects chosen so the declined byte is sometimes absent and sometimes
   present. Read the single JSON line: `"differing": 0` is the pass.
2. **`make test-codegen CC=gcc-16`** (`build/codegen1.log`) — the suite D94's
   addendum names. **RUN, and the verdict is in**: `run_group: 9/10 scripts
   passed`, `make: *** [test-codegen] Error 1`, and the sole red is the
   standing darwin `nm arm_a.o (no rx_search symbol)` probe in
   `run_inline_capability.sh` — the one this file's 29 sibling reports already
   carry. Log `build/codegen1.log`. `run_recursion_identity.sh` is NOT in this
   group (it is its own on-demand target), so the owed FILEPIN does not show
   here.
3. **`make test-axes AXES="-fno-req-byte -fno-req-run" CC=gcc-16`**
   (`build/axes1.log`) — restricted to this change's own two axes, per
   BOILERPLATE's darwin sizing note. Expect answer-identity on both.
4. **`scripts/emit_sweep.py --ref ed9c9392`** (`build/sweep1.log`) — the
   five-stream byte sweep against the branch point. It is NOT expected to read
   zero movers: the `.c` streams must move on every reached artifact (the new
   stamp line, and the pre-check's removal on the declining population), the
   `emit-ir` stream must read **0 movers** (the listing carries no `#define`
   and no search entry), and the `dumps` stream must read 0 (no registry
   surface moved — no axis bit was spent). That asymmetry is the real
   assertion: a mover in `emit-ir` or `dumps` is a finding.
5. **S269 solo, then S270 solo** (`build/S269.log`, `build/S270.log`) — each
   `bash tests/mech/run_sabotage_matrix.sh S26x`. Expect **DETECTED** on the
   `prechecks` arm and a GREEN `harness` arm, which is the rows' own point
   (§6).
6. **full `make test CC=gcc-16`** (`build/admitimpl_test.log`) — the last act.
   Read it by make's `*** [test-X] Error` lines, never by a `FAIL:` grep
   (learnings §3). Completion line: `sections ran: N/M`. The only expected red
   is `test-codegen`'s standing darwin `nm` probe; comparison (B) is NOT in
   `TEST_SECTIONS` and cannot appear here.

---

## §6 THE SABOTAGE ROWS

`S269_precheck_admission_removed.sh` (G2) and
`S270_precheck_dominance_removed.sh` (G1). Highest id on the tree before them
was 268; field validation reads 278 definitions valid.

**These are the first two rows in this directory whose plant cannot move an
answer in either direction**, which is a stronger statement than S263's or
S266's. Those plant a mechanism that could in principle have been wired to
delete matches, and the row records that the SOUND direction is the
undetectable one. Here the mechanism *is* a decision not to emit, so restoring
the emission is restoring a CORRECT compiler: the pre-check answers NOMATCH
only where the engine below it then answers NOMATCH anyway. Both rows therefore
declare their `harness` arm EXPECTED GREEN in their own `SAB_DESC` and
`SAB_DOC_FIGURE`, rather than leaving a green corpus arm to be misread as an
undetected regression.

**Both plants empty the PREDICATE, not the call site**, and the reason is that
deleting `req_admit`'s `if (req_route_one_attempt(cx))` line would leave the
function unreferenced and the build would WARN — a different failure from the
one under test. Emptying the predicate leaves every caller, every stamp and
every other rule where they are.

Each row's `SAB_REACH` probe asserts BOTH halves of the site (the stamp value
AND the absence of the emitted `memchr`), so a later change that keeps the
stamp and moves the emission reads UNREACHED rather than green.

---

## §7 SPEC DELTA (D80)

- **`docs/spec/tuning.md` §2.29 (new)** — the admission as its own subsection,
  explicitly NOT an axis (no flag, no bit), with both rules, their measured
  populations, the encoding rule, the one-byte scoping and its reason, the
  four-token stamp table, and the `<string.h>` consequence. §2.27 and §2.28
  each gain one paragraph saying their stamp names the ANALYSIS and pointing at
  §2.29.
- **`docs/spec/match_api.md` §6** — the new `abi` 31 entry at the head of the
  one change log, the `30` entry re-headed, the log's own range sentence
  corrected.
- **`docs/spec/match_api.md` §6.3** — `<PREFIX>_REQ_WHY`'s full entry, and two
  corrections to that section found in passing and flagged here rather than
  left: **(a)** `<PREFIX>_REQ_BYTE`'s paragraph still said the value "is the
  RIGHTMOST member of the necessary set — the same choice PCRE2's
  `PCRE2_INFO_LASTCODEUNIT` makes", which batch 2's `[OPT-FREQPICK]` falsified
  a day earlier (`tuning.md` §2.27 is correct; this copy was not); **(b)**
  `<PREFIX>_REQ_RUN` had **no §6.3 entry at all** — batch 2 added the stamp and
  documented it in `tuning.md` §2.28 and in the abi log, and never gave it the
  macro-contract entry its two siblings have. Both fixed here. Neither is this
  lane's mechanism, and a reviewer may prefer them split out.

---

## §8 CLAUDE.md UPDATES

`tests/codegen/CLAUDE.md` (§5's charter, the analysis-vs-emission split and
what the folded alternative would have cost), `tests/mech/CLAUDE.md` (the
two-row table and the answer-invisibility argument), `src/gen/CLAUDE.md` (a new
section: the one derivation, its four readers, why G2 inherits rather than
restates, why G1 reads axis B's selection, and the cheap witnesses per arm),
`src/opt/CLAUDE.md` (a new closing section: whether a pre-check is emitted is
not that directory's question).

---

## §9 FOR A FRESH AGENT RESUMING THIS LANE

Everything except §5.1's chained runs is committed and green. If the chain's
logs show a red, the three things to check first, in order: (1) is it the
standing darwin `nm arm_a.o` probe or comparison (B)'s un-re-pinned FILEPIN,
both expected; (2) does a [MECH-REACH] witness somewhere outside
`tests/codegen/run_prechecks.sh` read for a `memchr` that a decline removed —
the fix is at ITS build site and §4's table is the shape to follow; (3) is it a
pin whose VALUE moves with the stamp line but whose text cites no abi digit
(§3's second reader class, which has now fired at four sites in this tree).

The one open design question, with its trigger named: **should G1 cover tier
2b's RUN check?** §0 F3 says no on the dominance argument's own content and on
D77, and names the measurement that would change the answer (a run-rate
analysis, `reqpos_2b.md` §5's own missing instrument). The population it would
move is measurable today from `build/census2_feat.tsv` plus a `REQ_RUN` read.
