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
import configparser
from pathlib import Path
from typing import List

from taggercore.model import Tag
from taggercore.usecase import configure_account_and_profile

from taggercli.config.exceptions import ConfigFileNotWellFormedError


class Config:
    def __init__(
        self,
        tags: List[Tag] = None,
        profile: str = None,
        account_id: str = None,
        default_region: str = None,
    ):
        self.tags = tags
        self.profile = profile
        self.account_id = account_id
        self.default_region = default_region


_config: Config = Config()

TAGGER_PATH = Path.home().joinpath(".tagger/")
FILE_NAME = "config.ini"


def get_config() -> Config:
    global _config
    return _config


def set_config(config: Config) -> None:
    global _config
    _config = config


def read_config_file(file_path: str) -> Config:
    config = configparser.ConfigParser()
    # this confusing configuration preserves the key case
    config.optionxform = str
    config.read_file(open(file_path))
    try:
        parsed_config = Config(
            account_id=config["Account"]["Id"],
            profile=config["Account"]["Profile"],
            tags=parse_tags(config["Tags"]),
            default_region=config["Account"]["Region"],
        )
    except KeyError as ex:
        raise ConfigFileNotWellFormedError(f"Missing key: {ex.args[0]}")
    set_config(parsed_config)
    return parsed_config


def parse_tags(tag_config: configparser.SectionProxy) -> List[Tag]:
    return [Tag(key, value) for key, value in tag_config.items()]


def init_config():
    config_path = TAGGER_PATH.joinpath(FILE_NAME)
    config_file_exists = config_path.is_file()
    if config_file_exists:
        config = read_config_file(str(config_path))
    else:
        raise Exception("No configuration found. Please call config create first")
    configure_account_and_profile(config.account_id, config.profile)
