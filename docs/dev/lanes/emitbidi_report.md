# emitbidi report -- [EMIT-BIDI] one C-text escaper with a context flag

Lane emitbidi (sonnet), 2026-10-25, branch lane/emitbidi from main b8ddfe45b. Nothing was built or run
(box rule); every claim below about behaviour is from reading, plus `gcc -fsyntax-only -Wall -Wextra` on
`core/sb.c`, `gen/emit_dfa.c`, `gen/emit_vm.c` (clean) and `gen/memfn_sites.c` (clean). Validation is OWED
and is the queued job `docs/dev/lanes/emitbidi_job`.

PREMISE TEST: true as briefed. The map-comment loop copied everything but newline and the two hazard pairs raw
(its own comment recorded that routing it through the shared escaper "moved 115 artifacts" and was refused for
identity; the abi bump retires that constraint).

## The function and its table

`pcrec_sb_ctext(StrBuf *, const unsigned char *s, size_t n, PcrecCtext ctx)` in `src/core/sb.c`, declared in
`core/internal.h` (the old `pcrec_sb_cstr` block, rewritten as the contract). Three frames, one more than briefed:

- `PCREC_CTEXT_COMMENT` -- block comment.
- `PCREC_CTEXT_COMMENT_QUOTED` -- the same plus `"` and `\` numbered. Needed because the DFA state legend's
  `extra_escape` was the only `emit_comment_safe_byte` caller with one; folded into the table rather than left to
  the caller. Legend now builds its example into a local `unsigned char[LEGEND_MAX_EXAMPLE]` and makes one call.
- `PCREC_CTEXT_STRING` -- string-literal body.

Declared first-match row table (`ctext_rows[]`: frame set, required previous SOURCE byte or -1, byte, text) plus a
per-frame numeric spelling (`ctext_num[]`: `\xNN`, `\xNN`, `\NNN`). Rows: `*` then `/` and `/` then `*` split
(look BEHIND, each byte consumed once); `"` `\` as `\x22` `\x5c` in the quoted frame; `"` `\` `?` backslash-escaped
in the string frame; `\n \t \r` named in all three. Reasoning comments are condensed at the declaration in
`core/internal.h`. Look-behind is internal to one call (no `*prevp` threading): every caller already had one
contiguous buffer.

## Sites and dispositions

Deleted (callers moved): `emit_comment_safe_byte` (emit_dfa.c); `emit_c_string_literal` static (the exported
`pcrec_emit_c_string_literal` stays as the quote-wrapping caller of the string frame, 9 callers unchanged);
`pcrec_sb_cstr` (sb.c); the map-comment inline loop; `legend_extra_escape`; `vm_var_word_bytes` (emit_vm.c).

| site | disposition |
|---|---|
| `emit_pattern_comment` (provenance, .c and .h) | routed, COMMENT |
| orientation block pattern echo (emit_dfa.c ~14790, the bug) | routed, COMMENT (every non-printable-ASCII byte now escaped) |
| `pcrec_emit_comment_bytes` (used by emit_subst.c:585 template echo) | routed, COMMENT |
| `req_note_run` four `[OPT-REQPOS]`/`[K66]` run echoes | routed, COMMENT |
| `emit_state_legend` example | routed, COMMENT_QUOTED |
| `.pattern =` (emit_dfa.c:3319), `.engine_why`, names/scope (3121-3124), opt name, value, emit_subst.c template/vrefs/names, emit_vm.c:11119 | routed (via `pcrec_emit_c_string_literal`), STRING |
| `memfn_sites.c` `sink_cstr` (the kit's run-compare constants) | routed, STRING; kit output moves for `\n \t \r` only (octal -> named), same string value |
| `emit_vm.c` `vm_var_word_bytes` (VM `${...}` default-word literal) | routed, STRING; was hex-plus-`""`, now octal (same value) |
| `emit_vm.c` ~12432 `${...}` expansion comment (`pcrec_varexp_render`) | FOUND UNESCAPED (raw word bytes in a block comment: `*/`, newline, non-ASCII); routed, COMMENT. A second latent instance of the same bug class |
| `emit_vm.c` 8879 `vm_lit_describe`, 9222 class describe | left: `--emit-ir`/role text, already printable-ASCII-or-`\xNN` with `\` and `'` numbered; not a C-comment echo of raw bytes. Role text lands in `//` comments but is pure ASCII and `\`-escaped |
| `emit_vm.c` 12228 | that was `vm_var_word_bytes` (above), not a byte constant |
| `syntax_dump.c:208`, `sb.c:476` (`sb_frame_byte`) | different contract (TSV frames), untouched as briefed |
| `emit_vm.c:11107` `Engine: vm (forced by: %s)` / `fit.why` | left: fixed phrase + `at pattern offset N` (select_engine.c `why_text`), no pattern bytes |
| feature-set comment, `emit_compound.c` row/role, `.engine` comment, prefix | left: pcrec's own fixed vocabulary / validated identifier |
| `pcrec_emit_legend_byte` (legend `'c'`/number) | left: printable or decimal, never a raw byte |
| memfn/src (read-only) | only `runcmp.c` calls the sink's `cstr` (constants); no kit site echoes user text into a comment. Nothing to report beyond the `\n\t\r` byte move above |

No other site in src/, cli/ found writing user bytes into C text (grepped `\\x%02x`, `\\%03o`, `cx->pat`,
`Pattern:`/`Template:`, comment-bearing `%s` printfs in src/gen). Residual risk: a comment `%s` site I did not
recognise as user-derived.

## abi 84 -> 86

Readers found by grep and edited: `PCREC_ARTIFACT_ABI` (emit_dfa.c); `ABI_EXPECT` (tests/codegen/run_codegen_tests.sh);
S693 BEFORE/AFTER (AFTER = 84, the parent's number) + header note; docs/spec/match_api.md (the emitted
`PCREC_RX_ABI_H` guard sample x3 at 178-182, the rx_info table row 1584, 6¶17); docs/dev/history/abi_changelog.md
(new top entry, notes 85 reserved by the kit's S3); the identity gate (B) pin `FILEPIN` in
tests/codegen/run_recursion_identity.sh set to `dba52b4b4` (my last src commit; the manager re-pins to the merge
per the self-pin convention). Comment-only mentions of 84 (NOTES, lane reports, run_resource/cpset_structure
history comments) are records, left. Not re-measured (needs a build): run_resource_tests.sh and run_cpset_structure.sh
byte rows (abi digits keep their width; only patterns with tab/newline/CR/non-ASCII bytes move) -- the day-slot
`make test` is where they would show.

Spec hunk: match_api.md 6¶23 gains the promise that echoed caller text is pure ASCII (numbers, named `\n\t\r`,
split comment pairs). src/gen/CLAUDE.md (the K79 line now names `pcrec_sb_ctext`; ASCII-only rule points at the
check), src/core/NOTES.md (sb.c role line), tests/codegen/CLAUDE.md (new check), lanes/NOTES.md index entry.

## The check and sabotages

`tests/codegen/run_ctext_ascii.sh` (in `test-codegen`'s group, Makefile): pattern = U+200E U+200F `x*/y/*z"\\"a??(b)` TAB
under `-e utf8`, default and `-fcomments`, auto and forced VM; per label: .c/.h pure ASCII, compiles under
`-Wall -Wextra -Werror -Wbidi-chars=any`, and `.pattern` decodes (python3 -I) to the original bytes. 12 checks.
Residual risk: never run; the pattern's acceptance by `--features all -e utf8` and `--engine=vm` is assumed.
Sabotages (ids from range): S1620 (comment frame prints bytes >= 0x80 raw -> ascii + compile arms must go RED),
S1621 (the string frame's `?` row removed -> `??(` trigraph, compile arm RED). Both BEFORE strings verified to occur
exactly once in sb.c. Results OWED (not run).

## Owed run

`docs/dev/lanes/emitbidi_job`: `--ready` exits 75 until 2026-10-26 10:00 local (verified); `--dry-run` prints cap 14400,
patience 54000 and expects whose strings I verified in the scripts: `strict: whole tree compiles clean` (Makefile strict),
`run_group: 19/19 scripts passed` (run_group.sh; 19 = 18 + mine), `checks passed: 12` (the new check),
`run_axes.sh: all axes answer-identical` (run_axes.sh:2295), `== mech run COMPLETE: 2 rows` (run_sabotage_matrix.sh:3790),
`sections ran: 79/79` (79 counted in TEST_SECTIONS). Not validated through `boxqueue add`'s own dry-run grammar
(adding enqueues); the manager's `add` will refuse it if a declaration is off. The mech stage uses `git archive HEAD`, so
the lane must stay committed.

## Notes for the manager

- Behaviour change worth knowing: a comment now shows `\n \t \r` where it showed `\x0a \x09 \x0d`, and a UTF-8 pattern
  in the orientation block shows `\xe2\x80\x8f`-style bytes (previously raw). Intended (ASCII-only rule).
- I took no D/K/I/R number; none seemed needed. One judgement the manager may want to rule: I added a third frame
  (COMMENT_QUOTED) instead of keeping a caller-side predicate.
- Frame for `${...}` expansion comment fix is a find outside the brief's named sites; it moves VM `${...}` artifacts.

## STATE AT HANDOFF

Rulings file `emitbidi_rulings.md`: read at start (no entries); last entry applied: none. Branch lane/emitbidi, all
committed; last src commit `dba52b4b4`. Not built, not run. Owed: the job above (build, strict, test-codegen, new check,
`-fcomments` axis, S1620/S1621, full make test), then the manager's merge, FILEPIN re-pin and renumbering (85/86) at landing.
