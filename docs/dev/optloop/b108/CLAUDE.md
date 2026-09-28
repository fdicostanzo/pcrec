# docs/dev/optloop/b108/ — the [B108] reading's compile-side instruments

Reproduction pieces for `../b108_reading.md` (lane o64read, 2026-09-28). No
clock is read anywhere here. The generated `.c`/`.s`/`.lst` artifacts are NOT
archived; they regenerate from pcrec `a32bc86e` and the pattern texts named in
the memo.

## Files

- `fncmp.sh` compares two x86_64 gcc-15 `-O2 -fPIC -S` assemblies of one
  artifact (default against `-fno-lit-run`) function by function. It
  normalizes labels (`.L*`, `LFB`/`LFE`, `.LC*`), so only instruction text is
  compared. Usage: `fncmp.sh DIR NAME...`, reading `DIR/NAME.{off,on}.s`.
- `offs.py` reads the per-function start offsets in `.text` out of gas `-aln`
  listings. It prints each offset and its value mod 64.
- `transcript.txt` holds every number the memo's §1 and §5 cite:
  - the function-identity table;
  - the offsets;
  - the VM body's shape (pushes, instructions, branches, `memcmp` calls);
  - lp's register-save region in both arms;
  - the L-sweep's pre-check shape per L.

  Its header states how the assemblies were made: the source was piped over
  ssh stdin to the bench box's own gcc, and nothing was written there.
