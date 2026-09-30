# axtri report — `make test-axes` refusals, Linux final run of main d6cb0bb4 (abi 49)

Lane `axtri` (sonnet, 2026-09-30), branch `lane/axtri` from main `495d3138`.
Logs read in place on ubuntubudu (`~/pcrec/.final_lx_keep/final_axes.log`); the
axes log caps its per-case listing at 20 lines per axis, so the full populations
were re-derived locally (Mac, gcc-16, this tree's `build/pcrec`).

## Verdict

Refusals only, zero answer movers, and every refusal is on ONE file,
`tests/utf8/wclass_illformed.rxt` (the [CLS-TREE] S4 wide-class corpus).
Corrected against the log's own sample: the 109 for `-fno-cls-kit` are TWO
groups, not one (the log's 20 lines only showed the first).

| axis | cases | route | cap | diagnostic | class |
|---|---|---|---|---|---|
| `-fprefilter` | 32 | `engine vm`, `\p{Xwd}` bare/captured, utf8 | emitted-BYTES 1,000,000 (1,013,468 / 1,013,932) | "bytes of emitted C source (limit 1000000" | (a) documented limit |
| `-fno-cls-kit` | 77 | `engine vm`, `\p{Xwd}` x2 (16+16), `\P{Unknown}` x3 (15x3), utf8 | emitted-CODE 500,000 (576,773 / 577,122 / 526,899) | "bytes of emitted code (limit" | (a) documented limit |
| `-fno-cls-kit` | 32 | default route, captured `x(\p{L})y`, `x(\P{L})y`, utf8 | emitted-BYTES 1,000,000 (1,179,060 / 1,153,832) | "bytes of emitted C source (limit" | (b) rescued by D135 |

No size-vs-state-cap split in the usual sense: all five are size caps; no DFA
or NFA state cap is involved.

## Evidence per group

**`-fprefilter`, (a).** `build/pcrec -p rx -e utf8 --features all --engine=vm
-fprefilter --pattern 'x\p{Xwd}y'` refuses at 1,013,468 bytes; without the
flag the artifact is 31,647 bytes. The forced prefilter is the byte DFA, which
is what the size is. tuning.md §2.5/§2.17 already say `-fprefilter` is
do-or-die and never dropped, and makes the size-ladder rungs that would undo it
ineligible. Checked against lane/pfdrop's compiler (read-only): it refuses
identically with and without `--fast-or-fail`, i.e. the D135 drop rung is
correctly not offered. So not (b) (brief point 4), and no defect.

**`-fno-cls-kit` 77, (a).** Denying the kit puts every wide class back on the
pre-abi-48 byte alternation, so the K55 refusal that S4 retired returns on
exactly its population (`--engine=vm` `\P{Unknown}` and `\p{Xwd}`); the
alternation is 526-577 KB against the 500 KB VM code cap. `engine vm` has no
prefilter, so pfdrop's drop rung has nothing to drop: pfdrop's compiler refuses
these 77 identically. Same diagnostic and substring as `-fno-size-term`'s
entry.

**`-fno-cls-kit` 32, (b).** On the default route the captured `(\p{L})`
compiles as a VM hybrid whose prefilter carries the byte alternation, 1.18 MB
against the 1 MB cap. lane/pfdrop's compiler rescues both
(`RX_ENGINE_SEL "size-cap-retry"`, `RX_VM_PREFILTER "none"`, 430,907 /
413,437 bytes); `--fast-or-fail` restores the refusal. Not documented as an
axis limit: it clears the day pfdrop merges and a substring for it would go
vacuous. The drop rung is not blocked here, since `-fno-cls-kit` is not
`-fprefilter`.

## Fix (commit `4fc0fe2c`)

- `tests/axes/run_axes.sh`: `REFUSAL_PATTERN["-fprefilter"]` gains the sixth
  shape; new `REFUSAL_PATTERN["-fno-cls-kit"]="bytes of emitted code (limit"`
  with `REFUSAL_FLOOR["-fno-cls-kit"]=60` (K35, measured 77). Comments carry the
  measured populations, the reason, and why the 32 are left out.
- `docs/spec/tuning.md`: a paragraph in §2.5 (forced prefilter is charged
  against the emitted-bytes cap, never dropped to fit) and one after §2.33's
  "Denied" (the K55 refusal returns by design). Per D80.
- `tests/axes/CLAUDE.md`: a short triage note.
- No `known_issues` row: nothing is (c). K81 is not consumed.

## Validation (local, single file, `SKIP_ORACLE=1 AXES="-fno-cls-kit -fprefilter"`)

Command: `bash tests/axes/run_axes.sh tests/utf8/wclass_illformed.rxt`.
- Before, this tree's compiler: `-fprefilter` 32 undocumented, `-fno-cls-kit`
  109 undocumented (matches the Linux log's counts exactly).
- After, this tree: `-fprefilter` 0 mismatches, 222 refused-documented;
  `-fno-cls-kit` refused-documented=77, mismatches=32 (the (b) group).
- After, `PCREC=` lane/pfdrop's `build/pcrec`: `-fno-cls-kit` OK, agree=667,
  refused-documented=77, mismatches=0; `-fprefilter` 0 mismatches.
- The `-fprefilter` "floor breached" line on a single-file run is inherent
  (222 against 12,000); the axis reads OK on a full run.

## Owed / ordering

1. **Merge lane/pfdrop before (or with) lane/axtri.** Until pfdrop is on main,
   `-fno-cls-kit` stays red on exactly the 32 group-(b) cases. If the manager
   would rather have the axes green first, adding `"bytes of emitted C source
   (limit"` to the `-fno-cls-kit` entry does it, at the cost of a substring
   that goes vacuous at pfdrop's merge (the floor of 60 would then not catch
   it, so it would need removing in the same merge).
2. Full `make test-axes` on Linux is the manager's, not run here. Expect
   `-fprefilter` and `-fno-cls-kit` green (post-pfdrop) and every other axis
   as in the failing run.
3. Not run: `make test`/`make strict` (script and docs only; `bash -n` clean).
