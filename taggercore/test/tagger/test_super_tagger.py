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
from taggercore.model import TaggingResult
from taggercore.tagger import (
    SuperTagger,
    AbstractResourceGroupApiTagger,
    ServiceTagger,
    RegionTagger,
    GlobalTagger,
)


class TestSuperTagger:
    def test_should_create_region_taggers(
        self, mocker, account_and_profile_configured, resources_from_two_regions, tags
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(resources_from_two_regions, tags)

        assert len(tagger.region_taggers) == 2
        assert len(tagger.service_taggers) == 0
        assert tagger.region_taggers[0].region == "eu-central-1"
        assert tagger.region_taggers[1].region == "eu-west-1"
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger(
        self, mocker, account_and_profile_configured, iam_roles, tags
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(iam_roles, tags)

        assert len(tagger.service_taggers) == 1
        assert len(tagger.region_taggers) == 0
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger_and_region_taggers(
        self,
        mocker,
        account_and_profile_configured,
        iam_roles,
        resources_from_two_regions,
        tags,
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(iam_roles + resources_from_two_regions, tags)

        assert len(tagger.service_taggers) == 1
        assert tagger.service_taggers[0].resources == iam_roles
        assert len(tagger.region_taggers) == 2
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger_and_region_taggers_and_global_tagger_with_arns(
        self,
        mocker,
        account_and_profile_configured,
        iam_roles,
        resources_from_two_regions,
        global_resources,
        tags,
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(
            iam_roles + resources_from_two_regions + global_resources, tags
        )

        assert len(tagger.service_taggers) == 1
        assert len(tagger.region_taggers) == 2
        assert tagger.global_tagger.arns == [
            resource.arn for resource in global_resources
        ]

    def test_should_combine_results_from_regions(
        self, mocker, account_and_profile_configured, resources_from_two_regions, tags
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_region_tagger = mocker.patch.object(RegionTagger, "tag_all")
        mocked_region_tagger.side_effect = [
            [
                TaggingResult(
                    [
                        "arn:aws:ec2:eu-west-1:111111111111:network-acl/acl-abc",
                    ],
                    {
                        "arn:aws:ec2:eu-west-1:111111111111:security-group/sg-b501f6d1": "Failed to tag security group"
                    },
                )
            ],
            [
                TaggingResult(
                    [
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
                        "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0009",
                    ],
                    {
                        "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0008": "Failed to tag subnet"
                    },
                )
            ],
        ]

        actual = SuperTagger(resources_from_two_regions, tags).tag_regions()

        assert len(actual.successful_arns) == 3
        assert len(actual.failed_arns) == 2

    def test_should_combine_results_from_non_regional_tagger(
        self, mocker, account_and_profile_configured, global_resources, iam_roles, tags
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        mocked_global_tagger = mocker.patch.object(GlobalTagger, "tag_all")
        mocked_service_tagger = mocker.patch.object(ServiceTagger, "tag_resources")
        mocked_global_tagger.return_value = [
            TaggingResult(
                [
                    "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                ],
                {
                    "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70": "Failed to tag healthcheck"
                },
            )
        ]

        mocked_service_tagger.return_value = [
            TaggingResult(
                [
                    "arn:aws:iam::111111111111:role/some-role",
                    "arn:aws:iam::111111111111:role/another-role",
                ],
                {},
            )
        ]

        actual = SuperTagger(
            global_resources + iam_roles, tags
        ).tag_non_regional_resources()

        assert len(actual.successful_arns) == 3
        assert len(actual.failed_arns) == 1

    def test_should_combine_region_and_non_regional_results(
        self,
        mocker,
        account_and_profile_configured,
        global_resources,
        iam_roles,
        tags,
        resources_from_two_regions,
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_region_tagger = mocker.patch.object(RegionTagger, "tag_all")
        mocked_global_tagger = mocker.patch.object(GlobalTagger, "tag_all")
        mocked_service_tagger = mocker.patch.object(ServiceTagger, "tag_resources")

        mocked_global_tagger.return_value = [
            TaggingResult(
                [
                    "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                ],
                {
                    "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70": "Failed to tag healthcheck"
                },
            )
        ]

        mocked_service_tagger.return_value = [
            TaggingResult(
                [
                    "arn:aws:iam::111111111111:role/some-role",
                    "arn:aws:iam::111111111111:role/another-role",
                ],
                {},
            )
        ]

        mocked_region_tagger.side_effect = [
            [
                TaggingResult(
                    [
                        "arn:aws:ec2:eu-west-1:111111111111:network-acl/acl-abc",
                    ],
                    {
                        "arn:aws:ec2:eu-west-1:111111111111:security-group/sg-b501f6d1": "Failed to tag security group"
                    },
                )
            ],
            [
                TaggingResult(
                    [
                        "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
                        "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0009",
                    ],
                    {
                        "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0008": "Failed to tag subnet"
                    },
                )
            ],
        ]

        actual = SuperTagger(
            global_resources + iam_roles + resources_from_two_regions, tags
        ).tag_all()

        assert len(actual.successful_arns) == 6
        assert len(actual.failed_arns) == 3

    def test_should_return_empty_result(self, mocker, tags):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_region_tagger = mocker.patch.object(RegionTagger, "tag_all")
        mocked_global_tagger = mocker.patch.object(GlobalTagger, "tag_all")
        mocked_service_tagger = mocker.patch.object(ServiceTagger, "tag_resources")

        mocked_global_tagger.return_value = [
            TaggingResult(
                [],
                {},
            )
        ]

        mocked_service_tagger.return_value = [
            TaggingResult(
                [],
                {},
            )
        ]

        mocked_region_tagger.return_value = [
            TaggingResult(
                [
                    "arn:aws:ec2:eu-west-1:111111111111:network-acl/acl-abc",
                ],
                {
                    "arn:aws:ec2:eu-west-1:111111111111:security-group/sg-b501f6d1": "Failed to tag security group"
                },
            )
        ]

        actual = SuperTagger([], tags).tag_all()

        assert len(actual.successful_arns) == 0
        assert len(actual.failed_arns) == 0
