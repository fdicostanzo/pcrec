"""C17's dynamic half: the corpus-pass census ([MEMFN], integration.md
§R4.3.4 rule 2; R4c, Q3).

RULE 2: a site reaches the kit (`mf_define` / `mf_emit`) with no `delegated`
manifest row. The site is identified by the pcrec FUNCTION that makes the call
(a manifest row names its emitters and companions; after a step's REPLACE the
emitters column names the pcrec site builders, Q4), and the calls are COUNTED
over a corpus compile pass:

  1. static discovery (`find_callers`): every `mf_define(` / `mf_emit(` call
     under src/, attributed to its enclosing function. This is the key the
     rev-3 text got wrong (`mf_emit_site(` names nothing in the API);
  2. a TRACED build (`build_traced`): the caller files are recompiled with a
     shim that logs (kind, file, function) before forwarding to the kit, then
     relinked over a copy of build/libpcrec.a. The shim is this check's own
     (never src/'s), so pcrec grows no tracing hook;
  3. the corpus pass (`corpus_patterns`, `run_corpus`): the patterns of the
     tests' .rxt files, deterministically sampled, compiled by the traced
     binary; the trace file gives the sites rendered per compile;
  4. the verdict (`verdict`): every function seen calling the kit must be
     named by a `delegated` row (an unlisted site), and every `delegated`
     row must be REACHED by at least one call over the corpus (a delegation
     nothing renders is a vacuous row; K35's reach).

PCREC'S DOORS (R4c FIX): pcrec's builders do not call `mf_define` directly;
they call a pcrec function that checks the description against
DELEG_SITES (C10), makes the sink and forwards (`pcrec_memfn_define`, and
since M1b `pcrec_memfn_emit` for the VMRUN site's one-call EXPR;
src/gen/memfn_sites.c). A door is plumbing every site shares, so it is not
a site: the SITE is the door's caller. `DOORS` names each door and the
header that declares it (the shim must see the prototype before it wraps
the name). The door is held to account both ways: statically, a listed
door that no longer calls the kit is stale (red), and a door's callers are
held to the same row rule as direct kit callers; dynamically, per compile,
the kit calls made INSIDE doors must equal the door calls traced at their
callers (`door accounting`), so a door call the shim missed, or a kit call
a door made on nobody's behalf, is red rather than unattributed.

UNREACHED, LOUDLY: with no caller under src/ and no `delegated` row the half
has nothing to count; the caller prints that, and it is never a pass.
The mechanism is exercised on a SYNTHETIC caller every run (`selftest`), so
"UNREACHED" says "no pcrec site yet", never "the census machinery is broken".
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c17_lex import _name_from_header  # noqa: E402

CALL_RX = re.compile(r'\bmf_(define|emit)\s*\(')
# pcrec's doors over mf_define: name -> the header that declares it (see the
# module docstring). A door is renamed or added in the same change as this.
DOORS = {'pcrec_memfn_define': 'gen/memfn_sites.h',
         'pcrec_memfn_emit': 'gen/memfn_sites.h'}       # M1b: VMRUN
DOOR_RX = re.compile(r'\b(' + '|'.join(DOORS) + r')\s*\(')
CORPUS_CAP = 300            # compiles per pass
CORPUS_FLOOR = 100          # K35: a pass that compiled fewer is not a census


def strip_c(text):
    def blank(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
                  blank, text, flags=re.S)


def callers_in_text(text, rx=CALL_RX):
    """{enclosing definition: number of calls matching `rx`} (default: the
    kit's mf_define/mf_emit). A door's own definition header is not a call:
    only matches inside a function body count."""
    code = strip_c(text)
    out, depth, head, name = {}, 0, 0, None
    events = sorted([(m.start(), 'call') for m in rx.finditer(code)] +
                    [(i, c) for i, c in enumerate(code) if c in '{};'])
    for at, what in events:
        if what == '{':
            if depth == 0:
                name = _name_from_header(re.sub(r'^\s*#[^\n]*', '', code[head:at], flags=re.M))
            depth += 1
        elif what == '}':
            depth = max(0, depth - 1)
            if depth == 0:
                head, name = at + 1, None
        elif what == ';':
            if depth == 0:
                head = at + 1
        elif depth > 0:
            key = name if name else '<file scope>'
            out[key] = out.get(key, 0) + 1
    return out


def find_callers(root, rx=CALL_RX):
    """{relative file: {function: calls}} for every C file under src/."""
    res = {}
    for dp, _dns, fns in os.walk(os.path.join(root, 'src')):
        for fn in sorted(fns):
            if not fn.endswith('.c'):
                continue
            path = os.path.join(dp, fn)
            with open(path, encoding='utf-8', errors='replace') as fh:
                c = callers_in_text(fh.read(), rx)
            if c:
                res[os.path.relpath(path, root)] = c
    return res


def find_door_callers(root):
    """{relative file: {function: door calls}}: the sites behind pcrec's
    doors."""
    return find_callers(root, DOOR_RX)


SHIM_H = r'''/* C17 census trace shim (generated by tests/memfn/site_census.py) */
#include <stddef.h>
void c17_trace(const char *kind, const char *file, const char *func);
#undef mf_define
#undef mf_emit
#define mf_define(...) (c17_trace("define", __FILE__, __func__), MF_NS(define)(__VA_ARGS__))
#define mf_emit(...)   (c17_trace("emit",   __FILE__, __func__), MF_NS(emit)(__VA_ARGS__))
'''

def door_shim(doors):
    """The door half of the shim, for a file that CALLS the doors and defines
    none: each door's header first (its prototype must not be wrapped), then
    a self-referential macro that logs the caller and forwards."""
    out = ['/* C17 census door shim (generated by tests/memfn/site_census.py) */']
    for d in doors:
        out.append('#include "%s"' % DOORS[d])
    for d in doors:
        out.append('#define %s(...) (c17_trace("door", __FILE__, __func__), %s(__VA_ARGS__))'
                   % (d, d))
    return '\n'.join(out) + '\n'


SHIM_C = r'''#include <stdio.h>
#include <stdlib.h>
void c17_trace(const char *kind, const char *file, const char *func)
{
    const char *p = getenv("C17_TRACE_FILE");
    FILE *f = p ? fopen(p, "a") : NULL;
    if (!f) return;
    fprintf(f, "%s\t%s\t%s\n", kind, file, func);
    fclose(f);
}
'''


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def build_traced(root, cc, files, tmp, door_files=()):
    """Recompile `files` (kit callers) and `door_files` (door callers) with
    the shim over a copy of build/libpcrec.a and link cli/main.c; returns
    (binary, None) or (None, why). A door caller that also DEFINES a door
    cannot be traced this way and is refused."""
    lib = os.path.join(root, 'build/libpcrec.a')
    if not os.path.isfile(lib):
        return None, 'build/libpcrec.a is absent: run `make` first'
    hdr = os.path.join(tmp, 'c17_shim.h')
    with open(hdr, 'w') as fh:
        fh.write(SHIM_H)
    shim_c = os.path.join(tmp, 'c17_shim.c')
    with open(shim_c, 'w') as fh:
        fh.write(SHIM_C)
    kit_h = os.path.join(root, 'memfn/include/memfn.h')
    inc = ['-I' + os.path.join(root, 'lib'), '-I' + os.path.join(root, 'src')]
    members = run(['ar', 't', lib]).stdout.split()
    objs = [os.path.join(tmp, 'c17_shim.o')]
    r = run([cc, '-O1', '-std=gnu11', '-c', '-o', objs[0], shim_c])
    if r.returncode:
        return None, 'shim does not compile: ' + r.stderr[:200]
    dhdr = os.path.join(tmp, 'c17_door_shim.h')
    with open(dhdr, 'w') as fh:
        fh.write(door_shim(sorted(DOORS)))
    olds = []
    for f in sorted(set(files) | set(door_files)):
        base = os.path.splitext(os.path.basename(f))[0] + '.o'
        if members.count(base) != 1:
            return None, 'archive member %s is not unique (%d)' % (base, members.count(base))
        extra = []
        if f in door_files:
            with open(os.path.join(root, f), encoding='utf-8', errors='replace') as fh:
                code = strip_c(fh.read())
            if re.search(r'^[^\s#][^;{]*\b(' + '|'.join(DOORS) + r')\s*\([^;]*\{', code, re.M):
                return None, '%s both defines and calls a door: cannot trace its callers' % f
            extra = ['-include', dhdr]
        o = os.path.join(tmp, 'tr_' + base)
        r = run([cc, '-O1', '-std=gnu11'] + inc + ['-include', kit_h, '-include', hdr] + extra +
                ['-c', '-o', o, os.path.join(root, f)])
        if r.returncode:
            return None, '%s does not compile with the shim: %s' % (f, r.stderr[:300])
        shutil.copy(o, os.path.join(tmp, base))
        olds.append(base)
        objs.append(os.path.join(tmp, base))
    tlib = os.path.join(tmp, 'libtraced.a')
    shutil.copy(lib, tlib)
    if run(['ar', 'd', tlib] + olds).returncode:
        return None, 'ar d failed'
    if run(['ar', 'rs', tlib] + objs).returncode:
        return None, 'ar r failed'
    exe = os.path.join(tmp, 'pcrec_traced')
    r = run([cc, '-O1', '-std=gnu11'] + inc + ['-o', exe, os.path.join(root, 'cli/main.c'), tlib])
    if r.returncode:
        return None, 'traced link failed: ' + r.stderr[:300]
    return exe, None


def corpus_patterns(root):
    """Deterministic sample of the .rxt corpus's `pattern` lines."""
    pats = []
    for dp, dns, fns in os.walk(os.path.join(root, 'tests')):
        dns[:] = sorted(d for d in dns if d != 'memfn')
        for fn in sorted(fns):
            if fn.endswith('.rxt'):
                with open(os.path.join(dp, fn), encoding='utf-8', errors='replace') as fh:
                    for line in fh:
                        if line.startswith('pattern '):
                            pats.append(line[8:].rstrip('\n'))
    seen, uniq = set(), []
    for p in pats:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    step = max(1, len(uniq) // CORPUS_CAP)
    return uniq[::step][:CORPUS_CAP]


def run_corpus(exe, pats, tmp):
    """Compile every pattern; returns (compiles ok, [per-compile trace rows])."""
    trace = os.path.join(tmp, 'trace.tsv')
    out = os.path.join(tmp, 'out.c')
    per, okc = [], 0
    for p in pats:
        if os.path.exists(trace):
            os.remove(trace)
        env = dict(os.environ, C17_TRACE_FILE=trace)
        try:
            r = subprocess.run([exe, '--features', 'all', '-p', 'rx', '-o', out, '--pattern', p],
                               capture_output=True, env=env, timeout=30)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode != 0:
            continue
        okc += 1
        rows = []
        if os.path.exists(trace):
            with open(trace) as fh:
                rows = [l.rstrip('\n').split('\t') for l in fh if l.strip()]
        per.append(rows)
    return okc, per


def verdict(per, deleg, doors=DOORS):
    """per: per-compile [(kind, file, func)]; deleg: {row id: set of functions}.
    A `door` row names a site (its caller); a define/emit row made INSIDE a
    door is the door's forwarding, counted against the door rows of the same
    compile (door accounting), never a site. Returns (problems, stats)."""
    probs = []
    seen = {}
    bad_acct = 0
    for rows in per:
        inside = sum(1 for k, _f, fn in rows if k != 'door' and fn in doors)
        through = sum(1 for k, _f, _fn in rows if k == 'door')
        if inside != through:
            bad_acct += 1
        for k, _f, fn in rows:
            if k != 'door' and fn in doors:
                continue
            seen[fn] = seen.get(fn, 0) + 1
    if bad_acct:
        probs.append('rule 2 (door accounting): in %d compile(s) the kit calls made inside '
                     'pcrec\'s doors (%s) differ from the door calls traced at their callers: '
                     'a door call the shim missed, or a door reaching the kit on no site\'s '
                     'behalf' % (bad_acct, ','.join(sorted(doors))))
    listed = set().union(*deleg.values()) if deleg else set()
    for fn in sorted(seen):
        if fn not in listed:
            probs.append('rule 2: %s reached the kit %d time(s) over the corpus pass with no '
                         '`delegated` row naming it (an unlisted site)' % (fn, seen[fn]))
    for row in sorted(deleg):
        if not (deleg[row] & set(seen)):
            probs.append('rule 2 (reach): `delegated` row %s was never rendered over the corpus '
                         'pass (none of %s called the kit): a delegation nothing renders is '
                         'vacuous, or the corpus lacks its witness'
                         % (row, ','.join(sorted(deleg[row]))))
    calls = [sum(1 for k, _f, fn in r if k == 'door' or fn not in doors) for r in per]
    stats = {'compiles': len(per), 'calls': sum(calls), 'max': max(calls) if calls else 0,
             'withsite': sum(1 for c in calls if c), 'seen': seen}
    return probs, stats


def selftest(cc):
    """The mechanism on a SYNTHETIC caller: [(ok, message)]."""
    res = []
    # (a) call discovery, with decoys that must not count
    src = ('/* mf_define( in a comment */\n'
           'static const char *s = "mf_emit(";\n'
           'static void builder(mf_art *a) { mf_define(a); { mf_emit(a); } }\n'
           'int other(void) { return 0; }\n')
    got = callers_in_text(src)
    res.append((got == {'builder': 2}, 'selftest: call discovery attributes 2 calls to `builder`, '
                'ignores a comment and a string (got %r)' % got))
    # (b) verdict logic on synthetic traces
    t = [[('define', 'f.c', 'fake_builder')], [], [('emit', 'f.c', 'fake_builder')]]
    p, st = verdict(t, {'ROW': {'fake_builder'}})
    res.append((not p and st['calls'] == 2 and st['withsite'] == 2,
                'selftest: a listed and reached site passes, 2 calls over 3 compiles'))
    p, _ = verdict(t, {'ROW': {'other_fn'}})
    res.append((len(p) == 2, 'selftest: an unlisted caller AND an unreached delegated row each '
                'fail (%d problems)' % len(p)))
    # (b') the door path: a site behind a door is its caller; the door is not
    d = [[('door', 'f.c', 'fake_builder'), ('define', 'g.c', 'fake_door')]]
    p, st = verdict(d, {'ROW': {'fake_builder'}}, {'fake_door': 'g.h'})
    p2, _ = verdict([[('define', 'g.c', 'fake_door')]], {'ROW': {'fake_builder'}},
                    {'fake_door': 'g.h'})
    res.append((not p and st['seen'] == {'fake_builder': 1} and len(p2) == 2,
                'selftest: a site behind a door is attributed to the door\'s caller, and a '
                'door call with no traced caller fails door accounting (%d problems)' % len(p2)))
    # (c) the shim, end to end, on a synthetic caller
    if shutil.which(cc) is None:
        res.append((False, 'selftest: compiler %r not found' % cc))
        return res
    tmp = tempfile.mkdtemp(prefix='c17census.', dir=os.environ.get('TMPDIR'))
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        kit_h = os.path.join(here, '../../memfn/include/memfn.h')
        with open(os.path.join(tmp, 'c17_shim.h'), 'w') as fh:
            fh.write(SHIM_H)
        with open(os.path.join(tmp, 'c17_shim.c'), 'w') as fh:
            fh.write(SHIM_C)
        with open(os.path.join(tmp, 'stub.c'), 'w') as fh:
            fh.write('#include "memfn.h"\n'
                     'int mf_define(mf_art *a, const mf_site *s, const mf_hooks *d, mf_sink *f, '
                     'uint32_t *h) { (void)a; (void)s; (void)d; (void)f; (void)h; return 0; }\n'
                     'int mf_emit(mf_art *a, const mf_site *s, const mf_hooks *d, mf_sink *b, '
                     'mf_sink *f, mf_result *r) { (void)a; (void)s; (void)d; (void)b; (void)f; '
                     '(void)r; return 0; }\n')
        with open(os.path.join(tmp, 'fake.c'), 'w') as fh:
            fh.write('#include "memfn.h"\n'
                     'static void fake_builder(mf_art *a) { uint32_t h; mf_define(a, 0, 0, 0, &h); }\n'
                     'static void fake_emitter(mf_art *a) { mf_emit(a, 0, 0, 0, 0, 0); }\n'
                     'int main(void) { fake_builder(0); fake_emitter(0); return 0; }\n')
        exe = os.path.join(tmp, 'fake')
        inc = ['-I' + os.path.join(here, '../../memfn/include')]
        # the stub defines the REAL symbol names (through MF_NS), so it is compiled
        # WITHOUT the shim's macros
        stub_o = os.path.join(tmp, 'stub.o')
        r1 = run([cc, '-std=gnu11', '-c'] + inc + ['-o', stub_o, os.path.join(tmp, 'stub.c')])
        r2 = run([cc, '-std=gnu11', '-O0'] + inc + ['-include', os.path.abspath(kit_h), '-include',
                  os.path.join(tmp, 'c17_shim.h'), '-o', exe, os.path.join(tmp, 'fake.c'),
                  os.path.join(tmp, 'c17_shim.c'), stub_o])
        tr = os.path.join(tmp, 'trace.tsv')
        r3 = run([exe], env=dict(os.environ, C17_TRACE_FILE=tr)) if r2.returncode == 0 else None
        rows = []
        if r3 is not None and os.path.exists(tr):
            with open(tr) as fh:
                rows = [l.rstrip('\n').split('\t') for l in fh if l.strip()]
        want = [('define', 'fake_builder'), ('emit', 'fake_emitter')]
        have = [(k, fn) for k, _f, fn in rows]
        res.append((r1.returncode == 0 and r2.returncode == 0 and have == want,
                    'selftest: the shim logs a synthetic caller\'s define and emit by function '
                    '(%s)' % (have if have else (r1.stderr + r2.stderr)[:160])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res
