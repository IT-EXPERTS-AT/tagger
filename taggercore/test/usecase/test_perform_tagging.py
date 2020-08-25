#
# Copyright (c) 2020 it-eXperts IT-Dienstleistungs GmbH.
#
# This file is part of tagger
# (see TBD).
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
from taggercore.tagger import SuperTagger, AbstractResourceGroupApiTagger, ServiceTagger
from taggercore.usecase import perform_tagging
from test.stubs import regional_resources, global_resources, tags


class TestPerformTagging:
    def test_perform_tagging(self, mocker):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        expected_tagging_result = TaggingResult(
            [
                "arn:aws:sqs:eu-central-1:111111111111:someq",
                "arn:aws:sqs:eu-central-1:111111111111:someq2",
                "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
                "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            ],
            {},
        )
        mocked_super_tagger_tag = mocker.patch.object(SuperTagger, "tag_all")

        mocked_super_tagger_tag.return_value = expected_tagging_result

        actual = perform_tagging(regional_resources() + global_resources(), tags())

        assert actual == expected_tagging_result
