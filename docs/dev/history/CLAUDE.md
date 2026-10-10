# docs/dev/history/ — build history moved out of the spec tier

docs/spec/ states contracts and carries no build history (docs/spec/CLAUDE.md;
`make test-spec-history`). When a spec document is cleaned to facts only, the
history it carried — revision notes, rulings, walkbacks, superseded wordings,
dated row notes — comes here, so nothing is lost and nothing here is mistaken
for a promise. Files here are RECORDS: never normative, never cited as the
contract. Created by lane specclean (2026-10-09, `[SPEC-CLEAN]`).

## Files

- `match_api_record.md` — FROZEN. The history `docs/spec/match_api.md`
  carried until its facts-only rewrite: every flagged paragraph of the old
  text, verbatim and in order, each tagged with its old section and line
  range, plus docs/spec/CLAUDE.md's old `match_api.md` entry. The complete
  old text is `git show aee1a570:docs/spec/match_api.md`;
  `studies/specclean/claims.tsv` maps its claims to the new document.
- `registry_record.md` and `table_contract_record.md` — FROZEN. The history
  `docs/spec/registry.md` and `docs/spec/table_contract.md` carried until
  their facts-only rewrite (lane specreg, `[SPEC-CLEAN]`): the flagged
  paragraphs of the old text, verbatim and in order, each tagged with its
  old section and line range. Counts and "was N" narratives in them are as
  of the time written. The complete old texts are
  `git show 43cec6c0:docs/spec/registry.md` and `…table_contract.md`;
  `docs/dev/lanes/specreg_report.md` carries the claims ledgers.
- `limits_record.md` and `cli_record.md` — FROZEN. The complete text
  `docs/spec/limits.md` and `docs/spec/cli.md` carried until their facts-only
  rewrite (lane speclim, `[SPEC-CLEAN]`), moved verbatim. The rewritten specs
  keep the contract-bearing facts; dated narrative, rulings, revision history
  and measurements that the code has since overtaken are only here, and
  counts in them are as of the time written. The same texts are in git at the
  commit before the rewrite; `docs/dev/lanes/speclim_report.md` carries the
  claims ledgers.
- `facts_listing_record.md`, `ir_listing_record.md` and `findings_record.md`
  — FROZEN. The complete text `docs/spec/facts_listing.md`,
  `docs/spec/ir_listing.md` and `docs/spec/findings.md` carried until their
  facts-only rewrite (lane specsmall, `[SPEC-CLEAN]`), moved verbatim. The
  rewritten specs keep the contract-bearing facts; the revision notes, step
  narrative and statements the code has since overtaken (the `prefilter`
  vocabulary was called nine tokens; it is eleven) are only here. The same
  texts are in git at the commit before the rewrite;
  `docs/dev/lanes/specsmall_report.md` carries the claims ledgers.
- `rxt_format_record.md` — FROZEN. The complete text `docs/spec/rxt_format.md`
  carried until its facts-only rewrite (lane specrxt, `[SPEC-CLEAN]`), moved
  verbatim. The rewritten spec keeps the contract-bearing facts; the
  build-step tags, measurements, the "drift found" section and the statements
  the code has since overtaken (the `oracle` engine grammar, the block
  `description` block scalar, `features only` called inert) are only here.
  The same text is `git show eac53111:docs/spec/rxt_format.md`;
  `docs/dev/lanes/specrxt_report.md` carries the claims ledger.
- `abi_changelog.md` — LIVING. The `abi` change log, newest first, one entry
  per bump (D76 addendum [REVW.A1] named its home; it moved here verbatim
  from match_api.md §6). **An `abi` bump adds its entry here in the bump's
  own commit**, beside the spec's `rx_info.abi` sentence (D76/D94's readers).

Maintenance: a future spec cleanup adds its own `<doc>_record.md` here and a
line above.
