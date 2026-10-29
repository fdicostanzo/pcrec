#!/usr/bin/env python3
"""tests/subst/cli_option_census.py -- [M4-SUBST] review CHK-7: every option
`pcrec` documents is refused by `--subst` and by `--emit-support` (subst_api.md
§5¶1, §10¶2), by its PRESENCE, a default value included.

THE POPULATION IS DERIVED, never listed here: every option token of `pcrec
--help` (its two-space-indented first column) plus every `-f`/`-fno-` flag of
`pcrec --list-axes`. What this file holds is how to SPELL each one (VALUES),
and a documented option VALUES does not know fails the run, so a new option
cannot slip past the loop. What the population cannot see: an option the help
text does not document (`--list-analyses`, `--view=` ... are documented
elsewhere); the floor below catches a help text that shrinks.

Per option, with `--subst x` and with `--emit-support`, the refusal must come
from the MODE (its own diagnostic, naming the token or the query), never from
the option parser: a value spelled wrong here would otherwise read as a pass.
Options the subst mode admits (`-p`, `-e`, ...) are held to compile instead.

Prints `FAIL: ...` per failure and `checks passed: N` / `checks failed: M`.
Usage: cli_option_census.py PCREC WORKDIR
"""
import os
import re
import subprocess
import sys

PCREC, WORK = sys.argv[1], sys.argv[2]
FLOOR = 60      # options measured 2026-10-24: 44 from --help, 17+ from --list-axes

# How to spell each documented option: its argv, and its CLASS --
#   opt    an option of a pattern compile: refused by presence, and accepted
#          with --pattern (the positive control)
#   query  a mode or query of its own: refused by the mode's first check
#   admit  admitted by --subst: the subst compile must succeed with it
#   exit   prints and exits 0 before any mode (-h, --version): not probed
VALUES = {
    '--pattern': (['--pattern', 'a'], 'query'),
    '--subst': (None, 'admit'), '--subst-file': (None, 'admit'),
    '--emit-support': (None, 'admit'), '-o': (None, 'admit'),
    '-p': (None, 'admit'), '-e': (['-e', 'utf8'], 'admit'),
    '--encoding': (['--encoding=utf8'], 'admit'),
    '--features': (['--features', 'subst-extended'], 'admit'),
    '-i': (['-i'], 'opt'), '--ucp': (['--ucp'], 'opt'),
    '--emit-main': (['--emit-main'], 'opt'), '--pattern-esc': (['--pattern-esc'], 'opt'),
    '--callout': (['--callout', '1:consume'], 'opt'),
    '--allow-code': (['--allow-code=c'], 'opt'),
    '--code-header': (['--code-header', 'c:x.h'], 'opt'),
    '--no-captures': (['--no-captures'], 'opt'), '--trace': (['--trace'], 'opt'),
    '--emit-ir': (['--emit-ir'], 'query'), '--emit-facts': (['--emit-facts'], 'query'),
    '--engine': (['--engine=auto'], 'opt'), '--memfn': (['--memfn='], 'opt'),
    '--tune': (['--tune=0'], 'opt'), '--part-layout': (['--part-layout=find:auto'], 'opt'),
    '--part-inline-rank': (['--part-inline-rank=none'], 'opt'),
    '--part-residual': (['--part-residual=auto'], 'opt'),
    '--step-budget': (['--step-budget=500000000'], 'opt'),
    '--work-budget': (['--work-budget=1000000000'], 'opt'),
    '--fno-step-budget': (['--fno-step-budget'], 'opt'),
    '--warn-emit-bytes': (['--warn-emit-bytes=0'], 'opt'),
    '--max-emit-code-bytes': (['--max-emit-code-bytes=500000'], 'opt'),
    '--max-emit-bytes': (['--max-emit-bytes=1000000'], 'opt'),
    '--size-cap': (['--size-cap=degrade'], 'opt'),
    '--max-nfa-states': (['--max-nfa-states=131072'], 'opt'),
    '--max-dfa-states-goto': (['--max-dfa-states-goto=10000'], 'opt'),
    '--max-subset-elems': (['--max-subset-elems=48000000'], 'opt'),
    '--max-auto-dfa-elems': (['--max-auto-dfa-elems=30000000'], 'opt'),
    '--backtrack-frames': (['--backtrack-frames=64'], 'opt'),
    '-h': (None, 'exit'), '--help': (None, 'exit'), '--version': (None, 'exit'),
    '--target': (['--target', 's'], 'query'), '--lib-path': (['--lib-path', '.'], 'query'),
    '-I': (['-I', '.'], 'query'),
    '--list-syntax': (['--list-syntax'], 'query'), '--list-definitions': (['--list-definitions'], 'query'),
    '--list-verbs': (['--list-verbs'], 'query'), '--list-families': (['--list-families'], 'query'),
    '--list-axes': (['--list-axes'], 'query'), '--list-limits': (['--list-limits'], 'query'),
    '--list-schema': (['--list-schema'], 'query'), '--explain': (['--explain', 'a'], 'query'),
    '--flavour': (['--flavour', 'pcre2'], 'query'), '--count-groups': (['--count-groups'], 'query'),
    '--list-source': (['--list-source', 'x.rxt'], 'query'),
    '--list-callouts': (['--list-callouts', 'x.rxt'], 'query'),
    '--include-block': (['--include-block', 'x.rxt:1'], 'query'),
    '--probe-ask': (['--probe-ask', 'result', 'a'], 'query'),
}
# The positive control's pattern arguments where `--pattern a` alone is not
# one (the option needs a module, or reads the pattern in its own form).
CONTROL = {'--ucp': ['--features', 'ucp', '--pattern', 'a'],
           '--callout': ['--features', 'callouts', '--pattern', 'a(?C1)b'],
           '--pattern-esc': ['--pattern', '"a"'],
           '--code-header': ['--allow-code=c', '--pattern', 'a']}
SUBST_MODE = ('--subst/--subst-file takes only', '--subst/--subst-file compiles a template')
SUPPORT_MODE = '--emit-support takes no pattern'

passed = failed = 0


def check(ok, what):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print('FAIL: %s' % what)


def run(args):
    r = subprocess.run([PCREC] + args, capture_output=True, timeout=60)
    return r.returncode, r.stderr.decode('latin-1')


def population():
    names = []
    for ln in subprocess.run([PCREC, '--help'], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r'^  (-\S.*?)(?:  |$)', ln)
        for piece in (m.group(1).split(', ') if m else []):
            t = re.match(r'-[-A-Za-z0-9]+', piece.strip())
            if t and t.group(0) not in names:
                names.append(t.group(0))
    axes = subprocess.run([PCREC, '--list-axes'], capture_output=True, text=True).stdout
    for ln in axes.splitlines():
        if ln.startswith('#'):
            continue
        for f in ln.split('\t')[8:11]:
            if re.fullmatch(r'-f[a-z0-9-]+', f) and f not in names:
                names.append(f)
    return names


def main():
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, 'o.c')
    names = population()
    check(len(names) >= FLOOR, 'the option population is %d, below the floor %d' % (len(names), FLOOR))
    for name in names:
        if name.startswith('-f') and name not in VALUES:
            args, cls = [name], 'opt'
        elif name in VALUES:
            args, cls = VALUES[name]
        else:
            check(False, '%s: a documented option this census cannot spell (add it to VALUES)' % name)
            continue
        if cls == 'exit':
            continue
        if cls == 'admit':
            if args:
                rc, err = run(args + ['-p', 's', '-o', out, '--subst', 'x'])
                check(rc == 0, '%s: admitted with --subst, yet refused: %s' % (name, err.strip()[:200]))
            continue
        if cls == 'opt':     # the positive control: the spelling is a valid option
            rc, err = run(args + ['-p', 's', '-o', out] + CONTROL.get(name, ['--pattern', 'a']))
            check(rc == 0, '%s: the census spelling %s does not compile a pattern: %s'
                  % (name, args, err.strip()[:200]))
        rc, err = run(args + ['-p', 's', '-o', out, '--subst', 'x'])
        check(rc != 0 and any(m in err for m in SUBST_MODE)
              and (cls == 'query' or "'%s" % args[0] in err),
              '%s: with --subst: rc %d, %s' % (name, rc, err.strip()[:200]))
        rc, err = run(['--emit-support'] + args + ['-o', out])
        check(rc != 0 and SUPPORT_MODE in err and "'%s" % args[0] in err,
              '%s: with --emit-support: rc %d, %s' % (name, rc, err.strip()[:200]))
    print('options probed: %d (help + axes)' % len(names))
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
