# k73utf — K73 fixed (ruling (a)), and the [UTF-VALID] design note

Lane `k73utf` (opus, 2026-09-29), branch `lane/k73utf` from `lane/k7273`
(`f5a8cec1`), main merged in before work began. Scratch in `build/scratch/`
(gitignored) and `/tmp/claude-k73/`; four LIGHT probe compiles on ubuntubudu
(tailnet, `mktemp -d /tmp/...`, removed), transcripts archived in
`docs/dev/lanes/k73utf_evidence/`.

## Part 1 — K73 FIXED

### The mechanism

ONE emitter primitive, `pcrec_emit_start_zero` (`src/gen/emit_dfa.c`,
declared in `src/core/internal.h` with the `PcrecStart0` action enum), renders
"offset 0 is attempted only if it is a character start" from the backend's
start predicate. Each caller-facing body calls it with the action its return
convention needs:

| site | action | emitted line (utf8, nullable pattern) |
|---|---|---|
| unanchored DFA scan body (`emit_unanchored`): the DFA entry AND the VM hybrid's internal prefilter | SEEK | `if (search_from == 0 && !(S)) do search_from++; while (!(S));` |
| ENG_ATTEMPT start loop (`emit_attempt`) | SKIP | `if (start == 0 && !(S)) continue;` |
| VM search `_run`, after the first attempt position is set | SEEK | `if (attempt_position == 0 && !(S)) do attempt_position++; while (!(S));` |
| VM anchored `_run` ×2; DFA unwrapped `<prefix>_match` | NOMATCH | `if (ctx->pos == 0 && !(S)) return -1;` (DFA: on `search_from`) |

`S` is the utf8 backend's `start_guard`, which became the PLAIN predicate
(`@P >= @N || (@S[@P] & 0xC0) != 0x80`). Its old leading `@P == 0 ||` — the
caller exemption from the refusal — moved into `pcrec_startpos_guard_text`'s
composition (`!(P == 0 || S)`), so the emitted K50 guard line is
byte-identical. Only ENG_ATTEMPT's `continue` gate lost a dead
`start == 0 ||` clause.

**Which variable is sought is load-bearing, and it is why there are three
actions and not one.** `\G` reads the CALLER's `search_from` by name
(ENG_ATTEMPT's `start == search_from` dispatch; the VM's `, search_from`
argument), and libpcre2 answers `\G` FALSE after the move (`\G` on `\x80`: no
match; `\G|b` on `\x80\x80b`: (2,3)). Seeking `search_from` everywhere would
make `\G` true at the moved start. So only the unanchored scan body (which
never carries `\G` — `pcrec_nfa_has_bot` routes it to ENG_ATTEMPT) seeks
`search_from`; the VM seeks its own `attempt_position`; ENG_ATTEMPT skips.

**Gated on `pcrec_startgate_needed`** ([K50-NULLGATE]'s proof: a match that
consumes a byte begins on a character start, so a non-nullable pattern cannot
match at a continuation byte). So the population that moves is NULLABLE utf8
artifacts, not every utf8 artifact — narrower than the brief's "every -e utf8
artifact's guard".

**No flag.** Emitted under `-fno-startpos-guard` too. The report's option (a)
text said "-fno-startpos-guard staying byte-identical"; I did NOT do that,
for three reasons: (1) that flag's contract (tuning.md §2.23) governs where a
CALLER may point the entry and explicitly not engine positions; offset 0 on a
leading continuation byte is not a caller pointing inside a character;
(2) `run_startbnd_diff.sh`'s driver defines offset 0 as a position where the
two arms MUST AGREE, so a flag-gated rule would turn its B161/8080 subjects
into OTHER cells; (3) the axis sweep stays answer-identical over the corpus.
The manager can overrule; the change would be one `if` in
`pcrec_emit_start_zero` plus re-deriving (2).

### Found on the way, fixed with it: the unwrapped DFA `_match` had no K50 guard

§3.1 promises "the anchored entries carry the same guard". The DFA's
`"unwrapped"` `<prefix>_match` ([ENG-ABS]) calls no search and emitted no
guard: `x*` at `ctx->pos == 1` of `C3 A9` returned 0 instead of
PCREC_ERR_STARTPOS (measured on the branch point). It now emits
`pcrec_emit_startpos_guard` + the NOMATCH rule. Invisible before because
`run_startbnd_diff.sh` swept `<prefix>_search` only. Its two-arm driver now
sweeps `<prefix>_match` as well (own `match-buckets:` line, own 150 floor);
the failing-direction run against the branch-point compiler reads the five
DFA-routed witnesses at `match refused=0 other=15`, 75 < 150.

### abi 46 -> 47 (D76/D94)

The branch first bumped the abi from 45 to 46. Main then landed [UCP] U2 at
46, so the merge before delivery (`40c56343`) made this change 46 -> 47.
The readers were found by grep for `PCREC_ARTIFACT_ABI`, `ABI_EXPECT`,
`FILEPIN` and the digit, re-checking the ucpu1 bump's own list:

- `src/gen/emit_dfa.c:51`.
- `docs/dev/history/abi_changelog.md`: the new entry, with U2's 46 now "was".
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT`, and its §6-copied
  failure message, which gains a 46->47 clause after U2's.
- `tests/codegen/run_recursion_identity.sh` (B) FILEPIN: `7e8ab18a` ->
  `40c56343`, the merge commit that carries this lane's last `src/` change
  (self-pin). The gate compiles `byte` only, so (A) cannot move.

Every other hit is a number-free citation or dated history.

### Oracle and witnesses

- `tests/utf8/k73_startskip.rxt` — 11 blocks / 86 cells: `(?:)` (the empty
  pattern; see Findings F3 for why not `pattern-esc ""`), `\B`, `x*`, `(?=)`,
  `^`, `$`, `\b`, `\G`, `\G|b`, `(?m)^a|\B`, `a|` over five subjects that
  begin with 0x80 and three controls. Every cell from libpcre2 **10.46**,
  PCRE2_UTF|PCRE2_MATCH_INVALID_UTF (`k73utf_evidence/k73_witness_10.46.txt`,
  probe `pr2.c`). 86/86 on the fix; **45 fail** on the branch-point compiler.
  Two oracle cells deliberately omitted (Findings F1).
- `run_startbnd_diff.sh` §5: seven [K73] engine rows (DFA scan, ENG_ATTEMPT,
  VM, VM behind `-fprefilter`, `^`, `\G|b` on both engines), pinned to the
  same transcript, both arms required equal. All fail on the branch point.
  §5's permissive-arm failure message no longer blames the flag when both
  arms give the same wrong answer (the failing-direction run printed that
  false claim once per row).
- The anchored oracle: libpcre2 under PCRE2_ANCHORED advances too and reports
  the match at the moved start ((1,1) for `x*` on `\x80`); pcrec's anchored
  contract cannot report a start other than `ctx->pos`, so it answers -1 —
  stated in §3.1 as a second divergence. Both DFA forms and the VM agree.
- `mc` protocol: `x?` over `\x80\x80\x80` is now 1 (was 2), 10.46 through the
  same loop (`k73_mc_findall_10.46.txt`, probe `pr3.c`). The W23.5 fixture
  `mc_illformed_utf8.rxtin` used that subject to witness SW7's skip rule; K73
  took it out of that rule's reach, so the fixture's first case is now
  `a\x80\x80\x80` -> 2 (SW7 still load-bearing) and `\x80\x80\x80` -> 1 is its
  second. `verify_rxt.py`'s python transcription of the protocol applies the
  offset-0 skip before its first search; `rxt_format.md`'s `mc` paragraph
  says so.

### Sabotage rows (numbers checked against main AND open lane branches:
`lane/s3build`/`lane/land3` hold S365/S366)

- **S367** `pcrec_emit_start_zero` writes nothing — detectors: startbnd §5's
  K73 rows, `k73_startskip.rxt` via the harness arm.
- **S368** the unwrapped `_match` loses its guard — detector: startbnd's
  match sweep and its floor.
Field-validated (`VALIDATE_ONLY=1`: both FIELDS OK). The failing direction of
each detector was measured against the branch-point compiler (which is both
plants' state); the mech solo runs themselves are OWED (see Validation).

### Spec hunks (D80)

`docs/spec/match_api.md` §9.2-§9.5 (§9.2¶9, §9.3, §9.5) (the "neither arm rounds" sentence scoped to
`startpos > 0`; two new bullets: offset 0, anchored entries; the
engine-positions paragraph), docs/dev/history/abi_changelog.md (abi 46); `docs/spec/tuning.md` §2.23;
`docs/spec/rxt_format.md`'s `mc` paragraph. `known_issues.md` K73 FIXED.

## Findings (Part 1)

- **F1 — a second, pre-existing ill-formed-subject divergence, NOT K73's.**
  `$` on `\xff` and on `\xe3\x80` (an ill-formed LEAD at the end): libpcre2
  10.46 no match, pcrec (1,1)/(2,2) — identical before and after this fix
  (A/B against the branch-point binary). Likewise `\B` on `a\x80` (10.48
  local: no match; pcrec (2,2)). The shape is "an assertion at the end of a
  subject whose last character is ill-formed". Not filed; the manager's call
  whether it is a K-entry or a stated divergence under ASK 1.
- **F2 — the spec's own find-all loop stops at a stray continuation byte
  after a non-empty match.** `a` over `a\x80a`: the loop passes
  `caps[0][1] == 1` as the next `startpos`, which is a continuation byte, so
  the K50 guard refuses it (-7) and the loop ends with 1 match where libpcre2
  through the same loop counts 2 ((0,1),(2,3); `k73_mc_findall_10.46.txt`).
  Pre-existing (the branch point does the same) and a direct consequence of
  ruling (a) keeping the explicit-`startpos` refusal: the refusal cannot tell
  "a caller pointing inside a well-formed character" from "a caller resuming
  at a stray continuation byte". The harness also mislabels the -7 as "VM
  budget exhausted". A question for Frank, with the same three shapes as
  K73's: leave it, extend the SEEK to any `startpos` whose PREVIOUS byte is
  not a lead expecting it, or have the protocol step `p` through
  `next_pos` when `s[p]` is a continuation byte.
- **F3 — a file whose first block opens with `pattern-esc` is read as
  head-bearing by `run.sh` and by `run_rxtsource_tests.sh`'s awk census.**
  rulefix's ruling 2 fixed leg C only; the population was zero until this
  lane's first draft (`pattern-esc ""` first) made C0a and C1 red. Measured:
  with the census awk widened to the opener set, `run.sh` still called
  `--list-source` on the file (C0a 25 vs 24). Worked around by spelling the
  empty pattern `(?:)`; the latent disagreement stands, population zero again.
- **F4 — the K50 guard's comment is emitted in DEFAULT artifacts.** It is part
  of `pcrec_startpos_guard_text`'s snprintf, not a `pcrec_sb_cmt_open`
  region, so `-fno-comments` does not remove it; the unwrapped `_match` now
  carries it too. Pre-existing; noted, not changed (it would be its own
  byte-moving event).
- **F5 — `run_encoding_checks.sh` is red at the branch point**, 5 checks,
  every one reproduced identically there with the branch point's own script
  and binary (same 228/244 strict pairs, same FINDING set): `RX_FINDINGS`
  stamp and `REQ_WHY` differences, the K50 gate-refinement manifest's 8 stale
  / 8 new rows. Not this lane's. This lane added the `start_zero` region
  (102 excisions at slice 250) and `startpos_guard` rose 420 -> 514 (the new
  unwrapped `_match` guards); nothing else moved.

## Validation (Part 1)

All on this Mac (darwin, gcc-16), at 2 workers or fewer, logs under
`worktrees/k73utf/build/scratch/`:

- `make strict CC=gcc-16`: clean (`strict.log`).
- `tests/harness/run.sh tests/utf8 tests/classes tests/ucp` (PROCS=2):
  **3906 passed / 0 failed** (`h1.log`, run before `k73_startskip.rxt`
  existed — so no pre-existing corpus cell flipped); `k73_startskip.rxt`
  alone **86/0** (45 fail on the branch-point compiler).
- `tests/utf8/run_startbnd_diff.sh`: **8/0** (`startbnd.log`; search 150 +
  match 150 refused, 680 same, 0 other; §5 incl. the seven K73 rows).
  Failing direction against the branch-point binary: red on §1/§2, both
  floors, all seven K73 rows (`startbnd_base.log`).
- `make test-rxtsource` (PROCS=2): **270 passed / 0 failed / 1 RECORD** (the
  standing py3.9 C3 note) after the census re-pin (`rxts4.log`).
- `make test-codegen` (PROCS=2): **11/12 scripts**; the one red is the
  standing darwin `nm could not read arm_a.o` probe (`codegen.log`), incl.
  `[SABANCHOR]` 344/344 and `ABI_EXPECT=46`.
- `make test-registry`: every section green except the definitions oracle,
  whose 12 "result file truncated" cells were 10 s WALL timeouts at load
  average ~9 (`reg.log`, watchdog lines); re-run standalone
  (`tests/registry/run_definitions_oracle.sh`): **354 cells, 101,244 +
  101,244 comparisons, 0 disagreements** (`defor.log`).
- `tests/codegen/run_encoding_checks.sh` (slice 250): 10/5 — the same five
  reds, same FINDING set, as the branch point's own script + binary (F5).
- Sabotage rows S367/S368: `VALIDATE_ONLY=1` FIELDS OK; anchors 344/344.
- **Mover census** (`k73utf_evidence/k73_census.py`, output
  `k73_census.out`): every distinct corpus `pattern` line (3,353) compiled by
  the branch-point and the fixed compiler, same `-o` basename, abi digit
  normalised. **`byte`: 0 movers** (2,986 identical, 367 refused both).
  **`-e utf8` default route: 1,361 movers**, of which 1,210 carry the new
  unwrapped-`_match` K50 guard and 384 carry the zero rule (849 lines).
  **`-e utf8 --engine=vm`: 386 movers**, every one exactly the zero rule's
  three lines (search + both anchored `_run`s), 1,158 lines. UNPREDICTED:
  **0** on both utf8 configs. No refusal mismatch anywhere.

**After merging main (U2, abi 46 -> 47), re-run on the merged tree:**
- `make strict`: clean.
- `k73_startskip.rxt` + U2's `axis13_ctx_illformed.rxt`: 118/0.
- `run_startbnd_diff.sh`: 8/0.
- `make test-rxtsource`: **270/0**, with the combined pins U2 + K72 + K73 =
  256/4261/31703, C3 SKIP 17711 and pcre2-only 3504, holding on first run.
- `make test-codegen`: 11/12, the standing `nm` probe only, with
  `ABI_EXPECT=47` passing.

The mover census was taken before the merge (abi 45 vs 46), and U2 moves
lookaround artifacts on its own. The census script accepts 45-47, but it
was not re-run.

**OWED to the manager:** the full `make test`; `make mech` rows S367 and
S368 solo (their detectors' failing direction is measured above against the
branch-point compiler, which is both plants' state); the recursion-identity
gate at the new (B) pin (`tests/codegen/run_recursion_identity.sh`, opt-in,
not run here — the pin moves by the abi digit only); `make test-axes`
restricted to `-fno-startpos-guard` if wanted (the rule is unconditional, so
the axis is expected answer-identical over the corpus).

## Part 2 — the [UTF-VALID] design note

The note is `docs/design/utf_valid_design.md`, with its evidence in
`docs/design/utf_valid_evidence/`. Summary:

- **PCRE2's contract, measured on 10.46**: before any attempt it checks
  `[startoffset − max lookbehind (chars), n)`, and the error offset is the
  first bad sequence's first byte. `a` on `a\xff` is REFUSED even though the
  match precedes the bad byte, and a lookbehind that reaches back widens the
  checked range.
- **One option, two contracts, one first-match table** (inert / off /
  scan-fused / precheck). The precheck is the total fallback, because its
  promise implies the incremental one.
- **Recommendation: build `whole` only.** It is a precheck through an
  encoding-residual entry, called once per call by the entry wrapper, which
  is `[VAR]`'s `$_var_valid` shape. It would become the ONE validator for
  the precheck, the caller's offset query and `var_valid`.
- **Do not build `scan`.** Its contract depends on the bytes the optimizer
  skips, it has no VM coverage, and it costs states that can move the
  refusal set.
- **Caller surface**: a compile-time axis (D18), one code `PCREC_ERR_UTF`
  (-9), and an exported `<prefix>_utf_invalid_at(s, n, from)` for the
  offset, so that `caps` stays untouched.
- **The find-all loop becomes quadratic** under `whole`, as it is in
  PCRE2. The answer is to validate once and use a non-checking artifact.
- **Cost (darwin, directional).** With an ASCII fast path the check costs
  0.04 ns/B on ASCII text: 17x a call a prefilter answers, 1.6x a call a
  pre-check answers, 12% of a scanning call. On non-ASCII text it costs
  1.0-2.5 ns/B, 3x-7x a full DFA scan. The byte-class-DFA validator is a
  flat 1.95 ns/B.
- **It is an abi event once built**, default-off artifacts included,
  through the shared-block code and an unconditional stamp.
- **Ten questions for Frank**, each with a recommendation.

Probes: two LIGHT tailnet probes to 10.46 (`pr4.c`, transcript archived).
Timing: `utfcheck_bench.c` run twice at load average 7-10, plus
`scanbench.c` for the pcrec reference rates.
