# TPL lens — template forms vs spec and pcre2_substitute (critic round subst, 2026-10-24)
SUBJECT 1222b31be. Findings appended as found.

(Probe kit: /tmp/claude-1001/crit-subst/tpl/src/{h.py,drv.c}: compiles rx + subst artifacts with $W/build/pcrec, drives
rx_subst_replace_all over the by-name helper's map (flags 0 and RX_SUBST_STRICT), and runs libpcre2-8 10.46's
pcre2_substitute GLOBAL (+UNSET_EMPTY unless strict, +EXTENDED for module subst-extended) on the same inputs.)

### TPL-1  The encoding -1 rule ignores escapes: an all-ASCII `subst-extended` template whose escapes yield a byte above 0x7F is accepted against an rx of the other encoding and renders other bytes than PCRE2
- status: CONFIRMED. Template compiled `pcrec --features subst-extended -e utf8 -p s --subst '<\xe9>'` has `encoding = -1`
  in its record (same for `<\x{e9}>`, `<\o{351}>`, `<\x{100}>`, `<\N{U+41}>`), so `pcrec_subst_check` accepts a `-e byte`
  rx (`(b)`) and replace-all over "ab" renders `a<\xc3\xa9>`; pcre2_substitute (non-UTF, EXTENDED) renders `a<\xe9>`
  (and refuses `\x{100}` / `\N{U+41}` with -57, which pcrec renders as `\xc4\x80` / `A`). The reverse: `<\xe9>` compiled
  `-e byte` (encoding -1) is accepted with a `-e utf8` rx and emits the lone byte 0xE9 (ill-formed UTF-8 output) where
  PCRE2 (UTF) renders `\xc3\xa9`. Repro kit: /tmp/claude-1001/crit-subst/tpl/c6.json cases e1-e6 via src/h.py.
- severity: answer
- effort: S (set the record's encoding when an escape's value is above 0x7F, or for any `\x`/`\o`/`\N` escape); blast
  radius: any extended template with a numeric escape >= 0x80 shared across encodings — silently wrong bytes, the very
  mixing §2¶5 promises to refuse "before any output".
- where: src/gen/emit_subst.c:1124-1133 `subst_bind_encoding` (its comment names "escapes above 0x7F" but it scans only the template TEXT bytes; scanning the parsed literal bytes would fix it); subst_api.md §2¶5 ("an all-ASCII template without case forcing reads the same in every encoding" is false under
  §2¶10's escapes); src/parse/subst_template.c / src/gen/emit_subst.c where the record's `encoding` is chosen.
- body: §2¶10 itself says `\xe9` "is the two bytes of é there [utf8], one byte under byte" — the template's meaning
  depends on the encoding, so the -1 exemption must not apply. The record is the only guard (§3¶8); there is no other
  place a caller would learn of the mismatch.

### TPL-2  §2¶14a is ambiguous about WHERE a byte "begins a well-formed character": pcrec judges per source piece, so ill-formed fragments from two sources join into a well-formed character that a case region leaves unmapped
- status: CONFIRMED (pcrec-only territory, §9 row 19). Pattern `x` (`-e utf8`), template `\U$`$'` (`-e utf8 --features
  subst-extended`), subject `\xc3 x \xa9`: the replacement is `\xc3\xa9` — a well-formed `é` in the OUTPUT, not upper-cased
  (a stream reading of §2¶14a gives `\xc3\x89` = `É`). Each byte is ill-formed within its own source (`$`` = `\xc3`,
  `$'` = `\xa9`), which is what the element tests. Kit: c4.json case v9.
- severity: doc
- effort: S (one sentence: "a byte that does not begin a well-formed character WITHIN THE PIECE IT COMES FROM"); blast
  radius: readers/test authors of §2¶14a; no oracle exists, so the spec is the only definition.
- where: subst_api.md §2¶14a.
- body: §2¶13 defines "a character is anything produced", i.e. output order, which invites the stream reading; the
  implementation's per-source reading is the sane one (it never lets a group's bytes change meaning by context) and
  should be the stated one.

### TPL-3  A refusal's "template offset" has no stated meaning, and pcrec uses two (construct start vs fault point)
- status: CONFIRMED. Construct start: `${1 }` → 0, `${g` → 0, `${2-x}` → 0, `\x{110000}` → 0, `\o{8}` → 0, `${65536}` → 0,
  name > 128 bytes → 1 (the `$`). Fault point: `${ 1}` → 2, `${2:-x` → 6, `${2:-${}` → 7, `${2:-\Qa}` → 5 (the `\Q`),
  nesting > 10 → 50 (the 11th `${`), ill-formed UTF-8 → the bad byte. libpcre2 10.46 reports the fault point
  throughout (3, 3, 3, 9, 3, 3, 132 ...). Offsets are byte offsets in both (checked across 2-byte `é`).
- severity: doc
- effort: S (say "the offset of the construct that is refused" in §2¶4, or move the brace/escape cases to the fault
  point); blast radius: tooling that points at a template error; D26 makes wording free but §2¶4 promises an offset.
- where: subst_api.md §2¶4; src/parse/subst_template.c error sites.

### TPL-4  Template compile memory is ~155 bytes of RSS per template byte, with no template-size limit
- status: CONFIRMED. `--subst-file` of N bytes of `a`: 1 MB → 157 MB RSS, 4 MB → 620 MB RSS (0.3 s); `$$`×1M (2 MB)
  → 311 MB; `$1`×200k → 200 001 pieces, 19.8 MB of C. limits.def has no template-length or piece-count row
  (only PCREC_MAX_TEMPLATE_GROUP / _NESTING).
- severity: size
- effort: S-M (a PCREC_MAX_TEMPLATE_LEN / piece cap with a refusal, or find the per-byte arena cost); blast radius: a
  build step fed a large or hostile template file; outputs are correct.
- where: src/core/limits.def (no row); the per-byte cost site not located (SUSPECTED: per-literal-byte arena/strbuf growth in the parser or emitter).
- body: low priority (templates are small in practice); the pattern side carries explicit compile budgets, the template
  side none. The emitted text and the rendered output of these huge templates were correct (3000×`$0` matched libpcre2).

## PROBED-AND-HELD
Each case: pcrec replace-all (flags 0 and STRICT, by-name helper map) vs pcre2_substitute GLOBAL (+UNSET_EMPTY / strict,
+EXTENDED), bytes identical or both errors; compile refusals compared with libpcre2's error for the same template.
- Core module (66 cases, c1.json): empty matches, unset vs set-empty groups, greedy `$12`/`$gx`, `${01}`/`$00`/22 leading
  zeros, `${65535}` (MISSING_REF) vs `${65536}`/`$4294967297`/`${18446744073709551617}`/`$000...065536` (refused, no wrap),
  `${ 1}` `${1 }` `${}` `${-1}` `${+1}` `${1g}`, `$_`/`${_}`/`$_a`, `$&&`, `${&}` (refused, as PCRE2 -35), `$` at end
  everywhere incl. inside conditional text, `$*MARK`/`${*MARK}`/`$*`/`${*}` (§9 row 17), `(?J)` duplicate names (first
  that participated), UTF-8 names incl. \p{Nd}/Lm/Mn/No/ZWNJ/U+00B7 boundaries, 128/129-byte names, high bytes under byte.
- subst-extended (100 cases, c2.json): every conditional form + refused operators, `:` and `{`/`}` handling, `\Q` in
  text (protects, open → refused), nesting 10 OK / 11 refused, every escape row of §2¶10 incl. `\0777`, `\08`, `\c{`, `\c~`,
  `\c `, `\c\`, braces with spaces/tabs, leading-zero and overflowing `\x{}`/`\o{}`/`\N{U+}`, surrogates, `\x{10ffff}`,
  `\x{110000}`, bare `\x`/`\o`/`\N`/`\c`, `\q`, trailing `\`, `\1`-`\9`, `\10`/`\18`/`\351` refused (§9 row 16), `\Q\Q\E`.
- Case forcing (80 cases, c3/c5.json): all §2¶13a/13b witnesses, one-shot vs empty/unset group/empty conditional,
  `\u` before escapes / `\Q\E` / `$$` / NUL-producing escapes, case state through and out of conditional text, per-match
  reset, `\U\1\u\1`, title-case/`ß`/`ẞ`/U+01C4-6/U+0130/U+0131/U+212A/U+023A, byte encoding leaves non-ASCII alone.
- Full Unicode sweep (68 cases, c7.json): every scalar value 1..0x10FFFF (no surrogates) under `\U$1\L$1\u$1\l$1` on
  `(.)`: identical to libpcre2 10.46.
- Ill-formed UTF-8 under case forcing (pcrec-only, 5 cases): one-shot consumed by `\xff`, truncated sequences copied.
- Encoding guard: `\U$1` byte template with utf8 rx and utf8 non-ASCII template with byte rx → MISMATCH, as §2¶5 says.
- CLI: `--subst '-x$1'`, empty template (PIECES 1), NUL bytes via `--subst-file` (comment escapes `\x00`), `*/`,
  `??/`, `"`, `\`+newline in the template text: emitted C compiles under gnu and -std=c11.
- Piece shape: `x\ny$$`, `$$x$$` one literal piece; nested conditionals pad to max.

## NOT COVERED
- `${!name}` variables in templates (no PCRE2 oracle; only refusal of `${!v:-x}` and `${!}` seen).
- NOSPACE / scratch-sizing exactness and the §4¶22 1.5x bound as a bound (outputs were right; sneed not measured).
- Hand maps / RX_SUBST_NOGROUP / composed rx / MAP_ABSENT (other lenses); start offsets (`rx_iter_at`).
- The per-match / batch / no-gaps recipes: I drove only rx_subst_replace_all.

## DONE
