# START-SET — where can a match begin? (`[OPT-FIRSTSET]` + `[OPT-VMSEED]`, one mechanism)

**Status: PROPOSED, design only** (lane `startset`, 2026-10-05, from main
`a4c752a2`, abi 61). Round 2 of `[OPTLOOP]` under D144 addendum 3 ("design
before build"). Nothing under `src/`, `cli/`, `lib/` or `tests/` changed. The
instruments, the census and the hand-twin transcripts are in `startset/` (its
own `CLAUDE.md`).

**Process bar before any build (D122 addendum 4 item 3).** This changes the
SHAPE of `dfa_pfs[]` (it becomes engine-neutral and gains a VM consumer), so it
needs a FULL D6 panel with distinct lenses (answer soundness, selection/axis
semantics, the hybrid/VM consumer contract) before a line is built.

Ids used here: sabotage S478-S485, no K-row filed, D148 proposed (§9 Q1).

---

## 0. Findings first

1. **The census (D77) says the VM half is a FIRST-BYTE question, not a
   run-offset question.** The plan row frames `[OPT-VMSEED]` as "begin attempts
   at q − (the run's offset bound)". At abi 61, among the prefilter-less VM
   artifacts the `auto` route builds, a bounded necessary run exists on **0 of
   18** unanchored bench artifacts and **10 of 166** corpus ones. A narrowing
   AST start set exists on **17 of 18** and **59 of 166**. Under
   `--engine=vm` the run seed reaches 89 bench / 363 corpus artifacts, and
   **every one of them also has a narrowing start set** (`RUN_only = 0` on
   every population). So stage 1 is the start-set row. The run seed is
   stage 4, triggered by a measurement (§8).
2. **The re-seed is sound on the hybrid.** The brief carries the reading "re-seed
   unsound for hybrid". `firstset_design.md` §4.6.5 measured that NARROWING
   WITHOUT the re-seed deletes matches on the hybrid too; it did not test the
   re-seed there. Measured here on the real hybrid artifact
   (`RX_VM_PREFILTER "hybrid"`, captures on): `\b(ab|cd)\b` over 17,736,745
   (subject, startpos) cells, narrowed-no-re-seed **768 lost matches**,
   narrowed-with-re-seed **0**. The hybrid's inlined prefilter IS the DFA
   unanchored scan (`pcrec_emit_dfa_engine`), so `pf_emit_ofs_reseed`'s
   argument applies unchanged (§4.1, `startset/twin/hybtwin_out.txt`).
3. **The DFA hat reaches the CTX group as well.** Its movers (seeded machine,
   `T = S ∩ E ⊊ E`) are 18 bench / 58 corpus artifacts (9+9 / 46+12 DFA+hybrid).
   Besides five START-SET cells, they include **`level-context` and the four
   `ctx-*` hybrids**, the gap report's rank-2 CTX group (E 63 → T 3 bytes,
   d 77% → 1.1% / 6.7%). The plan row's do-not-regress
   `wild-logparse-quotedstring-grok` is NOT unchanged: it moves (E 4 → T 3).
4. **Six of the gap report's 14 START-SET cells are not start-set cells.**
   `asr-wb`, `asr-nwb`, `asr-b-ascii`, `stack-frame` (two cells) and
   `github-pat` already scan with an `offset-set[-bounded]` row, which
   re-seeds, and five of them gained the K82 handoff at abi 61, AFTER the gap
   report's pin. Neither hat moves them. Their residual is per-candidate cost
   and belongs to another group (§9 Q8).
5. **The independent control caught the census's own defect.** On an UNSEEDED
   DFA machine, the emitted escape set `E` must be a subset of the AST start
   set `S`. The first census run had 33 violations, every one a non-ASCII
   pattern: the driver passed `pattern.decode("latin-1")` as argv, and Python
   re-encoded it as UTF-8, so a different pattern was compiled. After the fix:
   **685 artifacts, 0 violations**. The failing-direction twin (drop one
   member of `S`) fires on all 685 (§6.2).
6. **A prior first-set analysis exists, reverted, at `a07a87c6`**
   (`src/opt/firstset.c`, `[OPT-ALTCLS]` stage 3). It was declined because
   its win was confined to `--engine=vm`. Its two REVISIT-WHEN triggers have
   both fired: VM-mandatory constructs landed (M6), and the bench shows
   default-route VM cells losing (`quoted-delim-match` ×21.5,
   `balanced-parens-rec` ×9.1, `bak-k-named` ×3.37). Its reasons for
   declining zero-width nodes do not carry over (§3.2).

---

## 1. The question and its population

**The question.** Given a position `p`, what is the next position `≥ p` where a
match could start? `compare_stack.md` calls this layer L3. It is the question
`dfa_pfs[]` already answers for the DFA (D122 addendum 4 item 2). D124 has one
table answer it for both emissions, with the engine as a row predicate and a
consumer hat.

**The two consumers.** They have different contracts (D124 item 3):

| hat | what it does with the answer | what it must get right |
|---|---|---|
| **DFA** (unanchored forward scan; the VM hybrid's inlined prefilter is the same emitted function) | re-enters its machine at the landing position | the machine's STATE after the jump. A `\b`/`(?m)^` machine carries the previous byte's class in its state (`firstset_design.md` §4.2, §4.6) |
| **VM** (prefilter-less attempt loop: `RX_VM_PREFILTER "none"`, at `auto` or under `--engine=vm`) | starts an attempt at the landing position | nothing is carried: every attempt re-reads its context (`\b`, lookbehind, `\G`) from the subject. What matters is that no successful attempt start is skipped |

**The census** (`startset/census.py` → `census.tsv`, `census_summary.txt`). It
is compile-only, on darwin at abi 61, at the bench's own `pcrec-auto` flags and
again with `--engine=vm`. The populations are every bench export (345, 321
compile) and every DISTINCT corpus pattern text (3,521, 3,147 compile; corpus
at byte encoding).

| population | bench | corpus |
|---|---|---|
| `auto` routes: dfa / hybrid / vm-none | 250 / 50 / 21 | 1,700 / 1,106 / 341 |
| **VM hat at `auto`**: vm-none, unanchored | 18 | 166 |
| … with a narrowing start set (FS) | **17** (8 singletons, 10 with ≤16 bytes) | **59** (47 singletons) |
| … with a bounded necessary run (RUN) | **0** | **10** |
| … RUN without FS | 0 | 0 |
| **VM hat under `--engine=vm`**: unanchored | 294 | 2,660 |
| … FS / RUN / RUN without FS | 273 / 89 / **0** | 2,263 / 363 / **0** |
| **DFA hat**: dfa or hybrid with a seeded machine | 30 | 140 |
| … that narrow (T ⊊ E) | **18** (9 dfa, 9 hybrid) | **58** (46 dfa, 12 hybrid) |
| … narrowed to one byte | 2 | 36 |

(`firstset_design.md` §4.6.3 counted 54 seeded-skip artifacts, 42 DFA and 12
hybrid, at its own pin; this census counts 58 narrowing ones.)

**Bench movers by hat** (density `d` = share of capability's `t-1m` subject in
the set; the sha256 is checked against the bench manifest):

- **DFA hat, 18 (`E` → `T`)**:
  - aws ×2 (63 → 1, d 0.17%);
  - json-constant (63 → 3, 7.9%);
  - dbnames (63 → 14, 22%);
  - bignum (63 → 10, 12%);
  - hex32-id (63 → 16, 32%);
  - level-context and four ctx-* (63 → 3, 1.1% / 6.7%);
  - quotedstring-grok/-noatomic (4 → 3, 0.57%);
  - syslogbase-expanded (63 → 16);
  - float-literal-bound (11 → 10);
  - kv-quoted (63 → 27, 57%);
  - wb-256/512 (63 → 26, 56%).
- **VM hat at `auto`, 17 (`S`)**:
  - quoted-delim (2, 0.57%);
  - balanced-parens-rec, rec-1, rec-name, rec-r-uc (`(`, 0.58%);
  - nested-comment-rec (`/`, 2.9%);
  - tag-pair-match, tag-depth3-bound, bak-k-named (`<`, ~0%);
  - phone-palindrome-6 (10);
  - six `\b(\w+)…\1` shapes (doubled-word, dup-param-detect, bak-1, bak-2,
    bak-g-rel, bak-py) plus mod-j-uc (63, 77%: dense, guard cells).
- **Not reached**: the three anchored VM-none patterns (`[OPT-ANCHOR-VM]` owns
  them: one attempt), and `cls-upto-32768` (nullable).

**Against the gap report's START-SET group** (18 cells; 14 distinct cells
named):

| cell | reached by | expected |
|---|---|---|
| aws-access-key-id thr (capability ×43.9, litrun ×5.31) | DFA hat (hybrid prefilter, `T = {A}`) | large: memchr-shaped scan at d 0.17% |
| json-constant thr (×2.12) | DFA hat | ×1.9 (F1's twin: 1.52-1.66 vs 3.09 ns/B) |
| dbnames thr (×1.82 re2), bignum thr (×1.16), hex32-id thr (×1.76 rust) | DFA hat | moderate; model §4.4 |
| quoted-delim thr (×21.5) + short (+99 ns, tier C) | VM hat | Mac scratch ×6.0 |
| balanced-parens-rec thr (×9.11) | VM hat | Mac scratch ×3.4 |
| bak-k-named thr (×3.37) | VM hat | the syntax subject is not local; owed |
| asr-wb, asr-nwb, asr-b-ascii, stack-frame ×2, github-pat | neither (already `offset-set` + re-seed; handoff at abi 61) | none; re-bucket (§9 Q8) |

---

## 2. The rows: one first-match table, two hats

**The table** stays `dfa_pfs[]`, built by implement-then-replace (D124 item 4).
- **Stage 1** generalizes the SELECTION VALUE and the ROW STRUCT in place:
  `DfaSel` gains a `route` and a `const StartSet *`, and `DfaPf` gains a VM
  hook and the K84 scan field.
- **The rename** (`dfa_pfs[]` → `cand_rows[]`, `DfaPf` → `CandRow`) is a
  separate no-mover commit, and is Q2.
- **The memory rule binds**: decisions are first-match predicate-row tables.
  `dfa_select` walks the list; the first row that applies and is not denied
  executes.

```
row                    deny                          DFA predicate                         VM predicate                    DFA hat (emit, reseeds)        VM hat
---------------------  ----------------------------  ------------------------------------  ------------------------------  -----------------------------  -----------------------
run-pinned-bounded     OFFSET_SKIP|RUN_PREFILTER     (today)                               never (needs the NFA k-sets)    (today) ofsskip, yes           -
run-pinned             OFFSET_SKIP|RUN_PREFILTER     (today)                               never                           (today) ofsskip, yes           -
offset-set-bounded     OFFSET_SKIP                   (today)                               never                           (today) ofsskip, yes           -
offset-set             OFFSET_SKIP                   (today)                               never                           (today) ofsskip, yes           -
first-memchr-bounded   START_SET  (NEW)              F ∧ views ∧ |T| = 1                   never (no view concept)         memchr(T), yes                 -
first-memchr           START_SET  (NEW)              F ∧ |T| = 1                           V ∧ |S| = 1                     memchr(T), yes                 memchr(S) seek
first-class-bounded    START_SET  (NEW)              F ∧ views                             never                           class loop(T), yes             -
first-class            START_SET  (NEW)              F                                     V                               class loop(T), yes             class loop(S) seek
memchr-bounded         0                             (today)                               never                           (today), no                    -
memchr                 0                             (today)                               never                           (today), no                    -
byte-class-bounded     0                             (today)                               never                           (today), no                    -
byte-class             0                             (today)                               never                           (today), no                    -
none                   0                             always                                always                          nothing                        today's attempt loop
```

**F** (DFA, forward machine, unanchored body):
- the machine is SEEDED (`dfa_needs_seed`);
- the start set `S` is a necessary condition: not nullable, and `|S| < 256`;
- `T = S ∩ E` is a PROPER, non-empty subset of `E`, where `E` is today's
  `us.cand.set`.

Where `T == E` the four new rows are transparent and every artifact is
byte-identical (S1's prepend argument, `litscan_s1.md` §1.2). On an UNSEEDED
machine `E ⊆ S` (§6.2), so `T == E` and nothing moves by construction.

**V** (VM): all of the following must hold.
- **Route**: the artifact's VM route has no `prefn`, at `auto` or under
  `--engine=vm`. A hybrid's prefilter takes the DFA hat.
- **Anchoring**: `start_anchor == unanchored`. An anchored or `\G`-start
  pattern runs one attempt (`[OPT-ANCHOR-VM]`).
- **Necessary set**: `S` is not nullable and `|S| < 256`.
- **No verb or callout**: the same fact k82h §1.4 (g) reads. Today this is
  structurally unreachable (§3.3).
- **Encoding**: under a multibyte encoding, every member of `S` is a
  character-start byte by the encoding BACKEND's predicate, never a spelled
  range (DD-12 (7)). Today this is an ASSERTION, not a decline (§3.4).
- **Not denied**: `-fno-start-set`.

**Why the new rows sit below the offset rows and above the plain ones.** An
`offset-set` or `run-pinned` row already answers the question with more
information (a k-set conjunction or a verified run). It also already
re-seeds. On the 6 "not reached" gap cells above it is selected today and
stays selected. The new rows replace exactly the plain `memchr`/`byte-class`
rows, and only where those scan a context-carrying set that is wider than the
start set. Ordering by information is the existing table's own principle. It
is not a cost comparison (D146).

**One deny, both hats** (`-fno-start-set`, `PCREC_NO_START_SET`, the next free
bit 47, in `strategy_denials`). The deny names the mechanism, not an engine,
as `litscan_s1.md` §1.5 item 3 rules. So test-axes proves both hats against
one arm. **No force flag** is proposed (Q3). Most optimization axes are
deny-only (`axes.def:106`), and "force a first-set row over an offset row"
would be a selection override with no measured customer.

---

## 3. The fact: the AST start set

### 3.1 Definition and owner

`start_set` is a NEW CORE fact in `src/facts/` (PATFACTS, D126). Its owner is a
new `src/facts/startset.c` and its epoch is E2, beside `nullable`/`req_set`.
It is computed on the LOWERED tree (after `pcrec_lower_enc`), so every
`A_CLASS` is a byte class, and it is consumed by both hats. Its value is a
256-bit set plus a `nullable` bit. `--emit-facts` gains one row, `start_set`,
whose value is the popcount and the hex set, or `all` when nullable or full.

The walk (the census probe `startset/fs_probe.c` is this table, minus the
record plumbing):

| node | FIRST | nullable |
|---|---|---|
| `A_CLASS` | its bytes (`pcrec_cls_bits`) | no |
| `A_CAT l r` | `F(l) ∪ (null(l) ? F(r) : ∅)` (iterative spine; K20) | both |
| `A_ALT` | union | either |
| `A_REP {m,…}` | the body's | `m == 0` or the body's |
| `A_CAP`, `A_ATOMIC`, `A_WCLASS` | the child's | the child's |
| zero-width: `A_EMPTY A_BOL A_EOL A_END A_CTX A_GSTART A_KRESET A_LOOK` | ∅ | yes |
| `A_BREF`, `A_CALL`, `A_VAR` | all 256 | yes |

The switch has no `default:` (mrl.c's rule). A future kind, such as a built
`(*ACCEPT)` or a conditional, is a COMPILE ERROR here, which is the alarm we
want.

### 3.2 Soundness: why zero-width nodes are ∅ here and "all bytes" in possessify

The claim is that every successful attempt at `p` that consumes at least one
byte consumes `s[p]` first, and `s[p] ∈ S`.

- **Zero-width nodes.** Each consumes nothing and constrains which strings
  match. Replacing it by ε admits a SUPERSET language `L⁺ ⊇ L`. `S` is the
  first-byte set of `L⁺`, so it is a superset of `L`'s first bytes. If `L⁺`
  is not nullable, `L` is not either. That is the whole argument for `\b`,
  `\B`, lookaround, `^`, `$`, `\z`, `\G` and `\K`.
  - Under `\K` the reported start moves, but the ATTEMPT start (the position
    the skip moves) does not.
  - `\G` reads `search_from`, which neither hat changes (k82h Claim 2′).
- **Backreferences, calls and variables** are "all 256, nullable". That is the
  conservative answer; the callee's FIRST set is a later refinement with no
  measured customer.
- **The prior designs drew the line differently, and for their own consumer.**
  - `possessify.c` widens `A_LOOK` to all-bytes because its FIRST feeds a
    follow-set DISJOINTNESS test in which a gate inside a retreat path
    matters (its §2.5 refutation).
  - `a07a87c6`'s `firstset.c` declined `^`/`$` on possessify's precedent, and
    its own header calls that caution "matching precedent".
  - The start set is not reasoned about inside a retreat. It is the first
    consumed byte of a whole attempt, so the superset argument above is
    complete.
- **Why possessify's walk is not reused.** It runs ABOVE the encoding lowering,
  on code points, and widens out-of-byte-range classes to all bytes. The start
  set must be on the lowered byte tree. Different tree level and different
  zero-width policy make it a different question (Q4).

### 3.3 Verbs and callouts

The hazard is k82h §1.4 (g). A FAILED attempt below the next candidate that
runs `(*COMMIT)` can end the whole search under PCRE2, so skipping it would
turn a NOMATCH into a match. Today `(*COMMIT)`, `(*PRUNE)`, `(*SKIP)`,
`(*THEN)` and `(*MARK)` are "outside pcrec's scope", and `(*ACCEPT)`,
`(*FAIL)` and `(?C…)` are unbuilt (measured: each refuses at compile). The V
predicate reads the same verbs/callouts fact as k82h's (g) and
`[OPT-HYB-RESEED]`'s decline, never a second spelling of it. Its sabotage row
ships declared UNREACHED with a compile-time assertion beside it (S475's
precedent).

### 3.4 Encoding

Under `-e utf8`, `S` is computed on the lowered tree, so its members are the
lead bytes of the characters a match can begin with. That makes the VM hat's
landing a character start on any subject:
- **Well-formed text**: a non-continuation byte is a character start.
- **Ill-formed text** (K73/K75): a match never starts on a continuation byte,
  and every other byte is a legal attempt start.

**Census.** 0 of the 76 utf8-set artifacts have a continuation byte in `S`;
the 14 bench rows that do are byte-encoding sets, where the question does not
arise. So the conjunct is a `pcrec_ctx_fail` assertion.
- **The predicate asked** is "every member of `S` satisfies the backend's
  start predicate", phrased through the encoding seam.
- **Construction**: no spelling in the shipped grammar produces a
  continuation byte in `S` under utf8. A class `[\x80-\xbf]` is the code
  points U+0080-U+00BF, which lower to the lead byte C2.
- **Sabotage**: its row ships UNREACHED (S483).

The DFA hat needs no conjunct: under utf8 the machine already steps characters,
and the re-seed reads the class of `s[landing − 1]`, which the entry seed reads
at any startpos (§4.1).

---

## 4. Soundness per row and per hat

### 4.1 DFA hat: the narrowed rows re-seed, and why that is enough

**The invariant.** Each step below reads emitted code, not the design.
1. The skip runs only while `forward_state == 0` and
   `last_accept_position == -1` (the emitted gate). State 0 means "no live
   thread except the fresh start thread, in the start context". Nothing
   partial is in flight, so nothing is lost by moving.
2. A byte `b ∉ E` read in state 0 leaves the machine in state 0. A byte
   `b ∉ S` cannot begin a match at its position. So every position skipped
   with `b ∉ T = S ∩ E` begins no match.
3. After skipping `[p, q)`, the true state equals the state the entry
   initializer computes at a startpos of `q`:
   `seed[class(s[q−1])]` (`emit_dfa.c`'s entry line). That is because the
   only thing the skipped bytes leave behind is the class of the last one.
   This is the SAME premise every caller startpos already relies on
   (`match_api.md` §3.1, k82h Claim 3). The every-startpos identity sweeps
   (`tests/utf8/run_startbnd_diff.sh`, the identity gates) test it today.
   - **On a multi-byte context**, the premise would already be false at the
     entry. `pf_emit_ofs_reseed` makes the same assumption for `[OPT-K]`.
4. So the re-seed is `pf_emit_ofs_reseed(c, f, ind)` called from the new rows'
   emitters, with `reseeds = true` on all four rows. It is a second and third
   call site of an existing primitive, not a mechanism
   (`firstset_design.md` §4.6.4).

**The views (`-bounded`) twins** mirror `memchr-bounded`/`byte-class-bounded`:
- the skip stops at `n − 1`;
- there is no early `return 0`;
- both landing paths re-seed (`pf_emit_ofs_bounded`'s shape).

**The hybrid.** Its `static <p>_prefilter` IS this emitter's output, so the
proof carries over. Two hybrid-only readings:
- **The window's start is a lower bound** (P5, `emit_dfa.c:5454`). A narrowed
  scan never skips the true first start `p*`, so the reverse pass returns a
  start `≤ p*`. On an `exact` prefilter it returns `p*` itself.
- **On a COUNT-COLLAPSED prefilter** (`L′ ⊋ L`, the ctx-* movers) the scan
  skips positions where an `L′`-only match could begin. The reverse pass may
  then return a start below `q` (an `L′`-match that began in the skipped
  region and ends where the forward scan stopped).
  - **Why that is still sound**: the VM verifies, and the start is still `≤ p*`.
  - **Why the window END does not matter there**: `mrl_win` is false on every
    count-collapsed hybrid (H3), so no ceiling is read from it.
  - **The obligation**: the build must include ≥1 count-collapsed hybrid mover
    in its differential (the ctx-* family).

**Measured** (`startset/twin/`, every subject over the alphabet up to the
length shown, every startpos, the full capture vector; tw = narrowed without
the re-seed, rs = narrowed with it):

| pattern | route | `\|E\|` → `\|T\|` | cells | tw lost | rs diffs |
|---|---|---|---|---|---|
| `\b(ab\|cd)\b` | hybrid | 63 → 2 | 17,736,745 | **768** | **0** |
| `\b(?:ab\|cd)\b` | dfa | 63 → 2 | 17,736,745 | **768** | **0** |
| `\b[0-9]{2,3}\b` | dfa | 63 → 10 | 757,305 | **1,024** | **0** |
| `\b(?:true\|false\|null)\b` | dfa, hybrid | 63 → 3 | 17,736,745 each | 0 | 0 |

The last row reads 0 lost because of REACH: its minimal witness is 10 bytes and
the sweep stops at 8 (`firstset_design.md` §4.6.2's own finding). Every lost
match is the §4.6 shape: a word byte before the keyword, and a real match
later.

### 4.2 VM hat: skipping attempts that cannot succeed

**The argument.** An attempt at `p` succeeds only if `s[p] ∈ S` (§3.2, since
`S` is not nullable).
- **Entry.** Seeking `attempt_position` from `search_from` to the first byte in
  `S` skips only failing attempts.
- **Retry.** After a failed attempt and the encoding's own advance (K49's
  `retry_adv`, unchanged), seeking again skips only failing attempts.
- **Every start rule is preserved.** `\G` reads `search_from`, which is
  unchanged. The K73 offset-0 SEEK runs before the seed. The end-window clamp
  and the K65/K66 pre-checks run above it. `[OPT-ANCHOR-VM]`'s `attempt_max`
  is moot, because the predicate requires `unanchored`.
- **No candidate.** If the seek reaches `subject_length`, the answer is
  `return 0`. No attempt at `n` can succeed, because the pattern is not
  nullable.

**The contract to the VM consumer (D124 item 3, the K64 lesson).** The hat
removes only attempts that FAIL, so the per-call step and work meters can only
DECREASE.
- **The consequence**: a call that returns `PCREC_ERR_STEPS` with the deny flag
  may return the unbounded-budget answer without it. It is never the reverse.
- **Why it is observable**: k82h's r1 C-C8 finding is that "unobservable by the
  contract" is false for the give-up surface.
- **Reach**: **11 of the corpus's 35 budget/`gu` blocks are VM-hat movers**
  (`tests/litscan/reqcube.rxt` ×6, `k66_precheck_whole_run.rxt` ×2,
  `k65_precheck_whole_set.rxt` ×3; `[a-z]`-led, `|S|` = 26).
- **What follows**: the spec sentence and the allowance below are REQUIRED,
  not hypothetical. The build re-runs those 11 blocks, and a give-up may become
  only the answer that the deny arm returns at an unbounded budget. Every other
  change is a defect.

**Measured** (`startset/twin/vmtwin_out.txt`, the same harness): every
(subject, startpos) cell compared on the full capture vector. A skip twin
patched at the entry and at the end of the attempt loop, after the encoding
advance:

| pattern | flags | `\|S\|` | cells | diffs |
|---|---|---|---|---|
| `\((?:[^()]\|(?R))*\)` | auto | 1 | 280,483 | 0 |
| `(["'])(?:(?!\1)[^\\]\|\\.)*\1` | auto | 2 | 757,305 | 0 |
| `<(?<t>\w+)>[^<]*</\k<t>>` | auto | 1 | 14,913,081 | 0 |
| `\b(\w+)\s+\1\b` | auto | 63 | 757,305 | 0 |
| `x*(a)\1` (nullable prefix) | auto | 2 | 20,481 | 0 |
| `(a+)x\1catdog` | auto | 1 | 2,054,353 | 0 |
| `\Bcat\B`, `(?i)cat`, `(?:\Ga\|b)c`, `a\Kb`, `\b(?:true\|false\|null)\b`, `(?<=a)b(c)` | `--engine=vm` | 1-3 | 20k-2.6M each | 0 |
| `(?i)café`, `(?i)straße` (`S` holds the `ſ` lead byte C5) | `--engine=vm -e utf8` | 2, 3 | 1.17M, 4.89M | 0 |
| **CONTROLS: one member dropped** — quoted-delim `'`, `(?i)cat` `c`, `(?i)straße` `s` | | | | **150,977 / 2,824 / 1** |

The `straße` reach is thin (3 matching cells), and the controls show it can
fail.

### 4.3 Cross-row facts each hat must leave alone

- **`pcrec_artifact_has_dfa_scan(cx)` stays FALSE on a VM-hat artifact.**
  K65/K66's no-DFA pre-checks, G1's dominance and the K82 handoff's (a) all key
  on it. The VM hat is not a DFA scan. Flipping the predicate would elide the
  linear no-match proofs that K65/K66 exist for, which is the K64 shape
  exactly. This is a build assertion and sabotage S484.
- **The `reseeds` field stays a static row property.** Its one consumer,
  `src/opt/scanedge.c` precondition (8), forbids a chain head that is a seed
  target on a machine whose prefilter re-seeds. On DFA-hat movers that
  condition becomes true, so **scan-edge selections may move on them** (a
  SECOND mover class). The build's mover census reports it.
- **K84 is fixed first (stage 0).** Two readers classify the row by `strcmp`
  on its name:
  - `dfa_cand_scan`, for G1's single-byte dominance;
  - `pcrec_dfa_cand_ppm`, for `[OPT-HYB-RESEED]`'s candidate density.

  A `first-class` row would be priced at 1,000,000 ppm and escape G1 silently.
  The fix gives the row a field `scan` ∈ {`OFS`, `BYTE`, `SET`, `NONE`} plus
  the set it scans (`E` or `T`), and both readers test the field. That moves
  no byte today (K84's own fix shape). After stage 3 the readers see the
  NARROWED set, which yields two more mover classes:
  - **G1**: a hybrid or DFA mover whose `T` is the single byte its REQ_BYTE
    pick names may have its pre-check elided as dominated;
  - **`[OPT-HYB-RESEED]`**: a hybrid mover's candidate ppm (the prior's MASS
    over the scanned set, `pcrec_find_set_ppm`, not a subject density) drops
    from the 63-byte word class's to one byte's (aws), so its re-seed row may
    move from `adaptive-dense` to `adaptive`/`fixed`.

  The build's census reports all three classes (prefilter row, `REQ_WHY`,
  re-seed row).

### 4.4 Cost model (the DFA hat), and why there is still no decline rule

`firstset_design.md` §3 is used unchanged:
- per-byte cost is `(L·b + w·a + c)/(L+w)` with `L = (1−d)/d`;
- `a = 3.21` and `b = 0.84` ns are measured on Linux (I-85);
- its derivative in `L` is negative for every admissible value.

F1 (O-46) refuted the one contradicting measurement and RETIRED the decline
rule. The re-seed adds one lookup per skip exit that actually skipped (F3, the
owed cost of the repair, §7). The `first-memchr` form takes aws from a
byte-class loop at d 0.17% to a `memchr`. The pair filter
(`firstset_design.md` §6) remains `[WORD-FOLD]`/S4 territory and is not
absorbed.

**The VM hat has no model** and needs none. A skipped position costs a table
read or part of a `memchr`. A non-skipped one costs what it costs today, plus
one byte test. The one regime where the hat could LOSE is a dense
single-byte `S` read by `memchr` per failed attempt:
- the call entry (~5 ns, `cycle2_batch2_reading.md` §4.1's `c_call`) is paid
  on candidates 1-2 bytes apart;
- that is a FORM choice inside a delegated site, which is the kit's under D146
  (§5);
- the alpha carries a dense-candidate guard cell (§7).

---

## 5. Consumers, sites and the [MEMFN] manifest (D146/D147, integration.md rev 4.4)

| site | today | change | manifest (`tests/memfn/site_manifest.tsv`) |
|---|---|---|---|
| T1 PF (`pf_emit_memchr[_bounded]`, `pf_emit_bcls[_bounded]`): the DFA unanchored skip, and the hybrid's inlined copy | FIND over `E` | the DFA hat: the same emitters called with `T`. The OPERAND changes, the site does not. The re-seed line after it is pcrec's (§8.5: "state writes stay pcrec's") | no new row. The existing T1 PF rows cover it (pending until M1/M2) |
| **VMSTART** (NEW): the VM attempt loop's entry and retry seek | none (step one position) | FIND over `S` from `attempt_position`, handoff = the VM attempt start, D91 budget 1 (called per failed attempt, as the hybrid's retry prefilter is) | **a NEW row, `pending`, migrating with T1 PF's step**, because it renders through the SAME primitive. If C17 exists at landing, the row lands in the same commit, or C17's static half fails (a `memchr(` in an `emit_vm.c` function no row names) |

**One spelling (D122, C17 rule 3).** VMSTART must not spell its own loop.
- **Stage 2 extracts** `pf_emit_bcls`'s inner `while (…&& !<p>_<set>[subject[pos]]) pos++;`
  and `pf_emit_memchr`'s call into ONE emitter, parameterized by position
  variable, bound and table name. It has two callers, and the DFA's text stays
  byte-identical (the identity gates are the check).
- **What crosses to the kit, and when.** pcrec decides the row semantically
  (`|set| == 1` selects `memchr`, as today). It does no cost comparison and
  carries no architecture knowledge. When T1 PF migrates, both sites migrate
  together and the FORM (memchr, a table loop, a SIMD set classifier, a
  short-span loop-free path) becomes the kit's choice.
- **D147 addendum 4.** At M5 "the reseed becomes unconditional". The DFA hat's
  rows already re-seed unconditionally, so they need no change at M5.

---

## 6. Axis, stamps, sabotage, checks

### 6.1 Axis and stamps

- **Axis.** `-fno-start-set` / `PCREC_NO_START_SET`, bit 47, one `axes.def`
  row, in `strategy_denials` from its first commit. That is the
  `-fno-req-run` lesson: a bit outside the mask moves `rx_info.flags` bytes on
  non-movers.
  - **Under the deny**, `T` is never computed into an emitted table and the VM
    loop steps as today.
  - **The deny arm is today's emitter**: byte-identical on every artifact,
    and that IS the control.
- **DFA hat stamp.** The existing `<PREFIX>_DFA_PREFILTER` value moves on
  movers (four new values). There is no new stamp. Every reader of that value
  set is found BY GREP at landing:
  - `stamps.py`/`gapconfig`;
  - the bench's own scripts (relayed);
  - `match_api.md`'s value table;
  - the tests that enumerate it (S1 found a reader class this way).
- **VM hat stamp.** A NEW movers-only stamp, `<PREFIX>_VM_START_SCAN`, whose
  value is the row name (`"first-memchr"` / `"first-class"`). It goes on
  movers only, for k82h Q3's reasons.
  - **`RX_VM_PREFILTER` keeps its meaning** ("a DFA prefilter: hybrid/none")
    and its values.
  - **Why not re-spell it**: a re-spelling would move every VM-hat artifact's
    `"none"`, and readers grep that value (the gap report's causes, the bench's
    program-identity census).

### 6.2 The independent controls (standing question 2)

| check | subject | checked against | independent because |
|---|---|---|---|
| **C-SS (the fact's own control)** | `start_set` (the AST walk) | the emitted escape set `E` of every UNSEEDED DFA/hybrid machine: `E ⊆ S` must hold | `E` comes from subset construction over the NFA, and the walk shares no code with it. **Measured: 685 artifacts, 0 violations. The drop-one twin fires on all 685. The first run's 33 violations were the census's own argv defect, found by this check** (`summarize.py`) |
| answer identity, both hats | the built artifact | the `-fno-start-set` arm (today's emitter), every corpus pattern × every startpos × {auto, `--engine=vm`, `--no-captures`} | the deny arm never reads `start_set`. It is the pre-change program |
| oracle | the built artifact | the committed libpcre2 store (C3) and the corpus `.rxt` expectations | external |
| mover biconditional (K35) | the emitted text (`_VM_START_SCAN` present / `DFA_PREFILTER` changed) | the census predicate F/V recomputed by `census.py` from facts and stamps | the counts come from two derivations. The census is the denominator and the build reports both |
| give-up surface | the 11 `gu`/budget blocks in reach | the deny arm at an unbounded budget | the deny arm is the reference |

### 6.3 Sabotage rows (numbered after the highest S on main at landing; S477 today)

| id | plant | detector | witness (REACHES its site, [MECH-REACH]) |
|---|---|---|---|
| S478 | the VM hat's emitted set drops one member | answer identity | new `tests/startset/vmhat.rxt`: quoted-delim with a `'`-quoted subject (twin: 150,977 diffs) |
| S479 | the DFA hat's re-seed deleted | answer identity | new `tests/startset/dfahat.rxt`: `\b(?:ab\|cd)\b` on `bab ab` → (4,6), and `atrue true` (firstset §4.6's witness; twin: 768 lost). **The bench subjects are structurally blind** (`matches=0` either way), so the fixture is the only reach |
| S480 | `T` widened by one byte that cannot begin a match | a codegen check: on every DFA-hat mover the emitted table must EQUAL `start_set` (the `--emit-facts` row) ∩ the `-fno-start-set` arm's emitted table. The plant sits in the emission step, after the fact, so the two derivations disagree. It is not answer-visible: cost only (firstset §9) | the aws-shaped fixture, `\|T\|` = 1 |
| S481 | the `A_CALL` arm returns ∅ (drops its bytes) instead of all/nullable | answer identity (VM hat) | `(?1)x(y)` **under `--engine=vm`** on `yxy` → (0,3) (verified on this build; the bench's `rec-fwd` shape). With the correct fact `S` is all 256 and the row does not fire; the plant makes `S = {x}` and the seek skips position 0. At `auto` the pattern is a hybrid, so the fixture pins the engine |
| S482 | V's non-nullable conjunct removed | answer identity | `a*b?` **under `--engine=vm`** on `zz` → (0,0) (verified; at `auto` it is a DFA artifact) |
| S483 | the utf8 start-byte assertion removed | none possible. The population is empty by construction (§3.4) | **declared UNREACHED**, with a compile-time assertion beside it (S475's precedent) |
| S484 | `pcrec_artifact_has_dfa_scan` returns true on a VM-hat artifact | K65/K66 `gu`/NOMATCH cells | `tests/base/k65_precheck_whole_set.rxt` (a VM-hat mover, §4.2) |
| S485 | `pcrec_dfa_cand_ppm` re-reads the row NAME (K84 regression) | the re-seed row stamp on a hybrid mover | the aws hybrid fixture |

Each row's `SAB_REACH` is born with it (opt5 §5's discipline).

---

## 7. Alpha plan (D144 + addendum 3) and the landing bar

**Per change** (each stage below is its own commit and its own alpha):
- `make test`;
- test-axes over its own flag (`AXES="-fno-start-set"`), both engines;
- its own mech rows;
- **an ASan/UBSan pass over its own movers**, because both hats change how
  emitted code reads memory. The VM hat adds a subject scan. The DFA hat adds
  the re-seed's `subject[q−1]` read, which is guarded by `q > entry`;
- the targeted Linux timing: `taskset`-pinned, via the executor channel, with
  base against deny as the noise floor (D144 addendum 1). Short-call cells are
  absolute deltas against that floor.

**Landing bar: IMPROVE** (D119's measured-gap bar on each named cell):

| hat | cells |
|---|---|
| DFA | capability aws thr; litrun aws thr; json-constant thr; dbnames thr; loglines bignum thr; hex32-id thr |
| DFA, secondary (the CTX group) | level-context thr + short; ctx-lazy-64/256/1024 and ctx-greedy-256 thr |
| VM (auto) | quoted-delim thr (+ short, tier C absolute); balanced-parens-rec thr; bak-k-named thr |
| VM (`--engine=vm`, the pcrec-vm testee) | mod-i, mod-r, cls-fold-pair, cls-pair-ctl, ci-strasse thr (K82's forced-VM losses, +0.64..+2.02 ns/B); aws forced-VM (Mac scratch ×12.2) |

**DO NOT REGRESS**:
- **Non-movers** (program-identical, the null band): floor-byte thr/srch,
  high-byte-run thr, uuid-near-miss srch, union-select, ci-ascii-control.
- **Movers expected flat-to-better**: wild-logparse-quotedstring-grok thr (it
  moves: 4 → 3 bytes), kv-quoted, wb-256/512 (d 56-57%).
- **Dense-`S` VM guard cells**: doubled-word, bak-1 (`|S|` = 63); one
  dense SINGLE-byte VM-none cell (constructed, e.g. `e(\w)\1` on prose) for
  the per-attempt `memchr` entry (§4.4).
- **A pre-check-dominated VM mover**: nested-comment-rec, where FREQPICK's
  absent `*` answers first, so a null result is expected.

**Mac scratch, directional only** (`startset/twin/tdrv.c`, find-all on
capability `t-1m`, M1, gcc-16 -O2, best of 5, answers checked equal):

| pattern | base | VM-hat twin | |
|---|---|---|---|
| quoted-delim-match | 3.304 ns/B | 0.555 | ×6.0 |
| balanced-parens-rec | 2.376 | 0.696 | ×3.4 |
| aws `--engine=vm` | 4.441 | 0.365 | ×12.2 |
| `(?i)cat`, `c[aA]t` (`--engine=vm`), bak-k-named | — | — | ×1.0: the K65 pre-check answers first on this subject (no `cat`, no `</`). Their cells are the syntax set's own subjects (not committed); Linux alpha owed |

**Owed measurements**:
- **F3** (the re-seed's cost). It is folded into the DFA hat's alpha: deny
  against base on json-constant and aws.
- **F4** (firstset §7). This is the VM hat's alpha above.

---

## 8. Staged build plan (implement-then-replace, D124 item 4)

| stage | content | movers / abi |
|---|---|---|
| 0 | K84's fix: the row's `scan` field, both readers re-pointed | none (byte-identity gates) |
| 1 | the `start_set` core fact (`src/facts/startset.c`, `--emit-facts` row, C-SS as a check in `tests/`); `DfaSel`/`DfaPf` gain `route`, the `StartSet` pointer and the VM hook slot (NULL); the shared FIND-loop emitter extracted from `pf_emit_bcls`/`pf_emit_memchr` | none (the identity gates; `--emit-facts` is a debug listing, `docs/spec/facts_listing.md` gains its row) |
| 2 | **VM hat**: rows `first-memchr`/`first-class` with V and the VM hook; `-fno-start-set` (bit 47); `<PREFIX>_VM_START_SCAN`; VMSTART manifest row; S478, S481-S484; fixtures; the give-up spec sentence | auto 17 bench / 59 corpus, forced 273 / 2,263; **abi event** (next number) |
| 3 | **DFA hat**: F on the four rows, `-bounded` twins, the `pf_emit_ofs_reseed` call sites; S479, S480, S485; F3 | 18 bench / 58 corpus, plus the scan-edge, G1 and re-seed-row classes (§4.3); **abi event** |
| 4 (filed, TRIGGERED) | VM run seed: `req_uses[]`'s `handoff` (a) widened to the no-DFA VM entry, plus a `run-seed` row for retries (a cached `q`, `lo = max(p, q − K)`); [OPT-REQPOS] tier 2's VM instance, k82h Q7 | **trigger**: stage 2's alpha leaves any K82 forced-VM cell past the floor above its pre-C3 level. The census shows it never applies without stage 2's row already applying |
| 5 (filed) | offset-k sets from the AST (the VM's `offset-set` analogue, no NFA); `[ENG-TACTICS]` (b)/(c); the pair filter | each D77, no customer measured |

Stages 2 and 3 can swap: either is a complete hat on its own. The recommendation
is VM first, because it serves the round's named `[OPT-VMSEED]` population and
has no reseed hazard. The DFA hat follows with F3 measured in its own alpha.

**abi ritual (D76/D94), per mover stage.**
- `PCREC_ARTIFACT_ABI` goes to the next number at landing, never a literal
  here.
- **Readers found by grep today**:
  - `src/gen/emit_dfa.c:52`;
  - `tests/codegen/run_codegen_tests.sh:3021` (`ABI_EXPECT`);
  - `docs/spec/match_api.md` (the abi sentence, the `#error` example at :302,
    the change log);
  - the identity gate's (B) pin;
  - the byte-count reader class (size tripwire pins, `run_cpset_structure.sh`
    re-records).
- Then `make test-codegen`, then the suites that count (registry, codegen,
  rxtsource).

**Spec hunks (D80, same change).**
- `tuning.md` gains the axis.
- `match_api.md` gains:
  - the `_VM_START_SCAN` stamp;
  - the four `DFA_PREFILTER` values;
  - the §3.1 give-up sentence (k82h's sentence, generalized: "positions a
    start-set or necessary-literal proof excludes consume no budget; a search
    that gives up with `-fno-start-set` may return the answer an unbounded
    budget returns").
- `facts_listing.md` gains the row.

---

## 9. Questions for Frank (with recommendations)

**RULED 2026-10-05 (Frank): all nine as recommended — D148** (docs/dev/decisions.md). The D6 panel (review r4) runs before stage 0 and may revise this note.

- **Q1. Rule the shape as D148?** The shape: one candidate-finding table, a
  start-set fact, two hats, one deny. **Recommend YES**, then a FULL D6 panel
  (D122 addendum 4 item 3) before stage 0.
- **Q2. Rename `dfa_pfs[]` → `cand_rows[]` (`DfaPf` → `CandRow`, `DfaSel` →
  `CandSel`)?** **Recommend YES, as its own no-mover commit after stage 3**,
  not before. A rename mid-build makes every stage's diff unreadable.
- **Q3. A force flag?** **Recommend NO** (deny-only, the
  `-fno-run-prefilter`/`-fno-req-handoff` precedent). "Force" has no meaning
  for a row that applies wherever its predicate holds, other than overriding
  the offset rows, which no measurement asks for. This departs from the "deny
  AND force" memory wording, deliberately.
- **Q4. Unify with `possessify.c`'s `first_of`?** **Recommend NO**: different
  tree level (code points versus lowered bytes) and different zero-width
  policy (§3.2). Record it in PATFACTS' inventory as two facts with two
  questions, not a redundancy.
- **Q5. VM hat before DFA hat?** **Recommend YES** (§8).
- **Q6. The give-up allowance.** **Recommend accepting it** as the spec
  sentence in §8: a give-up may turn into the unbounded answer, never the
  reverse. Its population is 11 corpus blocks, measured.
- **Q7. An early batch gate?** D144 addendum 3 allows one for "a
  shared-mechanism change with a large cross-engine mover population".
  **Recommend NO.** The `auto` population is small (76 + 117 artifacts across
  both hats). The large population is `--engine=vm` (2,263 corpus), which the
  per-change test-axes sweep of `-fno-start-set` × `--engine=vm` covers.
- **Q8. Re-bucket the six non-start-set cells** (asr-wb, asr-nwb, asr-b-ascii,
  stack-frame ×2, github-pat) out of START-SET in the next gap report's
  `causes.tsv`, after the bench re-measures at abi ≥ 61 (the handoff moved
  five of them)? **Recommend YES.** The next gap-report lane reads them; this
  lane does not edit the report.
- **Q9. Stage 4's trigger** as stated (a K82 forced-VM cell still past the floor
  after stage 2)? **Recommend YES.**

---

## 10. The standing questions (docs/design/CLAUDE.md)

**1. Measurement regime: RELEVANT.**
- **Census counts**: compile-only, darwin, abi 61, regime-free.
- **Densities**: one subject (capability `t-1m`, throughput regime, prose-like
  text). A log or JSON subject moves `d`, not the sign.
- **The cost model's `a`/`b`**: Linux Ryzen, gcc-15, I-85, throughput,
  dependent calls.
- **The Mac twins**: find-all, M1, gcc-16 -O2, darwin libc `memchr`,
  directional only (D144 addendum 1).
- **The gap cells**: the bench's Linux pin `c4c70f2c`, abi 60.
- **What could flip a decision**:
  - the dense single-byte VM regime (per-attempt `memchr` entry; a guard
    cell, and the form is the kit's);
  - short-call search, where the VM hat adds one entry scan. Tier C: an
    absolute delta against the floor, never a ratio.

**2. Independent control: RELEVANT.** §6.2:
- **C-SS** is the fact's control. It shares no code with the walk, and it
  already caught a real defect.
- **The deny arm** is the answer control.
- **K35 / mover populations**: the census counts both hats' movers by
  predicate, and the build counts them by emitted text (the biconditional).
- **Reach**: every sabotage witness is a named fixture, because the bench
  subjects are blind to S479. S483 is declared UNREACHED with an assertion.

**3. What moves when data is regenerated: RELEVANT, narrowly.**
- `start_set` is a pure function of the pattern: no table, no calibration.
- Two indirect data dependencies:
  - **the frequency prior / findings bundle** feeds `pcrec_dfa_cand_ppm`. Once
    it reads the narrowed set (§4.3), regenerating a bundle can move a hybrid
    mover's `[OPT-HYB-RESEED]` row. That is already true of byte-class rows
    today and is not new in kind. It is an abi event only if a bundled default
    table changes (the existing rule);
  - **the census TSV here** is read by no check. Re-running `census.py` at a
    later pin moves nothing.
- Each mover stage is an abi event (§8) with spec hunks (D80).

---

## 11. The four lenses (+ D124's)

| lens | verdict |
|---|---|
| specific vs general | GENERAL: one fact (the first-byte set of the zero-width-erased language), one table, rows by the information they use. No pattern is named |
| core vs derived | `start_set` is CORE (an AST walk). Both hats are DERIVED consumers. The re-seed is an existing primitive |
| applicable vs assumption-changing | APPLICABLE. The one assumption it leans on (the idle state is a function of the previous byte's class) is the entry seed's own, and it is tested at every startpos today |
| fits-arch vs refactor | FITS: rows on `dfa_pfs[]` (D122 addendum 4), a hook slot, one fact. The rename is deferred (Q2) |
| D124: a question both emissions share? | YES. That is the design. The engine appears only in F/V and in the emit hook |
