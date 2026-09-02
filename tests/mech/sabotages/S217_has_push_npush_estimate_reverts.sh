# S217 ([CC-CLANG] fix, 2026-09-01) — THE has_push GATE AND THE COUNTER
# RUNG'S UNBOUNDED ARM BOTH REVERT TO THE HISTORICAL DEFECT TOGETHER.
#
# WHAT IT BREAKS, AND WHY BOTH SITES ARE ONE ROW. `src/gen/emit_vm.c`'s fail
# label emits its pop-and-resume dispatch (the ONLY indirect `goto *` on a
# frameless program's remaining path) only when `has_push` is true. Today
# that reads `v.emitted_push` (set by `vm_push_at`, the ONE primitive that
# writes a push, in the SAME call that writes the bytes -- ae3e6ca). This row
# restores the PRE-FIX state at BOTH of the two sites that together produced
# the miscompile the fix note (2026-09-01, journal parts 2-3) records:
#
#   site 1: `has_push` reads the PRE-PASS ESTIMATE `v.npush` again, instead
#           of the emitted-text flag.
#   site 2: the counter rung's UNBOUNDED (`rmax < 0`) arm loses its own
#           special case and falls back through the ternary that computes
#           `nopt = rmax - rmin`, which is NEGATIVE for an unbounded repeat
#           (`rmax == -1`) and SUBTRACTS from `v->npush`.
#
# NEITHER SITE ALONE REPRODUCES THE DEFECT. Site 1 alone leaves `v.npush`
# computed correctly (site 2's fix still in place) and every push-bearing
# program still estimates a positive count, so `has_push` still reads true
# everywhere it should. Site 2 alone drives `v.npush` negative but
# `has_push` still reads the emitted-text flag, which is unaffected by the
# pre-pass's own arithmetic. Only BOTH TOGETHER is the tree main actually
# shipped between `c657ae9` ([CC-CLANG] step 1) and `adc0f5a` (the fix): the
# gate reads the estimate, and the estimate's one unbounded arm cancels a
# replicated body's real pushes to zero or below on `(?:ab|b){8,}+c` (ten
# live `RX_PUSH` sites, `npush` driven non-positive), which omits the fail
# label's dispatch entirely -- nomatch on every subject needing the second
# alternative, against both libpcre2's and python3 `re`'s match.
#
# WHY NOT THE BLUNTER FORM (deleting `v->emitted_push = true;` in
# `vm_push_at`). That single-line edit omits the dispatch from EVERY
# pushing program in the tree -- has_push would read false unconditionally,
# a much larger population than the historical defect ever reached, and it
# would be caught by nearly every backtracking-bearing corpus file at once.
# That is a bigger net for a smaller argument: it certifies "the field is
# read", not "the SPECIFIC unbounded-counter accounting bug that shipped is
# gone". This row instead restores the EXACT two-site historical shape (the
# two edits `adc0f5a` and its own header comment name as the cause), which
# is the tighter claim and the one docs/dev/learnings.md SS3's check-design
# rule asks for: edit the SPECIFIC mechanism, not a stand-in for it. It is
# also the row that would have caught the SHIPPED bug during the window it
# was live -- the blunter form would have too, but by accident rather than
# by aiming at the accounting error.
#
# WHY tests/atomic_groups/run_atomic_diff.sh IS THE ONLY PREDICTED DETECTOR.
# The witness pattern is not invented for this row: `(?:ab|b){8,}+c` is
# already `tests/atomic_groups/run_atomic_diff.sh`'s own `cut:` PATSPEC entry
# (the file this fix's own journal entry names as the sabotage's origin --
# it caught the real bug the day it shipped). Grepped for elsewhere in the
# tree (`grep -rn 'pattern.*|.*{[0-9]+,}+' tests/`), no `.rxt` corpus file
# and no other mech-adjacent driver contains an UNBOUNDED (`{N,}+` or
# `(?>...)+` over an alternation) counter-rung witness at all -- every other
# bounded counter-rung fixture in the tree (e.g. `(?:aa|a){8,12}+ab` in
# `tests/atomic_groups/possessive.rxt`) has `rmax >= 0`, so `nopt` stays
# non-negative there and this row's edit changes nothing on it. That is the
# population this defect needs, and `run_atomic_diff.sh`'s own PATSPEC is
# the only place in the tree carrying it.
#
# PREDICTED DETECTORS, HAND-TRACED (the mech matrix itself is the manager's
# battery under the box hold in force at this row's writing -- the DETECTED
# figure is owed there, S216's own precedent for a row written under a
# hold). `run_atomic_diff.sh`'s §1+§2+§2b subject sweep drives the `cut:
# (?:ab|b){8,}+c` cell on all three arms it builds for every pattern --
# DEFAULT (hybrid), `--engine=vm`, and `-fno-possessify` -- and `vm_cuts`
# for this pattern is `a->u.rep.possessive` (the quantifier's own written
# `+`), which `-fno-possessify` does not clear (that flag denies the LIFT
# for an ATOMIC GROUP's cut, not a directly-possessive quantifier's own
# flag; `vm_cuts(a, under_atomic) == a->u.rep.possessive || under_atomic`).
# So all three arms take the same sabotaged counter-rung arithmetic and are
# predicted to differ from libpcre2 on every subject in the sweep whose
# match requires backtracking into the pattern's SECOND alternative (`b`
# alone, past a failed `ab`) -- the historical fix note's own description of
# the failure population. `corpus`/`harness` are predicted GREEN: no `.rxt`
# file in the tree reaches an unbounded counter-rung alternation body (see
# above), so the whole `.rxt` corpus and every other suite that drives it
# stay untouched by this edit -- the same "answer-identity-preserving
# outside its one witness" shape S216 and S141 both record for a row whose
# population is narrower than its mechanism's file.
SAB_ID="S217-has-push-npush-estimate-reverts"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="atomicdiff"
SAB_DESC="Both halves of the shipped has_push miscompile restored together: (1) the fail label's has_push gate reads the pre-pass ESTIMATE v.npush again instead of v.emitted_push (the emitted-text flag vm_push_at sets); (2) the counter rung's UNBOUNDED (rmax < 0) arm loses its own special case, so npush falls through nopt = rmax - rmin, which is NEGATIVE there and subtracts from the running count. Neither edit alone reproduces the defect -- only together do they reproduce the tree that shipped between c657ae9 and adc0f5a, where (?:ab|b){8,}+c's ten live RX_PUSH sites drive npush non-positive and the fail label's pop-and-resume dispatch is omitted: nomatch on every subject needing the second alternative, against both oracles"
SAB_DOC_FIGURE="docs/dev/dev_journal.md 2026-09-01 parts 2 and 3 (the miscompile's own record, and the two fix commits adc0f5a/ae3e6ca); src/gen/emit_vm.c's own header comments at the emitted_push field (~line 461), the counter-rung's [CC-CLANG fix, 2026-09-01] comment (~line 2615) and the fail label's [CC-CLANG fix, 2026-09-01] comment (~line 9467-9481). HAND-TRACED by lane s217 (2026-09-01) against the box hold in force at write time; the mech matrix's own DETECTED figure, predicted atomicdiff:Nfail (some N>0 on the cut:(?:ab|b){8,}+c cell across the DEFAULT/VM/NOPOSS arms) / corpus:0fail, is owed at the manager's battery run once the hold lifts"
SAB_COUNT=1
SAB_BEFORE='    const bool has_push = v.emitted_push || v.has_linked_calls;'
SAB_AFTER='    /* SABOTAGE S217 site 1/2: has_push reads the pre-pass ESTIMATE again,
     * not the emitted-text flag. */
    const bool has_push = v.npush > 0 || v.has_linked_calls;'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='            v->npush += a->u.rep.rmax < 0 ? 1
                      : cuts ? (nopt >= K ? 1 : nopt)
                             : (nopt >= K ? K + nopt % K : nopt);'
SAB_AFTER2='            /* SABOTAGE S217 site 2/2: the unbounded arm loses its own case and
             * falls through to nopt = rmax - rmin, negative when rmax < 0. */
            v->npush += cuts ? (nopt >= K ? 1 : nopt)
                             : (nopt >= K ? K + nopt % K : nopt);'
