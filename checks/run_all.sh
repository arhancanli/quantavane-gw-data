#!/bin/zsh
# Rebuilds every output in out/ (12 Nov 2026). Needs a C compiler and python3; the witness check also needs the
# folder gw/ of this repository (S below) and, for the l = 5 green controls, the files of gw/l5cert.
set -e
cd ${0:a:h}
S=${S:-${0:a:h}/../gw}
cc -O2 -o gwcheck gwcheck.c
cc -O2 -o primes primes.c -lm
( for l in 4 5 6 7 8 9; do ./primes 2 $l 3 1; done; for l in 3 4 5 6; do ./primes 3 $l 4 1; done
  for l in 3 4 5; do ./primes 4 $l 5 1; done; for l in 3 4; do ./primes 5 $l 6 1; done
  for l in 3 4 5; do ./primes 3 $l 5 2; done; for l in 3 4 5; do ./primes 4 $l 6 2; done
  for l in 3 4; do ./primes 5 $l 7 2; done ) > out/primes.txt
./primes 2 3 3 1 > out/primes_m2_l3.txt
python3 -I smax.py > out/smax.txt
python3 -I residue.py > out/residue_colourings.txt && ./gwcheck < out/residue_colourings.txt > out/residue_check.txt
python3 -I aligned_m.py > out/aligned_m_colourings.txt && ./gwcheck < out/aligned_m_colourings.txt > out/aligned_m_check.txt
python3 -I table_checks.py > out/table_colourings.txt && ./gwcheck < out/table_colourings.txt > out/table_check.txt
python3 -I period28.py > out/period28.txt
python3 -I z4zq.py > out/z4zq_colourings.txt && ./gwcheck < out/z4zq_colourings.txt > out/z4zq_check.txt
for f in residue aligned_m table z4zq; do paste -d' ' <(grep '^#' out/${f}_colourings.txt) out/${f}_check.txt > out/${f}_summary.txt; done
./primes 6 3 7 1 > out/primes_extra_m6.txt; ./primes 6 4 7 1 >> out/primes_extra_m6.txt
./primes 5 5 6 1 > out/primes_extra_m5l5.txt                       # about one minute
( for l in 3 4 5 6 7; do ./primes 2 $l 4 2; done ) > out/primes_pigeon_m2.txt
cc -O2 -o window_second window_second.c
{ python3 -I window.py 4 6 101; python3 -I window.py 5 6 293; python3 -I window.py 4 5 101; python3 -I window.py 5 5 293
  ./window_second 4 6 3 101; ./window_second 5 6 3 293; ./window_second 4 5 3 101; ./window_second 5 5 3 293; } > out/window_searches_rerun.txt
echo done
