# S41 — [M4.5c] THE LISTING DRIFTS FROM THE ARTIFACT. engine_m4.md S10's one
# constraint on DD-8's dump is that it "must be derived from the same
# structure the emitter walks, never a parallel description — a second source
# of truth for what the VM does is worse than no dump."
#
# The emitter satisfies that by construction (every listing event is appended
# by the same call that writes the corresponding C), and this sabotage attacks
# exactly that construction: the ACCEPT label goes back to being emitted by a
# direct sb_printf instead of through vm_lbl, so the artifact has a label the
# listing does not.
#
# It is not an invented failure. That is precisely how the accept label was
# emitted in this lane's first draft, and tests/codegen/run_ir_listing.sh's
# label-set check caught it on its very first run — which is the argument for
# having written the check rather than trusting the structural argument.
SAB_ID="S41-ir-label-drift"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="irlisting"
SAB_DESC="the accept label is emitted by a direct sb_printf, bypassing vm_lbl, so it never reaches the listing's event stream"
SAB_DOC_FIGURE="tests/codegen/run_ir_listing.sh: the PROGRAM label-set check fails for every pattern"
SAB_COUNT=1
SAB_BEFORE="        vm_lbl(&v, acc, \"the pattern is complete\");"
SAB_AFTER="        sb_printf(v.b, \"%s_L%d: __attribute__((unused));\\\\n\", v.p, acc);  /* SABOTAGE S41 */"
