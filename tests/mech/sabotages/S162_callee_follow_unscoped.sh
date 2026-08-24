# S162 ([DD-14] wave B+C, design SS9.3 S-SR16) -- THE CALLEE'S FOLLOW IS
# SCOPED.
#
# THE RULE (design SS5.4): a callee body is emitted with `v->fmin` and
# `v->fdyn` ZEROED, and restored on every return path. `vm_atomic` and
# `vm_look` carry the same two lines, and the REASON here is a third one --
# which is the part a reader is most likely to get wrong, because the code
# looks identical at all three sites:
#
#     vm_atomic   the CUT. The group matches its body's own FIRST success, so
#                 the choice must be made without peeking at the follow.
#     vm_look     the OVERLAP. A lookahead's follow starts at the assertion's
#                 ENTRY position, so body + follow DOUBLE-COUNTS the same bytes.
#     a callee    the follow is UNKNOWN. A shared body has MANY CALLERS with
#                 different follows, and a rung bound baked from one caller's
#                 follow is wrong for every other.
#
# ONLY THE THIRD REASON SURVIVES A SPLICE, which is why it matters that it is
# stated separately: wave G will inline eligible call sites, and an implementer
# who read this scoping as the CUT's or the OVERLAP's would delete it there.
#
# THE DETECTOR IS A TWO-CALL-SITE CELL AND NOTHING ELSE CAN SEE IT. With one
# call site the baked bound is that site's own and the artifact is CORRECT --
# so a single-call-site corpus goes green on this compiler however many
# subjects it sweeps. Design SS9.3 says so, and it is the same shape as the
# ANCHOR warning that row carries: `v->fmin = 0; v->fdyn = NULL;` is a
# two-line idiom shared with `vm_atomic`, so an anchor on those two lines
# matches three times and `replace.py` refuses on the count. This
# implementation avoids that by passing the zeroes as ARGUMENTS to
# `vm_emit_fd`.
#
# **THE FIRST VERSION OF THIS SABOTAGE WAS A NO-OP AND THE MATRIX SAID SO.**
# It passed `v->fmin` where the region passes 0 -- and scored UNDETECTED at
# corpus 0fail/306pass, because **`v->fmin` IS ALREADY 0 when `vm_region`
# runs**: `vm_emit_f` saves and restores it around every node, so by the time
# the main-body walk returns the accumulator is back at the root's own value,
# which is 0 (nothing follows the whole pattern). The sabotage substituted
# zero for zero. That is a finding about the ROW, and it is this project's own
# "prove your instrument is live before trusting a negative result".
#
# THE CORRECTED SABOTAGE CAPTURES A REAL CALLER'S FOLLOW AND HANDS IT TO THE
# REGION, which is what "the shared body inherits one caller's follow" has to
# mean. It is TWO SITES: the first call site records `v->fmin` at the moment
# it is emitted (a file-static, which is exactly the kind of thing the shipped
# emitter may not have and a sabotage may), and the region reads it. On
# `^(a+)x(?1)y(?1)zzzz$` the two call sites have follows of 6 and 4, so a
# region built from the first loses the matches the second needs.
SAB_ID="S162-callee-follow-unscoped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="the callee region is emitted with the CALL SITE's follow instead of a ZEROED one, so a shared body gets one caller's MRL prune bound baked in as a literal and every OTHER caller loses matches"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR16): a shared callee gets ONE caller's prune bound baked in and THE OTHER CALLER LOSES MATCHES -- a two-call-site cell, which no single-call-site cell can catch. run_recursion_diff.sh's 5.2 clobber row (^(?:(?<g>x|xy)){0}(?&g)(?&g)y\$) is a two-site shape and the corpus carries more."
SAB_COUNT=1
SAB_BEFORE='static void vm_call(Vm *v, int entry, const Ast *a, int next)
{
    vm_charge(v);'
SAB_AFTER='/* SABOTAGE S162: one caller'"'"'s follow, captured and handed to the region. */
static long long sab_first_fmin = 0;
static int sab_seen_call = 0;

static void vm_call(Vm *v, int entry, const Ast *a, int next)
{
    vm_charge(v);
    if (!sab_seen_call) { sab_seen_call = 1; sab_first_fmin = v->fmin; }'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='    vm_emit_fd(v, v->rgn_lbl[i], body, v->rgn_exit[i], 0, NULL);'
SAB_AFTER2='    vm_emit_fd(v, v->rgn_lbl[i], body, v->rgn_exit[i], sab_first_fmin, NULL);   /* SABOTAGE S162 */'
