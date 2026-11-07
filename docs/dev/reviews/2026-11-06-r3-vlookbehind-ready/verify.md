# verify (vlb4 verifier; build tree worktrees/crit-vlb4 @80341284e, design @2ef0d1818)

Paths are relative to /home/pcrec/projects/pcrec/worktrees/crit-vlb4 unless stated. Scratch: /var/tmp/pcrec-pcrec/scratch/crit-vlb4/verify/.

## FIXIND-1: HOLDS (structure re-run; the rule-(b) red is a literal reading of the design text, no rule exists yet to run)
- Two byte rows define `$_span_match_caseless`: src/enc/enc_byte.c:162 (decls_bref_ci_doc, SPAN_CASELESS) and :307 (the UCP row's def; sites_byte at :328-331 lists both ids). enc.h:230-233: UCP "Defines the SAME `$_span_match_caseless` symbol as SPAN_CASELESS and is in the mask INSTEAD of it".
- Shared helper names: enc_byte.c:294 `$_span_ci_fold` and :297 `$_span_ci_fold_pairs` vs enc_utf8.c:164 `$_span_ci_fold_pairs[][2]`, :173 `$_span_ci_fold`. Probe: `build/pcrec --features all -e byte|utf8 -p b -o u_$e.c --pattern '(*UCP)(?i)(a+)\1'` -> byte artifact defines span_ci_fold_pairs/span_ci_fold/span_match_caseless (UCP entry); utf8 artifact defines the same three names (SPAN_CASELESS entry).
- Within ONE artifact symbol->entry is a function (mask holds one of the two); it is not across the two backends' lists, and the design's rule (b) (design.md:1466-1469, "admits one side only where the reader lists the entry in that backend alone") admits UCP (byte-only) but SPAN_CASELESS is in both lists, so a byte-UCP vs utf8-SPAN_CASELESS pair is not admitted. Literal reading: red. Block 718 (`(*UCP)(?i)(a+)\1`) is the pair (see FIXIND-2).
- Pre-existing SIG_RE half: run_encoding_checks.sh:455 has `static\s+unsigned` and `static\s+const\s+unsigned` followed by `\s+rx_`; the byte heads are `static unsigned char b_span_ci_fold(` (enc_byte.c:294) and `static const unsigned char ..._pairs` (enc.c latin1 table), so `unsigned char` is not matched. HOLDS textually; the full-sweep STRICT-bucket divergence was not re-run (needs ENC_MAX_BLOCKS=0 sweep): not verified.

## FIXIND-2: HOLDS
- Extractor lines 95-162 of tests/codegen/run_encoding_checks.sh run verbatim with maxb=0: `ASCII_BLOCKS=4843`. Exactly one block with `(*UCP`: index 718, `(*UCP)(?i)(a+)\1`. Default `ENC_MAX_BLOCKS=250` (line 70), the slice takes the first 250 emitted blocks, so 718 is outside it.
- No `ucp` text anywhere in the script's compile invocations (`grep -n ucp` is empty), so only the `(*UCP)` verb could reach the byte UCP entry. Explicit list (line ~1531): `a*`, `(?i)(?<=a)(b)\1x`, `(?<=a)(b)\1x`, `^${v}$`, `(?i)(?<=ab)(b)\1x`: none UCP. Design item 4 (design.md:1478-1480) adds only `(?<=a{1,2})x`. So a derived floor "every entry the reader lists is reached" is red on the default slice. (Whether the floor is checked per run with ENC_MAX_BLOCKS default is the design's own wording "across the run".)

## FIXIND-3: HOLDS (all four sub-claims), but one line citation is wrong
- Line number: the exact guard is `if [ "$resid_backdecl" -ne 7 ]` at tests/codegen/run_codegen_tests.sh:1599 (READY-2 is right). FIXIND-3's 1606 is the line `fi` after the ok message; wrong cite, right fact.
- writers.tsv:29 A4 hand map (verified quote above in the finding); A6 at :31 is `(forward|reverse|anchored|retry)_(step|...)`, no `fwd`. Census: run_partlayout.py:479-491 flags `unlisted` for any attribute not matching a row, over `pop` (the frozen tests/partlayout/population.txt, 395 lines). Population lookbehinds: 52; the only `{n,m}` match among them is `\W{1,2}(?<=\b)a*` where the quantifier is outside the lookbehind, so no range lookbehind -> latent, as claimed.
- sec_seam: run_partlayout.py:538-539 regex `rx_(?:span_match\w*|back_step|decode|bref_match\w*)` has no fwd_step: coverage gap confirmed.
- run_codegen_tests.sh:1665-1673 c1 arm: fixtures table ends `expvar` (7 rows) and `[ "$exp_n" -ne 7 ]`; explb/exputflb are `(?<=ab)c`, none a range lookbehind. Confirmed.
- resid_backdecl counting: line 1421 `[ "$nback" -gt 0 ] && resid_backdecl=$((resid_backdecl + 1))`; design.md:1831-1833 declares `residlbrange` with `back_step:3` plus a utf8 twin -> 7+2 = 9 vs literal 7. The design never states the edit (design.md:1515-1519 says only "existing fixtures are unchanged").
- Not re-checked: the "safe" run_dfa_uniform_fold.sh note.

## FIXIND-4, -5: not in my assignment.

## FIXIND-6: HOLDS (design-level, low)
- src/enc/enc.c:156-157: `if (t->id == PCREC_ENCE_SPAN_CASELESS_UCP) enc_emit_latin1_fold_table(sb, prefix);` inside enc_emit_inline_defs. Design item 1 (design.md:1456-1459) says the new function carries "what enc.c itself emits beside a row (today only SPAN_CASELESS_UCP's ... table)" "beside the code", which is a second statement of the same condition. Fact holds; severity is a judgment.

## READY-1: HOLDS
- tests/mech/sabotages/S133_backstep_inlined.sh SAB_BEFORE is 6 lines: `pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);`, the `vm_ev(... "lookbehind: the ENCODING SEAM'\''s back-step, %d character%s" ...)` note, and `pcrec_vm_b_branch(v->sb, vm_condf(v, "scan_position == %s_BACK_STEP_NONE", v->p), pcrec_vm_tgt_fail());`. S134 (S134_backstep_sentinel_unchecked.sh) anchors the same 2-line branch with `pcrec_vm_tgt_fail()`.
- Design says (design.md:1368-1371, 1815, 1822-1827) S133's SAB_BEFORE is "the exact line" `pcrec_vm_b_seek(..., k);` and S133 "keeps SAB_COUNT=1"; the range row's lo_i sentinel goes to `L_n_i` (design.md:518), not tgt_fail, and the note text changes (design.md:899, "NEAREST start"). The file's 6-line block therefore cannot stay byte-identical across both rows; U8 (design.md:1679) names "S133/S134 twins" but not re-cutting the existing SAB_BEFORE/AFTER and SAB_DOC_FIGUREs. (Whether the build keeps COUNT=1 depends on how the shared emission is written; not predictable here.)

## READY-2: HOLDS
- run_codegen_tests.sh:1599 `-ne 7`; header sentence "one per top-level branch per lookbehind" at :1594-1597; counted per fixture with back_step in `decl` (:1417-1421). residlbrange + utf8 twin: 9 (see FIXIND-3). Design lists only `INLINE_RESID` for [M5-SEAM] (design.md:1515-1519), not U6 either (design.md:1677).

## READY-3: HOLDS (run); path in the finding is wrong
- The file is docs/design/eng_brep_measurements/probes/pcre2_ctypes.py (NOT tests/backrefs/); line 141-142 `if isinstance(pattern, str): pattern = pattern.encode("latin-1")`. Command (scratch p3.py, `python3 -I`, probes dir on sys.path): `P.Compiled('(?<=é|bc)x', P.PCRE2_UTF)` -> `Pcre2Error pcre2_compile failed at offset 4: UTF-8 error: byte 2 top bits not 0x80`; `P.Compiled('(?<=a|bc)x', P.PCRE2_UTF)` compiles.
- Consequence: tests/backrefs/bref_oracle.py:81 `rx = P.Compiled(pat)` (no options at all) with pat from a text-mode read; `except Exception` -> `sys.exit(2)` (:85). For chars above U+FF `.encode("latin-1")` raises UnicodeEncodeError, also caught -> exit 2. Module's only UTF/context constants: `['PCRE2_UTF']` (dir() filter on UTF/INVALID/ontext): no MATCH_INVALID_UTF, no compile context. Precedent: tests/axes/utfcheck_arm.py:48 `pat.encode("utf-8", "surrogateescape")`. The design (design.md:1611) says the binding "already takes compile options": true for options, silent on the str encoding. tests/backrefs/CLAUDE.md lists the oracle files; not edited by U6 (design.md:1677 names CLAUDE.md files for codegen/lookaround/testing only). Not verified: the claim "gate 3's max_varlookbehind=0 unaskable" (needs a compile-context API; consistent with the absent constants but not tested further).

## READY-5: HOLDS
- Makefile:835-837 `test-encoding-checks: all` -> `bash tests/codegen/run_encoding_checks.sh`; Makefile:685-688 `test-codegen` runs run_codegen_tests.sh and siblings; run_encoding_checks.sh appears in the Makefile only at :837. Design.md:1661 says "`make test-codegen`'s `run_encoding_checks.sh`".

## READY-6: HOLDS
- Totals: `const int nguard_total = v->nguard, nlow_total = v->nlow;` at emit_vm.c:10600 inside `vm_plan` (:10515), not pcrec_emit_vm (:14124). VmFrame `const VmFrame fr = {...}` at :13056 inside `vm_emit_search_body` (:12819). Back-step mask OR `v->enc_mask |= PCREC_ENCE_BACK_STEP;` at :7397 inside `vm_look_behind` (:7363); it is not in `vm_look_behind_branch` (:7117, called at :7413), contrary to U5 (design.md:1676) and design.md:1419-1421, nor in `vm_look`. Design.md:827 and :1385 say `pcrec_emit_vm` for both totals and VmFrame.

## READY-7: HOLDS
- src/core/internal.h:1858 `const int *widths;` (comment 1834-1870); readers: mod_lookaround.c:395 `la_lb_raise(Ctx*, const int *w, int nbr)`, :427 fix_widths, :451 store, :586-633 hook, emit_vm.c:7122 `const int k = a->u.look.widths[i];`, vm_count_slots_look (:3038) and vm_cost_look (:2858) exist. U1 (design.md:1672) names none of internal.h, the widths storage change ("a pair per branch", design.md:773, :1043) or the readers. LA_MSG_MAX deletion/keeping mentioned at design.md:1128 only as a sentence; its comment is not assigned in U1. (Which readers truly need change was not individually traced.)

## READY-8: PARTLY (cells and guard cited correctly; the +N and the S136 figure not run)
- run_lookaround_diff.sh:270 `if [ "$NPO" -ne 69 ]`, NPO counts `# pcre2-only` answer-bearing blocks. tests/lookaround/refused.rxt:104/220/228 are `pattern (?<=(a|bc))x`, `(?<!(a|bc))x`, `(?<*(a|bc))x` with `perr`; the header (:98-103) records libpcre2 accepts and python refuses. Design.md:1908 makes `(?<=(a|bc))x` a match example, so these flip; the design never mentions the 69 guard or pcre2-only blocks. That the flipped cells become `# pcre2-only` (hence NPO moves) is inferred, not executed (no make). S136 figure: not verified.

## READY-9: HOLDS
- docs/design/stream/arev.md:341 (the critic gave no dir): "a `VmSeekKind` member ... (today's four are slot-restore, advance, back-step, span commit)". src/gen/vm_stmt.h:131-136 `VmSeek` has exactly four members today (SPAN_COMMIT, RESTORE, ADVANCE, BACKSTEP); stage 1 adds VSK_STEP_CHAR (design.md:1354) -> five. tests/codegen/run_encoding_checks.sh:2098-2100 "the boundary rule is now spelled TWICE per backend" and :2105 "that same artifact's linked `next_pos`"; the design makes a third spelling and an #include-d artifact (design.md:1500 ff.). Both are doc fixes.

## Unassigned / not verified
READY-4/10/11 and FIXIND-4/5 were not in the assignment.

VERIFY COMPLETE
