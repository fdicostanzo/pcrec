# trimreg report: `\s+$` on t-trim-match-60k, 6.1x regression (6b2dbd3e -> 9ae59f5d4)

Diagnosis only; no src/ change (no build go).

## 1. Reproduction (Ryzen 7700X, boxlock, `rx_search(buf,n,0,caps)` as the bench's pb_search)
Driver `docs/dev/lanes/trimreg/drv.c`, artifact from `pcrec -p rx --features all --pattern '\s+$'`,
`gcc -O2`, subject = the bench's t-trim-match-60k.bin (sha eb6cb875..., 61,440 B), result [0,61440).
- 6b2dbd3e (abi 76): 11,830-12,195 ns/call (bench 11,900)
- 9ae59f5d4 (abi 84): 73,950-74,940 ns/call (bench 72,890)
Ratio 6.2x vs the bench's 6.1x. Reproduced.

## 2. Bisect
`docs/dev/lanes/trimreg/bisect_step.sh` (good < 30 us), `git bisect run` over 6b2dbd3e..9ae59f5d4, one run:
first bad commit **4ea6fb19c** (2026-10-12, WIP): "B3.1/B3.2 (WIP): F1 one-seed in form W, the tail read
off \Z's definitions row, lower_eol as an NFA-build parameter + the pair construction, accept value =
distance set ..." -- lane b3build, D164 B3 (the `rev-end` one-walk / end-mark lowering, abi 78 family).
Bad value there 71,600 ns. Not bisected below abi steps because the commit is a single step.

## 3. Diagnosis (diff of the two emitted artifacts)
Both are `scan="rev-end"`, `search_form="reverse-pass"`: one reverse walk from n.
- OLD: reverse machine with 2 byte classes + an EOL view; its self-loop state (4) is a scan head, and the
  walk runs `while (rewind_position > search_from && rx_reverse_scan2[subject[rewind_position-1]]) rewind_position--;`
  -- a tight byte-set run loop (~0.19 ns/B), "every position the run passed accepts".
- NEW: `$` is lowered into the machine (lower_eol, `\n` handled at the seed), which splits `\n` into its
  OWN byte class (rx_reverse_byte_class: space/tab/VT/FF/CR = 1, `\n` = 2). The run states (cells 6 and
  12) self-loop on BOTH class 1 and class 2 and leave dead on class 0. No scan edge fires, so the walk is
  the generic loop: per byte `accept probe -> table load -> dead test` with the next table address
  depending on the previous load (the pointer-chasing chain scanedge.c's header measures at ~1.2-3.6 ns/B).
  1.19 ns/B vs 0.19 ns/B.
Root cause in code: `src/opt/scanedge.c` `shaped()` (~line 269) accepts a state only when exactly ONE class C
advances and EVERY other class goes to the same exit E (`tr[cls] == e` -> false). A state whose live
bytes are two classes both going to the same next state is "not scan-shaped", although the emitter
(`edge_advance`, emit_dfa.c ~12265) already builds the run test from a 256-byte SET (`set[b] = clsmap[b]==cls`),
so the emitted side needs no new idea. (`pick_skip_states` stay skips don't cover it either: they need > 191
stay bytes.) Nothing in the new emit is wrong; the abi-84 artifact is correct, just a byte-at-a-time walk.

## 4. Proposed fix (words only)
General form: scan-shaped w.r.t. a class SET, not a class. A chain member is scan-shaped for (S, E) when
every class in S goes to the same successor u_{i+1} (itself for `*`/`+`) and every class outside S goes to
the same exit E; the scan test becomes the byte set union(S) (a table/memfn set site, which `edge_advance`
and `scan_test` already produce for any set; DState needs `scan_cls` -> a class bitset or a representative
plus a set). Chains compare on (S, E, accept value) in `same_shape`. This is the same fact as the existing
single-class rule with |S| = 1, not a parallel mechanism. Alternative considered and rejected as a
special case: re-merging the `\n` class in the reverse machine (loses the lowered-mark distinction at
the seed). Owner: [OPT-EDGE]/[OPT-5] scan-edge code (src/opt/scanedge.c + emit_dfa.c scan edge emit),
reached through the D164 [OPT-REVEND]/endmark B3 form; the kit side (DELEG_EDGE advance site) already takes a
set. An emitted-text change => abi bump + identity-gate re-pin (D76/D94 ritual) when built. Also a
scan_cls consumer list: internal.h:2318, emit_dfa.c edge_advance/scan_test/scan_choice.

## 5. Population (measured locally, same driver, old -> new ns/call, 61,440 B subjects)
Affected (new ~71 us ~ 1.2 ns/B vs ~11.7 us old, i.e. 6x) only where the run class contains `\n` AND other
bytes that share the walk with it, as in `\s`:
- `\s+$` on all-space: 11.8 -> 72.0 us; `\s+$`/`[\n ]+$` on all-`\n`: 91.8 -> 71.7 us (old was already
  slow there: old scan2 head needed a separate class); `\s*$` all-space: 68.7 -> 67.4 us (old already slow).
Unaffected (new == old, ~11.5 us): `a+$`, `[a-z]+$`, `\d+$`, `\w+$`, `.+$`, `\s+\z` (no `$` lowering),
`[^x]+$`, `[\s\S]+$`, `(?s).+$` on `\n`-bearing text, `\W+$` on all-`\n` (these got faster or equal;
36-> 12 us for the three \n-class cases).
Bench side: the capability@0.2 report's own threshold population says 1 regress among 137 cross-pin
cells (line 55): this cell (and its nocaps twin, line ~4892 at 6.12x) is the only one. So the wider population
is "trailing-whitespace trim" idioms (`\s+$`, `\s*$`, `[ \t\n]+$`), which are a common real-world shape
but NOT otherwise in the bench's current patterns. Note old `\s*$` was already ~68 us on whitespace runs,
so the same fix would also win there.

## STATE AT HANDOFF
Reproduced, bisected, diagnosed, fix proposed; nothing built in src/. Rulings file
docs/dev/lanes/trimreg_rulings.md: no entries applied (file absent or empty at the check). Scratch worktrees
trimreg-old/new/bis removed via wtprune; branch lane/trimreg carries driver + notes only.
Files: docs/dev/lanes/trimreg/{drv.c,bisect_step.sh,pop_run.sh}.
