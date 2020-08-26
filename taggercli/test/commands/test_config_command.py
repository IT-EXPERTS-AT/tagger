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
import os

from taggercore.model import Tag
from typer.testing import CliRunner

from taggercli.main import cli
from taggercli.commands.exceptions import IllegalInputError
from taggercli.config import get_config


class TestConfigCommand:
    def test_config_command(self, mocker, tmpdir):
        tagger_path_mock = mocker.patch(
            "taggercli.commands.config.TAGGER_PATH", return_value=tmpdir
        )
        mocker.patch("taggercli.commands.config.Path.mkdir")
        expected_file_path = str(tmpdir) + "/config.ini"
        tagger_path_mock.joinpath.return_value = expected_file_path

        runner = CliRunner()
        actual = runner.invoke(
            cli,
            ["config", "create"],
            input="111111111111\n eu-central-1\n admin-profile\n Owner=Fritz, Project=CRM\n",
        )
        config = get_config()

        assert not actual.exception
        assert config.account_id == "111111111111"
        assert config.default_region == "eu-central-1"
        assert config.profile == "admin-profile"
        assert config.tags == [Tag("Owner", "Fritz"), Tag("Project", "CRM")]
        assert os.path.isfile(expected_file_path)

    def test_config_command_with_broken_input(self):
        runner = CliRunner()
        actual = runner.invoke(
            cli,
            ["config", "create"],
            input="111111111111\n eu-central-1\n admin-profile\n Owner=Fritz Project=CRM\n",
        )

        assert type(actual.exception) == IllegalInputError
