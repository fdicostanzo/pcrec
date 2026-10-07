# Hook census (tree worktrees/memfn, lane/memfn-rowcon)

Method: static read of every `mf_hooks` construction, then 14 compiles of
`build/pcrec` (of 60 allowed).

## Where pcrec builds hooks

Only four sites build an `mf_hooks`. The tree has no other `.s =`, `.lo =`,
`.n =`, `.cursor`, `.more`, `.peek`, `.on_cand`, `.member`, `.floor`, `.miss`
or `.count` hook initializer in `src/gen/`. Those hooks are never set by
pcrec today, so they are NULL at every site.

| # | Site | Where |
|---|------|-------|
| 1 | PRE define (`req_site_define`) | src/gen/emit_dfa.c:1490 |
| 2 | PRE use (`pcrec_emit_req_byte_check`) | src/gen/emit_dfa.c:1552 |
| 3 | OFS define (`ofs_site_define`) | src/gen/emit_dfa.c:6208 |
| 4 | OFS call (`pf_ofs_call`) | src/gen/emit_dfa.c:6229 |
| 5 | VMRUN (`vm_run_compare`) | src/gen/emit_vm.c:4431 |

## Table

| Site | Hook | Text / variants | Class | Evidence |
|---|---|---|---|---|
| PRE use | s | `subjvar`. Every caller passes the literal `"subject"` (3 callers, no other variant). | PRIMARY (identifier) | emit_dfa.c:8655, 8948; emit_vm.c:13231 |
| PRE use | n | `lenvar`, always the literal `"subject_length"`. | PRIMARY | same 3 callers |
| PRE use | lo | `posvar`, always the literal `"search_from"` (the DFA forward, DFA reverse-entry and VM entries alike). | PRIMARY | same 3 callers |
| PRE use | result | literal `"handoff_position"`, an lvalue identifier. | PRIMARY | emit_dfa.c:1554 |
| PRE use | result_decl | literal `"size_t "`, a declaration prefix. | PRIMARY (declaration, not an expression) | emit_dfa.c:1555 |
| PRE use | on_miss | literal `REQ_ON_MISS` = `"return 0;"`: one statement, no braces, no bare break/continue. The site states `on_miss_leaves = 1`. | SAFE statement | emit_dfa.c:1412, 1554, 1487 |
| PRE use | indent | literal `"    "` (4 spaces), from all 3 callers. | n/a (whitespace) | same callers |
| PRE use | note | `req_site_note` writes a comment through the sink. It is pcrec text emitted as a comment, not pasted inside an expression. | n/a (comment writer) | emit_dfa.c:1396-1408 |
| PRE use | comment_tier | `PCREC_CMT_NONESSENTIAL` | n/a | emit_dfa.c:1556 |
| PRE define | fn_name | `<prefix>_reqrun` or `<prefix>_reqrun_whole`, from `dfa_fragf("%s_reqrun[_whole]", cx->opt->prefix)`. | PRIMARY (identifier) | emit_dfa.c:1051-1054, 1383-1387 |
| PRE define | note_tag | literal `"[K66]"` or `"[OPT-REQPOS]"`, in a comment. | n/a (comment text; contains no `*/`) | emit_dfa.c:1390-1394 |
| PRE define | s, n, lo, result, on_miss, ... | NOT SET at define. The hooks carry only `fn_name`, `note_tag`, `comment_tier` and `u`. | n/a | emit_dfa.c:1490-1493 |
| OFS define | fn_name | `<prefix>_ofsskip`, from `dfa_fragf("%s_ofsskip", f->p)`. | PRIMARY | emit_dfa.c:6176-6183 |
| OFS define / call | table_name | `<prefix>_ofs_k<K>`, K a decimal int, from `dfa_fragf("%s_ofs_k%d")`. | PRIMARY | emit_dfa.c:6132-6135, 6186-6191 |
| OFS call | s | literal `"subject"` | PRIMARY | emit_dfa.c:6230 |
| OFS call | n | literal `"subject_length"` | PRIMARY | emit_dfa.c:6230 |
| OFS call | lo | literal `"scan_position"` | PRIMARY | emit_dfa.c:6230 |
| VMRUN | s | literal `"subject"` | PRIMARY | emit_vm.c:4432 |
| VMRUN | n | literal `"subject_length"` | PRIMARY | emit_vm.c:4432 |
| VMRUN | lo | literal `"scan_position"` | PRIMARY | emit_vm.c:4432 |
| VMRUN | everything else | not set. VM sites are EXPR/BOOL, with no statement hooks. The run-term `off` is an int in the site, not a hook text. | n/a | emit_vm.c:4406-4416 |

Hooks never set by any site: floor, miss, count, cursor, step, more, peek,
on_cand, member. They are NULL at every site, so no variants are possible.
`floor` is NULL, which the kit reads as `"0"`.

## Prefix dependence (question 4)

Only the names (`fn_name`, `table_name`) depend on `-p PREFIX`. They have the
form `<prefix>_reqrun`, `<prefix>_reqrun_whole`, `<prefix>_ofsskip` and
`<prefix>_ofs_k<N>`. `compile.c:1497` rejects any prefix that is not a C
identifier of limited length ("invalid symbol prefix (must be a C identifier,
<= N chars)"). So a legal prefix can only make these names longer or
reserved-looking (for example `-p _` gives `__reqrun`, which compiles but is a
reserved identifier). It cannot make them risky. The value hooks
(s, n, lo, result, on_miss) never contain the prefix.

## Latent notes (not risks today)

- The kit composes `lo + <int offset>` itself. Examples are the emitted
  `subject + scan_position + 1` and `q_w2(subject + cand + 1)`. This is
  safe only because `lo` and `s` are bare identifiers at every site. If a
  future site passed an unparenthesized sum or ternary as `lo`, `s` or `n`,
  the kit's `lo + off` would re-associate. No such site exists.
- `on_miss` is a bare single `return` statement. It would need a
  brace-wrap only if a future on_miss held an `if/else` or a bare
  `break`/`continue`. None does today.

## Confirmed by compile (emitted lines)

All with `build/pcrec -p PFX --pattern P -o file`.

1. PRE use, `-p rx`, `(?:ab|cd)hello`: `size_t handoff_position = rx_reqrun(subject, subject_length, search_from);` then `if (handoff_position >= subject_length) return 0;`. This confirms s, n, lo, result, result_decl and on_miss verbatim.
2. PRE use as a bare check, `-p Pre_9x`, `foo[0-9]+bar`: `if (Pre_9x_reqrun(subject, subject_length, search_from) >= subject_length) return 0;`. The prefix appears only in the function name.
3. PRE, `-p a`, `x.{3}needle`: `size_t handoff_position = a_reqrun(subject, subject_length, search_from);`
4. PRE, `-p _`, `x.{3}needle`: `size_t handoff_position = __reqrun(subject, subject_length, search_from);`. The odd prefix stays an identifier.
5. OFS call, `-p rx`, `(?:ab|cd)hello`: `size_t cand = rx_ofsskip(subject, subject_length, scan_position, rx_ofs_k0);`. It uses the table name `rx_ofs_k0`, and the definition is at line 46.
6. OFS define, same artifact: `static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos, const unsigned char *rx_ofs_k0)`
7. VMRUN, `-p q --engine=vm`, `(ab|cd)xyz[0-9]`: `if (scan_position + 3 <= subject_length && q_w2(subject + scan_position) == q_w2("xy") && q_w2(subject + scan_position + 1) == q_w2("yz")) { scan_position += 3; goto q_L11; }`. The guard is pcrec's, and the run compare is the kit's with `lo` = `scan_position`.
8. VMRUN, `-p q --engine=vm`, `x(a|b)+hello`: `q_w4(subject + scan_position) == q_w4("hell") && q_w4(subject + scan_position + 1) == q_w4("ello")`
9. PRE run block in VM-routed text, `-p rx`: `static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)` followed by `rx_w4(subject + cand) == rx_w4("hell") && ...`.
10. `-p Pre_9x`: the helper `Pre_9x_w2` and the fn name share one stem, with no other prefix-derived text.

Several attempted patterns (`\b`, `(?=`, `\1`) were refused by pcrec with
"requires module ...". They are not evidence either way.

## Verdict

NO RISKY HOOK FOUND. Every value hook pcrec passes today (s, n, lo, result,
result_decl, indent) is a string literal that is a bare identifier. The one
statement hook, `on_miss`, is the single statement `return 0;`. The names
(`fn_name`, `table_name`) are `<prefix>_<suffix>` identifiers, and a legal
prefix cannot make them risky. Unset hooks are NULL.
