# gamescape

Visualize evolutionary game theory dynamics in your terminal. Computes replicator equations, finds fixed points, classifies games, and renders ASCII phase portraits.

## Install

```bash
pip install -e .
```

## Usage

```bash
# Analyze a classic game
gamescape prisoners-dilemma
gamescape stag-hunt
gamescape hawk-dove
gamescape coordination
gamescape harmony

# Custom payoff matrix (CC, CD, DC, DD)
gamescape --matrix 3,0,5,1

# List available games
gamescape --list

# Disable colors
gamescape hawk-dove --no-color
```

## What it shows

- **Payoff matrix** — the 2x2 symmetric game
- **Classification** — dominant-cooperate, dominant-defect, coordination, coexistence, bistable
- **Fixed points** — boundary and interior equilibria with stability (`@` = stable, `o` = unstable)
- **Phase flow** — 1D flow line showing direction of replicator dynamics
- **Trajectories** — x(t) plot from 5 initial conditions converging to attractors

## Example output

```
  Classification: coexistence

  Fixed Points:
    o x=0.0000 (all-D, unstable)
    @ x=0.2857 (interior, stable)
    o x=1.0000 (all-C, unstable)

  Phase Flow:
  all-D |o>>>>>>>>>>>>>>>>@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<o| all-C
```

## As a library

```python
from gamescape.dynamics import PayoffMatrix, find_fixed_points, classify_game, trajectory

game = PayoffMatrix(a=3, b=0, c=5, d=1)  # Prisoner's Dilemma
print(classify_game(game))  # "dominant-defect"

for fp in find_fixed_points(game):
    print(f"x={fp.x:.2f} stable={fp.stable} ({fp.label})")

traj = trajectory(game, x0=0.5)  # simulate from x=0.5
```

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
