"""Streaming ridge regression for affine maps between residual streams."""
from __future__ import annotations

import torch


class RidgeAcc:
    """Accumulates sufficient statistics for Y ≈ X W + b (float64)."""

    def __init__(self, dx: int, dy: int):
        self.n = 0
        self.sx = torch.zeros(dx, dtype=torch.float64)
        self.sy = torch.zeros(dy, dtype=torch.float64)
        self.xx = torch.zeros(dx, dx, dtype=torch.float64)
        self.xy = torch.zeros(dx, dy, dtype=torch.float64)
        self.yy_diag = torch.zeros(dy, dtype=torch.float64)

    def add(self, X: torch.Tensor, Y: torch.Tensor):
        X = X.reshape(-1, X.shape[-1]).double(); Y = Y.reshape(-1, Y.shape[-1]).double()
        self.n += X.shape[0]
        self.sx += X.sum(0); self.sy += Y.sum(0)
        self.xx += X.T @ X; self.xy += X.T @ Y
        self.yy_diag += (Y * Y).sum(0)

    def centered(self):
        mx = self.sx / self.n; my = self.sy / self.n
        Cxx = self.xx / self.n - torch.outer(mx, mx)
        Cxy = self.xy / self.n - torch.outer(mx, my)
        vy = self.yy_diag / self.n - my * my
        return mx, my, Cxx, Cxy, vy

    def solve(self, lam_rel: float):
        """lam_rel is relative to mean eigenvalue of Cxx (scale-free)."""
        mx, my, Cxx, Cxy, _ = self.centered()
        lam = lam_rel * torch.trace(Cxx) / Cxx.shape[0]
        W = torch.linalg.solve(Cxx + lam * torch.eye(Cxx.shape[0], dtype=Cxx.dtype), Cxy)
        b = my - mx @ W
        return W.float(), b.float()

    def train_r2(self, W, b):
        """Fraction of total (summed over dims) variance of Y explained on the fitting data."""
        mx, my, Cxx, Cxy, vy = self.centered()
        W = W.double()
        # E||Yc - Xc W||^2 = tr(Cyy) - 2 tr(W^T Cxy) + tr(W^T Cxx W)
        resid = vy.sum() - 2 * (W * Cxy).sum() + (W * (Cxx @ W)).sum()
        return float(1 - resid / vy.sum())


def apply(X, W, b):
    return X @ W + b
