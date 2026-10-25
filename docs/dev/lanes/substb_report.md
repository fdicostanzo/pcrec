# substb — [M4-SUBST] phase B BUILD (lanes substb1 + substb2, opus)

Branch `lane/subst` (from 115585ec1, the R3 design head). Design of record:
`docs/design/replace_design.md` §R3. Contract: `docs/spec/subst_api.md` (new).
Build go: Frank 2026-10-21 "1,2,3 go"; the Q-F1..F4 leanings are built as R3
states them, each kept local.

## STATE AT HANDOFF (2026-10-22, substb2)

- **ABI: NO rx abi event. abi stays 84.** The rx shared block
  (`PCREC_RX_ABI_H`) is byte-unchanged. The subst block lives only in subst
  headers, under its own guard `PCREC_SUBST_H`, and `#error`s unless
  `PCREC_RX_ABI_H` equals the abi it was built for. No rx artifact moves: the
  emit path for patterns is untouched; `emit_dfa.c` only gained three exports
  (`pcrec_emit_rx_abi_block`, `pcrec_artifact_abi`, `pcrec_emit_comment_bytes`)
  wrapping existing statics.
- Commits (substb2): 5b8a3e68a src + CLI, e74be8de5 tests/subst, 5b27cb41e
  make/CI/mech wiring + cells, 027fbe5b7 sabotage files, f69f59895 spec +
  CLAUDE.md files, then this report.
- Rulings file `subst_rulings.md`: header only at every checkpoint (no
  rulings applied).
- Validation run here (light, single probes):
  - `bash tests/subst/run_subst_tests.sh`: **checks passed 729, failed 0**
    (51 cells, 25 rx + 31 subst artifacts, 42 compared with libpcre2 10.46
    `pcre2_substitute`; every REACH_NEED token reached).
  - `make strict`: clean. `make test-ci-shards`: 9/0.
  - `make test-spec-history`: one FAIL, NOT this lane's: `tests/compound/
    CLAUDE.md` cites a measures.md paragraph (section 5, paragraph 8) that exists on main but not on this
    branch's base. It resolves at merge.
  - mech `VALIDATE_ONLY`: 19 rows S1346-S1364 FIELDS OK. Hand pre-check
    (plant, rebuild, run the section, revert) on 4 rows: S1347 4 fails, S1357
    13, S1358 2, S1364 1; all detected.
- **OWED** (queued on boxqueue, owner `subst`, all after i2build-parity, which
  was already green when queued; the hold was proven to answer 75 on a
  pending key):
  - `700-subst-test`: nice make -j8, make strict, perfrun make test, red-line
    grep. Log: `worktrees/.boxqueue/done|failed/<ts>-700-subst-test/` (BQ_LOG
    and `BQ_LOG.make`).
  - `701-subst-mech`: `bash tests/mech/run_sabotage_matrix.sh S1346..S1364`
    (19 rows, all SAB_EXPECT=DETECTED).
  - `702-subst-diff`: `bash tests/subst/run_subst_tests.sh` alone (expects
    `checks failed: 0`, zero oracle SKIPs).
  - NOT built: R3.13's timing cell (dense matches, glue vs a per-match loop):
    Q-F2's trigger measurement. Owed to a timing window.
- Merge notes for the manager: this branch's lanes index lives in
  `docs/dev/lanes/CLAUDE.md` (main has moved it to the history file:
  relocate this entry); `docs/dev/plan.md` [M4-SUBST] was not touched here
  (main's row is newer).

## What was built

1. **Template compiler** (`src/parse/subst_template.c`, `pcrec_subst_parse`):
   PCRE2's non-extended grammar. Literals (backslash literal), `$n`/`${n}`
   (greedy digits, >65535 refused), `$name`/`${name}` (greedy), `$$`,
   `${!name}` (module subst-pcrec, via `src/core/varexp.c`). Operator forms
   refuse as module `subst-extended`; `$*MARK` refused. Every refusal carries
   a template offset.
2. **Per-template artifact** (`src/gen/emit_subst.c`): `<p>_render` (the
   batch element, `rx_substfn`), `<p>_subst_info` with the NEEDED shape as an
   `rx_group_entry` array (named rows, then numbered), stamps `<P>_NREFS`,
   `<P>_NSEGS`, `<P>_MAXNUM` in the .h, `<P>_SUBST_UNSET` and
   `<P>_SUBST_MODULES` in the .c only (match_api §6.3.1's rule).
3. **Generic bind**: `rx_shape_match` plus `rx_group_run` (the shared
   name -> (first, count) helper); `pcrec_subst_bind` records tag, ncaps,
   rx, sub, runs; MISMATCH / MISSING_REF with `*bad_ref`.
4. **Glue** in the subst block: `pcrec_subst(b, it, limit, out, cap, outlen,
   nsubst)`. Span validation -> BADSPAN, saturating lengths, outlen/nsubst on
   every path, six codes (-11..-16), the limit argument (never a request past
   it), batches of 1, 2, 4 .. min(64, PAIRS/ncaps) in a VLA sized from
   ncaps (no group ceiling). `PCREC_SUBST_PAIRS 256` is labelled an
   UNMEASURED default in the emitted text and the spec.
5. **CLI**: `--subst T`, `--subst-file F`, `--unset=empty|error`; `-o -`
   writes one self-contained .c.
6. **Spec**: `docs/spec/subst_api.md` (numbered from birth; named `_api`
   because the bare stem `subst` collided with old `subst §2.4` citations of
   the design doc); match_api §2¶6 (ncap's completion-producer), §3.8¶2a
   (ill-formed UTF-8, candidate C1), §3.8¶9a (the rx_iter fields shared code
   reads); cli.md §1.19.
7. **Tests**: `tests/subst/` (`make test-subst`, in TEST_SECTIONS, CI shard
   3 with an ESTIMATED weight of 10 s), mech arm `subst`, sabotage rows
   S1346-S1364 (S1365-S1385 unused, returned).

## Findings

- **F-1, ctx_init vs the design.** R3 says the shared code may read
  `it->vars` when the iterator is BOUND or ENDED. An iterator ENDED by a
  refusal before normalization can hold garbage there, so the build reads
  them only when BOUND, or FRESH with `PCREC_ITER_OPT_VARS`. Spec'd as
  match_api §3.8¶9a. S1352 guards it.
- **F-2, no Ctx on the template path.** `pcrec_subst_compile` runs outside
  `compile_driver`; Arena/StrBuf have no ctx, so OOM aborts (the K7 class).
  It is CLI-only until [IFACE-PUSH], which should route it through the
  driver.
- **F-3, `${site.group}`** is not parseable (varexp refuses `.`), though
  `rx_group_run` already takes a ref scope. A grammar addition when a
  compound caller wants it.
- **F-4, module gating.** `--features` is not consulted for `subst` /
  `subst-pcrec`, and no registry rows were added (rows would move rx stamps
  through the registry listing). File with [IFACE-PUSH].
- **F-5, cosmetic**: literal runs either side of `$$` are not coalesced; the
  emitted element uses short local names (an [M6-READ] pass may flag them).
- **F-6, differences from pcre2_substitute** are all labelled per cell
  against subst_api §9: NUL +1 on every NOSPACE length, the ill-formed-UTF-8
  row (4 vs 3), the BADSPAN corner (`[][zy]` vs -60), unknown group at bind
  (-49 there), unset (-55 there), --no-captures, the step-budget give-up.

## What a D27 blinded writer should attack next

1. Duplicate-name runs where the bsearch lands mid-run and the participating
   member is the LAST row; runs across `(?|...)` branch resets.
2. `limit` at 0, 1, k-1, k, k+1 against the glue's doubling boundary (2, 4,
   ... 64) and against ncaps above 256 (kmax = 1).
3. NOSPACE at every cap from 0 to the length, with an empty match at the
   subject end, and with a tail-only output.
4. Ill-formed UTF-8 subjects with empty matches next to the bad byte under
   GAPS and without.
5. Saturation: a template rendering a huge group many times (w near
   SIZE_MAX) on 32-bit `size_t` if a 32-bit build is available.
6. Iterators set with `rx_iter_at` mid-subject and `rx_iter_vars` with
   duplicate names, NULL values, or zero-length names.
7. Two different rx artifacts of equal ncaps through one binding (UNDEFINED
   by spec: check it is documented, not that it is detected).
8. Templates at the grammar edges: `$` at offset 0 and end, `${`  nested in
   literals, names of 32+ bytes, digits with leading zeros (`$01`).
