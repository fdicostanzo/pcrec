# r15scope — [MEMFN] R-15 step 1: READ-ONLY scoping of the one-byte ASSIGN gate row

**Lane `r15scope`, 2026-10-11, opus. READ-ONLY: no code, no build, no test,
no timing** (slot21 held the box). The only processes run were three
`build/pcrec -p rx -o … --pattern P` emits from the MAIN tree's binary
(`taskset -c 0-3`; built 2026-10-10 17:51, and no commit under `src/`,
`memfn/src`, `memfn/include`, `lib/` or `cli/` since, so it is current for
main `0c100281`, abi 74), written to the job scratchpad. Everything else is
read from the source on `lane/memfn-r15` (`ace7b104`, main `0c100281` plus
the R-15 ack) and from lane rlhtwin's own artifacts
(`worktrees/rlhtwin/build/rlh/cells/{ipv6,ipv4}/src_{o,h1,h1m,h2}/rx.c`, read only).

Charter: `memfn/docs/requests.md` R-15. Customer: `[REQ-HANDOFF-L1]`
(plan.md; manager rulings Q1-Q4 under Frank's pre-approval), measured by
`rlhtwin_report.md` §5 Q4. Sabotage ids S800-S804.

## 0. Answers first (resume from here)

1. **The site does not exist on main.** pcrec states the PRE site
   (`req_site_define`, `src/gen/emit_dfa.c:1524`) as ASSIGN only when a RUN
   window ships (`len >= 2`), and then `ret_pred` names the run. The R-15
   shape, (ALL_PRESENT, ASSIGN, SET) with `ret_pred` naming a ONE-BYTE SET
   predicate, appears only under rlhtwin's NOT-FOR-MERGE scratch emitter
   (`ceca117d`), and so only after [REQ-HANDOFF-L1] lands. On main all three
   cells render the byte gate as ON_MISS, through the `precheck` row's
   `memchr` (§1.3). **Consequence:** the kit row can land at ZERO movers,
   with reach `pending-site:REQ-HANDOFF-L1`. The only byte event is then
   L1's own merge, which is the one abi event the charter asks for (§4).
2. **The set term in all three cells is ONE byte, not a class.** It is
   `:` (58) on ipv6 and `.` (46) on ipv4 and dotted4. The hex and digit
   classes are the cells' START sets: the NEXT slot's `byte-class` walk
   serves them, not this site. By construction pcrec's gate byte is always
   a single member (`pcrec_memfn_term_byte`, `src/gen/memfn_sites.c:227`;
   the gate is `req_byte`). So the row's population is one-member sets.
3. **Why generic is chosen today (by reading).** The arms walk runs
   `ofsskip`, `precheck`, `precheck_assign`, `runcmp`, the five `pf_*`,
   `mismatch_inplace`, then `generic`. Every row above `precheck_assign`
   and below it is DECLINED by its contract's `form`/`op`/`handoff`.
   `precheck_assign` passes the gate, but its predicate is false:
   `precheck_applies`' last line (`memfn/src/precheck.c:88`) requires
   `run_part(&preds[ret_pred])`, and a SET part is not a run. **`generic`
   is chosen.** It renders a byte-at-a-time statement expression and
   flips `RX_MEMFN_LIBC` from `"memchr"` to `"none"`.
4. **The scalar form is `memchr` (one member), and it is a NEW ROW in the
   existing `arms[]` table.** It is a third row of precheck.c's ONE
   renderer (N3's split idiom), `precheck_assign_byte`, placed before
   `generic`, with its own options.def deny (the kit's FIRST scalar deny).
   Its OFF arm is the generic row: the bytes L1 would emit without R-15.
   The other forms the brief listed (table walk, SWAR class test,
   two-`memchr` merge) have NO population here (point 2). They are filed,
   not built (D77). The SIMD candidates are filed behind `-fmemfn-simd`,
   §2.3. The more valuable of them (entry 4's in-register neighbour filter
   for dead dots) needs a pcrec FACT first, so it is an unlock row on L1,
   not on R-15.
5. **Nobody has measured the twin that justifies the row.** rlhtwin timed
   generic against memchr only at the ENTRY (h1 vs h1m: about 0, because
   the entry scans only to the first landmark). The re-entered form h2 was
   built with `memchr` at both points, so "generic loop under re-entry"
   was never timed. Under re-entry the generic loop is plausibly the same
   order of cost as the byte-class walk it replaces, which would give back
   much of h2's win, but that is unmeasured. **R-15 step 2 opens with that
   twin (scratch tier, about minutes, after slot21) before any code**
   (Q-R15-2).
6. **Main's design choice decides whether this row is on the hot path at
   all (Q-R15-1).** The re-entry's landmark scan can be stated three ways:
   - as a SECOND USE of the PRE site handle: this row then serves both the
     entry and the re-entry;
   - as a separate FIND/STMT/ASSIGN site: `pf_memchr` already serves that
     shape, given an EXCLUDED empty range;
   - as a FUNC call.

   *Leaning: the second use.* It is one fact and one site, and §14.3
   already says the ret_pred is found by the FIND contract.

## 1. The site today

### 1.1 The facts pcrec states (the scratch emitter's site, `ceca117d`)

`req_site_define`'s byte arm, with rlhtwin's two scratch lines (`handoff =
req_use(cx) == REQ_USE_HANDOFF;` and `s->ret_pred = np` where `handoff &&
!nrun`). Field by field (`mf_site`, `memfn/include/memfn.h`):

| field | value | source |
|---|---|---|
| `form` / `op` / `handoff` | STMT / ALL_PRESENT / ASSIGN | `emit_dfa.c:1579-1581` |
| `reverse` / `end_back` | 0 / 0 | the zeroed site (`pcrec_memfn_site`) |
| `empty` | MISS | `:1582` |
| `npred` / `ret_pred` | 1 / 0 | scratch |
| `preds[0]` | `nterm` 1, `need` REQUIRED (byte-only path: `gate_need` stays REQUIRED), `fn_ref` 0, `plan_hint` none, `rank_n` 0 | `:1566-1569` |
| `preds[0].term[0]` | `kind` SET, `offset` 0, `need` REQUIRED, ONE member, `table_ref` 0, density unknown | `pcrec_memfn_term_byte` |
| `use` / `consumer` | POSITION / ENGINE | `:1583-1584` |
| `on_miss_leaves` | 1 (`return 0;`) | `:1587` |
| `span_*`, `policy`, `denies`, `opts` | pcrec's per-artifact values; not read by any precheck row | |

The use hooks (`pcrec_emit_req_byte_check`, `:1641-1648`) are:
- `s` = `subject`, `n` = `subject_length`, `lo` = `search_from`;
- `result` = `handoff_position`, `result_decl` = `"size_t "`,
  `miss` = `MF_MISS_N`;
- `on_miss` = `"return 0;"`, `indent` = 4 spaces;
- pcrec's `note`.

The define hooks are `fn_name`, `note_tag` and `comment_tier`.

The member, per cell (`RX_REQ_BYTE`; scratch K from rlhtwin §1.3):

| cell | pattern | member | K | route |
|---|---|---|---|---|
| loglines/ipv6 | `(?:(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}\|(?:[0-9a-f]{1,4}:){1,7}:[0-9a-f]{0,4})` | 58 `:` | 4 | DFA, `byte-class` prefilter |
| loglines/ipv4 | `(?:(?:25[0-5]\|…\|[1-9]?[0-9])\.){3}(?:…)` | 46 `.` | 3 | DFA, `byte-class` prefilter, `reverse-pass` |
| bounded/dotted4 | `(?:\d{1,3}\.){3}\d{1,3}` | 46 `.` | 3 | DFA |

rlhtwin's census found two more movers: `syntax/grp-atomic-alt` (K 2, on
the VM hybrid route) and `syntax/qnt-poss-brace` (K 2, DFA). The row
serves those too: the site shape is the same.

### 1.2 The row walk (by reading; an MF_TRACE run is owed, light)

pcrec uses define then use, so the walk runs at `mf_define` with the
define hooks and the gate re-checks the chosen row at each `mf_use`. The
walk order is compose.c `arms[]`:

| row | verdict | why |
|---|---|---|
| `ofsskip` | DECLINED | contract `form` FUNC, `handoff` RETURN (ofsskip.c:738-740) |
| `precheck` | DECLINED | contract `handoff` ON_MISS, `ret_pred` NONE (precheck.c, `precheck_ct`) |
| `precheck_assign` | PRED_FALSE | gate passes (ASSIGN, PRED, MISS_N, JUMP, E_MISS, leaves YES); `precheck_applies` admits part 0 as `single_byte`, then fails its last line, `run_part(&preds[ret_pred])` (:88): the ret_pred is a SET |
| `runcmp` | DECLINED | EXPR / VERIFY / BOOL (runcmp.c:402-404) |
| `pf_memchr` … `pf_memchr_back` | DECLINED | `op` FIND (pffind.c:276) |
| `mismatch_inplace` | DECLINED | `op` MISMATCH |
| **`generic`** | **CHOSEN** | the total fallback |

No arm in `arms[]` has a `--memfn=` deny today. `arm_table`'s `opt`
accessor is NULL (compose.c:229), and compose.c:253 says "each byte-moving
row brings one, D144 item 4".

### 1.3 The emitted text

**Main today (abi 74), all three cells: the ON_MISS gate through `precheck`.**
ipv6 is shown; ipv4 and dotted4 are the same with 46:

```c
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 58, subject_length - search_from))
        return 0;
```

The stamps are `RX_REQ_BYTE "58"`/`"46"`, `RX_REQ_HANDOFF "none"`,
`RX_MEMFN_LIBC "memchr"`, `RX_MEMFN_FORMS "none"`. ipv4's restart point,
where L1's re-entry goes (main, `ipv4.c:172-175`), is:

```c
        if (forward_state == 0 && last_accept_position == (size_t)-1) {
            while (scan_position < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;
            if (scan_position >= subject_length) return 0;
        }
```

That `while` is the `pf_walk` row.

**Under L1 without R-15 (rlhtwin's h1, the scratch artifact): the generic row.**

```c
    size_t handoff_position = ({ const unsigned char *rx_mf1_s = (const unsigned char *)(subject); size_t rx_mf1_n = subject_length; size_t rx_mf1_lo = search_from; int rx_mf1_a = 1; size_t rx_mf1_r = 0; if (rx_mf1_a) { size_t rx_mf1_c0 = rx_mf1_lo; int rx_mf1_f0 = 0; for (; rx_mf1_c0 < rx_mf1_n; rx_mf1_c0++) if ((rx_mf1_c0 + 1 <= rx_mf1_n && (rx_mf1_s[rx_mf1_c0] == 58))) { rx_mf1_f0 = 1; break; } if (!rx_mf1_f0) rx_mf1_a = 0; rx_mf1_r = rx_mf1_c0; } rx_mf1_a ? rx_mf1_r : (subject_length); });
    if (handoff_position == (subject_length)) {
        return 0;
    }
    if (handoff_position - search_from > 4) {
        handoff_position -= 4;
    } else
        handoff_position = search_from;
```

The last four lines are pcrec's (`emit_req_handoff_rest`). The stamps
become `RX_REQ_HANDOFF "4"` and `RX_MEMFN_LIBC "none"`: a stamp regression
on every mover whose only `memchr` was this gate.

**rlhtwin's hand form (h1m, then h2), what R-15's row would replace it
with.** The kit owns the spelling:

```c
    const unsigned char *rlh_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL; size_t handoff_position = rlh_q ? (size_t)(rlh_q - subject) : subject_length;
```

h2's re-entry, at the restart point above:

```c
            if (rlh_lm < scan_position) {
                const unsigned char *q = scan_position < subject_length ? memchr(subject + scan_position, 46, subject_length - scan_position) : NULL;
                if (!q) return 0;
                rlh_lm = (size_t)(q - subject);
            }
            if (rlh_lm - scan_position > 3) scan_position = rlh_lm - 3;
```

## 2. Candidate forms (the kit owns the method; scalar layer first, D144/D147)

### 2.1 The set shapes the row meets

The three cells (and all five census movers) each state one member, so
the row's real population is "one SET term of exactly one member at
offset 0, REQUIRED, the ret_pred". Multi-member landmarks are not a shape
pcrec states, because the gate is `req_byte`. They would come only from a
future pcrec change (for example a necessary SET narrowed to a pair).

### 2.2 Scalar forms

| form | serves | contract it needs | twin it must beat | cells that judge it | verdict |
|---|---|---|---|---|---|
| **S1. `memchr` ASSIGN** (`n > lo ? memchr(s + lo, b, n - lo) : NULL`, store the hit or `n`, then `if (result >= n) on_miss`; the empty test kept because a NULL subject with length 0 is legal, match_api §3.1, and UBSan reads it) | one member | §3.2's contract: STMT/ALL_PRESENT/ASSIGN, `ret_pred` a one-member SET at offset 0, REQUIRED; `empty` MISS; `miss` MISS_N; `end_back` 0; forward; `s`/`n`/`lo` IDENT; `on_miss` JUMP\|BRACED; no `floor` | the GENERIC row under the RE-ENTERED form (h2 with the generic loop at both points, "h2g"): **not yet measured** (§0 item 5). At the entry alone the twin is h1 vs h1m: about 0 on ipv6/ipv4 (rlhtwin §3.1). | loglines/ipv6, loglines/ipv4 (throughput + search_short), bounded/dotted4; controls: the two syntax movers, and loglines/kv-quoted plus altwide/sfx-64 IF the re-entry of a run landmark also goes through PRE (Q-R15-1) | **BUILD**, after the h2g twin |
| S2. 256-entry table walk (`while (lo < n && !T[s[lo]]) lo++`; pf_walk's text) | any set | a table the caller names (`table_ref` + `table_name`) or one the kit emits | S1 on one member; generic on many | none: no multi-member population | FILE (D77; trigger: pcrec states a multi-member landmark) |
| S3. SWAR range/class test (8 bytes per step, "has-between" bit trick) | a range, or a small union of ranges | the set's ranges | S2 | none | FILE (same trigger; D149: the word width is the type's, not a tuning constant) |
| S4. two-`memchr` merge (two streams, the lower of the next hits) | two members | the two members | S2; generic | none | FILE (same trigger; fn-pair's two-stream body is the precedent) |
| S5. a short inline probe before `memchr` (test the first few bytes inline, then call) | one member | as S1 | S1, on the re-entry's short landmark gaps (ipv4 syslog: a `.` every ~dozen bytes) | ipv4's syslog throughput subjects; ipv4 search_short `s-010`/`s-027`, the two h2 lost | NOT proposed: its probe length is a tuning constant (memory `pcrec-suspect-tuning-constants`). The Mac probe in `docs/design/memfn/requirements.md` puts an inline byte loop behind `memchr` from 2-4 bytes. Revisit only if a profile of the built row shows `memchr`'s call term |

### 2.3 SIMD layer (CANDIDATES only, behind `-fmemfn-simd`, after the scalar row)

| form | needs | twin | cells | leaning |
|---|---|---|---|---|
| V1. an inline vector byte-eq scan (16/32-byte compare, movemask, ctz), with the floor rule's `#else` = S1 | one member; a level from `levels.def`; the over-read argument vrun.c makes | S1 (glibc's `memchr` is already vectorized on x86-64 and aarch64, so V1 can win only the call term on short gaps) | ipv4 syslog subjects, ipv6/ipv4 search_short | low expected value; file |
| V2. ideas.md entry 4: the landmark plus neighbour classes in register (`cmpeq(x[i], '.') & digit(x[i-1]) & digit(x[i+1])`), with entry 5's held mask across re-entries (entry 6 names the re-entered skip as its natural home) | a pcrec FACT: the landmark predicate stated as a conjunction (`.` at 0, a digit class at -1 and +1, each proven necessary at every guaranteed occurrence); the scalar layer first is then the existing offset-set FUNC (memchr + table check) | S1 on dense-dot text; it attacks rlhtwin's one measured loss (h2 is 1.5-1.7x rev-inner on ipv4's four syslog subjects: dead `.` landmarks re-run the DFA over K + a few bytes each) | ipv4 syslog; dotted4; a dense-dot cell | **an UNLOCK on [REQ-HANDOFF-L1], not R-15**: it widens pcrec's fact, so the site is no longer one term. Trigger: after L1 lands, a bench reading in which the re-entered handoff trails rev-inner on dense-landmark subjects |

V2's soundness, stated for whoever picks it up: the K bound needs the
LEAST conjunction hit to be at or before the first match's guaranteed
landmark. That holds iff each neighbour term holds at EVERY guaranteed
occurrence, which is a fact pcrec proves, never a heuristic the kit
assumes (D157: facts only).

## 3. Row placement: a new row in the existing `arms[]` table

### 3.1 The table and the order

- It is a NEW ROW in the composer's existing first-match table
  (`arms[]`, compose.c:131), not a new table. The site's op, handoff and
  term kinds are already in the vocabulary (compose.c:669). The site is
  STMT, not a FUNC body, so `fn_rows[]` is the wrong table.
- The row is a THIRD ROW of precheck.c's ONE renderer, in N3's idiom
  ("a shape-dependent row is split"). Its name is `precheck_assign_byte`
  (trace and rows.tsv), and its form id is `precheck` like its siblings,
  because it is the same renderer.
- The renderer gains one branch: a byte part that IS `ret_pred` renders
  as the ASSIGN line (S1) instead of `gate()`.
- The predicate: `handoff == ASSIGN && precheck_applies(...)` with the
  last line reading "ret_pred names part 0, and part 0 is
  `single_byte`". The part rules for any later parts are
  `precheck_applies`' own. This is not a special case: the composite's
  ret_pred is found by the FIND contract whatever its kind (§14.3), and
  today the renderer knows that only for a run.
  - *Leaning:* keep the general part rules. G2 tests them from the
    contract, and pcrec sends only `npred` 1 (L1's internal check forbids
    a part after the landmark).
- The order: directly after `precheck_assign`. The two predicates are
  disjoint (run ret_pred vs byte ret_pred), so the position among the
  precheck rows is immaterial. First-match needs it above `generic`
  only.
- **The deny row is `generic`.** Denying the new row leaves `generic` as
  the only row that serves the site, and it renders exactly the h1 text
  of §1.3: the bytes L1 alone would emit. That is D147's OFF arm.

### 3.2 The contract (`precheck_assign_byte_ct`)

The row inherits `PRECHECK_SERVES` and `precheck_assign_uses` (s, n, lo,
indent, on_miss; result, miss), plus:

- `handoff` ASSIGN, `ret_pred` PRED, `miss` MISS_N (the text tests
  `>= n`), `result` / `result_decl` ANY.
- `table_ref` and `member` stay ANY: the row reads the set bits and never
  pcrec's table.
- `floor` 0: a stated floor declines (R2).
- `policy` ANY (scalar).

Held by the predicate (a class cannot say it):
- the ret_pred's SET has exactly one member at offset 0;
- `need` is REQUIRED on both the term and the predicate. An OPTIONAL
  ret_pred is not a position anyone may keep, so G2 should check that the
  row declines it.

### 3.3 The deny

- The deny is a new `options.def` row:
  `MF_OPT("precheck-assign-byte", MF_OPT_DENY, MF_B_ANY, MF_L_SCALAR, …)`.
  The kit owns the name.
  - The budget is ANY: the entry use is SCAN; the re-entry use, if
    Q-R15-1 lands as recommended, is per restart.
- It is the kit's FIRST scalar `--memfn=` row, so two small structural
  changes come with it:
  - the `arm` struct gains an `opt` name (NULL on the transcribed,
    undeniable rows);
  - `arm_table` gains its `opt` accessor. `walk_row` already reads
    `t->opt`, so there is no new mechanism.
- Readers that move with it (found by grep: `vrun-kb`'s precedent):
  - `--list-axes`' `memfn` section, plus the section floor literal in
    `docs/spec/registry.md` §6;
  - `docs/spec/tuning.md` §2.43¶3b, which today describes only SIMD
    rows: a scalar row's deny is live at `-fno-memfn-simd`;
  - `tests/memfn/rows.tsv`, `row_floors.tsv`, `ROWS_FLOOR`, and
    memfn/CLAUDE.md's "born empty / first rows are SIMD" sentences.
- `test-axes` gains the deny as an axis (memfn/CLAUDE.md: options.def is
  the ONE enumeration point for `test-axes`). That gives a free
  answer-identity sweep once L1 lands.

## 4. The abi plan

**Recommended sequencing (Q-R15-3):**

**(1) The kit row lands on `lane/memfn-r15` and is delivered to main
AHEAD of L1, at ZERO generated-byte movers.**
- On main no site has the R-15 shape (§0 item 1; `ALL_PRESENT` is built
  only by `req_site_define`, grep `MF_OP_ALL_PRESENT` in `src/`), so the
  row is unreachable.
- rows.tsv reach: `pending-site:REQ-HANDOFF-L1`, a fixture witness in
  `arm_fixtures.c`, `pcrec_floor` `-` (the N2 census must count 0).
- This is NOT an abi event: no generated byte moves.
- Only the `--list-axes` dump moves: the dumps stream, one row.

Proof of zero movers:
- `scripts/emit_sweep.py --ref-bin <main build/pcrec>` over every stream:
  - `--variant all`;
  - `--arms start`;
  - `--extra=-fmemfn-simd` (the row is scalar, so SIMD-on must also show
    0 movers);
  - expected: 0 artifact movers, and dumps 1 (`--list-axes`).
- The N2 census: the row chosen 0 times. A nonzero count is STALE by the
  census's own rule.

**(2) L1's merge is the ONE abi event** (74 to the next number, readers by
grep, D76/D94). It carries both pcrec's changes and the row's first
bytes.

Expected movers, by site shape:

| stream | movers the ROW owns | how they are recognized |
|---|---|---|
| c-default (byte and utf8 bases) | every artifact whose PRE site is ASSIGN on a byte landmark: `RX_REQ_HANDOFF` numeric AND `RX_REQ_RUN "none"` (bench: the five of §1.1; corpus: L1's census, owed) | the gate lines; `RX_MEMFN_LIBC` stays `"memchr"` where L1 alone would make it `"none"` |
| c-vm / composition | the same rule (the VM hybrid route reaches PRE, §15.5 rev4.6; grp-atomic-alt is the bench witness) | as above |
| emit-ir-vm, facts | 0 from the row (the pre-check is C text, not IR; L1's fact row is L1's mover) | |
| re-entry use (if Q-R15-1 = second use) | the same artifacts, at the restart point; a RUN-landmark re-entry renders through `precheck_assign` (an existing row), so it moves no kit form | |

**Proving the row moved nothing else, with a control that does not share
a source with the row:**
- (a) Population P is read from pcrec's STAMPS: `RX_REQ_HANDOFF` numeric
  and `RX_REQ_RUN "none"`. It is never read from the kit's output or the
  trace.
- (b) The mover set D comes from a byte diff of the L1 tree against itself
  with the row denied. The cheapest spelling: `emit_sweep.py --ref-bin`
  pointed at a two-line wrapper that runs the same binary with
  `--memfn=no-precheck-assign-byte` appended. Both sides are one build;
  only the row differs.
- (c) The verdict is D == P exactly. Each mover's diff must be confined
  to the PRE use's lines plus the `RX_MEMFN_LIBC` line. That is a
  classifier `--event r15` in `tests/memfn/stamp_mover_census.py`'s
  idiom, with every other difference OTHER and red.
- (d) The N2 census at L1's merge pins the row's `pcrec_floor`, and its
  reach becomes `pcrec`:
  - witness `(?:\d{1,3}\.){3}\d{1,3}`;
  - control `=` under `--memfn=no-precheck-assign-byte`;
  - signature a fragment of the row's `memchr` ASSIGN line.
- (e) Answer identity: `test-axes` over the new deny, the corpus, and
  rlhtwin's identity harness (`docs/dev/optloop/rlhtwin/ident.sh`, against
  libpcre2 10.46).

## 5. Checks

### 5.1 Sabotage, S800-S804

Grepped free on main and in every `worktrees/*/tests/mech/sabotages`; the
highest on main is S792, and S800-S804 are R-15's allocation. Every
anchor is to be copied from `git show HEAD:<path>` once the code exists.

| id | plant (in the row's renderer/predicate) | why it is not an equivalent mutant | detector (mech arm) | expect |
|---|---|---|---|---|
| S800 | the ASSIGN stores a LATER occurrence (searches from `lo + 1`, or stores hit + 1) | a later landmark moves the handoff past matches that begin in `[c-K, c'-K)`. NOT an earlier one: K-1..1 are equivalent on reverse-pass bodies (rlhtwin §2.2; plan row "K=0 or a later occurrence") | `memfnarms` (the new fixture's pin moves, plus a behavioural check on fixed subjects, as S617's check 9: "x.y" from 0 must answer 1); after L1 also `harness` (a landmark at `lo`) | DETECTED |
| S801 | the empty test dropped (`memchr(s + lo, b, n - lo)` with `lo == n`) | answer-invisible on a non-NULL subject; UB on the legal NULL+0 subject (match_api §3.1) | `ubsan` / G2's sanitizer build (G2 full runs ASan+UBSan); `memfnarms` pin | DETECTED by the sanitizer axis; the mech arm for it is owed (§5.3) |
| S802 | on a NULL hit, store `lo` and fall through (no `on_miss`) | on pcrec's customer the answer is unchanged (no landmark, no match: slower only, S617's class). The KIT contract (ASSIGN on a miss runs `on_miss`) breaks | `memfnarms` behavioural check (a no-landmark subject must take the on_miss path); G2 | DETECTED by the kit's checks only (document this, as S617 does) |
| S803 | the deny unwired (the row's `opt` NULL, or `arm_table.opt` dropped) | `--memfn=no-precheck-assign-byte` still renders the row: the OFF arm is gone | `run_rows.sh` check C (the control must not choose the row, signature absent); registry/`--list-axes` | DETECTED, but there is **no mech arm for `test-memfn-rows` today** (§5.3) |
| S804 | the predicate widened: the single-member test dropped, so a multi-member ret_pred renders `memchr` of its LOWEST member | pcrec never sends a multi-member ret_pred, so pcrec's corpus is blind to it by construction; only the contract's predicate space reaches it | G2 (the extended gate family's multi-member near-misses, §5.2); `memfnarms` (a 2-member fixture's pin must stay generic's) | DETECTED by G2 + arms |

Each row carries `SAB_REACH` (the witness compile or fixture showing the
row's text) and `SAB_DOC_FIGURE` hand-measured by the build lane ([MECH-REACH]).

### 5.2 G2: the predicate space comes from the CONTRACT

G2's `gate` family (`memfn/tests/g2/g2_gen.c:3036-3098`) always makes the
RUN window the ret_pred, so it never generates the R-15 shape. The
generated space (`plan_all`) reaches it only by accident: one predicate,
one term, one member at offset 0. The extension is a D27-blinded author's.
The author works from memfn.h's `mf_site`, integration.md §14.3-§14.5
and the row's contract table (§3.2), never from precheck.c's text. The
extension:

- **The landmark-gate shape:**
  - a one-member SET at offset 0 as `ret_pred`, at index 0;
  - `npred` 1, plus later parts admitted by the composite's rules (runs
    with `fn_ref`, singleton set-rest members);
  - the empty range MISS;
  - `miss` stated as n, and also stated as other text (must decline);
  - `on_miss_leaves` 1 and 0, `result_decl` stated and unstated.
- **Boundary near-misses the row must DECLINE, with the answer still
  right through `generic`:**
  - 2, 3, 255 and 256 members;
  - offset 1 and offset -1;
  - an OPTIONAL term or predicate;
  - `ret_pred` at a later index;
  - `table_ref` set;
  - `end_back` 1;
  - `empty` NOP/EXCLUDED/AT_N;
  - a stated `floor`.
- **Subjects:**
  - NULL with length 0, `lo == n`;
  - the landmark at `lo`, at `n - 1`, absent, and repeated (the LEFTMOST
    must be kept);
  - all 256 byte values as the member.
- **The oracle:** G2's reference (`g2_ref.c`), the contract's definition.
- **Floors:**
  - the family's `FAM_FLOORS` entry;
  - `FORM_FLOORS`, unchanged in count (same form id `precheck`);
  - a `g2_floor` for `precheck_assign_byte` in `row_floors.tsv`,
    measured floor(0.9 x) per its header.

### 5.3 Light vs heavy validation

**Light (the build lane, pinned, about minutes; box permitting):**
- `make -j16`, `make strict`;
- `make test-memfn-arms` (the new fixture's pin and behavioural checks);
- `make test-memfn-rows` (rows.tsv: the row, reach `pending-site`, the
  control);
- `make test-memfn-stamps`, `make test-memfn-manifest`,
  `make test-memfn-g2` (quick, the extended family);
- `scripts/emit_sweep.py --ref-bin <main> --every 20`: 0 movers, dumps 1;
- each of S800-S804 by its own mech row;
- the h2g twin of §0 item 5, before any code.

**Owed harness work, light:**
- a mech arm `memfnrows` for S803;
- a mech arm for G2 quick (only `g2simd` exists), or S802/S804 written to
  `memfnarms` behavioural checks alone.

**Heavy (the manager's slot):**
- the full `emit_sweep` (all streams, `--variant all`, `--arms start`,
  `--extra=-fmemfn-simd`);
- the full N2 census (the row at 0, pending-site);
- `make test-memfn-g2-full`;
- `scripts/perfrun --label r15 -- …` (`make test`).

**At L1's merge (main's), the §4 (a)-(e) set:**
- the `--event r15` mover classifier;
- the N2 census re-pinning the row's `pcrec_floor`;
- `test-axes` over the new deny.

**The official verdict:** a pcrec-bench run (D144 addendum 4) on
loglines/ipv6, loglines/ipv4 and bounded/dotted4, throughput and
search_short, comparing:
- BASE;
- L1+R-15;
- L1 with `--memfn=no-precheck-assign-byte`;
- `-fno-req-handoff`.

This joins rlhtwin's bench question 1.

## 6. The three standing design questions

1. **Measurement regime. RELEVANT.**
   - Every number cited is rlhtwin's scratch tier: a non-quiet box,
     interleaved, one pinned core, gcc 15.2 `-O2`, glibc's `memchr`
     (AVX2/EVEX-dispatched on the 7700X).
   - Kit timings are unofficial; the official verdict is the bench's.
   - A regime that could flip the decision: on short gaps (dense
     landmarks) the twin is `memchr`'s call term against an inline loop.
     On a libc without a vectorized `memchr`, or on the Mac's (arm64
     libc), S1's margin over generic differs.
   - The bench must read both boxes before any S5/V1 follow-up.
2. **Independent control. RELEVANT.**
   - The mover population is read from pcrec's stamps, and the mover set
     from a byte diff under the deny (§4 (a)-(c)). Neither comes from the
     kit's output or its trace.
   - G2's space comes from the contract, written blind (§5.2).
   - The population is counted by: the N2 census for the row (0 before
     L1, floored after) and L1's census for P.
   - Every sabotage carries a reach witness. S802 and S804 are honest:
     pcrec's corpus cannot see them, and only the kit's checks can.
3. **What moves when data is regenerated. RELEVANT, narrowly.**
   - The row reads no table, calibration or prior: the member is pcrec's
     `req_byte`.
   - Regenerating `row_floors.tsv` / N2 moves only pins.
   - If pcrec's byte-rate prior ever picks a different `req_byte`, the
     artifact's member byte moves (pcrec's selection, not the row).
   - The row's own bytes move only in the L1 abi event (§4).

## 7. Questions for Frank (each with a recommendation)

**Q-R15-1.** The re-entry's landmark scan: how does pcrec state it?
- *The problem.* The row is on the hot path only if the re-entry goes
  through it.
- *The ways pcrec can state it:*
  - (a) a second `mf_use` of the PRE site handle, with the re-entry's
    hooks (`lo` = `scan_position`, `result` the kept landmark, no decl,
    `on_miss` `return 0;`). One fact, one site. A run landmark's re-entry
    would then render `precheck_assign`'s text, including the OPTIONAL
    lead byte's `memchr` per restart, which rlhtwin's run-reentry twin
    (`rx_reqrun` alone) did not pay.
  - (b) a separate FIND/STMT/ASSIGN site. `pf_memchr` already renders it
    if pcrec proves the range non-empty (EXCLUDED); R-15 then serves only
    the cold entry.
  - (c) `mf_call` of the run's FUNC part for runs, plus (a) or (b) for
    bytes.
- *Recommendation:* (a) for both landmark lengths. The ret_pred is "found
  by the FIND contract" (§14.3), so the kit may, in a later row, skip an
  OPTIONAL lead on a use that keeps the position. Re-time kv-quoted on the
  build, as rlhtwin's bench question 1 already asks. This is main's
  design call in the L1 build lane. R-15's value depends on it.

**Q-R15-2.** Build the row before timing generic under re-entry?
- *Recommendation:* no. R-15 step 2 opens with the h2g twin:
  - h2 with the generic loop at both the entry and the re-entry;
  - built from rlhtwin's own `mktwin.py` artifacts in a scratch copy;
  - minutes;
  - after slot21, pinned.

  Build only if S1 beats h2g on the three cells (D77: rlhtwin measured
  memchr against generic only at the entry, where it was about 0). I
  expect a large margin, but it is a claim until timed.

**Q-R15-3.** Sequencing.
- *Recommendation:* the kit row lands FIRST at zero movers, reach
  `pending-site:REQ-HANDOFF-L1` (no abi event, only the `--list-axes`
  dump moves). L1's merge is then the ONE abi event carrying the row's
  first bytes, and the row's deny separates the two layers' movers
  exactly (§4). The alternative is one combined merge. It is equally
  valid, but it makes L1's mover census attribute two changes at once.

**Q-R15-4.** The forms with no population (table walk, SWAR, two-memchr
merge, the inline short probe, V1).
- *Recommendation:* file each as a BOONIES line in `memfn/docs/ideas.md`,
  with the trigger "pcrec states a multi-member landmark" (S2-S4), or "a
  profile shows `memchr`'s call term on the re-entry" (S5/V1). Build
  none now (D77, memory `pcrec-high-impact-focus`).

**Q-R15-5.** V2 (the dead-dot neighbour filter).
- *Recommendation:* file it as an UNLOCK on `[REQ-HANDOFF-L1]`, not on
  R-15. It needs pcrec to state the landmark predicate as a proven
  conjunction (the landmark plus neighbour classes). Its scalar layer
  already exists (the offset-set FUNC), and its SIMD layer is ideas.md
  entries 4-6.
- *Trigger:* after L1 lands, a bench reading in which the re-entered
  handoff trails rev-inner on dense-landmark subjects. rlhtwin's scratch
  run shows 1.5-1.7x on ipv4's syslog subjects.

The kit's own choices are not for Frank (memory
`pcrec-answer-free-choices-are-mine`):
- the row's name and its options.def spelling;
- the `arm.opt` field;
- the generic part rules in the predicate;
- the exact `memchr` spelling.

## 8. What this lane ran

- Three emits (ipv6, ipv4, dotted4) from main's `build/pcrec`
  (`taskset -c 0-3`, `gnutimeout 30`, rc 0 each), outputs in the job
  scratchpad (not committed).
- No build, no test, no timing.
- §1.2's walk is by reading, so an MF_TRACE run of the scratch site is
  owed (light, in step 2).
- Commits: this report and its index line in `docs/dev/lanes/CLAUDE.md`.
