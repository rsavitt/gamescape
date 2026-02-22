"""CLI entry point for gamescape."""

from __future__ import annotations

import argparse
import sys

from gamescape.dynamics import PayoffMatrix, CLASSIC_GAMES
from gamescape.render import render_analysis


def parse_matrix(s: str) -> PayoffMatrix:
    """Parse 'a,b,c,d' into a PayoffMatrix."""
    parts = s.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"Expected 4 comma-separated values (a,b,c,d), got {len(parts)}"
        )
    try:
        vals = [float(p.strip()) for p in parts]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Non-numeric value in matrix: {e}")
    return PayoffMatrix(*vals)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="gamescape",
        description="Visualize evolutionary game theory dynamics in your terminal.",
        epilog="Examples:\n"
        "  gamescape prisoners-dilemma\n"
        "  gamescape --matrix 3,0,5,1\n"
        "  gamescape stag-hunt --no-color\n"
        "  gamescape --list\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "game",
        nargs="?",
        choices=list(CLASSIC_GAMES.keys()),
        help="Name of a classic 2x2 game",
    )
    parser.add_argument(
        "--matrix", "-m",
        type=str,
        help="Custom payoff matrix as 'a,b,c,d' (row-major: CC,CD,DC,DD)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available classic games",
    )

    args = parser.parse_args(argv)

    if args.list:
        print("\nAvailable classic games:")
        for name, game in CLASSIC_GAMES.items():
            m = game.matrix
            print(f"  {name:20s}  [{m[0,0]:.0f},{m[0,1]:.0f},{m[1,0]:.0f},{m[1,1]:.0f}]")
        print()
        return

    if args.matrix:
        game = parse_matrix(args.matrix)
    elif args.game:
        game = CLASSIC_GAMES[args.game]
    else:
        parser.print_help()
        sys.exit(1)

    output = render_analysis(game, color=not args.no_color)
    print(output)


if __name__ == "__main__":
    main()
