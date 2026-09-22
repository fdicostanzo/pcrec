# [OPTLOOP.1.impl] BATCH 1 — three whole-window pre-checks (lane `optimpl1`)

Branch `lane/optimpl1` from `main` `ff63ebf3`. D119 batch 1 as Frank
confirmed it on 2026-09-22: **[OPT-ANCHOR-VM] + [OPT-ENDWIN] + [OPT-REQBYTE]**
(FIRSTSET out, ENDWIN in). Four commit groups, each with an independent
revert:

| commit | what |
|---|---|
| `be7e8ef3` | [OPT-ANCHOR-VM] — `src/opt/startanch.c`, the VM's attempt-loop start bound |
| `fa1abf3b` | [OPT-ENDWIN] — `src/opt/endwin.c`, the end-anchor start window |
| `3aa13b6b` | [OPT-REQBYTE] — `src/opt/reqbyte.c`, the necessary-byte pre-check |
| `b7f46d6b` | the `abi` 28 → 29 bump and the whole D94 ritual, once, for all three |

---

## 0. The three findings worth reading before anything else

**0.1 A carve-out cell in `[OPT-REQBYTE]`'s own plan row is FALSIFIED, and
the mechanism is what falsified it.** The row names `router-prefix-order`
(`/user|/users`) as a do-not-regress cell on the ground that it "records no
required unit at all and whose emitted text must therefore be byte-identical".
It is not byte-identical: pcrec stamps `RX_REQ_BYTE "114"` (`'r'`) and emits
the pre-check. Both halves of the claim are wrong in the same direction and
for one reason — **the row's premise is PCRE2's derivation, not this one**.
PCRE2 records no required unit for an alternation; this analysis INTERSECTS
the branches' necessary sets, which is strictly stronger there, and it
additionally does not impose PCRE2's "other than at its start" restriction
(§1.3 below says why that restriction is unnecessary for a whole-window
consumer). Every match of `/user|/users` does contain `'r'`, so the check is
sound; what moved is the cell's own prediction. Two consequences the bench
needs: that cell is no longer a byte-identity control, and its throughput
number should be read as a TARGET rather than a floor.

**0.2 `cycle1_analysis.md`'s own M4 hand-twin over-counts the window by one,
and the landed mechanism is tighter.** The M4.b block inserts
`search_from = subject_length - 5` with the comment *"maxw(abc$) = 4, +1 for
`$\n`"*. `abc$` has a maximum width of **3**, so the window is 4 and the
landed artifact stamps `RX_END_WINDOW "4"`. The twin's 5 is sound (a wider
window only scans more) but it is not what the mechanism computes, so a
reader comparing the twin's emitted text against the landed artifact will
find a one-byte difference that is the twin's, not the compiler's. The
profile's timing conclusion is unaffected — both collapse to O(1).

**0.3 Two of the three mechanisms have NO answer-level detector anywhere in
this tree, and that is a property of what they do rather than a gap.**
[OPT-ANCHOR-VM]'s bound and [OPT-REQBYTE]'s pre-check (in its sound sense)
remove only work an artifact would have done and thrown away, so no
differential, no oracle and no corpus cell can see a plant that deletes
either. `tests/codegen/run_prechecks.sh` is where they are defended, and
S263's measured `corpus:0fail/28960pass` beside `prechecks:4fail/19pass` is
that asymmetry stated as a number. [OPT-ENDWIN] is the exception: it MOVES a
search's start position, so an error there loses matches — S264 measures
`corpus:178fail/28848pass`. The three rows together are a small experiment in
which kinds of optimization a corpus can police and which kinds it cannot.

---

## 1. The three mechanisms, and where each fact lives

All three are AST-level analyses over the **lowered** tree, derived once per
attempt in `src/core/compile.c` (after `pcrec_lower_enc`, before either
emitter) into `Job`, because `pcrec_emit_dfa` is handed a machine and not a
tree. Each applies its own denial AT THE ANALYSIS, so a denied build is
indistinguishable from a pattern with nothing to find — possessify's
no-trace rule, and what makes `make test-axes`' sweep of the three new bits a
control rather than a comparison of two new shapes.

### 1.1 [OPT-ANCHOR-VM] — `src/opt/startanch.c`, axis bit 28

`pcrec_start_anchor` returns `PCREC_SANCH_BOT` / `_GSTART` / `_NONE`. The VM
emits `const size_t attempt_max = search_from;` and reads it in the attempt
loop's existing continue test; an `unanchored` artifact keeps today's text
byte for byte.

**The DFA's `dfa_interior_dead` pair becomes a CONFIRMATION, and the
implication runs in ONE DIRECTION.** `PCREC_SANCH_BOT` must imply the
machine's `anchored`; the converse is FALSE and is not asserted, because the
subset construction has already pruned branches the tree still carries (an
unsatisfiable alternative, a class the lowering emptied). The sound direction
is asserted inside `emit_attempt`, at the one site holding both answers, by
`pcrec_ctx_fail` — and **verified silent over the whole shipped corpus at
three engine settings** (3,252 distinct patterns × default / `--engine=dfa` /
`--engine=vm`, 0 internal errors) before it was committed, because an
internal error that can fire on a user pattern is a refusal regression.

**One emitted bound serves both non-`unanchored` values**, because both mean
"at most one start position can match" and the loop has already tried it. The
STAMP is what distinguishes `anchored` from `gstart`, so no fact is lost.

### 1.2 [OPT-ENDWIN] — `src/opt/endwin.c`, axis bit 29

`pcrec_end_window` returns the byte window `W = maxw + eps`, or `-1`. One
emitter (`pcrec_emit_end_window_clamp`) writes the clamp for both engines'
search entries, so the two routes cannot take the bound in two shapes.

**Four structural declines, each with its own reason rather than a shared
"be careful".** An unbounded `pcrec_cwmax` (the common case, free); a
multi-byte encoding; a `\G` anywhere in the pattern; a multiline `$`.

The encoding decline is the one worth reading. The clamp computes a BYTE
offset and hands it to the machine as a start position; under `utf8` that
offset can land inside a character, which is K49/K50's territory — a leading
negative assertion succeeds exactly where its body has no path, so a
mid-character start is a WRONG ANSWER and not merely a wasted attempt. The
test is `PcrecEnc.start_cls != NULL`, the same field `<PREFIX>_STARTPOS_GUARD`
reads, **and it discharges two obligations at once**: an encoding with no
non-boundary positions is exactly one whose every character is one byte,
which is also what makes `pcrec_cwmax`'s CHARACTER count a BYTE count here.
Had the decline been spelled as an encoding-NAME comparison, the second
obligation would have been undischarged and invisible.

The `\G` decline is the other one an implementer walks into: `\G` is the one
assertion whose truth is a function of the `search_from` this clamp MOVES,
and both emitters compare a position against that parameter by name. This is
also why [OPT-ANCHOR-VM] and [OPT-ENDWIN] do not interact — they decline
disjointly on exactly that construct.

### 1.3 [OPT-REQBYTE] — `src/opt/reqbyte.c`, axis bit 30

A bottom-up walk producing a SET (concat unions, alternation INTERSECTS, a
min-0 quantifier contributes nothing, a one-byte class is a singleton,
`A_BREF`/`A_CALL`/every assertion is empty), and the emitter takes the
RIGHTMOST member — PCRE2's own `LASTCODEUNIT` choice, so a later multi-byte
form is a WIDENING of this mechanism rather than a different one.

**Two deliberate departures from PCRE2's fact, both stated in the file:**

- **The whole window counts.** PCRE2 excludes the match's first unit because
  its consumer is a per-attempt check. This consumer runs once per call over
  `[search_from, subject_length)`, where every byte of every match lies
  whatever its position in the match, so the restriction buys nothing and
  costs patterns. §0.1 is what that is worth in practice.
- **A lookaround's body is NOT descended into**, and this one is a
  CORRECTNESS decline rather than a missed opportunity: a lookbehind's bytes
  sit BEFORE the match's start and can be outside that window entirely.

**The independent confirmation of the derivation is PCRE2's own table.** The
five M1 target patterns stamp `'>'`, `'='`, `'>'`, `'='`, `'\'` — byte for
byte the `PCRE2_INFO_LASTCODEUNIT` column `cycle1_analysis.md` §2.3(c)
measured against libpcre2, derived here by a walk that has never seen it.

---

## 2. Validation — COMPLETE except where marked OWED

### 2.1 Answer identity, the mechanisms' central claim

Each mechanism was swept against its OWN deny flag, comparing
`rx_search` at EVERY startpos over every subject, on all three engine
settings (`auto` / `--engine=vm` / `--engine=dfa`):

| mechanism | patterns × engines × subjects | mismatches |
|---|---|---|
| [OPT-ENDWIN] (`-fno-end-window`) | 16 × 3 × 9 | **0** |
| [OPT-REQBYTE] (`-fno-req-byte`) | 20 × 3 × 12 | **0** |
| [OPT-ANCHOR-VM] (`-fno-vm-anchor-bound`) | 8 × 3 × 7 | **0** |

The [OPT-ENDWIN] set carries the four `cycle1_analysis.md` M4.c carve-out
subjects plus `\z`/`\Z`/`(?m)`/`\K`/unbounded-width shapes; the [OPT-REQBYTE]
set carries the backreference, lookahead, lookbehind, caseless and
empty-pattern arms.

### 2.2 The corpus

| check | result |
|---|---|
| every corpus pattern compiled, default / `--engine=dfa` / `--engine=vm` | **0 internal errors** (3,252 patterns × 3) |
| a 600-pattern random sample compiled with the harness's own `-O1 -Wall -Wextra -Werror` | **0 failures** |
| `tests/assertions/end_window.rxt` under `tests/harness/run.sh` | **66 / 0** |
| `tests/assertions/end_window.rxt` against python3 `re` (independent reader, documented `\z`≡python `\Z` mapping) | **66 cases, 0 disagreements** |

### 2.3 Suites

| suite | result |
|---|---|
| `make strict` | clean, after every commit |
| `make test-prechecks` (new) | **113 / 0** |
| `make test-codegen` | 9 of 10 scripts — the sole red is the standing darwin `nm arm_a.o` probe (documented in 29 other lane reports) |
| `tests/codegen/run_cpset_structure.sh` | **28 / 0** after re-recording the manifest |
| `tests/registry/limits_check.sh` | **27 / 0** |
| `tests/registry/axes_registry_check.sh` | **120 / 0** (was 108; the pin moved with it) |
| `tests/rxtsource/run_rxtsource_tests.sh` | **212 / 0**, 1 RECORD (this box's documented darwin C3 population note) |
| `tests/resource/run_resource_tests.sh` | **27 / 0** after re-pinning 762125 → 762312 |
| `tests/assertions/run_assertions_tests.sh` | **54 / 0** |
| `scripts/m6read_check_sab_anchors.py` | 273 sabotages / 289 anchor sites, **all resolve** |

### 2.4 Sabotage rows, each run SOLO

| row | verdict | arms |
|---|---|---|
| S263 (the bound emitted as `subject_length`) | **DETECTED** | `reach:ok(1/1)`, `prechecks:4fail/19pass`, `corpus:0fail/28960pass` |
| S264 (the window one byte too FEW) | **DETECTED** | `reach:ok(1/1)`, `corpus:178fail/28848pass`, `prechecks:11fail/50pass` |
| S265 (the `memchr` sense inverted) | OWED — see §4 |

Each was measured at its own mechanism's landing commit, where
`run_prechecks.sh` carried only the sections that existed then; each row's
`SAB_DOC_FIGURE` records the tree and says so, because the `prechecks`
denominator grows with the batch while the row's own red count does not.

---

## 3. The landing bar, confirmed by STAMPS rather than by timing

Nothing was timed on this Mac. Every bench pattern in
`/Users/fdicostanzo/pcrec-bench/bench/capability/patterns/` (read-only) was
compiled with this build and its stamps read.

**Targets — every one stamps its mechanism ON:**

| cell | mechanism | stamp |
|---|---|---|
| `tag-depth3-bound` | M1 | `RX_REQ_BYTE "62"` (`'>'`) + the `memchr` |
| `dup-param-detect` | M1 | `"61"` (`'='`) + the `memchr` |
| `tag-pair-match` | M1 | `"62"` (`'>'`) + the `memchr` |
| `wild-secrets-username-password-pair` | M1 | `"61"` (`'='`) + the `memchr` |
| `wild-logparse-winpath-grok` | M1 | `"92"` (`'\'`) + the `memchr` |
| `bracket-array-define` | M2 | `RX_VM_START "anchored"` |
| `evil-alt-nested` | M2 | `"anchored"` |
| `trim-nested-star` | M2 | `"anchored"` |
| `wild-semdiv-dollar-trailing-newline-pcre2` | M4 | `RX_END_WINDOW "4"` |

The M1 hand-twin's `memchr` line appears in general form in all five target
artifacts, as
`!memchr(subject + search_from, <byte>, subject_length - search_from)`.

**Floors — every one reads as expected, with two moves to report:**

| cell | expected | read |
|---|---|---|
| `floor-byte` | no start bound, no window | `VM_START` absent (DFA), `END_WINDOW "none"` ✓; gains `REQ_BYTE "126"` and its `memchr` — the M1 carve-out the profile measured at **+0.52%**, against a 2% bar |
| `nested-comment-rec` | unanchored | `VM_START "unanchored"`, `END_WINDOW "none"` ✓ (gains `REQ_BYTE "47"`, the M1 carve-out again) |
| `codegrammar-flat` | unanchored, byte-identical | `VM_START "unanchored"` ✓ (gains `REQ_BYTE "58"`) |
| `high-byte-run` | narrow prefilter untouched | `REQ_BYTE "none"`, `END_WINDOW "none"` — byte-identical but for the stamps ✓ |
| `wild-logparse-quotedstring-grok` | untouched | all three declined ✓ |
| `wild-validator-email-owasp` | no window | `END_WINDOW "none"` ✓ |
| `router-prefix-order` | **byte-identical** | **NOT** — `REQ_BYTE "114"`. §0.1 |
| `uuid-near-miss`, `ipv4-near-miss` | "a second bound must be free" | both GAIN a window (`"37"`, `"16"`) on top of `start_max = 0`. Sound — a `^…$` pattern of finite width cannot match a longer subject — and it is two instructions on a path already O(1), but it is a MOVE and the bench should read it as one |

`--list-limits` is untouched (no new limit).

### Size

Measured per artifact by diffing two builds written to the SAME `-o`
basename (this house's recorded basename trap, fifth instance at lane
`evtriage3`), never by subtracting sizes:

| artifact shape | delta | composition |
|---|---|---|
| declines everything (e.g. `(?i)HeLLo`) | **+56 B** | the two shared-prologue stamp lines, exactly |
| declines everything, VM | **+89 B** | + `RX_VM_START "unanchored"` (33 B) |
| one required byte, DFA (`a`, `abc`) | **+187 B** | stamps 55 B + the three-line `memchr` 132 B |
| required byte + end window (`^foo$`) | **+321 B** | + the two-line clamp and a `#include <string.h>` |
| VM with a required byte (`(?<=foo)bar`) | **+222 B** | |

All twelve `EMITTED_BYTES` rows of
`tests/codegen/manifests/m5_stage1_stamps.tsv` moved, every delta in that
range and accounted for line by line; the manifest was re-recorded
deliberately. The size tripwire's own ceilings (1.4 MB, 8.0 CPU-s) are three
orders of magnitude away and did not move.

---

## 4. OWED at hand-off

**The box was never free during this lane's working period.** The MAIN
TREE's own `make test` (pid 24849, launched 10:25, `timeout 9000`) was still
running at hand-off, so no suite-scale command was run here — the brief's own
rule. Instead the three owed runs are ARMED AND CHAINED:
`build/optimpl1_final.sh`, running as **pid 25279**, polls for pid 24849 to
exit and then runs them in series, each to its own log, one heavy suite at a
time. Progress line by line in `build/optimpl1_chain.log`; the last line it
writes is `[chain] ALL OWED RUNS COMPLETE`. Kill the whole chain with
`scripts/safekill 25279` if the manager wants the box for a merge battery
instead — nothing in it is required before review, only before merge.

One caveat on item 1's own side effect: a full `make test` REGENERATES
`docs/dev/artifact_size_log.tsv`. Per `tt4m_time.md` that regeneration is not
to be committed from a run taken on a warm, contended box; `git checkout` it
after reading the suite's verdict.

1. **`make test`** — full suite. Log: `build/optimpl1_test.log` in the
   worktree. Completion line: `sections ran: N/M`.
2. **`make test-axes`** — the answer-identity sweep, now over three more
   bits. Log: `build/optimpl1_axes.log`. Completion line: `run_axes.sh:` with
   its verdict.
3. **S265 run solo** — `bash tests/mech/run_sabotage_matrix.sh S265`. Log:
   `build/optimpl1_s265.log`. Completion line: `mech run COMPLETE:`. The row
   predicts DETECTED with a LARGE `corpus` fail count (unlike S263) and reds
   in `run_prechecks.sh` §3.1c.
4. **The identity gate (B) pin**, `RECURSION_IDENTITY_FILEPIN` in
   `tests/codegen/run_recursion_identity.sh`, is deliberately LEFT at
   `a70982c9` — D76's pin must name a commit REACHABLE AFTER THE MERGE, which
   a lane branch's is not (opt5i / ccdiff1 / [EMIT-VERB] precedent). That gate
   is therefore RED on this branch BY CONSTRUCTION, with the exact message
   *"the emitted scaffolding changed: bump `abi` … and re-pin comparison
   (B)"*. Comparison **(A)** is the one this lane owns and it is expected at
   zero movers: all three stamps are `#define` lines above `goto <p>_L0;`, and
   the emitted program text all three mechanisms add sits in the SEARCH ENTRY
   rather than in the VM program region.
5. **`python3 scripts/emit_sweep.py --ref c9305c24`** — the five-stream
   identity gate. It is NOT expected to read zero: streams 1–4 move on every
   artifact (the abi bump is the point) and stream 5 moves by the seven new
   `--list-axes` rows. What it is for here is the SHAPE of the movement, and
   §3's per-shape deltas are what a reader checks it against.
6. **The bench's own measurement** of the landing-bar cells, after merge, via
   the executor. Nothing in this report is a timing claim.
7. **`tests/codegen/run_recursion_identity.sh`** was launched here and had
   not finished at hand-off (it builds a reference compiler and compiles the
   corpus twice). It is NOT in `TEST_SECTIONS`, so item 1 does not cover it;
   run it after the chain. Expected: comparison **(A)** at zero movers,
   comparison **(B)** RED with the re-pin message, per item 4.

---

## 5. Smaller findings

**5.1 `docs/spec/registry.md`'s axis transcript had gone stale a THIRD
time** — it read 24 values while `alt-island`, `cls-fold`, `comments` and
`startpos-guard` had all landed. Re-derived to 31 (87 rows) in the same
change, and the line's own "this has gone stale TWICE" sentence updated to
say what caught it this time. `tests/axes/run_axes.sh`'s header said "twelve
bit-flag axes" at twenty-four; that number is now stated as DERIVED rather
than restated.

**5.2 D107's numeric-constant scan caught three constants and both
dispositions were new kinds.** `EW_EOL_SLACK` is a SEMANTIC WIDTH OF THE
NEWLINE CONVENTION — nothing can be measured against it, and the only thing
that would move it is pcrec adopting a multi-byte newline convention
(DD-11), which is a semantics change. `SA_BOT`/`SA_GSTART` are BIT POSITIONS
IN A FILE-PRIVATE SET. Both are on the NON-LIMIT allowlist with those
reasons, as a fifth and a sixth kind; a `limits.def` row for the first would
have invited `--eol-slack=`, which is not a knob this tree can offer.

**5.3 The registry's axes-coverage pin moved 108 → 120 and no abi grep could
have found it** — it cites no axis, no macro and no abi digit. The D94
addendum's own shape, third recorded instance; the registry run is the suite
that COUNTS over the area touched, which is how it surfaced.

**5.4 `tests/assertions/end_window.rxt` carries every claim twice**, at a
subject length that leaves the clamp inert and at one that makes it fire. A
window one byte too narrow is SILENT on short subjects, and short subjects
are what a hand-written test reaches for. S264's `178fail/28848pass` is that
decision paying: the long rows lose their matches and the short ones do not.

**5.5 `run_prechecks.sh` asserts the `memchr`'s SENSE separately from its
ARGUMENT**, because S265 inverts the sense and leaves the byte alone. One
assertion covering both would have gone red naming the wrong half — the
`w23impl_report.md` generalisation (*a check's FAILURE MESSAGE is a second,
undeclared claim about the space of causes*) applied before the fact rather
than after it.

**5.6 Every section of `run_prechecks.sh` carries a POPULATION FLOOR** (K35):
an assertion of the form "every artifact that stamps X also contains Y" is
vacuously green when nothing stamps X, and each floor additionally asserts
that its own EXTRACTOR is healthy before reading the count — the repair
`w233_report.md` had to make to W23-S3 arm 4, applied at birth.

---

## Triage (lane b1triage)

The manager's hypothesis was VERIFIED before any fix: `-p pa`/`-p pb`/`-p rx`
builds of every red witness were reproduced and grepped for
`!memchr(subject + search_from, <byte>, ...)`. Every one of the 13 reds
(25 of the log's 26 non-standing `FAIL` lines) is [MECH-REACH] — [OPT-REQBYTE]
(src/opt/reqbyte.c) short-circuits to nomatch before the mechanism under test
ever runs, because each witness's subject deliberately omits the pattern's
one required byte. None was a genuine regression. `-fno-req-byte` denies the
axis at the exact call site(s) each check builds from; where a build is
reused by more than one assertion, the flag was added once and re-verified
against every consumer.

| red | cause | fix | re-run |
|---|---|---|---|
| `tests/cli` case15 (4 FAILs): step-budget/frame-capacity give-up | `(a*)*b`/`((a)|b)*c` witnesses over a 'b'/'c'-free subject; req-byte's memchr answers nomatch before the VM budget can exhaust | `-fno-req-byte` on both `pcrec_run` calls (`tests/cli/run_cli_tests.sh`) | 10/10 case15 assertions PASS |
| `tests/lib/run_gen_timeout_tests.sh` gen-run CPU/wall kill controls (2 FAILs) | `(a*)*b` over 200 'a's (no 'b') needs a real ~5s VM run for the kill controls to fire; req-byte answers instantly | `-fno-req-byte` on the slowrun build | 18/18 PASS (CPU kill 123/cpukill, wall kill 124) |
| `tests/vm/run_vm_tests.sh` §4/§4.5/§4.7 CONTRAST (3 FAILs) | same shape: `(a*)*b`/`(a*)b`/`((a)|b)*c` witnesses missing their required byte | `-fno-req-byte` on the `steps`/`frames`/`cliffvm` builds (the `hy` default-engine and `vmp` possessified-rescan rows are unaffected, verified) | 48/48 PASS |
| `tests/possessify/run_possessify_tests.sh` §3b boundary probe (1 FAIL) | `(x)(?:a|bc)+d` over an 'x'+'a'*n harness subject with no 'd'; both the denied and possessified arms answer via the pre-check at every probed length | `-fno-req-byte` on `ceil_off` (section 3, reused) and the section-3b `ceil_on` rebuild; verified it does not move the static `subject_ceiling` stamp either arm reports | 18/18 PASS; `run_possdiff.sh` re-run clean (155/0/0) |
| `tests/mrl/run_mrldiff.sh` answer-more exemption (1 FAIL) | `(a*)*b` / `(a{1,4})+b` excused population needs the denied arm to GIVE UP and the pruned arm to ANSWER on a 'b'-free subject; req-byte makes both answer via the pre-check, so they trivially agree instead of diverging | `-fno-req-byte` on the pruned (`pa`) and denied (`pb`) builds; referee (`pc`, a pure DFA, no give-up path) left untouched | excused_total back to the pinned 22 (8+14 by pattern), 22 refereed, 0 unrefereed |
| `tests/island/run_island_tests.sh` §2.20 budget witness (1 FAIL) | `(?:aabb|...)+?q` over four 'a'/'b'-only subjects with no 'q'; req-byte answers both the island and chain arms before either runs | `-fno-req-byte` on both the `on`/`off` arms | 4/4 witnesses diverge correctly; 39/39 island checks PASS |
| `tests/lookaround/run_expansion_diff.sh` §6.3 population (13 FAILs: §1's 10 counts + policy P1/P2/NONE's 3) | NOT [MECH-REACH] — a real corpus-population move. `[OPTLOOP.1.impl]` batch 1 added `tests/assertions/end_window.rxt` (13 qualifying blocks / 66 cells, confirmed via `wc -l`/`grep -c` against the file itself) between this check's pin and HEAD | re-derived and re-pinned every moved literal (`tot_blocks` 469→482, `tot_beh` 10136→10202, `qual_blocks` 264→277, `qual_beh` 8276→8342, `p1_patterns` 264→277, `p2_patterns` 362→377, `p1_identity` 56→58, `p2_identity` 84→86, `p1_lookaround` 200→211, `p2_lookaround` 249→261); Q1-Q6 disqualification counts confirmed UNCHANGED before re-pinning, not merely assumed | 11/11 PASS, 29,319 three-way cells / 931 patterns, 0 disagreements |

S265 (already DETECTED per the prior report, unaffected by this triage) is
untouched.

**A note on scope**: no [OPT-REQBYTE]/[OPT-ENDWIN]/[OPT-ANCHOR-VM] `src/`
code changed in this triage — every fix is test-side, denying an axis whose
mechanism is working exactly as batch 1 designed it (a whole class of
ReDoS witnesses answering in one `memchr` is the feature). Six files
touched, six commits, each independently re-verified green before the next.

**Validation, chained** (box confirmed free at hand-off — no main-tree
`make test` running): `build/b1triage_final.sh`, pid recorded in
`build/b1triage_chain.log`, runs `make test-axes` then `make test` in
series, each to its own log (`build/b1triage_axes.log`,
`build/b1triage_test.log`). Completion lines: `run_axes.sh:` with its
verdict for the axes run, `sections ran: N/M` for the full suite. BOTH ARE
OWED at hand-off — this is the lane's last act per BOILERPLATE's
DO-THEN-FINISH. Kill with `scripts/safekill <chain pid>` if the manager
needs the box first.

---

## Axes fix (lane axesfix)

**Cause, established from `make test-axes`'s own baseline output (not
guessed):** the baseline run (`bash tests/axes/run_axes.sh`, HARNESS_BATCH
unset, no `RXTFLAGS`) is `tests/harness/run.sh` with no args over the whole
`.rxt` corpus, no extra flags — the SAME mechanism `test-corpus` rides
(`tests/size/run_size_log.sh` wraps the identical no-args `run.sh` call).
Reproduced standalone with the checked-out build binary:
`env PCREC=build/pcrec CC=gcc-16 bash tests/harness/run.sh
tests/harness/giveup.rxt` failed 2/2, both `gu` cells, before this fix.
This is [MECH-REACH] again — same class the triage section above fixed six
times over — but a SEVENTH instance the triage's own six-file list never
reached, because `tests/harness/giveup.rxt` isn't a suite script with a
`build()` call to add `-fno-req-byte` to; it's swept generically by
`run.sh`'s tree-wide `.rxt` discovery (same path `test-corpus` and the
axes baseline both take). Confirmed via `pcrec --list-schema`: the `pcrec`
raw-flags line is `config`-scope only, never `block`-scope, so no `.rxt`
`pattern` block can deny a compiler axis at all; `RXTFLAGS` is the
format's one escape hatch for exactly this gap, but it's a run-wide env
var, not a per-file one — so the flag-based fix the other six suites used
does not exist for a bare corpus file.

**Fix, at the pattern rather than the flag**: `src/opt/reqbyte.c`'s own
"safe direction" arm declines outright on a class of more than one
member. Swapped the trailing literal for an equally-unsatisfied two-member
class (`(a*)*b` -> `(a*)*[bc]`, `((a)|b)*c` -> `((a)|b)*[cd]`), keeping the
identical catastrophic-backtracking shape, subjects and budgets. Verified
both patterns now stamp `RX_REQ_BYTE "none"` (`--pattern '(a*)*[bc]'
-fcomments` / `--pattern '((a)|b)*[cd]' -fcomments`), and the file now
passes 2/2 standalone. Zero `src/` changes. No directive, line, or block
count moved (still 2 `pattern` / 2 `gu` / 3 `budget` / 2 `engine` lines),
so no `tests/rxtsource/run_rxtsource_tests.sh` RUNSH_*/CENSUS_* pin and no
`verify_rxt.py` `gu`-census pin moved either — both count by directive
keyword, never by pattern text. `tests/harness/CLAUDE.md`'s two mentions
of this file updated to match. Commit `ae7259b3` on `lane/optimpl1`.

**A side finding, not this task's fix but worth the manager's attention:**
the "make test is GREEN (42/42)" reading in this report's own §4 OWED
section and in the triage section above is a MISREADING of the trailer.
`sections ran: N/M` (the Makefile's `test:` recipe, `tests/lib/
test_trailer.sh`) counts sections `make -k` LAUNCHED, per the recipe's own
comment block — never sections that PASSED. `build/b1triage_test.log`
itself shows `make: *** [test-corpus] Error 1` (this exact giveup.rxt
failure), `make: *** [test-registry] Error 1`, and `make: *** [test-codegen]
Error 1` (the latter is the documented standing darwin `nm arm_a.o` probe,
correctly accounted for) — plus `make: *** [test] Error 1` at the very
end. Re-ran `bash tests/registry/run_registry_tests.sh` standalone just
now: exit 0, clean, 0 failures visible in the log — so `test-registry`'s
Error 1 reads as a box-contention flake from running concurrently with
the main tree's own `make test` at the time (that report's own §4 already
flagged the box as contended throughout), not a second standing
regression. Recommend the manager re-run `make test-registry` once more
in isolation before trusting that verdict fully, since this lane only
re-ran it once.

**Validation status at hand-off:**
- Standalone `tests/harness/giveup.rxt`: **2/2 PASS** (was 2/2 FAIL) —
  confirmed directly, not OWED.
- `make test-corpus CC=gcc-16`: launched detached, but hit its OWN 900s
  timeout wrapper (this section measures 1,717s serial per docs/testing.md
  TT-14, longer than the 900s I wrapped it in) — killed before finishing,
  no verdict. `docs/dev/artifact_size_log.tsv`'s partial regeneration from
  that run was `git checkout`'d back, per this report's own §4 caveat
  (never commit a size-log regen from a run that didn't finish clean).
  Superseded by the next item, which runs the identical corpus pass as
  its own baseline.
- `make test-axes CC=gcc-16`: **OWED.** Launched detached
  (`nohup timeout 3600 make test-axes CC=gcc-16 > build/axesfix_axes.log
  2>&1 & disown`), PID 66860, started 17:25:41. Log: `build/axesfix_axes.log`
  in the worktree. Completion is `run_axes.sh:` with its verdict line
  (agree/budget-bound/refused-documented/lost/mismatches/gained per axis,
  including bits 28-30 [OPT-ANCHOR-VM]/[OPT-ENDWIN]/[OPT-REQBYTE]) followed
  by `tests/codegen/run_form_census.sh`'s own summary. Expect the BASELINE
  to now complete (source of the original FATAL) and every axis
  answer-identical to default, same bar the manager's brief set.
- Not re-run: the corpus-section identity gates this touched file rides
  (`make test-rxtsource`, to confirm the RUNSH_*/CENSUS_* reconciliation
  really did not move) — reasoned about from the awk census's own field
  rules (keyword-only, not pattern-text) rather than measured live. Worth
  a manager spot-check if there is any doubt.
- `docs/testing.md`'s "Answer-identity sweep" section carries one
  historical prose line (`-fprefilter`: "2 MISMATCH in
  tests/harness/giveup.rxt") from BEFORE [OPT-REQBYTE] existed, describing
  a different axis (`-fprefilter`'s forced hybrid prefilter, unrelated to
  `-fno-req-byte`) that should be unaffected by this fix in mechanism but
  was not independently re-confirmed at the digit — flagged rather than
  edited blind.

Kill the axes run with `scripts/safekill 66860` if the box is needed first;
nothing here is required before review, only before merge.
