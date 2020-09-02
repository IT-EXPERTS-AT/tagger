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
from taggercore.scanner import RegionScanner, GlobalScanner
from taggercore.usecase import scan_region, scan_region_and_global


class TestScan:
    def test_scan_region(self, mocker, regional_resources):
        mocked_region_scanner_scan = mocker.patch.object(RegionScanner, "scan")
        mocked_region_scanner_scan.return_value = regional_resources

        actual = scan_region("eu-central-1")
        assert actual == regional_resources

    def test_scan_region_and_global(self, mocker, regional_resources, global_resources):
        mocked_region_scanner_scan = mocker.patch.object(RegionScanner, "scan")
        mocked_region_scanner_scan.return_value = regional_resources
        mocked_global_scanner_scan = mocker.patch.object(GlobalScanner, "scan")
        mocked_global_scanner_scan.return_value = global_resources

        region = "eu-central-1"
        actual = scan_region_and_global(region)
        assert actual[region] == regional_resources
        assert actual["global"] == global_resources
