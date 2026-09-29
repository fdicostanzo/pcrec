# ucpu2 — [UCP] U2 delivery report: the context node and the per-machine context-set table

Lane `ucpu2` (opus, feature tier), branch `lane/ucpu2`, from main `fdcf3e00`
(2026-09-29). Charter: `docs/design/ucp_design.md` §6's U2 row, as ruled by
D130 Q6 and chartered by D131 item 10. Scope held: the pcrec repo only, this
worktree; scratch in `/tmp/ucpu2s/`. Reproduction pieces:
`docs/dev/lanes/ucpu2_evidence/` (own CLAUDE.md).

## 1. What landed

- **The context node, `A_CTX`** (internal.h): a zero-width node carrying a
  code-point SET and a TRUTH FUNCTION over (prev ∈ C, next ∈ C), a 4-bit
  table (`CTXFN_*`); absent (start/end of subject) reads as not-in-C. `\b`
  and `\B` build it directly (`mod_assertions.c`) — [M6.2] wave B's
  `A_WORDB`/`A_NWORDB` (and `N_WORDB`/`N_NWORDB`) are RETIRED into it, one
  kind, every `case A_WORDB: case A_NWORDB:` site now `case A_CTX:`, each
  re-read (every one was a generic zero-width arm; none depended on the word
  set). The NFA carries `N_CTX` (`cls` = the set's byte image, `ctxfn`).
- **T3, the recognizer** (`src/parse/ctxnode.c`): a first-match table,
  rows as data (`pcrec_look_rows`) — `ctx-node` (deny `-fno-ctx-node`,
  `PCREC_NO_CTX_NODE`, bit 35) then `lookaround` (always). Row 1: the body
  is capture-free and assertion-free, its LANGUAGE is a set of single
  characters (alternation, class, `(?>…)`, `{1}`, empty-padded
  concatenation — so `(?<=a|b)` ≡ `(?<=[ab])`), AND every member is one byte
  of the encoding. Asked by the lookaround port at construction (so a
  context node is never stamped with the lookaround rows' VM_ONLY mask and
  `first_vmonly_pos` never names a construct the tree no longer has).
  `--list-axes` walks the rows live.
- **UCP `\b`/`\B` under `-e byte`** build (the Latin-1 word set); under
  `-e utf8` they stay refused by name (U3/U4).
- **The per-machine context-set TABLE** (`src/ir/dfa.c`, §2.4 / r1 GEN-1),
  replacing `upc_of_class`'s fixed two-set if-chain and the
  `has_word`/`has_nl`/`startcls` flags:
  - `ctx_rows[]`, a CONTRIBUTOR table (data): every A_CTX set in NFA order
    (deduplicated by set equality), then the newline set (`(?m)^/$`), then
    the encoding's NON-start set (K50's gate) → `Dfa.ctx[]`, each entry
    `{name, desc, row, bits}`.
  - `eqclasses` refines by every live entry; a class's context is its ATOM,
    the membership vector over the list; `Dfa.atomvec[]` holds the realized
    vectors SORTED (atom 0 = the empty vector = the absent side);
    `upc_of_class` is `return d->catom[c];`.
  - `DState.up[]` is arena-sized to `natoms`; `s1u[]`/`s1g[]` are atom
    families; `make_state` closes one view per atom; the closure's `N_CTX`
    arm is one truth-function read of the set's bit on each side; `N_BOT_M`,
    `N_EOL_M`, `N_CSTART` read the newline / non-start bits the same way.
  - IDENTITY BY CONSTRUCTION: with the list `{word, newline, non-start}` the
    sorted atoms are vectors 0,1,2,4 — exactly UPC_PLAIN/WORD/NL/NOSTART in
    the old order — and class ids are by lowest member byte whatever the
    refinement order. The identity gate (§4) is the check.
  - Overlap is exact by construction (V∩W, W∖V, V∖W, neither).
  - `PCREC_MAX_CTX_SETS` (32) / `PCREC_MAX_CTX_ATOMS` (16), two `limits.def`
    rows (`limits.md` §3.9); over either the machine is DECLINED through the
    state-cap overflow's own shape (`[SEL-1]`: auto retries on the VM,
    `--engine=dfa` refuses), never truncated. Measured: 17 singleton
    lookaheads → `RX_ENGINE "vm"`, `RX_ENGINE_WHY "dfa overflowed: >16
    context atoms"`; 14 → DFA.
  - The `-DPCREC_NO_WORDCTX` / `NO_MLINECTX` reference knobs moved to
    `ctx_entry_live`, the list's two consumers; the emitter's
    `upc_emit_live` half is deleted (the atoms can no longer answer a context
    the analysis did not build).
- **Byte-expressibility, one precondition** (§2.3): `PcrecEnc.onebyte_max`
  (byte 0xFF, utf8 0x7F; a D58 seam scalar) and `pcrec_enc_set_bytes`, asked
  by `\b`'s producer, T3, the NFA lowering and `vm_ctx`.
- **VM**: `vm_wordb` → `vm_ctx`, whose emitted form is a table keyed only on
  the truth function (`vm_ctx_forms[]`); its two two-sided rows are wave B's
  `\b`/`\B` text character for character.
- **A reverse-machine fix the node forced**: a pattern ending in a
  lookahead that needs a next character (`z(?=a)`) has a DEAD reverse `s0`
  ("nothing to the right") with LIVE seeds; `unanch_start` treated `rs < 0`
  as an empty engine and emitted `return 0`. Emptiness is now "`s0` and
  every seed dead"; `dfa_s0_cell` emits the dead cell for a dead `s0`
  (never a walk's start: the forward pass cannot end a match at `n` there).
  Found by the lookaround corpus (25 red cells) before it reached any report.
- **A shared-set fix the expansion corpus forced**: the list is deduplicated
  by set equality, so `(?=\n)` beside `(?m)^` share ONE entry; the first
  version remembered only the row that CREATED it, so the multiline arms
  found no newline entry — `(?m)^ERROR(?:(?=\n)|\z)` answered nomatch (68
  cells of `run_expansion_diff.sh`'s policy P2, A≠B and A≠C). Each entry now
  carries `rows`, every contributor row that reads it; readers and knobs go
  through it. Three witness blocks joined `ctxnode.rxt` (red on the pre-fix
  binary: 3 cells) and sabotage S343 plants the first-row-only form.

## 2. Tables (§0.1's rule), with their rows

| table | where | rows (name — deny — predicate) |
|---|---|---|
| T3 lookaround lowering | `src/parse/ctxnode.c` `pcrec_look_rows` | `ctx-node` — `-fno-ctx-node` — capture-free, assertion-free, LANGUAGE a set of single characters, every member one byte of the encoding; `lookaround` — — always (VM sub-match) |
| context-set contributors (not a selection; a listable data table) | `src/ir/dfa.c` `ctx_rows` | `ctx` — N_CTX's own set; `newline` — N_BOT_M/N_EOL_M, `pcrec_cls_newline`; `nostart` — N_CSTART, the complement of `start_cls` |
| VM context test forms | `src/gen/emit_vm.c` `vm_ctx_forms` | `CTXFN_BOUNDARY` both `!=`; `CTXFN_NONBOUNDARY` both `==`; `CTXFN_PREV` / `NOT_PREV` prev; `CTXFN_NEXT` / `NOT_NEXT` next |
| T4 (U2's slice) | — | not built as rows: in U2 no non-byte-expressible set can reach the DFA (T3 and `\b`'s producer refuse it upstream; nfa.c/vm_ctx fail loudly if one ever does), so T4 degenerates to `bytes` + the atom/set-cap `decline`. The island rows are U3's. |

**Design deviation, recorded (not improvised):** T3 row 1 carries the
byte-expressibility conjunct §0.1's text did not state — U2 has no engine
that reads a non-byte-expressible context set, so such a lookaround takes
row 2 (sound, today's answer). §0.1 now carries a *[U2 build]* note under T3;
U3/U4 drop it. List order also differs in spelling from §2.4's `{word,
newline, start, then A_CTX sets}`: the word set is not special — it is just
`\b`'s A_CTX set — so the list is `{A_CTX sets…, newline, non-start}`, which
yields the same atoms for every `\b` machine.

## 3. The critic-run "no spiderweb" pass (Step 0)

Two sonnet critics. The first (at charter, pre-code) never delivered through
this session's handback channel. The second reviewed the implementation:
**no BLOCKER, no MUST-FIX**; SHOULD U2-NS1 (state the T3 conjunct — applied as
the §0.1 note), SHOULD U2-NS2 (`Ast.u.ctx.anchor`: held — PCRE2's grammar
refuses `\b*` but accepts `(?=a)*`, a spelling fact), NIT U2-NS3 (stale
`A_WORDB` prose — fixed). Recorded as the review file's second addendum
(`docs/dev/reviews/2026-09-28-r1-ucp-design.md`).

## 4. Identity gate and movers

**Identity sweep** (`ucpu2_evidence/ident.sh`): every unique corpus `pattern`
line (3,375), `--features all`, `-e byte` and `-e utf8`, base binary (main
`fdcf3e00`) vs U2 before the abi digit moved, `-o -`, compared whole:

| axis | byte ident / diff / both-refuse | utf8 ident / diff / both-refuse |
|---|---|---|
| default engine | 2,735 / 274 / 366 | 2,752 / 258 / 365 |
| `--no-captures` | 2,735 / 274 / 366 | 2,755 / 258 / 362 |
| `--engine=vm` | 2,736 / 274 / 365 | 2,750 / 258 / 367 |
| bench (292 `.rxt` patterns, default) | 245 / 9 / 24 | 247 / 8 / 23 |

**Every differing artifact is accounted for, on every axis:** recompiled with
`-fno-ctx-node`, 522 of the 532 (and all 17 bench diffs) reproduce the base
artifact BYTE FOR BYTE — they are T3 movers and nothing else — and the other
10 are the five UCP `\b`/`\B` patterns × 2 encodings (byte: refused → built;
utf8: refusal wording). So every `\b`, `\B`, `(?m)^/$` and K50-gated utf8
class-axis artifact is byte-identical: the atom table reproduced the old
partition exactly. (A first sweep, before T3 existed, read 2,971/2,972 ident
with the only 4 diffs the UCP `\b` rows.)

**Mover census** (§7 a1, the lookaround census population of 493,
`ucpu2_evidence/movers_*.tsv`): captures ON (the default): **141** move VM →
DFA (138 byte "all-(a)" + 2 utf8 ASCII-set + 1 the census's syntax rule
missed, `(?=a|b)[ab]c` — the LANGUAGE predicate at work); 18 byte all-(a)
patterns stay VM because they CAPTURE (`((?=a)z)`). `--no-captures`: **159**
= exactly the design's predicted **158** (156 byte + 2 utf8) + that one. 14
utf8 patterns with non-ASCII sets stay VM (U3). Bench: 5 capability movers
(`currency-lookbehind-fixed`, `float-literal-bound`, `utf8-lead-no-cont`, the
two `wild-logparse-*-noatomic`); `utf8/asr-lb-{class,fixed,neg}` stay VM
(non-ASCII sets). **Named manifest**: `tests/ucp/ctxnode_route.tsv` (all 493
+ 6 synthetic rows, default and denied engine), asserted by
`run_ctxnode_tests.sh` §3 (502/0).

## 5. Oracle agreement

- `tests/ucp/ctxnode.rxt` (42 blocks): generated from libpcre2 10.48,
  **re-verified on 10.46: 199/199 cells agree** (`verify_ctxnode_10.46.txt`);
  `verify_ucp.py` (local 10.48) re-checks it on every `make test-ucp`.
- `tests/utf8/axis13_ctx_illformed.rxt` (8 blocks, §2.3's hazard cells):
  oracle UTF|MATCH_INVALID_UTF, **10.46: 32/32** (`verify_axis13_10.46.txt`);
  `(?<=[^a])a` on `80 61` nomatch, on `C3 A9 61` (2,3).
- Harness over `tests/lookaround tests/assertions tests/ucp tests/utf8`:
  **16,148 passed / 0 failed**.
- `run_ctxnode_tests.sh`: corpus default 220/0, under `-fno-ctx-node` 220/0,
  route manifest 499 rows — **502 passed / 0 failed**.
- The assertion-expansion corpus (`make test-lookaround`'s
  `run_expansion_diff.sh`, A==B==C against local libpcre2): see §7.

## 6. Sabotage rows (main's highest was S336; new S337–S343)

New `ctxnode` mech arm (`tests/ucp/run_ctxnode_tests.sh`), registered before
the rows. One id per invocation, at `405a4de1`:

| row | plant | verdict |
|---|---|---|
| S337 | the old first-match chain over overlapping sets (`ctx_vec_of_byte` returns the first set's bit) | DETECTED — ctxnode 1 fail (`(?<=[aeiou])x\b` on "axa") |
| S338 | T3 accepts a two-character body (`(?<=ab)x` → `(?<=a)x`) | DETECTED — 115 fail |
| S339 | T3 accepts a capture-bearing body | DETECTED — 39 fail (`g 1 0 1` unset) |
| S340 | the byte-expressibility precondition clamps instead of refusing (non-ASCII set under utf8) | DETECTED — 21 fail (the §2.3 hazard cell `80 61`) |
| S341 | the absent side reads as in-set (`s0` closed under the last atom) | DETECTED — 2 fail |
| S342 | **GEN-4 shape**: a DENIED T3 row falls through to an erased (unsound) lowering | DETECTED — 438 fail, only via the `-fno-ctx-node` half and the route's denied column; the default path never reaches the denied row |
| S343 | a SHARED context set keeps only the row that created it | run in the final chain (§7); its witness is red on the pre-fix binary (3 cells) |

**Re-aimed anchors (11), intent re-verified, each annotated in its own file**:
S69, S71, S76 (the `has_word`/`has_nl` gates are gone — S71/S76 now plant the
word/newline set on every machine's context LIST, where it is filled, with the
knobs at its consumers so they cannot cancel), S75 (`vm_ctx`'s pool bitmap),
S78, S81, S83, S218, S220, S269, S276 (signature-only). Anchor checker: 343
rows, all resolve. Their DETECTED re-runs: see §7.

## 7. Validation

Run and green on the branch (darwin, gcc-16): `make strict` (clean);
`test-reject` (655/0, coverage 290/120/0/112 re-pinned); `test-definitions`
(22/0); `test-registry` (re-pinned: axes coverage 138 → 141, limits 35 → 37,
limits manifest +2 names; the lookaround VM_ONLY witnesses asked under
`-fno-ctx-node`, the configuration where the column is exactly true);
`test-assertions`' `run_wordctx_identity.sh` (2,893 `\b`-free patterns identical,
positive control 106 differ — BOTH builds now deny T3: a one-character
lookaround is a context node on the very axis `-DPCREC_NO_WORDCTX` removes, so
without the deny 173 `\b`-free lookaround patterns read as paying for the word
context; the gate is about `\b`'s axis and T3's own identity is
`run_ctxnode_tests.sh`'s); `test-ucp` (all checks passed, §4 included);
`test-cli` green;
`test-codegen`'s three scripts that the change touched, re-run after fixture
fixes: `run_codegen_tests.sh` 0 failed, `run_dfa_stamps.sh` 0 failed (empty-
engine manifest +24 NAMED patterns — one-character lookarounds whose empty
language the DFA now proves), `run_facts_checks.sh` 0 failed (the first full
`test-codegen` run had 8/12 scripts; the one remaining red is
`run_inline_capability.sh`'s standing darwin `nm arm_a.o` red, pre-existing);
`run_ctxnode_tests.sh` 502/0; mech S337–S342 DETECTED.

OWED — filled in below by the chain's own lines (see §9).

## 8. abi decision

**Bump, 45 → 46** (D76/K64): one-character-lookaround patterns get different
emitted text for identical inputs (VM → DFA, or `vm_ctx` in place of the
sub-match), and UCP `\b` under byte moves the refusal set. Full D94 ritual:
the constant committed alone (`7e8ab18a`), `docs/spec/match_api.md` §6's
change-log entry, `run_codegen_tests.sh` `ABI_EXPECT=46` + its copied
message, `run_recursion_identity.sh` FILEPIN self-pinned to `7e8ab18a`; grep
for other readers of 45 found none. No struct offset moves, no `rx_info`
member; `PCREC_NO_CTX_NODE` is masked out of `rx_info.flags`.

**Spec hunks (D80)**: `tuning.md` §2.32 (+ §4 rows for bits 32, 33, 35 —
32/33 were missing, backfilled), `limits.md` §3.8/§3.9, `cli.md` (UCP `\b`;
the `-f` family list), `match_api.md` §6, `facts_listing.md` (the
`lookaround` kind), `docs/pcre2_compliance.md`'s `(*UCP)` survey row.

## 9. Findings not fixed

- **Pre-existing MIU divergence** (not U2's; base binary identical): an
  empty/nullable pattern on the lone byte `80` under `-e utf8` answers
  `(0,0)`; libpcre2 10.46 UTF|MIU answers `(1,1)` (MIU re-positions past an
  invalid byte). `ucpu2_evidence/side_finding_empty_at_0x80_10.46.txt`.
  Worth a K-number; the lane did not file one.
- The design's "artifact's stamp names the list" (§2.4) is not built: a
  stamp on every `\b` artifact would break the identity the gate requires; a
  `--emit-facts` or [LIST-TABLES] surface is the natural home.
- b-ctx (U2's customers' throughput on ubuntubudu, §7) is owed to the bench
  after merge — 5 capability movers named above.
