# s30afix report

## Summary
rows_check §S no longer dereferences commit 067aca4df. It reads each RULING row's quote from the working-tree file the row names (memfn/docs/responses.md, which lane/memfn-k1107's merge put in this tree). Closes s30a Deviation 6.

## The change
- tests/memfn/rows_check.py §S: opens root/PATH as a file; unreadable file or absent quote is red. The row regex still requires a 7-40 hex provenance token, never looked up. Header comment updated.
- tests/memfn/stream_support.tsv: header/columns text (PATH PROVENANCE); rows unchanged.
- memfn/src/window.c wf_support comment and plan_frame.md §2.5.2 sentence: mechanism wording only.

## Plants (deleted and invented lines)
Scratch: /var/tmp/pcrec-pcrec/scratch/memfn/s30afix. Plants use STREAM_SUPPORT_TSV (existing override) with run_rows.sh.
- Unplanted: exit 0, 243 passed, 0 failed.
- (a) quote deleted from a scratch copy of responses.md, pin rows pointed at that copy by absolute path: exit 1, LIBC and LIBC_BACK red.
- (b) invented RULING row (WALK, quote not in file): exit 1, WALK red.
- (c) row naming a missing file: exit 1, LIBC and LIBC_BACK red "not readable".

## Checks run
run_rows.sh (rows_check §R and §S) green as above; nice make strict exit 0.

## Charter-vs-committed checklist
- read from working tree, quoted verbatim, no sha lookup: done
- provenance column keeps ledger and commit: done
- fail closed on absent quote and missing file: done, planted
- window.c :2023 and plan_frame.md only as far as mechanism: done
- plants both ways with commands and exit codes: done
- rows_check and make strict: done
