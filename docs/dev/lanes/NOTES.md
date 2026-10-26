# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## Moved from CLAUDE.md, 2026-10-22 (4 KB hot-path limit): the full pre-trim text


Purpose: the lanes' own voice. One `<lane>_report.md` (delivery: commits, the
brief's acceptance table filled with MEASURED values, findings) and/or one
`<lane>_log.md` (running log, in order, for the lane's restart) per lane that
chose to keep them, plus lane-owned evidence/instrument files.

## Standing rules

- `BOILERPLATE.md` (2026-09-06, Frank) is the standing rules every lane reads
  FIRST: scope mandate, worktree ritual, box facts, process rules, lifecycle
  policy (NO self-keepalive crons - subagent caches are 5-minute TTL; finish,
  hand back complete, END, never idle). Briefs name only task, tier and
  deliverable and point there. When a rule changes, update BOILERPLATE.md;
  do not grow briefs back.
- `BRIEF_TEMPLATE.md` (2026-10-20) is the manager's field list for every lane
  brief (rulings quoted, id ranges, the owner's BUILD GO or "NO BUILD GO",
  stop rule and premise test, owed-run wording, deliverable and reply size);
  skill `pcrec-manager` section 3 points at it, BOILERPLATE carries the
  matching STOP rule. Point at these two files; never restate them here.
- A lane's report MUST be added to this directory's history index (the
  per-lane entry list, now in the history file) in the SAME change as the
  report (N-1 / D149; applies to pcrec and kit lanes; kit briefs say so).
- `_log.md` and `_report.md` are optional: briefs allow, never require them.
- `<lane>_brief.md` is the MANAGER's artifact, kept only when a lane is
  PARKED mid-flight across a session boundary: the original launch brief
  verbatim (stale sections marked) so a fresh agent can be relaunched onto
  the lane's branch. Delete it when the lane's row completes and merges.
- Lane files are the lane's voice, not the manager's: plan, journal and
  decisions log carry the manager's record; on disagreement the committed
  docs in docs/dev/ win. Historical once the lane is merged; never edited
  afterwards.
- Lane-written files stay inside this directory (evidence dirs, scripts,
  patches); the scope mandate in the root CLAUDE.md applies.

## Files / subdirectories

- `BOILERPLATE.md` — standing rules every lane reads first.
- `BRIEF_TEMPLATE.md` — the manager's brief field list.
- `<lane>_report.md` — delivery report for lane `<lane>` (about 480 exist,
  each described by one entry in the history file's list: tag, date, lane,
  tier, what it delivered and its key findings).
- `<lane>_log.md` — the lane's running log, where kept.
- `<lane>_brief.md` — parked-lane launch brief, where present
  (A `NAME_rulings.md` file is polled by a running lane.)
- `<name>_evidence/`, `grid1/`, `grid2/`, `gridread/`, `costmodel/`,
  `armread/`, `b3b/`, `b4p/`, `m0build/`, `mechpar_chain/`, `origsurvey/`, `pcscope/`,
  `r17b2/`, `regimefacts/`, `rwcorpus/`, `rwquest/`, `rwquest2/`, `sbscope/`,
  `slotarms/` — per-lane instrument/evidence directories (data, drivers,
  logs) cited by the matching report.
- Loose lane artifacts: `*.py`, `*.sh`, `*.c`, `*.patch`, `*.tsv`, `*.out`,
  `*.log`, `*.txt` instruments and data (census scripts, sweeps, movers,
  probes); `I-43_draft.md`, `iface_digest.md`, `mechpar_profile.md`,
  `rel1pre_facts.md`, `tiers88_inbox_draft.md`, `vecspike_reading.md`,
  `w4_facts.md`, `w5_facts.md` — lane-written notes/drafts.

## Pointers

- `docs/dev/lanes/BOILERPLATE.md`, `BRIEF_TEMPLATE.md`; `.claude/skills/pcrec-manager` section 3.
- `docs/dev/plan.md`, `docs/dev/dev_journal.md`, `docs/dev/decisions.md` (the manager's record, which wins on disagreement); `docs/dev/reviews/` (panel reviews lanes cite).

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__lanes.md

## [FINDALL-NEXT] lane iterland: additions carried from lane/itertri (verbatim)

- `i1build_report.md` (+ `i1build_rulings.md`) — [FINDALL-NEXT] I0 + I1 BUILT (2026-10-21, lane i1build, opus; abi 82 -> 83): the `reports_empty` fact, the DFA notempty root, the `mg` line (I0, zero emitted bytes), then `<prefix>_next` over `rx_iter` with `rx_nextfn`/`rx_info.next`, the NOTEMPTY retry (DFA notempty root, VM accept guard), checks hoisted to bind, the residual twins, no batch ABI (ruling); tests/findall/, run_residual_twins.sh, S1297-S1308; validation queued at handoff.
- `i1tri_report.md` — TRIAGE of I1's red `make test` (job 610) (2026-10-21, lane i1tri, opus; continues lane/i1build, abi 83 unchanged): 610 was TRUNCATED (scripts/sectiontimes died on a non-UTF-8 byte, make took SIGPIPE), so compound/partlayout/encoding-checks never reported; fix-by-fix table: stale checks the `__find` split and twins moved (body extractors, M5-SEAM parsers, reseed/anchored/start readers, facts MACHINERY, inline arm B, n1 budget + limits.md), four real I1 defects fixed (utf8 vars resolver before its twin, the setter's non-essential comment, the fold stamp's retry machine, widths.c's shared WCLASS arm), FILEPIN re-pinned, S02/S05 re-anchored; jobs 611-641 queued with their green lines.
- `i1tri2_report.md` — TRIAGE round 2 of I1's red `make test` (job 611) (2026-10-21, lane i1tri2, opus; continues lane/i1build, abi 83 unchanged): eight red sections; three real I1 defects fixed (the part layout's FIND owner bit and the label-table `__find`'s copyable fact; a kept residual's stray static declaration), the rest stale readers of the `__find` split, the twins and round 1's own moves (codegen OS-1/OS-0b, cpset -145, C4 allowlist, pr8, E0 fixture, B0 kept-twin, DD12a(i) twins/forwarders/bind_checks, partlayout writers, startset global.rxt movers); jobs 609/612 queued.
- `i1tri3_report.md` — TRIAGE round 3 of I1's compound-part failures (job 609) (2026-10-21, lane i1tri3, opus; continues lane/i1build, abi 83 unchanged, no C change): B1's hand controller called F's static residuals by their pre-I1 names (a static residual is its twin `<p>__f__next_pos` under F-1; test fix, same root as round 2's fix (c)); round 2's fix (b) judged RIGHT on evidence (F's label table is in its noinline `__f__find`, the `_search` subject copies, and `_next` is a second caller), so `held-compound` is re-pinned as `compound-inline` (P5/P5) with tuning §2.51¶1a and match_api §6.3.11 hunks; test-compound PASS and test-partlayout 49/0 seen; chain re-queued as 613.
- `s1300_report.md` — disposition of I1's UNDETECTED sabotage S1300 (2026-10-21, lane s1300, opus): MISSING WITNESS, not an equivalent plant. findall_iter.md §6.8 names `a\x80a`; cells.tsv never carried a stray continuation byte after a non-empty match. Adds `a\x80a`/`\xc3\xa9\x80a` to the six non-empty utf8 patterns × 3 flag sets (36 cells, libpcre2 the run-time oracle). The clean findall section and the S1300 mech row are queued (622-i1build-findall1300 then 622-i1build-mech1300); verdicts OWED.
- `i2design_report.md` — [FINDALL-NEXT] I2 design note (2026-10-21, lane i2design, opus; design only, from lane/i1build): delivers `docs/design/findall_iter_i2.md`. It designs `<prefix>_next_n` (k full-capture entries; a return below k means ENDED; k calls of `next` by construction; no rx_iter change) and the shared-block `RX_FOREACH` over `rx_info.next_n` (4→64 doubling stack buffer, no allocation, no artifact `.h` needed). It withdraws the internal batch. Its REVISION 2 section (lane i2rev) applies panel r1 (`../reviews/2026-10-21-r1-findall-i2.md`): one body `__one`, no new entry, revision 3's stage numbers kept (this stage is I4), doubling from 1, a rebuilt timing gate, S1309-S1320 with witnesses and reach counts, and Q1-Q4 settled. It also lists five items for the manager.
- `i2build_report.md` — [FINDALL-NEXT] I4 BUILD (2026-10-21, lane i2build, opus; abi 83 -> 84, on lane/i2build from lane/i2design): `<p>__one` (I1's `_next` body) with `_next` and `_next_n` over it, `RX_FOREACH` + `rx_foreach` + `rx_nextnfn` in the shared block, `rx_info.next_n`; spec §3.8.1/§3.8.2; the R1 ruling (the objdump identity of `_next` is unattainable once `_next_n` exists, replaced by a text check, run_one_body.sh); H1-H3 results; an I1 defect the gstart iterator arm found and fixed (a DFA `\G` artifact reported an empty match at n+1 forever); I4 arms in tests/findall (reach floors), encseam, gstart, entry_shape; S1309-S1321; the PARITY_I4 timing cell. make test, mech, census and timing queued (660-663).
- `iteropt_report.md` — [FINDALL-NEXT] per-call overhead of `_next`/`_next_n` (2026-10-22, lane iteropt, opus; folded into abi 84). NULL caps go to the noinline `<p>__one_local`, so the controllers carry no canary (-7 instructions per match). `rx_iter_init` writes every field, so `__enter` is one inline store (-19 per find-all). §3.8¶5 is updated and the dirty arm re-aimed. Causes c/d/e are not fixed (they need a run_one_body re-pin or a layout ruling). The report carries the per-cause instruction table, the 598 predictions and the RX_FOREACH effect.
- `iteropt2_report.md` — [FINDALL-NEXT] causes (c)+(e) of the iterator overhead (2026-10-22, lane iteropt2, opus; folded into abi 84). (c) `__step`/`__one` take a cursor, `_next_n` holds it in locals: I identical, N4/N64/F 3-9% fewer instructions per match on dense cells, N1 +2..+6. (e) three loop variants measured, none adopted (register pressure). run_one_body re-pinned (the I1 text identity retired). Merge into findbench, 599, census and make test are OWED (§5).
- `itertri_report.md` — triage of the red make-test runs of iteropt/iteropt2 (2026-10-22, lane itertri, sonnet): all three reds legitimate moves of the iterator-entry text, no regression; S1321 anchor re-aimed, resource pin 766980, cpset manifest 12 EMITTED_BYTES rows re-recorded. Solo re-runs OWED (report).

- `iterdoc_report.md` — iterator spec fixes from the iterd27 D27 findings (2026-10-22, sonnet): match_api.md §3.1.3¶4a/¶6/¶11a, §3.8¶2a/¶5a/¶6a/¶9, §3.8.2¶5, §4¶9a, §9.3¶4, §9.5¶2-3; spec only.
- `emitbidi_report.md` — [EMIT-BIDI] one C-text escaper (2026-10-25, lane emitbidi, sonnet; abi 84 -> 86, 85 reserved by the kit S3 branch): `pcrec_sb_ctext` (core/sb.c; comment / quoted-comment / string frames from one declared row table) replaces `emit_comment_safe_byte`, `emit_c_string_literal`, `pcrec_sb_cstr`, the map-comment loop and the VM word-bytes loop; the unescaped `${...}` comment echo is fixed; check `tests/codegen/run_ctext_ascii.sh`, sabotages S1620/S1621; validation OWED (job `emitbidi_job`).
- `emitbidifix_report.md` — [EMIT-BIDI] fix round (2026-10-25, lane emitbidifix): triage of job 800 (RED): the new run_ctext_ascii.sh check had its own bug (whole-artifact high-byte grep vs the emitter comment prose).
- `emitbidi2_report.md` — [EMIT-BIDI] second round (2026-10-25, lane emitbidi2): ASCII-only emitter literals (S1622), abi changelog, job file `emitbidi_job`; merged 7234c2e86 by landing lane emitbidiland.
- `scanset_report.md` — [SCANEDGE-SET] scan edge over a byte-class SET (2026-10-26, lane scanset, opus; abi 86 -> 87 provisional): `shaped()` keys a set by its lowest class, `DState.scan_set` + `pcrec_scan_has`; census sections (7)/(8) + `scan_set_check.py`, `tests/classes/scan_set.rxt`, S1633-S1637, S213 re-aimed; `\s+$` 1.17 -> 0.19 ns/B; validation OWED (job `scanset_job`).
