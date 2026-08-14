# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Test Settings"""

from .common import *  # noqa

DEBUG = True

# Send it in a dummy outbox
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

INSTALLED_APPS.append(  # noqa
    "plane.tests"
)

# Do not rate limit the API key surface during tests.
#
# `common.py` defaults API_KEY_RATE_LIMIT to "60/minute", and the contract suite
# already makes more than fifty X-API-Key requests. Adding any further test on that
# surface pushes the whole run past the ceiling, and every later api_key_client test
# then fails with 429 rather than with anything about its own subject.
#
# The counter lives in Valkey, not in PostgreSQL, so it is not rolled back by the
# test transaction and not reset by `--create-db`. That makes the failure worse than
# a normal order dependency: it accumulates across runs inside the same minute, so
# the failure count grows each time the suite is run and the suite looks
# progressively more broken while nothing has changed.
API_KEY_RATE_LIMIT = "10000/minute"
