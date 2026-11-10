# scripts index

One line per file under `scripts/` ([DOC-INDEX], D192; docs/design/doc_index_format.md §8.2). Format:
`- <name> <state> — when: <the situation that calls for it>; does: <what it does>. {keywords}`.
States: `live`, `retired` (kept for the record, or deleted; a retired line need not name an existing file).
`<name>` is the path under `scripts/` (`hooks/pre-push` for the hooks). Not listed: `CLAUDE.md`, `NOTES.md`, this
file, and `tests/` plus `hooks/test_*.sh` (self-tests, own CLAUDE.md). Read it with
`scripts/entry NAME` (level 2 adds the script's own header comment), `scripts/entry -g WORD -p scripts`.
`scripts/entry --lint-scripts` (in `make test-doc-lint`) fails on a script with no line, a line with no file,
a missing `when:`/`does:`/`{keywords}`, or a live script with no header comment.

## Process control and run control

- safekill live — when: you must stop any process (a stray suite, a hung run); never `pkill -f`/`pgrep -f`; does: kills the process group and tree of ONE PID and writes an audit line. {kill, stop, pid, process, pkill}
- watchdog live — when: running something that can hang or runaway-allocate (a compiler on a hostile pattern, a generated matcher, a battery); does: wall + tree-RSS + CPU kill with GNU exit codes and one log line (`-m` bare number is BYTES). {timeout, hang, memory, rss, cap, supervise}
- wtprune live — when: removing a delivered lane worktree; never raw `git worktree remove` or `rm -rf`; does: dry run then `--apply`, gated on merged/clean/quiet/no-cwd/no-lock/not-pinned; dirty targets by name via `--apply --force NAME..`. {worktree, remove, prune, cleanup}
- branchprune live — when: deleting a delivered lane branch after wtprune removed its worktree; does: dry run then `--apply` of safe `git branch -d` over protected/kit/checked-out/merged/quiet gates; unmerged only `--archive NAME..`. {branch, delete, prune, merged}
- mk_d27_cell.sh live — when: launching a D27-blinded test author; does: creates the delivery worktree AND a parallel allowlist-filtered non-git cell the author works in (needs an explicit allowlist per call). {d27, blind, cell, worktree, author}
- boxlock live — when: starting anything heavy (make test, a sweep over ~50 compiles, a lane's -j build) and before a hand-run suite; does: the box's one heavy-run lock (`run`, `status`), yields to ready queue jobs, names the holder. {lock, heavy, flock, serialize, status}
- boxqueue live — when: queueing a suite, battery or sweep for the box, or asking what is queued/running; does: the one job queue (`add`, `batch`, `plan`, `status`, `state`, `after`, `retry`, `cancel`), shortest ready run first, dry-runs a job before enqueueing. {queue, job, schedule, heavy, status}
- boxqueue_window live — when: never run by hand; the queue copies it as the placeholder job for an imported bench window; does: holds the box lock while the bench runs its own window and reports RUNNING/DONE through a state file. {bench, window, reservation, placeholder}
- boxqueue.inboxes live — when: pointing the queue at a bench inbox/log root on a new box; does: data file naming the bench inbox the runner imports `.window` files from. {bench, inbox, window, config}
- chainrun live — when: running a multi-stage heavy chain (build, test, strict, ...) with per-stage caps; never hand-write chain.sh; does: runs a stages file (`NAME CLASS CAP COMMAND`), heavy stages under the box lock, DONE line on every ending; `--check` parses only. {chain, stages, pipeline, lift}
- watchrun live — when: polling a lane or background run for liveness; does: zero-model-call watcher that loops on a run's artifacts and exits once with one line when the state is actionable. {watch, poll, liveness, log, stall}
- verdict live — when: reading whether a gate or suite log passed; never grep for FAIL or "sections ran"; does: reads pass/fail from the run's own make `*** [test-X] Error` lines and trailers. {verdict, log, red, green, gate}
- perfrun live — when: running `make test` under a measured parallelism shape ([TT-JTUNE]); does: picks the least-sampled (make -j, PROCS) shape from perfrun.shapes, runs under a cap and appends a ledger row. {parallelism, jobs, tuning, ledger}
- perfrun.shapes live — when: changing the rotation of parallelism shapes perfrun samples; does: data file of `J P` pairs. {shapes, parallelism, config}
- cpusample.sh live — when: a heavy run needs a CPU-utilisation trace or a contamination probe; does: one TSV row per interval (`busy_pct`, `other_trees`) until a stop file exists; `--probe SECS` one reading. {cpu, utilization, contamination, sample}
- sectiontimes live — when: you want per-section wall times of a `make test` run without changing make test; does: reads GNU make `--debug=j` child lines into a per-section time table. {timing, sections, make, wall}
- battery.sh live — when: the merge/close validation chain (test, strict, axes, san, alloc, lint, mech, recidentity) must run as one detached run; does: runs the stages in order, self-logging with a trailer. {battery, full suite, close, validation}
- fullsuite_job.sh live — when: queuing the full suite for a frozen main commit as a box-queue job (D177); does: records `git rev-parse main` once, builds a detached worktree, runs battery.sh with a retained verdict; `--dry-run` is the only safe check. {full suite, queue, battery, frozen commit}
- fullsuite_resume live — when: the owner commands a resume of a red full-suite run ([SUITE-RESUME]); never automatic; does: queues a job calling fullsuite_job.sh `--resume RUNDIR`, refusing before anything queues. {resume, full suite, red}
- queuewatch live — when: watching the whole box queue for events (the standing /pcrec-monitor loops it); does: prints ONE line per queue or CI event from persisted state, then exits; `--no-ci` skips CI. {queue, monitor, event, ci}
- queuemon live — when: the plain-script form of the queue monitor runs ([MON-SCRIPT]); does: loops queuewatch and applies the monitor skill's first-match table, appending one line per event to worktrees/.mgr/monitor.log. {monitor, journal, queue, owner}
- monread live — when: reading the queue monitor's journal for OWNER, or waiting for gate jobs (`monread OWNER --wait`); does: prints the owner's unread lines past its cursor and advances it; reports a dead or stale monitor as PROBLEM. {monitor, cursor, wait, gate, journal}
- monitor_preflight live — when: a /pcrec-monitor session starts; does: checks every tool the monitor needs, one PASS/FAIL line each and a DONE line; changes nothing. {monitor, preflight, tools}
- monitor_rehearsal live — when: rehearsing the monitor skill end to end (a human runs it too); does: builds a scratch queue of simulated full-suite scenarios and compares the monitor's journal; never touches the live queue. {monitor, rehearsal, test mode, scratch}
- session_role live — when: a manager session starts (register main or kit) or a hook must know which manager it serves; does: registers/looks up a session id's role under worktrees/.mgr/roles. {role, main, kit, session, hook}
- lanecheck live — when: an agent finishes and must verify its own deliverable against the brief's DELIVER block; does: form checks of the report and deliver file, writes the sealed `.done` marker, ends on DONE. {lane, deliver, done, report, check}
- lanewatch live — when: checking that agents ended on a passing lanecheck, or following one lane (`--follow NAME`); does: one line per agent with a missing, stale or hand-written `.done`. {lane, watch, done, stopped}
- gestalt live — when: a manager heartbeat wants the box and sessions state; does: one-shot read-only status, only lines whose threshold row holds (load, session, disk, context, ci, queue, docs, and the plan-health rows owner-waits, open, ready-idle, stale, questions, push-owed, prune-owed); `--all` prints every non-empty line. {status, heartbeat, load, disk, context}
- statusline.sh live — when: configuring the Claude Code status line or reading context/usage snapshots; does: renders the project status line and writes the per-session snapshot JSON gestalt reads. {statusline, context, usage}
- tmpdir.sh live — when: a script needs a temp file; source it, never use /tmp; does: defines PCREC_TMPDIR (default /var/tmp/pcrec-<user>) and forces TMPDIR to it. {tmp, tmpdir, scratch, var/tmp}
- test_queuemon.sh live — when: queuemon, monread or hooks/monitor_unread.sh changes; does: offline self-test over a scratch dir with a scripted fake queuewatch. {selftest, queuemon, monread}

## Checkers and document tooling

- Makefile live — when: you want to run a scripts self-test (`make testscripts`, run ON CHANGE, never part of `make test`, D48); does: the scripts/ directory's own make rules for scripts/tests/*.test. {selftest, testscripts, make}
- entry live — when: looking up a ruling, plan row, bug or script by id or word, or choosing work (`--work`); does: levelled read-only accessor (level 0 line, 1 working fields, 2 whole entry), item grep, `--levels`, `--over-cap`, `--lint-scripts`, `--selftest`. {lookup, plan, decisions, index, work, grep}
- doc_profiles.py live — when: adding a tracker file, a level or a profile (decisions, plan, completed, known, upstream, scripts); does: the ONE profile table scripts/entry and the linters read. {profile, table, index, levels}
- plan_lint.py live — when: editing docs/dev/plan.md; does: the plan row-format linter (PL rules, no warnings), plus `--stale` informational report. {plan, lint, rows, format}
- plan_lint.sh live — when: linting the plan from the shell or a hook (`--staged`, `--stale`, `--selftest`, `--rules`); does: runs plan_lint.py with `python3 -I`. {plan, lint, staged}
- doc_census.py live — when: the decisions addendum owner table must be re-derived or checked ([DOC-INDEX] unit 1.0); does: classifies every addendum marker/mention and emits or `--check`s the owner table. {census, addendum, owner, decisions}
- doc_control.py live — when: checking a converted decisions index/details pair against the old file and owner table; does: the per-extent control, clauses (i)-(vi), plants P1-P21 via `--selftest`. {control, extent, conversion, decisions}
- doc_cites.py live — when: a change adds, edits or moves a decisions cite (Dn, Dn addendum K, Dn.aK) or renumbers an addendum, or a decisions split must prove no cite broke ([DOC-INDEX] G4); does: resolves every decisions cite in the tree to owner-table rows, `--inbound ID` lists who cites ID, `--check` fails on a NEW dangling cite or a changed resolution vs the BEFORE baselines, `--selftest` plants. {cites, dangling, inbound, resolver, decisions}
- check_claudemd_size.sh live — when: adding to any CLAUDE.md or before committing one; does: fails a CLAUDE.md over its limit (root 20 KB, others per table); `--all`/`--staged`. {claude.md, size, orientation, cap}
- check_pcre2_note.sh live — when: a pcre2-reader note lands in docs/dev/pcre2_notes/ (D181); does: rejects what a source paste looks like (fences, preprocessor lines, C operator runs, internal identifiers). {pcre2, clean room, note, wall}
- spec_toc.py live — when: a docs/spec/*.md heading changes; does: rebuilds that document's table of contents between its marker comments. {spec, toc, headings}
- m6read_check_sab_anchors.py live — when: sabotage rows or their target files change, as a cheap tripwire beside `make mech`; does: greps that every SAB_BEFORE anchor still occurs in its target. {mech, sabotage, anchor, stale}
- measure.sh live — when: running a design probe from tests/probes/ (D35); does: builds and runs it and archives a stable-named diffable report under docs/measurements/. {probe, measurement, report}
- size_diff live — when: reading how the artifact-size log moved ([ART-SIZE.1b]); does: one summarised report of per-pattern movement between two size TSVs. {artifact size, diff, log}

## Instruments and censuses

- emit_sweep.py live — when: a change claims it moves no emitted byte, or after an emitter refactor ([BSWEEP]); does: compiles the committed population with a baseline and a candidate and compares emitted C byte for byte; `--trace` writes selection traces. {emitter, byte identity, sweep, neutrality}
- trace_diff.py live — when: comparing two emit_sweep.py `--trace` streams ([START-TABLE] C0); does: diffs reference and working selection traces. {trace, diff, selection}
- cls_identity.py live — when: proving a class-lowering change byte-identical across encodings ([CLS-TREE] S3); does: compiles every corpus/bench triple with two binaries and compares the emitted C. {class, encoding, identity, utf8}
- compile_time_census.py live — when: measuring pcrec's compile TIME on the cls_identity population ([OPT-CLOSURE-CTX]); does: child CPU time per triple, two binaries interleaved, plus retry-ladder stamps. {compile time, census, retry, cpu}
- alt_census.py live — when: sizing alternation shapes for the alternation island ([ENG-ISL]); does: counts flat/qualifying alternations, branch widths, trie and mask depth over the corpus and bench patterns. {alternation, census, trie, island}

## Generators

- embed_text.sh live — when: findings or measure-set text must reach libpcrec (`make gen-findings`); does: embeds each file's bytes as a C array with a name index in src/core/findings_store.inc. {embed, findings, generate}
- ksgen.c live — when: a knowledge kind's store text needs its build-time pre-parse table ([KNOW-SRC], `make gen-tables`); does: `ksgen KIND OUT FILE...` writes the C table a library TU compiles in. {generator, knowledge store, embed}

## Hooks

- hooks/no_cd_worktree.sh live — when: a Bash command would `cd` into worktrees/ (the hook blocks it); does: PreToolUse guard, exit 2 with a reason; use `git -C` or absolute paths. {cd, worktree, cwd, hook}
- hooks/no_commit_all.sh live — when: a `git commit -a`/`--all` would sweep another session's edits (the hook blocks it); does: PreToolUse guard; commit named paths. {commit, all, guard, hook}
- hooks/lane_writes_in_worktree.sh live — when: a lane writes to a main-tree path outside worktrees/ (the hook blocks it); does: PreToolUse(Write|Edit) guard, escape via worktrees/.mgr/main_write_ok (manager-written). {lane, write, worktree, hook}
- hooks/no_stale_claudemd.sh live — when: a Read/Write targets an old worktree's docs/ where pre-de-bulk CLAUDE.md files would be injected; does: PreToolUse guard (exit 2). {claude.md, stale, injection, hook}
- hooks/pcre2_ref_guard.sh live — when: any tool touches the pinned PCRE2 source copy (D181); does: lets only agent type pcre2-reader read it, blocks everything else, fails closed. {pcre2, clean room, reader, hook}
- hooks/monitor_unread.sh live — when: a manager session starts or prompts; does: SessionStart/UserPromptSubmit hook showing that manager's unread queuemon lines once. {monitor, unread, hook, context}
- hooks/post_compact.sh live — when: a session has just compacted; does: SessionStart(compact) hook re-injecting the manager's durable state (owner view, wake file). {compact, wake, owner, hook}
- hooks/pre-commit live — when: committing with hooks installed (`make hooks HOOKS=pre-commit`); does: opt-in gate that lints the plan when staged and runs the spec-citation checks. {commit, plan lint, spec, hook}
- hooks/pre-push live — when: pushing with hooks installed; does: opt-in gate that runs `make test` before the push leaves the machine ([TT-1]). {push, make test, hook}
- hooks/pre-push-light live — when: pushing with the light gate installed; does: about a minute of cheap whole-tree checks (plan lint with PL14 scan, the tree-wide spec scan, strict: whole tree compiles clean with -Werror -Wshadow; the kit's target table check passes) that otherwise only run in `make test` or CI. {push, light, gate, hook}

## Retired

- m6read_rename_emitted.py retired — when: only to read how the [M6-READ] emitted-identifier rename was done; does: rewrote identifiers inside C string literals only, leaving emitter locals untouched. {m6read, rename, one-shot}
- pcrec_analyze.py retired — when: never; deleted in [FINDINGS] B6 (b8ae03901) in favour of the separate `analyze/` binary; does: was the Python analyzer prototype. {analyze, findings, deleted}
