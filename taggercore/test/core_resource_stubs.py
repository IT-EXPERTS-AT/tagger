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

from taggercore.model import Resource, Tag


def tags() -> List[Tag]:
    return [
        Tag("Project", "CoolProject"),
        Tag("Owner", "Fritz"),
        Tag("Created", "2020-08-01"),
    ]


def regional_resources() -> List[Resource]:
    return [
        Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags()
        ),
        Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq2", "someq2", "queue", tags()
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            "sg-b501f6d0",
            "security-group",
            tags(),
        ),
    ]


def global_resources() -> List[Resource]:
    return [
        Resource(
            "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
            "EMS6KR7IENMDE",
            "distribution",
            tags(),
        ),
        Resource(
            "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            "healthcheck",
            tags(),
        ),
    ]


def too_many_resources_for_single_boto_call() -> List[Resource]:
    return [
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d1",
            "sg-b501f6d1",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d2",
            "sg-b501f6d2",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d3",
            "sg-b501f6d3",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d4",
            "sg-b501f6d4",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d5",
            "sg-b501f6d5",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d6",
            "sg-b501f6d6",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d7",
            "sg-b501f6d7",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d8",
            "sg-b501f6d8",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d9",
            "sg-b501f6d9",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d10",
            "sg-b501f6d10",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d11",
            "sg-b501f6d11",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d12",
            "sg-b501f6d12",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d13",
            "sg-b501f6d13",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d14",
            "sg-b501f6d14",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d15",
            "sg-b501f6d15",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d16",
            "sg-b501f6d16",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d17",
            "sg-b501f6d17",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d18",
            "sg-b501f6d18",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d19",
            "sg-b501f6d19",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d20",
            "sg-b501f6d20",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d21",
            "sg-b501f6d21",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d22",
            "sg-b501f6d22",
            "security-group",
            tags(),
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d23",
            "sg-b501f6d23",
            "security-group",
            tags(),
        ),
    ]


def resources_from_two_regions() -> List[Resource]:
    return [
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


def iam_roles() -> List[Resource]:
    return [
        Resource("arn:aws:iam::111111111111:role/some-role", "some-role", "role", []),
        Resource(
            "arn:aws:iam::111111111111:role/another-role", "another-role", "role", []
        ),
    ]
