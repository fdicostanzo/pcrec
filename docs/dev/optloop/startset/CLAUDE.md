# docs/dev/optloop/startset/ — START-SET's alpha blocks (round 2, D144)

- `alpha_s2.sh` — stage 2 (THE VM HAT)'s Linux alpha (D144 item 1 and
  addenda 1/3; `docs/design/startset.md` §7's cells), on
  `../s4/alpha_k82h.sh`'s protocol: BASE (abi 61) / NEW (abi 62) / DENY
  (`-fno-start-set`), `W` movers (NEW != BASE, DENY == BASE) and `C` controls,
  absolute deltas against the |DENY - BASE| floor, the libc recorded in the
  header. WRITTEN, NOT RUN by lane ssbuild2: the run is owed to the manager's
  executor channel (`docs/dev/lanes/ssbuild2_report.md` §7 has the command).
- `alpha_s3.sh` — stage 3 (THE DFA HAT)'s Linux alpha, `alpha_s2.sh`'s
  protocol: BASE (main before the hat) / NEW (abi 64) / DENY
  (`-fno-start-set`), `W` movers (NEW stamps `first-*`, DENY == BASE) and `C`
  controls, absolute deltas against |DENY - BASE|; the IMPROVE cells, F3 at
  the DENSE movers (kv-quoted, wb-256/512, hex32-id: sign 0), the one-byte
  null cells (grok, float-literal) and the null band. WRITTEN by lane
  ssbuild3; the Linux run is the manager's (`docs/dev/lanes/ssbuild3_report.md`
  has the command and the Mac directional reading).
