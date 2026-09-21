# examples/ — worked, tested examples of using pcrec

Runnable examples showing pcrec used the way a real project would use it.
Unlike `studies/` (exploratory measurement work, never built by `make`) and
`docs/`'s prose, everything here is a real, buildable artifact with its own
test section under `tests/examples/`, wired into `make test`.

## Directories

- `makefile/` — [REL-1.10] (D118)'s own test case: `.rxt` sources compiled
  by a plain Makefile build step into a static library a small consumer
  links against. Demonstrates the gcc-shaped CLI (a positional operand is
  an input FILE, several files pool their targets into one `-o DIR` call)
  end to end. `tests/examples/run_examples_tests.sh` copies this directory
  to a scratch dir, builds it against the tree's own `build/pcrec`, and
  checks the archive holds every target's entry symbol and the linked
  consumer runs and matches.

## Conventions

An example here is BUILDABLE and TESTED, not merely illustrative — if it
cannot be copied to a scratch directory and built with a stranger's plain
`make`, it does not belong here. Maintenance: update this file when
directories are added or removed.
