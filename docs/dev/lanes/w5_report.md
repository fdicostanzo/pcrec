# [REVW.5] WAVE 5 (public surface) + [REVW.A1] — LANE REPORT

Lane `w5` (opus), worktree `worktrees/w5`, branch `lane/w5` from `main` at
`25b1984f`. Thirteen commits. The last items of the 2026-09-17 code review.

**The wave's headline number: `nm -g build/libpcrec.a` reports 295 exported
definitions and ZERO of them without a `pcrec_` prefix.** It was 34 unprefixed
at the branch point.

---

## 0. What the sources got wrong, measured against this branch point

Four corrections, each found by re-measuring rather than by reading:

1. **The rename population is 34, not 29 and not 12.** D104 named twelve;
   `w5_facts.md` re-measured 29 at `b1f0a430`; at `25b1984f` it is **34**.
   `sb_cmt_open`, `sb_cmt_close`, `sb_comments` and `sb_len_uncut` landed
   with [EMIT-VERB] in between, by the same mechanism the sheet documented —
   `static` dropped so the emission kit could cross a translation-unit
   boundary, with no wave chartered to look at the linker surface. The
   population has grown in every measurement anyone has taken of it.

2. **`w4_report.md`'s motivating example for the union mode membership is
   FALSE.** It says `--probe-ask --flavour=pcre2` is ACCEPTED today. It is
   REFUSED, rc 1, `--flavour applies to --list-syntax, --list-definitions and
   --explain only` — the probe-ask site's own `if (flavour)` arm gets there
   first. See §2; it changes the item's disposition.

3. **`ctx_fail` has TWO sabotage anchors, not eight.** D104's figure came
   from `grep -rl` over `tests/mech/sabotages/`, which counts files that
   MENTION the symbol. Rows quote callers in their prose constantly; only
   `SAB_BEFORE`/`SAB_AFTER` is load-bearing. Anchor-level census over all 34
   names: **33 rows**, and `pcrec_sb_printf` alone carries 19 of them.

4. **`emit_dfa.c`'s abi log had 8 gaps, not the 9 the sheet reported** —
   `26 -> 27` WAS backfilled. The 8 are lens 4's original 8, unchanged since
   the review. (The sheet's other A1 findings all held.)

---

## 1. Item 1 — the spec sweep (L9-P3 + §5.2 rider + L9-P6). Commit `370c977f`

| finding | before | after |
|---|---|---|
| `match_api.md` §8.2's struct quotation | 9 of 19 members | **19 of 19**, declaration order, one-line gloss each |
| `tuning.md` §4's `pcrec_options` mirror | 14 of 28 `flags` bits | **28 of 28**, and the table says it is exhaustive |
| `match_api.md` §8.2's mask catalogue | delegated to `lib/pcrec.h`'s comments | points at `tuning.md` §2, the spec tier |

Ten members were invisible to a caller reading the contract:
`vm_entry_shape`, the six `max_*` caps, `warn_emit_bytes`, `name`, `tune`.
The quotation block now states the rule it follows, so the next field added
has somewhere to land.

Nine `flags` bits had no mirror row — the seven lens 9 named plus §2.24's
`-fno-comments` pair, which landed after the review. `--vm-entry-shape`'s
`PCREC_VM_ENTRY_*` constants had no spec row anywhere under their enum
spellings, which is what a library caller writes; they have one now. The four
bits that are NOT tuning axes (`PCREC_CASELESS`, `PCREC_EMIT_MAIN`,
`PCREC_NO_CAPTURES`, `PCREC_TRACE`) are named underneath with where each IS
documented, so "not in the table" reads as a decision rather than a gap.

No line number is cited anywhere in the change, per the brief's rule. One
citation was corrected mid-flight: an early draft sent `--trace` to
"`table_contract.md` §1", which has no numbered sections and which places the
trace stream explicitly OUT of scope. It now cites that document's Scope
section for what it actually says.

**Sweep:** 0 movers, 0 asymmetric, five streams, self-check PASSED at full
reach, 275.1s.

---

## 2. Item 2 — the UNION MODE MEMBERSHIP: MEASURED, and **NOT BUILT**

The brief's gate: build it only if every flipped pair is a nonsense
combination; if any flipped pair is a plausible use, table the pairs.

Measured with the committed instrument `docs/dev/lanes/w4_modesweep.py`
against a union-mask build (each site's mask replaced by "every mode but this
site's own"; the registry site's count relation widened to "at most one mode
at all"), 1,407 invocations, three operand shapes:

| measure | today | union |
|---|---:|---:|
| identical (rc + stdout + stderr) | — | 1,365 / 1,407 |
| accepted (rc = 0) | 15 | 11 |
| differing | — | 42 |

**THE FOUR ACCEPTANCE FLIPS, all accept → refuse:**

| invocation | today | union |
|---|---|---|
| `--list-syntax --flavour pcre2` | 0 | 1 |
| `--list-definitions --flavour pcre2` | 0 | 1 |
| `--explain \d --flavour pcre2` | 0 | 1 |
| `--emit-ir --flavour pcre2 -- a(b\|c)` | 0 | 1 |

**DO NOT BUILD.** Three of the four are the DOCUMENTED PRIMARY USE of
`--flavour`. `docs/spec/cli.md`'s own section is titled
"`--explain SYNTAX` / `--flavour NAME`" and says "`--flavour` restricts
either query"; the CLI's own live diagnostic names exactly these three modes
as the ones `--flavour` applies to. The union refuses all three. This is not
a nonsense combination flipping — it is the feature.

The proposal rested on an asymmetry that does not exist at the observable
level. `--probe-ask --flavour=pcre2` is refused TODAY, and so is every other
mode-plus-`--flavour` pairing outside those three, by the sites' own
`if (flavour)` arms with the applies-to diagnostic. What the four masks
differ about is WHICH check does the refusing, not what is accepted. The
reader-can't-explain-it complaint is real and is about the masks' names; the
union is the wrong remedy for it, because `--flavour` is a QUALIFIER that
three modes take and not a fourteenth output mode. **The remedy worth
proposing instead** is to stop treating `--flavour` as a mode row at all and
give it its own applies-to relation, which would let the remaining thirteen
take one union mask honestly. Not built here: it is a design change, not a
D80 batch item, and it needs a ruling.

No commit. No `docs/spec/cli.md` hunk, because acceptance did not move.

---

## 3. Item 3 — the limits surface (L9-P4). Commit `a5d8cb54`

The eleven cited-but-undeclared constants sorted into three groups:

**EIGHT are real and a caller legitimately needs their values** —
`PCREC_MAX_VM_EMIT_CODE_BYTES`, `PCREC_MAX_EMIT_BYTES`,
`PCREC_MAX_NFA_STATES`, `PCREC_MAX_DFA_STATES_GOTO`, `PCREC_MAX_SUBSET_ELEMS`,
`PCREC_MAX_AUTO_DFA_ELEMS`, `PCREC_DEFAULT_WARN_EMIT_BYTES`,
`PCREC_DEFAULT_UNROLL_K`. Each has a `pcrec_options` field and six of those
are RAISE-ONLY, so a caller must know the default to raise a cap — and its
only route was to trigger the refusal and parse English out of
`pcrec_error.msg`.

**ONE is real and correctly not a lever** — `PCREC_MAX_DFA_STATES_TABLE`,
whose own comment already explains that raising it past what the emitted cell
type can hold would be a lever whose numerator lies. Left cited.

**TWO were not real at all**, which is the finding under the finding:
- `PCREC_PREFILTER_EXACT_NFA_STATES` was DELETED at [OPT-4] (2026-08-29) with
  deliberately nothing in its place, and `lib/pcrec.h` had gone on describing
  a collapse that fires "above" it ever since — a threshold that does not
  exist, in the contract's own words.
- `PCREC_VM_INLINE_CHAIN_MAX_BYTES` is spelled `VM_INLINE_CHAIN_MAX_BYTES` in
  the tree. The header INVENTED the prefix; a caller who grepped for it found
  nothing.

**The fix is ONE declaration, not eight.** `char *pcrec_limits_tsv(void)` is
declared in `lib/pcrec.h` with its full contract, and **its declaration LEAVES
`src/core/internal.h`** (which includes `pcrec.h`, so every internal caller
still sees it) — two declarations of one contract is the second-spelling shape
this project has a rule against. This is lens 9's shape (b). Shape (a),
emitting the values as `#define`s, is declined in writing at the site: a
second spelling of every NUMBER, free to drift from `limits.def`, which is
D90's ruled single home. D80: `docs/spec/limits.md` gains §3.4a.

**Not taken, and named so it is not lost:** lens 9 §5.1's rider that the
header says nothing about NUL termination (K9). That sentence would state a
CONTRACT about an open issue with two competing remedies — a ruling this lane
does not have.

**Sweep:** 0 movers, five streams, self-check PASSED, 271.4s.

---

## 4. Item 5 / [REVW.A1] — the abi change log. Commit `2c5c1948`

Four homes, measured at `abi` 27:

| home | before |
|---|---|
| `src/gen/emit_dfa.c`'s comment log, 449 lines | 8 transitions missing, surviving entries OUT OF NUMERICAL ORDER (`8->9` between `3->4` and `4->5`) |
| `run_codegen_tests.sh`'s failure message | missing `20->21`, `21->22` |
| `src/gen/CLAUDE.md`'s `##` sections | last abi-numbered title `17->18` |
| `docs/spec/match_api.md` §6 | **gap-free `2`..`27`** |

§6 is complete for a structural reason: every bump's D76/D94 ritual carries a
`docs/spec/` hunk, so the same act that takes the bump maintains §6, while the
three copies were maintained by nothing. That is `learnings.md` §3 twice —
a population nobody censused (lens 4 counted three homes without sweeping for
a fourth), and copies with no shared source.

Landed as ruled: §6 says it is the log, in its own paragraph; `emit_dfa.c`
449 comment lines → 22 (meaning, ritual, current bump, pointer, and why the
log left); `src/gen/CLAUDE.md` gains a pointer and keeps its per-milestone
DESIGN sections, now explicitly not a log; the codegen suite's string stays —
**a check is not a home** — with both transitions backfilled FROM §6 and a
comment at the site stating which direction the copying goes; D76 gains an
addendum with the table above. `coding_guide.md` §3.1 said "`abi` is 26 today"
with a line citation, stale by a bump and against its own cite-by-name rule;
§4.2's "three drifting homes" sentence is rewritten to what is now true.

**Sweep:** 0 movers, 261.6s. **`make test-codegen`:** 9/10 scripts, 174 checks
passed / 0 failed, sole FAIL the standing darwin `nm` probe in
`run_inline_capability.sh`. All 285 anchor sites resolve after the 449-line cut.

---

## 5. Item 4 + item 6 — THE RENAMES

### 5.1 The table

| symbol | new name | src+cli sites | anchors | commit |
|---|---|---:|---:|---|
| `nfa_has_asserts` | `pcrec_nfa_has_asserts` | 2 | 0 | `d690b9a9` |
| `nfa_has_bot` | `pcrec_nfa_has_bot` | 8 | 0 | `d690b9a9` |
| `nfa_wrap_unanchored` | `pcrec_nfa_wrap_unanchored` | 27 | 0 | `d690b9a9` |
| `arena_free` | `pcrec_arena_free` | 26 | 0 | `00670fe9` |
| `cg_sat_mul` | `pcrec_cg_sat_mul` | 5 | 0 | `00670fe9` |
| `sb_comments` | `pcrec_sb_comments` | 7 | 0 | `00670fe9` |
| `sb_fragfv` | `pcrec_sb_fragfv` | 10 | 0 | `00670fe9` |
| `sb_free` | `pcrec_sb_free` | 13 | 0 | `00670fe9` |
| `sb_join` | `pcrec_sb_join` | 10 | 0 | `00670fe9` |
| `sb_row` | `pcrec_sb_row` | 24 | 0 | `00670fe9` |
| `sb_take` | `pcrec_sb_take` | 19 | 0 | `00670fe9` |
| `sb_textn` | `pcrec_sb_textn` | 9 | 0 | `00670fe9` |
| `sb_upper` | `pcrec_sb_upper` | 9 | 0 | `00670fe9` |
| `vm_fmul` | `pcrec_vm_fmul` | 13 | 0 | `00670fe9` |
| `sb_field` | `pcrec_sb_field` | 22 | 0 | `3b2e2327` |
| `sb_fragf` | `pcrec_sb_fragf` | 12 | 0 | `3b2e2327` |
| `sb_len_uncut` | `pcrec_sb_len_uncut` | 7 | 0 | `3b2e2327` |
| `sb_stamp_str` | `pcrec_sb_stamp_str` | 24 | 0 | `3b2e2327` |
| `sb_stampwf` | `pcrec_sb_stampwf` | 12 | 0 | `3b2e2327` |
| `sb_text` | `pcrec_sb_text` | 30 | 0 | `3b2e2327` |
| `sb_cmt_open` | `pcrec_sb_cmt_open` | 74 | 0 | `3b2e2327` |
| `cg_sat_add` | `pcrec_cg_sat_add` | 4 | 0 | `f2438be5` |
| `mrl_sat_add` | `pcrec_mrl_sat_add` | 25 | 3 | `f2438be5` |
| `mrl_sat_mul` | `pcrec_mrl_sat_mul` | 12 | 1 | `f2438be5` |
| `vm_fadd` | `pcrec_vm_fadd` | 27 | 0 | `f2438be5` |
| `sb_stampf` | `pcrec_sb_stampf` | 38 | 3 | `1f9c7acd` |
| `sb_cmt_close` | `pcrec_sb_cmt_close` | 72 | 1 | `1f9c7acd` |
| `sb_putc` | `pcrec_sb_putc` | 141 | 1 | `d18ec20c` |
| `sb_puts` | `pcrec_sb_puts` | 407 | 3 | `d18ec20c` |
| `sb_printf` | `pcrec_sb_printf` | 477 | 19 | `d4eccc7b` |
| `arena_alloc` | `pcrec_arena_alloc` | 206 | 2 | `b5cb8f85` |
| `ctx_nomem` | `pcrec_ctx_nomem` | 26 | 2 | `b5cb8f85` |
| `PCREC_DEFAULT_FEATURES` | `pcrec_default_features` | 7 | 0 | `589acaf1` |
| `ctx_fail` | `pcrec_ctx_fail` | 260 | 2 | `376e34b4` |

Ten commits, grouped by blast radius as the D104 addendum rules: `nfa_*`
first as the pattern-prover, `ctx_fail` last, one mechanical commit for the
eleven with neither an anchor nor a name-keyed reader, and the rest grouped
by FAMILY (the saturating-arithmetic four; the `sb_*` text primitives) so a
bisect lands on a whole relation rather than half of one. No shims, no
aliasing macros: one spelling per symbol.

**Unprefixed exports: 34 → 31 → 20 → 13 → 9 → 7 → 5 → 4 → 2 → 1 → 0.**

### 5.2 How the anchor population was measured, and the two wrong answers first

"Does a sabotage row name this symbol" is a question about ANCHOR TEXT, not
about the file. `grep -rl` over-counts. Two hand-written extractors then
under-counted: the first read only lines beginning `SAB_BEFORE=`, missing
every multi-line anchor; the second tracked `"` and missed every
single-quoted one, which is most of them. The count settled only when
extraction was handed to BASH — sourcing each definition exactly as
`run_sabotage_matrix.sh` does, so quoting is the shell's business.

**And the tree already ships the right instrument.**
`scripts/m6read_check_sab_anchors.py` validates all 285 anchor sites and runs
inside `make test-codegen`. It was found only after the hand-rolled one was
written and sabotage-validated. Every commit of this wave from rename 1 on
uses the repo's.

### 5.3 What is NOT rewritten, deliberately

`docs/dev/dev_journal.md`, `docs/dev/lanes/`, `docs/dev/reviews/`,
`docs/dev/decisions.md`, `docs/dev/plan.md`, `docs/dev/summaries/`,
`tests/fuzz/campaigns/`, `tools/review/out/`. They record what was measured
or ruled WHEN it was. D104's own text names the twelve by their old
spellings; rewriting a ruling's subject falsifies the record. D104 gets a
STATUS block instead, which says so.

`tools/review/out/*.tsv` are dated metric artifacts of the review; a
measurement records what it measured.

### 5.4 The emitted-byte argument, proved not asserted

Every rename target is a compiler-internal C identifier called at compile
time to BUILD emitted text, never written into an artifact. Swept `src/` and
`cli/` for STRING LITERALS containing any of the 34 names: the only true hit
in the whole population is `compile.c`'s internal-error text naming
`sb_cmt_open`/`sb_cmt_close`, which reaches `pcrec_error.msg` and no
artifact, and which no test pins. (Two apparent hits were my own line-based
regex misreading a `'"'` char literal and a quoted phrase inside a `/* */`
comment.)

What the argument does NOT cover, and it came up: the rename reaches string
literals in `tests/` too. `tests/core/sat_arith_check.c`'s failure message
names the three functions it compares, and sabotage row S254's
`SAB_DOC_FIGURE` quotes that message VERBATIM as its documented figure. It
stayed true only because the rename pass covers the check's source and the
sabotage file together. A figure that quotes a message is a reader of that
message, and it cites no symbol it does not also print — so grep for a symbol
would not have found it.

### 5.5 Readers re-aimed and DRIVEN

| reader | kind | result |
|---|---|---|
| `tests/core/run_core_tests.sh` | C unit checks | 3 checks / 0 failed (sat_arith 7 sub, sb_fragf 6, sb_stamp 6 — both counts intact) |
| `tests/codegen/run_comments_axis.sh` | axis suite | 65 / 0 |
| `tests/codegen/run_longprefix_sweep.sh` | corpus sweep | 3,939 rows vs census pin 3,939; gcc-failure-at-60 rows 0 |
| `tests/spec_mod0/check01_isolation.sh` | **name-keyed filter** | populations intact (36 symbol/TU pairs); see the red below |
| `scripts/m6read_check_sab_anchors.py` | anchor gate | 269 sabotages / 285 sites, all resolve, after every commit |
| `tools/review/function_census.py` | prose | re-aimed |
| `scripts/m6read_rename_emitted.py` | prose | re-aimed |

**The name-keyed filter is why `pcrec_default_features` got its own commit.**
`check01_isolation.sh` finds the enabled-set symbols with a REGEX ON THE NAME,
widened at STD1c specifically to catch `PCREC_DEFAULT_FEATURES` because — its
own header says so — the symbol "carries no `enabled`/`gate` substring". A
rename leaving the regex alone would have silently dropped one symbol from a
population the check ratchets a FLOOR on: `learnings.md` §3's shape exactly.

### 5.6 Sabotage rows re-driven SOLO

Nine driven, all **DETECTED**, each `bash tests/mech/run_sabotage_matrix.sh <id>`
with 1 row / 0 unexpected / 0 undetected / 0 unreached / 0 anomalies:

`S-U4-width-rule-byte-units`, `S58-mrl-minw-underreports`,
`S59-mrl-minw-overreports`, `S07-ts1-errno` (twice — its anchor spans two
commits of this wave), `S224-vm-frameless-stamp-inverted`,
`S225-vm-frameless-stamp-from-npush`, `S226-vm-frameless-stamp-conditional`,
`S185-ofsskip-resume-off-by-one`, `S200-rxt-pattern-unescaped`.

**Intent re-verified, structurally rather than by reading:** a pure identifier
substitution applied to the source AND the anchor in one pass changes the
anchor's TEXT and not the EDIT it describes. The verdicts are the evidence
that the planted defect still plants and is still caught.

**OWED: the other 24 of the 33 affected rows.** A batch of 19
(`pcrec_sb_printf`'s) was launched and then KILLED on purpose — the runner
re-reads `git archive HEAD` per row, so rows driven mid-wave measure an
intermediate tree while the merge sees the final one. Driving them against
the final tree is both cheaper and the meaningful test. The exact command is
in §7.

---

## 6. Rulings received

- **D104 extends to the whole population**, grouped by blast radius; the
  brief's re-measure instruction is what surfaced 34 rather than 29.
- **`docs/spec/match_api.md` §6 is THE abi log**; the other narrative homes
  become pointers; a CHECK is not a home — keep it, backfill from §6, say
  which way the copying goes.
- **P5's structural half is DEFERRED to v1** and was not touched.
- **The union membership is gated on measurement**, which is what declined it.

## 7. Validation — state and what is owed

**COMPLETE:** build and `make strict` green after every one of the thirteen
commits. `scripts/m6read_check_sab_anchors.py` 285/285 after every commit.
`make test-codegen` 174 checks / 0 failed, 9/10 scripts, sole FAIL the
standing darwin `nm` probe. **SIX `emit_sweep.py --ref 25b1984f` runs** —
items 1, 3 and 5, renames 1–3, and the WAVE-CLOSING run on the final tree
(which is the one that covers `pcrec_sb_printf`, `pcrec_arena_alloc` and
`pcrec_ctx_fail`) — every one **0 movers and 0 asymmetric on all five
streams** (c-default 3518, c-vm 3519, emit-ir-vm 3519, composition 33/98,
dumps 7), self-check PASSED at full reach, 261.4s for the last.

So the emitted-byte claim for the whole wave is witnessed and not only
argued: 34 renames, six full-corpus sweeps, zero moved bytes.

**OWED, with commands:**

```
# the 24 remaining re-aimed sabotage rows, against the FINAL tree
for r in S06 S123 S133 S134 S135 S148 S168 S214 S227 S255 S256 S41 S51 \
         S53 S56 S57 S64 S68 S72 S73 S74 S86 S170 S260; do
  bash tests/mech/run_sabotage_matrix.sh $r
done
# the suite
make test
```

**A RED THAT IS NOT THIS LANE'S, A/B-ed:** `tests/spec_mod0/check01_isolation.sh`
FAILS here and fails IDENTICALLY on a scratch build of `25b1984f` — "the
SPEC-M named exception (mod_modifiers.o / pcrec_feature_enabled) fired 0
time(s), expected exactly 1". Cause: darwin's `nm` prefixes every symbol with
`_`, so the loop compares `_pcrec_feature_enabled` against an `EXC_SYMBOL`
written without it and the exception arm can never fire on this box. **It is a
POSITIVE CONTROL that has been dead on the Mac since the two-machine split** —
the L8-F6 shape the coding guide names. Reported, not fixed: whether the
comparison should strip the platform prefix is a check-design ruling.

---

## 8. For the guided tour

A reader of the refactored tree should look at these four things, in order:

1. **`nm -g build/libpcrec.a | grep -v pcrec_`** and see nothing. That is the
   whole of P1, and it is the only one of this wave's items whose result is a
   single command.
2. **`src/gen/emit_dfa.c` above `.abi = %d`** — 22 lines where 449 were, and
   the 22 say where the log went and why. Then `docs/spec/match_api.md` §6,
   which says it IS the log. The pair is the shape [REVW.A1] is arguing for.
3. **`lib/pcrec.h`'s tail** — one declaration, `pcrec_limits_tsv`, with the
   reasoning for why it is a table and not thirty `#define`s. It is the
   smallest change in the wave and the one that turns eight undeclared
   constants into a readable surface.
4. **`docs/spec/tuning.md` §4** — a mirror table that now says it is
   exhaustive and names what it deliberately excludes. A table that states
   its own completeness is the difference between "not in the table" reading
   as a decision and reading as a gap.

And one thing a reader should NOT expect to find: a union mode mask in
`cli/main.c`. §2 says why.
