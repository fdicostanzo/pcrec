# possarms — [ART-POSS-ARMS] design lane report

Lane `possarms`, opus, DESIGN ONLY, 2026-10-07. Branch `lane/possarms` from
main `bcb7b128`. Nothing under `src/`, `cli/`, `lib/` or `tests/` changed.

Deliverables:

- `docs/design/poss_arms.md`, the note;
- `docs/design/poss_arms_measurements/`, the evidence, with its own CLAUDE.md;
- `docs/design/CLAUDE.md`, two new entries.

## Headline

| arm | as the row states it | verdict |
|---|---|---|
| **A** `\b` after a greedy word-pure single-class repeat, `m ≥ 1` | refuted twice: `k+\b` under `utf,i`, where Kelvin U+212A is in the folded class and is not `\w`; and a multi-character body's polarity, which must come from LAST and not FIRST | **SOUND AS RESTATED.** It is `first_of`'s `A_CTX` arm valued from the truth table `fn` with the previous-character polarity set `P`: A0 is context-free, A1 is `P` = polarities of the Glushkov LAST set, greedy only, `m ≥ 1`, feeding row 3 only. Narrower on the purity test (folded code points); wider on multi-character bodies and lookaround-born gates |
| **B** a backreference's FIRST = its closed, non-nullable group's FIRST | "closed" is unnecessary; "non-nullable" is the wrong condition; "the group" must be EVERY `A_CAP` every `refs[]` member can name; the fold keys on the REFERENCE's caselessness | **SOUND AS RESTATED.** Two future tripwires: `(*ACCEPT)` (module `verbs`, unbuilt) and `MATCH_UNSET_BACKREF` (out of scope) |

**Evidence.** libpcre2 equivalence sweeps compare each greedy spelling under
`no_auto_possess` with its possessive spelling. The claims come from a Python
predicate whose class membership is asked of libpcre2 itself.

| sweep | claimed | diverging claims | non-claimed diverging |
|---|---|---|---|
| arm A | 3,294 (deep re-sweep 1,165-1,411 subjects each) | **0** | 7,413 (control non-vacuity) |
| arm B | 399 | **0** | every narrower-rule witness |

Every cited witness was re-run on libpcre2 **10.46** on ubuntubudu
(`witnesses_10.46.out`), and all agree.

## Findings beyond the row (for the manager)

1. **PRE-EXISTING MISCOMPILE ON MAIN** (already sent as an interim message).
   possessify judges a quantifier inside a SUBROUTINE-CALL TARGET against the
   group's lexical follow.
   - `(a+)b(?1)a` on `abaa`: pcrec NOMATCH, 10.46 (0,4). Three more witnesses
     are in note §1. The behaviour is independent of `-fno-splice-calls`.
   - **Sibling hole:** `atomic.c`'s free discharge. Under `-fno-possessify`,
     `((?>a+))b(?1)a` gives (0,4) where 10.46 gives NOMATCH.
   - **Twist:** for `(?R)`, PCRE2's OWN auto-possess is not call-aware.
     `(?:b(?R)a|a+)` on `baa` is (1,3) by default and (0,3) under
     `no_auto_possess`. pcrec default matches 10.46, and `-fno-possessify`
     does not, so `run_possdiff.sh`'s premise does not hold there.
   - **Needs:** a K row and its own lane. The arms must ship after it.
2. **THE GIVE-UP SURFACE IS NOT ONE-WAY.** This is a property of
   possessification in general, not of these arms.
   - STEPS/FRAMES give-ups can only disappear, but a WORK give-up can APPEAR.
     On `doubled-word` (1.5 KB subject) the minimum `--work-budget` goes
     1,070 → 2,565 with the arms.
   - The user-written `\b(\w++)\b\s++\1\b` also gives up at
     `--work-budget=1500` where the denied build answers.
   - `tuning.md` §2.1's "changes no answer" holds only under default budgets.
     Spec drafts are in note §6.
3. **`run_possdiff.sh` cannot test these arms today.**
   - It passes no `--features`: 36 of 36 arm patterns were refused until a
     shim added `--features all`.
   - Its alphabet generator does not produce the discriminating subjects. The
     fold-removal plant (S563) was MISSED: 7 agreed, 0 diverged.
   - The extension plan is note §8.1. S560/S564's plants WERE detected by the
     unmodified harness.
4. **Side finding, pre-existing, for a separate K row.** The byte backend's
   `$_span_match_caseless` folds ASCII only. Under `--ucp` pcrec's classes
   fold Latin-1, and so does libpcre2. So `(\xe9)\1` with `-i --ucp` on
   `\xe9\xc9` is NOMATCH in pcrec and a match in libpcre2 10.48. (Not
   re-checked on 10.46; the local oracle is noted as such.)
5. **Census (K35)**, with a scratch prototype of both arms over [ARTREV]'s
   populations (345 bench / 3,764 corpus):
   - arm A fires on 6 / 12 (`--engine=vm`), arm B on 1 / 1;
   - DEFAULT-route frames move on **3 bench** (`doubled-word` → frameless,
     `email-local-nodup`, `wild-logparse-syslogbase-expanded`) and
     **3 corpus** (`wordb_vm.rxt:339`, `startset/vmhat.rxt:381`,
     `startset/hybrid.rxt:280`);
   - this is a superset of ARTREV's 1 / 2;
   - `run_possdiff.sh` over the 18 byte-encoded firing patterns with the
     prototype armed: 18 agreed, 0 diverged, 19,368 cells.
6. **abi event: yes**, by the [OPT-VEDGE]/[OPT-REQRUN-ENC] precedent. It
   moves program text, `RX_VM_STRATS` and the frame capacity values on the
   movers. No layout moves.
7. **Family lens.** This is a member of `decision_families_survey.md` §3.7's
   first-byte family. D148 Q4's "do not merge `first_of`" stands. The note
   recommends two SHARED primitives instead:
   - `pcrec_ctx_admits`;
   - a facts-layer capture-number → `A_CAP` list.

   possessify reads them first and startset could read them next.

## Open questions for the D6 panel (note §11)

- **Q1.** Fix §1's miscompile first? (Recommend yes.)
- **Q2.** Deny bits: two, one per arm? (Recommend two.)
- **Q3.** Ship A0 at all? (Recommend yes.)
- **Q4.** Is the `(?R)` contract PCRE2's auto-possess answer? (Recommend
  yes, and file an upstream issue.)
- **Q5.** File the seam Latin-1 fold K row.
- **Q6.** Agree to the tripwire form for verbs, branch-reset and the
  unset-backref option.
- **Q7.** Share the primitives in the build commit?

Also for the panel: round3_selection Q4's G1 must read no `possessive` field
(note §7).

## Validation

This is a design lane, so no build validation is owed and `make test` was not
run. What was run:

- the libpcre2 sweeps above;
- the 10.46 witness transcript;
- `tests/possessify/run_possdiff.sh` on the prototype (through a shim; the
  file is unmodified), three runs plus three sabotage plants;
- the census.

All logs are in `docs/design/poss_arms_measurements/`.

## Not done / owed

- Sabotage reach for S561, S562 and S565 against the prototype. Their
  witnesses are oracle-confirmed, but those plants were not run through
  possdiff.
- The census of A0's extra reach for lazy loops and `m = 0` (A0 is sound
  there, but the census counted greedy `m ≥ 1` only).
- A 10.46 check of finding 4.
- plan.md: [ART-POSS-ARMS]'s STATE was left for the manager. It should
  record the design note and the §1 prerequisite.
