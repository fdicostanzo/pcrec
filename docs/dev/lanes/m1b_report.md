# m1b — [MEMFN] R-5 / M1b: runcmp migrates into the kit, zero movers

Lane m1b (opus), 2026-10-07, branch `lane/m1b` cut from the kit branch
`lane/memfn-m1b` (main 993f8c1d + the R-4 `done:` response, aa7b82b1).
Charter: the kit manager's brief (rulings Q-M1b-1..8), R-5 in
`memfn/docs/requests.md`, the scope pass
`worktrees/m1bscope-scratch/m1b_scope.md` (written at 54c42e36; every
file:line below is re-derived on THIS tip), integration.md §R4.7, §R4.6,
§14, §15, §18, §22.

## 1. Summary (resume from here)

- **No STOP.** No emitted byte moved anywhere I could measure (§5), no start
  decision moved (§3), no pcrec abi event. All 8 rulings applied as ruled.
- **Commits** (shas in the handback; see `git log 993f8c1d..lane/m1b`):
  0 CONTRACT (integration.md rev 4.8), 1 IMPLEMENT (kit runcmp arm + I1),
  2 REPLACE (callers switched, `src/gen/runcmp.c` deleted, checks/mech),
  then docs/spec/CLAUDE.md + the Linux wrapper, then this report.
- **Mech:** 7 rows re-anchored (S267 S443 S444 S445 S285 kit-side in
  `memfn/src/runcmp.c`; S279 S454 in `memfn/src/ofsskip.c`), 3 adjacent
  verified unchanged (S514 S516 S528), 4 new (S570-S573). Every re-anchored
  and new row hand-planted (§4). [SABANCHOR]: 486 rows, all anchors resolve.
- **OWED:** the Linux verdict, `docs/design/memfn/probes/lxrun/memfn_m1b.sh`
  (§6); the Mac `make test` slot (the manager's); the kit journal +
  `responses.md` `done:` (the kit session's files).

## 2. Per-commit contents

### Commit 0 — CONTRACT (`docs/design/memfn/integration.md` rev 4.8)

- New top-level §R4.8: the by-id table of Q-M1b-1..8 and where each lives,
  what changed (§R4.8.1), the three standing questions (§R4.8.2).
- §14.8 CORRECTED in place (`[rev4.8]`): pcrec's `stamp` op quotes, so
  RUN_WORDS through it would read `"0"` on every artifact; the kit writes
  it through the new unquoted `stamp_int`, first of THREE lines, and pcrec
  calls `mf_stamps` from its finishing pass (not "at the two old points").
- §14.0 note: `MF_SITE_ABI` 4 (`stamp_int` appended last; `run_cmp`
  retired; `note` no longer carries helpers; denies asserted equal).
- §14.10 bit 43 row, §15.6 (`empty` EXCLUDED, `use` DISCARD), §22 M1b row.
- `docs/design/memfn/CLAUDE.md`, `memfn/CLAUDE.md`: rev 4.8 pointers.
- The memfn.h contract comments landed with the code (commit 1/2), since
  the header is code.

### Commit 1 — IMPLEMENT (pcrec still renders; zero movers)

Kit:
- `memfn/src/runcmp.c` (NEW, SPDX 0BSD + `Provenance: pcrec 993f8c1d …
  src/gen/runcmp.c …`, PROVENANCE.md row): the four rows (`words`,
  `overlap` denied by `MF_D_RUN_OVERLAP`; `bytes`, `memcmp` fallbacks),
  their writers transcribed (sink in place of StrBuf; `c->cstr` for
  literals), `run_cmp_render` (one compare; records `wused`, counts
  `words`, sets `MF_INC_STRING_H` for words/memcmp), `run_cmp_prepare`
  (a FUNC definition's per-RUN-term "record width, flush ALL pending" —
  pcrec_runcmp_prepare's exact semantics), `mf_flush_helpers` (moved here
  from compose.c; comment via `cmt_open(MF_CMT_NONESSENTIAL)`, loads, blank
  line, idempotent by bitmask), `mf_run_rows(i)` (Q-M1b-3 accessor), and
  `runcmp_arm` (VERIFY/EXPR/BOOL, `guard_by_caller`, one RUN term, every
  byte inside its mask; base `<s> + <lo>`, offset the term's). D149: the
  overlap lengths and the width rule are labelled DERIVED with the study.
- `kit.h`: `mf_art.words/wused/wemitted`; the runcmp internals.
- `compose.c`: `runcmp_arm` in the table above generic; `mf_define` refuses
  `site.denies != art.denies` (Q-M1b-1); `mf_stamps` writes RUN_WORDS via
  `stamp_int` first.
- `memfn.h`: `MF_SITE_ABI 4`, `mf_sink.stamp_int` appended LAST,
  `MF_CMT_NONESSENTIAL` (CHOSEN: the tier a hook-less kit comment opens;
  pcrec `_Static_assert`s it equals `PCREC_CMT_NONESSENTIAL`), `cstr`
  stated as a literal's BODY (CHOSEN — see §7 F1), `mf_run_row` +
  `mf_run_rows`, three-stamp and denies comments. `run_cmp` kept for this
  commit only (dual protocol: the kit's own compare where it is NULL).
- `ofsskip.c`/`precheck.c`: `ofs_fn_applies` no longer needs `run_cmp`
  (needs `run_cmp_sat` instead); verify chain and define take the new
  protocol where `run_cmp` is NULL.
- G2 (`memfn/tests/g2/g2_gen.c`): `sk_stamp_int` appended to the positional
  sink; `sk_cstr` writes the body only; one `denies` per batch art (every
  third batch `MF_D_RUN_OVERLAP`; the per-site draw kept so the random
  stream does not move); a refusal case `denies-not-the-art's`.
pcrec:
- `memfn_sites.c`: THE DENY MAP (`deny_map`, `pcrec_memfn_denies`,
  `pcrec_memfn_deny_flags`) filling every site's `denies` and
  `mf_art_begin`; the I1 shadow comparator (a SHADOW art per attempt,
  `Job.mf_i1`): each define's whole span re-rendered through the new
  protocol and compared byte for byte (muted bytes included), each VM
  literal-run compare (a VMRUN site through `mf_emit`, plus C10's
  `deleg_check`/`check_use`), the prologue's helper flush, and the
  RUN_WORDS line against the shadow `mf_stamps`' first line.
- DELEG_SITES row `VMRUN` (`MF_OP_VERIFY`, `DELEG_H(MF_H_BOOL)`,
  `MF_TK_RUN`, `DELEG_LOOP`, ceiling `MF_USE_DISCARD`), so the I1 site is
  the REPLACE site; `vm_run_site`/`vm_run_compare` in `emit_vm.c`.
- `memfn_stamps.c`: the real pass's `stamp_int` held back (pcrec still
  wrote RUN_WORDS) — replaced at REPLACE.

### Commit 2 — REPLACE (zero movers)

- Kit: `run_cmp` member deleted, `note`'s helper role ended (comment says
  so), the dual-protocol branches deleted; `pidx` left the offset-skip
  function's internals (no hook takes a term id any more) — S454 re-anchor.
- pcrec: `src/gen/runcmp.c` DELETED; `internal.h` loses `Job.rc_*`,
  `mf_i1`, `PcrecRun`, `PcrecRunRow`, the rows and the five runcmp
  declarations; `memfn_sites.c` loses I1, `run_of`, `pred_at`,
  `pcrec_memfn_note_helpers`, `pcrec_memfn_run_cmp`, gains the door
  `pcrec_memfn_emit` (→ `mf_emit`, no file-scope sink) and
  `pcrec_memfn_flush_helpers`; `emit_dfa.c`: the two hook initializers
  lose `.note`/`.run_cmp`, the prologue calls `pcrec_memfn_flush_helpers`,
  the RUN_WORDS call is deleted (the mark is where the line was);
  `emit_vm.c`: `vm_run_compare` → the door (per-instance `check_use`), the
  RUN_WORDS call deleted; `memfn_stamps.c`: real `stamp_int`
  (`pcrec_sb_stampf "%lld"`); `axes_dump.c`: run-overlap rows read
  `mf_run_rows` + `pcrec_memfn_deny_flags`; `axes.def` comment.
- Checks: manifest VERIFY (emitters `ofs_site_define,req_site_define`,
  companions `ofs_pred_of,pcrec_memfn_term_run`) and VMRUN (emitters
  `vm_run_site,vm_run_compare`, companions `vm_lit,vm_isl_emit`) →
  `delegated` (rows stay 13, delegated 3 → 5); C12 drops runcmp.c's three
  rows, `C12_CEIL_ROWS_FLOOR` 12 → 9, header "(9) … (13 forms"; 
  `site_census.DOORS` + `pcrec_memfn_emit`; C5: the fixtures' stand-in
  `run_cmp` gone, a `cstr` op, each fixture's art flushes helpers into
  `def`, six new runcmp fixtures (overlap L3, overlap L13 with escapes,
  memcmp L8, masked words, masked denied → bytes, exact denied → memcmp);
  4 run-bearing def pins moved (ofs-pair, ofs-run-pinned,
  pre-masked-whole-rest, pre-window-handoff), 12 new rows, 28 total;
  `ARMS_ROW_FLOOR` 16 → 28, `ARMS_EXPECTED` + `runcmp`.
- Mech: §4.
- Docs (D80): nothing a caller observes changed (no stamp value, spelling,
  type or position; `--list-axes` byte-identical). Two CURRENT-STATE spec
  sentences named the deleted internals and were updated:
  `docs/spec/tuning.md` §2.38 ("written by ONE renderer … the kit's run
  compare … `MF_D_RUN_OVERLAP`") and `docs/spec/match_api.md` §6.3's
  RUN_WORDS entry (the kit writes the line, first of three, still an
  unquoted integer). The dated abi change-log entries (abi 58, 63) are
  history and were left as written.
- CLAUDE.md: `src/gen`, `memfn/src`, `memfn/tests`, `tests/memfn`,
  `tests/mech`, `tests/codegen`, `tests/litscan`, `probes/lxrun`.

## 3. THE BOUNDARY: D1-D12 restated at this tip

No start-decision line was edited (`git diff 993f8c1d -- src/gen/emit_dfa.c
src/gen/emit_vm.c` touches only comments, the two hook initializers, the
prologue's flush call, the two RUN_WORDS calls, and the VM run-compare
calls). `src/gen/emit_dfa.c` unless named:

| # | file:line (this tip) | read |
|---|---|---|
| D1 | 1409 (`req_site_define`, 1402) | `pcrec_fact_req_byte`, `pcrec_fact_req_run(cx)->len < 2`: no site |
| D2 | 1410 | `req_admit_emits(req_admit(cx))` |
| D3 | 1411 | `req_run->len >= 2`: run form vs one-byte |
| D4 | 1412-1414 | `req_lead_byte(cx)`; `pcrec_artifact_has_dfa_scan` → the lead's need |
| D5 | 1417; B5′ 1526 (`pcrec_emit_req_byte_check`) | `req_use(cx) == REQ_USE_HANDOFF` |
| D6 | 1043 (`req_run_tests`, 1029), 1290 (`req_set_rest_members`, 1283) | `pcrec_artifact_has_dfa_scan` |
| D7 | 9704-9706 (`pcrec_emit_prologue`, 9693) | `dfa_body && (UNANCH \|\| (ATTEMPT && attempt_cand && use_memchr))` → `<string.h>` |
| D8 | 9716-9717 | `req_admit(cx)` → `<string.h>` |
| D9 | 9727 (`body_memcmp`, from emit_vm.c 14056 `v.nlitrun > 0`) | the VM literal runs' `<string.h>`; `pcrec_memfn_art_end` still asserts `mf_includes ⊆ string_h` |
| D10 | 6146 (`ofs_site_define`) | none in the function (the hooks initializer at 6157-6160 lost `.note`/`.run_cmp`) |
| D11 | emit_vm.c 4538 (`vm_isl_emit`, 4446), 8683 (`vm_lit`, 8678) | the P8 bounds guard `scan_position + N <= subject_length`, pcrec's text before the kit's EXPR |
| D12 | emit_vm.c 4458-4461 (`inrun[]`, bit 33), 8722/8728 (`vm_cat`: `vm_lit_run`, `vm_lit`) | whether a run is fused at all: pcrec's |

The edited lines nearest a decision: `req_site_define`'s hooks initializer
(1453-1456, now one line shorter), the prologue flush at 9955 (~250 lines
below D7/D8), `ofs_site_define`'s initializer. [START-TABLE] C1 re-derives
its trace sites on a main containing this.

## 4. Mech rows

| row | was | now | plant evidence (hand-planted, built, run) |
|---|---|---|---|
| S267 | runcmp.c `pcrec_sb_puts(c, "!memcmp(")` | kit runcmp.c `c->puts(c->u, "!memcmp(")` | `a=b` (-fno-offset-skip -fno-run-overlap): `if (memcmp(subject + cand, "a=b", 3))`; "xxa=bxx" clean `match 2 5` → nomatch |
| S443 | runcmp.c `int at = …` | kit, VERBATIM anchor, SAB_FILE only | `xyz(a\|ab)c` VM: last word `rx_w2(… + 2) == rx_w2("z\000")`; "xyzac" → nomatch |
| S444 | same | same | first word twice (last byte unchecked); "xyQac" under -fno-req-byte: clean nomatch → `match 0 5` (false match) |
| S445 | `pcrec_sb_printf(c, ") == %s_w%d(\"" …` | `kit_out(c, ") == …` | `!=` both words; "xyzac" → nomatch |
| S279 | ofsskip.c `h->run_cmp(…, t->offset,` | ofsskip.c `if (run_cmp_render(art, t, "subject + cand", t->offset, o))` | `/user\|/users`: `rx_w4(subject + cand + 1) == rx_w4("/use") …`; "GET /users" clean `match 4 9` → nomatch |
| S285 | memfn_sites.c `PcrecRun run = …` (`run_of`) | kit runcmp.c `rc_run r = { t->run, t->mask, (int)t->run_len };` (Q-M1b-4: the renderer's one read of run_len) | `/user\|/users`: second word `rx_w4("ser\000")`; "GET /users" → nomatch |
| S454 | `pair_body(art, h, p, pidx, …)` | `pair_body(art, h, p, maxk, …)` (pidx removed) | `(?i)select`: one memchr stream; "x select" clean `match 2 8` → nomatch |
| S514, S516, S528 | — | anchors unchanged, resolve (S516 gained a note: VM artifacts now lose all three kit lines) | not re-planted (anchor text untouched) |
| **S570** NEW | — | kit `rc_row_of` ignores the deny | runcmp_check.py: 80 passed / **18 failed** ("-fno-run-overlap: a word compare … survives the deny") |
| **S571** NEW | — | pcrec `deny_map` maps bit 43 to 0 | runcmp_check.py: 80 / **18 failed** (same lines) |
| **S572** NEW | — | prologue flush deleted | runcmp_check.py: 74 / **24 failed** (island: helper after first use; does not compile under -Werror) |
| **S573** NEW | — | `art->words += 2` | runcmp_check.py: 80 / **18 failed** ("RX_RUN_WORDS reads 2, the text carries 1") |

Clean runcmp_check.py: 98 passed, 0 failed. Every row's SAB_REACH run on
the clean tree prints its expected token; `VALIDATE_ONLY=1` reads FIELDS
OK for all 14. **Count: 7 re-anchored (5 kit runcmp.c, 2 kit ofsskip.c;
S454 is beyond the brief's six, forced by the `pidx` removal), 3 adjacent
verified, 4 new (S570-S573 of the issued S570-S579 block).** Detector runs
of the full rows (the matrix) are OWED to the Linux script.

## 5. Validation (Mac, light)

Run (all on this worktree's tip, Mac, gcc-16):

| check | result |
|---|---|
| `make` / `make strict` | clean, at IMPLEMENT and at REPLACE |
| I1 sweep at IMPLEMENT (`build/m1bscratch/i1sweep.py`: ref binary at 993f8c1d vs the IMPLEMENT binary, every unique `.rxt` corpus pattern, 3598, × 10 flag sets: default, `--engine=vm`, `-fno-run-overlap`, `-fcomments`, `-fcomments --engine=vm -fno-run-overlap`, `-fno-lit-run`, `-fno-alt-island`, `-e utf8`, `-fno-offset-skip`, `-fno-req-run-fold`, all on `--features all`) | 35,980 compiles, 32,250 ok: **0 I1 internal errors, 0 movers (.c+.h sha), 0 asymmetric refusals** |
| the same sweep at the REPLACE tip | **0 movers, 0 asymmetric, 0 internal errors** |
| I1 sensitivity (hand plants at IMPLEMENT) | a shifted word, an extra comment byte, a RUN_WORDS off by one: each refused by its I1 comparison (VM compare, define span, helper flush at both tiers, RUN_WORDS line) |
| `--list-axes`, `--list-limits`, `--list-syntax` vs 993f8c1d | byte-identical |
| smoke (25 run-bearing patterns × 14 flag sets, both engines) | 350 compiles, 0 differ, 0 rc mismatches |
| `tests/codegen/runcmp_check.py` (direct) | 98 passed, 0 failed |
| C5 fixture driver (direct build) | 14 fixtures render through their pinned arms (ofsskip ×4, precheck ×4, runcmp ×6) |
| `scripts/m6read_check_sab_anchors.py` | 486 rows (504 anchor sites), all resolve |
| mech `VALIDATE_ONLY=1` | FIELDS OK × 14 rows |

**Scale, stated plainly:** the I1 and zero-mover sweeps (35,980 compiles
each, about a minute apiece at 3 processes) went well past the brief's
"handful of patterns" smoke, and ran while k93tri held the Mac suite lock.

**Not run on the Mac (kit manager's ruling: the lock was held to ~10:00Z):**
`test-memfn-g2`, `test-memfn-arms`, `test-memfn-manifest` (C17 incl. the
new door's census), `test-memfn-forms` (C12 9 rows), `test-memfn-deleg`,
`test-memfn-link` (C15/C16), `test-memfn-stamps` (C11), `test-memfn-arch`
(C4), `test-memfn-reach`, `make test-codegen`, `test-registry`,
`test-rxtsource` — each **covered by memfn_m1b.sh's make test (Linux)**.

## 6. The Linux verdict (OWED, manager's executor)

`docs/design/memfn/probes/lxrun/memfn_m1b.sh TIP` — `make strict`, then
`memfn_r4c.sh` with every step: gate `--ref 993f8c1d --zero-dumps`, full
`make test`, the 14 mech rows solo, the memfn-simd axes pair, C11, every
I2 arm (every `--list-axes` flag incl. -fno-run-overlap/-fno-lit-run/
-fno-alt-island and the --tune positions, both comment tiers; start arms;
inertness arms; the M1 denies at `-e utf8`). Last line exactly
`== m1b-lx DONE rc=N ==`. `bash -n` clean; NOT run. Expected wall: 5-8 h
(launch under `gnutimeout 600m`). Caveat: memfn_r4c_i2.py's DECLARED
failure lines were measured at e6e6d6eb; a declaration that stopped firing
at 993f8c1d would read STALE (a judge-table fix, not an M1b mover).

## 7. Findings / CHOSEN items for the kit manager

- **F1 (CHOSEN): `cstr` writes a literal's BODY.** memfn.h never said;
  pcrec's sink (pcrec_sb_cstr) writes the body, G2's sink wrote the quotes
  too. The run compare is the first kit text to call it; with G2's spelling
  a compare reads `w2(""\141\142"")`, which does not compile. memfn.h now
  states it and G2's `sk_cstr` follows it.
- **F2 (CHOSEN): `MF_CMT_NONESSENTIAL`.** `mf_flush_helpers` has no hooks
  and so no `comment_tier`; the helpers' comment needs one. A kit constant
  equal to pcrec's (pcrec asserts it) rather than a signature change.
- **F3: the deny assertion moved G2's population shape.** A batch art has
  one `denies`; the deny is now drawn per batch, not per site (same count
  over the run, same random stream).
- **F4: arm selection in kit tests moved, as predicted.** G2's EXPR VERIFY
  `guard_by_caller` single-RUN sites go to `runcmp`; FUNC FIND sites with a
  RUN term can now take `ofsskip` (it no longer needs `run_cmp`). G2's
  quick tier is the check (§5).
- **F5:** at IMPLEMENT only, libpcrec.a held two `runcmp.o` members
  (`src/gen/` and `memfn/src/`); it linked (distinct symbols) and REPLACE
  removes one. A future migration whose kit file shares a pcrec basename
  meets the same thing in its IMPLEMENT commit.

## 8. Charter vs committed

| item | state |
|---|---|
| 0 CONTRACT: §14.8 corrected, stamp_int + MF_SITE_ABI 4 in §14.0 and memfn.h, rulings recorded | DONE (§R4.8; memfn.h with the code) |
| 1 kit runcmp arm, SPDX/provenance, PROVENANCE row | DONE |
| art-level helper + words state, stamp_int, row accessor | DONE |
| I1 shadow comparator, every call | DONE at IMPLEMENT (defines, VM compares, helper flush, RUN_WORDS), deleted at REPLACE |
| 2 callers switched, src/gen/runcmp.c deleted | DONE |
| mf_stamps RUN_WORDS, FORMS, LIBC | DONE |
| axes_dump via accessor + map | DONE (`--list-axes` byte-identical) |
| manifest, C12 (12 → 9), site_census door, DELEG VMRUN | DONE |
| mech re-points + new rows, hand-planted | DONE (§4); matrix detector runs OWED (Linux script, manager) |
| CLAUDE.md files; spec hunk only where caller-observable | DONE (none observable; two internal-name sentences updated) |
| risk: helper flush art-level, VM widths survive to the prologue | DONE (I1 + S572) |
| risk: deny reaches every site | DONE (deny map → every site + art; S570/S571; I1 -fno-run-overlap arm) |
| risk: D149 labels | DONE (runcmp.c header, `rc_width`, `rc_holds`) |
| risk: MF_INC_STRING_H for memcmp and helpers | DONE |
| risk: G2/C5 side effects; ARMS_ROW_FLOOR raised | DONE (16 → 28) |
| Linux wrapper memfn_m1b.sh, bash -n | DONE; RUN OWED (owner: pcrec manager via the executor; trigger: this handback) |
| Mac `make test` and the light sections | NOT RUN (ruling); covered by memfn_m1b.sh's make test (Linux) |
| memfn journal, responses.md `done:`, pcrec dev_journal line | OWED (owner: kit session / pcrec manager at merge) |
