# lane gaprep: report

**Lane** `gaprep`, 2026-10-03, branch `lane/gaprep` from `d986874b`.
**Task**: the first instance of [OPT-GAPREPORT], whose contract is D144
addendum 2.
**Deliverable**: `docs/dev/optloop/gapreport_2026-10-03.md`, with its
instruments in `docs/dev/optloop/gapreport/`.

## What was done

- Copied the seven `b120b121-fc719ca4` report groups' `.tsv` and
  `.interpretation.md` files from the Linux box into the session
  scratchpad, by scp, read-only. Also copied the `fullroster-751b9c6d`
  matrices, which confirmed the comparator rosters are the same.
- Extracted every timing cell (`extract.py`).
- Compiled all 331 bench patterns with both the pin's compiler
  (`fc719ca4`, built in the scratchpad from `git archive`) and main's, to
  read the D81 stamps (`stamps.py`). No selection stamp moved.
- Computed the D144 metric per cell (`gap.py`) and the throughput
  denominators (`nmatch.py`).
- Assigned every losing cell to a cause group by hand (`causes.tsv`), with
  0 unassigned, and ranked the groups (`rank.py`).
- Probed `--emit-ir` prefilter reasons and the byte-vs-utf8 prefilter form
  for the new findings.

No `src/`, `tests/` or spec change. No make, no timing, and nothing written
to pcrec-bench.

## Findings beyond the ranking (for a resuming agent)

1. **U8-PICK (NEW, suspected defect, not traced in `src/`).** Under
   `-e utf8`:
   - no bench pattern gets `run-pinned`, and literals stamp
     `offset-set "0,1*"`;
   - `item done`'s required run starts at byte 1;
   - `cat`'s run pick moves from `@0` to `@2`.

   Byte mode gives the same literals run-pinned or memchr. Evidence:
   `gapreport/u8pick_probe.txt`.
2. **NULLABLE-ANCH (NEW).** The `no-nullable-exact` hybrid decline also
   fires on start-anchored one-attempt machines (`^(([a-z]+)*)+$`,
   `^(\s+)*$`), where its "zero-length match at every position" premise
   does not hold. re2 is x38 and x1081 ahead, and the cells carry a
   give-up.
3. **FS-VM shares START-SET's question.** The backref and recursion VM
   routes decline every prefilter (`no-backreference`/`no-linked-call`),
   but a first-byte start set is sound for them. [OPT-VMSEED], as
   chartered, seeds only from a necessary run. One question, two consumers
   (D124).
4. **The match regime has no same-form peer** (bench Q3). pcre2-jit is
   measured only `plain`, pcrec only `whole-subject`.

## Validation

There is no code, so there are no test runs. The data checks were:

- `rank.py` reports 0 unassigned losing cells.
- The group scores are re-summed in the report (START-SET 16.40 = 9.98 +
  6.42, and so on).
- The census totals are 603 = 501 + 15 + 87.
- The tier-C counts are 285 = 276 + 7 + 2.
