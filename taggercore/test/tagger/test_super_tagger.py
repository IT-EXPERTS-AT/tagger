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
from taggercore.tagger import SuperTagger, AbstractResourceGroupApiTagger, ServiceTagger
from test.stubs.core_resource_stubs import (
    tags,
    resources_from_two_regions,
    iam_roles,
    global_resources,
)


class TestSuperTagger:
    def test_should_create_region_taggers(self, mocker, account_and_profile_configured):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(resources_from_two_regions(), tags())

        assert len(tagger.region_taggers) == 2
        assert len(tagger.service_taggers) == 0
        assert tagger.region_taggers[0].region == "eu-central-1"
        assert tagger.region_taggers[1].region == "eu-west-1"
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger(self, mocker, account_and_profile_configured):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(iam_roles(), tags())

        assert len(tagger.service_taggers) == 1
        assert len(tagger.region_taggers) == 0
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger_and_region_taggers(
        self, mocker, account_and_profile_configured
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(iam_roles() + resources_from_two_regions(), tags())

        assert len(tagger.service_taggers) == 1
        assert tagger.service_taggers[0].resources == iam_roles()
        assert len(tagger.region_taggers) == 2
        assert tagger.global_tagger.arns == []

    def test_should_create_service_tagger_and_region_taggers_and_global_tagger_with_arns(
        self, mocker, account_and_profile_configured
    ):
        mocker.patch.object(AbstractResourceGroupApiTagger, "init_session")
        mocker.patch.object(ServiceTagger, "init_session")
        tagger = SuperTagger(
            iam_roles() + resources_from_two_regions() + global_resources(), tags()
        )

        assert len(tagger.service_taggers) == 1
        assert len(tagger.region_taggers) == 2
        assert tagger.global_tagger.arns == [
            resource.arn for resource in global_resources()
        ]
