# substfix — the compiled-substitution build's review and D27 fixes

Lane substfix (opus, 2026-10-22), worktree `worktrees/subst`, branch
`lane/subst` (base 3ae4c57f1). Inputs: the code review
(`worktrees/.mgr/substpanel/code_review.md`), the D27 report and corpus
(`worktrees/.mgr/substd27/`, now `tests/subst/d27/`). Build go: Frank,
2026-10-21, "1,2,3 go."

## STATE AT HANDOFF

- Branch tip: the commit that adds this report (code through 4832fd53d).
  Nothing uncommitted. Not merged.
- Rulings file `docs/dev/lanes/subst_rulings.md`: header only at every
  checkpoint and at handoff; no ruling to apply.
- **The rx block (abi 84) is byte-unchanged.** I compared the base
  (3ae4c57f1, built in scratch) with the tip over 11 patterns (byte,
  utf8, latin1; named groups, `\K`, lookbehind, recursion): the `.c`/`.h`
  output and the diagnostics are identical. The UTF-8 pattern
  diagnostics (overlong, surrogate, above U+10FFFF, truncated, bad lead)
  are identical too. The codegen identity gate itself runs in 703-subst-test.
- Verified here, light, single probes:
  - `make strict` clean.
  - `bash tests/subst/run_subst_tests.sh`: 2519 passed, 0 failed. That is
    67 cells, 55 compared with pcre2 10.46, every REACH_NEED token
    carried, and the whole cell pass repeated under ASan+UBSan.
  - test-ci-shards 9/0; limits_check 37/0.
  - D27: the API drivers (8 binaries, 213 cases; TSan thread run) and
    the CLI suite (76/0) all pass. Families big, nogap and byte pass, as
    does a 26-row subset of the retagged F1-F4/F7 rows. Only PASS and
    PCREC_REFUSED outcomes, no FAIL.
  - Sabotage rows S1364-S1382 pass field validation (VALIDATE_ONLY).
- **OWED (queued, held on i2build-parity by `--ready`; the hold was
  tested with a stub state = pending, which gave rc 75):**
  - `703-subst-test`: make, make strict, perfrun make test (it includes
    test-subst and test-subst-d27), then the red-line grep.
  - `703-subst-d27`: `make test-subst-d27` alone, timed. That gives the
    real CI weight; the shard row now carries an ESTIMATED 300 s.
  - `703-subst-mech`: S1346-S1382 (37 rows; S1346-S1364 were never run).
  - Job scripts: `build/substfix/jobs/`.
- **Expected red, not mine:** `test-spec-history` fails on this branch.
  `tests/compound/CLAUDE.md:125` cites paragraph 8 of section 5 of `measures.md`, but the
  branch's `measures.md` predates that paragraph. The CLAUDE.md came over
  from main in 115585ec1; main has the paragraph. The failure resolves at
  merge. Every other line of that check passes.

## Code review (all ACCEPTED, all done)

| item | fix |
|---|---|
| MF1 | The guard is `PCREC_SUBST_GEN_<prefix verbatim>_H`. It is a stem no rx guard uses, so it cannot collide with an rx header of the same prefix. It also cannot collide with a case-only-different subst prefix (`sq`/`sQ`). The reviewer's `PCREC_GEN_SUBST_<UP>` would collide with an rx prefix `subst_x`. The one-TU check covers an rx+subst header of one prefix and `sq`+`sQ` (S1365). Case-only prefixes still share UPPER stamps; §1¶3 says so. |
| MF2 | New ns_reserved row `subst-block` (cli.md §1.6¶2). It refuses `rx_subst`, `rx_shape`, `rx_group` and `pcrec_subst`, alone or followed by `_`, on both compile paths (S1379). |
| MF3 | `<S>_NVREFS` = max(1,n) (S1366). The element gives MISMATCH when vars is NULL or nvars < nvrefs (S1374), and PCREC_ERR_UNSET_VAR for an unset var under --unset=error (S1375). §7¶5's example now uses `rx_var vres[DMY_NVREFS]`. |
| MF4 | The glue refuses a non-FRESH iterator with PCREC_ERR_ITER and leaves it as it was (S1367; the `stale` arm checks BOUND and ENDED). |
| MF5 | match_api §4 reserves −11..−16 for the subst block. |
| MF6 | `PCREC_MAX_TEMPLATE_GROUP` (65535) is now in limits.def; the manifest was re-pinned to 75. |

Review gaps, all closed:
- The agreement cells `agreedup` (`(?J)` duplicate `n` + `\k<n>`) and
  `agreepfx` (`ab`/`a` sort and prefix).
- The function family is now in the spec as subst_api §4¶8 (§R3.12
  already had it in the design).
- S1364 is now witnessed by the ASan pass.
- The untested behaviours now have arms:
  - `nogap`: the element without GAPS is compared with pcre2
    REPLACEMENT_ONLY.
  - `unk`: an unknown flag.
  - `bmis`: a run short, and ncaps 0. nseg<1 needs no arm, because
    `seg_user` is NULL-allowed when nsegs is 0.
  - `@START` cells: rx_iter_at copies the start offset (`at`,
    `atcopy`, `at1`).
  - same-prefix and colliding headers: the `tu` check.
- `(?|)` refs: pcrec refuses the pattern ("branch-reset ... not
  implemented yet"), so there is no subst cell to write; it is owed when
  that module lands.

## D27 findings

| F | disposition |
|---|---|
| F1 | Fixed. `$_` is the subject, `$_1` is the subject then "1", and `${_}` is the group `_`, all as measured on PCRE2 10.46 (S1370). |
| F2 | Implemented: `$&` (S1373), `` $` `` (S1371), `$'` (S1372). `${&}` and `$+` are refused, as PCRE2 refuses them. |
| F3 | utf8 templates take `\p{L}`/`\p{Nd}` names (S1382); byte templates refuse bytes ≥ 0x80. The source notes the rule unifies with lane/langfix's `pcrec_group_name_scan` at merge. End-to-end Unicode-name cells cannot bind on this branch (the pattern side refuses them; K116 is langfix's), so the D27 F3 rows read PCREC_REFUSED. A full cell is owed at the langfix merge. |
| F4 | A utf8 template is UTF-checked at compile (S1377). `-e` reaches the subst compile (S1381). The record carries the template's encoding, and bind refuses a mismatch (S1368; −1 means an ASCII template, which fits any rx). §9 row 13. |
| F5 | Same as MF1. |
| F6, F8 | Doc fixes (§4¶7, §6¶2). The two API cases now point at the corrected text. |
| F7 | Names cap at 128 bytes on both spellings at compile (S1376), as PCRE2's −35. |
| F9 | Every pattern-compile option is refused with `--subst` (S1380). `-e` is applied (§2¶5). `--unset=` without `--subst` is refused in both values. |
| F10 | §4¶5 states the group spans. The element also refuses a match end past `len` (S1369). |
| F11 | rx_shape_match refuses a negative number (S1378). |
| F12 | Non-FRESH: see MF4. `rx_iter_at(pos>n)` is documented in §9 row 14 (PCRE2 gives −33; the glue copies the subject). Limit 0 runs no search and so no UTF check; §6¶1 now says so. |

D27 adoption: `tests/subst/d27/` is the writer's corpus. Its provenance is in
`d27/CLAUDE.md`, and every changed line is marked `substfix`. It runs as
`make test-subst-d27` (its own section and CI shard row; not in the mech arm,
since it has ~1,500 cases). The scorer is `tests/subst/run_d27.sh`: it counts
every family's cases and fails on any FAIL, FINDING or FIXED?, then checks
the API drivers and the CLI floor. The full family run is in 703.

## Residuals (not done, by scope)

- **rx-side guard collision.** rx guards collide for case-only prefixes
  (`PCREC_GEN_<UPPER>_H`). Fixing it is an rx abi event, so it is out of
  scope here.
- **`X_subst_info` collision.** An rx prefix `X_subst` and a subst prefix
  `X` both declare `X_subst_info`.
- **Streaming must handle the new whole-subject templates.**
  `$_`/`` $` ``/`$'` read the whole subject, and replace_design §R2.6
  now says such templates refuse streaming. In the same section, the
  in-place/streaming bound is corrected to the back-reach, not LB.
- **OOM aborts** on the template path (review F-2 note).
- **The glue's batch loop copies RX_FOREACH's.** PCREC_SUBST_PAIRS, the
  64 cap and the doubling duplicate it. The unlock: give RX_FOREACH a
  limit and a k=1 fallback.
- **`-std=c99 -pedantic`** is untested.
- **`${&}` diagnostic.** It reads "a ${...} variable name must start
  ..." at offset 2. That is the wording tier (D26), so I left it.
