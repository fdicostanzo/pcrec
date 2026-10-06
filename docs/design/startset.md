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

**BUILD (lane `ssbuild2`, 2026-10-05): stage 2, THE VM HAT, BUILT, abi 61 -> 62** — `first-class` serving the VM route alone (Q-R5: the table form only; S479 UNREACHED behind an assertion), V as §2 states it, the seek after K73's offset-0 seek and before the first attempt and after each failed one, `-fno-start-set` (bit 47, in `strategy_denials`), `<PREFIX>_VM_START_SCAN` on every artifact; the edge cells `vmhat.rxt`/`giveup.rxt` moved into `tests/startset/`; the run_axes product arm; the every-startpos differential and start-byte oracle as standing checks; the mover manifests regenerated with the fixtures (+12/+13 rows, nothing else moved) and matched by ID. One finding against §6.1's "modulo the abi digit and the stamp": the hat's 256-entry table is K-invariant bytes the size term's materiality bar reads, so a borderline ladder pattern's unroll K can move (measured on a threshold-1000 reference compiler, 0 corpus patterns at the shipped threshold). `docs/dev/lanes/ssbuild2_report.md`.

**BUILD (lane `ssbuild01`, 2026-10-05): stages 0 and 1 BUILT, zero movers, no abi event** — K84 fixed (`DfaPf.scan`), the `start_set` fact, the route mask, the FIND extraction, `tests/startset/` (C-SS\* et al.), the stage-1 census with per-block options (`startset/s1/`) and the stage-2/3 mover manifests (`tests/startset/manifests/`); sabotage S495, S501, S502 landed early on their stage-1 detectors. `docs/dev/lanes/ssbuild01_report.md`.

Ids used here: sabotage S478-S502 (rev 2, §6.3; r3 used S478-S485; §6.4 proposes S503-S504), no K-row filed, D148 RULED
(§9), rev-2 questions Q-R1..Q-R6 RULED 2026-10-05 as recommended (D148 addendum 2; Q-R4 with Frank's caution: stage 4 demoted to filed-not-planned).

**REVISION 2 (lane `ssrev`, 2026-10-05, from main `08caf4a3`, abi 61)
applies the FULL D6 panel r4** (`../dev/reviews/2026-10-05-r4-startset.md`:
critics ssc-sound, ssc-checks and ssc-cost; 34 finding ids, all
dispositioned). **Read §R2 first.** The panel found one BLOCKER, sound-F1:
the DFA hat's `T = S ∩ E` deletes matches on 6 corpus movers. Revision 2
replaces it with a measured-sound set (§4.1a). Six questions go back to
Frank (§9b). Nothing under `src/`, `cli/`, `lib/` or `tests/` changed. The
rev-2 instruments and transcripts are in `startset/rev2/`.

**§6.4 (lane `ssedge`, 2026-10-05, from main `e6ceeefa`) answers D148
addendum 1's direction: edge cases, and whether the tests SEE each wrong
variant.** 80 draft edge blocks / 2,070 cells, every answer libpcre2's
(10.48 and the 10.46 reference agree on all of them), and a mutation run in
which every listed wrong variant is detected at answer level, except two
that are equivalent on every buildable machine (argued, with the check that
sees each). It also refutes two claims of this note: the unconditional
re-seed loses matches on ordinary seeded movers, not only on `\G` (§6.4.3
item 1), and `Tdfa` is not a sound floor (item 2; the ruled `T = S` is
unaffected). It flags S481/S482 as unreachable and S483-S485/S480 as weak,
and proposes S503/S504. Instruments: `startset/edge/`.

---

## R2. What changed in revision 2, and why

Keyed to the r4 finding ids. "Q-R*n*" marks a change that alters a D148
ruling's text or basis; it is not applied, only proposed (§9b).

| ids | section | change |
|---|---|---|
| sound-F1 | §2 F, §4.1, §4.1a | **The DFA-hat set is now `T = S ∩ E*` (which equals `S`), admitted iff `T ⊊ E`.** r3's `T = S ∩ E` is UNSOUND when `S \ E ≠ ∅`. A skipped byte in `E \ S` moves the true context to another seed state, where a byte in `S \ E` can begin a match, and the skip runs past it. Measured over the six corpus witnesses and a 94-row seeded-machine sweep: 13,583,325 cells; the r3 set gives 322,771 diffs on 20 rows; (a)/(b) give 0. `E*` is all 256 bytes on every seeded machine (structural, §4.1a), so (a) ≡ (b), and the subset admission makes them mover-identical to (c). **Q-R1.** |
| sound-F1, checks-F4 | §6.3 | S480's expectation, "emitted table == `start_set` ∩ the deny arm's table", pinned the defect. It now reads "== `start_set`, and ⊊ the deny arm's table" (rev 2's S486). The six witnesses become fixtures. A new row plants "T from s0's escape set only", i.e. r3's formula (S480). |
| sound-F2, checks-F2 | §6.2 | **C-SS is replaced by a control that reaches seeded machines and can fail in the WALK.** `Tdfa ⊆ S` is checked on every machine, with `Tdfa` read off the emitted tables (864 artifacts read, 170 of them seeded). Four planted walk defects each fire: 367 / 185 / 118 / 23 violations, baseline 0 (`rev2/out/control.txt`). The drop-one twin is retired as a control (it checked set arithmetic). The START-BYTE ORACLE is added, external to the walk. On the VM hat it reads 0 violations over 76 auto rows and 2,470 forced-VM rows, 202.7M cells (§4.2, §6.2). |
| sound-F3 | §4.2, §8 | The give-up surface includes CAPACITY (`PCREC_ERR_FRAMES`, trail, the caller-buffer `_in` entries), not only meters. **Q-R3** (extends ruled Q6's sentence). |
| sound-F4 | §1, §3.1, §3.4, §6.3 | The fact reads the compile's own options. A flagged (`-i`, `--ucp`) witness joins the fact's checks. The utf8 start-byte assertion (rev 2's S497, r3's S483) is ordered after the non-nullable and `\|S\|<256` conjuncts. The census re-run with per-block options is owed at stage 1, before the mover manifest is pinned. |
| sound-F5 | §4.1, §4.2 | The vacuous `(a+)x\1catdog` row is removed. The `straße` control transcript is corrected (1 diff; the claim was right). Newline cells are now reached (`\x`-decoding drivers). The count-collapsed obligation needs a FAILING witness at stage 3. |
| sound-F6, cost-F4 | §4.2, §4.3, §7 | **The VM-hat entry order is stated**: range guard → K50 → `rx_valid_upto` → K65/K66 pre-check → seek from `max(search_from, K82 lo)` → loop. An S == REQ_BYTE hit-dense alpha cell is added, and a VM-hat dominance/handoff row is FILED with it as its trigger. |
| sound-F7 | §2 F, §4.1 | F requires the unanchored scan kind. The new rows' re-seed is CONDITIONAL on the scan having moved, so `\G`'s gseed at `q == search_from` survives. |
| sound-F8, checks-F3, cost-F8 | §6.2, §7, §9b | The forced-VM coverage Q7 relied on does not exist. Stage 2 delivers a `run_axes.sh` product arm and an every-startpos differential, both named and floored. The engine axis also runs under `-fno-start-set`. "76 + 117" is corrected. **Q-R2** (Q7's basis). |
| sound-F9, checks-F9 | §3.1 | **The row reads the walk's nullable bit.** That bit is the erased language's nullability, a different question under D120. A check pins `NULLABLE ⇒ walk.nullable`. The epoch wording is fixed. |
| checks-F1 | §6.1 | `<PREFIX>_VM_START_SCAN` goes on EVERY artifact of both engines, `"none"` where unapplied (Frank's K82 Q3 ruling; `REQ_HANDOFF`'s built precedent). The byte-count readers are re-priced. **Q-R6** asks only to confirm the family. |
| checks-F4 | §6.3 | The sabotage table is rebuilt: per form × per conjunct × per arm, each row with its `SAB_REACH`, renumbered from S478 (S477 is the highest on main). S484 (r3) becomes S494 and gets a solo-run confirmation before numbering. |
| checks-F5 | §6.2, §10 | A committed mover manifest by ID, per hat per stage, checked at build. The census TSV now moves a check when it is regenerated. |
| checks-F6 | §2 | A per-row route mask is tested before `applies`. The zero value is the legacy DFA route. A structural check covers the `DfaSel` initializers. |
| checks-F7, checks-F10 | §8 | The reader list is extended. `scripts/emit_sweep.py` is each zero-mover stage's gate, and a stage-0 no-`strcmp`-on-row-name check is added. |
| checks-F8, cost-F10 | §5, §4.4 | VMSTART is D91 budget 2. Every unmeasured constant is labelled (D149). |
| checks-F11 | §2, §4.1, §7 | Citations are corrected. |
| checks-F12 | §5 | The form-carrying names are kept (D148 ruled them). The rename is recorded as an M1 cost with the existing `memchr`/`byte-class` debt. |
| checks-F13 | §5 | Both manifest rows name the extracted emitter, which takes a `pcrec_` prefix and the link-symbol check. |
| cost-F1 | §2, §4.4, §7 | The VM hat's dense single-byte regime loses (memchr ×0.6 at d 80%). **Q-R5**: emit the table form only at stage 2, and file MASS admission with its trigger. |
| cost-F2, cost-F3, cost-F5, cost-F6, cost-F7 | §7, §4.4, §10 | The Mac numbers are labelled as the table form. The memchr form's Linux timing is owed. Match-dense and short-call cells are added. F3 runs at the dense movers, with an expected sign per cell. One-byte narrowings are null cells. The null band is per configuration. The libc is recorded and both layers are reported. "A narrower set never costs" is withdrawn to "no measured loss". |
| cost-F9 | §8 | Stage 4's trigger is a regression guard, not a need. **Q-R4**. |
| cost-N1 | §10 | Stated: the cost side's only independent control is the Linux deny floor. |

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
   [rev 2, sound-F1: true for the set measured here, where `S ⊆ E`. With
   r3's `T = S ∩ E` and `S \ E ≠ ∅`, the re-seed does NOT repair the scan.
   `lookbehind.rxt:212` is a hybrid that loses 11,772 cells (§4.1a).]
3. **The DFA hat reaches the CTX group as well.** Its movers (seeded machine,
   byte-class skip, `T ⊊ E`) are **18 bench / 38 corpus** artifacts
   (9+9 / 31+7 DFA+hybrid) under rev 2's set (§4.1a). [rev 2, sound-F1: r3
   read 18 / 58. That count included 14 corpus rows where `S ∩ E = ∅`, which
   F's non-empty conjunct declines anyway, and 6 rows where `S \ E ≠ ∅`,
   which the r3 set got wrong (`startset/rev2/out/sweep_summary.txt`).]
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
   member of `S`) fires on all 685 (§6.2). [rev 2, sound-F2/checks-F2: that
   twin checks set arithmetic, not the walk, because `min(E) ∈ E` holds for
   every non-empty `E`. The population had no seeded machine, which is
   where the BLOCKER lives. The control is rebuilt in §6.2. On every
   machine, seeded included, it checks the emitted `Tdfa` ⊆ the walk's `S`,
   and four planted WALK defects fire.]
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
| … with a byte-class skip and a necessary `S` (the rows a new row can replace) | 20 | 74 |
| … that narrow under rev 2 (`T = S ∩ E* ⊊ E`) | **18** (9 dfa, 9 hybrid) | **38** (31 dfa, 7 hybrid) |
| … r3's count (`S ∩ E ⊊ E`, empty T included) — superseded | 18 | 58 |

[rev 2] The middle rows are from `startset/rev2/out/sweep.tsv`, 94 rows in
all. The memchr rows have `|E| = 1` and cannot narrow. Offset-set rows sit above the new rows. **Census fidelity
(sound-F4)**: corpus rows compile every DISTINCT pattern text at byte
encoding with no per-block flags. 629 blocks are utf8 and 124 carry flags,
and dedup by text merges, e.g., `[a-z]` with its `i` twin. The stage-1
census re-run reads each block's own options and dedups on (text, options)
before the mover manifest (§6.2) is pinned.

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

**F** (DFA, forward machine, unanchored body). Rev 2, after sound-F1 and
sound-F7:
- the machine is SEEDED (`dfa_needs_seed`);
- the scan kind is the UNANCHORED forward scan (`RX_DFA_SCAN` unanchored).
  `\G` and `(?m)^` machines take the attempt scan and are out (sound-F7);
- the start set `S` is a necessary condition: not nullable, and `|S| < 256`;
- `T = S ∩ E*` is a PROPER, non-empty subset of `E`. Here `E` is today's
  `us.cand.set` (s0's escape set), and `E*` is the union of the escape sets
  of every seed state and s0. **On every seeded machine `E* = all 256`, so
  `T = S`** (§4.1a gives the argument and the measurement). The row is
  therefore "scan `S`, admitted iff `S ⊊ E`". Q-R1 asks Frank to rule
  between this and its two alternatives (§9b).

  **[r3 text, SUPERSEDED — sound-F1]** `T = S ∩ E`. That set is unsound
  wherever `S \ E ≠ ∅`. On the 6 corpus movers where it differs from rev
  2's set, it loses 11,040-60,430 cells each at the witness alphabets
  (§4.1a).

Where `T == E` the four new rows are transparent and every artifact is
byte-identical (S1's prepend argument, `litscan_s1.md` §1.2). On an UNSEEDED
machine `E ⊆ S` (§6.2), so `T == E` and nothing moves by construction.

**The route mask (checks-F6).** `dfa_select` (`emit_dfa.c:5071-5086`) calls
`cand->applies(s)` on every non-denied row. Today's rows' `applies` read
`s->us`/`s->d`, which a VM-route selection does not have. So each row
carries a ROUTE MASK (`DFA`, `VM`, both), and the walk tests it BEFORE
calling `applies`: the table's "never" cells are data, not code.
- The mask's zero value is the legacy DFA route, so no existing row
  changes.
- `DfaSel` gains `route` the same way. Every positional initializer (e.g.
  `{ cx, d, NULL, true, -1 }`) is converted to designated initializers in
  stage 1, and a structural check fails on a `DfaSel` initializer that
  omits `route`.
- `--list-axes` lists a two-predicate row once, with both predicates
  (`dfa: …; vm: …`), and `axes_registry_check.sh` counts it once.

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
  range (DD-12 (7)). Today this is an ASSERTION, not a decline (§3.4). It is
  evaluated AFTER the non-nullable and `|S| < 256` conjuncts (sound-F4). The
  only sets that carry a continuation byte are all-256 sets (9 corpus
  blocks), and checking them first would refuse those blocks at compile.
- **Not denied**: `-fno-start-set`.
- **Form (rev 2, Q-R5 OPEN)**. As ruled, `first-memchr`'s VM predicate is
  `V ∧ |S| = 1`. The recommendation is that at stage 2 the VM hat emits
  ONLY the table form (`first-class`, any `|S|`), and that `first-memchr`'s
  VM column reads "never" until the kit owns the form choice (D146). The
  reason is cost-F1's measurement: a dense single-byte `S` read by `memchr`
  per failed attempt measured ×0.6 at d 80%, against ×0.9 for the table
  loop. The `|S| = 1 → memchr` cut-over is an unmeasured default for VM
  attempts (D149). Both readings are kept until Q-R5 is ruled.

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
deny-only (`axes.def:43`, `:90`; rev 2, checks-F11), and "force a first-set row over an offset row"
would be a selection override with no measured customer.

---

## 3. The fact: the AST start set

### 3.1 Definition and owner

`start_set` is a NEW CORE fact in `src/facts/` (PATFACTS, D126). Its owner is a
new `src/facts/startset.c`. Its epoch is E2, beside `req_set`.
[rev 2, checks-F9: `NULLABLE` is E1 (`facts.def:42`), not E2.]
It is computed on the LOWERED tree (after `pcrec_lower_enc`), so every
`A_CLASS` is a byte class, and it is consumed by both hats. Its value is a
256-bit set plus a `nullable` bit. `--emit-facts` gains one row, `start_set`,
whose value is the popcount and the hex set, or `all` when nullable or full.

**It reads the compile's own options (rev 2, sound-F4).** `-i`, `--ucp`,
`-e`, inline `(*UCP)` and per-block `.rxt` flags all reach the lowered tree,
so a fact computed on the compile's own lowered tree reads them by
construction. The r3 census probe did not: it passed only `-e`. Under
`-e byte --ucp`, its `S` for `(?i)\xe9x` was {E9} while the artifact matches
"\xc9x" (4,239 twin diffs). The fact's checks therefore include a flagged
witness under `-i` and one under `--ucp` (§6.2).

**The `nullable` column is the ERASED language's (rev 2, sound-F9 +
checks-F9).** The two critics asked opposite things. sound-F9 says the row
should read the walk's own bit; checks-F9 says it should derive from
`NULLABLE` or say why not. They are reconciled under D120's
one-owner-per-QUESTION rule:
- The walk's bit answers "can the zero-width-ERASED language `L⁺` match
  empty". That is the premise of §3.2's superset argument: `S` is `L⁺`'s
  first-byte set.
- `NULLABLE` answers "can `L` match empty". These are two questions with
  two owners.
- The row reads the walk's bit, which errs safe: the walk widens
  `A_BREF`/`A_CALL`/`A_VAR` to nullable.
- A stage-1 check pins `NULLABLE ⇒ start_set.nullable` on every corpus
  artifact (`L ⊆ L⁺`), so the two derivations cannot drift silently. If
  `NULLABLE` ever says "nullable" where the walk says "not", the walk has
  under-approximated and the check fails.

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
arise. So the conjunct is a `pcrec_ctx_fail` assertion. [rev 2, sound-F4:
the critic widened this to the corpus's 629 utf8 blocks, flags mapped to
`(?i)`/`(*UCP)`. 598 compile and 561 are non-nullable; 0 of the 561 have a
continuation byte in `S`. Only all-256 sets carry one: 9 blocks,
`tests/vars/caseless.rxt` ×8 and `tests/recursion/k69.rxt:183`. Hence the
assertion is evaluated after the non-nullable and `|S| < 256` conjuncts
(§2 V).]
- **The predicate asked** is "every member of `S` satisfies the backend's
  start predicate", phrased through the encoding seam.
- **Construction**: no spelling in the shipped grammar produces a
  continuation byte in `S` under utf8. A class `[\x80-\xbf]` is the code
  points U+0080-U+00BF, which lower to the lead byte C2.
- **Sabotage**: its row ships UNREACHED (S483; rev 2's S497).

The DFA hat needs no conjunct: under utf8 the machine already steps characters,
and the re-seed reads the class of `s[landing − 1]`, which the entry seed reads
at any startpos (§4.1).

---

## 4. Soundness per row and per hat

### 4.1 DFA hat: the narrowed rows re-seed, and why that is enough

**[stage 1, lane ssbuild01: steps 1-3's WORDING is superseded by §6.4.3
item 2's corrected argument — the re-seed is exact iff every skipped byte is
outside `S`; `E` plays no part in soundness; "state 0 means no live thread"
is not true of a minimized machine. Step 4's re-seed must be CONDITIONAL
(§6.4.3 item 1), a soundness requirement, not a hedge. Both bind stage 3.]**

**The invariant.** Each step below reads emitted code, not the design.
1. The skip runs only while `forward_state == 0` and
   `last_accept_position == -1` (the emitted gate). State 0 means "no live
   thread except the fresh start thread, in the start context". Nothing
   partial is in flight, so nothing is lost by moving.
2. **[rev 2, sound-F1: REWRITTEN. r3's step 2 held only for positions read
   IN STATE 0.]** During a skip that started in state 0, the true state at
   every skipped position is a SEED state: s0, or some `seed[c]`.
   - A skipped byte that begins no thread moves the machine to
     `seed[class(b)]`. This is step 3's premise, the entry seed's own.
   - So a skipped byte in `E \ S` changes the CONTEXT. At the next position,
     a byte that cannot begin a match in s0 (`∉ E`) may begin one in that
     new context.
   - The sound condition is therefore: **every byte that begins a live
     thread from ANY seed state is in `T`**. Call that set `Tdfa`; it is
     read off the emitted tables (`startset/rev2/estar.py`).
   - `Tdfa ⊆ S` whenever `S` is sound. `S` is a superset of every
     non-empty match's first byte, in every context. So `T = S` satisfies
     the condition, and so does `T = S ∩ E*` (§4.1a: the two are equal).
   - r3's `T = S ∩ E` drops `S \ E`. That is exactly the set of bytes that
     begin a match only in a context the skip reaches by moving out of s0.
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
   - **[rev 2, checks-F11]** The existing `memchr`/`byte-class` rows have
     `reseeds = false` and emit no re-seed (`emit_dfa.c:6465-6468`), so the
     new rows need WRAPPER emitters around the shared FIND loop. They are not
     "the same emitters called with `T`".
   - **[rev 2, sound-F7]** The re-seed at the new call sites is CONDITIONAL
     on the scan having moved: `if (q > entry) state = seed[class(s[q−1])]`,
     the twin's form. `pf_emit_ofs_reseed`'s unconditional
     `pos ? seed[…] : s0` (`emit_dfa.c:6373`) would, on a gseed (`\G`)
     machine, overwrite the `\G` start state at `q == search_from`. F
     excludes the attempt scan, so no shipped mover reaches it, but the
     conditional form makes the row safe if F's scan-kind conjunct ever
     widens.

**The views (`-bounded`) twins** mirror `memchr-bounded`/`byte-class-bounded`:
- the skip stops at `n − 1`;
- there is no early `return 0`;
- both landing paths re-seed (`pf_emit_ofs_bounded`'s shape).

**The hybrid.** Its `static <p>_prefilter` IS this emitter's output, so the
proof carries over. Two hybrid-only readings:
- **The window's start is a lower bound** (P5, `emit_vm.c:9393-9401`; rev 2,
  checks-F11: r3 cited `emit_dfa.c:5454`, which is the EOL-view emission). A narrowed
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
  - **[rev 2, sound-F5 (d)] The obligation needs a FAILING witness.** With
    `-fprefilter-collapse` on `\b(ab|cd)\b.{0,2}\b(ab|c)\b` and
    `\b(a|b)\b.{1,3}\bc\b`, the critic measured re-seeded 0 diffs and
    no-re-seed 0 too, so the hazard is not reached. Stage 3 must find a
    collapsed mover whose no-re-seed twin LOSES matches, or declare the
    obligation UNREACHED with that sweep as its evidence.

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

[rev 2] Every r3 twin pattern has `S ⊆ E`, and `dfatwin.py` computed `T` by
the formula under test. The table above therefore could not see sound-F1
(learnings §3: the control shared its source with the subject).

### 4.1a The DFA-hat set, measured (rev 2, sound-F1; Q-R1)

**The three candidate repairs** the manager asked to be compared:
- (a) `T = S ∩ E*`, where `E*` is the union of the escape sets of every
  seed state and s0;
- (b) `T = S`;
- (c) decline the row when `S ⊄ E`.

All three re-seed. The instruments are in `startset/rev2/` (`run.sh`
reproduces everything):
- `estar.py` reads `E`, `E*` and `Tdfa` off the EMITTED tables;
- `patch.py` builds the twins;
- `drv5.c` runs base against four twins, every subject, every startpos,
  the full capture vector. It has a local-libpcre2 arm and the START-BYTE
  ORACLE: every byte that begins a non-empty match under base or libpcre2
  must be in `T`;
- `sweep.py` drives the population.

**A structural fact first: `E* = all 256` on every seeded machine.**
- A byte `b` that begins no thread moves ANY seed state to the single
  state `seed[class(b)]`.
- A byte that begins a thread moves it out of the seed states altogether.
- So with two or more distinct seed states, which is what "seeded" means,
  every byte leaves at least one of them.

Hence (a) ≡ (b) on every seeded machine. Measured: `|E*| = 256` on 94 of
94 rows, and `T_a == S` on 94 of 94. The machine's own floor `Tdfa` also
equals `S` on 94 of 94: on this population the walk is exact against the
subset construction, with no slop.

**The six sound-F1 witnesses**, at the critic's alphabets, maxlen 7
(`rev2/out/witnesses.tsv`). Local libpcre2 agreed with base on every cell.
"static" is `Tdfa ⊆ T`; "oracle" is the start-byte oracle; `1` = holds.

| pattern | route | cells | `\|E\|` | `\|S\|` | `\|T\|` r3 / a / b | diffs r3 / a / b | static r3 / a / b | oracle r3 / a / b |
|---|---|---|---|---|---|---|---|---|
| `(?:(?<=a)z\|w)` (`matrix.rxt:1064`) | dfa | 167,481 | 2 | 2 | 1 / 2 / 2 | **11,040** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |
| `(?:(?<*a)z\|w)` (`:2597`) | dfa | 167,481 | 2 | 2 | 1 / 2 / 2 | **11,040** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |
| `(?:(?<=[ab])z\|w)` (`:1122`) | dfa | 756,836 | 3 | 2 | 1 / 2 / 2 | **60,430** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |
| `(?:(?<*[ab])z\|w)` (`:2662`) | dfa | 756,836 | 3 | 2 | 1 / 2 / 2 | **60,430** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |
| `(?<=a)b\|(?<=bc)d` (`lookbehind.rxt:212`) | hybrid | 167,481 | 2 | 2 | 1 / 2 / 2 | **11,772** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |
| `(?m)(?<=\n)a\|b$` (`ucp/ctxnode.rxt:400`) | dfa | 167,481 | 2 | 2 | 1 / 2 / 2 | **12,264** / 0 / 0 | 0 / 1 / 1 | 0 / 1 / 1 |

The r3 column reproduces ssc-sound's 11,040 / 11,772 / 12,264 exactly.

**The seeded-machine sweep** (`rev2/out/sweep.tsv`, `sweep_summary.txt`).
Population: every census row whose auto artifact is a seeded DFA or hybrid
with a byte-class skip and a necessary `S`, 94 rows (20 bench, 74 corpus).
Each row uses an alphabet of one representative per forward byte class,
`S \ E` members first, capped at 7. The length is 5-7 by alphabet size.

| `T` | rows with diffs | total diffs | static fails | oracle fails |
|---|---|---|---|---|
| r3 `S ∩ E` | 20 | 322,771 | 21 | 21 |
| (a) `S ∩ E*` | 0 | 0 | 0 | 0 |
| (b) `S` | 0 | 0 | 0 | 0 |
| `Tdfa` (the machine's floor; a control) | 0 | 0 | 0 | 0 |

The sweep covers 13,583,325 cells and 3,688,128 matches. 78 of the 94 rows
reach at least one match; `wb-512` reaches none at its alphabet, so it
counts as unreached. libpcre2 against base: 0 diffs.

**The mover effect of each option**:

| option | admission | movers: bench | corpus | total |
|---|---|---|---|---|
| r3 | `S ∩ E ⊊ E`, non-empty | 18 | 44 (6 of them UNSOUND) | 62 |
| **(a)** = (b) | **`T ⊊ E`** (the scan set shrinks) | **18** | **38** | **56** |
| (a) = (b) | `\|T\| < \|E\|` | 18 | 53 | 71 |
| (c) | decline when `S ⊄ E` (else r3's set) | 18 | 38 | 56 |

**The choice is the admission rule, not the set.**
- Under the subset admission, (a), (b) and (c) emit IDENTICAL tables on an
  IDENTICAL mover set, by algebra: `S ⊊ E` ⇔ `S ⊆ E ∧ S ∩ E ⊊ E`.
- The cardinality admission adds 15 corpus rows and no bench row. All 15
  are lookbehind/context test shapes, e.g. `matrix.rxt:1100` (`|E| 2 → |S| 1`)
  and `axis13_ctx_illformed.rxt:21` (`|E| 255 → |S| 1`).
- On those 15 the scanned set SWAPS members: bytes of `S \ E` enter, bytes
  of `E \ S` leave. §4.4's "a narrower set never costs" argument does not
  cover a swap, and no bench cell asks for it (D77).

**Recommendation (Q-R1): (a)**, written as `T = S ∩ E*` and admitted iff
`T ⊊ E`.
- It is the manager's (a). It is shown sound: 0 diffs on 13.58M cells,
  plus the static and the oracle checks.
- It is mover-identical to (c).
- It keeps the D148 shape: the DFA hat reads the `start_set` fact, and
  `E*` costs one table read.
- The build asserts `T == S` on every mover, so the `E*` intersection
  stays a stated identity, not a silent no-op. A machine where it fails is
  a seeded machine with one seed state, which is a contradiction worth an
  assertion.

`Tdfa` alone would also be sound and would need no AST fact. **[REFUTED,
§6.4.3 item 2: `(?:\b|x)y` on `xy` — `Tdfa` is not a sound floor; stage 1's
C-SS\* check says so in its own header.]** It is
recorded as a finding, not proposed: on this population it equals `S`
everywhere, and using it would make the DFA hat a second mechanism beside
the shared fact (D148 Q1, D124). It is the CHECK instead (§6.2).

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
- **The entry order, stated (rev 2, sound-F6 + cost-F4).** The emitted
  VM-none order today is: range guard → K50 `STARTPOS` → `rx_valid_upto`
  (`-futf-check`, D133) → K65/K66 pre-check → attempt loop. The seek goes
  between the pre-check and the loop, and it starts at
  `max(search_from, lo)`, where `lo` is the K82 handoff's start when the
  handoff applies.
  - **After `rx_valid_upto`**: otherwise an ill-formed subject with no
    `S` byte returns 0 instead of −9 (`PCREC_ERR_UTF`).
  - **After the pre-check**: a pre-check NOMATCH stays the whole answer,
    which is K65/K66's linear no-match proof.
  - **From the handoff's `lo`**: the seek never re-scans below a start the
    handoff already proved.
  - **The cost of this order**: where `S == {REQ_BYTE}`, the pre-check and
    the seek `memchr` the same byte once each per call, the K85 shape. That
    is cost-F4's alpha cell (§7). A VM-hat dominance/handoff row (hand the
    pre-check's found position to the seek as its first candidate) is FILED
    with that cell as its D77 trigger, not built.
- **No candidate.** If the seek reaches `subject_length`, the answer is
  `return 0`. No attempt at `n` can succeed, because the pattern is not
  nullable.

**The contract to the VM consumer (D124 item 3, the K64 lesson).** The hat
removes only attempts that FAIL, so the per-call step and work meters can only
DECREASE, and so can every CAPACITY the skipped attempts would have used.
[rev 2, sound-F3: r3 named only the meters. Witness: `(?=(?:a|b|x)*c)x`
under `--engine=vm --backtrack-frames=8`, on `(ab)×12` + `"xc"`. Base returns
−3, `PCREC_ERR_FRAMES`, because the attempt at 0 (`a ∉ S = {x}`) exhausts
frames inside the lookahead. The VM-hat twin returns 1, (24,25). The corpus
has 22 `gu frames` lines beside 13 `gu steps`. The give-up surface is
`PCREC_ERR_STEPS`, `PCREC_ERR_WORK`, `PCREC_ERR_FRAMES`, the trail capacity,
and the caller-buffer `_in` entries' capacities. The direction is unchanged.
Q-R3 extends ruled Q6's spec sentence to name them (§8, §9b).]
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
| ~~`(a+)x\1catdog`~~ — **removed (rev 2, sound-F5 (a))**: 0 matches at maxlen 6, below the 9-byte minimum match; vacuous | auto | 1 | 2,054,353 | — |
| `\Bcat\B`, `(?i)cat`, `(?:\Ga\|b)c`, `a\Kb`, `\b(?:true\|false\|null)\b`, `(?<=a)b(c)` | `--engine=vm` | 1-3 | 20k-2.6M each | 0 |
| `(?i)café`, `(?i)straße` (`S` holds the `ſ` lead byte C5) | `--engine=vm -e utf8` | 2, 3 | 1.17M, 4.89M | 0 |
| **CONTROLS: one member dropped** — quoted-delim `'`, `(?i)cat` `c`, `(?i)straße` `s` | | | | **150,977 / 2,824 / 1** |

The `straße` reach is thin (3 matching cells), and the controls show it can
fail.

[rev 2, sound-F5 (b), (c), sound-F10]
- **The `straße` control transcript.** `vmtwin_out.txt` records the
  `(?i)stra\x{df}e` CONTROL line (DROP=73) as `diffs=0`. The critic re-ran
  it and got `DIFF [straße]@0 base=1(0,7) twin=0`, `diffs=1`. The claim
  above is right and the transcript is mis-recorded. The file stays as the
  r3 lane wrote it; this paragraph is the correction.
- **Newlines.** Every r3 driver read subjects with `fgets`, so no subject
  held '\n'. The critic's `\x`-decoding drivers
  (`../dev/reviews/2026-10-05-r4-startset/ssc-sound-harness/`) reached
  `(?m)$\na`, `(?m)^ab` and `(?m)(?<=^a)b` on the VM hat: 0 diffs each.
- **What else held** (sound-F10, 0 diffs each, every startpos, full capture
  vector): `(?<!a)b`, `(?=ab)a`, `(?>a|)b`, `a?+b`, `(a|)(?1)b`,
  `(?:\1a|(b))+`, `(?(DEFINE)(a))b(?1)`, `(?=a)?b`; and utf8 with ill-formed
  bytes, e.g. `(?i)kx` with U+212A and a lone E2/84.

**The start-byte oracle on the VM hat (rev 2, checks-F2 (b)).**
`rev2/vmoracle.py` + `drv_obs.c` take the expectation from OUTSIDE the
walk. Over every subject on a per-row alphabet, at every startpos, every
byte that begins a non-empty match under the artifact or under local
libpcre2 must be in `S`.
- **At `auto`**: the 76 VM-hat rows (17 bench + 59 corpus), 8,372,295
  cells, 767,881 matches, 41 rows reaching a match. 0 violations, and 0
  artifact-vs-libpcre2 disagreements (`rev2/out/vmoracle_auto.tsv`).
- **Under `--engine=vm`**: 2,470 rows (66 `\K` rows skipped, because
  their reported start is not the attempt start), 194,302,213 cells,
  50,325,304 matches, 1,875 rows reaching a match. **0 violations.** Three
  rows disagree with local libpcre2, and all three are documented PCRE2
  defects the corpus already marks: `atomic_groups/possessive.rxt:424/430`
  (U9) and `base/fuzz_regressions.rxt:29` (U1). See
  `rev2/out/vmoracle_vm.{tsv,txt}`.

This oracle reaches the VM-only arms (`A_BREF`, `A_CALL`, `A_VAR`, and
the zero-width set), which no DFA-side control can.

### 4.3 Cross-row facts each hat must leave alone

- **`pcrec_artifact_has_dfa_scan(cx)` stays FALSE on a VM-hat artifact.**
  K65/K66's no-DFA pre-checks, G1's dominance and the K82 handoff's (a) all key
  on it. The VM hat is not a DFA scan. Flipping the predicate would elide the
  linear no-match proofs that K65/K66 exist for, which is the K64 shape
  exactly. This is a build assertion and sabotage S494 (r3's S484).
- **The seek runs after the pre-check, and it can scan the same byte
  (rev 2, cost-F4).** Where `S == {REQ_BYTE}`, the K65 pre-check and the
  seek both `memchr` that byte: two libc entries per call. The order is
  §4.2's. Its price is an alpha cell (§7). The dominance/handoff row is
  filed behind that cell.
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

**[rev 2, cost-F5] "A narrower set never costs" is WITHDRAWN to "no
measured loss".**
- **The model has no re-seed term `r`.** The re-seed is paid per skip exit
  that actually skipped. Its weight is largest at the DENSE movers:
  kv-quoted 57%, wb-256/512 56%, hex32 32%.
- **The r3 schedule measured F3 where `r` is most amortized**:
  json-constant (7.9%) and aws (0.17%).
- **The critic's DFA twin `\b[x][0-9]\b` (E 63)** shows the narrowing's
  gain vanishing above d ≈ 20%: no difference at 29%; ×1.1-1.2 at 19%;
  ×5.5 at 0.6%. The Mac base spread is up to 45%, so no cost is
  resolvable either way there.
- **A T⊊E narrowing by one low-density byte** (float-literal 11→10,
  grok 4→3) gains ≈0 and still pays `r` and an abi move.
- **Consequences in §7**: F3 runs at the dense movers too, each cell
  states its expected sign, and one-byte narrowings are NULL cells with a
  deny floor.
- **No decline rule is added.** D148 has none, and none is measured to be
  needed. The admission `T ⊊ E` has NO MARGIN, which is an unmeasured
  default (D149, below).

**The VM hat has no model** and needs none. A skipped position costs a table
read or part of a `memchr`. A non-skipped one costs what it costs today, plus
one byte test. The one regime where the hat could LOSE is a dense
single-byte `S` read by `memchr` per failed attempt:
- the call entry (~5 ns, `cycle2_batch2_reading.md` §4.1's `c_call`) is paid
  on candidates 1-2 bytes apart;
- that is a FORM choice inside a delegated site, which is the kit's under D146
  (§5);
- the alpha carries a dense-candidate guard cell (§7).

**[rev 2, cost-F1] That regime is measured, and it loses.**
- **Setup**: `a(\w)\1` (vm/none, `S = {a}`, REQ_BYTE 97) on a random
  8-symbol subject at a-density d, find-all, base → twin.

  | d | table twin | memchr twin |
  |---|---|---|
  | 5% | ×1.1 | ×1.2 |
  | 17% | ×1.0 | ×0.9 |
  | 33% | ×0.9 | ×0.9 |
  | 50% | ×0.9 | ×0.9 |
  | 80% | ×0.9 | **×0.6** |
- **The loss is per call / per dense MATCH, not per retry.** On
  `a(\w)\1\1\1\1\1` (rare matches) both twins win at every d up to 50%,
  and only memchr loses at 80% (×0.9).
- **So the hat needs either a form rule or an admission.** Q-R5 recommends
  the form rule: the table loop only at stage 2. That removes the ×0.6
  without a new constant. MASS admission (`pcrec_find_set_ppm` over `S`,
  the existing prior; its threshold would be a new constant to MEASURE,
  D149) is FILED, with the dense guard cells as its trigger.
- **§10.1's sentence "a log or JSON subject moves `d`, not the sign" is
  withdrawn**: at d ≥ 33% on a match-dense subject the sign flips.

**Unmeasured defaults (D149), labelled here and in place at build:**

| constant | where | status | what would measure it |
|---|---|---|---|
| `\|S\| = 1 → memchr` cut-over (VM hat) | §2 V | UNMEASURED for VM attempts; inherited from the DFA scan | the dense cell above at Linux/glibc (glibc's call term ~3.4 ns, k82cost Q7); gap break-even ~1-6 B by the critic's arithmetic |
| `\|S\| < 256` as the only narrowness gate (both hats) | §2 F/V | UNMEASURED default | the dense guard cells (`.`-led `\|S\| = 255`, `\w`-led 63) |
| `T ⊊ E` with no margin (DFA hat) | §2 F | UNMEASURED default | F3 at the one-byte-narrowing null cells (float-literal, grok) |
| `a = 3.21`, `b = 0.84` ns | this section | MEASURED, but in another regime (I-85: Linux Ryzen gcc-15, dependent-chain throughput); reused for a per-retry claim it does not cover | F3 at the dense movers |
| VMSTART's D91 budget | §5 | was "1", now **2**, UNMEASURED | the short-call cell (§7) |

---

## 5. Consumers, sites and the [MEMFN] manifest (D146/D147, integration.md rev 4.4)

| site | today | change | manifest (`tests/memfn/site_manifest.tsv`) |
|---|---|---|---|
| T1 PF (`pf_emit_memchr[_bounded]`, `pf_emit_bcls[_bounded]`): the DFA unanchored skip, and the hybrid's inlined copy | FIND over `E` | the DFA hat: the shared FIND loop called with `T` from WRAPPER emitters that add the conditional re-seed (§4.1 step 4). The OPERAND changes, the site does not. The re-seed line after it is pcrec's (§8.5: "state writes stay pcrec's") | no new row. The existing T1 PF rows cover it (pending until M1/M2). The row NAMES the extracted emitter's function (checks-F13) |
| **VMSTART** (NEW): the VM attempt loop's entry and retry seek | none (step one position) | FIND over `S` from `attempt_position`, handoff = the VM attempt start. **D91 budget 2** (rev 2, checks-F8: it runs per failed attempt, on candidates that can be 1-2 bytes apart, so dispatch is NOT noise), UNMEASURED (D149) | **a NEW row, `pending`, migrating with T1 PF's step**, because it renders through the SAME primitive, NAMED in the row. If C17 exists at landing, the row lands in the same commit, or C17's static half fails (a `memchr(` in an `emit_vm.c` function no row names) |

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
- **The extracted primitive is cross-file** (DFA and VM emitters), so it
  takes a `pcrec_` prefix and the link-symbol check (rev 2, checks-F13).
- **The `|set| == 1 → memchr` split is a pcrec-side form choice** for now,
  recorded as migrating to the kit with the site (checks-F13). Under Q-R5
  (a) the VM site does not take it at all at stage 2.
- **Form-carrying names (checks-F12, declined with cost recorded).**
  `first-memchr`/`first-class` name a FORM, which D146/D147 make the kit's
  choice. After migration, the `DFA_PREFILTER`/`VM_START_SCAN` values would
  misreport it, and renaming them is an abi event plus a spec change. D148
  Q1 ruled these names, and the existing `memchr`/`byte-class` rows carry
  the same debt. So the rename is a known M1 COST, paid once for the whole
  family at the T1 PF migration, not piecemeal here.
- **D147 addendum 4.** At M5 "the reseed becomes unconditional". The DFA
  hat's rows re-seed whenever the scan moved (§4.1 step 4, the conditional
  form). That is unconditional in D147's sense: every skip exit that
  skipped re-seeds. So they need no change at M5.

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
    and that IS the control. [rev 2: modulo the abi digit and the
    every-artifact stamp line, see below.]
- **DFA hat stamp.** The existing `<PREFIX>_DFA_PREFILTER` value moves on
  movers (four new values). There is no new stamp. Every reader of that value
  set is found BY GREP at landing:
  - `stamps.py`/`gapconfig`;
  - the bench's own scripts (relayed);
  - `match_api.md`'s value table;
  - the tests that enumerate it (S1 found a reader class this way).
- **VM hat stamp (rev 2, checks-F1).** A NEW stamp, `<PREFIX>_VM_START_SCAN`,
  whose value is the row name (`"first-class"`; `"first-memchr"` only if
  Q-R5 keeps that VM form). **It goes on EVERY artifact of both engine
  families**, with `"none"` where the hat does not apply.
  - **Why**: Frank's ruling on k82h Q3 (`litscan_k82h.md`, Rulings):
    "stamps vary only by engine family, never by presence within a family,
    and 'does not apply' is a value". `<PREFIX>_REQ_HANDOFF` was built that
    way, on every artifact of both engines (`k82hbuild_report.md`).
  - **r3 was wrong**: it put the stamp on movers only and cited "k82h Q3's
    reasons", which was the note's REVERSED recommendation.
  - **The family is both engines**, as `REQ_HANDOFF`'s is. Q-R6 asks only
    to confirm it.
  - **Cost**: one line on every artifact. The byte-count readers move, and
    are re-priced as k82h §2.3a did: `m5_stage1_stamps.tsv`, the resource
    pin, `artifact_size_log.tsv`, the recursion-identity sweep, and the
    size-tripwire pins. Each is found by grep and re-pinned in stage 2's
    own change.
  - **The deny arm's identity** becomes: under `-fno-start-set`, every
    artifact equals the PRE-CHANGE program plus the abi digit and one
    `_VM_START_SCAN "none"` line. A non-mover is byte-identical between
    BASE and DENY.
  - **`RX_VM_PREFILTER` keeps its meaning** ("a DFA prefilter: hybrid/none")
    and its values.
  - **Why not re-spell it**: a re-spelling would move every VM-hat artifact's
    `"none"`, and readers grep that value (the gap report's causes, the bench's
    program-identity census).

### 6.2 The independent controls (standing question 2)

**Rev 2 rebuilds this table** (sound-F2, checks-F2, -F3, -F5; sound-F8).
In r3, C-SS reached no mover of either hat: every DFA-hat mover is seeded,
and every VM-hat mover has no DFA machine. Its failing direction checked set
arithmetic. And the forced-VM sweep it leaned on did not exist.

| check | subject | checked against | independent because | measured (rev 2) / owed |
|---|---|---|---|---|
| **C-SS* (the fact's control, every machine)** — supersedes r3's C-SS | `start_set`, as the BUILT fact reads it: the stage-1 check pins that it reads `src/facts/startset.c`'s row, never a probe that rebuilds the pipeline prefix (checks-F2; the c2prep F5 hazard) | `Tdfa` read off every emitted DFA/hybrid machine, seeded included: the bytes that begin a live thread from ANY seed state (on an unseeded machine, the emitted `can_begin_match`). `Tdfa ⊆ S` must hold wherever `S` is necessary | `Tdfa` comes from the subset construction's tables, and the walk shares no code with it. **The failing direction plants defects in the WALK** (`fs_probe_plant.c`), not in set arithmetic | `rev2/control.py` → `out/control.txt`: 864 artifacts read (170 seeded), **0 violations**. Plants: `cat-null` (drop `null(l) ? F(r)`) **367** (154 seeded); `alt-right` **185**; `look-eats` (zero-width read as consuming) **118** (74 seeded); `rep-min0` **23**. Each plant's reach is printed beside its detections. 1,721 artifacts are UNREAD (no emitted table, or a seeded table that is not s0's escape set), counted and listed rather than dropped. The drop-one twin is RETIRED |
| **start-byte oracle, both hats** (checks-F2 (b)) | the built artifact's `S` / `T` | the first byte of every non-empty match that the deny/base build OR libpcre2 reports, over exhaustive small subjects at every startpos | the expectation comes from MATCHES, not from the walk or the machine. It reaches the VM-only arms (`A_BREF`/`A_CALL`/`A_VAR`, the zero-width set). It is necessary, not sufficient: it does not see context, which the differential does | DFA hat: r3's `T` fails on 21 rows; (a)/(b) on 0 (§4.1a). VM hat: 76 auto rows (8.37M cells), 0; forced VM, 2,470 rows (194.3M cells), 0 (`out/vmoracle_*.txt`). **At build**: a per-`AKind` arm-reach count (K35 style) with a floor at the committed count |
| answer identity, both hats | the built artifact | the `-fno-start-set` arm (today's emitter) | the deny arm never reads `start_set`. It is the pre-change program | **at build, named and floored (checks-F3)**: (1) a `run_axes.sh` PRODUCT ARM: `--engine=vm` against `-fno-start-set --engine=vm`, with its own baseline and a mover-count floor (today's `run_axes.sh:50-52` sweeps axes at auto only); (2) an every-startpos differential in `tests/utf8/run_startbnd_diff.sh`'s shape, which decodes `\x` (sound-F5 (c)), over the movers × {auto, `--engine=vm`, `--no-captures`}, plain and ASan/UBSan (k82hbuild's 4.4M-cell precedent). At stage 2 the DFA half of "both engines" has no population, and is stated vacuous |
| engine cross-check (sound-F8) | the DFA's answers on S | `--engine=vm` UNDER `-fno-start-set` | once both hats read `start_set`, the engine axis alone no longer checks one against the other. Under the deny, neither reads it | the engine axis row in test-axes gains the `-fno-start-set` arm |
| oracle | the built artifact | the committed libpcre2 store (C3) and the corpus `.rxt` expectations | external | — |
| **mover manifest by ID** (K35; checks-F5) | the emitted text (`_VM_START_SCAN != "none"` / `DFA_PREFILTER` changed) | a COMMITTED manifest, one per hat per stage, of the artifact IDs F/V admit, generated from the stage-1 census re-run (§1, per-block options) | two derivations: facts+predicate against emitted text. Checked at build: 0 off-diagonal, deny-identical. The k82hbuild precedent | at build. Regenerating the census then MOVES A CHECK (§10 Q3) |
| `NULLABLE ⇒ start_set.nullable` (sound-F9/checks-F9) | the walk's bit | the E1 `NULLABLE` fact | two owners of two questions; `L ⊆ L⁺` | at stage 1 |
| give-up surface | the 11 `gu`/budget blocks in reach, and the `gu frames` blocks (sound-F3) | the deny arm at an unbounded budget AND unbounded capacity | the deny arm is the reference | at stage 2 |

### 6.3 Sabotage rows (numbered after the highest S on main at landing; S477 today, verified)

**Rev 2 rebuilds this table (checks-F4, sound-F1).**
- **The bar is D122 addendum 4 item 3**: a row per new predicate, which
  here means per hat × per form (memchr/class, bounded/unbounded), per F
  and V conjunct, and per conservative walk arm.
- **Every row carries its `SAB_REACH` from birth.**
- **UNREACHED rows say why.** Some are unreachable by construction, others
  until a witness is found. An unreachable-by-construction row carries an
  assertion as its guard.
- **The "r3" column maps the old ids**, so citations of r3's numbers can be
  followed.
- **Witnesses marked "verify"** are constructed from the mechanism and must
  be confirmed on the build before the row is numbered. A row whose
  detection is uncertain also gets a SOLO run first (r1mtriage's S220
  precedent; checks-F4 on S484).

| id | r3 | plant | detector | witness (REACHES its site, [MECH-REACH]) |
|---|---|---|---|---|
| S478 | S478 | VM hat, `first-class`: the emitted set drops one member | answer identity | `tests/startset/vmhat.rxt`: quoted-delim on a `'`-quoted subject (twin: 150,977 diffs) |
| S479 | — | VM hat, `first-memchr`: the seek starts one byte late (`memchr(q + 1, …)`) | answer identity | `\((?:[^()]\|(?R))*\)` on `(a)` → (0,3) (verify). **If Q-R5 (a) is ruled, the VM `first-memchr` form does not exist: declared UNREACHED, with a compile-time assertion that no VM-route selection takes it** |
| S480 | — | DFA hat: `T` computed from s0's escape set only, i.e. r3's `S ∩ E` (sound-F1) | answer identity + C-SS* + the start-byte oracle | the six corpus fixtures `matrix.rxt:1064/1122/2597/2662`, `lookbehind.rxt:212`, `ucp/ctxnode.rxt:400`, copied into `tests/startset/dfahat.rxt` with the witness subjects `aza`@0 → (1,2), `aba`@0 → (1,2), `\naa`@0 → (1,2) (measured: 11,040-60,430 diffs each, §4.1a) |
| S481 | S479 | DFA hat, `first-class`: re-seed deleted | answer identity | `\b(?:ab\|cd)\b` on `bab ab` → (4,6), and `atrue true` (twin: 768 lost). **The bench subjects are structurally blind** (`matches=0` either way), so the fixture is the only reach |
| S482 | — | DFA hat, `first-memchr` (`\|T\| = 1`): re-seed deleted | answer identity | `\bab\b` (`T = {a}`): on `bab ab`, the skip lands at 1 in the wrong context (verify) |
| S483 | — | DFA hat, `first-class-bounded`: one of the two landing paths' re-seed deleted (the `n − 1` stop) | answer identity | a `\b`-class fixture whose only `T` byte is the subject's LAST byte (verify) |
| S484 | — | DFA hat, `first-memchr-bounded`: the same, memchr form | answer identity | the same shape, `\|T\| = 1` (verify) |
| S485 | — | DFA hat: the re-seed made UNCONDITIONAL (sound-F7) | codegen structural check: every DFA-hat mover's re-seed sits under `if (scan_position > entry…)` | ~~answer-invisible on F's population~~ **withdrawn by §6.4.3 item 1**: the unconditional form loses matches on ordinary seeded movers; its answer witnesses are `reseed.rxt`'s RS blocks. The structural check is a second detector; its population is the DFA-hat manifest |
| S486 | S480 | `T` widened by one byte that cannot begin a match (cost only, firstset §9) | codegen check, **expectation corrected**: on every DFA-hat mover the emitted table EQUALS `start_set` (the `--emit-facts` row) and is a PROPER SUBSET of the `-fno-start-set` arm's table. r3's "`start_set` ∩ the deny table" pinned the sound-F1 defect | the aws-shaped fixture, `\|T\| = 1` |
| S487 | — | F's SEEDED conjunct removed | none possible: on an unseeded machine `E ⊆ S` (C-SS*), so `T == E` and the row is transparent | **declared UNREACHED by construction**; C-SS* is its guard |
| S488 | — | F's NON-NULLABLE conjunct removed | answer identity (lost empty matches at skipped positions) | a seeded byte-class artifact with a nullable `S`. The build's sweep looks for one; if the population is empty it is declared UNREACHED with that count (verify) |
| S489 | — | F's `\|S\| < 256` conjunct removed | none possible: `S` = all 256 ⇒ `T == E`, not a proper subset | **declared UNREACHED by construction**; the `T ⊊ E` conjunct is its guard |
| S490 | — | F's SCAN-KIND conjunct removed (sound-F7) | codegen structural check: no `RX_DFA_SCAN` attempt artifact carries a `first-*` `DFA_PREFILTER` value | a `\G`- or `(?m)^`-led seeded artifact (verify reach on the corpus) |
| S491 | S482 | V's NON-NULLABLE conjunct removed | answer identity | `a*b?` **under `--engine=vm`** on `zz` → (0,0) (verified on r3's build; at `auto` it is a DFA artifact) |
| S492 | — | V's UNANCHORED conjunct removed | codegen structural check: no artifact with `start_anchor != unanchored` carries `_VM_START_SCAN != "none"` | probably answer-invisible (an anchored attempt that is moved still fails its own anchor); the structural check is the detector (checks-F4) |
| S493 | — | V's NO-PREFN conjunct removed (a hybrid also takes the VM hat) | codegen structural check: every hybrid reads `_VM_START_SCAN "none"` | the ctx-* hybrids |
| S494 | S484 | `pcrec_artifact_has_dfa_scan` returns true on a VM-hat artifact | K65/K66 `gu`/NOMATCH cells | `tests/base/k65_precheck_whole_set.rxt` (a VM-hat mover, §4.2). **A solo run confirms the detection before numbering**: the plant goes into a function that has no VM-hat knowledge today |
| S495 | S485 | `pcrec_dfa_cand_ppm` re-reads the row NAME (K84 regression) | the re-seed row stamp on a hybrid mover | the aws hybrid fixture |
| S496 | — | V's verbs/callouts conjunct removed (§3.3) | none possible today: every verb and callout refuses at compile | **declared UNREACHED**, with a compile-time assertion beside it (S475's precedent). r3's §3.3 promised this row and r3's §6.3 omitted it (checks-F4) |
| S497 | S483 | the utf8 start-byte assertion removed | none possible: the population is empty by construction (§3.4) | **declared UNREACHED**, with a compile-time assertion beside it, evaluated AFTER the non-nullable and `\|S\| < 256` conjuncts (sound-F4) |
| S498 | S481 | walk: the `A_CALL` arm returns ∅ (drops its bytes) instead of all/nullable | answer identity (VM hat) | `(?1)x(y)` **under `--engine=vm`** on `yxy` → (0,3) (verified on r3's build). At `auto` the pattern is a hybrid, so the fixture pins the engine |
| S499 | — | walk: the `A_BREF` arm returns ∅ | answer identity (VM hat) | `(?=(a))\1b` on `ab` → (0,2): the plant makes `S = {b}` and the seek skips the `a` (checks-F4's witness; verify) |
| S500 | — | walk: the `A_VAR` arm returns ∅ | answer identity (VM hat) | a `${v}x`-led `tests/vars/` fixture with `v = a` (verify; module `vars`) |
| S501 | — | walk: a zero-width arm (`A_LOOK`/`A_CTX`) read as CONSUMING its set | C-SS* (measured: `look-eats` 118 violations, 74 seeded) + answer identity on both hats | `(?:(?<=a)z\|w)` (DFA hat): the plant gives `S = {a,w}` |
| S502 | — | walk: `A_CAT` drops the `null(l) ? F(r)` term | C-SS* (measured: `cat-null` 367 violations) + answer identity | `(?<=a)z` **under `--engine=vm`** on `az` → (1,2): the plant gives a non-nullable `S = ∅`, so the seek finds no candidate and the call returns 0 (verify) |

Each row's `SAB_REACH` is born with it (opt5 §5's discipline).

### 6.4 Edge cases and detection (lane `ssedge`, D148 addendum 1)

Frank's direction (D148 addendum 1): the set argument is an argument, not a
proof, so the EDGES carry the evidence, and the planned tests must be shown
to SEE each wrong variant at ANSWER level. This section is that evidence.
Instruments and verbatim transcripts: `startset/edge/` (own CLAUDE.md;
`run.sh` reproduces everything).

**What exists.**
- **80 edge blocks, 2,070 cells**, as DRAFT `.rxt` in the house format
  (10 files, 2,022 cells) plus `utfcheck_cells.tsv` (48 `-futf-check`
  cells, which no `.rxt` directive can compile). Every cell is asked at
  EVERY startpos that is a character boundary of its subject.
- **Every answer is libpcre2's.** The cells are generated from `cells.py`
  (pattern, options, subjects, edge key, reason) by `gen_rxt.py`; no answer
  is typed by hand.
  - Local 10.48 and the 10.46 reference (ubuntubudu, one compile + 2,070
    matches, `out/oracle_ref_10.46.host`) agree on **2,070 of 2,070**
    cells. The writer refuses any cell on which they disagree.
  - Today's emitter (the `-fno-start-set` arm) agrees with **every** cell:
    0 base disagreements over the 80 blocks. So the cells are true of the
    pre-change program, and any red on the build is the hat's.
- **The mutation run** (`edge/mut.py`) reads the drafts BACK (the cells as
  written, not their source). For every block it builds the base, the
  CORRECT hat twin, and every mutant whose shape applies. DETECTED means
  some cell's answer differs from the cell's expectation. A sweep arm
  (twin vs base over every subject on the block's alphabet up to length
  6, every startpos) says whether a mutant the cells miss is observable on
  that machine at all.
- **Iterated to closure.** Every mutant the sweep saw and no cell saw got
  its sweep witness added as a subject, and the run was repeated, until no
  block had a MISSED variant (four rounds; the witnesses are the subjects
  `azz`, `babx`, `xz`, `abza`, `xzx`, … in the drafts).

#### 6.4.1 Coverage of the edge list

| D148 addendum 1 / brief item | blocks (edge key) | hat reached |
|---|---|---|
| the six sound-F1 corpus witnesses | `witnesses.rxt` (W): `matrix.rxt:1064/1122/2597/2662`, `lookbehind.rxt:212`, `ucp/ctxnode.rxt:400` | none: all six are DECLINED by the ruled admission (`S ⊄ E`); r3's set ADMITS them. They are where the set bug is seen |
| lookbehind context across the skip, 1..k bytes, multi-byte, nested | LB2, LB3, LBN, LBNEG: `\b(?:(?<=bc)d\|w)`, `(?<=ab)z\|\bw`, `(?<=abc)d\|\bx`, `(?:(?<=b(?<=ab)c)d\|\bw)`, `(?:(?<!a)z\|w)` | DFA hat on hybrids and DFA. A multi-byte lookbehind ALONE (`(?<=bc)d`) is a `memchr` hybrid, not a mover: the prefilter erases it, so it needs a one-byte context (`\b`) beside it to be seeded |
| an `S \ E` byte startable only after k context-changing skipped bytes | LBK, W3 | the seed is the class of the LAST skipped byte, so k bytes are the 1-byte case repeated: `bbbaz`, `abbbz`, `babaz` |
| `\b` / `\B`, both polarities, ASCII and `--ucp` | WB, WBU (0xE9/0xAA are word bytes under `--ucp`) | DFA hat. **`-e utf8 --ucp \b` is refused today** ("UCP `\b` is not built yet under encoding utf8"), so the utf8 half has no cell to write |
| `(?m)` under every newline convention | ML | pcrec builds LF ONLY (`DEF_NEWLINE_CONV` has no producer, D64; `(*CR)`/`(*CRLF)`/`(*ANYCRLF)`/`(*ANY)`/`(*NUL)` are refused, `tests/reject/run_reject_tests.sh:1650`). The cells pin `\r` and `\r\n` as ORDINARY bytes in context and before `$` |
| utf8: a continuation byte as the context; ill-formed bytes; `-futf-check` | U8, UC | `(?:(?<=é)a\|\bw)` (the context's last byte is A9), lone C3/80/FF around contexts; DFA- and VM-hat `-futf-check` blocks |
| caseless | CI, U8CI, VMI, VMU | case twins in `T`; KELVIN SIGN (E2 84 AA) as a context and as a start-set LEAD byte |
| `search_from > 0`, context from the byte before it | every block (every startpos) + SF | — |
| subject start, end, empty | BD | the bounded skip's `n − 1` stop |
| `\G` | BG, VMG | **no `\G` machine reaches the DFA hat by construction**: `N_GSTART` ⇒ `pcrec_nfa_has_bot` (`src/ir/nfa.c:1221`) ⇒ `PCREC_ENG_ATTEMPT` (`src/core/compile.c:1873`) ⇒ F's scan-kind conjunct declines. The BG blocks are non-mover controls |
| hybrid; count-collapsed hybrid, with a witness that FAILS without the re-seed | HY, HYC | **found** (sound-F5(d)): see §6.4.3 item 4 |
| the capacity give-ups of Q-R3 | GU | `(?=(?:a\|b\|x)*c)x`, `budget frames=8`: the deny arm gives up at 0 and the correct VM hat answers (24,25), as Q-R3 says. Trail and caller-buffer `_in` capacities have NO cell (the drafts' reader routes `_search` only), OWED at stage 2 |
| VM hat: backrefs to empty groups, recursion, lookahead-first, nullable decline | VMB, VMR, VML, VMN, plus VMC (`(?1)`), VMW, VMK (`\K`) | VM hat |
| the re-seed's FORM, and the `first-memchr-bounded` landing paths | RS, M1 | added by this lane (§6.4.3 items 1 and 3) |

#### 6.4.2 The mutation table

Per mutant: the blocks it was BUILT on (others decline it, or it builds a
table identical to the correct one), how many of those a CELL detects, and
the first detecting cell. "MISSED" (sweep sees it, no cell does) is 0 for
every row after closure. `out/mut_summary.txt`, `out/mut.variants.tsv`.

| mutant | built on | detected by cells | first detecting cell | verdict |
|---|---|---|---|---|
| **correct DFA hat** (D0: `T = S ∩ E*`, `T ⊊ E`, conditional re-seed) | 41 movers | 0 (sweep: 0 diffs on all 41) | — | the control: the cells pass the correct build |
| `T = S ∩ E` (r3, the sound-F1 bug) | 16 (all non-movers) | **16** | `witnesses.rxt` `(?:(?<=a)z\|w)` `ms 0 "aza"` → (1,2), twin 0 | DETECTED. On every MOVER it is the identical table (`S ⊆ E`), so S480 reaches only non-movers, by construction |
| E\* missing one seed state (each `k ≠ s0`) | 14 | **14** | as above | DETECTED where the machine has exactly 2 seed states (it then IS r3's set). On the other 46 blocks it declines or builds the IDENTICAL table (with 3+ seed states E\* is still 256): an equivalent mutant, §6.4.3 item 6 |
| E\* missing s0 | 10 | **7** | `witnesses.rxt` `(?:\bab\|x)` `ms 0 " ab"` → (1,3), twin 0 | DETECTED: on a `\b`-machine the word-context seed alone does not escape on `a` |
| re-seed removed | 41 | **26** | `wordb.rxt` `\b(?:ab\|cd)\b` `ms 0 "bab ab"` → (4,6), twin 0 | DETECTED (15 blocks where the stale s0 is harmless) |
| re-seed UNCONDITIONAL (`pos ? seed[..] : s0`) | 41 | **6** | `reseed.rxt` `(?:\b\|xy)a` `ms 0 "xya"` → (0,3), twin 0 | DETECTED — on ordinary seeded movers, not on `\G` (§6.4.3 item 1) |
| seek before `rx_valid_upto` (DFA hat) | 1 | **1** | `utfcheck_cells.tsv` `\b(?:ab\|cd)\b` -futf-check on `\xff` → −9, twin 0 | DETECTED |
| seek from `search_from` instead of `max(search_from, lo)` (DFA hat, handoff movers) | 3 | 0 (sweep 0) | — | UNOBSERVABLE: an equivalent mutant (§6.4.3 item 7) |
| `first-memchr-bounded`, hit-path re-seed deleted (S483/S484) | 5 | **3** | `reseed.rxt` `\B(?<!a)d` `ms 0 "xdz"` → (1,2) | DETECTED, only under a RESTRICTIVE context (§6.4.3 item 3) |
| `first-memchr-bounded`, clamp-path (`n − 1`) re-seed deleted | 5 | **2** | `reseed.rxt` `\B(?<!a)d` `ms 0 "xd"` → (1,2) | DETECTED, same |
| `T` missing one member (DFA) | 84 drops | 54 | `wordb.rxt` `\b(?:ab\|cd)\b` drop `a`: `ms 0 "ab"` | DETECTED per member the cells start a match with |
| `T = Tdfa` (§4.1a's "would also be sound") | 2 | **1** | `witnesses.rxt` `(?:\b\|x)y` `ms 0 "xy"` → (0,2), twin 0 | **the claim is FALSE** (§6.4.3 item 2) |
| **correct VM hat** (V0) | 13 | 0 (sweep 0) | — | the control |
| seek one byte late (S479) | 13 | **13** | `vmhat.rxt` `\((?:[^()]\|(?R))*\)` `ms 0 "(a)"` → (0,3) | DETECTED on every VM block |
| `S` missing its first byte | — | yes | `vmhat.rxt` `(ab)\1` drop `a`: `ms 0 "abab"` | DETECTED |
| `S` missing a caseless twin | — | yes | `vmhat.rxt` `(?i)(ca)t\1` drop `C`: `ms 0 "Catca"` | DETECTED (1 cell; the sweep's own reach is 8 cells) |
| `S` missing a utf8 LEAD byte | — | yes | `vmhat.rxt` `(k)\1` `-i -e utf8` drop E2: `ms 0 "\xe2\x84\xaak"` | DETECTED |
| (all VM `S`-member drops) | 23 | 20 | — | the 3 undetected drop a member no cell starts a match with (`0` from `\w`): §6.4.3 item 8 |
| nullable treated as non-nullable | 1 | **1** | `vmhat.rxt` `a*b?` (forced VM) `ms 0 ""` → (0,0), twin 0 | DETECTED |
| retry seek skips a valid later start | 13 | **11** | `vmhat.rxt` `(ab)\1` `ms 0 "aabab"` → (1,5) | DETECTED (2 blocks with no failing-then-valid adjacent pair) |
| seek before `rx_valid_upto` (VM hat) | 1 | **1** | `utfcheck_cells.tsv` `(\w)\1x` -futf-check on `\xff` → −9, twin 0 | DETECTED |
| seek from `search_from` instead of `max(search_from, lo)` (VM hat) | 0 | — | — | NOT BUILDABLE: no VM-hat artifact carries a handoff (item 7) |

**Every mutant the brief lists is DETECTED at answer level by a draft cell,
except two that are EQUIVALENT on every machine pcrec can build** (the
seek-start mutant on both hats, and E\* without one seed on 3+-seed
machines). §6.4.3 items 6-7 give the argument and name the check that sees
each.

#### 6.4.3 Findings

1. **The unconditional re-seed loses matches on ORDINARY seeded movers,
   not only on `\G`** (sound-F7 and S485 are wrong about where the hazard
   lives).
   - **Witness**: `(?:\b|xy)a` on `xya` → (0,3); the unconditional twin
     returns 0. Mechanism: after `xy` the forward machine is back in state 0
     (s0's future: `a` now matches), but `seed[class(y)]` is the
     word-context seed. When the skip does not move at `q == entry`, the
     unconditional form overwrites a CORRECT state 0 with that seed.
   - **Measured** (`search_uncond.py`, a random 2-3-branch family over
     `\b \B (?<=a) (?<!a) x y ab …`): 6 of 84 DFA-hat movers differ under the
     unconditional form; 0 of 84 under the conditional one. Two of the six
     lose where NO re-seed at all does not (`(?:abz|x(?<=[ab])|\bz)y`,
     `(?:\b(?<!a)a|a[xy]a|\ba)z`). On the 56 census movers at rev 2's
     alphabets: 0 (`census_reseed.py`), so no shipped mover reaches it today.
   - **Consequence**: the conditional form is a SOUNDNESS requirement. S485
     keeps its structural check and gains answer witnesses (`reseed.rxt`,
     edge RS); its "answer-invisible on F's population" is withdrawn.
2. **`Tdfa` is not a sound floor; §4.1 step 2's stated condition and
   §4.1a's "Tdfa alone would also be sound" are refuted.** The ruled rule is
   unaffected.
   - **Witness**: `(?:\b|x)y` on `xy` → (0,2). Here `δ(s0, x) = s0` and
     `δ(word, x) = s0` (after `x`, a `y` matches, exactly as at a nonword
     context), so `x` never leaves the seed set and `x ∉ Tdfa = {y}`. But
     `seed[class(x)]` is the WORD seed. Skipping `x` and re-seeding lands in
     the wrong state, and `T = Tdfa` loses the match. (The block is a
     non-mover — `x ∈ S \ E` — so only a `T = Tdfa` build would reach it.)
   - **The corrected argument** (it replaces §4.1 steps 1-3's wording): a
     skipped byte `b ∉ S` begins no match in ANY context. So the state after
     it has exactly the future of the startpos state with context `b`, i.e.
     `seed[class(b)]` — equality of minimized states is equality of future
     languages. By induction over the skipped run, the re-seed is exact iff
     every skipped byte is outside `S`, i.e. iff `T ⊇ S`. `E` plays no part
     in soundness (only in admission and cost), and "state 0 means no live
     thread" (step 1) is not true of a minimized machine (state 0 is
     RE-ENTERED with in-flight threads, item 1), and is not needed.
   - **For the checks**: C-SS\* (`Tdfa ⊆ S`) still holds and stays a valid
     WALK check, but it cannot certify a `T`: only the start-byte oracle
     (every byte that begins a match is in `T`) and the answer cells see a
     too-small `T`. A `T` derived from the machine instead of from `S` would
     pass C-SS\* and lose matches.
3. **The DFA hat has no unbounded population; only the `-bounded` rows are
   reachable.** A machine whose start depends on a context byte carries a
   class context (`clsctx`), and `wctx ⇒ views` (`emit_dfa.c:4184-4189`),
   so its skip is the `-bounded` form. The build should ASSERT "seeded ⇒
   views" rather than rely on this reading. Measured: 170 of 170 seeded census artifacts carry a
   `-bounded` prefilter or none (`byte-class-bounded` 94, `offset-set-bounded`
   35, `memchr-bounded` 26, none 15). So the DFA-hat columns of
   `first-class` and `first-memchr` are UNREACHABLE by construction.
   - **The bounded landing paths are answer-visible only under a
     RESTRICTIVE context.** With `\b`-only movers the stale s0 is
     permissive (it can only add a candidate the reverse pass or the VM
     rejects), so deleting either path's re-seed was unobservable on 2 of
     the 5 `|T| = 1` movers. Under `\B` or a negative lookbehind the stale
     s0 forbids a real start: `\B(?<!a)d` on `xd` (the `d` is the last byte,
     so `memchr` over `[0, n−1)` misses and the clamp path lands) and on
     `xdz` (the hit path).
4. **The count-collapsed obligation has its FAILING witness** (sound-F5(d)).
   `search_uncond.py FAMILY=collapsed` (`X{m,n}` cores, `-fprefilter-collapse`):
   **36 of 97 collapsed hybrid movers lose without the re-seed, 0 with it.**
   The critic's two patterns read 0 because their collapsed core repeats,
   so the reverse pass recovers the earlier start (§4.1's own "start below
   q" reading). The witness needs a core whose first copy is the only
   copy: `\B(a|b){1,3}` on `xa` → (1,2); `\B(x|ab){1,2}\b` on `zx`
   (`hybrid.rxt`, edge HYC, built through a `-fprefilter-collapse`
   target).
5. **Re-seed REMOVED is answer-visible on 26 of 41 movers**; on the other
   15 the stale s0 is permissive (item 3's reason), which is why S481/S483
   need `\b` fixtures with a FOLLOWING real match (`bab ab`, `babx`) and
   `\B` fixtures (`xabx`).
6. **E\* without one seed state is an EQUIVALENT mutant on every mover.**
   - With 3+ seed states, E\* is still all 256 without any one of them (a
     byte that begins no thread moves every OTHER seed to `seed[class(b)]`),
     so the emitted table is identical.
   - With 2 seed states, dropping the non-s0 seed gives r3's `S ∩ E`, which
     equals `S` on every mover. It is visible only on the six non-mover
     witnesses, which the mutant ADMITS.
   - **What sees it**: no answer and no check on the artifact can, because
     the artifact is unchanged. The §4.1a build assertion "`T == S` on every
     mover" (equivalently `|E*| == 256` on every seeded machine) is the
     guard. It fires at compile time for every non-equivalent E\* defect.
7. **The seek-start mutant (`search_from` instead of `max(search_from,
   lo)`) is equivalent on both hats.**
   - **VM hat**: no VM-hat artifact has a handoff. `req_handoff_applies`'s
     premise (a) requires a DFA scan, and `emit_vm.c:13411` fails the
     compile if the handoff reaches a VM-none artifact. So
     `max(search_from, lo)` is `search_from`.
   - **DFA hat** (built: the scan starts at `search_from` with the state the
     handoff seeded for `lo`): every match contains the run within K of its
     start. So no match, and no false accept under the wrong context, can
     start in `[search_from, lo)`. Measured: 0 diffs on the 3 handoff movers.
   - **What sees it**: a structural check, "no artifact with
     `_VM_START_SCAN != "none"` has `REQ_HANDOFF != "none"`", and a cost
     read. No answer can.
8. **Per-member `S`/`T` drops are seen only for the members the cells start
   a match with.** `(\w)\1x` without `0` is undetected by every cell and by
   the sweep. Full membership is a POPULATION question, and the start-byte
   oracle (§6.2) is its detector. The cells pin the ROLES (first byte,
   caseless twin, utf8 lead) and the oracle pins the rest.

#### 6.4.4 Homes in `tests/` and the sabotage rows they pin

The drafts become HAND files under `tests/startset/` at the build stage of
their hat, keeping `cells.py` + `gen_rxt.py` as their generator (the
`tests/utfcheck/` shape: the authored half and a committed 10.46
transcript). The sweep arm becomes the stage-2 every-startpos differential
of §6.2 (GENERATED, `run_startbnd_diff.sh`'s shape) over these blocks'
alphabets.

| edge keys | draft | home | stage | pins (§6.3) |
|---|---|---|---|---|
| W, W3 | `witnesses.rxt` | `tests/startset/dfahat.rxt` | 3 | **S480** (its ONLY reach, by construction: item 6), S501 (`(?:(?<=a)z\|w)`), C-SS\*, the start-byte oracle |
| S0, LBK | `witnesses.rxt`, `lookbehind.rxt` | `tests/startset/dfahat.rxt` | 3 | the §4.1a `T == S` assertion's answer witness (E\* without s0); S480 |
| LB2, LB3, LBN, LBNEG | `lookbehind.rxt` | `tests/startset/dfahat.rxt` (+ hybrid) | 3 | S481/S483 (re-seed deleted, bounded), S493 on the hybrids |
| WB, WBU, CI, SF, BD | `wordb.rxt`, `bounds.rxt` | `tests/startset/dfahat.rxt` | 3 | S481/S483, S486 (WBU/CI with the options read, sound-F4) |
| HO | `wordb.rxt` | `tests/startset/dfahat.rxt` | 3 | the handoff composition (item 7's structural check) |
| RS, M1 | `reseed.rxt` | `tests/startset/reseed.rxt` | 3 | **S485** (answer witnesses), **S483/S484** (the two landing paths) |
| ML | `multiline.rxt` | `tests/startset/dfahat.rxt` | 3 | S480 (`ctxnode.rxt:400`), S490 (the `(?m)^` attempt scan) |
| U8, U8CI | `utf8.rxt` | `tests/startset/dfahat.rxt` (`encoding utf8` blocks) | 3 | S497's guard order (sound-F4), S486 |
| BG, VMG | `bounds.rxt`, `vmhat.rxt` | `dfahat.rxt` / `vmhat.rxt` | 2/3 | S490 (scan kind), S485's `\G` argument |
| HY, HYC | `hybrid.rxt` (head: the collapse targets) | `tests/startset/hybrid.rxt` | 3 | S481/S483 on the hybrid, S493, the sound-F5(d) obligation |
| VMR, VMB, VML, VMC, VMW, VMK | `vmhat.rxt` | `tests/startset/vmhat.rxt` | 2 | S478, S479, S498 (`(?1)x(y)`), S499, the V2/V4 mutants |
| VMN | `vmhat.rxt` | `tests/startset/vmhat.rxt` | 2 | **S491** (`a*b?` forced VM), S488 |
| VMI, VMU | `vmhat.rxt` | `tests/startset/vmhat.rxt` | 2 | S478 (caseless twin, utf8 lead) |
| GU | `giveup.rxt` | `tests/startset/giveup.rxt` | 2 | the Q-R3 allowance (§6.2's give-up row) |
| UC | `utfcheck_cells.tsv` | rows of `tests/utfcheck/gen_cases.py` + its 10.46 transcript | 2/3 | NO §6.3 row: **proposed S503/S504** (the no-candidate return hoisted above `rx_valid_upto`, VM / DFA) |

**§6.3 rows the mutation run shows WEAK or mis-aimed.**
- **S482** (`first-memchr`, re-seed deleted): its witness `\bab\b` is not
  a mover at all (`offset-set-bounded` wins first), and the unbounded
  DFA-hat form has no population (item 3). Declare it UNREACHED by
  construction, with an assertion (seeded ⇒ views ⇒ `-bounded`), or
  retarget it at `first-memchr-bounded` with `\B(?<!a)d`.
- **S481** (`first-class`, re-seed deleted): the same. Its witness
  `\b(?:ab|cd)\b` is a `first-class-BOUNDED` artifact, so S481 and S483
  plant the same row. Fold S481 into S483, or declare it UNREACHED.
- **S483/S484** ("verify"): measured witnesses now exist, and they must be
  RESTRICTIVE-context movers (item 3). `\b`-only fixtures read 0.
- **S485**: no longer structural-only (item 1). Its answer witnesses are
  `reseed.rxt`'s RS blocks. Its population on the corpus is 0 of 56, so the
  fixtures are its only reach.
- **S480**: sound, but its reach is ONLY the six non-mover fixtures (the
  plant equals the correct table on every mover). The plant must also
  carry r3's ADMISSION (`S ∩ E ⊊ E`), or it is the identical program and
  reads UNREACHED.
- **C-SS\***: right as a walk check, but item 2 means it cannot stand in for
  the start-byte oracle as the check on `T`. §6.2's table should say that the
  oracle, not C-SS\*, is the detector for a too-small `T`.
- **No row** covers the seek placed before `rx_valid_upto` (D148 addendum 1
  lists it). Proposed S503 (VM hat) and S504 (DFA hat), with the UC cells as
  witnesses.

#### 6.4.5 What is owed, and the standing questions

- **Owed**: trail and caller-buffer (`frames-buffer=`) give-up cells (GU
  covers frames only); `-e utf8 --ucp` word-boundary cells once [UCP] U3/U4
  builds it; the drafts' move into `tests/` (§6.4.4) at each hat's stage.
- **Q1, the measurement regime**: answers only. No clock is read. The
  oracle is two libpcre2 builds (10.48 Mac, 10.46 Linux), and they agree on
  every cell.
- **Q2, the independent control**: each cell's expectation comes from
  libpcre2, never from pcrec, and the twins share no code with the oracle.
  The run's own controls are the correct twins (0 diffs on all 54 hat
  blocks) and the base (0 disagreements). The sweep is a second detector,
  and it is what found every cell added in closure.
- **Q3, what moves when regenerated**: `gen_rxt.py write` rewrites the
  drafts from the oracle transcripts. A changed answer is a changed oracle,
  and with REF given the writer refuses it. Nothing emitted moves; no abi
  event.

---

## 7. Alpha plan (D144 + addendum 3) and the landing bar

**Per change** (each stage below is its own commit and its own alpha):
- `make test`;
- test-axes over its own flag (`AXES="-fno-start-set"`), PLUS the new
  PRODUCT ARM (`--engine=vm` against `-fno-start-set --engine=vm`, with its
  own baseline and a mover floor). `run_axes.sh` sweeps axes at auto only
  today (`:50-52`), so "both engines" needs that arm (rev 2, checks-F3). The
  engine axis also runs under `-fno-start-set` (sound-F8). The every-startpos
  differential runs plain and under ASan/UBSan (§6.2);
- its own mech rows;
- **an ASan/UBSan pass over its own movers**, because both hats change how
  emitted code reads memory. The VM hat adds a subject scan. The DFA hat adds
  the re-seed's `subject[q−1]` read. That read is safe at any `q > 0`: the
  emitted guard is `pos ? seed[…] : s0` (`emit_dfa.c:6373`), and the new
  rows' conditional form adds `q > entry` (§4.1 step 4). r3 attributed the
  safety to `q > entry` alone (checks-F11);
- the targeted Linux timing: `taskset`-pinned, via the executor channel, with
  base against deny as the noise floor (D144 addendum 1). Short-call cells are
  absolute deltas against that floor;
- **every reading records the libc** (glibc version on Linux) and reports
  BOTH layers (D147, rev 2 cost-F7). `first-memchr`'s dispatch is a libc
  layer. After the VMSTART/T1 PF migration, the cells are re-read with
  `-fmemfn-simd` on and off.

**Landing bar: IMPROVE** (D119's measured-gap bar on each named cell):

| hat | cells |
|---|---|
| DFA | capability aws thr; litrun aws thr; json-constant thr; dbnames thr; loglines bignum thr; hex32-id thr |
| DFA, secondary (the CTX group) | level-context thr + short; ctx-lazy-64/256/1024 and ctx-greedy-256 thr |
| VM (auto) | quoted-delim thr (+ short, tier C absolute); balanced-parens-rec thr; bak-k-named thr |
| VM (`--engine=vm`, the pcrec-vm testee) | mod-i, mod-r, cls-fold-pair, cls-pair-ctl, ci-strasse thr (K82's forced-VM losses, +0.64..+2.02 ns/B); aws forced-VM (Mac scratch ×12.2, against forced-VM walking every position. **Not an auto cell** (rev 2, cost-F2): at auto, aws is a hybrid and takes the DFA hat) |

**Per VM improve cell (rev 2, cost-F3)**, besides its throughput cell:
- a MATCH-DENSE subject (JSON strings for quoted-delim, tag-dense for the
  tag cells, paren-dense for balanced-parens). capability `t-1m` has `"` at
  0.57% and `(` at 0.58%, so every r3 improve cell sat on the sparsest
  subject;
- a SHORT-CALL cell: absolute ns against the base/deny floor, the K88
  shape. The per-call entry is what a match-dense find-all pays.
- **bak-k-named has no measurement at all.** Mac read ×1.0, and the syntax
  subject is not local. Its first reading is a bench request (relayed, never
  reverse-engineered from the bench's ledgers).
- **A forced-VM cost read on a SECOND subject class** (rev 2, cost-F8): one
  log-shaped and one JSON-shaped subject over the pcrec-vm testee's movers.
  This rides Q-R2's recommendation: no early gate, but a stage-2 read
  beyond capability `t-1m`.

**DO NOT REGRESS**:
- **Non-movers** (program-identical, the null band): floor-byte thr/srch,
  high-byte-run thr, uuid-near-miss srch, union-select, ci-ascii-control.
  **The null band is per CONFIGURATION** (rev 2, cost-F6). These are
  non-movers at auto only. The census shows them DFA-route at auto, and
  under `--engine=vm` (the table the forced-VM improve cells come from)
  they are VM-hat MOVERS. So at `--engine=vm` they are guard cells, not
  null cells.
- **Movers expected flat-to-better**: wild-logparse-quotedstring-grok thr (it
  moves: 4 → 3 bytes), kv-quoted, wb-256/512 (d 56-57%).
  **[rev 2, cost-F5] Each cell states its expected sign**:
  - kv-quoted, wb-256/512: sign `0` (flat). Above d ≈ 20% the narrowing's
    gain vanishes (§4.4) while `r` is paid, so a loss up to the floor is
    possible. Each is read against the deny floor.
  - hex32-id (32%), dbnames (22%), bignum (12%): sign `0` or `+`. Under
    D144 addendum 1 they may read NULL against an IMPROVE bar. Their row
    in the IMPROVE table stays, labelled "may read null".
  - grok (4 → 3, d 0.57%) and float-literal-bound (11 → 10): ONE-BYTE
    narrowings with expected effect ≈0. They are NULL cells with a deny
    floor: re-seed fixed-cost cells, not null controls.
- **Dense-`S` VM guard cells**: doubled-word, bak-1 (`|S|` = 63); one
  dense SINGLE-byte VM-none cell (constructed, e.g. `e(\w)\1` on prose) for
  the per-attempt `memchr` entry (§4.4).
  **[rev 2, cost-F1/F3]**
  - The `e(\w)\1`-on-prose cell has d = 8.5%, where the sweep shows almost
    no loss. It is kept, and joined by the measured loss regime itself:
    `a(\w)\1` at d = 33% and d = 80% on a match-dense subject. Those read
    ×0.9 table and ×0.6 memchr on the Mac.
  - A `|S| ≥ 128` cell (`.`-led, `|S|` = 255).
  - An S == REQ_BYTE hit-dense cell (cost-F4: the pre-check and the seek
    scan the same byte, §4.2). This cell is the trigger of the filed VM-hat
    dominance/handoff row.
- **A pre-check-dominated VM mover**: nested-comment-rec, where FREQPICK's
  absent `*` answers first, so a null result is expected.

**Mac scratch, directional only** (`startset/twin/tdrv.c`, find-all on
capability `t-1m`, M1, gcc-16 -O2, best of 5, answers checked equal).
[rev 2, cost-F2]
- **Every number below is the TABLE form.** `vmtwin.py` always emits the
  256-entry table loop, even at `|S| = 1`. The `first-memchr` form was never
  timed by the r3 lane. The critic timed it on libSystem: balanced-parens
  ×7.9-8.5. glibc's call term (~3.4 ns, k82cost Q7) is unmeasured for the
  VM hat, and its Linux timing is OWED in the stage-2 alpha.
- **There was no deny-style null control.** The twin is a separate TU with
  a different prefix, so layout was argued away by magnitude only, which
  works for ×6 and not for ×1.0 rows. Cold start is excluded.
- **Against the gap report**: ×6 on quoted-delim still leaves ≈×3.6 against
  the JIT (auto 7.214 ns/B, JIT 0.336). ×3.4 on balanced-parens leaves
  ≈×2.7. That passes an IMPROVE bar and does not close the gap.

| pattern | base | VM-hat twin | |
|---|---|---|---|
| quoted-delim-match | 3.304 ns/B | 0.555 | ×6.0 |
| balanced-parens-rec | 2.376 | 0.696 | ×3.4 |
| aws `--engine=vm` | 4.441 | 0.365 | ×12.2 |
| `(?i)cat`, `c[aA]t` (`--engine=vm`), bak-k-named | — | — | ×1.0: the K65 pre-check answers first on this subject (no `cat`, no `</`). Their cells are the syntax set's own subjects (not committed); Linux alpha owed |

**Owed measurements**:
- **F3** (the re-seed's cost). It is folded into the DFA hat's alpha: deny
  against base on json-constant and aws, and (rev 2, cost-F5) on the DENSE
  movers too: kv-quoted, wb-256/512, hex32-id. That is where `r` is least
  amortized.
- **F4** (firstset §7). This is the VM hat's alpha above.
- **The `first-memchr` form at Linux/glibc** (cost-F2). It is moot at stage
  2 if Q-R5 (a) is ruled; then it moves to the kit's migration.
- **The count-collapsed hybrid FAILING witness** (sound-F5 (d), §4.1),
  stage 3.

---

## 8. Staged build plan (implement-then-replace, D124 item 4)

| stage | content | movers / abi |
|---|---|---|
| 0 | K84's fix: the row's `scan` field, both readers re-pointed. **+ (rev 2, checks-F10) a structural check that no `strcmp` on a `dfa_pfs[]` row name remains** (S495 only becomes reachable at stage 3) | none. **Gate (checks-F10):** `scripts/emit_sweep.py --ref <branch point>` over its five streams, REACH figure reported; plus the identity gates |
| 1 | the `start_set` core fact (`src/facts/startset.c`, `--emit-facts` row); **C-SS\* as a check in `tests/`** (rev 2: every machine, seeded included; walk plants as its failing direction; pinned to read the shipped fact row, never a probe), **the `NULLABLE ⇒ start_set.nullable` check**, the flagged (`-i`, `--ucp`) witnesses; `DfaSel`/`DfaPf` gain `route` (designated initializers + the structural check, checks-F6), the route mask, the `StartSet` pointer and the VM hook slot (NULL); the shared FIND-loop emitter extracted (`pcrec_`-prefixed); **the census re-run with per-block options** (sound-F4) and the stage-2/3 mover MANIFESTS generated from it | none. **Gate:** `emit_sweep.py` (REACH reported) + the identity gates. `--emit-facts` is a debug listing; `docs/spec/facts_listing.md` gains its row |
| 2 | **VM hat**: row `first-class` (and `first-memchr` only if Q-R5 keeps it) with V and the VM hook; `-fno-start-set` (bit 47); `<PREFIX>_VM_START_SCAN` on EVERY artifact (checks-F1); VMSTART manifest row (budget 2); S478, S479, S491-S494, S496-S500 (§6.3); fixtures; the give-up spec sentence (with capacity, Q-R3); the run_axes PRODUCT ARM and the every-startpos differential (checks-F3); the VM-hat start-byte oracle as a standing check | auto 17 bench / 59 corpus, forced 273 / 2,263 (the census's; the manifest pins the build's own); **abi event** (next number) |
| 3 | **DFA hat**: F (rev 2: `T = S ∩ E*` admitted iff `T ⊊ E`, scan-kind conjunct, Q-R1) on the four rows, `-bounded` twins, the CONDITIONAL re-seed through wrapper emitters; S480-S490, S495, S501-S502; F3 at the dense movers; the count-collapsed failing witness | **18 bench / 38 corpus** (rev 2, §4.1a; r3 read 18 / 58), plus the scan-edge, G1 and re-seed-row classes (§4.3); **abi event** |
| 4 (filed, TRIGGERED) | VM run seed: `req_uses[]`'s `handoff` (a) widened to the no-DFA VM entry, plus a `run-seed` row for retries (a cached `q`, `lo = max(p, q − K)`); [OPT-REQPOS] tier 2's VM instance, k82h Q7 | **trigger (as ruled, D148 Q9)**: stage 2's alpha leaves any K82 forced-VM cell past the floor above its pre-C3 level. The census shows it never applies without stage 2's row already applying. **[rev 2, cost-F9; Q-R4 OPEN]** After k82halpha (abi 61, accepted 2026-10-05), mod-i/mod-r, cls-fold-pair and ci-strasse already sit at or below pre-C3, so as ruled this fires only if stage 2 itself REGRESSES them: a regression guard, not a need. **Proposed trigger**: a VM-hat mover where handing the pre-check's candidate to the seek (`lo = c − K`) saves more than the floor, measured on the 4 bench `run_present_unbounded` cells. The regression guard stays as a do-not-regress row in stage 2's alpha |
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
    re-records). With the every-artifact stamp (§6.1) this class grows:
    `m5_stage1_stamps.tsv`, the resource pin, `artifact_size_log.tsv`, and
    the recursion-identity sweep;
  - **[rev 2, checks-F7] also, when the AXIS lands**:
    - the registry axes pin `run_registry_tests.sh:633-645` (189, +3 per
      axis);
    - `registry.md`'s row and axis counts, and `cli.md`'s deny list;
    - the `lib/pcrec.h` bit and the `axes.def` row;
    - `run_axes.sh`'s `tuning.md` "(bit N)" cross-check;
  - **and, when the stamp or the abi moves**:
    - the abi mentions in `tests/codegen/CLAUDE.md` and `docs/testing.md`;
    - the `rx_info.prefilter` runtime mirror of the `DFA_PREFILTER`
      values (`emit_dfa.c:3141`), which gains the four new values.
  - This list stays a GREP RECIPE (D94): grep the tree for the current abi
    number, the bit number and each new stamp/value name at landing. The
    enumeration above is what the grep found today, not a substitute for
    it.
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
    **[rev 2, sound-F3; Q-R3 OPEN: this EXTENDS ruled Q6's sentence]**
    Proposed: "positions a start-set or necessary-literal proof excludes
    consume no budget and no capacity. A search that gives up with
    `-fno-start-set`, whether on steps, work, backtrack frames, trail, or a
    caller-provided buffer's capacity (the `_in` entries), may return the
    answer an unbounded budget and capacity return. It never does the
    reverse."
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
  both hats). [rev 2, cost-F8: "76 + 117" does not add up. VM hat 17 + 59 =
  76, DFA hat 18 + 38 = 56 under rev 2 (r3: 18 + 58 = 76), and 117 is
  59 + 58, corpus only. The basis this answer gave for the large population
  is refuted by checks-F3; see Q-R2.] The large population is `--engine=vm` (2,263 corpus), which the
  per-change test-axes sweep of `-fno-start-set` × `--engine=vm` covers.
- **Q8. Re-bucket the six non-start-set cells** (asr-wb, asr-nwb, asr-b-ascii,
  stack-frame ×2, github-pat) out of START-SET in the next gap report's
  `causes.tsv`, after the bench re-measures at abi ≥ 61 (the handoff moved
  five of them)? **Recommend YES.** The next gap-report lane reads them; this
  lane does not edit the report.
- **Q9. Stage 4's trigger** as stated (a K82 forced-VM cell still past the floor
  after stage 2)? **Recommend YES.**

## 9b. Questions for Frank, revision 2 (each changes a D148 ruling's text or basis)

None of these is applied in rev 2's text without its marker. The panel
record is `../dev/reviews/2026-10-05-r4-startset.md`.

- **Q-R1 (sound-F1, the BLOCKER; changes D148 Q1's DFA-hat formula).**
  What does the DFA hat scan?
  - (a) `T = S ∩ E*`, `E*` = the union of every seed state's escape set
    and s0's;
  - (b) `T = S`;
  - (c) keep r3's `S ∩ E`, but decline when `S ⊄ E`.

  **Measured (§4.1a)**:
  - `E*` is all 256 on every seeded machine (structural; 94/94 rows), so
    (a) ≡ (b).
  - (a)/(b) give 0 diffs over 13,583,325 cells and pass the static
    (`Tdfa ⊆ T`) and start-byte-oracle checks. r3's set gives 322,771
    diffs and fails both on 21 rows.
  - Under the admission `T ⊊ E`, (a), (b) and (c) emit identical tables on
    identical movers: 18 bench / 38 corpus.
  - Admitting on `|T| < |E|` instead adds 15 corpus-only rows whose scan
    set SWAPS members, with no cost argument and no bench customer.

  **Recommend (a)**, `T = S ∩ E*`, admitted iff `T ⊊ E`, with a build
  assertion that `T == S` on every mover. It is the manager's preferred
  option, shown sound, and mover-identical to the fallback (c).
- **Q-R2 (checks-F3, cost-F8, sound-F8; changes D148 Q7's BASIS, not
  necessarily its answer).** Q7 was ruled "no early gate" BECAUSE "the
  per-change test-axes sweep of `-fno-start-set` × `--engine=vm` covers"
  the forced-VM population. That sweep does not exist: `run_axes.sh` sweeps
  axes at auto only. Options:
  - (i) keep NO early gate, and make the `run_axes.sh` product arm and the
    every-startpos differential named, floored stage-2 deliverables (§6.2,
    §7), plus a forced-VM cost read on a second subject class;
  - (ii) adopt an early batch gate after stage 2 (D144 addendum 3);
  - (iii) (i) plus a bench pcrec-vm read requested after stage 2.

  **Recommend (i)**: it restores the ruled answer's premise by building
  it. (iii) is the escalation if the second-subject-class read shows a
  sign flip.
- **Q-R3 (sound-F3; EXTENDS ruled Q6's spec sentence).** The give-up
  allowance must name CAPACITY give-ups (`PCREC_ERR_FRAMES`, trail, the
  caller-buffer `_in` entries) as well as meters. The witness is
  `(?=(?:a|b|x)*c)x` at `--backtrack-frames=8`: base returns −3, the hat
  returns a match. The direction is unchanged. **Recommend YES**, with the
  sentence in §8.
- **Q-R4 (cost-F9; changes D148 Q9's trigger).** As ruled, stage 4's
  trigger can only fire on a stage-2 REGRESSION, because k82halpha already
  brought the K82 forced-VM cells to or below pre-C3. **Recommend
  replacing it** with a NEED trigger: a VM-hat mover where handing the
  pre-check's candidate to the seek saves more than the floor, measured on
  the 4 bench `run_present_unbounded` cells. The regression guard stays as
  a do-not-regress row in stage 2's alpha.
- **Q-R5 (cost-F1, cost-F10; changes D148 Q1's VM `first-memchr` cell).**
  A dense single-byte `S` loses on the VM hat: memchr ×0.6 at d 80%, table
  ×0.9 at d ≥ 33% on match-dense find-all (Mac, directional). Options:
  - (a) at stage 2 the VM hat emits the TABLE form only; `first-memchr`'s
    VM column reads "never" until the kit owns the form (D146); dense guard
    cells in the alpha; MASS admission (the existing
    `pcrec_find_set_ppm`) FILED with those cells as its trigger;
  - (b) keep `first-memchr` on the VM, and add MASS admission now. Its
    threshold is a new constant that must be measured first (D149);
  - (c) as ruled, with the guard cells only.

  **Recommend (a)**. It removes the measured ×0.6 without a new constant.
  It costs the sparse single-byte cells little: memchr ×1.2 against table
  ×1.1 at d 5%. And it leaves the form to the kit, where D146 puts it.
- **Q-R6 (checks-F1; applies Frank's K82 Q3 ruling, asks only the
  family).** `<PREFIX>_VM_START_SCAN` goes on every artifact, `"none"`
  where unapplied. **Recommend the family "both engines"**, as
  `<PREFIX>_REQ_HANDOFF` was built (`k82hbuild_report.md`), rather than
  "VM artifacts only". A DFA artifact then reads `"none"`, consistent with
  the handoff stamp's precedent.

---

## 10. The standing questions (docs/design/CLAUDE.md)

**1. Measurement regime: RELEVANT.**
- **Census counts**: compile-only, darwin, abi 61, regime-free.
- **Densities**: one subject (capability `t-1m`, throughput regime, prose-like
  text). ~~A log or JSON subject moves `d`, not the sign.~~ [rev 2, cost-F3:
  WITHDRAWN. On the VM hat, d ≥ 33% on a match-dense subject flips the
  sign (§4.4); §7 adds match-dense and short-call cells per VM improve
  cell.]
- **The cost model's `a`/`b`**: Linux Ryzen, gcc-15, I-85, throughput,
  dependent calls.
- **The Mac twins**: find-all, M1, gcc-16 -O2, darwin libc `memchr`,
  directional only (D144 addendum 1). [rev 2, cost-F2: the TABLE form
  only. The memchr form and glibc's call term are owed at Linux.]
- **The rev-2 soundness instruments** (`startset/rev2/`) are answer-only
  and regime-free. Their oracle arm is LOCAL libpcre2 10.48, not the 10.46
  reference. It disagreed with base only on U1/U9 rows, which the corpus
  already marks.
- **The unmeasured constants** are labelled in §4.4's D149 table.
- **The gap cells**: the bench's Linux pin `c4c70f2c`, abi 60.
- **What could flip a decision**:
  - the dense single-byte VM regime (per-attempt `memchr` entry; a guard
    cell, and the form is the kit's);
  - short-call search, where the VM hat adds one entry scan. Tier C: an
    absolute delta against the floor, never a ratio.

**2. Independent control: RELEVANT.** §6.2:
- **C-SS\*** (rev 2) is the fact's control. It runs on every machine,
  seeded included, against the emitted `Tdfa`, and its failing direction is
  planted in the WALK (four plants, each firing). r3's C-SS reached no
  mover and had a tautological twin (sound-F2, checks-F2).
- **The start-byte oracle** takes its expectation from matches (base and
  libpcre2), outside both the walk and the machine. It reaches the VM-only
  arms.
- **The cost side's only independent control is the Linux deny floor**
  (rev 2, cost-N1), by design: there is no second cost model to check the
  first against.
- **The deny arm** is the answer control.
- **K35 / mover populations**: the census counts both hats' movers by
  predicate, and the build counts them by emitted text (the biconditional).
  [rev 2, checks-F5: the count is now a COMMITTED MANIFEST by ID per hat
  per stage, checked at build (0 off-diagonal, deny-identical). It is
  generated from the stage-1 census re-run with per-block options.]
- **Reach**: every sabotage witness is a named fixture, because the bench
  subjects are blind to S479. S483 is declared UNREACHED with an assertion.
  [rev 2: the numbering is §6.3's (re-seed rows S481-S484, utf8 assertion
  S497), and the population counts are the mover manifests, not the census
  (checks-F5).]

**3. What moves when data is regenerated: RELEVANT, narrowly.**
- `start_set` is a pure function of the pattern: no table, no calibration.
- Two indirect data dependencies:
  - **the frequency prior / findings bundle** feeds `pcrec_dfa_cand_ppm`. Once
    it reads the narrowed set (§4.3), regenerating a bundle can move a hybrid
    mover's `[OPT-HYB-RESEED]` row. That is already true of byte-class rows
    today and is not new in kind. It is an abi event only if a bundled default
    table changes (the existing rule);
  - **the census TSV here** is read by no check. Re-running `census.py` at a
    later pin moves nothing. **[rev 2, checks-F5: from stage 1 on, the
    MOVER MANIFESTS generated from the census ARE read by a check.
    Regenerating them moves that check's expectation, and they are
    regenerated only in a change that states why the population moved.]**
    `startset/rev2/out/` is read by no check.
- Each mover stage is an abi event (§8) with spec hunks (D80).

---

## 11. The four lenses (+ D124's)

| lens | verdict |
|---|---|
| specific vs general | GENERAL: one fact (the first-byte set of the zero-width-erased language), one table, rows by the information they use. No pattern is named |
| core vs derived | `start_set` is CORE (an AST walk). Both hats are DERIVED consumers. The re-seed is an existing primitive |
| applicable vs assumption-changing | APPLICABLE. The one assumption it leans on (the idle state is a function of the previous byte's class) is the entry seed's own, and it is tested at every startpos today. [rev 2, sound-F1: r3 applied the assumption at the landing but reasoned about the SKIPPED positions as if they were all read in s0. Rev 2's set takes every seed context into account (§4.1 step 2)] |
| fits-arch vs refactor | FITS: rows on `dfa_pfs[]` (D122 addendum 4), a hook slot, one fact. The rename is deferred (Q2) |
| D124: a question both emissions share? | YES. That is the design. The engine appears only in F/V and in the emit hook |
