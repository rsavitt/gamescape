"""Tests for ASCII rendering."""

from gamescape.dynamics import PRISONERS_DILEMMA, HAWK_DOVE
from gamescape.render import render_flow_line, render_analysis, render_payoff_table


class TestRenderFlowLine:
    def test_produces_string(self):
        line = render_flow_line(PRISONERS_DILEMMA, color=False)
        assert isinstance(line, str)
        assert "all-D" in line
        assert "all-C" in line

    def test_contains_fixed_points(self):
        line = render_flow_line(HAWK_DOVE, color=False)
        assert "@" in line  # stable interior fixed point


class TestRenderAnalysis:
    def test_full_output(self):
        output = render_analysis(PRISONERS_DILEMMA, color=False)
        assert "Payoff Matrix" in output
        assert "Classification" in output
        assert "Fixed Points" in output
        assert "Phase Flow" in output
        assert "dominant-defect" in output

    def test_color_output_no_crash(self):
        output = render_analysis(HAWK_DOVE, color=True)
        assert len(output) > 0


class TestRenderPayoffTable:
    def test_values_present(self):
        table = render_payoff_table(PRISONERS_DILEMMA, color=False)
        assert "3.0" in table
        assert "5.0" in table
