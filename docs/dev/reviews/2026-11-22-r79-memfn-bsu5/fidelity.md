# CRITIC fidelity: memfn-bsu5 (r79)

## Findings

### FIDELITY-1 (CONFIRMED; severity speed (measurement fidelity); effort small; blast radius C6+C6c hexb32 cells only)
`c6_hexb32` (`\b[0-9a-f]{32}\b`, loglines/hex32-id) in regimes `near-miss-in` and `near-miss`, at both layers (C6 `on`,
C6c `off-clang`): the cell NEVER CALLS THE SPAN, so it is timed as a V-vs-H64 comparison of a site neither arm reaches.
cards.py:418-444 (`subject`): NMI's miss byte and near-miss's miss byte are the first of "zZ#@!" outside the set, i.e. `z`,
a WORD char; the subject's whole alphabet is [0-9a-f z] (all `\w`). The emitted site (artifact a_5c811767a5e1d1bd.c line 400,
`Pattern: \b[0-9a-f]{32}\b`, V on) tests the LEFT `\b` (`s[c-1]` non-word) BEFORE `rxa_mf1_vs0(...)` with `&&`, so the
selector is reached only at c = 0. Repro (pure functions only): `cards.subject('c6_hexb32', R, 1<<20, 1)` and count c with
(c == 0 or s[c-1] non-word) and s[c+31] hex: near-miss 0, near-miss-in 1 (of 1 MiB); hit-dense 31775, random 30778 for
contrast. Expected: §8's "near-miss-in at the window sites" is 710's span-depth staircase; here it is a dead cell. C6_SEP
(cards.py:326) already fixes exactly this for hit-dense (a ' ' after each match), but not for the two miss regimes. The
§8/C6_RULE N/A rule would exclude such a cell only via U6's still-unbuilt call count ("UNMEASURED DEFAULT, U6's reader"), so
as delivered these 2 x 3 arms x 2 layers = 12 cells (of 216) enter the plan's counts and expected wall time and, if U6 forgets
the N/A read, the verdict as a TIE. Fix: a non-word miss byte where the pattern needs one (e.g. extend C6_SEP's role: miss
from " #@!" for `\b` patterns), or declare the two cells N/A/CUT in the card; and a dry check that each C6 cell's span is
reached (an untimed call count), which also discharges the N/A rule's owed input. Minimum witness: k 31, 1 MiB subject.

### FIDELITY-2 (CONFIRMED deviation from §8's text; provenance of the cut SUSPECTED; severity speed (coverage); effort trivial; blast radius one pattern, C6 only)
§8 "Regimes": "The cards' six regimes, plus near-miss-in at the window sites." `regimes_of` (cards.py:375-379) adds NMI only
where `k + 1 <= 255`, so the window site `c6_hex1001` (window k 1000, w4095, the UPPER-bound cell) gets no near-miss-in
(plan.out line 1603: "near-miss-in at the window sites with k + 1 <= 255: c6_hex17,c6_hex32,c6_hex33,c6_hexb32"; dry.out has
no hex1001 NMI row). The docstring's reason ("710's definition: the cards' near-miss never calls the span there") does not
hold for this card's own generator: `cards.subject('c6_hex1001', 'near-miss-in', 1<<18, 1)` run through the emitted site's
shape (probe s[c+1000] hex -> span; a/a_89374422a2ab0410.c, `Pattern: [0-9a-f]{1001}`) calls the span 86057 times in 256 KiB,
failing index min/median/max 0/490/992: exactly the deep staircase near-miss-in exists to time, at the k where V's block
loop runs longest. §8 states no k limit, and the cut is not listed among §8's CUT cells. Either §8 gains the limit with 710's
citation (if 710's definition really bounds k; I could not read 710's generator: denied scratch), or the cell is added
(3 arms, 1 layer: +3 cells). Minimum witness: k 1000, 256 KiB.

### FIDELITY-3 (CONFIRMED by reading; severity design (owed to U6, worth naming now); effort small; blast radius every future C6/C6c result)
§8: "The rule's sha is recorded with the result" and deps `kit:form.span-vector=<hash>`. cards.py has NO writer that records
either with a result: the results row (HEADER, cards.py:882) is card/pattern/arm/regime/layer/status/median/spread/launches/
method/variants; the RUNDIR records are `run_id`, `run_id.timed`, `rule_g2.json`, `same_as_I.json`, `sizes_h*.tsv` (grep of
`json.dump`/rundir writes); `C6_RULE_SHA` (cards.py:1006) is printed only by `plan`. The row also does not carry: the WINDOW
WIDTH (a code-constant function of the pattern id, `C6_WIDTH`: an edit to it re-means every earlier row under an unchanged
key), the compiler IDENTITY (the exe cache key carries `cc_ident(cc)` = name + `--version`, cards.py:680-690, but the row
names only the layer `on`/`off-clang`; `CLANG`/`CC` are env-overridable), and the frozen binary's identity (the artifact key
hashes the binary, the row does not). Nothing times C6 today (claim 6 holds, see PROBED-AND-HELD), so this is not a wrong
number yet; but §14's U5 row claims the card "as §8 states", and the place the sha/hash/width/compiler land is a format
decision best made with the card, not by U6's timer. Suggested minimum: `time_cells` writes one `#`-header line per results
file for C6 cells: rule sha, formhash value, frozen-binary sha, `cc_ident` per layer, and the (pattern, width) map.

### FIDELITY-4 (CONFIRMED gap, no wrong value today; severity maintenance; effort small; blast radius C6 regime set + plan's printed claims)
`C6_SITE` (cards.py:316) — each pattern's site kind and k — is a hand-typed annotation that DRIVES behaviour (`regimes_of`
adds near-miss-in only where kind == "window") and is printed by `plan` as fact ("c6_hex17(w32,window k16)"), but no check reads
it against the artifact. `check_c6` (cards.py:641-665) checks only that V carries `__body`/selector (+`__w32` at `on`) and H64
none; it would pass with a wrong k or kind (e.g. `c6_hex17` edited to `{18}`: k 17, still inside the bound, V renders, plan
still prints k16; or a scan pattern mislabelled "window" gains an NMI cell). I verified all 8 by hand on the dry's artifacts
(`__w32`'s loop bound = k: 31,31,31,16,32,1000,24,64; finder shape: Horspool `rxa_mf1_sh` probe = window/D-hors for the 4 hex
+ hexb32, byte-scan `while` + `p = s + c + 1` = scan/R7w for the 3 \d): ALL MATCH today. Fix: in `check_c6`, parse the
`__w32` loop's bound (or the selector's k) and the finder shape and compare with `C6_SITE`, failing the dry on a mismatch.

### FIDELITY-5 (CONFIRMED; severity doc; effort trivial; blast radius block_span.md §8/§2.2.1/§14)
The design of record at SUBJECT does not describe C6c: §8 says "The SIMD-off wrapper is not timed anywhere (r68 F-14): U2b's
census is its record", lists no clang arm, and §2.2.1 still reads `wrap-clang` (OPEN); yet C6c times exactly the SIMD-off
wrapper (V vs `--memfn=no-span-vector` at `off-clang`, 60 cells; plan.out 1602), with a new UNMEASURED alignment-variant default
`CLANG_ALIGN_OFF` (cards.py:697) absent from §12's constants register. The authority exists elsewhere (plan row
[BSPAN-CLANG-DIFF]: "trigger: ... rides the kit's U5 C6 card"; D201 add. 5), and cards.py's own comments cite it, but U5's diff
has no block_span.md hunk (diff --stat: no docs/design path), so a reader of §8 (the contract C6 is reviewed against) is told
the wrapper is untimed. Fix: a §8 paragraph for C6c (patterns = the 3 real sites, layer off-clang, its alignment variant, what
it settles: [BSPAN-CLANG-DIFF], not the CANDIDATE gate), §2.2.1 marked ANSWERED (add. 5), §12 gains CLANG_ALIGN_OFF.

## PROBED-AND-HELD

- (a) END TO END, one C6 cell (`C6 c6_hex32 V hit-dense on`) and one C6c cell (`C6c c6_dig32 H64 near-miss off-clang`):
  `artifact` (args = PCREC, `--window-search-width=32` from C6_WIDTH, LAYER_FLAGS[layer], arm flags; cached on hash(args, binary
  bytes)) -> `text_key` (hash of artifact + DRIVER) -> `build_cell` (pool draw from the text key; `cc_of(layer)`; `flags_for`
  maps gcc's align-off draw to CLANG_ALIGN_OFF; exe name = text key + v + variant_key(text, prelude, flags, cc_ident(cc))) ->
  `prepare_cell` gates EVERY variant's exe on the regime's subject -> `time_cells` times `argv[c][v]`, the SAME exe path and
  subject with CARD_TIME=1, which re-gates its own first call before timing. The timed entry IS the gated entry. HELD.
- Exe key carries every exe input: verified the gcc and clang names differ for the same text on all 4 variants; the dry's bin/
  holds 88 exes = 22 texts x 4, `.o` comments: 64 GCC 15.2.0 (16 texts) + 24 clang 21.1.8 (6 texts = 3 patterns x {V,H64}) —
  exactly the layer->compiler map. Width and layer enter via the artifact args; arm via its flags. C1-C5 exe names unchanged
  (cc_ident(CC) yields the same string as the old cc_ident()). HELD.
- Uniqueness: `cells(cards=('C6','C6c'))` = 216 cells, 216 unique keys; C6 and C6c rows of one pattern differ in card AND layer;
  no C6 pattern id or text is shared with C1-C5 (C1's `hex32` is the same regex at width 4095: a different text). H64.b's text
  key == H64's (the A/A arm times the deny exe twice, as §8 says); V's != H64's (c6_hex32, c6_dig65 checked). HELD.
- Plant "swap an arm's key" (copy of the module in-process, arm_flags V<->H64, cached artifacts only, 0 compiles): `check_c6`
  fails 30 times over 11 pairs ("DENY IGNORED ..."; "arm V carries no wrapper"); unplanted: 11 pairs, 0 failures. HELD.
- Plant "halve the timed loop only" (on paper): the timed loop lives in DRIVER, which every arm's TU shares byte for byte, so
  any edit to it moves V, H64 and H64.b alike and the card's unit (a V/H64 ratio in one cell) cannot see it, nor can it bias
  one arm; an arm-local timed-path edit is impossible without a different text, which `check_c6`/the text key separate. HELD
  (with the standing caveat that the timed reps are not answer-checked, pre-existing, symmetric).
- Claim 6 (nothing timed; no command times C6): every `time_cells` caller reads STEP1 / C3 / confirm_cells (built from the
  rule's C1/C2 loops) / a rerun of results.tsv or results_c3_h* (STEP1 / C3 cells); `rule`, `identity`, `selftest` loop over
  ("C1","C2"), C3, or the harness; `plan` and `dry` only list/build/gate. No path reaches a C6/C6c cell with a clock. HELD.
- (b) THE CELLS, from the dry's artifacts (22 texts, every `Pattern:` header read): all 8 §8 patterns present (3 real at w32;
  window k16/k31 at w32, k32/k1000 at w4095; scan k24 at w32, k64 at w4095), nothing extra in C6; F2 DIFFERS list empty with its
  reason. Each V artifact routes the site to the stated finder (window: Horspool probe at c+k, `rxa_mf1_vs0` called on a hex
  probe; scan: the `\d` byte scan, V from c+1) with `__w32`'s bound = the stated k (31,31,31,16,32,1000,24,64). Arm V at `on`
  carries `<immintrin.h>`, the target pragma, `__body`, `__w32`, selector; H64 at `on` none of them (stamps differ only by the
  include/pragma block); at `off-clang` V carries `__body` + selector and no `__w32`, H64 none, `#` lines identical. HELD (minus
  FIDELITY-1's hexb32 miss regimes and FIDELITY-2's hex1001 NMI).
- Dry/plan counts: dry 216 cells built and gated, 0 failures, 22 distinct compiles, 22 pools x 4 refused 0; plan C6 156 / C6c 60.
  Consistent with cells(). HELD.
- 710 rule sha in cards (6351bff3901e3955) equals R/meta_710.json `rule_sha` and the rule file's line 1. HELD (whether it is
  RECORDED is FIDELITY-3).
- Budget used: 0 pcrec compiles, 0 gcc/clang compiles (all from the dry's cache, copied to fidelity/rd/).

CRITIC COMPLETE
