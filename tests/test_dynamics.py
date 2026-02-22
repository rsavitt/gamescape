"""Tests for replicator dynamics and fixed-point analysis."""

import pytest
from gamescape.dynamics import (
    PayoffMatrix,
    replicator_dx,
    find_fixed_points,
    trajectory,
    classify_game,
    PRISONERS_DILEMMA,
    STAG_HUNT,
    HAWK_DOVE,
    COORDINATION,
    HARMONY,
)


class TestPayoffMatrix:
    def test_fitness_symmetric(self):
        game = PayoffMatrix(a=3, b=0, c=5, d=1)
        f0, f1 = game.fitness(0.5)
        assert f0 == pytest.approx(1.5)  # 3*0.5 + 0*0.5
        assert f1 == pytest.approx(3.0)  # 5*0.5 + 1*0.5

    def test_avg_fitness(self):
        game = PayoffMatrix(a=3, b=0, c=5, d=1)
        avg = game.avg_fitness(0.5)
        # 0.5*1.5 + 0.5*3.0 = 2.25
        assert avg == pytest.approx(2.25)


class TestReplicatorDx:
    def test_boundary_zero(self):
        """dx/dt = 0 at boundaries x=0 and x=1."""
        assert replicator_dx(PRISONERS_DILEMMA, 0.0) == 0.0
        assert replicator_dx(PRISONERS_DILEMMA, 1.0) == 0.0

    def test_prisoners_dilemma_defection_dominates(self):
        """In PD, defection dominates: dx/dt < 0 for all interior x."""
        for x in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert replicator_dx(PRISONERS_DILEMMA, x) < 0

    def test_harmony_cooperation_dominates(self):
        """In Harmony game, cooperation dominates: dx/dt > 0."""
        for x in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert replicator_dx(HARMONY, x) > 0


class TestFixedPoints:
    def test_pd_fixed_points(self):
        fps = find_fixed_points(PRISONERS_DILEMMA)
        labels = {fp.label: fp for fp in fps}
        assert "all-D" in labels
        assert "all-C" in labels
        assert labels["all-D"].stable is True
        assert labels["all-C"].stable is False
        # No interior fixed point in PD
        assert "interior" not in labels

    def test_hawk_dove_interior(self):
        fps = find_fixed_points(HAWK_DOVE)
        interior = [fp for fp in fps if fp.label == "interior"]
        assert len(interior) == 1
        assert interior[0].stable is True
        assert 0 < interior[0].x < 1

    def test_stag_hunt_bistable(self):
        fps = find_fixed_points(STAG_HUNT)
        labels = {fp.label: fp for fp in fps}
        assert labels["all-C"].stable is True
        assert labels["all-D"].stable is True
        interior = [fp for fp in fps if fp.label == "interior"]
        assert len(interior) == 1
        assert interior[0].stable is False

    def test_harmony_all_c_stable(self):
        fps = find_fixed_points(HARMONY)
        labels = {fp.label: fp for fp in fps}
        assert labels["all-C"].stable is True
        assert labels["all-D"].stable is False


class TestTrajectory:
    def test_pd_converges_to_zero(self):
        traj = trajectory(PRISONERS_DILEMMA, 0.5, steps=5000)
        assert traj[-1] < 0.01

    def test_harmony_converges_to_one(self):
        traj = trajectory(HARMONY, 0.5, steps=5000)
        assert traj[-1] > 0.99

    def test_trajectory_stays_in_bounds(self):
        for game in [PRISONERS_DILEMMA, STAG_HUNT, HAWK_DOVE]:
            traj = trajectory(game, 0.5)
            assert all(0 <= x <= 1 for x in traj)


class TestClassification:
    def test_pd_is_dominant_defect(self):
        assert classify_game(PRISONERS_DILEMMA) == "dominant-defect"

    def test_harmony_is_dominant_cooperate(self):
        assert classify_game(HARMONY) == "dominant-cooperate"

    def test_hawk_dove_is_coexistence(self):
        assert classify_game(HAWK_DOVE) == "coexistence"

    def test_stag_hunt_is_coordination(self):
        assert classify_game(STAG_HUNT) == "coordination"
