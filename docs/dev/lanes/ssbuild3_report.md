# ssbuild3 — START-SET stage 3, THE DFA HAT (lane report)

Lane `ssbuild3`, 2026-10-06, opus. Branch `lane/ssbuild3` off main
`57db5152` (stage 2 landed, abi 62). Builds `docs/design/startset.md` §8's
stage-3 row (rev 2 + ssedge's §6.4) under D148 + addenda 1-2. **AN ABI
EVENT: this lane's number is 64** (63 is reserved for the memfn kit's R4a′;
see §1 for how the bump was drafted). A fresh agent resumes from §8.

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

PLACEHOLDER-GATES

### 4.1 The §6.4 mutation table, on this build

| mutant (§6.4.2) | how it is seen here | evidence |
|---|---|---|
| correct DFA hat (control) | — | differential 0 defects; fixtures 1,769 / 0 |
| `T = S ∩ E` (r3, sound-F1) | S480 | 23 failing fixture cells (the six `W` witnesses) plus three structural arms |
| E* missing one seed state | the `T == S` BUILD ASSERTION | a scratch mutant (`dfa_estar` skips the last seed) REFUSES 16 corpus blocks — the six sound-F1 witnesses and their fixture copies — with the assertion's internal error; the other 3,512 artifacts are byte-identical (an equivalent mutant on every mover, §6.4.3 item 6) |
| E* missing s0 | equivalent on this build | the same scratch run: 3,528 of 3,528 byte-identical. ssedge's twin saw it (7 of 10) because it read the seed family off the emitted table; in pcrec `s0` IS `s1u[UPC_PLAIN]` on every ENG_UNANCH machine (`start_pinned_assert_routing` asserts it), so `E*`'s union already holds `s0`'s escapes |
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
   table. In the compiler `s0` IS `s1u[UPC_PLAIN]` on every `ENG_UNANCH`
   machine (`start_pinned_assert_routing` asserts it), so the union over the
   live seeds already holds `s0`'s escapes: 3,528 of 3,528 artifacts
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

PLACEHOLDER-OWED

## 8. Questions

PLACEHOLDER-QUESTIONS
