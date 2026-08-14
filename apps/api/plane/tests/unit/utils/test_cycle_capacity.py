# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for the cycle capacity evaluator.

The spec is docs/features/new/cycle-capacity-threshold.md. Two rules carry the
whole feature:

1. Rule zero. A NULL capacity short circuits before the aggregate query.
2. The trip wire uses ">". A sum that equals the capacity is not over it.

Every test here builds unsaved model instances, so no row reaches the database.
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from plane.db.models import Cycle, Estimate, Project
from plane.db.models.cycle import CycleCapacityMode
from plane.utils.cycle_capacity import build_capacity_status, evaluate_cycle_capacity


def make_project(estimate_type="points"):
    """A project instance that holds an estimate, with no database row.

    The estimate carries an id, so that `project.estimate_id` is set and the guard
    that reads `project.estimate.type` runs. Django caches the assigned instance, so
    reading it back costs no query.
    """
    project = Project(name="Capacity Project", identifier="CAP", timezone="UTC")
    if estimate_type is not None:
        project.estimate = Estimate(id=uuid4(), name="Story points", type=estimate_type)
    return project


def make_cycle(capacity=None, mode=CycleCapacityMode.WARN, active=True):
    """A cycle instance with no database row. Active by default."""
    now = timezone.now()
    if active:
        start_date, end_date = now - timedelta(days=1), now + timedelta(days=13)
    else:
        start_date, end_date = now + timedelta(days=7), now + timedelta(days=21)
    return Cycle(
        name="Sprint 14",
        capacity=capacity,
        capacity_mode=mode,
        start_date=start_date,
        end_date=end_date,
    )


@pytest.mark.unit
class TestRuleZero:
    """A cycle with no capacity costs nothing. The evaluator returns before the query."""

    @pytest.mark.django_db
    def test_verdict_is_not_set_when_capacity_is_null(self):
        result = evaluate_cycle_capacity(cycle=make_cycle(capacity=None), project=make_project())

        assert result["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_no_query_runs_when_capacity_is_null(self, django_assert_num_queries):
        with django_assert_num_queries(0):
            evaluate_cycle_capacity(cycle=make_cycle(capacity=None), project=make_project())

    @pytest.mark.django_db
    def test_write_allowed_is_true_when_capacity_is_null(self):
        result = evaluate_cycle_capacity(cycle=make_cycle(capacity=None), project=make_project(), incoming_points=999)

        assert result["write_allowed"] is True

    @pytest.mark.django_db
    def test_verdict_is_not_set_when_project_estimate_is_categories(self):
        result = evaluate_cycle_capacity(
            cycle=make_cycle(capacity=40), project=make_project(estimate_type="categories")
        )

        assert result["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_no_query_runs_when_project_estimate_is_categories(self, django_assert_num_queries):
        with django_assert_num_queries(0):
            evaluate_cycle_capacity(cycle=make_cycle(capacity=40), project=make_project(estimate_type="categories"))

    @pytest.mark.django_db
    def test_verdict_is_not_set_when_the_project_has_no_estimate(self):
        result = evaluate_cycle_capacity(cycle=make_cycle(capacity=40), project=make_project(estimate_type=None))

        assert result["verdict"] == "not_set"


@pytest.mark.unit
class TestTheActiveCycleRule:
    """The gate runs for the active cycle only."""

    @pytest.mark.django_db
    def test_verdict_is_not_set_for_an_upcoming_cycle(self):
        result = evaluate_cycle_capacity(cycle=make_cycle(capacity=40, active=False), project=make_project())

        assert result["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_no_query_runs_for_an_upcoming_cycle(self, django_assert_num_queries):
        with django_assert_num_queries(0):
            evaluate_cycle_capacity(cycle=make_cycle(capacity=40, active=False), project=make_project())

    @pytest.mark.django_db
    def test_verdict_is_not_set_for_a_completed_cycle(self):
        now = timezone.now()
        cycle = make_cycle(capacity=40)
        cycle.start_date = now - timedelta(days=30)
        cycle.end_date = now - timedelta(days=1)

        result = evaluate_cycle_capacity(cycle=cycle, project=make_project())

        assert result["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_verdict_is_not_set_for_a_cycle_with_no_dates(self):
        cycle = make_cycle(capacity=40)
        cycle.start_date = None
        cycle.end_date = None

        result = evaluate_cycle_capacity(cycle=cycle, project=make_project())

        assert result["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_verdict_is_not_set_for_an_archived_cycle(self):
        cycle = make_cycle(capacity=40)
        cycle.archived_at = timezone.now()

        result = evaluate_cycle_capacity(cycle=cycle, project=make_project())

        assert result["verdict"] == "not_set"


@pytest.mark.unit
class TestTheTripWire:
    """The three worked examples from the spec, plus the two modes."""

    def test_verdict_is_ok_at_28_of_40(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.WARN, used_points=28)

        assert result["verdict"] == "ok"
        assert result["write_allowed"] is True

    def test_verdict_is_ok_at_40_of_40(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.WARN, used_points=40)

        assert result["verdict"] == "ok"

    def test_verdict_is_warn_at_41_of_40_in_warn_mode(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.WARN, used_points=41)

        assert result["verdict"] == "warn"

    def test_verdict_is_block_at_41_of_40_in_block_mode(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.BLOCK, used_points=41)

        assert result["verdict"] == "block"

    def test_the_result_carries_every_number(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.BLOCK, used_points=38, incoming_points=5)

        assert result == {
            "capacity": 40,
            "mode": "block",
            "used_points": 38,
            "incoming_points": 5,
            "projected_points": 43,
            "verdict": "ok",
            "write_allowed": False,
        }


@pytest.mark.unit
class TestWriteAllowed:
    """write_allowed describes the write in front of it, not the cycle."""

    def test_write_allowed_when_projected_equals_capacity_in_block_mode(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.BLOCK, used_points=35, incoming_points=5)

        assert result["write_allowed"] is True

    def test_write_refused_when_projected_passes_capacity_in_block_mode(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.BLOCK, used_points=38, incoming_points=5)

        assert result["write_allowed"] is False

    def test_write_allowed_when_projected_passes_capacity_in_warn_mode(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.WARN, used_points=38, incoming_points=5)

        assert result["write_allowed"] is True

    def test_write_allowed_when_incoming_points_are_negative(self):
        result = build_capacity_status(capacity=40, mode=CycleCapacityMode.BLOCK, used_points=44, incoming_points=-5)

        assert result["write_allowed"] is True
        assert result["verdict"] == "block"

    def test_capacity_of_zero_refuses_any_add_worth_a_point(self):
        allowed = build_capacity_status(capacity=0, mode=CycleCapacityMode.BLOCK, used_points=0)
        refused = build_capacity_status(capacity=0, mode=CycleCapacityMode.BLOCK, used_points=0, incoming_points=1)

        assert allowed["write_allowed"] is True
        assert allowed["verdict"] == "ok"
        assert refused["write_allowed"] is False
