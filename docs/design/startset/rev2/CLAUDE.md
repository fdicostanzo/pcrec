# docs/design/startset/rev2/ — START-SET revision 2's instruments

Reproduction pieces for `../../startset.md` revision 2 (lane `ssrev`,
2026-10-05, from main `08caf4a3`, abi 61), which applies the D6 panel r4
(`../../../dev/reviews/2026-10-05-r4-startset.md`). Everything here is
answer-only and compile-side. Local libpcre2 is 10.48 (Homebrew), NOT the
10.46 reference. Nothing here is built or run by pcrec's `make`, and no
check reads `out/`.

- `estar.py` reads an EMITTED artifact's forward tables and returns `E`
  (s0's escape set, checked against `can_begin_match`), `E*` (the union of
  every seed state's escape set) and `Tdfa` (the bytes that begin a live
  thread from some seed state). It handles premultiplied and strided step
  forms, `==N`/`<0` dead states, and the `search_from`/`handoff_position`
  initializers.
- `patch.py` writes a set into `<pfx>_can_begin_match` and adds the re-seed
  on skip exit. The patch text is `dfatwin.py`'s.
- `drv5.c` runs base against four narrowed+re-seeded twins (`c_` r3's
  `S ∩ E`, `a_` `S ∩ E*`, `b_` `S`, `d_` `Tdfa`). It covers every subject
  and every startpos, compares the full capture vector, and has a
  `-DWITH_PCRE2` arm. It also emits the START-BYTE ORACLE sets.
- `sweep.py` drives `drv5.c` over the six sound-F1 witnesses
  (`ALPHA`/`MAXLEN`) and over every seeded byte-class census row (per-row
  alphabet). It reports diffs, the static check `Tdfa ⊆ T`, the oracle
  check, and each option's admission verdict.
- `summarize.py` turns `out/witnesses.tsv` + `out/sweep.tsv` into
  `out/sweep_summary.txt`, the tables in startset.md §4.1a.
- `fs_probe_plant.c` is `../fs_probe.c` with four planted WALK defects
  selected by env `PLANT`: `cat-null`, `alt-right`, `look-eats`,
  `rep-min0`. Unset, it is identical to the original.
- `control.py` is C-SS\*: `Tdfa ⊆ S` (seeded) / emitted `can_begin_match ⊆ S`
  (unseeded) on every DFA/hybrid census row, for the shipped walk and each
  plant. It reports reach beside detections and counts the UNREAD rows.
- `drv_obs.c` + `vmoracle.py` are the start-byte oracle on the VM hat's
  populations (`auto`, `vm`), with the artifact and libpcre2 as the two
  sources of match starts.
- `run.sh` is the end-to-end reproduction from the repo root.
  `W=<scratch> docs/design/startset/rev2/run.sh` writes `out/`.
- `out/` holds the transcripts the note cites:
  - `witnesses.tsv`
  - `sweep.tsv` (its `wb-512` row was re-run after `estar.py` learned the
    signed/strided table form)
  - `sweep_summary.txt`
  - `control.txt`
  - `vmoracle_auto.{tsv,txt}`
  - `vmoracle_vm.{tsv,txt}`

  They were produced by the same commands `run.sh` chains, run step by
  step. `run.sh` itself was not run end to end.

**Instrument defects found while running (none reached a cited number).**
- `estar.py` first assumed state 0 was the start state. On UNSEEDED machines
  the start state can be any id (`dig-exact-2` starts at 2 and carries a
  scan edge). That made `control.py`'s first run read 2,585 rows with wrong
  unseeded `E`s. It now parses the initializer, and on unseeded machines
  `control.py` reads the emitted `can_begin_match`, which is r3 C-SS's
  subject.
- `estar.py` also failed on the signed/strided table form (`wb-512`) and on
  the K82 handoff initializer (`kv-quoted`, `word_boundary.rxt:91`). The
  sweep's own numbers predate the initializer parse, but every seeded row
  there starts at 0. A re-read of all 93 sweep artifacts with the final
  `estar.py` reproduces every `|E|`/`|E*|`/`|Tdfa|` exactly.
