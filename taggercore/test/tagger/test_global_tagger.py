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
from taggercore.tagger import GlobalTagger, AbstractResourceGroupApiTagger
from test.stubs.core_resource_stubs import tags, global_resources


class TestGlobalTagger:
    def test_verify_correct_boto_client_call(
        self, mocker, account_and_profile_configured
    ):
        expected_tags = {tag.key: tag.value for tag in tags()}
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocked_init_client = mocker.patch.object(GlobalTagger, "init_client")

        GlobalTagger(tags(), global_resources()).tag_all()

        mocked_init_client.return_value.tag_resources.assert_called_with(
            ResourceARNList=[
                "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            ],
            Tags=expected_tags,
        )
