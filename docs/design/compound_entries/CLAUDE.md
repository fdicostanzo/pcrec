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
- `rev4_osize.py`, `rev4_osize_cls.py`, `rev4_vmshape_o.sh` — revision 4's
  SCRATCH-GRADE size probes (lane `cmprev4`, 2026-10-16, main `8eec6f874`;
  single run, compile-only, gcc 15.2 `-O2`, no clock). `rev4_osize.py`: the
  whole-`.o` bytes (`.text`, `.eh_frame`, allocated total, file, stripped file)
  of the layout witnesses under `gcc`/`shared`/`inline` at `-O2` and
  `-O2 -fPIC` (it imports `probe_layout.py`'s `variant()`). `rev4_osize_cls.py`:
  the same, with the attribute written on ONE part class at a time (prefilter,
  compound, and the owned VM entry chain for reference). `rev4_vmshape_o.sh`:
  three larger VM witnesses at `--vm-entry-shape=1..4`. Outputs
  `results/rev4_osize.tsv`, `results/rev4_osize_cls.tsv`,
  `results/rev4_vmshape_o.tsv`. The `o_file` column carries the source file
  name in the object's symbol table, so it moves by a few bytes with the
  scratch path; `.text` does not.
- `results/` — `entries.tsv`, `layout.tsv`, `plt.tsv`, `vm_entry_shape.tsv`:
  the outputs the note cites (gcc 15.2, x86-64, the Linux dev box, main
  `d6e7fa993`).

Callgrind Ir is an instruction count, not time: it ignores branch prediction,
caches and the cost of the PLT's indirect jump. The note says where a time
measurement is owed.
