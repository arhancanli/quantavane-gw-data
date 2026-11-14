/* Primes for the residue theorems (written for papers/gw-2026, independent of thm/pstar*.c).
   Usage: primes m l k mode, mode 1 = conditions (i) [for k = m+1] and (ii); mode 2 = (ii) only (Theorem 9:
   needs k >= m+2 and p > max(k-1,l-1)). Scans every prime p = 1 (mod m) with p > l (and p > k-1 in mode 2)
   up to the Weil cutoff W = floor((m^l((m-1)l/m - 1 + m^-l) + l)^2) + 1 and prints the qualifying primes. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef unsigned long long u64;
static u64 pw(u64 a, u64 e, u64 p) { u64 r = 1; a %= p; while (e) { if (e & 1) r = r * a % p; a = a * a % p; e >>= 1; } return r; }
static int isprime(u64 n) { if (n < 2) return 0; for (u64 q = 2; q * q <= n; q++) if (n % q == 0) return 0; return 1; }
int main(int argc, char **argv) {
  int m = atoi(argv[1]), l = atoi(argv[2]), k = atoi(argv[3]), mode = atoi(argv[4]);
  long double c = powl(m, l) * ((long double)(m - 1) * l / m - 1 + powl(m, -l)) + l;
  u64 W = (u64)floorl(c * c) + 1;
  int cnt = 0; u64 last = 0;
  printf("m=%d l=%d k=%d mode=%d cutoff=%llu primes:", m, l, k, mode, W);
  for (u64 p = 2; p <= W; p++) {
    if (p % m != 1 || !isprime(p) || p <= (u64)l) continue;
    if (mode == 2 && p <= (u64)(k - 1)) continue;
    u64 e = (p - 1) / m;
    if (mode == 1) { /* condition (i): for each i in 0..m the classes of j - i (j != i) are not all distinct */
      int ok = 1;
      for (int i = 0; i <= m && ok; i++) {
        u64 cl[16]; int t = 0, rep = 0;
        for (int j = 0; j <= m; j++) if (j != i) { long long v = j - i; u64 r = (u64)((v % (long long)p + (long long)p) % (long long)p); cl[t++] = pw(r, e, p); }
        for (int a = 0; a < t && !rep; a++) for (int b = a + 1; b < t; b++) if (cl[a] == cl[b]) { rep = 1; break; }
        if (!rep) ok = 0;
      }
      if (!ok) continue;
    }
    /* condition (ii): no l consecutive elements of {1,...,p-1} in one class */
    int run = 0, okr = 1; u64 prev = 0;
    for (u64 a = 1; a <= p - 1; a++) {
      u64 v = pw(a, e, p);
      run = (a > 1 && v == prev) ? run + 1 : 1; prev = v;
      if (run >= l) { okr = 0; break; }
    }
    if (!okr) continue;
    printf(" %llu", p); cnt++; last = p;
  }
  printf("\ncount=%d largest=%llu\n", cnt, last);
  return 0;
}
