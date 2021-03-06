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
from typing import List

import pytest

from taggercore.config import set_config, Config
from taggercore.model import Resource, Tag


class ResourceStub:
    def __init__(self, arn, id, type, tags, name: str = None):
        self.arn = arn
        self.id = id
        self.resourcetype = type
        self.tags = tags
        self.name = name


@pytest.fixture(scope="function")
def account_and_profile_configured():
    yield set_config(Config(profile="another-profile", account_id="111111111111"))
    set_config(Config())


@pytest.fixture(scope="module")
def region_scan():
    yield mock_regional_scan


def mock_regional_scan(service: str):
    if "apigateway" in service:
        return [
            ResourceStub(
                "arn:aws:sqs:eu-central-1:111111111111:someq",
                "someq",
                "queue",
                {},
                "queue-name",
            )
        ]
    elif "cloudformation" in service:
        return [
            ResourceStub(
                "arn:aws:cloudformation:eu-central-1:111111111111:stack/some-stack/b35ac3c0-912c-11ea-890f-02508c92de23",
                "some-stack",
                "stack",
                {},
                None,
            )
        ]
    else:
        return []


@pytest.fixture(scope="module")
def global_scan():
    yield mock_global_scan


def mock_global_scan(service: str):
    if "route53" in service:
        return [
            ResourceStub(
                "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
                "healthcheck",
                {},
                None,
            )
        ]
    elif "cloudfront" in service:
        return [
            ResourceStub(
                "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
                "EMS6KR7IENMDE",
                "distribution",
                {},
                "some-domain",
            )
        ]
    elif "iam" in service:
        return [
            ResourceStub(
                "arn:aws:iam::111111111111:role/some-role",
                "some-role",
                "role",
                {},
                "some-role",
            )
        ]
    else:
        return []


@pytest.fixture(scope="module")
def tags() -> List[Tag]:
    yield [
        Tag("Project", "CoolProject"),
        Tag("Owner", "Fritz"),
        Tag("Created", "2020-08-01"),
    ]


@pytest.fixture(scope="module")
def regional_resources(tags) -> List[Resource]:
    yield [
        Resource("arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags),
        Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq2", "someq2", "queue", tags
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            "sg-b501f6d0",
            "security-group",
            tags,
        ),
    ]


@pytest.fixture(scope="module")
def regional_resources_with_invalid_resource(tags) -> List[Resource]:
    yield [
        Resource("arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags),
        Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq2", "someq2", "queue", tags
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            "sg-b501f6d0",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:invalid",
            "sg-b501f6d0",
            "security-group",
            tags,
        ),
    ]


@pytest.fixture(scope="module")
def global_resources(tags) -> List[Resource]:
    yield [
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
    ]


@pytest.fixture(scope="module")
def too_many_resources_for_single_boto_call(tags) -> List[Resource]:
    yield [
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d1",
            "sg-b501f6d1",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d2",
            "sg-b501f6d2",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d3",
            "sg-b501f6d3",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d4",
            "sg-b501f6d4",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d5",
            "sg-b501f6d5",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d6",
            "sg-b501f6d6",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d7",
            "sg-b501f6d7",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d8",
            "sg-b501f6d8",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d9",
            "sg-b501f6d9",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d10",
            "sg-b501f6d10",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d11",
            "sg-b501f6d11",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d12",
            "sg-b501f6d12",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d13",
            "sg-b501f6d13",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d14",
            "sg-b501f6d14",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d15",
            "sg-b501f6d15",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d16",
            "sg-b501f6d16",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d17",
            "sg-b501f6d17",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d18",
            "sg-b501f6d18",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d19",
            "sg-b501f6d19",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d20",
            "sg-b501f6d20",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d21",
            "sg-b501f6d21",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d22",
            "sg-b501f6d22",
            "security-group",
            tags,
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d23",
            "sg-b501f6d23",
            "security-group",
            tags,
        ),
    ]


@pytest.fixture(scope="module")
def resources_from_two_regions() -> List[Resource]:
    yield [
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0008",
            "subnet-57ce0008",
            "subnet",
            [],
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:subnet/subnet-57ce0009",
            "subnet-57ce0009",
            "subnet",
            [],
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            "sg-b501f6d0",
            "security-group",
            [],
        ),
        Resource(
            "arn:aws:ec2:eu-west-1:111111111111:network-acl/acl-abc",
            "acl-abc",
            "network-acl",
            [],
        ),
        Resource(
            "arn:aws:ec2:eu-west-1:111111111111:security-group/sg-b501f6d1",
            "sg-b501f6d1",
            "security-group",
            [],
        ),
    ]


@pytest.fixture(scope="module")
def iam_roles() -> List[Resource]:
    yield [
        Resource("arn:aws:iam::111111111111:role/some-role", "some-role", "role", []),
        Resource(
            "arn:aws:iam::111111111111:role/another-role", "another-role", "role", []
        ),
    ]


@pytest.fixture(scope="module")
def iam_user() -> List[Resource]:
    yield [
        Resource("arn:aws:iam::111111111111:user/some-user", "some-user", "user", []),
        Resource(
            "arn:aws:iam::111111111111:user/another-user", "another-user", "user", []
        ),
    ]
