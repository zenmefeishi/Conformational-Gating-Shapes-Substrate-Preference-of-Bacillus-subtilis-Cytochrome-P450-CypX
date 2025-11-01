# MD Methods — CypX–PIY

Generated on 2025-11-01 from your PIY `.mdp/.tpr/.gro/.itp/.ndx` files.

## Software
- **GROMACS**: [Fill with `gmx dump -s step5_1.tpr | head -n 40`]

## Force Field & Water
- **Ligand**: `PIY.itp` (please add a short provenance note later if needed).
- **Other topology components provided**: `PROA.itp`, `HEME.itp`, `MG.itp`, `SOD.itp`, `CLA.itp`.
- **Water model**: **TIP3P** (from `TIP3.itp`).

## Electrostatics & van der Waals (production stage)
- **Coulomb type**: `PME`
- **PME**: `fourierspacing = 0.12`, `pme-order = 4`
- **vdW type**: `Cut-off`
- **Cutoffs**: `rlist = 1.2`, `rcoulomb = 1.2`, `rvdw = 1.2`
- **Neighbor list**: `nstlist = 20`, `verlet-buffer-tolerance = 0.005`

## Constraints & Time Step (production stage)
- **Constraints**: `h-bonds`; algorithm: `[FILL]`
- **LINCS**: `lincs-iter = 1`, `lincs-order = 4`
- **Time step Δt**: `dt = 0.002 ps`
- **Integrator**: `md`

## Thermostat & Barostat (production stage)
- **Thermostat**: `v-rescale`; `tc-grps = [FILL]`, `tau-t = [FILL]`, `ref-t = [FILL]`
- **Barostat**: `C-rescale`; `tau-p = [FILL]`, `ref-p = [FILL]`, `compressibility = 4.5e-5`

## Simulation Schedule & Durations
- **Energy minimization**: `step4.0_minimization.mdp` → `step4.0_minimization.tpr` → `step4.0_minimization.gro` — length: [FILL]
- **Equilibration**: `step4.1_equilibration.mdp` → `step4.1_equilibration.tpr` → `step4.1_equilibration.gro` — length: 125 ps
- **Production**: `step5_production.mdp` → `step5_1.tpr` → `step5_1.gro` — length: 1000.000 ns

## Index Groups for Gating Metrics
- Groups found in `index.ndx`: SOLU , SOLV , SYSTEM 
- **Gating atom pairs (Cα–Cα, default)**  
  - d_in: PHE96-CA ↔ SER206-CA  
  - d_out: ARG233-CA ↔ THR241-CA  

## Reproducibility & Version Check
- Stage parameters are taken from the stage `.mdp` files (authoritative). Effective parameters also available in `mdout.mdp`.
- To record exact GROMACS build string from the TPR (optional):
```
gmx dump -s step5_1.tpr | head -n 80
```


## Topology Assembly (from `topol.top`)
- **#include order** (top→bottom): toppar/forcefield.itp, toppar/PROA.itp, toppar/HEME.itp, toppar/PIY.itp, toppar/MG.itp, toppar/SOD.itp, toppar/CLA.itp, toppar/TIP3.itp

**[ molecules ]** (name  count):
```
; Compound	#mols
PROA  	           1
HEME  	           1
PIY   	           1
MG    	           1
SOD   	          78
CLA   	          65
TIP3  	       23123
```
