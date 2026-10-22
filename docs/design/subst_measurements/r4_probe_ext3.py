import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from r4_probe_ext import sub, S_EXT, R
one = b'(b)'; twelve = b'(b)' + b'(x)?' * 11
for p, t in [(one, b'<\\8>'), (one, b'<\\10>'), (one, b'<\\12>'), (one, b'<\\18>'), (one, b'<\\01>'),
             (twelve, b'<\\10>'), (twelve, b'<\\12>'), (twelve, b'<\\1x>'),
             (b'(b)', b'\\U$1\xc3\x9f'), (b'(b)', b'<\\x41\\x4>')]:
    print('%-14r %-12r -> %s' % (p[:14], t, sub(p, t, b'abc', S_EXT)))
for t in [b'\\U$1', b'\\L$1']:
    print('latin1 byte', t, sub(b'(.+)', t, b'\xe0\xc0z', S_EXT))
