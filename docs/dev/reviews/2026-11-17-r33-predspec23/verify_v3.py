import re
nums = [str(n) for n in range(100)]           # the string set of /(?<n>\d+)/ & (n: <100) (canonical numerals)
for nm, order in [("shortest-first", sorted(nums, key=len)), ("longest-first", sorted(nums, key=len, reverse=True))]:
    SET = "|".join(order)
    for s in ["1234", "123456"]:
        print(nm, s, re.findall(r"[\s\S]*?(" + SET + ")", s))
