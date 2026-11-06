# altrev1 — alt_normal_form.md revision 1 (lane report)

Lane altrev1 (opus), 2026-11-05. Design only: no edits under `src/`, `cli/`,
`lib/`, `memfn/src/`, `tests/`. Branch `lane/altrev1`, cut from main
7ffbd4deb. Subject: `docs/design/alt_normal_form.md` rev 0 (lane altdesign)
→ rev 1, applying the RULED review `docs/dev/reviews/2026-11-05-r2-alt-normal-form.md`
and Frank's five rulings of 2026-11-05 ("Yes to all").

## Premise test

SND-1 reproduced before any text was written, pcrec (`--emit-main` + `gcc -O1`)
against libpcre2-8 10.46 (ctypes; utf8 = UTF|UCP|MATCH_INVALID_UTF),
`docs/dev/lanes/altrev1_evidence/premise.out`: `(?:ab|a|ad)` on `ad` = (0,1) in
both; the width-grouped `(?:a[bd]|a)` = (0,2) in both; `(?:for|fo|fox)`/`fox`
(0,2) vs (0,3); `(?:ac|x|xc)`/`xc` (0,1); `(?i)(?:αb|α|αd)`/`αd` (0,2).
CONFIRMED.

## What changed (rev 0 → rev 1)

- **Rewrites vs facts split** (ruling O1, C1): tree rewrites are exact and
  preference-preserving, owned by the rewrite owner; facts may be supersets and
  come from a separate description. The owner's hull and "trie output" are
  dropped (no reader; SLOT-3, OWN-4).
- **One adjacency test** (§3.2) replaces width grouping (SND-1): branches i < j
  combine only if no branch between them can match a proper prefix or
  extension of either. Prefix factoring needs a fixed-width capture-free key
  and keeps a shorter branch as EMPTY in its slot (SND-2, C2); suffix factoring
  needs only adjacency. In lowering the test is true by construction.
- **altcls's two stages become owner rules** (OWN-1): sibling merge is the
  one-position case of factoring; the one-byte key widens to a fixed-width key.
- **Order** (SIM-2): "a reproducible reduction, not a canonical form"; one
  declared strategy (position-major, last position first, hashed), canonical
  per code-point set in lowering.
- **Concatenation and per-length pieces** (OWN-3, ruling O4): concatenation is
  composed in the facts; a mixed-width letter gives one fixed-width piece per
  total length. `(?i)москва` has 4 pieces; the width-12 one is a 12-position run
  when spelled as bytes (measured: `d09cd09ed081d09ad092d090/ffdfffdffedfffdfffdfffdf`).
- **The wider general form named** (SLOT-6, ruling O5, §3.5): CLASS = position,
  EMPTY = unit, CAT = product, ALT = union with per-width hulls, REP{n,n} =
  power, positive lookaround = a non-consuming piece at an offset; siblings
  staged in §9 with decision points and witnesses.
- **The unit's owner is the kind row** (SLOT-2): a `UNIT` TEXT value for
  `A_EMPTY`; three private spellings become its readers.
- **abi call reversed** (PREM-2/SLOT-1): every byte-moving stage, and a UCD
  bump, is an abi event with the D94 ritual as required steps.
- **Stage 1** (ruling O2): kinds per regime (byte no change; utf8 unit except
  pick-flip choice cells); VM island obligation (PREM-1: read a set position
  inside `A_WCLASS` as its members; island census gate; witness S-i); dot /
  negated / `\p` / `\W` as certain movers (SIM-4, 20 of 76 bench/utf8
  patterns); U1 two-sided from an independent box model (SIM-3); B0 population
  named (`emit_sweep.py --bases byte` + bench); U3 per machine (PREM-5/SIM-8).
- **Stages re-cut**: 1, 2a (ALT + EMPTY arms, census before the build go, D77
  re-argued, OWN-2), 2p (pieces, a new fact, inert until a consumer), 2b
  (altcls via the owner, tree-level movers, A-ISL overlap), 3 (set positions,
  rides [POS-ONE-DETECTOR]; 3m folded in, SLOT-4). Figures per member bound
  (SIM-1: 1403 at the ruled bound 2, 1416 at 3, 1417 at 4).
- **Witnesses rebuilt** (lesson 1): each states why it can fail in both builds.
  S-c `xy(?:ab|abc)zw`, S-f `(?i)xyzk`, S-d SND-1's shapes, S-k the
  variable-key case, S-g (new, the unit arm), S-e at bound 3 (stated as a
  bound-3 witness), S-i (new, island), S-p (a fact witness, stated as unable to
  move answers while inert). Answers measured in `wit.out`, `premise.out`.
- G3 is a ledger (§2.3); §2.2 (1)'s inverted comment reading corrected; §4.6's
  evidence bar now pcrec-side plus a request to the kit (OWN-5); reader audit
  +9 rows (PREM-6); §8 corrected (SIM-5: αβγ 160 → 112, Ελληνικά 1430 → 1040)
  and the k/s caveat traced.
- Disposition table: note §14 (every finding id → section).

## Self-correction during the revision (recorded, not hidden)

My first draft credited stage 2a with `ci-greek-run`'s run. That was wrong:
β's second-byte hull `{92,b2,90}` is out of the cube domain, so 2a does not
move it; its 3-position run comes from stage 1 (the seal's removal, §8 `s0`),
and its 6 come only from stage 3 at member bound 3. Fixed in G4, stage 2a,
stage 3 and §13 q3 before commit. Stage 2a's fold population is instead the
132 equal-width classes whose hull is a cube of ≤ 2 members (766 → about 898,
INFERRED from the critic recount in the review's verify.md; the census owes the
exact number).

## C1-C4 verdicts (note §8a; probes `c4.out`, `c4b.out`, `premise.out`)

| id | verdict | the deciding evidence |
|---|---|---|
| C1 facts are order-free | SOUND | a fact is a necessary condition on the string set; SND-1/SND-2 reproduce only on tree rewrites |
| C2 exact-only rewrites, fixed-width prefix key, EMPTY kept in its slot, adjacency | SOUND-UNDER-CONDITION (key capture-free and fixed-width; consecutive branches; the between-test decided on fixed-position set sequences, failed otherwise) | `a(?:b||d)` equals `(?:ab|a|ad)` on `ad`, `ab`, `adc`, with a following capture `(d?)`; `fo(?:r||x)x` equals on `foxx`; prefix-or-extension is complete because two matches at one start differ only by one being a prefix of the other. Adopted (§3.2, §6) |
| C3 priority-tagged trie in the VM island | SOUND, already built for singleton edges (`vm_isl_build`: accepts in ascending original index, the continuation backtracks into the next); SOUND-UNDER-CONDITION for set edges (sibling edges must stay disjoint) | stage 1 reads a lowered class's set edge as its members, so today's island is unchanged; caseless set edges for user words are U4, riding A-ISL |
| C4 zero-width lookahead after the shorter branch | UNSOUND in local form; the exact form `a(?=X)` (X = the whole continuation) is sound but licenses no merge | `(?:ab|a(?!d)|ad)` on `ad` (0,2) vs (0,1); with `(?:x|dy)` on `ady` NOMATCH vs (0,3); capture `(d?)` moves (1,2) → (2,2). `(?:a[bd]|a(?=X))X`, X = `(?:d|ddd)`, on `addd` (0,3) vs (0,2). The negated-continuation guard `(?:a(?!X)[bd]|a)X`, X = `(?:x|b)`, on `abx` (0,2) vs (0,3). Not adopted; recorded in §8a |

## Plan rows

Status lines rewritten (each ≤ 300 chars), `scripts/plan_lint.sh` from the
worktree: `299 rows parsed, 0 violations`: [RUN-POS-SET], [LOWERENC-SEAL]
(absorbed by stage 1), [REQ-EMPTYCAT] (direct half = stage 2a; quantified half
later; stale FLAG-SPELL symptom noted gone), [REPEAT-RUN] (the REP arm),
[REQ-LOOKAROUND] (the positive-lookaround arm). No new row: every PLAN item
became a named piece of the note (SIM-2 decided in §3.3; SLOT-5 = `rr_alt` row
1b, census-gated; SLOT-6 = §3.5/§9). Owed by the manager (requests are the
manager's to file): a memfn request asking whether a form consumes the
per-length piece set / string-set fact (§3.4, §4.6).

## Open questions for Frank (plain words; note §13)

1. **Per-length pieces have no reader yet.** pcrec can now say, for
   `(?i)москва`, "every match contains one of these four byte patterns". None
   of pcrec's own search code can use a "one of these" fact; searching for one
   of several patterns is a search method, the kit's choice. Leaning: state the
   fact now as ruled, ask the kit, and do not build a pcrec-side "search for
   one of several" form. Cost: `ci-moskva` speeds up only when the kit says yes.
   (This is the stop-rule item: the ruling is sound as a fact, but "now" cannot
   mean a speedup now without a new search form.)
2. **Wider sets per position after stage 3.** The two-value limit per run
   position exists because the old scan had two arms; once positions go to the
   kit as sets, that reason is the kit's. Allow stage 3 to propose three or
   more as a measured choice, starting from two? Leaning: yes.
3. **Count before building stage 2a.** The equal-width-alternation and
   empty-node change has never been counted. Leaning: a small counting lane
   first (no build); build only if a bench cell moves. About 132 more fold
   letters gain from it; which bench cells move is unknown.

## Validation

Design lane: no build changes, no suites owed. One `nice make -j4` of the
worktree (rc 0) for probes. Probes: 4 case files, about 60 pcrec compiles +
gcc builds and libpcre2 runs, all in `altrev1_evidence/`; `--emit-facts`
probes quoted inline in the note. `plan_lint`: 0 violations; pre-commit
staged checks passed (52/0); `check_claudemd_size` within limits.

## STATE AT HANDOFF

STATE: done. Branch `lane/altrev1`: commits e8c4848d9 (evidence), f7fd1a759
(note rev 1, plan status lines, docs/design/CLAUDE.md line), then this report
and the lanes history index entry. Rulings file `altrev1_rulings.md`: empty at
every checkpoint (no entry to apply). Next: the re-check critic round on rev 1,
then Frank's answers to §13, then the build go (after span_pick 1e).
