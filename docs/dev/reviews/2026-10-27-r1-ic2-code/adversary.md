# Critic ic2: adversary lens

Subject 864902a48 (lane/ic2), BASE 614d45eb3. The review-tree compiler
(worktrees/crit-ic2/build/pcrec) and the BASE compiler were NOT BUILT
during this lens's run (the box lock was held by queue jobs 621/622), so
every pcrec-side item below is SUSPECTED from source reading. The
gcc-side halves were run with gcc 15.2.0 on harmless inputs. No denied
file was opened.

## Findings

### ADV-1 (SUSPECTED; trust/doc; effort S; blast: every code segment)
The refusal table in src/parse/mod_code.c `code_invisible[]` (and spec
match_api.md §11.9¶3, design §2.4) leaves out U+061C ARABIC LETTER MARK.
U+061C is one of the twelve Unicode Bidi_Control code points, and the
Trojan Source (CVE-2021-42574) paper lists it next to LRM/RLM, which the
table does cover. The spec sentence promises to refuse "a Unicode
bidirectional control", so the stated set and the claim don't match.
gcc-side: a C file with U+061C in a string and in a comment compiles
with no warning under `gcc -Wall -Wextra -Wbidi-chars=any` (rc 0), so
gcc's own warning doesn't cover the gap either. To confirm on the pcrec
side: build, then compile `--allow-code=c` with a segment holding the
bytes D8 9C inside a C comment and expect it to be accepted. Fix: add
the row {0xD8,0x9C,0x9C,0x9C,0x061C} (a two-byte lead, so it needs a
two-byte arm) and name it in the spec list.

### ADV-2 (SUSPECTED; trust; effort S; blast: segments shown to a reviewer)
The C0 rule lets a lone carriage return (0x0D) through. gcc treats a
lone CR as a line end: probed, `// comment<CR>return 7;` inside a
function returns 7, so the text after the CR is compiled code and not
part of the comment. Plain terminal viewers (cat, head) show a CR as a
carriage return, so text after the CR overwrites the line before it on
screen. What a reviewer sees in a terminal can then differ from what
gcc compiles, which is the exact shape §11.9¶3 gives as its reason for
refusing characters. Suggested rule: refuse a CR not followed by LF (or
refuse CR altogether). Spec: §11.9¶3's allow-list names CR explicitly.

### ADV-3 (SUSPECTED; trust/doc; effort S-M; blast: segments)
"Invisible format character" covers only U+200B-U+200F, U+2060-U+2064
and U+FEFF. Code points gcc accepts that render as blank or as a line
break are not refused. Probed: U+3164 HANGUL FILLER is accepted as a C
identifier by gcc -Wall with no diagnostic, and U+2028 LINE SEPARATOR
inside a `//` comment stays part of the comment for gcc while some
viewers draw it as a new line. Either way the reader's view and the
compiled code can diverge. Either widen the set (Default_Ignorable_Code_Point
plus U+2028/U+2029/U+0085, or Unicode's own lists, in line with the
official-data-only rule) or narrow the spec's claim to the listed
ranges and say the user's review tooling covers the rest. Today the
claim is broader than the check.

### ADV-4 (SUSPECTED; answer/trust; effort M; blast: code in a LOCAL definition used through composition)
`code_segment` (src/gen/emit_code.c) computes the segment's `#line`
line and column by scanning `cx->pat[0 .. code_at)`. `code_at` is
recorded in `pcrec_codeport` as `code - cx->pat`, but when the segment
sits in a definition bound by `rc_bind` (src/parse/rxt_compose.c),
`cx->pat` at parse time is `def->pattern`. At emit time `cx->pat` is the
target's own pattern again. So for a same-file definition with code
that the target references: (a) the line count is taken over the wrong
buffer, and `#line` names the target's block line and the entry file
rather than the definition's line, against §11.9¶4's promise that a
diagnostic names the user's line; (b) if `code_at` is past the end of
the target's (shorter) pattern, the loop reads past that buffer. That is
an out-of-bounds read in the compiler, which `make asan` would catch
given a corpus case. To confirm: a .rxt with a named local block
holding a segment far into its text, and a short target pattern that
references it, compiled under --allow-code=c in the asan build.

### ADV-5 (SUSPECTED; doc; effort S; blast: describe-mode readers)
`--emit-facts` (a describe mode, given the code grant automatically by
src/dump/facts_dump.c) makes its `decisions` section by reading every
object-like line `#define <PREFIX>_...` / `PCREC_FEATURE_...` off the
whole finished `.c` buffer (`fd_decisions`), and the segment block is in
that buffer. A segment's text that holds such a line therefore shows up
as a decisions row, so the record would show values pcrec never decided.
The same applies to the stamps in a single-file artifact: a segment may
`#undef`/`#define` a kept stamp name (code_keep keeps `<PREFIX>_*`
live), and that includes `<PREFIX>_CODE_LANGS`, the disclosure stamp.
Spec §11.9 does not say that a segment can redefine the stamps and the
helpers that come after it, or that describe modes read segment text.
Fix: stop fd_decisions at the segment block's start, and add one
sentence to §11.9¶4 saying the text is unconfined C at file scope after
the matcher.

### ADV-6 (SUSPECTED; design/doc; effort S; blast: tests/ tree)
The harness grant is a FILE: any directory under tests/ whose
harness.manifest carries `allow-code c` grants code to every .rxt it
holds under a plain `make test` (run.sh `manifest_allow_code`).
§11.9¶8 / §5.1 say "Nothing else enables it ... not by a features list
or a file", and §5.7 says every section except the code section
compiles without the grant. Nothing I found limits which manifests may
carry the line. Suggested: one check that `allow-code` appears in
tests/code/ manifests only (an allow-list), plus a spec sentence that
the harness manifest is the test-suite invoker's grant.

### ADV-7 (CONFIRMED gcc-side; trust, low; effort S; blast: users who compile files with untrusted names)
`#line` writes the FILE operand through pcrec_sb_ctext's string frame,
which is ASCII in the artifact. gcc decodes those escapes and prints
the decoded name raw in its diagnostics. Probed with a `#line` name
holding octal-escaped control bytes: gcc's stderr carried the raw
control bytes. Before stage 2 a file name never reached gcc's output;
from now on a segment warning echoes it. Low severity, because pcrec's
own diagnostics already print the path raw. One spec sentence would do,
or refuse/replace control bytes in the `#line` name.

## PROBED-AND-HELD

- features vocabulary: `all` excludes RF_INVOKER_ONLY rows; a list
  naming code-c is refused by name (enabled.c); named sets go through
  find_module_bits, and the shipped std1 holds no code module. Held (read).
- config `pcrec` line: `--allow-code`/`--code-header` refused by
  rxt_source.c, and apply_target overwrites ts.opt.allow_code with the
  CLI's value anyway, so a file-set value would be dropped. Held (read).
- `target` lines resolve only blocks of the entry file, so a lib
  definition can never be a target's top-level pattern. Held (read).
- `include` fragments: the CLI never compiles fragment blocks. The
  harness grants only rxt_entries, the set built after the
  discovered-fragment subtraction, and parallel workers re-expand their
  own entry. Held (read; 1 fixture: tests/code/frag).
- code-header lines: compiled only with the language granted
  (compile.c), taken from the entry file only, and fragments cannot
  carry them. Held (read).
- Library: allow_code is the only door; pcrec_count_groups, the
  built-status probe, pcrec_emit_ir and pcrec_emit_facts open the
  describe mask and write no C. Held (read), except ADV-5.
- pcrec-bench: no loader or config sets --allow-code; pcrec flags come
  from configs.toml plus $PCREC_LOCAL_FLAGS (the invoker). Held (grep).
- gcc probes run: 5 (CR line end, U+2028 in comment, U+3164 identifier,
  U+061C under -Wbidi-chars=any, #line name echo).
- NOT RUN (compiler unbuilt): every pcrec-side repro, the
  --pattern-esc tag-byte production, and the --help mode-table walk.
