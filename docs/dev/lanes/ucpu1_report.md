# ucpu1 — [UCP] U0 + U1 delivery report

Lane `ucpu1` (opus, feature tier), branch `lane/ucpu1`, from main `cd2c681b`
(2026-09-28). Charter: `docs/design/ucp_design.md` §6's U0 and U1 rows, as
ruled by D130 (Q1–Q9 all YES). Commits: U0 `42a85627`, then U1 (WIP
`6a96fc6e` + the closing commit(s) on the branch).

## 1. What landed, per stage

### U0 (`42a85627`)

- **Registry**: three `(*` name rows owned by NEW module `ucp`
  (`FEAT_UCP`, bit 18): `(*UCP)` (unbuilt at U0: "(*UCP) requires module
  'ucp'"), `(*UTF)` and `(*UTF8)` (a live synonym on 10.46/10.48). They are
  RF_INDEX name rows on the alpha-lookaround rows' own mechanism
  (`pcrec_registry_verb_name_row`); `(*UCP)` no longer answers "requires
  module 'verbs'" (O-71: the wrong OWNER, D26's exact tier).
- **`(*UTF)`/`(*UTF8)`**: accepted as a restatement when the encoding's
  universe is Unicode (asked of `PcrecEnc.max_cp`, never the encoding's id);
  refused BY NAME under `byte` at every gate state ("(*UTF) requires
  --encoding=utf8" — an RD_FIXED capability sentence, not a module promise).
- **The start-of-pattern OPTION RUN**: `Ctx.optrun_end` replaces
  mod_verbs.c's `at == 0` rule (the comment there always said the general
  prefix-run rule would replace it the day a verb was accepted), so
  `(*UTF)(*UCP)` combines in either order.
- **O-71**: `PcrecEnc.implied_features` (utf8: `unicode-props | ucp`) OR'd into
  the compile's feature MASK only; `PCREC_FEATURE_SET/MODULES` keep stamping
  the REQUESTED set, so no artifact moves (Q-C to the manager).
- **SEM-1**: the `parse.c` fold comments (both sites) corrected in both
  halves.
- The bare-name module refusal renders without `:...` (only GROUPARG names
  carry it).

### U1

- **The surface**: `--ucp` (`PCREC_UCP`, bit 34, reflected in
  `rx_info.flags` unmasked), `(*UCP)` (port sets `ParseMods.ucp`), `.rxt`
  `flags u` in all three readers (`run.sh`, `verify_rxt.py`,
  `rxt_source.c` + `pcrec_rxt_flags_from_letters`). `--ucp` with module
  `ucp` off is refused by name.
- **T1 = the definitions table**: `DEF_UCP` split into `DEF_UCP_{D,S,W,P,T}`
  (predicate UCP ∧ ¬restriction; `_T` is ¬aP ∧ ¬aT). New `DefKind`
  **DEFK_SET** + trailing `RegDef.set` (a `PcrecSetDef`: a union of
  unicode-props bare-namespace spans and ranges, optionally complemented,
  with a `fold_inert` marker). Entries on `\d \D \s \S \w \W` and on the
  POSIX row per NAME (13 names; `[:ascii:]` unchanged), plus a DEFK_STR
  `DEF_UCP_W` entry on `\b`/`\B` (the lookaround spelling over `\p{Xwd}`).
  ext.c's PORT_SET branch and mod_classes.c's POSIX port RESOLVE the row
  (new `pcrec_def_resolve_operand` for the per-name POSIX walk) and build a
  DEFK_SET entry through the ONE producer, `pcrec_setdef_class`
  (mod_ucp.c); every other resolution is the port's own byte table (== the
  DEF_ALWAYS entry). U1 is the table's first wiring customer, for SET-valued
  entries only.
- **The route table** (mod_ucp.c, first-match rows as data): `narrow` —
  clamped set ≤ `PCREC_UCP_NARROW_MAX_INTERVALS` (new limits.def row, 128,
  limits.md §3.8) → build; `wide` → refuse by name (D130 Q3). The measured
  rule reproduces exactly the ruled list: largest narrow `\p{Nd}` 71
  intervals, narrowest wide `[:punct:]` 193. Under `byte` every set clamps
  narrow.
- **T2 = the fold table** (parse.c `fold_rows`, first-match, rows as data):
  `none` / `property` / `inert` / `ascii-named` / `latin1` / `encoding`. It
  replaced the per-caller fold argument at `char_node`, `p_class`'s own
  members, `pcrec_ast_class_from_bits` and `pcrec_ast_class_from_iv` (one
  constructor, `pcrec_ast_class_from_cpset`, allocation order preserved).
  One row beyond the design's five: `property` (a `\p` set is never folded —
  unicode-props chose its caseless span), which is today's behaviour made a
  row rather than a special case at `from_iv`.
- **The (encoding, UCP) fold**: new `pcrec_fold_latin1` (fold.c), DERIVED
  from the Unicode simple-fold link table restricted to Latin-1.
- **`(?a…)` real**: `ParseMods.arestrict` (scoped; `(?a)` all five, `(?-a)`
  all, `(?-aX)` one; SURVIVES `(?^)` — measured on 10.48, `(?aD)(?^)\d`
  stays ASCII).
- **Refused by name at U1**: the wide UCP sets under `-e utf8` (both
  polarities, atom or class, `(*UCP)` or `flags u`), and UCP `\b`/`\B` under
  BOTH encodings (Q-B to the manager: the design's §6 puts the byte tier's
  UCP `\b` in U2, which conflicts with D130's "whole byte tier at U1"; I
  took the design's staging — it needs §2.4's per-machine word set).
  `(?aW)`/`(?aP)` make a refused construct ASCII again and it compiles.

## 2. Tables added (§0.1's rule), with their rows

| table | where | rows (name — predicate) |
|---|---|---|
| T1 (definitions) | registry.c RegDef lists | `ucp` (DEF_UCP_x: UCP ∧ family unrestricted) — `ascii` (DEF_ALWAYS) |
| T2 (class fold) | parse.c `fold_rows` | none — `(?i)` off; property — a `\p` set; inert — fold-inert UCP set; ascii-named — named/ASCII-restricted byte set; latin1 — UCP under a one-byte encoding; encoding — always |
| U1 route | mod_ucp.c `route_rows` | narrow — clamped intervals ≤ 128; wide — always (refuse) |

No row carries a deny flag: every one changes answers (D125's structurally
ineligible kind), which the tables' own comments state.

## 3. Checks and numbers

- **Oracle, corpus** (`tests/ucp/*.rxt`, 120 blocks, 1,563 harness cases):
  generated from libpcre2 10.48, **re-verified on 10.46: 1,540 / 1,540
  agree** (23 perr blocks are pcrec's own refusals) —
  `docs/dev/lanes/ucpu1_evidence/verify_10.46.txt`. `verify_ucp.py`
  re-checks every cell on every `make test-ucp` (local 10.48: 1,540 / 0).
- **Oracle store** (D130 Q9): `OracleId.config` gains `ucp` (store format
  1 → 2; the three committed files re-headered, answers untouched, every
  hash recomputes identically); new `oracle_store/libpcre2-10.46-ucp/
  membership.tsv`, **46 cells** captured over one light ssh session.
- **UCP sets vs the store** (`ucp_compare.py`): **23 sets compared EXACT
  (16 byte + 7 narrow utf8), 9 wide utf8 refused by name with
  construct == spelling in the store; 42 checks, 0 failed.**
- **The byte-tier fold** (`latin1_fold_check.c`): pcrec_fold_latin1 ==
  10.46 UCP|CASELESS over all 256×256 byte pairs (112 partner pairs);
  controls: the ASCII fold reads 60 disagreements, the utf8 fold 10.
- **Definitions structural tie**: every DEFK_SET `str`, parsed by the real
  parser under `-e utf8`, equals the producer's set (19 entries, negated
  rows complemented) — `tests/registry/definitions_check.c`.
- **Identity gate** (4,061 corpus blocks, base `cd2c681b` binary vs this
  branch, same `-o` basename, `.c` and `.h`): **3,593 byte-identical, 465
  both-refuse with identical text, 3 verdict moves** — the three
  `^\p{L}$` `-e utf8` blocks in `tests/utf8/axis10_surrogate_witness.rxt`
  that O-71 turned from refused into compiling (promoted in U0, cases from
  their own oracle-annotated header lines). Same result at U0 and U1: **every
  UCP-free artifact is byte-identical**. With every block forced to
  `--features all`: only `PCREC_FEATURE_MODULES` gains `,ucp` (Q-A). With
  every block forced to `-e utf8`: 3,604 identical; the only movers are `\p`
  patterns (7 verdict, 34 refusal-text), all O-71.
- **Sabotage rows** (numbered from main's highest, S332; one id per
  `run_sabotage_matrix.sh` invocation): **S333** `(*UCP)` answering `verbs`
  again — DETECTED (reach ok, reject 3 fail / 642 pass); **S334** DEF_UCP_D
  true without UCP — DETECTED (reach ok, harness tests/ucp 4 fail / 1,559);
  **S335** `[:lower:]` folding under `(?i)` UCP — DETECTED (reach ok,
  tests/ucp/byte.rxt 9 fail / 750); **S336** `(?aW)` not reaching `\b` —
  DETECTED (reach ok, tests/ucp/knobs.rxt 29 fail / 240).
- **Re-aimed anchors** (the change moved their source text; intent
  unchanged, each row's own file says what moved): S08, S09, S-U1 (p_class /
  char_node fold now `cls_fold(..., CLS_LITERAL)`), S24 (the a-sub-letter
  consume), S26 (the set/unset block gained the arestrict lines), S29
  (`at != cx->optrun_end`). `scripts/m6read_check_sab_anchors.py`: 337 rows,
  0 stale. Their DETECTED re-verification is OWED (§5).
- **Pre-existing defect found and fixed**: `tests/reject/run_reject_tests.sh`'s
  COVERAGE guard was DEAD on this box — the [VAR] message reintroduced
  backticks and `${...}` text that fail inside the echo, and a mismatched
  run exited 0 (measured). Every `$`/backtick in the message is now inert;
  the guard fires and exits 1 (measured both ways).

## 4. Spec hunks (D80)

`cli.md` (`--ucp`; `-e utf8` implies modules; `(*UTF)`; the module table's
`ucp` row, 18 modules), `limits.md` §3.8, `tuning.md` §4 (PCREC_UCP in the
not-a-tuning-axis list), `rxt_format.md` (`flags u`), `match_api.md` (§8.2's
reflection paragraph: bit 34, unmasked, no abi event), `registry.md` (module
list), `docs/pcre2_compliance.md` (survey rows + regenerated index).

## 5. Validation run by the lane, and what is OWED

Run and green on the branch (darwin, gcc-16): `make strict`;
`test-registry`, `test-reject`, `test-cli`, `test-definitions`,
`test-uprops`, `test-rxtsource` (census re-pinned 252/4181/30967, RUNSH
228/4181/30967, C3 SKIP/own-oracle +1,563, ARM_PIN re-pinned for the `flags`
arm body), `test-ucp`, `bash tests/harness/run.sh tests/ucp` (1,563/0) and
`tests/utf8/axis10_surrogate_witness.rxt` (27/0). `test-codegen`: green but
for `run_inline_capability.sh`'s "nm could not read arm_a.o", which the base
binary reproduces identically (the known darwin red).

**OWED — one detached chain, launched as the lane's last act** (log:
`/tmp/ucpu1s/final_chain.log`, detached with nohup + caffeinate):
1. `bash tests/mech/run_sabotage_matrix.sh` for each RE-AIMED row, one id
   per invocation: S08, S09, S-U1, S24, S26, S29 — each must read
   `DETECTED` (completion line per row: `== mech run COMPLETE: 1 rows ...`).
2. `make test CC=gcc-16` — the full suite, completion line
   `sections ran: 45/45` plus the `RUN-STAMP:` line; the verdict is make's
   `*** [test-X] Error` lines (a darwin `test-codegen` red from
   inline_capability is pre-existing). The chain prints `FINAL_CHAIN_DONE`
   last.

Deferred / not in this lane: plan.md's [UCP] row and the journal (the
manager's); the D27-blinded corpus for UCP (none chartered); U2–U4.
Side finding, filed as **K72** (`docs/dev/known_issues.md`, lane ucpu1b,
not fixed): pcrec's `\h`/`\v` under `-e utf8` are the byte sets (`\h` does
not match U+3000; PCRE2_UTF's `\h` does, confirmed by a light ssh probe
against libpcre2 10.46 — `docs/dev/lanes/ucpu1_evidence/probe_hv.py` +
`probe_hv_10.46.txt`) — a pre-existing divergence from PCRE2 independent
of UCP (`h_def`/`v_def`, `src/parse/registry.c`, are fixed `DEF_ALWAYS`
strings never widened); UCP `[:blank:]` is built from the Unicode `\h`
list directly, so it is right.

## 6. Questions sent to the manager (Q-A..Q-D), with the defaults taken

- **Q-A** abi: **RULED (lane ucpu1b, 2026-09-29): bump taken, 44 -> 45.**
  The lane's own default ("no bump — rx_info's layout is unchanged, no
  UCP-free artifact moves") is overridden: adding module `ucp` changes
  the `--features all` `PCREC_FEATURE_MODULES` stamp regardless of
  whether the requesting build ever asked for the module, which is
  emitted SCAFFOLDING and by D76/D94 plus the `vars` precedent
  (`d755a944`, abi 31 -> 32, the landing that added `,vars` to the same
  stamp) is an `abi` event on its own. Full D94 ritual applied (the
  constant, `docs/dev/history/abi_changelog.md` entry, `tests/
  codegen/run_codegen_tests.sh`'s `ABI_EXPECT`/failure-message copy,
  `run_recursion_identity.sh`'s FILEPIN self-pinned to `a6e367a7`).
  Identity result restated: **UCP-free artifacts are byte-identical
  except the abi digit (a same-length 44->45 substitution — 0 net
  bytes) and the `--features all` module stamp** (`,ucp`, +4 bytes,
  present only under `--features all`, present on every artifact —
  UCP-bearing or not — compiled that way). See
  `docs/dev/lanes/ucpu1b_report.md` for the triage/ritual/validation
  record.
- **Q-B** UCP `\b` under `byte`: refused at U1 (design §6 staging).
- **Q-C** implied modules: mask only; stamps keep the requested set.
- **Q-D** spellings: `flags u`; `(*UTF8)` ≡ `(*UTF)`; UTF rows owned by
  module `ucp` with an RD_FIXED capability sentence; the wide predicate as a
  limits.def row.
