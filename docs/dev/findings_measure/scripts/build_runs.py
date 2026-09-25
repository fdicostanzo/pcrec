#!/usr/bin/env python3
"""Builds data/runs.tsv: the candidate literal runs to rank (D123 addendum 3,
Q5's "run to rank" set). Two sources, neither of them raw corpus text:

  - the bench capability patterns' necessary literal RUNS (run_len >= 2),
    read from the already-committed run census
    docs/dev/optloop/c2/reqpos_census.tsv (produced by compiling the bench's
    patterns.rxt with build/pcrec and reading RX_REQ_RUN stamps -- see that
    census's own script, c2/reqpos_census.py, for the compile step; this
    script reuses its output rather than recompiling);
  - the three WAF keywords named in the brief (union / select / from,
    docs/dev/optloop/waf_attribution.md §3.2).

Output columns: name, run_hex, run_repr, run_len.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FM = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(FM)))
CENSUS = os.path.join(REPO, 'docs/dev/optloop/c2/reqpos_census.tsv')


def main() -> None:
    runs: dict[str, bytes] = {}
    with open(CENSUS) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.rstrip('\n').split('\t')
            if parts[0] == 'pop':
                continue
            pop, pid = parts[0], parts[1]
            run_len = int(parts[7])
            run_hex = parts[8]
            if pop == 'bench' and pid.startswith('capability/') and run_len >= 2 and run_hex != '-':
                runs[pid] = bytes.fromhex(run_hex)

    waf = {'waf/union': b'union', 'waf/select': b'select', 'waf/from': b'from'}
    runs.update(waf)

    out_path = os.path.join(FM, 'data', 'runs.tsv')
    with open(out_path, 'w') as f:
        for name, r in runs.items():
            f.write(f"{name}\t{r.hex()}\t{r!r}\t{len(r)}\n")
    print(f"wrote {len(runs)} runs to {out_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
