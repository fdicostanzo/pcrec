import re, datetime
# 2026-11-27 his example "Wednesday June 12, 1994": the weekday NAME before the date, tested against the date's own
# weekday by a test written AFTER both are matched. python's datetime stands in for the planned native weekday_of.
MON = ['January','February','March','April','May','June','July','August','September','October','November','December']
R = re.compile(r'(?P<wd>[A-Z][a-z]+day) (?P<month>[A-Z][a-z]+) (?P<day>\d{1,2}), (?P<year>\d{4})')
def ok(m):
    if m is None or m['month'] not in MON: return False
    try: d = datetime.date(int(m['year']), MON.index(m['month']) + 1, int(m['day']))
    except ValueError: return False
    return d.strftime('%A') == m['wd']
def findall(s):
    out, i = [], 0
    while i <= len(s):
        m = R.match(s, i)
        if ok(m): out.append(f'{m.group()}@{i}'); i = m.end()
        else: i += 1
    return out
print('June 12, 1994 was a', datetime.date(1994, 6, 12).strftime('%A'))
for w in ['Wednesday June 12, 1994', 'Sunday June 12, 1994', 'Wednesday June 15, 1994']:
    print('WHOLE', repr(w), 'HOLDS' if ok(R.fullmatch(w)) else 'FAILS')
s = 'Wednesday June 12, 1994; Sunday June 12, 1994; Wednesday June 15, 1994'
print('SEARCHED', repr(s), (findall(s) or [None])[0]); print('FIND-ALL', findall(s))
