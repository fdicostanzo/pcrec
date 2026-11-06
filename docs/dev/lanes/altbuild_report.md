# Lane altbuild — alternation normal form stages 1, 2p, 2b (BUILD)

STATE: in progress (WIP). Design: `docs/design/alt_normal_form.md` rev 3.
Build go: Frank, 2026-11-06, stages 1, 2p, 2b only.

## Ids taken

- Sabotage ids: **S1880-S1899** (the highest on main and in every worktree at
  this lane's start was S1856; taken from well above it, since another lane
  and the kit are allocating).
- abi: current + 1 at landing (grep at the time; another lane may bump first).

## Premise test (base 80341284e, before any code edit)

Reproduced on `build/pcrec` at the base: utf8 `req_whole_run` lengths
`(?i)abcdÀefgh` 6, `(?i)αβγ` 0, `(?i)Ελληνικά` 0, `(?i)привет мир` 0,
`(?i)naïve café` 8; `--engine=vm -fno-cls-kit` islands `x(?:[éà]1|q2|r3)y` 1,
`x(?:1[éè]|q2|r3)y` 0, `x(?:1[éà]|q2|r3)y` 1, `x(?:[éà]|q2|r3)y` 1,
`a[éÉ]b` 1, `(?i)aéb` 1, `(?i)xé+y` 2 (rungs `0x4u`, 3319 B). All as §5 states.
