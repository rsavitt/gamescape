"""Replicator dynamics and fixed-point analysis for 2x2 symmetric games."""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class PayoffMatrix:
    """2x2 symmetric game payoff matrix.

    Rows = focal player's strategy, Columns = opponent's strategy.
    Entry (i, j) = payoff to focal player using strategy i against opponent using strategy j.

    For a symmetric game:
        Player uses C vs C: a    Player uses C vs D: b
        Player uses D vs C: c    Player uses D vs D: d
    """

    a: float  # (C, C)
    b: float  # (C, D)
    c: float  # (D, C)
    d: float  # (D, D)

    @property
    def matrix(self) -> np.ndarray:
        return np.array([[self.a, self.b], [self.c, self.d]])

    def fitness(self, x: float) -> tuple[float, float]:
        """Fitness of each strategy given population fraction x of strategy 0 (cooperators)."""
        f0 = self.a * x + self.b * (1 - x)
        f1 = self.c * x + self.d * (1 - x)
        return f0, f1

    def avg_fitness(self, x: float) -> float:
        f0, f1 = self.fitness(x)
        return x * f0 + (1 - x) * f1


# --- Classic 2x2 games ---

PRISONERS_DILEMMA = PayoffMatrix(a=3, b=0, c=5, d=1)
STAG_HUNT = PayoffMatrix(a=4, b=0, c=3, d=2)
HAWK_DOVE = PayoffMatrix(a=0, b=3, c=5, d=1)
COORDINATION = PayoffMatrix(a=4, b=0, c=0, d=3)
HARMONY = PayoffMatrix(a=4, b=3, c=2, d=1)

CLASSIC_GAMES: dict[str, PayoffMatrix] = {
    "prisoners-dilemma": PRISONERS_DILEMMA,
    "stag-hunt": STAG_HUNT,
    "hawk-dove": HAWK_DOVE,
    "coordination": COORDINATION,
    "harmony": HARMONY,
}


@dataclass(frozen=True)
class FixedPoint:
    """A fixed point of the replicator dynamics."""

    x: float  # fraction of cooperators
    stable: bool
    label: str  # "interior", "all-C", "all-D"


def replicator_dx(game: PayoffMatrix, x: float) -> float:
    """Replicator equation: dx/dt = x(1-x)(f0 - f1).

    x = fraction playing strategy 0 (cooperate).
    """
    if x <= 0 or x >= 1:
        return 0.0
    f0, f1 = game.fitness(x)
    return x * (1 - x) * (f0 - f1)


def find_fixed_points(game: PayoffMatrix) -> list[FixedPoint]:
    """Find all fixed points of the replicator dynamics."""
    points: list[FixedPoint] = []

    # Boundary fixed points are always present
    # Stability: check sign of dx/dt near the boundary
    eps = 1e-8
    dx_near_0 = replicator_dx(game, eps)
    dx_near_1 = replicator_dx(game, 1 - eps)

    points.append(FixedPoint(x=0.0, stable=dx_near_0 < 0, label="all-D"))
    points.append(FixedPoint(x=1.0, stable=dx_near_1 > 0, label="all-C"))

    # Interior fixed point: f0(x*) = f1(x*) => x* = (d - b) / (a - b - c + d)
    denom = game.a - game.b - game.c + game.d
    if abs(denom) > 1e-12:
        x_star = (game.d - game.b) / denom
        if 0 < x_star < 1:
            # Stability: check derivative of dx/dt at x*
            # d(dx/dt)/dx at interior = (1-2x*)(f0-f1) + x*(1-x*)(f0'-f1')
            # At fixed point f0=f1, so first term vanishes
            # f0' - f1' = a - b - c + d = denom
            deriv = x_star * (1 - x_star) * denom
            # But we also need the (1-2x) term evaluated properly
            # Actually: d/dx[x(1-x)(f0-f1)] at f0=f1:
            # = (1-2x*)*0 + x*(1-x*) * d(f0-f1)/dx
            # d(f0-f1)/dx = (a-b) - (c-d) = a - b - c + d = denom
            stable = deriv < 0
            points.append(FixedPoint(x=x_star, stable=stable, label="interior"))

    return sorted(points, key=lambda p: p.x)


def trajectory(game: PayoffMatrix, x0: float, dt: float = 0.01, steps: int = 2000) -> list[float]:
    """Simulate replicator dynamics from initial condition x0."""
    xs = [x0]
    x = x0
    for _ in range(steps):
        dx = replicator_dx(game, x)
        x = x + dt * dx
        x = max(0.0, min(1.0, x))
        xs.append(x)
        if abs(dx) < 1e-10:
            break
    return xs


def classify_game(game: PayoffMatrix) -> str:
    """Classify a 2x2 symmetric game by its dynamics."""
    fps = find_fixed_points(game)
    interior = [fp for fp in fps if fp.label == "interior"]
    all_c = next(fp for fp in fps if fp.label == "all-C")
    all_d = next(fp for fp in fps if fp.label == "all-D")

    if all_c.stable and not all_d.stable and not interior:
        return "dominant-cooperate"
    if all_d.stable and not all_c.stable and not interior:
        return "dominant-defect"
    if all_c.stable and all_d.stable and interior and not interior[0].stable:
        return "coordination"
    if not all_c.stable and not all_d.stable and interior and interior[0].stable:
        return "coexistence"
    if all_c.stable and all_d.stable and not interior:
        return "bistable"
    return "other"
