# s4rev2 report — [OPT-LITSCAN] S4 C3 revision r2 (2026-10-03, lane s4rev2, opus, design only)

Branch `lane/s4rev2` from main `af615d01`. Nothing under `src/`. The task:
apply the nine round-2 findings (`docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`,
"Round 2") to `docs/design/litscan_s4.md` C3, each per its disposition, edits
marked `[r2 <id>]`, plus a §R2 table.

## Summary (resume from here)

All nine applied; §R2 is the table. **The mechanism's shape did not change**
(position domain, hull, one ranking, one floor, pair arm, P7 conjunct, bit 44,
stamp grammar, C3 last).

- R2-S1: no pair-arm search above the loop; a `fresh` flag, every search under
  `pos + maxk < n` (emitted block written out); empty/short-subject cells;
  ASan/UBSan at exact subject length; `[K27]` NULL driver; S454.
- R2-S2: dispatch `run_mask && run_mask[scan_k - run_o] != 0xFF` → pair arm
  FIRST; S453 + a lowercase cell; `ofsk_emit_verify`'s run term masked in
  `t[0]` and `t[1]`.
- R2-S3: `T & ~K == 0` stated, refused at `rr_pos`, checked via
  `--emit-facts`; S455.
- R2-C1: `pcrec_find_pick` takes cube candidates (`care`, NULL = bytes), NONE
  = rightmost inside; `findings/design.md` §6.1/§6.2 hunk named for C3's
  commit (NOT edited now: it describes shipped code); `bar(?i:x)` stated.
- R2-C2: "byte-identical" reworded as facts; the §5.1 manifest is the byte
  evidence (auto + `--engine=vm`, bench 4 configs).
- R2-C3: pins kept — the maximal exact stretch around the window's rarest
  exact byte; G1's "verifies" read over cubes.
- R2-C4: C2's slack control read on C2's commit only; `syslogbase-expanded`
  survives C3.
- R2-C5/C6: the two floors said plainly; four §4 readers added
  (`ship_log_movers.txt`, CHANGELOG, a bit-44 `run_axes.sh` group,
  `docs/guide/` none).

## The census re-run (R2-C3)

`docs/dev/optloop/s4/c3census/`, PROTO = main `af615d01` + `proto.patch`
(now with r2's fact half), BASE = main's `build/pcrec`. Serial, compile-only,
60 s per compile, none fired; ~3 min per run on the loaded Mac. Run twice:
the first pin rule ("longest exact stretch") moved `/abcd[xy]/user`'s pin
6 → 0, so the rule became "the stretch around the window's rarest EXACT byte"
(one PICK call), which keeps it at 6. The committed TSV/summary are the
second run.

- Class B (exact winning run): 505 + 98 = 603, identical on whole run, window
  + idx, `req_byte` and `run_pin` (B! = 0).
- A1 ∪ C = 41 (23 + 18), unchanged. Bench compiled 317 → 321 (the live
  pcrec-bench exports grew; all four new ones are A0).
- `a[bc]de` → `run_pin 2:2+2`, `(?i)x/1234` → `1:1+5`: same offsets and
  stretches as today's runs, so both keep `run-pinned` (0 selections move;
  r1 had 2).
- Of r1's 10 lost pins: 9 keep a pin at the same offset, 1 lost (`slack`,
  `offset-set`, row does not read the pin).
- G1: `a[bc]de` `dominated` → `emitted` (offset 1 untested by its run-pinned
  test, read off BASE's `RX_DFA_PREFILTER_OFFSETS "0,2*,3"`); `(?i)x/1234`
  stays `dominated` (offset 0 is a model term `{x,X}`). A prediction; the
  build's manifest confirms.

## Validation

Design only: no `make test` (per brief). The proto built clean apart from one
`-Wmissing-field-initializers` on a proto-only line. The scratch proto
worktree (`worktrees/s4rev2-proto`) was removed after the run.

## Owed / for the build lane

- `findings/design.md` §6.1/§6.2 hunk lands with C3's code, not here.
- The G1 move on `a[bc]de` has no timing cell; bit 44 is its interim kill
  switch.
