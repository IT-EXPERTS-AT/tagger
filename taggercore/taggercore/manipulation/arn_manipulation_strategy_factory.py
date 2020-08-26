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
from typing import Dict

from .arn_manipulation_strategy import ArnManipulationStrategy
from .no_arn_manipulation_strategy import NoArnManipulationStrategy
from .s3_arn_manipulation_strategy import S3ArnManipulationStrategy


class ArnManipulationStrategyFactory:
    """ARNs returned from skew might need some manipulation to be valid """

    _service_strategy_mapping: Dict[str, ArnManipulationStrategy] = {
        "s3": S3ArnManipulationStrategy
    }

    @staticmethod
    def manipulation_strategy_for_service(service: str) -> ArnManipulationStrategy:
        """If manipulation for service exists return it, otherwise use NoArnManipulationStrategy"""
        return ArnManipulationStrategyFactory._service_strategy_mapping.get(
            service, NoArnManipulationStrategy
        )
