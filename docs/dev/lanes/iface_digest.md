# Interface digest — facts extracted for the D116 interface discussion

Chartered by [D116] (`docs/dev/decisions.md`, last entry): Frank wants to
discuss the pcrec interface before the user guide is written. This is
FACTS EXTRACTED — no recommendations, no process prose. Every claim cites
`file:line` or the `--help`/`--version` line it came from. Sources:
`docs/spec/{cli,match_api,tuning,limits,registry,table_contract,rxt_format,
ir_listing}.md`, `lib/pcrec.h`, `cli/main.c`'s usage text, `APPROACH.md`.
Lane `rel1b` is landing `--version` (D115) concurrently — marked LANDING
below, not present in the built `build/pcrec` at the time this was written
(confirmed live: `build/pcrec --version` → "unknown option '--version'").

---

## 1. The three surfaces

**(a) The CLI.** `pcrec [options] -o OUT.c [--] 'PATTERN'` (`cli/main.c:142`).
`-o FILE` writes `FILE` (C) plus a matching `.h`; `-o -` prints
self-contained C with no header to stdout (`cli/main.c:143-145`). `-p
PREFIX` sets the generated-symbol prefix, default `rx` (`cli/main.c:146`).
A pattern is a positional argv operand, or `--pattern-esc` decodes it in
the `.rxt` quoted-escape form first (`\" \\ \n \t \r \f \v \xHH`;
`cli/main.c:155-158`). `--source FILE` switches to compiling a `.rxt`
SOURCE file's `target` lines instead of a positional pattern — one target
per translation unit, `-o` takes a FILE (one target), an existing
DIRECTORY (`<dir>/<prefix>.{c,h}` per target) or `-` (one target, stdout)
(`cli/main.c:234-243`; `docs/spec/cli.md:488-656`). Seven no-pattern
`--list-*` registry dumps and three query modes (`--explain`,
`--count-groups`, `--probe-ask`) round out the surface (`cli/main.c:250-305`).

**(b) The library** (`lib/pcrec.h`, the ONLY public header — `lib/CLAUDE.md`).
Four functions:

| function | role |
|---|---|
| `void pcrec_default_options(pcrec_options *opt)` | fills `opt` with defaults (zeroed struct; `lib/pcrec.h:1031`) |
| `int pcrec_compile(const char *pattern, const pcrec_options *opt, pcrec_output *out, pcrec_error *err)` | compiles `pattern` (NUL-terminated, no length param — §4 below) to C; returns 0 and fills `out`, or −1 and fills `err` if non-NULL (`lib/pcrec.h:1034-1035`) |
| `void pcrec_output_free(pcrec_output *out)` | frees `out->c_src`/`out->h_src` (`lib/pcrec.h:1133`) |
| `char *pcrec_limits_tsv(void)` | returns a `malloc`'d TSV of every numeric limit and its raise-only override route; caller frees with plain `free`, NOT `pcrec_output_free` (`lib/pcrec.h:1146-1161`) — added [REVW.5] 2026-09-19, a promotion of an always-compiled-in function, not new work |

Types: `pcrec_options` (prefix, encoding, `flags` bitmask, engine, six
budgets/caps, `vm_entry_shape`, `tune`, `name`, `header_name` —
`lib/pcrec.h:768-1007`), `pcrec_error` (`{msg[256], pos, input}` —
`lib/pcrec.h:1019-1024`), `pcrec_output` (`{c_src, h_src}`, both `malloc`'d,
`h_src` is NULL when `header_name` was NULL — `lib/pcrec.h:1026-1029`).
`PCREC_ENC_BYTE`/`PCREC_ENC_UTF8` (`lib/pcrec.h:24-28`) is the `--features`
equivalent's *encoding* half; the module-gate equivalent is
`pcrec_options.flags` for the boolean axes plus a SEPARATE mechanism,
`pcrec_enabled_set_spec` (`src/parse/enabled.c`). [CORRECTED 2026-09-21
evening, [REL-1.11]: `pcrec_options.features` now carries the same spec
string, applied per `pcrec_compile` call; NULL means the EMPTY raw
library default per D37's addendum — NOT `std1`, which is the CLI's bare
default and one explicit line for a library caller. The original digest
sentence "a library caller gets the default `std1` set unconditionally"
was wrong on both counts.] Error reporting is a
fixed 256-byte message buffer plus a byte offset (`pos`) into whichever
input `pcrec_err_input` names (`lib/pcrec.h:1009-1024`) — today always
`PCREC_ERR_INPUT_PATTERN`, since no other input exists yet.

**(c) The generated artifact.** Every compile emits, unconditionally, on
both engines (`lib/pcrec.h:1037-1131`, `docs/spec/match_api.md` §3, §6):

- `int <prefix>_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2])` — leftmost search over `s[startpos..n)`; `1` match, `0` no-match, negative = give-up/refusal (§ give-up codes below). `caps` may be NULL.
- `<prefix>_match` / `<prefix>_match_caps` — anchored match-here at `ctx->pos`, no search loop; return length / `-1` / give-up (a DIFFERENT return convention from `_search`: `0` here IS a zero-length match, `-1` is no-match — `docs/spec/match_api.md:539-540`).
- `<prefix>_search_in` / `_match_in` / `_match_caps_in` — the un-suffixed twins plus a final `const <prefix>_buffers *` (caller-supplied `{frames, nframes, trail, ntrail}`); `NULL` descriptor is DEFINED as the un-suffixed call ([DD-14.FB] — `lib/pcrec.h:1083-1100`).
- `size_t <prefix>_next_pos(const unsigned char *s, size_t n, size_t pos)` — the encoding residual: next character boundary strictly after `pos` ([M5-SEAM]/D58 — `lib/pcrec.h:1108-1119`).
- `extern const struct rx_info <prefix>_info` — the reflection structure (§ below).

Give-up/error codes (uniform code space at every entry,
`docs/spec/match_api.md` §4, `PCREC_RX_ABI_H` block): `PCREC_ERR_STEPS
(-2)`, `_FRAMES (-3)`, `_WORK (-4)`, `_RECURSE (-5, reserved, no producer)`,
`PCREC_ERR_FLOOR = -5`; below the floor, NOT give-ups: `PCREC_ERR_INTERNAL
(-6)` (artifact caught its own analysis/emission inconsistency — one
producer today, module `lookaround`'s negative-polarity lookbehind
end-check) and `PCREC_ERR_STARTPOS (-7)` ([K50] — a non-boundary
`startpos` under a multi-byte encoding, refused before any attempt).

The `abi` stamp (`rx_info.abi`, currently **27** —
`docs/dev/decisions.md` D76/D94/[EMIT-VERB]): a layout-version integer,
bumped whenever the emitted scaffolding changes shape, independent of the
new `PCREC_VERSION` product-version string LANDING via D115/[REL-1.4]
(`0.1.0-beta`, `--version`, a stamped header line — not yet in the built
binary). A consumer may `#if`/read at runtime six of `rx_info`'s 15+
fields mirrored as compile-time macros (`<PREFIX>_ENGINE`,
`_ENGINE_WHY`, `_NCAPS`, `_STEP_BUDGET`, `_WORK_BUDGET`, `_BT_FRAMES`)
plus an unconditional "selection facts" family
(`<PREFIX>_DFA_SCAN`/`_DFA_PREFILTER`/`_DFA_TABLE`/`_DFA_MATCH`/
`_DFA_START`/`_VM_PREFILTER`/`_VM_PREFILTER_LANG`/`_VM_CALL_SPLICED`/
`_VM_CALL_LINKED`/`_VM_ALT_ISLANDS`/`_VM_CLS_FOLDS`/`_ALTCLS_MERGES`/
`_ALTCLS_FACTORED`/`RX_TUNE`), present or absent per an IFF rule stated
per-macro (`docs/spec/match_api.md` §6.3). `rx_info` itself (link-time,
not runtime, data — §6.1) carries `abi, flags, encoding, ncaps, ngroups,
nnames, engine, step_budget, work_budget, frame_capacity,
subject_ceiling, resume_frames, trail_frames, resume_frame_size,
trail_frame_size, pattern, pattern_len, groups, engine_why, scan,
prefilter, match_form, name, nentries, search_form` (`docs/spec/
match_api.md:1561-1660`).

---

## 2. Every CLI flag

| flag | does | spec section |
|---|---|---|
| `-o FILE` / `-o -` | output path; `-` = self-contained stdout, no header | cli.md §1 |
| `-p PREFIX` | symbol prefix (default `rx`) | cli.md §1 |
| `-e ENC`, `--encoding=ENC` | subject encoding: `byte` (default) or `utf8` | cli.md §1 |
| `-i` | case-insensitive (ASCII), folded into the automaton | cli.md §1 |
| `--emit-main` | append standalone `main()` (subject from argv[1]) | cli.md §1 |
| `--pattern-esc` | PATTERN operand is `.rxt`'s quoted-escape form | cli.md §1 |
| `--no-captures` | emit capture-free (`NCAPS 1`, DFA) matcher | cli.md §1 |
| `--emit-ir` | print VM program listing (TSV, VM-only), exit; no `-o` | cli.md §2, ir_listing.md |
| `--trace` | emit instrumented matcher (stderr push/pop/write log) | cli.md §1 |
| `--engine=E` | `dfa\|vm\|auto` (default auto); do-or-die refusal | cli.md §1 |
| `--tune=N` | speed-vs-size dial, −2..2 or named alias | cli.md §1, tuning.md §5 |
| `--step-budget=N` | VM backtrack-resumption budget (default 500,000,000) | limits.md §3.1 |
| `--work-budget=N` | VM forward-work budget (default 1,000,000,000) | limits.md §3.1 |
| `--fno-step-budget` | disable BOTH counters, one gate | limits.md §3.1 |
| `--warn-emit-bytes=N` | advisory-only size warning; 0 disables | limits.md "advisory warning" |
| `--max-emit-code-bytes=N`, `--max-emit-bytes=N` | raise the two emitted-size caps (raise-only) | limits.md §8 |
| `--max-nfa-states=N`, `--max-dfa-states-goto=N`, `--max-subset-elems=N` | raise three compile-time construction budgets (raise-only) | limits.md §3.3 |
| `--max-auto-dfa-elems=N` | raise the `--engine=auto` DFA-attempt work budget only | limits.md §3.3 |
| `--backtrack-frames=N` | resume-stack capacity override | limits.md §3.2 |
| `-h`, `--help` | usage text | — |
| `--source FILE` | compile `.rxt` source's `target` lines | cli.md §1 |
| `--target NAME` | build only the named target | cli.md §1 |
| `--lib-path DIR` | search path for `lib "path"` refs (repeatable) | cli.md §1 |
| `--list-syntax` | TSV: every non-base construct | registry.md, cli.md §2 |
| `--list-definitions` | TSV: replacement/definition table | registry.md §9 |
| `--list-verbs` | TSV: `(*VERB)` names | registry.md |
| `--list-families` | TSV: construct families | registry.md |
| `--list-axes` | TSV: optimization-axis registry | cli.md §2 |
| `--list-limits` | TSV: every numeric limit + override route | limits.md §3.4a |
| `--list-schema` | TSV: `.rxt` format's own schema | rxt_format.md |
| `--explain SYNTAX` | what pcrec knows about one construct | cli.md §2 |
| `--flavour NAME` | restrict a query to a syntax flavour (`pcre2` only today) | cli.md §2 |
| `--count-groups [--] PATTERN` | parse only; print capturing-group count | cli.md §2 |
| `--features LIST` | enable feature modules for this invocation | cli.md §1 |
| `--list-source FILE` | TSV: a `.rxt` file as written, unresolved | rxt_format.md, cli.md §2 |
| `--probe-ask WANT [--] CONSTRUCT` | drive one doorway once, report parser cursor | cli.md §2 |

The seven `--list-*` dumps and `--explain`/`--probe-ask`/`--count-groups`
are mutually exclusive query MODES (no `-o`, no pattern for the dumps);
`--list-axes`/`--list-limits`/`--list-schema` take no `--flavour`
(`cli/main.c` usage text, `cli/CLAUDE.md` L11-F4 note).

**LANDING (not yet in the built binary):** `--version` (D115,
`docs/dev/decisions.md:7787`) — prints `PCREC_VERSION` (`"0.1.0-beta"`),
also exported from `lib/pcrec.h` and stamped as a line in every emitted
header.

---

## 3. Knobs a user tunes

**`--tune=N`** (`PCREC_TUNE_MIN_SIZE=-2` .. `PCREC_TUNE_MAX_SPEED=2`,
aliases `min-size|size|balanced|speed|max-speed`, default 0/`balanced` =
byte-for-byte today's defaults). A PINNED policy table
(`docs/spec/tuning.md` §5, D103): a position sets *parameters* existing
per-pattern mechanisms then spend, never a per-pattern decision itself.
Every position is answer-identity-preserving; explicit `-f`/`-fno-` flags
beat the dial where a spelling exists.

**The `-f`/`-fno-` axis family** (`src/core/axes.def`, one row per axis;
names only — see `lib/pcrec.h` for what each denies):
`-fno-possessify`, `-fno-revdet`, `-fno-counter`, `-fno-length-prune`,
`-fno-atomic-discharge`, `-fno-splice-calls`, `-fno-prefilter`/
`-fprefilter` (force pair), `-fno-prefilter-collapse`/
`-fprefilter-collapse` (force pair), `-fno-altcls-merge`,
`-fno-altcls-factor`, `-fno-alt-island`, `-fno-cls-fold`,
`-fno-tiered-entry`, `-fno-size-term`, `-fno-premul-table`,
`-fno-offset-skip`, `-fno-anchored-dfa`, `-fno-scan-edge`,
`-fno-start-pinned`, `-fno-startpos-guard` (the ONE member that changes an
ANSWER, not just a shape — [K50]), `-fno-comments`/`-fcomments` (force
pair, default OFF — [EMIT-VERB]/D112, the only pair whose axis starts off).
None of these except `-fno-startpos-guard`/`-fno-comments`/
`--pattern-esc`/`--work-budget` appear in `--help` (`cli/CLAUDE.md`:
"testing and tuning axes... not sprawling top-level user features").

**`--engine`**: `auto` (default), `dfa`, `vm` — do-or-die, refuses rather
than downgrading; `vm` additionally disables the DFA prefilter.

**`-e` / `--encoding`**: `byte` (default), `utf8`.

**`--features` values**: comma list from `--list-syntax`'s module
column, `std1` (frozen: `{classes, modifiers}`), `all`, `none`. Default
(no flag) resolves through `std1` (D37). 17 module names total; 10 built
today (`classes`, `modifiers`, `assertions`, `named-groups`,
`atomic-groups`, `backrefs`, `lookaround`, `recursion`, `quoting`,
`unicode-props` partial); 7 not built (`branch-reset`, `callouts`,
`comments`, `conditionals`, `extended-classes`, `misc`, `verbs`)
(`docs/spec/cli.md:335-352`).

**PCREC_\* limits a caller can hit, and the documented remedy**
(`docs/spec/limits.md`, `pcrec --list-limits`):

| limit | default | remedy |
|---|---|---|
| `PCREC_MAX_NFA_STATES` | 131,072 | `--max-nfa-states=N` (raise-only) |
| `PCREC_MAX_DFA_STATES_GOTO` | 10,000 | `--max-dfa-states-goto=N` |
| `PCREC_MAX_DFA_STATES_TABLE` | 32,000 | **not raisable** — emitted cell is a C `short`/`unsigned short` |
| `PCREC_MAX_SUBSET_ELEMS` | 48,000,000 | `--max-subset-elems=N` |
| `PCREC_MAX_AUTO_DFA_ELEMS` | 30,000,000 | `--max-auto-dfa-elems=N`; `--engine=dfa` explicit bypasses this and pays the full subset-elems cap |
| `PCREC_MAX_EMIT_CODE_BYTES` / `_EMIT_BYTES` | 500,000 / 1,000,000 | `--max-emit-code-bytes=N` / `--max-emit-bytes=N`, or per-pattern size levers (`--unroll=1`, `--engine=dfa`/`vm`, `-fno-anchored-dfa`, split the pattern) — `limits.md` §8 |
| step budget | 500,000,000 | `--step-budget=N`, or `--fno-step-budget` |
| work budget | 1,000,000,000 | `--work-budget=N` (rides the same gate) |
| frame/trail capacity | sized exactly where statically bounded, else a stamped default | `--backtrack-frames=N`, or the `_in` caller-buffer entries |

All raise-only caps refuse a value BELOW the built-in default rather than
honouring it — a lowerable cap would let a caller manufacture someone
else's refusal.

---

## 4. Input/output encodings and subject conventions

- **Two encodings compile**: `byte` (default, 8-bit clean, no case, no
  meaning above 0x7F) and `utf8` (1–4 byte characters, byte-wise DFA, no
  runtime decode in the hot path). Per-COMPILE-CALL scalar, never global
  (`pcrec_options.encoding`); `-e byte` and the bare default are
  byte-identical artifacts, not merely equivalent.
- **Subjects are LENGTH-COUNTED**, `(s, n)`, never NUL-terminated
  (`<prefix>_search(s, n, startpos, caps)`); `s` may be NULL only when
  `n == 0`, and the matcher never reads `s[n]`.
- **The PATTERN, by contrast, is NUL-terminated with no length parameter**
  (`pcrec_compile(const char *pattern, ...)`) — a documented asymmetry. A
  raw `0x00` byte inside a pattern silently truncates the compile and
  reports SUCCESS for the shorter pattern (measured symmetric with
  libpcre2's own `PCRE2_ZERO_TERMINATED` mode). Filed as K9; the
  documented remedy is a caller-side `strlen` pre-flight, or
  `--pattern-esc`'s `\x00`-refusing decoder at the CLI. Full
  length-taking compile support is NOT part of the contract yet (tracked
  under `DD-3`).
- **`startpos` must be a character boundary** of the artifact's encoding
  under the DEFAULT setting ([K50]); a non-boundary start under `utf8` is
  refused with `PCREC_ERR_STARTPOS` (O(1) test, reads ≤1 byte). Under
  `byte` every position is a boundary, so the guard is inert.
  `-fno-startpos-guard` selects a different, PCRE2-DIVERGENT permissive
  semantics instead (the automaton's own answer at a mid-character
  start) — this is the one axis that changes an answer rather than a shape.
  `<prefix>_next_pos` is the supported way to produce a valid `startpos`.
- **Newline convention for `$`/`(?m)`**: pcrec is fixed at `NEWLINE_LF`
  (PCRE2's own build default) — `$` admits a trailing newline at default
  options, same as plain PCRE2. `DD-11` (the NEWLINE_CONVENTION axis and
  `\R`'s BSR setting — `PCRE2_NEWLINE_*`/`PCRE2_BSR_*`,
  `PCRE2_DOLLAR_ENDONLY`, `PCRE2_FIRSTLINE`, `PCRE2_ALT_CIRCUMFLEX`) is
  **`docs/dev/plan.md`, STATE:not-started** (`docs/pcre2_options.md:87-89`)
  — no CLI/library lever exists to change it today.
- Whole-subject / end-anchored matching uses the `(?:P)\z` idiom, not
  `$` (`$` admits a trailing `\n`; `\z` does not) — `docs/spec/
  match_api.md` §3.6, ruled permanent D77.

---

## 5. Open questions the spec itself flags

- **DD-11 (newline/BSR convention) is STATE:not-started** — no lever
  exists for it; every oracle measurement in the tree runs at
  libpcre2 `options=0` (`docs/pcre2_options.md:87-89`).
- **Streaming interface is specified in APPROACH.md §6 but not emitted**:
  `<prefix>_stream_init/feed/end` "arrives with milestone M3, whose
  design gate ... owns reconciling that contract with the two-pass
  engine before any streaming code is written" (`lib/pcrec.h:1128-1131`).
  `match_api.md:1460`: "No partial-match or streaming window state."
- **`--emit-dot`** (a DOT-format graph dump) was promised alongside
  `--emit-ir` in `APPROACH.md` §6 but was never built; `[DD-8]` is
  STATE:started with `--emit-ir` landed and `--emit-dot` explicitly
  named as one of the still-not-started pieces within it
  (`docs/spec/cli.md:988-994`).
- **`[V-E]` multi-pattern compilation units** (several named,
  cross-referencing patterns sharing one translation unit) —
  `docs/dev/plan.md:581`, STATE:not-started. `--source` compiles several
  patterns per invocation today but each target is still its own
  separate TU (D88).
- **`[LIB]`, the reusable-subpattern library** — `docs/dev/plan.md:580`,
  STATE:not-started, and its own row records that its place on the
  roadmap has not been ruled ("planned but I don't know that I'd put
  them on the spine," Frank, 2026-08-24). `--lib-path` resolves only
  whether a referenced file EXISTS, not its contents.
- **`limits.md:779`'s own text is now STALE**: it still reads "What is
  NOT yet built is the path that COMPILES from a pattern-source file at
  all — `--source` and `--target`" — but `--source`/`--target` shipped
  at [DD-13b.W1.2] (2026-08-31) and are documented as built elsewhere in
  the same tree (`docs/spec/cli.md` §1). The sentence was never updated
  after the feature landed.
- **The callout/composition trap contract has no producer yet**: "Composed
  call sites must trap below the floor" (`docs/spec/match_api.md:1315-1321`)
  binds a call shape (callout code generation, submatcher composition)
  that no emitter builds today — the obligation is recorded for whichever
  future work first emits such a call site.
- **`unicode-props` module ships a proper SUBSET**: two boolean-property
  families (`\p{Alphabetic}`, `Bidi_Class`) are declined by design; six
  names (`\p{C}`, `\p{Cn}`, `\p{L}`, `\p{Xan}`, `\p{Xwd}`,
  `\p{Unknown}`) exceed the emitted-size cap under `utf8` at default
  settings and refuse with the generic "pattern too large" diagnostic
  rather than their own message (K53).
- **Diagnostic wording is explicitly NOT promised** (D26 tier 3):
  `requires module 'X'` discharges the obligation in full; PCRE2's own
  error text and offset are not reproduced. pcrec's OWN offset is exact
  and stable, but is not PCRE2's number for the same input.

### Observed, not ruled

- **The CLI has three UNRELATED small-integer exit/return vocabularies**
  that share values with no relationship: `pcrec`'s own exit codes
  (0/1/3), an `--emit-main` binary's exit codes (0/1/2/3, match/
  no-match/usage/give-up on the EMITTED program), and a generated
  function's give-up CODE space (`PCREC_ERR_STEPS` etc., all negative).
  Stated explicitly in `docs/spec/cli.md:895-897` as a caller trap.
- **`<prefix>_search`'s `0` return and `<prefix>_match`'s `0` return mean
  opposite things** — `_search`'s `0` is "no match"; `_match`'s `0` IS a
  successful zero-length match, and `_match`'s "no match" is `-1`
  (`docs/spec/match_api.md:539-540`). Two entry points on one artifact,
  two conventions for the same integer.
- **The pattern is NUL-terminated; the subject is length-counted** — an
  asymmetry between the two string inputs `pcrec_compile` and
  `<prefix>_search` each take, and the NUL-terminated half is where K9
  lives (§4 above).
- **`--features` has no `pcrec_options` field** — the library surface
  (`lib/pcrec.h`) has no lever for the module-enable set at all; only the
  CLI's `--features` flag and its own default resolution
  (`pcrec_default_features`, `src/parse/enabled.c`) reach
  `pcrec_enabled_set_spec`. A library caller cannot ask for `all` or a
  named module set through `pcrec_options`.
- **A flag whose default surprises**: `-fno-comments`/`-fcomments` is the
  only axis pair whose deny/force sense is inverted from every other pair
  in the family — comments are OFF by default and the FORCE flag turns
  them on, where every other force pair (`-fprefilter`,
  `-fprefilter-collapse`) restores an axis the compiler would otherwise
  decide for itself (`src/core/axes.def:150-158`).
- **`PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM` are `#define`s, not enum
  members**, unlike `PCREC_ENGINE_AUTO` beside them in the same block —
  a deliberate asymmetry forced by artifacts also emitting identical
  `#define`s of the same names, which would otherwise textually rewrite
  an `enum` declaration into a syntax error (`lib/pcrec.h:724-742`).
- **`rx_info`'s compile-time macro mirror is PARTIAL**: on a VM artifact
  6 of 15+ struct fields have a macro; `ngroups` — the field
  `docs/spec/match_api.md` §6.2 works hardest to distinguish from
  `ncaps` — has NO macro and is reachable only by reading `rx_info` at
  run time (`docs/spec/match_api.md:2356-2368`).
