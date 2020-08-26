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

import typer
from rich.console import Console
from taggercore.model import Tag

from taggercli.commands.exceptions import IllegalInputError
from taggercli.config import set_config, Config, TAGGER_PATH, FILE_NAME

config_group = typer.Typer()

console = Console()


@config_group.command("create")
def config_create():
    account_id = remove_whitespace(typer.prompt("Account ID"))
    default_region = remove_whitespace(typer.prompt("Default region"))
    profile = remove_whitespace(typer.prompt("Profile"))
    tags = remove_whitespace(typer.prompt("Tags (Key=Value) separated by ,"))
    parsed_tags = parse_tags(tags)
    create_config_file(account_id, default_region, profile, parsed_tags)
    set_config(Config(parsed_tags, profile, account_id, default_region))


def remove_whitespace(input_str: str) -> str:
    return input_str.lstrip().rstrip()


def parse_tags(splitted_input: str) -> List[Tag]:
    tags = []
    for tag in splitted_input.split(","):
        try:
            tag_without_whitespace = remove_whitespace(tag)
            key, value = tag_without_whitespace.split("=")
            tags.append(Tag(key, value))
        except ValueError:
            raise IllegalInputError(
                "Please provide tags in the following format: Key=Value and separate them with ,"
            )
    return tags


def create_config_file(
    account_id: str, default_region: str, profile: str, tags: List[Tag]
) -> None:
    config = configparser.ConfigParser()
    config.optionxform = str
    config["Account"] = {"Id": account_id, "Profile": profile, "Region": default_region}
    config["Tags"] = {tag.key: tag.value for tag in tags}

    Path(TAGGER_PATH).mkdir(parents=True, exist_ok=True)
    path = TAGGER_PATH.joinpath(FILE_NAME)
    with open(str(path), "w") as configfile:
        config.write(configfile)
