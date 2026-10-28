# Critic round ic2, lens CONTRACT: does the code do exactly what the spec says?

Subject 864902a48 (lane/ic2), base 614d45eb3. Read-only. Review tree
worktrees/crit-ic2; scratch /tmp/claude-1001/crit-ic2/contract/.
No denied file was opened.

## Findings

### CON-1 (CONFIRMED by source + gcc; pcrec probe below) the bidi/invisible refusal list is narrower than the class the spec names, and it is hand-typed rather than read from the vendored UCD
- Severity: trust. Effort: small (derive the table from
  third_party/ucd-16.0.0 through `make gen-tables`, or extend the hand list
  and drop the class words). Blast radius: every code segment.
- Where: src/parse/mod_code.c:113-122 (`code_invisible[]`); spec
  match_api.md §11.9¶3, pattern_language.md §7.12¶3, inline_c.md §2.4.
- The spec sentence says a segment refuses "a Unicode bidirectional control or
  invisible format character (U+200B-U+200F, U+202A-U+202E, U+2060-U+2064,
  U+2066-U+2069, U+FEFF), so the code a reviewer reads is the code that
  compiles". The code refuses exactly the parenthesised list. But:
  - U+061C ARABIC LETTER MARK is a Bidi_Control in the repo's own vendored
    UCD (third_party/ucd-16.0.0/PropList.txt:28, `061C ; Bidi_Control`), and it
    is not in the list. It is not refused.
  - Default_Ignorable_Code_Point (DerivedCoreProperties.txt:10583-10609) holds
    the invisible characters the CVE-2021-42574 family actually uses beyond
    bidi: U+3164 HANGUL FILLER, U+115F/U+1160, U+FFA0, U+00AD, U+180E,
    U+FE00-U+FE0F and U+E0100-U+E01EF (variation selectors), U+E0020-U+E007F
    (TAG characters, the "ASCII smuggling" set), U+206A-U+206F.
- gcc 15.2 proof that these reach compiled code unseen, with no warning under
  `-Wall -Wextra -Wbidi-chars=any` (scratch contract/invis.c): an identifier
  `x<U+3164>` (renders as `x`) beside a real `x`, and a string
  `"admin<U+E0041>"` (renders as `"admin"`, is 6 bytes) both compile clean;
  the program returns 2, i.e. it read the invisible variable and the hidden
  byte. In a segment that is `rx_eq(RX_CAP(1), "admin<TAG>")`: the reviewer
  reads a check for "admin", the artifact compares with something else. gcc
  does not flag U+061C either (contract/bidi_alm.c: no warning; LRM and RLO
  warn), so the §6 sentence "compiles clean under -Wbidi-chars whenever the
  user's code does" gives no cover.
- Which is wrong: the spec's GOAL ("the code a reviewer reads is the code that
  compiles") is right and the LIST is wrong. Memory "official Unicode data
  only" (Frank 2026-10-24) argues for reading the property from the vendored
  UCD (Bidi_Control union Default_Ignorable_Code_Point, at minimum the Cf/Lo/Mn
  assigned ones), not typing five ranges; the list then has one home and the
  spec cites the property instead of restating ranges in three documents.

### CON-2 (CONFIRMED by source) a FILE operand's `code-header` lines are silently capped at 256
- Severity: answer (low odds) / trust of the contract. Effort: trivial
  (allocate, or refuse past a declared limit with a `--list-limits` row).
  Blast radius: FILE targets with >256 `code-header` lines.
- Where: cli/main.c:2193-2200 (`PcrecCodeHeader hdrs[256]; ... nh < 256`).
- Spec: rxt_format.md §1.1 `code-header` row and match_api.md §11.9¶7 say
  each line is emitted "in the order written, a repeated text once". The
  257th and later lines are dropped with no diagnostic (the loop condition
  just stops), and the count includes duplicates, so 256 copies of one line
  plus a distinct one drops the distinct one. A dropped header is usually a
  C compile error in the user's build, but a header that only defines macros
  a segment tests with `#ifdef` changes the compiled code silently. House
  rule "no silent defaults"/D105 "no silent-degradation path". Code is wrong;
  the spec is right.

### CON-3 (CONFIRMED by source) the harness manifest's `allow-code` line: "at most one per manifest" is not enforced, and the `-I` rule differs from the spec sentence
- Severity: doc / maintenance (test-contract only). Effort: trivial.
- Where: tests/harness/run.sh `manifest_objs` (accepts the line, checks only
  its shape) and `manifest_allow_code` (returns the FIRST line's LANGS);
  spec rxt_format.md §6 manifest table ("At most one per manifest") and
  §6¶3a ("compiles each driver with -I of the manifest's directory").
- A second `allow-code` line is silently ignored rather than being the
  harness failure §6¶4 makes of every other malformed manifest line. And the
  `-I` is added only for a file that HAS a `code-header` line (run.sh: the
  `code_inc` array is set inside the `code-header` row arm), of the .rxt
  file's own directory, not "each driver" of "the manifest's directory". Same
  directory in practice; the spec sentence over-promises. Either the code
  refuses a second line and the spec says "-I when the file has a
  code-header line", or both move the other way.

- PROBE (CON-1, built compiler): every one of U+061C, U+3164, U+115F,
  U+00AD, U+180E, U+FE0F and U+E0041 inside a segment compiles (rc 0,
  artifact written; contract/p2.sh); U+200E, U+202E, U+2066, U+FEFF are
  refused as specified. End-to-end deception (contract/exploit_pattern.txt):
  ``a(?C`c: int ok<U+3164> = 1; int ok = 0; (void)ok; return ok<U+3164> ? RX_PASS : RX_FAIL;`)b``
  renders as "int ok = 1; int ok = 0; ... return ok ? ..." (a reviewer reads
  a check that always fails), compiles under `--allow-code=c`, and the
  matcher answers `match 0 2` on "ab".

### CON-4 (CONFIRMED) `--allow-code` and `--code-header` are missing from `pcrec --help`
- Severity: doc (caller-facing). Effort: trivial. Where: cli/main.c usage
  text; cli.md §1.22, §1.18¶1.
- `pcrec --help | grep -c 'allow-code\|code-header'` prints 0, while
  `--callout N:ATTRS` (stage 1b) and `--features` are listed. cli.md §1.18¶1
  names the only options deliberately left out of `--help` (the `-f`/`-fno-`
  axes, `--unroll=K`); the grant is a user feature and the ONLY door to
  module `code-c`, so a user reading `--help` cannot find how to enable what
  the refusal tells them to enable. Code is wrong (the usage text).

### CON-5 (CONFIRMED) `--code-header c:` (empty header) is refused as "malloc: Success"
- Severity: doc (diagnostic wording, but the text is false). Effort: trivial.
- Where: cli/main.c:1083-1115 `cli_code_header`: for an empty value `hdr`
  stays NULL, and `if (!lang || !hdr) { ... perror("malloc"); return 1; }`
  reports an allocation failure that did not happen.
- Repro: `pcrec -p rx -o x.c --allow-code=c --code-header c: --pattern ab`
  -> stderr `malloc: Success`, rc 1. Expected (cli.md §1.22¶2, and the
  function's own `why`): `--code-header: wants LANG:HEADER ... (got 'c:')`.

### CON-6 (CONFIRMED) a set EMPTY group on a NULL subject reads as the UNSET span
- Severity: answer (edge). Effort: trivial (test `len < 0` only, or define
  the unset span by `len == -1` alone in both the helpers and §11.10).
- Where: src/gen/emit_code.c:41,48,61,73,93,106 (`if (!s.p || s.len < 0)`)
  vs match_api.md §11.10¶1 ("the UNSET span (`p == NULL`, `len == -1`)") and
  §3.1¶8 (`s` may be NULL when `n == 0`).
- Repro (contract/nul/): pattern ``()(?C`c: return rx_eq(RX_CAP(1), "") ? RX_PASS : RX_FAIL;`)``,
  `rx_search(NULL, 0, 0, caps)` returns 0 (no match); the same call with
  `""` returns 1; with the segment `return RX_CAP_SET(1) ? ...` the NULL call
  returns 1. So group 1 is SET, `RX_CAP(1)` is `{NULL, 0}`, and every helper
  reads it as unset (rx_eq 0, rx_find -1) although §11.10 says unset is
  `p == NULL` AND `len == -1` and rx_eq's row says "1 when s is set and its
  bytes are exactly z". The code is wrong; the spec's definition is the
  right one (a legal subject must not change a group's set-ness).

### CON-7 (CONFIRMED) a `code-header` line's `#line` stays in force over the generated macro set and function header
- Severity: doc (diagnostic location). Effort: trivial (emit `#line N+1 "<the .c>"`
  is impossible without the output name, so instead emit the header block's
  `#line` only right before the `#include` and put the macro set BEFORE the
  header block, or drop the header `#line` and let a missing header be
  reported at the .c line, which then names the header text).
- Where: src/gen/emit_code.c:414-416; match_api.md §11.9¶7 says each header
  is "written `#include` AS WRITTEN"; no spec sentence mentions a `#line`
  before it.
- Repro (contract/ln/m.rxt, 4 lines): `code-header c <stdint.h>` then
  ``pattern (a)(?C`c: return RX_CAP(1);`)c`` on line 4; gcc says
  `m.rxt:12:34: error: incompatible types when returning type 'rx_span'`
  and `m.rxt:4:26: note: in expansion of macro 'RX_CAP'`. Line 12 of a
  4-line file is the generated `#define RX_CAP` line, attributed to the
  .rxt because the header's `#line 1 "m.rxt"` was never superseded until the
  segment's own `#line`. Without a `code-header` line the same define is
  located in the .c. The missing-header case itself (i.rxt:1:10 fatal
  error) works as intended.

### CON-8 (CONFIRMED) internal `<PREFIX>_*` macros stay live at the segment block: the keep table keeps every upper-prefix name, and the live-macro check exempts the same family
- Severity: maintenance / contract (no answer change seen). Effort: small
  (keep the STAMP names, read from the stamp catalogue src/gen/stamp_kinds.c
  `stamp_rows[]` or from `pcrec_sb_stamp*`'s own record, not the whole
  `\x01Q_` prefix; drop the `${upx}_` exemption from the check).
- Where: src/gen/emit_code.c:159-166 (`{ "\x01Q_", false }` "<PREFIX>_*
  stamps"); tests/code/run_code_tests.sh arm 7 (`grep -vE "^(_|${upx}_|...)"`).
  Spec: match_api.md §11.9¶4 ("`#undef` of every macro the artifact defined
  for its own use that is still defined there (what stays defined is the
  public contract: the stamps, ...)") and §6.3.1¶10, which names
  `<PREFIX>_SLOT_*`, `<PREFIX>_NSLOTS`, `<PREFIX>_R_*` as INTERNAL; design
  inline_c.md §3.2 lists `RX_CUT`, `RX_PRUNE_*`, `RX_SLOT_*`, `RX_R_*`,
  `RX_SLOT_GROUP<n>_*` among the names the block must `#undef`.
- Repro (contract/p9/: `gcc -E -dD` of the artifact, macros live at the
  `code-header` include point, the include point being the first line after
  the `#undef` block): ``(?<=x)(a+)\1(?C`c: return RX_PASS;`)b`` `-e utf8
  --features all` leaves live RX_CUT, RX_PRUNE_CLAMP_SPAN, RX_PRUNE_TOO_SHORT,
  RX_R_STEPS/_FRAMES/_WORK/_RECURSE/_INTERNAL, RX_SLOT_GROUP1_START/_END/
  _PENDING, RX_SLOT_SPAN_LOW0, RX_SLOT_WHOLE_START/_END, RX_NSLOTS,
  RX_CHARGE_WORK (plus the real stamps). ``(a|b)*+c(?>d|e)(?=f)...`` adds
  RX_SLOT_CUT_MARK0, RX_SLOT_REVDET0_*. Only the LOWER-prefix
  `rx_VALID_LB` is `#undef`ed. The code is wrong against both documents;
  the check cannot see it because its exemption `${upx}_` is the bug's own
  rule (learnings §3: a control that shares a source with what it controls).

### CON-9 (CONFIRMED) a multi-target FILE without the grant writes the code-free targets, then refuses: "nothing is written" is not what happens
- Severity: doc (contract over-claims; no code is compiled, so trust holds).
  Effort: trivial for the spec ("the target holding the segment writes
  nothing; earlier targets are written as usual"), small for the code
  (check every target's grant before the first write, which is what
  inline_c.md §5.9's "emits zero bytes" reads as).
- Where: cli/main.c `compile_sources` (per-target compile-then-write);
  cli.md §1.22¶1 ("Without it a code segment is refused ... and nothing is
  written"), match_api.md §11.9¶8 ("every segment is refused by name and no
  artifact is written").
- Repro (contract/p11/two.rxt): `target ta = pa`, `target tb = pb`, `pa` =
  `ab`, `pb` = ``c(?C`c: return RX_PASS;`)d``; `pcrec -o o two.rxt` -> rc 1,
  refuses tb by name, and `o/ta.c`, `o/ta.h` exist. Also only the FIRST
  segment is named, not "every segment".

### CON-10 (CONFIRMED) describe modes refuse code under an explicit EMPTY grant
- Severity: doc/edge. Effort: trivial (treat "" like NULL in
  `pcrec_emit_ir`/`pcrec_emit_facts`, or say so in the spec).
- Where: src/core/compile.c:3601-3604 and src/dump/facts_dump.c:194-197
  (`if (!defo.allow_code) defo.allow_code = pcrec_code_all_langs();`).
- Spec: match_api.md §11.9¶8 and cli.md §1.22¶1: "the describe modes ...
  parse code without it". `pcrec --emit-ir --pattern 'a(?C`c: ...`)b'` -> rc 0;
  `pcrec --allow-code= --emit-ir ...` -> rc 1 "requires module 'code-c'".
  `""` and NULL both mean "no grant" everywhere else
  (`pcrec_code_grant_resolve`: "NULL or "" grants nothing"), so a describe
  mode's answer depends on how "no grant" was spelled. Code is wrong.

### CON-11 (CONFIRMED) a code site's refusals name module `callouts`, and one says it "is enabled" when it is not
- Severity: doc (D26 wording tier, but two of these state a false fact).
  Effort: small. Where: src/parse/mod_callouts.c `pcrec_callout_attrs`
  (shared with the code port); the tag-shape fallback to the binding row.
- `pcrec --allow-code=c --pattern 'a(?C`c,verify: return RX_PASS;`)b'` ->
  "module 'callouts' is enabled but the callout attribute 'verify' is not
  implemented yet": `callouts` is NOT enabled in that compile and the site's
  module is `code-c`.
- `(?C`c,: ...`)` (an empty attribute, which pattern_language.md §7.12¶3
  lists as a code refusal) and `(?C`py: x`)` (inline_c.md §2.4: "unknown tag
  ... refused by name") are not recognised as code at all: without
  `--features callouts` both answer "(?C...) requires module 'callouts'",
  with it "unknown callout attribute ': return RX_PASS;'" /
  "a (?C"...") string is a binding name ...". The REALITY is right (both are
  refused); per D26 the wording is not owed, except that "is enabled" and an
  "attribute" quoting the user's code are false statements. Spec §11.9¶1
  already says such strings "stay a binding name", so the design's
  "unknown tag refused by name" row is the stale document.

### CON-12 (CONFIRMED) §11.2¶1a "a binding the compiler can see ... is called directly" is false at -O0
- Severity: doc. Effort: trivial ("with optimization, -O1 and above").
- Repro (contract/p8/): two code sites; gcc 15.2 `-S`: `-O0` 2 indirect
  calls (`call *%rdx`-shape) and 0 direct; `-O1`, `-O2`, `-Os` 0 indirect,
  0 direct (inlined). The spec sentence is unconditional and also covers the
  user's unity build. The code is fine; the sentence needs its condition.

### CON-13 (SUSPECTED, latent for stage 3) a segment's `#line`/column is computed from the TARGET's pattern even when the segment came from a definition
- Severity: answer-of-diagnostics + memory safety, once reachable. Effort:
  small (carry the source text, line and file on the node, as the stage-3
  §1.9 lift needs anyway).
- Where: src/gen/emit_code.c:345-359 reads `cx->pat[i]` for `i < code_at`,
  but `code_at` (mod_code.c:230) is an offset into whichever text was being
  parsed, and `rc_bind` (rxt_compose.c:546-569) parses a definition with
  `cx->pat = def->pattern`. Unreachable TODAY: every same-file definition
  path is refused first by stage 1b's "callout inside a group reached by a
  subroutine call" (probed: `(?&d)`, `(?&s=d)`, `(?&=d)`, `(?&*=d)`), and lib
  code by §5.4 row 3. When stage 3 lifts §1.9 rows 3/4, a definition segment
  would be mapped to the target block's line, and `code_at` beyond the
  target's length reads past its buffer. Confirm: a stage-3 build with a
  definition segment whose offset exceeds the calling pattern's length,
  under ASan.

## PROBED-AND-HELD

Built compiler worktrees/crit-ic2/build/pcrec (SUBJECT), gcc 15.2. Scripts
in /tmp/claude-1001/crit-ic2/contract/p1.sh .. p6.sh and the probe dirs.

- Tag and attribute grammar (§2.2, §11.9¶1), 14 cases: `c,consume` compiles
  and consumes; `c,once` on `a+` refused naming the quantifier and the fix;
  `c,bogus` refused by name; `c,once,once` refused as repeated; `c,verify`
  refused (wording: CON-11); `(?C"c")` and `(?C"c,consume")` are bindings
  named `c` (rc 0); `x__y` refused for `__`; `C:` (upper) and `c :` are not
  code and are refused as bad binding names; `(?C"c:x")` without the grant
  refuses naming `code-c`. Held.
- Delimiters (§11.9¶2), 9 cases: `` ` `` `'` `"` `^` `%` `#` `$` `{`..`}`
  all compile; `{c: { return RX_PASS; }}}` (doubled `}}`) and ``"``"``
  inside a backtick string decode to one byte (macros.rxt cases run green
  here too). `(?x)`: a `#` inside a segment is kept (p12), and a `(?C` inside
  an `(?x)` comment, inside `\Q..\E` and inside `[...]` is not code (rc 0
  with no grant). Held.
- The grant (§11.9¶8, cli.md §1.22, §8.2¶7c), 16 cases: no grant, `--allow-code=`,
  `--features all`, `--features callouts` all refuse naming `--allow-code=c`
  and write 0 files; `-o -` without the grant writes 0 bytes to stdout;
  `--allow-code=c,c` ok; `c,` and `py` refused by name; later
  `--allow-code` wins both ways; `--trace` refuses without and compiles with;
  a header-only target (`code-header`, no segment) refused without the grant,
  emitted with it; config `pcrec --code-header=...`, `pcrec --features=code-c`
  and a fragment's `code-header` line refused; rxt bare header and unknown
  language refused by value shape. Library: `allow_code` NULL / "" refuse,
  "c" compiles. Held (except CON-9, CON-10).
- REACHED code (§5.4 row 3): a lib definition's segment refused by
  `file:line` for plain and delivering calls; an include fragment's blocks
  are never FILE targets, and a target cannot name a fragment's definition.
  Held.
- Refusal list (§11.9¶3): U+200E, U+202E, U+2066, U+FEFF refused with code
  point and byte offset; DEL and \x01 refused; NUL cannot arrive (K9). The
  list itself: CON-1.
- Macro set (§11.9¶5), 13 driver cases: RX_POS/RX_START (unanchored attempt
  at 2; after `\K` the attempt start, not the moved start); RX_USER NULL;
  eval-once for RX_CAP_SET/RX_CAP_P/RX_CAP/RX_CAP_LEN/RX_CAP_S/RX_CAP_E with
  `i++`; slot 0, 99, -5, 7 read unset; a repeated group's view inside its
  second iteration reads the previous iteration ({0,2}); RX_G_ of a (?J) run
  with none set reads the first number and RX_CAP_SET false, with a later
  member set reads 3; a non-ASCII name has no macro (gcc: undeclared
  `RX_G_é`) and its ASCII sibling has one. Held (except CON-6).
- Trap (§11.9¶4, §11.4¶2): falling off the end, a check returning 1, and a
  consume past the subject end all die with SIGILL. Held.
- `#line` and columns (§11.9¶4), 11 cases: rxt `pattern` line a.rxt:3:25;
  named target h.rxt:4:25; two segments on one line, the second at 1:49;
  a non-ASCII byte and a TAB before the segment: right line, no padding;
  doubled delimiter: right line, no padding; `pattern-esc` and
  `--pattern-esc` multi-line: every decoded line `#line` the opener's line,
  error on the right line; `--pattern` single and multi-line
  `<command line>:1:17` / `:3:10`; library `<pattern>:2:16`; missing header
  `i.rxt:1:10`. Held (except CON-7). A TAB between `pattern` and its value is
  refused by the format itself, so `RxtRow.col`'s TAB branch never fires.
- Placement, order, dedup (§11.9¶4, ¶7): headers after the matcher and after
  `main()` under `--emit-main` (segment definition is the last thing in the
  `.c`), in order, `c:b.h` and `c:"b.h"` deduplicated, none in the `.h`;
  `-Wall -Wextra -Werror -Wbidi-chars=any` clean with the headers present;
  two code artifacts (`-p ra`, `-p rb`) in one TU compile. Held.
- Stamps (§6.3): `RX_CODE_LANGS "c"` in the `.h` (and in the `.c` under
  `-o -`); absent on a binding-only artifact; `RX_CALLOUT_BINDINGS ""` when
  every site is code, `"rx_callout_3,rx_callout_zz"` mixed; span helpers on
  every callout artifact, none on a callout-free one; abi 90 in the
  provenance line, the guard and the changelog. Held.
- `--emit-main` (cli.md §1.10¶2, §11.2¶2): code-only accepted and the program
  answers 0/1; code + `(?C"q")` + `(?C"p")` refused naming `rx_callout_q`
  (first in site order). Held.
- Entry points (§5.9): `--emit-ir`, `--emit-facts`, `--count-groups` parse
  code with no grant; the IR listing prints the pattern escaped
  (`\x0a`), `--emit-facts` prints no code text; `--explain` describes the row
  with the grant sentence; `--list-syntax` shows `code-c` `invoker-only`.
  `--list-callouts` is stage 3 (§9.1), so not probed. Held (except CON-10).
- Span helpers (§11.10), 40 calls: UINT64_MAX ok, +1 refused with `*out`
  untouched, 45-digit leading-zero form ok, empty/`+1`/` 1` refused;
  16 hex digits ok, 17 refused, `0x` refused, leading zeros ok, `g`/`G`/`@`/
  `` ` `` refused; rx_in bounds; rx_eqi folds only A-Z (`\xC3\x89` vs
  `\xC3\xA9`, `@`/`` ` ``, `[`/`{` all 0); rx_eq length mismatch both ways;
  rx_find empty needle 0, in empty span 0, unset -1; rx_u8next refuses
  C0 80, C1 BF, E0 80 80, E0 9F BF, ED A0 80, ED BF BF, F0 80 80 80,
  F4 90 80 80, F5.., truncated E2 82, bad continuation, lone 80, each with
  `*i`/`*cp` unchanged, and decodes U+00E9, U+1F600, U+FFFF. One note: a
  negative `*i` returns 0 ("at the end"), which §11.10 does not mention.
- ONE CALL FORM (§11.2¶1a): sites call `rx__code<k>_ref.fn(&rx_co_ctx)`
  through `static const rx_callout_ref`; inlined (0 calls) at -O1/-O2/-Os.
  Held (except CON-12).
- D174 names: `--allow-code`, `allow_code`, `code-header`, `invoker-only`,
  `<PREFIX>_CODE_LANGS`, `RX_CAP*`, `rx_*` describe what a caller sees; none
  names a mechanism. Held.
