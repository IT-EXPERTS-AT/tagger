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
from taggercore.model import Tag, Resource
from typer.testing import CliRunner

from taggercli.config.config import Config
from taggercli.main import cli

tags = [Tag("Project", "Super1"), Tag("Owner", "Owner1"), Tag("Created", "Yesterday")]


class TestTag:
    def test_tag_all_with_detailed_list(self, mocker):
        scanned_resources = {
            "eu-central-1": [
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "someq",
                    "queue",
                    tags,
                ),
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                    "someq2",
                    "queue",
                    tags,
                ),
            ],
            "global": [
                Resource(
                    "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                    "EMS6KR7IENMDE",
                    "distribution",
                    tags,
                ),
                Resource(
                    "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                    "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                    "healthcheck",
                    tags,
                ),
            ],
        }
        some_config = Config(
            [Tag("Owner", "Fritz"), Tag("Project", "CRM")],
            default_region="eu-central-1",
        )
        runner = CliRunner()
        scan_mock = mocker.patch(
            "taggercli.commands.tag.scan_region_and_global",
            return_value=scanned_resources,
        )
        mocker.patch("taggercli.commands.tag.init_config")
        mocker.patch("taggercli.commands.tag.get_config", return_value=some_config)

        actual = runner.invoke(cli, ["tag", "all"], input="y\n n\n")

        assert not actual.exception
        assert actual.exit_code == 0
        assert actual.stdout.find("Scanning completed")
        assert actual.stdout.find(
            f"Found {len(scanned_resources['global'])} global resources"
        )
        assert actual.stdout.find(
            f"Found {len(scanned_resources['eu-central-1'])} resources in region eu-central-1"
        )
        scan_mock.assert_called_once_with("eu-central-1")

    def test_tag_all_with_region_input(self, mocker):
        expected_region = "eu-west-1"
        scanned_resources = {
            expected_region: [
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "someq",
                    "queue",
                    tags,
                ),
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                    "someq2",
                    "queue",
                    tags,
                ),
            ],
            "global": [
                Resource(
                    "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                    "EMS6KR7IENMDE",
                    "distribution",
                    tags,
                ),
                Resource(
                    "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                    "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                    "healthcheck",
                    tags,
                ),
            ],
        }
        expected_resources = (
            scanned_resources[expected_region] + scanned_resources["global"]
        )
        expected_tags = [Tag("Owner", "Fritz"), Tag("Project", "CRM")]
        some_config = Config(expected_tags, default_region="eu-central-1")
        runner = CliRunner()
        scan_mock = mocker.patch(
            "taggercli.commands.tag.scan_region_and_global",
            return_value=scanned_resources,
        )
        mocker.patch("taggercli.commands.tag.init_config")
        mocker.patch("taggercli.commands.tag.get_config", return_value=some_config)
        perform_tagging_mock = mocker.patch("taggercli.commands.tag.perform_tagging")

        actual = runner.invoke(
            cli, ["tag", "all", "--region", expected_region], input="y\n y\n"
        )

        assert not actual.exception
        assert actual.exit_code == 0
        assert actual.stdout.find("Scanning completed")
        assert actual.stdout.find(
            f"Found {len(scanned_resources['global'])} global resources"
        )
        assert actual.stdout.find(
            f"Found {len(scanned_resources[expected_region])} resources in region eu-central-1"
        )
        scan_mock.assert_called_once_with(expected_region)
        perform_tagging_mock.assert_called_with(expected_resources, expected_tags)
