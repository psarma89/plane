# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Contract tests for the cycle capacity threshold, on the session API.

The spec is docs/features/new/cycle-capacity-threshold.md. The capacity is a trip
wire in estimate points. A sum that equals the capacity is not over it.

The fixtures live in plane/tests/contract/conftest.py.
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from plane.db.models import CycleIssue, EstimatePoint, Issue
from plane.tests.contract.conftest import set_capacity


def cycle_url(slug, project_id, cycle_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/"


def cycle_issues_url(slug, project_id, cycle_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/"


def cycle_issue_url(slug, project_id, cycle_id, issue_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/{issue_id}/"


def progress_url(slug, project_id, cycle_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/progress/"


def transfer_url(slug, project_id, cycle_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/transfer-issues/"


def draft_to_issue_url(slug, draft_id):
    return f"/api/workspaces/{slug}/draft-to-issue/{draft_id}/"


def issue_url(slug, project_id, issue_id):
    return f"/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/"


@pytest.mark.contract
class TestCycleCapacityFields:
    """Slice 1. The two columns reach the database and come back on the response."""

    @pytest.mark.django_db
    def test_patch_sets_capacity_and_mode_and_response_returns_both(
        self, session_client, workspace, capacity_project, active_cycle
    ):
        url = cycle_url(workspace.slug, capacity_project.id, active_cycle.id)

        response = session_client.patch(url, {"capacity": 40, "capacity_mode": "block"}, format="json")

        assert response.status_code == status.HTTP_200_OK, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity"] == 40
        assert response.data["capacity_mode"] == "block"

        active_cycle.refresh_from_db()
        assert active_cycle.capacity == 40
        assert active_cycle.capacity_mode == "block"

    @pytest.mark.django_db
    def test_patch_rejects_an_unknown_capacity_mode(self, session_client, workspace, capacity_project, active_cycle):
        url = cycle_url(workspace.slug, capacity_project.id, active_cycle.id)

        response = session_client.patch(url, {"capacity_mode": "banana"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        active_cycle.refresh_from_db()
        assert active_cycle.capacity_mode == "warn"

    @pytest.mark.django_db
    def test_a_new_cycle_carries_no_capacity_and_warn_mode(self, active_cycle):
        assert active_cycle.capacity is None
        assert active_cycle.capacity_mode == "warn"

    @pytest.mark.django_db
    def test_guest_cannot_set_capacity(self, guest_client, workspace, capacity_project, active_cycle):
        url = cycle_url(workspace.slug, capacity_project.id, active_cycle.id)

        response = guest_client.patch(url, {"capacity": 40}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        active_cycle.refresh_from_db()
        assert active_cycle.capacity is None


@pytest.mark.contract
class TestAddWorkItemsToACycle:
    """Slice 3. The gate on the session add-to-cycle path."""

    @pytest.mark.django_db
    def test_add_work_items_under_capacity_returns_201_with_verdict_ok(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40)
        make_issue(20, in_cycle=active_cycle)
        joining = make_issue(13)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "ok"
        assert response.data["capacity_status"]["used_points"] == 33

    @pytest.mark.django_db
    def test_add_work_items_to_exactly_capacity_returns_201_with_verdict_ok(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        """Filling a cycle to 40 of 40 points raises no alert, even in block mode."""
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        joining = make_issue(20)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "ok"
        assert response.data["capacity_status"]["used_points"] == 40

    @pytest.mark.django_db
    def test_add_work_items_past_capacity_in_warn_mode_returns_201_with_verdict_warn(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="warn")
        make_issue(40, in_cycle=active_cycle)
        joining = make_issue(5)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "warn"
        assert CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=joining.id).exists()

    @pytest.mark.django_db
    def test_add_work_items_past_capacity_in_block_mode_returns_400_with_error_code(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        joining = make_issue(5)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error_code"] == "CYCLE_CAPACITY_EXCEEDED"
        assert "45" in response.data["error"]
        assert "40" in response.data["error"]

    @pytest.mark.django_db
    def test_refused_request_writes_no_cycle_issue_row(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        joining = make_issue(5)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=joining.id).exists()

    @pytest.mark.django_db
    def test_remove_work_item_from_a_blocked_cycle_returns_204(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        """A full cycle is not frozen. Removal always lowers the sum, so it always passes."""
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        leaving = make_issue(5, in_cycle=active_cycle)

        url = cycle_issue_url(workspace.slug, capacity_project.id, active_cycle.id, leaving.id)
        response = session_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=leaving.id).exists()

    @pytest.mark.django_db
    def test_gate_does_not_run_for_an_upcoming_cycle(
        self, session_client, workspace, capacity_project, upcoming_cycle, make_issue
    ):
        set_capacity(upcoming_cycle, 1, mode="block")
        make_issue(20, in_cycle=upcoming_cycle)
        joining = make_issue(13)

        url = cycle_issues_url(workspace.slug, capacity_project.id, upcoming_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_gate_does_not_run_for_a_completed_cycle(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        """The completed-cycle refusal already exists, and it fires before this gate."""
        set_capacity(active_cycle, 1, mode="block")
        joining = make_issue(13)
        active_cycle.end_date = timezone.now() - timedelta(days=1)
        active_cycle.save(update_fields=["end_date"])

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error_code" not in response.data

    @pytest.mark.django_db
    def test_gate_does_not_run_when_the_project_estimate_is_categories(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, points_estimate
    ):
        set_capacity(active_cycle, 1, mode="block")
        joining = make_issue(13)
        points_estimate.type = "categories"
        points_estimate.save(update_fields=["type"])

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "not_set"

    @pytest.mark.django_db
    def test_a_cycle_with_no_capacity_returns_not_set(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        """Rule zero. A NULL capacity leaves the write path exactly as it is today."""
        joining = make_issue(13)

        url = cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        assert response.data["capacity_status"]["verdict"] == "not_set"


@pytest.mark.contract
class TestTransferWorkItemsIntoACycle:
    """Slice 4, path 4. The transfer route moves work into the destination cycle."""

    @pytest.mark.django_db
    def test_transfer_past_capacity_in_block_mode_returns_400(
        self, session_client, workspace, capacity_project, active_cycle, closed_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        moving = make_issue(40, in_cycle=closed_cycle)

        url = transfer_url(workspace.slug, capacity_project.id, closed_cycle.id)
        response = session_client.post(url, {"new_cycle_id": str(active_cycle.id)}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error_code"] == "CYCLE_CAPACITY_EXCEEDED"
        assert CycleIssue.objects.filter(cycle_id=closed_cycle.id, issue_id=moving.id).exists()

    @pytest.mark.django_db
    def test_transfer_under_capacity_still_succeeds(
        self, session_client, workspace, capacity_project, active_cycle, closed_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        moving = make_issue(13, in_cycle=closed_cycle)

        url = transfer_url(workspace.slug, capacity_project.id, closed_cycle.id)
        response = session_client.post(url, {"new_cycle_id": str(active_cycle.id)}, format="json")

        assert response.status_code == status.HTTP_200_OK, f"Got {response.status_code}: {response.data!r}"
        assert CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=moving.id).exists()

    @pytest.mark.django_db
    def test_transfer_of_a_cycle_into_itself_is_not_double_counted(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        """The work items already sit in the destination, so they add nothing."""
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        make_issue(13, in_cycle=active_cycle)

        url = transfer_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.post(url, {"new_cycle_id": str(active_cycle.id)}, format="json")

        assert response.status_code == status.HTTP_200_OK, f"Got {response.status_code}: {response.data!r}"


@pytest.mark.contract
class TestPromoteADraftIntoACycle:
    """Slice 4, path 3. A draft promotion creates the work item and the cycle row."""

    @pytest.mark.django_db
    def test_draft_promotion_past_capacity_in_block_mode_returns_400(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, make_draft, points_estimate
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        draft = make_draft()
        point = EstimatePoint.objects.get(estimate=points_estimate, value="5")

        url = draft_to_issue_url(workspace.slug, draft.id)
        response = session_client.post(
            url,
            {
                "name": "Promoted work item",
                "estimate_point": str(point.id),
                "cycle_id": str(active_cycle.id),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error_code"] == "CYCLE_CAPACITY_EXCEEDED"
        assert not Issue.objects.filter(name="Promoted work item").exists()

    @pytest.mark.django_db
    def test_draft_promotion_under_capacity_still_succeeds(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, make_draft, points_estimate
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        draft = make_draft()
        point = EstimatePoint.objects.get(estimate=points_estimate, value="5")

        url = draft_to_issue_url(workspace.slug, draft.id)
        response = session_client.post(
            url,
            {
                "name": "Promoted work item",
                "estimate_point": str(point.id),
                "cycle_id": str(active_cycle.id),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        promoted = Issue.objects.filter(name="Promoted work item").first()
        assert promoted is not None
        assert CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=promoted.id).exists()


@pytest.mark.contract
class TestRaiseAnEstimateInsideACycle:
    """Slice 4, path 5. Both surfaces write estimate_point through a serializer."""

    @pytest.mark.django_db
    def test_estimate_point_raise_past_capacity_in_block_mode_returns_400(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, points_estimate
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        raised = make_issue(13, in_cycle=active_cycle)
        bigger = EstimatePoint.objects.get(estimate=points_estimate, value="40")

        url = issue_url(workspace.slug, capacity_project.id, raised.id)
        response = session_client.patch(url, {"estimate_point": str(bigger.id)}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "CYCLE_CAPACITY_EXCEEDED" in str(response.data)
        raised.refresh_from_db()
        assert raised.estimate_point.value == "13"

    @pytest.mark.django_db
    def test_lower_estimate_in_a_blocked_cycle_succeeds(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, points_estimate
    ):
        """A cycle at 45 of 40 points is not frozen. A lower estimate always passes."""
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        lowered = make_issue(5, in_cycle=active_cycle)
        smaller = EstimatePoint.objects.get(estimate=points_estimate, value="1")

        url = issue_url(workspace.slug, capacity_project.id, lowered.id)
        response = session_client.patch(url, {"estimate_point": str(smaller.id)}, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT, f"Got {response.status_code}: {response.data!r}"
        lowered.refresh_from_db()
        assert lowered.estimate_point.value == "1"

    @pytest.mark.django_db
    def test_estimate_raise_that_lands_on_the_capacity_still_succeeds(
        self, session_client, workspace, capacity_project, active_cycle, make_issue, points_estimate
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        raised = make_issue(13, in_cycle=active_cycle)
        bigger = EstimatePoint.objects.get(estimate=points_estimate, value="20")

        url = issue_url(workspace.slug, capacity_project.id, raised.id)
        response = session_client.patch(url, {"estimate_point": str(bigger.id)}, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT, f"Got {response.status_code}: {response.data!r}"
        raised.refresh_from_db()
        assert raised.estimate_point.value == "20"


@pytest.mark.contract
class TestCycleProgressCapacityStatus:
    """Slice 5. The progress body carries the verdict that the panel renders."""

    @pytest.mark.django_db
    def test_progress_endpoint_returns_capacity_status(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="warn")
        make_issue(40, in_cycle=active_cycle)
        make_issue(5, in_cycle=active_cycle)

        url = progress_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["capacity_status"]["verdict"] == "warn"
        assert response.data["capacity_status"]["capacity"] == 40
        assert response.data["capacity_status"]["used_points"] == 45

    @pytest.mark.django_db
    def test_progress_endpoint_returns_not_set_without_a_capacity(
        self, session_client, workspace, capacity_project, active_cycle, make_issue
    ):
        make_issue(40, in_cycle=active_cycle)

        url = progress_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = session_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["capacity_status"]["verdict"] == "not_set"
