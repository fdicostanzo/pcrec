# famdef2 report: `\K` split into module `match-start-reset` before the first family freeze (lane famdef2, sonnet, 2026-11-10)

## STATE AT HANDOFF

**The split is built and committed on lane/famdef2; its gates are QUEUED and OWED (the full suite holds the box until
about 08:00 Wed).** The default is NOT moved and no frozen member is added (that is the next lane, after the gates).

### 1. What changed

| piece | change |
|---|---|
| FEAT bit | `FEAT_MATCH_START_RESET = 1u << 20` (`src/core/internal.h`). The feature mask is an `unsigned`: 21 of 32 bits used after, 20 before (11 free). |
| registry | `M_match_start_reset` and the `\K` row now owned by `match-start-reset` (`src/parse/registry.c`); the producer stays in `mod_assertions.c`, selected by the row's port, so no parser logic moved. `--list-syntax` row: `esc K \K match-start-reset 0x100000 ... requires module 'match-start-reset'`; `assertions` has 6 rows left (`\b \B \A \Z \z \G`), `match-start-reset` has 1. |
| named sets | `std1` never held `assertions`; `all` is derived from the registry and so holds both. No existing set name changes what it accepts. An EXPLICIT list that named `assertions` to get `\K` no longer does (spec 7.1 para 5 says so). |
| corpus | every `.rxt` block whose pattern holds `\K` and whose `features` names `assertions` now also names `match-start-reset` (135 lines in 21 files, by a block-aware script, not a blanket edit: blocks that test `assertions` gating without `\K` are untouched). The generators that write those corpora are edited to the same rule and reproduced the committed files byte for byte where they run (`tests/recursion/gen_corpus.py`, `tests/lookaround/gen_corpus.py`, `tests/recursion/d27/sr_gen.py` apart from an unrelated hand-edited `sr_depth.rxt` header, left alone). `tests/lookaround/d27/gen_refusals.py` and `tests/assertions/d27/mkcorpus.py` are edited but could not be re-run here (stale probe path / no run needed), their `.rxt` outputs were edited by the same rule. |
| scripts | `tests/assertions/run_assertions_tests.sh` (compile loop, new bare + `assertions`-only refusal rows for `\K` naming `match-start-reset`, `--no-captures` row, engine-stamp rows), `run_kreset_diff.sh` (two compile sites), `tests/codegen/run_codegen_tests.sh` (two `\K` compile sites), `tests/recursion/run_frame_buffer.sh`, `tests/reject/run_reject_tests.sh` (the `\K` gate-closed pin names the new module; coverage counts unchanged: 290 rejections), `tests/registry/registry_check.c` (witness table), `tests/endmark/gen_b3_rows.py`, `tests/revend/gen_rev_end.py`, `gen_stage2.py`, `tests/recursion/d27/sr_features.py` (lexical scanner maps `\K` to the new module; its `ALL` list names it), `tests/fuzz/fuzz.py` (`EXTENDED_FEATURES` names it). |
| compliance | `docs/pcre2_compliance.md` generated index regenerated (`compliance_section.py --write`), the `\K` annotation and the hand survey line updated; `compliance_section.py` check reads "matches the dump (144 rows)". |
| spec (D80) | `pattern_language.md` 7.1 (table, new 7.1 para 5, 8.x owner table row), `match_api.md` 3.1 para 20, `registry.md` and `cli.md` 1.17 module rosters. |
| abi | **98 -> 99** (see 2). |

### 2. abi: a bump, not "no emitted byte moves"

Under `--features all` (and under any list naming the module) the module's name joins `PCREC_FEATURE_MODULES`, which is
emitted scaffolding. This is the `ucp` precedent exactly (abi_changelog, 44 -> 45: "adding a module moves the
`--features all` scaffolding"), so I did the ritual rather than call it a value. Evidence (small run, 30 corpus rows
against the pre-split lane/famdef tip, `emit_sweep --limit 30`): every `--features all` artifact moves; the whole
difference for `a(b|c)+d` is three lines: the provenance abi digit, the `PCREC_FEATURE_MODULES` value gaining
`,match-start-reset`, and `.abi = 99`. `--emit-ir`, facts, stderr and composition streams: 0 movers except the
dumps (`--list-syntax`, `--list-families`: the `\K` row's module column and mask, declared above).
Readers found by grep for the old number: `src/gen/emit_dfa.c` (`PCREC_ARTIFACT_ABI`), `docs/spec/match_api.md` (the
`PCREC_RX_ABI_H` guard block, the field table, 6 para 17), `tests/codegen/run_codegen_tests.sh` (`ABI_EXPECT` and its
transition narrative), `tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE/AFTER re-aimed), `docs/dev/history/abi_changelog.md`
(canonical paragraph), and the identity gate's (B)/(A) pins in `tests/codegen/run_recursion_identity.sh` (self-pinned to
`2a36eb5ce0`, the lane's last src commit; the manager re-pins to the merge). Not touched, to be read from the queued
`make test`: `tests/resource/run_resource_tests.sh` byte pins (artifact sizes under `all`), if any moved.
Merge note: main may bump abi again before this lands; renumber at the merge like altcatch did.

### 3. Flag-bit budget ([IFACE-PUSH])

No `PCREC_*` option bit was added (`lib/pcrec.h` is untouched): the 64-bit `flags` word is where it was (highest bit
in use 57). The FEAT module mask is a separate `unsigned` (20 -> 21 of 32 bits). The split does not cross the hard
trigger.

### 4. Gates (all OWED; keys in `worktrees/.boxqueue`; done line = the queue's `done/` entry green, read with `scripts/verdict`)

| key | what | expected line |
|---|---|---|
| `421-main-famdef2-quoting` | quoting vs libpcre2 10.46 differential | 27,004 / 27,004 cells, 14/14 refusals, rc 0 (famdef's local figure) |
| `422-main-famdef2-named` | named-groups differential | 21,567 / 21,567, 20/20, rc 0 |
| `423-main-famdef2-fuzzext` | `fuzz.py --set extended`, seeds 1-4 x 1500 | rc 0 (any divergence exits nonzero) |
| `424-main-famdef2-test` | `make test` through perfrun on this tree | no `*** [Makefile:N: test-X] Error` line |
| `425-main-famdef2-axes` | `make test-axes` (the module bit in the axis sweep, answer identity over the corpus) | no `*** [... test-` error line |

famdef's own queued jobs (`410`-`413`, tree `worktrees/famdef`) are superseded by these (same checks, on the tree that
carries the split); cancel them when these are queued ahead.
Not queued: a full-corpus `emit_sweep` (it cannot be green across an abi bump: no abi normalisation; the small-run
evidence in 2 stands, and `make test-codegen`/`test-axes` carry the identity gates).

LOCAL results before the queue (single compiles, `nice`, PROCS 2): `make test-registry` registry_check, definitions
and compliance-index parts green after the fixes above (the registry section also runs libpcre2 PC-3 which was not
reached to its end here); `make test-assertions`: after the script edits, `run_assertions_tests.sh`, `run_gstart_diff`,
`run_mline_diff`, `run_kreset_diff` green in the second run (4/7 scripts; the three identity scripts of that run were
confounded by my abi rebuild mid-run, so they were re-run alone: see the IDENTITY line below).
IDENTITY (endvar/wordctx/gstart, re-run alone on the final build): IDENT_RESULT

### 5. Drafts for the next lane (NOT applied)

**Frozen member lists (explicit lists, never references; built-at-the-cut rule of the D37 addendum):**

- `basic1` = `classes, modifiers, quoting, named-groups, ucp, unicode-props, assertions`
- `extended1` = `basic1` + `match-start-reset, backrefs, lookaround, atomic-groups`
- `pcre2-1` = `extended1` + `recursion`

Excluded because unbuilt at the cut (stated in the announcement): `conditionals`, `branch-reset`, `verbs`, `misc`,
`comments`, `extended-classes`, `vars`, `callouts`; `code-c` is invoker-only. `unicode-props` is in `basic1` by gradthink Q2's
lean (2 of 3 rows built; `\N{U+hhhh}` stays "not implemented yet"); needs the owner's confirmation at the move.

**Default move change list** (one commit, after 421-425 are green on the merged tree): `pcrec_default_features`
`"std1"` -> `"extended"` (`src/parse/enabled.c`, with the three explicit lists above as `NamedFeatureSet` rows and the
`extended` MOVING name resolving to `extended1`); the stamp text and so abi (bump, readers by grep); spec hunks
`cli.md` 1.17, `pattern_language.md` 2.3 / 7.x default-set sentences, `match_api.md` 8.2; `reject_gated` inversions
and the corpus `features` directives that currently say `std1` or none; the bare-default reject pins in
`tests/reject`; `tests/families` differentials in the checklist run; the `docs/dev/release_checklist.md` pass;
`docs/guide/features-and-modules.md` pointer; announcement.

**K74 line for the announcement:** "Known divergence: under `-e utf8`, at the end of an ILL-FORMED subject, the
end-of-subject assertions (`$`, `\Z`, `\z`, `\B`) can answer differently from PCRE2 (K74); well-formed subjects are
unaffected."

**D37 addendum text (for main to append to decisions.md):** "Recorded 2026-11-10 (lanes famdef, famdef2): `\K` is its
own module `match-start-reset` (Frank 2026-11-06; the name describes what the caller sees, D174), split from
`assertions` BEFORE the first frozen member so no frozen member's language can lose `\K` to a later split (abi 98 -> 99,
the `ucp` precedent: a module name joining `PCREC_FEATURE_MODULES` is an abi event). Explicit lists that named
`assertions` for `\K` must now name `match-start-reset` too; `std1` and `all` are unaffected. The quoting and
named-groups differentials (`tests/families/`) and the set-alphabet fuzz (`fuzz.py --set extended`) exist."

### 6. Not done / to know

- The fixed-seed fuzz slice in `make test` (famdef's open item) is still the owner's call.
- A few docs mention `\K` under `assertions` in history text (`docs/design/assertions_design.md`, lane reports); left as
  history.
- `tests/lookaround/d27/gen_refusals.py` cannot be re-run from this tree (its probe path is stale, pre-existing).
- Sabotage rows that name `tests/assertions/kreset.rxt` as their harness target are unaffected (the corpus carries the
  module); not re-run here.
