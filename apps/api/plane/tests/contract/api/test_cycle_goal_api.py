# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Contract tests for the cycle goal field on the external API surface.

The spec requires the `X-API-Key` surface to return the goal. Without this file the
`CycleCreateSerializer` edit in `plane/api/serializers/cycle.py` is unproven, and
the two surfaces are not symmetric in the way the spec claims.

The external surface behaves differently from `plane/app/`. It serialises its
responses, so one serializer edit covers it, where `plane/app/` needed the field in
seven hand-written `.values(...)` lists.

Spec: docs/features/new/cycle-goal-2026-08-14.md
"""

import pytest
from rest_framework import status

from plane.db.models import Project, ProjectMember

GOAL = "Ship the export pipeline behind a flag"
GOAL_OVER_LIMIT = "x" * 256


@pytest.fixture
def project(db, workspace, create_user):
    project = Project.objects.create(
        name="Goal API Project",
        identifier="GAP",
        workspace=workspace,
        created_by=create_user,
        cycle_view=True,
    )
    ProjectMember.objects.create(project=project, member=create_user, role=20, is_active=True)
    return project


def cycles_url(workspace_slug, project_id):
    return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/cycles/"


@pytest.mark.contract
class TestCycleGoalExternalAPI:
    """The token surface must accept and return the goal, like the session surface."""

    @pytest.mark.django_db
    def test_create_accepts_and_returns_the_goal(self, api_key_client, workspace, project):
        url = cycles_url(workspace.slug, project.id)

        response = api_key_client.post(url, {"name": "Sprint 14", "goal": GOAL}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, (
            f"Got {response.status_code}: {getattr(response, 'data', None)!r}"
        )
        assert response.data.get("goal") == GOAL, (
            "The external surface does not return goal, so the CycleCreateSerializer "
            f"field list was not updated. Body: {response.data!r}"
        )

    @pytest.mark.django_db
    def test_the_list_route_returns_the_goal(self, api_key_client, workspace, project):
        url = cycles_url(workspace.slug, project.id)
        api_key_client.post(url, {"name": "Sprint 14", "goal": GOAL}, format="json")

        response = api_key_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        rows = response.data.get("results", response.data)
        assert rows, f"The list route returned nothing. Body: {response.data!r}"
        assert rows[0].get("goal") == GOAL, (
            f"The list route omits goal. Row: {rows[0]!r}"
        )

    @pytest.mark.django_db
    def test_a_goal_over_the_column_limit_is_rejected(self, api_key_client, workspace, project):
        url = cycles_url(workspace.slug, project.id)

        response = api_key_client.post(
            url, {"name": "Sprint 14", "goal": GOAL_OVER_LIMIT}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f"A 256 character goal must be refused. Got {response.status_code}: "
            f"{getattr(response, 'data', None)!r}"
        )
