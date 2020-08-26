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
from distutils.core import setup

from setuptools import find_packages

setup(
    name="taggercli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "taggercore @ git+https://github.com/IT-EXPERTS-AT/tagger.git#egg=taggercore&subdirectory=taggercore",
        "typer",
        "rich",
        "jinja2"
    ],
    extras_require={
        "dev": [
            "pytest",
            "tox",
            "pytest-cov",
            "pytest-mock",
            "black"
        ]
    },
    url="",
    license="",
    author="IT-experts",
    author_email="github@it-experts.at",
    description="",
    entry_points="""
            [console_scripts]
            tagger=taggercli.main:cli
        """,
    include_package_data=True,
)
