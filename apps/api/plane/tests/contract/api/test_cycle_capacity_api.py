# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Contract tests for the cycle capacity threshold, on the X-API-Key API.

A gate on one surface only is the defect this feature is most likely to ship. A
script with an API key would walk past the capacity while the web client refuses.

The fixtures live in plane/tests/contract/conftest.py.
"""

from uuid import uuid4

import pytest
from rest_framework import status

from plane.db.models import CycleIssue
from plane.db.models.api import APIToken
from plane.tests.contract.conftest import set_capacity


@pytest.fixture
def capacity_api_client(db, api_client, create_user):
    """A client with its own API key.

    `ApiKeyRateThrottle` in plane/api/rate_limit.py keys the bucket on the API key
    string, and `API_KEY_RATE_LIMIT` allows 60 requests per minute. The `api_token`
    fixture hardcodes one token for the whole suite, so every test that uses it
    shares one bucket. A unique token here keeps these tests out of that bucket.
    """
    token = APIToken.objects.create(
        user=create_user,
        label="Cycle capacity token",
        token=f"capacity-token-{uuid4().hex}",
    )
    api_client.credentials(HTTP_X_API_KEY=token.token)
    return api_client


def external_cycle_url(slug, project_id, cycle_id):
    return f"/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/"


def external_cycle_issues_url(slug, project_id, cycle_id):
    return f"/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/"


@pytest.mark.contract
class TestExternalCycleCapacity:
    @pytest.mark.django_db
    def test_external_patch_sets_capacity_and_mode(
        self, capacity_api_client, workspace, capacity_project, active_cycle
    ):
        url = external_cycle_url(workspace.slug, capacity_project.id, active_cycle.id)

        response = capacity_api_client.patch(url, {"capacity": 40, "capacity_mode": "block"}, format="json")

        assert response.status_code == status.HTTP_200_OK, f"Got {response.status_code}: {response.data!r}"
        active_cycle.refresh_from_db()
        assert active_cycle.capacity == 40
        assert active_cycle.capacity_mode == "block"

    @pytest.mark.django_db
    def test_external_add_past_capacity_in_block_mode_returns_400(
        self, capacity_api_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(40, in_cycle=active_cycle)
        joining = make_issue(5)

        url = external_cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = capacity_api_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "CYCLE_CAPACITY_EXCEEDED"
        assert not CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=joining.id).exists()

    @pytest.mark.django_db
    def test_external_add_under_capacity_still_succeeds(
        self, capacity_api_client, workspace, capacity_project, active_cycle, make_issue
    ):
        set_capacity(active_cycle, 40, mode="block")
        make_issue(20, in_cycle=active_cycle)
        joining = make_issue(13)

        url = external_cycle_issues_url(workspace.slug, capacity_project.id, active_cycle.id)
        response = capacity_api_client.post(url, {"issues": [str(joining.id)]}, format="json")

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED), (
            f"Got {response.status_code}: {response.data!r}"
        )
        assert CycleIssue.objects.filter(cycle_id=active_cycle.id, issue_id=joining.id).exists()
