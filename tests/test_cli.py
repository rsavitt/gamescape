"""Tests for CLI entry point."""

import pytest
from gamescape.cli import main, parse_matrix
from gamescape.dynamics import PayoffMatrix


class TestParseMatrix:
    def test_valid(self):
        m = parse_matrix("3,0,5,1")
        assert m == PayoffMatrix(3, 0, 5, 1)

    def test_with_spaces(self):
        m = parse_matrix("3, 0, 5, 1")
        assert m == PayoffMatrix(3, 0, 5, 1)

    def test_floats(self):
        m = parse_matrix("3.5,0.1,5.2,1.0")
        assert m.a == pytest.approx(3.5)

    def test_wrong_count(self):
        with pytest.raises(Exception):
            parse_matrix("3,0,5")


class TestCLI:
    def test_list(self, capsys):
        main(["--list"])
        captured = capsys.readouterr()
        assert "prisoners-dilemma" in captured.out
        assert "stag-hunt" in captured.out

    def test_named_game(self, capsys):
        main(["prisoners-dilemma", "--no-color"])
        captured = capsys.readouterr()
        assert "dominant-defect" in captured.out

    def test_custom_matrix(self, capsys):
        main(["--matrix", "3,0,5,1", "--no-color"])
        captured = capsys.readouterr()
        assert "Fixed Points" in captured.out

    def test_no_args_exits(self):
        with pytest.raises(SystemExit):
            main([])
