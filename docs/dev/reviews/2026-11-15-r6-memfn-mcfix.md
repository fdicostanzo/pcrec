# 2026-11-15 r6 memfn-mcfix — light code round on the r5 fix diff (DRAFT, dispositions PROPOSED)

Coordinator draft for the kit manager to rule. Critic texts, COMMON and verify.md are in the sibling dir `review/`
(round dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/).

## Subject

- Mode: code. SUBJECT = `fe1b24e2a6b38bc32fd52053d773c01c3dee91b4` (merge 'lane/memfn-mcfixa' into lane/memfn-mfind).
  BASE = `9cb09119989d72a0b96bbdae97afca23b1cab434` per the launcher (NOT merge-base main, by design: the code up to
  BASE was reviewed by r5 memfn-mfindcomb). Reviewed: the fix diff only (lane reports/journals excluded).
- Review tree built unlocked (`nice make -j2`, rc 0); a JMH dry run of the review tree was pre-run into the kit
  (172 arms; gate + round check green on 7 launches) and `d197_rule.py drill` (21 cases ok).
- Rulings frozen at main `bf16c278f` (decisions/plan last touched `bf8319fb8`); D197 at decisions.md:10219.
- FREEZE NOTE: main's conditions on the rule table (one verdict per level, 1-2 of 36 must reproduce, second
  INCONCLUSIVE = NOT-WIN, ...) had no main record at the freeze (message only); their home is the subject's
  `d197_rule.tsv` header.
- FREEZE DRIFT (at hand-back): main moved to `f9c9306e2`; plan.md +12 lines, none naming mfind/D197/mfcard/memchr;
  decisions.md unchanged. The subject BRANCH moved one commit past the freeze (`ac097a76e`, S3198 comment
  respelled); not reviewed.

## Lenses as run

| lens | model | question | why chosen | time |
|---|---|---|---|---|
| harness fidelity | opus | is the TIMED thing the GATED/KEYED/RECORDED thing, inline as pcrec emits it; plant TIMED-SHAPE's opposite; swap plants on the new pins | the diff is mostly the slot timing harness (lens table: measurement harness) | 5.3 min |
| rule simulate + measurement (+ the two standing questions) | opus | does d197_rule.tsv decide what D197 + main's conditions require for every outcome; implement from the TSV text first, then diff the script | a declared verdict table + reader + drill (simulate; measurement drills) | 4.7 min |
| check adequacy | sonnet | per new/changed kit/test check: what input makes it fail; deleted/invented line plants; S3198 reach | new checks, one sabotage row | 3.9 min |
| verifier | sonnet | re-derive every CONFIRMED finding that changes code | §6.2 | 1.9 min |

All three critics returned in the launch turn with complete files and lanecheck DONE.

## Findings (by id, PROPOSED disposition)

Verified status from verify.md in brackets.

### Measurement-level (the D197 verdict could be reached wrongly)

- **RULE-1** [HOLDS] — a SECOND run whose shipped arm has no verdict reads INCONCLUSIVE (offers a third run), because
  verdict row `INCONCLUSIVE shipped-arm-no-verdict` precedes `NOT-WIN second-run`. Contradicts main's condition "a
  second INCONCLUSIVE is NOT-WIN". **FIX-NOW**: move/add the `NOT-WIN second-run` row above row 1 (or a combined
  predicate) + a drill case. Effort: one row.
- **RULE-2** [HOLDS] — `--confirm` (and `--second`) accept ANY records, including the first run's own: the drill's
  own "[R3] that one-cell loss REPRODUCES" case passes the identical record as its confirmation; a 1-2 cell loss then
  "reproduces" with no re-run. The control shares its source with what it controls (learnings §3). **FIX-NOW**:
  refuse a confirm record that is not window `mfconfirm`, has the first run's run id, or whose JMHC cells differ from
  the CONFIRM verdict's `d197_confirm_cells`; refuse `--second` on the first run's run id; refuse records whose
  `code_commit` / plan / kit fold differ between the two arms and between run and confirm (fidelity's FIDELITY-2
  tail: no `code_commit` read in d197_rule.py). Fold RULE-6 here (derive second-ness from the record rather than a
  flag the CONFIRM trigger forgets). A drill case with the same record must REFUSE. Effort: small.
- **RULE-3** [HOLDS] — the rule (d197_rule.tsv/.py) is NOT PINNED in the run record; the scorer loads the live table
  at verdict time, so "declared before any number exists" is unenforced. **FIX-NOW** (before the 01:00 window, since
  the pin must be taken at `window` time): record.py pins both sha-256 at `window` (it already pins plan/floor/cards/
  policy); `rule` refuses a mismatch. Effort: small.
- **FIDELITY-2 + RULE-8(b)** [PARTLY: mechanics hold; main's literal "variant recorded" is met] — the SHIPPED arm
  takes `want_variant "any"`: two AVX2-tunable records passed as (shipped, avx2) score WIN at all three levels and
  EVEX memchr is never timed; the `axes` column asserts "32-byte EVEX shipped" with nothing holding the record to it.
  **FIX-NOW** (XS): the shipped arm refuses a record carrying GLIBC_TUNABLES, or whose variant equals the AVX2 arm's
  (or: print the axes' libc width from the recorded variant). Effort: XS.
- **FIDELITY-1** [HOLDS] — TIMED-SHAPE refuses only callees named in the object's own defined-symbol set; it passes
  the site out of line via a section-symbol reloc (`noinline,section`), via gcc's own `cold`/`.text.unlikely`
  placement (a shape gcc can produce unprompted at -O2), via an indirect call, or via an external definition; the
  `ext` list it returns is discarded at link.py:590. Today's 172 arms are clean (guard gap, not a wrong timing).
  **FIX-NOW** (S): a per-form callee allowlist (mfind-*: none; fn-memchr: memchr), refuse section-symbol and indirect
  call/jmp targets in `_time`. Proposed FIX-NOW because the check is exactly what r5 FIDELITY-1's fix promises and
  the window is tonight; PLAN is defensible since today's arms pass the stronger check (fidelity PROBED-AND-HELD).
- **RULE-7** [HOLDS] — the drill's "scan ratio printed per level" check can never fail (the format string always
  contains the word "ratio", `ratio -` when a row is missing). Main's condition has no failing witness.
  **FIX-NOW** (1 line): check for a number.
- **RULE-5** [HOLDS] — a missing/refused confirming record re-issues CONFIRM without bound; the TSV is silent (text
  reader read LOSS, script CONFIRM). Contradicts no ruling. **FIX-NOW** with RULE-2 (one declared row, e.g. a
  refused/absent confirmation is INCONCLUSIVE for that level, + a drill case). Effort: one row.
- **FIDELITY-3** [HOLDS, upgraded from SUSPECTED by plant] — CELL TWICE's comment (est.py:559-560) claims to catch
  two keys' cells renamed into each other; a full swap keeps every key unique and est prices the swapped values
  (verifier plant: swar <-> w16 rows exchange, rc 0). Cells files are not pinned in the record. A tamper/relabel
  vector only (no producer path writes a swap). **DOC** now (correct the comment) + **PLAN** (pin each cells file's
  sha-256 in the record at finalize), unless RULE-3's pin work makes it free, then FIX-NOW with it.

### Check-quality

- **CHECKS-A1** [HOLDS] — window.c's new `_Static_assert` is tautological (array sized `FF_MFIND + 1`, assert
  `== FF_MFIND + 1`): an enum member added after FF_MFIND compiles rc 0 and answers NONE by the bounds test, the
  exact case the comment says it prevents (SILENT-MOVE plant). finder.c's `ff_name` assert has the same shape
  (pre-existing). **FIX-NOW** (trivial): an enum sentinel (`FF__COUNT`) or key both to an independent bound; no
  emitted byte moves. Sibling finder.c: same fix, same commit.
- **CHECKS-A2** [HOLDS] — rows_check accepts `instrument:<any non-empty unit>`; the unit is read by nothing (6 of 7
  plants red; `instrument:bogus-unit` green). Nothing checks an instrument row is truly unpicked. **PLAN** (tie the
  unit to the kit's lever list; low risk while one instrument exists).
- **CHECKS-A3** [HOLDS] — run_g2_mfind.py floors scale to 0 at `--sites <= 40` (all floors vacuous); defaults 80/160
  unchanged. **NOTED** (non-default only); a one-line refusal of `--sites < 80` would close it if the manager
  prefers.
- **CHECKS-A4** — G2's mfind generator holds use/body/handoff/empty/span/policy constant (list in checks.md); a
  mfind_applies branch keyed on another value is reached only by the 2 simdguarded lever witnesses. **NOTED**.

### Doc / design

- **RULE-4** [PARTLY] — the reader prices rows est's own `unpriced()` calls null/text; `either-row-unpriced` is
  evaluated on the same object twice (d197_rule.py:94). **DOC**: define "unpriced" in the TSV header (absent | drift
  | no W) and drop the two-row wording.
- **RULE-6** — CONFIRM's trigger omits `--second`. **DOC**, folded into RULE-2's fix.
- **RULE-8(a)** — "loss CELLS" in the TSV vs the reader's (cell, libc row) COMPARISONS (which is what main's condition
  says). **DOC**: rename the predicate and header words. (b) the w32 row's axes omit its w16 tail — **DOC**.
- **RULE-9** — the third ad-hoc `#section`/verdict reader in slot/ (record.py, est.py, d197_rule.py; j1_rule.py's
  constants in code). General form: one `rules.py` (sections, WHEN registry, first-match with why, table sha pin,
  unreached-row/unused-predicate check over the drill). Unlocks: pre-registration for every slot verdict (RULE-3
  once), per-row drill reach. **PLAN**, trigger: the next declared verdict table (the stage-2 re-measure after a WIN,
  or J1's re-run).
- **Differing axes timed vs production** (fidelity PROBED-AND-HELD): caller loop (tight restart vs DFA re-entry at
  state 0), host function's other inlined sites (register pressure; `text_bytes` covers the timed function only),
  placement, fixed compile flags, `evex` label not naming 256 vs 512. **NOTED**: name them in the mfcard ledger next
  to D197's declared one-sidedness.

## Proposed FIX-NOW

RULE-1, RULE-2 (+RULE-5, RULE-6, FIDELITY-2's commit-equality tail), RULE-3, FIDELITY-2/RULE-8(b), FIDELITY-1,
RULE-7, CHECKS-A1. All slot-local or comment-free C (CHECKS-A1); none moves an emitted byte. RULE-1/2/3/5/7 and
FIDELITY-2 are one file pair (d197_rule.tsv/.py + record.py) and fit one fix lane; FIDELITY-1 is link.py; CHECKS-A1
is window.c/finder.c/kit.h.

## PROBED-AND-HELD (summary; details in review/)

- Fidelity: TIMED-SHAPE over all 172 dry arms (mfind/base/w32 call nothing; fn-memchr only memchr); `_time` and
  `_gate` in separate objects; 3 of 7 out-of-line plants refused; the timed site text is byte-identical to
  `build/pcrec-harness --harness=mfind` at none/x86-64/x86-64-v3 (same pragma target, production inlines into
  rx_search, same w32 inner loop); the memchr probe binds evex/avx2 as the record says under 4 tunable settings and
  run.py's env reaches the timed processes; CONFIRM_CELLS refuses a non-cell.
- Rule: 30 constructed outcomes, 28 same between a TSV-only reader and d197_rule.py; per-level independence; 1-2
  comparisons -> CONFIRM, 3+ -> LOSS; floor ties -> tie; trimmed-launch WIN; 9/18 vs 10/18 wins; the statistic
  (per-hit slope over own miss-only base, paired A/A floor) matches the TSV; scan never decides; no global verdict.
- Checks: S3198's anchor occurs exactly once (vrun.c:683); its lever witnesses reach the fit test (by reading;
  unbuilt under the plant); `m6read_check_sab_anchors.py`: 1301 sabotages, all anchors resolve; the G2 top-rung
  check matches the emitted selector shape; rows_check 6 of 7 plants red.

## By-id completeness

FIDELITY-1..3, RULE-1..9, CHECKS-A1..A4: every id above has a disposition. Verified: FIDELITY-1/2/3, RULE-1..7,
CHECKS-A1..A3 (verify.md). Not verified (no code change proposed or doc only): RULE-8, RULE-9, CHECKS-A4.

## Recommendation

A D27 spec-first author is not proposed (no caller-facing contract in the diff). The subject is ready for the 01:00
window once RULE-1, RULE-2, RULE-3 and FIDELITY-2 land (they decide what the window's numbers can conclude);
FIDELITY-1, RULE-7 and CHECKS-A1 are cheap guard repairs that can ride the same lanes.

## Lessons for the guide (proposed)

- A declared verdict table with a confirm/second-run path: the simulate lens drills "the confirmation is the first
  run's own record" and "the second run's refusal" as standing cases (RULE-1, RULE-2 were both reachable only there).
- A check whose comment names a failure mode gets a plant OF THAT MODE (CHECKS-A1's static assert, FIDELITY-3's
  CELL TWICE swap, RULE-7's ratio check were each written for a named failure they cannot see).

## RULED (kit manager, 2026-11-15 ~13:05)
- Every PROPOSED disposition is accepted, with two upgrades:
  - FIDELITY-3: its cells-file sha-256 pin rides RULE-3's pin work (record.py at finalize), so it is FIX-NOW with RULE-3; the CELL TWICE comment is corrected too.
  - CHECKS-A3: FIX-NOW, a one-line refusal of `--sites < 80` in run_g2_mfind.py.
- FIX-NOW list: RULE-1, RULE-2 (+RULE-5, RULE-6, the code_commit/plan/kit-fold equality tail), RULE-3 (+FIDELITY-3 pin), FIDELITY-2/RULE-8(b), FIDELITY-1, RULE-7, CHECKS-A1 (window.c + finder.c sentinel), CHECKS-A3; DOC: RULE-4, RULE-8(a)/(b); PLAN: CHECKS-A2, RULE-9 (trigger as written); NOTED: CHECKS-A4, the timed-vs-production axes (named in the mfcard ledger beside D197).
- One fix lane (mcfixb, opus). Its diff gets a sized code round before it lands (Frank's rule: never skipped).
