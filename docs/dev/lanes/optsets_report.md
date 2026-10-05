# Lane optsets — report

**Task:** the first design note for plan row `[OPT-SETS]` (Frank,
2026-10-05): named option sets, their overlap, and a formal model of how
they interact. DESIGN ONLY: no code, no spec, no plan edits.
**Branch:** `lane/optsets`, from `main` `6f24e187`. **Model:** opus.

## Delivered

- `docs/design/option_sets.md`, sections §0-§6, about 1,050 lines.
- `docs/design/CLAUDE.md`: an entry for it.
- This report.

## Summary (what a resuming agent needs)

1. **Inventory (§1).** pcrec already has four set-shaped mechanisms, each
   with its own composition rule:
   - the dial, five pinned rows OR'd into `flags`;
   - `--features`, with `std1` frozen and `all` derived;
   - the `.rxt` `config`, with `from`/`with` later-wins;
   - the findings bundle, which composes only inside itself (D123).

   Today the tree gives three different answers when one source
   contradicts itself. A deny/force pair is REFUSED. A repeated value
   option is LATER-WINS. The comments pair is DENY-WINS. All three were
   verified live on `build/pcrec`.
2. **Model (§2).**
   - A set is a named partial assignment, either PINNED or DERIVED.
     Derived means a registry predicate, materialized when pcrec is built.
   - Sets combine by compatible union. The union is commutative and
     idempotent, and a disagreement is a conflict, refused by name.
   - A FAMILY is an exclusive group (`tune`, `isa`, `vector`), and a family
     is an axis. Its members therefore replace each other and never
     conflict.
   - Precedence has two tiers per source: sets, then explicit flags, with
     explicit winning regardless of argv order. Across sources, D93 is
     unchanged per axis. The one new reading: a set named in a file makes
     the file speak about every axis in that set.
   - One first-match constraint table (REFUSE / INERT / DERIVE) collects
     the scattered shipped pair refusals and inert rules. A new rule may
     refuse or mark inert; it may never silently assign.
   - A class column (identity / engine-selecting / policy / contract /
     semantic / instrument) decides the sweep and family eligibility. It
     is the same column `[AXES-DENY-MASK]` wants.
   - Building the set mechanism builds `opt_dial_design.md` §1.3's
     deferred per-axis PROVENANCE: the set mechanism is that design's
     named third consumer.
3. **Surfaces (§3):**
   - `--set=`, `--list-sets`, a `set` config line, and
     `pcrec_options.sets`;
   - `RX_SETS`, unconditional, non-default members only, with a `;`
     override tail;
   - `RX_TUNE` kept, and no `rx_info` mirror;
   - `test-axes`: a set is a job; no products except a reasoned `pairs`
     list (`vector` × `isa` first); ISA members run per box via the poset;
     vacuous members still run;
   - three identity gates, whose expectation side is the spec, never the
     set table;
   - seven sabotage rows. The conflict row may ship UNREACHED until two
     real overlapping sets exist.
4. **Worked examples (§4):**
   - the dial as five pinned members. This needs four unspelled axes, and
     λ becomes a `cls-matcher` axis that clskit reads in place of the
     position;
   - `vector` = `auto`/`simd`/`no-simd`/`scalar`. SWAR stays outside
     `no-simd`, per D122 addendum 3's arch-specificity line;
   - the ISA poset;
   - `readable`/`trace`;
   - `--features` as a model check, with a recommendation not to migrate
     it;
   - a contract-class `pcre2-utf`.
5. **Questions (§5.4).** Twelve questions, each with a recommendation.
   §6's trigger is `[MEMFN]` R4c plus a second vector deny, OR R4g
   `--isa`, OR a bench testee request. R4c′'s lone SWAR bit does not
   trigger it.

## Findings outside the note's scope

- `cli.md` says `--no-captures` "forces the DFA engine". In fact
  `--no-captures --engine=vm` emits `RX_ENGINE "vm"` (verified live). That
  behaviour is reasonable; the sentence overstates it. It needs a
  one-sentence D80 fix the next time `cli.md` is touched (§1.3).
- Bench-only questions for relay to pcrecdev2 are in §3.5, items (i)-(iii).

## Validation

None is applicable: this is a docs-only change. No `make` was run. Every
live claim is a read-only `build/pcrec` invocation from the main tree,
writing to stdout. One stray write went to the system `$TMPDIR` early in
the session and was deleted immediately.

## Next

A light panel (the plan row's next step). §6 lists where to attack first.

---

## Revision 2 (lane optsrev, 2026-10-05)

**Task:** apply the light D6 panel r1
(`docs/dev/reviews/2026-10-05-r1-option-sets.md`, all findings accepted)
to `docs/design/option_sets.md`. **Branch:** `lane/optsrev`, from main
`9fd125cb`. **Model:** opus. Docs only. `build/pcrec` was built in the
worktree (`make -j4 CC=gcc-16`, exit 0) for light probes.

### Delivered

- `docs/design/option_sets.md` revision 2. Every change is marked
  `[r1 <id>]` in place, and §R maps all 18 findings to their sections.
- `docs/design/option_sets_measurements/`: `probe.sh` and `cases.sh` (42
  cross-source cells), plus `out/cross_source.txt`, its transcript.
- `docs/design/CLAUDE.md`: the entry updated, and the new directory
  listed.

### Summary (what a resuming agent needs)

1. **Measured (§2.5a).** Today's cross-source composition has six rules:
   - `-f` pairs: union, then refuse (A1/A2/A5), and comments deny-wins
     (A6/A7);
   - `flags` letters: union with the CLI (B1-B4);
   - `features`: whole-list file-wins, silent (C5/C6);
   - typed `engine`: the CLI-wins exception, reported (D1);
   - `analysis`: fill-only, reported (F1);
   - everything else, including every raw `pcrec`-line spelling: silent
     file-wins (D3, E2, G1/G2, H1/H3/H4).

   It also records three findings about today's tree, for the manager:
   - `cli.md` §1.1 misstates `flags` and `-f` bits;
   - the `--engine` exception and the `tune` report depend on the
     SPELLING (D3, E2);
   - the `tune` report names a config's raw `--tune=` as "CLI" (E3).
2. **Model changes.**
   - A deny/force pair is one three-valued axis that unions, then
     refuses, across sources (§2.4a).
   - Constraint rows all apply, REFUSE first, first-match only per party
     (cell M3 shows two rows co-firing). There are four verdicts,
     including GRANDFATHERED-ASSIGN (comments) and DERIVE as
     enable/disable. Row 8 is not built.
   - A `dominates` column, with the measured `min-size` + `-fno-size-term`
     witness.
   - Class is a SET, and each decision reads it through an explicit
     first-match table. DIAL-S3 is the real control.
   - Meta-sets are forbidden.
   - Family axes form one ordered CLI tier.
3. **Stamp.** Recommend NO `RX_SETS` until a consumer asks. The
   conditional design answers S1-S4 and S6.
4. **Checks.**
   - Each check has an independent expectation source: a spec
     member-count floor, and `vec-` name and emit-site counts for derived
     sets.
   - Gate 3 is split between pinned and derived sets.
   - The sabotage table gains a reach column, with `SAB_EXPECT=UNREACHED`
     and `NOW REACHED` for rows not yet reachable.
   - The conflict path is deferred behind a build-time disagreement
     check, and that check is trigger 2.
   - The pairs rows are floored at 3 × 2 per box, against a 32-job
     product.
   - ISA ownership is per box: ubuntubudu v1-v3, the Mac armv8-a, and
     v4/SVE/SVE2 UNOWNED (R6).
5. **Triggers (§6).**
   - §6.1: a consumer request over two or more `vec-` bits already on
     main, the first cross-family disagreement, or a bench request.
     R4g's `--isa` alone is not a trigger.
   - §6.2: the dial re-expression is its own step. Until it fires, the
     set layer reads `TUNE_TABLE` through its accessors. Its triggers are
     a D103 diff needing a column `TUNE_TABLE` lacks, or a second λ
     reader.
   - The D103 ritual gains the disagreement-check step.
6. **Questions (§5.4).** Q1-Q12 re-derived; Q5 and Q12 are REVERSED from
   revision 1. Rulings R1-R6:
   - R1: set cells join union-then-refuse;
   - R2: one axis, one rule, whatever the spelling. This flips D3, the
     one change of outcome;
   - R3: cross-source set disagreements are file-wins and reported;
   - R4: the reports generalize;
   - R5: `features` stays whole-list;
   - R6: the unowned ISA members.

   Q7 (comments) doubles as R7.

### Validation

None is applicable: this is a docs-only change. Validation was the probe
run itself: `SCRATCH=<dir> docs/design/option_sets_measurements/cases.sh`,
42 cells, against the worktree's `build/pcrec` at `9fd125cb` (`abi` 60).
Every scratch file lives in `worktrees/optsrev-scratch/`. Nothing was
written to `/tmp` or `$TMPDIR`.

### Next

Frank's rulings on §5.4. The manager also owes a disposition of §2.5a's
three findings (a D80 `cli.md` correction among them). R2's `.rxt` survey
is done: one fixture spells `pcrec --engine=`, no caller relies on it,
and no `.rxt` in pcrec-bench spells it.
