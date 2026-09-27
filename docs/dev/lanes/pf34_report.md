# pf34 — [PATFACTS] step 3.4, "E3: the k-set walk + pin" (lane report)

Lane pf34, 2026-09-27, opus. Branch `lane/pf34` off main `02db9c1b` (abi 41,
PATFACTS 3.0-3.2, B1 and S2a merged). Charter: `docs/design/patfacts/design.md`
§9's 3.4 row and "Why 3.4 is flagged" [r1 A2], §9.1, §3, §4.2, §4.5, R14.
**Not merged.**

## 1. Pre-lane deliverable: every reader of `run_pinned` / `run_o`, and its kind gate

Design §9 (3.4 row) requires this BEFORE any `src/` edit, because the step
widens the pin's domain: today `pcrec_prefix_ksets` (hence the pin) runs only
where `unanch_start`'s prefilter kind is not `DFA_PF_NONE`
(`src/gen/emit_dfa.c:3773-3774`), so `run_pinned` is 0 on every `DFA_PF_NONE`
artifact by accident of call order. A pure NFA+window pin is TRUE on some of
those. No byte moves only if every reader carries the kind gate.

Command (tree at `02db9c1b`), then each hit classified by reading it:

    grep -rn "run_pinned\|run_o\b" src cli lib tests docs/spec \
        --include=*.c --include=*.h --include=*.def --include=*.sh \
        --include=*.py --include=*.md | grep -v "^tests/mech"

plus `tests/mech/sabotages/` separately (one hit, S280) and pcrec-bench
read-only (no hit).

| site | what it is | reads the pin? | kind gate |
|---|---|---|---|
| `src/core/internal.h:1698-1704` | `PrefixKSets.run_pinned`/`run_o`, the declaration and its comment | no (declaration) | — |
| `src/opt/prefix_k.c:40-41, 386-399` | the header prose and THE WRITER (the pin loop) | no (writer) | — |
| `src/gen/emit_dfa.c:5343-5366` `pf_run_applies_common` | the run-pinned rows' predicate: reads `o->run_pinned` (`:5350`) and `o->run_o` (`:5351`) | **yes** | **EXPLICIT**: `:5348` `if (!s->forward \|\| u->kind == DFA_PF_NONE) return false;` precedes both reads |
| `src/gen/emit_dfa.c:5393-5434` `ofs_test_of`, run branch (`:5404-5416`) | reads `o->run_o` (`:5407`) and `o->run_pinned` (`:5416`, the drift assertion) | **yes** | **TRANSITIVE**: the branch is taken only when `pf->run_term`, and `pf` is at every caller (`:5897` `dfa_cand_scan`, `:6985` `dfa_form_derive`, `:8976` `dfa_prefilter_offsets`) the row `DFA_SELECT` chose (`dfa_pf_of` or the form's own `DFA_SELECT`). `dfa_select` (`:4533-4543`) returns a row only if its `applies` is true — there is no force override on axis B — and the only two `run_term` rows (`dfa_pfs[]`, `:5788-5791`) have `applies` = `pf_run_bounded_applies`/`pf_run_applies`, both of which are `pf_run_applies_common`, which gates |
| `src/gen/emit_dfa.c:5465-5476` `ofs_test_verifies_run` | reads `o->run_pinned` (`:5468`) and `o->run_o` (`:5472`) | **yes** | **TRANSITIVE**. Two callers: `:5361`, inside `pf_run_applies_common` AFTER its explicit gate; and `:5899` `dfa_cand_scan`, on a `t` filled by `ofs_test_of` returning true, which needs `pf->emit_block != NULL` — the four offset rows only, whose `applies` are `pf_ofs_applies_common` (`:5318-5322`, `u->kind != DFA_PF_NONE` explicit) or `pf_run_applies_common` (explicit) |
| `src/gen/emit_dfa.c:334, 5410, 5446-5447, 5545-5547, 5606` | `OfsTest.run_o` — a DIFFERENT field: the selected row's own copy of the offset, written only by `ofs_test_of`'s run branch (`:5410`) | reads `OfsTest`, not the pin | inherits `ofs_test_of`'s transitive gate |
| `src/gen/emit_dfa.c:7531` `anch_start` | `memset(&o->ofsk, 0, ...)` with `kind = DFA_PF_NONE` — the anchored match-here form | no (zeroes it) | its `kind` is `NONE`, so every pin reader above declines |
| `src/gen/CLAUDE.md:3216`, `src/opt/CLAUDE.md:321`, `tests/CLAUDE.md:549`, `tests/offsetskip/CLAUDE.md:3,53`, `tests/rxtsource/run_rxtsource_tests.sh:311,384` | prose / the `run_pinned.rxt` FILE name | no | — |
| `docs/spec/tuning.md:2414` | spec prose: `-fno-req-byte` leaves `u->ofsk.run_pinned` false | no (prose; updated by this step, D80) | — |
| `tests/mech/sabotages/S280_run_pin_bytes_ignored.sh` | plants into the WRITER | no | — |
| `docs/dev/optloop/s1/probe*_patch.py` (scratch probes) | compute their OWN pin from the walk, gated `nwalk` (i.e. only where the selection ran) | own pin | not an in-tree reader |

**Verdict: every reader carries the gate — two explicitly, the rest
transitively through `dfa_select`'s `applies`. No semantic mover is waiting
in a reader.** The transitive gates are exact today but they are a property
of three call chains, not of the read. So this step moves the gate to the
READ, where the design's §4.5 obligation says it belongs: the emitter reads
the pin through ONE helper that returns "unpinned" unless the prefilter kind
is not `DFA_PF_NONE`, and every reader above calls that helper. A future
reader in `emit_dfa.c` then cannot skip the gate. A reader in another file
(S2b, not built) still brings its own, as §4.5 states.

## 2. What landed, commit by commit

| commit | what | gate |
|---|---|---|
| `f84f02e9` | §1 above, before any `src/` edit | — |
| `9d874991` c1 | **The per-offset `ppm` leaves the walk** (r1 A2 (ii)). `PrefixK` loses `ppm`; `PrefixKSets.ppm[]` is the selection's own, computed by `pcrec_find_set_ppm` at the selection's head in the walk's offset order. The walk now reads no prior | A/B c1 (§3) |
| `3ae35e94` c2 | **The WALK relocated** to `src/facts/kset.c` (`Walk`/`wpush`/`wclose`/`frontier_union` + the loop, verbatim columns) as the E3 CORE fact `kset_walk` (`facts.def` row, `KsetWalk`/`PrefixK` in `facts.h`, `pcrec_fact_kset_walk`). **E3 sealed per branch**: `pcrec_facts_seal_e3` inside the ENG_UNANCH arm only, right after `pcrec_nfa_wrap_unanchored` (`compile.c`). On a route that sealed E2 but not E3, `pf_enter` answers an E3 fact with its empty value, status `absent`, `why` = `decline:attempt-unwrapped-nfa` (a forward NFA exists: `Job.nfa.n > 0`) or `decline:no-forward-nfa`; the force loop asks E3 facts on such routes so the listing names the reason. The selection takes the walk from the memo (`PrefixKSets.walk`), so **R14 is retired**: `unanch_start`'s up-to-seven asks per compile walk once. `pcrec_prefix_ksets` drops its `nfa` parameter. The pin still in the selection here | A/B c2 |
| `4486bc94` c3 | **The PIN relocated**: `pcrec_run_pin` in `kset.c`, the E3 DERIVED fact `run_pin` (DEPENDS-ON `kset_walk req_run`), a pure NFA+window fact. `PrefixKSets` loses `run_pinned`/`run_o`. **The kind gate moved to the read** (§1's verdict): `emit_dfa.c`'s one helper `us_run_pin(cx, us)` answers unpinned unless the prefilter kind is not `DFA_PF_NONE`, and `pf_run_applies_common`, `ofs_test_of` and `ofs_test_verifies_run` (now taking the `UnanchStart`) read through it | A/B c3 |
| `88f9729d` c4 | `run_facts_checks.sh` check 8 **[facts-e3]** + **S306/S307**; re-anchors **S280** (into `kset.c`), **S188** (RE-AIMED, §5), **S281/S289** (spellings); prose fix in S285. Spec (D80): `facts_listing.md` (the E3 rows, value spellings, the two decline tokens, `absent` on unsealed routes); `tuning.md` §2.27's `-fno-req-byte` note names the `run_pin` fact. `limits.def`: `PCREC_PREFIX_K_MAX`'s description names `kset.c` (description only; `limits_check.sh` 31/0). CLAUDE.md: `src/facts`, `src/opt`, `src/gen`, `tests/codegen`, `tests/mech`, `docs/dev/lanes` | tests/docs; `limits.def` text only |

Carve-out (e) held: c1, c2 and c3 each move one thing, and each has its own
A/B run. No emitted byte was intended to move in any of them.

**`--emit-facts` rows (listing, not artifact).** Two new rows,
`kset_walk` (E3, core) and `run_pin` (E3, derived), value spellings in
`facts_listing.md`. Examples at c3: `/abcd[xy]/user` →
`47,97,98,99,100,[2],47,117,115,101,114` / `6`; `^abc` → both `absent`,
`decline:attempt-unwrapped-nfa`; `(a)\1b` → both `absent`,
`decline:no-forward-nfa`.

## 3. The zero-movers gate (per commit)

Instrument reused, not a second one: `docs/dev/optloop/s1/s1_identity.py`,
unchanged, driven by a scratch copy of pf32's `gate.sh`. BASE = main
`02db9c1b`'s build. Grid = `{-e byte, -e utf8} × {default, -fno-req-byte,
-fno-req-run, -fno-end-window, -fno-vm-anchor-bound, -fno-run-prefilter,
-fno-offset-skip, -fno-lit-run}` — design §9's widest set (3.0's row) plus
pf32's `-fno-offset-skip` plus the brief's `-fno-lit-run`; 16 runs per
commit. Each run covers pcrec-bench's 64 capability patterns × 4 configs and
every distinct corpus pattern × {`--features all`, `+ --engine=vm`}, so
`--engine=vm` is inside every run. Raw comparison, no normalization.

| commit | runs | result |
|---|---|---|
| c1 `9d874991` | 16/16 | every identity line `identical`/`refused` only; **0 changed** (byte: bench 251/5 except `-fno-lit-run` 249/7, corpus 5723/715; utf8: bench 245/11, corpus 5771/667 except `-fno-lit-run` 5755/683 — the same refusal counts base and new) |
| c2 `3ae35e94` | 16/16 | **0 changed**, same tallies |
| c3 `4486bc94` | OWED at handoff — see §8 | |

REACH: the walk accessor is asked on every ENG_UNANCH artifact whose
prefilter kind is not `DFA_PF_NONE`; the pin on every such artifact with a
run (`widen_scan.py` below: 527 distinct corpus patterns at `-e byte`
default asked the pin through a pass, 275 of them pinned).

**Mover classification (§9.1): none found in c1/c2**, of either class.

## 4. The flag: (i) the widened domain, (ii) the moved rates

**(i) Measured, not only argued.** A scratch scan (`scratchpad/widen_scan.py`,
every distinct corpus pattern, `-e byte`, `--features all`, the c3 build)
reads the `run_pin` row's value and `used` bit and the artifact's
`RX_DFA_PREFILTER`: **exactly ONE pattern has a pin that no pass asked for:
`\zabc`** (pin 0, `RX_DFA_PREFILTER "none"`, an unmatchable pattern whose
walk passes the `\z` assertion). That is the widened domain on this corpus:
one artifact, read by no consumer — the kind gate held there, and it is now
a permanent [facts-e3] witness (REACH requires it). Tally: pin derived+asked
527 (275 pinned), derived+unasked 1,633 (1 pinned), absent 701, refused 358.

**(ii)** The rates are the same function of the same sets, asked in the same
order after the same `base_ppm` ask (so the findings consumption record's
first byte-rate ask is where it was); c1's gate is the evidence.

## 5. Sabotage

| row | plant | verdict |
|---|---|---|
| **S306** (new) | the E3 seal also in the ENG_ATTEMPT arm (`compile.c`) — byte-neutral today, only the record's route claim shows it | **DETECTED**, reach ok, pop 2, `facts:1fail/7pass` (single-row mech at `88f9729d`) |
| **S307** (new) | the unsealed arm's route test inverted (`facts.c`): the two decline tokens swap | **DETECTED**, reach ok, pop 3, `facts:1fail/7pass` |
| S280 | re-anchored into `kset.c`'s `pcrec_run_pin`, plant unchanged | OWED (chain) |
| S188 | **RE-AIMED**: its site (the walk's offset 0 taking `k0`) no longer exists — the walk is a fact with no DFA set in scope. The plant now hands the selection a COPY of the walk whose offset 0 is `k0` (the one place the two sets meet), so the emitted offset-0 verify is the escape set — same defect, same observable, same detectors; the shared fact is untouched. The row's header records the re-aim | OWED (chain) |
| S281, S289 | spelling re-anchors, columns kept | OWED (chain) |

`scripts/m6read_check_sab_anchors.py`: all 330 anchor sites resolve.
**No row for `us_run_pin`'s gate, deliberately:** every reader is also gated
by `dfa_select` and by the run rows' clause 3 (`u->kind == DFA_PF_MEMCHR` or
`nsel > 0`, both impossible at `DFA_PF_NONE`), so removing the helper's
gate moves nothing — a row with no failing direction (learnings §3). The
helper exists to make the obligation hold at the read for FUTURE readers in
this file; [facts-e3]'s widened-domain witness (`used no`) is the check that
no pass asks the pin there.

## 6. Validation

| check | result |
|---|---|
| `make strict` | clean (`-Werror -Wshadow`), at c3 |
| `run_facts_checks.sh` | 8/0, [facts-e3] REACH 8 witnesses, 3 of 3 routes, 1 widened-domain pin |
| `run_offset_skip.sh` | 23/0 (at c4) |
| `run_prechecks.sh` | 301/0 (at c4) |
| `tests/registry/limits_check.sh` | 31/0 |
| sabotage anchors | 314 rows, 330 sites, all resolve |
| A/B gate c1, c2 | 0 movers (§3) |
| A/B gate c3, S1 census re-run, `make test-codegen`, `run_ir_listing.sh`, `make test-recursion-identity`, mech S306/S307/S188/S280/S281/S289, `make test CC=gcc-16` | **OWED — the detached chain, §8** |

## 7. Deviations and notes

- **The census re-run is an A/B, not a literal diff against
  `census_b_main.tsv`.** That file was taken at `4976f385` (before S1's
  build) with a probe of that tree; the probe no longer compiles on main
  (it reads `Job.req_run`, which 3.0 moved into the record) and the corpus
  has grown since, so a literal identity is impossible for reasons that are
  not this step's. The chain runs ONE re-aimed probe
  (`scratchpad/probe_pf34_patch.py`: facts through the accessors, the walk
  through a per-side macro) on BASE (main) and NEW (lane HEAD) over the
  same populations and requires the two `census_b.tsv` IDENTICAL; it also
  writes a keyed comparison of BASE against `census_b_main.tsv`
  (`scratchpad/census_vs_main.txt`) so the drift since `4976f385` is
  visible and attributable. The probe computes its OWN pin from the walk,
  so it shares no source with the fact it checks.
- **The decline reason is read off the machine** (`Job.nfa.n > 0`), not off
  `Job.engine`: the fact layer reads the IR it is declared to read.
- **No stamp moved; no abi event.** The only caller-observable changes are
  the listing's two rows and two tokens (spec hunk) and one `--list-limits`
  description.

## 8. STATE AT HANDOFF

Everything above is committed on `lane/pf34` (HEAD at handoff: see `git log`).
One detached chain runs every remaining heavy stage serially:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/pf34/scratchpad/chain.sh`,
log `scratchpad/chain.log`, one `PF34 CHAIN:` line per stage, last line
`PF34 CHAIN: ALL DONE`. It first waits for gate c3
(`scratchpad/gate_c3.log`, completion line `GATE c3 DONE`).

| stage | log | how to read the verdict |
|---|---|---|
| A/B gate c3 | `gate_c3.log` | 32 `identity:` lines; `grep -c changed` must be 0. A nonzero count is a mover: classify per §9.1 before anything else (SEMANTIC = stop, K-row) |
| census BASE vs NEW | `census_base/`, `census_new/`, `census_{base,new}.log` | chain line `census IDENTICAL base vs new`; anything else is a finding |
| census vs `census_b_main.tsv` | `census_vs_main.txt` | informational: drift since `4976f385`, keyed by (pop, id, cfg) |
| `make test-codegen` | `codegen.log` | the one accepted red is `FAIL: nm could not read arm_a.o (no rx_search symbol)`; any other `FAIL:` is real |
| `run_ir_listing.sh` | `irlisting.log` | rc 0 |
| `make test-recursion-identity` | `recid.log` | rc 0; its (B) pin must NOT move (no abi event here) |
| mech S306 S307 S188 S280 S281 S289 | `mech_S*.log` | each `mech run COMPLETE ... (unexpected: 0, ...)` and the row's verdict DETECTED |
| `make test CC=gcc-16` | `make_test.log` | make's `*** [test-X] Error` lines are the verdict (none = green); darwin-known reds: A/B against a scratch build of `02db9c1b` before claiming one |
