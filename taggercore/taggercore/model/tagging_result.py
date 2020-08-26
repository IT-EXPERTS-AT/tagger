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
from typing import List, Dict


class TaggingResult:
    def __init__(self, successful_arns: List[str], failed_arns: Dict[str, str]):
        self._successful_arns = successful_arns
        self._failed_arns = failed_arns

    def __eq__(self, other):
        return (
            self._successful_arns == other.successful_arns
            and self._failed_arns == other.failed_arns
        )

    def __repr__(self):
        return "Successful: {} , Failed: {}".format(
            self._successful_arns, self._failed_arns
        )

    @property
    def successful_arns(self):
        return self._successful_arns

    @property
    def failed_arns(self):
        return self._failed_arns
