"""ASCII rendering of phase portraits and dynamics."""

from __future__ import annotations

from gamescape.dynamics import (
    PayoffMatrix,
    FixedPoint,
    find_fixed_points,
    replicator_dx,
    trajectory,
    classify_game,
)

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def _arrow(dx: float) -> str:
    """Map a derivative to an arrow character."""
    if dx > 0.1:
        return ">>>"
    elif dx > 0.01:
        return ">>"
    elif dx > 0.001:
        return ">"
    elif dx > 0:
        return ">"
    elif dx < -0.1:
        return "<<<"
    elif dx < -0.01:
        return "<<"
    elif dx < -0.001:
        return "<"
    elif dx < 0:
        return "<"
    return "."


def render_flow_line(game: PayoffMatrix, width: int = 60, color: bool = True) -> str:
    """Render a 1D flow line showing direction of replicator dynamics.

    x=0 (all-D) on left, x=1 (all-C) on right.
    """
    fps = find_fixed_points(game)
    cells: list[str] = []

    for i in range(width):
        x = i / (width - 1)
        dx = replicator_dx(game, x)

        # Check if near a fixed point
        near_fp = None
        for fp in fps:
            if abs(x - fp.x) < 0.5 / width:
                near_fp = fp
                break

        if near_fp is not None:
            if color:
                if near_fp.stable:
                    cells.append(f"{GREEN}{BOLD}@{RESET}")
                else:
                    cells.append(f"{RED}{BOLD}o{RESET}")
            else:
                cells.append("@" if near_fp.stable else "o")
        else:
            arrow = _arrow(dx)
            if color:
                if dx > 0:
                    cells.append(f"{CYAN}{arrow[-1]}{RESET}")
                elif dx < 0:
                    cells.append(f"{MAGENTA}{arrow[-1]}{RESET}")
                else:
                    cells.append(f"{DIM}.{RESET}")
            else:
                cells.append(arrow[-1])

    line = "".join(cells)
    return f"  all-D |{line}| all-C"


def render_trajectory_plot(
    game: PayoffMatrix, x0_values: list[float] | None = None,
    width: int = 70, height: int = 20, color: bool = True,
) -> str:
    """Render x(t) trajectories as an ASCII plot."""
    if x0_values is None:
        x0_values = [0.1, 0.3, 0.5, 0.7, 0.9]

    trajectories = [trajectory(game, x0, steps=200) for x0 in x0_values]
    max_t = max(len(t) for t in trajectories)

    # Build the grid
    grid = [[" " for _ in range(width)] for _ in range(height)]
    symbols = ["*", "+", "~", "#", "^", "=", "%", "&"]

    for idx, traj in enumerate(trajectories):
        sym = symbols[idx % len(symbols)]
        for t_idx, x_val in enumerate(traj):
            col = int(t_idx / max_t * (width - 1))
            row = height - 1 - int(x_val * (height - 1))
            row = max(0, min(height - 1, row))
            col = max(0, min(width - 1, col))
            grid[row][col] = sym

    lines: list[str] = []
    lines.append(f"  x(t) trajectories from {len(x0_values)} initial conditions")
    lines.append(f"  {'':>4} {'':─<{width}}")

    for r in range(height):
        x_label = f"{1.0 - r / (height - 1):.1f}"
        row_str = "".join(grid[r])
        if color:
            # Colorize each trajectory symbol
            colored = []
            colors = [CYAN, GREEN, YELLOW, MAGENTA, RED, BLUE, CYAN, GREEN]
            for ch in row_str:
                if ch in symbols:
                    c = colors[symbols.index(ch) % len(colors)]
                    colored.append(f"{c}{ch}{RESET}")
                else:
                    colored.append(ch)
            row_str = "".join(colored)
        lines.append(f"  {x_label:>4}|{row_str}|")

    lines.append(f"  {'':>4} {'':─<{width}}")
    lines.append(f"  {'':>4} t=0{'':>{width - 6}}t=T")

    # Legend
    lines.append("")
    legend_parts = []
    for idx, x0 in enumerate(x0_values):
        sym = symbols[idx % len(symbols)]
        if color:
            c = [CYAN, GREEN, YELLOW, MAGENTA, RED, BLUE, CYAN, GREEN][idx % 8]
            legend_parts.append(f"{c}{sym}{RESET} x0={x0:.1f}")
        else:
            legend_parts.append(f"{sym} x0={x0:.1f}")
    lines.append("  " + "  ".join(legend_parts))

    return "\n".join(lines)


def render_payoff_table(game: PayoffMatrix, color: bool = True) -> str:
    """Render the payoff matrix as a formatted table."""
    header = f"{'':>12}{'Cooperate':>12}{'Defect':>12}"
    row_c = f"{'Cooperate':>12}"
    row_d = f"{'Defect':>12}"

    if color:
        row_c += f"{GREEN}{game.a:>12.1f}{RESET}{RED}{game.b:>12.1f}{RESET}"
        row_d += f"{YELLOW}{game.c:>12.1f}{RESET}{BLUE}{game.d:>12.1f}{RESET}"
    else:
        row_c += f"{game.a:>12.1f}{game.b:>12.1f}"
        row_d += f"{game.c:>12.1f}{game.d:>12.1f}"

    return f"  {header}\n  {row_c}\n  {row_d}"


def render_analysis(game: PayoffMatrix, color: bool = True) -> str:
    """Full analysis output."""
    fps = find_fixed_points(game)
    classification = classify_game(game)

    lines: list[str] = []

    # Title
    if color:
        lines.append(f"\n{BOLD}  Game Analysis{RESET}")
    else:
        lines.append("\n  Game Analysis")
    lines.append("  " + "=" * 40)

    # Payoff matrix
    lines.append("")
    if color:
        lines.append(f"  {BOLD}Payoff Matrix:{RESET}")
    else:
        lines.append("  Payoff Matrix:")
    lines.append(render_payoff_table(game, color))

    # Classification
    lines.append("")
    if color:
        lines.append(f"  {BOLD}Classification:{RESET} {CYAN}{classification}{RESET}")
    else:
        lines.append(f"  Classification: {classification}")

    # Fixed points
    lines.append("")
    if color:
        lines.append(f"  {BOLD}Fixed Points:{RESET}")
    else:
        lines.append("  Fixed Points:")
    for fp in fps:
        stability = "stable" if fp.stable else "unstable"
        if color:
            s_color = GREEN if fp.stable else RED
            lines.append(
                f"    {s_color}{'@' if fp.stable else 'o'}{RESET} "
                f"x={fp.x:.4f} ({fp.label}, {s_color}{stability}{RESET})"
            )
        else:
            lines.append(
                f"    {'@' if fp.stable else 'o'} "
                f"x={fp.x:.4f} ({fp.label}, {stability})"
            )

    # Flow line
    lines.append("")
    if color:
        lines.append(f"  {BOLD}Phase Flow:{RESET}")
    else:
        lines.append("  Phase Flow:")
    lines.append(render_flow_line(game, color=color))

    # Trajectory plot
    lines.append("")
    if color:
        lines.append(f"  {BOLD}Trajectories:{RESET}")
    else:
        lines.append("  Trajectories:")
    lines.append(render_trajectory_plot(game, color=color))

    lines.append("")
    return "\n".join(lines)
