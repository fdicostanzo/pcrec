# D27 spec-first tests: [INLINE-C] stage 2 (embedded C) — REPORT

## Summary

`PCREC=build/pcrec CC=gcc timeout 1200 bash d27/run.sh`, run from the cell
against its `build/pcrec` (0.2.0-beta, abi 90) with gcc 15.2, reports
**`d27: 542 passed, 0 failed`**.

Every expectation comes from the spec text in the cell, and each case cites
its paragraph. No case found a wrong answer, a wrong span, a missed refusal or
a missed trap. Every FAIL on the early runs was my own misreading (listed
under Results).

There are three findings outside the test cases:
1. A refused header value echoes a raw Bidi_Control character in pcrec's
   diagnostic.
2. One refusal message is truncated mid-word.
3. Three refusal rows pass only because a different rule refuses first.

There are also twelve gaps or ambiguities in the spec.

A sabotage control run with `PCREC=/bin/true` gives `7 passed, 219 failed`,
so the harness can go red. The 7 that still pass are the five describe-mode
rows (they assert only exit 0 and no C on stdout) and two absence checks.

Files:
- `run.sh`
- the drivers: `driver_match.c`, `driver_helpers.c`, `driver_stamps.c`,
  `driver_names.c`, `driver_two.c`
- `cli_cases.tsv` (108 rows) and `match_cases.tsv` (71 rows); every row cites
  its paragraph
- `rxt/` (19 file-operand fixtures) and `hdr/` (two code-header fixtures)

Run output goes to `build/d27run/`, and the last log is
`build/d27_last_run.txt`.

## What was tested (by spec paragraph)

- **cli §1.22¶1, match_api §11.9¶8, pattern_language §7.12¶2 — the grant.**
  - The grant absent, `=c`, and the space form.
  - Unknown languages: `py`, `c,py`, `C`, and an unknown one with no segment.
  - An empty list means no grant.
  - A later `--allow-code` wins in both orders.
  - The refusal says `requires module 'code-c'` and names `--allow-code=c`.
  - A refused compile writes nothing.
- **cli §1.17¶3, match_api §8.2¶7c, §11.9¶8 — features never grant code.**
  - `--features code-c` and `--features classes,code-c` are refused, even
    with the grant.
  - `--features all` does not grant code.
  - A block's `features code-c` line is refused.
  - `PCREC_FEATURE_MODULES` under `all` does not list `code-c`.
- **§11.9¶1 — which strings are code.**
  - Every PCRE2 string delimiter (`` ` ``, `'`, `"`, `^`, `%`, `#`, `$`, `{}`)
    is recognised as code: refused without the grant, and run with it.
  - `c:` with no following space is code.
  - The attribute forms `c,consume:` and `c,consume,once:` are code.
  - These stay binding strings: `cc:`, `C:`, ` c:` (leading space), a leading
    doubled delimiter, `c,once` with no colon, and `"c,consume"`.
- **§11.9¶2 — where the code ends.**
  - A doubled `'` and a doubled `` ` `` are one byte.
  - A string opened with `{` closes at `}`, and `}}` is one byte.
  - `(?x)` makes neither `#` a comment nor spaces insignificant inside the code.
  - `(?i)` has no effect inside the code.
- **§11.9¶3 — the refusal set: one refused case per class, each with an
  admitted neighbour.**
  - Bidi_Control: U+202E, U+2066, U+061C, U+200F.
  - Default_Ignorable_Code_Point: U+200B, U+00AD, U+FEFF, U+FE0F, U+034F,
    U+3164, U+E0001, U+1D173.
  - Line ends: U+0085, U+2028, U+2029.
  - A lone CR, a CR as the last byte, and CR CR LF.
  - VT, FF, the C0 bytes 01, 1B and 1F, and DEL.
  - Admitted neighbours: é, U+3163, U+1F600, U+0086 (a C1 control, which the
    spec does not name), U+2027, CR LF, tab, LF, and `~`.
  - Ill-formed bytes are passed through: FF, a lone 80, a truncated E2 80, an
    overlong 4-byte U+2028, and the surrogate bytes ED A0 80.
  - The refusal names the code point and an offset.
  - A second segment is checked too.
  - A refused character next to an undone doubled delimiter is caught.
  - A refused character in a file operand is caught.
- **§11.1, §11.7, §11.8, pattern_language §7.11¶3 — the callout rules hold
  for code sites.**
  - A site in a lookbehind is refused; in a lookahead it is admitted.
  - A site in a group reached by recursion is refused; in a plain group it is
    admitted.
  - `(?C..)?` is refused; `(?:(?C..))*` is admitted.
  - `once` after `a+` is refused and the refusal names the offset; after `a++`
    it is admitted and runs.
  - `once` inside a repeat is refused.
  - `verify`, unknown, repeated, empty and trailing-empty attributes are
    refused.
  - A callout in a conditional's condition is refused (but see finding 3).
- **§11.2¶1 row 3 and ¶1a — the binding form.**
  - Each segment gets `<prefix>__code<k>_ref = { <prefix>__code<k>, NULL }`,
    numbered in pattern order. The driver calls each segment directly and
    checks it is the right one.
  - Two segments run in order.
  - Unreachable sites (`{0}` and an uncalled DEFINE) build under `-Werror`,
    in both the self-contained and the split form.
- **§11.3 and §11.9¶5 — the view and the macro set.**
  - `RX_SUBJ`, `RX_LEN`, `RX_POS`, `RX_START`; `RX_START` ignores `\K`.
  - `RX_CAP_SET`, `RX_CAP_S`, `RX_CAP_E`, `RX_CAP_LEN`, `RX_CAP_P` and
    `RX_CAP` on set, unset, not-yet-closed, empty and out-of-range groups
    (2, 5, 7, 99, -1), and on slot 0.
  - All six accessors evaluate their group number once.
  - A repeated group keeps its previous value until it closes again.
  - `RX_G_<name>`, including all three `(?J)` cases (the set member, the
    first member, and none set).
  - `RX_USER` and `ctx->user` are NULL.
  - `vars` is NULL and `nvars` is 0.
  - `ncap` is the pattern's group count plus one under `--no-captures`.
- **§11.4 and §4¶10 — returns.**
  - Pass and fail, including backtracking after a fail.
  - `consume`: the length, the enclosing group's span, a return of 0, that a
    consume is atomic, that it is asked again on a new path, and consuming to
    the subject end.
  - STEPS, FRAMES, WORK, INTERNAL, UNSET_VAR and UTF propagate out of the
    search unchanged.
  - These trap: STARTPOS, ITER, -42, a positive return from a check,
    consuming past the end, and consuming to a mid-character position under
    `-e utf8`.
- **§11.6¶1 — a pure callee.** It gets the backtracking-order answer: `(\d+)`
  with an even-position veto over `1234` matches `[0,3)`.
- **§11.9¶4 — the emitted layout and `#line`.**
  - The segment's definition comes last; only `#undef` lines follow it.
  - The macro set comes before the first `#line`.
  - `--pattern` text is named `#line N "<command line>"`.
  - gcc's diagnostic column is right for `--pattern` and for a file operand.
  - A file operand is named as typed (`./d27/rxt/../rxt/line.rxt`).
  - Every decoded line under `pattern-esc` / `--pattern-esc` names the
    opener's line.
  - Falling off the end traps, including an empty or blank body.
  - A `#define` inside a segment reaches the code after it.
  - The macro set, the `RX_G_*` names and the internal macros are `#undef`ed;
    the public names and the stamps stay defined.
  - Two code artifacts compile together in one translation unit.
- **§11.9¶7, cli §1.22¶2, rxt §1.1 — code headers.**
  - `--code-header` needs the grant even with no segment.
  - With the grant and no segment, the header is still emitted.
  - A bare name is written in double quotes; the `"..."` and `<...>` forms
    are both accepted.
  - A repeated header is emitted once, and order is kept. (The fixture
    `d27a.h` has no include guard and `d27b.h` `#error`s if it comes first.)
  - The includes come after the macro set and before the segment, and only in
    the `.c`.
  - The build runs.
  - Refused, from the CLI and in a file: a backslash, a control byte,
    non-ASCII, a bidi character, an unknown language, and `--code-header`
    combined with a file operand.
- **cli §1.1.1¶4, §1.22¶1, rxt §1.1¶2 — file builds.**
  - A refused target leaves no file of any target written; the plain target
    is listed first.
  - `-o -` with a refused target writes nothing to stdout.
  - The grant applies to every target.
  - A config `pcrec` line carrying `--allow-code` or `--code-header` is
    refused at parse, with or without the grant.
  - Code in a `lib` definition is refused even with the grant, through a
    plain call and through a delivering call.
- **cli §1.10 — `--emit-main`.**
  - With code it builds and exits 0 on a match and 1 on no match.
  - A pattern mixing code with a named binding is refused, naming
    `rx_callout_octet`.
- **Describe modes (cli §1.22¶1).** `--emit-ir`, `--emit-facts` and
  `--count-groups` exit 0 and write no C, whether the grant is absent, empty,
  or `c`.
- **§6.3.1¶1, §6.3.2, §11.2¶3, §1¶6b — stamps, read from the split form's
  `.h`.**
  - `_CALLOUTS`: 1; 2 for two segments; 4 for a mixed pattern that repeats a
    name; 1 for a `{0}` site.
  - `_CALLOUT_BINDINGS`: `""` when every site is code;
    `"rx_callout_1,rx_callout_octet"` (sorted, distinct, code not listed);
    `"rx_callout_c"` for `(?C"c,consume")`.
  - `_CODE_LANGS` is `"c"`, and absent on a callout artifact with no code.
  - `-p foo` gives the `FOO_*` names.
  - The span-helper and callout families are present on callout artifacts and
    absent on `abc`.
  - The engine is `vm` (§11¶1).
- **§11.10 — the seven span helpers, every input class.**
  - Unset spans: length -1, length -5, and a set pointer with a negative
    length.
  - `p == NULL, len 0` reads as `""`.
  - A span shorter than its memory, and an embedded NUL.
  - `rx_eqi` folds only the 26 ASCII letters (checked against the
    `@`/`` ` ``, `[`/`{` and `^`/`~` pairs and Latin-1 and UTF-8 É/é).
  - `rx_u64` / `rx_hex`: the maximum, maximum + 1, a value that wraps to
    something small, many leading zeros, empty, signs, spaces, non-ASCII
    digits, `0x`, `g`, and `*out` untouched on failure.
  - `rx_in`: the edges, lo > hi, the full range, and that hex is not read.
  - `rx_find`: an empty needle, an unset span, the first occurrence, and a
    match straddling or ending at the span end.
  - `rx_u8next`:
    - Every length (1-4 bytes) at its minimum and maximum, and on either side
      of the surrogates.
    - Decoding at an offset, at the end, past the end, and on an unset span.
    - Overlong forms (C0, C1, E0, E0 9F, F0, F0 8F), surrogates, values above
      U+10FFFF, F5 and FF.
    - A lone or bad continuation byte in positions 2, 3 and 4.
    - Sequences truncated by their bytes or by the span length.
    - `*i` and `*cp` left unchanged on -1.
  - The helpers are callable inside a segment and from an artifact whose
    binding is hand-written.
- **The ASCII rule (match_api §6, the paragraph before §6.1).**
  - Non-ASCII bytes appear only in the segment's lines.
  - A raw U+202E pattern literal outside the code is echoed as ASCII.
  - Every run artifact compiles under
    `-Wall -Wextra -Werror -Wbidi-chars=any`.

## Results

542 passed, 0 failed. No FAIL is a pcrec bug candidate.

These early FAILs were my misreadings, now fixed:
- Named and numbered callouts need `--features callouts`. (Code segments do
  not; see gap 1.)
- `a++` needs `--features atomic-groups`.
- My `PCREC_FEATURE_MODULES` check grepped for `code` and matched
  `unicode-props`.
- My emit-main subject `xab` could not satisfy `RX_POS == 1`.
- My "definition last" scan anchored on the marker in the line-1 provenance
  comment instead of in the segment.
- `lib_user.rxt` was missing `named-groups`. It is now refused for the code
  reason: "embedded code at d27/rxt/lib_def.rxt:2 is not allowed: code from
  included files needs pinned include lines (not in this build)".

## Findings (not test failures; the spec is silent on each)

### F1. A diagnostic echoes a raw Bidi_Control character

The value is correctly refused, but the message echoes U+202E raw to stderr.
In the same message a control byte is escaped (`\x01`). This is the
trojan-source class §11.9¶3 exists to stop, appearing in pcrec's own
diagnostic. cli §1.21 promises escaped control bytes for `--callout`;
nothing promises the same for `--code-header`.

Command (run from the cell):

    build/pcrec --allow-code=c $'--code-header=c:"a\xe2\x80\xaeb.h"' -o build/x.c --pattern 'a(?C`c: return RX_PASS;`)b' 2>&1 | od -c | tail -3

Observed: exit 1, and stderr carries the raw bytes `342 200 256`:

    pcrec: --code-header: a header name is printable ASCII with no backslash or closing delimiter (got 'c:"a<342 200 256>b.h"')

The same happens for the file form, `code-header c "a<U+202E>b.h"`
(`d27/rxt/hdr_nonascii.rxt`):

    pcrec: [value-shape] d27/rxt/hdr_nonascii.rxt:2: 'code-header': a header name is printable ASCII with no backslash or closing delimiter (got 'c "a<U+202E raw>b.h"')

For comparison, the control-byte case (`hdr_control_refused`) prints
`(got 'c:"a\x01b.h"')`, escaped. The logs are
`build/d27run/cli/hdr_bidi_refused.stderr`, `hdr_nonascii_refused.stderr` and
`hdr_control_refused.stderr`.

### F2. A refusal message is truncated mid-word

Command:

    build/pcrec --allow-code=c -o build/x.c --pattern-esc --pattern '"a(?C`c: /* x\ry */ return RX_PASS;`)b"'

Observed: exit 1, nothing written, and the message ends mid-word:

    pcrec: the code segment at offset 1 contains U+000D, a carriage return with no line feed after it (a line end to gcc, an overwritten line to a terminal), at byte 5 of the segment; such characters make the code a reviewer reads differ from what the compiler compi (pattern offset 1)

The tier is intact: exit 1, U+000D named, the offset given. The message hit
a length cap.

### F3. Three refusal rows pass only because a different rule refuses first

1. A callout in a conditional's condition (`cond_condition_refused`):

       build/pcrec --allow-code=c --features all -o build/x.c --pattern '(?(?=a(?C`c: return RX_PASS;`))a|b)'

   Observed: `pcrec: module 'conditionals' is enabled but (?(...) is not implemented yet (pattern offset 0)`

   The condition rule itself is untested until conditionals ship.

2. Code in an `include`d file (`file.include_code_refused`):

       build/pcrec --allow-code=c -o build/d27run/fb/x d27/rxt/inc_entry.rxt

   Observed: `pcrec: [value-shape] d27/rxt/inc_entry.rxt:4: 'target t' -> no definition 'fragblk'; searched the source's own directory (no --lib-path)`

   A fragment's block is not a definition a target can name, so the include
   half of "lib, include refused even with the grant" cannot be reached from
   the CLI.

3. The admitted LOCAL neighbour I wanted for the lib rule
   (`file.local_def_delivering_refused`):

       build/pcrec --allow-code=c -o - d27/rxt/deliver_local.rxt

   Observed: `pcrec: d27/rxt/deliver_local.rxt:6: target 't': a callout inside a group reached by a subroutine call or recursion (including a lib definition) is not supported: a call re-enters the site at a depth its view does not describe (pattern offset 7)`

   §11.1 refuses it first, so no admitted neighbour exists (see gap 3).

### Two smaller notes

- The refusal offset ("at byte N of the segment") is 0-based and counted in
  the DECODED code text after `c:`. In `` c: /* ``X`` */ `` it reports
  byte 5, the decoded position. The spec does not define it (gap 4).
- The describe modes apply the §11.9¶3 refusal set and refuse
  `--allow-code=py` with exit 1:

      build/pcrec --emit-ir --pattern-esc --pattern '"a(?C`c: /* \xe2\x80\xae */ return 0;`)b"'
      build/pcrec --emit-ir --allow-code=py --pattern 'a(?C`c: return 0;`)b'

  The spec does not say whether they should (gap 5).

## Spec gaps and ambiguities

1. **Does a code segment need module `callouts`?** pattern_language §7.12¶1
   says the return table and attributes are module `callouts`', and §11.9¶1
   says every rule of §11.1-§11.8 holds. Yet a code segment compiles under
   the default feature set without `callouts`, while `(?C"c")` does not.
   Is the grant alone meant to suffice? And what should
   `PCREC_FEATURE_MODULES` list for such an artifact?
2. **§11.1¶1 against §11.2¶1a/¶3 on DEFINE.** §11.1 lists "a `(?(DEFINE)`
   group" among refused places, while §11.2 builds and counts a site in an
   uncalled DEFINE group. pcrec admits the uncalled one, and I tested that
   reading. Suggested wording: "a DEFINE group a call reaches".
3. **The LOCAL rule of §11.9¶8 is unobservable for definitions.** §11.1
   refuses a site in any group a call reaches, a delivering call included,
   so a definition holding code never compiles, local or not. The include
   half cannot be reached from the CLI at all. The spec should say so, or
   name the case where LOCAL matters (a library caller's pattern?).
4. **"its byte offset in the segment" (§11.9¶3)** does not say whether it
   counts from 0 or 1, whether it starts at the tag or after `c:`, or
   whether it counts decoded or source bytes.
5. **Do the describe modes apply the refusal set?** "Parse code whatever the
   grant says (absent, empty or a list)" does not say whether the §11.9¶3
   refusals and the unknown-language refusal apply there.
6. **`rx_u8next` on a 0 return.** The spec does not say whether `*i` and
   `*cp` are left untouched (it says so only for -1), nor what a negative
   `*i` does. I tested neither.
7. **`z == NULL`** is unspecified for `rx_eq`, `rx_eqi` and `rx_find`.
8. **`--allow-code=c,c`** (a repeated language) is unstated, and so is
   letter case. `C` is refused, but the spec says only "c the one language".
9. **The header-name check also refuses a closing delimiter.** pcrec's
   message says "...or closing delimiter", but cli §1.22¶2 and rxt §1.1 say
   only "printable ASCII with no backslash". Neither says how a refused
   value is echoed (F1).
10. **Placement of a code header with no segment.** cli §1.22¶2 says each is
    emitted, but §11.9¶4's layout places them before the first segment.
    pcrec emits it anyway, and I tested that reading.
11. **The column when padding is off.** §11.9¶4's "padded to its column"
    says nothing about the column after a doubled delimiter, a tab or a
    non-ASCII byte. Under `pattern-esc`, "with no column" reads as "no
    padding", which matches gcc's `:1:8`.
12. **The `_CODE_LANGS` scope.** The stamp is scoped "code-bearing", so it
    is absent on a callout artifact with no code. Telling "has code?" then
    takes an `#ifdef`, which §6.3.1¶5's "never readable by absence"
    otherwise discourages.

**Not tested (missing inputs):**
- `pcrec_options.allow_code` (§8.2¶7c) and the `<pattern>` name for a
  library pattern (§11.9¶4): `lib/pcrec.h` is not in the cell.
- Inlining at `-O1` (§11.2¶1a).
- The step charged per fire (§11.6¶3).
- `-fcomments`.

## Disclosure

At spawn, before any tool ran, these were injected:
- the user-global `~/.claude/CLAUDE.md`;
- the session-root `/home/pcrec/projects/pcrec/CLAUDE.md` (process, build
  commands and the directory map; no source code and no test expectations);
- the memory index `MEMORY.md` (one-line process notes);
- the git status and recent commit subjects. One reads "merge lane/ic2fix:
  [INLINE-C] stage 2 (tagged (?C`c: ...`), --allow-code=c, span helpers) ...
  abi 90".

I used none of these to derive an expectation.

I read only files inside the cell: `docs/spec/*.md`, `docs/testing.md`, and
the artifacts the cell's `build/pcrec` generated. The generated C is the
thing under test (for example, I saw that `RX_CAP_SET` tests
`caps[n][1] >= 0`), but no expectation was taken from it. I ran no git and
read nothing outside the cell.

The rulings file `build/ic2d27_rulings.md` did not exist when I checked
before reporting. This report was written with a Bash heredoc at the
manager's direction, after the Write tool refused report files from a
subagent.
