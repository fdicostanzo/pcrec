# process — critic round ic1b-code

- 16:07 coordinator start. SUBJECT 1dd510468 (lane/ic1b), BASE 43414ddac.
- Box HELD by queue:530-ic0fix-test at freeze; no build. Review tree
  worktrees/crit-ic1b-code at SUBJECT; build/{pcrec,pcrec-harness,libpcrec.a}
  copied from worktrees/ic1b/build (lane tree clean at 1dd510468; binary mtime
  15:55:37, only CLAUDE.md files newer under src/cli/lib). Smoke: callout
  pattern compiles with --features classes,modifiers,callouts.
- Side observation (not subject): `--features std1,callouts` refused as
  "unknown module 'std1' ... named set: std1" — a named set cannot be listed
  with modules; the diagnostic contradicts itself. Pre-existing? to check.
- Profile: emitted C; decision tables (kindrow, callsite_rows, pf_admits,
  firing class); caller-facing contract; trust boundary (pattern bytes ->
  C identifiers; harness.manifest links C); checks/sabotage/floors; rulings.
- Lenses (5, cap): emitted-vs-replaced (opus), contract+goals (opus),
  adversary (opus), slot tracing+ruling check+sibling/general-form (opus),
  check adequacy+trade audit of re-pins (sonnet). NOT staffed: house rules
  (cap of 5; callout.c/mod_callouts.c plain C) — noted as a gap.

## Agents
| agent | model | launched | ended | final state | findings |
|---|---|---|---|---|---|
| emitted (a524c0491004ff000) | opus | 16:10 | ~16:24 (14m) | file complete, returned in launch turn | EMIT-1..3 (+1 note) |
| contract (a0cfaec9b4bfd30f0) | opus | 16:10 | ~16:24 (14m) | file complete | CON-1..10 |
| adversary (a6d7ca0355c706e00) | opus | 16:10 | ~16:15 (6m) | file complete | ADV-1..6 |
| slots (a5c115bcd46490eaf) | opus | 16:10 | ~16:20 (11m) | file complete | SLOT-1..10 |
| checks (a9ecb37c64d55d525) | sonnet | 16:10 | ~16:16 (6m) | file complete | CHK-1..6 |

- All 5 critics returned in the launch turn (skill §6.1's case); every
  "final reply" was lost ("ended without delivering a report through
  SubagentHandback") but every FILE was complete: the files-not-replies rule
  carried the round. No resend or nudge needed.
- Blinding: no critic reported opening a denied file. The checks critic ran a
  COPY of gen_diff.py (n=45) in scratch: a borderline read of "never run a
  suite" (a generator, not a suite; scratch only) — note for COMMON.
- Freeze drift: main advanced during the round (16:14, merge of lane/ic0,
  stage 0, abi 88). EMIT-2 / SLOT-7 (stage 0 not under the subject) are
  therefore now a REBASE item, not a merge-order risk. The contract critic
  noticed main had moved (12b5bd70c) and correctly declined to use main's
  build as BASE; the emitted critic used an abi-86 main build as NEAR-BASE and
  attributed deltas by shape.
- Overlaps: CON-1 = ADV-5 (trailing empty attribute); EMIT-2 = SLOT-7
  (stage 0 comment); CON-5 ~ SLOT-1 (never-run groups: stamps vs class);
  ADV-3/ADV-4 ~ CON-1 related (rxt/cli callout-line shape readers).
| verifier (a1941030158e30b89) | sonnet | 16:25 | 16:29 | ended in the launch turn WITHOUT its file (probes done in verify/); ONE resend asking for the file; file COMPLETE 16:29 | 31 ids: 27 HOLDS, 1 PARTLY (SLOT-6), 0 REFUTED; ran compliance_section.py --check (read-only; FAIL) |

- 16:30 review worktree removed (wtprune --force --quiet-min 1). Draft
  review.md at 16:30: about 23 min from freeze to draft.
- Per lens, raised / held under verification / severity:
  emitted 3/3 (speed, doc, size); contract 10/9 + 1 unverified (2 answer-level:
  CON-2, CON-8; CON-3 gate-red); adversary 6/6 (ADV-1 and ADV-3 answer-level);
  slots 10/9 + 1 PARTLY (no answer-level; SLOT-1 design); checks 6/4 + 2
  SUSPECTED (maintenance/doc).

## Process observations
- Every agent's final reply was lost ("ended without delivering a report
  through SubagentHandback"). Five of six had their files; the verifier had
  only probe scratch and needed the one resend. The verifier brief told it to
  write incrementally, but its header was never written before probing. A
  verifier, unlike a critic, tends to probe first and write last.
- The critics ran 6 to 14 minutes. The sonnet check critic was as quick as
  the fastest opus critic and found no answer-level issue. That fits its lens:
  check adequacy surfaced "skip green" and floor gaps, not bugs.
- The highest-value finding (CON-2, a firing-class error) came from the
  CONTRACT lens probing class claims at run time with a counting driver. The
  slot lens read the same function (co_choice) and found SLOT-1 but missed the
  A_LOOK atomic case. Run-time probing of a stated bound beat reading.
- Adversary was cheap (6 min) and found the only uncompilable-output bug
  (ADV-1). The lens table's "trust boundary" row framed it as
  untrusted-input-to-code. The real hit was a NAME COLLISION with the fixed ABI
  block, which is a namespace question, not an injection one.
- The house-rules lens went unstaffed (cap of 5); slots picked up two such
  items (SLOT-8, SLOT-10) on its own.
- Freeze drift: main merged a stage the subject depends on (ic0) mid-round. A
  finding (EMIT-2/SLOT-7) changed meaning from "merge-order risk" to "rebase
  step". The skill does not say whether to re-read main's state before drafting.
- The box was busy, so a same-commit binary from the lane's own worktree was
  used. Checking "lane tree clean at SUBJECT + no source newer than the
  binary" was quick and adequate.
- One critic ran a scratch COPY of a test generator (gen_diff.py, n=45).
  COMMON's "never run a suite" did not clearly cover that. It was harmless and
  useful.

## Proposed changes
1. Skill §6.2: "The verifier writes verify.md's header and one line per id
   AS IT GOES; a verifier that probes first and writes last loses everything
   when its reply is dropped (2026-10-26 ic1b-code: needed a resend)."
   Motivation: the verifier delivery failure above.
2. Lens table, `adversary` row question: add "...and every name the input
   becomes: does it collide with a FIXED name of the shared ABI block or the
   artifact (not only the prefix family)?" Motivation: ADV-1.
3. Lens table, `contract` row: add "where the spec states a bound or class
   (fires per attempt, a count), probe it with a counting driver, not by
   reading the derivation." Motivation: CON-2 was found by counting, and
   missed by reading.
4. Skill §6.3: before drafting, `git log BASE..main --format='%h %s'`. Any
   merge into main since the freeze that touches the subject's design order
   is named in the draft's subject section. Motivation: the ic0 merge at
   16:14.
5. COMMON template: "running a COPY of a test generator in scratch on a
   small n is allowed; the suite scripts and run.sh are not." Motivation: the
   check critic's gen_diff copy.

## Framework notes
- Coordinator pattern, code mode, fifth component (5 critics + 1 verifier):
  about 23 minutes wall from freeze to draft, at no manager turns. All
  results travelled as files. The rule "files, never replies" carried the
  round: 6/6 final replies were lost.
- Blindness held by construction: the coordinator knew no prior results, so
  no brief could leak them.
- Where else: any fan-out where workers' replies are unreliable but files
  are not, such as a bench-pattern triage, a doc consistency sweep across
  spec/ and design/, or a per-module compliance refresh. The shape is a cheap
  coordinator, narrow workers, an independent verifier, and one drafted
  ruling sheet.
