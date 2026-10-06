# memfnbump — [MEMFN] R4a′ re-pins on the merged tree + the abi bump 62 -> 63

Lane `memfnbump` (kit session, opus), 2026-10-06. Branch `lane/memfnbump`,
from `lane/memfn-r4a2` `f09b4a32` (the kit branch's merge of main
`57db5152`, START-SET stage 2, abi 62). Procedure:
`memfnstamp_report.md` §8. Delivered to the kit session for merge into
`lane/memfn-r4a2`; never to main.

**Status: both commits built and Mac-validated (directional).** The verdict is
the Linux `make test` (§6), run by the pcrec manager's executor.

| commit | what |
|---|---|
| `5d984c1d` | commit 1: re-pins for R4a′'s two lines on the merged tree (no abi change) + the census's named-mover rule |
| `b2e75d05` | commit 2: the abi bump 62 -> 63 and every reader found by grep |
| `a0670cba` | the recursion-identity FILEPIN self-pinned to `b2e75d05` (see §3.3 for why this is a separate commit) |
| (this commit) | this report + its `docs/dev/lanes/CLAUDE.md` index row |

## 1. Commit 1: the re-pins, measured on this tree

Every number was MEASURED from this tree's build. Each was then checked
against main `57db5152`'s compiler (the census's reference build,
`build-emitsweep/src_ref/build/pcrec`) by a whole-text diff. No delta was
added by hand.

| pin | file | main (abi 62) | merged tree | delta | how verified |
|---|---|---|---|---|---|
| `EMITTED_BYTES` x12 | `tests/codegen/manifests/m5_stage1_stamps.tsv` (read by `run_cpset_structure.sh`) | `a` 23467, `abc` 24272, `a(b\|c)+d` 32228, `(a)(b)(c)` 31888, `[a-z]+@[a-z]+` 27399, `^foo$` 18724, `\bword\b` 28396, `(?i)HeLLo` 31332, `cat\|dog\|cow\|calf\|camel` 28270, `(\w+)\s+\1` 29025, `(?<=foo)bar` 32609, `(a(?1)?b)` 32465 | each + delta | +61 x8 (LIBC `"memchr"`), +59 x3 (`^foo$`, `cat\|…`, `(\w+)\s+\1`: `"none"`), +68 x1 (`\bword\b`: `"memchr,memcmp"`) | the check's own sample loop on both compilers; the `-o -` diff of all 12 is exactly two `>` lines (`RX_MEMFN_FORMS`, `RX_MEMFN_LIBC`) each |
| `a{5,25000} -fno-scan-edge -fno-start-pinned` | `tests/resource/run_resource_tests.sh` | 762636 | 762697 | +61 (+30 FORMS, +31 LIBC `"memchr"`) | same `-o` basename `o.c`; `diff` = `9566a9567,9568`, the two lines only |
| (B) FILEPIN | `tests/codegen/run_recursion_identity.sh` | `b0eff398` (main's) | `f09b4a32` | — | the merge commit is the combined tree's last `src/`/`memfn/` commit (`git diff f09b4a32 -- src lib cli memfn` empty at commit 1; the K78 merge-pin precedent) |
| cap-rescue code cap | `tests/codegen/run_size_term.sh` | 31,900 | **32,300** | — | **found red by test-codegen, not in the brief's list.** See below |

**The size-term red.** test-codegen at commit 1 (before this re-pin) had a
second red besides the darwin `nm` one: `the rescue took K=2; ... rung 4 does
(31,555 B ...)`. The cell builds a reference compiler with
`-DPCREC_MAX_VM_EMIT_CODE_BYTES=31900` and expects the `(?:aa|a){8,12}+b`
rescue to take the largest fitting K, 4.
- The every-artifact stamps since its last calibration (RUN_WORDS,
  REQ_HANDOFF, VM_START_SCAN) had used up the cap's headroom. On main, K=4
  measured 31,846, which left 54 B. The two new lines (+61 B of code) put K=4
  at 31,907, 7 B over the cap.
- MEASURED by bisecting the cap on reference builds of this tree:
  - caps 31,901-31,906 take K=2;
  - caps 31,907-31,910, 31,930, 31,960 and 32,300 take K=4.
- The other rungs come from `--unroll=K --warn-emit-bytes=1`'s "N of code" on
  the default build, corrected by the same +5 B:
  - this tree: K=6 ~36,988, K=3 ~32,792, K=2 ~30,677;
  - main: K=4 31,841 + 5.
- New cap 32,300. Rungs 6 and 3 do not fit; 4 fits and is the largest that
  does; 2 fits too. That leaves about 390 B of headroom and about 490 B under
  K=3.
- The comment in the script records all of the above.
- Erratum: commit `5d984c1d`'s message says "2 B over". The measured figure is 7 B over (31,907 against 31,900). The `tests/codegen/CLAUDE.md` entry is corrected in the report commit.
- Standalone, `bash tests/codegen/run_size_term.sh` gave 32 passed, 0 failed.
  Post-bump, the file is also green inside `make test-codegen`, which chains
  it (§5).

**Re-pin comments.** Each comment names both events: stage 2's
`VM_START_SCAN` line, which the merged values already include, and R4a′'s two
lines on top of it. Each also says how it was measured and verified.

**Not re-pinned, with reason (unchanged from memfnstamp §7):**
`docs/dev/artifact_size_log.tsv` is rewritten by `make test`'s own size-log
section. The Linux run produces the new file, and the manager commits it.

**The census's named mover (commit 1).** Before this commit,
`tests/memfn/stamp_mover_census.py` accepted the `stamps+size` class on ANY
artifact. Now it accepts that class only for an artifact named in
`SIZE_MOVERS`, which records the artifact's cause:
- the one entry is `comp-c tests/uprops/size_ladder_prefilter_drop.rxt:rx.c`;
- its cause: `RX_VM_PREFILTER_WHY` quotes the discarded hybrid attempt's
  measured size, and that attempt now carries its own two lines (+59);
- a size-quote mover anywhere else is `OTHER`;
- a named mover that is not seen exactly once fails the run, so a stale name
  cannot pass silently;
- the run prints the named mover with its cause.

## 2. The mover census at both steps

`python3 tests/memfn/stamp_mover_census.py --ref 57db5152 [--abi 62:63]`.
Working side: this tree's `build/pcrec`. Population: 4,532 pattern rows and
364 composition files.

**Step 1 (commit 1, pre-bump), 106 s, CLEAN, exit 0:**

| stream | identical | abi | stamps | stamps+abi | stamps+size | OTHER | ASYMMETRIC | both-refuse |
|---|---|---|---|---|---|---|---|---|
| c-default | 0 | 0 | 4085 | 0 | 0 | 0 | 0 | 447 |
| c-vm | 0 | 0 | 4086 | 0 | 0 | 0 | 0 | 446 |
| comp-c | 0 | 0 | 53 | 0 | 1 | 0 | 0 | 0 |
| comp-h | 54 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| emit-ir-vm | 4086 | 0 | 0 | 0 | 0 | 0 | 0 | 446 |

**Step 2 (after the bump, `--abi 62:63`), 99 s, CLEAN, exit 0:**

| stream | identical | abi | stamps | stamps+abi | stamps+size | OTHER | ASYMMETRIC | both-refuse |
|---|---|---|---|---|---|---|---|---|
| c-default | 0 | 0 | 0 | 4085 | 0 | 0 | 0 | 447 |
| c-vm | 0 | 0 | 0 | 4086 | 0 | 0 | 0 | 446 |
| comp-c | 0 | 0 | 0 | 53 | 1 | 0 | 0 | 0 |
| comp-h | 0 | 54 | 0 | 0 | 0 | 0 | 0 | 0 |
| emit-ir-vm | 4086 | 0 | 0 | 0 | 0 | 0 | 0 | 446 |

Both runs printed the same named-mover line:
`named mover: comp-c tests/uprops/size_ladder_prefilter_drop.rxt:rx.c
(stamps+size): RX_VM_PREFILTER_WHY quotes the DISCARDED hybrid attempt's
measured size, ...`.

What the two tables show:
- Every `.c` artifact moved by exactly the two lines, plus the abi digit at
  step 2.
- The one named value moved, as accepted.
- The composition headers moved only by the digit.
- The IR listings did not move.
- No other mover appeared, so there is no finding.

## 3. Commit 2: every abi reader, found by grep

### 3.1 The greps (run at the bump base `5d984c1d`, N = 62)

| # | command | hits |
|---|---|---|
| g1 | `git grep -nE 'PCREC_ARTIFACT_ABI [0-9]\|ABI_EXPECT=\|\(abi 62\)\|abi 62\b\|PCREC_RX_ABI_H[^0-9]*62\b\|\.abi = 62\|ABI_SUBJ\|FILEPIN=' -- src cli lib tests docs/spec Makefile memfn` | 12 |
| g2 | ``git grep -nE '`abi` 62\b\|is `62`' -- docs/spec`` | 1 |
| g3 | `git grep -nE 'EMITTED_BYTES\|762697' -- tests docs/spec lib src Makefile` | 40 (byte pins; the digit keeps its width, so none moved; verified by test-cpset-structure and test-resource green post-bump) |
| g4 | `git grep -nlE 'emit_sweep\|norm\(' -- tests docs/dev/optloop` | 28 files. Each `tests/` file was read: all normalise the digit by regex (`[0-9]+`); none carries a literal 62. `docs/dev/optloop/startset/alpha_s2.sh` hard-codes `(61\|62)`, but it is stage 2's own alpha script, not run by make, and it stays as written |
| g5 (extension) | `git grep -nwE '62' -- src cli lib tests docs/spec Makefile memfn scripts examples analyze \| grep -iE abi` | 29 |
| g6 (extension, whole tree) | `git grep -nwiE 'abi' -- . ':!docs/dev/artifact_size_log.tsv' ':!docs/dev/dev_journal.md' ':!docs/dev/lanes' ':!docs/design' \| grep -wE '62'` | 54 |

Every g5/g6 hit was read. Those not in the table below are PROVENANCE, and
provenance does not move:
- "added at `abi` 62", "abi 61 -> 62" event headings in `src/gen/CLAUDE.md`,
  `tests/codegen/CLAUDE.md`, `tests/startset/CLAUDE.md`,
  `tuning.md` §2.42/§3504/§3994, `match_api.md` :595 and §6.3's START-SET
  heading;
- stage 2's own re-pin comments;
- plan/optloop/review documents;
- the kit's own `memfn/docs/wake.md`/`journal.md`, which belong to the kit
  session;
- unrelated 62s (a count of 62 producers, a `.rxt` line number 62, the
  62,872-cell population, `alnum 62`).

### 3.2 Readers changed

| reader | site | change |
|---|---|---|
| the constant | `src/gen/emit_dfa.c:53` | `PCREC_ARTIFACT_ABI 62` -> `63`. It moves the generated-by line `(abi N)`, `.abi = N`, and the K80 guard's `!= N` / `(abi N)` / `#define PCREC_RX_ABI_H N` (verified on `-o -` of `a`) |
| ABI_EXPECT | `tests/codegen/run_codegen_tests.sh:3021` | `62` -> `63`; the cause list gains the 62->63 entry, copied from §6 |
| K80 example | `docs/spec/match_api.md` §6 (three lines: `!= 63`, `(abi 63)`, `PCREC_RX_ABI_H 63`) | digit |
| the abi change log | `docs/spec/match_api.md` §6 | NEW entry "`rx_info.abi` is `63` ... (lane memfnbump bumped it from 62, 2026-10-06: [MEMFN] R4a′ — THE KIT'S TWO STAMPS ...)"; the 62 entry now reads "was `62`" (D80) |
| §6.3 heading | `docs/spec/match_api.md` | "[MEMFN] R4a′, `abi` 63, 2026-10-05 (the stamps' own `abi` event)" |
| (B) FILEPIN | `tests/codegen/run_recursion_identity.sh:1169` | `f09b4a32` -> `b2e75d05` (commit `a0670cba`) |
| the ABI_SUBJ/ABI_PIN tripwire | same file :1267-1276 | no edit; it reads both compilers' `.abi =` and passes because FILEPIN moved |
| CLAUDE.md | `src/gen/CLAUDE.md` (memfn_stamps.c entry), `tests/codegen/CLAUDE.md` (an R4a′ re-pin entry beside stage 2's) | provenance lines |

**Did NOT move with the digit (verified, not assumed):** the 12
`EMITTED_BYTES`, the resource pin and the size-term rungs. The digit keeps its
width, and test-cpset-structure, test-resource and test-codegen are all green
after the bump.

`docs/spec/CLAUDE.md` did not get an entry. It keeps entries only for selected
bumps; stage 2 has none there either, and §6 is "the only" change log.

### 3.3 Why the FILEPIN is its own commit

The self-pin convention points FILEPIN at the lane's last `src/` commit. A
commit cannot name itself, so the bump `b2e75d05` carries all of `src/` + spec
+ tests, and `a0670cba` (tests only) moves FILEPIN to it. This is memfnstamp
§8 step 3. Nothing after `a0670cba` touches `src/`, `lib/`, `cli/` or
`memfn/`, so (B) compares this tree's emitted text against an identical
compiler.

## 4. Mech solos S513-S517 (after the bump)

See §7, the validation log (filled from `build/scratch/mech.S51N.log`).

## 5. Suite results (Mac, gcc-16, directional)

Logs: `build/scratch/` in the worktree (gitignored). `c1.*` = commit 1,
`c2.*` = after the bump (tip `a0670cba`). Verdicts read from make's
`*** [test-X] Error` lines.

| run | commit 1 | after the bump |
|---|---|---|
| `make`, `make strict` | clean / "whole tree compiles clean with -Werror -Wshadow" | clean / same |
| test-codegen | red at 191 s: the darwin `nm could not read arm_a.o` AND the size-term K=2 red, which led to the re-pin in §1 (then `run_size_term.sh` standalone 32/0) | 226 s; ONE `*** [test-codegen] Error 1`, ONE `FAIL:`, the accepted darwin `nm could not read arm_a.o`; 701 PASS |
| test-registry | rc 0, 137 s | rc 0, 197 s |
| test-rxtsource | rc 0, 75 s | rc 0, 91 s |
| test-cli | rc 0, 20 s | rc 0, 28 s |
| test-resource | rc 0, 166 s | rc 0, 183 s |
| test-cpset-structure | rc 0, 26 s | rc 0, 27 s |
| test-memfn-link | rc 0 | rc 0 |
| test-memfn-manifest | rc 0 (22/0) | rc 0 (22/0; rule 2's dynamic half UNREACHED, as before) |
| test-memfn-g2 | rc 0, 51 s | rc 0, 65 s |
| test-memfn-stamps (C11) | rc 0, 30 s | rc 0, 37 s: 929 artifacts (dfa 353, vm 576), LIBC none 346, idiom 95, memchr 538, memcmp 50, strlen 49, printf 44, fprintf 96; 12/0 |
| census | CLEAN (§2) | CLEAN (§2) |
| test-recursion-identity | not run at commit 1. Its FILEPIN there is the merge, whose `src/` equals the tree's, so (B) is identical by construction | §7 |

## 6. The Linux run (the verdict): the command block for the pcrec manager

Run at the tip of the branch that carries this lane: `lane/memfnbump` at the
tip in the handback, or `lane/memfn-r4a2` after the kit session merges it.
The Mac pushes the tip to the box's repo first, because the box has no route
to the Mac:

```
# ON THE MAC (the manager). The ubuntubudu remote is ssh://duxevents@100.69.121.107/home/duxevents/pcrec
git -C /Users/fdicostanzo/pcrec push ubuntubudu lane/memfnbump:refs/heads/lane/memfnbump
# ON ubuntubudu (pcrecdev2's executor channel)
df -h / | tail -1                     # free space (ubuntubudu disk-space memory)
uptime                                # load1 < 0.5 before launching; otherwise wait
git -C /home/duxevents/pcrec worktree add --detach /home/duxevents/pcrec/worktrees/memfnbump-linux lane/memfnbump
git -C /home/duxevents/pcrec/worktrees/memfnbump-linux rev-parse HEAD      # expect the handback tip; otherwise STOP
cd /home/duxevents/pcrec/worktrees/memfnbump-linux && gnutimeout 1800 make -j8 2>&1 | tail -3
cd /home/duxevents/pcrec/worktrees/memfnbump-linux && nohup gnutimeout 10800 make test > /home/duxevents/pcrec/worktrees/memfnbump-linux/memfnbump_make_test.log 2>&1 &
```

**Completion.** The log ends with the trailer block
`== make test: completion trailer ==`, then `sections ran: N/N`, then
`RUN-STAMP: tree=<tip> (clean) sections=N/N duration=<s>s`.

**Judging the verdict:**
- `grep -n '\*\*\* \[test-' memfnbump_make_test.log` must print NOTHING;
- `make: *** [test] Error` must be absent.
- Never judge by "sections ran", and never by a grep for `FAIL:` (learnings
  §3, 2026-09-22).
- PC-3 against 10.46 is live on that box. A red there is real.

**Expected wall time.** On the Mac `make test` measures ~100-105 min. On CI
it takes ~37-39 min, and the box is about 1.3x faster than the Mac on full
batteries (docs/testing.md, 2026-09-26). Expect roughly 45-75 min on
ubuntubudu. The 3 h `gnutimeout` is the generous ceiling; if it fires, that
is a finding.

**After the run:**
- commit the `docs/dev/artifact_size_log.tsv` it rewrites (§1);
- re-run the census on Linux too. It is cheap: about 100 s on the Mac, one
  reference build plus about 9k compiles at 8 jobs, writing only under the
  gitignored `build-emitsweep/`. It needs `57db5152` in the box's repo
  (`git -C /home/duxevents/pcrec fetch origin` if not). Expect the §2 step-2
  table, `census: CLEAN`, exit 0:

```
cd /home/duxevents/pcrec/worktrees/memfnbump-linux && gnutimeout 1800 python3 tests/memfn/stamp_mover_census.py --ref 57db5152 --abi 62:63 2>&1 | tail -12
```

**Clean-up afterwards:** `git -C /home/duxevents/pcrec worktree remove
/home/duxevents/pcrec/worktrees/memfnbump-linux`.

## 7. Validation log: the owed tail of the chain

The post-bump chain ran detached (`build/scratch/chain2.sh`, summary
`build/scratch/c2.summary`) in this order: the census, the suites above, the
mech solos `bash tests/mech/run_sabotage_matrix.sh S51N` (logs
`build/scratch/mech.S51N.log`), then `make test-recursion-identity` (log
`build/scratch/c2.test-recursion-identity.log`). The completion line in the
summary is `CHAIN-DONE`.

RESULTS: see the handback message (filled in below when the chain finished).

## 8. Charter vs committed

| brief item | status |
|---|---|
| worktree off lane/memfn-r4a2, first command the toplevel | DONE |
| commit 1: re-pin, measured on this tree, for the four named pins | DONE: m5_stage1_stamps.tsv x12, resource 762697, FILEPIN f09b4a32 (the brief's four sites = three files plus the cpset runner's comment) |
| commit 1: anything else red in the listed suites | DONE: `run_size_term.sh` cap-rescue 31,900 -> 32,300 (bisected; §1). Nothing else red |
| re-pin comments name both events + verification | DONE |
| census vs main 57db5152, the named mover classified with its cause | DONE: CLEAN; the classifier now names exactly that artifact (SIZE_MOVERS) and fails on a stale name |
| commit 2: the abi bump 62 -> 63, readers by grep (incl. extensions) | DONE: §3, six greps with counts |
| spec change log (D80) | DONE: §6 entry for 63, §6.3 heading, K80 example |
| make test-codegen + registry/codegen/rxtsource after the bump | DONE: §5 |
| census `--abi 62:63` | DONE: CLEAN |
| make, make strict | DONE |
| test-cli, resource, cpset-structure, memfn link/manifest/g2/stamps | DONE: green |
| test-recursion-identity (~32 min, backgrounded) | §7 / handback |
| mech S513-S517 after the bump | §7 / handback |
| Linux command block, completion line, verdict rule, wall time, census | DONE: §6 |
| report + docs/dev/lanes/CLAUDE.md row | DONE |
| the bump as the LAST commit | the bump `b2e75d05` comes after the re-pins. Two tests/docs-only commits follow it: the FILEPIN self-pin (§3.3) and this report |
| full `make test`, the Mac suite lock | NOT run / NOT taken, per the brief |
