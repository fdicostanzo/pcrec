# m7 — [MEMFN] R-8 / M7: N7, the encoding seam's span compare, migrates into the kit, zero movers

Lane m7 (opus), 2026-10-08, branch `lane/m7` cut from the kit branch
`lane/memfn-m7` @ 1adead14. Charter: the kit manager's brief; R-8
(memfn/docs/requests.md); the R-8 rulings (memfn/docs/responses.md, last
entries); docs/dev/decisions.md D58 ADDENDUM 2 (binding); design input
docs/dev/lanes/m7scope_report.md. Every file:line below is this branch's tip.

## 1. Summary (resume from here)

- **No STOP. Zero movers, no abi event, NO `docs/spec/` hunk** (Q-R8-10:
  nothing a caller observes moved: entry names, signatures, return protocol,
  stamps and every `--list-*` dump are byte-identical; §4).
- **Commits** (`git log 1adead14..lane/m7`):
  - `0a6ab4d4` PHASE A, M7 prep (kit-only): MF_VOCAB 3, MF_SITE_ABI 7,
    `memfn/src/mismatch.c` (one renderer, two rows), K1 `mf_ref_mismatch`,
    fixtures, 17 gate cases, `pins/n7_target/`, C5 checks 10/11;
  - `610c1580` IMPLEMENT: enc's keyed side table (`PcrecEncSite`), DELEG_SITES
    row N7, gen's describer `pcrec_memfn_span_site`, the [M7 I1] shadow;
  - `bbfc7d4d` REPLACE: the backends' loops become the site token, the seam
    substitutes the kit's text, shadow deleted, manifest/C12/rows, the D58
    doc changes, the rider, sabotage re-pins and new rows, start_table
    anchors re-derived;
  - then this report.
- **OWED to the slot** (§8): identity gate, N2 census (pins
  `mismatch_inplace`'s pcrec_floor), G2 full, `make test`, 70 solo mech rows.
- **G2 IS RED BY DESIGN until a blinded lane lands** (§7): check (b), "rows
  never chosen: arms/mismatch_inplace" (47,436,029 passed / 1 failed at Phase
  A). `make test-memfn-g2` is a `make test` section: the blinded lane must
  land before the slot's `make test`.
- **Findings**: (F1) `emit_vm.o` had no `memfn.h` dependency in the Makefile
  (stack smashing on every backreference compile after `mf_hooks` grew, until
  rebuilt): fixed, with `fields.def` added to `KITHDRS`; (F2) the K79 prefix
  placeholder defeats a lexical "is this a call" test on hook text, found by
  the shadow, fixed in the kit; (F3) an answer-moving plant (S670) that no
  pcrec answer suite sees (§6).

## 2. PHASE A: M7 prep (kit-only, zero pcrec bytes; `0a6ab4d4`)

| ruling | what changed | where |
|---|---|---|
| vocabulary (MF_VOCAB 2 -> 3) | `MF_OP_MISMATCH` (F8: k = the least j < reflen with lo + j >= n or fold(s[lo+j]) != fold(ref[j]); EQUAL when none), `MF_H_ON_DIFF` (Q-R8-5: k written to `result`, then `on_miss`, which may read it; `on_miss_leaves` 1 required, pasteable more than once), `MF_T_REF`/`MF_TK_REF` (one REQUIRED term at offset 0, no data); vocab row `{MISMATCH, ON_DIFF, REF}` only | memfn.h; compose.c `vocab[]`, `pred_kinds`, `site_check` |
| MF_SITE_ABI 6 -> 7 | `mf_site.fold_kind` (`mf_fold` NONE/ASCII/UCP, the FACT, Q-R8-4; nonzero only on MISMATCH, else refused) and `mf_hooks.ref`/`reflen`/`fold` (pcrec's fold TEXT, `@` the byte), each appended LAST. No fold map (D77/D122) | memfn.h |
| site rules | MISMATCH: exactly one REF term, REQUIRED, offset 0; `reverse` 0, `end_back` 0, `empty` NOP (an empty reference is EQUAL), ON_DIFF needs `on_miss_leaves` 1; each refusal names its field in backquotes | compose.c `site_check` |
| classes | op MISMATCH, handoff ON_DIFF, `fold_kind` F_NONE/F_ASCII/F_UCP (read on a MISMATCH site only, else unstated), `fold` FOLD_EXPR / FOLD_STMT (a lexical check that reads THROUGH quoted literals; OTHER where fold_kind is NONE, so a fold stated against the fact is refused), `ref`/`reflen` IDENT/OTHER; `fold` read at define as well as use (ruling F1's pattern), so its shape selects the row | fields.def; gate.c `fold_shape`, `cl_*`; `kit_stmt_shape`/`kit_fold_shape` exported to the renderer |
| Q-R8-2 (loop only) / Q-R8-9 (rows) | ONE renderer `mm_render` (memfn/src/mismatch.c) as TWO rows: the GENERIC row renders exact and FOLD_EXPR (serves `fold` FOLD_EXPR only); the new row `mismatch_inplace` renders FOLD_STMT (temps `x`/`y`, renamed `<prefix>_mf<h>_x/_y` if a hook names either). Operands raw when identifiers, else parenthesized; the fold raw when call-shaped, else parenthesized; `on_miss` raw when JUMP/BRACED, else braced, never LOOP_EXIT (the form's own loop encloses it, Q-R7-3) | mismatch.c, generic.c (`case MF_OP_MISMATCH`, the ON_DIFF dispatch, uses/serves), kit.h, compose.c `arms[]` |
| K1 | `mf_ref_mismatch(a, b, n)` (F8) | k1_ref.c, memfn.h |
| provenance | mismatch.c `pcrec 1adead14 (relicensed 0BSD ...)`, its PROVENANCE.md row | memfn/PROVENANCE.md |

No `options.def` row and no `--list-axes` memfn floor raise: options.def rows
are each BYTE-MOVING kit change's own deny (memfn/CLAUDE.md; M4/R4g/R4h added
rows without one), M7 moves no byte, and a row would itself move the
`--list-axes` dump (a mover). Recorded as a judgement call for the kit
manager.

Fixtures and checks (tests/memfn): five MISMATCH fixtures through
`render_emit` with the residual entry's own hook spellings (`mm-exact`,
`mm-ucp-expr`, `mm-ascii-inplace`, `mm-nonident`, `mm-inplace-clash`), pinned
(`ARMS_ROW_FLOOR` 78 -> 88, `ARMS_EXPECTED` gains `mismatch_inplace`); 17 gate
cases (`GATE_CASE_FLOOR` 48 -> 65): six RENDER (exact, expression, in-place,
in-place with a BRACED on_miss, the UCP in-place fold, non-identifier hooks)
and eleven REFUSE (a `break;`, fold against NONE, ASCII with no fold, a
shapeless fold, `on_miss_leaves` 0, `reverse`, a non-NOP `empty`, a second
term, a REF term off 0, an unstated `ref`, `fold_kind` on a FIND), each
naming its field. **Check 10** (Q-R8-9's pinned targets): `pins/n7_target/
mm-exact.c`, `mm-ucp-expr.c`, `mm-ascii-inplace.c`, whose bodies are the loops
CUT from pre-edit build/pcrec artifacts, compared byte for byte with the
kit's fresh render, with a planted-byte control. **Check 11**: the five bodies
compiled in functions with the entry's signature and protocol and run over
every subject of length 0..4 on a 7-byte alphabet, every `at` in [0, n+1],
every separate reference of length 0..3 and every reference inside the
subject, NULL pointers at length 0, against a byte loop written from
memfn.h: 33,852,405 calls, 0 wrong. rows.tsv/row_floors.tsv gained
`mismatch_inplace` (reach `pending-site:M7-REPLACE` at Phase A; ROWS_FLOOR
14 -> 15).

At Phase A: arms 286/0, rows 127/0, link 8/0, manifest 17/0, deleg 5/0,
stamps 14/0, arch 15/0, forms 4/0, reach 4/0, `make strict` clean. **Zero
pcrec bytes: 41/41 witness compiles byte-identical** (§4's list).

## 3. The boundary as built (IMPLEMENT `610c1580`, REPLACE `bbfc7d4d`)

D58 addendum 2, the NO-CALLBACK form:

| text / decision | owner | where |
|---|---|---|
| signature, braces, `return (ptrdiff_t)reflen;`, UCP fold function + generated table, every comment and declaration | backend | `defs_bref`, `defs_bref_ci`, `defs_bref_ci_ucp` (enc_byte.c), `u8_defs_bref` (enc_utf8.c) |
| the ONE site token `PCREC_ENC_SITE` (`@site@` + newline, a whole line) where the loop sat | backend text | the four constants above |
| SITE DATA: fold kind, fold TEXT (`if (@ >= 'A' && @ <= 'Z') @ = (unsigned char)(@ + 32);`, `$_span_ci_fold(@)`), failure statement `return -(ptrdiff_t)i - 1;` | backend, a KEYED SIDE TABLE (not a `PcrecEncEntry` column) | `PcrecEncSite`, `PcrecEnc.sites`, `sites_byte`, `sites_utf8`, lookup `pcrec_enc_site` |
| operand spellings (entry parameter names, the index, its decl, the indent) | one spelling, enc.h | `PCREC_ENC_SPAN_*` |
| the token's rules (no other `@`, no token without a text, no text without a token) and the substitution | enc | `pcrec_enc_emit_text(…, site)`, `enc_emit_defs`; site-data text's `$` by `pcrec_enc_emit_site_text` (leaves the kit's `@`) |
| describing the site (MISMATCH/STMT/ON_DIFF, one REF term, NOP, leaves, fold fact + text) and rendering it through the door | gen | `pcrec_memfn_span_site` (memfn_sites.c), `emit_residual_defs` (emit_dfa.c), DELEG_SITES `N7` (MISMATCH/ON_DIFF/REF, `DELEG_LOOP`, POSITION) |
| the compare loop itself | **kit** | memfn/src/mismatch.c |

Data flows enc -> gen -> kit -> gen -> enc; `src/enc/` includes no gen or kit
header (its one call up the error path is `pcrec_ctx_fail`, core). Not
migrated: `u8_defs_bref_ci` (the per-character decode walk) keeps its body and
has no site row (N7U). D58 doc changes in the REPLACE commit: enc.h's "WHY
TEXT AND NOT A CALLBACK" paragraph and the third-encoding recipe, the
residual-text constraints and a seam-event paragraph in src/enc/CLAUDE.md.

## 4. Shadow and zero-mover evidence

- **I1 shadow (IMPLEMENT).** In `emit_residual_defs`, every carried entry
  with site data had its loop rendered through a SCRATCH art and compared
  byte for byte with the backend's loop (the text from the function's last
  `{` to its `    return (ptrdiff_t)reflen;`); a mismatch failed the compile
  `[M7 I1]`. Over the 4,380 unique corpus `pattern` lines (`--list-source`
  over every `tests/**/*.rxt`, deduplicated) x 10 configs, `--features all`:
  **43,800 compiles, 0 mismatches, 0 internal errors**. Reach (artifacts
  carrying the compare):

  | config | exact | caseless | UCP table |
  |---|---|---|---|
  | byte / byte -fcomments | 434 / 434 | 10 / 10 | 2 / 2 |
  | utf8 / utf8 -fcomments | 436 / 436 | 10 / 10 (walk, no site) | — |
  | byte --ucp / --ucp -fcomments | 434 / 434 | 10 / 10 | 10 / 10 |
  | (?i) byte / (?i) byte -fcomments | 1 / 1 | 439 / 439 | 0 / 0 |
  | (?i) byte --ucp | 1 | 439 | 439 |
  | (?i) utf8 | 1 | 441 (walk, no site) | — |

  Byte-wise sites compared: exact 2,612 artifacts (both encodings), byte
  caseless 1,357 (UCP shape 463, ASCII in-place 894).
  The first run of the shadow found the kit PARENTHESIZING
  `\x01q_span_ci_fold(...)`: the K79 placeholder is not identifier text, so
  the "is it a call" test failed (F2). Fixed in the kit (`call_shaped` reads
  the art's prefix as an identifier stem) before the sweep above.
- **REPLACE corpus pairs** (`build/m7scratch/ident_sweep.py`, gitignored):
  pre-edit binary `pcrec.base` (sha256 d125541e…) vs the post-rider REPLACE
  binary, same 4,380 x 10 configs, `-p rx -o rx.c` in sibling dirs, `.c`,
  `.h`, rc and stderr compared: **43,800 pairs, 0 movers** (and 0 on the
  pre-rider REPLACE binary). Logs `build/m7scratch/ident_sweep.final.log`,
  `ident_sweep.replace_prerider.log`.
- **Witness tier** (`build/m7scratch/zm.sh`, `witness.tsv`): **41/41 SAME** at
  Phase A, IMPLEMENT and REPLACE: byte `(a+)\1`, `(a*)\1`, `^(a)\1$`,
  `(?<n>a)\k<n>`, `(?J)(?<n>a)|(?<n>b)\k<n>`, `(?i)(ab)\1`, `(?i)(k)\1`,
  `(a)(?i:(b)\2)\1`, `(?<=a)(b)\1x`, `(?i)(?<=a)(b)\1x`, `a${v}b`,
  `(?i)a${v}b`, `--ucp (?i)(ab)\1`, `(*UCP)(?i)(.)\1`; utf8 `(a+)\1`,
  `(é+)\1`, `^(k)\1$`, `(?i)(ab)\1`, `(a)(?i:(b)\2)\1`, `a${v}b`,
  `(?i)a${v}b`; `-fcomments` x7 (both encodings, `--ucp`); `-p foo` x4;
  `--emit-main` x3; `--engine=vm` x3; `-fno-comments`; two controls.
- **Other streams:** `--list-axes`, `--list-limits`, `--list-syntax`,
  `--list-families`, `--list-definitions`, `--list-schema`,
  `--list-analyses` identical; `--emit-ir` and `--emit-facts` identical on
  five backreference/variable witnesses x 2 encodings.
- **Light checks at the tip:** arms 286/0, rows 127/0 (UNREACHED: 2
  PLACEHOLDER floor cells, `mismatch_inplace`'s), manifest 13/0 (14 rows,
  11 delegated / 3 pending; rule 2 reached `emit_residual_defs` 27 times over
  its 300-pattern sample), forms 4/0 (3 rows / 3 forms), deleg 5/0, stamps
  14/0, link 8/0, arch 15/0, reach 4/0, `limits_check.sh` 37/0,
  `run_encoding_checks.sh` 11/0 (DD12a), `run_codegen_tests.sh` 330/0,
  `run_backref_diff.sh` 13/0, `make strict` clean.

## 5. C12 / C17 (measured by running)

- **C17**: N7 `delegated` (emitters `pcrec_memfn_span_site,
  emit_residual_defs`; companions `defs_bref, defs_bref_ci, defs_bref_ci_ucp,
  u8_defs_bref, sites_byte, sites_utf8, pcrec_enc_site`); new row **N7U**
  (`u8_defs_bref_ci`, pending, step "after M7", trigger in the row text
  "completeness after M7 + a decode-hook vocabulary step", Q-R8-1).
  `C17_ROW_FLOOR` 13 -> 14. Rule 4 holds for N7U (`span-decode`). At
  IMPLEMENT C17 rule 2 was red on the shadow (it called `mf_emit`), as at M4;
  gone at REPLACE.
- **C12**: `enc_byte.c span-index 3` and `enc_utf8.c span-index 1` DELETED;
  `C12_CEIL_ROWS_FLOOR` 5 -> 3; the `span-decode` row stays for N7U.
- **C10**: `D91_LOOP` gains N7 (Q-R8-10, budget 2).
- **rows.tsv**: `mismatch_inplace` reach `pcrec`, witness `(?i)(ab)\1`,
  signature `unsigned char x, y;`, control `(ab)\1`; both floors
  PLACEHOLDER.
- **Rider**: `"memchr"` deleted from `src/gen/memfn_stamps.c`
  `libc_names[]`.

## 6. Sabotage

Every figure HAND-MEASURED (plant applied, tree rebuilt, the row's suites
run, restored; `build/m7scratch/plant_all.sh`, logs `build/m7scratch/plants/`).

| row | anchor | defect | measured |
|---|---|---|---|
| S116 | RE-ANCHORED to `sites_byte`'s fold text | 'Z'/'z' stop folding (now both operands) | brefdiff 1 failed / 12 passed (fold agreement); caseless.rxt 0/35 |
| S513 | RE-AIMED (Q-R8-7) to `"strlen"` on the next libc line | the vars resolver's strlen under-reported | memfnstamps 2 failed / 8 passed (C11 quick compiles `^${v}$`, `^${v:-\xff}$`): live again, `SAB_EXPECT` DETECTED |
| S517 | RE-ANCHORED (the rider's line) | memcmp dropped | memfnstamps 2 failed / 8 passed: NOT equivalent (a variable compare is pcrec text calling memcmp) |
| S666 (new) | mismatch.c exact/expr `if` line | subject-end test dropped | memfnarms 6 failed / 280 passed (check 11 fails to build: `n` unused under -Werror) |
| S667 (new) | the `for` line | `i <= reflen` | memfnarms 9/277, brefdiff 25 failed / 6 passed |
| S669 (new) | the `y` fold paste | fold on one side | memfnarms 4/282 (815,140 wrong calls), brefdiff 1/12, caseless.rxt 6 failed / 29 passed |
| S670 (new) | the in-place subject-end exit | `break;` instead of on_diff | memfnarms 4/282 (5,172,452 wrong); brefdiff 0/13 and caseless.rxt 0/35 (F3 below) |
| S671 (new) | the exact/expr on_diff line | k + 1 handed to on_miss | memfnarms 6/280; answer-neutral (work only), as argued |
| S673 (new) | `defs_bref`'s token line | the backend spells its loop again | memfnmanifest 1 failed / 12 passed (rule 1), memfnforms 1 failed / 3 passed (C12) |

S394 is untouched (no `PcrecEncEntry` column). Every new row's SAB_REACH
reaches on the clean tree (checked by hand); S673 also carries a
SAB_REACH_POP on the manifest's delegated N7 line. S668/S672/S674/S675 not
built (the scoping report's minimum set is S666 S667 S669 S670 S671 S673).

**F3, a coverage finding.** Under S670, `(?i)(a+)\1` on "aaa" answers
`(0,6)` (an end past the subject) where the clean tree answers `(0,2)`
(hand-run on `--emit-main`), yet `run_backref_diff.sh` and
`tests/backrefs/caseless.rxt` stay green: no answer cell has a caseless
reference the subject ends inside. Recommend an oracle-verified caseless
cell of that shape (not added here: test expectations are oracle work).

`python3 scripts/m6read_check_sab_anchors.py`: **555 sabotages / 573 anchor
sites, all resolve.** `docs/design/start_table/{call_graph.txt,
sabotage_anchors.tsv,.total}` re-derived by their scripts (S116's owner
`defs_bref_ci` -> `sites_byte`; S673 `defs_bref`; the kit rows `outside`;
S571's UNRESOLVED (rc 2) is pre-existing, M4's note); `inventory_check.py`
150/150.

## 7. G2: what a blinded lane must add (memfn/tests/ not edited)

G2 quick at Phase A and again at the tip (`build/m7scratch/g2q_prep.log`, `g2q_final.log`): **47,436,029 passed, 1
failed**: check (b), "rows never chosen: arms/mismatch_inplace". G2 builds
against MF_SITE_ABI 7 unchanged. Needs, in CONTRACT terms only (memfn.h is
the source):

1. **The op.** `MF_OP_MISMATCH` / STMT / `MF_H_ON_DIFF` over ONE REQUIRED
   `MF_T_REF` term at offset 0 (no data). k = the least j in [0, reflen)
   with lo + j >= n or fold(s[lo + j]) != fold(ref[j]). On a difference
   `result` == k when `on_miss` runs (which may read it, and must leave); on
   EQUAL `on_miss` does not run and `result` holds no promised value.
   `empty` NOP: reflen 0 is EQUAL and reads nothing. lo > n is a difference
   at 0 when reflen > 0.
2. **Read limits.** `s` only in [lo, n), `ref` only in [0, reflen); `s` may
   be NULL when n == 0, `ref` NULL when reflen == 0; `ref` may ALIAS `s`
   (before lo, at lo, overlapping the window). Guard pages on BOTH operands.
3. **Folds** (`fold_kind` + `fold`): NONE (no fold; a stated `fold` is
   REFUSED, naming `fold`), ASCII and UCP (a `fold` text is REQUIRED,
   refused naming `fold` if unstated). The text has two shapes: FOLD_EXPR
   (one expression of `@`, no `;`/brace outside quoted literals) and
   FOLD_STMT (statements folding the unsigned-char lvalue `@`, ending in `;`
   or `}`); text with no `@` is refused. The contract compares
   map(a) == map(b) and nothing more: generate maps (identity, ASCII-52,
   Latin-1 representatives, random idempotent and NON-idempotent maps), each
   spelled in both shapes, the hook text and the map agreeing.
4. **Refusals** (each names the field): `reverse` 1, `end_back` 1, `empty`
   other than NOP, a second term or a non-REF term, a REF term off 0 or
   OPTIONAL, `on_miss_leaves` 0, `on_miss` LOOP_EXIT (`break;`), `fold_kind`
   on a non-MISMATCH site, `fold_kind` outside the enum, a REF term in any
   other op (the vocabulary), an unstated `ref`/`reflen`, `MF_SITE_ABI + 1`.
5. **Rows**: check (b) must see `mismatch_inplace` chosen (a FOLD_STMT site)
   and the generic row rendering MISMATCH (a NONE or FOLD_EXPR site);
   FLOOR_ROWS 14 -> 15; a `g2_floor` for `mismatch_inplace` from G2's per-row
   count. Non-identifier hook texts must work (both rows parenthesize).
6. **K1**: `mf_ref_mismatch(a, b, n)` (F8, exact) is the reference.

## 8. The slot chain the manager must run

1. Merge `lane/m7` into the kit branch ALONE; `make -j16 && make strict`.
2. **The blinded G2 lane (§7) must land before step 6.**
3. Identity gate, 0 movers on every stream, BOTH bases plus `-fcomments` and
   `--ucp` arms, ref = M7's merge-base (re-take it if main moved, Q-R8-8):
   `python3 scripts/emit_sweep.py --ref <merge-base> …` (the R4c invocation,
   `--bases byte,utf8`, `--extra -fcomments`, `--extra --ucp`), judged by
   `python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps
   <out>`; print the reach (`_span_match`, `_span_match_caseless`,
   `_span_ci_fold_pairs`) per base.
4. N2 census (`docs/design/memfn/probes/rowcon/n2_census.sh`, JOBS=16), then
   `n2_report.py <out> --floors tests/memfn/row_floors.tsv --propose`: pin
   `mismatch_inplace`'s pcrec_floor. Expect would_decline 0.
5. G2 full (`make test-memfn-g2-full`) after step 2; pin the row's g2_floor.
6. `scripts/perfrun --label m7 -- <log>`; verdict `grep -E '\*\*\*
   \[(Makefile:[0-9]+: )?test-'`.
7. Mech, each SOLO (`bash tests/mech/run_sabotage_matrix.sh <id>`), rule (b)
   (rows anchored in the changed definitions: `defs_bref*`, `u8_defs_bref`,
   `sites_*`, `pcrec_enc_backend_*`, enc.c's emit functions,
   `emit_residual_defs`, memfn_sites.*, `libc_names`), every row on a
   `memfn/` or `tests/memfn/` file or on a memfn arm, the re-pinned/re-aimed
   rows, the new rows, the `src/enc/` rows and the scoping report's
   confidence set — **70 rows**: S68 S106 S109 S116 S185 S214 S229 S233 S265
   S267 S271 S273 S279 S285 S340 S390 S391 S394 S409 S410 S412 S443 S444
   S445 S447 S450 S454 S455 S464 S510 S511 S512 S513 S514 S515 S516 S517
   S518 S519 S520 S521 S522 S523 S524 S525 S526 S527 S528 S529 S570 S571
   S573 S590 S591 S616 S617 S618 S619 S666 S667 S669 S670 S671 S673 S-U2
   S-U3 S-U5 S-U6 S-U9. Expect every row DETECTED except the ones the row
   files expect UNDETECTED (S525 stays the TRIPWIRE it was re-pinned to at
   M4; S513 now expects DETECTED).
8. Not lane work: the kit's responses.md entry and journal line (single
   writer); pcrec's dev_journal line and plan.md's [MEMFN] M7 state.

## 9. Charter checklist

| item | state |
|---|---|
| MF_VOCAB 3 (MF_OP_MISMATCH, MF_T_REF, MF_H_ON_DIFF) | DONE (§2) |
| MF_SITE_ABI 7, hooks ref/reflen/fold + fold_kind fact appended last; readers by grep (memfn.h, memfn/CLAUDE.md, memfn/include/CLAUDE.md, memfn/src/CLAUDE.md) | DONE |
| rows (generic EXACT/EXPR + one named INPLACE row), K1 ref, fixtures, gate cases decline/refuse/positive, pins (pinned target files byte for byte, Q-R8-9) | DONE (§2) |
| options.def deny rows / --list-axes floor | NOT ADDED, reasoned (§2): zero movers, and a row would move the dump |
| zero pcrec bytes at PREP, both encodings | DONE (41/41) |
| enc keyed side table (not a PcrecEncEntry column), the token, gen's describer, enc never calls up | DONE (§3) |
| I1 shadow over the corpus, both encodings, -fcomments and --ucp, 0 mismatches | DONE (43,800 compiles, §4) |
| REPLACE: backend loops -> token; enc.h WHY-TEXT paragraph, third-encoding recipe, src/enc/CLAUDE.md | DONE (§3) |
| Q-R8-1: N7 delegated, N7U pending row with its trigger text; C17 floor | DONE (§5) |
| C12 ceiling rows deleted, floor; C10 D91 budget 2 (Q-R8-10) | DONE (§5) |
| rider (dead memchr) | DONE |
| S116 re-pinned, S394 untouched, S513 re-aimed (reached: strlen), S517 re-anchored + re-measured | DONE (§6) |
| new rows S666 S667 S669 S670 S671 S673 with reaching SAB_REACH, ids grepped free on main/worktrees/branches | DONE (§6) |
| call_graph / sabotage_anchors re-derived; m6read green | DONE |
| zero movers: corpus pairs both encodings + 25+ witnesses | DONE (43,800 pairs, 41 witnesses) |
| no docs/spec hunk (stated) | DONE: none needed |
| memfn/tests untouched; G2's needs listed | DONE (§7); G2 red until that lane |
| CLAUDE.md files (memfn, memfn/include, memfn/src, src/enc, src/gen, tests/memfn, tests/memfn/pins/n7_target, tests/mech, docs/dev/lanes) | DONE |
| identity gate, N2 census, G2 full, make test, mech rows | OWED to the slot (§8) |
