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
   fields, plus the `built` column — LANDED, D65,
   docs/design/registry_built_status_memo.md). Property: cannot drift from
   the compiler (SR-4). The checker is
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
   construct that moved") instead of silent. LANDED as
   `docs/pcre2_compliance_annotations.txt` ([DOC-DRV], 2026-08-21; see
   "Status of the migration" below): the checker is
   `tests/registry/compliance_section.py --check-annotations`.

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
   find its annotation by KEY in `docs/pcre2_compliance_annotations.txt`
   (the construct's `syntax` for a registry-backed key; grep the section's
   own material for a `base:` key covering several bundled spellings — see
   that file's own header) and re-verify it against the current tree —
   measurements re-run, never carried forward on faith (a number you did
   not just measure is a number you are quoting). Delete annotations whose
   premise is gone; date-stamp corrections. Then run
   `tests/registry/compliance_section.py --write-annotations` to render
   the edit back into the page, and `--check-annotations` to confirm no
   key went stale in the process (a construct removed or renamed from the
   registry in the same change orphans its annotation, and this is the
   check that catches it — the `docs/pcre2_compliance.md` survey table's
   own `syntax | status | becomes` row still needs its own hand edit
   separately, since that half is never generated).
3. **Re-run component 2 only when PC-2 fires or PCRE2 moves.** The survey
   refresh reads pcre2syntax.html (and the PCRE2 changelog for the delta),
   compares against BOTH the previous survey and the generated index, and
   records new constructs as new rows with a registry disposition question
   for Frank — never by quietly adding registry rows to make the comparison
   clean.
4. **Both-direction check.** After any refresh, run the full registry section
   (`make test-registry` covers compliance_section.py — `--check`,
   `--names`, `--check-annotations` and `--tension` — plus registry_check
   and PC-3) and read the page top to bottom once — the prose-mangling lesson
   (learnings §"prose that describes code has no test") applies to this file
   more than any other.
5. **Record.** A refresh that changed anything gets a line in the journal
   entry for the session and, if it corrected a stale claim, the stale claim
   is named (what it said, what was true, how long it was wrong) — the
   recurrence record is what justifies this process's cost.

## Status of the migration (update this section as it moves)

- **LANDED, 2026-08-21 ([DOC-DRV]).** All three components now exist as
  designed: component 1 (generated construct index) unchanged from SR-4;
  component 2 (the survey) is every section's `syntax | status | becomes`
  table, hand-written, notes column dropped; component 3 (keyed
  annotations) lives in `docs/pcre2_compliance_annotations.txt` — 90
  records (38 keyed to a live registry `syntax`, 52 `base:`-keyed for
  base-tier/cross-cutting material) migrated from the prose rows' former
  notes columns and from three section-level analysis blocks (the
  Unicode-properties K16 byte census, the option-run doorway ordering
  deep-dive, the backtracking-verbs Q1/K15/K14 intro material) — and
  renders back into the page as one `<!-- BEGIN GENERATED ANNOTATIONS:
  <slug> -->` block per section.
- `tests/registry/compliance_section.py` gained `--check-annotations` /
  `--write-annotations` (component 3's drift detector: a stale key or a
  page-vs-store render mismatch fails `make test` naming it) and
  `--tension` (the checked-tension report between components 1 and 2,
  both directions, informational by design). All wired into
  `tests/registry/run_registry_tests.sh`.
- Step 2's grep-the-prose-rows clause is RETIRED: annotations are now
  found by their key, not by grepping prose, and a construct whose
  generated facts move is exactly what `--check-annotations` catches if
  its annotation goes unreconciled.
- Residual, recorded rather than silently absorbed: three prose rows'
  original content was ambiguous enough at migration time to warrant a
  documented judgment call rather than a literal split (bundling several
  related spellings — e.g. `\d \D \s \S \w \W \h \H \V \N` — under one
  representative registry key); see the lane's hand-back migration
  manifest for the full row-by-row disposition. No row was left
  unclassified (disposition ASK): every prose row's content is now either
  an annotation, kept in the survey table, or logged as dropped-as-
  derivable/dropped-trivial.
