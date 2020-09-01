#
# Copyright (c) 2020 it-eXperts IT-Dienstleistungs GmbH.
#
# This file is part of tagger
# (see https://github.com/IT-EXPERTS-AT/tagger).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import pytest
import skew

from taggercore import scanner
from taggercore.config import TaggercoreConfigError, set_config, Config
from taggercore.model import Resource
from taggercore.scanner import GlobalScanner, GLOBAL_SERVICES
from taggercore.tagger import GLOBAL_RES_TYPE_NOT_TAGGABLE
from test.stubs import ResourceStub


def mock_global_scan(service: str):
    if "route53" in service:
        return [
            ResourceStub(
                "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "healthcheck",
                {},
                None,
            )
        ]
    elif "cloudfront" in service:
        return [
            ResourceStub(
                "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                "EMS6KR7IENMDE",
                "distribution",
                {},
                "some-domain",
            )
        ]
    elif "iam" in service:
        return [
            ResourceStub(
                "arn:aws:iam::111111111111:role/some-role",
                "some-role",
                "role",
                {},
                "some-role",
            )
        ]
    else:
        return []


class TestGlobalScanner:
    def test_global_scanner_with_config_set(
        self, mocker, account_and_profile_configured
    ):
        skew_scan = mocker.patch.object(scanner.global_scanner.skew, "scan")
        skew.scan.side_effect = mock_global_scan

        actual = GlobalScanner().scan(GLOBAL_RES_TYPE_NOT_TAGGABLE)

        assert len(actual) == 3
        assert (
            Resource(
                "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                "EMS6KR7IENMDE",
                "distribution",
                [],
            )
            in actual
        )
        assert (
            Resource(
                "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "healthcheck",
                [],
            )
            in actual
        )
        assert (
            Resource(
                "arn:aws:iam::111111111111:role/some-role",
                "some-role",
                "role",
                [],
                name="some-role",
            )
            in actual
        )
        assert skew_scan.call_count == len(GLOBAL_SERVICES)

    def test_global_scanner_without_config_set(self):
        set_config(Config())
        with pytest.raises(TaggercoreConfigError):
            GlobalScanner().scan(GLOBAL_RES_TYPE_NOT_TAGGABLE)
