# k382_evidence — lane k382's mover census ([MEMFN] R-38 K38-2, pcrec abi 100 -> 101 over main e889ba64c since lane k382m; 99 -> 100 over d81ebd294 before)

`census.py` answers, over the whole corpus: which artifacts move between BASE (main e889ba64c, abi 100; d81ebd294, abi 99, before lane k382m) and the K38-2 tip, does every moved line lie in a population declared by
`docs/design/memfn/span_runs_sheet.md` rev 1.3 §5.1, and did every artifact that SHOULD move (predicted from
BASE's own facts listing and artifact, never from the tip) move as declared. emit_sweep has no abi
normalization, so an abi event's identity witness is this census (shape: `r30b_evidence/census.py`).

    python3 -I census.py --base BASE_PCREC --new TIP_PCREC --tree WORKTREE --out FILE [--jobs N]
        [--shard I/3]                    # gate shards: corpus pattern k goes to shard (k % 3) + 1
        [--sample N [--sample-seed K]]   # a sample run (witnesses + long-run patterns + an even spread)
        [--patterns-file F]...           # extra raw patterns
        [--no-xarms] [--no-composition]  # skip the identity gate's --extra arms / the composition stream
        [--abi 100:101] [--base-rev e889ba64c] # the event and BASE's revision (defaults)
        [--witness-bins BASE_W TIP_W]    # -DPCREC_SIMD_WITNESS builds: the identity arm `witness`
        [--control no-p3|no-norm]        # NEGATIVE controls: each must turn the verdict red

Arms: c-default, c-utf8, c-vm, c-vm-utf8, c-comments (`-fcomments`), c-simd (`-fmemfn-simd`), ir
(`--engine=vm --emit-ir`, may not move), facts (`--emit-facts=byte,utf8`), every `--extra` arm of the
identity gate (`emit_sweep.ident_arms`, ~190 streams), its `start` arm table (`emit_sweep.arm_table`, 42 rows at
c-default/c-vm), `witness` (with `--witness-bins`; named NOT COVERED without), and the composition stream.
NEW's abi digits are mapped back; the numbers in pcrec's size diagnostics are masked on both sides.

Populations (the docstring is the definition): P1 K, P2a/P2b the REQ_RUN stamp (tested link or not), P2s the
short-run stamp that only loses its `@`, only where the tip renders no reqrun block, `cover` DFA scan or
`run-pinned` prefilter (else UNEXPLAINED; counted apart, 10 examples listed), P3 the reqrun block (P3v: the one
run part takes a SIMD form on the simd arm), P4 the run pin (P4f: the dominated -> emitted flips), P5/P5k
comment text, `used` facts rows. Output: one `MOVED`/`UNEXPECTED` line per (arm, artifact), `== overlap`,
`== P2s-example`, one `== arm` line per arm, the K35 floor line, and `== census COMPLETE: N unexplained,
verdict GREEN|RED rc=R`. Exit 1 on any UNEXPLAINED artifact, a MUST mover that did not move as declared, an
empty task list, or (not on `--sample`/`--patterns-file`) an empty P1/P2a/P2b/P3 over c-default + c-vm.

The gate jobs 601-603 (`$PCREC_TMPDIR/scratch/memfn/k382/jobs/ident.sh`) run it with `--shard I/3 --jobs 16`.
