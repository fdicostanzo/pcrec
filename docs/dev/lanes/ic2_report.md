# ic2 — [INLINE-C] stage 2: embedded C (module `code-c`), local-only gate

Lane ic2 (opus), 2026-10-27, worktree `worktrees/ic2` (branch `lane/ic2`,
from main 6d0974b74, with main 614d45eb3 merged in under ruling R2). Design:
`docs/design/inline_c.md` rev 1 §9.1 stage 2, cut down by ruling R1.

## Summary

Stage 2 is built for the tagged spelling ``(?C`c: CODE`)``, with every PCRE2
string delimiter and PCRE2's end rule. A segment becomes a file-local
`rx_matchfn` that the site calls through the ONE call form,
`<gen>_ref.fn(&ctx)`. The segment carries `#line` back to the user's source
and gets the macro set and the seven span helpers. The module opens only
through `--allow-code=c` / `pcrec_options.allow_code`, never through a
`features` text (the GRANT column, `RF_INVOKER_ONLY`). The `(?{ ... })`
spelling is deferred to [SCANNER-DOGFOOD] (R1); `(?{` behaves as on main.

abi 89 -> 90. Every artifact WITHOUT a callout is byte-identical apart from
the abi digits: emit_sweep over the corpus plus the 336 bench patterns found
219 moved or asymmetric rows, every one a `(?C` pattern, a tests/code/ file
or one of the three dumps (classifier `docs/dev/lanes/ic2_movers.py`,
`unexpected=0`).

Locally green: `make strict`, test-code (60 checks), test-callouts,
test-codegen, test-cli, test-registry, test-reject, test-rxtsource
(re-measured after the merge), test-claudemd-size, test-spec-history. The
full make test, mech and axes runs are owed as queue jobs 620/621/622.

## What was built

- **Language rows.** `src/parse/codelang.def` holds one row per language
  (`c` -> module `code-c`, `FEAT_CODE_C`). `src/parse/registry.c` generates
  one `RK_GROUP 'C'` row per language from it: `RF_INVOKER_ONLY`, VM only,
  port `pcrec_codeport`.
- **Parsing (`src/parse/mod_code.c`).** It reads the tag grammar
  (`lang[,attrs]:`; the attributes are module `callouts`' reader) and
  decodes the doubled delimiter. It refuses:
  - a bidi or invisible format character (§2.4), naming the code point and
    its byte offset;
  - a C0 control byte or DEL (see Deviations);
  - REACHED code, i.e. a segment inside a definition read from another file
    (§5.4 row 3), with or without the grant.
- **The gate.** `--allow-code=LANGS` (CLI) and `pcrec_options.allow_code`
  (library) are the only doors. `code-c` is in no feature set (`all`
  excluded). These are refused: `features code-c` (anywhere), a config's
  `pcrec` line carrying `--allow-code`, and `code-header` without the grant.
  The describe modes (`--emit-ir`, `--emit-facts`, `--count-groups`, the
  registry's `built` probe) open the describe mask
  (`pcrec_code_describe_mask`) and write no C.
- **Emission (`src/gen/emit_code.c`, plus hooks in emit_dfa.c/emit_vm.c).**
  - Each segment's prototype and file-local `rx_callout_ref` come before the
    matcher.
  - At the end of the `.c`: the `#undef` block of the artifact's own live
    macros, then the `code-header` `#include`s (each preceded by a `#line`
    naming its `.rxt` line), then, per segment, its macro set, the `#line`,
    the function and the set's `#undef`.
  - The `<PREFIX>_CODE_LANGS` stamp is in the `.h`.
  - The span helpers sit under the `PCREC_RX_SPAN_H` guard in every callout
    artifact.
- **Code headers.** The `.rxt` head line `code-header LANG HEADER` and the
  CLI option `--code-header LANG:HEADER` (refused with a file operand). The
  header is emitted as written and never opened.
- **Harness.** `harness.manifest` gains `allow-code LANGS`, granted to the
  directory's ENTRY files only (§5.2). A file's `code-header` rows reach its
  compile, and the `.rxt` directory is put on `-I`. verify_rxt.py knows
  `code-header` as a head word, and counts a head-bearing own-oracle file's
  expectation lines as own-oracle skips.
- **Registry and dumps.**
  - `--list-syntax` flags column: `invoker-only`.
  - The code-c row reads `built`.
  - The compliance index renders a syntax holding a backtick as a
    double-backtick span; `syntax_index_check.py` reads N-backtick spans.

## Spec hunks

- **`docs/spec/match_api.md`:**
  - §8.2¶7c `allow_code`;
  - §11.2¶1a/¶2, the one call form (direct when the compiler can see the
    binding, indirect otherwise);
  - §11.9 embedded code (¶1-¶8: spelling, end rule, opacity and the two
    refusals, the function and its layout, the macro set, reserved names,
    `code-header`, the grant);
  - §11.10 the span helpers;
  - the `<PREFIX>_CODE_LANGS` stamp row;
  - abi 90.
- **`docs/spec/cli.md`:** §1.22 `--allow-code` / `--code-header`; §1.10¶2
  and §1.17¶3 touched.
- **`docs/spec/rxt_format.md`:** §1.1¶1 (twelve declarations, with
  `code-header`); §2¶3; §6¶3/¶3a (the manifest's `allow-code`, and
  `code-header` in the harness).
- **`docs/spec/pattern_language.md`:** §7.12 Module `code-c`; §9¶10; the §10
  index row.
- **`docs/spec/registry.md`:** module and flags columns (`invoker-only`).
- **`docs/pcre2_compliance.md`:** the generated index (144 rows), an
  `OK-GATED` survey bullet and a Callouts table row, and a keyed annotation
  ``(?C`c: return RX_PASS;`)``.
- **`docs/guide/embedded-code.md` (new chapter):** the grant, the anchored
  validator and the unanchored trap, `once`, the four escaping layers,
  `code-header`. Every command in it was run against this build.
- **Design (`docs/design/inline_c.md`):** §1.4 row 1 and the ONE CALL FORM
  paragraph, the §3.1 binding sentence, and the §9.1 R1 note.

## Tests and sabotage

**`tests/code/` (`make test-code`, mech arm `code`; 11 arms, 60 checks):**
- **Corpus:** `ipv4.rxt` (UC-1a/1b, DT-1.1-1.6), `geoip.rxt` (UC-3,
  DT-3.1/3.2, `features all` with the grant), `macros.rxt` (macro set,
  guarded accessors, single evaluation, `RX_G_<name>` under (?J), span
  helpers in a segment, delimiters and doubling, `once`, `consume`).
- **T2 and the fragment rule:** `t2/t2.rxt` (no manifest, so its `perr`
  case is refused) and `frag/` (the entry is granted; the included fragment
  `frag_code.rxt` is refused).
- **Oracle:** `verify_code.py`: libpcre2 10.46 runs the SAME segment text,
  with §11.9's macros rewritten as functions. 34 cells agree, 0 disagree, 2
  `consume` cells are counted skips; floor 30.
- **Refusals:** the grant; `features` in a block, a config, a `pcrec` line,
  `--features` and the library; an unknown language or attribute; bidi and
  C0 bytes; reached code; a malformed `code-header`.
- **Entry-point table (§5.9):** enumerated from cli/main.c's
  CLI_MODE_TABLE, plus `lib_check.c`.
- **Diagnostics land on the user's line (DT-3.3/3.4):** `err.rxt:3:25`, a
  `pattern-esc` segment at its opener's line, `<command line>:1:17`, a
  missing header at its `code-header` line.
- **Header placement:** `poison.h` poisons `memchr memcmp memcpy` and still
  compiles.
- **Live-macro check (§3.2).**
- **Driver checks:** DT-4.1 inline; a check returning 1 and a segment
  falling off its end both trap (exit 132).
- **Span helpers:** `span_check.c`, 442,379 checks, 0 failed.
- **Call form, from the asm:** zero indirect calls in the unity build, the
  embedded segment and the artifact-as-callout; the separately compiled
  control shows one.
- **Card:** `card_inline.sh --smoke`.

**Sabotage (all DETECTED and REACHED in local mech runs):**

| row | design label | what it breaks |
|---|---|---|
| S1680 | S-IC8 | an unknown attribute is accepted |
| S1681 | S-IC9 | the opt-in check is removed |
| S1682 | S-IC10 | `#line` is dropped |
| S1683 | S-IC28 | `all` includes `code-c` |
| S1684 | S-IC29 | the harness grants fragments |
| S1685 | S-IC30 | a user header is emitted before the matcher |

S693 (the abi row) was re-aimed 89 -> 90. All seven go in queue job 621.

**Measurement card:** the inline-mode card (goal 3b; rows site_hit,
site_miss, tail; inline against the callout-free `--engine=vm` twin, fires
counted) is UNMEASURED. `--timed` needs a cleared timing window. The smoke
figures (site_hit inline 4.18 against twin 1.30 ns/B) come from a tiny,
single-repeat run and are not a measurement.

**Suite re-pins, each measured:**
- **registry:**
  - row count 143 -> 144; families 104 -> 105; atom ports 96 -> 97;
  - engine capability 76/63/63 -> 77/64/64, with a code-c witness compiled
    through `allow_code`;
  - built 115 -> 116; coverage 232 -> 233; PC-3 216 -> 217;
  - the GRANT-column refusal text has its own expectation; compliance dump
    143 -> 144.
- **cli:** case11 51 -> 52.
- **reject:** iteration 132 -> 133.
- **rxtsource:**
  - The census is summed with cired2's cscan: 306/6241/74709, run.sh
    282/6241/74709.
  - It now handles the corpus's first `include` fragment (CENSUS_FRAGMENTS,
    checked against a raw count of head `include` lines; C3's entry set;
    C3_FRAGMENT_LINES in the reconciliation; the W23-S7 control).
  - It handles the first head-bearing files that carry pattern blocks: leg
    C's projection and owed counts drop them, counted over the raw bytes.
  - `include` graduated from the keyword census (28 -> 27).
  - C3 SKIP 52589, own-oracle 30418.
- **codegen:** `LC_ALL=C` on two sorts (K35), `$TIMEOUT_BIN` on the card's
  compile (K37), `run_code_tests.sh` in `tests/lib/san_scripts.txt` (TT-9).
- **Other:** a CI shard row `test-code 2 60.0 ESTIMATED`.

## abi and re-pins

- **abi 89 -> 90:** `PCREC_ARTIFACT_ABI`, stamp_kinds, S693, match_api,
  run_codegen_tests.sh's transition string, abi_changelog.
- **Recursion identity:** self-pinned to the lane's last src commit
  `94568296a`, with history text; the manager re-pins to the merge.
- **What moves at 90:**
  - a callout-free artifact: the abi digits only;
  - a callout artifact: also the `PCREC_RX_SPAN_H` block;
  - a code artifact: the scaffolding of §11.9.
- **Proof:** emit_sweep (full mover lists, REF = 6d0974b74 built at abi 90)
  plus `ic2_movers.py`: `movers: DONE rows=219 unexpected=0`.
  - c-default and c-vm: 34 movers each, all callout artifacts.
  - emit-ir and stderr streams: 21 each, all code-c patterns (refusal text,
    describe modes).
  - composition: 1, `tests/code/ipv4.rxt`.
  - dumps: 3, `--list-syntax`, `--list-families`, `--list-schema`.
  - Every other row is byte-identical.

## Deviations from the design

1. **`(?{ ... })` deferred (R1):** to [SCANNER-DOGFOOD]. No C scanner, no
   scanner table tests, no S-IC7. `(?{` behaves as on main.
2. **C0 control bytes and DEL are refused in a segment** (other than tab,
   newline, VT, FF and CR). This was added beyond §2.4: `\x01` is the
   emitter's placeholder lead (K79), and a segment must never carry it into
   the artifact.
3. **A diagnostic from the macro set can name the `.rxt`.** The per-segment
   macro `#define`s follow the segment's `#line`, so a diagnostic inside a
   macro expansion names the `.rxt` position rather than the generated file.
4. **`--code-header` is refused with a file operand.** The file's head names
   its own headers (cli.md §1.22¶2).
5. **The library has no code-header member.** `pcrec_options` gained only
   `allow_code`; a library caller's segment includes nothing. Filed for
   [IFACE-PUSH].
6. **`--code-header` includes get no `#line`.** They have no source line;
   `.rxt` head `code-header` lines do get one.
7. **The inline-mode card is UNMEASURED** (no timing window).
8. **`PCREC_FEATURE_MODULES` does not list `code-c`.** This is by design:
   `code-c` is in no feature set.
9. **plan.md STATE tag not touched** (manager's).

## STATE AT HANDOFF

Owed queue jobs, queued as `620-ic2-test`, `621-ic2-mech`, `622-ic2-axes` (queue keys `ic2-test`, `ic2-mech`, `ic2-axes`; job files committed in this lane):

| key | job file | runs | logs | completion lines |
|---|---|---|---|---|
| `620-ic2-test` | `docs/dev/lanes/ic2_test_job` | build, strict, movers census, full make test | `job.log.strict`, `job.log.movers` (+ `.sweep`), `job.log.make` | `strict: DONE rc=0`; `movers: DONE rows=219 unexpected=0`; `sections ran: 81/81` |
| `621-ic2-mech` | `docs/dev/lanes/ic2_mech_job` | S1680-S1685 and S693 | `job.log` | `== mech run COMPLETE: 7 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) ==` |
| `622-ic2-axes` | `docs/dev/lanes/ic2_axes_job` | AXES_FULL=1 HARNESS_BATCH=64 `run_axes.sh`, plus the form census | `job.log.axes`, `job.log.census` | `axes: DONE rc=0`; `checks failed: 0`; `census: DONE rc=0` |

Job 622 has cap 15600; 620 and 621 keep their templates' caps.
