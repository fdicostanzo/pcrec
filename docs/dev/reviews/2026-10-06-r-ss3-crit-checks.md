# D6 critic — START-SET stage 3 (the DFA hat), lens: CHECKS, CONTROLS AND PINS

Critic `crit-ss3-checks`, 2026-10-06, read-only. Subject: `lane/ssbuild3`
(`git diff main...lane/ssbuild3`, head `29873a3c`), its report
`docs/dev/lanes/ssbuild3_report.md`, `docs/design/startset.md` §6/§8, D148.
Probes ran only `worktrees/ssbuild3/build/pcrec` (no make, no gcc), scratch in
the session scratchpad. Paths below are relative to `worktrees/ssbuild3/`.

No BLOCKER. Six MAJORs. They share one root: the stage's checks are well
built, but several of them count or score a population other than the one
the claim needs, and nothing fails if that population shrinks.

---

## MAJOR

### M1. S481-S485 are guaranteed DETECTED by a text pin that reads the exact line each plant edits. Their verdicts certify nothing about the answer checks.

`tests/startset/dfahat_checks.py:82` (`RESEED`) matches only the exact text
`if (scan_position > skip_from) forward_state = rx_forward_seed_state[...]`.
`[dfa-iff]` (`:261-265`) and `[dfa-reseed]` (`:268-269`) fail whenever that
line count is not exactly 1. Every one of these plants rewrites that line:

| row | plant text |
|---|---|
| S481 | `if (0 && …)` |
| S482 | `if (!q && …)` |
| S483 | `if (scan_position + 1 < subject_length && …)` |
| S484 | `if (q && …)` |
| S485 | `if (scan_position > (skip_from & 0))` |

All five rows have `SAB_SUITES='dfahat'`, and that is one arm, scored by the
single trailer `run_dfahat_checks.sh:46-47`. So each row reads DETECTED even
if the fixtures, `[dfa-fix]` and the every-startpos differential go
completely blind.

- `run_dfa_stamps.sh`'s new derivation (`read_artifact`, the `hat = 1` line)
  keys on the same text, so it is not an independent detector either.
- The report's §5 "how it is seen" column was read by hand from the kept
  logs at landing. That is right for that day. But the row contract that
  future mech runs enforce does not encode it.
- This is learnings §3's "control shares a source with what it controls",
  applied to the sabotage tier itself.

**Fix.** Either split the arm into `dfahat-answers` (fixtures + diff) and
`dfahat-struct`, and point S481-S485 at the answer arm (the structural pins
can keep their own rows), or have each row require a named detector line in
the arm log.

### M2. S487, S489 and S490 are declared UNREACHED, but their REACH probes can never flip, and the "equivalent mutant" claim was never measured.

Each probe compiles on the CLEAN tree and greps for a DFA-hat value on a
pattern that only the conjunct under test refuses. On the clean tree that
conjunct is present, so the probe reads MISSING by construction, whatever the
other conjuncts do. The headers promise "it reads NOW REACHED the day an
unseeded machine admits" (`S487:8-10`, `S489:9-10`, `S490:12-13`). Today that
is false: the event needs the guarded conjunct already gone on the clean
tree.

What the rows actually argue is different: the admission conjunct alone
declines (`T ⊊ E` fails; `emit_dfa.c` `pf_dfa_start_set`). That makes these
EQUIVALENT mutants, not unreached sites. The plant line runs on every
`ENG_UNANCH` compile, and for S487/S489 on every seeded one.

UNREACHED rows are never planted (`run_sabotage_matrix.sh:1188-1196`
NOT-RUN), so the equivalence is argued and never observed. The lane measured
the analogous E* mutants with scratch builds (report §4.1: 3,528/3,528
identical) but did not do so for these three. That leaves three of F's five
conjuncts, including sound-F7's scan-kind belt, with no live sabotage
evidence.

I checked the arguments by reading the code:
- `E = cand_from_escapes(fs)`, so `E ⊆ E*`, and the S489 argument holds.
- S487 depends on C-SS*, which is checked on the corpus only.

**Fix.** Re-type the three rows as equivalence rows: plant them, expect
byte-identical artifacts across the corpus and the bench, and record the
argument. Or give each probe a clean-tree observable that does not pass
through its own conjunct. For example, for S489, read `|S| == 256` from
`--emit-facts` and `T ⊊ E` from the deny build, and echo REACH if the
admission alone would admit.

### M3. The axes sweep has no counted DFA-hat population. The "11,000 floor reads 4,635 on the subset" reasoning answers the wrong question.

`tests/axes/run_axes.sh:1819-1831`:
- The product arm is `--engine=vm × -fno-start-set`.
- Its floor counts cases of `manifest_s2_vm_forced.tsv` (the VM hat) via
  `startset_arm.py`.
- Under `--engine=vm` there is no DFA scan (report §3.4).

So the floor never measured the DFA hat, on the subset or on the whole
corpus. The DFA hat's only axes coverage is the plain `-fno-start-set`
bit-axis job, which has no mover count and no floor. The lane did not touch
`tests/axes/` (`git diff --stat` is empty there). The GROUP F5 comment
(`run_axes.sh:954-964`) and `tests/axes/CLAUDE.md:545-560` still describe
`-fno-start-set` as the VM hat only.

The spec's new claim "ANSWER-IDENTITY-preserving and give-up-preserving"
(`docs/spec/tuning.md` §2.42 stage-3 hunk) is measured only on the 18 mover
files. That matters most for the 7 hybrid re-seed-row movers, whose
`RX_VM_RESEED` changes `adaptive-dense` → `adaptive`. The full `make
test-axes` is OWED (report §7.2).

**Fix.** Add a DFA-hat mover count to the `-fno-start-set` job: baseline
cases whose block is in `manifest_s3_dfa.tsv`, floored at half of the
landing figure. Update F5's comment and the axes CLAUDE.md in the same
change.

### M4. sound-F5(d)'s population (count-collapsed hybrids) is 5 pairs, uncounted, and lost its independent oracle in the import.

**The population is much smaller than the pair count suggests.** Measured
with this build over `manifest_s3_dfa.tsv`'s 71 corpus rows:
- Under `-fprefilter-collapse` only **5** artifacts read `RX_VM_PREFILTER_LANG
  "count-collapsed"`; 15 hybrids stay `exact` and 51 are DFA.
- **66 of the 71 `collapse` pairs are byte-identical to the `auto` pair.**

So the report's "the differential's `collapse` config reaches every hybrid
mover collapsed" (§3.3) and "30 collapse pairs" for S481 are mostly
duplicates of `auto`. The floor (`vmhat_diff.py`, `FLOOR=105` of 219) counts
pairs, not distinct or collapsed ones. Neither the per-config counts nor the
"matches" total is floored.

**The independent oracle was dropped.** ssedge's `hybrid.rxt` draft carried
`-fprefilter-collapse` targets so that collapsed answers would be checked
against libpcre2. `edge_import.py:29-58` drops those heads (report finding
3). `[dfa-fix]` therefore runs `hybrid.rxt` uncollapsed. The only oracle left
at the collapsed config is the same compiler's deny arm. The single
collapsed stamp witness (`[dfa-wit]` `\B(a|b){1,3}`) checks a stamp, not
answers.

**Fix.** In `run_dfahat_checks.sh`, run the four fixture files a second time
through the harness with `RXTFLAGS=-fprefilter-collapse`, floored. Floor the
collapsed population (count `count-collapsed` pairs) in `vmhat_diff.py`.
Dedupe pairs whose artifact equals `auto`'s before counting them toward the
floor.

### M5. Under `HAT=dfa` the sweep alphabet drops the byte outside E and the pattern's own bytes on all 71 movers.

The docstring says the sweep alphabet "also carries up to two bytes of the
deny arm's E outside S" (`vmhat_diff.py:39-43`). What actually happens:
- `subjects()` (`vmhat_diff.py:112-117`) caps the alphabet at 5. In `HAT=dfa`
  it builds `S[:3] + ctx[:2]` first, so the ctx bytes DISPLACE the rest
  rather than adding to it.
- I simulated the rule over all 71 movers. 71/71 lose the stage-2 "outside"
  byte (the one stage 2 added "so a seek has something to skip"), and 71/71
  lose pattern bytes.

Examples:
- `\b[0-9a-f]{8}\b` gets alphabet `012AB`. It has no non-word byte, so the
  exhaustive sweep never builds a `\b` boundary inside a subject, and no
  sweep subject of at most 4 bytes can match.
- `\b(?:cat|dog)\B` gets `cd01\`. It has no `a`/`t`/`o`/`g`, so the sweep
  produces zero matches.

Matches then come only from the block's own subjects and the random pool. The
headline (1,155,139 cells, 235,108 matches) is dominated by short patterns.
No per-pair match count or floor exists. As a result, the re-seed's
`seed[class(b)]` for b outside E (a different class from ctx) is exercised
only by own subjects.

**Fix.** Add ctx to the alphabet rather than displacing with it: raise the
cap or reserve the outside byte. Report a per-pair `matches > 0` count and
floor it.

### M6. The mech was scored before later check changes, and the full mech was not run.

The rows were scored at `8c69a359` (report §5, finding 9). After that:
- `da0cb761` changed `[dfa-deny]`'s logic (`dfahat_checks.py` class
  re-compare) and `hybrid.rxt` (heads dropped, so the collapsed fixture
  cells the rows cite changed population).
- Finding 9 argues that the anchors still resolve. Anchors resolving says
  nothing about verdicts (learnings §3: "an EARLIER control must be re-run
  after a LATER change").

The stage moves 71 corpus artifacts, three cross-row stamp classes (G1 28,
re-seed row 7, scan edge 15), and one name family (`can_begin_match` →
`start_bytes` on movers). Only 15 rows were run, and §7 OWED does not list a
full mech. Learnings §3.ab is the precedent: five weeks of drift were caught
only by a full mech.

What I could check read-only: I ran every one of the 242 rows' `SAB_REACH`
probes against this build. All agree with their `SAB_EXPECT`: 229 DETECTED
and 5 UNDETECTED rows reach, and the 8 UNREACHED rows read MISSING. So the
reach side is not stale beyond S501/S502. The 63 `SAB_REACH_POP` rows were
not probed, and detection was not re-checked for any row: that needs the full
mech.

**Fix.** Add a full mech at the merged tree to OWED (Linux, per the box
rules). Re-score S480-S490/S504 at the shipping head.

---

## MINOR

- **m1. A hat-arm refusal paired with a deny-arm compile is not a failure in
  two of the three scripts.**
  - `dfahat_checks.py:one()` returns `refused` when the hat compile fails,
    including on a timeout (`compile_c` returns None at `TMO`). Such blocks
    vanish from `[dfa-iff]`/`[dfa-table]`/`[dfa-deny]`; only the `[dfa-reach]`
    half-floor and `[dfa-movers]` (for manifest rows) can notice.
  - `vmhat_diff.py:run()` counts either arm's refusal as `refused`, per
    config, unfloored.
  - Both of this stage's assertions (`views`, `T == S`) are refusals
    (`pcrec_ctx_fail`), so "hat refuses, deny compiles" is exactly how they
    fail. The corpus harness catches it in `make test`. The stage's own
    checks should count it as a FAIL.
- **m2. The class re-compare never checks that the re-compiled pair still
  carries the hat.** `dfahat_checks.py:175-181` replaces `deny_same` with the
  class-denied pair. If `CLASS_DENY` ever turns the selection away from the
  hat, the pair compares two non-hat builds and passes vacuously. Measured
  today: all 33 class movers stay hat movers under `CLASS_DENY` (28 memchr,
  5 class). Assert it.
- **m3. `[dfa-table]` claims more independence than it has.** The docstring
  says "two sources that are not the predicate" (`dfahat_checks.py:24-30`).
  `S` IS the predicate's input. With the compiler's own `T == S` assertion,
  `T == S` can only fail through a defect after the assertion (S486's
  shape). It is a real emission check, not an independent derivation.
  Reword it. Per-member reach is the start-byte oracle's, which is limited
  by M5's alphabet.
- **m4. `startset_lib.machine_sets` silently goes vacuous on movers.**
  Movers emit no `can_begin_match`, so `Ecbm is None` and `cbm_agrees` is
  vacuously True (`startset_lib.py`, `machine_sets`). The
  `startset_checks.py` `[ss-ctrl]` guard ("seeded-table-not-s0" → unread)
  stops guarding on the 71 movers. This is harmless today because X comes
  from the transition tables, but the population moved without its needle
  moving. That is the same shape as finding 2, in a reader the lane did not
  list.
- **m5. The census can only be regenerated with a frozen pre-stage-3
  binary.** Run on the current compiler, `census_s1.py:fhat` declines every
  DFA-hat mover as `row:first-*`, so the s3 manifest would empty itself.
  The s3 CLAUDE.md therefore requires "a pre-stage-3 build". As main moves
  (R4a′, later opts), the frozen binary diverges from the compiler under
  test and the movers-by-ID check starts measuring compiler drift.
  **Fix:** compile the census's auto arm with `-fno-start-set` ("the deny
  arm is today's emitter") on the current build.
- **m6. The abi merge-order note (report §8 Q1) is incomplete.**
  - R4a′ is finished at abi 63 on `lane/memfn-r4a2`/`lane/memfnbump`, not
    merged.
  - Both branches touch the same `#define`, `ABI_EXPECT`, the K80
    example, match_api §6, `FILEPIN`, and
    `run_cpset_structure.sh`/`run_resource_tests.sh` byte pins. Both also
    regenerate `docs/dev/artifact_size_log.tsv` in full: 8,168 diff lines
    here, which must be regenerated after the merge, not hand-resolved.
  - "Re-run this lane's codegen pin, which only reads the number"
    understates the work. `FILEPIN` (self-pinned to `b42dffa6`, which has no
    R4a′ bytes) must re-pin after the merge, and the byte pins must be
    re-measured.
  - No check enforces abi MONOTONICITY. `ABI_EXPECT` is an equality. If
    stage 3 lands first, a "take theirs" resolution of R4a′'s `62 -> 63`
    produces 63 after 64, and nothing fails. The ledger sentence "63 is the
    memfn kit's R4a′" (match_api §6, codegen ledger) also assumes R4a′ lands
    first.
- **m7. A spec sentence is wrong.** `docs/spec/match_api.md` §6's new entry
  says "`-fno-start-set` restores the `abi`-62 program apart from the abi
  digits". The abi-62 default carried the VM hat, and `-fno-start-set` at 64
  removes it as well. It restores abi 62's `-fno-start-set` program, which is
  what the emit_sweep "hat" class actually compared (report §3.4).
  `tuning.md`'s "the pre-stage-3 program" has the same ambiguity.
- **m8. Bench reader of the stamp vocabulary.** The pcrec-bench adapter's
  `dfa_prefilter` enum is closed (`pcrec-bench/testees/pcrec/adapter.py:714-716`)
  and cross-checked against its archived `list_axes.tsv`. It lacks stage 2's
  `first-class` and stage 3's two values, and 18 bench movers will stamp
  them. The report relays only the timing questions (§7.3). The pin's inbox
  message should name the two new `RX_DFA_PREFILTER` values and the
  `--list-axes` order shift (`memchr-bounded` 6 → 8, etc.).

## NOTE

- **n1. S504 plants hypothetical code rather than the hat's own emission
  order.** That is fine as a positive control for the `utfcheck` config, but
  its anchor (`pcrec_emit_startpos_guard`'s UTF line) is not the code the
  claim "the skip runs after `rx_valid_upto`" depends on. That claim rests on
  where `pf_emit_first_*` is emitted inside the scan loop, which no row
  plants. Its only detector is 6 `utfcheck` pairs (unfloored per config).
- **n2. The class re-compare replaces the default-build comparison.** For
  class movers the default artifacts are never compared outside the hat; only
  the class-denied pair is. A non-class difference that disappears under
  `CLASS_DENY` is invisible to `[dfa-deny]`. The differential covers the
  answers.
- **n3. `vmhat_checks.py` `[vm-deny]` and `dfahat_checks.py` `[dfa-deny]`
  each exempt the other's movers.** I checked for a hole: `dfahat`
  evaluates `mover` first, so an artifact that is both would still be
  compared, normalized, and would fail on the VM table. No gap today.
- **n4. Optloop tools would misread movers if re-run.**
  `docs/dev/optloop/c2/{firstset_witness.sh, skiproute_census.py,
  scanloop_sim.py}` and `studies/pf_know/census.py` read `can_begin_match`
  as "the scan's set". They are not gates, but on stage-3 artifacts they
  would misread movers as having no table.
- **n5. The spec hunks are present for every caller-observable change I
  found.**
  - `match_api` §6.3 values, from nine to eleven.
  - The §6 abi entry and the K80 example.
  - `tuning` §2.42, including the three cross-row moves.
  - `registry.md` §6, at 129 rows.
  - The `lib/pcrec.h` bit comment.

  `RX_REQ_WHY "dominated"`'s table row (match_api.md "already scans a byte at
  least as rare") is general enough to cover the new cause.
