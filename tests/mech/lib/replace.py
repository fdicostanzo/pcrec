#!/usr/bin/env python3
"""tests/mech/lib/replace.py — the ONLY thing that touches a sabotaged file.

Usage: replace.py <target-file> <before-text-file> <after-text-file> <expected-count>

Reads BEFORE and AFTER as raw literal byte strings (no regex, no shell
expansion) and performs a plain str.replace on <target-file>. This exists so
every sabotage in tests/mech/sabotages/ is applied through ONE mechanism that:

  1. FAILS LOUDLY if the anchor text is not present exactly <expected-count>
     times (catches "the doc quoted stale source" before it silently no-ops).
  2. FAILS LOUDLY if BEFORE == AFTER (a sabotage that doesn't change anything
     is a bug in the sabotage definition, not a passing run).
  3. FAILS LOUDLY if, after writing, the AFTER text cannot be found in the
     result (catches a replace that landed somewhere unintended, e.g. AFTER
     text happening to already exist for an unrelated reason).

This is the MECH-2 lesson mechanized: "assert the target text was found and
changed, refuse to continue otherwise", applied per-file rather than trusting
a revert.
"""
import sys


def main():
    if len(sys.argv) != 5:
        print("usage: replace.py <target> <before-file> <after-file> <expected-count>",
              file=sys.stderr)
        sys.exit(2)
    target, before_path, after_path, count_str = sys.argv[1:5]
    try:
        expected = int(count_str)
    except ValueError:
        print(f"bad expected-count {count_str!r}", file=sys.stderr)
        sys.exit(2)

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()
    with open(before_path, "r", encoding="utf-8") as f:
        before = f.read()
    with open(after_path, "r", encoding="utf-8") as f:
        after = f.read()

    if before == after:
        print("SABOTAGE DEFINITION BUG: before-text and after-text are identical",
              file=sys.stderr)
        sys.exit(1)

    actual = content.count(before)
    if actual != expected:
        print(f"ANCHOR MISMATCH in {target}: expected {expected} occurrence(s) "
              f"of the anchor text, found {actual}. The source has drifted "
              f"since this sabotage was written, or the anchor was copied "
              f"wrong. Refusing to apply.", file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(before, after)

    if new_content.count(after) < 1:
        print(f"POST-CHECK FAILED in {target}: after-text not found in the "
              f"result. This should be unreachable if the replace above "
              f"succeeded; refusing to trust the file.", file=sys.stderr)
        sys.exit(1)

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"OK: {target}: replaced {actual} occurrence(s), verified after-text present")


if __name__ == "__main__":
    main()
