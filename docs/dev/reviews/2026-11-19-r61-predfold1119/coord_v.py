import re
def modes(rx, whole, srch, fa):
    r=re.compile(rx)
    print(rx, [ (w, bool(r.fullmatch(w))) for w in whole], (lambda m:(m.group(),m.start()) if m else None)(r.search(srch)), [(m.group(),m.start()) for m in r.finditer(fa)])
modes(r'(?:10|1)', ['10'], 'x10', '10 1 101')
modes(r'(?:1|10)', ['10'], 'x10', '10 1 101')
modes(r'(?!)(?P<c>\d)', ['3','7'], 'x3 7', '3 7 x')
modes(r'(?P<c>\d)', ['3','7'], 'x3 7', '3 7 x')
modes(r'(\d)(?:x(?<=[5-9]x))?', ['3','3x','7x'], 'a3x', '3x 7x')
modes(r'[5-9]x?', ['3','3x','7x'], 'a3x', '3x 7x')
modes(r'\b(?:1|2|3|4|5|6|7|8|9|10)\b', ['10'], 'x10', '10 3 11')
modes(r'\b(?:1|2|3|4|5|6|7|8|9|10)\b', ['10'], 'x10 10', '10 3 11')
