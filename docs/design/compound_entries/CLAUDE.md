# docs/design/compound_entries/ — the probes behind `../compound_entries.md`

Compile-only probes and clockless instruction counts for the assessment
"every exported entry as a compound controller over shared parts, the dial
deciding what is inline" (lane `cmpentry`, 2026-10-14). Nothing here is built
or run by `make`; nothing reads a clock. Scratch output goes under the
worktree's `build/` (gitignored); only the result tables are committed.

## Files

- `probe_entries.py` — the ENTRY MAP probe (§1.3). Compiles ten route
  witnesses with `build/pcrec`, then each object at `-O2` and `-O2 -fPIC`, and
  lists every function symbol (binding, size, instruction count) and its call
  edges from `objdump -dr`. A call to a global symbol is read from the
  RELOCATION on the line after the instruction (marked `@g`); objdump's
  printed target there is the placeholder's address and can name the next
  function, which the first version of this probe mis-attributed (fixed;
  sizes were unaffected). `python3 -I probe_entries.py PCREC SCRATCH >
  results/entries.tsv`.
- `probe_layout.py` — the LAYOUT probe (§2.1-§2.2). The same artifact under
  three layouts of its static parts (as emitted; every part `noinline`; every
  copyable part `always_inline`), `.text` bytes plus callgrind Ir per driver
  iteration (two iteration counts, differenced, so start-up cancels). gcc's
  refusals to copy a part are parsed from its error text and recorded as hard
  constraints. `python3 -I probe_layout.py PCREC SCRATCH drv.c >
  results/layout.tsv`.
- `probe_plt.sh` — the PLT probe (§2.3): static link vs shared object vs
  shared object built `-fno-semantic-interposition`, callgrind Ir per
  iteration; the last two differ only in the artifact's internal
  exported-to-exported edges.
- `probe_vmshape.sh` — the existing dial row (§2.4): `--vm-entry-shape=1..4`
  on a frameless VM witness, `.text` and Ir.
- `drv.c` — the driver all three dynamic probes link: N iterations of a
  find-all with `<p>_search` and the spec's advance, then one `<p>_match` per
  position, summed into a printed checksum.
- `results/` — `entries.tsv`, `layout.tsv`, `plt.tsv`, `vm_entry_shape.tsv`:
  the outputs the note cites (gcc 15.2, x86-64, the Linux dev box, main
  `d6e7fa993`).

Callgrind Ir is an instruction count, not time: it ignores branch prediction,
caches and the cost of the PLT's indirect jump. The note says where a time
measurement is owed.
