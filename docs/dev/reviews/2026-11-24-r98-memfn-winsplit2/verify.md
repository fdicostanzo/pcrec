# r98 verification (coordinator, inline: every claim checked is a quote or a one-call read)

- V1 READY-1: HOLDS. Makefile `strict:` recipe ends `@bash memfn/tests/check_targets.sh >/dev/null || { ...; exit 1; }`; the review build log printed the targets-check MISMATCH lines on this Mac (warning under `make`).
- V2 READY-3: HOLDS. run_g2_win.sh (plantcheck 8bd727eab) `if [ -z "${G2W_TRACE:-}" ]; then ... v_section` on the plain run; v_section runs g2_vspan.py, which `bad("unit: the host cannot run the x86-64-v3 text (a skip is not a pass)")` (g2_vspan.py :403, :725). run_g2_pres.sh `host_has()` tests /proc/cpuinfo for x86-64-v3 only, `*) return 0`, with TARGETS="x86-64-v3 x86-64 generic". run_g2.sh: no `--plant` option (grep: only comment hits).
- V3 READY-13: HOLDS. binders.py :27 `CHANGED = {'window.c', 'presence.c', 'compose.c', 'finder.c', 'ofsskip.c', 'precheck.c', ...}` (B's names).
- V4 READY-7 / FIXIND-3: HOLDS. run_link_checks.sh :171 "no row in PROVENANCE.md", :177 "a PROVENANCE.md row names a file that does not exist"; PROVENANCE.md row 54 is `src/window.c`; binders_tip_pc.txt homes mech S3252 and census `decide` at window_decide.c.
- V5 FIXIND-1: HOLDS. decider_census.py :458 and :479 `open(os.path.join(t, "src", "window.c"), "a")` (append, creates); :368 `open(path)` read in the `plant()` helper (the FileNotFoundError the note measured).
- V6 READY-10: HOLDS. binders_tip_pc.txt `g2 S1403 memfn/tests/run_g2_win.sh:170 OK kit_pick.c window.c`; §8.1 U3 does not name S1403.
- V7 READY-12 correction: HOLDS. `WF_SPAN_HEAD = 64` is window.c :1493 at B.
- V8 READY-11: PARTLY (as SUSPECTED): run_purity_reach.sh :71 inserts before `static const wf_arow wf_arows[] = {`, :75 compiles `$p/window.c` to `window.o`; the per-commit anchor is unstated in §7.4 (holds); whether a stated "include window.h" breaks U1-U3 depends on the U1 text not yet written.
- V9 READY-6: HOLDS. `make test-memfn-stamps` = `bash tests/memfn/run_libc_census.sh`; that script names none of MF_SITE_ABI / MF_CLASS_V / MF_VOCAB (grep 0).
- V10 FIXIND-11: HOLDS. plan.md [SP1D-KITSPLIT-SEAMS] status (origin/main 4d26eef02): "seam facts only: the rates are host-mutable and the trace names no rules version. The position-primitives half is OVERTAKEN by [KIT-WINSPLIT]"; no kit_run_set seam fact. r95 SLOT-4 quotes the earlier status naming "kit_mass and kit_run_set sit in presence.c".
- Not re-verified (critic probes with outputs in their dirs, internally consistent, design-only effect): READY-2's 28-pattern w32 population and set-aside probe; READY-5's --plant-check 33 -> 4 bad mirror; READY-6's nm +82/-3; READY-12's U4 separability compile; FIXIND-13's kitgraph spec runs; FIXIND-8's pure-cut census.
VERIFY COMPLETE
