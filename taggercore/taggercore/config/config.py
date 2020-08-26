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
from typing import Callable

import skew

from . import TaggercoreConfigError
from .credentials import Credentials


class Config:
    def __init__(
            self,
            credentials: Credentials = None,
            profile: str = None,
            account_id: str = None,
    ):
        self._credentials = credentials
        self._profile = profile
        self._account_id = account_id

    @property
    def credentials(self):
        return self._credentials

    @property
    def profile(self):
        return self._profile

    @property
    def account_id(self):
        return self._account_id


_config: Config = Config()


def get_config() -> Config:
    global _config
    return _config


def set_config(config_dict: Config):
    """ Set global config for taggercore and keep it in sync with skew configuration

    Setting the skew config is required to ensure scanners are working properly

    :param config_dict:
    """
    global _config
    skew.set_config(
        {"accounts": {config_dict.account_id: {"profile": config_dict.profile}}}
    )
    _config = config_dict


def ensure_config_is_set(func: Callable):
    """ Verifies that taggercore is configured

    :raises TaggercoreConfigError
    :param func: function which requires a config object
    :return:
    """

    def function_wrapper(*args):
        config = get_config()
        if not config.profile and not config.account_id:
            raise TaggercoreConfigError(
                f"No profile and no account id found. Please set the configuration before using {func}")
        else:
            return func(*args)

    return function_wrapper
