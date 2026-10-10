# Lane pfdesign — [PATFACTS] step 2 (the design) — report

**Lane:** pfdesign (opus), 2026-09-26, worktree `worktrees/pfdesign`, branch
`lane/pfdesign`, from main `e060f2e0`. Design lane: docs only. Nothing under
`src/`/`tests/`/`docs/spec/` changed. `plan.md` STATE was not touched (the
manager owns it).

## Delivered

1. **Step A: `docs/design/patfacts/inventory.md` § "Delta 2026-09-26".**
   N1-N9 are the new or moved facts (req_set, ReqRun.whole, vm_frameless,
   the run pin, OfsTest, CandScan, the 64-bit deny word plus bit 32, the
   rightmost run decline on `lane/reqrunenc2`, and B0's schema).
   D.2 covers new consumers of old facts. D.3 names three new
   redundancies:
   - **R13** is the `[OPT-REQRUN-ENC]` incident, named as a D120-class
     redundancy: two copies of the prior's non-byte decline, `rb_pick`
     rightmost vs `rn_scan_index` leftmost, which diverged into a shipped
     utf8 throughput defect. Stage 2 makes them AGREE, not ONE.
   - **R14**: the k-set walk is re-run per `req_admit` ask.
   - **R15**: one fact-deny has several consumers under one name.
   The section also records a small text slip in the reqrunenc2 amendment
   to `reqpos_2b.md` §2.3: it calls rb_pick's fallback "leftmost" and then
   "rightmost".
2. **Step B: `docs/design/patfacts/design.md` (PROPOSED).** §0 lists the
   ten decisions. §1 is the record table, giving for each fact its grain,
   core/derived, epoch, owner, deny and consumers. The remaining sections:
   - §2: lazy memoized accessors, with a lens table.
   - §3: three sealed epochs (E1 after callgraph, E2 after lower_enc,
     E3 after the final forward NFA).
   - §4: core vs derived, ownership (`src/opt/facts.c` = memo + epoch
     guard + deny only), what the record is not (rewrites, route and
     emission decisions), and the per-consumer contracts (D124 item 3).
   - §5: how consumers read.
   - §6: encoding. No fact reads the encoding enum. The prior's NONE
     answer is spelled once per QUESTION KIND (pick / compare / mass)
     inside findings primitives, which is R13's structural cure and
     amends findings sec. 6.1-sec. 6.3.
   - §7: deny. Fact denies are "nothing to find" for every consumer, and
     row denies are rows. Measured witness table. No use-deny is built
     (the four existing configs span the bench attribution).
   - §8: the first customers. B1 is the data tier plus three primitives.
     S2a reads ONE node-grain fact, the emission-contiguous literal run,
     which is not rb_walk's run. S2b (carried facts) is specified and not
     built, with a trigger.
   - §9: the migration order, with a gate and abi status per step.
   - §10: not built, each with its trigger.
   - §11: the inspection surface `--emit-facts` (scope addition, Frank 2026-09-26), below.
   - §12: ten questions for Frank.
3. **Step C:** `design.md` §12, ten open questions, each with a
   recommendation.
4. The CLAUDE.md files are updated: `docs/design/patfacts/CLAUDE.md` and
   `docs/design/CLAUDE.md`.

## Validation

A design lane has no suite verdict. Performed:
- `make -j4 CC=gcc-16` in the worktree (rc 0).
- Build/pcrec probes producing §7.2's witness table (run-pin and G2
  interactions under `-fno-req-byte`/`-fno-req-run`/`-fno-run-prefilter`/
  `-fno-vm-anchor-bound`).

Every cited `file:line` was re-grepped at `e060f2e0`. No heavy run was
launched (box rule).

## For a follow-up agent

- The D6 panel attacks `design.md`. Suggested lenses: (1) the soundness
  of the E1 invariance claim (§3) and of fact-deny-for-all-consumers (§7);
  (2) byte-identity of §6.3's candidate-order argument for `rb_pick`/
  `rn_scan_index`/`rn_window_start`; (3) the ownership/structural-check
  plan and the §9 gates (is the corpus A/B emit diff sufficient; the
  REACH line).
- If Frank adopts Q4, `findings/design.md` §6.1-§6.3 needs the manager
  edit before B1 opens. Its C2 row's "leftmost" NONE is already stale
  after reqrunenc2.
- APPROACH.md's D124 amendment is due after this step (§12).

## Round 2: the scope addition (Frank, 2026-09-26): an accessible record

New `design.md` §11 (the questions moved to §12, pointers to §13).
- **`--emit-facts`** is a query in `--emit-ir`'s style. It takes an
  encoding list, runs one compile per encoding, and prints three
  table-contract sections:
  - `facts`: every `facts.def` fact with epoch, status
    (derived/denied/declined/absent), used yes/no, the value, and a
    why token (`deny:<flag>` / `decline:<reason>` / `rate:...`);
  - `rate`: the `<P>_FINDINGS` tokens only;
  - `decisions`: the stamp block, CAPTURED as the prologue writes it.
- **One printer:** `src/dump/facts_dump.c` reads the memo, including the
  status and why stored by the accessor. It never calls a derivation (the
  grep check excludes it).
- **Unasked facts** are forced through the same accessors AFTER the
  artifact and stamps are complete, and marked `used no`.
- **Four checks:** non-perturbation, completeness, why-truthfulness
  against the deny sweep's own flag list, and decisions = the emitted
  `#define`s.
- **Contract recommendation:** a debug listing under a spec page
  (`docs/spec/facts_listing.md`, the `ir_listing.md` precedent: format
  and vocabularies promised, rows advisory, no abi).
- **Stamps:** `REQ_BYTE`/`REQ_RUN`/`VM_START` render through the fact's
  shared renderer (byte-identical, lands with step 3.0). Decision stamps
  stay with their owners and are captured.
- §10's "dump of the record" row is marked TRIGGER FIRED.
- New questions Q8-Q10.
