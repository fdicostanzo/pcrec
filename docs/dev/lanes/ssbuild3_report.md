# ssbuild3 — START-SET stage 3, THE DFA HAT (lane report)

Lane `ssbuild3`, 2026-10-06, opus. Branch `lane/ssbuild3` off main
`57db5152` (stage 2 landed, abi 62). Builds `docs/design/startset.md` §8's
stage-3 row (rev 2 + ssedge's §6.4) under D148 + addenda 1-2. **AN ABI
EVENT: this lane's number is 64** (63 is reserved for the memfn kit's R4a′;
see §1 for how the bump was drafted). A fresh agent resumes from §9.

## 0. Summary, against §8's stage-3 row and the manager's list

| item | where | state |
|---|---|---|
| F on the rows (`T = S ∩ E*` admitted iff `T` is a non-empty PROPER subset of `E`; the scan-kind, seeded, non-nullable and `|S| < 256` conjuncts) | `src/gen/emit_dfa.c` `pf_dfa_start_set`, `dfa_estar` | built |
| the BUILD ASSERTION `T == S` (Q-R1) | `pf_dfa_start_set` | built; fires on 16 corpus blocks under an "E* without one seed" mutant (§4) |
| the `-bounded` twins `first-memchr-bounded` / `first-class-bounded` | `dfa_pfs[]`, `pf_emit_first_memchr_bounded`, `pf_emit_first_class_bounded` | built |
| the unbounded DFA forms | — | NOT built: §6.4.3 item 3 (a seeded machine is a views machine); ASSERTED in `pf_dfa_start_set` ("seeded ⇒ views"); `first-class` stays VM-only |
| the CONDITIONAL re-seed through wrapper emitters | `pf_emit_moved_reseed`: `if (scan_position > skip_from) forward_state = seed[class(s[pos-1])]` | built |
| the scanned set read by every reader (K84's field kept honest) | `DfaPf.scan_set` + `pf_scan_set_of`: `dfa_form_derive`, `dfa_cand_scan` (G1), `pcrec_dfa_cand_ppm` (re-seed density) | built |
| the count-collapsed FAILING witness `\B(a|b){1,3}` on "xa" | `hybrid.rxt` (HYC), the differential's `collapse` config, transcript §3.3 | shown: hat (1,2), no-re-seed twin LOSES at startpos 0 |
| sabotage S480-S490, S495 (detector added), S501-S502 (arms added), S504 | `tests/mech/sabotages/`, new mech arm `dfahat` | §5 |
| F3 at the dense movers | `docs/dev/optloop/startset/alpha_s3.sh` | WRITTEN; Linux run is the manager's (§7) |
| fixtures home | `tests/startset/dfahat.rxt`, `reseed.rxt`, `hybrid.rxt` (ssedge drafts via `edge_import.py`), `dfahat_paths.rxt` (hand, python-verified) | done |
| checks | `tests/startset/run_dfahat_checks.sh` (`make test-startset`), `dfahat_checks.py`, `vmhat_diff.py` under `HAT=dfa` | green (§4) |
| spec hunks (D80) | `match_api.md` §6.3 (two values), `tuning.md` §2.42 (+ dial cell), `registry.md` §6 (129 rows) | done |
| mover manifests | regenerated with the PRE-STAGE-3 compiler (`docs/design/startset/s3/`) | done |

## 1. The abi event (62 -> 64), readers found by grep

**Drafted 62 -> 64, and R4a′ had NOT landed.** At the merge of main
`f69089bf` (merged ALONE, `eb4f07ba`; ARTREV docs only, no `src/`),
`PCREC_ARTIFACT_ABI` still read 62 on main, so 63 (the memfn kit's R4a′)
has no artifact yet. This lane bumps straight to 64 as briefed; whichever
of the two lands second re-reads the other's ledger entry (§6's narrative
and the codegen ledger name 63 as R4a′'s). `match_api.md` §6's 64
entry names 63 as R4a′'s; if R4a′ is dropped, 63 is a gap and that
sentence is what explains it.

The readers, found by `grep -rn` for the old number (code, tests, spec):

| reader | change |
|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` (feeds both emission sites: the generated-by line and `rx_info.abi`) | 62 -> 64 (`b42dffa6`) |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` + its ledger message | 64, ledger gains the stage-3 clause (copied from §6) |
| `docs/spec/match_api.md` §6 (the abi narrative) | new head entry for 64, the 62 entry demoted to "was" |
| `docs/spec/match_api.md` K80 `#error` worked example | 62 -> 64 (both lines) |
| `tests/codegen/run_recursion_identity.sh` (B) `FILEPIN` | self-pinned to `b42dffa6`, the lane's last `src/` commit |
| `tests/codegen/CLAUDE.md` | the stage-3 bump paragraph |

Readers that cite no abi digit but read bytes the bump could move (the
D94 addendum's second class): the cpset `EMITTED_BYTES` manifest and the
resource K59-PREMUL pin are unchanged, because 62 and 64 are one digit
wide (both re-run green after the bump, §4). `tests/startset/
CLAUDE.md`/`src/gen/CLAUDE.md` name the abi as history and were written
at 64. `docs/spec/match_api.md` §6.3's two new `RX_DFA_PREFILTER` rows cite
"abi 64".

## 2. What was built, and the four choices the design left open

1. **The table is `<p>_start_bytes`, not `can_begin_match`.** `T` is a
   different set from the escape set (`E`), and seven checks read
   `rx_can_begin_match` meaning `E` (`run_dfa_stamps.sh`,
   `run_offset_skip.sh` §2c, `run_anchored_match.sh`, `startset_lib.
   machine_sets`, ...). A new name keeps every one of those true, makes the
   hat greppable, and keeps the VM hat's `rx_start_set` (inside
   `<p>_search_run`) from colliding with `vmhat_checks.py`'s table count.
2. **`DfaPf.scan_set`, a row METHOD, is the predicate core itself.**
   `pf_dfa_start_set` both answers F and fills `T`; the rows' `applies` call
   it and `pf_scan_set_of` (the one place a reader of the scanned set asks)
   calls it again. So `T` has ONE derivation with four readers (the table or
   `memchr` byte, the `can_begin`... G1's byte, the re-seed density), K84's
   rule extended from the scan KIND to the scanned SET.
3. **Every DFA-route `DfaSel` that walks `dfa_pfs[]` carries `.ss`**
   (`dfa_pf_of`, `pcrec_dfa_scan_state_written`, `dfa_form_derive`,
   `pf_scan_set_of`), so the `start_set` fact is asked on every compile with
   a DFA scan (it already was, since stage 2's every-artifact stamp asks it).
4. **The re-seed's `skip_from` is declared in the hat's own block**, so it
   names the skip's entry and nothing else; one conditional line serves both
   landings (a hit and the `n - 1` clamp). The memchr twin keeps
   `memchr-bounded`'s `if (scan_position + 1 < subject_length) { ... }`
   shape around it.

## 3. Movers, manifests, and the three cross-row classes

### 3.1 Movers by ID

`tests/startset/dfahat_checks.py` over 3,528 artifact pairs (every corpus
block at its own options, default vs `-fno-start-set`):

| population | movers | `first-class-bounded` dfa / hybrid | `first-memchr-bounded` dfa / hybrid | vs manifest |
|---|---|---|---|---|
| corpus | 71 | 29 / 13 | 22 / 7 | == `manifest_s3_dfa.tsv` by ID, 0 off-diagonal |
| pcrec-bench (read-only, counted) | 18 | 9 / 7 | 0 / 2 | 18 of 18 rows move |

The manifest was REGENERATED by the stage-1 census instrument, unchanged,
run with the PRE-STAGE-3 compiler (main `57db5152`), so its `F` comes from
the deny-equivalent artifact's tables and the `--emit-facts` row and never
from this lane's selection: `s3_dfa` +39 rows (23 `dfahat.rxt`, 9
`reseed.rxt`, 6 `hybrid.rxt`, 1 `dfahat_paths.rxt`), `s2_vm_forced` +54 / -1
(the new fixtures are VM-hat movers under `--engine=vm`; the one removed row is
`tests/ucp/ctxnode.rxt:400`, whose (text, options) twin in `dfahat.rxt` now
sorts first in the census's dedup and takes its id), `s2_vm_auto` +0. The 32
pre-existing corpus rows and 18 bench rows did not move.

### 3.2 The deny arm and the cross-row classes (§4.3)

Non-movers: byte-identical to the deny arm (3,457 pairs; 176 VM-hat movers
are left to `vmhat_checks.py`). Movers: identical once the stamp, the
`rx_info.prefilter` value, the two tables and the skip block are normalized,
EXCEPT three cross-row classes, counted: **G1 28** (`RX_REQ_WHY "emitted"`
-> `"dominated"`: a one-byte `T` is the pre-check's byte, so the pre-check is
elided), **hybrid re-seed row 7** (`RX_VM_RESEED "adaptive-dense"` ->
`"adaptive"`: the mass over `T` is below the dense row), **scan edge 15**
(`RX_DFA_SCAN_EDGE`: precondition (8) reads `reseeds`). A mover in a class is
re-compiled on BOTH arms with `-fno-req-byte -fno-req-run -fno-hyb-reseed
-fno-scan-edge` and must then be equal outside the hat: 0 violations.

### 3.3 The count-collapsed failing witness (sound-F5(d))

`\B(a|b){1,3}` under `-fprefilter-collapse` (a VM hybrid, `RX_VM_PREFILTER_LANG
"count-collapsed"`), on "xa", deny / hat / the hat with its re-seed deleted
(emitted `if (0 && ...)`), one TU:

```
PA_DFA_PREFILTER "byte-class-bounded"   (deny)
PB_DFA_PREFILTER "first-class-bounded"  (hat)
xa  @0 deny=1(1,2) hat=1(1,2) hat-no-reseed=0(-1,-1)
xa  @1 deny=1(1,2) hat=1(1,2) hat-no-reseed=1(1,2)
xa  @2 deny=0(-1,-1) hat=0(-1,-1) hat-no-reseed=0(-1,-1)
```

The obligation is met on the BUILT artifact. The differential's `collapse`
config reaches every hybrid mover collapsed, and S481/S482 are red there.

### 3.4 `scripts/emit_sweep.py` against main, and the MOVER TABLE

`python3 scripts/emit_sweep.py --ref main` (main `f69089bf`, abi 62) against
this lane's build (abi 64). The self-check (main against a second build of
main) is all-identical at full reach. The real run:

| stream | reach | movers | asymmetric |
|---|---|---|---|
| `.c` default engine (`--features all`) | 4,147 | 4,147 | 0 |
| `.c` `--engine=vm` | 4,148 | 4,148 | 0 |
| `--emit-ir --engine=vm` | 4,148 | 0 | 0 |
| composition (38 producing files) | 108 artifacts | 108 | 0 |
| registry dumps | 7 | 1 (`--list-axes`: the two new `prefilter` rows, re-ordered after `first-class`) | 0 |

The sweep prints five movers per stream, so every `.c` mover was classified
by a separate pass (scratch `mover_table.py`, the sweep's own corpus
enumeration and compile line, the ref binary the sweep built). Each mover
gets ONE class: **abi** (main's text with its four abi spellings rewritten 62
-> 64 equals ours), **stamp** (every differing line a stamp line),
**hat** (our artifact names a DFA-hat value AND our `-fno-start-set` build
equals main's `-fno-start-set` build once its abi is rewritten), or
**FINDING**.

| stream | abi digit only | stamp lines | the DFA hat's table + seek | anything else (FINDING) |
|---|---|---|---|---|
| `.c` default | 4,059 | 0 | 88 | **0** |
| `.c` `--engine=vm` | 4,148 | 0 | 0 | **0** |

88 rather than §3.1's 71 because the sweep compiles every pattern line at
`--features all` with no per-block options (the census reads each block's
own). Forced `--engine=vm` has no DFA scan to put the hat on. The
composition movers are the abi digit (all 108; the composed patterns carry
no hat mover).

## 4. Gates (Mac, this lane)

All runs at the merged tree (main `f69089bf` merged alone as `eb4f07ba`),
abi 64, `CC=gcc-16`, `TMPDIR` in the session scratchpad. Logs are listed
in §9.

| gate | result |
|---|---|
| `make strict` | clean (`-Werror -Wshadow`) |
| `make test-startset` | 3 scripts green: start_set 3/0, vmhat 22/0, dfahat 21/0. The DFA-hat fixtures are 1,769 cases / 0 failed. Its differential covers 219 (mover, config) pairs and 1,155,139 cells with 0 defects. The VM-hat differential covers 528 pairs and 3,165,576 cells with 0 defects. |
| the DFA-hat differential under `SAN=1` (ASan + UBSan) | 219 pairs, 1,155,139 cells, 0 defects |
| `make test-codegen` | the only red is the accepted darwin `nm could not read arm_a.o`. Its first run also had `run_offset_skip.sh` §2c red, a reader this hat moved (finding 2). After the fix: offset_skip 23/0, anchored_match 20/0 (four mechanisms) |
| `test-registry` (axes pin 193 -> 199, 129 rows) | green in the full run |
| `test-rxtsource` | 267 passed / 0 failed / 1 RECORD (the darwin python-3.9 C3 note). The census is re-pinned for the four fixtures: 271 files / 4,594 blocks / 41,005 lines |
| `tests/codegen/run_cpset_structure.sh`, `tests/resource` | 28/0; 0 failed (1 darwin skip) |
| `AXES=-fno-start-set SKIP_ORACLE=1` over the 18 mover files | `-fno-start-set`, `--engine=vm`, and their product: 5,905 / 5,905 keys agree on each, 0 mismatches, 0 give-ups. The product arm's whole-corpus floor (11,000 mover cases) reads 4,635 on this subset; that is the subset (OWED item 2) |
| sabotage anchors (`scripts/m6read_check_sab_anchors.py`) | 458 rows, 474 anchor sites, all resolve |
| **the FULL Mac `make -k -j4 test CC=gcc-16`** at `3cf1cfbf`, detached under caffeinate, holding `worktrees/.mac-suite.lock` (released) | **`sections ran: 52/52`; the ONLY `*** [test-X] Error` is `test-codegen`, and the only FAIL line in it is the accepted darwin `nm arm_a.o`.** Wall 2,571 s. `-k` so one red cannot hide a later section |

### 4.1 The §6.4 mutation table, on this build

| mutant (§6.4.2) | how it is seen here | evidence |
|---|---|---|
| correct DFA hat (control) | — | differential 0 defects; fixtures 1,769 / 0 |
| `T = S ∩ E` (r3, sound-F1) | S480 | 23 failing fixture cells (the six `W` witnesses) plus three structural arms |
| E* missing one seed state | the `T == S` BUILD ASSERTION | a scratch mutant (`dfa_estar` skips the last seed) REFUSES 16 corpus blocks — the six sound-F1 witnesses and their fixture copies — with the assertion's internal error; the other 3,512 artifacts are byte-identical (an equivalent mutant on every mover, §6.4.3 item 6) |
| E* missing s0 | equivalent on this build | the same scratch run: 3,528 of 3,528 byte-identical. ssedge's twin saw it (7 of 10) because it read the seed family off the emitted table; in pcrec `s0` and `s1u[UPC_PLAIN]` differ only by the start-of-subject and `\G` bits, and a pattern that reads those takes the ATTEMPT scan, so on every unanchored machine `E*`'s union already holds `s0`'s escapes. [Corrected at ssfix3, sound-F2: this cell first cited `start_pinned_assert_routing`, which runs on the pinned branch only; the identity rests on engine routing, now pinned by `dfahat_checks.py` [dfa-bot].] |
| re-seed removed | S481 (class), S482/S484 (memchr hit / clamp) | 109 / 5 / 6 fixture cells; differential 96 / 81 / 25 pairs |
| re-seed UNCONDITIONAL | S485 | 31 fixture cells (reseed.rxt RS), differential 18 pairs |
| seek before `rx_valid_upto` (DFA) | S504 | the differential's `-futf-check` config, 6 pairs (deny -9, plant 0) |
| seek from `search_from` instead of `max(search_from, lo)` | equivalent (§6.4.3 item 7) | the hat runs inside the scan, after the K82 handoff's seeded start: the skip starts where the handoff put the scan |
| `first-class-bounded` clamp landing re-seed deleted | S483 | 12 fixture cells (`\B(?<!a)[de]` on "xd"), differential 12 pairs |
| `T` missing one member | S502 / S501 (the walk drops or mis-reads bytes, so `T` misses members) and the start-byte oracle | S502: 7 fixture cells + 36 differential pairs; per-member reach is the oracle's (§6.4.3 item 8) |
| `T = Tdfa` | not buildable without a second derivation; `[dfa-table]` pins `T == S` | — |

## 5. Sabotage rows (START-SET's S480-S490, S495, S501-S502, S504)

Solo runs, `bash tests/mech/run_sabotage_matrix.sh <id>` one row per run,
at `8c69a359` (KEEP=1, two chains of rows in parallel, the suite lock held):
**every row scored as expected — 0 unexpected, 0 undetected, 0 anomalies**.
The detecting arms are read from each row's kept `dfahat.log`: `[dfa-fix]`
is the four fixture files through the harness (answer level), "diff" the
every-startpos differential's defective (mover, config) pairs.

| id | plant | verdict | dfahat | how it is seen |
|---|---|---|---|---|
| S480 | `T = S ∩ E` with r3's admission, `T == S` assertion off (sound-F1) | DETECTED | 4 fail | 23 fixture cells (the six `W` witnesses), `[dfa-table]`, `[dfa-movers]`, `[dfa-wit]` |
| S481 | `first-class-bounded` re-seed deleted (re-aimed from the unbounded form) | DETECTED | 99 fail | 109 fixture cells; diff 96 pairs (32 auto / 30 collapse / 32 nocaps / 2 utfcheck); structural |
| S482 | `first-memchr-bounded` hit-path re-seed deleted (re-aimed) | DETECTED | 84 fail | 5 fixture cells; diff 81 pairs; structural |
| S483 | `first-class-bounded` clamp-path re-seed deleted | DETECTED | 15 fail | 12 fixture cells (`dfahat_paths.rxt`'s `\B(?<!a)[de]` on "xd"); diff 12; structural |
| S484 | `first-memchr-bounded` clamp-path re-seed deleted | DETECTED | 28 fail | 6 fixture cells (`\B(?<!a)d` on "xd"); diff 25; structural |
| S485 | the re-seed made unconditional | DETECTED | 21 fail | 31 fixture cells (reseed.rxt RS, `(?:\b|xy)a` on "xya"); diff 18; `[dfa-reseed]` |
| S486 | `T` widened by one byte of `E \ S` | DETECTED | 4 fail | `[dfa-table]` (T != S), `[dfa-wit]` (aws leaves the memchr form); answer-invisible by design |
| S487 | F's seeded conjunct removed | UNREACHED (expected) | — | reach MISSING; E within S on unseeded machines |
| S488 | F's non-nullable conjunct removed | DETECTED | 2 fail | `[dfa-movers]` + `[dfa-table]` on `\b\B|\b(?:ab|cd)`; answer-equivalent by argument (row header) |
| S489 | F's `|S| < 256` conjunct removed | UNREACHED (expected) | — | reach MISSING |
| S490 | F's scan-kind conjunct removed | UNREACHED (expected) | — | reach MISSING; `dfa_pfs[]` is consulted on ENG_UNANCH only |
| S495 | `pcrec_dfa_cand_ppm` reads the row name (K84) | DETECTED | candrows 1, dfahat 1 | `[dfa-wit]` `(?<=ab)z|\bw`'s `RX_VM_RESEED` adaptive -> adaptive-dense |
| S501 | the walk reads a lookaround as consuming | DETECTED | startset 2, vmhat 18, dfahat 17 | dfahat: `[dfa-movers]` + diff 16 pairs |
| S502 | the walk's `A_CAT` drops `null(l) ? F(r)` | DETECTED | startset 2, vmhat 63, dfahat 40 | dfahat: 7 fixture cells, diff 36 pairs, `[dfa-movers]`, `[dfa-wit]` |
| S504 | a no-candidate return above `rx_valid_upto` | DETECTED | 6 fail | diff `utfcheck` config only: 6 pairs, deny -9 vs plant 0 |

Every DETECTED row's REACH probe was evaluated on the clean build first
(`reach:ok(1/1)` in every row above); the three UNREACHED rows' probes
read MISSING, as their `SAB_EXPECT_REASON` says they must. S501/S502's
probes had stopped matching since stage 2 (they pinned the facts listing's
`used` column at `no`, and stage 2's every-artifact stamp turned it `yes`);
re-aimed here, intent unchanged.

**What S481/S482 replaced.** §6.3 named the UNBOUNDED `first-class` /
`first-memchr` forms; ssedge (§6.4.4) showed the DFA hat has no unbounded
population. The unbounded forms are not built (an assertion in F guards
the reading), and the two ids moved to the bounded forms' re-seed (whole,
and the hit path) beside S483/S484 (the clamp path of each form), so all
four (form x landing) cells have a detecting row.

## 6. Findings

1. **`E*` without `s0` is an EQUIVALENT mutant in pcrec.** ssedge's twin
   detected it (7 of 10) because it read the seed family off an emitted
   table. In the compiler `s0` and `s1u[UPC_PLAIN]` differ only by the
   start-of-subject and `\G` bits, and every pattern that reads them routes to
   the attempt scan, so on an `ENG_UNANCH` machine the union over the live
   seeds already holds `s0`'s escapes [corrected at ssfix3, sound-F2: this
   first cited `start_pinned_assert_routing`, which runs on the pinned branch
   only; the routing is now pinned by `dfahat_checks.py` [dfa-bot]]: 3,528 of 3,528 artifacts
   byte-identical under the mutant. `dfa_estar` keeps the `s0` term because it
   costs nothing and does not lean on that identity.
2. **A new table NAME keeps a reader's needle true, not its POPULATION.**
   §2 item 1 chose `<p>_start_bytes` so the checks that read
   `rx_can_begin_match` as `E` stay true, and their needles did. But
   `run_offset_skip.sh` §2c builds `uuid` with `-fno-offset-skip` to obtain
   `E`, and without the offset row `uuid` is a DFA-hat mover, so that build
   now emits `start_bytes` and the guard read nothing (`test-codegen` red,
   "could not read both offset-0 tables"). The guard's build now also denies
   the hat. Two checks that enumerate the candidate-start MECHANISMS by needle
   (`run_anchored_match.sh` §2, `run_mline_diff.sh`'s population) gained
   `rx_start_bytes[` as a fourth, with a witness for the anchored one.
3. **ssedge's `hybrid.rxt` draft carried HEAD declarations** (`config` +
   four `target` lines for `-fprefilter-collapse`). A head makes a corpus
   file unreadable to `verify_rxt.py` and the harness builds no target, so
   the first import put 14 reds into `test-rxtsource` (legs B/C disagreeing,
   the census, a `name` keyword collision). `edge_import.py` now drops head
   `config`/`target` lines and comments their `name` lines (line numbers
   hold); the collapsed compile is the differential's `collapse` config,
   which is where S481/S482 are red.
4. **S501/S502's REACH probes had been stale since stage 2.** Both pinned
   the facts listing's `used` column at `no`; stage 2's every-artifact
   `VM_START_SCAN` stamp asks the fact on every compile, so it reads `yes`.
   Re-aimed to any value of the column, intent unchanged, with a comment.
5. **S481/S482 were re-aimed** from the unbounded forms (no population,
   §6.4.4) to the bounded forms' re-seed (whole / hit path), so each
   (form x landing) cell has a row with S483/S484.
6. **The manifest regeneration moved one stage-2 id**:
   `tests/ucp/ctxnode.rxt:400`'s (text, options) twin in `dfahat.rxt` now
   sorts first in the census dedup and takes its id; the row is the same
   block (§3.1).
7. **S488 is answer-equivalent** (a nullable `S` on a seeded machine scans
   for a byte the empty match never needs, and the start state accepts
   there), so it is detected structurally only (`[dfa-movers]`,
   `[dfa-table]`), as its row header argues.
8. **The hat moves two other rows' verdicts on its movers** (§3.2): G1
   (28: a one-byte `T` IS the pre-check's byte, so the pre-check is
   `dominated` and elided) and the hybrid re-seed density (7: the mass over
   `T` falls below the dense row). Both are the intended reading of `T`
   through `pf_scan_set_of`, not side effects; F3 (`alpha_s3.sh`) carries
   cells for both.
9. **The mech rows were scored at `8c69a359`**, before the spec, check,
   `hybrid.rxt` and abi commits. None of those moves a plant's anchor
   (`scripts/m6read_check_sab_anchors.py`, §4); the verdicts are not re-run.

## 7. OWED (exact commands)

1. **The Linux alpha (F3 at the dense movers)** — the manager's, per the
   brief: `bash docs/dev/optloop/startset/alpha_s3.sh` on ubuntubudu (quiet
   box, `gnutimeout` per BOILERPLATE). Its cells: the dense movers (the
   `\b(?:true|false|null)\b` family, aws, the six count-collapsed hybrids),
   the G1 `dominated` movers, the re-seed-row movers, the null cells (a
   one-byte narrowing such as float-literal 11 -> 10, where the unmeasured
   proper-subset admission must not lose) and the deny/base noise floor.
   Written and syntax-checked here, never run.
2. **The full `make test-axes`** (all 42 bit axes + the product arm over the
   whole corpus). This lane ran `AXES=-fno-start-set SKIP_ORACLE=1` over the
   18 mover files only (§4); the product arm's 11,000-case floor is a
   whole-corpus number and reads 4,635 on that subset, which is the subset,
   not the hat.
3. **Bench questions** (for relay; no bench run was made): (a) the aws
   witness `\b((?:A3T[A-Z0-9]|AKIA|AGPA)[A-Z0-9]{16})\b` becomes
   `first-memchr-bounded` on 'A' — which subject does the bench time it on,
   and how dense is 'A' there; (b) do the CTX short-call subjects contain the
   context bytes (`E \ S`) the re-seed restores, i.e. will the bench see the
   re-seed's per-hit cost at all.
4. Nothing outside the worktree to clean: the KEEP=1 mech chains ran with
   `TMPDIR` in the session scratchpad, so their harness temp dirs were
   there (the `/var/folders/.../T/pcrec-mech-sabotage.*` dirs on the box
   date from 09-30 and 10-05 15:42, before this lane's runs) and were
   removed with the scratch trees.

## 8. Questions

- **Q1 (ABI ORDER).** This lane took 64 with R4a′ (63) not yet landed.
  If R4a′ lands after this lane, its own bump is 62 -> 63 on a tree that
  reads 64: the R4a′ lane should re-base onto 64 and take 65, or keep 63 as
  a historical slot with no artifact? The ledger entry this lane wrote
  assumes R4a′ keeps 63 and lands FIRST; recommendation: land R4a′ first
  and re-run this lane's codegen pin, which only reads the number.
- **Q2 (S505+).** Not taken, per the brief, and none was needed: every
  §6.4.2 mutant has a detecting row or check here (§4.1). `startset.md`
  names no id above S504.
- **Q3 (G1 elision on a one-byte `T`).** 28 movers lose their `memchr`
  pre-check as `dominated` because the hat now scans that same byte. This is
  the general reading (`pf_scan_set_of` is the one place the scanned set is
  asked), and answer-identical (0 defects on the differential, which covers
  these movers). Recommendation: accept; F3's G1 cells measure the cost
  side.
- **Q4 (the unmeasured admission).** `T ⊊ E` with no margin admits a
  one-byte narrowing. D149 labels it an unmeasured default; the null cells
  in `alpha_s3.sh` are the measurement. No change proposed until that runs.

## 9. State at hand-off

- Branch `lane/ssbuild3`, worktree `worktrees/ssbuild3`, clean, NOT
  merged. Commits after the mech pin `8c69a359`: `da0cb761` (spec, registry,
  checks, docs), `eb4f07ba` (main merged alone), `b42dffa6` (abi 64 + its
  readers, the lane's last `src/` commit), the FILEPIN self-pin, `820b9845`
  (the readers the hat moved), and the report commits.
- The suite lock is released. No process of this lane is running.
- Scratch logs (session scratchpad,
  `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/ssbuild3/scratchpad/`):
  `fulltest.log`, `startset.log`, `sandiff.log`, `codegen.log`, `axes.log`,
  `rxtsource.log`, `sweep.log`, `mover_table.log` + `movers.tsv` (the 88
  hat rows), `mech/S4*.log`/`S50*.log` (the solo rows). The mech scratch
  trees and the mutant trees have been removed.

## Panel fixes (ssfix3)

Lane `ssfix3`, 2026-10-06, opus, in this worktree on `lane/ssbuild3` (from
`61c5a6f0`). Charter: the D6 panel's dispositions,
`docs/dev/reviews/2026-10-06-r-ss3-panel.md`. **R4a′ (abi 63) is NOT on main
at this lane's finish** (main `8f91cba1` reads 62), so main was not merged and
the branch stays drafted 62 -> 64.

### F.1 The disposition table, resolved

| id | resolution | evidence |
|---|---|---|
| **sound F1 (BLOCKER)** | **`T = S`**, the intersection dropped (`4fdfbff3`). `dfa_estar` is deleted. The `T == S` assertion is replaced by a guard that cannot fire on a correct start set: `dfa_reseed_exact` reads the re-seed's premise off the machine (every byte outside `T` takes `s0` and every live seed to the seed of its own class). A witness's start byte that leaves every seed in place is outside `E`, so the existing `T ⊊ E` admission declines, and the artifact is the deny arm's. Fixture `tests/startset/dfahat_f1.rxt` holds the critic's six witnesses plus six fuzz finds: 12 blocks, 322 cases, libpcre2 at every startpos; the 11 byte-tier blocks are also python-verified (298 cells); the `flags u` block is libpcre2-only. The compile-only arm is `tests/startset/compile_fuzz.py`. | All six witnesses compile to `byte-class-bounded` (`RX_ENGINE "dfa"`, and `"vm"` + hybrid for `(?<=\w) *(a)`). `dfahat_f1.rxt` passes 322/0 on the fix and fails 0/322 on the pre-fix compiler. `emit_sweep.py --ref 61c5a6f0` (the pre-fix head) shows **0 movers, 0 asymmetric on all five streams at full reach** (4,147/4,148/4,148/38 files/7 dumps), so the fix moves no emitted byte on any artifact that compiled. `compile_fuzz.py` reads 0 over 9,000 at the committed seed and 0 over 3 × 20,000 more seeds. `dfa_reseed_exact` never fired over those 69,000 patterns or the corpus. |
| sound F2 (NOTE) | Report citation corrected in place (§4.1 table, §6 item 1). Cheap sentinel: `dfahat_checks.py` `[dfa-bot]` holds six start-of-subject/`\G` spellings (`^a\|\bb`, `\Ab\|\bc`, `\Ga\|\bb`, `(?m)^a\|\bb`, `(?:^\|-)\b(?:a\|b)`, `(?:\A\|\bq)(?:a\|b)`) to `RX_DFA_SCAN "attempt"`. | 6/6 PASS |
| sound F3 (NOTE) | Recorded; no change. The `views` assertion stays and is unreachable by construction. | — |
| **checks M1** | The arm is SPLIT. `run_dfahat_checks.sh` gains `DFAHAT_PART=answers\|struct\|all`. Mech arm `dfahat` is now answers only (the fixtures, the collapsed fixture pass, the differential). New arm `dfahatstruct` is `dfahat_checks.py` + `compile_fuzz.py`. S480-S485/S504 stay on `dfahat`, so the re-seed text pin can no longer detect them; S486/S488/S495 move to `dfahatstruct`. | the mech solos below |
| **checks M2** | S487/S489/S490 are re-typed as DECLARED EQUIVALENT MUTANTS (`SAB_EXPECT=UNDETECTED`, `dfahatstruct`, S219's shape). Planted, their artifacts must be the clean compiler's: `[dfa-deny]` + `[dfa-movers]` over the corpus is the byte-identity observable. Each REACH probe is a clean-tree population that does not pass through its own conjunct: an unseeded skip (`a+\|b+`); a seeded skip with a 256-member `--emit-facts` start set (`\b(?:\w\|[^\w]x)`); and a seeded attempt-scan artifact plus an unanchored hat mover (`(?m)^(?:ab\|\bcd)`, `\b(?:true\|false)\b`). | probes REACH on the clean tree; verdicts in the mech table |
| **checks M3** | `run_axes.sh` gains a DFA-HAT ARM after the product arm. It counts the default baseline's cases whose block is in `manifest_s3_dfa.tsv` (`startset_arm.py` with that manifest), floor `DH_MOVER_FLOOR` 689 (half of 1,378). The GROUP F5 comment and `tests/axes/CLAUDE.md` are updated. | `AXES=-fno-start-set SKIP_ORACLE=1 SS_MOVER_FLOOR=0` over the 18 mover files + `dfahat_f1.rxt`: `-fno-start-set`, `--engine=vm` and their product each 6,219/6,219 agree, 0 mismatches/give-ups/refusals. **DFA hat 1,378 mover cases, 71 of 71 blocks = the static count of their case lines exactly.** The product arm reads 4,949 (its 11,000 floor is whole-corpus; disabled for this subset run) |
| **checks M4** | `run_dfahat_checks.sh` runs the five fixture files a second time under `RXTFLAGS=-fprefilter-collapse` (`[dfa-fix-collapse]`, floor 1,045). This restores the oracle check at the collapsed config. `vmhat_diff.py` compiles first, dedupes any pair byte-identical to its mover's `auto` pair (run once, counted once), counts the distinct `count-collapsed` pairs and floors them (`FLOOR_COLLAPSED` 2). | fixture pass 2,091/0 under collapse (and plain). 66 of the 71 `collapse` pairs were `auto` duplicates; **5 distinct count-collapsed pairs** |
| **checks M5** | The sweep alphabet now keeps the outside byte and the pattern's literal bytes (alphanumerics first) up to five, and ADDS the context bytes beyond the five rather than displacing them. Pairs with at least one match are floored (`FLOOR_MATCHING` 75 DFA / 191 VM). | DFA: 153 distinct pairs, **1,920,044 cells** (was 1,155,139), 228,306 matches, 151 pairs matching (the 2 that do not are `\b(?<=bc)d`, which can never match), 0 defects. VM: 423 distinct pairs, 2,486,254 cells, 382 matching, 0 defects |
| **checks M6** | The START-SET mech solos re-run at the fixed tip, all 26 rows S478-S502 + S504. | table F.3 |
| m1 | A hat refusal or timeout where the deny arm compiles is a FAIL in both scripts: `dfahat_checks.py` `[dfa-refuse]`, and `vmhat_diff.py` (`hat-refused`, no longer counted as `refused`). This is the check that would have caught F1. | On the pre-fix compiler `[dfa-refuse]` reads **12 violations** (the 12 `dfahat_f1.rxt` blocks); on the fix, 3,540 pairs and 0 |
| m2 | The class re-compare asserts the re-compiled default still stamps a DFA-hat value (`classx_hat`). | `[dfa-deny]` green with the assert |
| m3 | The `[dfa-table]` docstring now says it checks EMISSION (`S` is the predicate's input), not an independent derivation. | — |
| m4 | Not changed. `machine_sets`' `cbm_agrees` still reads vacuously on movers, which stays harmless while X comes from the transition tables. A future reader of `can_begin_match` must know that movers emit `start_bytes`. | — |
| m5 | `census_s1.py` compiles every arm with `-fno-start-set` and reads F as `T = S`, so it runs on the CURRENT build. | Regenerated on this build: `s3_dfa` and `s2_vm_auto` **byte-identical**; `s2_vm_forced` **+12**, every one a `dfahat_f1.rxt` block. Summary `docs/design/startset/s3/census_ssfix3_summary.txt`; its `F-checked: \|E*\| < 256` row reads 12, the BLOCKER witnesses |
| m6 | See QUESTIONS (abi merge order). | — |
| m7 | `match_api.md` §6 and `tuning.md` §2.42 now say "restores the `abi`-62 `-fno-start-set` program (no VM hat either)". §2.42's applicability no longer claims `E*` is all 256; it states `T = S` and the decline. | — |
| m8 | For the landing inbox note (not written to pcrec-bench). The bench adapter's closed `dfa_prefilter` enum (`testees/pcrec/adapter.py:714-716`) lacks stage 2's `first-class` and stage 3's `first-memchr-bounded`/`first-class-bounded`, and 18 bench movers stamp them. `--list-axes`'s `prefilter` rows re-order (`memchr-bounded` 6 -> 8, ...). | — |
| notes n1-n5 | Recorded; no change. | — |

### F.2 The compile-only arm's failing-direction proof

`tests/startset/compile_fuzz.py` (9,000 patterns, `SEED=20261006`, 30% from
an F1-shaped template, flags drawn from none/`-i`/`--no-captures`/
`-fprefilter-collapse`/`-e utf8`/`--ucp`; 25 s on the Mac):

| compiler | population | deny-compiles | DFA-hat reach | deny compiles, default refuses |
|---|---|---|---|---|
| pre-fix (`61c5a6f0`) | committed (`TEMPLATE=0.3`) | 8,930 | 680 | **70** (all "the DFA hat's T = S & E* dropped N start-set byte(s)"; includes `\b\d*b+` and `\b[ab]*(?:ab\|b)+`, which are `\b` shapes, not only lookbehinds) |
| pre-fix | `TEMPLATE=0` (the critic's grammar) | 8,996 | 427 | **4**, the critic's rate (4 in 9,000) |
| fixed (`4fdfbff3`) | committed | 9,000 | 680 | **0** |
| fixed | seeds 1/2/3, N=20,000 each | 20,000 ×3 | 1,459 / 1,516 / 1,474 | **0** |

Floors (half the landing): `FLOOR_OK` 4,500 deny-compiling, `FLOOR_HAT` 340.

### F.3 Mech solos at the fixed tip (M6)

PENDING at the time of writing (`chain.sh` below). Filled in from the logs
when the chain completes.

### F.4 The full Mac `make -k -j4 test CC=gcc-16`

PENDING (same chain, after the mech; suite lock `worktrees/.mac-suite.lock`,
owner `ssfix3`).

### F.5 `scripts/emit_sweep.py` against main, and the mover table

PENDING (same chain, last): main `8f91cba1` built from `git archive`,
`--ref-bin`, then ssbuild3's `mover_table.py` (abi / stamp / hat / FINDING).

### F.6 Commits

`4fdfbff3` (the fix + `compile_fuzz.py`), `5736b577` (checks M1-M5, m1-m5,
m7, sound-F2, fixtures, manifests, spec), `7e99faa2` (rxtsource census
+1/+12/+322 for `dfahat_f1.rxt`: 272 files / 4,606 blocks / 41,327 lines; C3
PASS +298, SKIP and pcre2-only +24, verifiable +298), the mech and
src/gen/startset CLAUDE.md notes, and the `startset.md` §4.1a amendment.
`make strict` is clean. `make test-rxtsource` reads 278/0/1, where the 1 is
the darwin python-3.9 C3 RECORD. `DFAHAT_PART=struct` reads 32/0.

### F.7 QUESTIONS for Frank

- **Q-F1 (the addendum-1 retraction, D148).** Proposed text, to append to
  D148 addendum 1 (or as addendum 3):
  > **Retracted 2026-10-06 (the ss3 D6 panel's BLOCKER sound-F1, lane
  > ssfix3).** "`E*` is all 256 bytes on every seeded machine, so
  > `S ∩ E*` ≡ `S`" is false. It was a population measurement (94 rows,
  > 13.58M cells) whose population held no machine where a byte of `S`
  > leaves every seed state where it is, and `(?<=\w) *a` is one: the space
  > keeps the non-word seed and keeps the word-context thread in ` *`. As
  > built, the intersection dropped that start byte and the `T == S` build
  > assertion refused valid patterns at default flags; admitted silently, it
  > would have lost `(1,3)` on `"x a"`. The DFA hat's set is **`T = S`**,
  > repair (b) of §4.1a, admitted iff `T ⊊ E`. A start byte outside `E`
  > declines the row, so the artifact is the plain row's. `E*` has no role
  > in the predicate. The build guard is the re-seed's premise read off the
  > machine (`dfa_reseed_exact`).
- **Q3 (G1 elision on a one-byte `T`)** — unchanged, still open: 28 movers
  lose their `memchr` pre-check as `dominated`. Recommendation unchanged:
  accept, and F3's G1 cells measure the cost.
- **Q4 (the unmeasured `T ⊊ E` admission)** — unchanged, still open. With
  `T = S`, the F1 shapes now DECLINE through this admission. The null cells
  in `alpha_s3.sh` remain the measurement.
- **Q1 (abi order), checks-m6's completion.** R4a′ (abi 63) touches the
  same `#define`, `ABI_EXPECT`, the K80 example, match_api §6, `FILEPIN`,
  and the cpset/resource byte pins. Both branches regenerate
  `docs/dev/artifact_size_log.tsv` in full, and that file must be
  regenerated after the merge, not hand-resolved. If this branch lands
  second, `FILEPIN` re-pins and the byte pins are re-measured, not just the
  number re-read. No check enforces abi MONOTONICITY (`ABI_EXPECT` is an
  equality), so a "take theirs" on R4a′'s `62 -> 63` after this lands would
  go silent. Recommendation unchanged: land R4a′ first.
