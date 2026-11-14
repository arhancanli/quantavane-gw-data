/* p*(l): primes p = 1 (mod 8) whose Legendre colouring has no run of l consecutive nonzero residues with equal
   character. Exhaustive up to a Weil-type cutoff  sqrt(p) > 2^l (l/2 - 1 + 2^-l) + l  (beyond it a run must exist).
   Prints every qualifying prime and the largest per l.  Usage: pstar lmin lmax */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
static int isprime(uint64_t n){ if(n<2) return 0; for(uint64_t d=2; d*d<=n; d++) if(n%d==0) return 0; return 1; }
static int chi(uint64_t a, uint64_t p){ /* Euler criterion */ uint64_t e=(p-1)/2, r=1, b=a%p; while(e){ if(e&1) r=(__uint128_t)r*b%p; b=(__uint128_t)b*b%p; e>>=1;} return r==1 ? 1 : -1; }
int main(int argc, char **argv){
  int lmin = atoi(argv[1]), lmax = atoi(argv[2]);
  for (int l = lmin; l <= lmax; l++){
    double c = pow(2.0, l) * (l / 2.0 - 1 + pow(2.0, -l)) + l; uint64_t cut = (uint64_t)(c * c) + 1;
    uint64_t best = 0; int count = 0;
    for (uint64_t p = 17; p <= cut; p += 8){ if (!isprime(p)) continue;
      int run = 0, prev = 0, bad = 0;
      for (uint64_t a = 1; a < p; a++){ int x = chi(a, p); run = (x == prev) ? run + 1 : 1; prev = x; if (run >= l){ bad = 1; break; } }
      if (!bad){ best = p; count++; if (count <= 40) printf("l=%d p=%llu\n", l, (unsigned long long)p); }
    }
    printf("RESULT l=%d cutoff=%llu qualifying=%d largest p*=%llu  =>  GW(4;3,l), GW(5;3,l) >= (l-1)p*+2 = %llu\n", l, (unsigned long long)cut, count, (unsigned long long)best, (unsigned long long)((l-1)*best+2));
    fflush(stdout);
  }
  return 0;
}
