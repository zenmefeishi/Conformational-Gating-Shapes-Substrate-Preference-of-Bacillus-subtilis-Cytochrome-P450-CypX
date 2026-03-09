#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
BASE = "/mnt/e/article_2/xvg&csv"
IN_CSV = os.path.join(BASE, "Table1_state_populations_pooled.csv")

# outputs
OUT_TABLE = os.path.join(BASE, "Table1_state_populations_with_CR_PI.csv")
OUT_FIG_CR = os.path.join(BASE, "Figure7_CR_bar.png")
OUT_FIG_PI = os.path.join(BASE, "Figure7_PI_bar.png")

DPI = 300

# Use log scale to handle large dynamic ranges
USE_LOG_CR = True
USE_LOG_PI = True

# Avoid log(0): clamp to epsilon
EPS_CR = 1e-3
EPS_PI = 1e-3

# Figure size (inches)
FIGSIZE = (5.8, 3.8)

# =============================
# Colors (match rmsd_plot_fix.py)
# APO=black, PIY=red, AND=blue, EST=green, TES=purple
# =============================
SYSTEM_COLORS = {
    "APO": "black",
    "PIY": "red",
    "AND": "blue",
    "EST": "green",
    "TES": "purple",
}

# =============================
# MAIN
# =============================
def main():
    if not os.path.exists(IN_CSV):
        raise FileNotFoundError(f"Cannot find: {IN_CSV}")

    # Input format: index=system, columns include Open/Intermediate/Closed as fractions
    df = pd.read_csv(IN_CSV, index_col=0)

    # sanity check
    required = ["Open", "Intermediate", "Closed"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in {IN_CSV}. Found: {list(df.columns)}")

    # Compute indices
    # CR = P_closed / P_open
    # PI = (P_open + P_closed) / P_intermediate
    df = df.copy()
    df["CR"] = df["Closed"] / df["Open"]
    df["PI"] = (df["Open"] + df["Closed"]) / df["Intermediate"]

    # Presentation table (percent + indices)
    out = pd.DataFrame({
        "Open (%)": (df["Open"] * 100.0).round(1),
        "Intermediate (%)": (df["Intermediate"] * 100.0).round(1),
        "Closed (%)": (df["Closed"] * 100.0).round(1),
        "Closedness Ratio (CR)": df["CR"].replace([np.inf, -np.inf], np.nan).round(2),
        "Polarization Index (PI)": df["PI"].replace([np.inf, -np.inf], np.nan).round(2),
    })
    out.to_csv(OUT_TABLE, index=True)

    systems = out.index.tolist()
    bar_colors = [SYSTEM_COLORS.get(s, "C0") for s in systems]  # fallback to default if missing

    # -----------------------------
    # Figure 7A: Closedness Ratio
    # -----------------------------
    plt.figure(figsize=FIGSIZE, dpi=DPI)
    cr = out["Closedness Ratio (CR)"].astype(float).to_numpy()

    if USE_LOG_CR:
        cr_plot = np.clip(cr, EPS_CR, None)
        plt.bar(systems, cr_plot, color=bar_colors, width=0.6)
        plt.yscale("log")
        plt.ylabel("Closedness Ratio (CR) [log scale]")
        plt.title("Gating index: Closedness Ratio")
    else:
        plt.bar(systems, cr, color=bar_colors, width=0.6)
        plt.ylabel("Closedness Ratio (CR)")
        plt.title("Gating index: Closedness Ratio")

    plt.tight_layout()
    plt.savefig(OUT_FIG_CR)
    plt.close()

    # -----------------------------
    # Figure 7B: Polarization Index
    # -----------------------------
    plt.figure(figsize=FIGSIZE, dpi=DPI)
    pi = out["Polarization Index (PI)"].astype(float).to_numpy()

    if USE_LOG_PI:
        pi_plot = np.clip(pi, EPS_PI, None)
        plt.bar(systems, pi_plot, color=bar_colors, width=0.6)
        plt.yscale("log")
        plt.ylabel("Polarization Index (PI) [log scale]")
        plt.title("Gating index: Polarization Index")
    else:
        plt.bar(systems, pi, color=bar_colors, width=0.6)
        plt.ylabel("Polarization Index (PI)")
        plt.title("Gating index: Polarization Index")

    plt.tight_layout()
    plt.savefig(OUT_FIG_PI)
    plt.close()

    print("Wrote:", OUT_TABLE)
    print("Wrote:", OUT_FIG_CR)
    print("Wrote:", OUT_FIG_PI)

    # also print a quick summary to terminal
    print("\n=== Table1 (from pooled populations) ===")
    print(out.to_string())

if __name__ == "__main__":
    main()
