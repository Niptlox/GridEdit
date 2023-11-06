# /-1-\
# 6   2
# >-7-<
# 5   3
# \-4-/
from collections import defaultdict
from pprint import pprint

d = {
    1: (2, 3),
    2: (1, 2, 7, 5, 4),
    3: (1, 2, 7, 3, 4),
    4: (6, 7, 2, 3),
    5: (1, 6, 7, 3, 4),
    6: (1, 6, 7, 5, 3, 4),
    7: (1, 2, 3),
    8: (1, 2, 3, 4, 5, 6, 7),
    9: (1, 2, 3, 4, 6, 7),
    0: (1, 2, 3, 4, 5, 6),
}
ud = defaultdict(list)
for i, c in d.items():
    b = bin(i)[2:].rjust(4, "0")
    for n_c in c:
        ud[n_c].append(b)
    # print(b, i)
# pprint(ud)

nb = defaultdict(list)
for i in range(16):
    b = bin(i)[2:].rjust(4, "0")

    print(b, i)



