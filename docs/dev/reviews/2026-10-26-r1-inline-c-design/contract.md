# CON critic, inline-c

Lens: contract + trust. Subject: `subject_inline_c.md` (frozen rev 0).
Probes: `/tmp/claude-1001/crit-inline-c/probes/CON/` (build/pcrec at main
8f4fd7631, gcc, libpcre2 10.46). No denylisted file opened; no auto-injection
observed.

## Findings

### CON-1  `features all` (and the library's `features = "all"`) would grant code; the note refuses only a line that NAMES `code-c`
- status: CONFIRMED. Probe `fa.rxt`: a block line `features all` in a FILE is accepted today
  and the artifact stamps `PCREC_FEATURE_MODULES "classes,unicode-props,...,callouts,...,vars"`.
  `all` means every registered module (`cli.md` §1.17¶1). Once `code-c` is a registry module,
  `features all` in a FILE, or `pcrec_options.features = "all"` in a tool, enables it.
  inline_c §5.1 refuses only "a `features` line naming `code-c`"; §2.4 the same.
- severity: trust (also size/abi)
- effort: paragraph edit
- blast radius: enabled.c's `all`/named-set resolution; `PCREC_FEATURE_MODULES`; 366 corpus `.rxt` files use `features all`.
- where: inline_c §5.1, §2.4, §8.1 ("ZERO movers"); cli.md §1.17¶1; D178 addendum (a) (a new module moves `PCREC_FEATURE_MODULES` on every `all` artifact)
- argument: Goal 1 says nothing but the command line grants code. `all` is a wildcard that a file may
  write, so the opt-in can be satisfied without naming the module. Separately, if `code-c` joins the
  roster, every `--features all` artifact's `PCREC_FEATURE_MODULES` string changes at stage 2.
  That contradicts §8.1's "zero movers in the existing corpus" (the D178 addendum gives exactly this reason
  for not adding a module). `callouts` is already in the roster, so stage 1 does not have this problem;
  stage 2 does.
- proposed fix: state that `code-<lang>` modules belong to NO features vocabulary: not in `all`, not in
  any named set, and not nameable in `--features`/`features`/`pcrec_options.features`. The only way to
  set them is the `--allow-code`/options member. Disclose them through `<PREFIX>_CODE`, not through
  `PCREC_FEATURE_MODULES`. Add a refusal test for `features all` + a segment.

### CON-2  The `.rxt` harness compiles every block, fragment blocks included, as `--pattern` text, which makes reached code LOCAL
- status: CONFIRMED. `tests/harness/run.sh:1894` compiles each block with
  `"$PCREC" ... -o "$bdir/gen.c" --pattern "$cur_pattern"`; `rxt_format.md` §4¶8 runs every block of
  every `include` fragment as part of the entry's own turn. inline_c §5.2 classes `--pattern` text as
  LOCAL, so under the callouts runner's `--allow-code=c` (§5.7) a segment in an UNPINNED fragment compiles.
- severity: trust
- effort: section rewrite (§5.2/§5.7), plus a harness change in stage 3
- blast radius: run.sh, verify_rxt.py (the third reader, `rxt_format.md` §1.5¶3), stage 3 tests
- where: inline_c §5.2, §5.4 rows 2-3, §5.7, goal 1's ".rxt harness" entry point; run.sh:1644/1894
- argument: Goal 1 lists the harness as an entry point. Its pin rule (§5.4 row 3) assumes pcrec knows
  where a segment came from, but the harness hands the bytes over as a command-line literal and that
  knowledge is gone. Stage 3's planned test "unpinned include refused", run through the harness, would
  PASS the unpinned fragment's code. A check written that way would agree with itself.
- proposed fix: give the harness a provenance-preserving compile: build fragment blocks through the
  FILE path (or pass `--source-of FILE:LINE` so pcrec applies §5.4). Alternatively, rule that the harness
  refuses `--allow-code` for any block whose file is not the entry. State the rule in §5.2.

### CON-3  In v1 no REACHED code can ever compile through the CLI, so the pin machinery (stage 3) has no positive case
- status: CONFIRMED (text + probe). A `lib`'s content reaches a target ONLY through a call `(?&name)`
  (probe `inc/m2.rxt` builds; `inc/m3.rxt` `target rx = <lib def>` is refused, "no definition"). An
  `include` fragment's blocks are never CLI targets (probe `inc/main.rxt`: `target rx = fr` → "no
  definition 'fr'"). inline_c §1.9 row 3 refuses a site "inside a group reachable by ... `(?&n)`".
- severity: design
- effort: paragraph edit (re-scope stage 3) or a §1.9 decision
- blast radius: §5.3-§5.5, §3.3's lib `code-header` rule, stage 3's SHA-256 implementation and tests
- where: inline_c §1.9 rows 3-4, §5.4 rows 3-4, §3.3 "the head of every lib file that contributes a segment", §9.1 stage 3
- argument: Through the CLI, every reached segment is refused by §1.9 before §5.4 is consulted. Through
  the harness, every reached segment is laundered to LOCAL (CON-2). So row 4 ("allowed when pinned") has
  no input that reaches it in v1, and stage 3's "pinned lib → allowed" test cannot be written. Stage 3
  builds an in-tree SHA-256, chains and a listing to protect a path that does not exist yet (D77: build
  under measurement). Row 4 of §1.9 also makes rows 3/4 ambiguous: if row 3 already covers `(?&n)`, row
  4 is redundant; if it does not, then the view (`ncap`, enclosing groups) at a site inside a plain-called
  lib definition is unspecified. A plain call is capture-transparent (`rxt_format.md` §1.2), so whose group
  numbers would `ncap` count?
- proposed fix: say plainly that v1 refuses all reached code (§1.9 is the refusal, and its diagnostic names
  "reached" rather than a position). Move pins to the stage that lifts §1.9 row 3/4, so they are triggered by
  the first reachable case. Or, if pins stay in v1, name the input that reaches §5.4 row 4.

### CON-4  The slot-0 store overwrites the VM's `\K` register: `a\K(?C1)b` reports the wrong match start
- status: CONFIRMED (emitted code). Probe `k.c` (`(a)\Kb`, `--engine=vm`): `\K` is
  `RX_SET(RX_SLOT_WHOLE_START, scan_position)`, and `rx_report_captures` reports
  `capture_spans[0][0] = slot_values[0] != PCREC_UNSET ? slot_values[0] : match_start`. inline_c §1.2 step 2
  writes `stv[0] = attempt start` into "the VM's working slot array" (§1.2 step 1: `caps` IS that array),
  untrailed, at every fire.
- severity: answer
- effort: paragraph edit
- blast radius: §1.2, §1.3 slot-0 rule, §8.1 cost claim ("one store per fire")
- where: inline_c §1.2 step 2, §1.3 third bullet ("On a completed match the entry overwrites slot 0 as today": it does not overwrite, it READS slot 0 as the `\K` mark)
- argument: On `a\K(?C"p")b` over `ab` with a passing binding, the site turns slot 0 from `1` (the `\K` mark)
  into `0`, and the report gives `[0,2)` where PCRE2 gives `[1,2)`. A site before `\K` is harmless, and so is a
  pattern without `\K`, which explains why nothing in stage 1's planned tests catches it. §1.9 does not
  refuse `\K` with callouts.
- proposed fix: the callee must see `start_match` without the VM losing the `\K` mark. Options: save slot
  0, store, call, restore (two more stores on the fire path); give `\K` its own slot in callout artifacts;
  or build the view's slot-0 pair in a 2-word local and point `caps` at a view whose pair 0 is that local
  (costs the caps-is-the-working-array property). Add `a\K(?C"p")b` to stage 1, with a sabotage row.

### CON-5  The artifact's ASCII / `-Werror` / `-Wbidi-chars` promise breaks with verbatim user text; no spec hunk, and the reviewer's view inherits Trojan Source
- status: CONFIRMED (spec text + probe). `match_api.md` (just above §6.1, line ~1775-1789) promises
  "every byte of the artifact, `.c` and `.h`, is ASCII under every option, and it compiles clean under
  `-Wall -Wextra -Werror -Wbidi-chars` for any pattern". inline_c §3.1 emits the decoded segment
  verbatim, so that promise no longer holds; §8.2 schedules no hunk for that paragraph. Probe
  `bidi.rxt`: `--list-source` passes U+202E (RLO) and other non-ASCII bytes through RAW (it escapes
  only control bytes; `esc.rxt` shows `\x1b`). inline_c §5.6 says `--list-callouts` prints "the DECODED
  code" with no escaping rule.
- severity: trust (reviewer view), doc (spec promise)
- effort: paragraph edit + a spec hunk
- blast radius: match_api.md's ASCII paragraph, `-Werror` statements in testing docs/strict checks over generated code, `--list-callouts`
- where: inline_c §3.1, §5.6, §8.2; match_api.md:1775-1789; internal.h `pcrec_sb_ctext` ([EMIT-BIDI])
- argument: Q5's trust model is "re-inspect the file and update the pin" (§5.5 diagnostic). The tool for
  that inspection is `--list-callouts`. If it prints bidi overrides raw, a reviewer can see different code
  from what gcc compiles (CVE-2021-42574 shape), and gcc's default `-Wbidi-chars=unpaired` misses paired
  overrides. pcrec's emitter treats user bytes as untrusted everywhere else ([EMIT-BIDI]); this note is
  the first place user bytes reach the artifact unescaped, and it says nothing about that.
- proposed fix: (a) a spec hunk: the ASCII promise covers everything except segment bodies, which are the
  user's bytes as written. (b) `--list-callouts` prints the code column through an escaper that numbers
  every non-printable-ASCII byte, or flags any bidi/invisible format character in a segment. (c) Optionally,
  refuse a segment that contains Unicode bidi controls unless the user opts in (one row, same tier as
  §2.4).

### CON-6  `code-header` includes land BEFORE the generated matcher, so a user header's macros and pragmas can rewrite it; segments see live artifact-internal macros
- status: CONFIRMED (emitted text). inline_c §3.3: "Emitted ... after pcrec's own includes", which
  puts them ahead of the whole VM body. The VM body uses plain identifiers (`run`, `subject`,
  `subject_length`, `scan_position`, `capture_spans`, `group`, `i`; probe `v.c`/`k.c`). Macros still
  live at the end of the `.c`, where §3.1 puts the segments: `RX_CUT`, `RX_PRUNE_TOO_SHORT`,
  `RX_PRUNE_CLAMP_SPAN`, `RX_SLOT_*`, `RX_R_*`, `rx_VALID_LB` (lower-case, prefix-scoped), all stamps
  (probe `v.c`: defined, never `#undef`ed).
- severity: answer (header → matcher), maintenance (collision check)
- effort: paragraph edit
- blast radius: §3.3 placement, §3.2's disjointness check
- where: inline_c §3.3 first bullet, §3.2 "One collision to keep closed"
- argument: A user header containing `#define group ...`, `#pragma GCC optimize`, `#pragma pack`, or a
  `likely`/`min` macro can silently change or break the matcher. That is a miscompile which the trusted
  opt-in does not excuse: the user trusted their own code, not a rewrite of pcrec's. The segment
  prototypes before the VM need only `rx_ctx`, so nothing requires the includes to come early.
  §3.2's check compares the macro set against the STAMP inventory only. The live internal macros
  (`RX_CUT`, `RX_SLOT_GROUP1_END`, and the pattern-dependent `RX_VAR_<name>` / `RX_SLOT_GROUP<n>_*`)
  are wider than that, and a single-artifact check cannot cover pattern-dependent names.
- proposed fix: emit the `code-header` includes immediately before the first segment definition, after the
  matcher, and `#undef` (or never let escape) the artifact-internal macros before that point. Make §3.2's
  check "every identifier `#define`d and live at the segment block ∩ the macro set", computed from a
  corpus of artifacts, not one.

### CON-7  `verify` + `consume` (a `W_ANY` tail) makes §4.2's `e` meaningless
- status: CONFIRMED (design text). §2.2 admits `c,verify,consume:`. §4.2 builds the scan as "the
  capture-erased DFA of the pattern with each site erased by its width class", where a `W_ANY` site
  erases to "any bytes, any length" (§1.8). §4.2 step 1 then calls the tail at `pos = e`, treating `e`
  as the end of `R`.
- severity: answer
- effort: paragraph edit (one 4.3 row, or scan `R` alone)
- blast radius: §4.2, §4.3, §4.4 item 2
- where: inline_c §4.2, §4.3 (no row tests the tail's width), §4.4 item 2
- argument: For `R (?{c,verify,consume: ...})` the scanned language is `R·Σ*`, so the leftmost-first
  end is (greedily) the subject end, not `R`'s end. The tail runs at `len` and returns 0, and the answer
  is `[s, len)` where the reference gives `[s, e_R + k)`. §4.4's proof assumes the scan proves the end
  of `R`, which is true only when the tail erases to the empty string.
- proposed fix: build `scan-end`'s scan from `R` with the tail REMOVED, not erased, or add a 4.3 row
  `consuming-tail → hybrid without scan-end`. State which in §4.2.

### CON-8  §4.3 row 5 keys on DELIVERED captures (`NCAPS > 1`); under `--no-captures` a group-reading `verify` segment reaches `scan-end` with `ncap = 1`
- status: CONFIRMED (spec text). `cli.md` §1.11: `--no-captures` emits `RX_NCAPS 1` for a group-bearing
  pattern, and `--engine=vm --no-captures` builds a VM artifact. §4.3 row 5 fires only on
  `<PREFIX>_NCAPS > 1`. §4.2 step 1 builds `ncap = 1`. §1.3 gives the inline path `ncap = 1 + highest
  group opened before the site` (lexical).
- severity: answer
- effort: paragraph edit
- blast radius: §4.3 row 5, §1.3 (the view under `--no-captures` is not stated at all)
- where: inline_c §4.3 row 5, §4.4 item 2 ("With no capture slots beyond 0 (row 5)")
- argument: `(\d+)(?{c,verify: return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;})` with `--no-captures`:
  on `scan-end`, `RX_CAP_LEN(1)` is `-1` and the segment passes. Inline, group 1 is set and the segment
  vetoes `1234`. The deny flag would turn `make test-axes` red, but only if the corpus carries a
  `--no-captures` callout case, and the stage 4 test list has none.
- proposed fix: make row 5 "some `verify` site's `ncap > 1`" (the lexical fact). In §1.3, state that a
  site's groups are kept (as an `A_BREF`'s are) whatever `--no-captures` says.

### CON-9  `ext harness` + `link c` breaks `rxt_format.md` §1.12's graduation rule and is a C-execution path no opt-in gates
- status: CONFIRMED (spec text). §1.12¶9-¶14: "The day something in an `ext` block needs pcrec to ACT on
  it, it must GRADUATE ... 'Act on' means any of: a build reads it, a check reads it". inline_c §3.6:
  "The harness is the consumer; pcrec only carries the block ... the format gains no line kind". The
  harness is pcrec's own `make test`, and stage 1 uses `link` stubs with no `--allow-code` anywhere.
- severity: trust / design
- effort: paragraph edit + a schema row
- blast radius: rxt_format §1.12, run.sh, verify_rxt.py, stage 1 tests
- where: inline_c §3.6, §9.1 stage 1 ("stubs linked through `ext harness`"), §5.7
- argument: A `.rxt` file that names a C source makes the harness compile, link and RUN it. That is
  code from a pattern file with no `--allow-code`, which goal 1 exists to forbid ("a pattern source never
  becomes code without the invoker's say-so"), even if the harness is the program doing it. Aux
  data was promised never to be acted on (¶16: "a consumer who cannot cite a sentence saying pcrec
  will not read this ...").
- proposed fix: graduate it to a real production (a `link` head row with a schema row and a wave). Gate it
  with the same visible opt-in the callouts runner passes, and allow it only in the entry file, with a
  path under the entry's own directory.

### CON-10  Multi-line segments: `#line` points at the wrong `.rxt` line from the second line on
- status: CONFIRMED (format text). `pattern` is rest-of-line (`rxt_format.md` §1.5¶2), and
  `pattern`/`pattern-esc` are `RAW` rows with no prose-region form (`rxt_schema.def:201-202`). So
  multi-line code in a FILE exists ONLY as `pattern-esc` `\n` escapes on ONE physical line. inline_c
  §3.4: one `#line` before the text, "counting the newlines a `pattern-esc` value carries".
- severity: doc (goal 4's measurable "a compile error ... reported at the pattern file's own line")
- effort: paragraph edit
- blast radius: §3.1 example, §3.4, DT-3.3
- where: inline_c §3.1 (one `#line`, column padding), §3.4
- argument: gcc numbers decoded line k as `N+k`, which is an unrelated line of the `.rxt`. Counting
  decoded newlines for the FIRST byte moves it off its own physical line too. Column padding by byte
  count is also wrong where the prefix holds a tab (gcc `-ftabstop=8`), a multi-byte character (display
  columns), or an undone `}}`/`\n` escape before the code.
- proposed fix: emit `#line N` before EVERY decoded line (same N, mapped column), or state that
  diagnostics name the segment's line and not the sub-line. Specify the column as gcc's display column.

### CON-11  §8.2's spec-hunk list misses whole files and paragraphs that the design falsifies (D80)
- status: CONFIRMED (grep). Paragraphs that become false or incomplete and are not in §8.2:
  - `pattern_language.md` (line 565 module table, §8.1 `(?C1)` row): the syntax spec for `(?C` and the new
    `(?{`. No hunk at all.
  - `registry.md` §2 `module` roster (line 45, lists the modules by name), plus PC-3 (§7¶2), which checks
    every `RS_MODULE` row's existence against PCRE2. `(?{` is refused by PCRE2 (error 111), so the row needs
    the extension treatment, stated.
  - `ir_listing.md` §3.7¶1: "Module `callouts` has no producer, so this section is empty on every artifact."
  - `match_api.md` §2¶6: "Every emitted call site sets `ncap = 0` and nothing advances it ... no caller can
    observe a watermark". §1.3 makes it a per-site constant; §8.2 names §5 but not §2¶6.
  - `match_api.md` §1¶6 (unprefixed contract macros live in the shared ABI block, unconditionally):
    `RX_CALLOUT_PCRE2` (§7) is unprefixed, conditional and outside it.
  - `cli.md` §1.17¶3 roster; §2.10/§2.13 (`--emit-ir`, `--count-groups` on a code pattern); `cli.md` §2 row
    2 of the namespace table ("reserved; not yet enforced").
  - `rxt_format.md` §1.1's `lib` row ("named definitions — and nothing else, not its configs, targets or
    cases") versus §3.3's lib `code-header` lines; §2 `--list-source` columns for `sha256=`; §1.12 (CON-9).
  - `match_api.md`'s ASCII paragraph (CON-5).
- severity: doc
- effort: paragraph edit to §8.2
- blast radius: none beyond the table
- where: inline_c §8.2
- proposed fix: add the rows. Better: derive the list by grepping the tree for `callout`, `(?C`, `ncap`,
  the module roster and the ASCII promise, the way D94 requires readers to be found by grep.

### CON-12  Goal 1's entry-point list is hand-enumerated and incomplete; whether a non-emitting query needs the opt-in is unstated
- status: CONFIRMED (cli.md §2 index). Goal 1 lists the CLI FILE, `--pattern`, the library, the harness,
  and "every `--list-*` that compiles". Also parsing a pattern: `--emit-ir` (§2.10), `--emit-facts`
  (§2.11), `--count-groups --pattern` (§2.13), `--probe-ask` (§2.14), `--emit-main`, `--trace`,
  `--pattern-esc`, and the new `--list-callouts`.
- severity: doc / trust
- effort: paragraph edit
- blast radius: stage 2's refusal-test list
- where: inline_c goal 1, §5.6, §9.1 stage 2
- argument: `--list-callouts` must work WITHOUT `--allow-code`: its job is to let a reviewer read code
  BEFORE trusting it. That is a deliberate exception to "refuse every segment", and the note never makes
  it. `--count-groups` must also scan past a segment to count later groups. Each query needs a ruled
  answer and a refusal or acceptance test. Deriving the list from the CLI's own mode table, as the
  registry derives its roster, would stop it from drifting.
- proposed fix: a table with one row per pattern-taking mode: refuses / parses-without-emitting / lists-escaped
  (CON-5). Generate the test from the mode table.

### CON-13  An unbound binding is a link error, and nothing in the note says so; existing `features all` consumers change outcome class
- status: CONFIRMED (bench data). pcrec-bench's `grp-callout` pattern `ca(?C1)t` is `did_not_compile`
  ("module 'callouts' is enabled but (?C...) is not implemented yet") in
  `reports/2026-10-26-syntax-0.1-ryzen7700x-rebaseline-6b2dbd3e.subject-grain.tsv`. After stage 1 it
  compiles, and the bench driver fails at LINK (undefined `rx_callout_1`). An `--emit-main` build of
  `(?C1)` cannot link either. PCRE2 runs a pattern that has callouts but no callout function by IGNORING them.
- severity: doc (contract), plus a cross-repo heads-up
- effort: paragraph edit
- blast radius: bench outcome classes (D78 inbox), harness `perr`/compile expectations under `features all`, `--emit-main`
- where: inline_c §1.4 rows 2-3, §8.1 ("zero movers" is about bytes, but outcomes move)
- argument: "Same answer as PCRE2 for a pure callout" (goal 2) quietly assumes a binding exists. The
  contract for the absent binding (link error by design, D38) has to be stated, and so does `--emit-main`'s
  behaviour (refuse a binding site by name, or emit nothing).
- proposed fix: one spec sentence: an artifact with a binding site requires the user to define
  `rx_callout_<name>`, and an undefined one is a link error. Have `--emit-main` refuse binding sites by name.
  Add an `[inbox]` note to pcrec-bench at stage 1 landing.

### CON-14  Return-table rows 9-10 "checked before row 1": spelled literally, row 10 traps on every `-1`
- status: SUSPECTED (spec ambiguity; C semantics certain). Row 10 is `ret > len - pos`, with `ret` a
  `ptrdiff_t` and `len - pos` a `size_t`. Usual arithmetic conversions make `-1 > len-pos` true. §1.6
  says rows 9 and 10 are "checked before row 1 (first match)" and does not say whether that is also
  before rows 2-8.
- severity: doc (answer if implemented literally)
- effort: paragraph edit
- where: inline_c §1.6
- proposed fix: "rows 9-10 apply to `ret >= 0` only; order 2-8, then 9, 10, then 1", and give the
  comparison as `(size_t)ret > len - pos` after the sign test.

### CON-15  The macro set: `n` is evaluated more than once, `RX_START` and `RX_CAP_S(0)` disagree, and non-ASCII group names
- status: CONFIRMED (text + probe). The §3.2 guarded forms (`RX_CAP_S(n)`: check, then index) must
  evaluate `n` at least twice as macros; `RX_CAP_S(i++)` misbehaves, and the note says nothing.
  Slot 0 is `{start, UNSET}`, so `RX_CAP_SET(0)` is false and `RX_CAP_S(0)` is `-1`, while `RX_START`
  is the start. Unset `RX_CAP_LEN` is `-1`, so the headline example `RX_CAP_LEN(1) <= 3 && f(RX_CAP_P(1), ...)`
  passes `NULL, -1` to the user's function when group 1 is unset. Probe `u.c`: pcrec accepts
  `(?<café>a)` under `-e utf8`, as does libpcre2 (`p2.c`: ok), so `RX_G_café` is a non-ASCII
  identifier. §3.2 exempts only names containing `.`.
- severity: doc / maintenance
- effort: paragraph edit
- where: inline_c §3.2, §3.1 example
- proposed fix: define the accessors as GNU statement expressions (or `static inline` helpers in the
  generated namespace) that evaluate `n` once, and say so. State the slot-0 accessor rule. Give non-ASCII
  names no `RX_G_` macro, or spell them with UCNs (`é`, ASCII and accepted by gcc). Use an example
  that tests `RX_CAP_SET` first.

### CON-16  `RX_CALLOUT_PCRE2`: compiles clean, but a binding name containing `__` collides with its helper, and it has no home in a self-contained artifact; `RX_PASS`/`RX_FAIL` scope contradicts §1.5
- status: CONFIRMED (probe `w.c`). The macro compiles with `-std=gnu11 -Wall -Wextra -pedantic` with no
  diagnostics. The pattern `(?C"pcre2__octet")`, which declares `extern const rx_callout_ref rx_callout_pcre2__octet;`,
  combined with `RX_CALLOUT_PCRE2(octet, ...)` in one TU gives "error: 'rx_callout_pcre2__octet' redeclared as
  different kind of symbol". §7 puts the macro "in the `.h`", but `-o -` (`match_api.md` §1¶8) has no
  `.h`. §1.5 introduces `RX_PASS`/`RX_FAIL` as "named macros for the user's returns", but §3.2 defines
  them only inside segment bodies (`#undef`ed after), so a hand-written binding cannot use them.
- severity: doc
- effort: paragraph edit
- where: inline_c §7, §1.4 (binding-name grammar), §1.5, §3.2
- proposed fix: refuse binding names containing `__` (mirroring the prefix rule, D41.1). Put
  `RX_CALLOUT_PCRE2` and `RX_PASS`/`RX_FAIL` in the shared ABI block on callout artifacts, or say where
  they live in each artifact form.

### CON-17  The same file reached by two chains, and hashing the bytes that are parsed
- status: SUSPECTED. `rxt_source.c` `closure_walk` skips a lib already seen by realpath
  (`if (closure_seen(cl, rp)) continue;`), so a file reached by a pinned and an unpinned chain is
  parsed ONCE, and its definitions carry the first chain only. §5.4 row 3 says "some line on the chain".
  §5.3/§5.5 hash "the file's bytes exactly as read" but do not require the hash to be computed over the
  same read that is parsed.
- severity: trust (low)
- effort: paragraph edit
- where: inline_c §5.4, §5.5
- argument: The bytes are identical (one realpath), so the content argument holds, but the refusal and
  the listing's chain then depend on declaration order. A hash taken in a second `open` is a TOCTOU window.
- proposed fix: state "refused if ANY chain reaching the file is unpinned" (or "allowed if any is
  pinned", and say which), and "the hash is computed over the buffer that is parsed (one read)".

### CON-18  Artifact-as-callout across encodings is unstated
- status: CONFIRMED (text). §6 binds any `<prefix>_match`. A `-e utf8` inner called from a byte outer can
  get a mid-character `pos`, so the inner returns `PCREC_ERR_STARTPOS` and the outer's §1.6 row 6 traps.
  A byte inner inside a utf8 outer can consume half a character, and row 10 traps.
- severity: doc
- effort: one sentence
- where: inline_c §6
- proposed fix: state that composed artifacts must share the encoding, and that a mismatch traps at the
  first misaligned fire (or refuse it at link time with an encoding-stamped binding, if wanted later).

### CON-19  Names (D174): stamp values name mechanisms
- status: CONFIRMED (text). `<PREFIX>_CALLOUT_VERIFY` carries the 4.3 row names (`scan-end`, `no-scan`,
  `end-unproven`, `not-tail`), which are internal mechanism names in a caller-observable stamp.
  `<PREFIX>_CODE` says nothing about its value (a language list).
- severity: doc
- effort: paragraph edit
- where: inline_c §4.3, §5.6, §8.1
- proposed fix: give the stamp values what the caller sees (`checked-after-match`, `checked-inline:<reason>`),
  and rename `_CODE` to `_CODE_LANGS`. `--allow-code`, `code-header`, `consume` and `RX_CALLOUT_PCRE2`
  describe behaviour and are fine.

## PROBED-AND-HELD

- Echo of pattern text into C: the provenance line escapes via `pcrec_sb_ctext` (probe `a*/b` →
  `a*\x2fb`; `(?<café>)` → `"caf\303\251"` in `rx_info`). A segment's code repeated in the
  provenance comment is safe today. (2 probes)
- `#line` with a `PCREC_CTEXT_STRING`-escaped file name: gcc decodes octal and `\"` in the
  name and reports `café "q".rxt:4:10` (probe `l.c`). The existing escaper is enough for §3.4. The only
  gap is naming it (and the frame `COMMENT` for §3.1's comment). (1 probe)
- Without `--allow-code`, the binding-name path: the name must be a C identifier, so attacker bytes
  become only the identifier `rx_callout_<ident>`, never C text. The attacker can choose WHICH
  user-defined binding a site calls. That is inherent in D38's link-level binding, and an `rx_matchfn` must accept
  any `ctx`. Held.
- The config `pcrec` line already refuses non-compile options (probe `fb.rxt`: "compile options only").
  The §5.1 refusal of `--allow-code` there has a mechanism to ride.
- `${name}` (module `vars`) is a run-time construct, not a textual splice, and lib definitions reach a
  pattern only through calls (probes `inc/m2`, `inc/m3`). No path splices reached pattern TEXT into a
  local segment.
- Pin transitivity (§5.4): a content hash makes symlinks, realpath and `--lib-path` order irrelevant, and
  "every link pinned ⇒ every byte below fixed" is sound.
- `RX_CALLOUT_PCRE2` as written compiles clean under `-std=gnu11 -Wall -Wextra -pedantic`
  (`__builtin_trap` is noreturn, so there is no `-Wreturn-type`). A file-scope `const` object has external linkage in C,
  which matches the artifact's `extern const` declaration (probe `w.c`).
- `rx_ctx.caps` (`const ptrdiff_t (*)[2]`) over the VM's `ptrdiff_t slot_values[]` is type-correct (probe
  `v.c` line 73). `ncap >= 1` at every site keeps `RX_START`'s `caps[0][0]` in bounds.
- Return table rows 1-8 match `match_api.md` §4¶10 verbatim. Rows 9-10 are additive.
- `--list-source` escapes control bytes (`\x1b` in probe `esc.rxt`). It does NOT escape non-ASCII/bidi
  (CON-5).
- libpcre2 10.46 accepts non-ASCII group names under UTF and refuses `.` in names (probe `p2.c`; error 142).

Counts: 19 findings (answer 4: CON-4, CON-6, CON-7, CON-8; trust 5: CON-1, CON-2, CON-5, CON-9, CON-17;
design 1: CON-3; doc 9: CON-10 to CON-16, CON-18, CON-19). About 20 probes run (pcrec 12, gcc 4,
libpcre2 1, bench/greps 3). 10 PROBED-AND-HELD items.

## DONE
