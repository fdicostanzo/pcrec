# Release checklist: a move of the bare default or of a moving family name

DRAFT (lane famdef, 2026-11-10; from gradthink_report.md section 5, D37 addendum 2026-11-06). Run ONCE over the
whole set at each move; the record goes in the move's announcement. S = a script produces it, M = judgment.

1. **Membership** (S). `build/pcrec --list-syntax` module column for every module in the set; each module's rows
   all non-`unbuilt` except any the set explicitly excludes; the set's expanded list equals the stamp;
   `basicN <= extendedN <= pcre2-N`; every earlier frozen member byte-identical to its committed row.
2. **Per-construct differential coverage table** (S table, M verdict). For every registry row in the set's modules,
   the libpcre2 comparison that exercises it (script and cell count) or NONE; each NONE fixed or listed as a
   documented divergence. Quoting and named-groups: `tests/families/run_quoting_diff.sh`, `run_named_diff.sh`.
3. **Set-alphabet campaign** (S run, M triage). `tests/fuzz/fuzz.py --set extended`, fixed seeds, zero content
   divergences or each one triaged.
4. **Open wrong-answer entries** (M). Every OPEN known_issues entry that is a wrong answer on a construct in the
   set, ruled "fix first" or "accept as documented divergence" (K74 at the first move).
5. **Refusal wording inside the set** (S). `reject` table and `RS_REJECTED` identity green; a promised-but-unbuilt
   construct says "not implemented yet", never "requires module".
6. **Before/after of what a bare compile newly accepts or changes** (S). The bench 392, the `.rxt` corpus and the
   reject table compiled under the old and new default and diffed: zero newly refused, zero same-pattern
   different-match.
7. **Stamp and spec** (S). abi bump ritual if the stamp text moved (D76/D94); `docs/spec/` hunk for the default;
   `docs/guide/` pointer; `make test-codegen`.
8. **Full gate on the frozen commit** (S). `make test` and the full battery green on the commit the move names.
9. **Announcement** (M). The version boundary, the new frozen name, the opt-out (`--features std1` or the old
   frozen name), and the item 2/4 divergence list in plain words.
