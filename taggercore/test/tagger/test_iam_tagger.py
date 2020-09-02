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
import botocore
import pytest

from taggercore.config import TaggercoreConfigError
from taggercore.model import TaggingResult
from taggercore.tagger import IamTagger, ServiceTagger


class TestIamTagger:
    def test_tag_all_without_users_and_roles(
        self, mocker, account_and_profile_configured, tags
    ):
        mocker.patch.object(ServiceTagger, "init_session")
        mocker.patch.object(IamTagger, "_init_client")
        expected = [TaggingResult([], {}), TaggingResult([], {})]

        actual = IamTagger([], tags).tag_resources()

        assert actual == expected

    def test_tag_with_roles_and_user_succeeds(
        self, mocker, account_and_profile_configured, iam_roles, iam_user, tags
    ):
        mocker.patch.object(ServiceTagger, "init_session")
        mocked_init_client = mocker.patch.object(IamTagger, "_init_client")
        mocked_init_client.return_value.tag_user.side_effect = ["Success", "Success"]
        mocked_init_client.return_value.tag_role.return_value = []
        expected = [
            TaggingResult(
                [
                    "arn:aws:iam::111111111111:user/some-user",
                    "arn:aws:iam::111111111111:user/another-user",
                ],
                {},
            ),
            TaggingResult(
                [
                    "arn:aws:iam::111111111111:role/some-role",
                    "arn:aws:iam::111111111111:role/another-role",
                ],
                {},
            ),
        ]

        actual = IamTagger(iam_roles + iam_user, tags).tag_resources()

        assert actual == expected

    def test_tag_fails_without_config(self, iam_roles, tags):
        with pytest.raises(TaggercoreConfigError):
            IamTagger(iam_roles, tags).tag_resources()

    def test_tag_users_fails_to_tag(
        self, mocker, account_and_profile_configured, iam_user, tags
    ):
        mocker.patch.object(ServiceTagger, "init_session")
        mocked_client = mocker.patch.object(IamTagger, "_init_client")
        mocked_client.return_value.tag_user.side_effect = (
            botocore.exceptions.ClientError(
                operation_name="tag_user",
                error_response={
                    "Error": {
                        "Code": "NoSuchEntityException",
                        "Message": "The iam user doesnt exist",
                    },
                },
            )
        )
        expected = [
            TaggingResult(
                [],
                {
                    "arn:aws:iam::111111111111:user/some-user": "The iam user doesnt exist",
                    "arn:aws:iam::111111111111:user/another-user": "The iam user doesnt exist",
                },
            ),
            TaggingResult([], {}),
        ]

        actual = IamTagger(iam_user, tags).tag_resources()

        assert actual == expected

    def test_tag_roles_fails_to_tag(
        self, mocker, account_and_profile_configured, iam_roles, tags
    ):
        mocker.patch.object(ServiceTagger, "init_session")
        mocked_client = mocker.patch.object(IamTagger, "_init_client")
        mocked_client.return_value.tag_role.side_effect = (
            botocore.exceptions.ClientError(
                operation_name="tag_role",
                error_response={
                    "Error": {
                        "Code": "NoSuchEntityException",
                        "Message": "The iam role doesnt exist",
                    },
                },
            )
        )
        expected = [
            TaggingResult(
                [],
                {},
            ),
            TaggingResult(
                [],
                {
                    "arn:aws:iam::111111111111:role/some-role": "The iam role doesnt exist",
                    "arn:aws:iam::111111111111:role/another-role": "The iam role doesnt exist",
                },
            ),
        ]

        actual = IamTagger(iam_roles, tags).tag_resources()

        assert actual == expected
