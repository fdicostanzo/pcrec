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
    STATE AT HANDOFF names the last entry it applied (R-n), and the
    manager checks that against the file at acceptance (u25, 2026-11-07,
    reported "empty" over R1 and R2). The rulings file is GITIGNORED, so the lane looks for it with `ls`, not `git status` (land1115d reported "does not exist", 2026-11-15). A change bigger than
    a clarification (new scope, a reversed design) still goes to a FRESH
    lane.

    IDS YOU MAY USE: <abi number, deny/force bit, sabotage S-range from
    worktrees/.mgr/sabotage_ids.txt, and the D/K/I/R numbers from their
    ledgers (decisions.md; memfn/docs/requests.md and responses.md). A
    lane takes no id outside its range.>

    ARCHITECTURE NOTE: <path of the ACCEPTED note (docs/design/<topic>_arch.md) and its critic round, for a
    design or build lane of a feature above the size trigger; "below the trigger: <the one-paragraph form,
    pasted>" otherwise; "none: not a feature" for a fix, a measurement or a doc lane. The lane's design stays
    inside the note's site map and lands the note's first units first ([ARCH-STEP], 2026-11-17).>

    BUILD GO: <the owner's words and date, quoted verbatim>
      -- or --
    NO BUILD GO: design/measure only. (Required for any lane that edits
    src/, cli/, lib/ or memfn/src/. Without a quoted go the lane stops
    and asks; an agreed order is not a go.)

    STOP RULE: if the design of record or a measurement contradicts this
    brief, or a premise below fails, stop and report.
    PREMISE TEST: <the first check the lane makes that the brief's
    premises hold, with the expected result.>
    TODAY NUMBERS (design lanes): every "today the tree does X" number
    the note states carries the exact command that produced it (round
    covcap-r2, 2026-11-15: "`[ab]{1000}` lists 24" was false on one
    compile).

    (A lane that dispatches CLOUD runs proves each one in its report with the matching
    `git ls-remote origin 'refs/heads/cloud/OWNER/*/NAME*'` line; lanecheck knows only box-queue
    keys, so its report says `OWED: none` and names the cloud runs in their own section; 2026-11-16.)
    OWED RUNS: queue every owed stage as a box-queue job (RUNS.md), name
    their keys in STATE AT HANDOFF, run lanecheck, SendMessage, then END.
    Do NOT wait for the jobs or for any notification: a fresh agent reads
    the verdicts. (Lanes idled "waiting for a notification" with owed jobs
    on 2026-11-07.)
    (Never write "LAST act: make test, record its verdict, triage, then
    END": it tells the lane to idle through the run. Wording: memory
    pcrec-subagent-cache-warmth 6a, Frank 2026-09-27.)

    DELIVER: <the checkable block PASTED IN FULL (never only a path; a path-only
    brief read as "create this file" and the lane wrote its own, ic1bland
    2026-10-26), ALSO written by the manager to docs/dev/lanes/<name>_deliver.txt
    (or a path the agent can read): report: PATH; sections: A; B; ..;
    nonempty: all|LIST; cites: RE in X -> Y; commit: yes|no; owed: none|KEY..
    Format: the header of scripts/lanecheck. The agent ends only on
    `scripts/lanecheck` printing `lanecheck: DONE rc=0`; the manager polls
    with `scripts/lanewatch NAME..`. The MANAGER arms `scripts/lanewatch --follow NAME`
    (background) at every lane launch and relaunches it on CAP.>

    DELIVERABLE: <files; docs/dev/lanes/<name>_report.md with a STATE AT
    HANDOFF section>.
    REPLY: <size cap, e.g. under 2k chars>: a SendMessage to the manager,
    complete on its own, then END. Any question the manager asks the lane
    (and any the lane asks back) wants a reply EITHER WAY; never phrase a
    request as "reply only if ..." (Frank 2026-11-07).

TRIAGE LANE (a red, a bug; still NO FIX) additionally reports (D203, 2026-11-24): the defect CLASS; the house rule or
mechanism it breaks (the owning dir's CLAUDE.md) or "none"; a sibling-site COUNT with the grep used; a CLASS-LEVEL fix shape,
checked against the mechanism it relies on (K155: "free it on the error path" had no error path, errors longjmp).

Two more traps (2026-11-15): never run a fix lane in a worktree that queued box jobs build in (cut a new branch/worktree); and a prepare command chained with `&&` after a commit loses the deliver/rulings files when a hook rejects the commit (write them in their own command).
