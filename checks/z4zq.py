# Remark 4.1(iii): the rule of Theorem 1.3 over Z_4 x Z_q (rows (2X-1) mod 8, columns the quadratic character of
# (2X-1) mod q, third column for multiples of q), on [1,8q]; for q = 7 it is the colouring of Theorem 1.3.
T = [[0, 3, 1], [2, 0, 1], [2, 1, 0], [1, 3, 0]]
def chi(a, q):
    a %= q
    if a == 0: return 2
    return 0 if pow(a, (q - 1) // 2, q) == 1 else 1
for q in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    s = ''.join(str(T[((2 * X - 1) % 8) // 2][chi(2 * X - 1, q)]) for X in range(1, 8 * q + 1))
    print(f'# q={q}')
    print(4, 3, s)
