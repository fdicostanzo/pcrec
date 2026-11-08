# [TEST-REVIEW] row body (long notes)

## 2026-11-08 — filed (Frank: "Start an unscheduled testing review item with these notes")

Frank's question: "Our tests are integration tests in that they test paths. Is there value for this project in unit tests against functions?"

Inventory (manager, 2026-11-08): every test path is pattern -> compile -> run -> compare (the .rxt corpus, oracle differential, codegen structural checks, mech). The C drivers under tests/ (vm_driver.c, trail_compact_driver.c, findall_driver.c, ...) test GENERATED matchers. No test calls a src/ function directly.

Manager's notes (not ruled):
- **Where function-level tests would pay:**
  1. Fact and analysis functions (`src/facts/req.c` and siblings, the rewrites in `src/opt/`): near-pure, syntax tree in, facts out. Through the pipeline, a test input must survive every upstream rewrite to reach its function. The 2026-11-08 battery's three mech misses (S50, S806, S-U10; lane mechtri) were exactly that: the [ALT-NF] folds and variable lookbehind rerouted the witnesses. A direct test is immune to upstream drift, and it checks facts that change no answer (S-U10: same answers, different code).
  2. Seams: the handoff architecture already asks for contract + tests per seam, and plan-as-text means seam inputs can be text records. Recorded input -> the kit planner -> reply compared is a unit test of the seam; it grows with [IR-FORM].
  3. Declared decision tables: one witness per row, checking that the row fires. Cheap and stable, because the table is the contract.
- **Where they would not pay:** emitters and generated code. The oracle differential is the real check, and the abi stamps pin the emitted text; text-level unit tests would break on every layout change.
- **Main cost: churn.** Pre-1.0 internals are refactored often (D153 remodel-first). Test at STABLE boundaries (seam records, fact outputs, table rows), never at helpers.
- **Cheap middle path:** a mech witness could be compiled with the passes upstream of its site DENIED (the deny flags), so it keeps reaching the site whatever those passes learn. Not a unit test, but it would have prevented two of the three 2026-11-08 misses (S50, S806) at almost no cost.
- **Leaning:** no broad unit-test layer. (a) seam contract tests from text records, riding along with [IR-FORM]; (b) one small test-only driver for fact functions (pattern in, chosen passes on or off, printed facts compared with an expected file), starting with `req.c`, where witness drift recurs; (c) the deny-upstream witness rule for mech rows.

Related, not adopted (Frank 2026-11-08, "never mind"): a coverage path map selecting mech rows per landing. Recorded only so it is not re-proposed as new.
