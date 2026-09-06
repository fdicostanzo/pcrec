# Lane `k50bnd` — [K50-BNDSTART]: candidate match starts are character boundaries

Branch `lane/k50bnd`, worktree `worktrees/k50bnd`, 2026-09-06. Charter: plan
row `[K50-BNDSTART]`; defect: `docs/dev/known_issues.md` K50.

---

## 0. The headline, and the two things the charter did not know

**K50 is fixed on all three mechanisms, and the caller-startpos guard ships
default-on with its deny arm.** `\B` over `61 CE B1` from `startpos 0` answers
`(3,3)` on both engines, which is libpcre2 10.46's answer under both UTF
option words; it answered `(2,2)` — precisely libpcre2's `options=0` BYTE
answer — before.

Two things came out of the work that the charter could not have contained:

**(1) SITE (2) WAS A LIVE WRONG ANSWER, not a wasted attempt.** K50's site
list names `ENG_ATTEMPT`'s `start++` loop as *"the loop `utf8_design.md` §5.5
and ASK 5 are about"* and files no witness for it, because §5.5 asserts such
starts cannot produce a wrong answer and Frank's ASK 5 ruling was given that
claim. Measured on the shipped tree:

| | |
|---|---|
| pattern | `(?m)^a\|\B` (`--features assertions,modifiers`) |
| subject | `61 CE B1`, `startpos = 1` — a **real character boundary** |
| pcrec `-e utf8` before | `(2,2)` — mid-character |
| libpcre2 10.46 `PCRE2_UTF` | `(3,3)` |

The witness needs two branches and neither is optional: the BOT-family branch
routes the pattern to `ENG_ATTEMPT`, and the nullable second branch keeps an
interior start state live so `start_max` is the subject length. **A pure
`(?m)^` or `\G` pattern is self-gating** — `(?m)^` can hold only after a
newline and a newline is a character-start byte; `\G` gives one attempt at the
caller's own position — which is why the site stood unwitnessed for a whole
milestone. A fix closing only mechanism (1) would have left it standing.

**(2) MY OWN GUARD WAS WRONG ABOUT OFFSET 0, and `make test-axes` found it.**
See §6. It is the finding I would most want a reviewer to check.

---

## 1. What changed

### The engine half (no flag — this is the correctness fix)

One new datum on `PcrecEnc`, asked as a predicate rather than as a step:
`start_cls` (the bytes a character may start at, as a 32-byte class) and its
expression twin `start_guard`. **Both NULL under `byte`**, which is what makes
"the encoding with no defect pays nothing" a construction rather than a
comparison.

| site | mechanism | change |
|---|---|---|
| 1 | `src/ir/nfa.c` `nfa_wrap_unanchored` | **TWO split states.** `nfa->start` stays the ungated split (the caller's own position); the self-loop returns to a second split whose pattern branch is gated by a new `N_CSTART` node |
| 2 | `src/gen/emit_dfa.c` `ENG_ATTEMPT`'s start loop | `if (start > search_from && !(guard)) continue;` |
| 3 | `src/gen/emit_vm.c` hybrid handoff | **no change needed, and the entry's own reasoning is why** — a fix for (1) closes (3), because the prefilter IS a DFA emitted through `pcrec_emit_dfa_engine` and therefore carries the gate |

**Why two splits.** The engine owns the positions it INVENTS; the caller owns
the one it supplied. That split of responsibility is Frank's ruling, and it
buys something concrete: **one machine serves both arms of the deny axis**, so
the flag moves only the emitted entry guard and never the automaton. A gate on
the first split too would make the deny arm answer no-match where
`utf8_design.md` §2.6.1.1 rules `(1,1)` — the axis would have become a second
automaton rather than a guard.

**Why a `continue` at site 2 rather than K49's `advance` text.** Taking the
step means replacing a `for` header's increment with a trailing statement,
which moves every byte artifact — an abi event for the encoding that has no
bug. A guard is additive.

`N_CSTART` is `N_EOL_M`'s shape (one `end_ok` read, one class-axis read, no
direction), and the class axis gains a fourth partition value, `UPC_NOSTART`.
**Its partition precondition is CHECKED, not assumed** — a non-start byte that
were also a word byte would classify `UPC_WORD`, read as a character start to
the gate, and re-open K50 silently. `pcrec_enc_start_cls_ok()` refuses such a
backend by name.

### The caller half (the `-fno-startpos-guard` axis)

`PCREC_ERR_STARTPOS = (-7)`, below `PCREC_ERR_FLOOR`: a refusal of the CALL,
not a give-up — nothing was attempted and no budget was spent.

**The spelling you suggested was the deleted one.** `RX_ERR_STARTPOS` is the
per-artifact `<PREFIX>_ERR_*` form D60/[ABI-NS] deleted (not aliased) on
2026-08-18; `match_api.md` §4 makes these a pcrec-CONTRACT fact in the shared
unprefixed block.

`PCREC_NO_STARTPOS_GUARD` is bit 25. **It is the first member of that enum
that changes an answer**, and everything odd about it follows: it is NOT
masked out of `rx_info.flags` (a caller must be able to read which contract an
artifact carries), and `make test-axes` carries it as a documented divergence
class rather than an identity claim.

One emitter, four call sites (`pcrec_emit_startpos_guard`): `emit_search_head`
gated on `fit.chosen == ENGM_DFA` — the same discriminator the dead-group fill
uses, so the VM hybrid's internal prefilter is not guarded — and the VM's three
`_run` statics, **which is the one point every rung of the [CC-DIFF] STEP 2
entry ladder passes through in both delegation directions** (`plain`/`shared`
run `_in` → un-suffixed; `forward`/`inline` run the other way). Guarding there
makes the six public entries agree by construction rather than by six copies.

**Ordering against `startpos > n` is unforced, and that is a property of the
backend's text rather than of the placement.** `match_api.md` §3.1 promises
`0` there (libpcre2 answers `BADOFFSET`; pcrec does not follow), and the utf8
guard opens `@P >= @N`, so every position the range test owns passes untouched.

---

## 2. The 10.46 measurement, and what it decided

`docs/design/utf8_measurements/out/startbnd.txt`, written by
`probes/probe_startbnd.py` through the lane's own archiver — remote run,
header stamps `libpcre2 10.46 2025-08-27`, `selfcheck clean`, source SHAs for
the bytes that answered.

The charter says to measure BADUTFOFFSET before pinning any compat claim. The
question I asked was sharper than "what does it do", because an O(1) entry
guard can only reproduce a property of the OFFSET: **is the refusal uniform,
or pattern-dependent?**

**Uniform.** 10 patterns × 2 mid-character offsets = **20/20 `ERRM -36`**, and
the same 10 patterns at the three boundary offsets = **30/30 answer normally**.
Vacuity guarded in both directions. That is what licenses the shape.

Two further rows the transcript settles:

- `startoffset > n` under `PCRE2_UTF` is `ERRM -33 (BADOFFSET)` where pcrec
  promises `0`. **A deliberate, recorded divergence**, now stated in
  `match_api.md` §3.1 rather than left for someone to discover.
- §3's ill-formed rows record where pcrec's ruled semantics legitimately part
  company with `MATCH_INVALID_UTF` (`\B` on `61 FF B1` from offset 0: pcrec
  finds `(3,3)`, `MATCH_INVALID_UTF` reports no match, its barrier rule). Not
  chased — §2.6/ASK 1 rules pcrec's answer is the automaton's — but recorded.

**Result, default arm vs 10.46 `PCRE2_UTF` on §2.6.1.1's table, cell for cell:**

| pattern | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| `(?<!.)` pcrec | `(0,0)` | REFUSED | no-match | REFUSED | no-match |
| `(?<!.)` 10.46 | `(0,0)` | `ERRM -36` | no-match | `ERRM -36` | no-match |
| `(?!.)` pcrec | `(4,4)` | REFUSED | `(4,4)` | REFUSED | `(4,4)` |
| `(?!.)` 10.46 | `(4,4)` | `ERRM -36` | `(4,4)` | `ERRM -36` | `(4,4)` |

Identical modulo the code number, which D26 makes the wrong tier.

---

## 3. The abi ritual (D76/D94)

`abi` **23 → 24**. Readers found BY GREP over the current number, all updated:

```
src/gen/emit_dfa.c:1801        .abi = 23           -> 24  (the stamp)
src/gen/emit_dfa.c:1775        the abi comment block      (per-artifact-kind breakdown)
tests/codegen/run_codegen_tests.sh:2761  ABI_EXPECT=23 -> 24  (+ its message)
tests/codegen/run_recursion_identity.sh  FILEPIN            (B) re-pinned
docs/spec/match_api.md:159     "rx_info.abi is 23"  -> 24
docs/spec/match_api.md:1816    "rx_info.abi is 24 on every artifact today"
```

`tests/registry/run_registry_tests.sh:345` mentions abi 23 as *provenance for
a row-count pin*, not as a reader of the number — left alone deliberately.

**(B) is pinned to `9e276472`**, this lane's last `src` commit, per the
lane-pins-its-own/manager-re-pins-at-merge precedent. **You will need to
re-pin it to the merge commit.**

**What moves:** every artifact of both engines gains TWO lines — the
`PCREC_ERR_STARTPOS` define in the shared ABI block and a
`<PREFIX>_STARTPOS_GUARD` selection stamp in the shared prologue. **No `byte`
artifact's PROGRAM moves.** A `utf8` unanchored DFA artifact's MACHINE moves
(the gate is a real automaton state) — only the second bump in that file's
history to move a machine.

**It is the first bump in that list carried by a change that moves an ANSWER**,
so unlike every deny flag before it `-fno-startpos-guard` does not sweep this
to identity and is not meant to.

---

## 4. Validation

| instrument | result |
|---|---|
| identity gate, 4 axes | see §8 (run in the delivery block) |
| `make test-codegen` | see §8 |
| `make test-encoding-checks` | see §8 |
| `make test-startbnd` (new) | 6/6 sections |
| `bash tests/harness/run.sh tests/utf8` | 1342 cases, 0 failures |
| known-fail ratchet | fired `NOW PASSING` on K50's cell, then the cell moved live |
| `tests/rxtsource` | 106 pass / 14 fail, **byte-identical failure set to the branch point** (measured against a build of `1c4c91b4`) — the 14 are the darwin `xargs -a` and padded-`wc` issues that file's own comments already document |
| `python3 tests/harness/verify_rxt.py tests/utf8` | 388 pass / 0 fail / 100% |

### The differential — `tests/utf8/run_startbnd_diff.sh`

The shape is possessify's and **the claim is the opposite one**. Every other
`-fno-` differential checks that two arms AGREE; this axis is the only
non-answer-identical one in `tuning.md`, so agreement everywhere would mean the
flag does nothing. What is checked is WHERE they differ.

Six sections: §1/§2 the arms identical at every boundary and differing ONLY by
the typed refusal at mid-character positions (**340 agreeing, 150 refused, 0
otherwise**, 10 witnesses × 11 subjects); §3 the non-vacuity floor; §4 the byte
encoding paying nothing; §5 the cross-engine cells; §6 §2.6.1.1's ruled
permissive table pinned on the deny arm.

**The floor is DERIVED, not transcribed from a run** — 10 patterns × 14
continuation-byte positions across the subject list, with the per-subject
arithmetic written out at the check, so a reader can tell a shrinking
population from a re-baselined number.

**§5's cells are pinned to libpcre2 10.46 rather than to the other engine**,
and that is the section's whole value: for a milestone BOTH ENGINES ANSWERED
THE SAME WRONG THING, so nothing comparing pcrec against itself could have
caught K50.

### Sabotage validation — seven directions, all detected

| direction | caught by |
|---|---|
| guard deleted (backend supplies no `start_guard`) | §1's per-pattern "DEFAULT arm emitted NO guard" |
| over-firing at end-of-subject | classification defect (after the driver fix, §6) |
| over-firing on lead bytes | classification defect |
| leaking into the deny arm | the artifact TEXT check, before anything runs |
| leaking into byte artifacts | §4, **three independent ways** (mask, emitter, stamp) |
| IR gate deleted (K50's own defect) | §5, 4 of 7 cells |
| `ENG_ATTEMPT`'s continue deleted | §5, **exactly 1 of 7 cells** |

The last two firing DISJOINT cells is the matrix telling two mechanisms apart
rather than scoring one twice. Permanent rows: **S230** (IR gate), **S231**
(`ENG_ATTEMPT`), **S232** (deny-arm leak), **S233** (byte leak), each with
`SAB_REACH` from birth, plus the `startbnd` matrix arm registered before the
rows that name it (R31 C11).

---

## 5. The §5.5 throughput side-note — REFUTED, and it was worth measuring

The charter asks for §5.5's wasted-attempt claim to be re-measured "as the
fix's own throughput side-note", on the expectation that skipping mid-char
starts is *"also the OPTIMIZATION §5.5 called not optimal"*. **It is not an
optimisation.** Nine interleaved trials per cell (the box's known run-to-run
spread makes uninterleaved trials useless), gcc-16 -O2, M1, against a scratch
build of the same tree with the gate removed:

| route | witness | subject | gated vs ungated |
|---|---|---|---|
| `ENG_ATTEMPT` | `(?m)^zzz\|\bqqq` | 4,000 × 2-byte chars | **1.33× SLOWER** (10,450 vs 7,865 ns/search, no trial overlapping) |
| `ENG_ATTEMPT` | same | 4,000 × 4-byte chars | wash (15,468 vs 15,538 ns, 0.4%) |
| `ENG_UNANCH` | `\Bqqq` | 4,000 × 2-byte chars | wash (194.6 vs 195.6 ns, inside the spread) |

**The mechanism is a branch, not the skipped work.** The guard runs on EVERY
iteration and skips work on only some, and the work it skips is one seed
dispatch that dies immediately. On a 2-byte-character subject the guard's
branch alternates taken/not-taken every iteration — the worst case for a
predictor; on 4-byte it is taken 3 times in 4, more predictable and skipping
more, and the effects cancel. The DFA route pays nothing in TIME and pays in
SIZE: `\Bqqq`'s forward transition table grows 15 → 20 entries.

This changes nothing about the fix, which is a correctness fix paid for
whatever it costs. It changes the sentence, and §5.5's box now carries the
table so nobody cites it the other way.

---

## 6. THE FINDING I MOST WANT REVIEWED: the guard refused offset 0

Wiring the axis into `make test-axes` (charter (iii)) turned 21 oracle-verified
cells red across `tests/utf8/axis01`, `axis03` and `axis09` — `a` on the
one-byte subject `\x80` among them.

**The cause is a real asymmetry between pcrec and libpcre2, not a typo.** The
boundary predicate is LOCAL ("is this byte a continuation byte"), which is
exactly what libpcre2 asks under `PCRE2_UTF` — but libpcre2 asks it only AFTER
a whole-subject validation pass has already rejected an ill-formed subject
(§2.6(b)). **pcrec has no such pass**: ASK 1 rules that an ill-formed sequence
matches nothing, "no validation pass, no error return". So this guard sees
subjects libpcre2's never reaches, and on one that BEGINS with a continuation
byte the local test alone refuses offset 0 — turning "ill-formed input matches
nothing" into "ill-formed input is an error", which is that ruling inverted.

The guard gains `@P == 0 ||`. A caller naming offset 0 cannot have pointed
INSIDE a character, because none precedes it.

**MY OWN DIFFERENTIAL COULD NOT SEE IT**, and that is the second half of the
finding: none of its 9 subjects began with a continuation byte, so the guard's
treatment of offset 0 was unexercised. Two subjects added (`B161`, `8080`), the
driver's contract predicate gained the same clause — **it states the CONTRACT,
not what the backend implements**, which is the whole reason it is recomputed
there — and the floor moved 140 → 150. Re-validated: deleting the clause now
reds the sweep.

A second instrument defect surfaced the same way. **With a zero byte at
`s[n]`, the driver could not see a guard that reads past the end of the
subject** — a guard spelled without its end-of-subject arm read 4/4 GREEN.
The driver now parks `0x80` there.

---

## 7. Open questions for the manager

**(a) TWO `.rxt` FORMAT DECISIONS, which are yours under dd13b, not a lane's.**
Charter (i) asks for both-arm CELLS riding the `gu <code>` family. Neither half
is expressible today:

- `gu <code>` searches from **offset 0 only**, and offset 0 is always a
  boundary — so a refusal cell has no directive at all. It needs either a
  startpos-bearing give-up kind (`gus <P> <code> "<subject>"`) or a `<P>` on
  `gu`.
- **No directive spells a compile flag.** `flags` defines only `i`.

I did not invent either. The two affected cells (`axis09`'s
`midstart-row2`/`row4`) are PINNED in `run_startbnd_diff.sh` §6 with their
ruled values, and `axis09` carries a pointer at each block saying why it left
and what would bring it back. **If you rule the directives in, the blocks come
back and §6 becomes redundant** — that is the intended shape, not a permanent
arrangement.

**(b) `PCREC_ERR_STARTPOS = -7`, below the floor.** The consequence worth your
eye: §4's "composed call sites must trap below the floor" makes a composed site
trap on it. I think that is right — after this fix every engine-generated
position IS a boundary, so a composed callee seeing a non-boundary means the
engine broke its own rule — and no composed call sites are emitted today, so it
is a contract statement rather than a live trap. Overrule if you disagree.

**(c) THE `rx_info.flags` MASK IS NOW PER-ARTIFACT for this one bit.**
`PCREC_NO_STARTPOS_GUARD` joins `strategy_denials` **only where the encoding
restricts no position**. That is the mask's own rule (observable effect) applied
per artifact rather than a new rule — but it is the first conditional member,
and it is what makes the differential's §4 claim the strong one (a byte
artifact is BYTE-IDENTICAL under either setting, not merely guard-free).

**(d) The full battery is yours.** I ran the targeted suites named in §4 and
§8. `make test`, `make mech` (the four new rows have never run through the real
matrix, only as hand-planted edits), `make test-axes` in full, and the Linux
arm are all unrun here.

**(e) `make test-axes` full-corpus run is OWED.** I ran it scoped to
`tests/utf8` (which is where it found §6's defect) and the roster/derivation
cross-check on the whole tree (22 bits, matching `tuning.md`'s 22 documented
mentions). The FULL sweep needs to classify this axis's divergence population
under the harness's `refused-documented` vocabulary — I have not added that
classification, because the population to floor it against is a full-corpus
number I do not have. **This is the one charter item (iii) I have not
completed**, and it is the first thing to finish at merge.

---

## 8. Delivery-block results

Logs under the session scratchpad; the block ran with the tree settled and
nothing else touching `build/`.

> Filled in by the run whose log is
> `.../scratchpad/validate.log`; see §9.

---

## 9. Files

**Engine:** `src/gen/enc/enc.h`, `enc.c`, `enc_byte.c`, `enc_utf8.c`;
`src/core/internal.h`; `src/ir/nfa.c`, `dfa.c`; `src/opt/prefix_k.c`;
`src/gen/emit_dfa.c`, `emit_vm.c`; `lib/pcrec.h`; `cli/main.c`;
`src/parse/axes_dump.c`.

**Tests:** `tests/utf8/run_startbnd_diff.sh`, `startbnd_driver.c`,
`startbnd_engine_driver.c`, `axis11_startpos_boundary.rxt`,
`axis09_nextpos_findall.rxt`; `tests/known_fail/k50_utf8_dfa_midchar_start.rxt`
(deleted); `tests/mech/sabotages/S230..S233`;
`tests/mech/run_sabotage_matrix.sh`; `tests/rxtsource/run_rxtsource_tests.sh`;
`tests/codegen/run_recursion_identity.sh`, `run_codegen_tests.sh`; `Makefile`.

**Docs:** `docs/spec/match_api.md` (§3.1, §4, two abi sentences);
`docs/spec/tuning.md` (§1, new §2.23); `docs/design/utf8_design.md` (§5.5's
box, §2.6.1.1); `docs/dev/known_issues.md` (K50 → FIXED);
`docs/design/utf8_measurements/probes/probe_startbnd.py` +
`out/startbnd.txt`; four directory `CLAUDE.md`s.
