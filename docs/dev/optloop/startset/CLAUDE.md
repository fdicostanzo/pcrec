# docs/dev/optloop/startset/ — START-SET's alpha blocks (round 2, D144)

- `alpha_s2.sh` — stage 2 (THE VM HAT)'s Linux alpha (D144 item 1 and
  addenda 1/3; `docs/design/startset.md` §7's cells), on
  `../s4/alpha_k82h.sh`'s protocol: BASE (abi 61) / NEW (abi 62) / DENY
  (`-fno-start-set`), `W` movers (NEW != BASE, DENY == BASE) and `C` controls,
  absolute deltas against the |DENY - BASE| floor, the libc recorded in the
  header. WRITTEN, NOT RUN by lane ssbuild2: the run is owed to the manager's
  executor channel (`docs/dev/lanes/ssbuild2_report.md` §7 has the command).
