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
import pytest
from taggercore.model import Tag

from taggercli.config import read_config_file
from taggercli.config.exceptions import ConfigFileNotWellFormedError


class TestConfig:
    def test_parse_config(self):
        # path relative to tox.ini is required to make file accessible in tox ( https://stackoverflow.com/questions/53309298/how-can-i-make-test-data-files-accessible-to-pytest-tests-when-run-with-tox )
        config = read_config_file("test/config/test_config.ini")
        assert config.profile == "some-profile"
        assert config.account_id == "111111111111"
        assert config.tags == [
            Tag("service", "service1"),
            Tag("cost-center", "marketing"),
            Tag("timestamp", "20200808-1030"),
        ]

    def test_keep_case_of_tags(self):
        config = read_config_file("test/config/test_config_with_mixed_cases.ini")

        assert config.tags == [
            Tag("service", "service1"),
            Tag("cost-center", "Marketing"),
            Tag("timestamp", "20200808-1030"),
            Tag("Owner", "Fritz"),
        ]

    def test_throw_error_on_missing_key(self):
        with pytest.raises(ConfigFileNotWellFormedError):
            read_config_file("test/config/test_malformed_config.ini")
