# contract findings — altcode
STATE: done
## Findings

### CON-1: match_api.md §1¶7's guard block is half-bumped (two of three abi readers still say 95)
- status: CONFIRMED. `docs/spec/match_api.md` lines 211-215 at SUBJECT read
  `#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != 95` / `#error "... (abi 96) ..."` /
  `#define PCREC_RX_ABI_H 95`; the emitted header (`build/pcrec -p rx --features all -o y.c --pattern '(a)'`, y.h)
  reads `!= 96` and `#define PCREC_RX_ABI_H 96`. The diff BASE..SUBJECT changed only the `#error` line (212).
- severity: doc
- effort: S (two digits); blast radius: the spec's own quoted block contradicts itself and the artifact (D80 contract text)
- where: docs/spec/match_api.md:211, :215
- argument: the D76/D94 ritual (CLAUDE.md situation row: "every reader of the number, found by grep") — a grep for `95` in
  the abi sites of match_api.md finds both; nothing in the suite reads this block (it passed).
### CON-2: §8.5¶1b's "apart from ¶5's stamp, the -fno-alt-island artifact" has a knock-on byte when a later rung also fires
- status: CONFIRMED (minor). W = 1,000 random 8-letter words (seed 7), `build/pcrec -p rx -o k4.c --pattern "(W)"` (auto ->
  VM): notes for rung 2b then rung 5, rc 0, `RX_VM_ALT_ISLANDS 0`, `RX_ENGINE_SEL "size-cap-retry"`. Versus
  `-fno-alt-island -o k5.c` (rung 5 only): the only other diff is `RX_VM_PREFILTER_WHY "size cap retry, hybrid 1121635 >
  1000000"` vs `... 1121629 ...` -- 6 bytes = len("size-cap-retry") - len("selected"), i.e. the ¶5 stamp counted in the
  figure rung 5 quotes. With `--engine=vm` (rung 2b alone) the two artifacts are byte-identical (basename aside).
- severity: doc
- effort: S (say "and any figure a later rung quotes" in ¶1b, or accept); blast radius: none on answers
- where: docs/spec/limits.md §8.5¶1b
- argument: the claim is an exact-identity promise; it holds only when 2b is the last rung.

## PROBED-AND-HELD

All answer checks: span + every capture (pcrec spans[0] carries the \K start) vs libpcre2-8 10.x via ctypes
(utf8 = UTF|UCP|MATCH_INVALID_UTF), each pattern on 9-400 subjects (all strings to length 3 over the pattern's alphabet
plus 80 random to length 8). About 1,400 pcrec compiles total. Zero answer differences anywhere.
- 44 hand witnesses (w1) x {auto, vm, dfa where admitted}: adjacency rows 1/2/3 (`(?:ab|(x)ad|ad)`, `a\Kd`, `(?=(a))ad`,
  proper prefix `a`, `a(?=d)`, `(?:a|x)d` (row 2 pass), `(?:a|xy)d`, atomic both orders, `(?!(x))`, `(?<=(a))d`, `\G`, `$`,
  `\b`, repeats `{2}`/`{1,2}`/`[ab]{2}`, `.`), backrefs, `(?1)`, empties in every slot, nested alternations, captures in
  P rests / S heads, lookbehind bodies with mixed widths and a capture (`(?<=ab|(x)ad|ad)z`: owner stays out, held),
  caseless mixed width (`(?i)` with U+017F, U+212A). Conditionals: refused by pcrec ("not implemented yet"), not reachable.
- 19 more (w2) x {auto, vm}: recursion `^(ab|(x)ad|ad|\((?1)\))$`, `(ab|ac|a(?1)d)`, wide classes and caseless K inside
  lookbehind with a capture, lookahead holding the alternation, `(?:ab|(?:ab|a)c|ad)`, `(?:abc|a(?:b|x)(c)|abd)`.
- Randomized (writers: captures, \K, lookarounds with captures, atomic, nested alts, quantifiers incl. possessive, `$`,
  `\b`/`^`, `.`; branches mutated from earlier ones so M/P/S fire): byte 150 patterns, utf8 150, utf8 caseless (K/ß/é)
  120, byte caseless 80 -- {auto,vm} or {dfa,vm}; M fired on ~50% and P/S on ~40% of patterns (stamps read). Under deny
  levers (one of -fno-altcls-merge / -fno-altcls-factor / -fno-alt-island, one engine): byte 110, utf8 caseless 100.
- Deny levers: -fno-altcls-merge zeroes MERGES and leaves P/S live; -fno-altcls-factor zeroes FACTORED and leaves M live;
  both zero both (6 patterns x 4 settings). Lowering caller: `(?i)xβy` -e utf8 --engine=vm -fno-cls-kit IR differs with
  -fno-altcls-merge (with and without -fno-alt-island), so bit 10 reaches the lowering. `rx_info.flags` is 0 under both
  levers (masked, as §2.6/§2.7 say).
- Stamp contract (match_api §6.3.11¶3, tuning §2.6 examples): `x(?:a|b|cd|e|f)y` 1/0, `(?:ab\b|ad\b)` 1/2, `(?:xyr|zr)`
  0/1, `frank|fred` 0/1, `(?:ab|ac)(?:de|df)` 2/0 (two lists), dup-only `qb|qb` counted as a merge (consistent with §2.6's
  "a branch identical to an earlier one is dropped").
- req_pieces (facts_listing §4.1.2¶8c): `(?i)москва` 12/13/14/15 pieces checked by hand position by position against
  the U+1C80/1C82/1C83 fold variants of в/о/с -- every piece a sound superset; `(?i)kx`, `(?i)sk` (4 widths), `(?i)xß`,
  `(?i)ω` (Ohm sign), `a(?:bc|d)e` (spec example exact), `x(?:ab|cde)(?:f|gh)` (hull merge correct), `W@o:` form (39@7,
  140@108, last 32 positions), declines one-group / not-fixed-width (repeat, `^`, lookahead, `\K`, empty branch) /
  over-bound at 11 widths, 10 widths listed.
- Limits: --list-limits carries PCREC_MAX_REQ_PIECES 10, PCREC_MAX_ALTNF_WORK 1000000 (both unanchored internals,
  consistent with limits.md §0¶1); FACTOR_DEPTH re-described.
- K139 (limits §8.4¶2c / §8.5¶1b,¶5,¶6): 1,000-word --engine=vm: note printed, rc 0, VM_ALT_ISLANDS 0, artifact
  byte-identical to -fno-alt-island; --size-cap=refuse refuses quoting the unrescued 515,783 bytes; auto: ENGINE_SEL
  "size-cap-retry", 2b asked before rung 5.
- abi: artifacts stamp 96 (header guard, rx_info.abi); abi_changelog has the 96 entry (but see CON-1).
## Notes
- NOT probed: callouts (the driver has no binding; design §3.2 + match_api §11.6¶1 hunk cover fire count / give-up,
  verified the hunk is present); PCREC_MAX_ALTNF_WORK exhaustion (needs a ~3,000-branch mixed-width list, an expensive
  artifact); -I tests/findings/adversarial --analysis=uniform (the owner reads no prior, altnf.c header; not exercised).
- tuning.md §2.6 points to `limits.md` for PCREC_MAX_ALTNF_WORK, but limits.md has no text for it (only --list-limits,
  anchor empty). Cosmetic pointer, not filed.
- `a|a` under -fno-altcls-merge becomes `a(?:|)` (P with an un-merged empty rest list): answer-identical, FACTORED=1.
- A_EOL (`$`) is never "identical" for S (anf_node_same), so `(?:xa$|xb$)` does not suffix-factor while `\b` does: sound
  direction, a missed rewrite only.
- Harness: $R/contract/h/ (driver.c, diff.py, probe.py, w1.py, w2.py, rnd.py, rndf.py).
