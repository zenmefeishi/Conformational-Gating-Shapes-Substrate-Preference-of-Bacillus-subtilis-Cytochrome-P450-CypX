#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = "/mnt/e/article_2/xvg&csv/PCA"

SYSTEMS = ["APO", "PIY", "AND", "EST", "TES"]
COLORS = {"APO": "black", "PIY": "red", "AND": "blue", "EST": "green", "TES": "purple"}

DAT_TMPL = "PCA_{sys}_pooled_pc1_pc2.dat"
VAR_CSV = "pca_pooled_variance.csv"

# style
DPI = 300
POINT_SIZE = 10
POINT_ALPHA = 0.20        # ✅ 更透明（你可在 0.12–0.25 之间微调）
FIGSIZE = (6.8, 5.8)

# legend: enlarge color markers
LEGEND_MARKERSCALE = 1.0  # 这里不再用 markerscale 放大（我们自己控制 marker size）
LEGEND_FONTSIZE = 14
LEGEND_MARKERSIZE = 9     # ✅ 图例圆点大小（与图颜色一致）

def read_variance_percent():
    p = os.path.join(BASE, VAR_CSV)
    if not os.path.exists(p):
        return None, None
    df = pd.read_csv(p)
    m = {r["PC"]: float(r["explained_variance_percent"]) for _, r in df.iterrows()}
    return m.get("PC1", None), m.get("PC2", None)

def read_dat(sysname):
    p = os.path.join(BASE, DAT_TMPL.format(sys=sysname))
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing: {p}")
    arr = np.loadtxt(p, comments="#")
    if arr.ndim == 1:
        arr = arr.reshape(-1, 3)
    pc1 = arr[:, 1]
    pc2 = arr[:, 2]
    return pc1, pc2

def main():
    pc1_pct, pc2_pct = read_variance_percent()

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = plt.gca()

    # ===== scatter plots =====
    for sysname in SYSTEMS:
        pc1, pc2 = read_dat(sysname)
        ax.scatter(
            pc1, pc2,
            s=POINT_SIZE,
            alpha=POINT_ALPHA,                 # ✅ 更透明
            color=COLORS.get(sysname, "gray"),
            linewidths=0
        )

    # ===== axis labels =====
    if pc1_pct is not None and pc2_pct is not None:
        ax.set_xlabel(f"PC1 ({pc1_pct:.1f}%)", fontsize=18)
        ax.set_ylabel(f"PC2 ({pc2_pct:.1f}%)", fontsize=18)
    else:
        ax.set_xlabel("PC1", fontsize=18)
        ax.set_ylabel("PC2", fontsize=18)

    ax.tick_params(axis="both", labelsize=14)

    # ===== legend (ensure legend colors match points exactly) =====
    legend_handles = [
        Line2D(
            [0], [0],
            marker="o",
            linestyle="None",
            markersize=LEGEND_MARKERSIZE,
            markerfacecolor=COLORS.get(sysname, "gray"),
            markeredgecolor="none",
            label=sysname
        )
        for sysname in SYSTEMS
    ]

    ax.legend(
        handles=legend_handles,
        frameon=True,
        fontsize=LEGEND_FONTSIZE,
        scatterpoints=1
    )

    fig.tight_layout()

    out_png = os.path.join(BASE, "PCA_pooled_PC1_PC2_final.png")
    out_pdf = os.path.join(BASE, "PCA_pooled_PC1_PC2_final.pdf")
    fig.savefig(out_png)
    fig.savefig(out_pdf)
    plt.close(fig)

    print("Wrote:", out_png)
    print("Wrote:", out_pdf)

if __name__ == "__main__":
    main()
