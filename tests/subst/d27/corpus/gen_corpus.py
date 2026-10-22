#!/usr/bin/env python3
"""Writes the differential corpus TSVs beside this file (see lib/run_diff.py
for the columns).  Each family is a list of (flags, pattern, template,
unset, limit, subject, mode) rows; ids are FAMILY-NNN."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from esc import esc  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__))
FAM = {}


def add(fam, flags, pat, tpl, subj, limit='all', unset='empty', mode='diff'):
    b = lambda x: x if isinstance(x, bytes) else x.encode('utf-8')
    FAM.setdefault(fam, []).append((flags, b(pat), b(tpl), unset, str(limit), subj if subj == '<NULL>' else b(subj), mode))


# ---- tpl: every template form the contract lists (§2¶1), and the refusals (§2¶3)
T = 'tpl'
for tpl in ['$0', '${0}', '[$0]', '$1', '${1}', '$1$2', '${1}2', '$12', '$2$1', '$$', '$$1', '$$$1', '$$$$',
            '$01', '${01}', '$000002', '${0000}', '', 'lit', 'x\\ny', '\\$1', '\\', '\\\\', '}', '{', '{$1}',
            '${1}}', '$1}', '$1{', 'a$1b$2c$0d', '$0$0$0$0$0$0$0$0', '\x01\x7f\xff$1', '$1a', '$1_', '$2.5',
            '%$1%', '$0' * 50, 'x' * 300 + '$1']:
    add(T, '', r'(a)(b)?', tpl, 'xaab ab a')
for tpl in ['$1' + '0' * 1, '$10', '$11', '$12', '${12}', '$123', '$13']:   # greedy digits over 12 groups
    add(T, '', '(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)', tpl, 'abcdefghijkl-abcdefghijkl')
for tpl in ['$', 'a$', '$ ', '$-', '$+', '$!', '$\\', '$.', '$/', '${', '${1', '${}', '${ 1}', '${1 }', '${-1}',
            '${1a}', '${a b}', '${a-b}', '${1:-x}', '${1:+x}', '${n:-w}', '${n-w}', '${n+w}', '$*MARK', '${*MARK}',
            '$*', '${*}', '$65536', '${65536}', '$99999999999999999999', '${99999999999999999999}', '$}',
            '${!}', '${!1}', '${!a b}', '$\xc3\xa9', '${\xc3\xa9}', '\\u$1', '${{1}}']:
    add(T, '', r'(?<n>a)', tpl, 'xax', mode='tplrefuse' if 'MARK' in tpl else 'diff')
# PCRE2 10.46's other non-extended forms (pcre2api: $& $` $' $_), which §2¶1's table omits
for tpl in ['$&', '[$&]', '$`', "$'", '$_', '[$`|$&|$\'|$_]', '${&}', '${_}', '$_x', '${`}']:
    add(T, '', r'(?<n>a)', tpl, 'xaxay')   # substfix: F1/F2 fixed, retagged diff
for tpl in ['$_', '[$_]', '${_}', '$_1']:
    add(T, '', r'(?<_>a)(?<_1>b)?', tpl, 'xab-a')   # substfix: F1 fixed, retagged diff
for tpl in ['$0001', '${0001}', '$00', '$065535', '${065536}', '$0065536', '${' + 'L' * 129 + '}', '$' + 'L' * 129,
            '${' + 'L' * 300 + '}', '$1$', '$1${', '$$$', '${1}$']:
    add(T, '', r'(a)', tpl, 'xax')   # substfix: F7 fixed, retagged diff
for tpl in ['$65535', '${65535}', '$2', '${2}', '$nope', '${nope}', '$N', '$n_', '$nn']:   # parse, then bind refusal
    add(T, '', r'(?<n>a)', tpl, 'xax')
for tpl in ['$n', '${n}', '$n$n', '${n}x', '$nx', '$n-x', '$n.x', '$n$1', '${n}${1}$0']:
    add(T, '', r'(?<n>a)', tpl, 'xaxa')

# ---- grp: numbered groups, participation, unset axis (§4¶6, §9 row 5)
G = 'grp'
for unset in ['empty', 'error']:
    for pat, subj in [(r'(a)|(b)', 'ab'), (r'(a)?b', 'abb'), (r'(a)|b', 'ba'), (r'(a)?(b)?(c)?', 'cba'),
                      (r'(a|(b))+', 'aba'), (r'((a)|(b))+', 'abba'), (r'(a)*', 'aaxa'), (r'(a*)', 'b'),
                      (r'(?:(a)|b)(?:(c)|d)', 'adbc'), (r'(x)?y|(z)', 'yzxy'), (r'()', 'ab'),
                      (r'(a)(?:(b)|c)', 'acab')]:
        for tpl in ['<$1|$2|$3>', '$1']:
            add(G, '', pat, tpl, subj, unset=unset)
            add(G, '', pat, tpl, subj, limit=1, unset=unset)
add(G, '', r'(a)?(b)', '[$1$2]', 'bab', unset='error', limit=1)   # first match unset: error before output
add(G, '', r'(a)?(b)', '[$1$2]', 'abb', unset='error', limit=1)   # first match set: no error at limit 1
add(G, '', r'(a)?(b)', '[$1$2]', 'abb', unset='error')            # second match unset: error mid-way
add(G, '', r'(a)?(b)', '[$2]', 'bbb', unset='error')              # unreferenced unset group: no error
add(G, '', r'(a)?(b)', '$0', 'bbb', unset='error')
add(G, '', r'(a)?(b)', 'x', 'zzz', unset='error')                 # no match at all
add(G, '', r'(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)', '$10$9$1', 'abcdefghij')
add(G, '--no-captures', r'(a)(b)', '$1', 'ab', mode='expectrc:BIND -16 0')                    # ncaps 1: $1 refused at bind
add(G, '--no-captures', r'(a)(b)', '[$0]', 'abab')
add(G, '--engine=vm', r'(a)(b)', '[$2$1]', 'abab')
add(G, '--engine=dfa', r'ab|cd', '[$0]', 'abcdab')
add(G, '', r'(?|(a)|(b))', '[$1]', 'ab')                          # branch reset
add(G, '', r'(?|(a)(x)?|(b))', '[$1$2]', 'axb', unset='error')
add(G, '', r'(a)(?1)', '[$1]', 'aaa')                             # subroutine does not set the group
add(G, '', r'(a)\1', '[$1]', 'aaa')
add(G, '', r'(?:(a)|b)+', '[$1]', 'ab', unset='error')            # group set in an earlier iteration

# ---- name: named groups and duplicate runs (§3¶4, match_api §5.4¶6)
N = 'name'
for unset in ['empty', 'error']:
    for pat, subj in [(r'(?J)(?<n>a)|(?<n>b)', 'ab'), (r'(?J)(?<n>a)?(?<n>b)?', 'abba'),
                      (r'(?J)(?:(?<n>a)|(?<n>b))(?<n>c)?', 'acbc b'), (r'(?J)(?<n>x)?(?<m>y)(?<n>z)?', 'yxyyz'),
                      (r'(?<zeta>a)(?<alpha>b)(?<mu>c)', 'abc'), (r'(?<a>x)(?<ab>y)(?<abc>z)', 'xyz'),
                      (r'(?<n>a)|(?<N>b)', 'ab'), (r'(?<_>a)(?<_1>b)', 'ab'), (r'(?<n>a)?b', 'bab')]:
        for tpl in ['<$n>', '<${n}|$N|$m>', '<$zeta$alpha$mu|${alpha}>', '<$a|$ab|$abc|${a}b>', '<${_}|${_1}|${_}1>']:
            add(N, '', pat, tpl, subj, unset=unset)
add(N, '', r'(?<n>a)(?<m>b)', '$m$n$2$1$0', 'abab')
add(N, '', r'(?<n>a)(?<m>b)', '${m}${n}$m$n', 'ab')
add(N, '', r'(?<' + 'L' * 32 + r'>a)', '${' + 'L' * 32 + '}', 'xa')
add(N, '', r'(?<' + 'L' * 33 + r'>a)', '${' + 'L' * 33 + '}', 'xa')
add(N, '', r'(?<' + 'L' * 128 + r'>a)', '$' + 'L' * 128, 'xa')
add(N, '-e utf8', '(?<é>a)', '[${é}]', 'xa')   # substfix: F3 fixed (template side), retagged diff
add(N, '-e utf8', '(?<é>a)', '[$é]', 'xa')   # substfix: F3 fixed (template side), retagged diff
add(N, '-e utf8', '(?<aé>a)', '[${aé}]', 'xa')   # substfix: F3 fixed (template side), retagged diff
add(N, '', r'(?<_>a)(?<_1>b)', '<$_|$_1|${_}1>', 'ab')   # substfix: F1 fixed, retagged diff
add(N, '--no-captures', r'(?<n>a)', '$n', 'a', mode='expectrc:BIND -16 0')
add(N, '', r'(?J)(?<n>a)|(?<n>b)|(?<n>c)', '[$n]', 'cba')
add(N, '', r'(?|(?<n>a)|(?<n>b))', '[$n]', 'ab')

# ---- empty: empty matches and the retry (match_api §3.8¶2)
E = 'empty'
for pat in ['a*', 'x*', '', r'\b', '^', '$', r'(?=a)', 'a|', '|a', 'a??', r'(?:)', r'\B', r'a*?', r'(?m)^', r'(?m)$',
            r'\z', r'\Z', r'.*', r'a*|b', r'(?=a)|a', r'b*|a', r'(?<=a)', r'(?!a)', r'\G', r'\Ga', r'(?:a|)*', r'a{0,2}']:
    for subj in ['', 'a', 'bab', 'aab\nab\n', 'baaab']:
        add(E, '', pat, '[$0]', subj)
    add(E, '', pat, '[$0]', 'bab', limit=1)
    add(E, '', pat, '[$0]', 'bab', limit=2)
    add(E, '', pat, '[$0]', 'bab', limit=3)

# ---- lim: the limit argument (§6¶1, §6¶4)
L = 'lim'
for lim in [0, 1, 2, 3, 4, 5, 7, 8, 9, 63, 64, 65, 127, 128, 129, 200, 1000, 'all']:
    add(L, '', 'a', '[$0]', 'a' * 130 + 'b', limit=lim)
    add(L, '', 'x*', '<$0>', 'ab' * 70, limit=lim)
for lim in [0, 1, 2, 'all']:
    add(L, '', 'q', '[$0]', 'abc', limit=lim)
    add(L, '', 'q', '[$0]', '', limit=lim)
    add(L, '', '', '[$0]', '', limit=lim)

# ---- bsk: \K and lookaround (§4¶5, §9 rows 9)
K = 'bsk'
for pat, subj in [(r'a\Kb', 'abab'), (r'\Ka', 'aa'), (r'a\K', 'aaa'), (r'(?:a\K)+b', 'aab'), (r'a\K|b', 'abab'),
                  (r'ab\K\w*', 'abcd abx'), (r'(a)\K(b)', 'abab'), (r'a\K(?=b)', 'abab'), (r'a+\K', 'aaba'),
                  (r'\K', 'ab'), (r'(?<=a)b', 'abab'), (r'(?<=^|,)x', 'x,x,yx'), (r'(?<![a-z])\d+', 'a1 2 b33'),
                  (r'(?<=(a))b', 'abab'), (r'a(?=(bc))', 'abcabd'), (r'(?<=(\w))\b', 'ab cd'),
                  (r'(?=(\w+))\w', 'abc'), (r'(?<=\Ka)b', 'ab'), (r'(?=a\K)a', 'aa'), (r'x(?=(?1))|(b\K)', 'xb'),
                  (r'x|(?<=(?1))y|(\Kx)', 'xy'), (r'^|(?<=(?1))y|(?!)(\Kz)', 'zy')]:
    add(K, '', pat, '[$0|$1]', subj, mode='known:9' if 'Kz)' in pat else 'diff')
    add(K, '', pat, '[$0]', subj, limit=1)
    add(K, '', pat, '[$0]', subj, mode='known:9' if ('Kx)' in pat or 'Kz)' in pat) else 'nogap')

# the three spans §4¶5 / §9 row 9 name, with gaps, all matches: BADSPAN, or row 9's rendering
add(K, '', r'x(?=(?1))|(b\K)', '[$0]', 'xb')
add(K, '', r'x|(?<=(?1))y|(\Kx)', '[$0]', 'xy')
add(K, '', r'^|(?<=(?1))y|(?!)(\Kz)', '[$0]', 'zy', mode='expect:[][zy]')
add(K, '', r'^|(?<=(?1))y|(?!)(\Kz)', '[$0]', 'zyzy', mode='known:9')
add(K, '', r'x(?=(?1))|(b\K)', '[$0]', 'xb', limit=1)
add(K, '', r'(?<=(?1))y|(\Kz)', '[$0]', 'zy')

# ---- utf: -e utf8, ill-formed subjects (match_api §3.8¶2a, §9 row 11)
U = 'utf'
for pat in ['x*', '.', r'\w+', r'(.)', '\u00e9', r'[^a]', '', r'(?=.)', r'\b', r'\p{L}+', r'(*UCP)\d+', r'(*UCP)\w+']:
    for subj in ['aéb', 'éé', '日本\U0001F600', b'a\xffb', b'\xc3', b'\xe6\x97', b'\xc0\x80',
                 b'\xed\xa0\x80', b'\xf4\x90\x80\x80', b'a\xc3\xa9\xff\xc3\xa9']:
        illf = subj in (b'a\xffb', b'a\xc3\xa9\xff\xc3\xa9') and pat in ('x*', '', r'(?=.)', r'\b')
        add(U, '-e utf8', pat, '[$0]', subj, mode='known:11' if illf else 'diff')
add(U, '-e utf8 -i', 'é', '[$0]', 'ÉéE')
add(U, '-e utf8', '(é)', 'è$1è', 'aéb')
add(U, '-e utf8', 'a', b'[\xff]', 'aa')   # ill-formed template under utf8 (substfix: F4 fixed, retagged diff)
add(U, '-e utf8', 'a', b'[\xc3]', 'aa')   # substfix: F4 fixed, retagged diff
add(U, '', 'a', b'[\xff]', 'aa')
add(U, '-e utf8', 'x*', '[$0]', b'a\xffb', limit=1)
add(U, '-e utf8', 'x*', '[$0]', b'a\xffb', limit=2, mode='known:11')
add(U, '-e utf8', 'x*', '[$0]', b'a\xffb', mode='expect:[]a[]\\xff[]b[]')   # §9 row 11 verbatim

# ---- byte: byte-mode subjects with NULs and high bytes
B = 'byte'
for pat, subj in [(r'\x00', b'a\x00b\x00'), (r'[\x80-\xff]+', b'a\x80\xffb\xfe'), (r'.', b'\x00\n\xff'),
                  (r'(?s).', b'\x00\n\xff'), (r'\xff*', b'\xff\xffa\xff'), (r'(\x00+)', b'\x00\x00a'),
                  (r'\n', b'a\nb\r\n'), (r'(?m)^', b'a\nb\r\nc'), (r'$', b'a\n'), (r'\R', b'a\r\nb\rc\n')]:
    for tpl in ['[$0]', b'<\x00$1\x00>', '']:
        add(B, '', pat, tpl, subj)
add(B, '-i', r'(ab)', '[$1]', 'xAbaBAB')
add(B, '-i', r'\xe9', '[$0]', b'\xe9\xc9')
add(B, '-i --ucp', r'\xe9', '[$0]', b'\xe9\xc9')

# ---- big: long subjects, many matches, many groups (§6¶6)
Bg = 'big'
add(Bg, '', 'a', '[$0]', 'a' * 20000)
add(Bg, '', 'x*', '$0', 'ab' * 5000)
add(Bg, '', '(a)(b)?', '$2$1$2', 'ab' * 3000 + 'a')
add(Bg, '', '', '', 'z' * 5000)
add(Bg, '', 'b', 'x' * 1000, 'b' * 200)
for ng in [63, 64, 65, 127, 128, 129, 255, 256, 300]:
    pat = '(a)' * ng
    add(Bg, '', pat, '[$%d$1]' % ng, 'a' * ng + 'b' + 'a' * ng * 2)
add(Bg, '', '(?:(a)|b)' * 130, '[$130]', 'b' * 130 + 'a' * 130)

# ---- nogap: the element without RX_SUBST_GAPS vs PCRE2_SUBSTITUTE_REPLACEMENT_ONLY (§4¶3)
NG = 'nogap'
for pat, subj in [('a', 'banana'), ('x*', 'ab'), (r'(a)(n)?', 'banana'), ('', ''), ('q', 'abc'), (r'\w+', 'hi there you')]:
    for lim in [1, 2, 'all']:
        add(NG, '', pat, '<$0|$1>' if '(' in pat else '<$0>', subj, limit=lim, mode='nogap')

for fam, rows in FAM.items():
    with open(os.path.join(D, 'd_%s.tsv' % fam), 'w') as h:
        h.write('# id\tfamily\tflags\tpattern\ttemplate\tunset\tlimit\tsubject\tmode\n')
        for i, (flags, pat, tpl, unset, lim, subj, mode) in enumerate(rows):
            h.write('\t'.join([('%s-%03d' % (fam, i)), fam, flags, esc(pat), esc(tpl), unset, lim,
                               subj if subj == '<NULL>' else esc(subj), mode]) + '\n')
    print(fam, len(rows))
