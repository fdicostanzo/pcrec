# VERIFY brief: critic round vmcons3

Read /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/COMMON.md first: its scope mandate, box rules (no compiles after
18:45), denylist and review tree bind you too (you are the verifier, read-only; never run make or suites).

Inputs: the two critic files /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/sound/sound.md and
/var/tmp/pcrec-pcrec/scratch/crit-vmcons3/fixind/fixind.md (and their scratch artifacts beside them, which you may
read but must NOT trust: rebuild every answer-level twin from YOUR OWN emission of the review tree's build).

For each finding below, re-check it independently and write a verdict: HOLDS / REFUTED / PARTLY / not verified (why).
- Answer-level twins (rule-as-written, for stage (c)): SOUND-3 (C8 twin with a CLEAN kit-window slot write),
  SOUND-6 (stride-2 span, F = last position reading), SOUND-8 (C6 with stale RESTORE ordinals). Re-emit base,
  re-make the twin edit yourself, compile, run every subject, compare rc + every capture span, and run libpcre2.
  Also check the ARGUMENT: is the twin's reading of the rule one the design text actually admits?
- Structural claims, by quoting the cited review-tree lines and the design text (snapshot
  subject_vmcons3_report.md) and, where named, a probe: SOUND-1/FIX-3 (two templates, same bytes), SOUND-2
  (render-time text carries the \x01q placeholder: internal.h + compile.c lines; is the lexer necessarily
  run before the rewrite?), SOUND-4 (macro exits in RX_TRAIL/RX_PUSH/RX_CALL; CALLOUT consume edge),
  SOUND-5 (vm_cls_respell truncate-regrow after the walk; nested builders), SOUND-7 (uncut vs text offsets;
  re-run the slice), FIX-1 (vm_set bumps nset/emitted_set for snapshots/restores; margin counts them; the
  checkpoint exists only because of snapshots in the witness), FIX-2 (program_bytes/entry knee/emitted_set
  move with a DELETE), FIX-4 (registry writers run after the walk: emit order lines; memfn.h lines),
  FIX-5 (mf_result carries no helper names/effects), FIX-7 (memfn axis rows in --list-axes; DELIVER SETs only
  reachable via .rxt composition), FIX-9 (call_top pop before the return label).
- Skip FIX-6, FIX-8, FIX-10, FIX-11, FIX-12 (cost/check-design/doc/tail; judgment, not verification) except a
  one-line sanity note if a cited line is wrong.

Keep compiles under 30 total, one gcc at a time, generated matchers under scripts/watchdog.

Output: CREATE /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/verify.md (it does not exist yet) and write it
INCREMENTALLY, one `## <ID>` section per finding (verdict, what you ran, observed), then `## STATE AT HANDOFF`
(STATE: complete, OWED: none) and a final line `VERIFY COMPLETE`. Scratch artifacts under
/var/tmp/pcrec-pcrec/scratch/crit-vmcons3/verify/.
DELIVER file: /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/verify/verify_deliver.txt. When complete run
`/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/verify/verify_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons3 verify`
until `lanecheck: DONE rc=0`, then END. Final reply at most 100 words.
