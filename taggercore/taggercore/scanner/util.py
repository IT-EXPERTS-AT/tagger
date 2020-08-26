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
from typing import Any, List

from taggercore.model import Resource, Tag


def create_resource(resource: Any) -> Resource:
    """Map a skew resource to a taggercore resource"""
    return Resource(
        arn=resource.arn,
        id=resource.id,
        resource_type=resource.resourcetype,
        current_tags=[Tag(key, value) for key, value in resource.tags.items()],
        name=resource.name,
    )


def sort_resources(resources: List[Resource]) -> List[Resource]:
    return sorted(resources, key=lambda x: (x.service, x.resource_type))
