# memfnskel — [MEMFN] R4a part 1: the kit's code skeleton, linked, calling nothing

Lane `memfnskel` (kit session, opus), 2026-10-05. Branch `lane/memfnskel`
off `lane/memfn-r4a` at `eb327ff5`. Serves request **R-3 part 1 (R4a)**
(`memfn/docs/requests.md`); design of record `docs/design/memfn/
integration.md` rev 4.6 (§R4.6-§R4.3, §8.2/§8.3, §14.0-§14.10, §17, §20.3,
§22 R4a). ZERO MOVERS: no emitted artifact byte changes. Not in this lane:
`tests/memfn/site_manifest.tsv` + C17 (sibling lane) and G2 (the blinded
lane).

## 1. What was built, file by file

**The kit (`memfn/`, all 0BSD, SPDX + provenance header on every file)**

| file | what it is |
|---|---|
| `memfn/include/memfn.h` | THE one public header. `MF_SITE_ABI` 2, `MF_VOCAB` 2, `MF_NS(name)` → `pcrec_mf_name` (`mf_name` under `MF_STANDALONE`). The §8.2+§14.0 shapes: `mf_form`/`mf_op`/`mf_handoff`/`mf_empty`/`mf_need`/`mf_term_kind` enums, `mf_term`, `mf_pred`, `mf_site`; `mf_sink`, `mf_arena`, `mf_hooks` (§8.3 + §14.0 members); `MF_TOK_ACCEPT`/`MF_TOK_REJECT`; `mf_result`, opaque `mf_art`; entry points `mf_art_begin`/`mf_art_end`/`mf_art_error`, `mf_define`/`mf_use`/`mf_emit`/`mf_call`, `mf_flush_helpers`/`mf_includes`/`mf_stamps`, `mf_vocab_has`; the registry view `mf_option`/`mf_options()`/`mf_opts_check()`; K1's `mf_ref_*`. Every entry name is a `#define` onto its `MF_NS` symbol. No ISA name (C4). |
| `memfn/src/kit.h` | internal: `kb` (growable text over the caller's `mf_arena`), `struct mf_art` + per-site records, the arm interface. |
| `memfn/src/compose.c` | K2: `mf_art`; the define/use split with handle checks (undefined handle at use, unused handle at `mf_art_end`); `site_check`, the vocabulary rules every arm's input passes; the FIRST-MATCH arm table (one row: generic); `mf_vocab_has`'s (op, handoff, term-kinds) table; `mf_flush_helpers`/`mf_includes`/`mf_stamps` (nothing to write at R4a). |
| `memfn/src/generic.c` | THE GENERIC SCALAR ROW (§14.6), the table's last row: a plain byte loop over the conjunction for every (form, op, handoff) the vocabulary holds — EXPR (GNU statement expressions), FUNC (`static inline` definition + call), STMT ASSIGN / ON_MISS / ON_CAND / ADVANCE. Tests every term (OPTIONAL included), checks every read against `[floor, n)`, honours `end_back`, `reverse` and the three empty outcomes, uses pcrec's `member` hook when given. Declares only operands it reads (artifacts compile `-Wall -Wextra -Werror`). No tuning constant (D149). |
| `memfn/src/k1_ref.c` | K1 reference functions: F1 `find_byte`, F2 `find_any2`/`find_any3`, F4 `find_in_set`, F5 `skip_in_set`, F9 `find_literal`, F7 `run_verify`. The most obvious loop each (G2's oracle). |
| `memfn/src/options.def` | the kit's option registry, X-macro `MF_OPT(name, kind, budget, layer, doc)` with §R4.4.1's column doc comment, ZERO rows. |
| `memfn/src/options.c` | `mf_options(size_t *n)` and `mf_opts_check(str, err, n)` over the one table (`no-NAME` denies, bare `NAME` forces a `MF_OPT_PAIR` row; NULL/"" valid; any token is unknown while the registry is empty). |
| `memfn/PROVENANCE.md` | file → source → licence → what derives from it, 7 rows; C16 compares it to the tree. |
| `memfn/CLAUDE.md`, `include/CLAUDE.md`, `src/CLAUDE.md`, `README.md` | status and layout to R4a. |

**pcrec side**

| file | change |
|---|---|
| `Makefile` | `KITSRCS`/`KITOBJS`/`KITHDRS`/`KITFLAGS`; the kit compiles with NO `-Ilib -Isrc` (it cannot include pcrec — the boundary held by the build); `libpcrec.a` and the findings stage-0 archive link `$(KITOBJS)`; `axes_dump.o` depends on `memfn.h`; `make strict` and `make lint` cover `$(KITSRCS)`; new section `test-memfn-link` in `TEST_SECTIONS` and `.PHONY`. |
| `src/dump/axes_dump.c` | `--list-axes` prints `#section memfn` after the axis table, rows from `mf_options()` (pcrec names none); includes `../../memfn/include/memfn.h` (the one pcrec TU that includes the kit). |
| `tests/memfn/run_link_checks.sh`, `c15_allowlist.txt`, `CLAUDE.md` | C15 + C16 (§4). |
| `tests/lib/lib_srcs.sh` | `pcrec_lib_srcs ROOT`: the ONE list of library sources (src/ + memfn/src/) for scripts that build a compiler from source. |
| 12 scripts | moved onto `pcrec_lib_srcs`: `run_{wordctx,trie,endvar,mlinectx,gstart}_identity.sh`, `run_anchored_match.sh`, `run_n1_budget.sh`, `run_size_term.sh`, `run_cpset_structure.sh` (its scratch copy now carries `memfn/`), `tests/resource/run_resource_tests.sh` (REFCAP), `tests/thread/run_thread_tests.sh` (TSan library), `run_recursion_identity.sh` (the moving FILEPIN reference also archives `memfn/` when the pinned commit has it). Without this every from-source reference build fails to link (`pcrec_mf_options` undefined). |
| `tests/lib/table.sh` | `table_main FILE` (`-` = stdin): the leading anonymous table of a multi-section stream; command word `table-main`. |
| `tests/registry/axes_registry_check.sh` | reads pcrec's table via `table_main`; one new arm for the `memfn` section (present, header-truthful, columns by name) + the floor arm (UNREACHED while empty; FAIL if a row appears with no floor). |
| `tests/registry/run_registry_tests.sh` | axes PASS pin 189 → 190 (measured). |
| `tests/axes/run_axes.sh`, `tests/codegen/run_comments_axis.sh` | select the main table before reading rows. |
| `docs/spec/registry.md` §6, `docs/spec/table_contract.md`, `docs/spec/cli.md` | the D80 hunk (§5). |
| CLAUDE.md | `tests/`, `tests/lib/`, `tests/registry/`, `src/dump/`, `tests/memfn/` (new), the four under `memfn/`, `docs/dev/lanes/`. |

Exported kit symbols (26, all `pcrec_mf_*`): the 13 entry points, the 7
`ref_*`, `kb_init`/`kb_putn`/`kb_puts`/`kb_printf`, `kit_fail`,
`generic_arm` (the last six are kit-internal cross-file names, prefixed
through `MF_NS` like the rest).

## 2. Contract choices where the doc was ambiguous

Each is marked `CHOSEN` in `memfn.h` where it is a header spelling.

1. **`mf_sink`**: ops `puts`, `vprintf(u, fmt, va_list)` (a varargs op
   cannot be a function pointer usefully), `cmt_open(u, tier)` returning
   nonzero iff the gate is open (the kit writes the body only then),
   `cmt_close`, `stamp`, `cstr`, `comment_byte(u, int *prevp, byte,
   extra_escape)` (§14.2's stateful escaper), `legend_byte`. A NULL op is
   "not offered". The generic row needs only `puts`.
2. **`mf_arena`**: `{ void *u; void *(*alloc)(void *u, size_t n); }`;
   `alloc` may return NULL for a stand-alone caller; the kit never frees.
3. **`mf_hooks.hi` dropped**: §14.4 replaces it with `n` + `end_back`.
4. **`mf_site.token` (`--isa=`) dropped**: withdrawn by §R4.3.1 (no
   `--isa=` axis). `mf_kit_version()` not built: §18/§R4.3.3 put no kit
   version anywhere.
5. **`MF_P_BASELINE` not defined**: withdrawn (§R4.2 row 1). Policy bits
   are `MF_P_PORTABLE_ONLY`, `MF_P_INLOOP`, `MF_P_SIZE_LEANING`;
   `MF_D_RUN_OVERLAP` is bit 0 of `denies`; `MF_INC_STRING_H` bit 0.
6. **`MF_MAX_BACK` = 8**: the design names the bound, no value. A shape
   bound (today's deepest is −1, G2's space −2), not a tuning constant.
7. **`mf_use_kind` enum order**: `MF_USE_POSITION` = 0, so a zeroed site
   is POSITION, never the exploitable DISCARD (§14.5 `[rev4.6]`).
8. **`mf_art_end(art)` added**: §14.0 item 1 asserts "an unused handle at
   artifact end" but names no end call. **`mf_art_error(art)` added**: the
   text pcrec raises through `pcrec_ctx_fail` when a call returns nonzero.
9. **The `member` hook's `term` id** = the term's index in its predicate,
   plus `pred_index * MF_MAX_TERM` in an ALL_PRESENT site.
10. **FUNC's name** = `fn_name(u, site->pred.fn_ref)` for every op,
    ALL_PRESENT included (that op's `pred` carries only `fn_ref`).
11. **FUNC parameters** are exactly the operands the body reads, in the
    order subject, n, lo, floor, miss (`miss` for a valued FUNC, so the
    call passes pcrec's miss value). Recorded at define; every call passes
    the same list from the use hooks.
12. **The vocabulary** (`mf_vocab_has`): RETURN over FIND/SKIP/ALL_PRESENT
    (EXPR, FUNC); BOOL over FIND/VERIFY/ALL_PRESENT (EXPR, FUNC); ASSIGN
    over FIND/SKIP/ALL_PRESENT (STMT); ON_MISS over FIND/VERIFY/
    ALL_PRESENT (STMT); ON_CAND over FIND (STMT); ADVANCE over SKIP (STMT).
    SKIP takes exactly one SET term. The form follows from the handoff.
    ALL_PRESENT: `ret_pred` set iff RETURN/ASSIGN (§R4.6.1 item 4).
13. **NOP empty** only for STMT forms, and not for a declaring ASSIGN (a
    declaration cannot be skipped) or ON_CAND. ADVANCE is NOP by nature
    (pcrec's `more` owns the range).
14. **A miss test is `result == (miss)`** (ASSIGN's and ON_CAND's
    `on_miss`): sound because `miss` is a value no hit can take; stated in
    the `miss` hook's comment.
15. **ON_CAND** renders accept as `{ result = cand; goto <p>_done; }` and
    reject as `goto <p>_next;` (labels emitted only when reached, so
    `-Wunused-label` stays quiet); the hook's text may use only the capture
    sink's `puts`/`vprintf`.
16. **`step`** may come with or without its trailing `;`.
17. **The `--list-axes` section's words**: `kind` deny|pair, `budget`
    scan|loop|any, `layer` scalar|simd, `spelling` `--memfn=no-NAME`
    (`|--memfn=NAME` for a pair). The floor's spec spelling is
    `` `memfn` section floor: N `` in `registry.md` §6 (none at R4a).
18. **pcrec includes the header by relative path** from `src/dump/` rather
    than adding `-Imemfn/include`: every from-source reference build would
    otherwise need the flag too.
19. **K1 lives in `libpcrec.a`** (one rule: every `memfn/src/*.c` links).
20. **`generic` is the form id** the generic row reports in `mf_result`.

## 3. Zero movers — the proof

OWED (filled below when the run completes).

## 4. The checks and their witnesses

**C15** (`tests/memfn/run_link_checks.sh`): every global defined symbol of
`build/libpcrec.a` begins `pcrec_`. Measured: 457 globals, 26 the kit's,
0 exceptions, allowlist born empty.
- Built-in witness, every run: a probe archive with `pcrec_c15_probe_ok`
  and a planted `c15_probe_planted` must yield exactly the planted one
  (PASS; it also learns Mach-O's `_`).
- Population floor 200, reach (`pcrec_mf_options` present), stale
  allowlist arm.
- Real-tree sabotage: `static int in_set` → `int in_set` in `k1_ref.c`,
  object swapped into a copy of the archive (`LIB=`): **FAIL: … exports
  symbol(s) without the pcrec_ prefix … in_set** (7 pass / 1 fail).

**C16**: every file under `memfn/include` + `memfn/src` (7) carries a
D145 SPDX id (0BSD/Unlicense/CC0-1.0) in its first 5 lines and a
`Provenance:` line in its first 10, and `PROVENANCE.md` agrees file for
file and on the licence.
- Built-in witness, every run: a synthetic kit plants six defects (no
  SPDX, MIT, no Provenance, no row, a row with no file, licence
  disagreement); exactly those files are flagged (PASS).
- Real-tree sabotage (`KITDIR=` copy): `generic.c` SPDX → MIT: **FAIL**
  ×2 lines (off D145's list; disagrees with its row). A new
  `src/newarm.c` with a good header and no row: **FAIL: no row in
  PROVENANCE.md**.

**The `memfn` section arm** (`axes_registry_check.sh`):
- the base binary (no section): **FAIL: --list-axes has no '#section
  memfn'** (189 pass / 1 fail — every main-table check still passed,
  which also shows `table_main` returns a sectionless stream whole);
- a wrapper appending one kit row: the section arm PASSes and **FAIL: the
  section has 1 row(s) but docs/spec/registry.md §6 pins no … floor**
  (190 / 1). The planted kit row was NOT read as a pcrec axis (no
  truthfulness failure on the main table): the selection works.
- the real tree: 190 PASS, `UNREACHED: [memfn floor] the kit's registry
  is empty (0 rows) …` (K35: declared, never counted).

**The generic row** (scratch only, NOT committed — G2 is the blinded
lane's): 600 random sites × 2 seeds over 9 (op, handoff, form) kinds,
offsets −2..+4, RUN lengths 1-3 with masks, floors, `end_back`, reverse,
NOP; rendered text compiled `-Wall -Wextra -Werror`, run against a
brute-force interpreter over 400 random subjects each: **480,000 checks,
0 mismatches**. Sabotage (`<=` → `<` in the upper-bound test): **6,604
mismatches** caught.

## 5. The spec hunk (D80)

`--list-axes` is caller-observable, so:
- `docs/spec/registry.md` §6: the row-count pin's command now selects the
  main table (`table.sh table-main -`); a new **"THE `memfn` SECTION"**
  block — the six columns and their value sets, "NOT pcrec axes", EMPTY at
  R4a, the floor's spelling and birth at R4d, UNREACHED until then.
- `docs/spec/table_contract.md`: Scope row for `--list-axes` (one named
  section after the anonymous main table, `--list-source`'s shape);
  **consumer rule 5**: the leading anonymous table is every line before
  the first `#section`, `table_main` its shell implementation (§R4.4.1
  asked for this hunk if rule 2 did not already say it; it did not).
- `docs/spec/cli.md` `--list-axes`: the stream has two tables; consumers
  select.

No emitted artifact text, stamp, flag, limit or diagnostic changed. The
`--memfn=` CLI option is NOT added (not part of R4a's charter; pcrec holds
no string yet).

## 6. Validation

OWED (filled below).

## 7. Charter vs committed

| charter item | status |
|---|---|
| 1. `memfn.h`: `MF_SITE_ABI` 2, `MF_VOCAB` 2, `MF_NS`; §14.0 types and entry points incl. `mf_options`, `mf_opts_check` | DONE (§1; choices §2) |
| 2. `memfn/src/`: generic scalar row, K1 refs, `options.def` empty with accessor + parser; statics internal, externals via `MF_NS`; pcrec calls nothing | DONE (pcrec calls only `mf_options()`, for item 5) |
| 3. Makefile: libpcrec links the kit; `make`, `make strict` clean; nothing reaches an artifact | DONE (§6) |
| 4. C15 + C16 in `make test` with independent controls and witnesses; `PROVENANCE.md`; 0BSD SPDX | DONE (§4; section `test-memfn-link`) |
| 5. `--list-axes` `memfn` section, header + zero rows from `mf_options()`; spec hunk; every consumer selects; floor UNREACHED | DONE (§4, §5; consumers: axes_registry_check, run_axes, run_comments_axis; emit_sweep compares the dump whole, by design) |
| 6. CLAUDE.md for every touched dir; report entry in `docs/dev/lanes/CLAUDE.md` | DONE |
| Zero movers proved | §3 |
| Validation: make, strict, test-codegen, test-registry, test-cli, test-rxtsource, C15/C16 + witnesses, identity proof | §6 |
| NOT done (not charter): site manifest + C17, G2, the `--memfn=` CLI flag, a mech sabotage row for C15/C16 (in-script witnesses instead) | — |

## 8. For the kit session to decide

See §8 below the validation numbers.
