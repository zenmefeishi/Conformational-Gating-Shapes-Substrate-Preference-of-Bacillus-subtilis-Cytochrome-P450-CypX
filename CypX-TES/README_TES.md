# TES.itp — Parameter Provenance

Ligand: **TES** (testosterone)

**Inferred route**: Unknown.  
If this is incorrect, tell me which route you actually used and I'll update precisely (with versions & commands).

## What to record
- Toolchain & versions (e.g., AmberTools/GAFF2 + acpype vX.Y or CGenFF vX.Y + cgenff_charmm2gmx.py vX.Y)
- Charge method (e.g., AM1-BCC for GAFF2)
- Any penalty scores (CGenFF), if applicable
- Evidence files (TES.mol2 / TES.str / acpype.log)

## Mapping
- Topology: `TES.itp`
- Residue/atom names consistent with your PDB/GRO (e.g., `step3_input.gro`).
- Include order in `topol.top`: after protein/heme/ions.

Generated on 2025-11-01.


**Include order hint (from `topol.top`)**: toppar/forcefield.itp, toppar/PROA.itp, toppar/HEME.itp, toppar/MG.itp, toppar/TES.itp, toppar/SOD.itp, toppar/CLA.itp, toppar/TIP3.itp
