# Lane brief template — the manager fills every field

Every lane brief starts with a ONE-LINE TITLE, then the BOILERPLATE line
(skill §3), then the fields below. The title line is what the owner sees
in the agent list when the UI shows a prompt's first line, so it names the
lane, its tier and its task in under ~70 characters, the same words as the
Agent call's `name` and `description` (owner, 2026-10-20: "consistent
subagent titles"). The brief then carries the fields below; the standing rules live in BOILERPLATE.md and are
not restated. The template exists because the brief-writing step, not the
lane, was the root cause of recurring failures (idle-inviting wording,
rulings sent after the brief, colliding ids, build lanes launched without
the owner's go); each rule already sat in a memory file and was still
broken (docs/dev/devmethods/apply_here.md section 1, owner's go 2026-10-20).
A field with nothing to say is written "none", never dropped.

    LANE <name> (<tier>): <task in a few words>
    Read docs/dev/lanes/BOILERPLATE.md FIRST and follow it.
    Scope: <restated mandate>. Worktree: <path> (branch lane/<name>).

    TASK: <one paragraph>.  TIER: <sonnet | opus>.
    INPUTS: <pointers: files, design notes, the prior lane's report>.

    RULINGS ALREADY MADE: <every ruling bearing on the task, quoted
    verbatim where short, with decision id and date. Settle scope before
    briefing: a running lane misses addenda; a scope change goes to a
    FRESH follow-up lane.>

    RULINGS FILE: worktrees/<name>/docs/dev/lanes/<name>_rulings.md (in
    the lane's OWN worktree; created empty by the manager, appended by the
    manager only). Later rulings and scope clarifications travel HERE, not
    by message (a busy lane reads no message until it idles). The lane
    re-reads it at every CHECKPOINT: before each commit, before launching
    any run over ~2 min, and before writing its report; the report's
    STATE AT HANDOFF names the last entry it applied. A change bigger than
    a clarification (new scope, a reversed design) still goes to a FRESH
    lane.

    IDS YOU MAY USE: <abi number, deny/force bit, sabotage S-range from
    worktrees/.mgr/sabotage_ids.txt, and the D/K/I/R numbers from their
    ledgers (decisions.md; memfn/docs/requests.md and responses.md). A
    lane takes no id outside its range.>

    BUILD GO: <the owner's words and date, quoted verbatim>
      -- or --
    NO BUILD GO: design/measure only. (Required for any lane that edits
    src/, cli/, lib/ or memfn/src/. Without a quoted go the lane stops
    and asks; an agreed order is not a go.)

    STOP RULE: if the design of record or a measurement contradicts this
    brief, or a premise below fails, stop and report.
    PREMISE TEST: <the first check the lane makes that the brief's
    premises hold, with the expected result.>

    OWED RUNS: commit the report with a STATE AT HANDOFF section (logs,
    completion lines, owed stages), launch the remaining chain DETACHED
    (chain script runs every owed stage including make test), then END. A
    fresh agent reads the verdicts.
    (Never write "LAST act: make test, record its verdict, triage, then
    END": it tells the lane to idle through the run. Wording: memory
    pcrec-subagent-cache-warmth 6a, Frank 2026-09-27.)

    DELIVERABLE: <files; docs/dev/lanes/<name>_report.md with a STATE AT
    HANDOFF section>.
    REPLY: <size cap, e.g. under 2k chars>: a SendMessage to the manager,
    complete on its own, then END.
