---
name: compliance-refresh
description: Refresh docs/pcre2_compliance.md the annotated-derivation way — regenerate every derivable fact from the compiler, re-run the independent PCRE2-side survey, and reconcile the keyed hand-written annotations, without ever letting the three components contaminate each other. Use after a module lands, when a PC-2 re-survey fires, when a measurement or K/U-list entry changes a construct's caveat, or when the generated index moves.
---

# Compliance-page refresh (annotated derivation)

Chartered by Frank, 2026-08-21 (thirty-fifth session): the compliance page's
maintenance is a REPEATABLE PROCESS with three components of different
provenance, and the process — not any one refresh — is the deliverable this
skill carries. The failure class it exists to prevent has recurred for real:
hand-written prose rows going stale after waves land (the `\b \B \G` row read
REJECTED for two waves after both had shipped; waves B/D/E each needed row
corrections).

## The three-component model (the load-bearing idea)

`docs/pcre2_compliance.md` mixes three kinds of content, and each has a
DIFFERENT source of truth. Confusing them has cost a lane once already (the
[M6.2] wave E misread; see the page's own "How to read the generated index"
section):

1. **GENERATED FACTS** — derived from the compiler, never hand-edited.
   Source: `build/pcrec --list-syntax` (the registry's status/roadmap/module
   fields; plus the built-status column once the registry_built_status memo's
   implementation lands — docs/design/registry_built_status_memo.md).
   Property: cannot drift from the compiler (SR-4). The checker is
   `tests/registry/compliance_section.py`.
2. **THE INDEPENDENT SURVEY** — the PCRE2-side construct inventory, derived
   from PCRE2's own documentation (pcre2syntax.html; PC-2 is the periodic
   re-survey row). ITS VALUE IS ITS INDEPENDENCE: it answers "what does PCRE2
   have that pcrec's registry doesn't even LIST?", which nothing derived from
   the registry can answer. NEVER generate this half from the registry — a
   construct missing from the registry would silently vanish from the audit,
   certifying completeness from the thing being audited (the
   controls-sharing-a-source failure class, instance list in
   docs/dev/learnings.md §3).
3. **KEYED ANNOTATIONS** — hand-written measurements and judgment, each keyed
   to a construct/row it describes: OK-LIMITED qualifiers (e.g. the exact
   repeat-count narrowing), oracle-divergence notes (the U-list), K-list
   caveats, D26 tier assignments, and the deferral analysis with its revisit
   triggers. Hand-written is correct here — but each annotation must name the
   construct it belongs to, so staleness is detectable ("annotation names a
   construct that moved") instead of silent.

The page is trustworthy because components 1 and 2 are INDEPENDENTLY derived
and held in CHECKED TENSION. Removing the tension by deriving everything from
one source removes the audit, not the staleness.

## The refresh procedure

Run this after: a module lands or a wave changes a construct's shipped
behavior; a PC-2 re-survey; a K/U-list change touching a surveyed construct;
any change to the registry or `--list-syntax` output.

1. **Regenerate component 1.** Rebuild, re-emit the generated section the way
   `tests/registry/compliance_section.py --check` expects (read that script's
   header for the current emit/check invocation), and let the CHECK — not a
   hand-diff — say whether the page's copy matches. Never hand-edit inside
   the generated markers; if the generated content is wrong, the fix is in
   the registry or the dump code, not the page.
2. **Reconcile component 3 against what changed.** For every construct whose
   generated facts moved (new module built, gate opened, diagnostic changed):
   find its annotations and re-verify each against the current tree —
   measurements re-run, never carried forward on faith (a number you did not
   just measure is a number you are quoting). Delete annotations whose
   premise is gone; date-stamp corrections. Grep the PROSE rows for the
   construct too — until the prose-row-to-keyed-annotation migration is
   complete, the prose rows ARE the annotation store and go stale the same
   way.
3. **Re-run component 2 only when PC-2 fires or PCRE2 moves.** The survey
   refresh reads pcre2syntax.html (and the PCRE2 changelog for the delta),
   compares against BOTH the previous survey and the generated index, and
   records new constructs as new rows with a registry disposition question
   for Frank — never by quietly adding registry rows to make the comparison
   clean.
4. **Both-direction check.** After any refresh, run the full registry section
   (`make test-registry` covers compliance_section.py, registry_check, PC-3)
   and read the page top to bottom once — the prose-mangling lesson
   (learnings §"prose that describes code has no test") applies to this file
   more than any other.
5. **Record.** A refresh that changed anything gets a line in the journal
   entry for the session and, if it corrected a stale claim, the stale claim
   is named (what it said, what was true, how long it was wrong) — the
   recurrence record is what justifies this process's cost.

## Status of the migration (update this section as it moves)

- As of 2026-08-21: components 1+2 exist in today's page (generated index +
  hand-written survey/prose rows); component 3 exists only INSIDE the prose
  rows, not yet as keyed annotations. The restructure (migrate ~600 lines of
  prose-row content into construct-keyed annotations rendered by the
  generator, shrink the prose to survey + judgment) is chartered as plan row
  [DOC-DRV]; the built-status column (registry_built_status_memo.md, rulings
  pending) lands first and independently.
- Until [DOC-DRV] lands, step 2's grep-the-prose-rows clause is the live
  discipline.
