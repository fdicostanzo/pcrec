# r4 START-SET panel: ssc-sound (soundness vs PCRE2 semantics lens)

Review r4, soundness lens, on `docs/design/startset.md` (lane report `docs/dev/lanes/startset_report.md`, instruments `docs/design/startset/`). 10 findings: 1 BLOCKER, 1 MAJOR, 4 MINOR, 4 NOTE.

The DFA hat as specified (T = S ∩ E, with the re-seed) deletes matches on shipped-corpus patterns (F1). The VM hat survived every attack.

Read-only in the main tree. Probes were compiled with `build/pcrec` (abi 61, built 2026-10-05 14:18) and gcc-16 in the session scratchpad. The oracle is LOCAL libpcre2 10.48 (Homebrew), NOT the 10.46 reference. Base agreed with it on every spot check quoted here.

The harnesses that reproduce every run are in `ssc-sound-harness/` (README there). In the tables below:
- **"tw"** is the narrowed scan without the re-seed.
- **"rs"** (DFA) is the narrowed scan with the re-seed: the design's §4.1 shape, applied by the design's own `twin/dfatwin.py`.
- **"twin"** (VM) is the design's `twin/vmtwin.py` seek.
- Every row covers every subject over the given byte alphabet up to maxlen, at every startpos, comparing the full capture vector.

## F1. BLOCKER. §2 (predicate F), §4.1 step 2, §0 finding 2: the DFA hat's T = S ∩ E is unsound, and the re-seed does not repair it.
- **Claim:** "A byte b ∉ E read in state 0 leaves the machine in state 0. A byte b ∉ S cannot begin a match at its position. So every position skipped with b ∉ T = S ∩ E begins no match."
- **Why it fails:** the argument holds only for positions READ IN STATE 0.
  - A skipped byte in E \ S moves the true machine out of state 0. That is exactly the context change the re-seed exists to repair.
  - The NEXT skipped position is then in that new context, where a byte in S \ E can begin a match.
  - The skip never stops there, because that byte is not in T.
  - The re-seed only corrects the state at the landing; it cannot recover a start the scan ran past.
- **Evidence:**

  | pattern (source) | route | \|E\|→\|T\| | alphabet, maxlen | cells | tw diffs | **rs diffs** | witness |
  |---|---|---|---|---|---|---|---|
  | `(?:(?<=a)z\|w)` (`tests/lookaround/d27/matrix.rxt:1064`) | dfa, byte-class-bounded | 2→1 | a z w x, 7 | 167,481 | 14,306 | **11,040** | "aza"@0: base/PCRE2 (1,2), rs NOMATCH |
  | `(?<=a)b\|(?<=bc)d` (`tests/lookaround/lookbehind.rxt:212`) | vm/hybrid exact | 2→1 | a b c d, 7 | 167,481 | 16,070 | **11,772** | "aba"@0: base (1,2), rs NOMATCH |
  | `(?m)(?<=\n)a\|b$` (`tests/ucp/ctxnode.rxt:400`) | dfa, byte-class-bounded | 2→1 | a b \n x, 7 | 167,481 | 16,598 | **12,264** | "\naa"@0: base (1,2), rs NOMATCH |
  | `\b-x\|y` (constructed) | dfa, byte-class-bounded | 63→1 | a - x y sp, 7 | 756,836 | 10,782 | **10,782** | "x-x"@0: base/PCRE2 (1,3), rs NOMATCH |

  - The census already holds the population. Recomputed from `docs/design/startset/census.tsv`: 62 seeded narrowing rows, of which **6 have S \ E ≠ ∅**, all corpus:

    | pattern | \|E\| | \|T\| | S \ E |
    |---|---|---|---|
    | `matrix.rxt:1064` | 2 | 1 | {z} |
    | `matrix.rxt:1122` | 3 | 1 | {z} |
    | `matrix.rxt:2597` | 2 | 1 | {z} |
    | `matrix.rxt:2662` | 3 | 1 | {z} |
    | `lookbehind.rxt:212` | 2 | 1 | {b} |
    | `ucp/ctxnode.rxt:400` | 2 | 1 | {a} |

  - No check looked at S \ E on a seeded machine.
  - The design's twins could not see it. Every twin pattern has S ⊆ E, and `dfatwin.py` computes T by the same formula, so the control shares its source with the subject (learnings §3).
  - The shipped offset-set rows are NOT affected. An oracle sweep over {a,z,w,q,x}^≤6 at every startpos gave 0 diffs on `(?<=a)zq|wq`, `(?:(?<=a)zzq|wwq)` and `(?<=a)zqq|wqx` (all offset-set-bounded). The defect is specific to the new T.
- **Fix:** choose one.
  - T = S ∩ E*, where E* is the union over EVERY seed state (each `seed[c]`, plus s0) of that state's escape set. Every skipped position's true context is some seed state, so this is the sound intersection.
  - T = S, which is sound with the re-seed but may be wider than E.
  - Decline the row when S ⊄ E.

  In every case:
  - add the 6 corpus patterns as fixtures;
  - add a sabotage row "T computed from state 0's escape set only", detected by answer identity on those fixtures;
  - correct S480: its expectation "emitted table == `start_set` ∩ the deny arm's table" pins this bug.
  - The F2 seeded-machine check is the standing control.

## F2. MAJOR. §0 finding 5, §6.2 (C-SS): the fact's independent control cannot fail where soundness is at stake.
- **(a) The failing-direction twin is a tautology.**
  - `summarize.py` counts `if E and E <= S and not E <= (S - {min(E)})`.
  - Since min(E) ∈ E, this is true for every non-empty E.
  - "The drop-one twin fires on all 685" therefore checks set arithmetic, not the walk.
- **(b) The population excludes the arms that matter.**
  - C-SS runs only on UNSEEDED machines, so the `A_CTX`, `(?m)^` and lookbehind-context arms are out, and F1's whole class is invisible to it.
  - Its erasure policy (zero-width → ε) is the one `src/ir/nfa.c` itself uses. C-SS therefore checks that two implementations agree, not that the erasure argument of §3.2 is sound.
- **Fix:**
  - Add a seeded-machine check: for every seed state σ, the bytes of esc(σ) that begin a live start thread ⊆ S, and the emitted T ⊇ S ∩ E*.
  - Give it a failing direction that plants a defect in the WALK (for example, drop the `null(l) ? F(r)` term of `A_CAT`) and shows violations appear.

## F3. MINOR. §4.2 (the VM consumer contract), §8 (the spec sentence), Q6: the give-up surface includes CAPACITY, not only meters.
- **Claim:** "the per-call step and work meters can only DECREASE … a call that returns `PCREC_ERR_STEPS` with the deny flag may return the unbounded-budget answer". The spec sentence says "positions … consume no budget".
- **Evidence:**
  - Pattern `(?=(?:a|b|x)*c)x`, flags `--engine=vm --backtrack-frames=8`, subject "abababababababababababab" + "xc" (26 bytes).
  - Base: `rx_search` returns -3, `PCREC_ERR_FRAMES`. The attempt at 0 (s[0]='a' ∉ S={x}) exhausts frames inside the lookahead.
  - VM-hat twin (`vmtwin.py`): r=1, span (24,25).
  - The corpus has 22 `gu frames` lines (and 13 `gu steps`).
- **Fix:** the §4.2 text and the §8 spec sentence must name capacity give-ups too: `PCREC_ERR_FRAMES`, trail, and the caller-buffer `_in` entries. The direction is unchanged (a give-up may become the unbounded answer, never the reverse).

## F4. MINOR. §1 and §3.4: census fidelity.
- **Census options:**
  - `census.py` builds corpus rows with `extra=[]`, so every DISTINCT pattern text compiles at byte with NO per-block flags.
  - Measured over the corpus: 629 blocks are utf8 (551 + 78) and 124 carry flags (115 `i`, 9 `u`).
  - Dedup by text alone merges, for example, `[a-z]` with its `i` twin.
- **fs_probe options:** it passes only `-e`, so it ignores `-i` and `--ucp`.
  - Under `-e byte --ucp`, the probe's S for `(?i)\xe9x` is {E9}, while the artifact matches "\xc9x". The VM twin built from the probe's set gives 4,239 diffs over {e9,c9,x,a}^≤6.
  - `\b(\w)\1` under `--ucp` gives 2,740 diffs (the probe's S is ASCII `\w`).
  - Inline `(*UCP)` is honoured by the probe.
- **The §3.4 claim holds on the wider population.** I extended it from 76 bench artifacts to the corpus's 629 utf8 blocks (flags mapped to `(?i)` and `(*UCP)`):
  - 598 compile;
  - 561 are non-nullable;
  - **0 of the 561 have a continuation byte in S**.
  - Only all-256 sets carry one: 9 blocks, `tests/vars/caseless.rxt` ×8 (`${v}` forms) and `tests/recursion/k69.rxt:183`.
- **Fix:**
  - State that the built fact reads the compile's own options.
  - Add a flagged witness (`-i`, `--ucp`) to the fact's checks.
  - Evaluate the S483 utf8 assertion only AFTER the non-nullable and `|S| < 256` conjuncts, or those 9 blocks will refuse to compile.

## F5. MINOR. §4.1 and §4.2 tables: reach and provenance of the twin evidence.
- **(a) A vacuous row.** `(a+)x\1catdog` (§4.2) reads 0 matches in `vmtwin_out.txt` (alphabet `axcatdog`, maxlen 6, which is shorter than the 9-byte minimum match). It is not evidence.
- **(b) A mis-recorded control.**
  - The `(?i)stra\x{df}e` CONTROL line (DROP=73) in `vmtwin_out.txt` reads `diffs=0`, while §4.2 claims 1.
  - I re-ran it: `DIFF [straße]@0 base=1(0,7) twin=0`, `diffs=1`.
  - The transcript is mis-recorded; the claim is right.
- **(c) No newline ever reaches a twin.** [F5(c)-F10 appended by the manager from the critic's complete first message; the critic's own write was interrupted here.] Every twin driver reads subjects with fgets, so no subject can contain '\n', and every (?m)/$/\Z/line-context cell is unreachable. Re-run with \x0a-capable drivers (ssc-sound-harness/drv2e.c, drv3e.c):
  - VM hat `(?m)$\na`, `(?m)^ab`, `(?m)(?<=^a)b`: 0 diffs.
  - DFA hat `(?m)\b(?:ab|cd)$`: rs 0 diffs, tw 132 (the no-re-seed control fires).
- **(d)** The count-collapsed hybrid obligation has no failing witness. With `-fprefilter-collapse` on `\b(ab|cd)\b.{0,2}\b(ab|c)\b` and `\b(a|b)\b.{1,3}\bc\b`, rs = 0 but tw = 0 too, so the hazard is not reached. The build's required collapsed mover needs a witness that fails without the re-seed.
- **(e)** One transient run showed rs diffs on a hybrid and did not reproduce in 3 reruns; discarded.

## F6 MINOR — §4.2 "every start rule is preserved" omits ordering against D133 and K50.
- The emitted VM-none order is: range guard → K50 STARTPOS → rx_valid_upto (-futf-check) → K65 memchr pre-check → loop.
- The seek must follow rx_valid_upto; otherwise an ill-formed subject with no S byte returns 0 instead of -9.
- The seek must start at max(search_from, the K82 handoff lo).

## F7 NOTE — §2 F does not name the scan kind.
- It should require RX_DFA_SCAN == unanchored; \G and (?m)^ go to the attempt scan.
- pf_emit_ofs_reseed is UNCONDITIONAL. On a gseed machine a re-seed at q == search_from would drop the \G start state. Specify the twin's conditional form (re-seed only if the scan moved).

## F8 NOTE — --engine=vm stops being an independent cross-check of the DFA on S once both hats read start_set.
- The engine axis in test-axes should also run under -fno-start-set; the deny arm stays the only independent control.

## F9 NOTE — V should read the walk's own nullable bit, not E1's `nullable` fact.
- Two sources can drift; the walk's bit errs on the safe side.

## F10 NOTE — what held (VM-hat twins, 0 diffs each, every startpos, full capture vector).
- `(?<!a)b`, `(?=ab)a`, `(?>a|)b`, `a?+b`, `(a|)(?1)b`, `(?:\1a|(b))+`, `(?(DEFINE)(a))b(?1)`, `(?=a)?b`.
- The newline cells in F5(c).
- utf8 with ill-formed bytes: `(?i)kx` with U+212A and lone E2/84, `.x`, `[^a]x`, `(?i)(\x{e9})\1`, `(?i)(k)\1`, `\w+\b`, `(?<=\x{e9})a`, `(?i)\x{df}` with ẞ.
- DFA-hat re-seed on S ⊆ E shapes, including byte+ucp `\b`, `(?i)\b`, `\b(?:ab|cd)\b` under utf8, `(?:\bab|cd\B)`.
- Confirmed: verbs, callouts, conditionals, \C, \X and \R refuse at compile. DEFINE lowers to {0}. UCP \b under utf8 is refused, so the single-byte-context premise holds. The zero-width erasure argument (§3.2) holds for the VM hat.
