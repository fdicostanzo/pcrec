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
