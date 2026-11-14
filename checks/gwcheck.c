/* Independent checker for the paper (written for papers/gw-2026, shares no code with the lane checkers).
   Input lines: "k l colouring" (colouring: one symbol per point 1..n, symbols 0-9 then a-z = colours 0..35);
   lines starting with '#' are skipped. Output per line: n, number of colours used, number of rainbow k-APs
   (k pairwise distinct colours) and of monochromatic l-APs among x, x+d, ..., d >= 1, inside [1,n]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int sym(char ch) {
  if (ch >= '0' && ch <= '9') return ch - '0';
  if (ch >= 'a' && ch <= 'z') return 10 + ch - 'a';
  return -1;
}
int main(void) {
  static char line[1 << 20];
  static int c[1 << 19];
  while (fgets(line, sizeof line, stdin)) {
    if (line[0] == '#' || line[0] == '\n') continue;
    int k, l; char *s = malloc(strlen(line) + 1);
    if (sscanf(line, "%d %d %s", &k, &l, s) != 3) { free(s); continue; }
    int n = (int)strlen(s), used[36] = {0}, ncol = 0, bad = 0;
    for (int i = 0; i < n; i++) { c[i] = sym(s[i]); if (c[i] < 0) bad = 1; else used[c[i]]++; }
    for (int i = 0; i < 36; i++) ncol += used[i] > 0;
    long long rain = 0, mono = 0;
    for (int x = 0; x < n; x++)
      for (int d = 1; x + (k - 1) * d < n || x + (l - 1) * d < n; d++) {
        if (x + (k - 1) * d < n) {
          int distinct = 1;
          for (int i = 0; i < k && distinct; i++)
            for (int j = i + 1; j < k; j++)
              if (c[x + i * d] == c[x + j * d]) { distinct = 0; break; }
          rain += distinct;
        }
        if (x + (l - 1) * d < n) {
          int same = 1;
          for (int j = 1; j < l; j++) if (c[x + j * d] != c[x]) { same = 0; break; }
          mono += same;
        }
      }
    printf("k=%d l=%d n=%d colours=%d rainbow=%lld mono=%lld %s%s\n", k, l, n, ncol, rain, mono,
           (rain == 0 && mono == 0 && !bad) ? "GOOD" : "BAD", bad ? " (bad symbol)" : "");
    free(s);
  }
  return 0;
}
