# EMIT lens — emitted-vs-replaced (critic round subst, 2026-10-24)

Subject 1222b31be vs BASE 6ec3a2108. Scratch: /tmp/claude-1001/crit-subst/emit/ (bench/bench.c is the measurement harness).

Measurement setup (used by EMIT-1..3): rx `([a-z]+)@([a-z]+)` (pcrec default flags, prefix em/eu), 1 MiB subject
of `lorem ipsum foo@bar dolor sit amet, xy@zw. ` repeated = 48,771 matches. Every mode's output was checked
byte-identical (FNV hash) to pcre2_substitute's. `taskset -c 7 perf stat -e instructions:u`, per-run =
(I(11 reps) - I(1 rep))/10, 3 repeats each, spread < 20 instructions. Cycles cross-check: 41 reps x3.

| mode | instr/run | instr/match | cycles(41 reps) |
|---|---|---|---|
| find-all only (em_next_n, K=64) | 34.33M | 704 | - |
| `$2 at $1`: rx_subst_replace_all (spec §6¶9 sub_all) | 51.24M | 1051 | ~448M |
| `$2 at $1`: hand-written next_n + memcpy | 39.31M | 806 | ~373M |
| `$2 at $1`: pcre2_substitute GLOBAL, JIT | 66.17M | 1357 | ~560-618M |
| `$2 at $1`: pcre2_substitute GLOBAL, interpreter | 430.16M | 8820 | - |
| `\U$2\E at $1` byte: replace_all | 69.92M | 1434 | ~601M |
| `\U$2\E at $1` byte: hand-written | 39.53M | 811 | - |
| `\U$2\E at $1` byte: pcre2 JIT | 82.41M | 1690 | ~687M |
| `\U$2\E at $1` utf8 (-e utf8 rx + tmpl): replace_all | 109.99M | 2255 | ~883M |
| `\U$2\E at $1` utf8: pcre2 JIT (PCRE2_UTF) | 94.94M | 1947 | ~800M |

Headline: plain templates beat pcre2_substitute+JIT by 23% instructions (~25% cycles); byte case-forcing by
15%; UTF-8 case-forcing LOSES to pcre2+JIT by 16% instructions / ~10% cycles on pure-ASCII input.

### EMIT-1  UTF-8 case region: two full decode/bsearch/encode passes, ASCII through the bsearch, uncased tail inside the region; loses to pcre2+JIT
- status: CONFIRMED (repro: bench modes 9 vs 12 and 6; `pcrec --features subst-extended -e utf8 -p tw --subst '\U$2\E at $1'`; observed 109.99M instr vs pcre2 JIT 94.94M, vs the same template under byte 69.92M; expected: at or below pcre2+JIT, as every other row is)
- severity: speed
- effort: S-M ; blast radius: every `-e utf8` template with \U \L \u \l (the only subst row slower than pcre2+JIT)
- where: emitted `<p>_render` (two `<p>_match` loops: "sizing: validate and count" then "writing"), `<p>_put` -> `rx_subst_case_utf8` (support unit), `rx_subst_case_cp_`; src/gen/emit_subst.c; replace_design.md §R4.11 "Case forcing cannot be resolved at compile time" / "Nothing measures ... the case region's two passes ... UNMEASURED"
- body: Three separable costs, all on ASCII input here: (a) the sizing pass runs the whole UTF-8 decode + case map + encode with dst NULL, then the writing pass repeats it, so every region byte is converted twice (byte encoding avoids this only because `<p>_case_bytes` skips its loop when dst is NULL); (b) `rx_subst_case_utf8` has no ASCII fast path: every forced code point, including 'a'..'z', is a ~11-step binary search over a 1,466-entry table, and every UNforced character (mode 0) is still decoded and re-encoded instead of copied; (c) the region runs from the first case escape to the template's END, so ` at $1` after `\E` is pushed through the converter too (§R4.11 names the tighter region a later refinement). The cheapest fix needs no new contract: §4¶22 already gives a static bound (1.5x every byte entering the region), so the element can skip the sizing pass whenever `scap - sn >= ceil(1.5 * sum(entering bytes))` (an O(pieces) sum) and fall back to the exact pass only near the limit; plus a `cp < 0x80` branch in rx_subst_case_utf8 (map a-z/A-Z arithmetically, copy otherwise). Not against a ruling: §R4.11 labelled the two passes UNMEASURED with trigger "a user's hot \U template"; this is the measurement, and the result (the one subst row that loses to pcre2) arguably fires the trigger. Measured cost of (a)+(b)+(c) together: ~822 instr/match over the byte-encoding run of the same template on the same ASCII bytes.

### EMIT-2  replace-all's per-piece append re-checks overflow and fit through pointers: 3.4x the hand-written per-match overhead
- status: CONFIRMED (repro: bench modes 2 vs 3 vs 1; perf record -e instructions:u mode 2: rx_subst_append_ 15.7%, t1_render 9.5%, t1_subst_slot 2.3%; `gcc -O2 -S` of the support unit: rx_subst_append_'s loop stores *w and reloads *fits every piece and spills 3 callee-saved registers around memcpy)
- severity: speed
- effort: S ; blast radius: every rx_subst_replace_all caller (the spec's §6¶9 headline recipe)
- where: support unit `rx_subst_append_` / `rx_subst_replace_all` (emitted by pcrec_emit_support, src/gen/emit_subst.c)
- body: Substitution overhead over the bare find-all is 347 instr/match through replace_all versus 102 for a hand-written loop doing the same memcpys (51.24M vs 39.31M total: +30% instructions, ~+20% cycles end-to-end). The largest single term is rx_subst_append_ at ~164 instr/match (~33 per piece): per piece a SIZE_MAX-overflow test, a `*fits && out && len <= cap - *w` test and a store of *w through the pointer. `rx_subst_flatten` in the same unit already has the better shape (sum the batch's lengths with one overflow check, one fit decision, then a plain memcpy loop with a local w); append_ can do that per batch and keep the counting-only path for the no-fit case. The render side adds ~100 (piece stores, then a second walk over the piece array) - inherent to the pieces design and accepted by it. Still 23% fewer instructions than pcre2_substitute+JIT, so this is headroom, not a regression.

### EMIT-3  loop-invariant work re-done per match in the emitted element
- status: CONFIRMED (repro: `gcc -O2 -S` of t1.c / tu.c: `call t1_subst_slot` twice per match in the render loop; tu.s keeps 9 references to tu_case_next/tu_case_mode; the constant "-"/" at " in a case region goes through the case converter per match)
- severity: speed
- effort: S-M ; blast radius: every subst artifact (small per match: ~24 instr/match for the slot calls in t1; more in case templates)
- where: emitted `<p>_subst_slot`, `<p>_region`, `<p>_put` (src/gen/emit_subst.c)
- body: (a) `<p>_subst_slot` is out of line (2 call sites, gcc does not inline it) and re-tests `!map`, `k < 0 || k >= nc` for every reference of every match although map and nc are invariant for the call; with map == NULL the slot is the constant k, so a map-less loop (one `if (!map)` hoisted above the match loop) reduces each reference to the participation test. (b) The case state is passed by pointer into the non-inlined `<p>_put`, so the template-static state transitions (`st = case_next[0][st]` from st = 0) are NOT constant-folded: the tables are walked at run time on every match. (c) Constant bytes inside a region are case-mapped at run time every match; their forced form is knowable at compile time except after a possibly-empty group or a conditional (the reason §R4.11 gives), so the emitter could pre-case the constant whenever the state reaching it is static. None of these is an answer issue; they are emitted-code quality notes for when EMIT-1's trigger is acted on.

### EMIT-4  support unit (default IMPLEMENTATION mode) links 23 KB of case tables into every program, case forcing used or not
- status: CONFIRMED (repro: bench/mini.c = em + t1 (no case forcing) + `#define PCREC_SUPPORT_IMPLEMENTATION`: `size` text 41,532 B, rx_subst_lower_ 0x2c40 + rx_subst_upper_ 0x2dd0 = 23,056 B present; the same program with PCREC_SUPPORT_STATIC defined first: text 14,537 B, tables gone; support unit alone: 27,712 B text, 83% tables)
- severity: size
- effort: M ; blast radius: every program using the support unit the way examples/subst and spec §10¶3 show (IMPLEMENTATION in one TU)
- where: support unit `rx_subst_upper_` / `rx_subst_lower_` (`static const unsigned [][2]`), `rx_subst_case_utf8` extern
- body: The tables are 2,890 pairs of 32-bit code points (8 B/entry), sorted, overwhelmingly runs with constant delta (+-1 alternating, +-32, +-48, +-80): a run/delta encoding is roughly an order of magnitude smaller and also allows the ASCII fast path of EMIT-1. Separately, because `rx_subst_case_utf8` is an external definition in the IMPLEMENTATION TU, nothing drops it without -ffunction-sections/--gc-sections; a program with no case template pays 23 KB (2.8x its subst-related text here). SIBLING: this is the [DATA-PLAN] D179 family landed on main today ("compiler tables are a format question (delta-varint 3.6x)"; Unicode data in emitted code is "a form issue first") - the case table is a new member of that family (generated from vendored UCD-derived data, §R4.12) and should be listed there rather than shipping a third table format.

### EMIT-5  the case table reproduces libpcre2 10.46's othercase quirks, which the D26 addendum landed today may now rule against
- status: CONFIRMED (repro: /tmp/claude-1001/crit-subst/emit/case/p2.c against libpcre2-8 10.46 with PCRE2_SUBSTITUTE_EXTENDED, and the support table rows: \U on U+03B9 iota -> U+0345 (a combining mark, not U+0399), \U on U+03BC mu -> U+00B5 (not U+039C), \U on U+01C5 Dz-titlecase -> U+01C6 (a LOWERCASE letter under \U; Unicode simple upper is U+01C4), \U on U+03D0 -> U+03B2 (lowercase beta); pcrec's table rows {0x3B9,0x345} {0x3BC,0xB5} {0x1C5,0x1C6} {0x3D0,0x3B2} match libpcre2 exactly)
- severity: design (answer-tier, outside this lens; flagged because it is cheap to see from the emitted table)
- effort: S to rule, M to change ; blast radius: -e utf8 case-forcing templates on Greek/Latin-Extended input
- where: docs/spec/subst_api.md §2¶14 ("a character maps to the single code point libpcre2 10.46 maps it to"); support unit rx_subst_upper_/lower_
- body: pcrec is bug-compatible with 10.46 by explicit contract, which was the ruled position at BASE. The D26 addendum e04e9f61a (main, 2026-10-24, after BASE) says "compatible with PCRE2 unless PCRE2 has a bug; follow the standard, record the upstream issue". \U producing a lowercase letter (U+01C5 -> U+01C6, U+03D0 -> U+03B2) or a combining mark (U+03B9 -> U+0345) looks like PCRE2 reusing its caseless "other case" chain instead of Unicode Simple_Uppercase_Mapping. The manager should rule whether §2¶14 stands under the addendum; if it falls, the table becomes UnicodeData simple upper/lower and §9 gains a difference row.

### EMIT-6  dead `(void)` scaffolding and an unused local in every emitted case region
- status: CONFIRMED (repro: `pcrec --features subst-extended -p cu -e utf8 --subst '\U$1\E-\u$2'`: `<p>_region` declares `int ... sl = 0;` never used and emits `(void)map; (void)c; (void)nc; (void)flags; (void)s; (void)g; (void)rc; (void)sl;` after which every one of them is used)
- severity: maintenance
- effort: S ; blast radius: emitted text of every case-forcing artifact (an abi event to change, D76/D94 - bundle with EMIT-1/3 if those are taken)
- where: src/gen/emit_subst.c (the region emitter)
- body: A blanket unused-silencer, harmless to codegen, but it hides genuinely dead locals (`sl`) from -Wunused in the emitted code (not verified against a house rule; noise only). Emit the casts only for parameters the region body does not read.

## Part (2): pre-existing rx artifacts - no byte moved
- 36 patterns (literal, classes, alternation, captures, named groups, recursion, backrefs, lookaround, \b, anchors, \A\z, utf8 literals/classes/\p{L}, caseless byte+utf8, --ucp, --no-captures, lazy, counted, \x{..}; DFA/VM/auto engines) x {default features, --features all}: emitted .c AND .h byte-identical BASE vs SUBJECT for every one that compiles (26 default, 34 all); every refusal identical in text and exit code.
- 6 flag variants on `a(b|c)+d` (--emit-main, -e utf8 -i, -p foo, --trace, --engine=vm, -o -): identical.
- 58 diagnostic probes through the refactored code (ill-formed UTF-8 patterns via --pattern-esc under utf8/byte: bad lead, truncated, overlong 2/3-byte, surrogate, >U+10FFFF, 5-byte; \x, \x{..}, \cX, \c?, \o{}, octal, empty/oversized hex): stdout+stderr identical.
- PCREC_ARTIFACT_ABI stays 84 at SUBJECT. No rx byte changed, so no bump is owed; the shared block reaches the subst header through `pcrec_emit_rx_abi_block`, the same emitter, which is the right shape (one source for the shared bytes). The subst artifact is a NEW artifact kind stamped abi 84, which needs no re-pin of existing artifacts.
- The one rx-side caller-observable change is the new prefix reservation row 4 (`-p rx_subst`, `rx_group`, `pcrec_subst`, `pcrec_support`, alone or followed by `_`, are now refused for PATTERN compiles too; `rx_groups`, `rx_substr`, `pcrec_supports` still accepted). Its spec hunk is present (docs/spec/cli.md line 188 table). A default-prefix rx (`rx`) + default-prefix subst (`rx`) + a second subst + the support unit compile and link together under -Wall -Wextra with no collision.

## SIBLING OF A FAMILY
- The UTF-8 case table (EMIT-4/5) is a sibling of the Unicode data tables family ([DATA-PLAN], D179; third_party/*/generate.py -> generated tables): a fourth consumer with its own layout (pairs of `unsigned`) rather than the family's format.
- `ns_subst_block` + `ns_subst_families[]` is a new member of the prefix-reservation table `ns_reserved[]` (compile.c): correctly expressed as a row of the existing first-match table, not a parallel check; `pcrec_prefix_acceptable` reuses valid_prefix + ns_reserved_by (good).
- `rx_subst_utf8_char_` (run-time, emitted) is a third UTF-8 decoder beside the new compile-time `pcrec_utf8_decode` (enc.c) and the emitted matchers' own UTF-8 steppers; different tier (emitted text vs compiler), so not a duplication finding, but it is one more emitted decoder that a future "one emitted UTF-8 step" consolidation would own.
- `pcrec_esc_digits_value` / `pcrec_esc_ctrl_value` / `pcrec_utf8_decode`: extractions that make the template parser and the pattern parser share one decode each - the correct general form (verified answer-neutral above).

## GENERAL FORM + UNLOCKS
- General form: a match-to-output TRANSDUCER compiled from a template - per match, a static sequence of (constant | span-of-group | transform(region)) items over the find-all stream. Today's element is its piece-list instance; the case region is its first transform.
- Unlocks (each with trigger): (1) a fused rx+subst artifact (match loop writing pieces directly, no caps array round trip) - trigger: a measured workload where EMIT-2's residual (~100 instr/match render+piece walk) is a top cost; ruled out for R4 by ruling 4, so only on that measurement. (2) static case-state evaluation (EMIT-3c) generalising to any per-region transform (escaping for HTML/JSON/shell, which is exactly a case-like byte map) - trigger: a user asking for an escaping template. (3) the 1.5x bound fast path (EMIT-1) generalises to "skip sizing whenever a static expansion ratio is known" for any future transform - trigger: EMIT-1 acted on. (4) writev/iovec output straight from pieces (already listed in replace_design) - trigger unchanged.

## PROBED-AND-HELD
- 36 patterns x 2 feature sets = 72 compiles per side, 6 flag variants, 58 diagnostic probes: 0 byte differences (part 2).
- Output identity of all 12 bench modes (pcrec replace_all / hand / pcre2 interp+JIT, plain, byte case, utf8 case): identical hashes over 48,771 matches.
- Default-prefix coexistence (rx + 2 substs + support, -Wall -Wextra): clean.
- PCREC_SUPPORT_STATIC (defined first) drops the case tables and case_utf8 when unused (14.5 KB vs 41.5 KB).
- replace_all batch sizing: k = min(256/nc, cap/P, 64) = 64 for nc=3 (no per-call shrink on ordinary patterns).
- Subst artifact sizes (`size`, -O2): `$2 at $1` 1,271 B text; byte case 2,225 B; utf8 case 2,105 B (+ the support unit 27,712 B, 23,056 B of it tables); rx em.o 9,480 B for comparison.

## NOT COVERED
- Map-ful (by-name) render cost and the ${name:-..}/${name:+..} conditional forms per match; ${!var} references.
- Patterns with many groups (nc > 85 makes the replace_all batch < 3 matches per next_n call; nc > 256 is refused MISMATCH unless RX_SUBST_BATCH_PAIRS is overridden) - not measured.
- Non-ASCII subjects for the UTF-8 case path (only ASCII measured; ß-growth paths not timed).
- .rxt-file and `-o DIR` pooled compiles for the byte-identity check (only --pattern).
- Cycles were a cross-check only (3 runs, not interleaved); the instruction counts are the claim.

## DONE
