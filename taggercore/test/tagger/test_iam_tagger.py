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
from taggercore.tagger import IamTagger, ServiceTagger
from test.stubs.core_resource_stubs import tags, iam_roles


class TestIamTagger:
    def test_tag_all_without_users_and_roles(
        self, mocker, account_and_profile_configured
    ):
        mocker.patch.object(ServiceTagger, "init_session")
        mocker.patch.object(IamTagger, "_init_client")
        expected = [TaggingResult([], {}), TaggingResult([], {})]

        actual = IamTagger([], tags()).tag_resources()

        assert actual == expected

    def test_tag_with_users(self, mocker, account_and_profile_configured):
        mocker.patch.object(ServiceTagger, "init_session")
        mocked_init_client = mocker.patch.object(IamTagger, "_init_client")
        mocked_init_client.return_value.tag_user.side_effect = ["Success", "Success"]
        mocked_init_client.return_value.tag_role.return_value = []
        expected = [
            TaggingResult([], {}),
            TaggingResult(
                [
                    "arn:aws:iam::111111111111:role/some-role",
                    "arn:aws:iam::111111111111:role/another-role",
                ],
                {},
            ),
        ]

        actual = IamTagger(iam_roles(), tags()).tag_resources()

        assert actual == expected
