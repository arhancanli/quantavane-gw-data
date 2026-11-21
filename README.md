# Power-residue colourings and exact Gallai–van der Waerden numbers: programs, formulas, proofs and colourings

This repository holds the encoders, the formulas with their LRAT proofs, the checkers, the searches and every
colouring behind the paper "Power-residue colourings and exact Gallai–van der Waerden numbers" by Arhan Canli
(Quantavane), November 2026.

The Gallai–van der Waerden number GW(r; k, ℓ) of Mao, Ozeki, Robertson and Wang is the least m ≥ r such that for
every n ≥ m, every colouring of {1, …, n} that uses exactly r colours contains a rainbow k-term or a monochromatic
ℓ-term arithmetic progression. The paper determines three rows:

- GW(r; 3, 4) = 53 for 3 ≤ r ≤ 5;
- GW(3; 3, 5) = 293 and GW(4; 3, 5) = GW(5; 3, 5) = 294;
- GW(4; 4, 3) = 57, GW(5; 4, 3) = GW(6; 4, 3) = 40, GW(7; 4, 3) = GW(8; 4, 3) = 37 and GW(9; 4, 3) = 24;

with GW(r; k, ℓ) = r for all larger r in each row, and it gives the lower bound GW(4; 4, 4) ≥ 329. The lower bounds
are explicit colourings, most of them built from power residues modulo a prime. The upper bounds combine lemmas
with SAT refutations whose proofs, in the LRAT format, are checked by a strict checker.

## What is here

- `gw/`: the working folder of the computations, with its own layout kept so that the scripts find each other.
  - Encoders: `gw_cnf.py`, `gw_eq.py`, `gw_prefix.py`, `k4/gw_rgs.py`, `k5/vdw_cnf.py`; the scripts that produced
    the formulas and proofs of each row: `cert_l5.sh`, `k4/cert_k4l3.sh`, `k5/cert_k5.sh`.
  - `lratcheck.c`: the strict LRAT checker. `check_rm.py`, `k4/check_k4.py`, `k5/check_k5.c`: checkers of
    colourings, which count rainbow and monochromatic progressions.
  - Formulas and proofs: `certificates.tar.xz` (48 formulas with their proofs for the row (3, 4), and their
    digest list, a copy of which is `SHA256SUMS`); `k4/certificates_k4l3.tar.xz` and `k4/lrat/` (row (4, 3));
    `k5/certificates_k5.tar.xz` and `k5/lrat/`; `l5cert/` (row (3, 5): the five formulas, compressed with xz).
    `k4/SHA256SUMS_k4l3`, `k5/SHA256SUMS_k5` and `l5cert/SHA256SUMS` list the SHA-256 digests of every formula
    and proof, including those that are not in this repository (see below).
  - Exhaustive searches: `k4/dfs_k4l3.c` with its output `k4/dfs_k4l3.out`, and `k5/dfs_k5l3.c` with
    `k5/logs/dfs22.log`.
  - Colourings: `witnesses_52.txt`, `colouring_1_328.txt`, `k4/witnesses_k4l3.txt`, `k4/extremal56_rgs.txt`,
    `k5/witnesses_k5l3.txt`, `l5cert/g3_292.col`, `l5cert/g5_293.col`.
  - Prime scans: `thm/pstar.c`, `pstar3.c`, `pstar7.c`, `pstarm.c` and `k5/pstar_pig.c`.
  - `k4l4_exact/`: Section 6 of the paper, on GW(4; 4, 4). `gw44_cnf.py` is the encoder, `rigid44.py` writes the
    case files (`cubes44.py` writes those of the exploratory runs), `run44.py` solves each case and streams its
    proof into the checker,
    `cert44.sh` runs everything, and `status44.py`, `eval44.py` and `decode44.py` read the results. `R1.txt` and
    `R2.txt` are the two case files (15,914 cases). `logs/R1.log` and `logs/R2.log` have, for every case, the
    result and the SHA-256 digests of its formula and of its proof; the proofs themselves were streamed into the
    checker and not stored. The other files of `logs/` are the logs of the base instances and of red controls,
    and, in `logs/explore/`, of exploratory runs on which the paper makes no claim.
- `checks/`: the paper's own checks. `gwcheck.c` is a second checker of colourings, `primes.c` lists the
  admissible primes, `window.py` and `window_second.c` are the two window searches, and the other Python programs
  write the colourings that `gwcheck` checks. `run_all.sh` rebuilds the outputs in `checks/out/`; we have not run
  it in full from this repository.
- `results/`: `run_checks.sh`, which runs the quick checks below, and its output `results.txt`.

`SHA256SUMS` in the repository root lists every file of the repository.

## How to re-run the checks

Commands are run from the repository root. They need a C compiler and Python 3 (standard library only).

```sh
sh results/run_checks.sh
```

In under a minute it compares the files of the three archives and of `gw/l5cert/` with the stored digest lists,
prints the digests of the three formulas of the row (3, 5) (their first 16 hexadecimal digits are in Appendix C
of the paper) and of the two case files, runs the strict checker on all 53 proofs stored here, runs the colouring
checkers on the stored colourings, and runs `checks/gwcheck.c` on the colourings of `checks/out/`, comparing with
the stored outputs. The last line of `results/results.txt` must read `ALL PASS`.

One proof by hand:

```sh
cc -O2 -o gw/lratcheck gw/lratcheck.c
mkdir -p work && tar -xJf gw/k4/certificates_k4l3.tar.xz -C work && gzip -dc gw/k4/lrat/U56.lrat.gz > work/U56.lrat
gw/lratcheck work/cnf/U56.cnf work/U56.lrat          #   s VERIFIED UNSAT
```

To produce the formulas and proofs again, see the first lines of `gw/cert_l5.sh`, `gw/k4/cert_k4l3.sh`,
`gw/k5/cert_k5.sh` and `gw/k4l4_exact/cert44.sh` (zsh). They need CaDiCaL 3.0.1 (`CADICAL=/path/to/cadical`) and
the compiled `gw/lratcheck`; `cert_l5.sh` also uses drat-trim's `lrat-check` (`LRAT_CHECK=`). The runs of Section 6
streamed about 68 GB of proofs. We have not run these scripts again from this repository.

## Not in this repository

- Seven proofs are larger than 50 MB and are not stored here: `k4/lrat/P5.lrat.gz`, `P7.lrat.gz` and `P9.lrat.gz`,
  `k5/lrat/P19_40.lrat.gz`, and `l5cert/A3_293.lrat.gz`, `A5_294_clean.lrat.gz` and `P294.lrat.gz` (about 670 MB in
  all).
  Their SHA-256 digests are in the three digest lists, and their formulas are here.
- The Lean developments. Those the paper calls (L1) and (L2) are public in their own repositories
  ([quantavane-gw-residue](https://github.com/arhancanli/quantavane-gw-residue),
  [quantavane-gw-residue-power](https://github.com/arhancanli/quantavane-gw-residue-power)); the development (L3)
  of Section 7 is not in this repository.
- The solver outputs and the logs of the row (3, 5) that `l5cert/SHA256SUMS` lists.

## Notes on the files

In the five scripts `gw/cert_l5.sh`, `gw/k4/cert_k4l3.sh`, `gw/k5/cert_k5.sh`, `gw/k4l4_exact/cert44.sh` and
`gw/k4l4_exact/run44.py`, the lines that named folders and programs of the machine that ran them now take them
from the environment (`GW_WORK`, `GW_ROOT`, `GW44_WORK`, `PYTHON`, `CADICAL`, `LRAT_CHECK`, `LRATCHECK`), with
defaults inside this repository. In `checks/run_all.sh` the default of `S` is `gw/`. In 15 logs of
`gw/k4l4_exact/logs/` the absolute paths of that machine were replaced by `work/` and `../`. Nothing else was
changed. The archives were made on that machine and keep its user name in their headers.

## Credit and sources

- Y. Mao, K. Ozeki, A. Robertson and Z. Wang, *Arithmetic progressions, quasi progressions, and Gallai–Ramsey
  colorings*, J. Combin. Theory Ser. A 193 (2023), 105672, where the numbers GW(r; k, ℓ) are defined.
- Y. Si, *Complete determination of the Gallai–van der Waerden number GW(r; 3, 3)*, arXiv:2610.30711v2 (2026).
- The SAT solver is CaDiCaL (A. Biere and others); `lrat-check` is part of drat-trim (N. Wetzler, M. J. H. Heule
  and W. A. Hunt Jr.).

The paper gives the full list of references.

## Authorship and the role of AI

Author and maintainer: Arhan Canli (Quantavane, https://quantavane.com), who takes responsibility for the results.

The encoders, the checkers, the searches and the runs were written and carried out by AI agents (Claude, by
Anthropic) working for Quantavane under Arhan Canli's direction. Programs described as written separately share no
code but were written with the same AI system. No mathematician outside Quantavane has reviewed this repository;
the colourings and the proofs can be checked by anyone with the programs here or with their own.

## How to cite

If you use these programs, formulas, proofs or colourings, please cite them as below.

```bibtex
@misc{quantavane-gw-data,
  author       = {Canli, Arhan},
  title        = {Programs, formulas, proofs and colourings for ``Power-residue colourings and exact Gallai-van der Waerden numbers''},
  year         = {2026},
  howpublished = {\url{https://github.com/arhancanli/quantavane-gw-data}},
  note         = {Quantavane; CC BY 4.0 for the data and text, MIT licence for the code}
}
```

[CITATION.cff](CITATION.cff) gives the same reference for GitHub's "Cite this repository" button.

Known uses of this work are listed in [USED_BY.md](USED_BY.md). If you use it, please open an issue or a pull request
with a link so that yours can be added.

## Licence

The formulas, the proofs, the colourings, the logs and the text are under CC BY 4.0 (`LICENSE`); the code is under
the MIT licence (`LICENSE-CODE`). To cite: see `CITATION.cff`.
