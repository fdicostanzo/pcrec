# langfix — the pattern-language defects lane speclang found (2026-10-22)

Lane langfix (opus), branch `lane/langfix` off `lane/speclang` @ b17496589.
Brief: fix `speclang_report.md` §"Defects and findings" items 1, 3, 4, 2,
and 6/9 if small; list 5/7/8. Parked on the branch for review, not merged.

## STATE AT HANDOFF

- Code, corpus, sabotage rows, re-pins, spec hunks and K115-K118 committed.
- Rulings file `langfix_rulings.md`: one entry applied (hold every
  695-langfix-* job until `i2build-parity` ends; no -j builds outside the
  queue while 641 is pending). The early `make -j8` builds and the single
  section runs below were done before that entry was read.
- VALIDATION OWED (queued, held behind i2build-parity by the ruling):
  - `695-langfix-test`: make -j16, make strict, `scripts/perfrun --label
    langfix` make test. Log: the job's run dir under
    `worktrees/.boxqueue/`; completion = `== 695 step verdict OK`.
  - `696-langfix-mech`: S23 S1386..S1393; completion = `== mech run
    COMPLETE: 9 rows`. Every row's figure is PREDICTED until it runs.
- Run here, green, by hand (named files): `make test-reject` (657/0, after
  re-pinning three open-gate `\p` rows); `make test-rxtsource` (green, at
  286 files / 5850 blocks / 71334 lines); `bash tests/harness/run.sh` on each
  new file (18/0, 25/0, 10/0; on main's binary 11/7, 7/18, 4/7, so each file
  detects its fix); `python3 tests/harness/verify_rxt.py` on the new files
  (all pcre2-only, 0 failures); `compliance_section.py --check` and
  `--check-annotations` (pass after `--write`); `make test-spec-history`
  (11/0). NOT run here: `make test-registry` (its built-status tally was
  re-pinned 142 = 114 + 12 + 16 from the measured `--list-syntax` diff),
  test-codegen, the full suite.
- No emitted-byte change for existing patterns: the only emitter edit
  writes a group name through `emit_c_string_literal`, which is
  byte-identical for an ASCII name. No abi event (abi 85 untouched).

## What changed, per finding

1. **K115, the wrong answer: FIXED.** Census of libpcre2 10.46 PCRE2_UTF
   over every code point (`(?x)a<cp>b` vs "ab"): the skip set is
   {09-0D, 20, U+0085, U+200E, U+200F, U+2028, U+2029}. The same census
   found the comment terminator (0x0A only) and `(?xx)`'s class deletion
   ({09,20}) unchanged under UTF. parse.c: `xskip_char` is the character
   set, `xskip_len` decodes a byte >= 0x80 through `pcrec_pat_char`, so
   ill-formed text refuses exactly where it would as a literal. Under
   `byte` the four members above 0xFF are inert. S23's AFTER (it named
   `xskip_byte`) re-aimed at `xskip_char`; its BEFORE anchor is unchanged.
   Corpus `tests/modifiers/xmode_utf8.rxt`; sabotage S1386, S1387.
3. **K116, Unicode group names: FIXED.** Census over every code point in
   both positions: first character `[\p{L}_]`, later `[\p{L}\p{Nd}_]`
   (set-equal), the wall 128 bytes. `byte` admits no byte >= 0x80.
   `pcrec_group_name_scan` now takes the `Ctx` and asks the unicode-props
   tables (`pcrec_uprops_span("L"/"ND")`) through `ng_name_char`; all five
   readers share it (declaration, `\k`, `(?P=`, `\g{`, `(?&`, and the
   `(?&site=...)` scope name). Emitted names go through the C string
   escaper (`"\303\251"`); the generated `.c` compiles under
   `-Wall -Wextra -Werror`. No ABI question arose: names are emitted only as
   string literals, never as identifiers, so the STOP RULE did not fire.
   Corpus `tests/named_groups/utf8_names.rxt`; sabotage S1388, S1389.
4. **K117, `\x{ 41 }`: FIXED.** 10.46 admits spaces and tabs before and
   after the digits, never among them, never a newline. `esc_char_value`
   calls the brace quantifier's `skip_quant_space` (forward-declared) on
   both sides. Also measured: `\p{ L }`, `\g{ 1 }`, `\k{ n }` were already
   accepted; `\o{ 101 }` and `\N{ U+41 }` accept padding in PCRE2 but are
   not built in pcrec. Corpus `tests/base/xbrace_space.rxt`; sabotage
   S1390, S1391. The newline cell (`\x{\n41}` refused) is not in the corpus:
   a `pattern-esc` block made rxtsource's leg A/leg B comparison disagree
   (the dump-value seam), so every new block uses a raw `pattern` line.
2. **K118, `(?J)` ownership: OPEN, needs a design decision (STOP RULE).**
   Read from the records: the option-run row is `modifiers`' (it
   dispatches), the letter `J` is `backrefs'` (compliance page ASK-1), and
   `(?m)` has the identical shape with `assertions`. The refusal texts are
   right and `--list-syntax` is right about the row; nothing says the letter
   needs a second module except mod_modifiers.c's code. The speclang claim
   that `--explain`'s `agree` "compares the live names to themselves" is not
   what the clause does: it compares the closed-gate refusal's module with
   the row's module, `modifiers` on both sides, and it reads only the
   closed gate on purpose (R20/MOD07-2: comparing the open-gate letter
   answer fired on correct data). So there was nothing to plant: the check
   is not broken, it is blind to the letter by design. The fix that would
   close it is a per-letter module column on the option-letter rows, read
   by the letter gate in mod_modifiers.c instead of hard-coded
   `FEAT_BACKREFS`/`FEAT_ASSERTIONS`, shown by `--list-syntax`, and
   compared by an open-gate `--explain` clause. That is a `--list-syntax`
   schema change, so it is the manager's (and Frank's) call. Recommendation:
   do it as a declared row field when the next option letter with its own
   module appears (D77: two members today, `m` and `J`). Spec now says the
   two-module fact in `pattern_language.md` §6.2¶3; §9¶7 retired there.
6. **Malformed `\p` with the module enabled: FIXED.** With the gate open a
   malformed body is now `\p: malformed property escape` (PCRE2 error 146),
   with no "requires module". The same change for a one-letter unknown name
   (`\pA`), matching `\p{Q}`. This reverses a stage-3 pin that called the
   malformed tier gate-independent; the three re-pinned rows in
   tests/reject/ say why. Closed-gate wording unchanged. Sabotage S1392.
9. **`(*UTF)` built status: FIXED.** `pcrec_construct_built_status` probes
   every encoding (default first; the first answer other than `unbuilt`
   stands). Measured: exactly the two rows `(*UTF)a`/`(*UTF8)a` move to
   `built`; the registry tally and the compliance index re-pinned;
   `registry.md` §3¶1 says so. Sabotage S1393.
5. 7. **Not done (D26 wording).** 5: `\p{Foo}`/`\p{InGreek}` with the module
   enabled still say "not implemented yet". 7: the `(*...)` catch-all still
   promises `verbs` under `--features all`.
8. **Not done, not trivial.** `--features std1,quoting` is refused because
   D37 resolves a named set only when it is the WHOLE spec (enabled.c says
   so); composing a named set into a list is a D37 semantics question (what
   the label stamp says), not a parser slip.

## Owed elsewhere

- Compliance page hand rows (compliance-refresh, not run here): "whitespace
  inside `{ }` in `\g{2}` etc." reads `REJECTED` and is stale (`\g{ 1 }`,
  `\k{ n }`, quantifier braces and now `\x{ 41 }` all accept); the
  `(?x)` and named-group rows could cite K115/K116.
- tests/spec_mod0 (`make test-spec`, not in `make test`) does not link
  here (`undefined reference to pcre2_compile_8`) and check06 disagrees on
  rows reaching no doorway; not this lane's change, seen in passing.

## Files

src/parse/parse.c, src/parse/mod_named_groups.c, src/parse/mod_backrefs.c,
src/parse/mod_recursion.c, src/core/internal.h, src/parse/mod_uprops.c,
src/gen/emit_dfa.c, src/dump/syntax_dump.c; tests/modifiers/xmode_utf8.rxt,
tests/named_groups/utf8_names.rxt, tests/base/xbrace_space.rxt (+ their
CLAUDE.md rows); tests/mech/sabotages/S1386..S1393 and S23;
tests/reject/run_reject_tests.sh; tests/registry/registry_check.c;
tests/rxtsource/run_rxtsource_tests.sh; docs/spec/pattern_language.md,
docs/spec/registry.md, docs/pcre2_compliance.md, docs/dev/known_issues.md.
