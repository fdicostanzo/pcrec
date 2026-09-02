# vmfl0 lane log — [OPT-VMFL] / [ENG-DIRECT] STEP 0

2026-09-02. Measurement only; nothing under `src/`/`tests/`/`docs/spec/`
changed.

1. Read the charter (`plan.md` `[OPT-VMFL]` row), background (dev_journal
   fiftieth session parts 3-4, bench inbox I-31/I-32, `emit_vm.c`
   :8090-8170/:9450-9580, `opt5_step0_profile.md` as the memo model,
   `tests/CLAUDE.md`, `docs/spec/match_api.md` §6.3, `docs/dev/CLAUDE.md`'s
   own file index). Built the worktree (`make -j4`, clean).
2. Measurement (a): wrote `census.py` (scratchpad), ran it over 2,825
   distinct corpus `pattern` lines + 77 bench `.rx` patterns, both
   `--engine=vm` and `--engine=auto`, extracting `RX_RESUME_FRAMES` and
   `has_push` (`goto *run->resume_stack` / `NO RESUME FRAME AT ALL`
   presence) from each compiled artifact. Result: `census_result.json`
   (scratchpad). 198 divergent artifacts, all lookaround, all corpus, all
   in the over-count direction; zero of the under-count direction I-32
   flagged. Ran a second targeted pass compiling the 1,090 truly-frameless
   patterns under `auto` to check whether the shape reaches natural
   selection (it does, on ~35 % of that population).
3. Read `docs/dev/lanes/vmfl0_rulings.md` (R1, from Frank via the
   manager): `[OPT-VMFL]` is `[ENG-DIRECT]`'s territory (`plan.md:880`);
   read that row and its 2026-08-18 third-engine-roster ruling
   (`plan.md:920-925`) before writing the memo.
4. Measurement (b): picked `csv5`/`nest2-64`/`ctx-lazy-256` from
   `bench/bounded/patterns/`, confirmed each is call-free (`RX_PUSH` only,
   no `RX_CALL`), wrote `handtwin/make_twin.py` (the `const void
   *resume_label` → `int`, `&&rx_LN` → `N`, `goto *` → `switch`
   transform), applied it, compiled both variants
   `-O2 -std=gnu11 -Wall -Wextra -Werror` clean. Built a correctness
   driver (15/15 subject cells identical, orig vs twin) and a timing
   driver (match + find-all regimes, 5 trials each). First find-all
   attempt on `ctx-lazy-256` (a worst-case subject tiled to 64 KB) did not
   finish one pass in 120 s and was killed via `scripts/safekill`
   (never `pkill`); re-targeted at a realistic fast-matching subject
   tiled to 8 KB instead. Result: mixed — `nest2-64` (24 resume labels)
   3-4 % faster on both regimes, `csv5`/`ctx-lazy-256` (4-6 labels) flat
   to 2.9 % slower. D77 trigger for a real dispatcher: not met.
5. Measurement (c): classified the proposed macro under §6.3's (a)/(b)
   split (it's (b) — VM-only, `.c`-private, unconditional, no `rx_info`
   mirror per the `RX_DFA_TABLE`/D77 precedent), and — per R1 — added the
   recommend-not-decide section on whether the fact stays a VM-route macro
   or becomes a preview of `[ENG-DIRECT]`'s eventual third engine value.
6. Wrote `docs/dev/optvmfl_step0.md`, framed as both `[OPT-VMFL]`'s and
   `[ENG-DIRECT]`'s STEP 0 per R1, and the `docs/dev/CLAUDE.md` index line.
   One commit for the whole deliverable (no intermediate heavy suite ran,
   so no natural WIP-commit boundary existed beyond the census and the
   hand-twin, both captured in this log instead).

No `make test`/`mech`/`san` run from this lane — build-only, per charter.
`load average` stayed 0.30-1.10 throughout; no `.hold` file was ever set.
