# Lane ucpu3fix: review 2026-11-10 r4 ucpu3 FIX-NOW items on [UCP] U3

Branch `lane/ucpu3fix`, cut from `lane/ucpu3b` at 2b5adbff1. Scope: the FIX-NOW items of
`docs/dev/reviews/2026-11-10-r4-ucpu3.md`, as the manager's RULINGS there decided them. Scratch
evidence (plant trees, logs) is under `$PCREC_TMPDIR/scratch/ucpu3fix/`. Nothing was written outside the
repository and that directory.

## STATE AT HANDOFF

### Commits (oldest first)

| commit | content |
|---|---|
| f34dba46d | C: admission and diagnostics, the RECOVER stamp, the table pool, T5 removed, the memo bypass, the DECODE_BACK seam entry, the route table and the knee retired |
| 01ac66f4f | spec hunks, registry 84→83 and 43→42, reject knee rows, the island corpus regenerated, test-ucp §5, the partition gate retired |
| 808f99e19 | `tests/ucp/run_charstep_tests.sh` and the mech arm `charstep` |
| 092bdfa0a | the charstep corpus floor counts every case run |
| f35ec26ae | mech rows S3030-S3035 |
| 14b77d506 | the char-step method card (UNMEASURED) |
| 9f247001a | the char-step emitted comments are bracketed NONESSENTIAL, with no row id |

### Per finding: the fix and its proof

- **ADMIT-1 / RULES-6.** Over a char-step limit or a state cap, the pattern is REFUSED under every
  `--engine`. `limits.md` §3.9¶4 and §3.3.3¶1 now say so. `fit_sel1_eligible` has a
  `!island_route` conjunct, so the [SEL-1] VM retry no longer applies. Proof: the reject rows
  `char-step the state cap, --engine=auto/dfa` and `9 sets`.
- **ADMIT-2.** Every char-step refusal now names `(?aW)`; "try --engine=vm" is gone. `dfa_way_out`
  picks the way out, and byte-machine messages are unchanged byte for byte. Proof: the same rows, whose
  wording is asserted.
- **ADMIT-3.** A set that holds every non-ASCII character (`ISL_SET_ALL`) is not counted. The knee is
  exact: 7 scripts plus the word set is 8 sets and compiles; one more refuses. Atoms: n=29 is 32
  atoms and compiles; n=30 is 33 and refuses. Proof: four reject rows, plus mech S3034 (the plant
  that counts the set again turns the "8 sets" row red; the subject tip's table had no such row).
- **ADMIT-4 / EMIT-2.** Char-step artifacts stamp `RX_DFA_START "reverse-pass"`, through
  `CandLocate.own_recover`. `match_api.md` now names char-step in the reverse-pass table row.
  Proof: the route pin checks the stamp on all 46 patterns.
- **ADMIT-5.** The refusal now picks the LEFTMOST UCP context (`keep_leftmost`; the visit walks right to
  left). The start-anchor refusal fires on an anchor ANYWHERE in the pattern, at the anchor's own offset:
  `^` now carries `reg_at` (parse.c), and `pcrec_start_anchor_of` finds it. cli.md says "contains".
  Proof: the reject rows `a start anchor in a later branch` (offset 10) and `the leftmost Unicode word
  context named` (offset 6).
- **ADMIT-6 / RULES-7.** No refusal carries a row id; the reject helper fails any refusal containing
  `[UCP]`. Names are below, for main to check. The one emitted `[UCP] U3` comment is gone (9f247001a).
- **EMIT-1.** Built as a general mechanism: `src/gen/tblpool.c` is a content-keyed, file-scope table
  pool (`pcrec_tbl_ref`/`_emit`/`_done`). It is adopted by the char-step machines: forward, reverse
  and retry share one copy of each identical table. Measured rodata on three char-step artifacts:
  19,616→9,986, 29,406→10,112 and 20,359→10,473 bytes; the duplicate census reports 0 groups. Byte
  identity: 35 non-char-step artifacts (both encodings, VM/DFA/attempt/lookaround/UCP byte tier,
  `--engine=vm`) are byte-identical to a build of the subject tip 2b5adbff1; only the 2 char-step
  ones moved.
  - The scope question (should the byte machines adopt the pool here?) got no reply. I took my stated
    leaning: no shipped byte moves in this landing, so there is no abi event. Adopting the pool for
    the byte DFA (10 of 12 sampled byte artifacts duplicate tables) is filed as its own abi event in
    the PLAN rows below.
- **EMIT-3.** `DState.isl_kind`, `DFA_ISL_*` and `PCREC_DFA_ISLAND` are removed. `tr[isl_na]` holds
  `PCREC_DFA_DEAD`, and the allowlist moved with them (`ISL_SET_NONE`/`ISL_SET_ALL` were added).
- **EMIT-6.** Verified before fixing. The path IS reached: `(*UCP)\b\w{9000}\b` takes a second build of
  both char-step machines (4 memo stores, 0 hits), because the key compares arena pointers, which
  differ, so the unsafe restore was never taken. Fix: `dfamemo.c` bypasses the memo for char-step
  machines, and the branch's wiv/island key fields and the `nchr` copy sizing are removed.
- **RULES-1.** OWED, not run: the [ART-POSS-ARMS] `utf,ucp` re-sweep (`r21_claimmark.py UCP_PIN`).
  The evening box hold and the full suite running made it a landing-checklist item for main.
- **RULES-3 (small parts).** The driver reads selection's verdict (`Ctx.island_route`) instead of
  calling `pcrec_island_needed` again. The attempt refusal is selection's `island` row reason, and
  the driver's arm is now an internal error. The T4 table is a PLAN row (below).
- **RULES-5.** New seam entry `PCREC_ENCE_DECODE_BACK` (`$_decode_back`), re-spelled on `$_decode`,
  with ⊥ = 0. The private `<prefix>_isl_back` is removed. A missing DECODE or DECODE_BACK is an
  internal error. A D58 record is drafted below.
- **RULES-9.** The UCP route table and its dead refusal are deleted (mod_ucp.c, ext.c,
  mod_classes.c; `pcrec_setdef_class` is now infallible). `PCREC_UCP_NARROW_MAX_INTERVALS` is
  RETIRED (registry 84→83 rows and 43→42 anchored), and limits.md §3.8 is rewritten.
- **checks-1/7.** The reject knee rows and an `--engine=vm` row. Plant S3035, which drops the
  `--engine=vm` refusal, is caught by the new row; the old reject table's failures are identical with
  and without the plant.
- **checks-2/6.** The ill-formed file now has `mg` cells and hand subjects with a bad byte at each
  place a walk reads one, plus every startpos just after a bad byte.
  - Forward-step plant (S3033): the old corpus caught 8 cells, the new one 49.
  - Reverse-step plant ("moves 2"): survives every cell old and new. It is EQUIVALENT: no consuming
    set holds ⊥ and a reverse machine has no all-bytes loop, so the reverse walk is dead after a ⊥
    atom whatever the step. It is not a mech row.
- **checks-3.** Only DIVERGING cells are left out: 21, each named in `island_illformed.rxt`'s header
  (input `tests/ucp/island_diverge.tsv`). All are empty matches of nullable patterns. They fall
  under §9.5¶2 (stray continuation), ¶3 (ill-formed end) or the new ¶2a (between two ill-formed
  units). Every other empty-beside-ill-formed cell is written, since it agrees with PCRE2.
- **checks-4.** Edge blocks generated from libpcre2: the word set read from both sides (926
  intervals, 3,232 cells each), `\d` (280 cells) and `\p{Greek}` (142 cells).
  - Plant S3030 (`<=`→`<`): new nets 3,936 of 8,728 cells red.
  - In this tree the subject tip's corpus also catches it, on one pattern (13 cells, `é\b`). That is
    unlike the critic's report; the new net no longer rests on one literal.
- **checks-5.** Two patterns where the retry machine succeeds (`(*UCP)\b(?:|\w+)`, `(*UCP)\b\w*?`),
  with `mg` cells.
  - FINDING: the old corpus's `mc` cells can NEVER see the retry. `mc` is the protocol with no retry
    (rxt_format.md §1.7¶2), while the generator wrote PCRE2's global count with retry; they agreed only
    because no old pattern's retry succeeded. The generator now writes `mg` (§1.7.1, through
    `<prefix>_next`).
  - Plant S3031 (retry always -1): the old corpus is green (0 of 933 red), the new one 33 red.
- **checks-8.** The partition gate is retired with RULES-9. `ucp_sets.py` loses its `wide_utf8`
  column; `ucp_compare.py` now checks construct==spelling for every utf8 set (49 checks, all
  pass). The island sweep arm is a PLAN row (below).
- **checks-9.** New runner `tests/ucp/run_charstep_tests.sh` (test-ucp §5, mech arm `charstep`), and
  the generator moved into tests as `tests/ucp/gen_island_rxt.py`. It runs:
  - the corpus, with a floor of 8,000 cases (today 8,728);
  - the ROUTE PIN: every one of the 46 patterns stamps char-step, reverse-pass and SCAN_EDGE none
    (floor 40);
  - the MIU-aware libpcre2 verifier (`--verify`): 7,403 and 1,325 cells agree.

  Mech rows S3030-S3035, with REACH probes checked by hand. H2 (S3032): a byte scan edge on the
  char-step reverse machine turns 15 cells red (the old corpus: 9). The same plant on the retry
  machine's guard is answer-equivalent (the char-step retry walk reads no scan-edge field) and is not
  a row. A forward-machine scan edge makes the compiler stop at an internal error.
- **§9.5 wording** (ANSWERS-1): new `match_api.md` §9.5¶2a, "an empty match between two ill-formed
  units". Re-measured on 10.46: `\B` over `61 c3 c3 61` gives pcrec (2,2) from 0, 1 or 2; libpcre2
  gives no match from 0 or 1, and (2,2) from 2.
- **Measurement card.** The arm `cs` in `studies/u3_island_twin/` (gen_bases cases x3/x3b and
  run_bench) is the char-step DFA as built. Labelled UNMEASURED until a timing window runs it.

### Local validation (all green)

- `make strict`.
- The two island .rxt files through the harness: 8,728 of 8,728.
- `make test-ucp` in full: verify_ucp 9,058 cells, ucp_compare 49/0, ctxnode, charstep 3/3.
- `run_reject_tests.sh`: 0 failures, counts unmoved.
- `run_registry_tests.sh` (limits_check 42/0).
- The K37 sweep: one hit, `tests/doc_lint/run_doc_lint.sh:33`, which main already fixed in dc1988069.
  It comes from this branch's base and goes away at merge.
- Mech rows VALIDATE_ONLY: FIELDS OK, 6 of 6.
- `check_claudemd_size --all`.
- I did not run make test, test-axes, ubsan, asan or mech locally; those are queued.

### Queued (OWED, the lane's last act)

- `440-main-ucpu3fix-maketest`: make test, via perfrun, log `scratch/ucpu3fix/maketest.log`.
- `441-main-ucpu3fix-axes`: make test-axes.
- `442-main-ucpu3fix-ubsan`: make ubsan.
- `443-main-ucpu3fix-asan`: make asan.
- `444-main-ucpu3fix-mech`: mech S3030-S3035.

Jobs 430-433 (`main-ucpu3b-*`, the old tip) are CANCELLED with `boxqueue cancel`.

## Names proposed (D174; main checks at landing)

| was | now | where |
|---|---|---|
| `RX_DFA_SCAN "island"` | `"char-step"` | stamp, `rx_info.scan`, cand row `.c`/`.tok`/`.scan` |
| `RX_DFA_START "attempt-start"` on char-step | `"reverse-pass"` | stamp (ADMIT-4: it does run a reverse pass) |
| `decline:island-nfa` | `decline:char-step` | facts listing token |
| `PCREC_MAX_ISL_SETS/ATOMS` | `PCREC_MAX_CHAR_STEP_SETS/ATOMS` | limits registry |
| "island sets/atoms" | "non-ASCII character sets/atoms" | diagnostics |

The internal row and field names (`island` selection row, `Nfa.island`, `isl_*`) are unchanged: they
are not caller-facing.

## Drafts for main (decisions.md is not edited by this lane)

**D130 addendum (RULES-8).**
- [UCP] U3 lifts U1's wide-set refusal under `-e utf8` by PARITY: a wide UCP set compiles as the
  class its `\p{..}` spelling is, on the all-byte route. Example: `(*UCP)\w+` is byte-identical to
  `\p{Xwd}+` (613 KB).
- This is not the kit-sized DFA route item 3 conditioned the lift on. Such patterns move from "refused
  by name" to "shipped large, degraded or refused by size", like any large `\p{..}` class.
- `PCREC_UCP_NARROW_MAX_INTERVALS` is retired with the route table (review r4 ucpu3 RULES-9). The
  kit-sized route stays OWED under [CLS-TREE] / the kit producer.

**D134 addendum (RULES-2).**
- Item 2's MEASURED island-vs-hybrid row is met only vacuously at U3: no hybrid exists for UCP `\b`
  under utf8 until U4 lets the VM read the set, so the char-step DFA is a capability row
  (`ENGM_DFA` mask), not a priced one.
- The measured row is owed. Trigger: U4 or the D134 timing measurement, whichever comes first. It is
  due before the `island` row's mask changes.
- Evidence to start from: `u3_island_twin.md` has the island 1.35-2.8x slower than the hybrid on mixed
  and CJK subjects; the method card (arm `cs`) is UNMEASURED.

**D58 record (RULES-5).**
- New encoding entry `PCREC_ENCE_DECODE_BACK` (`$_decode_back`, inline_def, requires DECODE): the
  character ENDING at a position, with 0 for one ill-formed byte. It is re-spelled on `$_decode`, so
  forward and backward segmentation agree by construction.
- It differs from `$_back_step` on purpose: there an ill-formed byte is NONE, here it is a character.
  It is read by the char-step DFA's reverse walk and forward seed. `entries_byte[]` needs no row: the
  byte encoding never builds a char-step machine.

**known_issues row (the ¶2a divergence).**
- K-next: an empty match between two ill-formed units. `\B` (UCP or not) over `61 c3 c3 61` under
  `-e utf8`: pcrec (2,2) from startpos 0, 1 or 2; libpcre2 10.46 under MATCH_INVALID_UTF gives no
  match from 0 or 1, and (2,2) from 2.
- Every engine and the char-step DFA alike; pre-existing (BASE non-UCP `\B` is identical).
- Arguably a PCRE2 inconsistency: a search from 0 misses what a search from 2 finds.
- Owner: a pcre2-reader note on whether it is a PCRE2 bug (D26 addendum: compatible unless a PCRE2
  bug). Spec: match_api.md §9.5¶2a. The repro cells are named in `tests/utf8/island_illformed.rxt`'s
  header.

**PLAN rows (new, not scheduled).**
- [UCP-SKIM] (EMIT-4): a failing `<prefix>_match` on a char-step artifact runs the whole walk (the
  fifth search-filter population, now documented in §3.2¶6). Fix shape: an anchored char-step machine.
  Trigger: the first demand for match-here on UCP `\b`. Under the speed loop.
- [TBL-POOL-BYTE] (EMIT-1 second half): the byte DFA's forward, reverse and anchored machines adopt
  `tblpool.c`. 10 of 12 sampled artifacts duplicate tables (byte_class, is_accepting, ...). This is
  an abi event (bump plus identity re-pin) in one change.
- [UCP-T4-TABLE] (RULES-3): machine form T4 as a declared `machine_form_rows[]`, each optional
  machine's `applies` declining on `Dfa.island`. Trigger: the next char-step follow-up (T5 fast path,
  scan edge or attempt char-step).
- [UCP-SEGTEST] (RULES-4b): the char-step character test (segment table plus binary search) becomes
  the kit's membership producer. Trigger: U4.
- [CHAR-STEP-FAMILY] (RULES-11): the design note unifying the five "decode one character, then test
  it" mechanisms into one encoding-owned step plus one membership producer, with the review's unlocks
  and triggers.
- [UCP-ISLSWEEP] (checks-8 PLAN): the char-step sweep arm `(*UCP)\b<set>` over every code point, if
  the edge blocks prove insufficient. Trigger: a char-step answer bug that the edge blocks missed.
- RULES-1 owed: the [ART-POSS-ARMS] `utf,ucp` re-sweep (`r21_claimmark.py UCP_PIN`), on main's
  landing checklist.
