# Lane substr4b report (2026-10-22): the subst R4 light panel applied to the design

**Scope.** Design and draft spec only; nothing under `src/`, `cli/`, `lib/` or
`tests/` changed. Worktree `worktrees/subst`, branch `lane/subst`, from
7cea1fcb6. Rulings applied through R8 (`subst_rulings.md`, the last entry).

**Delivered.**
- `docs/design/replace_design.md`: REVISION 4a. New §R4.15 (finding → where
  table); in-place edits to §R4.2, §R4.4 (rewritten), §R4.5, §R4.7, §R4.9,
  §R4.10, §R4.12, §R4.13 and §R4.14, each marked `[R4a, id]`.
- `docs/design/subst_api_r4_draft.md`: the case state table (§2¶13), the
  ill-formed-UTF-8 rule (§2¶14a), the widened escape refusal (§2¶10, §2¶12),
  the check and context setup moved inline and taking `rx_info` and the map
  (§1¶1, §3¶8-¶12, §7¶3-¶4), the per-render re-assert (§4¶10-¶14), the
  sentinel (§4¶9), the bound (§4¶22), the recipes rewritten under one error
  rule (§6), no-overlap (§7¶1a), §9 rows 16/19/20, the support unit's content
  id and static mode (§10).
- `docs/dev/reviews/2026-10-22-r2-subst-r4-panel.md`: the panel record.
- `docs/dev/upstream_issues.md`: U22 (libpcre2 10.46 case-forcing segfault
  and read-past over ill-formed UTF-8). U21 is taken by lane corefix.

**Probes (libpcre2-8 10.46, ctypes, read-only, scripts on stdin).** The
4-rule case machine: 16 named cells plus 3,000 random cells, 0 mismatches.
Single-digit `\1`-`\9`: never group-count dependent (narrowing C1-3's
"refuse those too if so": they stay accepted). Every `\[1-9]\d+`: group-count
dependent. The segfaults reproduced (exit 139) and the read-past. Constant
growth under `\U`/`\L`, the `\Q` conditional cells and the −55 NOGROUP
equivalent confirmed. Details: the review record.

**Evidence that overturned or narrowed a disposition.**
- C1-3: single digits are NOT refused (probe).
- Family (e): cli.md has no emit-mode table; `--emit-support` becomes its own
  subsection naming its emit siblings.
- Q3 adoption: `rx_subst_ctx_init` is inline too (C2 listed it as an
  optional helper), since it runs the check and the recipes' setup must need
  no support unit for "a plain template is one `.c`" to hold.

**Validation.** `make test-plan-lint test-spec-history` on the worktree:
plan-lint green; spec-history RED on one pre-existing dangling cite
unrelated to this lane (`tests/compound/CLAUDE.md` cites a paragraph 8 of
measures.md section 5 that does not exist;
neither file touched here). Log: `worktrees/subst/build/r4b/lint.log`.

**Not committed.** `docs/dev/artifact_size_log.tsv` was already modified in
the worktree before this lane and is left as found.
