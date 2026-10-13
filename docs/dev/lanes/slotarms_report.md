# slotarms -- pcrec engine arms for the joint timing slot (PREPARED, nothing timed)

Lane `slotarms` (sonnet), 2026-10-13, branch lane/slotarms off c4e30f413. Files: `slotarms/`.

## Why these arms
The cost model is time ~ calls*C_call + uses*C_use + matches*C_match + bytes*c_byte. The kit measures its
own search-form terms; these arms isolate pcrec's per-ENGINE terms with the kit off the path.

Cells (`slotarms/arms.tsv`), all unanchored, byte encoding, `-p rx`, gcc -O2:

| cell | pattern | engine as built |
|---|---|---|
| p1-dfa / p1-vm | `[0-9][a-z]` | `--engine=dfa` / `--engine=vm` (forced; vm has no DFA prefilter) |
| p2-dfa / p2-hyb / p2-vm | `([0-9])[a-z]` | dfa: `--engine=dfa --no-captures`; hyb: auto = VM with the exact DFA prefilter (the HYBRID; the capture group forces the VM); vm: forced |
| p3-dfa / p3-vm | `[0-9]+[a-z]` | forced dfa / forced vm; variable-width match (in-match loop) |

Same-pattern pairs/triples give the engine contrast directly (p1: dfa vs vm; p2: dfa vs hybrid vs vm; p3 as p1 with a
loop in the match). Patterns are deliberately start-set-only (digits first), with no required literal, so there is no
offset-skip or memchr and no necessary run for the kit to render.

Subjects (`gen_subj.py`, deterministic): `e0` empty; `nm8 nm64 nm1k nm64k` all `a` (never hits the start set);
`mw2-L{8,64,1k}` / `mw5-L{8,64,1k}`: 64 KiB made of L-byte units, each unit = the match (`7a`, or `7777a` for p3) then
`a` filler, so there is EXACTLY one match per L bytes (8192 / 1024 / 64 matches), disjoint.

Rows per cell (8; 7 cells = 56 timed rows):
- C_call: `first` on `e0`, `nm8`, `nm64`, `nm1k` (no match: one call, bytes known; the intercept as a function of n).
- c_byte: `first` on `nm64k` (one call, 64Ki bytes, no match; slope against the C_call rows).
- C_match: `all` (match_api.md 3.1.3 loop over `rx_search`/`rx_next_pos`) on `m*-L8`, `-L64`, `-L1k`: matches/calls = 8192,
  1024, 64 over the same 65536 bytes, so c_byte is constant and the per-match increment is the slope in matches.
Collinearity: in find-all calls = matches + 1, so per-engine C_call+C_match is identified there and C_call alone from
the `first` rows; C_match = (find-all-row - c_byte*bytes)/matches - C_call.

## Verification (run, green; nothing timed)
- `verify.sh` stamps (read off each artifact): RX_ENGINE as in the table; p2-hyb `RX_VM_PREFILTER "hybrid"`, forced-vm
  cells `RX_VM_PREFILTER "none"`. NO KIT FORM: every artifact stamps `RX_MEMFN_FORMS "none"` and `RX_MEMFN_LIBC "none"`
  (no kit find form, no libc memchr skip), and `grep` of the 7 art.c for immintrin/emmintrin/ia32/memchr/memrchr/memmem
  is empty. DFA prefilter on the dfa/hybrid cells is `byte-class` (pcrec's own table walk, not a kit row).
- Answers: all 77 (cell, subject, mode) checks (first span; find-all count) equal python3 `re` on the same bytes: 0 mismatches.
  The check uses the same binaries as timing (`run SUBJECT MODE check`, no clock).

## Interface assumption
Targeted the kit's vecspike harness shape (read-only: `worktrees/vecspike/docs/dev/lanes/vecspike/{time.sh,build.sh,vdrv.c}`
and `memfn-slot/spike1/slot.sh`): `bin/<cell>/V0/run SUBJECT_FILE first|all` printing `matches=N hash=H ns/pass=X` (7-round
median, rounds calibrated >= 50 ms), subjects as files in `subj/`, V0/V0b A/A floor, CPU pin, load guard, completion line
`time.sh: COMPLETE rows=N wall=Ss`. Differences: (1) kit time.sh reports variant-minus-V0 deltas and prints nothing for a
V0-only cell, so `slotarms/time.sh` prints absolute ns with the A/A floor instead; to use the kit's own time.sh one would need
a second variant per cell (unneeded here). (2) In `first` mode `matches=` is 0/1 (found), not the kit's constant 1.
(3) Cells are named by pattern/engine, one variant `V0`. If the kit relays a different harness, only `build.sh`/`time.sh`
change; `arms.tsv`, `gen_subj.py`, `drv.c` and `verify.sh` carry over.

## Expected cost
`bash time.sh --estimate`: 56 rows x (5 launches x V0,V0b) x ~0.65 s = ~6.1 min plus load-guard waits; at the kit's
5-7 s per arm-cell that is 5-7 min wall. Build ~seconds (-j2, pinned to 12-13); verify well under a minute.
Run: `make; bash build.sh; bash verify.sh; OUT=... CPU=14 LAUNCHES=5 bash time.sh > time.log`.

## Caveats
- A 64 KiB subject exceeds L1 (32 KiB data) on Zen 4: c_byte is an L2-resident figure; the 1Ki rows are L1. Not changed; the
  kit's own subjects are 64k too (prose64k).
- Forced-VM `nm64k` is one linear start-scan pass (first-class table), not the quadratic case; the VM's step budget is untouched.
- Hybrid vs forced-VM share patterns, so hybrid-minus-vm is the prefilter's net effect, not a pure engine term.
