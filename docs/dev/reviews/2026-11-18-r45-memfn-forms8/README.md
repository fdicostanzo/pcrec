# r45 critic drill scripts (memfn-forms8)

The critic's repro scripts and their logs, cited by the review as `work/d1.py` etc. They import a
scratch copy of `memfn/tests/span_forms/cards.py` at 3fd31c86d patched by `critic_cards_patch.diff`
(a TSCALE launch-sigma hook and the "onereg"/"mix" layout models; lane formsfixm took the models and
the hook, as `tscale=`, into cards.py itself). Evidence only; nothing runs them.
