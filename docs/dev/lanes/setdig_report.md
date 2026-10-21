# setdig report -- the kit's interim/synthetic sets made valid under docs/spec/measures.md

Branch `lane/memfn-setdig`, cut from main 764223688 (abi 82, M0 merged). Zero pcrec
movers by construction (no `src/`, `cli/`, `lib/` byte touched); sweep verdict in §5.

## 1. What was invalid (found by running `build/pcrec --list-measurements=FILE`, not by reading)

| # | defect | files | spec |
|---|---|---|---|
| 1 | digest hashed the FIRST LETTER of unit and status, not the code-table bytes | all 5 sets | §3.1, §3.3¶1 |
| 2 | the FNV-1a-64 offset basis was mistyped (`1469598103934665603`, a digit short of `14695981039346656037` = `0xcbf29ce484222325`), so even with the right bytes no digest would match | all 5 | §3.3¶1 |
| 3 | synthetic rows had status `synthetic`, which is not in the closed list | 4 synthetic sets (and `b4prep-v1max2.tsv`'s 3 placeholder rows) | §3.1¶1 |
| 4 | no row for `unit_key` (`kit.beta.WALK.DFA_SCAN.r1e0c0`): the loader refuses "names no row" | 4 synthetic sets (and `b4prep-v1max2.tsv`) | §3.1¶2 |

Before: the loader refused all five (interim: digest mismatch; synthetics: status). After defects 1-2 are
fixed, `kit-interim-grid1` digests to `13a6536315af1520`, the same as the store's `zen4-grid1@1`
(same rows; `from_interim.py` changed only `id` and the digest, as its header says).

Header keys and columns: nothing else the spec requires is missing (every R key present, the
column lists equal §2.2's). Not done, deliberately: the files are not byte-canonical
(§6¶2 applies to COMMITTED STORE sets; these are not in the store). `--view=canonical` would
reorder the cards section and add an empty `libc`. Not required by anything that reads them.

## 2. The fix

- `memfn/data/sets/generate.py`: `UNIT`/`STATUS` from §3.1, right offset basis, digest feeds
  the two code bytes; synthetic rows status `measured` (tier `synthetic` and the source column
  carry the label); the four synthetic sets gain the unit row (ratio 1, `measured`); header
  comment now cites `docs/spec/measures.md`. Sets regenerated.
- `memfn/data/cards/kit-synthetic.tsv`: a `beta` card appended to `kit-synthetic@1` (the unit
  row has to be on-card). No existing row changed. Note: the cards file is "append-only by
  version"; this appends a quantity within @1 rather than opening @2. A ruling is welcome
  if you want @2 (every synthetic set's cards section and `method` would move).
- `docs/design/memfn/r17b_prime/b4prep/mk_lever_set.py` + regenerated `b4prep-v1max2.tsv`
  (it imports generate.py's `row`/`render`, so it would have KeyError'd; and its set had defects
  3 and 4): placeholders `measured`, unit row added. 11 rows (was 10). Digest `af6f4d99889cfea7`.
- The digest implementation: the tree's one C source is `src/core/ks_measures.c` (the loader); the
  independent spec-only reader is `tests/knowledge/ks_ref.py` (`digest FILE`). generate.py keeps
  its own writer-side digest (it must compute before the file exists); the check below does not
  trust it.

## 3. The check, and where it runs

`tests/memfn/finder_check.py` check C (`make test-memfn-finder`, already in `make test`'s list):
for each of the sets under `memfn/data/sets/`: (a) `generate.py --check` (existing); (b) a unit or
status outside §3.1's table is a FAIL; (c) `values_digest` recomputed by finder_check's OWN
digest, now written from the spec (it previously copied the same first-letter rule -- the control
shared its mistake with what it controlled, learnings §3); (d) `ks_ref.py digest FILE` must equal
the header; (e) `build/pcrec --list-measurements=FILE` must exit 0 (the C loader's digest, unit row,
code table, card and header checks). Count: finder_check now 964 checks (two new per set: ks_ref and the loader, plus the
code-table guard; the pre-change total was not recorded).

Red/green (logs in `build/tmp/`, not committed):
- GREEN, new files: `make test-memfn-finder` rc 0, `finder_check checks passed: 964, failed: 0`.
- RED, planted: `values_digest 0000000000000001` in `synthetic-all-v1.tsv`: rc 2, 4 FAILs (generate.py
  --check stale; finder_check's digest; ks_ref.py digest; the loader refuses). 
- RED, the OLD files (`git show HEAD:` restored): rc 2, 12 FAILs: interim digest by finder_check,
  ks_ref and the loader (66f013b21e281f18 vs 13a6536315af1520); the four synthetics' status outside
  the code table; the cards section mismatch (beta card); generate.py --check.
  (Before this lane's edit to finder_check the old files were GREEN: its twin shared the mistake.)

## 4. Readers of the set files, by grep (command grep over the worktree)

| reader | uses | behaviour change |
|---|---|---|
| `cli/main.c` `harness_measures_load` (`--harness=measures=FILE`) | `key value unit value_e6 status source`; skips only `status == null`; takes `kit.` rows; hands `values_digest` as a string without checking | none: `measured` is not `null`; `unit`/`source` text unchanged; the one added row is `kit.beta.WALK.DFA_SCAN.r1e0c0`, and no finder row reads a `beta` key (`command grep -rn 'kit\.beta' memfn/src src` finds only the generated `measures_table.inc` store data). The digest is stamped only when a set is CONSULTED, and no routed row reads a key before B4. |
| `tests/memfn/finder_check.py` (C, D, E, F) | the sets and `synthetic-every-key.tsv` as the full set | C updated (above); D/E/F run green (964 checks) |
| `tests/memfn/arm_fixtures.c` | in-C `mf_measures` fixtures with tier `"synthetic"`, own digests `0000000000000000` | none, no file read |
| `docs/design/memfn/r17b_prime/b4prep/mk_lever_set.py`, `jobs/chain_b4close2.sh` (`--set $B/`) | the lever set, harness lever | regenerated (see §2); same values for every key a row reads |
| `docs/design/memfn/r17b_prime/fdb1|fdb2/predicted_movers_B4.tsv`, `fdb1/CLAUDE.md`, `memfn/PROVENANCE.md` | cite the files in prose | none |
| `src/core/ks_measures.c`, `measure_store/from_interim.py`, `tests/knowledge/*` | read the STORE's `zen4-grid1`, not these files | none |
| sweeparm / finder-harness lever sets elsewhere | `command grep -rn 'synthetic-all\|synthetic-every\|kit-interim-grid1\|data/sets'` outside docs: only the above | none |

Light validation, all green: `make` , `make strict`, `make test-knowledge` (282 checks, 0 failed),
`make test-memfn-finder` (964), `make test-memfn-arms`, `make test-memfn-stamps`.

## 5. Zero artifact movers: emit_sweep plain arm

OWED at the time of this commit: the box lock was held by `queue:540-z2build-sweep`; the job is
armed and detached (survives the lane's end). Command (the r26zk job's plain arm, without
`python3 -I`; the reference is built by the script from `--ref 764223688`, main before this lane):

    scripts/boxlock run --label kit-setdig -- gnutimeout 3000 python3 scripts/emit_sweep.py \
      --ref 764223688 --bin build/pcrec --tree <worktree> --no-self-check --jobs 4 --comp-jobs 4 \
      --out <worktree>/build/tmp/sw_plain --streams c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr,dumps

Log: `/home/pcrec/projects/pcrec/worktrees/setdig/build/tmp/sweep.log`; completion line
`emit_sweep: DONE rc=0`; every stream must read `movers=0 asymmetric=0`. (No pcrec source differs
between the two builds, so movers=0 is expected; the sweep is the proof.)

## 6. Charter vs committed

Charter: valid digests + other missing spec fields, regenerated sets, cards if they cite digests
(they do not), an independent red/green check wired in an existing target, readers, sweep, CLAUDE.md.
Committed: all of it except the sweep verdict (OWED, §5). Beyond the charter: the `beta` card in
`kit-synthetic@1` (needed by the unit row), the b4prep lever set and its generator (a reader of
generate.py), finder_check's own digest corrected. Deliberately not done: canonical byte form
(§1), a `kit-synthetic@2` (§2).
