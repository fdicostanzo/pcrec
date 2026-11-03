# g2seg report

Cause: memfn/tests/g2/g2_gen.c: `free_site()` freed a site's arrays but the
file-global `cur_site` (read by the kit hooks `term_of`/`h_member`, line ~546)
kept pointing at it. The refusal controls (`mm_renders` from `mm_refusals`,
~3709/3821) call `pcrec_mf_use` with `h_member` and no site of their own, so
`term_of` read `cur_site->d.npred` / `preds[p]` from freed memory. Whether that
faulted depended on the allocator/ASLR state, hence the nondeterminism (the
program is the same with the fixed seed). Test-program bug only; no kit
(memfn/src) or emitter byte involved.

Fix: `free_site` clears `cur_site` when it equals the freed site (declaration
of `cur_site` moved just above `free_site`). `term_of` already returns NULL
for no site, and `h_member` already renders the G2_BAD_MEMBER_TERM text then.

Ran (light, no suites):
- plain build, seed 20261005: rc 0 (2 s) before the fix too (fault is state-dependent).
- ASan+UBSan build BEFORE the fix: heap-use-after-free at g2_gen.c:546 term_of
  <- h_member:605 <- member_test generic.c:137 <- mm_renders:3709 <- mm_refusals:3821;
  freed by free_site:412, allocated by alloc_preds:404. (the plant: the report itself)
- ASan+UBSan AFTER the fix, detect_leaks=0: rc 0, empty stderr.
  (With leaks on it reports only the generator's deliberate never-freed arena/strdups.)
- valgrind -q on the fixed plain build: clean, rc 0.
- `make strict`: clean.

OWED: run_g2.sh section 4 not run in isolation (needs the mftrace lib and the
whole G2 pass; over the light budget). The main manager's next test-memfn-g2 run
covers it. Other uses of cur_site after a free_site on a stack site (g2250 `cur_site=&g`)
are now cleared by the same hook only when freed via free_site; not otherwise audited.
