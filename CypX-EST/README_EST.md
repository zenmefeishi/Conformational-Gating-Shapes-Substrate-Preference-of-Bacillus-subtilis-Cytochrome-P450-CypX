# CypX–EST (B. subtilis CYP134A1 + EST)

This directory contains **machine‑readable inputs** and the **exact commands** to reproduce
the EST system setup and production MD used in the manuscript *“Conformational Gating Shapes Substrate Preference of Bacillus subtilis Cytochrome P450 CypX”*.

## Contents (current snapshot)
- `CLA.itp`
- `CypX_TES.rar`
- `EST.itp`
- `HEME.itp`
- `MD_METHODS.md`
- `MG.itp`
- `PIY.itp`
- `PROA.itp`
- `README_EST.md`
- `SOD.itp`
- `TES.itp`
- `TIP3.itp`
- `bootstrap_cypx_from_complex_wsl.sh`
- `cypx_1us_segment_runner.sh`
- `cypx_AND_all_in_one_wsl.sh`
- `cypx_APO_all_in_one_wsl.sh`
- `cypx_EST_all_in_one_wsl.sh`
- `cypx_PIY_all_in_one_wsl.sh`
- `cypx_TES_all_in_one_wsl.sh`
- `cypx_full_from_pdb_1us.sh`
- `forcefield.itp`
- `index.ndx`
- `mdout.mdp`
- `prep_commands.txt`
- `run_cypx_AND_wsl.sh`
- `run_cypx_APO_wsl.sh`
- `run_cypx_EST_wsl.sh`
- `run_cypx_PIY_wsl.sh`
- `run_cypx_TES_wsl.sh`
- `step3_input.gro`
- `step4.0_minimization.gro`
- `step4.0_minimization.mdp`
- `step4.0_minimization.tpr`
- `step4.1_equilibration.gro`
- `step4.1_equilibration.mdp`
- `step4.1_equilibration.tpr`
- `step5_1.gro`
- `step5_1.tpr`
- `step5_production.mdp`
- `topol.top`

> Outputs `seg_01…seg_20` will be produced after running the production section in `prep_commands.txt`.

## Quick Start
1. Check GROMACS availability: `gmx --version`  
2. Run: `bash -x prep_commands.txt` (or copy‑paste the commands)  
3. After all segments finish, concatenate with the commands at the bottom of `prep_commands.txt`.

## Methods Summary
See **metadata/MD_METHODS.md** for force field, PME/cutoffs, thermostat/barostat, dt, stage durations, and seeds.

## Ligand Parameter Provenance (EST.itp)
Document how `EST.itp` was generated (e.g., **CGenFF 2.x/ParamChem** or **GAFF2 + ACPYPE** with **AM1‑BCC**).
Include the exact commands and tool versions; keep any log file (e.g., `acpype.log`) for full traceability.

## Notes
- Trajectories are **not** distributed here; inputs and commands suffice for review and reproducibility tests.
- If required for peer review, consider a **Zenodo** private record and place its URL in your JCIM “Data & Software Availability” statement.
