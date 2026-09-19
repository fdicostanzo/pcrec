# evtriage — TRIAGE of [EMIT-VERB]'s two closing-chain reds

Lane `evtriage`, branch `lane/evtriage` from `lane/emitverb` tip `d672757f`
(the brief named `d702de76`; the branch had advanced two commits — `cd587462`,
the check-conversion commit this triage is largely about, and `d672757f`, the
report). 2026-09-19, opus.

Scope: nothing under `src/`, `cli/`, `lib/` touched. One test script, one
report. The branch-point tree used for the A/B is a `git archive` extraction in
the session scratchpad, never a worktree, never committed.

---

## 0. VERDICT IN ONE LINE PER RED

| red | verdict | disposition |
|---|---|---|
| RED 1 — `run_specimen_identity.sh` 10 fails | **PRE-EXISTING, not this branch's, not a compiler defect** | both defects FIXED in `8d513b4d`; check now **13 passed / 0 failed**, rc 0 |
| RED 2 — `make test` rc=2 | **UNDETERMINED at hand-off** — no per-section evidence survived the chain | re-run launched as this lane's last act; log + completion line named in §3 |

Neither red moves the `[EMIT-VERB]` merge decision on the evidence this lane
has. RED 1 is proven not to be the branch's. RED 2 is owed.

---

## 1. RED 1 — the A/B is decisive, and it is a tie

### 1.1 The method

The brief asked whether the ten failures are pre-existing or introduced. The
A/B run is the branch point's **own script** and the branch point's **own
binary**, so nothing of this branch reaches it:

```
git archive 4af16eb7 | tar -x -C $S/bp4af
cd $S/bp4af && make -j4 CC=gcc-16
timeout 1800 bash tests/recursion/run_specimen_identity.sh
```

### 1.2 The result

**Byte-for-byte the same verdict.** Branch point `4af16eb7`:
`checks passed: 5 / checks failed: 10`, rc 1 — the same five PASSes, the same
ten FAILs, the same messages, the same `.nentries = 0` vs `.nentries = 4` diff
bodies, and the same `[strip] the named exclusions remove 22 of the
reference's 1372 lines` count as the chain's own run at `d672757f`.

Log: `<scratchpad>/ab_bp_specimen.log` (`BP_SPECIMEN_RC=1`).

A direct artifact probe confirms it one level down, at both revisions, with
both binaries:

| artifact | `.ngroups` | `.nnames` | `.nentries` | fill-loop line | `RX_NCAPS` |
|---|---|---|---|---|---|
| `orig` @ 4af16eb7 | 0 | 0 | **0** | 1 | 1 |
| `factored` @ 4af16eb7 | 4 | 4 | **4** | 2 | 5 |
| `orig` @ d672757f | 0 | 0 | **0** | 1 | 1 |
| `factored` @ d672757f | 4 | 4 | **4** | 2 | 5 |
| `orig` `--no-captures`, both revisions | 0 | 0 | 0 | **1** | 1 |
| `factored` `--no-captures`, both revisions | 4 | 4 | **4** | **1** | 1 |

The branch's only edit to this file was adding `-fcomments` to ONE compile
site (`cd587462`). That flag is byte-neutral for every field above — the rows
are identical at both revisions — so **the conversion is exonerated**, and so
is the comment gate, `sb_len_uncut`, the 65 muted regions and the encoding
seam's doc/code split. The hypotheses the brief listed are all refuted by the
same table: nothing in the `.nentries` population depends on the comment gate,
and the diff exclusions were neither widened nor narrowed by the conversion.

### 1.3 Why nobody had seen it

`make test-specimen` is an **on-demand** gate. It is not a member of
`TEST_SECTIONS` (`Makefile:215-224`); its own recipe sits at `Makefile:901`
under a comment declaring it "a claim about a MOMENT, re-answered on demand,
not a standing invariant `make test` should pay for on every commit". So the
red has been live since whenever each defect landed, with nothing running the
gate in between. This is the reason to read the two root causes as staleness
rather than as regression.

### 1.4 Root cause (A) — `.nentries` was missing from both exclusion lists

Six of the ten FAILs (3 `[identity]`, 3 `[nocaps]`) are the same two-line diff:

```
1348c1348
<     .nentries = 0,
---
>     .nentries = 4,
```

`.nentries` is emitted by `src/gen/emit_dfa.c:2347` as
`sb_printf(c, "    .nentries = %u,\n", cx->n_named_groups)` — it reads **the
same count `.nnames` reads**, which `src/gen/CLAUDE.md:2362` states outright
("`nentries` READS THE SAME COUNT `nnames` DOES, AND SHIPS ANYWAY"). `orig`
declares no named group and writes 0; the three factored spellings name four
and write 4. That is a legitimate GROUP-INVENTORY difference of exactly the
kind both strip lists already excuse — they exclude `.ngroups`, `.nnames` and
`.groups` by name, and `§1b`'s own prose calls the family "THE GROUP
INVENTORY".

The field landed at **abi 15** ([DD-13b.W1.2], 2026-09-01), after both lists
were written (the `--no-captures` section is the manager's 2026-08-24 ruling).
The lists name the family **member by member**, so they went stale the day the
family gained one.

Fix: `.nentries` named beside `.nnames` in both `strip_named` and
`strip_nocaps`, and in the two prose blocks that enumerate the inventory. The
`[strip]` bounded control moves 22 → 23 dropped lines, well inside its own
1..40 window, so it stays a real bound rather than being widened to fit.

### 1.5 Root cause (B) — the `[nocaps]` fill needle matched a SECOND emission site

The remaining four FAILs are
`[nocaps] '<sp>' still carries the permanently-unset fill under --no-captures`,
one per spelling. They were **false positives**. The needle was

```
grep -q '^        for (int rx_g = 1;'
```

and that line is emitted at **two** sites in `src/gen/emit_dfa.c`:

- **`emit_search_head`** (`:610`) — wave G's dead-group fill, the thing the
  assertion is about, gated on
  `cx->job->fit.chosen == ENGM_DFA && dfa_artifact_ncaps(cx) > 1`. Under
  `--no-captures` the artifact's NCAPS is 1, so this site is **correctly
  absent** — the check's own claim was true the whole time.
- **`emit_anchored_match_caps_def`** (`:6474`) — the anchored-match form's
  `<prefix>_match_caps`, which writes an identical loop line
  **unconditionally**. Its own header comment says so: "`RX_NCAPS` is 1 on
  almost every DFA artifact and the loop then emits nothing at run time."

Measured: the matched line in every `--no-captures` artifact, at both
revisions, sits inside `rx_match_caps` — site (b), never site (a).

Fix: the needle is re-aimed at `^    if (capture_spans)$`, the block header
unique to site (a). That is not a new claim about uniqueness — it is the very
line `strip_named` already anchors its range deletion on, so this file already
depends on it.

**And the fix carries the control an absence assertion needs** (learnings.md
§3: not "does this check run" but "what would have to be true for it to
fail"). An absence is green when the needle dies, so a new arm asserts the
same needle is LIVE on the default axis, against a population that is
asymmetric by construction: exactly **1** block in each of the three
capture-declaring spellings (`RX_NCAPS 5`) and exactly **0** in `orig`
(`RX_NCAPS 1`). It fails if the needle stops matching AND if the fill ever
starts appearing where no group is promised. It reuses §1's already-compiled
artifacts, so it costs no compile.

### 1.6 Post-fix measurement

`bash tests/recursion/run_specimen_identity.sh` in this lane's worktree:
**`checks passed: 13`, `checks failed: 0`, rc 0** —
`<scratchpad>/ev_specimen_fixed.log` (`FIXED_SPECIMEN_RC=0`). The count
reconciles exactly: the ten FAILs collapse into the seven `ok` lines their
loops produce when green (3 `[identity]` + 1 `[nocaps]` declaration + 3
`[nocaps]` diff), 12 in total, plus the one new needle-liveness control.

### 1.7 Disposition, and why no `known_issues.md` row

The brief's conditional for a finding-plus-`known_issues`-row was "a REAL
artifact difference between spellings under `--no-captures`". It is not one.
Class (A) is a real and correct inventory difference that a stale exclusion
list stopped excusing, and class (B) never was a difference at all — the
artifact property the check asserts has held continuously. Both are
test-side staleness, which this repo's triage lanes fix and report
(`bat4triage`, `btriage_20260917`, `mtriage` are the precedents), not product
defects. **Nothing is fixed silently**: the commit message and this section
carry the A/B evidence, and if the manager would rather carry a row and revert
`8d513b4d`, the evidence to write it is all here.

---

## 2. RED 2 — what the chain left, and what it did not

`MAKE_TEST_RC=2` with `sections ran: 40/40`. Nothing else survives:

- The chain piped `make test` through `tail -60`, so only the last section's
  output is in `final_validation.log`. The visible tail (`uprops` 26/0,
  `tests/core` 3/0 with all sub-checks green) is green, which is why the tail
  alone identifies nothing.
- `make test`'s own per-section evidence is a **marker directory only** —
  `tests/lib/test_trailer.sh` reads `<name>.ran` touch-files that mean "make
  launched this recipe", never pass or fail — and the recipe `rm -rf`s it. Two
  stale marker dirs do survive in `$TMPDIR` from the chain; they carry only
  `.ran` names and answer nothing.
- `worktrees/emitverb/build/watchdog.log` (24,948 lines, through 14:16:02)
  survives and is **entirely clean**: zero non-`ok` verdicts, zero non-zero
  exits. So no section died to a hang, a wall/RSS/CPU kill or a budget
  timeout — every failure was an assertion, which the watchdog does not see.

So the failing sections cannot be named from the artifacts, and the re-run is
the only instrument. One known red is already sufficient to explain `rc=2` on
its own: `run_inline_capability.sh`'s `nm could not read arm_a.o`
(docs/dev/wake.md's standing darwin list, "TEST_RC=2 on a green run"). That is
a floor, not an answer — it does not rule out a second, real red.

### The triage rubric for whoever reads the re-run

Reds that are **NOT** the branch's:

- `run_inline_capability.sh` — `nm could not read arm_a.o`, standing darwin.
- `tests/thread` SKIPs (gcc-16 has no arm64 TSan) and the one standing
  `sections skipped: 1` in the resource suite.
- `run_recursion_identity.sh`'s **(B) file pin** — red BY CONSTRUCTION on this
  branch until the manager re-pins at merge (D76 pins must name a commit
  reachable after the merge, which a lane branch's is not).
- `run_atomic_identity.sh` / `run_backref_identity.sh` /
  `run_lookaround_identity.sh` — permanently retired.

Anything else is the branch's to answer, and the D112 question to ask of each
is which of three it is: a real regression; a stale pin the branch moved and
did not re-pin (the abi 26 → 27 bump is the obvious generator — re-pin readers
are found BY GREP, D94); or a comment-reading check the `-fcomments`
conversion missed, in which case say per check whether the right repair is
reading the stamp or passing `-fcomments` because the comment IS the
instrument.

---

## 3. THE RE-RUN — OWED, launched as this lane's last act

```
cd /Users/fdicostanzo/pcrec/worktrees/evtriage
make -k -j4 PROCS=3 test CC=gcc-16
```

- **Log:** `<scratchpad>/ev_make_test.log`
- **Completion line to grep:** `sections ran:` (the trailer), followed by
  `EV_MAKE_TEST_RC=` on the last line.
- **Failures:** `grep -nE '^(FAIL|make.*\*\*\*)' <log>` and the per-section
  summary lines each suite prints.
- Bounded `timeout 10800` (wake.md measures darwin `make test` at ~104 min /
  40 sections; the box was idle at launch, the chain having ended at 14:16).

**One caveat for whoever commits after it.** `make test` regenerates
`docs/dev/artifact_size_log.tsv` (SIZELOG rides `test-corpus`'s own compile
pass), so the worktree will carry an uncommitted change to that tracked file
when the run ends. The chain already measured this branch at **0 movers over
3,480 common rows**, so it is expected to come back byte-identical; a
non-empty diff there is itself a finding.

---

## 4. Rulings received

None. No question was sent; nothing in this lane's work was blocked.

## 5. Commits

- `8d513b4d` — RED 1: both pre-existing staleness defects in
  `tests/recursion/run_specimen_identity.sh`, with the A/B evidence in the
  message.
- this report.
