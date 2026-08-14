# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Fixtures shared by the cycle capacity contract tests on both API surfaces.

The session tests live in app/test_cycle_capacity_app.py and the X-API-Key tests
live in api/test_cycle_capacity_api.py. Both need the same project, estimate, and
cycle, so the fixtures sit here.
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from plane.db.models import (
    Cycle,
    CycleIssue,
    DraftIssue,
    Estimate,
    EstimatePoint,
    Issue,
    Project,
    ProjectMember,
    State,
    User,
    WorkspaceMember,
)

# Every point value that the capacity tests compose their sums from.
CAPACITY_POINT_VALUES = [1, 2, 3, 5, 8, 13, 20, 40]


@pytest.fixture
def capacity_project(db, workspace, create_user):
    """A project with cycles enabled, owned by the session user.

    The project-create view builds the default states inline, so a project made
    with the model has none. This fixture builds the one state that the tests need.
    """
    project = Project.objects.create(
        name="Capacity Project",
        identifier="CAP",
        workspace=workspace,
        created_by=create_user,
        cycle_view=True,
    )
    ProjectMember.objects.create(project=project, member=create_user, role=20, is_active=True)
    State.objects.create(
        name="Todo",
        project=project,
        workspace=workspace,
        group="backlog",
        default=True,
    )
    return project


@pytest.fixture
def points_estimate(db, workspace, capacity_project, create_user):
    """A points-type estimate on the project, with one point per value in the list."""
    estimate = Estimate.objects.create(
        name="Story points",
        project=capacity_project,
        workspace=workspace,
        type="points",
        created_by=create_user,
    )
    for key, value in enumerate(CAPACITY_POINT_VALUES):
        EstimatePoint.objects.create(
            estimate=estimate,
            project=capacity_project,
            workspace=workspace,
            key=key,
            value=str(value),
            created_by=create_user,
        )
    capacity_project.estimate = estimate
    capacity_project.save()
    return estimate


@pytest.fixture
def active_cycle(db, workspace, capacity_project, create_user):
    """A cycle whose dates bracket the current time."""
    now = timezone.now()
    return Cycle.objects.create(
        name="Sprint 14",
        project=capacity_project,
        workspace=workspace,
        owned_by=create_user,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=13),
    )


@pytest.fixture
def upcoming_cycle(db, workspace, capacity_project, create_user):
    """A cycle that starts in the future. The gate never runs for it."""
    now = timezone.now()
    return Cycle.objects.create(
        name="Sprint 15",
        project=capacity_project,
        workspace=workspace,
        owned_by=create_user,
        start_date=now + timedelta(days=14),
        end_date=now + timedelta(days=28),
    )


@pytest.fixture
def closed_cycle(db, workspace, capacity_project, create_user):
    """A cycle that ended. The transfer route moves its incomplete work items out."""
    now = timezone.now()
    return Cycle.objects.create(
        name="Sprint 13",
        project=capacity_project,
        workspace=workspace,
        owned_by=create_user,
        start_date=now - timedelta(days=28),
        end_date=now - timedelta(days=1),
    )


@pytest.fixture
def make_draft(db, workspace, capacity_project, create_user):
    """Return a factory that creates a draft work item in the project."""

    def _make(name="Draft work item"):
        return DraftIssue.objects.create(
            name=name,
            workspace=workspace,
            project=capacity_project,
            created_by=create_user,
        )

    return _make


@pytest.fixture
def make_issue(db, workspace, capacity_project, create_user, points_estimate):
    """Return a factory that creates a work item worth the given points."""
    state = State.objects.filter(project=capacity_project).first()

    def _make(points, in_cycle=None):
        estimate_point = EstimatePoint.objects.filter(estimate=points_estimate, value=str(points)).first()
        assert estimate_point is not None, f"No estimate point is worth {points}"
        issue = Issue.objects.create(
            name=f"Work item worth {points}",
            workspace=workspace,
            project=capacity_project,
            state=state,
            estimate_point=estimate_point,
            created_by=create_user,
        )
        if in_cycle is not None:
            CycleIssue.objects.create(
                issue=issue,
                cycle=in_cycle,
                project=capacity_project,
                workspace=workspace,
                created_by=create_user,
            )
        return issue

    return _make


@pytest.fixture
def guest_client(db, api_client, workspace, capacity_project):
    """A client for a user who is a guest at the workspace level and the project level.

    `allow_permission` carries a workspace-admin bypass, so a guest at one level only
    still passes the check.
    """
    uid = uuid4().hex[:8]
    guest = User.objects.create(
        email=f"guest-{uid}@plane.so",
        username=f"guest_{uid}",
        first_name="Guest",
        last_name="User",
    )
    WorkspaceMember.objects.create(workspace=workspace, member=guest, role=5)
    ProjectMember.objects.create(project=capacity_project, member=guest, role=5, is_active=True)
    api_client.force_authenticate(user=guest)
    return api_client


def set_capacity(cycle, capacity, mode="warn"):
    """Put a capacity on the cycle without going through the API."""
    cycle.capacity = capacity
    cycle.capacity_mode = mode
    cycle.save(update_fields=["capacity", "capacity_mode"])
    return cycle
