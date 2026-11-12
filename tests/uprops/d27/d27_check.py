#!/usr/bin/env python3
"""tests/uprops/d27/d27_check.py -- the two INDEPENDENT oracles for the D27
blinded \\p corpus (the .rxt files beside this script). Neither reads pcrec's
generated tables or runs pcrec:

  ucd     single-code-point blocks whose pattern is `\\p{X}` / `\\P{X}` /
          `\\p{^X}` (X a binary property, Bidi_Class, Block or Age) are
          re-derived from the vendored UCD 16.0.0 FILES themselves
          (third_party/ucd-16.0.0/), and every m/n case compared.
  pcre2   every block is run through libpcre2 (tests/lib/p2probe.c, built on
          demand into build/p2gen/) and every case compared, span and groups.

usage: d27_check.py {ucd|pcre2} [--list] [FILE.rxt ...]   (default: all files
here).  Exit 0 iff no DISAGREEMENT; blocks with no oracle (the Age/Block
extensions libpcre2 refuses, shapes the UCD arm does not evaluate) are
counted and, under --list, named."""
import bisect
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UCD = os.path.join(ROOT, 'third_party', 'ucd-16.0.0')


def unesc(s):
    out = bytearray()
    i = 0
    while i < len(s):
        if s[i] == '\\' and s[i + 1] == 'x':
            out.append(int(s[i + 2:i + 4], 16))
            i += 4
        else:
            out += s[i].encode()
            i += 1
    return bytes(out)


STR = re.compile(r'"((?:[^"\\]|\\.)*)"')


def parse(path):
    blocks, cur, pend = [], None, []
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if line.startswith('#'):
            pend.append(line)
            continue
        if not line.strip():
            continue
        w = line.split(None, 1)
        k = w[0]
        if k == 'pattern':
            cur = dict(file=os.path.basename(path), line=ln, pat=line[8:],
                       feat='', enc='byte', flags='', cases=[], perr=False,
                       title=' '.join(pend[-2:]))
            blocks.append(cur)
            pend = []
        elif k == 'features':
            cur['feat'] = w[1]
        elif k == 'encoding':
            cur['enc'] = w[1]
        elif k == 'flags':
            cur['flags'] = w[1]
        elif k == 'perr':
            cur['perr'] = True
        elif k in ('m', 'n', 'ms', 'ns'):
            sp = 0
            rest = w[1]
            if k in ('ms', 'ns'):
                sp, rest = rest.split(None, 1)
                sp = int(sp)
            m = STR.match(rest)
            nums = [int(x) for x in rest[m.end():].split()]
            cur['cases'].append(dict(k=k[0], sp=sp, subj=unesc(m.group(1)),
                                     span=tuple(nums), groups=[], ln=ln))
        elif k == 'g':
            cur['cases'][-1]['groups'].append([int(x) for x in w[1].split()])
        else:
            raise SystemExit('%s:%d: unknown directive %r' % (path, ln, k))
    return blocks


# ---------------------------------------------------------------- libpcre2
def probe():
    src = os.path.join(ROOT, 'tests', 'lib', 'p2probe.c')
    exe = os.path.join(ROOT, 'build', 'p2gen', 'p2probe')
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        subprocess.run(['gcc', '-O1', '-o', exe, src, '-lpcre2-8'], check=True)
    return exe


def run_pcre2(blocks, listing):
    exe = probe()
    st = dict(agree=0, noracle=0, dis=0, cases=0, perr_ok=0)
    for b in blocks:
        opts = ('u' if b['enc'] == 'utf8' else '') + ('i' if 'i' in b['flags'] else '')
        args = ['%d:%s' % (c['sp'], c['subj'].hex()) for c in b['cases']]
        out = subprocess.run([exe, opts, b['pat'].encode().hex()] + args,
                             capture_output=True, text=True, check=True).stdout.splitlines()
        where = '%s:%d %s' % (b['file'], b['line'], b['pat'])
        if out[0].startswith('ERR'):
            if b['perr']:
                st['agree'] += 1
            else:
                st['noracle'] += 1
                if listing:
                    print('NOORACLE', where, '|', out[0])
            continue
        if b['perr']:
            st['perr_ok'] += 1
            print('PERR-ACCEPTED-BY-PCRE2 (pcrec capability refusal?)', where,
                  '[enc=%s feat=%r]' % (b['enc'], b['feat']))
            continue
        bad = False
        for c, o in zip(b['cases'], out[1:]):
            st['cases'] += 1
            f = o.split()
            if f[0] == 'N':
                got = None
            elif f[0] == 'M':
                v = [int(x) for x in f[1:]]
                got = [tuple(v[i:i + 2]) for i in range(0, len(v), 2)]
            else:
                got = ('ERR', o)
            if c['k'] == 'n':
                ok = got is None
            else:
                ok = (isinstance(got, list) and got[0] == c['span'][:2] and
                      all(g[0] < len(got) and got[g[0]] == tuple(g[1:3])
                          for g in c['groups']))
            if not ok:
                bad = True
                st['dis'] += 1
                print('DISAGREE %s:%d %s subj=%s expect=%s%s libpcre2=%s' % (
                    b['file'], c['ln'], b['pat'], c['subj'], c['k'], c['span'], got))
        if not bad:
            st['agree'] += 1
    return st


# --------------------------------------------------------------------- UCD
def norm(s):
    return re.sub(r'[ _-]', '', s).lower()


def ranges(fn):
    """[(lo, hi, value-field-string)] from a UCD data file."""
    r = []
    for line in open(os.path.join(UCD, fn), encoding='utf-8'):
        line = line.split('#', 1)[0].strip()
        if not line or ';' not in line:
            continue
        a, v = [x.strip() for x in line.split(';')[:2]]
        lo, _, hi = a.partition('..')
        r.append((int(lo, 16), int(hi or lo, 16), v))
    return r


class Ucd:
    def __init__(self):
        self.bin = {}      # norm name -> set of cps
        longs = {}
        for line in open(os.path.join(UCD, 'PropertyAliases.txt'), encoding='utf-8'):
            line = line.split('#', 1)[0].strip()
            if ';' in line:
                f = [x.strip() for x in line.split(';')]
                for x in f:
                    longs[norm(x)] = f[1]
        self.longs = longs
        sets = {}
        for fn in ('PropList.txt', 'DerivedCoreProperties.txt', 'emoji-data.txt'):
            for lo, hi, v in ranges(fn):
                # DerivedCoreProperties has "InCB; Linker" style rows: key by whole value
                sets.setdefault(v, set()).update(range(lo, hi + 1))
        for line in open(os.path.join(UCD, 'UnicodeData.txt'), encoding='utf-8'):
            f = line.split(';')
            if f[9] == 'Y':
                sets.setdefault('Bidi_Mirrored', set()).add(int(f[0], 16))
        for k, s in sets.items():
            self.bin[norm(k)] = s
        self.bin['ascii'] = set(range(128))
        self.bin['any'] = set(range(0x110000))
        self.bin['asciihexdigit'] = self.bin.get('asciihexdigit', set())
        # Age
        self.age = {}
        for lo, hi, v in ranges('DerivedAge.txt'):
            for c in range(lo, hi + 1):
                self.age[c] = v
        # Blocks
        self.blk = []
        for lo, hi, v in ranges('Blocks.txt'):
            self.blk.append((lo, hi, v))
        self.blk.sort()
        self.blk_lo = [b[0] for b in self.blk]
        self.pva = {}
        for line in open(os.path.join(UCD, 'PropertyValueAliases.txt'), encoding='utf-8'):
            line = line.split('#', 1)[0].strip()
            if ';' in line:
                f = [x.strip() for x in line.split(';')]
                self.pva.setdefault(f[0], []).append(f[1:])
        # Bidi_Class: @missing defaults then explicit rows
        long2short = {f[1]: f[0] for f in self.pva['bc']}
        self.bc = {}
        self.bc_default = []
        for line in open(os.path.join(UCD, 'DerivedBidiClass.txt'), encoding='utf-8'):
            m = re.match(r'# @missing: ([0-9A-F]+)\.\.([0-9A-F]+); (\w+)', line)
            if m:
                self.bc_default.append((int(m.group(1), 16), int(m.group(2), 16),
                                        long2short[m.group(3)]))
        self.bc_explicit = ranges('DerivedBidiClass.txt')
        self._bcmap = {}
        for lo, hi, v in self.bc_default:
            for c in range(lo, hi + 1):
                self._bcmap[c] = v
        for lo, hi, v in self.bc_explicit:
            for c in range(lo, hi + 1):
                self._bcmap[c] = v

    def block_of(self, c):
        i = bisect.bisect_right(self.blk_lo, c) - 1
        if i >= 0 and self.blk[i][0] <= c <= self.blk[i][1]:
            return self.blk[i][2]
        return 'No_Block'

    def block_names(self, name):
        n = norm(name)
        for f in self.pva['blk']:
            if n in [norm(x) for x in f]:
                return {norm(x) for x in f}
        return None

    def member(self, prop, c):
        """True/False, or None if this arm does not evaluate `prop`."""
        if '=' in prop or ':' in prop:
            k, _, v = re.split(r'([=:])', prop, maxsplit=1)[0], None, re.split(r'[=:]', prop, maxsplit=1)[1]
            kn = norm(k)
            if kn in ('bidiclass', 'bc'):
                shorts = {f[0] for f in self.pva['bc']}
                match = [s for s in shorts if norm(s) == norm(v)]
                if not match:
                    return None
                return self._bcmap.get(c, 'L') == match[0]
            if kn in ('block', 'blk'):
                names = self.block_names(v)
                if names is None:
                    return None
                return norm(self.block_of(c)) in names
            if kn == 'age':
                if not v:
                    return None
                nv = v.upper().replace('_', '.')
                if nv.startswith('V'):
                    nv = nv[1:]
                if nv in ('NA', 'UNASSIGNED'):
                    return c not in self.age
                if not re.match(r'^\d+\.\d+$', nv):
                    return None
                return self.age.get(c) == nv
            return None
        n = norm(prop)
        n = norm(self.longs.get(n, n))
        if n not in self.bin:
            return None
        return c in self.bin[n]


PROP = re.compile(r'^\\([pP])\{(\^?)([^}]*)\}$')


def run_ucd(blocks, listing):
    u = Ucd()
    st = dict(blocks=0, cases=0, dis=0, skip=0)
    skipped = {}
    for b in blocks:
        m = PROP.match(b['pat'])
        if (b['perr'] or not m or 'i' in b['flags'] or
                any(c['k'] in 'ms' and c['sp'] for c in b['cases'])):
            st['skip'] += 1
            continue
        neg = (m.group(1) == 'P') ^ (m.group(2) == '^')
        prop = m.group(3)
        res, ok_block = [], True
        for c in b['cases']:
            try:
                cps = (c['subj'].decode('utf-8') if b['enc'] == 'utf8'
                       else c['subj'].decode('latin-1'))
            except UnicodeDecodeError:
                ok_block = False
                break
            if len(cps) != 1 or c['sp']:
                ok_block = False
                break
            mem = u.member(prop, ord(cps))
            if mem is None:
                ok_block = False
                skipped[prop] = skipped.get(prop, 0) + 1
                break
            res.append((c, mem != neg))
        if not ok_block:
            st['skip'] += 1
            continue
        st['blocks'] += 1
        for c, want in res:
            st['cases'] += 1
            claim = c['k'] == 'm' and c['span'][:2] == (0, len(c['subj']))
            if c['k'] == 'm' and not claim:
                print('ODD-SPAN %s:%d %s' % (b['file'], c['ln'], b['pat']))
                continue
            if claim != want:
                st['dis'] += 1
                print('DISAGREE %s:%d %s subj=%s rxt=%s UCD=%s' % (
                    b['file'], c['ln'], b['pat'], c['subj'], c['k'], 'member' if want else 'non-member'))
    if listing:
        print('unresolved property names:', sorted(skipped))
    return st


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ('ucd', 'pcre2'):
        raise SystemExit(__doc__)
    mode, listing = a[0], '--list' in a
    files = [x for x in a[1:] if x != '--list'] or sorted(
        os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith('.rxt'))
    blocks = []
    for f in files:
        blocks += parse(f)
    st = (run_ucd if mode == 'ucd' else run_pcre2)(blocks, listing)
    print('d27_check %s: %d blocks parsed, %s' % (mode, len(blocks), st))
    return 1 if st['dis'] else 0


if __name__ == '__main__':
    sys.exit(main())
