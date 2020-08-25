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
from taggercore.manipulation import S3ArnManipulationStrategy


class TestS3ArnManipulationStrategy:
    def test_should_remove_region(self):
        expected = "arn:aws:s3:::some-bucket"
        input_arn = "arn:aws:s3:eu-central-1:111111111111:bucket/some-bucket"

        manipulation_strategy = S3ArnManipulationStrategy()
        actual = manipulation_strategy.manipulate_arn(input_arn)

        assert actual == expected
