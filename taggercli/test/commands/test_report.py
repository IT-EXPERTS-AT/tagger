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
from datetime import datetime, timezone

from taggercore.model import Resource, TagDiffType, Tag, TagDiff, ResourceWithTagDiffs
from typer.testing import CliRunner

from config import Config
from main import cli
from taggercli.commands import (
    metrics_for_dashboard_by_service,
    prepare_data_for_dashboard_template,
)
from taggercli.config import set_config

diff_for_improperly_tagged_resource = [
    TagDiff(
        Tag("Project", "CRM"), Tag("Project", "CRM"), TagDiffType["EXISTING"]
    ),
    TagDiff(Tag("Owner", "Alice"), Tag("Owner", "Bob"), TagDiffType["NEW_VALUE"]),
    TagDiff(Tag(None, None), Tag("Department", "Marketing"), TagDiffType["NEW"]),
]

diff_for_properly_tagged_resource = [
    TagDiff(
        Tag("Project", "CRM"), Tag("Project", "CRM"), TagDiffType["EXISTING"]
    ),
    TagDiff(
        Tag("Created", "2020-08-10"),
        Tag(None, None),
        TagDiffType["EXISTING_NOT_IN_SCHEMA"],
    ),
]

tags = [Tag("Project", "CRM"), Tag("Owner", "Alice"), Tag("Created", "2020-08-10")]


class TestReport:
    def test_metrics_for_dashboard(self):
        resources_by_service = {
            "sqs": [
                ResourceWithTagDiffs(
                    Resource(
                        "arn:aws:sqs:eu-central-1:111111111111:someq",
                        "someq",
                        "queue",
                        tags,
                    ),
                    diff_for_improperly_tagged_resource,
                ),
                ResourceWithTagDiffs(
                    Resource(
                        "arn:aws:sqs:eu-central-1:111111111111:someq2",
                        "someq2",
                        "queue",
                        [Tag("Project", "Super1")],
                    ),
                    diff_for_properly_tagged_resource,
                ),
            ],
            "apigateway": [
                ResourceWithTagDiffs(
                    Resource(
                        "arn:aws:apigateway:eu-central-1::/apis/e5zcg2s231",
                        "e5zcg2s231",
                        "apigateway",
                        tags,
                    ),
                    diff_for_properly_tagged_resource,
                )
            ],
        }

        actual = metrics_for_dashboard_by_service(resources_by_service)

        assert actual == {
            "sqs": {
                "number_of_resources": 2,
                "number_of_resources_tagged_properly": 1,
                "ratio_tagged_properly": 0.5,
            },
            "apigateway": {
                "number_of_resources": 1,
                "number_of_resources_tagged_properly": 1,
                "ratio_tagged_properly": 1,
            },
        }

    def test_data_for_dashboard_template(self):
        creation_datetime = datetime(2020, 8, 7, 10, 5, 23, tzinfo=timezone.utc)

        resources_with_tag_diffs = [
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "someq",
                    "queue",
                    tags,
                ),
                diff_for_improperly_tagged_resource,
            ),
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                    "someq2",
                    "queue",
                    [Tag("Project", "Super1")],
                ),
                diff_for_properly_tagged_resource,
            ),
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:apigateway:eu-central-1::/apis/e5zcg2s231",
                    "e5zcg2s231",
                    "apigateway",
                    tags,
                ),
                diff_for_properly_tagged_resource,
            ),
        ]

        actual = prepare_data_for_dashboard_template(
            "111111111111", creation_datetime, resources_with_tag_diffs
        )

        assert actual == {
            "account_id": "111111111111",
            "creation_datetime": "Fri Aug  7 10:05:23 2020 (UTC)",
            "metrics_by_service": {
                "sqs": {
                    "number_of_resources": 2,
                    "number_of_resources_tagged_properly": 1,
                    "ratio_tagged_properly": 0.5,
                },
                "apigateway": {
                    "number_of_resources": 1,
                    "number_of_resources_tagged_properly": 1,
                    "ratio_tagged_properly": 1,
                },
            },
            "resources_by_service": {
                "sqs": [
                    ResourceWithTagDiffs(
                        Resource(
                            "arn:aws:sqs:eu-central-1:111111111111:someq",
                            "someq",
                            "queue",
                            tags,
                        ),
                        diff_for_improperly_tagged_resource,
                    ),
                    ResourceWithTagDiffs(
                        Resource(
                            "arn:aws:sqs:eu-central-1:111111111111:someq2",
                            "someq2",
                            "queue",
                            [Tag("Project", "Super1")],
                        ),
                        diff_for_properly_tagged_resource,
                    ),
                ],
                "apigateway": [
                    ResourceWithTagDiffs(
                        Resource(
                            "arn:aws:apigateway:eu-central-1::/apis/e5zcg2s231",
                            "e5zcg2s231",
                            "apigateway",
                            tags,
                        ),
                        diff_for_properly_tagged_resource,
                    )
                ],
            },
        }

    def test_report_command(self, mocker, tmpdir):
        expected_file_name = "report.html"
        expected_output_path = str(tmpdir) + "/" + expected_file_name
        resources_with_tag_diffs = [
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "someq",
                    "queue",
                    tags,
                ),
                diff_for_improperly_tagged_resource,
            ),
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                    "someq2",
                    "queue",
                    [Tag("Project", "Super1")],
                ),
                diff_for_properly_tagged_resource,
            ),
            ResourceWithTagDiffs(
                Resource(
                    "arn:aws:apigateway:eu-central-1::/apis/e5zcg2s231",
                    "e5zcg2s231",
                    "apigateway",
                    tags,
                ),
                diff_for_properly_tagged_resource,
            ),
        ]
        some_config = Config(
            [Tag("Owner", "Fritz"), Tag("Project", "CRM")], default_region="eu-west-1"
        )
        mocker.patch(
            "taggercli.commands.report.create_report",
            return_value=resources_with_tag_diffs,
        )
        mocker.patch("taggercli.commands.report.init_config")
        mocker.patch("taggercli.commands.report.get_config", return_value=some_config)

        runner = CliRunner()
        actual = runner.invoke(
            cli,
            ["report", "create", "--region", "eu-central-1", "--output-path", tmpdir],
        )

        assert not actual.exception
        assert actual.exit_code == 0
        with open(expected_output_path, "r") as generated_report:
            assert generated_report.read()
