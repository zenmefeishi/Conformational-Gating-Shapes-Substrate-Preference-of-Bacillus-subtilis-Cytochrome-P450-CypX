#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = "/mnt/e/article_2/xvg&csv/PCA"

SYSTEMS = ["APO", "PIY", "AND", "EST", "TES"]
COLORS = {
    "APO": "black",
    "PIY": "red",
    "AND": "blue",
    "EST": "green",
    "TES": "purple"
}

DAT_TMPL = "PCA_{sys}_pooled_pc1_pc2.dat"
VAR_CSV = "pca_pooled_variance.csv"

# ===== style =====
DPI = 300
POINT_SIZE = 10
POINT_ALPHA = 0.20
FIGSIZE = (6.8, 5.8)

TITLE_FONTSIZE = 18
LABEL_FONTSIZE = 18
TICK_FONTSIZE = 14

# whether to show title on each panel
SHOW_TITLE = True

# add a small margin around global axis limits
AXIS_MARGIN = 0.03


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


def compute_global_limits(all_data, margin=0.03):
    all_pc1 = np.concatenate([d[0] for d in all_data.values()])
    all_pc2 = np.concatenate([d[1] for d in all_data.values()])

    xmin, xmax = np.min(all_pc1), np.max(all_pc1)
    ymin, ymax = np.min(all_pc2), np.max(all_pc2)

    xpad = (xmax - xmin) * margin
    ypad = (ymax - ymin) * margin

    return (xmin - xpad, xmax + xpad), (ymin - ypad, ymax + ypad)


def save_single_system_plot(sysname, pc1, pc2, xlim, ylim, pc1_pct, pc2_pct):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = plt.gca()

    ax.scatter(
        pc1, pc2,
        s=POINT_SIZE,
        alpha=POINT_ALPHA,
        color=COLORS.get(sysname, "gray"),
        linewidths=0
    )

    if pc1_pct is not None and pc2_pct is not None:
        ax.set_xlabel(f"PC1 ({pc1_pct:.1f}%)", fontsize=LABEL_FONTSIZE)
        ax.set_ylabel(f"PC2 ({pc2_pct:.1f}%)", fontsize=LABEL_FONTSIZE)
    else:
        ax.set_xlabel("PC1", fontsize=LABEL_FONTSIZE)
        ax.set_ylabel("PC2", fontsize=LABEL_FONTSIZE)

    if SHOW_TITLE:
        ax.set_title(sysname, fontsize=TITLE_FONTSIZE)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.tick_params(axis="both", labelsize=TICK_FONTSIZE)

    fig.tight_layout()

    out_png = os.path.join(BASE, f"PCA_{sysname}_PC1_PC2.png")
    out_pdf = os.path.join(BASE, f"PCA_{sysname}_PC1_PC2.pdf")
    fig.savefig(out_png)
    fig.savefig(out_pdf)
    plt.close(fig)

    print("Wrote:", out_png)
    print("Wrote:", out_pdf)


def main():
    pc1_pct, pc2_pct = read_variance_percent()

    # ===== read all data first =====
    all_data = {}
    for sysname in SYSTEMS:
        pc1, pc2 = read_dat(sysname)
        all_data[sysname] = (pc1, pc2)

    # ===== use same global axis limits for all panels =====
    xlim, ylim = compute_global_limits(all_data, margin=AXIS_MARGIN)

    # ===== make one plot per system =====
    for sysname in SYSTEMS:
        pc1, pc2 = all_data[sysname]
        save_single_system_plot(sysname, pc1, pc2, xlim, ylim, pc1_pct, pc2_pct)


if __name__ == "__main__":
    main()
