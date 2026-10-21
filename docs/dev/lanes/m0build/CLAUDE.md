# docs/dev/lanes/m0build/ — lane m0build's instruments ([MEASURE-SET] M0)

The reproduction pieces behind `../m0build_report.md`. Historical once the
lane is merged; never edited afterwards.

- `census.py` — the MOVER CENSUS for M0's abi event (81 -> 82): the
  branch point's compiler against the lane's over every distinct corpus
  pattern (`scripts/emit_sweep.py`'s enumeration) on five arms (the `.c` at
  default, `-e utf8` and `--engine=vm`, the `--emit-ir` listing, the
  `--emit-facts` listing), with exactly the declared scaffolding removed
  from the new side (the `measures` member, `#define RX_MEASURES ""`,
  `.measures = ""`, the abi digits, K112's two strings). Any other
  difference in bytes, rc or stderr is a mover. `--movers FILE` also writes
  the census as `measure_store/movers/0001.tsv`, DEFAULTS transition 1.
  Trailer `== m0 census COMPLETE: patterns=P compiles=C movers=M`; exit 0
  iff M == 0. Runs under the box lock.

Maintenance: update this file when files are added/removed or their roles
change.
