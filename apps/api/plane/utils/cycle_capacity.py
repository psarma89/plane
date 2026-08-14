# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Measure a cycle against its point capacity.

The spec is docs/features/new/cycle-capacity-threshold.md.

`CycleIssue` has no custom `save()`, and no shared serializer covers every path
that raises the point sum of a cycle. The gate is therefore a call to
`evaluate_cycle_capacity` from each write path, and not a model hook. The shape
copies `plane/utils/cycle_transfer_issues.py`, which both API surfaces import.

This module raises nothing and writes nothing. The caller decides what to do
with the verdict.
"""

# Python imports
import math

# Django imports
from django.db.models import FloatField, Sum, Value
from django.db.models.functions import Cast
from django.utils import timezone

# Module imports
from plane.db.models import CycleIssue, EstimatePoint, Issue
from plane.db.models.cycle import CycleCapacityMode
from plane.db.models.estimate import EstimateType

# The error code that both API surfaces return with the 400. The web client matches
# the code and renders a translated string. It does not match the message text.
CAPACITY_EXCEEDED_ERROR_CODE = "CYCLE_CAPACITY_EXCEEDED"

VERDICT_NOT_SET = "not_set"
VERDICT_OK = "ok"
VERDICT_WARN = "warn"
VERDICT_BLOCK = "block"


def not_set_status():
    """The result when this feature does not apply to the cycle.

    `write_allowed` is True, so a call site that reads only that field lets every
    write through. That is the correct default if a call site forgets its own guard.
    """
    return {
        "capacity": None,
        "mode": None,
        "used_points": 0,
        "incoming_points": 0,
        "projected_points": 0,
        "verdict": VERDICT_NOT_SET,
        "write_allowed": True,
    }


def is_cycle_active(cycle):
    """Return True when the current time falls inside the dates of the cycle.

    `CycleViewSet.list` in plane/app/views/cycle/base.py defines the active cycle the
    same way. That code converts `timezone.now()` into the project timezone and back
    to UTC. Both conversions keep the same instant, so this comparison gives the same
    result with one step.
    """
    if cycle.archived_at is not None or cycle.start_date is None or cycle.end_date is None:
        return False
    return cycle.start_date <= timezone.now() <= cycle.end_date


def capacity_gate_applies(cycle, project):
    """Return True when the cycle is worth measuring. This runs no aggregate.

    A call site asks this first, so that it builds the incoming point sum only for a
    cycle that a capacity can refuse.
    """
    return (
        cycle.capacity is not None
        and is_cycle_active(cycle)
        and project.estimate_id is not None
        and project.estimate.type == EstimateType.POINTS
    )


def _finite(value):
    """Return the number, or 0 when it is NaN or infinite.

    `EstimatePoint.value` is an unrestricted CharField, so a points-type estimate can
    hold "NaN" or "inf". Both PostgreSQL and Python accept those strings as floats.
    Every comparison against NaN is false, so one such point disables block mode for
    the whole project. Treat a value that is not finite as no points.
    """
    return value if math.isfinite(value) else 0


def _sum_points(**filters):
    """Sum the estimate point values of the matching work items, as a float.

    Every sum counts a points-type estimate only. A categories-type point holds a
    label and not a number, so it must never reach the Cast.
    """
    aggregate = (
        Issue.issue_objects.filter(estimate_point__estimate__type=EstimateType.POINTS, **filters)
        .annotate(value_as_float=Cast("estimate_point__value", FloatField()))
        .aggregate(points=Sum("value_as_float", default=Value(0), output_field=FloatField()))
    )
    return _finite(aggregate["points"] or 0)


def cycle_used_points(cycle):
    """Sum the estimate points of every work item in the cycle.

    The filter matches `CycleProgressEndpoint`, so the two numbers agree. A project
    on a categories-type estimate sums to 0, which is why the caller checks the
    estimate type first.
    """
    return _sum_points(
        issue_cycle__cycle_id=cycle.id,
        issue_cycle__deleted_at__isnull=True,
        workspace_id=cycle.workspace_id,
        project_id=cycle.project_id,
    )


def points_for_issues(*, issue_ids, workspace_id, project_id):
    """Sum the estimate points of the given work items.

    This is the incoming point sum of a write. The scope repeats the workspace and
    the project, so that an id from another tenant adds nothing.
    """
    if not issue_ids:
        return 0
    return _sum_points(pk__in=issue_ids, workspace_id=workspace_id, project_id=project_id)


def build_capacity_status(*, capacity, mode, used_points, incoming_points=0):
    """Compare the numbers. This function is pure, and it runs no query.

    One comparison, used twice. The capacity itself is not over the capacity, so both
    sides use ">" and not ">=".

    - The alert shows when `used_points` passes the capacity.
    - A write is refused when `projected_points` passes it, and the mode is block.

    The two fields are separate on purpose. A cycle at 38 of 40 points reads `ok`, and
    a 5-point write into it is still refused, because the write lands at 43.
    """
    projected_points = used_points + incoming_points
    blocks = mode == CycleCapacityMode.BLOCK

    if used_points > capacity:
        verdict = VERDICT_BLOCK if blocks else VERDICT_WARN
    else:
        verdict = VERDICT_OK

    return {
        "capacity": capacity,
        "mode": str(mode),
        "used_points": used_points,
        "incoming_points": incoming_points,
        "projected_points": projected_points,
        "verdict": verdict,
        "write_allowed": not (blocks and projected_points > capacity),
    }


def evaluate_cycle_capacity(*, cycle, project, incoming_points=0):
    """Measure a cycle against its capacity. Return the verdict and the numbers.

    Three guards run before the aggregate, and not after it. Every cycle carries a
    NULL capacity on the day this ships, and the add-to-cycle route is a hot write
    path. A gate that queries before it discovers that it has nothing to compare
    taxes every team that never wanted this feature.
    """
    if not capacity_gate_applies(cycle, project):
        return not_set_status()

    return build_capacity_status(
        capacity=cycle.capacity,
        mode=cycle.capacity_mode,
        used_points=cycle_used_points(cycle),
        incoming_points=incoming_points,
    )


def evaluate_cycle_addition(*, cycle, project, issue_ids):
    """Measure a write that adds the given work items to the cycle.

    A work item that already sits in the cycle adds nothing to the sum, so this
    excludes it. An id from another tenant also adds nothing, because
    `points_for_issues` repeats the workspace and project scope.

    Call this before the first write. No path in this repository opens a
    transaction around the two writes of an add-to-cycle request.
    """
    if not capacity_gate_applies(cycle, project):
        return not_set_status()

    # The request body carries the ids as strings, and the column returns UUID
    # objects. Both sides become strings, so that the comparison holds.
    already_in_cycle = {
        str(issue_id)
        for issue_id in CycleIssue.objects.filter(cycle_id=cycle.id, issue_id__in=issue_ids).values_list(
            "issue_id", flat=True
        )
    }
    joining = [issue_id for issue_id in issue_ids if str(issue_id) not in already_in_cycle]

    return evaluate_cycle_capacity(
        cycle=cycle,
        project=project,
        incoming_points=points_for_issues(
            issue_ids=joining,
            workspace_id=cycle.workspace_id,
            project_id=cycle.project_id,
        ),
    )


def status_after_write(capacity_status):
    """Recompute the status with the write applied. This runs no query.

    The projected sum of the write becomes the used sum of the cycle. The response
    carries this result, so that the panel renders the alert without a second request.
    """
    if capacity_status["verdict"] == VERDICT_NOT_SET:
        return capacity_status
    return build_capacity_status(
        capacity=capacity_status["capacity"],
        mode=capacity_status["mode"],
        used_points=capacity_status["projected_points"],
    )


def estimate_point_value(estimate_point):
    """The numeric value of one estimate point. A categories point is worth 0.

    `EstimatePoint.value` is a CharField, so a points-type estimate can still hold a
    string that is not a number. That case returns 0 as well.
    """
    if estimate_point is None:
        return 0
    if estimate_point.estimate.type != EstimateType.POINTS:
        return 0
    try:
        return _finite(float(estimate_point.value))
    except (TypeError, ValueError):
        return 0


def points_for_estimate_point_id(*, estimate_point_id, project_id):
    """The numeric value of one estimate point, looked up by id inside the project."""
    if not estimate_point_id:
        return 0
    estimate_point = (
        EstimatePoint.objects.select_related("estimate").filter(pk=estimate_point_id, project_id=project_id).first()
    )
    return estimate_point_value(estimate_point)


def evaluate_estimate_change(*, issue, new_estimate_point):
    """Measure a change of estimate on a work item that sits in a cycle.

    Return `(cycle, capacity_status)` for the first cycle that refuses the change, and
    None when every cycle allows it. A change that lowers the estimate always returns
    None, so a full cycle is never frozen.

    The first query filters on a non-null capacity, so a work item in a cycle with no
    capacity costs one indexed lookup and nothing else.
    """
    cycle_issues = list(
        CycleIssue.objects.filter(issue_id=issue.id, cycle__capacity__isnull=False).select_related(
            "cycle__project__estimate"
        )
    )
    if not cycle_issues:
        return None

    delta = estimate_point_value(new_estimate_point) - estimate_point_value(issue.estimate_point)
    if delta <= 0:
        return None

    for cycle_issue in cycle_issues:
        capacity_status = evaluate_cycle_capacity(
            cycle=cycle_issue.cycle,
            project=cycle_issue.cycle.project,
            incoming_points=delta,
        )
        if not capacity_status["write_allowed"]:
            return cycle_issue.cycle, capacity_status
    return None


def format_points(value):
    """Render a point sum without a trailing zero. 28.0 becomes 28, and 2.5 stays 2.5."""
    return str(int(value)) if float(value).is_integer() else str(value)


def capacity_error_message(*, cycle_name, capacity_status):
    """The English message for the 400. It names the three numbers.

    The web client renders a translated string from the error code. This message is
    the fallback and the log line.
    """
    incoming = format_points(capacity_status["incoming_points"])
    used = format_points(capacity_status["used_points"])
    capacity = format_points(capacity_status["capacity"])
    projected = format_points(capacity_status["projected_points"])
    return (
        f"The work is worth {incoming} points. "
        f"{cycle_name} holds {used} of {capacity} points, so the total reaches "
        f"{projected} points, which is over the {capacity}-point capacity."
    )


def capacity_error_payload(*, cycle_name, capacity_status):
    """The 400 body for the session API. The external API uses `code` and `message`."""
    return {
        "error": capacity_error_message(cycle_name=cycle_name, capacity_status=capacity_status),
        "error_code": CAPACITY_EXCEEDED_ERROR_CODE,
        "capacity_status": capacity_status,
    }
