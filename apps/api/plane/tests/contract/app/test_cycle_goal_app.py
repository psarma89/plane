# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Contract tests for the cycle goal field.

The first test is the one that matters. ``CycleSerializer`` in
``plane/app/serializers/cycle.py`` declares an explicit field list, and only the
write serializer uses ``fields = "__all__"``. So a model field alone makes a write
succeed while the read omits the value. The symptom is a goal that saves and then
disappears on reload, which reads as a frontend defect and is not one.

Asserting the response body, rather than the status code, is what catches that.

Spec: docs/features/new/cycle-goal-2026-08-14.md
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from plane.db.models import Cycle, Project, ProjectMember, User, Workspace, WorkspaceMember

CYCLE_DETAIL_URL = "/api/workspaces/{slug}/projects/{project_id}/cycles/{pk}/"
CYCLE_ARCHIVE_URL = "/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/archive/"
ARCHIVED_CYCLES_URL = "/api/workspaces/{slug}/projects/{project_id}/archived-cycles/"

GOAL = "Ship the export pipeline behind a flag"

# Cycle.goal is CharField(max_length=255), so 256 is the first rejected length.
GOAL_OVER_LIMIT = "x" * 256


@pytest.fixture
def project(db, workspace, create_user):
    """A project in the fixture workspace. ``create_user`` is an active member."""
    project = Project.objects.create(
        name="Goal Project",
        identifier="GP",
        workspace=workspace,
        created_by=create_user,
    )
    ProjectMember.objects.create(project=project, member=create_user, workspace=workspace, role=20)
    return project


@pytest.fixture
def cycle(db, workspace, project, create_user):
    return Cycle.objects.create(
        name="Sprint 14",
        project=project,
        workspace=workspace,
        owned_by=create_user,
    )


@pytest.fixture
def outsider_client(db):
    """A session client for a user in a DIFFERENT workspace.

    The ``workspace`` fixture in conftest.py hardcodes ``slug="test-workspace"``,
    so a second workspace has to be built by hand with a unique slug.
    """
    unique_id = uuid4().hex[:8]
    outsider = User.objects.create(
        email=f"outsider-{unique_id}@plane.so",
        username=f"outsider_{unique_id}",
        first_name="Outsider",
        last_name="User",
    )
    outsider.set_password("test-password")
    outsider.save()
    other_workspace = Workspace.objects.create(
        name=f"Other {unique_id}",
        slug=f"other-{unique_id}",
        owner=outsider,
    )
    WorkspaceMember.objects.create(workspace=other_workspace, member=outsider, role=20)
    client = APIClient()
    client.force_authenticate(user=outsider)
    return client


@pytest.mark.contract
class TestCycleGoal:
    """A cycle goal must survive the round trip, and must respect its column bound."""

    @pytest.mark.django_db
    def test_patch_returns_the_goal_it_just_saved(self, session_client, workspace, project, cycle):
        """The read serializer must expose the field, not only the write serializer."""
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)

        response = session_client.patch(url, {"goal": GOAL}, format="json")

        assert response.status_code == status.HTTP_200_OK, (
            f"Got {response.status_code}: {getattr(response, 'data', None)!r}"
        )
        assert response.data.get("goal") == GOAL, (
            "The goal is missing from the response body, so the read serializer "
            f"does not expose it. Body: {response.data!r}"
        )

    @pytest.mark.django_db
    def test_the_saved_goal_survives_a_reload(self, session_client, workspace, project, cycle):
        """A separate GET must return the value, not just the PATCH response."""
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)
        session_client.patch(url, {"goal": GOAL}, format="json")

        response = session_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("goal") == GOAL, (
            f"The goal did not survive the reload. Body: {response.data!r}"
        )

    @pytest.mark.django_db
    def test_a_goal_over_the_column_limit_is_rejected(
        self, session_client, workspace, project, cycle
    ):
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)

        response = session_client.patch(url, {"goal": GOAL_OVER_LIMIT}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f"A 256 character goal must be refused. Got {response.status_code}: "
            f"{getattr(response, 'data', None)!r}"
        )

    @pytest.mark.django_db
    def test_an_unset_goal_is_the_empty_string(self, session_client, workspace, project, cycle):
        """Absence must be one value, not two.

        The field carries blank=True with a default and no null=True, so an unset
        goal is always "". An earlier version allowed NULL as well, which made a
        reader handle two spellings of the same absence.
        """
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)

        response = session_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Assert the key is PRESENT, then its value. `.get("goal") is None` is true
        # both when the field is absent and when it is null, so that form passes
        # before the field exists and cannot fail for the right reason.
        assert "goal" in response.data, (
            f"The read path does not expose goal at all. Body: {response.data!r}"
        )
        assert response.data["goal"] == "", (
            f"An unset goal must serialise as an empty string. Body: {response.data!r}"
        )

    @pytest.mark.django_db
    def test_clearing_the_goal_stores_the_empty_string_not_null(
        self, session_client, workspace, project, cycle
    ):
        """A client that clears the field must not create a second kind of absence."""
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)
        session_client.patch(url, {"goal": GOAL}, format="json")

        response = session_client.patch(url, {"goal": ""}, format="json")

        assert response.status_code == status.HTTP_200_OK, (
            f"Got {response.status_code}: {getattr(response, 'data', None)!r}"
        )
        assert response.data.get("goal") == "", (
            f"Clearing the goal must yield an empty string. Body: {response.data!r}"
        )
        cycle.refresh_from_db()
        assert cycle.goal == "", f"The column holds {cycle.goal!r}, not an empty string"

    @pytest.mark.django_db
    def test_the_archived_cycle_list_also_returns_the_goal(
        self, session_client, workspace, project, cycle
    ):
        """The archive routes build their own field list, in a different file.

        `plane/app/views/cycle/archive.py` repeats the `.values(...)` list twice.
        Without this test those two edits are proven only by analogy with
        `base.py`, and a field list that is copied by hand is exactly the thing
        that drifts.
        """
        # Set the goal through the API FIRST. A cycle whose end_date is in the past
        # is complete, and the update route rejects an edit to it with a 400.
        detail = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)
        patch_response = session_client.patch(detail, {"goal": GOAL}, format="json")
        assert patch_response.status_code == status.HTTP_200_OK, (
            f"Could not set the goal, so this test cannot judge the archive list: "
            f"{patch_response.status_code} {getattr(patch_response, 'data', None)!r}"
        )

        # Only then backdate it, so that it can be archived.
        # `archive.py` line 592 compares `cycle.end_date >= timezone.now()` with no
        # null guard, and `end_date` is nullable, so archiving a cycle that has no
        # end date raises a 500. That defect predates this branch and is reported
        # separately. Backdating here keeps this test about the goal field.
        #
        # Use queryset.update, not instance.save(). The fixture instance was loaded
        # before the PATCH above, so `cycle.save()` writes every field from that
        # stale copy and silently reverts goal to None.
        Cycle.objects.filter(pk=cycle.pk).update(
            start_date=timezone.now() - timedelta(days=14),
            end_date=timezone.now() - timedelta(days=1),
        )

        archive = CYCLE_ARCHIVE_URL.format(
            slug=workspace.slug, project_id=project.id, cycle_id=cycle.id
        )
        archive_response = session_client.post(archive)
        assert archive_response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        ), f"Archiving failed, so this test cannot judge the goal field: {archive_response.status_code}"

        response = session_client.get(
            ARCHIVED_CYCLES_URL.format(slug=workspace.slug, project_id=project.id)
        )

        assert response.status_code == status.HTTP_200_OK, (
            f"Got {response.status_code}: {getattr(response, 'data', None)!r}"
        )
        rows = [row for row in response.data if str(row.get("id")) == str(cycle.id)]
        assert rows, f"The archived cycle is missing from the list. Body: {response.data!r}"
        assert rows[0].get("goal") == GOAL, (
            "The archived cycle response omits goal, so the archive.py field list "
            f"was not updated. Row: {rows[0]!r}"
        )

    @pytest.mark.django_db
    def test_member_of_another_workspace_cannot_read_the_cycle(
        self, outsider_client, workspace, project, cycle
    ):
        """Tenant scoping. BaseViewSet applies no filter, so every route needs this."""
        url = CYCLE_DETAIL_URL.format(slug=workspace.slug, project_id=project.id, pk=cycle.id)

        response = outsider_client.get(url)

        # 403, not 404. `allow_permission` in plane/app/permissions/base.py refuses
        # before `get_queryset()` runs, and it returns an explicit 403 Response
        # rather than raising. A scoped queryset would give 404, but the decorator
        # never lets the request reach it.
        #
        # Asserting `in (403, 404)` would pass either way, so it could not catch a
        # regression in either direction. Pin the status the code actually returns.
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f"Cross-workspace read must be refused with 403. Got {response.status_code}: "
            f"{getattr(response, 'data', None)!r}"
        )
