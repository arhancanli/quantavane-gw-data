# Aligned zero class for every m (Proposition 3.5 of the paper): on [1,(l-1)p+1] colour x by the m-th power class
# of x-1 (class of 1 = colour 0) when p does not divide x-1; the zero-class points 1 and (l-1)p+1 get colour 0 and
# the interior zero-class points 1+jp (0 < j < l-1) the new colour m. Prints "k l colouring" lines (k = m+1) and
# whether 1, ..., l-1 are all m-th powers mod p (the proposition needs: not all).
SYM = '0123456789abcdefghijklmnopqrstuvwxyz'
def build(m, p, l):
    e = (p - 1) // m
    vals = [1] + sorted({pow(a, e, p) for a in range(1, p)} - {1})
    idx = {v: i for i, v in enumerate(vals)}
    cls = lambda a: idx[pow(a % p, e, p)]
    N = (l - 1) * p + 1
    c = []
    for x in range(1, N + 1):
        if (x - 1) % p == 0:
            j = (x - 1) // p
            c.append(0 if j in (0, l - 1) else m)
        else:
            c.append(cls(x - 1))
    allpow = all(cls(j) == 0 for j in range(1, l))
    return ''.join(SYM[t] for t in c), allpow
for m, l, p in [(2, 4, 17), (2, 5, 73), (2, 6, 193), (2, 7, 617), (2, 8, 881), (2, 9, 2377),
                (3, 3, 19), (3, 4, 109), (3, 5, 307), (3, 6, 1777), (4, 3, 17), (4, 4, 353), (4, 5, 4937),
                (5, 3, 31), (5, 4, 751)]:
    s, allpow = build(m, p, l)
    print(f'# aligned m={m} l={l} p={p} N={(l-1)*p+1} all of 1..l-1 are m-th powers: {allpow}')
    print(m + 1, l, s)
