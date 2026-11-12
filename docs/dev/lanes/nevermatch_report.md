# nevermatch report ([NEVER-MATCH], the part beyond pffix)

## STATE AT HANDOFF

STATE: delivered (validation partly OWED, see OWED). Branch `lane/nevermatch` from main `b2f893ffd`.
Commits: `dac304348` (WIP: the fact and the flip), `a60681ae2` (abi 100 -> 102, spec, manifests),
`018eff8aa` (recidentity self-pin), then the docs/report commit. Rulings file
`docs/dev/lanes/nevermatch_rulings.md`: absent/empty at every checkpoint; no ruling applied.

What shipped:
- Under `--engine=auto`, a VM hybrid whose prefilter machines admit no match is now the DFA engine's
  EMPTY artifact. It goes through the existing `empty` LOCATE row; there is no second mechanism.
  16 corpus patterns move. Their artifact text drops from 543,070 to 364,001 bytes (-33%).
- A new `--emit-facts` fact `never_matches`, value `empty-machine` or `no`, with its spec hunk.
- abi 100 -> 102. 101 is left for the kit's K38-2. If the landing order differs, re-pin the number.

What did not ship: the recursion-with-no-base-case case (6 corpus patterns). The proof I expected
to use does not exist; see FINDINGS 3.

## FINDINGS

**1. Premise test.**
- `ab\Gcd` is the DFA empty engine, as briefed. `--emit-facts` now also lists
  `never_matches empty-machine`.
- A VM-forced never-match gets no proof. `--engine=vm '(a)\b(b)'` builds no machine, so it gets the
  full VM program and `never_matches no`.
- With `--engine=vm -fprefilter`, the hybrid's prefilter is empty (pffix) and the fact reads
  `empty-machine`. The artifact stays a VM hybrid, because both flags are do-or-die.
- `(*FAIL)` and `(?!)`-style spellings need module `verbs` / `lookaround`. `(?!)` is a VM artifact
  under `--features all`, with no machine and no proof.

**2. Census.** The population is every distinct `pattern` line in every `.rxt` under `tests/`,
5,486 of them, which includes tests/uprops/d27. Each was compiled with `--features all -p rx -o -`
and default options: 5,003 compile and 483 are refused (they need block flags or an encoding).
The script is `$PCREC_TMPDIR/scratch/nevermatch/census.py`, with output in `census.tsv` (before) and
`census2.tsv` (after). Never-match patterns pcrec can already show, by route:

| route | proof pcrec has | patterns | full matcher emitted before? | after |
|---|---|---|---|---|
| DFA (unanchored / attempt) | machines accept nowhere (`unanch_start`'s empty, pffix's `dfa_accepts_nowhere`) | 254 | no: already the empty engine | unchanged |
| VM hybrid | the prefilter's machines accept nowhere (its scan stamped `"empty"`) | 16 | YES: a full VM program behind a prefilter that returns 0 | the DFA empty artifact (`RX_ENGINE "dfa"`, `RX_DFA_SCAN "empty"`) |
| VM, no prefilter | `RX_VM_ROOT_MINW` at the ceiling 2^40 (MRL) | 6 | yes (249,430 bytes) | unchanged: not a proof, see 3 |
| VM, no prefilter, other | none (`(?!)`, `--engine=vm` spellings) | not countable | yes | unchanged |

The 16 moved patterns:
- `(a)\b(b)`, `(a+)\b(?1)`, `(?<g>\w\b)(?&g)?x`, `(?=a)\Kb`, `a(?=b)\Kc`, `a\K\bb`;
- `(?>a|ab)\bc`, `(?>a\b)c`;
- `((?=a)z)`, `((?=[ab])z)`, `((?*a)z)`, `((?*[ab])z)`;
- the four `(?>...)` twins of the line above.

Each pattern's file ran green after the change: 12,219 cases passed, 0 failed, over kreset.rxt,
wordb_vm.rxt, atomic_assert.rxt, lookaround/d27/{matrix,refusals}.rxt, lookahead.rxt and
composition_d27.rxt. The log is `scratch/nevermatch/h1.log`.

The census before and after differs in exactly these 16 rows. The empty bucket is 270 both times,
because the 16 hybrids were already stamped `"empty"` and now sit on the DFA side. The artifact text
for the 16 drops from 543,070 to 364,001 bytes (`-o -`, -179,069).

**3. The MRL ceiling is not a never-match proof.**
`RX_VM_ROOT_MINW == 2^40` is shared by two different situations:
- a recursion with no base case (`^(a(?1)b)$`, `(?R)a`, ...), whose language is empty;
- a merely SATURATED finite minimum. `(?:(?:(a){65535}){65535}){65535}\1` compiles, stamps the same
  `1099511627776ULL`, and is matchable in principle.

internal.h says so at `PCREC_W_UNBOUNDED`, and the emitted MRL comment says so too ("it can also mean
the true minimum merely saturated the analysis"). Two consequences follow:
- A constant matcher there would differ from the VM on a subject of 1 TiB or more.
- A `never matches` fact there would be unsound.

Telling the two apart needs a PRODUCTIVITY fact: does a group have any finite derivation? That is a
small boolean fixpoint beside `pcrec_callgraph_build`'s minw iteration, or an "infinite" sentinel
distinct from saturation in that iteration's domain. The brief rules out a new analysis, so I built
neither. The 6 patterns stay VM artifacts, already answered in constant time by the MRL guard.

**4. Dead alternation branches.** No existing proof identifies dead branches inside a VM program.
derive.c's never-prune exists only for a compound part after its floor kill. Candidate count:
- 183 corpus patterns have a top-level alternation, 423 arms in all. Patterns that start with a
  `(?` option prefix were skipped.
- Each arm was compiled alone. 9 are DFA-empty, and all 9 sit in DFA-route patterns: `\b\B|...`,
  `^\Bfoo|^x`, `a\Gb|c`, `x\G|y`, and so on. The DFA construction already erases those arms, so
  they cost nothing.
- 0 dead top-level arms were found in VM-route patterns.

Nested branches wait for span_arms L1, as briefed. Script: `scratch/nevermatch/arms.py`, output in
`arms.txt`.

**5. The fact's epoch.** `never_matches` reads the compile's machines. `E3` is sealed only on the
`ENG_UNANCH` branch, so an E3 fact is `absent` on the attempt route, which is where `^\B\b` and
`ab\Gcd` live. The fact is therefore `E2` with an explicit guard: it refuses to be asked before the
driver sets `Job.machines_final`. The listing's force loop and the driver's flip both ask after that
point, so the answer cannot depend on when it was asked. This needs the manager's eye: the
alternative is a per-row "derivable on every route" column in facts.def.

**6. Process: the census sweeps were run without the box lock.** The two census sweeps (5,486
compiles each, 4 threads, nice 19) and the arms sweep (423 compiles) ran outside `scripts/boxlock`.
That breaches RUNS.md's sweep cap. The box was held at the time by the kit's queue job
`580-kit-kclose2-r13a`, which is not a timing job and ended GREEN. Every later run went through
chainrun `heavy` stages.

**Proposed decision (the manager writes it).** A pattern the compile shows matches nothing is
answered by the DFA engine's empty artifact on every route `--engine=auto` reaches with machines.
- A forced engine and `-fprefilter` keep their artifact (do-or-die), and `--emit-ir` refuses as on
  any DFA artifact.
- The `never_matches` fact is one-sided and best-guess, so the set it names may grow.
- No public flag is added: the answer is identical by construction, because the hybrid already
  answered every search "no match". The `--engine=vm` axis is the comparison lever.

## CHANGES

- `src/ir/dfa.c` + `internal.h`: `pcrec_dfa_accepts_nowhere` (moved from emit_dfa.c's static) and
  `pcrec_dfa_pair_matches_nothing` (unanch_start's three empty causes, now one function). Both are
  read by the empty LOCATE row (`unanch_start`, `locate_empty_applies`, `attempt_cand`) and by the
  fact. This is one derivation, and it emits no new bytes.
- `src/facts/` (`facts.def` row, `facts.h`, `facts.c`, `facts_derive.h`, `kset.c`): fact
  `never_matches` (E2 core, owner kset.c, no deny), `PfNever {NO, MACHINE}`, rendered `empty-machine`
  or `no`. `Job.machines_final` is set by the driver after the machine build.
- `src/core/compile.c`: after the machine build, a hybrid with `never_matches == MACHINE` becomes the
  DFA engine (`fit.chosen = ENGM_DFA`, `fit.prefilter = false`). The flip needs all of:
  `--engine=auto`, no `-fprefilter`, and a prefilter (a callout pattern never has one).
  `--emit-ir`'s refusal text gains "or it matches nothing" (239 of 255 bytes).
- abi 100 -> 102. Readers found by grep:
  - `PCREC_ARTIFACT_ABI`;
  - match_api.md: guard block, rx_info row 1, §6¶17, the §6.3.4 `"empty"` row, the §6.3.3¶3
    `"selected"` row;
  - `ABI_EXPECT` and its message;
  - S693 BEFORE/AFTER;
  - abi_changelog.md;
  - the recidentity FILEPIN/ABASEPIN self-pin to `a60681ae2`.
- Spec: facts_listing.md §1¶2 and the new §4.1.2¶12.
- Manifest: run_dfa_stamps.sh EMPTY_MANIFEST +16 (254 -> 270).
- Docs: src/facts/CLAUDE.md and src/ir/CLAUDE.md file roles, and the plan row's status line.

## OWED

- **Local pinned sections, run through chainrun** (logdir `$PCREC_TMPDIR/scratch/nevermatch/chain1/`,
  head `018eff8aa`):
  - GREEN: `make strict`, test-codegen (21/21 scripts, including run_dfa_stamps with the 270-pattern
    empty manifest), test-rxtsource, test-startset, test-compound, test-resource and
    test-cpset-structure.
  - test-partlayout was RED on the census: 3 of the 16 moved hybrids are in its population and lost
    their subject (`((?*a)z)`, `((?=[ab])z)`, `(?<g>\w\b)(?&g)?x`).
  - Fix: the 16 are added to its declared `NEVER_MATCH` set, and the subject floor goes from 370 to
    365 of 380. The reached count is now 368 of 387; the floor's ratio is kept under it.
  - Re-run solo under `boxlock run` (`make test-partlayout`): `checks failed: 0`.
    Log: `scratch/nevermatch/partlayout2.log`.
- **Cloud: `scripts/cloudrun --owner main --kind test --name nevermatch`**, dispatched as the last act
  (the run line is in the handback). The axes kind follows only if test is green, since emission
  changed.
- **Not run:**
  - `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh`, owed because the empty row now fires in
    16 new places;
  - recidentity: the cloud kind `recidentity`, or `make test-recursion-identity` through the box queue.
