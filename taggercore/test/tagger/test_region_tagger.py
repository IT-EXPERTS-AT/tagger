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
from unittest.mock import call

from botocore.exceptions import ClientError

from taggercore.model import TaggingResult
from taggercore.tagger import RegionTagger, AbstractResourceGroupApiTagger


class TestRegionTagger:
    def test_tag_all_with_failed_resource(self, mocker, tags, regional_resources):
        expected = [
            TaggingResult(
                [
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                ],
                {
                    "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0": "Error"
                },
            )
        ]
        tagging_response = {
            "FailedResourcesMap": {
                "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0": {
                    "StatusCode": 400,
                    "ErrorCode": "InvalidParameterValue",
                    "ErrorMessage": "Error",
                }
            }
        }
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_init_client = mocker.patch.object(RegionTagger, "init_client")
        mocked_init_client.return_value.tag_resources.return_value = tagging_response
        region_tagger = RegionTagger(tags, regional_resources, "eu-central-1")

        actual = region_tagger.tag_all()

        assert actual == expected

    def test_tag_all_without_failed_resources(self, mocker, tags, regional_resources):
        expected = [
            TaggingResult(
                [
                    "arn:aws:sqs:eu-central-1:111111111111:someq",
                    "arn:aws:sqs:eu-central-1:111111111111:someq2",
                    "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
                ],
                {},
            )
        ]
        tagging_response = {"FailedResourcesMap": {}}
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_init_client = mocker.patch.object(RegionTagger, "init_client")
        mocked_init_client.return_value.tag_resources.return_value = tagging_response

        region_tagger = RegionTagger(tags, regional_resources, "eu-central-1")
        actual = region_tagger.tag_all()

        assert actual == expected
        assert region_tagger.tags == tags
        assert region_tagger.resources_to_tag == regional_resources

    def test_should_split_resources(
        self, mocker, tags, too_many_resources_for_single_boto_call
    ):
        expected_tags = {tag.key: tag.value for tag in tags}
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_init_client = mocker.patch.object(RegionTagger, "init_client")
        tagger = RegionTagger(
            tags, too_many_resources_for_single_boto_call, "eu-central-1"
        )
        tagger.tag_all()

        mocked_init_client.return_value.tag_resources.assert_has_calls(
            [
                call(
                    ResourceARNList=[
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d1",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d2",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d3",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d4",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d5",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d6",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d7",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d8",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d9",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d10",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d11",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d12",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d13",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d14",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d15",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d16",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d17",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d18",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d19",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d20",
                    ],
                    Tags=expected_tags,
                ),
                call(
                    ResourceARNList=[
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d21",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d22",
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d23",
                    ],
                    Tags=expected_tags,
                ),
            ],
            any_order=True,
        )

    def test_should_remove_failed_resource_and_retry(
        self, mocker, tags, regional_resources_with_invalid_resource
    ):
        expected_tags = {tag.key: tag.value for tag in tags}
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_init_client = mocker.patch.object(RegionTagger, "init_client")

        mocked_init_client.return_value.tag_resources.side_effect = [
            ClientError(
                operation_name="tag_resources",
                error_response={
                    "Error": {
                        "Code": "InvalidParameterException",
                        "Message": "arn:aws:ec2:eu-central-1:111111111111:invalid is not a valid AmazonResourceName (ARN)",
                    },
                },
            ),
            {"FailedResourcesMap": {}},
        ]

        actual = RegionTagger(
            tags, regional_resources_with_invalid_resource, "eu-central-1"
        ).tag_all()

        mocked_init_client.return_value.tag_resources.assert_called_with(
            ResourceARNList=[
                "arn:aws:sqs:eu-central-1:111111111111:someq",
                "arn:aws:sqs:eu-central-1:111111111111:someq2",
                "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            ],
            Tags=expected_tags,
        )
        assert len(actual[0].successful_arns) == 3
        assert len(actual[0].failed_arns) == 1
        assert actual[0].failed_arns == {
            "arn:aws:ec2:eu-central-1:111111111111:invalid": "arn:aws:ec2:eu-central-1:111111111111:invalid is not a valid AmazonResourceName (ARN)"
        }
