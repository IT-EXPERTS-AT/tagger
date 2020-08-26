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
from taggercore.scanner import RegionScanner, GLOBAL_SERVICES
from taggercore.tagger import REG_RES_TYPE_NOT_TAGGABLE, REG_RES_TYPE_NOT_SUPPORTED
from test.stubs import ResourceStub


def mock_scan(service: str):
    if "apigateway" in service:
        return [
            ResourceStub(
                "arn:aws:sqs:eu-central-1:111111111111:someq",
                "someq",
                "queue",
                {},
                "queue-name",
            )
        ]
    elif "cloudformation" in service:
        return [
            ResourceStub(
                "arn:aws:cloudformation:eu-central-1:111111111111:stack/some-stack/b35ac3c0-912c-11ea-890f-02508c92de23",
                "some-stack",
                "stack",
                {},
                None,
            )
        ]
    else:
        return []


class TestRegionScanner:
    def test_scan(self, mocker, account_and_profile_configured):
        skew.set_config({"accounts": {"111111111111": {"profile": "profile-1"}}})
        number_of_supported_services = len(skew.ARN().service.choices()) - len(
            GLOBAL_SERVICES
        )
        skew_scan = mocker.patch.object(scanner.region_scanner.skew, "scan")
        skew.scan.side_effect = mock_scan

        actual = RegionScanner("eu-central-1").scan(
            REG_RES_TYPE_NOT_SUPPORTED + REG_RES_TYPE_NOT_TAGGABLE
        )

        # cloudformation stack is in REG_RES_TYPE_NOT_SUPPORTED therefore length should only be 1
        assert len(actual) == 1
        assert actual[0] == Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", []
        )
        assert skew_scan.call_count == number_of_supported_services

    def test_scan_without_config_set(self):
        skew.set_config({})
        set_config(Config())
        with pytest.raises(TaggercoreConfigError):
            RegionScanner("eu-central-1").scan(
                REG_RES_TYPE_NOT_SUPPORTED + REG_RES_TYPE_NOT_TAGGABLE
            )
